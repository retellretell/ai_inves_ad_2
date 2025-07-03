"""
ui_styles.py - UI 스타일 및 렌더링 함수들
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Dict, Any, Optional

def load_css():
    """CSS 스타일 로드"""
    css = """
    <style>
    /* HyperCLOVA X AI 투자 어드바이저 스타일 */

    /* 메인 헤더 */
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        animation: glow 2s ease-in-out infinite alternate;
    }

    @keyframes glow {
        from {
            filter: drop-shadow(0 0 5px rgba(102, 126, 234, 0.5));
        }
        to {
            filter: drop-shadow(0 0 15px rgba(118, 75, 162, 0.7));
        }
    }

    /* AI 응답 박스 */
    .ai-response {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 1rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2);
        position: relative;
        overflow: hidden;
    }

    .ai-response::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
        animation: shimmer 3s infinite;
    }

    @keyframes shimmer {
        0% { left: -100%; }
        100% { left: 100%; }
    }

    /* 상태 표시 */
    .status-good {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(76,175,80,0.3);
        display: flex;
        align-items: center;
        font-weight: 500;
        transition: all 0.3s ease;
    }

    .status-good:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(76,175,80,0.4);
    }

    .status-bad {
        background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(244,67,54,0.3);
        display: flex;
        align-items: center;
        font-weight: 500;
        transition: all 0.3s ease;
    }

    .status-bad:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(244,67,54,0.4);
    }

    /* 포트폴리오 정보 박스 */
    .portfolio-info {
        background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%);
        border: 2px solid #4CAF50;
        border-radius: 1rem;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(76,175,80,0.2);
    }

    /* 데이터 타임스탬프 */
    .data-timestamp {
        background: #e8f5e8;
        padding: 0.5rem;
        border-radius: 0.3rem;
        margin: 0.5rem 0;
        border-left: 3px solid #4CAF50;
        font-size: 0.9rem;
    }

    /* 오류 메시지 */
    .error-message {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 1rem;
        margin: 1rem 0;
        border-left: 5px solid #ff3838;
        box-shadow: 0 4px 15px rgba(255,107,107,0.3);
    }

    /* 샘플 질문 박스 */
    .sample-question {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        border: 1px solid #2196f3;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }

    .sample-question:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(33,150,243,0.3);
        background: linear-gradient(135deg, #bbdefb 0%, #90caf9 100%);
    }

    .sample-question::after {
        content: '→';
        position: absolute;
        right: 1rem;
        top: 50%;
        transform: translateY(-50%);
        opacity: 0;
        transition: all 0.3s ease;
    }

    .sample-question:hover::after {
        opacity: 1;
        right: 0.5rem;
    }

    /* 뉴스 아이템 */
    .news-item {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }

    .news-item:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        border-color: #2196f3;
    }

    /* 면책조항 */
    .disclaimer {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        border: 2px solid #ff6b35;
        border-radius: 0.8rem;
        padding: 1.5rem;
        margin: 1rem 0;
        color: #2d3436;
        box-shadow: 0 4px 15px rgba(255,107,53,0.2);
    }

    /* 창작자 정보 */
    .creator-info {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 1rem;
        margin: 2rem 0 1rem 0;
        border: 1px solid #dee2e6;
        position: relative;
        overflow: hidden;
    }

    /* 버튼 스타일 */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102,126,234,0.3);
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102,126,234,0.4);
        filter: brightness(1.1);
    }

    .stButton > button:active {
        transform: translateY(0);
    }

    /* 프로그레스 바 */
    .stProgress > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 0.5rem;
    }

    /* 메트릭 카드 */
    .metric-card {
        background: white;
        border-radius: 0.5rem;
        padding: 1rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border-left: 4px solid #2196f3;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
    }

    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    }

    /* 입력 필드 */
    .stTextArea > div > div > textarea {
        border-radius: 0.5rem;
        border: 2px solid #e0e0e0;
        transition: all 0.3s ease;
    }

    .stTextArea > div > div > textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 10px rgba(102,126,234,0.3);
    }

    /* 선택 박스 */
    .stSelectbox > div > div {
        border-radius: 0.5rem;
        border: 2px solid #e0e0e0;
        transition: all 0.3s ease;
    }

    .stSelectbox > div > div:focus-within {
        border-color: #667eea;
        box-shadow: 0 0 10px rgba(102,126,234,0.3);
    }

    /* 경고 메시지 */
    .stAlert {
        border-radius: 0.5rem;
        border: none;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }

    /* 확장 가능한 컨테이너 */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 0.5rem;
        border: 1px solid #dee2e6;
        transition: all 0.3s ease;
    }

    .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, #e9ecef 0%, #dee2e6 100%);
        transform: translateY(-1px);
    }

    /* 반응형 디자인 */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem;
            margin-bottom: 1rem;
        }
        
        .ai-response {
            padding: 1rem;
            margin: 0.5rem 0;
        }
        
        .sample-question {
            padding: 0.75rem;
            font-size: 0.9rem;
        }
    }

    @media (max-width: 480px) {
        .main-header {
            font-size: 1.5rem;
        }
        
        .ai-response {
            padding: 0.75rem;
            border-radius: 0.5rem;
        }
    }

    /* 커스텀 스크롤바 */
    ::-webkit-scrollbar {
        width: 8px;
    }

    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
    }

    /* 애니메이션 효과 */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .fade-in {
        animation: fadeIn 0.5s ease-out;
    }

    /* 로딩 애니메이션 */
    .loading-dots::after {
        content: '';
        animation: dots 1.5s steps(5, end) infinite;
    }

    @keyframes dots {
        0%, 20% { content: ''; }
        40% { content: '.'; }
        60% { content: '..'; }
        80%, 100% { content: '...'; }
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def render_header(current_time: datetime):
    """강화된 헤더 렌더링"""
    st.markdown(f"""
    <div style="background: linear-gradient(90deg, #ff6b6b, #4ecdc4); 
                padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem; color: white; position: relative;">
        <h2 style="margin: 0; color: white;">🔴 실시간 개인화 AI 투자 어드바이저</h2>
        <p style="margin: 0.5rem 0 0 0; color: white;">
            📅 현재 시간: {current_time.strftime('%Y년 %m월 %d일 %H시 %M분 %S초')}<br>
            📊 실시간 데이터 분석 + 개인 포트폴리오 맞춤 조언 | 🏆 AI Festival 2025<br>
            🔒 보안 강화 버전 • 🛡️ 개인정보 보호 • ⚡ 성능 최적화
        </p>
        <div style="position: absolute; top: 1rem; right: 1rem; font-size: 0.8rem; opacity: 0.8;">
            💻 by Rin.C
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_portfolio_info(portfolio_info: Optional[Dict[str, Any]]):
    """포트폴리오 정보 렌더링"""
    if not portfolio_info:
        return
    
    st.markdown("### 👤 감지된 포트폴리오 정보")
    
    # 포트폴리오 정보 표시
    with st.container():
        st.markdown('<div class="portfolio-info fade-in">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if portfolio_info.get('stock'):
                st.markdown(f"**📈 보유 종목**  \n{portfolio_info['stock']}")
            if portfolio_info.get('ticker'):
                st.caption(f"티커: {portfolio_info['ticker']}")
        
        with col2:
            if portfolio_info.get('buy_price'):
                st.markdown(f"**💰 매수가**  \n{portfolio_info['buy_price']:,.0f}원")
            if portfolio_info.get('shares'):
                st.markdown(f"**📊 보유 주수**  \n{portfolio_info['shares']:,}주")
        
        with col3:
            if portfolio_info.get('buy_price') and portfolio_info.get('shares'):
                invested_amount = portfolio_info['buy_price'] * portfolio_info['shares']
                st.markdown(f"**💼 투자금액**  \n{invested_amount:,.0f}원")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 실시간 손익 계산 (현재가가 있는 경우)
    if portfolio_info.get('current_price'):
        render_portfolio_metrics(portfolio_info)

def render_portfolio_metrics(portfolio_info: Dict[str, Any]):
    """포트폴리오 수익률 메트릭 렌더링"""
    buy_price = portfolio_info.get('buy_price', 0)
    current_price = portfolio_info.get('current_price', 0)
    shares = portfolio_info.get('shares', 0)
    
    if not all([buy_price, current_price, shares]):
        return
    
    invested_amount = buy_price * shares
    current_value = current_price * shares
    profit_loss = current_value - invested_amount
    profit_rate = ((current_price - buy_price) / buy_price) * 100
    
    st.markdown("#### 📊 실시간 손익 현황")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("현재가", f"{current_price:,.0f}원", f"vs 매수가 {buy_price:,.0f}원")
    
    with col2:
        st.metric("현재가치", f"{current_value:,.0f}원")
    
    with col3:
        profit_color = "normal" if profit_loss >= 0 else "inverse"
        st.metric("평가손익", f"{profit_loss:,.0f}원", f"{profit_rate:+.2f}%", delta_color=profit_color)
    
    with col4:
        if profit_rate >= 20:
            st.success("🎉 큰 수익!")
        elif profit_rate >= 10:
            st.info("📈 수익 중")
        elif profit_rate >= -10:
            st.warning("📊 소폭 변동")
        else:
            st.error("📉 손실 상태")

def render_error_message(error_msg: str, error_type: str = "general"):
    """강화된 오류 메시지 렌더링"""
    st.markdown('<div class="error-message">', unsafe_allow_html=True)
    
    if error_type == "api":
        st.markdown(f"""
        🚨 **API 연결 오류**
        
        {error_msg}
        
        **해결 방법:**
        - API 키 설정 확인
        - 네트워크 연결 상태 확인
        - 잠시 후 다시 시도
        """)
    elif error_type == "network":
        st.markdown(f"""
        🌐 **네트워크 오류**
        
        {error_msg}
        
        **해결 방법:**
        - 인터넷 연결 확인
        - VPN 사용 시 해제 후 재시도
        - 방화벽 설정 확인
        """)
    elif error_type == "data":
        st.markdown(f"""
        📊 **데이터 처리 오류**
        
        {error_msg}
        
        **해결 방법:**
        - 입력 데이터 형식 확인
        - 질문을 더 구체적으로 작성
        - 다른 종목으로 시도
        """)
    else:
        st.markdown(f"""
        ❌ **오류 발생**
        
        {error_msg}
        
        **해결 방법:**
        - 페이지 새로고침
        - 잠시 후 다시 시도
        - 지속적인 문제 시 고객센터 연락
        """)
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_disclaimer():
    """투자 면책조항 렌더링"""
    st.markdown("""
    <div class="disclaimer">
        <h4 style="color: #d63031; margin: 0 0 1rem 0;">⚠️ 투자 위험 고지 및 면책사항</h4>
        <div style="color: #2d3436; font-size: 0.9rem; line-height: 1.6;">
            <p><strong>🚨 중요한 투자 위험 안내</strong></p>
            <ul style="margin: 0.5rem 0; padding-left: 1.5rem;">
                <li>본 AI 분석은 <strong>정보 제공 목적</strong>이며, 투자 권유나 매매 신호가 아닙니다.</li>
                <li>모든 투자에는 <strong>원금 손실 위험</strong>이 있으며, 과거 성과가 미래 수익을 보장하지 않습니다.</li>
                <li>투자 결정은 <strong>본인의 판단과 책임</strong>하에 이루어져야 합니다.</li>
                <li>중요한 투자 결정 전에는 <strong>전문가 상담</strong>을 받으시기 바랍니다.</li>
                <li>AI 분석 결과의 <strong>정확성을 보장하지 않으며</strong>, 시장 상황에 따라 예측이 빗나갈 수 있습니다.</li>
            </ul>
            <p style="margin-top: 1rem;"><strong>📞 투자 상담:</strong> 미래에셋증권 고객센터 1588-6666</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_creator_info():
    """창작자 정보 렌더링"""
    st.markdown("""
    <div class="creator-info">
        <p style="margin: 0; font-size: 1rem; color: #495057;">🏆 <strong>AI Festival 2025</strong> 출품작</p>
        <p style="margin: 1rem 0; font-size: 1.4rem;">
            💻 Created by <span style="color: #667eea; font-size: 1.2rem; font-weight: bold; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">Rin.C</span>
        </p>
        <div style="font-size: 0.8rem; color: #6c757d; margin-top: 0.5rem; letter-spacing: 0.5px;">
            🤖 <strong>HyperCLOVA X</strong> • 📊 <strong>Real-time Market Data</strong> • 🔴 <strong>Live Analysis</strong>
        </div>
        <div style="margin-top: 1rem; font-size: 0.75rem; color: #adb5bd;">
            ⚡ Powered by Streamlit & Python • 🚀 Enhanced with AI • 📈 Financial Technology<br>
            🔒 Security Enhanced • 🛡️ Privacy Protected • ⚡ Performance Optimized
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_loading_animation(message: str = "처리 중..."):
    """로딩 애니메이션 렌더링"""
    st.markdown(f"""
    <div style="text-align: center; padding: 2rem;">
        <div style="display: inline-block; width: 40px; height: 40px; border: 3px solid #f3f3f3; border-top: 3px solid #667eea; border-radius: 50%; animation: spin 1s linear infinite;"></div>
        <p style="margin-top: 1rem; color: #667eea; font-weight: 500;">{message}</p>
    </div>
    
    <style>
    @keyframes spin {{
        0% {{ transform: rotate(0deg); }}
        100% {{ transform: rotate(360deg); }}
    }}
    </style>
    """, unsafe_allow_html=True)

def render_market_status_widget(market_data: Dict[str, Any]):
    """시장 상태 위젯 렌더링"""
    if not market_data:
        return
    
    st.markdown("### 📊 실시간 시장 현황")
    
    # 주요 지수들만 선택
    key_indices = ["KOSPI", "NASDAQ", "S&P 500", "USD/KRW"]
    
    cols = st.columns(len(key_indices))
    
    for i, index_name in enumerate(key_indices):
        if index_name in market_data:
            data = market_data[index_name]
            with cols[i]:
                change_color = "normal" if data['change'] >= 0 else "inverse"
                st.metric(
                    label=index_name,
                    value=f"{data['current']:.2f}",
                    delta=f"{data['change']:+.2f}%",
                    delta_color=change_color
                )

def render_news_widget(news_data: list):
    """뉴스 위젯 렌더링"""
    if not news_data:
        return
    
    st.markdown("### 📰 최신 경제 뉴스")
    
    for i, article in enumerate(news_data[:5], 1):
        with st.container():
            st.markdown(f"""
            <div class="news-item">
                <h5 style="margin: 0 0 0.5rem 0; color: #2d3436;">{i}. {article['title']}</h5>
                <p style="margin: 0 0 0.5rem 0; color: #636e72; font-size: 0.9rem;">
                    {article.get('summary', '')[:100]}{'...' if len(article.get('summary', '')) > 100 else ''}
                </p>
                <div style="font-size: 0.8rem; color: #74b9ff;">
                    📰 {article.get('source', 'News')} • 🕐 {article.get('published', '최근')}
                </div>
            </div>
            """, unsafe_allow_html=True)

def render_sample_questions_widget():
    """샘플 질문 위젯 렌더링"""
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
            if st.button(question, key=f"sample_{i}", use_container_width=True):
                st.session_state.selected_question = question
                st.rerun()

def render_analysis_progress(steps: list, current_step: int):
    """분석 진행률 렌더링"""
    progress = current_step / len(steps) if steps else 0
    
    st.progress(progress)
    
    if current_step < len(steps):
        st.text(f"🔄 {steps[current_step]} ({current_step + 1}/{len(steps)})")
    else:
        st.text("✅ 분석 완료!")

def render_success_message(message: str):
    """성공 메시지 렌더링"""
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #00b894 0%, #00a085 100%); 
                color: white; padding: 1rem; border-radius: 0.5rem; margin: 1rem 0;">
        ✅ <strong>{message}</strong>
    </div>
    """, unsafe_allow_html=True)

def render_warning_message(message: str):
    """경고 메시지 렌더링"""
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #fdcb6e 0%, #e17055 100%); 
                color: white; padding: 1rem; border-radius: 0.5rem; margin: 1rem 0;">
        ⚠️ <strong>{message}</strong>
    </div>
    """, unsafe_allow_html=True)

def render_info_message(message: str):
    """정보 메시지 렌더링"""
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%); 
                color: white; padding: 1rem; border-radius: 0.5rem; margin: 1rem 0;">
        ℹ️ <strong>{message}</strong>
    </div>
    """, unsafe_allow_html=True)

def render_troubleshooting_guide():
    """문제 해결 가이드 렌더링"""
    st.markdown("### 🔧 문제 해결 방법")
    
    with st.expander("📋 자주 발생하는 문제와 해결책", expanded=False):
        st.markdown("""
        #### 🔑 API 키 관련 문제
        - **문제**: API 키 인증 실패
        - **해결**: `.streamlit/secrets.toml` 파일에 올바른 API 키 설정
        - **확인**: 네이버 클라우드 플랫폼에서 API 키 재발급
        
        #### 🌐 네트워크 연결 문제
        - **문제**: 연결 시간 초과 또는 연결 오류
        - **해결**: 인터넷 연결 상태 확인, VPN 해제, 방화벽 설정 확인
        
        #### 💾 데이터 로딩 문제
        - **문제**: 시장 데이터나 뉴스를 불러올 수 없음
        - **해결**: 페이지 새로고침, 잠시 후 재시도
        
        #### 🤖 AI 분석 오류
        - **문제**: AI 분석 결과가 나오지 않음
        - **해결**: 질문을 더 구체적으로 작성, 다른 종목으로 시도
        
        #### 📱 긴급 연락처
        - **고객센터**: 1588-6666 (24시간 상담 가능)
        - **카카오톡**: '미래에셋증권' 검색 후 친구추가
        """)

def render_api_status_indicator(api_key: str, service_name: str = "HyperCLOVA X"):
    """API 상태 표시기 렌더링"""
    if api_key:
        st.markdown(f"""
        <div class="status-good">
            🔴 LIVE - {service_name} 연결됨
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="status-bad">
            ❌ {service_name} API 키 미설정
        </div>
        """, unsafe_allow_html=True)
        st.error(f"⚠️ {service_name} API 키를 설정해야 서비스 이용이 가능합니다!")

def render_data_source_status(sources: Dict[str, bool]):
    """데이터 소스 상태 렌더링"""
    st.markdown("### 📡 데이터 소스 상태")
    
    source_names = {
        'market_data': '시장 데이터',
        'news_feed': '뉴스 피드',
        'dart_api': 'DART 공시',
        'naver_trends': '네이버 트렌드',
        'economic_indicators': '경제 지표'
    }
    
    for source_key, source_name in source_names.items():
        status = sources.get(source_key, False)
        icon = "✅" if status else "⚠️"
        status_text = "활성" if status else "비활성"
        st.caption(f"{icon} {source_name}: {status_text}")

def render_portfolio_summary_card(portfolio_metrics: Dict[str, Any]):
    """포트폴리오 요약 카드 렌더링"""
    if not portfolio_metrics:
        return
    
    st.markdown("### 💼 포트폴리오 요약")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "투자금액",
            f"{portfolio_metrics.get('invested_amount', 0):,.0f}원"
        )
    
    with col2:
        st.metric(
            "현재가치", 
            f"{portfolio_metrics.get('current_value', 0):,.0f}원"
        )
    
    with col3:
        profit_loss = portfolio_metrics.get('profit_loss', 0)
        profit_rate = portfolio_metrics.get('profit_rate', 0)
        profit_color = "normal" if profit_loss >= 0 else "inverse"
        st.metric(
            "평가손익",
            f"{profit_loss:,.0f}원",
            delta=f"{profit_rate:+.2f}%",
            delta_color=profit_color
        )
    
    with col4:
        current_price = portfolio_metrics.get('current_price', 0)
        buy_price = portfolio_metrics.get('buy_price', 0)
        st.metric(
            "현재가",
            f"{current_price:,.0f}원",
            delta=f"vs 매수가 {buy_price:,.0f}원"
        )

