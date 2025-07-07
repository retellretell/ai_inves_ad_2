"""
main.py - 통합된 메인 애플리케이션
HyperCLOVA X 기반 AI 투자 어드바이저 + 보안/마케팅/고급 기능 통합
Core 폴더 구조 유지 버전
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

# 보안 강화 모듈 (선택적 로드)
try:
    from security_config import (
        secure_config, privacy_manager, error_handler, compliance_manager
    )
    SECURITY_ENABLED = True
    logger.info("보안 모듈 로드 성공")
except ImportError as e:
    logger.warning(f"보안 모듈을 찾을 수 없습니다: {e}")
    SECURITY_ENABLED = False

# 강화된 오류 처리 (선택적 로드)
try:
    from enhanced_error_handler import (
        init_error_handling, handle_api_error, show_service_status, collect_user_feedback
    )
    ERROR_HANDLER_ENABLED = True
    logger.info("오류 처리 모듈 로드 성공")
except ImportError as e:
    logger.warning(f"오류 처리 모듈을 찾을 수 없습니다: {e}")
    ERROR_HANDLER_ENABLED = False

# 마케팅 CTA 시스템 (선택적 로드)
try:
    from cta_marketing import (
        init_marketing_system, show_marketing_cta, track_user_action
    )
    MARKETING_ENABLED = True
    logger.info("마케팅 모듈 로드 성공")
except ImportError as e:
    logger.warning(f"마케팅 모듈을 찾을 수 없습니다: {e}")
    MARKETING_ENABLED = False

# 새로운 기능 모듈들 (선택적 로드)
try:
    from realtime_alert_engine import integrate_realtime_alerts
    ALERTS_ENABLED = True
    logger.info("실시간 알림 모듈 로드 성공")
except ImportError as e:
    logger.warning(f"실시간 알림 모듈을 찾을 수 없습니다: {e}")
    ALERTS_ENABLED = False

try:
    from advanced_investor_features import render_advanced_features
    ADVANCED_FEATURES_ENABLED = True
    logger.info("고급 투자자 기능 모듈 로드 성공")
except ImportError as e:
    logger.warning(f"고급 투자자 기능 모듈을 찾을 수 없습니다: {e}")
    ADVANCED_FEATURES_ENABLED = False

try:
    from ai_backtesting_system import render_backtesting_system
    BACKTESTING_ENABLED = True
    logger.info("백테스팅 모듈 로드 성공")
except ImportError as e:
    logger.warning(f"백테스팅 모듈을 찾을 수 없습니다: {e}")
    BACKTESTING_ENABLED = False

try:
    from enhanced_features import integrate_advanced_features
    ENHANCED_FEATURES_ENABLED = True
    logger.info("향상된 기능 모듈 로드 성공")
except ImportError as e:
    logger.warning(f"향상된 기능 모듈을 찾을 수 없습니다: {e}")
    ENHANCED_FEATURES_ENABLED = False

# Core 모듈들 (core 폴더에서 로드)
try:
    from core.config import Config, get_api_key
    CONFIG_ENABLED = True
    logger.info("Core 설정 모듈 로드 성공")
except ImportError as e:
    logger.warning(f"Core 설정 모듈을 찾을 수 없습니다: {e}")
    CONFIG_ENABLED = False
    # 기본 설정 클래스 정의
    class Config:
        CLOVA_BASE_URL = "https://clovastudio.stream.ntruss.com"
        CLOVA_MODEL = "HCX-005"
        AI_PARAMS = {
            'topP': 0.8,
            'topK': 0,
            'maxTokens': 3000,
            'temperature': 0.2,
            'repeatPenalty': 1.3,
            'stopBefore': [],
            'includeAiFilters': True,
            'seed': 0
        }
        DEFAULT_STOCKS = {
            "삼성전자": "005930.KS", "삼전": "005930.KS", "samsung": "005930.KS",
            "SK하이닉스": "000660.KS", "하이닉스": "000660.KS", "sk": "000660.KS",
            "네이버": "035420.KS", "NAVER": "035420.KS", "naver": "035420.KS",
            "카카오": "035720.KS", "kakao": "035720.KS",
            "테슬라": "TSLA", "tesla": "TSLA", "테슬": "TSLA",
            "애플": "AAPL", "apple": "AAPL",
            "엔비디아": "NVDA", "nvidia": "NVDA",
            "마이크로소프트": "MSFT", "ms": "MSFT",
            "구글": "GOOGL", "google": "GOOGL",
            "KOSPI": "^KS11", "KOSDAQ": "^KQ11", "NASDAQ": "^IXIC", 
            "S&P 500": "^GSPC", "USD/KRW": "KRW=X"
        }
    
    def get_api_key():
        """CLOVA Studio API 키 가져오기"""
        try:
            return st.secrets.get("CLOVA_STUDIO_API_KEY", "")
        except:
            return os.getenv("CLOVA_STUDIO_API_KEY", "")

try:
    from core.data_collector import get_real_time_market_data, get_recent_news, get_stock_data
    DATA_COLLECTOR_ENABLED = True
    logger.info("Core 데이터 수집 모듈 로드 성공")
except ImportError as e:
    logger.warning(f"Core 데이터 수집 모듈을 찾을 수 없습니다: {e}")
    DATA_COLLECTOR_ENABLED = False

try:
    from portfolio_parser import parse_user_portfolio
    PORTFOLIO_PARSER_ENABLED = True
    logger.info("포트폴리오 파서 모듈 로드 성공")
except ImportError as e:
    logger.warning(f"포트폴리오 파서 모듈을 찾을 수 없습니다: {e}")
    PORTFOLIO_PARSER_ENABLED = False

try:
    from chart_utils import create_stock_chart, display_market_metrics
    CHART_UTILS_ENABLED = True
    logger.info("차트 유틸리티 모듈 로드 성공")
except ImportError as e:
    logger.warning(f"차트 유틸리티 모듈을 찾을 수 없습니다: {e}")
    CHART_UTILS_ENABLED = False

# AI 클라이언트 (Core 폴더에서 로드)
try:
    from core.ai_client import EnhancedHyperCLOVAXClient
    AI_CLIENT_CLASS = EnhancedHyperCLOVAXClient
    AI_CLIENT_ENABLED = True
    logger.info("Core AI 클라이언트 로드 성공")
except ImportError as e:
    logger.warning(f"Core AI 클라이언트를 찾을 수 없습니다: {e}")
    AI_CLIENT_ENABLED = False

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

# 기본 기능들 (모듈이 없을 경우 대체)
@st.cache_data(ttl=300)  # 5분 캐시
def fallback_get_market_data():
    """기본 시장 데이터 수집 (대체 함수)"""
    try:
        collected_time = datetime.now()
        
        indices = {
            "KOSPI": "^KS11",
            "KOSDAQ": "^KQ11",
            "삼성전자": "005930.KS",
            "SK하이닉스": "000660.KS",
            "NASDAQ": "^IXIC", 
            "S&P 500": "^GSPC",
            "USD/KRW": "KRW=X"
        }
        
        market_data = {}
        for name, ticker in indices.items():
            try:
                data = yf.Ticker(ticker).history(period="2d", interval="5m")
                if not data.empty:
                    current = data['Close'].iloc[-1]
                    prev = data['Close'].iloc[0]
                    change = ((current - prev) / prev) * 100
                    
                    market_data[name] = {
                        'current': current,
                        'change': change,
                        'volume': data['Volume'].iloc[-1] if not data['Volume'].empty else 0,
                        'collected_at': collected_time.strftime('%H:%M:%S'),
                        'timestamp': collected_time
                    }
            except Exception as e:
                logger.warning(f"{name} 데이터 수집 실패: {e}")
                continue
        
        return market_data
    except Exception as e:
        logger.error(f"시장 데이터 수집 오류: {e}")
        return {}

@st.cache_data(ttl=1800)  # 30분 캐시
def fallback_get_news():
    """기본 뉴스 데이터 수집 (대체 함수)"""
    try:
        collected_time = datetime.now()
        
        news_sources = [
            'https://feeds.finance.yahoo.com/rss/2.0/headline'
        ]
        
        articles = []
        for url in news_sources:
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries[:3]:
                    articles.append({
                        'title': entry.get('title', ''),
                        'summary': entry.get('summary', ''),
                        'published': entry.get('published', ''),
                        'source': feed.feed.get('title', 'News'),
                        'collected_at': collected_time.strftime('%H:%M:%S')
                    })
            except Exception as e:
                logger.warning(f"뉴스 수집 실패 ({url}): {e}")
                continue
        
        return articles[:6]
    except Exception as e:
        logger.error(f"뉴스 수집 오류: {e}")
        return []

def fallback_parse_portfolio(question):
    """기본 포트폴리오 파싱 (대체 함수)"""
    import re
    
    portfolio_info = {}
    
    # 종목명 추출
    stock_mapping = {
        "삼성전자": "005930.KS", "삼전": "005930.KS",
        "SK하이닉스": "000660.KS", "하이닉스": "000660.KS",
        "네이버": "035420.KS", "NAVER": "035420.KS",
        "카카오": "035720.KS", "kakao": "035720.KS",
        "테슬라": "TSLA", "tesla": "TSLA",
        "애플": "AAPL", "apple": "AAPL",
        "엔비디아": "NVDA", "nvidia": "NVDA"
    }
    
    for korean_name, ticker in stock_mapping.items():
        if korean_name.lower() in question.lower():
            portfolio_info['stock'] = korean_name
            portfolio_info['ticker'] = ticker
            break
    
    # 매수가 추출
    price_patterns = [
        r'(\d+)만원',
        r'(\d+)천원',
        r'(\d+,?\d*\.?\d*)원',
        r'(\d+,?\d*\.?\d*)'
    ]
    
    for pattern in price_patterns:
        matches = re.findall(pattern, question)
        if matches:
            price_str = matches[0].replace(',', '')
            try:
                if '만원' in question:
                    portfolio_info['buy_price'] = float(price_str) * 10000
                elif '천원' in question:
                    portfolio_info['buy_price'] = float(price_str) * 1000
                else:
                    price = float(price_str)
                    if price < 1000:
                        portfolio_info['buy_price'] = price * 10000
                    else:
                        portfolio_info['buy_price'] = price
                break
            except:
                continue
    
    # 보유 주식 수 추출
    share_patterns = [r'(\d+)주', r'(\d+)개', r'(\d+)장']
    
    for pattern in share_patterns:
        matches = re.findall(pattern, question)
        if matches:
            try:
                portfolio_info['shares'] = int(matches[0])
                break
            except:
                continue
    
    return portfolio_info

def fallback_display_metrics(market_data):
    """기본 메트릭 표시 (대체 함수)"""
    if not market_data:
        st.info("시장 데이터 로딩 중...")
        return
    
    key_indices = ["KOSPI", "KOSDAQ", "NASDAQ", "S&P 500"]
    
    cols = st.columns(len(key_indices))
    
    for i, index_name in enumerate(key_indices):
        if index_name in market_data:
            data = market_data[index_name]
            with cols[i]:
                st.metric(
                    label=index_name,
                    value=f"{data['current']:.2f}",
                    delta=f"{data['change']:+.2f}%",
                    delta_color="normal"
                )

def fallback_create_chart(data, ticker):
    """기본 차트 생성 (대체 함수)"""
    fig = go.Figure(data=go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name=ticker
    ))
    
    fig.update_layout(
        title=f"{ticker} 주가 차트",
        yaxis_title="Price",
        xaxis_title="Date",
        template="plotly_white",
        height=500
    )
    
    return fig

# 기본 AI 클라이언트 (대체)
class FallbackHyperCLOVAXClient:
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

class IntegratedInvestmentAdvisor:
    """통합된 투자 어드바이저"""
    
    def __init__(self):
        self.session_id = self._init_session()
        
        # 보안 및 에러 처리 초기화 (활성화된 경우)
        if ERROR_HANDLER_ENABLED:
            try:
                self.error_handler, self.feedback_collector = init_error_handling()
            except Exception as e:
                logger.warning(f"오류 처리 초기화 실패: {e}")
                self.error_handler = None
                self.feedback_collector = None
        
        # 마케팅 시스템 초기화 (활성화된 경우)
        if MARKETING_ENABLED:
            try:
                self.marketing_system = init_marketing_system()
            except Exception as e:
                logger.warning(f"마케팅 시스템 초기화 실패: {e}")
                self.marketing_system = None
    
    def _init_session(self) -> str:
        """세션 초기화"""
        if 'session_id' not in st.session_state:
            st.session_state.session_id = str(uuid.uuid4())
        
        if 'session_start' not in st.session_state:
            st.session_state.session_start = datetime.now()
        
        # 기능 활성화 상태 표시
        if 'feature_status' not in st.session_state:
            st.session_state.feature_status = {
                'security': SECURITY_ENABLED,
                'error_handler': ERROR_HANDLER_ENABLED,
                'marketing': MARKETING_ENABLED,
                'alerts': ALERTS_ENABLED,
                'advanced_features': ADVANCED_FEATURES_ENABLED,
                'backtesting': BACKTESTING_ENABLED,
                'enhanced_features': ENHANCED_FEATURES_ENABLED,
                'ai_client': AI_CLIENT_ENABLED,
                'config': CONFIG_ENABLED,
                'data_collector': DATA_COLLECTOR_ENABLED,
                'portfolio_parser': PORTFOLIO_PARSER_ENABLED,
                'chart_utils': CHART_UTILS_ENABLED
            }
        
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
            if ERROR_HANDLER_ENABLED and self.error_handler:
                try:
                    error_info = self.error_handler.handle_secure_error(e, "main_app")
                    st.error(f"서비스에 일시적인 문제가 발생했습니다. (오류 ID: {error_info['error_id']})")
                    if self.feedback_collector:
                        self.feedback_collector.show_feedback_form(f"Main app error: {error_info['error_id']}")
                except:
                    st.error(f"오류 발생: {str(e)}")
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
        
        # 시스템 상태 확인 (관리자 모드)
        if st.secrets.get("ADMIN_MODE", False):
            with st.expander("🔧 시스템 상태 (관리자)", expanded=False):
                self._show_system_status()
        
        # 실시간 데이터 로드
        with st.spinner("📊 실시간 시장 데이터 로딩 중..."):
            if DATA_COLLECTOR_ENABLED:
                market_data = get_real_time_market_data()
                news_data = get_recent_news()
            else:
                market_data = fallback_get_market_data()
                news_data = fallback_get_news()
        
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
                try:
                    integrate_realtime_alerts()
                except Exception as e:
                    st.error(f"실시간 알림 모듈 오류: {str(e)}")
                    st.info("기본 알림 기능이 비활성화되었습니다.")
            tab_index += 1
        
        # 고급 기능 탭
        if ADVANCED_FEATURES_ENABLED:
            with main_tabs[tab_index]:
                try:
                    render_advanced_features()
                except Exception as e:
                    st.error(f"고급 기능 모듈 오류: {str(e)}")
                    st.info("고급 기능이 비활성화되었습니다.")
            tab_index += 1
        
        # 백테스팅 탭
        if BACKTESTING_ENABLED:
            with main_tabs[tab_index]:
                try:
                    render_backtesting_system()
                except Exception as e:
                    st.error(f"백테스팅 모듈 오류: {str(e)}")
                    st.info("백테스팅 기능이 비활성화되었습니다.")
            tab_index += 1
        
        # 기술적 분석 탭
        if ENHANCED_FEATURES_ENABLED:
            with main_tabs[tab_index]:
                try:
                    advanced_analytics = integrate_advanced_features()
                    portfolio_data = st.session_state.get('monitored_portfolio', [])
                    advanced_analytics.render_advanced_dashboard(
                        portfolio_data=portfolio_data,
                        news_data=news_data
                    )
                except Exception as e:
                    st.error(f"기술적 분석 모듈 오류: {str(e)}")
                    st.info("기술적 분석 기능이 비활성화되었습니다.")
            tab_index += 1
        
        # 면책조항
        if SECURITY_ENABLED:
            try:
                compliance_manager.show_investment_disclaimer()
            except:
                self._show_basic_disclaimer()
        else:
            self._show_basic_disclaimer()
        
        # 만든이 정보
        self._render_creator_info()
    
    def _show_system_status(self):
        """시스템 상태 표시"""
        st.markdown("#### 🔍 모듈 로드 상태")
        
        status = st.session_state.feature_status
        
        cols = st.columns(4)
        modules = [
            ("보안", status['security']),
            ("오류처리", status['error_handler']),
            ("마케팅", status['marketing']),
            ("알림", status['alerts']),
            ("고급기능", status['advanced_features']),
            ("백테스팅", status['backtesting']),
            ("기술분석", status['enhanced_features']),
            ("AI클라이언트", status['ai_client']),
            ("설정", status['config']),
            ("데이터수집", status['data_collector']),
            ("포트폴리오", status['portfolio_parser']),
            ("차트", status['chart_utils'])
        ]
        
        for i, (name, enabled) in enumerate(modules):
            with cols[i % 4]:
                if enabled:
                    st.success(f"✅ {name}")
                else:
                    st.error(f"❌ {name}")
        
        if ERROR_HANDLER_ENABLED:
            try:
                show_service_status()
            except:
                st.info("서비스 상태 모니터링을 사용할 수 없습니다.")
    
    def _show_basic_disclaimer(self):
        """기본 면책조항"""
        st.markdown("""
        <div style="background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%); border: 2px solid #ff6b35; border-radius: 0.8rem; padding: 1.5rem; margin: 1rem 0;">
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
    
    def _render_header(self, current_time):
        """헤더 렌더링"""
        st.markdown('<div class="main-header">🤖 HyperCLOVA X AI 투자 어드바이저</div>', unsafe_allow_html=True)
        
        # 모듈 상태 표시
        enabled_count = sum(st.session_state.feature_status.values())
        total_count = len(st.session_state.feature_status)
        
        st.markdown(f'<p style="text-align: center; color: #666; font-size: 1.1rem;">🔴 실시간 분석 • 📊 Live Market Data • 🚀 {enabled_count}/{total_count} Modules Active</p>', unsafe_allow_html=True)
        st.markdown(f'<p style="text-align: center; color: #999; font-size: 0.9rem;">📅 {current_time.strftime("%Y년 %m월 %d일 %H시 %M분 %S초")}</p>', unsafe_allow_html=True)
    
    def _render_sidebar(self, market_data):
        """사이드바 렌더링"""
        # AI 클라이언트 선택
        if AI_CLIENT_ENABLED:
            ai_client = AI_CLIENT_CLASS()
        else:
            ai_client = FallbackHyperCLOVAXClient()
        
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
                    if MARKETING_ENABLED and self.marketing_system:
                        try:
                            track_user_action("sidebar_question_clicked")
                        except:
                            pass
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
                "enabled": AI_CLIENT_ENABLED
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
                bg_color = "#e8f5e8" if feature["enabled"] else "#ffe6e6"
                st.markdown(f"""
                <div style="background: {bg_color}; padding: 1.5rem; border-radius: 0.5rem; text-align: center; height: 150px;">
                    <div style="font-size: 2rem;">{feature["icon"]}</div>
                    <h4 style="margin: 0.5rem 0;">{feature["title"]} {status}</h4>
                    <p style="font-size: 0.9rem; color: #666;">{feature["desc"]}</p>
                </div>
                """, unsafe_allow_html=True)
        
        # 시장 개요
        if market_data:
            st.markdown("#### 📈 오늘의 시장")
            if CHART_UTILS_ENABLED:
                display_market_metrics(market_data)
            else:
                fallback_display_metrics(market_data)
        
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
            
            # 보안 체크 (활성화된 경우)
            if SECURITY_ENABLED:
                if not secure_config.check_rate_limit(self.session_id):
                    st.error("🚫 요청이 너무 빈번합니다. 잠시 후 다시 시도해주세요.")
                    return
                
                # 입력 무력화
                sanitized_question = secure_config.sanitize_input(st.session_state.user_question)
                st.session_state.user_question = sanitized_question
            
            # 포트폴리오 정보 추출
            if PORTFOLIO_PARSER_ENABLED:
                portfolio_info = parse_user_portfolio(st.session_state.user_question)
            else:
                portfolio_info = fallback_parse_portfolio(st.session_state.user_question)
            
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
                    response = ai_client.get_real_time_analysis(
                        st.session_state.user_question,
                        market_data,
                        news_data
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
                        if DATA_COLLECTOR_ENABLED:
                            stock_data = get_stock_data(portfolio_info['ticker'])
                        else:
                            # 기본 방식으로 데이터 수집
                            stock = yf.Ticker(portfolio_info['ticker'])
                            stock_data = stock.history(period="6mo")
                        
                        if stock_data is not None and not stock_data.empty:
                            if CHART_UTILS_ENABLED:
                                chart = create_stock_chart(stock_data, portfolio_info['ticker'])
                            else:
                                chart = fallback_create_chart(stock_data, portfolio_info['ticker'])
                            st.plotly_chart(chart, use_container_width=True)
                    except Exception as e:
                        st.warning(f"차트를 불러올 수 없습니다: {str(e)}")
                
                # 마케팅 CTA (활성화된 경우)
                if MARKETING_ENABLED and self.marketing_system:
                    try:
                        track_user_action("analysis_completed")
                        context = "general"
                        if portfolio_info:
                            # 간단한 수익률 계산
                            if portfolio_info.get('buy_price') and portfolio_info.get('ticker'):
                                try:
                                    current_data = yf.Ticker(portfolio_info['ticker']).history(period="1d")
                                    if not current_data.empty:
                                        current_price = current_data['Close'].iloc[-1]
                                        profit_rate = ((current_price - portfolio_info['buy_price']) / portfolio_info['buy_price']) * 100
                                        if profit_rate < -15:
                                            context = "high_loss"
                                        elif profit_rate > 25:
                                            context = "high_profit"
                                except:
                                    pass
                        show_marketing_cta(context, portfolio_info, response)
                    except Exception as e:
                        logger.warning(f"마케팅 CTA 오류: {e}")
                
            except Exception as e:
                progress_bar.empty()
                status_text.empty()
                
                # 에러 처리
                if ERROR_HANDLER_ENABLED and self.error_handler:
                    try:
                        error_info = self.error_handler.handle_secure_error(e, "ai_analysis")
                        st.markdown(f'<div class="error-message">', unsafe_allow_html=True)
                        st.markdown(f"🚨 **분석 중 오류 발생**\n\n{error_info['user_message']}\n\n오류 ID: {error_info['error_id']}")
                        st.markdown('</div>', unsafe_allow_html=True)
                        if self.feedback_collector:
                            self.feedback_collector.show_feedback_form(f"Analysis error: {error_info['error_id']}")
                    except:
                        st.error(f"❌ 오류 발생: {str(e)}")
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
                        if MARKETING_ENABLED and self.marketing_system:
                            try:
                                track_user_action("sample_question_clicked")
                            except:
                                pass
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
        else:
            st.markdown("### 🔧 문제 해결 방법")
            st.markdown("""
            1. **페이지 새로고침**: F5 키를 눌러 페이지를 새로고침하세요
            2. **브라우저 캐시 삭제**: Ctrl+Shift+Delete로 캐시를 삭제하세요
            3. **다른 브라우저 시도**: Chrome, Firefox, Edge 등 다른 브라우저로 접속해보세요
            4. **인터넷 연결 확인**: 네트워크 연결 상태를 확인하세요
            5. **잠시 후 재시도**: 서버가 일시적으로 과부하일 수 있습니다
            """)

if __name__ == "__main__":
    main()
