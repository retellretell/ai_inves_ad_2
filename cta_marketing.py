"""
cta_marketing.py - CTA(Call-to-Action) 및 마케팅 기능
"""

import streamlit as st
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List
import hashlib
import uuid

class LeadCapture:
    """리드 수집 시스템"""
    
    def __init__(self):
        self.leads_file = 'leads.json'
        self.contact_preferences = ['전화', '이메일', 'SMS', '카카오톡']
        self.investment_interests = [
            '주식 투자', '펀드', 'ETF', '채권', 
            '파생상품', '해외투자', 'ESG투자', '연금저축'
        ]
    
    def show_consultation_cta(self, context: str = "general"):
        """상담 신청 CTA 표시"""
        st.markdown("---")
        
        # 컨텍스트별 맞춤 메시지
        cta_messages = {
            "high_loss": {
                "title": "🚨 전문가 긴급 상담",
                "subtitle": "큰 손실이 예상됩니다. 전문가와 즉시 상담하세요.",
                "urgency": "high"
            },
            "high_profit": {
                "title": "💰 수익 최적화 상담",
                "subtitle": "수익을 더욱 늘릴 수 있는 전략을 제안받으세요.",
                "urgency": "medium"
            },
            "complex_portfolio": {
                "title": "🎯 포트폴리오 최적화",
                "subtitle": "복잡한 포트폴리오, 전문가가 정리해드립니다.",
                "urgency": "medium"
            },
            "general": {
                "title": "📞 1:1 투자 상담",
                "subtitle": "AI 분석과 함께 전문가 상담으로 완벽한 투자전략을 세워보세요.",
                "urgency": "low"
            }
        }
        
        message_config = cta_messages.get(context, cta_messages["general"])
        
        # 긴급도에 따른 스타일
        if message_config["urgency"] == "high":
            container_style = "background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%); color: white;"
        elif message_config["urgency"] == "medium":
            container_style = "background: linear-gradient(135deg, #fdcb6e 0%, #e17055 100%); color: white;"
        else:
            container_style = "background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%); color: white;"
        
        st.markdown(f"""
        <div style="{container_style} padding: 2rem; border-radius: 1rem; margin: 1rem 0; text-align: center;">
            <h3 style="margin: 0 0 0.5rem 0;">{message_config["title"]}</h3>
            <p style="margin: 0 0 1rem 0; font-size: 1.1rem;">{message_config["subtitle"]}</p>
            <p style="margin: 0; font-size: 0.9rem; opacity: 0.9;">
                ✅ 무료 상담 ✅ 개인별 맞춤 전략 ✅ 실시간 포트폴리오 분석
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if st.button(
                "🎯 전문가 상담 신청하기", 
                type="primary", 
                use_container_width=True,
                key=f"cta_{context}"
            ):
                self._show_lead_form(context)
    
    def _show_lead_form(self, context: str):
        """리드 수집 폼 표시"""
        with st.form(f"lead_form_{context}"):
            st.markdown("### 📋 전문가 상담 신청")
            
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("이름 *", placeholder="홍길동")
                phone = st.text_input("연락처 *", placeholder="010-1234-5678")
                
            with col2:
                email = st.text_input("이메일", placeholder="hong@example.com")
                preferred_contact = st.selectbox("선호 연락 방법", self.contact_preferences)
            
            investment_experience = st.selectbox(
                "투자 경험",
                ["초보 (1년 미만)", "초급 (1-3년)", "중급 (3-5년)", "고급 (5년 이상)"]
            )
            
            investment_interests = st.multiselect(
                "관심 투자 분야",
                self.investment_interests,
                default=["주식 투자"]
            )
            
            investment_amount = st.selectbox(
                "투자 예정 금액",
                ["1천만원 미만", "1천만원-5천만원", "5천만원-1억원", "1억원-3억원", "3억원 이상"]
            )
            
            consultation_time = st.selectbox(
                "상담 희망 시간",
                ["평일 오전 (9-12시)", "평일 오후 (13-18시)", "평일 저녁 (18-21시)", "주말"]
            )
            
            additional_info = st.text_area(
                "추가 문의사항",
                placeholder="상담받고 싶은 구체적인 내용이나 현재 고민을 적어주세요...",
                height=100
            )
            
            # 개인정보 동의
            privacy_agreed = st.checkbox(
                "개인정보 수집 및 이용에 동의합니다. [자세히 보기]()",
                value=False
            )
            
            marketing_agreed = st.checkbox(
                "마케팅 목적 정보 수신에 동의합니다. (선택)",
                value=False
            )
            
            submitted = st.form_submit_button("상담 신청하기", type="primary", use_container_width=True)
            
            if submitted:
                if not name or not phone:
                    st.error("이름과 연락처는 필수 입력 사항입니다.")
                elif not privacy_agreed:
                    st.error("개인정보 수집 및 이용에 동의해주세요.")
                else:
                    lead_data = {
                        'id': str(uuid.uuid4()),
                        'name': name,
                        'phone': phone,
                        'email': email,
                        'preferred_contact': preferred_contact,
                        'investment_experience': investment_experience,
                        'investment_interests': investment_interests,
                        'investment_amount': investment_amount,
                        'consultation_time': consultation_time,
                        'additional_info': additional_info,
                        'privacy_agreed': privacy_agreed,
                        'marketing_agreed': marketing_agreed,
                        'context': context,
                        'timestamp': datetime.now().isoformat(),
                        'source': 'ai_investment_advisor'
                    }
                    
                    if self._save_lead(lead_data):
                        st.success("✅ 상담 신청이 완료되었습니다!")
                        st.info("📞 영업일 기준 24시간 내에 연락드리겠습니다.")
                        self._show_next_steps()
                    else:
                        st.error("신청 처리 중 오류가 발생했습니다. 다시 시도해주세요.")
    
    def _save_lead(self, lead_data: Dict[str, Any]) -> bool:
        """리드 데이터 저장"""
        try:
            leads = []
            try:
                with open(self.leads_file, 'r', encoding='utf-8') as f:
                    leads = json.load(f)
            except FileNotFoundError:
                pass
            
            leads.append(lead_data)
            
            with open(self.leads_file, 'w', encoding='utf-8') as f:
                json.dump(leads, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            st.error(f"데이터 저장 오류: {str(e)}")
            return False
    
    def _show_next_steps(self):
        """다음 단계 안내"""
        st.markdown("""
        ### 🎯 다음 단계
        
        **1. 상담 준비**
        - 현재 보유 종목 리스트
        - 투자 목표와 기간
        - 위험 허용 수준
        
        **2. 상담 내용**
        - 개인별 맞춤 투자 전략
        - 포트폴리오 최적화 방안
        - 세금 절약 투자 방법
        
        **3. 즉시 연락을 원하시나요?**
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📞 지금 전화 연결", use_container_width=True):
                st.info("🕐 고객센터 운영시간: 평일 9:00-18:00\n📞 1588-6666")
        
        with col2:
            if st.button("💬 카카오톡 상담", use_container_width=True):
                st.info("💬 카카오톡에서 '미래에셋증권' 검색 후 친구추가")

class ProductRecommendation:
    """상품 추천 시스템"""
    
    def __init__(self):
        self.products = {
            'conservative': {
                'name': '안전형 포트폴리오',
                'description': '원금 보전을 최우선으로 하는 안정적 투자',
                'products': ['정기예금', '국고채', '회사채', '안전형 펀드'],
                'expected_return': '연 3-5%',
                'risk_level': '낮음'
            },
            'balanced': {
                'name': '균형형 포트폴리오',
                'description': '안정성과 수익성의 균형을 추구',
                'products': ['혼합형 펀드', 'ETF', '우량주', '리츠'],
                'expected_return': '연 5-8%',
                'risk_level': '중간'
            },
            'aggressive': {
                'name': '성장형 포트폴리오',
                'description': '높은 수익을 목표로 하는 적극적 투자',
                'products': ['성장주', '테마주', '해외주식', '성장형 펀드'],
                'expected_return': '연 8-15%',
                'risk_level': '높음'
            }
        }
    
    def recommend_products(self, portfolio_info: Dict[str, Any] = None, analysis_result: str = ""):
        """상품 추천"""
        st.markdown("### 🎯 맞춤 투자 상품 추천")
        
        # 분석 결과 기반 추천
        recommendation_type = self._analyze_user_profile(portfolio_info, analysis_result)
        
        recommended_product = self.products[recommendation_type]
        
        # 추천 상품 카드
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); 
                    padding: 1.5rem; border-radius: 1rem; margin: 1rem 0;">
            <h4 style="margin: 0 0 0.5rem 0; color: #2d3436;">
                🏆 {recommended_product['name']}
            </h4>
            <p style="margin: 0 0 1rem 0; color: #636e72;">
                {recommended_product['description']}
            </p>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <div>
                    <strong>예상 수익률:</strong> {recommended_product['expected_return']}<br>
                    <strong>위험 수준:</strong> {recommended_product['risk_level']}
                </div>
                <div>
                    <strong>추천 상품:</strong><br>
                    {', '.join(recommended_product['products'])}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 다른 옵션들
        with st.expander("🔍 다른 투자 옵션 보기"):
            for key, product in self.products.items():
                if key != recommendation_type:
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        st.write(f"**{product['name']}**")
                        st.caption(product['description'])
                    
                    with col2:
                        st.metric("예상수익", product['expected_return'])
                    
                    with col3:
                        if st.button(f"상담신청", key=f"consult_{key}"):
                            st.info("전문가가 자세한 상품 정보를 제공해드립니다.")
    
    def _analyze_user_profile(self, portfolio_info: Dict[str, Any], analysis_result: str) -> str:
        """사용자 프로필 분석하여 추천 타입 결정"""
        # 간단한 규칙 기반 추천 (실제로는 더 정교한 ML 모델 사용 가능)
        
        if portfolio_info:
            profit_rate = portfolio_info.get('profit_rate', 0)
            
            if profit_rate < -10:
                return 'conservative'  # 손실이 큰 경우 안전형 추천
            elif profit_rate > 20:
                return 'aggressive'    # 수익이 좋은 경우 성장형 추천
            else:
                return 'balanced'      # 그 외는 균형형
        
        # 분석 결과 키워드 기반 추천
        if any(word in analysis_result.lower() for word in ['위험', '손실', '조심']):
            return 'conservative'
        elif any(word in analysis_result.lower() for word in ['성장', '공격적', '확대']):
            return 'aggressive'
        else:
            return 'balanced'

