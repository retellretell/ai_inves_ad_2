"""
security_config.py - 보안 강화 설정
"""

import streamlit as st
import os
import logging
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import json

# 보안 로깅 설정
security_logger = logging.getLogger('security')
security_logger.setLevel(logging.INFO)

# 보안 핸들러 추가
if not security_logger.handlers:
    handler = logging.FileHandler('security.log')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    security_logger.addHandler(handler)

class SecureConfig:
    """보안 강화된 설정 관리 클래스"""
    
    def __init__(self):
        self.api_keys = {}
        self.session_timeout = 3600  # 1시간
        self.max_requests_per_hour = 100
        self.encrypted_keys = {}
        
    def get_api_key(self, service: str) -> Optional[str]:
        """보안 강화된 API 키 조회"""
        try:
            # 1. Streamlit Secrets 우선 확인
            if hasattr(st, 'secrets'):
                key = st.secrets.get(f"{service.upper()}_API_KEY", "")
                if key and self._validate_api_key(key, service):
                    self._log_api_access(service, "secrets", True)
                    return key
            
            # 2. 환경변수 확인
            key = os.getenv(f"{service.upper()}_API_KEY", "")
            if key and self._validate_api_key(key, service):
                self._log_api_access(service, "env", True)
                return key
            
            # 3. 암호화된 키 파일 확인 (추가 보안)
            encrypted_key = self._load_encrypted_key(service)
            if encrypted_key:
                self._log_api_access(service, "encrypted", True)
                return encrypted_key
            
            self._log_api_access(service, "none", False)
            return None
            
        except Exception as e:
            security_logger.error(f"API 키 조회 오류 ({service}): {str(e)}")
            return None
    
    def _validate_api_key(self, key: str, service: str) -> bool:
        """API 키 유효성 검증"""
        if not key or len(key) < 10:
            return False
            
        # 서비스별 키 패턴 검증
        patterns = {
            'clova_studio': {'prefix': 'nv-', 'min_length': 32},
            'dart': {'prefix': '', 'min_length': 20},
            'naver': {'prefix': '', 'min_length': 16}
        }
        
        pattern = patterns.get(service.lower(), {'prefix': '', 'min_length': 10})
        
        if pattern['prefix'] and not key.startswith(pattern['prefix']):
            return False
            
        if len(key) < pattern['min_length']:
            return False
            
        return True
    
    def _load_encrypted_key(self, service: str) -> Optional[str]:
        """암호화된 키 파일에서 로드 (고급 보안)"""
        try:
            key_file = f".secure/{service}_key.enc"
            if os.path.exists(key_file):
                with open(key_file, 'r') as f:
                    encrypted_data = f.read()
                # 실제 운영에서는 KMS나 Vault 같은 키 관리 서비스 사용 권장
                return self._decrypt_key(encrypted_data)
        except Exception as e:
            security_logger.warning(f"암호화된 키 로드 실패 ({service}): {str(e)}")
        return None
    
    def _decrypt_key(self, encrypted_data: str) -> str:
        """키 복호화 (실제로는 더 강력한 암호화 사용)"""
        # 실제 운영환경에서는 AWS KMS, Azure Key Vault 등 사용
        # 여기는 예시용 간단 구현
        return encrypted_data  # 실제로는 복호화 로직 구현
    
    def _log_api_access(self, service: str, source: str, success: bool):
        """API 접근 로그"""
        user_ip = self._get_client_ip()
        security_logger.info(f"API_ACCESS - Service: {service}, Source: {source}, Success: {success}, IP: {user_ip}")
    
    def _get_client_ip(self) -> str:
        """클라이언트 IP 조회"""
        try:
            # Streamlit Cloud나 배포 환경에서 실제 IP 조회
            return st.context.headers.get('x-forwarded-for', 'unknown')
        except:
            return 'localhost'
    
    def check_rate_limit(self, user_id: str = "anonymous") -> bool:
        """요청 빈도 제한 체크"""
        try:
            if 'rate_limits' not in st.session_state:
                st.session_state.rate_limits = {}
            
            now = datetime.now()
            hour_key = now.strftime('%Y%m%d%H')
            user_key = f"{user_id}_{hour_key}"
            
            current_count = st.session_state.rate_limits.get(user_key, 0)
            
            if current_count >= self.max_requests_per_hour:
                security_logger.warning(f"RATE_LIMIT_EXCEEDED - User: {user_id}, Count: {current_count}")
                return False
            
            st.session_state.rate_limits[user_key] = current_count + 1
            return True
            
        except Exception as e:
            security_logger.error(f"Rate limit 체크 오류: {str(e)}")
            return True  # 오류 시 허용
    
    def sanitize_input(self, user_input: str) -> str:
        """사용자 입력 무력화"""
        if not user_input:
            return ""
        
        # 위험한 문자 제거
        dangerous_chars = ['<', '>', '"', "'", '&', '\x00', '\n\r']
        sanitized = user_input
        
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        
        # 길이 제한
        sanitized = sanitized[:1000]
        
        # SQL 인젝션 패턴 검사
        sql_patterns = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'SELECT', '--', ';']
        upper_input = sanitized.upper()
        
        for pattern in sql_patterns:
            if pattern in upper_input:
                security_logger.warning(f"POTENTIAL_SQL_INJECTION - Input: {sanitized[:50]}")
                # 위험한 패턴 제거 또는 차단
                sanitized = sanitized.replace(pattern.lower(), '').replace(pattern.upper(), '')
        
        return sanitized.strip()
    
    def validate_session(self) -> bool:
        """세션 유효성 검증"""
        try:
            if 'session_start' not in st.session_state:
                st.session_state.session_start = datetime.now()
                return True
            
            session_age = datetime.now() - st.session_state.session_start
            
            if session_age.total_seconds() > self.session_timeout:
                security_logger.info("SESSION_EXPIRED")
                st.session_state.clear()
                return False
            
            return True
            
        except Exception as e:
            security_logger.error(f"세션 검증 오류: {str(e)}")
            return False