def render_analysis_summary_card(analysis_time: datetime, portfolio_info: Optional[Dict[str, Any]] = None):
    """분석 요약 카드 렌더링"""
    st.markdown(f"""
    <div class="data-timestamp">
        📊 <strong>분석 완료</strong>: {analysis_time.strftime('%Y년 %m월 %d일 %H시 %M분 %S초')}<br>
        🔄 <strong>데이터 소스</strong>: 5개 통합 (실시간 시장 + 뉴스 + 공시 + 트렌드 + 경제지표)<br>
        👤 <strong>개인화</strong>: {'포트폴리오 맞춤 분석' if portfolio_info else '일반 시장 분석'}<br>
        🤖 <strong>AI 엔진</strong>: HyperCLOVA X (HCX-005)<br>
        🔒 <strong>보안</strong>: 데이터 암호화 및 개인정보 보호 적용
    </div>
    """, unsafe_allow_html=True)

def render_feature_showcase():
    """기능 소개 렌더링"""
    st.markdown("### 🚀 주요 기능")
    
    features = [
        {
            "icon": "🤖",
            "title": "AI 개인화 분석",
            "description": "HyperCLOVA X 기반 맞춤형 투자 조언"
        },
        {
            "icon": "📊",
            "title": "실시간 시장 데이터",
            "description": "5분 간격 실시간 시장 현황 분석"
        },
        {
            "icon": "📰",
            "title": "최신 뉴스 분석",
            "description": "경제 뉴스 자동 수집 및 감정 분석"
        },
        {
            "icon": "💼",
            "title": "포트폴리오 관리",
            "description": "보유 종목 자동 인식 및 손익 계산"
        },
        {
            "icon": "📈",
            "title": "기술적 분석",
            "description": "RSI, MACD, 볼린저밴드 등 기술 지표"
        },
        {
            "icon": "🛡️",
            "title": "보안 강화",
            "description": "개인정보 보호 및 데이터 암호화"
        }
    ]
    
    cols = st.columns(3)
    for i, feature in enumerate(features):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="metric-card" style="text-align: center;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">{feature['icon']}</div>
                <h4 style="margin: 0.5rem 0; color: #2d3436;">{feature['title']}</h4>
                <p style="margin: 0; color: #636e72; font-size: 0.9rem;">{feature['description']}</p>
            </div>
            """, unsafe_allow_html=True)

def render_quick_actions():
    """빠른 액션 버튼들 렌더링"""
    st.markdown("### ⚡ 빠른 실행")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📊 시장 현황", use_container_width=True):
            st.session_state.selected_question = "현재 주요 지수들의 상황과 시장 전망을 알려주세요"
            st.rerun()
    
    with col2:
        if st.button("🔥 HOT 종목", use_container_width=True):
            st.session_state.selected_question = "지금 가장 주목받는 HOT한 종목들을 추천해주세요"
            st.rerun()
    
    with col3:
        if st.button("💎 투자 전략", use_container_width=True):
            st.session_state.selected_question = "현재 시장 상황에서 최적의 투자 전략을 제시해주세요"
            st.rerun()
    
    with col4:
        if st.button("⚠️ 리스크 체크", use_container_width=True):
            st.session_state.selected_question = "현재 시장의 주요 리스크 요인들을 분석해주세요"
            st.rerun()

def render_footer():
    """푸터 렌더링"""
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0; color: #666; font-size: 0.8rem;">
        <p style="margin: 0;">
            🔒 <strong>개인정보 보호</strong> | 🛡️ <strong>보안 강화</strong> | ⚡ <strong>실시간 분석</strong>
        </p>
        <p style="margin: 0.5rem 0 0 0;">
            본 서비스는 정보 제공 목적이며, 투자 권유가 아닙니다. 투자 결정은 본인 책임하에 하시기 바랍니다.
        </p>
    </div>
    """, unsafe_allow_html=True)

