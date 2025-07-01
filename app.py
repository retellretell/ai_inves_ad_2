"""
HyperCLOVA X 기반 AI 투자 어드바이저
미래에셋증권 AI Festival 2025 출품작
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
.ai-response {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 2rem;
    border-radius: 1rem;
    margin: 1rem 0;
    box-shadow: 0 8px 32px rgba(0,0,0,0.1);
}
.status-good {
    background: #4CAF50;
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 0.5rem;
    margin: 0.5rem 0;
}
.status-bad {
    background: #f44336;
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 0.5rem;
    margin: 0.5rem 0;
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

# HyperCLOVA X 클라이언트
class HyperCLOVAXClient:
    def __init__(self):
        self.api_key = get_api_key()
        self.endpoint = "https://clovastudio.stream.ntruss.com/testapp/v1/chat-completions/HCX-003"
        
    def get_response(self, question: str) -> str:
        """HyperCLOVA X API 호출"""
        if not self.api_key:
            return self._get_fallback_response(question)
        
        try:
            headers = {
                'X-NCP-CLOVASTUDIO-API-KEY': self.api_key,
                'X-NCP-APIGW-API-KEY': self.api_key,
                'Content-Type': 'application/json',
                'Accept': 'text/event-stream'
            }
            
            payload = {
                'messages': [
                    {
                        'role': 'system',
                        'content': '당신은 전문적인 투자 어드바이저입니다. 한국어로 정확하고 실용적인 투자 조언을 제공해주세요. 구체적인 데이터와 분석을 포함하여 답변해주세요.'
                    },
                    {
                        'role': 'user',
                        'content': question
                    }
                ],
                'topP': 0.8,
                'topK': 0,
                'maxTokens': 1000,
                'temperature': 0.5,
                'repeatPenalty': 1.2,
                'stopBefore': [],
                'includeAiFilters': True
            }
            
            response = requests.post(
                self.endpoint,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                # HyperCLOVA X 응답 파싱
                if 'result' in result and 'message' in result['result']:
                    content = result['result']['message'].get('content', '')
                    if content:
                        return f"🤖 **HyperCLOVA X 분석 결과**\n\n{content}"
                    else:
                        raise Exception("응답 내용이 비어있습니다.")
                else:
                    raise Exception("응답 형식이 올바르지 않습니다.")
            else:
                raise Exception(f"API 호출 실패: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"HyperCLOVA X API 오류: {str(e)}")
            return f"⚠️ **HyperCLOVA X 연결 오류**\n\n{str(e)}\n\n---\n\n{self._get_fallback_response(question)}"
    
    def _get_fallback_response(self, question: str) -> str:
        """API 실패 시 대체 응답"""
        if any(keyword in question.lower() for keyword in ["삼성", "samsung", "005930"]):
            return """
📊 **삼성전자 투자 분석** (대체 응답)

**🎯 투자 포인트**
• AI 반도체 수요 급증으로 HBM 시장 독점적 지위
• 메모리 반도체 업황 회복 기대
• 안정적인 배당 수익률 약 3%
• 글로벌 기술주 대비 상대적 저평가

**📈 기술적 분석**
• 현재가: 약 75,000원 수준
• 목표가: 85,000원 (+13%)
• 지지선: 70,000원
• 저항선: 80,000원

**⚠️ 리스크 요인**
• 중국 경제 둔화 영향
• 메모리 사이클 변동성
• 환율 리스크 (달러 강세)

**💡 투자 전략**
장기 관점에서 분할 매수 권장. 포트폴리오의 15-20% 적정 비중.

*⚠️ 본 분석은 참고용이며, 실제 투자 결정은 신중히 하시기 바랍니다.*
            """
        
        elif any(keyword in question.lower() for keyword in ["테슬라", "tesla", "tsla"]):
            return """
🚗 **테슬라 투자 분석** (대체 응답)

**⚡ 성장 동력**
• FSD(완전자율주행) 기술 선도
• 로보택시 사업 확장 기대
• 에너지 저장 사업 성장
• 글로벌 전기차 시장 확대