class DataPrivacyManager:
    """개인정보 보호 관리"""
    
    def __init__(self):
        self.privacy_consent = {}
        self.data_retention_days = 30
        
    def check_privacy_consent(self) -> bool:
        """개인정보 동의 확인"""
        if 'privacy_consent' not in st.session_state:
            return False
        return st.session_state.privacy_consent.get('analytics', False)
    
    def show_privacy_notice(self):
        """개인정보 처리 방침 표시"""
        with st.expander("🔒 개인정보 처리 방침", expanded=False):
            st.markdown("""
            ### 개인정보 수집 및 이용 안내
            
            **수집하는 정보:**
            - 투자 질문 내용 (포트폴리오 정보 포함)
            - 사용 패턴 및 분석 결과
            - 접속 로그 (IP, 시간 등)
            
            **이용 목적:**
            - AI 투자 분석 서비스 제공
            - 서비스 개선 및 품질 향상
            - 보안 및 부정 사용 방지
            
            **보관 기간:**
            - 30일 후 자동 삭제
            - 법적 요구사항에 따른 예외
            
            **귀하의 권리:**
            - 개인정보 열람, 수정, 삭제 요청 가능
            - 서비스 이용 중단 시 즉시 삭제
            """)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("동의", key="privacy_agree"):
                    st.session_state.privacy_consent = {
                        'analytics': True,
                        'timestamp': datetime.now(),
                        'version': '1.0'
                    }
                    st.success("개인정보 처리에 동의했습니다.")
                    st.rerun()
            
            with col2:
                if st.button("거부", key="privacy_deny"):
                    st.session_state.privacy_consent = {
                        'analytics': False,
                        'timestamp': datetime.now(),
                        'version': '1.0'
                    }
                    st.warning("분석 기능이 제한될 수 있습니다.")
                    st.rerun()
    
    def anonymize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """데이터 익명화"""
        anonymized = data.copy()
        
        # 민감한 정보 마스킹
        if 'question' in anonymized:
            question = anonymized['question']
            # 구체적인 금액이나 수량 마스킹
            import re
            question = re.sub(r'\d+만원', 'X만원', question)
            question = re.sub(r'\d+원', 'X원', question)
            question = re.sub(r'\d+주', 'X주', question)
            anonymized['question'] = question
        
        # 개인 식별 정보 제거
        if 'user_id' in anonymized:
            anonymized['user_id'] = hashlib.md5(anonymized['user_id'].encode()).hexdigest()[:8]
        
        return anonymized

