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
        st.caption(f"✅