def get_custom_theme():
    """커스텀 테마 설정 반환"""
    return {
        'primary_color': '#667eea',
        'secondary_color': '#764ba2',
        'success_color': '#4CAF50',
        'warning_color': '#ff6b35',
        'error_color': '#f44336',
        'info_color': '#2196f3',
        'background_color': '#ffffff',
        'text_color': '#2d3436'
    }

# 유틸리티 함수들
def format_number(num: float, decimal_places: int = 0) -> str:
    """숫자 포맷팅"""
    if decimal_places == 0:
        return f"{num:,.0f}"
    else:
        return f"{num:,.{decimal_places}f}"

def format_percentage(num: float, decimal_places: int = 2) -> str:
    """퍼센트 포맷팅"""
    return f"{num:+.{decimal_places}f}%"

def format_currency(num: float, currency: str = "원") -> str:
    """통화 포맷팅"""
    return f"{num:,.0f}{currency}"

def get_trend_icon(change: float) -> str:
    """변동률에 따른 아이콘 반환"""
    if change > 2:
        return "🚀"
    elif change > 0:
        return "📈"
    elif change > -2:
        return "📊"
    else:
        return "📉"

def get_risk_color(risk_level: str) -> str:
    """리스크 레벨에 따른 색상 반환"""
    colors = {
        'LOW': '#4CAF50',
        'MEDIUM': '#ff9800',
        'HIGH': '#f44336',
        'CRITICAL': '#9c27b0'
    }
    return colors.get(risk_level.upper(), '#666666')

def render_custom_metric(label: str, value: str, delta: str = None, 
                        delta_color: str = "normal", help_text: str = None):
    """커스텀 메트릭 렌더링"""
    delta_html = ""
    if delta:
        color = "#28a745" if delta_color == "normal" and delta.startswith('+') else "#dc3545" if delta_color == "inverse" or delta.startswith('-') else "#6c757d"
        delta_html = f'<div style="color: {color}; font-size: 0.8rem; margin-top: 0.2rem;">{delta}</div>'
    
    help_html = ""
    if help_text:
        help_html = f'<div style="color: #6c757d; font-size: 0.7rem; margin-top: 0.3rem;">💡 {help_text}</div>'
    
    st.markdown(f"""
    <div class="metric-card">
        <div style="color: #495057; font-size: 0.9rem; margin-bottom: 0.3rem;">{label}</div>
        <div style="font-size: 1.5rem; font-weight: bold; color: #212529;">{value}</div>
        {delta_html}
        {help_html}
    </div>
    """, unsafe_allow_html=True)