class ErrorSecurityHandler:
    """보안을 고려한 오류 처리"""
    
    def __init__(self):
        self.error_counts = {}
        self.max_errors_per_hour = 50
        
    def handle_secure_error(self, error: Exception, context: str = "") -> Dict[str, str]:
        """보안을 고려한 오류 처리"""
        error_id = self._generate_error_id()
        
        # 상세 오류는 로그에만 기록
        security_logger.error(f"ERROR_{error_id} - Context: {context}, Error: {str(error)}")
        
        # 사용자에게는 일반적인 메시지만 표시
        user_message = self._get_user_friendly_message(error)
        
        # 오류 빈도 체크
        self._track_error_frequency()
        
        return {
            'error_id': error_id,
            'user_message': user_message,
            'show_details': False
        }
    
    def _generate_error_id(self) -> str:
        """오류 추적 ID 생성"""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def _get_user_friendly_message(self, error: Exception) -> str:
        """사용자 친화적 오류 메시지"""
        error_type = type(error).__name__
        
        messages = {
            'ConnectionError': '네트워크 연결에 문제가 있습니다. 잠시 후 다시 시도해주세요.',
            'TimeoutError': '요청 처리 시간이 초과되었습니다. 다시 시도해주세요.',
            'KeyError': '필요한 정보가 누락되었습니다. 입력을 확인해주세요.',
            'ValueError': '입력값에 문제가 있습니다. 올바른 형식으로 입력해주세요.',
            'APIError': 'AI 서비스에 일시적 문제가 있습니다. 잠시 후 다시 시도해주세요.'
        }
        
        return messages.get(error_type, '일시적인 오류가 발생했습니다. 계속 문제가 발생하면 고객센터에 문의해주세요.')
    
    def _track_error_frequency(self):
        """오류 빈도 추적"""
        now = datetime.now()
        hour_key = now.strftime('%Y%m%d%H')
        
        if hour_key not in self.error_counts:
            self.error_counts[hour_key] = 0
        
        self.error_counts[hour_key] += 1
        
        if self.error_counts[hour_key] > self.max_errors_per_hour:
            security_logger.critical(f"HIGH_ERROR_RATE - Hour: {hour_key}, Count: {self.error_counts[hour_key]}")

class ComplianceManager:
    """규정 준수 관리"""
    
    def __init__(self):
        self.disclaimer_shown = False
        self.risk_warnings = []
        
    def show_investment_disclaimer(self):
        """투자 면책조항 강화"""
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
        
        self.disclaimer_shown = True
    
    def add_risk_warning(self, risk_level: str, message: str):
        """위험 경고 추가"""
        self.risk_warnings.append({
            'level': risk_level,
            'message': message,
            'timestamp': datetime.now()
        })
        
        # 높은 위험도인 경우 즉시 표시
        if risk_level in ['HIGH', 'CRITICAL']:
            self._show_immediate_warning(risk_level, message)
    
    def _show_immediate_warning(self, level: str, message: str):
        """즉시 위험 경고 표시"""
        if level == 'CRITICAL':
            st.error(f"🚨 **긴급 위험 경고**: {message}")
        elif level == 'HIGH':
            st.warning(f"⚠️ **높은 위험**: {message}")
    
    def generate_compliance_report(self) -> Dict[str, Any]:
        """규정 준수 보고서 생성"""
        return {
            'disclaimer_shown': self.disclaimer_shown,
            'risk_warnings_count': len(self.risk_warnings),
            'high_risk_warnings': [w for w in self.risk_warnings if w['level'] in ['HIGH', 'CRITICAL']],
            'compliance_timestamp': datetime.now(),
            'version': '1.0'
        }

# 전역 보안 관리자 인스턴스
secure_config = SecureConfig()
privacy_manager = DataPrivacyManager()
error_handler = ErrorSecurityHandler()
compliance_manager = ComplianceManager()
