"""
enhanced_marketing_cta.py - 강화된 마케팅 CTA 시스템
실제 고객 전환에 최적화된 CTA 및 리드 수집 시스템
"""

import streamlit as st
import json
import uuid
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class EnhancedMarketingCTA:
    """강화된 마케팅 CTA 시스템"""
    
    def __init__(self):
        self.initialize_session_state()
        self.conversion_tracking = []
        
    def initialize_session_state(self):
        """세션 상태 초기화"""
        if 'leads' not in st.session_state:
            st.session_state.leads = []
        
        if 'cta_interactions' not in st.session_state:
            st.session_state.cta_interactions = []
        
        if 'user_journey' not in st.session_state:
            st.session_state.user_journey = {
                'start_time': datetime.now(),
                'page_views': 0,
                'ai_analysis_count': 0,
                'feature_usage': [],
                'engagement_score': 0
            }
    
    def track_user_action(self, action: str, context: Dict[str, Any] = None):
        """사용자 액션 추적"""
        interaction = {
            'action': action,
            'timestamp': datetime.now(),
            'context': context or {},
            'session_id': st.session_state.get('session_id', 'anonymous')
        }
        
        st.session_state.cta_interactions.append(interaction)
        
        # 사용자 여정 업데이트
        if action == 'page_view':
            st.session_state.user_journey['page_views'] += 1
        elif action == 'ai_analysis':
            st.session_state.user_journey['ai_analysis_count'] += 1
        elif action == 'feature_usage':
            st.session_state.user_journey['feature_usage'].append(context.get('feature', 'unknown'))
        
        # 참여도 점수 계산
        self._update_engagement_score()
    
    def _update_engagement_score(self):
        """참여도 점수 업데이트"""
        journey = st.session_state.user_journey
        
        # 기본 점수 계산
        score = 0
        score += min(journey['page_views'] * 10, 50)  # 페이지 뷰 (최대 50점)
        score += min(journey['ai_analysis_count'] * 20, 100)  # AI 분석 (최대 100점)
        score += min(len(journey['feature_usage']) * 15, 75)  # 기능 사용 (최대 75점)
        
        # 시간 기반 보너스
        session_duration = (datetime.now() - journey['start_time']).total_seconds() / 60
        if session_duration > 5:  # 5분 이상 체류
            score += 25
        
        st.session_state.user_journey['engagement_score'] = min(score, 250)
    
    def get_user_segment(self) -> str:
        """사용자 세그먼트 분류"""
        engagement = st.session_state.user_journey['engagement_score']
        ai_usage = st.session_state.user_journey['ai_analysis_count']
        
        if engagement >= 150 and ai_usage >= 3:
            return "high_value"
        elif engagement >= 100 or ai_usage >= 2:
            return "engaged"
        elif engagement >= 50:
            return "interested"
        else:
            return "visitor"
    
    def show_contextual_cta(self, context: str = "general", portfolio_info: Dict[str, Any] = None):
        """상황별 맞춤 CTA 표시"""
        
        # 사용자 세그먼트 확인
        user_segment = self.get_user_segment()
        
        # 액션 추적
        self.track_user_action('cta_view', {'context': context, 'segment': user_segment})
        
        # 컨텍스트별 CTA 구성
        cta_config = self._get_cta_config(context, user_segment, portfolio_info)
        
        # CTA 렌더링
        self._render_cta(cta_config, context)
        
        # 추가 혜택 표시
        self._show_additional_benefits(user_segment)
        
        # 긴급성 메시지 (고가치 사용자)
        if user_segment in ["high_value", "engaged"]:
            self._show_urgency_message(context)
    
    def _get_cta_config(self, context: str, user_segment: str, portfolio_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """CTA 설정 생성"""
        
        base_configs = {
            "high_loss": {
                "title": "🚨 전문가 긴급 상담",
                "subtitle": "큰 손실 방지를 위해 즉시 전문가와 상담하세요",
                "bg_color": "linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%)",
                "urgency": "매우 높음",
                "primary_cta": "긴급 상담 신청",
                "benefits": ["즉시 손실 분석", "리스크 최소화 전략", "전문가 직접 상담"],
                "trust_signals": ["24시간 상담 가능", "무료 긴급 분석", "즉시 연결"]
            },
            "high_profit": {
                "title": "💰 수익 최적화 전문 상담",
                "subtitle": "더 큰 수익을 위한 맞춤 전략을 제안받으세요",
                "bg_color": "linear-gradient(135deg, #4CAF50 0%, #45a049 100%)",
                "urgency": "높음",
                "primary_cta": "수익 극대화 상담",
                "benefits": ["포트폴리오 최적화", "세금 절약 전략", "추가 투자 기회"],
                "trust_signals": ["VIP 고객 전용", "수익률 20% 향상", "전문가 1:1 관리"]
            },
            "general": {
                "title": "📞 1:1 맞춤 투자 상담",
                "subtitle": "AI 분석과 전문가 상담으로 완벽한 투자전략을 세워보세요",
                "bg_color": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                "urgency": "중간",
                "primary_cta": "무료 상담 신청",
                "benefits": ["개인 맞춤 전략", "실시간 분석", "24시간 지원"],
                "trust_signals": ["100% 무료", "전문가 직접 상담", "즉시 연결 가능"]
            }
        }
        
        config = base_configs.get(context, base_configs["general"]).copy()
        
        # 사용자 세그먼트별 맞춤화
        if user_segment == "high_value":
            config["title"] = f"🏆 VIP {config['title']}"
            config["benefits"].insert(0, "VIP 전용 혜택")
            config["trust_signals"].append("프리미엄 서비스 제공")
        elif user_segment == "engaged":
            config["benefits"].append("활성 사용자 특별 혜택")
        
        # 포트폴리오 정보 기반 맞춤화
        if portfolio_info:
            portfolio_value = self._estimate_portfolio_value(portfolio_info)
            if portfolio_value > 100000000:  # 1억 이상
                config["title"] = f"💎 고액 투자자 {config['title']}"
                config["benefits"].insert(0, "고액 투자자 전용 서비스")
        
        return config
    
    def _estimate_portfolio_value(self, portfolio_info: Dict[str, Any]) -> float:
        """포트폴리오 가치 추정"""
        try:
            current_price = portfolio_info.get('current_price', 0)
            shares = portfolio_info.get('shares', 0)
            return current_price * shares
        except:
            return 0
    
    def _render_cta(self, config: Dict[str, Any], context: str):
        """CTA 렌더링"""
        st.markdown("---")
        
        # 메인 CTA 박스
        st.markdown(f"""
        <div style="background: {config['bg_color']}; color: white; padding: 2.5rem; 
                    border-radius: 1rem; margin: 1.5rem 0; text-align: center;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.3); position: relative; overflow: hidden;">
            
            <!-- 애니메이션 효과 -->
            <div style="position: absolute; top: 0; left: -100%; width: 100%; height: 100%;
                        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
                        animation: shimmer 3s infinite;"></div>
            
            <h2 style="margin: 0 0 1rem 0; font-size: 2rem; font-weight: bold;">
                {config['title']}
            </h2>
            <p style="margin: 0 0 1.5rem 0; font-size: 1.2rem; opacity: 0.9;">
                {config['subtitle']}
            </p>
            
            <!-- 혜택 나열 -->
            <div style="display: flex; justify-content: center; gap: 2rem; margin: 1.5rem 0; flex-wrap: wrap;">
                {' '.join([f'<div style="background: rgba(255,255,255,0.1); padding: 0.8rem 1.2rem; border-radius: 2rem; font-weight: 500;">✅ {benefit}</div>' for benefit in config['benefits']])}
            </div>
            
            <!-- 신뢰 신호 -->
            <div style="margin: 1.5rem 0; font-size: 0.95rem; opacity: 0.9;">
                {' | '.join(config['trust_signals'])}
            </div>
        </div>
        
        <style>
        @keyframes shimmer {{
            0% {{ left: -100%; }}
            100% {{ left: 100%; }}
        }}
        </style>
        """, unsafe_allow_html=True)
        
        # CTA 버튼들
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if st.button(
                f"🎯 {config['primary_cta']}", 
                type="primary", 
                use_container_width=True,
                key=f"main_cta_{context}"
            ):
                self.track_user_action('cta_click', {'type': 'primary', 'context': context})
                self._show_lead_capture_form(context, config)
        
        # 보조 액션들
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📞 즉시 전화 연결", use_container_width=True, key=f"phone_{context}"):
                self.track_user_action('cta_click', {'type': 'phone', 'context': context})
                self._show_phone_connection()
        
        with col2:
            if st.button("💬 카카오톡 상담", use_container_width=True, key=f"kakao_{context}"):
                self.track_user_action('cta_click', {'type': 'kakao', 'context': context})
                self._show_kakao_info()
        
        with col3:
            if st.button("📱 앱 다운로드", use_container_width=True, key=f"app_{context}"):
                self.track_user_action('cta_click', {'type': 'app', 'context': context})
                self._show_app_download()
    
    def _show_additional_benefits(self, user_segment: str):
        """추가 혜택 표시"""
        if user_segment == "high_value":
            st.markdown("""
            <div style="background: linear-gradient(135deg, #ffd700 0%, #ffed4a 100%); 
                        color: #333; padding: 1.5rem; border-radius: 0.8rem; margin: 1rem 0;">
                <h4 style="margin: 0 0 1rem 0; color: #d35400;">🏆 VIP 고객 특별 혜택</h4>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                    <div>
                        <strong>🎯 전용 서비스</strong><br>
                        • 전담 PB 배정<br>
                        • 우선 상담 예약<br>
                        • 프리미엄 정보 제공
                    </div>
                    <div>
                        <strong>💰 특별 혜택</strong><br>
                        • 수수료 최대 50% 할인<br>
                        • 우선 IPO 참여 기회<br>
                        • 해외투자 수수료 면제
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        elif user_segment == "engaged":
            st.markdown("""
            <div style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); 
                        color: #333; padding: 1.5rem; border-radius: 0.8rem; margin: 1rem 0;">
                <h4 style="margin: 0 0 1rem 0; color: #2d3436;">🌟 활성 사용자 특별 혜택</h4>
                <div style="text-align: center;">
                    <strong>📊 AI 분석 리포트 무료 제공 + 🎁 투자 가이드북 증정</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    def _show_urgency_message(self, context: str):
        """긴급성 메시지 표시"""
        if context in ["high_loss", "high_profit"]:
            urgency_messages = {
                "high_loss": "⏰ 지금 상담 신청 시 30분 내 전문가 직접 연결! (하루 10명 한정)",
                "high_profit": "🔥 오늘 상담 신청 시 수익 최적화 리포트 무료 제공! (선착순 20명)"
            }
            
            message = urgency_messages.get(context, "")
            if message:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #ff9500 0%, #ff6b00 100%); 
                            color: white; padding: 1rem; border-radius: 0.5rem; 
                            text-align: center; margin: 1rem 0; animation: pulse 2s infinite;">
                    <strong>{message}</strong>
                </div>
                <style>
                @keyframes pulse {{
                    0% {{ opacity: 1; }}
                    50% {{ opacity: 0.7; }}
                    100% {{ opacity: 1; }}
                }}
                </style>
                """, unsafe_allow_html=True)
    
    def _show_lead_capture_form(self, context: str, config: Dict[str, Any]):
        """리드 수집 폼 표시"""
        with st.form(f"lead_form_{context}_{int(time.time())}"):
            st.markdown(f"### 📋 {config['primary_cta']} 신청")
            
            # 기본 정보
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("이름 *", placeholder="홍길동")
                phone = st.text_input("연락처 *", placeholder="010-1234-5678")
                
            with col2:
                email = st.text_input("이메일", placeholder="hong@example.com")
                contact_time = st.selectbox("상담 희망 시간", 
                                          ["평일 오전 (9-12시)", "평일 오후 (13-18시)", 
                                           "평일 저녁 (18-21시)", "주말 상담"])
            
            # 투자 정보
            col1, col2 = st.columns(2)
            
            with col1:
                investment_experience = st.selectbox(
                    "투자 경험",
                    ["초보 (1년 미만)", "초급 (1-3년)", "중급 (3-10년)", "고급 (10년 이상)"]
                )
                
                investment_amount = st.selectbox(
                    "투자 가능 금액",
                    ["1천만원 미만", "1천-5천만원", "5천만원-1억원", "1억원-5억원", "5억원 이상"]
                )
            
            with col2:
                investment_goals = st.multiselect(
                    "투자 목표",
                    ["단기 수익", "장기 자산 증식", "은퇴 준비", "자녀 교육비", "부동산 구매"]
                )
                
                consultation_topics = st.multiselect(
                    "상담 희망 주제",
                    ["포트폴리오 분석", "리스크 관리", "세금 절약", "해외 투자", "연금 계획"]
                )
            
            # 추가 정보
            current_portfolio = st.text_area(
                "현재 보유 자산 (선택)",
                placeholder="예: 삼성전자 100주, 국고채 5000만원 등",
                height=80
            )
            
            additional_info = st.text_area(
                "상담받고 싶은 구체적인 내용",
                placeholder="투자 고민이나 궁금한 점을 자세히 적어주세요...",
                height=100
            )
            
            # 동의 사항
            col1, col2 = st.columns(2)
            
            with col1:
                privacy_agreed = st.checkbox("개인정보 수집 및 이용에 동의합니다. *")
                marketing_agreed = st.checkbox("마케팅 목적 정보 수신에 동의합니다.")
            
            with col2:
                sms_agreed = st.checkbox("SMS 투자 정보 수신에 동의합니다.")
                call_agreed = st.checkbox("투자 상담 전화 수신에 동의합니다.")
            
            # 제출 버튼
            submitted = st.form_submit_button(
                f"✨ {config['primary_cta']} 완료", 
                type="primary", 
                use_container_width=True
            )
            
            if submitted:
                if not name or not phone:
                    st.error("이름과 연락처는 필수 입력 사항입니다.")
                elif not privacy_agreed:
                    st.error("개인정보 수집 및 이용에 동의해주세요.")
                else:
                    # 리드 데이터 저장
                    lead_data = {
                        'id': str(uuid.uuid4()),
                        'name': name,
                        'phone': phone,
                        'email': email,
                        'contact_time': contact_time,
                        'investment_experience': investment_experience,
                        'investment_amount': investment_amount,
                        'investment_goals': investment_goals,
                        'consultation_topics': consultation_topics,
                        'current_portfolio': current_portfolio,
                        'additional_info': additional_info,
                        'privacy_agreed': privacy_agreed,
                        'marketing_agreed': marketing_agreed,
                        'sms_agreed': sms_agreed,
                        'call_agreed': call_agreed,
                        'context': context,
                        'user_segment': self.get_user_segment(),
                        'engagement_score': st.session_state.user_journey['engagement_score'],
                        'timestamp': datetime.now().isoformat(),
                        'source': 'ai_investment_advisor'
                    }
                    
                    # 세션에 저장
                    st.session_state.leads.append(lead_data)
                    
                    # 전환 추적
                    self.track_user_action('lead_captured', {
                        'context': context,
                        'lead_id': lead_data['id'],
                        'investment_amount': investment_amount
                    })
                    
                    # 성공 메시지 및 다음 단계
                    self._show_conversion_success(lead_data, context)
    
    def _show_conversion_success(self, lead_data: Dict[str, Any], context: str):
        """전환 성공 메시지"""
        st.success("✅ 상담 신청이 완료되었습니다!")
        
        # 개인화된 다음 단계
        user_segment = lead_data['user_segment']
        investment_amount = lead_data['investment_amount']
        
        if "5억원 이상" in investment_amount or user_segment == "high_value":
            expected_contact = "1시간 내"
            service_level = "VIP 전담팀"
        elif "1억원" in investment_amount:
            expected_contact = "2시간 내"
            service_level = "프리미엄팀"
        else:
            expected_contact = "24시간 내"
            service_level = "전문 상담팀"
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%); 
                    color: white; padding: 2rem; border-radius: 1rem; margin: 1rem 0;">
            <h3 style="margin: 0 0 1rem 0;">🎉 상담 신청 완료!</h3>
            <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 0.5rem;">
                <p style="margin: 0 0 0.5rem 0;"><strong>📞 연락 예정 시간:</strong> {expected_contact}</p>
                <p style="margin: 0 0 0.5rem 0;"><strong>👥 담당팀:</strong> {service_level}</p>
                <p style="margin: 0;"><strong>📋 상담 ID:</strong> {lead_data['id'][:8].upper()}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 즉시 혜택 제공
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 즉시 포트폴리오 분석 받기", type="primary"):
                st.info("📈 전문가가 귀하의 포트폴리오를 분석하여 개선점을 제시해드립니다.")
        
        with col2:
            if st.button("📚 투자 가이드북 다운로드", type="secondary"):
                st.info("📖 '2025 스마트 투자 가이드'를 이메일로 발송해드렸습니다.")
        
        # 추가 서비스 안내
        st.markdown("### 🎁 추가 서비스")
        
        services = [
            "📱 실시간 시장 알림 서비스 (무료)",
            "📈 AI 기반 종목 추천 (월간)",
            "💰 세금 절약 투자 전략 가이드",
            "🌍 해외 투자 기회 분석 리포트"
        ]
        
        for service in services:
            st.markdown(f"• {service}")
    
    def _show_phone_connection(self):
        """전화 연결 정보"""
        st.markdown("""
        <div style="background: #e8f5e8; padding: 1.5rem; border-radius: 0.8rem; margin: 1rem 0;">
            <h4 style="margin: 0 0 1rem 0; color: #2e7d32;">📞 즉시 전화 상담</h4>
            <div style="font-size: 1.5rem; font-weight: bold; color: #1565c0; text-align: center; margin: 1rem 0;">
                1588-6666
            </div>
            <div style="color: #333;">
                <strong>운영시간:</strong> 평일 09:00-18:00, 토요일 09:00-13:00<br>
                <strong>상담 내용:</strong> "AI 투자 어드바이저 상담" 요청<br>
                <strong>평균 대기시간:</strong> 30초 이내<br>
                <strong>전문 상담사:</strong> 투자 전문가 직접 연결
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def _show_kakao_info(self):
        """카카오톡 상담 정보"""
        st.markdown("""
        <div style="background: #fff3e0; padding: 1.5rem; border-radius: 0.8rem; margin: 1rem 0;">
            <h4 style="margin: 0 0 1rem 0; color: #f57c00;">💬 카카오톡 상담</h4>
            <div style="color: #333;">
                <strong>1단계:</strong> 카카오톡에서 <span style="background: #ffeb3b; padding: 0.2rem 0.5rem; border-radius: 0.3rem;">'미래에셋증권'</span> 검색<br>
                <strong>2단계:</strong> 친구 추가 후 "AI 투자 상담" 메시지 전송<br>
                <strong>3단계:</strong> 전문 상담사가 실시간 채팅으로 도움<br><br>
                <strong>🕐 상담 가능 시간:</strong> 평일 09:00-21:00<br>
                <strong>📱 평균 응답 시간:</strong> 2분 이내
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def _show_app_download(self):
        """앱 다운로드 정보"""
        st.markdown("""
        <div style="background: #f3e5f5; padding: 1.5rem; border-radius: 0.8rem; margin: 1rem 0;">
            <h4 style="margin: 0 0 1rem 0; color: #7b1fa2;">📱 미래에셋 mPOP 앱</h4>
            <div style="color: #333;">
                <strong>🎯 앱 전용 혜택:</strong><br>
                • AI 투자 분석 무제한 이용<br>
                • 실시간 포트폴리오 모니터링<br>
                • 푸시 알림으로 투자 기회 알림<br>
                • 수수료 할인 혜택<br><br>
                
                <strong>📥 다운로드:</strong><br>
                • <strong>아이폰:</strong> App Store에서 "미래에셋 mPOP" 검색<br>
                • <strong>안드로이드:</strong> Google Play에서 "미래에셋 mPOP" 검색
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def show_exit_intent_popup(self):
        """이탈 의도 감지 시 팝업"""
        if st.session_state.user_journey['engagement_score'] > 50:
            st.markdown("""
            <div style="position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
                        background: white; border: 3px solid #ff6b35; border-radius: 1rem;
                        padding: 2rem; box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                        z-index: 1000; max-width: 500px;">
                <h3 style="margin: 0 0 1rem 0; color: #d63031;">잠깐! 놓치기 아까운 혜택이 있어요!</h3>
                <p>지금 상담 신청하시면 <strong>AI 투자 분석 리포트</strong>를 무료로 받으실 수 있습니다.</p>
                <div style="text-align: center; margin-top: 1.5rem;">
                    <button style="background: #00b894; color: white; border: none; padding: 1rem 2rem; border-radius: 0.5rem; font-size: 1.1rem; cursor: pointer;">
                        🎁 무료 혜택 받기
                    </button>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    def show_social_proof(self):
        """사회적 증명 표시"""
        st.markdown("### 💬 실제 고객 후기")
        
        testimonials = [
            {
                'name': '김○○님 (30대, 직장인)',
                'rating': 5,
                'comment': 'AI 분석이 정말 정확해요. 포트폴리오 수익률이 20% 향상되었습니다!',
                'profit': '+2,340만원',
                'period': '6개월'
            },
            {
                'name': '박○○님 (40대, 자영업)',
                'rating': 5,
                'comment': '복잡한 시장 상황을 쉽게 설명해주고, 실행 방안까지 구체적이에요.',
                'profit': '+890만원',
                'period': '3개월'
            },
            {
                'name': '이○○님 (50대, 주부)',
                'rating': 4,
                'comment': '투자 초보도 이해하기 쉽고, 리스크 관리에 큰 도움이 됩니다.',
                'profit': '+450만원',
                'period': '4개월'
            }
        ]
        
        for testimonial in testimonials:
            st.markdown(f"""
            <div style="background: white; border: 1px solid #e0e0e0; border-radius: 0.8rem; 
                        padding: 1.5rem; margin: 1rem 0; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                    <strong style="color: #2c3e50;">{testimonial['name']}</strong>
                    <span style="color: #f39c12;">{'⭐' * testimonial['rating']}</span>
                </div>
                <p style="margin: 0.5rem 0; color: #34495e; font-style: italic;">"{testimonial['comment']}"</p>
                <div style="display: flex; gap: 2rem; margin-top: 1rem; font-size: 0.9rem; color: #7f8c8d;">
                    <span style="background: #e8f5e8; padding: 0.3rem 0.8rem; border-radius: 1rem;">
                        💰 수익: {testimonial['profit']}
                    </span>
                    <span style="background: #e3f2fd; padding: 0.3rem 0.8rem; border-radius: 1rem;">
                        📅 기간: {testimonial['period']}
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # 통계 정보
        st.markdown("### 📊 서비스 이용 현황")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("누적 사용자", "15,420명")
        with col2:
            st.metric("AI 분석 제공", "127,854건")
        with col3:
            st.metric("고객 만족도", "4.7/5.0")
        with col4:
            st.metric("수익 개선률", "73.2%")
    
    def get_conversion_analytics(self) -> Dict[str, Any]:
        """전환 분석 데이터"""
        total_interactions = len(st.session_state.cta_interactions)
        leads_captured = len(st.session_state.leads)
        
        conversion_rate = (leads_captured / total_interactions * 100) if total_interactions > 0 else 0
        
        # 세그먼트별 분석
        segment_data = {}
        for lead in st.session_state.leads:
            segment = lead.get('user_segment', 'unknown')
            if segment not in segment_data:
                segment_data[segment] = 0
            segment_data[segment] += 1
        
        return {
            'total_interactions': total_interactions,
            'leads_captured': leads_captured,
            'conversion_rate': round(conversion_rate, 2),
            'segment_distribution': segment_data,
            'avg_engagement_score': np.mean([lead.get('engagement_score', 0) for lead in st.session_state.leads]) if st.session_state.leads else 0
        }

# 편의 함수들
def init_marketing_system():
    """마케팅 시스템 초기화"""
    if 'marketing_cta' not in st.session_state:
        st.session_state.marketing_cta = EnhancedMarketingCTA()
    
    return st.session_state.marketing_cta

def show_marketing_cta(context: str = "general", portfolio_info: Dict[str, Any] = None):
    """마케팅 CTA 표시 헬퍼"""
    marketing_system = init_marketing_system()
    
    # 사회적 증명 먼저 표시
    marketing_system.show_social_proof()
    
    # 상황별 CTA 표시
    marketing_system.show_contextual_cta(context, portfolio_info)

def track_user_action(action: str, context: Dict[str, Any] = None):
    """사용자 액션 추적 헬퍼"""
    marketing_system = init_marketing_system()
    marketing_system.track_user_action(action, context)

def show_conversion_dashboard():
    """전환 대시보드 표시 (관리자용)"""
    if not st.secrets.get("ADMIN_MODE", False):
        return
    
    marketing_system = init_marketing_system"""
enhanced_marketing_cta.py - 강화된 마케팅 CTA 시스템
실제 고객 전환에 최적화된 CTA 및 리드 수집 시스템
"""

import streamlit as st
import json
import uuid
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class EnhancedMarketingCTA:
    """강화된 마케팅 CTA 시스템"""
    
    def __init__(self):
        self.initialize_session_state()
        self.conversion_tracking = []
        
    def initialize_session_state(self):
        """세션 상태 초기화"""
        if 'leads' not in st.session_state:
            st.session_state.leads = []
        
        if 'cta_interactions' not in st.session_state:
            st.session_state.cta_interactions = []
        
        if 'user_journey' not in st.session_state:
            st.session_state.user_journey = {
                'start_time': datetime.now(),
                'page_views': 0,
                'ai_analysis_count': 0,
                'feature_usage': [],
                'engagement_score': 0
            }
    
    def track_user_action(self, action: str, context: Dict[str, Any] = None):
        """사용자 액션 추적"""
        interaction = {
            'action': action,
            'timestamp': datetime.now(),
            'context': context or {},
            'session_id': st.session_state.get('session_id', 'anonymous')
        }
        
        st.session_state.cta_interactions.append(interaction)
        
        # 사용자 여정 업데이트
        if action == 'page_view':
            st.session_state.user_journey['page_views'] += 1
        elif action == 'ai_analysis':
            st.session_state.user_journey['ai_analysis_count'] += 1
        elif action == 'feature_usage':
            st.session_state.user_journey['feature_usage'].append(context.get('feature', 'unknown'))
        
        # 참여도 점수 계산
        self._update_engagement_score()
    
    def _update_engagement_score(self):
        """참여도 점수 업데이트"""
        journey = st.session_state.user_journey
        
        # 기본 점수 계산
        score = 0
        score += min(journey['page_views'] * 10, 50)  # 페이지 뷰 (최대 50점)
        score += min(journey['ai_analysis_count'] * 20, 100)  # AI 분석 (최대 100점)
        score += min(len(journey['feature_usage']) * 15, 75)  # 기능 사용 (최대 75점)
        
        # 시간 기반 보너스
        session_duration = (datetime.now() - journey['start_time']).total_seconds() / 60
        if session_duration > 5:  # 5분 이상 체류
            score += 25
        
        st.session_state.user_journey['engagement_score'] = min(score, 250)
    
    def get_user_segment(self) -> str:
        """사용자 세그먼트 분류"""
        engagement = st.session_state.user_journey['engagement_score']
        ai_usage = st.session_state.user_journey['ai_analysis_count']
        
        if engagement >= 150 and ai_usage >= 3:
            return "high_value"
        elif engagement >= 100 or ai_usage >= 2:
            return "engaged"
        elif engagement >= 50:
            return "interested"
        else:
            return "visitor"
    
    def show_contextual_cta(self, context: str = "general", portfolio_info: Dict[str, Any] = None):
        """상황별 맞춤 CTA 표시"""
        
        # 사용자 세그먼트 확인
        user_segment = self.get_user_segment()
        
        # 액션 추적
        self.track_user_action('cta_view', {'context': context, 'segment': user_segment})
        
        # 컨텍스트별 CTA 구성
        cta_config = self._get_cta_config(context, user_segment, portfolio_info)
        
        # CTA 렌더링
        self._render_cta(cta_config, context)
        
        # 추가 혜택 표시
        self._show_additional_benefits(user_segment)
        
        # 긴급성 메시지 (고가치 사용자)
        if user_segment in ["high_value", "engaged"]:
            self._show_urgency_message(context)
    
    def _get_cta_config(self, context: str, user_segment: str, portfolio_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """CTA 설정 생성"""
        
        base_configs = {
            "high_loss": {
                "title": "🚨 전문가 긴급 상담",
                "subtitle": "큰 손실 방지를 위해 즉시 전문가와 상담하세요",
                "bg_color": "linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%)",
                "urgency": "매우 높음",
                "primary_cta": "긴급 상담 신청",
                "benefits": ["즉시 손실 분석", "리스크 최소화 전략", "전문가 직접 상담"],
                "trust_signals": ["24시간 상담 가능", "무료 긴급 분석", "즉시 연결"]
            },
            "high_profit": {
                "title": "💰 수익 최적화 전문 상담",
                "subtitle": "더 큰 수익을 위한 맞춤 전략을 제안받으세요",
                "bg_color": "linear-gradient(135deg, #4CAF50 0%, #45a049 100%)",
                "urgency": "높음",
                "primary_cta": "수익 극대화 상담",
                "benefits": ["포트폴리오 최적화", "세금 절약 전략", "추가 투자 기회"],
                "trust_signals": ["VIP 고객 전용", "수익률 20% 향상", "전문가 1:1 관리"]
            },
            "general": {
                "title": "📞 1:1 맞춤 투자 상담",
                "subtitle": "AI 분석과 전문가 상담으로 완벽한 투자전략을 세워보세요",
                "bg_color": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                "urgency": "중간",
                "primary_cta": "무료 상담 신청",
                "benefits": ["개인 맞춤 전략", "실시간 분석", "24시간 지원"],
                "trust_signals": ["100% 무료", "전문가 직접 상담", "즉시 연결 가능"]
            }
        }
        
        config = base_configs.get(context, base_configs["general"]).copy()
        
        # 사용자 세그먼트별 맞춤화
        if user_segment == "high_value":
            config["title"] = f"🏆 VIP {config['title']}"
            config["benefits"].insert(0, "VIP 전용 혜택")
            config["trust_signals"].append("프리미엄 서비스 제공")
        elif user_segment == "engaged":
            config["benefits"].append("활성 사용자 특별 혜택")
        
        # 포트폴리오 정보 기반 맞춤화
        if portfolio_info:
            portfolio_value = self._estimate_portfolio_value(portfolio_info)
            if portfolio_value > 100000000:  # 1억 이상
                config["title"] = f"💎 고액 투자자 {config['title']}"
                config["benefits"].insert(0, "고액 투자자 전용 서비스")
        
        return config
    
    def _estimate_portfolio_value(self, portfolio_info: Dict[str, Any]) -> float:
        """포트폴리오 가치 추정"""
        try:
            current_price = portfolio_info.get('current_price', 0)
            shares = portfolio_info.get('shares', 0)
            return current_price * shares
        except:
            return 0
    
    def _render_cta(self, config: Dict[str, Any], context: str):
        """CTA 렌더링"""
        st.markdown("---")
        
        # 메인 CTA 박스
        st.markdown(f"""
        <div style="background: {config['bg_color']}; color: white; padding: 2.5rem; 
                    border-radius: 1rem; margin: 1.5rem 0; text-align: center;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.3); position: relative; overflow: hidden;">
            
            <!-- 애니메이션 효과 -->
            <div style="position: absolute; top: 0; left: -100%; width: 100%; height: 100%;
                        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
                        animation: shimmer 3s infinite;"></div>
            
            <h2 style="margin: 0 0 1rem 0; font-size: 2rem; font-weight: bold;">
                {config['title']}
            </h2>
            <p style="margin: 0 0 1.5rem 0; font-size: 1.2rem; opacity: 0.9;">
                {config['subtitle']}
            </p>
            
            <!-- 혜택 나열 -->
            <div style="display: flex; justify-content: center; gap: 2rem; margin: 1.5rem 0; flex-wrap: wrap;">
                {' '.join([f'<div style="background: rgba(255,255,255,0.1); padding: 0.8rem 1.2rem; border-radius: 2rem; font-weight: 500;">✅ {benefit}</div>' for benefit in config['benefits']])}
            </div>
            
            <!-- 신뢰 신호 -->
            <div style="margin: 1.5rem 0; font-size: 0.95rem; opacity: 0.9;">
                {' | '.join(config['trust_signals'])}
            </div>
        </div>
        
        <style>
        @keyframes shimmer {{
            0% {{ left: -100%; }}
            100% {{ left: 100%; }}
        }}
        </style>
        """, unsafe_allow_html=True)
        
        # CTA 버튼들
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if st.button(
                f"🎯 {config['primary_cta']}", 
                type="primary", 
                use_container_width=True,
                key=f"main_cta_{context}"
            ):
                self.track_user_action('cta_click', {'type': 'primary', 'context': context})
                self._show_lead_capture_form(context, config)
        
        # 보조 액션들
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📞 즉시 전화 연결", use_container_width=True, key=f"phone_{context}"):
                self.track_user_action('cta_click', {'type': 'phone', 'context': context})
                self._show_phone_connection()
        
        with col2:
            if st.button("💬 카카오톡 상담", use_container_width=True, key=f"kakao_{context}"):
                self.track_user_action('cta_click', {'type': 'kakao', 'context': context})
                self._show_kakao_info()
        
        with col3:
            if st.button("📱 앱 다운로드", use_container_width=True, key=f"app_{context}"):
                self.track_user_action('cta_click', {'type': 'app', 'context': context})
                self._show_app_download()
    
    def _show_additional_benefits(self, user_segment: str):
        """추가 혜택 표시"""
        if user_segment == "high_value":
            st.markdown("""
            <div style="background: linear-gradient(135deg, #ffd700 0%, #ffed4a 100%); 
                        color: #333; padding: 1.5rem; border-radius: 0.8rem; margin: 1rem 0;">
                <h4 style="margin: 0 0 1rem 0; color: #d35400;">🏆 VIP 고객 특별 혜택</h4>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                    <div>
                        <strong>🎯 전용 서비스</strong><br>
                        • 전담 PB 배정<br>
                        • 우선 상담 예약<br>
                        • 프리미엄 정보 제공
                    </div>
                    <div>
                        <strong>💰 특별 혜택</strong><br>
                        • 수수료 최대 50% 할인<br>
                        • 우선 IPO 참여 기회<br>
                        • 해외투자 수수료 면제
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        elif user_segment == "engaged":
            st.markdown("""
            <div style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); 
                        color: #333; padding: 1.5rem; border-radius: 0.8rem; margin: 1rem 0;">
                <h4 style="margin: 0 0 1rem 0; color: #2d3436;">🌟 활성 사용자 특별 혜택</h4>
                <div style="text-align: center;">
                    <strong>📊 AI 분석 리포트 무료 제공 + 🎁 투자 가이드북 증정</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    def _show_urgency_message(self, context: str):
        """긴급성 메시지 표시"""
        if context in ["high_loss", "high_profit"]:
            urgency_messages = {
                "high_loss": "⏰ 지금 상담 신청 시 30분 내 전문가 직접 연결! (하루 10명 한정)",
                "high_profit": "🔥 오늘 상담 신청 시 수익 최적화 리포트 무료 제공! (선착순 20명)"
            }
            
            message = urgency_messages.get(context, "")
            if message:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #ff9500 0%, #ff6b00 100%); 
                            color: white; padding: 1rem; border-radius: 0.5rem; 
                            text-align: center; margin: 1rem 0; animation: pulse 2s infinite;">
                    <strong>{message}</strong>
                </div>
                <style>
                @keyframes pulse {{
                    0% {{ opacity: 1; }}
                    50% {{ opacity: 0.7; }}
                    100% {{ opacity: 1; }}
                }}
                </style>
                """, unsafe_allow_html=True)
    
    def _show_lead_capture_form(self, context: str, config: Dict[str, Any]):
        """리드 수집 폼 표시"""
        with st.form(f"lead_form_{context}_{int(time.time())}"):
            st.markdown(f"### 📋 {config['primary_cta']} 신청")
            
            # 기본 정보
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("이름 *", placeholder="홍길동")
                phone = st.text_input("연락처 *", placeholder="010-1234-5678")
                
            with col2:
                email = st.text_input("이메일", placeholder="hong@example.com")
                contact_time = st.selectbox("상담 희망 시간", 
                                          ["평일 오전 (9-12시)", "평일 오후 (13-18시)", 
                                           "평일 저녁 (18-21시)", "주말 상담"])
            
            # 투자 정보
            col1, col2 = st.columns(2)
            
            with col1:
                investment_experience = st.selectbox(
                    "투자 경험",
                    ["초보 (1년 미만)", "초급 (1-3년)", "중급 (3-10년)", "고급 (10년 이상)"]
                )
                
                investment_amount = st.selectbox(
                    "투자 가능 금액",
                    ["1천만원 미만", "1천-5천만원", "5천만원-1억원", "1억원-5억원", "5억원 이상"]
                )
            
            with col2:
                investment_goals = st.multiselect(
                    "투자 목표",
                    ["단기 수익", "장기 자산 증식", "은퇴 준비", "자녀 교육비", "부동산 구매"]
                )
                
                consultation_topics = st.multiselect(
                    "상담 희망 주제",
                    ["포트폴리오 분석", "리스크 관리", "세금 절약", "해외 투자", "연금 계획"]
                )
            
            # 추가 정보
            current_portfolio = st.text_area(
                "현재 보유 자산 (선택)",
                placeholder="예: 삼성전자 100주, 국고채 5000만원 등",
                height=80
            )
            
            additional_info = st.text_area(
                "상담받고 싶은 구체적인 내용",
                placeholder="투자 고민이나 궁금한 점을 자세히 적어주세요...",
                height=100
            )
            
            # 동의 사항
            col1, col2 = st.columns(2)
            
            with col1:
                privacy_agreed = st.checkbox("개인정보 수집 및 이용에 동의합니다. *")
                marketing_agreed = st.checkbox("마케팅 목적 정보 수신에 동의합니다.")
            
            with col2:
                sms_agreed = st.checkbox("SMS 투자 정보 수신에 동의합니다.")
                call_agreed = st.checkbox("투자 상담 전화 수신에 동의합니다.")
            
            # 제출 버튼
            submitted = st.form_submit_button(
                f"✨ {config['primary_cta']} 완료", 
                type="primary", 
                use_container_width=True
            )
            
            if submitted:
                if not name or not phone:
                    st.error("이름과 연락처는 필수 입력 사항입니다.")
                elif not privacy_agreed:
                    st.error("개인정보 수집 및 이용에 동의해주세요.")
                else:
                    # 리드 데이터 저장
                    lead_data = {
                        'id': str(uuid.uuid4()),
                        'name': name,
                        'phone': phone,
                        'email': email,
                        'contact_time': contact_time,
                        'investment_experience': investment_experience,
                        'investment_amount': investment_amount,
                        'investment_goals': investment_goals,
                        'consultation_topics': consultation_topics,
                        'current_portfolio': current_portfolio,
                        'additional_info': additional_info,
                        'privacy_agreed': privacy_agreed,
                        'marketing_agreed': marketing_agreed,
                        'sms_agreed': sms_agreed,
                        'call_agreed': call_agreed,
                        'context': context,
                        'user_segment': self.get_user_segment(),
                        'engagement_score': st.session_state.user_journey['engagement_score'],
                        'timestamp': datetime.now().isoformat(),
                        'source': 'ai_investment_advisor'
                    }
                    
                    # 세션에 저장
                    st.session_state.leads.append(lead_data)
                    
                    # 전환 추적
                    self.track_user_action('lead_captured', {
                        'context': context,
                        'lead_id': lead_data['id'],
                        'investment_amount': investment_amount
                    })
                    
                    # 성공 메시지 및 다음 단계
                    self._show_conversion_success(lead_data, context)
    
    def _show_conversion_success(self, lead_data: Dict[str, Any], context: str):
        """전환 성공 메시지"""
        st.success("✅ 상담 신청이 완료되었습니다!")
        
        # 개인화된 다음 단계
        user_segment = lead_data['user_segment']
        investment_amount = lead_data['investment_amount']
        
        if "5억원 이상" in investment_amount or user_segment == "high_value":
            expected_contact = "1시간 내"
            service_level = "VIP 전담팀"
        elif "1억원" in investment_amount:
            expected_contact = "2시간 내"
            service_level = "프리미엄팀"
        else:
            expected_contact = "24시간 내"
            service_level = "전문 상담팀"
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%); 
                    color: white; padding: 2rem; border-radius: 1rem; margin: 1rem 0;">
            <h3 style="margin: 0 0 1rem 0;">🎉 상담 신청 완료!</h3>
            <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 0.5rem;">
                <p style="margin: 0 0 0.5rem 0;"><strong>📞 연락 예정 시간:</strong> {expected_contact}</p>
                <p style="margin: 0 0 0.5rem 0;"><strong>👥 담당팀:</strong> {service_level}</p>
                <p style="margin: 0;"><strong>📋 상담 ID:</strong> {lead_data['id'][:8].upper()}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 즉시 혜택 제공
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 즉시 포트폴리오 분석 받기", type="primary"):
                st.info("📈 전문가가 귀하의 포트폴리오를 분석하여 개선점을 제시해드립니다.")
        
        with col2:
            if st.button("📚 투자 가이드북 다운로드", type="secondary"):
                st.info("📖 '2025 스마트 투자 가이드'를 이메일로 발송해드렸습니다.")
        
        # 추가 서비스 안내
        st.markdown("### 🎁 추가 서비스")
        
        services = [
            "📱 실시간 시장 알림 서비스 (무료)",
            "📈 AI 기반 종목 추천 (월간)",
            "💰 세금 절약 투자 전략 가이드",
            "🌍 해외 투자 기회 분석 리포트"
        ]
        
        for service in services:
            st.markdown(f"• {service}")
    
    def _show_phone_connection(self):
        """전화 연결 정보"""
        st.markdown("""
        <div style="background: #e8f5e8; padding: 1.5rem; border-radius: 0.8rem; margin: 1rem 0;">
            <h4 style="margin: 0 0 1rem 0; color: #2e7d32;">📞 즉시 전화 상담</h4>
            <div style="font-size: 1.5rem; font-weight: bold; color: #1565c0; text-align: center; margin: 1rem 0;">
                1588-6666
            </div>
            <div style="color: #333;">
                <strong>운영시간:</strong> 평일 09:00-18:00, 토요일 09:00-13:00<br>
                <strong>상담 내용:</strong> "AI 투자 어드바이저 상담" 요청<br>
                <strong>평균 대기시간:</strong> 30초 이내<br>
                <strong>전문 상담사:</strong> 투자 전문가 직접 연결
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def _show_kakao_info(self):
        """카카오톡 상담 정보"""
        st.markdown("""
        <div style="background: #fff3e0; padding: 1.5rem; border-radius: 0.8rem; margin: 1rem 0;">
            <h4 style="margin: 0 0 1rem 0; color: #f57c00;">💬 카카오톡 상담</h4>
            <div style="color: #333;">
                <strong>1단계:</strong> 카카오톡에서 <span style="background: #ffeb3b; padding: 0.2rem 0.5rem; border-radius: 0.3rem;">'미래에셋증권'</span> 검색<br>
                <strong>2단계:</strong> 친구 추가 후 "AI 투자 상담" 메시지 전송<br>
                <strong>3단계:</strong> 전문 상담사가 실시간 채팅으로 도움<br><br>
                <strong>🕐 상담 가능 시간:</strong> 평일 09:00-21:00<br>
                <strong>📱 평균 응답 시간:</strong> 2분 이내
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def _show_app_download(self):
        """앱 다운로드 정보"""
        st.markdown("""
        <div style="background: #f3e5f5; padding: 1.5rem; border-radius: 0.8rem; margin: 1rem 0;">
            <h4 style="margin: 0 0 1rem 0; color: #7b1fa2;">📱 미래에셋 mPOP 앱</h4>
            <div style="color: #333;">
                <strong>🎯 앱 전용 혜택:</strong><br>
                • AI 투자 분석 무제한 이용<br>
                • 실시간 포트폴리오 모니터링<br>
                • 푸시 알림으로 투자 기회 알림<br>
                • 수수료 할인 혜택<br><br>
                
                <strong>📥 다운로드:</strong><br>
                • <strong>아이폰:</strong> App Store에서 "미래에셋 mPOP" 검색<br>
                • <strong>안드로이드:</strong> Google Play에서 "미래에셋 mPOP" 검색
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def show_exit_intent_popup(self):
        """이탈 의도 감지 시 팝업"""
        if st.session_state.user_journey['engagement_score'] > 50:
            st.markdown("""
            <div style="position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
                        background: white; border: 3px solid #ff6b35; border-radius: 1rem;
                        padding: 2rem; box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                        z-index: 1000; max-width: 500px;">
                <h3 style="margin: 0 0 1rem 0; color: #d63031;">잠깐! 놓치기 아까운 혜택이 있어요!</h3>
                <p>지금 상담 신청하시면 <strong>AI 투자 분석 리포트</strong>를 무료로 받으실 수 있습니다.</p>
                <div style="text-align: center; margin-top: 1.5rem;">
                    <button style="background: #00b894; color: white; border: none; padding: 1rem 2rem; border-radius: 0.5rem; font-size: 1.1rem; cursor: pointer;">
                        🎁 무료 혜택 받기
                    </button>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    def show_social_proof(self):
        """사회적 증명 표시"""
        st.markdown("### 💬 실제 고객 후기")
        
        testimonials = [
            {
                'name': '김○○님 (30대, 직장인)',
                'rating': 5,
                'comment': 'AI 분석이 정말 정확해요. 포트폴리오 수익률이 20% 향상되었습니다!',
                'profit': '+2,340만원',
                'period': '6개월'
            },
            {
                'name': '박○○님 (40대, 자영업)',
                'rating': 5,
                'comment': '복잡한 시장 상황을 쉽게 설명해주고, 실행 방안까지 구체적이에요.',
                'profit': '+890만원',
                'period': '3개월'
            },
            {
                'name': '이○○님 (50대, 주부)',
                'rating': 4,
                'comment': '투자 초보도 이해하기 쉽고, 리스크 관리에 큰 도움이 됩니다.',
                'profit': '+450만원',
                'period': '4개월'
            }
        ]
        
        for testimonial in testimonials:
            st.markdown(f"""
            <div style="background: white; border: 1px solid #e0e0e0; border-radius: 0.8rem; 
                        padding: 1.5rem; margin: 1rem 0; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                    <strong style="color: #2c3e50;">{testimonial['name']}</strong>
                    <span style="color: #f39c12;">{'⭐' * testimonial['rating']}</span>
                </div>
                <p style="margin: 0.5rem 0; color: #34495e; font-style: italic;">"{testimonial['comment']}"</p>
                <div style="display: flex; gap: 2rem; margin-top: 1rem; font-size: 0.9rem; color: #7f8c8d;">
                    <span style="background: #e8f5e8; padding: 0.3rem 0.8rem; border-radius: 1rem;">
                        💰 수익: {testimonial['profit']}
                    </span>
                    <span style="background: #e3f2fd; padding: 0.3rem 0.8rem; border-radius: 1rem;">
                        📅 기간: {testimonial['period']}
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # 통계 정보
        st.markdown("### 📊 서비스 이용 현황")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("누적 사용자", "15,420명")
        with col2:
            st.metric("AI 분석 제공", "127,854건")
        with col3:
            st.metric("고객 만족도", "4.7/5.0")
        with col4:
            st.metric("수익 개선률", "73.2%")
    
    def get_conversion_analytics(self) -> Dict[str, Any]:
        """전환 분석 데이터"""
        total_interactions = len(st.session_state.cta_interactions)
        leads_captured = len(st.session_state.leads)
        
        conversion_rate = (leads_captured / total_interactions * 100) if total_interactions > 0 else 0
        
        # 세그먼트별 분석
        segment_data = {}
        for lead in st.session_state.leads:
            segment = lead.get('user_segment', 'unknown')
            if segment not in segment_data:
                segment_data[segment] = 0
            segment_data[segment] += 1
        
        return {
            'total_interactions': total_interactions,
            'leads_captured': leads_captured,
            'conversion_rate': round(conversion_rate, 2),
            'segment_distribution': segment_data,
            'avg_engagement_score': np.mean([lead.get('engagement_score', 0) for lead in st.session_state.leads]) if st.session_state.leads else 0
        }

# 편의 함수들
def init_marketing_system():
    """마케팅 시스템 초기화"""
    if 'marketing_cta' not in st.session_state:
        st.session_state.marketing_cta = EnhancedMarketingCTA()
    
    return st.session_state.marketing_cta

def show_marketing_cta(context: str = "general", portfolio_info: Dict[str, Any] = None):
    """마케팅 CTA 표시 헬퍼"""
    marketing_system = init_marketing_system()
    
    # 사회적 증명 먼저 표시
    marketing_system.show_social_proof()
    
    # 상황별 CTA 표시
    marketing_system.show_contextual_cta(context, portfolio_info)

def track_user_action(action: str, context: Dict[str, Any] = None):
    """사용자 액션 추적 헬퍼"""
    marketing_system = init_marketing_system()
    marketing_system.track_user_action(action, context)

def show_conversion_dashboard():
    """전환 대시보드 표시 (관리자용)"""
    if not st.secrets.get("ADMIN_MODE", False):
        return
    
    marketing_system = init_marketing_system()
    analytics = marketing_system.get_conversion_analytics()
    
    st.markdown("### 🎯 마케팅 전환 대시보드 (관리자)")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("총 상호작용", analytics['total_interactions'])
    with col2:
        st.metric("리드 전환", analytics['leads_captured'])
    with col3:
        st.metric("전환율", f"{analytics['conversion_rate']}%")
    with col4:
        st.metric("평균 참여도", f"{analytics['avg_engagement_score']:.0f}")
    
    # 세그먼트별 분포
    if analytics['segment_distribution']:
        st.markdown("**사용자 세그먼트별 전환율:**")
        for segment, count in analytics['segment_distribution'].items():
            st.write(f"• {segment}: {count}명")
    
    # 최근 리드 목록
    if st.session_state.leads:
        st.markdown("**최근 리드 (최대 10건):**")
        recent_leads = st.session_state.leads[-10:]
        
        for lead in reversed(recent_leads):
            with st.expander(f"{lead['name']} - {lead['investment_amount']} ({lead['timestamp'][:19]})"):
                st.write(f"**연락처:** {lead['phone']}")
                st.write(f"**투자경험:** {lead['investment_experience']}")
                st.write(f"**상담주제:** {', '.join(lead.get('consultation_topics', []))}")
                st.write(f"**참여도점수:** {lead.get('engagement_score', 0)}")
                if lead.get('additional_info'):
                    st.write(f"**추가정보:** {lead['additional_info']}")

if __name__ == "__main__":
    import numpy as np
    
    st.set_page_config(page_title="강화된 마케팅 CTA", page_icon="🎯", layout="wide")
    st.title("🎯 강화된 마케팅 CTA 시스템")
    
    # 데모 실행
    marketing_system = init_marketing_system()
    
    tab1, tab2, tab3 = st.tabs(["🎯 CTA 시스템", "📊 사회적 증명", "📈 전환 분석"])
    
    with tab1:
        st.markdown("### CTA 시스템 데모")
        
        # 컨텍스트 선택
        demo_context = st.selectbox("테스트할 CTA 상황", ["general", "high_loss", "high_profit"])
        
        # 포트폴리오 정보 시뮬레이션
        portfolio_info = None
        if st.checkbox("포트폴리오 정보 포함"):
            portfolio_info = {
                'current_price': 70000,
                'shares': 100,
                'buy_price': 65000
            }
        
        # CTA 표시
        marketing_system.show_contextual_cta(demo_context, portfolio_info)
    
    with tab2:
        marketing_system.show_social_proof()
    
    with tab3:
        show_conversion_dashboard()"""
enhanced_marketing_cta.py - 강화된 마케팅 CTA 시스템
실제 고객 전환에 최적화된 CTA 및 리드 수집 시스템
"""

import streamlit as st
import json
import uuid
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class EnhancedMarketingCTA:
    """강화된 마케팅 CTA 시스템"""
    
    def __init__(self):
        self.initialize_session_state()
        self.conversion_tracking = []
        
    def initialize_session_state(self):
        """세션 상태 초기화"""
        if 'leads' not in st.session_state:
            st.session_state.leads = []
        
        if 'cta_interactions' not in st.session_state:
            st.session_state.cta_interactions = []
        
        if 'user_journey' not in st.session_state:
            st.session_state.user_journey = {
                'start_time': datetime.now(),
                'page_views': 0,
                'ai_analysis_count': 0,
                'feature_usage': [],
                'engagement_score': 0
            }
    
    def track_user_action(self, action: str, context: Dict[str, Any] = None):
        """사용자 액션 추적"""
        interaction = {
            'action': action,
            'timestamp': datetime.now(),
            'context': context or {},
            'session_id': st.session_state.get('session_id', 'anonymous')
        }
        
        st.session_state.cta_interactions.append(interaction)
        
        # 사용자 여정 업데이트
        if action == 'page_view':
            st.session_state.user_journey['page_views'] += 1
        elif action == 'ai_analysis':
            st.session_state.user_journey['ai_analysis_count'] += 1
        elif action == 'feature_usage':
            st.session_state.user_journey['feature_usage'].append(context.get('feature', 'unknown'))
        
        # 참여도 점수 계산
        self._update_engagement_score()
    
    def _update_engagement_score(self):
        """참여도 점수 업데이트"""
        journey = st.session_state.user_journey
        
        # 기본 점수 계산
        score = 0
        score += min(journey['page_views'] * 10, 50)  # 페이지 뷰 (최대 50점)
        score += min(journey['ai_analysis_count'] * 20, 100)  # AI 분석 (최대 100점)
        score += min(len(journey['feature_usage']) * 15, 75)  # 기능 사용 (최대 75점)
        
        # 시간 기반 보너스
        session_duration = (datetime.now() - journey['start_time']).total_seconds() / 60
        if session_duration > 5:  # 5분 이상 체류
            score += 25
        
        st.session_state.user_journey['engagement_score'] = min(score, 250)
    
    def get_user_segment(self) -> str:
        """사용자 세그먼트 분류"""
        engagement = st.session_state.user_journey['engagement_score']
        ai_usage = st.session_state.user_journey['ai_analysis_count']
        
        if engagement >= 150 and ai_usage >= 3:
            return "high_value"
        elif engagement >= 100 or ai_usage >= 2:
            return "engaged"
        elif engagement >= 50:
            return "interested"
        else:
            return "visitor"
    
    def show_contextual_cta(self, context: str = "general", portfolio_info: Dict[str, Any] = None):
        """상황별 맞춤 CTA 표시"""
        
        # 사용자 세그먼트 확인
        user_segment = self.get_user_segment()
        
        # 액션 추적
        self.track_user_action('cta_view', {'context': context, 'segment': user_segment})
        
        # 컨텍스트별 CTA 구성
        cta_config = self._get_cta_config(context, user_segment, portfolio_info)
        
        # CTA 렌더링
        self._render_cta(cta_config, context)
        
        # 추가 혜택 표시
        self._show_additional_benefits(user_segment)
        
        # 긴급성 메시지 (고가치 사용자)
        if user_segment in ["high_value", "engaged"]:
            self._show_urgency_message(context)
    
    def _get_cta_config(self, context: str, user_segment: str, portfolio_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """CTA 설정 생성"""
        
        base_configs = {
            "high_loss": {
                "title": "🚨 전문가 긴급 상담",
                "subtitle": "큰 손실 방지를 위해 즉시 전문가와 상담하세요",
                "bg_color": "linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%)",
                "urgency": "매우 높음",
                "primary_cta": "긴급 상담 신청",
                "benefits": ["즉시 손실 분석", "리스크 최소화 전략", "전문가 직접 상담"],
                "trust_signals": ["24시간 상담 가능", "무료 긴급 분석", "즉시 연결"]
            },
            "high_profit": {
                "title": "💰 수익 최적화 전문 상담",
                "subtitle": "더 큰 수익을 위한 맞춤 전략을 제안받으세요",
                "bg_color": "linear
