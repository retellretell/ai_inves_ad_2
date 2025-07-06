"""
HyperCLOVA X 기반 AI 투자 어드바이저
미래에셋증권 AI Festival 2025 출품작
- 실시간 분석 전용 버전
"""

import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import requests
import feedparser
from datetime import datetime, timedelta
import json
import os
import time
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 페이지 설정
st.set_page_config(
    page_title="HyperCLOVA X AI 투자 어드바이저",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 파일 로드
def load_css():
    """CSS 스타일 로드"""
    try:
        with open('styles.css', 'r', encoding='utf-8') as f:
            css = f.read()
        st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        # CSS 파일이 없을 경우 기본 스타일 사용
        st.markdown("""
        <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            color: #1f77b4;
            text-align: center;
            margin-bottom: 2rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .ai-response {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            border-radius: 1rem;
            margin: 1rem 0;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
        }
        .status-good {
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 0.5rem;
            margin: 0.5rem 0;
            box-shadow: 0 4px 15px rgba(76,175,80,0.3);
        }
        .status-bad {
            background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%);
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 0.5rem;
            margin: 0.5rem 0;
            box-shadow: 0 4px 15px rgba(244,67,54,0.3);
        }
        .error-message {
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 1rem;
            margin: 1rem 0;
            border-left: 5px solid #ff3838;
        }
        </style>
        """, unsafe_allow_html=True)

# API 설정
def get_api_key():
    """API 키 가져오기"""
    try:
        # Streamlit Secrets에서 가져오기
        return st.secrets.get("CLOVA_STUDIO_API_KEY", "")
    except:
        # 환경변수에서 가져오기
        return os.getenv("CLOVA_STUDIO_API_KEY", "")

# 실시간 데이터 수집
@st.cache_data(ttl=300)
def get_real_time_market_data():
    """실시간 시장 데이터 수집"""
    try:
        # 주요 지수 데이터
        indices = {
            "KOSPI": "^KS11",
            "NASDAQ": "^IXIC", 
            "S&P 500": "^GSPC",
            "USD/KRW": "KRW=X"
        }
        
        market_data = {}
        for name, ticker in indices.items():
            try:
                data = yf.Ticker(ticker).history(period="1d", interval="1m")
                if not data.empty:
                    current = data['Close'].iloc[-1]
                    prev = data['Close'].iloc[0]
                    change = ((current - prev) / prev) * 100
                    market_data[name] = {
                        'current': current,
                        'change': change
                    }
            except:
                continue
        
        return market_data
    except Exception as e:
        logger.error(f"시장 데이터 수집 오류: {e}")
        return {}

@st.cache_data(ttl=1800)
def get_recent_news():
    """최신 경제 뉴스 수집"""
    try:
        news_sources = [
            'https://feeds.finance.yahoo.com/rss/2.0/headline',
            'https://feeds.reuters.com/reuters/businessNews',
            'https://rss.cnn.com/rss/money_news_international.rss'
        ]
        
        articles = []
        for url in news_sources:
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries[:2]:
                    articles.append({
                        'title': entry.get('title', ''),
                        'summary': entry.get('summary', ''),
                        'published': entry.get('published', ''),
                        'source': feed.feed.get('title', 'News')
                    })
            except:
                continue
        
        return articles[:6]
    except Exception as e:
        logger.error(f"뉴스 수집 오류: {e}")
        return []

# HyperCLOVA X 클라이언트 (실시간 전용)
class HyperCLOVAXClient:
    def __init__(self):
        self.api_key = get_api_key()
        self.base_url = "https://clovastudio.stream.ntruss.com"
        
    def get_real_time_analysis(self, question: str, market_data: dict, news_data: list) -> str:
        """실시간 데이터 기반 HyperCLOVA X 분석"""
        if not self.api_key:
            raise Exception("API 키가 설정되지 않았습니다. .streamlit/secrets.toml 파일에 CLOVA_STUDIO_API_KEY를 설정해주세요.")
        
        # 실시간 컨텍스트 구성
        market_context = self._format_market_context(market_data)
        news_context = self._format_news_context(news_data)
        
        # 시스템 프롬프트에 실시간 데이터 포함
        system_prompt = f"""당신은 전문적인 AI 투자 어드바이저입니다.
아래 실시간 시장 데이터와 최신 뉴스를 바탕으로 정확하고 실용적인 투자 분석을 제공해주세요.

=== 실시간 시장 데이터 ===
{market_context}

=== 최신 뉴스 ===
{news_context}

=== 분석 형식 ===
📊 **실시간 시장 분석**
[현재 시장 상황 분석]

💡 **투자 기회**  
[실시간 데이터 기반 투자 포인트]

⚠️ **리스크 요인**
[현재 시장 리스크]

📈 **실행 전략**
[구체적 투자 실행 방안]

🕐 **타이밍 분석**
[현재 시점 기준 매매 타이밍]

위 실시간 정보를 적극 활용하여 현재 시점에 최적화된 투자 분석을 제공해주세요."""

        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            url = f"{self.base_url}/testapp/v1/chat-completions/HCX-003"
            
            payload = {
                'messages': [
                    {
                        'role': 'system',
                        'content': system_prompt
                    },
                    {
                        'role': 'user', 
                        'content': f"현재 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n질문: {question}"
                    }
                ],
                'topP': 0.8,
                'topK': 0,
                'maxTokens': 2000,
                'temperature': 0.2,  # 정확한 분석을 위해 낮은 temperature
                'repeatPenalty': 1.2,
                'stopBefore': [],
                'includeAiFilters': True,
                'seed': 0
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                
                # 응답 파싱
                if 'result' in result:
                    if 'message' in result['result']:
                        content = result['result']['message'].get('content', '')
                    elif 'messages' in result['result'] and len(result['result']['messages']) > 0:
                        content = result['result']['messages'][0].get('content', '')
                    else:
                        content = str(result['result'])
                    
                    if content:
                        return f"🤖 **HyperCLOVA X 실시간 분석** ({datetime.now().strftime('%H:%M:%S')})\n\n{content}"
                    else:
                        raise Exception("AI 응답이 비어있습니다.")
                else:
                    raise Exception(f"응답 형식 오류: {result}")
                    
            elif response.status_code == 401:
                raise Exception("API 키 인증 실패: 네이버 클라우드 플랫폼에서 API 키를 다시 확인해주세요")
            elif response.status_code == 403:
                raise Exception("API 접근 권한 없음: CLOVA Studio에서 테스트 앱이 생성되었는지 확인해주세요")
            elif response.status_code == 429:
                raise Exception("API 사용량 한도 초과: 잠시 후 다시 시도해주세요")
            elif response.status_code == 400:
                error_detail = response.json() if response.content else "잘못된 요청"
                raise Exception(f"요청 오류: {error_detail}")
            else:
                raise Exception(f"API 호출 실패 (HTTP {response.status_code}): {response.text[:200]}")
                
        except requests.exceptions.ConnectTimeout:
            raise Exception("네트워크 연결 시간 초과: 인터넷 연결을 확인하고 다시 시도해주세요")
        except requests.exceptions.ConnectionError:
            raise Exception("네트워크 연결 오류: 인터넷 연결 상태를 확인해주세요")
        except Exception as e:
            # 모든 오류를 상위로 전파
            raise e
    
    def _format_market_context(self, market_data: dict) -> str:
        """시장 데이터를 컨텍스트 형식으로 변환"""
        if not market_data:
            return "시장 데이터를 불러올 수 없습니다."
        
        context = []
        for name, data in market_data.items():
            change_symbol = "📈" if data['change'] >= 0 else "📉"
            context.append(f"{change_symbol} {name}: {data['current']:.2f} ({data['change']:+.2f}%)")
        
        return "\n".join(context)
    
    def _format_news_context(self, news_data: list) -> str:
        """뉴스 데이터를 컨텍스트 형식으로 변환"""
        if not news_data:
            return "최신 뉴스를 불러올 수 없습니다."
        
        context = []
        for i, article in enumerate(news_data[:3], 1):
            context.append(f"{i}. {article['title']}")
            if article.get('summary'):
                context.append(f"   요약: {article['summary'][:100]}...")
        
        return "\n".join(context)

# 주식 데이터 수집
@st.cache_data(ttl=300)
def get_stock_data(ticker: str):
    """주식 데이터 수집"""
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period="6mo")
        if data.empty:
            raise ValueError(f"'{ticker}' 데이터를 찾을 수 없습니다.")
        return data
    except Exception as e:
        st.error(f"주식 데이터 오류: {str(e)}")
        return None

# 차트 생성 함수
def create_stock_chart(data, ticker):
    """주식 차트 생성"""
    fig = go.Figure(data=go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name=ticker
    ))
    
    fig.update_layout(
        title=f"{ticker} 주가 차트 (6개월)",
        yaxis_title="Price",
        xaxis_title="Date",
        template="plotly_white"
    )
    
    return fig