**📊 밸류에이션**
• 현재 PER: 60배+ (프리미엄)
• 성장률: 연 20-30% 기대
• 시장 지배력: 전기차 점유율 1위

**⚠️ 주요 리스크**
• 높은 밸류에이션 부담
• 중국 전기차 업체 경쟁 심화
• 일론 머스크 개인 리스크
• 자동차 경기 민감성

**💡 투자 의견**
고위험 고수익 성향 투자자에게 적합. 포트폴리오 5-10% 수준 권장.

*⚠️ 본 분석은 참고용이며, 실제 투자 결정은 신중히 하시기 바랍니다.*
            """
        
        else:
            return """
📊 **AI 투자 상담** (대체 응답)

**💡 기본 투자 원칙**

**1. 분산 투자**
• 여러 종목, 섹터에 분산
• 지역별 분산 (국내/해외)
• 시간 분산 (적립식 투자)

**2. 장기 투자**
• 최소 3-5년 이상 관점
• 복리 효과 활용
• 단기 변동성 극복

**3. 리스크 관리**
• 비상금 6개월분 확보
• 위험 허용도 파악
• 정기적 포트폴리오 점검

**🎯 현재 시장 환경**
• AI 기술 발전으로 관련 주식 주목
• 금리 변동에 따른 섹터 로테이션
• ESG 투자 트렌드 지속

더 구체적인 종목이나 전략에 대해 질문해주세요!

