"""
performance_utils.py - 성능 최적화 및 사용자 경험 개선
"""

import streamlit as st
import time
import threading
import asyncio
import concurrent.futures
from datetime import datetime, timedelta
import pickle
import hashlib
import logging
from typing import Dict, Any, Optional, List
import pandas as pd

logger = logging.getLogger(__name__)

class CacheManager:
    """향상된 캐시 관리 시스템"""
    
    def __init__(self, cache_dir: str = ".cache"):
        self.cache_dir = cache_dir
        self.memory_cache = {}
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0
        }
        
        # 캐시 디렉토리 생성
        import os
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
    
    def _generate_cache_key(self, func_name: str, *args, **kwargs) -> str:
        """캐시 키 생성"""
        key_data = f"{func_name}_{str(args)}_{str(sorted(kwargs.items()))}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """캐시에서 데이터 조회"""
        # 메모리 캐시 먼저 확인
        if key in self.memory_cache:
            item = self.memory_cache[key]
            if item['expires'] > datetime.now():
                self.cache_stats['hits'] += 1
                return item['data']
            else:
                del self.memory_cache[key]
        
        # 디스크 캐시 확인
        try:
            cache_file = f"{self.cache_dir}/{key}.pkl"
            import os
            if os.path.exists(cache_file):
                with open(cache_file, 'rb') as f:
                    item = pickle.load(f)
                    if item['expires'] > datetime.now():
                        # 메모리 캐시에도 저장
                        self.memory_cache[key] = item
                        self.cache_stats['hits'] += 1
                        return item['data']
                    else:
                        os.remove(cache_file)
        except Exception as e:
            logger.warning(f"캐시 조회 오류: {e}")
        
        self.cache_stats['misses'] += 1
        return None
    
    def set(self, key: str, data: Any, ttl_seconds: int = 3600):
        """캐시에 데이터 저장"""
        expires = datetime.now() + timedelta(seconds=ttl_seconds)
        item = {'data': data, 'expires': expires}
        
        # 메모리 캐시 저장 (최대 100개)
        if len(self.memory_cache) >= 100:
            # 가장 오래된 항목 제거
            oldest_key = min(self.memory_cache.keys(), 
                           key=lambda k: self.memory_cache[k]['expires'])
            del self.memory_cache[oldest_key]
            self.cache_stats['evictions'] += 1
        
        self.memory_cache[key] = item
        
        # 디스크 캐시 저장
        try:
            cache_file = f"{self.cache_dir}/{key}.pkl"
            with open(cache_file, 'wb') as f:
                pickle.dump(item, f)
        except Exception as e:
            logger.warning(f"캐시 저장 오류: {e}")
    
    def clear(self):
        """모든 캐시 삭제"""
        self.memory_cache.clear()
        try:
            import os
            import glob
            for cache_file in glob.glob(f"{self.cache_dir}/*.pkl"):
                os.remove(cache_file)
        except Exception as e:
            logger.warning(f"캐시 삭제 오류: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """캐시 통계 반환"""
        total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
        hit_rate = (self.cache_stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'hit_rate': f"{hit_rate:.1f}%",
            'total_requests': total_requests,
            'memory_items': len(self.memory_cache),
            **self.cache_stats
        }

class DataPreloader:
    """데이터 사전 로딩 시스템"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager
        self.preload_tasks = {}
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=3)
    
    def preload_market_data(self):
        """시장 데이터 사전 로딩"""
        def _load_data():
            try:
                from data_collector import get_real_time_market_data
                return get_real_time_market_data()
            except Exception as e:
                logger.error(f"시장 데이터 사전 로딩 실패: {e}")
                return {}
        
        if 'market_data' not in self.preload_tasks:
            self.preload_tasks['market_data'] = self.executor.submit(_load_data)
    
    def preload_news_data(self):
        """뉴스 데이터 사전 로딩"""
        def _load_data():
            try:
                from data_collector import get_recent_news
                return get_recent_news()
            except Exception as e:
                logger.error(f"뉴스 데이터 사전 로딩 실패: {e}")
                return []
        
        if 'news_data' not in self.preload_tasks:
            self.preload_tasks['news_data'] = self.executor.submit(_load_data)
    
    def get_preloaded_data(self, data_type: str, timeout: float = 5.0):
        """사전 로딩된 데이터 조회"""
        if data_type in self.preload_tasks:
            try:
                return self.preload_tasks[data_type].result(timeout=timeout)
            except concurrent.futures.TimeoutError:
                logger.warning(f"{data_type} 사전 로딩 시간 초과")
                return None
            except Exception as e:
                logger.error(f"{data_type} 사전 로딩 오류: {e}")
                return None
        return None