# 메인 애플리케이션
def main():
    # CSS 로드
    load_css()
    
    # 헤더
    st.markdown('<div class="main-header">🤖 HyperCLOVA X AI 투자 어드바이저</div>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666; font-size: 1.1rem;">🔴 실시간 분석 전용 - Live Market Data</p>', unsafe_allow_html=True)
    
    # 클라이언트 초기화
    ai_client = HyperCLOVAXClient()
    
    # 실시간 데이터 로드
    with st.spinner("📊 실시간 시장 데이터 로딩 중..."):
        market_data = get_real_time_market_data()
        news_data = get_recent_news()
    
    # 사이드바
    with st.sidebar:
        st.header("🏆 AI Festival 2025")
        
        # API 상태
        if ai_client.api_key:
            st.markdown('<div class="status-good">🔴 LIVE - HyperCLOVA X 연결됨</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-bad">❌ API 키 미설정</div>', unsafe_allow_html=True)
            st.error("⚠️ API 키를 설정해야 실시간 분석이 가능합니다!")
        
        st.markdown("---")
        
        # 실시간 시장 현황
        st.markdown("### 📊 실시간 시장 현황")
        if market_data:
            for name, data in market_data.items():
                change_color = "🟢" if data['change'] >= 0 else "🔴"
                st.metric(
                    name,
                    f"{data['current']:.2f}",
                    f"{data['change']:+.2f}%",
                    delta_color="normal"
                )
        else:
            st.info("시장 데이터 로딩 중...")
        
        st.markdown("---")
        
        # 인기 질문 (실시간 분석 중심)
        st.markdown("### 💡 실시간 분석 질문")
        popular_questions = [
            "현재 시장 상황 분석",
            "오늘 매매 타이밍은?", 
            "지금 주목해야 할 섹터",
            "실시간 리스크 요인"
        ]
        
        for question in popular_questions:
            if st.button(question, key=f"sidebar_{question}", use_container_width=True):
                st.session_state.selected_question = question
                st.rerun()
        
        st.markdown("---")
        st.caption(f"🔴 실시간 업데이트: {datetime.now().strftime('%H:%M:%S')}")
    
    # 메인 입력 영역
    st.markdown("### 💬 실시간 투자 분석 요청")
    
    # 세션 상태 초기화
    if 'user_question' not in st.session_state:
        st.session_state.user_question = ""
    if 'selected_question' not in st.session_state:
        st.session_state.selected_question = ""
    
    # 선택된 질문이 있으면 업데이트
    if st.session_state.selected_question:
        st.session_state.user_question = st.session_state.selected_question
        st.session_state.selected_question = ""
    
    # 실시간 데이터 표시
    if market_data or news_data:
        with st.expander("📊 현재 사용 중인 실시간 데이터", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**시장 지수**")
                for name, data in market_data.items():
                    st.write(f"• {name}: {data['current']:.2f} ({data['change']:+.2f}%)")
            
            with col2:
                st.markdown("**최신 뉴스**")
                for i, article in enumerate(news_data[:3], 1):
                    st.write(f"• {article['title'][:50]}...")
    
    # 질문 입력
    user_question = st.text_area(
        "",
        value=st.session_state.user_question,
        placeholder="예: 현재 시장 상황을 보면 삼성전자 매수 타이밍이 맞나요?",
        height=100,
        label_visibility="collapsed",
        key="question_input"
    )
    
    # 질문이 변경되면 세션 상태 업데이트
    if user_question != st.session_state.user_question:
        st.session_state.user_question = user_question
    
    # 실시간 분석 버튼
    if st.button("🔴 실시간 AI 분석 시작", type="primary", use_container_width=True):
        if not ai_client.api_key:
            st.error("⚠️ API 키가 설정되지 않았습니다. .streamlit/secrets.toml 파일에 CLOVA_STUDIO_API_KEY를 설정해주세요.")
            st.stop()
            
        if st.session_state.user_question.strip():
            # 진행 표시
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                status_text.text("🔍 실시간 데이터 분석 중...")
                progress_bar.progress(20)
                
                status_text.text("🤖 HyperCLOVA X AI 분석 시작...")
                progress_bar.progress(40)
                
                status_text.text("📊 시장 데이터 통합 분석...")
                progress_bar.progress(60)
                
                # 실시간 AI 분석
                response = ai_client.get_real_time_analysis(
                    st.session_state.user_question, 
                    market_data, 
                    news_data
                )
                
                status_text.text("✅ 실시간 분석 완료!")
                progress_bar.progress(100)
                
                time.sleep(0.5)
                progress_bar.empty()
                status_text.empty()
                
                # 응답 표시
                st.markdown('<div class="ai-response">', unsafe_allow_html=True)
                st.markdown(response)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # 데이터 출처 표시
                st.info(f"📊 **분석 기준**: 실시간 시장 데이터 + 최신 뉴스 + HyperCLOVA X AI | 분석 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
            except Exception as e:
                progress_bar.empty()
                status_text.empty()
                
                # 오류 메시지 표시
                st.markdown('<div class="error-message">', unsafe_allow_html=True)
                st.markdown(f"🚨 **실시간 분석 오류**\n\n{str(e)}")
                st.markdown('</div>', unsafe_allow_html=True)
                
                # 해결 방법 제시
                st.markdown("### 🔧 문제 해결 방법")
                st.markdown("""
                1. **API 키 확인**: `.streamlit/secrets.toml` 파일에 올바른 API 키 설정
                2. **네트워크 확인**: 인터넷 연결 상태 점검
                3. **계정 상태**: 네이버 클라우드 플랫폼 계정 및 크레딧 확인
                4. **앱 설정**: CLOVA Studio에서 테스트 앱 생성 확인
                """)
        else:
            st.warning("💬 분석할 질문을 입력해주세요.")
    
    # 면책 조항 (강화)
    st.warning("⚠️ **실시간 투자 분석 주의사항**: 본 분석은 실시간 데이터를 바탕으로 한 AI 분석 결과이며, 투자 권유가 아닙니다. 실제 투자 결정은 충분한 검토와 전문가 상담 후 본인 책임하에 하시기 바랍니다.")

# 앱 실행
if __name__ == "__main__":
    main()
