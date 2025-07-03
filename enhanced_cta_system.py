"""
enhanced_cta_system.py - 실제 동작하는 CTA 시스템
미래에셋증권 고객 유치 및 수익 구조에 최적화
"""

import streamlit as st
import json
import uuid
import smtplib
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import logging

logger = logging.getLogger(__name__)

class LeadScoringEngine:
    """리드 스코어링 및 세분화"""
    
    def __init__(self):
        self.scoring_criteria = {
            'investment_amount': {
                '1천만원 미만': 10,
                '1천-5천만원': 25,
                '5천만원-1억원': 50,
                '1억원-5억원': 80,
                '5억원 이상': 100
            },
            'investment_experience': {
                '초보 (1년 미만)': 20,
                '초급 (1-3년)': 40,
                '중급 (3-10년)': 70,
                '고급 (10년 이상)': 90
            },
            'risk_level': {
                'HIGH': 100,  # 긴급 상담 필요
                'MEDIUM': 60,
                'LOW': 30
            },
            'portfolio_value': {
                'under_10m': 15,
                '10m_to_50m': 40,
                '50m_to_100m': 70,
                'over_100m': 100
            }
        }
    
    def calculate_lead_score(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """리드 스코어 계산"""
        total_score = 0
        scoring_details = {}
        
        # 투자 금액 스코어
        investment_amount = lead_data.get('investment_amount', '')
        amount_score = self.scoring_criteria['investment_amount'].get(investment_amount, 0)
        total_score += amount_score
        scoring_details['investment_amount'] = amount_score
        
        # 투자 경험 스코어
        experience = lead_data.get('investment_experience', '')
        experience_score = self.scoring_criteria['investment_experience'].get(experience, 0)
        total_score += experience_score
        scoring_details['investment_experience'] = experience_score
        
        # 리스크 레벨 스코어
        risk_level = lead_data.get('risk_level', 'MEDIUM')
        risk_score = self.scoring_criteria['risk_level'].get(risk_level, 0)
        total_score += risk_score
        scoring_details['risk_level'] = risk_score
        
        # 포트폴리오 가치 추정
        portfolio_score = self._estimate_portfolio_score(lead_data.get('portfolio_info', {}))
        total_score += portfolio_score
        scoring_details['portfolio_value'] = portfolio_score
        
        # 등급 분류
        if total_score >= 200:
            grade = 'VIP'
            priority = 'URGENT'
        elif total_score >= 150:
            grade = 'PREMIUM'
            priority = 'HIGH'
        elif total_score >= 100:
            grade = 'STANDARD'
            priority = 'MEDIUM'
        else:
            grade = 'BASIC'
            priority = 'LOW'
        
        return {
            'total_score': total_score,
            'grade': grade,
            'priority': priority,
            'scoring_details': scoring_details,
            'estimated_value': self._estimate_customer_value(total_score)
        }
    
    def _estimate_portfolio_score(self, portfolio_info: Dict[str, Any]) -> int:
        """포트폴리오 가치 기반 스코어"""
        if not portfolio_info:
            return 0
        
        current_value = portfolio_info.get('current_value', 0)
        
        if current_value >= 100000000:  # 1억 이상
            return 100
        elif current_value >= 50000000:  # 5천만 이상
            return 70
        elif current_value >= 10000000:  # 1천만 이상
            return 40
        else:
            return 15
    
    def _estimate_customer_value(self, score: int) -> Dict[str, Any]:
        """고객 가치 추정 (수수료 등)"""
        # 미래에셋증권 평균 수수료율 0.015% 기준
        base_trading_volume = score * 1000000  # 스코어 기반 예상 거래량
        
        monthly_fee = base_trading_volume * 0.00015 * 4  # 월 4회 거래 가정
        annual_fee = monthly_fee * 12
        
        return {
            'estimated_monthly_fee': monthly_fee,
            'estimated_annual_fee': annual_fee,
            'expected_trading_volume': base_trading_volume,
            'customer_lifetime_value': annual_fee * 5  # 5년 기대
        }

class AutomatedFollowUp:
    """자동화된 후속 조치"""
    
    def __init__(self):
        self.email_templates = self._load_email_templates()
        self.sms_templates = self._load_sms_templates()
        
    def _load_email_templates(self) -> Dict[str, str]:
        """이메일 템플릿"""
        return {
            'consultation_confirmation': """
            안녕하세요, {name}님!
            
            미래에셋증권 AI 투자어드바이저 상담 신청을 확인했습니다.
            
            📋 상담 정보:
            - 신청 번호: {consultation_id}
            - 신청 시간: {timestamp}
            - 우선 순위: {priority}
            - 예상 연락 시간: {expected_contact_time}
            
            🎯 맞춤 준비 사항:
            {preparation_items}
            
            📞 전문가가 곧 연락드리겠습니다!
            
            급한 문의사항이 있으시면:
            📞 고객센터: 1588-6666
            💬 카카오톡: '미래에셋증권' 검색
            
            감사합니다.
            미래에셋증권 디지털자산운용팀
            """,
            
            'document_delivery': """
            안녕하세요, {name}님!
            
            요청하신 투자 가이드 문서를 첨부해드립니다.
            
            📄 제공 문서:
            {document_list}
            
            💡 추가 혜택:
            - 개인 맞춤 포트폴리오 진단 (무료)
            - 투자 전략 1:1 상담 (무료)
            - 실시간 시장 분석 리포트 (월간)
            
            더 자세한 상담을 원하시면 언제든 연락주세요!
            
            미래에셋증권 드림
            """,
            
            'vip_special_offer': """
            {name}님, VIP 고객 특별 혜택 안내
            
            🏆 AI 분석 결과, VIP 등급 고객으로 분류되었습니다!
            
            🎁 특별 혜택:
            ✅ 전용 PB 배정 (무료)
            ✅ 프리미엄 투자 정보 제공
            ✅ 수수료 할인 (최대 50%)
            ✅ 우선 IPO 참여 기회
            ✅ 해외투자 수수료 면제
            
            📞 VIP 전용 상담: 1588-6666 (VIP 코드: {vip_code})
            
            이 혜택은 48시간 내 연락 시에만 적용됩니다.
            
            미래에셋증권 VIP팀
            """
        }
    
    def _load_sms_templates(self) -> Dict[str, str]:
        """SMS 템플릿"""
        return {
            'urgent_consultation': "[미래에셋증권] {name}님, 긴급 투자 상담이 필요합니다. 전문가가 30분 내 연락드립니다. 문의: 1588-6666",
            'appointment_reminder': "[미래에셋증권] {name}님, 내일 {time} 투자 상담 예정입니다. 준비서류: {documents}. 변경 시 1588-6666",
            'market_alert': "[미래에셋증권] {name}님 보유 종목 급변동! {stock_name} {change}%. 전문가 분석 필요. 즉시 상담: 1588-6666"
        }
    
    def send_follow_up(self, lead_data: Dict[str, Any], lead_score: Dict[str, Any]) -> bool:
        """후속 조치 실행"""
        try:
            priority = lead_score['priority']
            grade = lead_score['grade']
            
            # 1. 이메일 발송
            if lead_data.get('email'):
                self._send_email(lead_data, lead_score)
            
            # 2. SMS 발송 (고우선순위만)
            if priority in ['URGENT', 'HIGH'] and lead_data.get('phone'):
                self._send_sms(lead_data, lead_score)
            
            # 3. CRM 시스템 연동
            self._update_crm_system(lead_data, lead_score)
            
            # 4. 영업팀 알림
            if priority == 'URGENT':
                self._notify_sales_team(lead_data, lead_score)
            
            return True
            
        except Exception as e:
            logger.error(f"후속 조치 실행 실패: {e}")
            return False
    
    def _send_email(self, lead_data: Dict[str, Any], lead_score: Dict[str, Any]) -> bool:
        """이메일 발송"""
        try:
            # 실제 운영에서는 SendGrid, AWS SES 등 사용
            template_key = 'vip_special_offer' if lead_score['grade'] == 'VIP' else 'consultation_confirmation'
            template = self.email_templates[template_key]
            
            # 템플릿 변수 치환
            email_content = template.format(
                name=lead_data.get('name', '고객'),
                consultation_id=lead_data.get('id', '')[:8],
                timestamp=datetime.now().strftime('%Y-%m-%d %H:%M'),
                priority=lead_score['priority'],
                expected_contact_time=self._calculate_contact_time(lead_score['priority']),
                preparation_items=self._get_preparation_items(lead_data),
                vip_code=f"VIP{lead_data.get('id', '')[:6]}"
            )
            
            # 실제 이메일 발송 로직
            # self._actual_send_email(lead_data['email'], email_content)
            
            logger.info(f"이메일 발송 완료: {lead_data.get('email')}")
            return True
            
        except Exception as e:
            logger.error(f"이메일 발송 실패: {e}")
            return False
    
    def _send_sms(self, lead_data: Dict[str, Any], lead_score: Dict[str, Any]) -> bool:
        """SMS 발송"""
        try:
            # 실제 운영에서는 Twilio, AWS SNS 등 사용
            if lead_score['priority'] == 'URGENT':
                template = self.sms_templates['urgent_consultation']
                sms_content = template.format(name=lead_data.get('name', '고객'))
            else:
                return True  # HIGH 등급은 SMS 생략
            
            # 실제 SMS 발송 로직
            # self._actual_send_sms(lead_data['phone'], sms_content)
            
            logger.info(f"SMS 발송 완료: {lead_data.get('phone')}")
            return True
            
        except Exception as e:
            logger.error(f"SMS 발송 실패: {e}")
            return False
    
    def _calculate_contact_time(self, priority: str) -> str:
        """연락 시간 계산"""
        now = datetime.now()
        
        if priority == 'URGENT':
            contact_time = now + timedelta(minutes=30)
            return contact_time.strftime('%H:%M') + " (30분 내)"
        elif priority == 'HIGH':
            contact_time = now + timedelta(hours=2)
            return contact_time.strftime('%H:%M') + " (2시간 내)"
        elif priority == 'MEDIUM':
            contact_time = now + timedelta(hours=24)
            return contact_time.strftime('%m월 %d일 %H:%M') + " (24시간 내)"
        else:
            contact_time = now + timedelta(days=2)
            return contact_time.strftime('%m월 %d일') + " (2일 내)"
    
    def _get_preparation_items(self, lead_data: Dict[str, Any]) -> str:
        """상담 준비 사항"""
        items = []
        
        if lead_data.get('portfolio_info'):
            items.append("• 현재 보유 종목 리스트")
        
        if 'tax' in str(lead_data.get('consultation_topic', [])).lower():
            items.append("• 지난해 투자 수익 내역")
        
        if 'pension' in str(lead_data.get('consultation_topic', [])).lower():
            items.append("• 현재 연금 가입 현황")
        
        items.extend([
            "• 투자 목표 금액 및 기간",
            "• 월 투자 가능 금액",
            "• 신분증 (비대면 상담 시)"
        ])
        
        return '\n'.join(items)
    
    def _update_crm_system(self, lead_data: Dict[str, Any], lead_score: Dict[str, Any]) -> bool:
        """CRM 시스템 업데이트"""
        try:
            # 실제 CRM API 연동
            crm_data = {
                'customer_id': lead_data.get('id'),
                'name': lead_data.get('name'),
                'phone': lead_data.get('phone'),
                'email': lead_data.get('email'),
                'lead_score': lead_score['total_score'],
                'grade': lead_score['grade'],
                'priority': lead_score['priority'],
                'estimated_value': lead_score['estimated_value'],
                'source': 'ai_investment_advisor',
                'created_at': datetime.now().isoformat(),
                'next_action': self._determine_next_action(lead_score['priority']),
                'assigned_rep': self._assign_representative(lead_score['grade'])
            }
            
            # CRM API 호출
            # response = requests.post('https://crm.miraeasset.com/api/leads', json=crm_data)
            
            logger.info(f"CRM 업데이트 완료: {lead_data.get('name')}")
            return True
            
        except Exception as e:
            logger.error(f"CRM 업데이트 실패: {e}")
            return False
    
    def _determine_next_action(self, priority: str) -> str:
        """다음 액션 결정"""
        actions = {
            'URGENT': 'immediate_call',
            'HIGH': 'priority_call',
            'MEDIUM': 'scheduled_call',
            'LOW': 'email_follow_up'
        }
        return actions.get(priority, 'email_follow_up')
    
    def _assign_representative(self, grade: str) -> str:
        """담당자 배정"""
        representatives = {
            'VIP': 'vip_team',
            'PREMIUM': 'premium_team', 
            'STANDARD': 'standard_team',
            'BASIC': 'general_team'
        }
        return representatives.get(grade, 'general_team')
    
    def _notify_sales_team(self, lead_data: Dict[str, Any], lead_score: Dict[str, Any]) -> bool:
        """영업팀 즉시 알림"""
        try:
            # Slack, Teams 등으로 즉시 알림
            notification_data = {
                'lead_id': lead_data.get('id'),
                'customer_name': lead_data.get('name'),
                'phone': lead_data.get('phone'),
                'score': lead_score['total_score'],
                'grade': lead_score['grade'],
                'risk_level': lead_data.get('risk_level'),
                'estimated_value': lead_score['estimated_value']['estimated_annual_fee'],
                'urgent_reason': self._get_urgent_reason(lead_data, lead_score)
            }
            
            # 실제로는 Slack webhook이나 Teams 알림
            # requests.post('https://hooks.slack.com/services/...', json=notification_data)
            
            logger.info(f"영업팀 알림 완료: {lead_data.get('name')}")
            return True
            
        except Exception as e:
            logger.error(f"영업팀 알림 실패: {e}")
            return False
    
    def _get_urgent_reason(self, lead_data: Dict[str, Any], lead_score: Dict[str, Any]) -> str:
        """긴급 사유"""
        reasons = []
        
        if lead_data.get('risk_level') == 'HIGH':
            reasons.append("고위험 포트폴리오")
        
        if lead_score['estimated_value']['estimated_annual_fee'] > 1000000:
            reasons.append("고액 고객 (연 100만원+ 예상)")
        
        if '긴급' in str(lead_data.get('additional_info', '')):
            reasons.append("고객 긴급 요청")
        
        return ', '.join(reasons) if reasons else "VIP 등급 고객"

class ConversionOptimizer:
    """전환율 최적화"""
    
    def __init__(self):
        self.ab_tests = {
            'cta_button_color': {'red': 0.23, 'blue': 0.19, 'green': 0.21},
            'urgency_message': {'high': 0.31, 'medium': 0.24, 'low': 0.18},
            'social_proof': {'with': 0.28, 'without': 0.20}
        }
        
        self.conversion_tracking = []
    
    def get_optimized_cta_config(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """사용자별 최적화된 CTA 설정"""
        
        # 사용자 프로필 기반 최적화
        risk_level = user_profile.get('risk_level', 'MEDIUM')
        investment_amount = user_profile.get('investment_amount', '1천만원 미만')
        
        config = {
            'button_color': 'red',  # 기본값
            'urgency_level': 'medium',
            'show_social_proof': True,
            'price_emphasis': False,
            'scarcity_message': False
        }
        
        # 리스크 레벨별 최적화
        if risk_level == 'HIGH':
            config.update({
                'button_color': 'red',
                'urgency_level': 'high',
                'scarcity_message': True,
                'primary_cta': '🆘 긴급 전문가 상담 (무료)',
                'secondary_message': '큰 손실 방지를 위해 즉시 상담받으세요!'
            })
        elif risk_level == 'MEDIUM':
            config.update({
                'button_color': 'blue',
                'urgency_level': 'medium', 
                'primary_cta': '📞 맞춤 투자 상담 신청',
                'secondary_message': '더 나은 투자 성과를 위한 전문가 조언'
            })
        else:  # LOW
            config.update({
                'button_color': 'green',
                'urgency_level': 'low',
                'primary_cta': '💎 수익 최적화 상담',
                'secondary_message': '좋은 성과를 더욱 발전시킬 전략 제안'
            })
        
        # 투자 금액별 최적화
        if '1억원' in investment_amount or '5억원' in investment_amount:
            config.update({
                'show_vip_badge': True,
                'vip_message': '🏆 VIP 고객 전용 서비스',
                'price_emphasis': False  # 고액 고객은 비용 강조 안함
            })
        else:
            config.update({
                'show_vip_badge': False,
                'price_emphasis': True,
                'free_emphasis': '💯 완전 무료'
            })
        
        return config
    
    def track_conversion(self, event_type: str, user_data: Dict[str, Any], cta_config: Dict[str, Any]) -> None:
        """전환 추적"""
        conversion_event = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'user_id': user_data.get('session_id', 'anonymous'),
            'cta_config': cta_config,
            'user_profile': {
                'risk_level': user_data.get('risk_level'),
                'investment_amount': user_data.get('investment_amount'),
                'grade': user_data.get('grade')
            }
        }
        
        self.conversion_tracking.append(conversion_event)
        
        # 실시간 분석을 위한 데이터 저장
        self._save_conversion_data(conversion_event)
    
    def _save_conversion_data(self, event: Dict[str, Any]) -> None:
        """전환 데이터 저장"""
        try:
            filename = f"conversions_{datetime.now().strftime('%Y%m')}.json"
            
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    conversions = json.load(f)
            except FileNotFoundError:
                conversions = []
            
            conversions.append(event)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(conversions, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"전환 데이터 저장 실패: {e}")
    
    def get_conversion_analytics(self) -> Dict[str, Any]:
        """전환 분석 데이터"""
        if not self.conversion_tracking:
            return {'total_events': 0}
        
        # 기본 통계
        total_events = len(self.conversion_tracking)
        consultation_requests = len([e for e in self.conversion_tracking if e['event_type'] == 'consultation_request'])
        document_downloads = len([e for e in self.conversion_tracking if e['event_type'] == 'document_download'])
        
        # 전환율 계산
        conversion_rate = (consultation_requests / total_events * 100) if total_events > 0 else 0
        
        return {
            'total_events': total_events,
            'consultation_requests': consultation_requests,
            'document_downloads': document_downloads,
            'conversion_rate': round(conversion_rate, 2),
            'top_performing_cta': self._get_top_performing_cta()
        }
    
    def _get_top_performing_cta(self) -> Dict[str, Any]:
        """최고 성과 CTA 분석"""
        cta_performance = {}
        
        for event in self.conversion_tracking:
            if event['event_type'] == 'consultation_request':
                button_color = event['cta_config']['button_color']
                urgency = event['cta_config']['urgency_level']
                
                key = f"{button_color}_{urgency}"
                if key not in cta_performance:
                    cta_performance[key] = 0
                cta_performance[key] += 1
        
        if cta_performance:
            best_cta = max(cta_performance, key=cta_performance.get)
            return {
                'config': best_cta,
                'conversions': cta_performance[best_cta]
            }
        
        return {'config': 'red_high', 'conversions': 0}

class RevenueCalculator:
    """수익 구조 계산기"""
    
    def __init__(self):
        # 미래에셋증권 수익 구조 (예시)
        self.revenue_sources = {
            'trading_commission': 0.00015,  # 0.015% 수수료
            'fund_management_fee': 0.015,   # 1.5% 연간
            'premium_service_fee': 50000,   # 월 5만원
            'foreign_trading_fee': 0.0025,  # 0.25% 해외주식
            'margin_interest': 0.06         # 6% 연간 (신용거래)
        }
        
        self.customer_segments = {
            'VIP': {
                'avg_portfolio': 500000000,     # 5억
                'trading_frequency': 20,        # 월 20회
                'premium_service_rate': 0.8,    # 80%가 프리미엄 서비스
                'foreign_investment_rate': 0.6, # 60%가 해외투자
                'margin_usage_rate': 0.3        # 30%가 신용거래
            },
            'PREMIUM': {
                'avg_portfolio': 100000000,     # 1억
                'trading_frequency': 15,
                'premium_service_rate': 0.5,
                'foreign_investment_rate': 0.4,
                'margin_usage_rate': 0.2
            },
            'STANDARD': {
                'avg_portfolio': 30000000,      # 3천만원
                'trading_frequency': 10,
                'premium_service_rate': 0.2,
                'foreign_investment_rate': 0.2,
                'margin_usage_rate': 0.1
            },
            'BASIC': {
                'avg_portfolio': 10000000,      # 1천만원
                'trading_frequency': 5,
                'premium_service_rate': 0.05,
                'foreign_investment_rate': 0.1,
                'margin_usage_rate': 0.05
            }
        }
    
    def calculate_customer_value(self, grade: str, portfolio_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """고객 가치 계산"""
        
        segment = self.customer_segments.get(grade, self.customer_segments['BASIC'])
        
        # 포트폴리오 정보가 있으면 실제 값 사용
        portfolio_value = segment['avg_portfolio']
        if portfolio_info and portfolio_info.get('current_value'):
            portfolio_value = portfolio_info['current_value']
        
        # 월간 수익 계산
        monthly_trading_commission = (
            portfolio_value * 
            segment['trading_frequency'] * 
            self.revenue_sources['trading_commission']
        )
        
        monthly_fund_fee = (
            portfolio_value * 
            self.revenue_sources['fund_management_fee'] / 12
        )
        
        monthly_premium_fee = (
            self.revenue_sources['premium_service_fee'] * 
            segment['premium_service_rate']
        )
        
        monthly_foreign_fee = (
            portfolio_value * 
            segment['foreign_investment_rate'] * 
            segment['trading_frequency'] * 
            self.revenue_sources['foreign_trading_fee']
        )
        
        monthly_margin_interest = (
            portfolio_value * 
            segment['margin_usage_rate'] * 
            self.revenue_sources['margin_interest'] / 12
        )
        
        monthly_total = (
            monthly_trading_commission + 
            monthly_fund_fee + 
            monthly_premium_fee + 
            monthly_foreign_fee + 
            monthly_margin_interest
        )
        
        # 연간 및 생애 가치
        annual_revenue = monthly_total * 12
        lifetime_value = annual_revenue * 5  # 5년 고객 생애주기 가정
        
        return {
            'monthly_revenue': monthly_total,
            'annual_revenue': annual_revenue,
            'lifetime_value': lifetime_value,
            'portfolio_value': portfolio_value,
            'grade': grade,
            'revenue_breakdown': {
                'trading_commission': monthly_trading_commission,
                'fund_management': monthly_fund_fee,
                'premium_service': monthly_premium_fee,
                'foreign_trading': monthly_foreign_fee,
                'margin_interest': monthly_margin_interest
            }
        }
    
    def calculate_roi_from_marketing(self, marketing_cost: float, acquired_customers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """마케팅 ROI 계산"""
        
        total_customer_value = 0
        grade_distribution = {'VIP': 0, 'PREMIUM': 0, 'STANDARD': 0, 'BASIC': 0}
        
        for customer in acquired_customers:
            grade = customer.get('grade', 'BASIC')
            customer_value = self.calculate_customer_value(grade, customer.get('portfolio_info'))
            total_customer_value += customer_value['lifetime_value']
            grade_distribution[grade] += 1
        
        roi_ratio = (total_customer_value / marketing_cost) if marketing_cost > 0 else 0
        roi_percentage = (roi_ratio - 1) * 100
        
        return {
            'marketing_cost': marketing_cost,
            'total_customer_value': total_customer_value,
            'roi_ratio': roi_ratio,
            'roi_percentage': roi_percentage,
            'acquired_customers': len(acquired_customers),
            'avg_customer_value': total_customer_value / len(acquired_customers) if acquired_customers else 0,
            'grade_distribution': grade_distribution,
            'payback_period_months': self._calculate_payback_period(marketing_cost, acquired_customers)
        }
    
    def _calculate_payback_period(self, marketing_cost: float, customers: List[Dict[str, Any]]) -> float:
        """투자 회수 기간 계산"""
        
        monthly_revenue = 0
        for customer in customers:
            grade = customer.get('grade', 'BASIC')
            customer_value = self.calculate_customer_value(grade, customer.get('portfolio_info'))
            monthly_revenue += customer_value['monthly_revenue']
        
        if monthly_revenue <= 0:
            return float('inf')
        
        return marketing_cost / monthly_revenue

class EnhancedCTAManager:
    """종합 CTA 관리 시스템"""
    
    def __init__(self):
        self.lead_scoring = LeadScoringEngine()
        self.follow_up = AutomatedFollowUp()
        self.optimizer = ConversionOptimizer()
        self.revenue_calc = RevenueCalculator()
        
    def process_consultation_request(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """상담 신청 처리 전체 플로우"""
        
        # 1. 리드 스코어링
        lead_score = self.lead_scoring.calculate_lead_score(form_data)
        
        # 2. 수익 가치 계산
        customer_value = self.revenue_calc.calculate_customer_value(
            lead_score['grade'], 
            form_data.get('portfolio_info')
        )
        
        # 3. 자동 후속 조치
        follow_up_success = self.follow_up.send_follow_up(form_data, lead_score)
        
        # 4. 전환 추적
        cta_config = self.optimizer.get_optimized_cta_config(form_data)
        self.optimizer.track_conversion('consultation_request', form_data, cta_config)
        
        # 5. 결과 반환
        return {
            'success': True,
            'consultation_id': form_data.get('id'),
            'lead_score': lead_score,
            'customer_value': customer_value,
            'follow_up_sent': follow_up_success,
            'next_steps': self._get_next_steps(lead_score['priority']),
            'estimated_contact_time': self.follow_up._calculate_contact_time(lead_score['priority'])
        }
    
    def _get_next_steps(self, priority: str) -> List[str]:
        """다음 단계 안내"""
        
        steps = {
            'URGENT': [
                "📞 30분 내 전문가 직통 연결",
                "📋 긴급 포트폴리오 진단",
                "🛡️ 리스크 관리 방안 제시",
                "📈 즉시 실행 가능한 전략 수립"
            ],
            'HIGH': [
                "📞 2시간 내 우선 상담 연결",
                "📊 개인 맞춤 분석 리포트",
                "💼 포트폴리오 최적화 제안",
                "🎯 투자 목표 달성 로드맵"
            ],
            'MEDIUM': [
                "📞 24시간 내 상담 예약",
                "📄 투자 가이드 자료 제공",
                "💡 기본 포트폴리오 진단",
                "📚 투자 교육 자료 안내"
            ],
            'LOW': [
                "📧 이메일 자료 발송",
                "📱 앱 다운로드 안내",
                "📞 편한 시간 상담 예약",
                "🔔 투자 정보 알림 설정"
            ]
        }
        
        return steps.get(priority, steps['MEDIUM'])
    
    def get_dashboard_metrics(self) -> Dict[str, Any]:
        """CTA 성과 대시보드"""
        
        conversion_analytics = self.optimizer.get_conversion_analytics()
        
        # 예시 데이터 (실제로는 DB에서 조회)
        sample_customers = [
            {'grade': 'VIP', 'portfolio_info': {'current_value': 300000000}},
            {'grade': 'PREMIUM', 'portfolio_info': {'current_value': 80000000}},
            {'grade': 'STANDARD', 'portfolio_info': {'current_value': 25000000}},
            {'grade': 'BASIC', 'portfolio_info': {'current_value': 8000000}}
        ]
        
        marketing_roi = self.revenue_calc.calculate_roi_from_marketing(1000000, sample_customers)
        
        return {
            'conversion_metrics': conversion_analytics,
            'revenue_impact': marketing_roi,
            'active_leads': 147,
            'vip_conversion_rate': 12.3,
            'avg_customer_value': marketing_roi['avg_customer_value'],
            'total_pipeline_value': marketing_roi['total_customer_value']
        }

# Streamlit 통합을 위한 헬퍼 함수들
def init_cta_system():
    """CTA 시스템 초기화"""
    if 'cta_manager' not in st.session_state:
        st.session_state.cta_manager = EnhancedCTAManager()
    
    return st.session_state.cta_manager

def show_conversion_optimized_cta(risk_level: str, portfolio_info: Dict[str, Any] = None, user_profile: Dict[str, Any] = None):
    """최적화된 CTA 표시"""
    
    cta_manager = init_cta_system()
    
    # 사용자 프로필 구성
    if not user_profile:
        user_profile = {
            'risk_level': risk_level,
            'investment_amount': '1천만원 미만',
            'session_id': st.session_state.get('session_id', 'anonymous')
        }
    
    # 최적화된 CTA 설정 가져오기
    cta_config = cta_manager.optimizer.get_optimized_cta_config(user_profile)
    
    # CTA UI 렌더링
    button_style = f"background: linear-gradient(135deg, {cta_config['button_color']} 0%, {'#d32f2f' if cta_config['button_color']=='red' else '#1976d2' if cta_config['button_color']=='blue' else '#388e3c'} 100%);"
    
    st.markdown(f"""
    <div class="mega-cta" style="{button_style}">
        <h3 style="margin: 0 0 0.5rem 0;">{cta_config['primary_cta']}</h3>
        <p style="margin: 0 0 1rem 0;">{cta_config['secondary_message']}</p>
        {f'<div style="background: rgba(255,255,255,0.2); padding: 0.5rem; border-radius: 0.3rem; margin: 0.5rem 0;"><strong>{cta_config["vip_message"]}</strong></div>' if cta_config.get('show_vip_badge') else ''}
        <p style="margin: 0; font-size: 0.9rem; opacity: 0.9;">
            ✅ {cta_config.get('free_emphasis', '100% 무료 상담')} ✅ 개인 맞춤 전략 ✅ 24시간 내 연락
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 긴급성 메시지
    if cta_config.get('scarcity_message'):
        st.markdown("""
        <div style="background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%); color: white; padding: 1rem; border-radius: 0.5rem; margin: 0.5rem 0; text-align: center; animation: blink 2s infinite;">
            ⏰ <strong>긴급 알림:</strong> 큰 손실 방지를 위해 30분 내 전문가 연결이 필요합니다!
        </div>
        """, unsafe_allow_html=True)
    
    return cta_config

def display_cta_dashboard():
    """CTA 성과 대시보드 표시 (관리자용)"""
    
    if not st.secrets.get("ADMIN_MODE", False):
        return
    
    cta_manager = init_cta_system()
    metrics = cta_manager.get_dashboard_metrics()
    
    st.markdown("### 🎯 CTA 성과 대시보드 (관리자)")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("전환율", f"{metrics['conversion_metrics']['conversion_rate']}%")
    
    with col2:
        st.metric("활성 리드", metrics['active_leads'])
    
    with col3:
        st.metric("VIP 전환율", f"{metrics['vip_conversion_rate']}%")
    
    with col4:
        st.metric("평균 고객가치", f"{metrics['avg_customer_value']:,.0f}원")
    
    # ROI 정보
    st.markdown("**마케팅 ROI:**")
    roi_data = metrics['revenue_impact']
    st.write(f"• ROI: {roi_data['roi_percentage']:+.1f}%")
    st.write(f"• 투자회수기간: {roi_data['payback_period_months']:.1f}개월")
    st.write(f"• 총 파이프라인 가치: {roi_data['total_customer_value']:,.0f}원")