class ProgressTracker:
    """진행률 추적 및 사용자 피드백"""
    
    def __init__(self):
        self.current_step = 0
        self.total_steps = 0
        self.progress_bar = None
        self.status_text = None
    
    def start(self, total_steps: int, title: str = "처리 중..."):
        """진행률 추적 시작"""
        self.total_steps = total_steps
        self.current_step = 0
        
        st.markdown(f"### {title}")
        self.progress_bar = st.progress(0)
        self.status_text = st.empty()
    
    def update(self, step_name: str):
        """진행률 업데이트"""
        self.current_step += 1
        progress = self.current_step / self.total_steps
        
        if self.progress_bar:
            self.progress_bar.progress(progress)
        
        if self.status_text:
            self.status_text.text(f"🔄 {step_name} ({self.current_step}/{self.total_steps})")
    
    def complete(self, success_message: str = "완료!"):
        """진행률 추적 완료"""
        if self.progress_bar:
            self.progress_bar.progress(1.0)
        
        if self.status_text:
            self.status_text.text(f"✅ {success_message}")
        
        time.sleep(1)
        
        if self.progress_bar:
            self.progress_bar.empty()
        if self.status_text:
            self.status_text.empty()

class ErrorHandler:
    """향상된 오류 처리 시스템"""
    
    def __init__(self):
        self.error_log = []
        self.retry_attempts = {}
    
    def handle_api_error(self, error: Exception, context: str = ""):
        """API 오류 처리"""
        error_msg = str(error)
        timestamp = datetime.now()
        
        # 오류 로그 기록
        self.error_log.append({
            'timestamp': timestamp,
            'context': context,
            'error': error_msg,
            'type': type(error).__name__
        })
        
        # 특정 오류에 대한 사용자 친화적 메시지
        if "401" in error_msg or "authentication" in error_msg.lower():
            st.error("🔐 **인증 오류**: API 키를 확인해주세요.")
            self._show_api_key_help()
        elif "429" in error_msg or "rate limit" in error_msg.lower():
            st.warning("⏳ **사용량 한도 초과**: 잠시 후 다시 시도해주세요.")
            self._show_rate_limit_help()
        elif "timeout" in error_msg.lower():
            st.warning("⏱️ **시간 초과**: 네트워크 연결을 확인해주세요.")
            self._show_network_help()
        elif "404" in error_msg:
            st.error("🔍 **리소스 없음**: 요청한 데이터를 찾을 수 없습니다.")
        else:
            st.error(f"❌ **오류 발생**: {error_msg}")
        
        return False
    
    def _show_api_key_help(self):
        """API 키 설정 도움말"""
        with st.expander("🔧 API 키 설정 방법", expanded=False):
            st.markdown("""
            1. `.streamlit/secrets.toml` 파일 생성
            2. 다음 내용 추가:
            ```toml
            CLOVA_STUDIO_API_KEY = "your-api-key-here"
            ```
            3. 네이버 클라우드 플랫폼에서 API 키 발급
            """)
    
    def _show_rate_limit_help(self):
        """사용량 한도 도움말"""
        with st.expander("📊 사용량 관리 팁", expanded=False):
            st.markdown("""
            - 요청 간격을 늘려보세요
            - 캐시된 데이터를 활용하세요
            - 불필요한 반복 요청을 피하세요
            """)
    
    def _show_network_help(self):
        """네트워크 문제 도움말"""
        with st.expander("🌐 네트워크 문제 해결", expanded=False):
            st.markdown("""
            - 인터넷 연결 상태 확인
            - VPN 사용 시 해제 후 재시도
            - 방화벽 설정 확인
            """)
    
    def get_error_summary(self) -> Dict[str, Any]:
        """오류 요약 정보"""
        if not self.error_log:
            return {'total': 0, 'recent': []}
        
        recent_errors = [
            {
                'time': err['timestamp'].strftime('%H:%M:%S'),
                'context': err['context'],
                'type': err['type']
            }
            for err in self.error_log[-5:]  # 최근 5개
        ]
        
        return {
            'total': len(self.error_log),
            'recent': recent_errors
        }

class SessionManager:
    """세션 상태 관리"""
    
    @staticmethod
    def initialize_session():
        """세션 상태 초기화"""
        defaults = {
            'user_question': "",
            'selected_question': "",
            'analysis_history': [],
            'portfolio_data': [],
            'user_preferences': {
                'theme': 'default',
                'auto_refresh': True,
                'notifications': True
            },
            'last_analysis_time': None,
            'cache_manager': CacheManager(),
            'error_handler': ErrorHandler()
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
    
    @staticmethod
    def save_analysis_result(question: str, result: str, portfolio_info: dict = None):
        """분석 결과 저장"""
        if 'analysis_history' not in st.session_state:
            st.session_state.analysis_history = []
        
        analysis_record = {
            'timestamp': datetime.now(),
            'question': question,
            'result': result[:500] + "..." if len(result) > 500 else result,  # 요약 저장
            'portfolio_info': portfolio_info,
            'analysis_id': len(st.session_state.analysis_history) + 1
        }
        
        st.session_state.analysis_history.append(analysis_record)
        
        #
