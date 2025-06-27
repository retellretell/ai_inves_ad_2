import streamlit as st
import requests
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import feedparser
from dotenv import load_dotenv
import time
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 환경변수 로드
load_dotenv()

# ================================
# 환경 설정 및 API 키 관리
# ================================

class Config:
    """환경 설정 클래스"""
    
    # HyperCLOVA X API 설정
    HYPERCLOVA_API_KEY = os.getenv('HYPERCLOVA_API_KEY', '')
    HYPERCLOVA_API_URL = os.getenv('HYPERCLOVA_API_URL', 'https://clovastudio.stream.ntruss.com/testapp/v1/chat-completions/HCX-DASH-001')
    
    # OpenAI API 설정 (HyperCLOVA X 실패시 대체)
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    OPENAI_API_URL = 'https://api.openai.com/v1/chat/completions'
    
    # 뉴스 API 설정
    NEWS_API_KEY = os.getenv('NEWS_API_KEY', '')
    NEWS_API_URL = 'https://newsapi.org/v2/everything'
    
    # Alpha Vantage API (ESG 데이터용)
    ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', '')
    
    # 기본 설정
    DEFAULT_STOCKS = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'NVDA']
    MAX_RETRIES = 3
    TIMEOUT = 30

# ================================
# API 통신 클래스
# ================================

