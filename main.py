"""
main.py - 메인 애플리케이션
"""

import streamlit as st
import time
from datetime import datetime

# 모듈 임포트
from config import setup_page_config, get_api_key, get_dart_api_key, get_naver_api_keys
from ui_styles import load_css, render_header, render_portfolio_info, render_error_message, render_disclaimer
from data_collector import get_real_time_market_data, get_recent_news, get_stock_data
from stock_mapper import AutoStockMapper
from portfolio_parser import parse_user_portfolio, calculate_portfolio_metrics
from ai_client import EnhancedHyperCLOVAXClient
from chart_utils import create_stock_chart, display_market_metrics, display_portfolio_summary

def initialize_session_state():
    """세션 상태 초기화"""
    if 'user_question' not in st.session_state:
        st.session_state.user_question = ""
    if 'selected_question' not in st.session_state:
        st.session_state.selected_question = ""

def render_sidebar(ai_client, market_data):
    """사이드바 렌더링"""
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
        display_market_metrics(market_data)
        
        st.markdown("---")
        
        # 개인화 질문 예시
        st.markdown("### 💡 개인화 분석 질문")
        personalized_questions = [
            "삼전 6만원에 100주 보유, 언제 팔까?",
            "테슬라 300달러에 50주, 추가 매수?", 
            "네이버 15만원에 200주, 손절해야 할까?",
            "현재 포트폴리오 리밸런싱 필요?"
        ]
        
        for question in personalized_questions:
            if st.button(question, key=f"sidebar_{question}", use_container_width=True):
                st.session_state.selected_question = question
                st.rerun()
        
        st.markdown("---")
        
        # 데이터 소스 상태
        st.markdown("### 📡 데이터 소스 상태")
        dart_key = get_dart_api_key()
        naver_id, naver_secret = get_naver_api_keys()
        
        st.caption(f"✅ 시장 데이터: 활성")
        st.caption(f"✅ 뉴스 피드: 활성")
        st.caption(f"{'✅' if dart_key else '⚠️'} DART 공시: {'활성' if dart_key else '비활성'}")
        st.caption(f"{'✅' if naver_id else '⚠️'} 네이버 트렌드: {'활성' if naver_id else '비활성'}")
        
        st.markdown("---")
        st.caption(f"🔄 실시간 업데이트: {datetime.now().strftime('%H:%M:%S')}")

