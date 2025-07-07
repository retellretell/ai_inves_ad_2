"""
main.py - 통합된 메인 애플리케이션
HyperCLOVA X 기반 AI 투자 어드바이저 + 보안/마케팅/고급 기능 통합
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
import uuid

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 페이지 설정
st.set_page_config(
    page_title="HyperCLOVA X AI 투자 어드바이저 Pro",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 보안 강화 모듈
try:
    from security_config import (
        secure_config, privacy_manager, error_handler, compliance_manager
    )
    SECURITY_ENABLED = True
except ImportError:
    logger.warning("보안 모듈을 찾을 수 없습니다. 기본 모드로 실행합니다.")
    SECURITY_ENABLED = False

# 강화된 오류 처리
try:
    from enhanced_error_handler import (
        init_error_handling, handle_api_error, show_service_status, collect_user_feedback
    )
    ERROR_HANDLER_ENABLED = True
except ImportError:
    ERROR_HANDLER_ENABLED = False

# 마케팅 CTA 시스템
try:
    from cta_marketing import (
        init_marketing_system, show_marketing_cta, track_user_action
    )
    MARKETING_ENABLED = True
except ImportError:
    MARKETING_ENABLED = False

# 새로운 기능 모듈들
try:
    from realtime_alert_engine import integrate_realtime_alerts
    ALERTS_ENABLED = True
except ImportError:
    logger.warning("실시간 알림 모듈을 찾을 수 없습니다.")
    ALERTS_ENABLED = False

try:
    from advanced_investor_features import render_advanced_features
    ADVANCED_FEATURES_ENABLED = True
except ImportError:
    logger.warning("고급 투자자 기능 모듈을 찾을 수 없습니다.")
    ADVANCED_FEATURES_ENABLED = False

try:
    from ai_backtesting_system import render_backtesting_system
    BACKTESTING_ENABLED = True
except ImportError:
    logger.warning("백테스팅 모듈을 찾을 수 없습니다.")
    BACKTESTING_ENABLED = False

try:
    from enhanced_features import integrate_advanced_features
    ENHANCED_FEATURES_ENABLED = True
except ImportError:
    logger.warning("향상된 기능 모듈을 찾을 수 없습니다.")
    ENHANCED_FEATURES_ENABLED = False

# 기본 모듈들
from config import Config, get_api_key
from data_collector import get_real_time_market_data, get_recent_news, get_stock_data
from portfolio_parser import parse_user_portfolio
from chart_utils import create_stock_chart, display_market_metrics

# CSS 스타일 로드
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

# HyperCLOVA X 클라이언트
class HyperCLOVAXClient:
    def __init__(self):
        self.api_key = get_api_key()
        self.base_url = Config.CLOVA_BASE_URL
        
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
                'X-NCP-CLOVASTUDIO-API-KEY': self.api_key,
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            url = f"{self.base_url}/testapp/v1/chat-completions/{Config.CLOVA_MODEL}"
            
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
                **Config.AI_PARAMS
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

# 강화된 AI 클라이언트 (통합 버전 사용)
try:
    from ai_client import EnhancedHyperCLOVAXClient
    AI_CLIENT_CLASS = EnhancedHyperCLOVAXClient
except ImportError:
    AI_CLIENT_CLASS = HyperCLOVAXClient

class IntegratedInvestmentAdvisor:
    """통합된 투자 어드바이저"""
    
    def __init__(self):
        self.session_id = self._init_session()
        
        # 보안 및 에러 처리 초기화
        if ERROR_HANDLER_ENABLED:
            self.error_handler, self.feedback_collector = init_error_handling()
        
        # 마케팅 시스템 초기화
        if MARKETING_ENABLED:
            self.marketing_system = init_marketing_system()
    
    def _init_session(self) -> str:
        """세션 초기화"""
        if 'session_id' not in st.session_state:
            st.session_state.session_id = str(uuid.uuid4())
        
        if 'session_start' not in st.session_state:
            st.session_state.session_start = datetime.now()
        
        # 기능 활성화 상태 초기화
        if 'show_advanced_features' not in st.session_state:
            st.session_state.show_advanced_features = True
        
        if 'show_backtesting' not in st.session_state:
            st.session_state.show_backtesting = True
            
        if 'show_realtime_alerts' not in st.session_state:
            st.session_state.show_realtime_alerts = True
        
        if 'user_question' not in st.session_state:
            st.session_state.user_question = ""
            
        if 'selected_question' not in st.session_state:
            st.session_state.selected_question = ""
        
        return st.session_state.session_id
    
    def run(self):
        """메인 애플리케이션 실행"""
        try:
            # CSS 로드
            load_css()
            
            # 보안 검사 (활성화된 경우)
            if SECURITY_ENABLED:
                if not self._security_checks():
                    return
                
                # 개인정보 처리 방침 확인
                if not privacy_manager.check_privacy_consent():
                    privacy_manager.show_privacy_notice()
                    return
                
                # 세션 유효성 검증
                if not secure_config.validate_session():
                    st.error("세션이 만료되었습니다. 페이지를 새로고침해주세요.")
                    return
            
            # 메인 애플리케이션 렌더링
            self._render_main_app()
            
        except Exception as e:
            logger.error(f"메인 애플리케이션 오류: {str(e)}")
            if ERROR_HANDLER_ENABLED:
                error_info = error_handler.handle_secure_error(e, "main_app")
                st.error(f"서비스에 일시적인 문제가 발생했습니다. (오류 ID: {error_info['error_id']})")
                collect_user_feedback(f"Main app error: {error_info['error_id']}")
            else:
                st.error(f"오류 발생: {str(e)}")
    
    def _security_checks(self) -> bool:
        """보안 검사"""
        if not SECURITY_ENABLED:
            return True
            
        try:
            if not secure_config.check_rate_limit(st.session_state.get('session_id', 'anonymous')):
                st.error("🚫 요청이 너무 빈번합니다. 잠시 후 다시 시도해주세요.")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"보안 검사 오류: {str(e)}")
            return True  # 보안 검사 실패 시에도 계속 진행
    
    def _render_main_app(self):
        """메인 애플리케이션 렌더링"""
        # 헤더 렌더링
        current_time = datetime.now()
        self._render_header(current_time)
        
        # 서비스 상태 확인 (관리자 모드)
        if st.secrets.get("ADMIN_MODE", False):
            with st.expander("🔧 시스템 상태 (관리자)", expanded=False):
                if ERROR_HANDLER_ENABLED:
                    show_service_status()
                else:
                    st.info("시스템 상태 모니터링이 비활성화되어 있습니다.")
        
        # 실시간 데이터 로드
        with st.spinner("📊 실시간 시장 데이터 로딩 중..."):
            market_data = get_real_time_market_data()
            news_data = get_recent_news()
        
        # 사이드바 렌더링
        ai_client = self._render_sidebar(market_data)
        
        # 메인 탭 구성
        tabs = ["🏠 홈", "🤖 AI 분석"]
        
        # 조건부로 탭 추가
        if ALERTS_ENABLED:
            tabs.append("🔔 실시간 알림")
        if ADVANCED_FEATURES_ENABLED:
            tabs.append("🚀 고급 기능")
        if BACKTESTING_ENABLED:
            tabs.append("📊 백테스팅")
        if ENHANCED_FEATURES_ENABLED:
            tabs.append("📈 기술적 분석")
        
        main_tabs = st.tabs(tabs)
        
        # 탭 콘텐츠 렌더링
        tab_index = 0
        
        # 홈 탭
        with main_tabs[tab_index]:
            self._render_home_content(market_data, news_data)
        tab_index += 1
        
        # AI 분석 탭
        with main_tabs[tab_index]:
            self._render_ai_analysis_content(ai_client, market_data, news_data)
        tab_index += 1
        
        # 실시간 알림 탭
        if ALERTS_ENABLED:
            with main_tabs[tab_index]:
                integrate_realtime_alerts()
            tab_index += 1
        
        # 고급 기능 탭
        if ADVANCED_FEATURES_ENABLED:
            with main_tabs[tab_index]:
                render_advanced_features()
            tab_index += 1
        
        # 백테스팅 탭
        if BACKTESTING_ENABLED:
            with main_tabs[tab_index]:
                render_backtesting_system()
            tab_index += 1
        
        # 기술적 분석 탭
        if ENHANCED_FEATURES_ENABLED:
            with main_tabs[tab_index]:
                advanced_analytics = integrate_advanced_features()
                portfolio_data = st.session_state.get('monitored_portfolio', [])
                advanced_analytics.render_advanced_dashboard(
                    portfolio_data=portfolio_data,
                    news_data=news_data
                )
            tab_index += 1
        
        # 면책조항
        if SECURITY_ENABLED:
            compliance_manager.show_investment_disclaimer()
        else:
            st.warning("⚠️ **투자 주의사항**: 본 분석은 정보 제공 목적이며, 투자 권유가 아닙니다. 투자 결정은 본인 책임하에 하시기 바랍니다.")
        
        # 만든이 정보
        self._render_creator_info()
    
    def _render_header(self, current_time):
        """헤더 렌더링"""
        st.markdown('<div class="main-header">🤖 HyperCLOVA X AI 투자 어드바이저</div>', unsafe_allow_html=True)
        st.markdown(f'<p style="text-align: center; color: #666; font-size: 1.1rem;">🔴 실시간 분석 • 📊 Live Market Data • 🚀 Pro Features</p>', unsafe_allow_html=True)
        st.markdown(f'<p style="text-align: center; color: #999; font-size: 0.9rem;">📅 {current_time.strftime("%Y년 %m월 %d일 %H시 %M분 %S초")}</p>', unsafe_allow_html=True)
    
    def _render_sidebar(self, market_data):
        """사이드바 렌더링"""
        ai_client = AI_CLIENT_CLASS()
        
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
            
            # 인기 질문
            st.markdown("### 💡 인기 질문")
            popular_questions = [
                "현재 시장 상황 분석",
                "오늘 매매 타이밍은?", 
                "지금 주목해야 할 섹터",
                "실시간 리스크 요인"
            ]
            
            for question in popular_questions:
                if st.button(question, key=f"sidebar_{question}", use_container_width=True):
                    st.session_state.selected_question = question
                    if MARKETING_ENABLED:
                        track_user_action("sidebar_question_clicked")
                    st.rerun()
            
            st.markdown("---")
            st.caption(f"🔴 실시간 업데이트: {datetime.now().strftime('%H:%M:%S')}")
        
        return ai_client
    
    def _render_home_content(self, market_data, news_data):
        """홈 화면 렌더링"""
        st.markdown("### 🏠 AI 투자 어드바이저 홈")
        
        # 기능 소개 카드
        st.markdown("#### 🌟 주요 기능")
        
        feature_cols = st.columns(4)
        
        features = [
            {
                "icon": "🤖",
                "title": "AI 실시간 분석",
                "desc": "HyperCLOVA X 기반 맞춤 분석",
                "enabled": True
            },
            {
                "icon": "🔔",
                "title": "24/7 알림",
                "desc": "실시간 포트폴리오 모니터링",
                "enabled": ALERTS_ENABLED
            },
            {
                "icon": "📊",
                "title": "백테스팅",
                "desc": "전략 검증 및 최적화",
                "enabled": BACKTESTING_ENABLED
            },
            {
                "icon": "🚀",
                "title": "고급 분석",
                "desc": "기술적 분석 및 리스크 관리",
                "enabled": ADVANCED_FEATURES_ENABLED
            }
        ]
        
        for col, feature in zip(feature_cols, features):
            with col:
                status = "✅" if feature["enabled"] else "❌"
                st.markdown(f"""
                <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 0.5rem; text-align: center; height: 150px;">
                    <div style="font-size: 2rem;">{feature["icon"]}</div>
                    <h4 style="margin: 0.5rem 0;">{feature["title"]} {status}</h4>
                    <p style="font-size: 0.9rem; color: #666;">{feature["desc"]}</p>
                </div>
                """, unsafe_allow_html=True)
        
        # 시장 개요
        if market_data:
            st.markdown("#### 📈 오늘의 시장")
            display_market_metrics(market_data)
        
        # 최신 뉴스
        if news_data:
            st.markdown("#### 📰 최신 뉴스")
            for article in news_data[:3]:
                with st.container():
                    st.markdown(f"**{article['title']}**")
                    if article.get('summary'):
                        st.caption(f"{article['summary'][:100]}...")
                    st.caption(f"출처: {article.get('source', 'News')} | {article.get('published', '최근')}")
        
        st.markdown("---")
        st.info("💡 **시작하기**: 위 탭에서 원하는 기능을 선택하거나, AI 분석 탭에서 질문을 입력하세요!")
    
    def _render_ai_analysis_content(self, ai_client, market_data, news_data):
        """AI 분석 콘텐츠 렌더링"""
        st.markdown("### 💬 실시간 AI 투자 분석")
        
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
        
        # 선택된 질문 업데이트
        if st.session_state.selected_question:
            st.session_state.user_question = st.session_state.selected_question
            st.session_state.selected_question = ""
        
        # 질문 입력
        user_question = st.text_area(
            "",
            value=st.session_state.user_question,
            placeholder="예: 삼성전자 70,000원에 100주 보유 중인데 계속 들고 있는 게 맞을까요?",
            height=100,
            label_visibility="collapsed",
            key="question_input"
        )
        
        if user_question != st.session_state.user_question:
            st.session_state.user_question = user_question
        
        # 분석 버튼
        if st.button("🔴 실시간 AI 분석 시작", type="primary", use_container_width=True):
            if not ai_client.api_key:
                st.error("⚠️ API 키가 설정되지 않았습니다.")
                return
            
            if not st.session_state.user_question.strip():
                st.warning("💬 분석할 질문을 입력해주세요.")
                return
            
            # 보안 체크
            if SECURITY_ENABLED:
                if not secure_config.check_rate_limit(self.session_id):
                    st.error("🚫 요청이 너무 빈번합니다. 잠시 후 다시 시도해주세요.")
                    return
                
                # 입력 무력화
                sanitized_question = secure_config.sanitize_input(st.session_state.user_question)
                st.session_state.user_question = sanitized_question
            
            # 포트폴리오 정보 추출
            portfolio_info = parse_user_portfolio(st.session_state.user_question)
            
            # 포트폴리오 정보 표시
            if portfolio_info:
                st.markdown("### 👤 감지된 포트폴리오 정보")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if portfolio_info.get('stock'):
                        st.metric("종목", portfolio_info['stock'])
                
                with col2:
                    if portfolio_info.get('buy_price'):
                        st.metric("매수가", f"{portfolio_info['buy_price']:,.0f}원")
                
                with col3:
                   if portfolio_info.get('shares'):
                       st.metric("보유 수량", f"{portfolio_info['shares']}주")
               
               # 손익 정보 표시
               if portfolio_info.get('current_price') and portfolio_info.get('buy_price'):
                   profit_rate = portfolio_info.get('profit_rate', 0)
                   profit_amount = portfolio_info.get('profit_amount', 0)
                   
                   col1, col2 = st.columns(2)
                   with col1:
                       st.metric("수익률", f"{profit_rate:+.2f}%", 
                               delta_color="normal" if profit_rate >= 0 else "inverse")
                   with col2:
                       st.metric("손익금액", f"{profit_amount:+,.0f}원",
                               delta_color="normal" if profit_amount >= 0 else "inverse")
           
           # 진행률 표시
           progress_bar = st.progress(0)
           status_text = st.empty()
           
           # 분석 단계
           steps = [
               ("🔍 질문 분석 중...", 0.2),
               ("📊 실시간 시장 데이터 수집...", 0.4),
               ("📰 최신 뉴스 분석...", 0.6),
               ("🤖 AI 분석 실행...", 0.8),
               ("✅ 분석 완료!", 1.0)
           ]
           
           for step, progress in steps:
               status_text.text(step)
               progress_bar.progress(progress)
               time.sleep(0.5)
           
           try:
               # AI 분석 수행
               with st.spinner("🤖 HyperCLOVA X가 실시간 분석 중입니다..."):
                   if hasattr(ai_client, 'get_real_time_analysis'):
                       response = ai_client.get_real_time_analysis(
                           st.session_state.user_question,
                           market_data,
                           news_data
                       )
                   else:
                       # 기본 분석 메소드 사용
                       response = ai_client.get_personalized_analysis(
                           st.session_state.user_question,
                           portfolio_info
                       )
               
               # 진행률 제거
               progress_bar.empty()
               status_text.empty()
               
               # 응답 표시
               st.markdown('<div class="ai-response">', unsafe_allow_html=True)
               st.markdown(response)
               st.markdown('</div>', unsafe_allow_html=True)
               
               # 분석 요약
               st.markdown(f"""
               <div style="background: #e8f5e8; padding: 0.5rem; border-radius: 0.3rem; margin: 0.5rem 0;">
                   📊 분석 완료: {datetime.now().strftime('%Y년 %m월 %d일 %H시 %M분 %S초')}<br>
                   🔄 데이터 소스: 실시간 시장 + 최신 뉴스 + AI 분석<br>
                   🤖 AI 엔진: HyperCLOVA X (네이버 클라우드 플랫폼)
               </div>
               """, unsafe_allow_html=True)
               
               # 차트 표시 (포트폴리오 종목이 있는 경우)
               if portfolio_info and portfolio_info.get('ticker'):
                   st.markdown("### 📈 종목 차트")
                   try:
                       stock_data = get_stock_data(portfolio_info['ticker'])
                       if stock_data is not None:
                           chart = create_stock_chart(stock_data, portfolio_info['ticker'])
                           st.plotly_chart(chart, use_container_width=True)
                   except Exception as e:
                       st.warning("차트를 불러올 수 없습니다.")
               
               # 마케팅 CTA (활성화된 경우)
               if MARKETING_ENABLED:
                   track_user_action("analysis_completed")
                   context = "general"
                   if portfolio_info:
                       profit_rate = portfolio_info.get('profit_rate', 0)
                       if profit_rate < -15:
                           context = "high_loss"
                       elif profit_rate > 25:
                           context = "high_profit"
                   show_marketing_cta(context, portfolio_info, response)
               
           except Exception as e:
               progress_bar.empty()
               status_text.empty()
               
               # 에러 처리
               if ERROR_HANDLER_ENABLED:
                   error_info = error_handler.handle_secure_error(e, "ai_analysis")
                   st.markdown(f'<div class="error-message">', unsafe_allow_html=True)
                   st.markdown(f"🚨 **분석 중 오류 발생**\n\n{error_info['user_message']}\n\n오류 ID: {error_info['error_id']}")
                   st.markdown('</div>', unsafe_allow_html=True)
                   collect_user_feedback(f"Analysis error: {error_info['error_id']}")
               else:
                   st.error(f"❌ 오류 발생: {str(e)}")
               
               # 문제 해결 가이드
               st.markdown("### 🔧 문제 해결 방법")
               st.markdown("""
               1. **API 키 확인**: 사이드바에서 API 연결 상태 확인
               2. **네트워크 확인**: 인터넷 연결 상태 확인
               3. **질문 단순화**: 더 간단한 질문으로 재시도
               4. **페이지 새로고침**: 브라우저 새로고침 후 재시도
               """)
       
       # 샘플 질문
       if not st.session_state.user_question:
           st.markdown("### 💡 샘플 질문")
           
           sample_questions = [
               "삼성전자 65,000원에 150주 보유 중, 지금 매도해야 할까요?",
               "오늘 시장 상황 어떤가요? 매수하기 좋은 타이밍인가요?",
               "반도체 섹터 전망은 어떤가요?",
               "현재 가장 주목해야 할 투자 테마는?",
               "달러 환율이 계속 오르는데 어떻게 대응해야 할까요?",
               "AI 관련주 투자 전략 알려주세요"
           ]
           
           cols = st.columns(2)
           for i, question in enumerate(sample_questions):
               with cols[i % 2]:
                   if st.button(question, key=f"sample_{i}"):
                       st.session_state.selected_question = question
                       if MARKETING_ENABLED:
                           track_user_action("sample_question_clicked")
                       st.rerun()
   
   def _render_creator_info(self):
       """만든이 정보 렌더링"""
       st.markdown("---")
       st.markdown("""
       <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border-radius: 1rem; margin: 2rem 0;">
           <p style="margin: 0; font-size: 1rem; color: #495057;">🏆 <strong>AI Festival 2025</strong> 출품작</p>
           <p style="margin: 1rem 0; font-size: 1.4rem;">
               💻 Created by <span style="color: #667eea; font-size: 1.2rem; font-weight: bold;">Rin.C</span>
           </p>
           <div style="font-size: 0.8rem; color: #6c757d; margin-top: 1rem;">
               🤖 HyperCLOVA X • 📊 Real-time Market Data • 🔴 Live Analysis • 🚀 Pro Features
           </div>
       </div>
       """, unsafe_allow_html=True)

def main():
   """메인 함수"""
   try:
       # 통합 투자 어드바이저 실행
       app = IntegratedInvestmentAdvisor()
       app.run()
       
   except Exception as e:
       logger.critical(f"치명적 오류 발생: {str(e)}")
       st.error("🚨 시스템에 치명적인 오류가 발생했습니다.")
       
       # 관리자 모드에서만 상세 오류 표시
       if st.secrets.get("ADMIN_MODE", False):
           st.exception(e)

if __name__ == "__main__":
   main()
