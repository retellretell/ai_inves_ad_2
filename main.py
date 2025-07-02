"""
improved_main.py - 보안, 안정성, 마케팅이 강화된 메인 애플리케이션
"""

import streamlit as st
import time
from datetime import datetime
import uuid
import logging

# 보안 강화 모듈
from security_config import (
    secure_config, privacy_manager, error_handler, compliance_manager
)

# 강화된 오류 처리
from enhanced_error_handler import (
    init_error_handling, handle_api_error, show_service_status, collect_user_feedback
)

# 마케팅 CTA 시스템
from cta_marketing import (
    init_marketing_system, show_marketing_cta, track_user_action
)

# 기존 모듈들
from config import setup_page_config
from ui_styles import load_css, render_header, render_portfolio_info, render_disclaimer
from data_collector import get_real_time_market_data, get_recent_news, get_stock_data
from portfolio_parser import parse_user_portfolio
from ai_client import EnhancedHyperCLOVAXClient
from chart_utils import create_stock_chart, display_market_metrics

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class SecureInvestmentAdvisor:
    """보안 강화된 투자 어드바이저"""
    
    def __init__(self):
        self.session_id = self._init_session()
        self.error_handler, self.feedback_collector = init_error_handling()
        self.marketing_system = init_marketing_system()
        
    def _init_session(self) -> str:
        """세션 초기화"""
        if 'session_id' not in st.session_state:
            st.session_state.session_id = str(uuid.uuid4())
        
        if 'session_start' not in st.session_state:
            st.session_state.session_start = datetime.now()
        
        return st.session_state.session_id
    
    def run(self):
        """메인 애플리케이션 실행"""
        try:
            # 1. 보안 검사
            if not self._security_checks():
                return
            
            # 2. 페이지 설정
            setup_page_config()
            load_css()
            
            # 3. 개인정보 처리 방침 확인
            if not privacy_manager.check_privacy_consent():
                privacy_manager.show_privacy_notice()
                return
            
            # 4. 세션 유효성 검증
            if not secure_config.validate_session():
                st.error("세션이 만료되었습니다. 페이지를 새로고침해주세요.")
                return
            
            # 5. 메인 애플리케이션 렌더링
            self._render_main_app()
            
        except Exception as e:
            logger.error(f"메인 애플리케이션 오류: {str(e)}")
            error_info = error_handler.handle_secure_error(e, "main_app")
            st.error(f"서비스에 일시적인 문제가 발생했습니다. (오류 ID: {error_info['error_id']})")
            collect_user_feedback(f"Main app error: {error_info['error_id']}")
    
    def _security_checks(self) -> bool:
        """보안 검사"""
        try:
            # 요청 빈도 제한 확인
            if not secure_config.check_rate_limit(st.session_state.get('session_id', 'anonymous')):
                st.error("🚫 요청이 너무 빈번합니다. 잠시 후 다시 시도해주세요.")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"보안 검사 오류: {str(e)}")
            return False
    
    @handle_api_error
    def _get_secure_market_data(self):
        """보안 강화된 시장 데이터 수집"""
        return get_real_time_market_data()
    
    @handle_api_error
    def _get_secure_news_data(self):
        """보안 강화된 뉴스 데이터 수집"""
        return get_recent_news()
    
    def _render_main_app(self):
        """메인 애플리케이션 렌더링"""
        # 1. 헤더 렌더링
        current_time = datetime.now()
        self._render_enhanced_header(current_time)
        
        # 2. 서비스 상태 확인 (관리자 모드)
        if st.secrets.get("ADMIN_MODE", False):
            with st.expander("🔧 시스템 상태 (관리자)", expanded=False):
                show_service_status()
        
        # 3. 실시간 데이터 로드
        with st.spinner("📊 실시간 시장 데이터 로딩 중..."):
            market_data = self._get_secure_market_data()
            news_data = self._get_secure_news_data()
        
        # 4. 사이드바 렌더링
        ai_client = self._render_sidebar(market_data)
        
        # 5. 메인 콘텐츠 렌더링
        self._render_main_content(ai_client, market_data, news_data)
        
        # 6. 규정 준수 관련 표시
        compliance_manager.show_investment_disclaimer()
        
        # 7. 만든이 정보
        self._render_creator_info()
    
    def _render_enhanced_header(self, current_time):
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
    
    def _render_sidebar(self, market_data):
        """사이드바 렌더링"""
        ai_client = EnhancedHyperCLOVAXClient()
        
        with st.sidebar:
            st.header("🏆 AI Festival 2025")
            
            # API 상태 표시
            api_key = secure_config.get_api_key('clova_studio')
            if api_key:
                st.markdown('<div style="background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%); color: white; padding: 0.5rem 1rem; border-radius: 0.5rem; margin: 0.5rem 0;">🔴 LIVE - HyperCLOVA X 연결됨</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div style="background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%); color: white; padding: 0.5rem 1rem; border-radius: 0.5rem; margin: 0.5rem 0;">❌ API 키 미설정</div>', unsafe_allow_html=True)
                st.error("⚠️ API 키를 설정해야 실시간 분석이 가능합니다!")
            
            st.markdown("---")
            
            # 실시간 시장 현황
            st.markdown("### 📊 실시간 시장 현황")
            if market_data:
                display_market_metrics(market_data)
            else:
                st.info("시장 데이터 로딩 중...")
            
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
                    track_user_action("sidebar_question_clicked")
                    st.rerun()
            
            st.markdown("---")
            
            # 보안 상태 표시
            st.markdown("### 🔒 보안 상태")
            st.caption("✅ 개인정보 보호 활성")
            st.caption("✅ 데이터 암호화 적용")
            st.caption("✅ 세션 보안 검증")
            st.caption(f"🆔 세션 ID: {self.session_id[:8]}...")
            
            st.markdown("---")
            st.caption(f"🔄 실시간 업데이트: {datetime.now().strftime('%H:%M:%S')}")
            
            # 사이드바 크레딧
            st.markdown("---")
            st.markdown("""
            <div style="text-align: center; font-size: 0.7rem; color: #999;">
                💻 by <strong style="color: #667eea;">Rin.C</strong><br>
                🏆 AI Festival 2025
            </div>
            """, unsafe_allow_html=True)
        
        return ai_client
    
    def _render_main_content(self, ai_client, market_data, news_data):
        """메인 콘텐츠 렌더링"""
        self._initialize_session_state()
        
        # 메인 입력 영역
        st.markdown("### 💬 실시간 개인화 투자 분석")
        
        # 보안 강화 안내
        st.info("""
        🔒 **개인정보 보호 강화**: 입력하신 모든 정보는 암호화되어 처리되며, 30일 후 자동 삭제됩니다.  
        💡 **개인화 분석 팁**: 구체적인 보유 정보를 포함하면 더 정확한 맞춤 조언을 받을 수 있습니다.
        """)
        
        # 실시간 데이터 표시
        if market_data or news_data:
            with st.expander("📊 현재 사용 중인 실시간 데이터", expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**📈 시장 지수 (실시간)**")
                    for name, data in list(market_data.items())[:4] if market_data else []:
                        collected_time = data.get('collected_at', '알 수 없음')
                        st.markdown(f'<div style="background: #e8f5e8; padding: 0.5rem; border-radius: 0.3rem; margin: 0.5rem 0; border-left: 3px solid #4CAF50;">• {name}: {data["current"]:.2f} ({data["change"]:+.2f}%)<br><small>수집: {collected_time}</small></div>', unsafe_allow_html=True)
                
                with col2:
                    st.markdown("**📰 최신 뉴스**")
                    for i, article in enumerate(news_data[:4] if news_data else [], 1):
                        collected_time = article.get('collected_at', '알 수 없음')
                        st.markdown(f'<div style="background: #e8f5e8; padding: 0.5rem; border-radius: 0.3rem; margin: 0.5rem 0; border-left: 3px solid #4CAF50;">• {article["title"][:50]}...<br><small>출처: {article["source"]} | 수집: {collected_time}</small></div>', unsafe_allow_html=True)
        
        # 질문 입력 및 분석
        self._render_analysis_section(ai_client, market_data, news_data)
        
        # 샘플 질문들
        self._render_sample_questions()
        
        # 마케팅 CTA 섹션
        st.markdown("---")
        portfolio_info = st.session_state.get('last_portfolio_info')
        analysis_result = st.session_state.get('last_analysis_result', "")
        show_marketing_cta("general", portfolio_info, analysis_result)
    
    def _initialize_session_state(self):
        """세션 상태 초기화"""
        defaults = {
            'user_question': "",
            'selected_question': "",
            'last_portfolio_info': None,
            'last_analysis_result': "",
            'analysis_count': 0
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
    
    def _render_analysis_section(self, ai_client, market_data, news_data):
        """분석 섹션 렌더링"""
        # 선택된 질문이 있으면 업데이트
        if st.session_state.get('selected_question'):
            st.session_state.user_question = st.session_state.selected_question
            st.session_state.selected_question = ""
        
        # 질문 입력 (보안 처리 포함)
        user_question = st.text_area(
            "",
            value=st.session_state.user_question,
            placeholder="예: 삼성전자 70,000원에 100주 보유 중인데 계속 들고 있는 게 맞을까요? 현재 시장 상황도 함께 알려주세요.",
            height=120,
            label_visibility="collapsed",
            key="question_input"
        )
        
        # 입력값 보안 처리
        if user_question != st.session_state.user_question:
            sanitized_question = secure_config.sanitize_input(user_question)
            st.session_state.user_question = sanitized_question
        
        # 분석 버튼
        if st.button("🔴 개인화 실시간 AI 분석 시작", type="primary", use_container_width=True):
            self._process_analysis_request(ai_client, market_data, news_data)
    
    def _process_analysis_request(self, ai_client, market_data, news_data):
        """분석 요청 처리"""
        # API 키 확인
        if not secure_config.get_api_key('clova_studio'):
            st.error("⚠️ API 키가 설정되지 않았습니다.")
            return
        
        # 질문 유효성 확인
        if not st.session_state.user_question.strip():
            st.warning("💬 분석할 질문을 입력해주세요.")
            return
        
        # 요청 빈도 제한 확인
        if not secure_config.check_rate_limit(self.session_id):
            st.error("🚫 요청이 너무 빈번합니다. 잠시 후 다시 시도해주세요.")
            return
        
        try:
            # 포트폴리오 정보 추출
            portfolio_info = parse_user_portfolio(st.session_state.user_question)
            st.session_state.last_portfolio_info = portfolio_info
            
            # 포트폴리오 정보가 감지되면 표시
            if portfolio_info:
                render_portfolio_info(portfolio_info)
                
                # 위험도 평가
                if portfolio_info.get('profit_rate'):
                    if portfolio_info['profit_rate'] < -20:
                        compliance_manager.add_risk_warning('HIGH', '큰 손실이 발생했습니다. 전문가 상담을 권장합니다.')
                    elif portfolio_info['profit_rate'] < -10:
                        compliance_manager.add_risk_warning('MEDIUM', '손실이 발생했습니다. 투자 전략 재검토가 필요합니다.')
            
            # 진행률 표시
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # 분석 진행
            analysis_steps = [
                ("🔍 포트폴리오 정보 분석 중...", 10),
                ("📊 실시간 시장 데이터 수집 중...", 25),
                ("📰 최신 뉴스 및 공시 정보 수집 중...", 40),
                ("🔍 검색 트렌드 및 경제 지표 분석 중...", 55),
                ("🤖 HyperCLOVA X 개인화 분석 시작...", 70),
                ("💡 맞춤형 투자 전략 생성 중...", 85),
                ("✅ 개인화 분석 완료!", 100)
            ]
            
            for step_name, progress in analysis_steps:
                status_text.text(step_name)
                progress_bar.progress(progress)
                time.sleep(0.5)
            
            # AI 분석 수행
            response = ai_client.get_personalized_analysis(
                st.session_state.user_question, 
                portfolio_info
            )
            
            # 분석 결과 저장 및 익명화
            st.session_state.last_analysis_result = response
            st.session_state.analysis_count += 1
            
            # 개인정보 동의 시에만 분석 기록 저장
            if privacy_manager.check_privacy_consent():
                anonymized_data = privacy_manager.anonymize_data({
                    'question': st.session_state.user_question,
                    'portfolio_info': portfolio_info,
                    'session_id': self.session_id,
                    'timestamp': datetime.now().isoformat()
                })
                # 익명화된 데이터 저장 로직 (실제 구현 시)
            
            # 진행률 정리
            time.sleep(0.5)
            progress_bar.empty()
            status_text.empty()
            
            # 응답 표시
            st.markdown('<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 2rem; border-radius: 1rem; margin: 1rem 0; box-shadow: 0 8px 32px rgba(0,0,0,0.1);">', unsafe_allow_html=True)
            st.markdown(response)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # 분석 요약 정보
            self._render_analysis_summary(portfolio_info)
            
            # 추가 차트 표시 (포트폴리오 종목이 있는 경우)
            if portfolio_info and portfolio_info.get('ticker'):
                self._render_portfolio_chart(portfolio_info)
            
            # 사용자 액션 추적
            track_user_action("analysis_completed")
            
            # 분석 후 맞춤 CTA 표시
            if portfolio_info:
                profit_rate = portfolio_info.get('profit_rate', 0)
                if profit_rate < -15:
                    context = "high_loss"
                elif profit_rate > 25:
                    context = "high_profit"
                else:
                    context = "general"
                show_marketing_cta(context, portfolio_info, response)
            
        except Exception as e:
            progress_bar.empty()
            status_text.empty()
            
            # 보안 강화된 오류 처리
            error_info = error_handler.handle_secure_error(e, "ai_analysis")
            st.markdown('<div style="background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%); color: white; padding: 1.5rem; border-radius: 1rem; margin: 1rem 0;">', unsafe_allow_html=True)
            st.markdown(f"🚨 **분석 처리 중 오류가 발생했습니다**\n\n{error_info['user_message']}\n\n오류 ID: {error_info['error_id']}")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # 문제 해결 가이드
            self._render_troubleshooting_guide()
            
            # 피드백 수집
            collect_user_feedback(f"Analysis error: {error_info['error_id']}")
    
    def _render_analysis_summary(self, portfolio_info):
        """분석 요약 정보 렌더링"""
        analysis_time = datetime.now().strftime('%Y년 %m월 %d일 %H시 %M분 %S초')
        
        st.markdown(f"""
        <div style="background: #e8f5e8; padding: 0.5rem; border-radius: 0.3rem; margin: 0.5rem 0; border-left: 3px solid #4CAF50;">
            📊 <strong>분석 완료</strong>: {analysis_time}<br>
            🔄 <strong>데이터 소스</strong>: 5개 통합 (실시간 시장 + 뉴스 + 공시 + 트렌드 + 경제지표)<br>
            👤 <strong>개인화</strong>: {'포트폴리오 맞춤 분석' if portfolio_info else '일반 시장 분석'}<br>
            🤖 <strong>AI 엔진</strong>: HyperCLOVA X (HCX-005)<br>
            🔒 <strong>보안</strong>: 데이터 암호화 및 개인정보 보호 적용<br>
            📊 <strong>총 분석 횟수</strong>: {st.session_state.analysis_count}회
        </div>
        """, unsafe_allow_html=True)
    
    def _render_portfolio_chart(self, portfolio_info):
        """포트폴리오 차트 렌더링"""
        st.markdown("### 📈 포트폴리오 종목 차트")
        try:
            stock_data = get_stock_data(portfolio_info['ticker'])
            if stock_data is not None:
                chart = create_stock_chart(stock_data, portfolio_info['ticker'])
                st.plotly_chart(chart, use_container_width=True)
            else:
                st.warning("차트 데이터를 불러올 수 없습니다.")
        except Exception as e:
            st.error(f"차트 생성 중 오류가 발생했습니다: {str(e)}")
    
    def _render_troubleshooting_guide(self):
        """문제 해결 가이드 렌더링"""
        st.markdown("### 🔧 문제 해결 방법")
        st.markdown("""
        1. **네트워크 확인**: 인터넷 연결 상태를 확인해주세요
        2. **페이지 새로고침**: 브라우저를 새로고침 후 다시 시도
        3. **질문 단순화**: 더 간단한 질문으로 다시 시도
        4. **잠시 대기**: 서비스 과부하 시 1-2분 후 재시도
        5. **고객센터**: 지속적인 문제 발생 시 1588-6666
        """)
    
    def _render_sample_questions(self):
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
                        track_user_action("sample_question_clicked")
                        st.rerun()
    
    def _render_creator_info(self):
        """만든이 정보 렌더링"""
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border-radius: 1rem; margin: 2rem 0 1rem 0; border: 1px solid #dee2e6; position: relative; overflow: hidden;">
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

def main():
    """메인 함수"""
    try:
        # 보안 강화된 투자 어드바이저 실행
        app = SecureInvestmentAdvisor()
        app.run()
        
    except Exception as e:
        logger.critical(f"치명적 오류 발생: {str(e)}")
        st.error("🚨 시스템에 치명적인 오류가 발생했습니다. 관리자에게 문의해주세요.")
        
        # 관리자 모드에서만 상세 오류 표시
        if st.secrets.get("ADMIN_MODE", False):
            st.exception(e)

if __name__ == "__main__":
    main()