*⚠️ 본 내용은 일반적인 정보이며, 개별 투자 권유가 아닙니다.*
            """

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

# 뉴스 데이터 수집
@st.cache_data(ttl=1800)
def get_news_data():
    """뉴스 데이터 수집"""
    try:
        rss_urls = [
            'https://feeds.finance.yahoo.com/rss/2.0/headline',
            'https://feeds.reuters.com/reuters/businessNews'
        ]
        
        articles = []
        for url in rss_urls:
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries[:3]:
                    articles.append({
                        'title': entry.get('title', ''),
                        'summary': entry.get('summary', ''),
                        'link': entry.get('link', ''),
                        'published': entry.get('published', ''),
                        'source': feed.feed.get('title', 'RSS')
                    })
            except:
                continue
        
        return articles[:5]
    except:
        return []

# 메인 애플리케이션
def main():
    # 헤더
    st.markdown('<div class="main-header">🤖 HyperCLOVA X AI 투자 어드바이저</div>', unsafe_allow_html=True)
    
    # 클라이언트 초기화
    ai_client = HyperCLOVAXClient()
    
    # 사이드바
    with st.sidebar:
        st.header("🏆 AI Festival 2025")
        
        # API 상태
        api_status = "연결됨" if ai_client.api_key else "미설정"
        if ai_client.api_key:
            st.markdown('<div class="status-good">✅ HyperCLOVA X 연결됨</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-bad">❌ API 키 미설정</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # 인기 질문
        st.markdown("### 💡 인기 질문")
        popular_questions = [
            "삼성전자 투자 전망",
            "테슬라 주식 분석", 
            "AI 포트폴리오 구성",
            "초보자 투자 전략"
        ]
        
        for question in popular_questions:
            if st.button(question, key=f"sidebar_{question}", use_container_width=True):
                st.session_state.selected_question = question
                st.rerun()
        
        st.markdown("---")
        st.caption("🕐 실시간 업데이트")
        st.caption(f"마지막 업데이트: {datetime.now().strftime('%H:%M:%S')}")
    
    # 메인 입력 영역
    st.markdown("### 💬 투자 질문하기")
    
    # 세션 상태 초기화
    if 'user_question' not in st.session_state:
        st.session_state.user_question = ""
    if 'selected_question' not in st.session_state:
        st.session_state.selected_question = ""
    
    # 선택된 질문이 있으면 업데이트
    if st.session_state.selected_question:
        st.session_state.user_question = st.session_state.selected_question
        st.session_state.selected_question = ""  # 초기화
    
    # 질문 입력
    user_question = st.text_area(
        "",
        value=st.session_state.user_question,
        placeholder="예: 삼성전자 주식 투자 전망을 HyperCLOVA X로 분석해주세요",
        height=100,
        label_visibility="collapsed",
        key="question_input"
    )
    
    # 질문이 변경되면 세션 상태 업데이트
    if user_question != st.session_state.user_question:
        st.session_state.user_question = user_question
    
    # 분석 버튼
    if st.button("🤖 AI 분석 시작", type="primary", use_container_width=True):
        if st.session_state.user_question.strip():
            # 진행 표시
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("🔍 HyperCLOVA X가 분석을 시작합니다...")
            progress_bar.progress(25)
            
            # AI 응답 생성
            with st.spinner("🤖 HyperCLOVA X가 전문 분석을 수행하고 있습니다..."):
                status_text.text("🧠 데이터 분석 중...")
                progress_bar.progress(50)
                
                time.sleep(1)  # 사용자 경험을 위한 딜레이
                
                status_text.text("📊 투자 인사이트 생성 중...")
                progress_bar.progress(75)
                
                response = ai_client.get_response(st.session_state.user_question)
                
                status_text.text("✅ 분석 완료!")
                progress_bar.progress(100)
                
                time.sleep(0.5)
                progress_bar.empty()
                status_text.empty()
            
            # 응답 표시
            st.markdown('<div class="ai-response">', unsafe_allow_html=True)
            st.markdown(response)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # 추가 정보 제공
            col1, col2 = st.columns(2)
            
            with col1:
                # 관련 뉴스
                st.markdown("### 📰 관련 뉴스")
                news_articles = get_news_data()
                
                if news_articles:
                    for article in news_articles[:3]:
                        with st.expander(f"📄 {article['title'][:50]}..."):
                            st.write(article['summary'][:200] + "...")
                            if article['link']:
                                st.markdown(f"[전체 기사 읽기]({article['link']})")
                            st.caption(f"출처: {article['source']}")
                else:
                    st.info("뉴스 데이터를 불러오는 중입니다...")
            
            with col2:
                # 주식 데이터 (질문에 종목이 포함된 경우)
                if any(keyword in st.session_state.user_question.lower() for keyword in ["삼성", "테슬라", "애플"]):
                    st.markdown("### 📊 주가 정보")
                    
                    # 종목 매핑
                    ticker_map = {
                        "삼성": "005930.KS",
                        "테슬라": "TSLA", 
                        "애플": "AAPL"
                    }
                    
                    for keyword, ticker in ticker_map.items():
                        if keyword in st.session_state.user_question.lower():
                            stock_data = get_stock_data(ticker)
                            if stock_data is not None:
                                current_price = stock_data['Close'].iloc[-1]
                                prev_price = stock_data['Close'].iloc[-2]
                                change = current_price - prev_price
                                change_pct = (change / prev_price) * 100
                                
                                st.metric(
                                    f"{keyword.title()} 현재가",
                                    f"${current_price:.2f}" if ticker != "005930.KS" else f"₩{current_price:,.0f}",
                                    f"{change:+.2f} ({change_pct:+.2f}%)"
                                )
                            break
            
            # 면책 조항
            st.warning("⚠️ **투자 주의사항**: 본 AI 분석은 참고용 정보이며, 실제 투자 결정은 충분한 검토 후 본인 책임하에 하시기 바랍니다.")
            
        else:
            st.warning("💬 질문을 입력해주세요.")
    
    # 샘플 질문 (메인 영역)
    if not st.session_state.user_question:
        st.markdown("### 💡 샘플 질문")
        
        sample_questions = [
            "삼성전자 주식 투자 전망을 분석해주세요",
            "테슬라 주식의 장단점을 알려주세요", 
            "AI 관련 주식 투자 전략은?",
            "초보자를 위한 안전한 투자 방법",
            "현재 시장에서 주목해야 할 섹터는?",
            "ESG 투자의 장단점은 무엇인가요?"
        ]
        
        cols = st.columns(2)
        for i, question in enumerate(sample_questions):
            with cols[i % 2]:
                if st.button(question, key=f"main_sample_{i}"):
                    st.session_state.selected_question = question
                    st.rerun()

# 앱 실행
if __name__ == "__main__":
    main()