class LLMClient:
    """LLM API 클라이언트"""
    
    def __init__(self):
        self.config = Config()
    
    def call_hyperclova_x(self, prompt: str) -> str:
        """HyperCLOVA X API 호출"""
        try:
            if not self.config.HYPERCLOVA_API_KEY:
                raise ValueError("HyperCLOVA X API 키가 설정되지 않았습니다.")
            
            headers = {
                'X-NCP-CLOVASTUDIO-API-KEY': self.config.HYPERCLOVA_API_KEY,
                'X-NCP-APIGW-API-KEY': self.config.HYPERCLOVA_API_KEY,
                'Content-Type': 'application/json'
            }
            
            payload = {
                'messages': [
                    {
                        'role': 'system',
                        'content': '당신은 전문적인 투자 어드바이저입니다. 정확하고 유용한 투자 정보를 제공해주세요.'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'topP': 0.8,
                'topK': 0,
                'maxTokens': 1000,
                'temperature': 0.3,
                'repeatPenalty': 1.2,
                'includeAiFilters': True
            }
            
            response = requests.post(
                self.config.HYPERCLOVA_API_URL,
                headers=headers,
                json=payload,
                timeout=self.config.TIMEOUT
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('result', {}).get('message', {}).get('content', '응답을 생성할 수 없습니다.')
            else:
                raise Exception(f"API 호출 실패: {response.status_code}")
                
        except Exception as e:
            logger.error(f"HyperCLOVA X API 오류: {str(e)}")
            raise e
    
    def call_openai(self, prompt: str) -> str:
        """OpenAI API 호출 (대체 수단)"""
        try:
            if not self.config.OPENAI_API_KEY:
                raise ValueError("OpenAI API 키가 설정되지 않았습니다.")
            
            headers = {
                'Authorization': f'Bearer {self.config.OPENAI_API_KEY}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': 'gpt-3.5-turbo',
                'messages': [
                    {
                        'role': 'system',
                        'content': '당신은 전문적인 투자 어드바이저입니다. 정확하고 유용한 투자 정보를 제공해주세요.'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'max_tokens': 1000,
                'temperature': 0.3
            }
            
            response = requests.post(
                self.config.OPENAI_API_URL,
                headers=headers,
                json=payload,
                timeout=self.config.TIMEOUT
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                raise Exception(f"API 호출 실패: {response.status_code}")
                
        except Exception as e:
            logger.error(f"OpenAI API 오류: {str(e)}")
            raise e
    
    def get_ai_response(self, prompt: str) -> str:
        """AI 응답 생성 (HyperCLOVA X 우선, 실패시 OpenAI)"""
        try:
            # HyperCLOVA X 우선 시도
            return self.call_hyperclova_x(prompt)
        except Exception as e:
            st.warning(f"HyperCLOVA X 연결 실패: {str(e)}")
            try:
                # OpenAI로 대체
                st.info("OpenAI API로 대체하여 응답을 생성합니다...")
                return self.call_openai(prompt)
            except Exception as e2:
                st.error(f"모든 AI API 연결 실패: {str(e2)}")
                return "죄송합니다. 현재 AI 서비스에 연결할 수 없습니다. API 키 설정을 확인해주세요."

# ================================
# 데이터 수집 클래스
# ================================

class DataCollector:
    """실제 데이터 수집 클래스"""
    
    def __init__(self):
        self.config = Config()
    
    def get_stock_data(self, symbol: str, period: str = "1y") -> pd.DataFrame:
        """실제 주식 데이터 수집"""
        try:
            stock = yf.Ticker(symbol)
            data = stock.history(period=period)
            if data.empty:
                raise ValueError(f"'{symbol}' 종목 데이터를 찾을 수 없습니다.")
            return data
        except Exception as e:
            logger.error(f"주식 데이터 수집 오류 ({symbol}): {str(e)}")
            raise e
    
    def get_stock_info(self, symbol: str) -> dict:
        """주식 기본 정보 수집"""
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            return {
                'name': info.get('longName', symbol),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'marketCap': info.get('marketCap', 0),
                'pe_ratio': info.get('forwardPE', 0),
                'dividend_yield': info.get('dividendYield', 0)
            }
        except Exception as e:
            logger.error(f"주식 정보 수집 오류 ({symbol}): {str(e)}")
            return {'name': symbol, 'sector': 'N/A', 'industry': 'N/A', 'marketCap': 0, 'pe_ratio': 0, 'dividend_yield': 0}
    
    def get_financial_news(self, query: str = "stock market", limit: int = 10) -> list:
        """실제 금융 뉴스 수집"""
        try:
            # NewsAPI를 우선 시도
            if self.config.NEWS_API_KEY:
                return self._get_news_from_api(query, limit)
            else:
                # 무료 RSS 피드 사용
                return self._get_news_from_rss(limit)
        except Exception as e:
            logger.error(f"뉴스 수집 오류: {str(e)}")
            return []
    
    def _get_news_from_api(self, query: str, limit: int) -> list:
        """NewsAPI에서 뉴스 수집"""
        try:
            params = {
                'q': query,
                'language': 'en',
                'sortBy': 'publishedAt',
                'pageSize': limit,
                'apiKey': self.config.NEWS_API_KEY
            }
            
            response = requests.get(self.config.NEWS_API_URL, params=params, timeout=self.config.TIMEOUT)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('articles', [])
            else:
                raise Exception(f"NewsAPI 오류: {response.status_code}")
                
        except Exception as e:
            logger.error(f"NewsAPI 오류: {str(e)}")
            return []
    
    def _get_news_from_rss(self, limit: int) -> list:
        """RSS 피드에서 뉴스 수집"""
        try:
            # 무료 금융 뉴스 RSS 피드들
            rss_urls = [
                'https://feeds.finance.yahoo.com/rss/2.0/headline',
                'https://www.cnbc.com/id/100003114/device/rss/rss.html',
                'https://www.reuters.com/markets/rss'
            ]
            
            articles = []
            for url in rss_urls:
                try:
                    feed = feedparser.parse(url)
                    for entry in feed.entries[:limit//len(rss_urls)]:
                        articles.append({
                            'title': entry.get('title', ''),
                            'description': entry.get('summary', ''),
                            'url': entry.get('link', ''),
                            'publishedAt': entry.get('published', ''),
                            'source': {'name': feed.feed.get('title', 'RSS Feed')}
                        })
                except Exception as e:
                    logger.error(f"RSS 피드 오류 ({url}): {str(e)}")
                    continue
            
            return articles[:limit]
            
        except Exception as e:
            logger.error(f"RSS 뉴스 수집 오류: {str(e)}")
            return []
    
    def get_esg_data(self, symbol: str) -> dict:
        """ESG 데이터 수집 (시뮬레이션)"""
        try:
            # 실제 ESG API가 있다면 여기서 호출
            # 현재는 yfinance에서 가능한 정보만 수집
            stock = yf.Ticker(symbol)
            info = stock.info
            
            # ESG 관련 정보 추출 (제한적)
            esg_data = {
                'esg_score': info.get('totalEsgScore', 0),
                'environment_score': info.get('environmentScore', 0),
                'social_score': info.get('socialScore', 0),
                'governance_score': info.get('governanceScore', 0),
                'controversy_level': info.get('highestControversy', 0),
                'last_updated': datetime.now().strftime('%Y-%m-%d')
            }
            
            return esg_data
            
        except Exception as e:
            logger.error(f"ESG 데이터 수집 오류 ({symbol}): {str(e)}")
            return {
                'esg_score': 0,
                'environment_score': 0,
                'social_score': 0,
                'governance_score': 0,
                'controversy_level': 0,
                'last_updated': datetime.now().strftime('%Y-%m-%d')
            }

# ================================
# 시각화 클래스
# ================================

class ChartGenerator:
    """차트 생성 클래스"""
    
    @staticmethod
    def create_stock_chart(data: pd.DataFrame, symbol: str) -> go.Figure:
        """주식 차트 생성"""
        try:
            fig = go.Figure()
            
            # 캔들스틱 차트
            fig.add_trace(go.Candlestick(
                x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name=symbol
            ))
            
            # 거래량 추가
            fig.add_trace(go.Scatter(
                x=data.index,
                y=data['Volume'],
                mode='lines',
                name='Volume',
                yaxis='y2',
                line=dict(color='rgba(0,100,80,0.8)')
            ))
            
            fig.update_layout(
                title=f'{symbol} 주가 차트',
                xaxis_title='날짜',
                yaxis_title='주가 (USD)',
                yaxis2=dict(
                    title='거래량',
                    overlaying='y',
                    side='right'
                ),
                template='plotly_white',
                height=600
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"차트 생성 오류: {str(e)}")
            raise e
    
    @staticmethod
    def create_portfolio_chart(portfolio_data: dict) -> go.Figure:
        """포트폴리오 차트 생성"""
        try:
            symbols = list(portfolio_data.keys())
            values = list(portfolio_data.values())
            
            fig = go.Figure(data=[go.Pie(
                labels=symbols,
                values=values,
                hole=0.3
            )])
            
            fig.update_layout(
                title='포트폴리오 구성',
                template='plotly_white',
                height=500
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"포트폴리오 차트 생성 오류: {str(e)}")
            raise e
    
    @staticmethod
    def create_esg_chart(esg_data: dict) -> go.Figure:
        """ESG 차트 생성"""
        try:
            categories = ['Environment', 'Social', 'Governance']
            scores = [
                esg_data.get('environment_score', 0),
                esg_data.get('social_score', 0),
                esg_data.get('governance_score', 0)
            ]
            
            fig = go.Figure(data=[
                go.Bar(x=categories, y=scores, marker_color=['green', 'blue', 'orange'])
            ])
            
            fig.update_layout(
                title='ESG 점수',
                xaxis_title='ESG 카테고리',
                yaxis_title='점수',
                yaxis=dict(range=[0, 100]),
                template='plotly_white',
                height=400
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"ESG 차트 생성 오류: {str(e)}")
            raise e

# ================================
# 메인 애플리케이션
# ================================

def main():
    """메인 애플리케이션"""
    
    # 페이지 설정
    st.set_page_config(
        page_title="HyperCLOVA X 기반 AI 투자 어드바이저",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 스타일 설정
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 헤더
    st.markdown('<div class="main-header">📈 HyperCLOVA X 기반 AI 투자 어드바이저</div>', unsafe_allow_html=True)
    
    # 클라이언트 초기화
    llm_client = LLMClient()
    data_collector = DataCollector()
    chart_generator = ChartGenerator()
    
    # 사이드바 - 설정
    with st.sidebar:
        st.header("⚙️ 설정")
        
        # API 상태 확인
        st.subheader("API 상태")
        hyperclova_status = "✅ 연결됨" if Config.HYPERCLOVA_API_KEY else "❌ 미설정"
        openai_status = "✅ 연결됨" if Config.OPENAI_API_KEY else "❌ 미설정"
        news_status = "✅ 연결됨" if Config.NEWS_API_KEY else "⚠️ RSS 사용"
        
        st.write(f"HyperCLOVA X: {hyperclova_status}")
        st.write(f"OpenAI: {openai_status}")
        st.write(f"뉴스 API: {news_status}")
        
        # 설정 가이드
        with st.expander("API 키 설정 가이드"):
            st.write("""
            **환경변수 설정 방법:**
            
            1. `.env` 파일 생성:
            ```
            HYPERCLOVA_API_KEY=your_key_here
            OPENAI_API_KEY=your_key_here
            NEWS_API_KEY=your_key_here
            ```
            
            2. Streamlit Secrets 사용:
            `.streamlit/secrets.toml` 파일 생성
            
            3. 시스템 환경변수 설정
            """)
    
    # 메인 탭
    tab1, tab2, tab3, tab4 = st.tabs(["💬 AI 상담", "📊 시장 분석", "🌱 ESG 분석", "📰 뉴스"])
    
    # 탭 1: AI 상담
    with tab1:
        st.markdown('<div class="section-header">AI 투자 상담</div>', unsafe_allow_html=True)
        
        # 질문 입력
        user_question = st.text_area(
            "투자 관련 질문을 입력하세요:",
            placeholder="예: 삼성전자 주식 전망은 어떤가요? 또는 달러 환율 전망을 알려주세요.",
            height=100
        )
        
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("💡 AI 상담", type="primary"):
                if user_question.strip():
                    with st.spinner("AI가 답변을 생성하고 있습니다..."):
                        try:
                            # AI 응답 생성
                            response = llm_client.get_ai_response(user_question)
                            
                            # 응답 표시
                            st.markdown('<div class="info-box">', unsafe_allow_html=True)
                            st.markdown("**🤖 AI 투자 어드바이저 답변:**")
                            st.write(response)
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                            # 주의사항 표시
                            st.warning("⚠️ 본 내용은 참고용이며, 실제 투자 결정은 신중히 하시기 바랍니다.")
                            
                        except Exception as e:
                            st.error(f"AI 상담 중 오류가 발생했습니다: {str(e)}")
                else:
                    st.warning("질문을 입력해주세요.")
        
        # 샘플 질문
        st.markdown("**💡 샘플 질문:**")
        sample_questions = [
            "테슬라 주식의 장단기 전망은?",
            "반도체 섹터 투자 전략을 추천해주세요",
            "달러 강세가 한국 주식시장에 미치는 영향은?",
            "ESG 투자의 장단점을 설명해주세요"
        ]
        
        for i, question in enumerate(sample_questions):
            if st.button(f"📝 {question}", key=f"sample_q_{i}"):
                st.text_area("투자 관련 질문을 입력하세요:", value=question, key=f"filled_q_{i}")
    
    # 탭 2: 시장 분석
    with tab2:
        st.markdown('<div class="section-header">실시간 시장 분석</div>', unsafe_allow_html=True)
        
        # 종목 선택
        col1, col2 = st.columns([2, 1])
        with col1:
            symbol = st.selectbox(
                "분석할 종목을 선택하세요:",
                Config.DEFAULT_STOCKS + ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX'],
                index=0
            )
        
        with col2:
            period = st.selectbox(
                "기간:",
                ["1mo", "3mo", "6mo", "1y", "2y"],
                index=3
            )
        
        if st.button("📊 분석 시작", type="primary"):
            try:
                with st.spinner("시장 데이터를 분석하고 있습니다..."):
                    # 주식 데이터 수집
                    stock_data = data_collector.get_stock_data(symbol, period)
                    stock_info = data_collector.get_stock_info(symbol)
                    
                    # 기본 정보 표시
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("종목명", stock_info['name'])
                    with col2:
                        current_price = stock_data['Close'].iloc[-1]
                        prev_price = stock_data['Close'].iloc[-2]
                        change = current_price - prev_price
                        change_pct = (change / prev_price) * 100
                        st.metric("현재가", f"${current_price:.2f}", f"{change:+.2f} ({change_pct:+.2f}%)")
                    with col3:
                        st.metric("섹터", stock_info['sector'])
                    with col4:
                        market_cap = stock_info['marketCap']
                        if market_cap > 1e12:
                            market_cap_str = f"${market_cap/1e12:.2f}T"
                        elif market_cap > 1e9:
                            market_cap_str = f"${market_cap/1e9:.2f}B"
                        else:
                            market_cap_str = f"${market_cap/1e6:.2f}M"
                        st.metric("시가총액", market_cap_str)
                    
                    # 차트 생성
                    chart = chart_generator.create_stock_chart(stock_data, symbol)
                    st.plotly_chart(chart, use_container_width=True)
                    
                    # 기술적 분석
                    st.subheader("📈 기술적 분석")
                    
                    # 이동평균
                    stock_data['MA20'] = stock_data['Close'].rolling(window=20).mean()
                    stock_data['MA50'] = stock_data['Close'].rolling(window=50).mean()
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**이동평균 분석:**")
                        current_price = stock_data['Close'].iloc[-1]
                        ma20 = stock_data['MA20'].iloc[-1]
                        ma50 = stock_data['MA50'].iloc[-1]
                        
                        if current_price > ma20 > ma50:
                            st.success("✅ 상승 추세 (현재가 > MA20 > MA50)")
                        elif current_price < ma20 < ma50:
                            st.error("❌ 하락 추세 (현재가 < MA20 < MA50)")
                        else:
                            st.warning("⚠️ 혼조 상태")
                    
                    with col2:
                        st.write("**변동성 분석:**")
                        volatility = stock_data['Close'].pct_change().std() * (252**0.5) * 100
                        st.metric("연간 변동성", f"{volatility:.2f}%")
                        
                        if volatility > 30:
                            st.error("높은 변동성")
                        elif volatility > 20:
                            st.warning("중간 변동성")
                        else:
                            st.success("낮은 변동성")
                    
            except Exception as e:
                st.error(f"시장 분석 중 오류가 발생했습니다: {str(e)}")
                st.info("다른 종목을 선택하거나 잠시 후 다시 시도해주세요.")
    
    # 탭 3: ESG 분석
    with tab3:
        st.markdown('<div class="section-header">ESG 분석</div>', unsafe_allow_html=True)
        
        esg_symbol = st.selectbox(
            "ESG 분석할 종목을 선택하세요:",
            Config.DEFAULT_STOCKS,
            index=0,
            key="esg_symbol"
        )
        
        if st.button("🌱 ESG 분석", type="primary"):
            try:
                with st.spinner("ESG 데이터를 분석하고 있습니다..."):
                    # ESG 데이터 수집
                    esg_data = data_collector.get_esg_data(esg_symbol)
                    
                    # ESG 점수 표시
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("총 ESG 점수", f"{esg_data['esg_score']}/100")
                    with col2:
                        st.metric("환경 점수", f"{esg_data['environment_score']}/100")
                    with col3:
                        st.metric("사회 점수", f"{esg_data['social_score']}/100")
                    with col4:
                        st.metric("지배구조 점수", f"{esg_data['governance_score']}/100")
                    
                    # ESG 차트
                    if any(esg_data[key] > 0 for key in ['environment_score', 'social_score', 'governance_score']):
                        esg_chart = chart_generator.create_esg_chart(esg_data)
                        st.plotly_chart(esg_chart, use_container_width=True)
                    else:
                        st.info("📊 해당 종목의 ESG 데이터가 제한적입니다.")
                    
                    # ESG 리스크 분석
                    st.subheader("⚠️ ESG 리스크 분석")
                    
                    controversy_level = esg_data['controversy_level']
                    if controversy_level == 0:
                        st.success("✅ ESG 관련 논란 없음")
                    elif controversy_level <= 2:
                        st.warning(f"⚠️ 낮은 수준의 ESG 논란 (레벨 {controversy_level})")
                    elif controversy_level <= 3:
                        st.warning(f"⚠️ 중간 수준의 ESG 논란 (레벨 {controversy_level})")
                    else:
                        st.error(f"❌ 높은 수준의 ESG 논란 (레벨 {controversy_level})")
                    
                    # ESG 투자 가이드
                    with st.expander("📚 ESG 투자 가이드"):
                        st.write("""
                        **ESG 점수 해석:**
                        - **80-100점**: 매우 우수한 ESG 성과
                        - **60-79점**: 우수한 ESG 성과
                        - **40-59점**: 평균적인 ESG 성과
                        - **20-39점**: 개선이 필요한 ESG 성과
                        - **0-19점**: ESG 위험이 높음
                        
                        **ESG 투자 시 고려사항:**
                        - 환경: 탄소 배출, 재생에너지 사용, 환경 오염 관리
                        - 사회: 직원 복지, 지역사회 기여, 제품 안전성
                        - 지배구조: 이사회 독립성, 투명한 경영, 주주 권익 보호
                        """)
                    
                    st.caption(f"데이터 업데이트: {esg_data['last_updated']}")
                    
            except Exception as e:
                st.error(f"ESG 분석 중 오류가 발생했습니다: {str(e)}")
                st.info("다른 종목을 선택하거나 잠시 후 다시 시도해주세요.")
    
    # 탭 4: 뉴스
    with tab4:
        st.markdown('<div class="section-header">실시간 금융 뉴스</div>', unsafe_allow_html=True)
        
        # 뉴스 카테고리 선택
        col1, col2 = st.columns([2, 1])
        with col1:
            news_query = st.selectbox(
                "뉴스 카테고리:",
                ["stock market", "cryptocurrency", "economy", "federal reserve", "inflation", "technology stocks"],
                index=0
            )
        
        with col2:
            news_count = st.selectbox("뉴스 개수:", [5, 10, 15, 20], index=1)
        
        if st.button("📰 뉴스 불러오기", type="primary"):
            try:
                with st.spinner("최신 뉴스를 불러오고 있습니다..."):
                    # 뉴스 데이터 수집
                    news_articles = data_collector.get_financial_news(news_query, news_count)
                    
                    if news_articles:
                        st.success(f"✅ {len(news_articles)}개의 뉴스를 불러왔습니다.")
                        
                        # 뉴스 표시
                        for i, article in enumerate(news_articles):
                            with st.expander(f"📄 {article.get('title', 'No Title')}", expanded=(i < 3)):
                                col1, col2 = st.columns([3, 1])
                                
                                with col1:
                                    # 뉴스 내용
                                    description = article.get('description', '내용이 없습니다.')
                                    if description:
                                        st.write(description)
                                    
                                    # 뉴스 링크
                                    url = article.get('url', '')
                                    if url:
                                        st.markdown(f"[📖 전체 기사 읽기]({url})")
                                
                                with col2:
                                    # 뉴스 메타데이터
                                    source = article.get('source', {})
                                    source_name = source.get('name', 'Unknown') if isinstance(source, dict) else str(source)
                                    st.caption(f"출처: {source_name}")
                                    
                                    published_at = article.get('publishedAt', '')
                                    if published_at:
                                        try:
                                            # 날짜 파싱 시도
                                            if 'T' in published_at:
                                                pub_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                                                st.caption(f"발행: {pub_date.strftime('%Y-%m-%d %H:%M')}")
                                            else:
                                                st.caption(f"발행: {published_at}")
                                        except:
                                            st.caption(f"발행: {published_at}")
                        
                        # AI 뉴스 요약
                        if st.button("🤖 AI 뉴스 요약", key="news_summary"):
                            with st.spinner("AI가 뉴스를 요약하고 있습니다..."):
                                try:
                                    # 뉴스 제목들을 합쳐서 요약 요청
                                    news_titles = [article.get('title', '') for article in news_articles[:5]]
                                    summary_prompt = f"다음 금융 뉴스 제목들을 바탕으로 현재 시장 상황을 요약해주세요:\n" + "\n".join(news_titles)
                                    
                                    summary = llm_client.get_ai_response(summary_prompt)
                                    
                                    st.markdown('<div class="info-box">', unsafe_allow_html=True)
                                    st.markdown("**🤖 AI 뉴스 요약:**")
                                    st.write(summary)
                                    st.markdown('</div>', unsafe_allow_html=True)
                                    
                                except Exception as e:
                                    st.error(f"뉴스 요약 중 오류가 발생했습니다: {str(e)}")
                    else:
                        st.warning("⚠️ 뉴스를 불러올 수 없습니다. 네트워크 연결을 확인해주세요.")
                        
                        # 대체 뉴스 피드 제안
                        st.info("""
                        **대체 뉴스 소스:**
                        - [Yahoo Finance](https://finance.yahoo.com/news/)
                        - [CNBC](https://www.cnbc.com/markets/)
                        - [Reuters Business](https://www.reuters.com/business/)
                        - [Bloomberg](https://www.bloomberg.com/markets)
                        """)
                    
            except Exception as e:
                st.error(f"뉴스 로딩 중 오류가 발생했습니다: {str(e)}")
                st.info("잠시 후 다시 시도해주세요.")
    
    # 하단 정보
    st.markdown("---")
    
    # 포트폴리오 시뮬레이션 섹션
    with st.expander("💼 포트폴리오 시뮬레이션", expanded=False):
        st.markdown("**포트폴리오 구성:**")
        
        portfolio_stocks = st.multiselect(
            "종목 선택:",
            Config.DEFAULT_STOCKS + ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA'],
            default=['AAPL', 'GOOGL', 'MSFT']
        )
        
        if portfolio_stocks:
            # 비중 설정
            weights = []
            st.write("**종목별 비중 설정 (%):**")
            cols = st.columns(len(portfolio_stocks))
            
            for i, stock in enumerate(portfolio_stocks):
                with cols[i]:
                    weight = st.number_input(
                        f"{stock}",
                        min_value=0.0,
                        max_value=100.0,
                        value=100.0/len(portfolio_stocks),
                        step=5.0,
                        key=f"weight_{stock}"
                    )
                    weights.append(weight)
            
            total_weight = sum(weights)
            if abs(total_weight - 100.0) > 0.1:
                st.warning(f"⚠️ 총 비중이 {total_weight:.1f}%입니다. 100%로 맞춰주세요.")
            else:
                st.success("✅ 포트폴리오 비중이 올바르게 설정되었습니다.")
                
                if st.button("📊 포트폴리오 분석"):
                    try:
                        with st.spinner("포트폴리오를 분석하고 있습니다..."):
                            # 포트폴리오 데이터 생성
                            portfolio_data = dict(zip(portfolio_stocks, weights))
                            
                            # 포트폴리오 차트
                            portfolio_chart = chart_generator.create_portfolio_chart(portfolio_data)
                            st.plotly_chart(portfolio_chart, use_container_width=True)
                            
                            # 포트폴리오 성과 분석
                            st.subheader("📈 포트폴리오 성과 분석")
                            
                            total_return = 0
                            total_risk = 0
                            
                            for stock, weight in portfolio_data.items():
                                try:
                                    stock_data = data_collector.get_stock_data(stock, "1y")
                                    returns = stock_data['Close'].pct_change().dropna()
                                    annual_return = returns.mean() * 252 * 100
                                    annual_volatility = returns.std() * (252**0.5) * 100
                                    
                                    total_return += annual_return * (weight / 100)
                                    total_risk += (annual_volatility * (weight / 100)) ** 2
                                except:
                                    continue
                            
                            total_risk = (total_risk ** 0.5)
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("예상 연간 수익률", f"{total_return:.2f}%")
                            with col2:
                                st.metric("예상 연간 변동성", f"{total_risk:.2f}%")
                            with col3:
                                sharpe_ratio = total_return / total_risk if total_risk > 0 else 0
                                st.metric("샤프 비율", f"{sharpe_ratio:.2f}")
                            
                            # 리스크 평가
                            if total_risk < 15:
                                st.success("✅ 낮은 리스크 포트폴리오")
                            elif total_risk < 25:
                                st.warning("⚠️ 중간 리스크 포트폴리오")
                            else:
                                st.error("❌ 높은 리스크 포트폴리오")
                    
                    except Exception as e:
                        st.error(f"포트폴리오 분석 중 오류가 발생했습니다: {str(e)}")
    
    # 푸터
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**💡 사용 팁:**")
        st.write("- API 키를 설정하면 더 정확한 분석이 가능합니다")
        st.write("- 실시간 데이터는 시장 개장 시간에 업데이트됩니다")
    
    with col2:
        st.markdown("**⚠️ 주의사항:**")
        st.write("- 본 서비스는 참고용이며 투자 권유가 아닙니다")
        st.write("- 실제 투자 시 충분한 검토가 필요합니다")
    
    with col3:
        st.markdown("**🔧 기술 스택:**")
        st.write("- HyperCLOVA X / OpenAI API")
        st.write("- yfinance, plotly, streamlit")
    
    # 실시간 시계 (선택사항)
    with st.sidebar:
        st.markdown("---")
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.caption(f"현재 시간: {current_time}")
        
        # 시장 상태 표시
        now = datetime.now()
        if 9 <= now.hour < 16:  # 대략적인 미국 시장 시간 (EST 기준)
            st.success("🟢 미국 시장 개장 중")
        else:
            st.info("🔴 미국 시장 마감")

if __name__ == "__main__":
    main()
