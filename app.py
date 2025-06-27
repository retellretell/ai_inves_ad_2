"""
HyperCLOVA X 기반 AI 투자 어드바이저
Streamlit Cloud 배포용 버전
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import requests
import random
import feedparser
from datetime import datetime, timedelta
import json

# 페이지 설정
st.set_page_config(
    page_title="HyperCLOVA X 기반 AI 투자 어드바이저",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API 키 설정 (Streamlit Secrets에서 읽기)
def get_api_key():
    """Streamlit Secrets에서 API 키 가져오기"""
    try:
        return st.secrets["OPENAI_API_KEY"]
    except:
        return None

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
.metric-card {
    background-color: #ffffff;
    padding: 1rem;
    border-radius: 0.5rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    border: 1px solid #e0e0e0;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# AI API 클라이언트 클래스
class AIClient:
    def __init__(self):
        self.api_key = get_api_key()
        self.api_url = "https://api.openai.com/v1/chat/completions"
    
    def get_response(self, question: str) -> str:
        """AI 응답 생성"""
        if not self.api_key:
            return self._get_mock_response(question)
        
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': 'gpt-3.5-turbo',
                'messages': [
                    {
                        'role': 'system',
                        'content': '당신은 전문적인 투자 어드바이저입니다. 한국어로 정확하고 유용한 투자 정보를 제공해주세요. 답변은 구체적이고 실용적으로 해주세요.'
                    },
                    {
                        'role': 'user',
                        'content': question
                    }
                ],
                'max_tokens': 1500,
                'temperature': 0.3
            }
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                return f"❌ API 호출 오류: {response.status_code}. 잠시 후 다시 시도해주세요."
                
        except Exception as e:
            return f"❌ 오류가 발생했습니다: {str(e)}"
    
    def _get_mock_response(self, question: str) -> str:
        """API 키가 없을 때 모의 응답"""
        mock_responses = {
            "삼성전자": """
📊 **삼성전자 투자 분석**

**✅ 긍정적 요인:**
• 메모리 반도체 업황 회복 신호
• AI 반도체 수요 증가로 수혜 예상
• 안정적인 배당 수익률 (약 2-3%)
• 글로벌 기술주 대비 저평가 상태

**⚠️ 주의할 점:**
• 중국 경제 둔화 영향
• 반도체 사이클의 변동성
• 환율 변동 리스크

**💡 투자 의견:**
중장기 관점에서 매력적인 투자처로 판단됩니다. 
적립식 투자를 통한 분할 매수를 권장드립니다.

*⚠️ 본 분석은 참고용이며, 실제 투자 결정은 신중히 하시기 바랍니다.*
            """,
            
            "테슬라": """
📊 **테슬라 투자 분석**

**✅ 성장 동력:**
• 전기차 시장 선도 기업 지위
• 자율주행 기술 발전
• 에너지 저장 사업 확장
• 슈퍼차저 네트워크 경쟁 우위

**⚠️ 리스크 요인:**
• 높은 밸류에이션 (PER 60배 이상)
• 중국 전기차 업체들과의 경쟁 심화
• 일론 머스크 개인 리스크

**💡 투자 의견:**
고위험 고수익을 추구하는 성장주 투자자에게 적합합니다.
전체 포트폴리오의 5-10% 수준에서 고려해보세요.

*⚠️ 본 분석은 참고용이며, 실제 투자 결정은 신중히 하시기 바랍니다.*
            """,
            
            "default": """
📊 **투자 가이드**

**💡 기본 투자 원칙:**

**1. 분산 투자**
• 여러 종목, 섹터에 분산
• 지역별 분산 (국내/해외)
• 시간 분산 (적립식 투자)

**2. 장기 투자**
• 최소 3-5년 이상 투자 관점
• 단기 변동성에 흔들리지 않기
• 복리 효과 활용

**3. 리스크 관리**
• 생활비 6개월분 비상금 확보
• 투자 금액은 여유 자금으로만
• 본인의 위험 허용도 파악

**4. 지속적인 학습**
• 기업 분석 능력 향상
• 경제 흐름 이해
• 투자 심리 관리