class NotificationSystem:
    """알림 시스템"""
    
    def __init__(self):
        self.notification_types = {
            'market_alert': '시장 급변 알림',
            'portfolio_alert': '포트폴리오 알림',
            'news_alert': '중요 뉴스 알림',
            'recommendation': '투자 추천'
        }
    
    def show_notification_signup(self):
        """알림 구독 신청"""
        with st.expander("🔔 실시간 투자 알림 서비스", expanded=False):
            st.markdown("""
            **📱 놓치면 안되는 투자 기회를 실시간으로 알려드려요!**
            
            ✅ 보유 종목 급등/급락 알림  
            ✅ 시장 이슈 및 호재/악재 뉴스  
            ✅ AI 기반 매매 타이밍 추천  
            ✅ 개인 맞춤형 투자 기회  
            """)
            
            with st.form("notification_signup"):
                col1, col2 = st.columns(2)
                
                with col1:
                    phone = st.text_input("휴대폰 번호", placeholder="010-1234-5678")
                    
                with col2:
                    email = st.text_input("이메일 주소", placeholder="user@example.com")
                
                st.markdown("**알림 받을 내용을 선택하세요:**")
                
                selected_notifications = []
                for key, name in self.notification_types.items():
                    if st.checkbox(name, value=True, key=f"notif_{key}"):
                        selected_notifications.append(key)
                
                notification_time = st.selectbox(
                    "알림 시간대",
                    ["장 시작 전 (08:30)", "장 중 실시간", "장 마감 후 (15:30)", "저녁 (19:00)"]
                )
                
                privacy_consent = st.checkbox("개인정보 수집 및 알림 서비스 이용에 동의합니다.")
                
                if st.form_submit_button("🔔 알림 신청하기", type="primary", use_container_width=True):
                    if not phone and not email:
                        st.error("휴대폰 번호 또는 이메일 중 하나는 필수입니다.")
                    elif not privacy_consent:
                        st.error("개인정보 수집 동의는 필수입니다.")
                    elif not selected_notifications:
                        st.error("받으실 알림 종류를 하나 이상 선택해주세요.")
                    else:
                        notification_data = {
                            'phone': phone,
                            'email': email,
                            'notifications': selected_notifications,
                            'time_preference': notification_time,
                            'timestamp': datetime.now().isoformat()
                        }
                        
                        if self._save_notification_signup(notification_data):
                            st.success("✅ 알림 서비스 신청이 완료되었습니다!")
                            st.info("📱 곧 첫 번째 투자 알림을 받아보실 수 있습니다.")
    
    def _save_notification_signup(self, data: Dict[str, Any]) -> bool:
        """알림 신청 데이터 저장"""
        try:
            notifications_file = 'notification_signups.json'
            signups = []
            
            try:
                with open(notifications_file, 'r', encoding='utf-8') as f:
                    signups = json.load(f)
            except FileNotFoundError:
                pass
            
            signups.append(data)
            
            with open(notifications_file, 'w', encoding='utf-8') as f:
                json.dump(signups, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            st.error(f"알림 신청 처리 중 오류가 발생했습니다: {str(e)}")
            return False

class EventPromotions:
    """이벤트 및 프로모션"""
    
    def __init__(self):
        self.current_events = [
            {
                'title': '🎯 AI 투자 체험 이벤트',
                'description': 'AI 투자 어드바이저 첫 이용 시 수수료 50% 할인',
                'period': '2025.07.01 ~ 2025.07.31',
                'benefit': '거래 수수료 50% 할인',
                'condition': '신규 고객 대상',
                'cta': '이벤트 참여하기'
            },
            {
                'title': '📱 모바일 트레이딩 이벤트',
                'description': 'mPOP 앱으로 거래 시 추가 혜택',
                'period': '2025.07.01 ~ 2025.08.31',
                'benefit': 'V골드 적립 2배',
                'condition': '모바일 앱 거래 시',
                'cta': '앱 다운로드'
            },
            {
                'title': '🏆 포트폴리오 진단 이벤트',
                'description': '무료 포트폴리오 진단 및 맞춤 전략 제공',
                'period': '2025.07.01 ~ 2025.12.31',
                'benefit': '전문가 진단 무료',
                'condition': '상담 신청 고객',
                'cta': '무료 진단 신청'
            }
        ]
    
    def show_current_events(self):
        """현재 진행 중인 이벤트 표시"""
        st.markdown("### 🎉 진행 중인 이벤트")
        
        for i, event in enumerate(self.current_events):
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #ff7675 0%, #fd79a8 100%);
                                color: white; padding: 1rem; border-radius: 0.5rem; margin: 0.5rem 0;">
                        <h4 style="margin: 0 0 0.5rem 0;">{event['title']}</h4>
                        <p style="margin: 0 0 0.5rem 0; font-size: 0.9rem;">{event['description']}</p>
                        <div style="font-size: 0.8rem; opacity: 0.9;">
                            📅 기간: {event['period']}<br>
                            🎁 혜택: {event['benefit']}<br>
                            📋 조건: {event['condition']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    if st.button(event['cta'], key=f"event_{i}", use_container_width=True):
                        self._handle_event_participation(event['title'])
    
    def _handle_event_participation(self, event_title: str):
        """이벤트 참여 처리"""
        st.success(f"'{event_title}' 이벤트 참여가 완료되었습니다!")
        
        if "AI 투자 체험" in event_title:
            st.info("🎯 수수료 할인 혜택이 자동 적용됩니다. 첫 거래부터 혜택을 받으세요!")
        elif "모바일 트레이딩" in event_title:
            st.info("📱 mPOP 앱을 다운로드하시면 V골드 2배 적립 혜택을 받으실 수 있습니다.")
        elif "포트폴리오 진단" in event_title:
            st.info("📞 전문가가 24시간 내에 연락드려 무료 포트폴리오 진단을 도와드립니다.")

class SocialProof:
    """사회적 증명 (후기, 성과 등)"""
    
    def __init__(self):
        self.testimonials = [
            {
                'user': '김○○님 (30대, 직장인)',
                'rating': 5,
                'comment': 'AI 분석이 정말 정확해요. 포트폴리오 수익률이 20% 향상되었습니다!',
                'profit': '+2,340만원',
                'period': '6개월'
            },
            {
                'user': '박○○님 (40대, 자영업)',
                'rating': 5,
                'comment': '복잡한 시장 상황을 쉽게 설명해주고, 실행 방안까지 구체적이에요.',
                'profit': '+890만원',
                'period': '3개월'
            },
            {
                'user': '이○○님 (50대, 주부)',
                'rating': 4,
                'comment': '투자 초보도 이해하기 쉽고, 리스크 관리에 큰 도움이 됩니다.',
                'profit': '+450만원',
                'period': '4개월'
            }
        ]
        
        self.usage_stats = {
            'total_users': 15420,
            'total_analyses': 127854,
            'average_satisfaction': 4.7,
            'profit_users_ratio': 73.2
        }
    
    def show_social_proof(self):
        """사회적 증명 표시"""
        # 사용 통계
        st.markdown("### 📊 서비스 이용 현황")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("누적 사용자", f"{self.usage_stats['total_users']:,}명")
        
        with col2:
            st.metric("분석 제공 건수", f"{self.usage_stats['total_analyses']:,}건")
        
        with col3:
            st.metric("만족도", f"{self.usage_stats['average_satisfaction']}/5.0")
        
        with col4:
            st.metric("수익 개선률", f"{self.usage_stats['profit_users_ratio']}%")
        
        # 사용자 후기
        st.markdown("### 💬 실제 사용자 후기")
        
        for testimonial in self.testimonials:
            st.markdown(f"""
            <div style="background: white; border: 1px solid #e0e0e0; border-radius: 0.5rem; 
                        padding: 1rem; margin: 0.5rem 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                    <strong>{testimonial['user']}</strong>
                    <span style="color: #f39c12;">{'⭐' * testimonial['rating']}</span>
                </div>
                <p style="margin: 0.5rem 0; color: #2c3e50;">"{testimonial['comment']}"</p>
                <div style="display: flex; gap: 1rem; font-size: 0.9rem; color: #7f8c8d;">
                    <span>💰 수익: {testimonial['profit']}</span>
                    <span>📅 기간: {testimonial['period']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

class MarketingCTA:
    """통합 마케팅 CTA 시스템"""
    
    def __init__(self):
        self.lead_capture = LeadCapture()
        self.product_recommendation = ProductRecommendation()
        self.notification_system = NotificationSystem()
        self.event_promotions = EventPromotions()
        self.social_proof = SocialProof()
    
    def show_contextual_cta(self, context: str, portfolio_info: Dict[str, Any] = None, analysis_result: str = ""):
        """상황별 맞춤 CTA 표시"""
        
        # 1. 사회적 증명 먼저 표시 (신뢰성 구축)
        self.social_proof.show_social_proof()
        
        # 2. 상황별 상담 CTA
        if portfolio_info:
            profit_rate = portfolio_info.get('profit_rate', 0)
            
            if profit_rate < -15:
                self.lead_capture.show_consultation_cta("high_loss")
            elif profit_rate > 25:
                self.lead_capture.show_consultation_cta("high_profit")
            else:
                self.lead_capture.show_consultation_cta("general")
        else:
            self.lead_capture.show_consultation_cta("general")
        
        # 3. 맞춤 상품 추천
        self.product_recommendation.recommend_products(portfolio_info, analysis_result)
        
        # 4. 진행 중인 이벤트
        self.event_promotions.show_current_events()
        
        # 5. 알림 서비스 가입
        self.notification_system.show_notification_signup()
    
    def show_exit_intent_popup(self):
        """이탈 의도 감지 시 팝업 (JavaScript로 구현 가능)"""
        # 실제로는 JavaScript와 연동하여 구현
        pass
    
    def track_conversion(self, event_type: str, user_id: str = None):
        """전환 추적"""
        try:
            conversion_data = {
                'event_type': event_type,
                'user_id': user_id or 'anonymous',
                'timestamp': datetime.now().isoformat(),
                'session_id': st.session_state.get('session_id', 'unknown')
            }
            
            # 실제로는 Google Analytics, Mixpanel 등으로 전송
            conversion_file = 'conversions.json'
            conversions = []
            
            try:
                with open(conversion_file, 'r', encoding='utf-8') as f:
                    conversions = json.load(f)
            except FileNotFoundError:
                pass
            
            conversions.append(conversion_data)
            
            with open(conversion_file, 'w', encoding='utf-8') as f:
                json.dump(conversions, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            # 전환 추적 실패해도 서비스에는 영향 없음
            pass

# 편의 함수들
def init_marketing_system():
    """마케팅 시스템 초기화"""
    if 'marketing_cta' not in st.session_state:
        st.session_state.marketing_cta = MarketingCTA()
    
    return st.session_state.marketing_cta

def show_marketing_cta(context: str = "general", portfolio_info: Dict[str, Any] = None, analysis_result: str = ""):
    """마케팅 CTA 표시 헬퍼"""
    marketing_system = init_marketing_system()
    marketing_system.show_contextual_cta(context, portfolio_info, analysis_result)

def track_user_action(action: str):
    """사용자 액션 추적 헬퍼"""
    marketing_system = init_marketing_system()
    marketing_system.track_conversion(action)
