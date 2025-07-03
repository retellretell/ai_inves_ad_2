"""
enhanced_error_handler.py - 강화된 오류 처리 및 복구 시스템
"""

import streamlit as st
import logging
import traceback
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Callable
from functools import wraps
import json

# 전용 오류 로거 설정
error_logger = logging.getLogger('investment_advisor_errors')
error_logger.setLevel(logging.ERROR)

if not error_logger.handlers:
    # 파일 핸들러
    file_handler = logging.FileHandler('app_errors.log')
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    error_logger.addHandler(file_handler)

class ServiceStatus:
    """서비스 상태 모니터링"""
    
    def __init__(self):
        self.services = {
            'hyperclova_x': {'status': 'unknown', 'last_check': None, 'error_count': 0},
            'market_data': {'status': 'unknown', 'last_check': None, 'error_count': 0},
            'news_feed': {'status': 'unknown', 'last_check': None, 'error_count': 0},
            'dart_api': {'status': 'unknown', 'last_check': None, 'error_count': 0},
            'naver_trends': {'status': 'unknown', 'last_check': None, 'error_count': 0}
        }
    
    def check_service_health(self, service_name: str) -> Dict[str, Any]:
        """서비스 상태 체크"""
        try:
            if service_name == 'hyperclova_x':
                return self._check_hyperclova_health()
            elif service_name == 'market_data':
                return self._check_market_data_health()
            elif service_name == 'news_feed':
                return self._check_news_health()
            elif service_name == 'dart_api':
                return self._check_dart_health()
            elif service_name == 'naver_trends':
                return self._check_naver_health()
            else:
                return {'status': 'unknown', 'message': '알 수 없는 서비스'}
        except Exception as e:
            error_logger.error(f"서비스 상태 체크 실패 ({service_name}): {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def _check_hyperclova_health(self) -> Dict[str, Any]:
        """HyperCLOVA X API 상태 체크"""
        try:
            from security_config import secure_config
            api_key = secure_config.get_api_key('clova_studio')
            
            if not api_key:
                return {'status': 'error', 'message': 'API 키가 설정되지 않음'}
            
            # 간단한 헬스체크 요청 (실제로는 더 가벼운 엔드포인트 사용)
            headers = {
                'X-NCP-CLOVASTUDIO-API-KEY': api_key,
                'Content-Type': 'application/json'
            }
            
            # 실제로는 헬스체크 전용 엔드포인트가 있다면 그것을 사용
            response = requests.get(
                'https://clovastudio.stream.ntruss.com/health',  # 가상의 헬스체크 엔드포인트
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 200:
                return {'status': 'healthy', 'message': '정상 작동 중'}
            else:
                return {'status': 'degraded', 'message': f'응답 코드: {response.status_code}'}
                
        except requests.exceptions.ConnectTimeout:
            return {'status': 'error', 'message': '연결 시간 초과'}
        except requests.exceptions.ConnectionError:
            return {'status': 'error', 'message': '연결 오류'}
        except Exception as e:
            return {'status': 'error', 'message': f'알 수 없는 오류: {str(e)}'}
    
    def _check_market_data_health(self) -> Dict[str, Any]:
        """시장 데이터 API 상태 체크"""
        try:
            import yfinance as yf
            # 간단한 데이터 요청으로 상태 확인
            ticker = yf.Ticker("^KS11")  # 코스피 지수
            data = ticker.history(period="1d", interval="1m")
            
            if not data.empty:
                return {'status': 'healthy', 'message': '시장 데이터 정상'}
            else:
                return {'status': 'degraded', 'message': '데이터 없음'}
                
        except Exception as e:
            return {'status': 'error', 'message': f'시장 데이터 오류: {str(e)}'}
    
    def _check_news_health(self) -> Dict[str, Any]:
        """뉴스 피드 상태 체크"""
        try:
            import feedparser
            # 하나의 뉴스 소스만 빠르게 체크
            feed = feedparser.parse('https://feeds.finance.yahoo.com/rss/2.0/headline')
            
            if len(feed.entries) > 0:
                return {'status': 'healthy', 'message': '뉴스 피드 정상'}
            else:
                return {'status': 'degraded', 'message': '뉴스 데이터 부족'}
                
        except Exception as e:
            return {'status': 'error', 'message': f'뉴스 피드 오류: {str(e)}'}
    
    def _check_dart_health(self) -> Dict[str, Any]:
        """DART API 상태 체크"""
        try:
            from security_config import secure_config
            api_key = secure_config.get_api_key('dart')
            
            if not api_key:
                return {'status': 'disabled', 'message': 'DART API 키 미설정'}
            
            # DART API 간단 상태 체크
            response = requests.get(
                "https://opendart.fss.or.kr/api/list.json",
                params={'crtfc_key': api_key, 'page_no': 1, 'page_count': 1},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == '000':
                    return {'status': 'healthy', 'message': 'DART API 정상'}
                else:
                    return {'status': 'error', 'message': f"DART 오류: {data.get('message', '알 수 없음')}"}
            else:
                return {'status': 'error', 'message': f'HTTP {response.status_code}'}
                
        except Exception as e:
            return {'status': 'error', 'message': f'DART API 오류: {str(e)}'}
    
    def _check_naver_health(self) -> Dict[str, Any]:
        """네이버 API 상태 체크"""
        try:
            from security_config import secure_config
            client_id, client_secret = secure_config.get_api_key('naver_client_id'), secure_config.get_api_key('naver_client_secret')
            
            if not client_id or not client_secret:
                return {'status': 'disabled', 'message': '네이버 API 키 미설정'}
            
            return {'status': 'healthy', 'message': '네이버 API 키 설정됨'}
            
        except Exception as e:
            return {'status': 'error', 'message': f'네이버 API 오류: {str(e)}'}
    
    def update_service_status(self, service_name: str, status_info: Dict[str, Any]):
        """서비스 상태 업데이트"""
        if service_name in self.services:
            self.services[service_name].update({
                'status': status_info['status'],
                'last_check': datetime.now(),
                'message': status_info.get('message', ''),
                'error_count': self.services[service_name]['error_count'] + (1 if status_info['status'] == 'error' else 0)
            })

class FallbackDataProvider:
    """대체 데이터 제공자"""
    
    def __init__(self):
        self.cache_file = '.fallback_cache.json'
        self.mock_data = {
            'market_data': {
                'KOSPI': {'current': 3066.01, 'change': -0.59},
                'NASDAQ': {'current': 20392.93, 'change': 1.00},
                'S&P 500': {'current': 6227.27, 'change': 0.51},
                'USD/KRW': {'current': 1352.48, 'change': -0.14}
            },
            'news_data': [
                {'title': '시장 상황 안정세 지속', 'source': 'Cache', 'published': '최근'},
                {'title': 'AI 관련 주식 관심 증가', 'source': 'Cache', 'published': '최근'},
                {'title': '반도체 업종 전망 긍정적', 'source': 'Cache', 'published': '최근'}
            ]
        }
    
    def get_fallback_market_data(self) -> Dict[str, Any]:
        """대체 시장 데이터 제공"""
        try:
            # 캐시된 데이터 우선 시도
            cached_data = self._load_cached_data('market_data')
            if cached_data:
                return cached_data
            
            # 목업 데이터 반환
            return self.mock_data['market_data']
            
        except Exception as e:
            error_logger.error(f"대체 시장 데이터 제공 실패: {str(e)}")
            return self.mock_data['market_data']
    
    def get_fallback_news_data(self) -> list:
        """대체 뉴스 데이터 제공"""
        try:
            cached_data = self._load_cached_data('news_data')
            if cached_data:
                return cached_data
            
            return self.mock_data['news_data']
            
        except Exception as e:
            error_logger.error(f"대체 뉴스 데이터 제공 실패: {str(e)}")
            return self.mock_data['news_data']
    
    def _load_cached_data(self, data_type: str) -> Optional[Any]:
        """캐시된 데이터 로드"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
                    
                cache_entry = cache.get(data_type)
                if cache_entry:
                    # 캐시 유효성 확인 (1시간 이내)
                    cache_time = datetime.fromisoformat(cache_entry['timestamp'])
                    if datetime.now() - cache_time < timedelta(hours=1):
                        return cache_entry['data']
            
            return None
            
        except Exception as e:
            error_logger.warning(f"캐시 데이터 로드 실패 ({data_type}): {str(e)}")
            return None
    
    def save_cache_data(self, data_type: str, data: Any):
        """데이터 캐시 저장"""
        try:
            cache = {}
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
            
            cache[data_type] = {
                'data': data,
                'timestamp': datetime.now().isoformat()
            }
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            error_logger.warning(f"캐시 데이터 저장 실패 ({data_type}): {str(e)}")

class RobustErrorHandler:
    """강건한 오류 처리 시스템"""
    
    def __init__(self):
        self.service_status = ServiceStatus()
        self.fallback_provider = FallbackDataProvider()
        self.retry_config = {
            'max_retries': 3,
            'base_delay': 1,
            'backoff_factor': 2
        }
    
    def with_error_handling(self, service_name: str = "unknown"):
        """오류 처리 데코레이터"""
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                last_exception = None
                
                for attempt in range(self.retry_config['max_retries']):
                    try:
                        result = func(*args, **kwargs)
                        
                        # 성공 시 서비스 상태 업데이트
                        self.service_status.update_service_status(
                            service_name, 
                            {'status': 'healthy', 'message': '정상 작동'}
                        )
                        
                        # 성공한 데이터 캐시 저장
                        if service_name in ['market_data', 'news_data'] and result:
                            self.fallback_provider.save_cache_data(service_name, result)
                        
                        return result
                        
                    except Exception as e:
                        last_exception = e
                        error_logger.error(
                            f"Attempt {attempt + 1} failed for {service_name}: {str(e)}\n"
                            f"Traceback: {traceback.format_exc()}"
                        )
                        
                        # 재시도 전 대기
                        if attempt < self.retry_config['max_retries'] - 1:
                            delay = self.retry_config['base_delay'] * (
                                self.retry_config['backoff_factor'] ** attempt
                            )
                            time.sleep(delay)
                
                # 모든 재시도 실패 시
                self.service_status.update_service_status(
                    service_name,
                    {'status': 'error', 'message': str(last_exception)}
                )
                
                # 대체 데이터 제공 시도
                return self._provide_fallback_data(service_name, last_exception)
            
            return wrapper
        return decorator
    
    def _provide_fallback_data(self, service_name: str, original_error: Exception):
        """대체 데이터 제공"""
        try:
            if service_name == 'market_data':
                fallback_data = self.fallback_provider.get_fallback_market_data()
                st.warning("🔄 시장 데이터 서비스에 일시적 문제가 있어 캐시된 데이터를 사용합니다.")
                return fallback_data
                
            elif service_name == 'news_data':
                fallback_data = self.fallback_provider.get_fallback_news_data()
                st.warning("🔄 뉴스 서비스에 일시적 문제가 있어 캐시된 데이터를 사용합니다.")
                return fallback_data
                
            elif service_name == 'hyperclova_x':
                st.error("🚨 AI 분석 서비스에 일시적 문제가 있습니다. 잠시 후 다시 시도해주세요.")
                self._show_alternative_options()
                raise original_error
                
            else:
                # 기본 대체 동작
                st.warning(f"⚠️ {service_name} 서비스에 일시적 문제가 있습니다.")
                return None
                
        except Exception as e:
            error_logger.critical(f"대체 데이터 제공도 실패 ({service_name}): {str(e)}")
            raise original_error
    
    def _show_alternative_options(self):
        """대안 옵션 표시"""
        with st.expander("🔧 대안 서비스 이용 방법", expanded=True):
            st.markdown("""
            **AI 분석 서비스 이용이 어려운 경우:**
            
            1. **📞 전문가 상담**: 미래에셋증권 고객센터 1588-6666
            2. **💻 웹사이트**: [미래에셋증권 공식 홈페이지](https://securities.miraeasset.com)
            3. **📱 모바일앱**: 'mPOP' 앱 다운로드
            4. **⏰ 잠시 후 재시도**: 서비스가 곧 복구될 예정입니다
            
            **현재 이용 가능한 기능:**
            - 실시간 시장 데이터 (제한적)
            - 기본 투자 정보
            - 과거 분석 결과 (캐시)
            """)
    
    def display_system_status(self):
        """시스템 상태 표시"""
        st.markdown("### 🔍 시스템 상태 모니터링")
        
        # 실시간 상태 체크
        with st.spinner("시스템 상태 확인 중..."):
            for service_name in self.service_status.services.keys():
                status_info = self.service_status.check_service_health(service_name)
                self.service_status.update_service_status(service_name, status_info)
        
        # 상태 표시
        cols = st.columns(len(self.service_status.services))
        
        for i, (service_name, service_info) in enumerate(self.service_status.services.items()):
            with cols[i]:
                status = service_info['status']
                
                if status == 'healthy':
                    st.success(f"✅ {service_name.replace('_', ' ').title()}")
                elif status == 'degraded':
                    st.warning(f"⚠️ {service_name.replace('_', ' ').title()}")
                elif status == 'disabled':
                    st.info(f"ℹ️ {service_name.replace('_', ' ').title()}")
                else:
                    st.error(f"❌ {service_name.replace('_', ' ').title()}")
                
                if service_info.get('message'):
                    st.caption(service_info['message'])
                
                if service_info.get('last_check'):
                    st.caption(f"확인: {service_info['last_check'].strftime('%H:%M')}")

class UserFeedbackCollector:
    """사용자 피드백 수집"""
    
    def __init__(self):
        self.feedback_file = 'user_feedback.json'
    
    def show_feedback_form(self, error_context: str = ""):
        """피드백 폼 표시"""
        with st.expander("💬 서비스 개선을 위한 피드백", expanded=False):
            st.markdown("**문제점이나 개선사항을 알려주세요:**")
            
            feedback_type = st.selectbox(
                "피드백 유형",
                ["버그 신고", "기능 개선 제안", "사용성 문제", "기타"]
            )
            
            feedback_text = st.text_area(
                "상세 내용",
                placeholder="겪으신 문제나 개선 아이디어를 자세히 알려주세요...",
                height=100
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("피드백 제출", type="primary"):
                    if feedback_text.strip():
                        self._save_feedback({
                            'type': feedback_type,
                            'content': feedback_text,
                            'context': error_context,
                            'timestamp': datetime.now().isoformat(),
                            'session_id': st.session_state.get('session_id', 'anonymous')
                        })
                        st.success("피드백이 제출되었습니다. 감사합니다!")
                    else:
                        st.warning("피드백 내용을 입력해주세요.")
            
            with col2:
                if st.button("고객센터 연결"):
                    st.info("📞 미래에셋증권 고객센터: 1588-6666")
    
    def _save_feedback(self, feedback: Dict[str, Any]):
        """피드백 저장"""
        try:
            feedbacks = []
            if os.path.exists(self.feedback_file):
                with open(self.feedback_file, 'r', encoding='utf-8') as f:
                    feedbacks = json.load(f)
            
            feedbacks.append(feedback)
            
            with open(self.feedback_file, 'w', encoding='utf-8') as f:
                json.dump(feedbacks, f, ensure_ascii=False, indent=2)
                
            # 로그에도 기록
            error_logger.info(f"USER_FEEDBACK - Type: {feedback['type']}, Content: {feedback['content'][:100]}")
            
        except Exception as e:
            error_logger.error(f"피드백 저장 실패: {str(e)}")

def init_error_handling():
    """오류 처리 초기화"""
    if 'error_handler' not in st.session_state:
        st.session_state.error_handler = RobustErrorHandler()
    
    if 'feedback_collector' not in st.session_state:
        st.session_state.feedback_collector = UserFeedbackCollector()
    
    return st.session_state.error_handler, st.session_state.feedback_collector

# 편의 함수들
def handle_api_error(func: Callable, service_name: str = "api"):
    """API 오류 처리 헬퍼"""
    error_handler, _ = init_error_handling()
    return error_handler.with_error_handling(service_name)(func)

def show_service_status():
    """서비스 상태 표시 헬퍼"""
    error_handler, _ = init_error_handling()
    error_handler.display_system_status()

def collect_user_feedback(context: str = ""):
    """사용자 피드백 수집 헬퍼"""
    _, feedback_collector = init_error_handling()
    feedback_collector.show_feedback_form(context)