*⚠️ 본 내용은 일반적인 정보 제공 목적이며, 개별 투자 권유가 아닙니다.*
            """
        }
        
        question_lower = question.lower()
        if any(keyword in question for keyword in ["삼성", "samsung", "005930"]):
            return mock_responses["삼성전자"]
        elif any(keyword in question_lower for keyword in ["테슬라", "tesla", "tsla"]):
            return mock_responses["테슬라"]
        else:
            return mock_responses["default"]

# 주식 데이터 클래스
class StockData:
    def __init__(self):
        # 주요 주식 종목 데이터 (실시간 데이터 시뮬레이션)
        self.stocks = {
            'AAPL': {'name': '애플', 'price': 175.23, 'change': 2.45, 'volume': 45000000},
            'GOOGL': {'name': '구글', 'price': 140.67, 'change': -1.23, 'volume': 28000000},
            'MSFT': {'name': '마이크로소프트', 'price': 378.91, 'change': 4.56, 'volume': 32000000},
            'TSLA': {'name': '테슬라', 'price': 248.48, 'change': -3.21, 'volume': 95000000},
            'NVDA': {'name': '엔비디아', 'price': 456.78, 'change': 12.34, 'volume': 67000000},
            '005930.KS': {'name': '삼성전자', 'price': 75000, 'change': 1000, 'volume': 12000000},
            '000660.KS': {'name': 'SK하이닉스', 'price': 128000, 'change': -2000, 'volume': 8500000}
        }
    
    def get_stock_info(self, symbol):
        """주식 정보 반환"""
        if symbol in self.stocks:
            stock = self.stocks[symbol].copy()
            # 실시간 가격 변동 시뮬레이션
            change_pct = random.uniform(-2, 2)
            stock['price'] *= (1 + change_pct/100)
            stock['change'] += stock['price'] * (change_pct/100)
            return stock
        return None
    
    def generate_chart_data(self, symbol, days=30):
        """차트 데이터 생성"""
        if symbol not in self.stocks:
            return None
        
        base_price = self.stocks[symbol]['price']
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        prices = []
        volumes = []
        
        current_price = base_price * 0.9  # 시작 가격
        
        for _ in range(days):
            # 가격 변동
            change = random.uniform(-0.05, 0.05)
            current_price *= (1 + change)
            prices.append(current_price)
            
            # 거래량 변동
            base_volume = self.stocks[symbol]['volume']
            volume = base_volume * random.uniform(0.5, 1.5)
            volumes.append(int(volume))
        
        return pd.DataFrame({
            'Date': dates,
            'Price': prices,
            'Volume': volumes
        })

# 뉴스 데이터 클래스
class NewsData:
    def __init__(self):
        pass
    
    def get_financial_news(self, limit=10):
        """금융 뉴스 가져오기"""
        try:
            # Reuters 비즈니스 뉴스 RSS
            rss_urls = [
                'https://feeds.reuters.com/reuters/businessNews',
                'https://feeds.finance.yahoo.com/rss/2.0/headline'
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
                            'published': entry.get('published', ''),
                            'source': feed.feed.get('title', 'RSS Feed')
                        })
                except:
                    continue
            
            return articles[:limit]
        
        except:
            return self._get_sample_news()
    
    def _get_sample_news(self):
        """샘플 뉴스 데이터"""
        return [
            {
                'title': '미국 증시, 기술주 강세로 상승 마감',
                'description': 'AI 관련 기술주들이 강세를 보이며 나스닥이 1.2% 상승했습니다.',
                'url': '#',
                'published': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'source': '샘플 뉴스'
            },
            {
                'title': '연준, 금리 동결 신호 지속',
                'description': '연방준비제도가 현재 금리 수준을 당분간 유지할 것으로 전망됩니다.',
                'url': '#',
                'published': (datetime.now() - timedelta(hours=2)).strftime('%Y-%m-%d %H:%M'),
                'source': '샘플 뉴스'
            }
        ]

# 메인 애플리케이션
def main():
    # 헤더
    st.markdown('<div class="main-header">📈 HyperCLOVA X 기반 AI 투자 어드바이저</div>', unsafe_allow_html=True)
    
    # 클라이언트 초기화
    ai_client = AIClient()
    stock_data = StockData()
    news_data = NewsData()
    
    # 사이드바
    with st.sidebar:
        st.header("⚙️ 시스템 상태")
        
        # API 상태 확인
        api_status = "✅ 연결됨" if ai_client.api_key else "❌ 미설정"
        st.write(f"**OpenAI API:** {api_status}")
        
        if not ai_client.api_key:
            st.warning("⚠️ API 키가 설정되지 않았습니다.")
            st.info("""
            **Streamlit Cloud 설정 방법:**
            1. 앱 설정(⚙️) → Secrets 탭
            2. 다음 내용 추가:
            ```
            OPENAI_API_KEY = "your-api-key"
            ```
            """)
        else:
            st.success("🚀 AI 상담 서비스 이용 가능!")
        
        st.markdown("---")
        
        # 실시간 시계
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.caption(f"🕐 현재 시간: {current_time}")
        
        # 시장 상태
        now = datetime.now()
        if 9 <= now.hour < 16:
            st.success("🟢 미국 시장 개장 중")
        else:
            st.info("🔴 미국 시장 마감")
    
    # 메인 탭
    tab1, tab2, tab3, tab4 = st.tabs(["💬 AI 투자 상담", "📊 주식 분석", "📰 금융 뉴스", "💼 포트폴리오"])
    
    # 탭 1: AI 투자 상담
    with tab1:
        st.markdown('<div class="section-header">AI 투자 상담</div>', unsafe_allow_html=True)
        
        # 질문 입력
        user_question = st.text_area(
            "💭 투자 관련 질문을 입력하세요:",
            placeholder="예: 삼성전자 주식 어떻게 생각하세요? 또는 초보자 투자 전략을 알려주세요.",
            height=120
        )
        
        # 상담 버튼
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("🤖 AI 상담 시작", type="primary", use_container_width=True):
                if user_question.strip():
                    with st.spinner("AI 투자 어드바이저가 분석 중입니다..."):
                        # AI 응답 생성
                        response = ai_client.get_response(user_question)
                        
                        # 응답 표시
                        st.markdown("---")
                        st.markdown("### 🤖 AI 투자 어드바이저 답변")
                        st.markdown('<div class="info-box">', unsafe_allow_html=True)
                        st.markdown(response)
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        if not ai_client.api_key:
                            st.info("💡 **실제 AI 답변을 받으려면** 왼쪽 사이드바의 안내에 따라 API 키를 설정하세요!")
                        
                        st.warning("⚠️ **투자 주의사항:** 본 내용은 참고용이며, 실제 투자 결정은 충분한 검토 후 신중히 하시기 바랍니다.")
                else:
                    st.warning("⚠️ 뉴스를 불러올 수 없습니다. 잠시 후 다시 시도해주세요.")
                    
        except Exception as e:
            st.error(f"❌ 뉴스 로딩 중 오류: {str(e)}")
    
    # 탭 4: 포트폴리오
    with tab4:
        st.markdown('<div class="section-header">포트폴리오 시뮬레이션</div>', unsafe_allow_html=True)
        
        st.markdown("**💼 나만의 포트폴리오를 구성해보세요**")
        
        # 포트폴리오 종목 선택
        available_stocks = list(stock_data.stocks.keys())
        selected_stocks = st.multiselect(
            "포트폴리오에 포함할 종목을 선택하세요:",
            available_stocks,
            default=available_stocks[:4],
            format_func=lambda x: f"{stock_data.stocks[x]['name']} ({x})"
        )
        
        if selected_stocks:
            st.markdown("### 📊 종목별 비중 설정")
            
            # 비중 설정
            weights = {}
            total_weight = 0
            
            cols = st.columns(len(selected_stocks))
            for i, stock in enumerate(selected_stocks):
                with cols[i]:
                    weight = st.slider(
                        f"{stock_data.stocks[stock]['name']}",
                        min_value=0,
                        max_value=100,
                        value=100//len(selected_stocks),
                        step=5,
                        key=f"weight_{stock}"
                    )
                    weights[stock] = weight
                    total_weight += weight
            
            # 비중 검증
            st.markdown("---")
            if abs(total_weight - 100) <= 5:
                st.success(f"✅ 총 비중: {total_weight}% (포트폴리오 구성 완료)")
                
                # 포트폴리오 차트
                if st.button("📊 포트폴리오 분석", type="primary"):
                    # 파이 차트
                    labels = [f"{stock_data.stocks[stock]['name']}\n({weight}%)" 
                             for stock, weight in weights.items() if weight > 0]
                    values = [weight for weight in weights.values() if weight > 0]
                    
                    fig_portfolio = go.Figure(data=[go.Pie(
                        labels=labels,
                        values=values,
                        hole=0.4,
                        textinfo='label+percent',
                        textposition='outside'
                    )])
                    
                    fig_portfolio.update_layout(
                        title="💼 포트폴리오 구성",
                        height=500,
                        showlegend=True
                    )
                    
                    st.plotly_chart(fig_portfolio, use_container_width=True)
                    
                    # 포트폴리오 성과 요약
                    st.markdown("### 📈 포트폴리오 요약")
                    
                    total_value = 0
                    total_change = 0
                    
                    portfolio_data = []
                    for stock, weight in weights.items():
                        if weight > 0:
                            info = stock_data.get_stock_info(stock)
                            value_contribution = (weight / 100) * info['price']
                            change_contribution = (weight / 100) * info['change']
                            total_value += value_contribution
                            total_change += change_contribution
                            
                            portfolio_data.append({
                                '종목': info['name'],
                                '비중': f"{weight}%",
                                '현재가': f"${info['price']:.2f}" if 'KS' not in stock else f"₩{info['price']:,.0f}",
                                '등락': f"{info['change']:+.2f}" if 'KS' not in stock else f"{info['change']:+,.0f}",
                                '기여도': f"{change_contribution:+.3f}"
                            })
                    
                    # 포트폴리오 테이블
                    df_portfolio = pd.DataFrame(portfolio_data)
                    st.dataframe(df_portfolio, use_container_width=True, hide_index=True)
                    
                    # 포트폴리오 전체 성과
                    portfolio_change_pct = (total_change / total_value) * 100 if total_value > 0 else 0
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("포트폴리오 변동", f"{total_change:+.2f}")
                    with col2:
                        st.metric("수익률", f"{portfolio_change_pct:+.2f}%")
                    with col3:
                        risk_level = "높음" if abs(portfolio_change_pct) > 3 else "중간" if abs(portfolio_change_pct) > 1 else "낮음"
                        st.metric("위험도", risk_level)
                    
                    # 투자 조언
                    st.markdown("### 💡 포트폴리오 조언")
                    if portfolio_change_pct > 2:
                        st.success("✅ 우수한 성과를 보이고 있습니다. 장기 보유를 고려해보세요.")
                    elif portfolio_change_pct < -2:
                        st.warning("⚠️ 단기적으로 부진합니다. 장기적 관점에서 접근하세요.")
                    else:
                        st.info("📊 안정적인 수익률을 보이고 있습니다.")
                    
            else:
                st.error(f"❌ 총 비중이 {total_weight}%입니다. 100%에 맞춰주세요.")
        
        else:
            st.info("💡 종목을 선택하여 포트폴리오를 구성해보세요.")
        
        # 투자 가이드
        with st.expander("📚 포트폴리오 구성 가이드"):
            st.markdown("""
            ### 💡 효과적인 포트폴리오 구성 방법
            
            **1. 분산 투자 원칙**
            - 서로 다른 섹터의 종목으로 구성
            - 지역별 분산 (미국, 한국, 기타)
            - 성장주와 가치주의 균형
            
            **2. 리스크 관리**
            - 한 종목에 30% 이상 집중 지양
            - 변동성이 큰 종목은 비중 조절
            - 정기적인 리밸런싱 실시
            
            **3. 투자 성향별 권장 비중**
            - **보수적**: 대형주 70% + 안전자산 30%
            - **중도적**: 대형주 50% + 중소형주 30% + 안전자산 20%
            - **공격적**: 성장주 60% + 중소형주 30% + 테마주 10%
            
            **⚠️ 주의사항**: 본 시뮬레이션은 교육 목적이며, 실제 투자는 충분한 검토 후 결정하세요.
            """)

# 푸터
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 2rem; background-color: #f8f9fa; border-radius: 10px; margin-top: 2rem;'>
    <h4 style='color: #2c3e50; margin-bottom: 1rem;'>📈 HyperCLOVA X 기반 AI 투자 어드바이저</h4>
    <p style='color: #666; margin-bottom: 0.5rem;'>
        <strong>🤖 AI 기술:</strong> OpenAI GPT-3.5 Turbo | 
        <strong>📊 데이터:</strong> 실시간 시뮬레이션 | 
        <strong>📰 뉴스:</strong> RSS 피드
    </p>
    <p style='color: #e74c3c; font-weight: bold; margin: 0;'>
        ⚠️ 본 서비스는 투자 참고용이며, 실제 투자 결정은 신중히 하시기 바랍니다.
    </p>
</div>
""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()❗ 질문을 입력해주세요.")
        
        # 빠른 질문 버튼들
        st.markdown("---")
        st.markdown("### 💡 빠른 질문")
        
        quick_questions = [
            "삼성전자 주식 전망은?",
            "테슬라 투자 어떻게 생각하세요?",
            "초보자 투자 전략 알려주세요",
            "ESG 투자가 뭔가요?",
            "지금 금리 상황에서 어떻게 투자해야 할까요?",
            "반도체 주식 전망은?"
        ]
        
        cols = st.columns(3)
        for i, question in enumerate(quick_questions):
            with cols[i % 3]:
                if st.button(question, key=f"quick_q_{i}", use_container_width=True):
                    # 세션 상태에 질문 저장
                    st.session_state.quick_question = question
                    st.rerun()
        
        # 빠른 질문이 선택되었을 때 처리
        if hasattr(st.session_state, 'quick_question'):
            selected_question = st.session_state.quick_question
            st.text_area("💭 투자 관련 질문을 입력하세요:", value=selected_question, key="filled_question")
            del st.session_state.quick_question
    
    # 탭 2: 주식 분석
    with tab2:
        st.markdown('<div class="section-header">주식 시장 분석</div>', unsafe_allow_html=True)
        
        # 종목 선택
        col1, col2 = st.columns([2, 1])
        with col1:
            selected_symbol = st.selectbox(
                "📈 분석할 종목을 선택하세요:",
                list(stock_data.stocks.keys()),
                format_func=lambda x: f"{stock_data.stocks[x]['name']} ({x})"
            )
        
        with col2:
            chart_period = st.selectbox("📅 차트 기간:", [7, 14, 30, 60], index=2)
        
        if selected_symbol:
            stock_info = stock_data.get_stock_info(selected_symbol)
            
            if stock_info:
                # 주식 정보 카드
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4>{stock_info['name']}</h4>
                        <p style="color: #666; margin: 0;">{selected_symbol}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    price = stock_info['price']
                    change = stock_info['change']
                    change_pct = (change / price) * 100
                    color = "#4CAF50" if change > 0 else "#F44336" if change < 0 else "#666"
                    
                    if 'KS' in selected_symbol:
                        price_str = f"₩{price:,.0f}"
                        change_str = f"{change:+,.0f}원 ({change_pct:+.2f}%)"
                    else:
                        price_str = f"${price:.2f}"
                        change_str = f"${change:+.2f} ({change_pct:+.2f}%)"
                    
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4>현재가</h4>
                        <h3 style="margin: 5px 0;">{price_str}</h3>
                        <p style="color: {color}; margin: 0; font-weight: bold;">{change_str}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    volume_str = f"{stock_info['volume']:,}"
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4>거래량</h4>
                        <h3 style="margin: 5px 0;">{volume_str}</h3>
                        <p style="color: #666; margin: 0;">주</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    trend = "상승" if change > 0 else "하락" if change < 0 else "보합"
                    trend_emoji = "📈" if change > 0 else "📉" if change < 0 else "➡️"
                    trend_color = "#4CAF50" if change > 0 else "#F44336" if change < 0 else "#666"
                    
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4>추세</h4>
                        <h3 style="margin: 5px 0; color: {trend_color};">{trend_emoji}</h3>
                        <p style="color: {trend_color}; margin: 0; font-weight: bold;">{trend}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # 차트 생성
                st.markdown("---")
                chart_data = stock_data.generate_chart_data(selected_symbol, chart_period)
                
                if chart_data is not None:
                    # 가격 차트
                    fig_price = go.Figure()
                    fig_price.add_trace(go.Scatter(
                        x=chart_data['Date'],
                        y=chart_data['Price'],
                        mode='lines',
                        name='주가',
                        line=dict(color='#1f77b4', width=3),
                        hovertemplate='날짜: %{x}<br>가격: %{y:,.2f}<extra></extra>'
                    ))
                    
                    fig_price.update_layout(
                        title=f"📈 {stock_info['name']} 주가 차트 ({chart_period}일)",
                        xaxis_title="날짜",
                        yaxis_title="가격",
                        height=400,
                        template="plotly_white",
                        hovermode='x'
                    )
                    
                    st.plotly_chart(fig_price, use_container_width=True)
                    
                    # 거래량 차트
                    fig_volume = go.Figure()
                    fig_volume.add_trace(go.Bar(
                        x=chart_data['Date'],
                        y=chart_data['Volume'],
                        name='거래량',
                        marker_color='rgba(55, 128, 191, 0.7)',
                        hovertemplate='날짜: %{x}<br>거래량: %{y:,}<extra></extra>'
                    ))
                    
                    fig_volume.update_layout(
                        title=f"📊 {stock_info['name']} 거래량 차트 ({chart_period}일)",
                        xaxis_title="날짜",
                        yaxis_title="거래량",
                        height=300,
                        template="plotly_white",
                        hovermode='x'
                    )
                    
                    st.plotly_chart(fig_volume, use_container_width=True)
                    
                    # 기술적 분석 요약
                    st.markdown("### 📊 간단 분석")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**가격 동향:**")
                        avg_price = chart_data['Price'].mean()
                        current_vs_avg = ((stock_info['price'] - avg_price) / avg_price) * 100
                        
                        if current_vs_avg > 5:
                            st.success(f"✅ 평균 대비 {current_vs_avg:.1f}% 높음 (강세)")
                        elif current_vs_avg < -5:
                            st.error(f"❌ 평균 대비 {current_vs_avg:.1f}% 낮음 (약세)")
                        else:
                            st.info(f"⚡ 평균 대비 {current_vs_avg:.1f}% (횡보)")
                    
                    with col2:
                        st.markdown("**거래량 분석:**")
                        avg_volume = chart_data['Volume'].mean()
                        current_vs_avg_vol = ((stock_info['volume'] - avg_volume) / avg_volume) * 100
                        
                        if current_vs_avg_vol > 20:
                            st.success(f"📊 평균 대비 {current_vs_avg_vol:.1f}% 높음 (활발)")
                        elif current_vs_avg_vol < -20:
                            st.warning(f"📊 평균 대비 {current_vs_avg_vol:.1f}% 낮음 (한산)")
                        else:
                            st.info(f"📊 평균 대비 {current_vs_avg_vol:.1f}% (보통)")
                
                st.caption("⚠️ 위 데이터는 시연용 시뮬레이션 데이터입니다.")
    
    # 탭 3: 금융 뉴스
    with tab3:
        st.markdown('<div class="section-header">실시간 금융 뉴스</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("최신 금융 시장 뉴스를 확인하세요")
        with col2:
            if st.button("🔄 뉴스 새로고침", type="secondary"):
                st.rerun()
        
        # 뉴스 불러오기
        try:
            with st.spinner("📰 최신 뉴스를 불러오는 중..."):
                news_articles = news_data.get_financial_news(10)
                
                if news_articles:
                    st.success(f"✅ {len(news_articles)}개의 뉴스를 불러왔습니다")
                    
                    for i, article in enumerate(news_articles):
                        with st.expander(f"📄 {article['title']}", expanded=(i < 2)):
                            col1, col2 = st.columns([4, 1])
                            
                            with col1:
                                if article['description']:
                                    st.write(article['description'])
                                
                                if article['url'] and article['url'] != '#':
                                    st.markdown(f"[📖 전체 기사 읽기]({article['url']})")
                            
                            with col2:
                                st.caption(f"🏢 {article['source']}")
                                if article['published']:
                                    st.caption(f"🕐 {article['published']}")
                else:
                    st.warning("
