"""
ui_styles.py - UI 스타일 및 테마 관리
"""

import streamlit as st

def load_css():
    """CSS 스타일 로드"""
    try:
        with open('styles.css', 'r', encoding='utf-8') as f:
            css = f.read()
        st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        # CSS 파일이 없을 경우 기본 스타일 사용
        apply_default_styles()

def apply_default_styles():
    """기본 CSS 스타일 적용"""
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
    .realtime-header {
        background: linear-gradient(90deg, #ff6b6b, #4ecdc4);
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        color: white;
    }
    .data-timestamp {
        background: #e8f5e8;
        padding: 0.5rem;
        border-radius: 0.3rem;
        margin: 0.5rem 0;
        border-left: 3px solid #4CAF50;
    }
    .portfolio-analysis {
        background: linear-gradient(135deg, #ffeaa7 0%, #fdcb6e 100%);
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border-left: 5px solid #e17055;
    }
    </style>
    """, unsafe_allow_html=True)

def render_header(current_time):
    """실시간 헤더 렌더링"""
    st.markdown(f"""
    <div class="realtime-header">
        <h2 style="margin: 0; color: white;">🔴 실시간 개인화 AI 투자 어드바이저</h2>
        <p style="margin: 0.5rem 0 0 0; color: white;">
            📅 현재 시간: {current_time.strftime('%Y년 %m월 %d일 %H시 %M분 %S초')}<br>
            📊 실시간 데이터 분석 + 개인 포트폴리오 맞춤 조언 | 🏆 AI Festival 2025
        </p>
    </div>
    """, unsafe_allow_html=True)

def render_portfolio_info(portfolio_info):
    """포트폴리오 정보 렌더링"""
    if portfolio_info:
        st.markdown(f"""
        <div class="portfolio-analysis">
            <h4>👤 감지된 포트폴리오 정보</h4>
            <p>
                🏢 종목: {portfolio_info.get('stock', '알 수 없음')}<br>
                💰 매수가: {portfolio_info.get('buy_price', 0):,.0f}원<br>
                📊 보유량: {portfolio_info.get('shares', 0):,}주
            </p>
        </div>
        """, unsafe_allow_html=True)

def render_error_message(error_msg):
    """오류 메시지 렌더링"""
    st.markdown('<div class="error-message">', unsafe_allow_html=True)
    st.markdown(f"🚨 **실시간 분석 오류**\n\n{error_msg}")
    st.markdown('</div>', unsafe_allow_html=True)

def render_disclaimer():
    """면책조항 렌더링"""
    st.markdown("""
    <div style="background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%); border: 1px solid #ffeaa7; border-radius: 0.5rem; padding: 1.5rem; margin: 1rem 0;">
        <h4 style="color: #856404; margin: 0 0 0.5rem 0;">⚠️ 개인화 투자 분석 주의사항</h4>
        <p style="color: #856404; margin: 0; font-size: 0.9rem;">
            <strong>본 AI 분석은 실시간 데이터를 바탕으로 한 참고용 정보입니다.</strong><br>
            • 실제 투자 결정은 충분한 검토와 전문가 상담 후 본인 책임하에 하시기 바랍니다.<br>
            • 개인화 분석은 제공된 정보를 기반으로 하며, 정확성을 보장하지 않습니다.<br>
            • 시장 상황은 빠르게 변할 수 있으므로 최신 정보를 지속적으로 확인하세요.<br>
            • 투자에는 원금 손실 위험이 있으며, 분산 투자를 권장합니다.
        </p>
    </div>
    """, unsafe_allow_html=True)