def render_main_content(ai_client, market_data, news_data):
    """메인 콘텐츠 렌더링"""
    initialize_session_state()
    
    # 실시간 헤더
    current_time = datetime.now()
    render_header(current_time)
    
    # 메인 입력 영역
    st.markdown("### 💬 실시간 개인화 투자 분석")
    
    # 실시간 분석 안내
    st.info("""
    💡 **개인화 분석 팁**: 
    구체적인 보유 정보를 포함하면 더 정확한 맞춤 조언을 받을 수 있습니다.
    예: "삼성전자 70,000원에 100주 보유 중, 계속 들고 있어야 할까요?"
    """)
    
    # 실시간 데이터 표시
    if market_data or news_data:
        with st.expander("📊 현재 사용 중인 실시간 데이터", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**📈 시장 지수 (실시간)**")
                for name, data in list(market_data.items())[:4]:
                    collected_time = data.get('collected_at', '알 수 없음')
                    volume_info = f" | 거래량 비율: {data.get('volume_ratio', 0):.0f}%" if data.get('volume_ratio') else ""
                    st.markdown(f'<div class="data-timestamp">• {name}: {data["current"]:.2f} ({data["change"]:+.2f}%){volume_info}<br><small>수집: {collected_time}</small></div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown("**📰 최신 뉴스**")
                for i, article in enumerate(news_data[:4], 1):
                    collected_time = article.get('collected_at', '알 수 없음')
                    st.markdown(f'<div class="data-timestamp">• {article["title"][:50]}...<br><small>출처: {article["source"]} | 수집: {collected_time}</small></div>', unsafe_allow_html=True)
    
    # 선택된 질문이 있으면 업데이트
    if st.session_state.selected_question:
        st.session_state.user_question = st.session_state.selected_question
        st.session_state.selected_question = ""
    
    # 질문 입력
    user_question = st.text_area(
        "",
        value=st.session_state.user_question,
        placeholder="예: 삼성전자 70,000원에 100주 보유 중인데 계속 들고 있는 게 맞을까요? 현재 시장 상황도 함께 알려주세요.",
        height=120,
        label_visibility="collapsed",
        key="question_input"
    )
    
    # 질문이 변경되면 세션 상태 업데이트
    if user_question != st.session_state.user_question:
        st.session_state.user_question = user_question
    
    # 분석 버튼 및 처리
    render_analysis_section(ai_client, market_data, news_data)
    
    # 샘플 질문들
    render_sample_questions()

def render_analysis_section(ai_client, market_data, news_data):
    """분석 섹션 렌더링"""
    if st.button("🔴 개인화 실시간 AI 분석 시작", type="primary", use_container_width=True):
        if not ai_client.api_key:
            st.error("⚠️ API 키가 설정되지 않았습니다. .streamlit/secrets.toml 파일에 CLOVA_STUDIO_API_KEY를 설정해주세요.")
            st.stop()
            
        if st.session_state.user_question.strip():
            # 포트폴리오 정보 추출
            portfolio_info = parse_user_portfolio(st.session_state.user_question)
            
            # 포트폴리오 정보가 감지되면 표시
            render_portfolio_info(portfolio_info)
            
            # 진행 표시
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                status_text.text("🔍 포트폴리오 정보 분석 중...")
                progress_bar.progress(10)
                
                status_text.text("📊 실시간 시장 데이터 수집 중...")
                progress_bar.progress(25)
                
                status_text.text("📰 최신 뉴스 및 공시 정보 수집 중...")
                progress_bar.progress(40)
                
                status_text.text("🔍 검색 트렌드 및 경제 지표 분석 중...")
                progress_bar.progress(55)
                
                status_text.text("🤖 HyperCLOVA X 개인화 분석 시작...")
                progress_bar.progress(70)
                
                status_text.text("💡 맞춤형 투자 전략 생성 중...")
                progress_bar.progress(85)
                
                # AI 분석
                response = ai_client.get_personalized_analysis(
                    st.session_state.user_question, 
                    portfolio_info
                )
                
                status_text.text("✅ 개인화 분석 완료!")
                progress_bar.progress(100)
                
                time.sleep(0.5)
                progress_bar.empty()
                status_text.empty()
                
                # 응답 표시
                st.markdown('<div class="ai-response">', unsafe_allow_html=True)
                st.markdown(response)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # 분석 요약 정보
                render_analysis_summary(portfolio_info)
                
                # 추가 차트 표시 (포트폴리오 종목이 있는 경우)
                if portfolio_info and portfolio_info.get('ticker'):
                    render_portfolio_chart(portfolio_info)
                
            except Exception as e:
                progress_bar.empty()
                status_text.empty()
                render_error_message(str(e))
                render_troubleshooting_guide()
        else:
            st.warning("💬 분석할 질문을 입력해주세요.")

def render_analysis_summary(portfolio_info):
    """분석 요약 정보 렌더링"""
    analysis_time = datetime.now().strftime('%Y년 %m월 %d일 %H시 %M분 %S초')
    data_sources_count = 5  # 시장, 뉴스, 공시, 트렌드, 경제지표
    
    st.markdown(f"""
    <div class="data-timestamp">
        📊 <strong>분석 완료</strong>: {analysis_time}<br>
        🔄 <strong>데이터 소스</strong>: {data_sources_count}개 통합 (실시간 시장 + 뉴스 + 공시 + 트렌드 + 경제지표)<br>
        👤 <strong>개인화</strong>: {'포트폴리오 맞춤 분석' if portfolio_info else '일반 시장 분석'}<br>
        🤖 <strong>AI 엔진</strong>: HyperCLOVA X (HCX-005)
    </div>
    """, unsafe_allow_html=True)

def render_portfolio_chart(portfolio_info):
    """포트폴리오 차트 렌더링"""
    st.markdown("### 📈 포트폴리오 종목 차트")
    stock_data = get_stock_data(portfolio_info['ticker'])
    if stock_data is not None:
        chart = create_stock_chart(stock_data, portfolio_info['ticker'])
        st.plotly_chart(chart, use_container_width=True)

def render_troubleshooting_guide():
    """문제 해결 가이드 렌더링"""
    st.markdown("### 🔧 문제 해결 방법")
    st.markdown("""
    1. **API 키 확인**: `.streamlit/secrets.toml` 파일에 올바른 API 키 설정
    2. **네트워크 확인**: 인터넷 연결 상태 점검  
    3. **계정 상태**: 네이버 클라우드 플랫폼 계정 및 크레딧 확인
    4. **앱 설정**: CLOVA Studio에서 테스트 앱 'AI투자어드바이저_API' 생성 확인
    5. **질문 형식**: 구체적인 포트폴리오 정보 포함 권장
    """)

def render_sample_questions():
    """샘플 질문 렌더링"""
    if not st.session_state.user_question:
        st.markdown("### 💡 개인화 분석 샘플 질문")
        
        sample_questions = [
            "삼성전자 65,000원에 150주 보유 중, 지금 매도해야 할까요?",
            "테슬라 250달러에 30주 가지고 있는데 추가 매수가 좋을까요?", 
            "네이버 12만원에 100주 보유, 손절매 타이밍이 맞나요?",
            "현재 AI 관련 주식들 어떤 종목이 유망한가요?",
            "반도체 업종 전망과 투자 전략 알려주세요",
            "지금 시장에서 주목해야 할 섹터는 어디인가요?"
        ]
        
        cols = st.columns(2)
        for i, question in enumerate(sample_questions):
            with cols[i % 2]:
                if st.button(question, key=f"main_sample_{i}"):
                    st.session_state.selected_question = question
                    st.rerun()

def main():
    """메인 애플리케이션 실행"""
    # 페이지 설정
    setup_page_config()
    
    # CSS 로드
    load_css()
    
    # AI 클라이언트 초기화
    ai_client = EnhancedHyperCLOVAXClient()
    
    # 실시간 데이터 로드
    with st.spinner("📊 실시간 시장 데이터 로딩 중..."):
        market_data = get_real_time_market_data()
        news_data = get_recent_news()
    
    # 사이드바 렌더링
    render_sidebar(ai_client, market_data)
    
    # 메인 콘텐츠 렌더링
    render_main_content(ai_client, market_data, news_data)
    
    # 면책조항 렌더링
    render_disclaimer()
    
    # 만든이 정보 추가
    render_creator_info()

def render_creator_info():
    """만든이 정보 렌더링"""
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; padding: 2rem 0; color: #666; font-size: 0.9rem;">
            <p style="margin: 0;">🏆 <strong>AI Festival 2025</strong> 출품작</p>
            <p style="margin: 0.5rem 0 0 0;">
                💻 Created by <strong style="color: #667eea; font-size: 1.1rem;">Rin.C</strong>
            </p>
            <p style="margin: 0.5rem 0 0 0; font-size: 0.8rem;">
                🤖 Powered by HyperCLOVA X • 📊 Real-time Market Data • 🔴 Live Analysis
            </p>
        </div>
        """, 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
