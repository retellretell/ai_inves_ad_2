"""
integrated_cta_system.py - 통합 CTA 마케팅 시스템
미래에셋증권 고객 유치 및 수익 구조에 최적화된 완전체
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

class ProductRecommendationEngine:
    """상품 추천 시스템"""
    
    def __init__(self):
        self.products = {
            'conservative': {
                'name': '안전형 포트폴리오',
                'description': '원금 보전을 최우선으로 하는 안정적 투자',
                'products': ['정기예금', '국고채', '회사채', '안전형 펀드'],
                'expected_return': '연 3-5%',
                'risk_level': '낮음',
                'min_investment': 1000000,
                'target_customers': ['BASIC', 'STANDARD'],
                'commission_rate': 0.0001
            },
            'balanced': {
                'name': '균형형 포트폴리오',
                'description': '안정성과 수익성의 균형을 추구',
                'products': ['혼합형 펀드', 'ETF', '우량주', '리츠'],
                'expected_return': '연 5-8%',
                'risk_level': '중간',
                'min_investment': 5000000,
                'target_customers': ['STANDARD', 'PREMIUM'],
                'commission_rate': 0.00015
            },
            'aggressive': {
                'name': '성장형 포트폴리오',
                'description': '높은 수익을 목표로 하는 적극적 투자',
                'products': ['성장주', '테마주', '해외주식', '성장형 펀드'],
                'expected_return': '연 8-15%',
                'risk_level': '높음',
                'min_investment': 10000000,
                'target_customers': ['PREMIUM', 'VIP'],
                'commission_rate': 0.0002
            },
            'vip_exclusive': {
                'name': 'VIP 전용 프리미엄',
                'description': '초고액 고객을 위한 독점 투자 상품',
                'products': ['사모펀드', '헤지펀드', '구조화상품', '대체투자'],
                'expected_return': '연 10-20%',
                'risk_level': '매우 높음',
                'min_investment': 100000000,
                'target_customers': ['VIP'],
                'commission_rate': 0.0025
            }
        }
        
        self.special_offers = {
            'new_customer': {
                'name': '신규 고객 특별 혜택',
                'discount': 0.5,  # 50% 할인
                'period_days': 90,
                'description': '첫 3개월 수수료 50% 할인'
            },
            'high_volume': {
                'name': '대량 거래 우대',
                'discount': 0.3,  # 30% 할인
                'min_amount': 100000000,
                'description': '1억원 이상 거래 시 수수료 30% 할인'
            }
        }
    
    def get_personalized_recommendations(self, lead_data: Dict[str, Any], lead_score: Dict[str, Any]) -> Dict[str, Any]:
        """개인화된 상품 추천"""
        
        grade = lead_score['grade']
        risk_level = lead_data.get('risk_level', 'MEDIUM')
        portfolio_info = lead_data.get('portfolio_info', {})
        investment_amount = lead_data.get('investment_amount', '1천만원 미만')
        
        # 리스크 성향 기반 기본 추천
        if risk_level == 'HIGH' or '손실' in str(lead_data.get('additional_info', '')).lower():
            primary_recommendation = 'conservative'
        elif risk_level == 'LOW' and grade in ['PREMIUM', 'VIP']:
            primary_recommendation = 'aggressive'
        else:
            primary_recommendation = 'balanced'
        
        # VIP 고객에게는 전용 상품도 추천
        recommendations = [primary_recommendation]
        if grade == 'VIP':
            recommendations.append('vip_exclusive')
        
        # 투자 금액에 따른 필터링
        investment_numeric = self._parse_investment_amount(investment_amount)
        filtered_recommendations = []
        
        for rec_type in recommendations:
            product = self.products[rec_type]
            if investment_numeric >= product['min_investment']:
                filtered_recommendations.append(rec_type)
        
        # 추천 상품이 없는 경우 기본 상품 추천
        if not filtered_recommendations:
            filtered_recommendations = ['conservative']
        
        # 특별 혜택 계산
        applicable_offers = self._get_applicable_offers(lead_data, lead_score)
        
        return {
            'primary_recommendation': filtered_recommendations[0],
            'all_recommendations': filtered_recommendations,
            'products': {rec: self.products[rec] for rec in filtered_recommendations},
            'special_offers': applicable_offers,
            'estimated_returns': self._calculate_estimated_returns(filtered_recommendations, investment_numeric),
            'next_steps': self._get_product_next_steps(grade)
        }
    
    def _parse_investment_amount(self, amount_str: str) -> int:
        """투자 금액 문자열을 숫자로 변환"""
        if '5억원 이상' in amount_str:
            return 500000000
        elif '1억원' in amount_str:
            return 100000000
        elif '5천만원' in amount_str:
            return 50000000
        elif '1천만원' in amount_str and '미만' not in amount_str:
            return 10000000
        else:
            return 5000000  # 기본값
    
    def _get_applicable_offers(self, lead_data: Dict[str, Any], lead_score: Dict[str, Any]) -> List[Dict[str, Any]]:
        """적용 가능한 특별 혜택"""
        offers = []
        
        # 신규 고객 혜택
        if lead_data.get('source') == 'ai_investment_advisor':
            offers.append(self.special_offers['new_customer'])
        
        # 대량 거래 우대
        investment_amount = self._parse_investment_amount(lead_data.get('investment_amount', ''))
        if investment_amount >= self.special_offers['high_volume']['min_amount']:
            offers.append(self.special_offers['high_volume'])
        
        return offers
    
    def _calculate_estimated_returns(self, recommendations: List[str], investment_amount: int) -> Dict[str, Any]:
        """예상 수익률 계산"""
        results = {}
        
        for rec_type in recommendations:
            product = self.products[rec_type]
            
            # 수익률 범위에서 중간값 계산
            return_range = product['expected_return']
            if '3-5%' in return_range:
                avg_return = 0.04
            elif '5-8%' in return_range:
                avg_return = 0.065
            elif '8-15%' in return_range:
                avg_return = 0.115
            elif '10-20%' in return_range:
                avg_return = 0.15
            else:
                avg_return = 0.05
            
            estimated_annual_profit = investment_amount * avg_return
            estimated_monthly_profit = estimated_annual_profit / 12
            
            results[rec_type] = {
                'annual_profit': estimated_annual_profit,
                'monthly_profit': estimated_monthly_profit,
                'return_rate': avg_return,
                'commission_cost': investment_amount * product['commission_rate'] * 12  # 연간 거래 수수료
            }
        
        return results
    
    def _get_product_next_steps(self, grade: str) -> List[str]:
        """상품별 다음 단계"""
        if grade == 'VIP':
            return [
                "🏆 VIP 전담 PB와 1:1 상담",
                "📊 개인 맞춤 포트폴리오 설계",
                "💎 독점 투자 기회 안내",
                "🛡️ 프리미엄 리스크 관리 서비스"
            ]
        elif grade == 'PREMIUM':
            return [
                "📞 프리미엄 상담사 배정",
                "📈 고수익 상품 포트폴리오 제안",
                "🎯 목표 수익률 달성 전략",
                "📱 전용 트레이딩 플랫폼 제공"
            ]
        else:
            return [
                "📋 기본 포트폴리오 진단",
                "📚 투자 교육 프로그램 제공",
                "💡 단계별 투자 가이드",
                "🔔 시장 동향 알림 서비스"
            ]

class AutomatedFollowUp:
    """자동화된 후속 조치 (알림 시스템 통합)"""
    
    def __init__(self):
        self.email_templates = self._load_email_templates()
        self.sms_templates = self._load_sms_templates()
        self.notification_types = {
            'market_alert': '시장 급변 알림',
            'portfolio_alert': '포트폴리오 알림',
            'news_alert': '중요 뉴스 알림',
            'recommendation': '투자 추천',
            'consultation_reminder': '상담 일정 알림'
        }
        
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
            
            💎 추천 투자 상품:
            {recommended_products}
            
            📞 전문가가 곧 연락드리겠습니다!
            
            급한 문의사항이 있으시면:
            📞 고객센터: 1588-6666
            💬 카카오톡: '미래에셋증권' 검색
            
            감사합니다.
            미래에셋증권 디지털자산운용팀
            """,
            
            'product_recommendation': """
            {name}님께 맞춤 투자 상품을 제안드립니다!
            
            🎯 {name}님 맞춤 포트폴리오: {product_name}
            
            📊 상품 특징:
            - 예상 수익률: {expected_return}
            - 위험 수준: {risk_level}
            - 최소 투자금액: {min_investment:,}원
            
            💰 예상 수익 (연간):
            - 투자금액: {investment_amount:,}원
            - 예상 수익: {estimated_profit:,}원
            - 수수료: {commission_cost:,}원
            
            🎁 특별 혜택:
            {special_offers}
            
            📞 자세한 상담을 원하시면 언제든 연락주세요!
            전담 상담사: {assigned_consultant}
            
            미래에셋증권 상품팀
            """,
            
            'vip_special_offer': """
            {name}님, VIP 고객 특별 혜택 안내
            
            🏆 AI 분석 결과, VIP 등급 고객으로 분류되었습니다!
            
            🎁 VIP 전용 특별 혜택:
            ✅ 전용 PB 배정 (무료)
            ✅ 프리미엄 투자 정보 제공
            ✅ 수수료 할인 (최대 50%)
            ✅ 우선 IPO 참여 기회
            ✅ 해외투자 수수료 면제
            ✅ VIP 전용 투자 상품 액세스
            
            💎 VIP 전용 상품:
            {vip_products}
            
            📞 VIP 전용 상담: 1588-6666 (VIP 코드: {vip_code})
            
            이 혜택은 48시간 내 연락 시에만 적용됩니다.
            
            미래에셋증권 VIP팀
            """,
            
            'notification_setup': """
            {name}님, 투자 알림 서비스가 설정되었습니다!
            
            🔔 설정된 알림:
            {notification_list}
            
            📱 알림 발송 시간: {notification_time}
            
            💡 알림 예시:
            - "삼성전자 +3.2% 상승! 매도 타이밍 검토 필요"
            - "코스피 급락 -2.1%, 리밸런싱 기회"
            - "AI 추천: TSLA 매수 신호 감지"
            
            ⚙️ 알림 설정 변경: 앱에서 [설정] > [알림 관리]
            
            미래에셋증권 알림센터
            """
        }
    
    def _load_sms_templates(self) -> Dict[str, str]:
        """SMS 템플릿"""
        return {
            'urgent_consultation': "[미래에셋증권] {name}님, 긴급 투자 상담이 필요합니다. 전문가가 30분 내 연락드립니다. 문의: 1588-6666",
            'appointment_reminder': "[미래에셋증권] {name}님, 내일 {time} 투자 상담 예정입니다. 준비서류: {documents}. 변경 시 1588-6666",
            'market_alert': "[미래에셋증권] {name}님 보유 종목 급변동! {stock_name} {change}%. 전문가 분석 필요. 즉시 상담: 1588-6666",
            'product_alert': "[미래에셋증권] {name}님께 새로운 투자 기회! {product_name} 한정 모집. 자세히: 1588-6666",
            'profit_alert': "[미래에셋증권] 축하합니다! {name}님 포트폴리오 수익률 +{profit_rate}% 달성. 수익 확대 전략 상담: 1588-6666"
        }
    
    def send_follow_up(self, lead_data: Dict[str, Any], lead_score: Dict[str, Any], 
                      product_recommendations: Dict[str, Any] = None) -> bool:
        """통합 후속 조치 실행"""
        try:
            priority = lead_score['priority']
            grade = lead_score['grade']
            
            # 1. 이메일 발송
            if lead_data.get('email'):
                self._send_email(lead_data, lead_score, product_recommendations)
            
            # 2. SMS 발송 (고우선순위만)
            if priority in ['URGENT', 'HIGH'] and lead_data.get('phone'):
                self._send_sms(lead_data, lead_score)
            
            # 3. 알림 서비스 자동 등록 (동의한 경우)
            if lead_data.get('marketing_agreed'):
                self._setup_notification_service(lead_data, lead_score)
            
            # 4. CRM 시스템 연동
            self._update_crm_system(lead_data, lead_score, product_recommendations)
            
            # 5. 영업팀 알림
            if priority == 'URGENT':
                self._notify_sales_team(lead_data, lead_score)
            
            return True
            
        except Exception as e:
            logger.error(f"후속 조치 실행 실패: {e}")
            return False
    
    def _send_email(self, lead_data: Dict[str, Any], lead_score: Dict[str, Any], 
                   product_recommendations: Dict[str, Any] = None) -> bool:
        """향상된 이메일 발송"""
        try:
            grade = lead_score['grade']
            
            # 템플릿 선택
            if grade == 'VIP':
                template_key = 'vip_special_offer'
                vip_products = self._format_vip_products(product_recommendations)
                extra_vars = {'vip_products': vip_products, 'vip_code': f"VIP{lead_data.get('id', '')[:6]}"}
            elif product_recommendations:
                template_key = 'product_recommendation'
                extra_vars = self._format_product_email_vars(lead_data, product_recommendations)
            else:
                template_key = 'consultation_confirmation'
                extra_vars = {}
            
            template = self.email_templates[template_key]
            
            # 기본 템플릿 변수
            base_vars = {
                'name': lead_data.get('name', '고객'),
                'consultation_id': lead_data.get('id', '')[:8],
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'priority': lead_score['priority'],
                'expected_contact_time': self._calculate_contact_time(lead_score['priority']),
                'preparation_items': self._get_preparation_items(lead_data),
                'recommended_products': self._format_recommended_products(product_recommendations)
            }
            
            # 템플릿 변수 병합
            template_vars = {**base_vars, **extra_vars}
            email_content = template.format(**template_vars)
            
            # 실제 이메일 발송 로직
            # self._actual_send_email(lead_data['email'], email_content)
            
            logger.info(f"이메일 발송 완료: {lead_data.get('email')}")
            return True
            
        except Exception as e:
            logger.error(f"이메일 발송 실패: {e}")
            return False
    
    def _setup_notification_service(self, lead_data: Dict[str, Any], lead_score: Dict[str, Any]) -> bool:
        """알림 서비스 자동 설정"""
        try:
            # 고객 등급별 기본 알림 설정
            grade = lead_score['grade']
            
            if grade == 'VIP':
                default_notifications = ['market_alert', 'portfolio_alert', 'news_alert', 'recommendation']
            elif grade == 'PREMIUM':
                default_notifications = ['market_alert', 'portfolio_alert', 'recommendation']
            else:
                default_notifications = ['portfolio_alert', 'recommendation']
            
            notification_data = {
                'customer_id': lead_data.get('id'),
                'phone': lead_data.get('phone'),
                'email': lead_data.get('email'),
                'notifications': default_notifications,
                'time_preference': self._get_optimal_notification_time(grade),
                'frequency': 'real_time' if grade == 'VIP' else 'daily',
                'created_at': datetime.now().isoformat(),
                'auto_setup': True
            }
            
            # 알림 설정 저장
            self._save_notification_data(notification_data)
            
            # 설정 완료 이메일 발송
            if lead_data.get('email'):
                self._send_notification_setup_email(lead_data, notification_data)
            
            return True
            
        except Exception as e:
            logger.error(f"알림 서비스 설정 실패: {e}")
            return False
    
    def _format_product_email_vars(self, lead_data: Dict[str, Any], 
                                  product_recommendations: Dict[str, Any]) -> Dict[str, Any]:
        """상품 추천 이메일 변수 포맷팅"""
        if not product_recommendations:
            return {}
        
        primary_rec = product_recommendations['primary_recommendation']
        product = product_recommendations['products'][primary_rec]
        estimated_returns = product_recommendations['estimated_returns'][primary_rec]
        
        investment_amount = self._parse_investment_amount(lead_data.get('investment_amount', '1천만원 미만'))
        
        special_offers_text = '\n'.join([
            f"• {offer['name']}: {offer['description']}" 
            for offer in product_recommendations.get('special_offers', [])
        ]) or '현재 적용 가능한 특별 혜택이 없습니다.'
        
        return {
            'product_name': product['name'],
            'expected_return': product['expected_return'],
            'risk_level': product['risk_level'],
            'min_investment': product['min_investment'],
            'investment_amount': investment_amount,
            'estimated_profit': int(estimated_returns['annual_profit']),
            'commission_cost': int(estimated_returns['commission_cost']),
            'special_offers': special_offers_text,
            'assigned_consultant': self._assign_consultant_name(lead_data.get('grade', 'BASIC'))
        }
    
    def _parse_investment_amount(self, amount_str: str) -> int:
        """투자 금액 파싱"""
        if '5억원 이상' in amount_str:
            return 500000000
        elif '1억원' in amount_str:
            return 100000000
        elif '5천만원' in amount_str:
            return 50000000
        elif '1천만원' in amount_str and '미만' not in amount_str:
            return 10000000
        else:
            return 5000000
    
    def _assign_consultant_name(self, grade: str) -> str:
        """등급별 상담사 배정"""
        consultants = {
            'VIP': '김영수 VIP 전담 PB',
            'PREMIUM': '박지은 프리미엄 상담사',
            'STANDARD': '이민호 투자 상담사',
            'BASIC': '최유리 고객 상담사'
        }
        return consultants.get(grade, '고객 상담팀')
    
    def _get_optimal_notification_time(self, grade: str) -> str:
        """최적 알림 시간 결정"""
        if grade == 'VIP':
            return '실시간'
        elif grade == 'PREMIUM':
            return '장 시작 전 (08:30) + 장 마감 후 (15:30)'
        else:
            return '저녁 (19:00)'
    
    def _save_notification_data(self, data: Dict[str, Any]) -> bool:
        """알림 데이터 저장"""
        try:
            filename = 'notification_subscriptions.json'
            subscriptions = []
            
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    subscriptions = json.load(f)
            except FileNotFoundError:
                pass
            
            subscriptions.append(data)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(subscriptions, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            logger.error(f"알림 데이터 저장 실패: {e}")
            return False
    
    def _send_notification_setup_email(self, lead_data: Dict[str, Any], 
                                     notification_data: Dict[str, Any]) -> bool:
        """알림 설정 완료 이메일"""
        try:
            template = self.email_templates['notification_setup']
            
            notification_list = '\n'.join([
                f"✅ {self.notification_types[notif]}" 
                for notif in notification_data['notifications']
            ])
            
            email_content = template.format(
                name=lead_data.get('name', '고객'),
                notification_list=notification_list,
                notification_time=notification_data['time_preference']
            )
            
            # 실제 이메일 발송
            # self._actual_send_email(lead_data['email'], email_content)
            
            return True
            
        except Exception as e:
            logger.error(f"알림 설정 이메일 발송 실패: {e}")
            return False
    
    def _format_vip_products(self, product_recommendations: Dict[str, Any]) -> str:
        """VIP 상품 포맷팅"""
        if not product_recommendations or 'vip_exclusive' not in product_recommendations.get('products', {}):
            return "프리미엄 포트폴리오, 사모펀드, 헤지펀드, 구조화상품"
        
        vip_product = product_recommendations['products']['vip_exclusive']
        return f"{vip_product['name']}: {', '.join(vip_product['products'])}"
    
    def _format_recommended_products(self, product_recommendations: Dict[str, Any]) -> str:
        """추천 상품 포맷팅"""
        if not product_recommendations:
            return "개인 맞춤 포트폴리오를 상담 시 제안해드립니다."
        
        primary_rec = product_recommendations['primary_recommendation']
        product = product_recommendations['products'][primary_rec]
        
        return f"• {product['name']}\n• 예상 수익률: {product['expected_return']}\n• 추천 상품: {', '.join(product['products'][:3])}"
    
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
        
        consultation_topics = lead_data.get('consultation_topic', [])
        if 'tax' in str(consultation_topics).lower():
            items.append("• 지난해 투자 수익 내역")
        
        if 'pension' in str(consultation_topics).lower():
            items.append("• 현재 연금 가입 현황")
        
        items.extend([
            "• 투자 목표 금액 및 기간",
            "• 월 투자 가능 금액",
            "• 신분증 (비대면 상담 시)"
        ])
        
        return '\n'.join(items)
    
    def _send_sms(self, lead_data: Dict[str, Any], lead_score: Dict[str, Any]) -> bool:
        """SMS 발송"""
        try:
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
    
    def _update_crm_system(self, lead_data: Dict[str, Any], lead_score: Dict[str, Any], 
                          product_recommendations: Dict[str, Any] = None) -> bool:
        """CRM 시스템 업데이트"""
        try:
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
                'assigned_rep': self._assign_representative(lead_score['grade']),
                'recommended_products': product_recommendations.get('primary_recommendation') if product_recommendations else None,
                'notification_preferences': self._get_notification_preferences(lead_data, lead_score)
            }
            
            # CRM API 호출
            # response = requests.post('https://crm.miraeasset.com/api/leads', json=crm_data)
            
            logger.info(f"CRM 업데이트 완료: {lead_data.get('name')}")
            return True
            
        except Exception as e:
            logger.error(f"CRM 업데이트 실패: {e}")
            return False
    
    def _get_notification_preferences(self, lead_data: Dict[str, Any], lead_score: Dict[str, Any]) -> Dict[str, Any]:
        """알림 선호도 설정"""
        grade = lead_score['grade']
        
        return {
            'email_enabled': bool(lead_data.get('email')),
            'sms_enabled': grade in ['VIP', 'PREMIUM'] and bool(lead_data.get('phone')),
            'frequency': 'real_time' if grade == 'VIP' else 'daily',
            'marketing_agreed': lead_data.get('marketing_agreed', False)
        }
    
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

class MarketingContent:
    """마케팅 콘텐츠 관리 (이벤트, 프로모션, 사회적 증명)"""
    
    def __init__(self):
        self.current_events = [
            {
                'id': 'ai_experience_2025',
                'title': '🎯 AI 투자 체험 이벤트',
                'description': 'AI 투자 어드바이저 첫 이용 시 수수료 50% 할인',
                'period': '2025.07.01 ~ 2025.07.31',
                'benefit': '거래 수수료 50% 할인',
                'condition': '신규 고객 대상',
                'target_grades': ['BASIC', 'STANDARD', 'PREMIUM'],
                'cta': '이벤트 참여하기',
                'max_participants': 1000,
                'current_participants': 342
            },
            {
                'id': 'mobile_trading_2025',
                'title': '📱 모바일 트레이딩 이벤트',
                'description': 'mPOP 앱으로 거래 시 추가 혜택',
                'period': '2025.07.01 ~ 2025.08.31',
                'benefit': 'V골드 적립 2배 + 수수료 20% 할인',
                'condition': '모바일 앱 거래 시',
                'target_grades': ['STANDARD', 'PREMIUM'],
                'cta': '앱 다운로드',
                'max_participants': 5000,
                'current_participants': 1243
            },
            {
                'id': 'portfolio_diagnosis_2025',
                'title': '🏆 포트폴리오 진단 이벤트',
                'description': '무료 포트폴리오 진단 및 맞춤 전략 제공',
                'period': '2025.07.01 ~ 2025.12.31',
                'benefit': '전문가 진단 무료 (30만원 상당)',
                'condition': '상담 신청 고객',
                'target_grades': ['BASIC', 'STANDARD', 'PREMIUM', 'VIP'],
                'cta': '무료 진단 신청',
                'max_participants': 10000,
                'current_participants': 2847
            },
            {
                'id': 'vip_exclusive_2025',
                'title': '💎 VIP 전용 프리미엄 이벤트',
                'description': 'VIP 고객만을 위한 독점 투자 기회',
                'period': '2025.07.01 ~ 2025.09.30',
                'benefit': '사모펀드 우선 참여 + 수수료 면제',
                'condition': 'VIP 등급 고객만',
                'target_grades': ['VIP'],
                'cta': 'VIP 전용 상담',
                'max_participants': 100,
                'current_participants': 23
            }
        ]
        
        self.testimonials = [
            {
                'id': 'test_001',
                'user': '김○○님 (30대, 직장인)',
                'rating': 5,
                'comment': 'AI 분석이 정말 정확해요. 포트폴리오 수익률이 20% 향상되었습니다!',
                'profit': '+2,340만원',
                'period': '6개월',
                'grade': 'PREMIUM',
                'verified': True,
                'date': '2025-06-15'
            },
            {
                'id': 'test_002',
                'user': '박○○님 (40대, 자영업)',
                'rating': 5,
                'comment': '복잡한 시장 상황을 쉽게 설명해주고, 실행 방안까지 구체적이에요.',
                'profit': '+890만원',
                'period': '3개월',
                'grade': 'STANDARD',
                'verified': True,
                'date': '2025-06-20'
            },
            {
                'id': 'test_003',
                'user': '이○○님 (50대, 주부)',
                'rating': 4,
                'comment': '투자 초보도 이해하기 쉽고, 리스크 관리에 큰 도움이 됩니다.',
                'profit': '+450만원',
                'period': '4개월',
                'grade': 'BASIC',
                'verified': True,
                'date': '2025-06-10'
            },
            {
                'id': 'test_004',
                'user': '최○○님 (45대, 대기업 임원)',
                'rating': 5,
                'comment': 'VIP 서비스 정말 만족합니다. 전담 PB의 전문성이 뛰어나네요.',
                'profit': '+5,670만원',
                'period': '8개월',
                'grade': 'VIP',
                'verified': True,
                'date': '2025-05-28'
            }
        ]
        
        self.usage_stats = {
            'total_users': 15420,
            'total_analyses': 127854,
            'average_satisfaction': 4.7,
            'profit_users_ratio': 73.2,
            'average_profit_rate': 18.5,
            'retention_rate': 89.3,
            'vip_conversion_rate': 12.8,
            'last_updated': datetime.now().isoformat()
        }
        
        self.social_proof_data = {
            'recent_signups': 127,  # 최근 24시간
            'active_consultations': 43,  # 현재 진행 중
            'success_stories_this_month': 234,
            'total_profit_generated': 12847000000  # 전체 고객 누적 수익
        }
    
    def get_personalized_events(self, grade: str) -> List[Dict[str, Any]]:
        """개인화된 이벤트 목록"""
        applicable_events = []
        
        for event in self.current_events:
            if grade in event['target_grades']:
                # 참여율 계산
                participation_rate = (event['current_participants'] / event['max_participants']) * 100
                event_copy = event.copy()
                event_copy['participation_rate'] = participation_rate
                event_copy['urgency'] = 'high' if participation_rate > 80 else 'medium' if participation_rate > 50 else 'low'
                applicable_events.append(event_copy)
        
        # 긴급도 순으로 정렬
        return sorted(applicable_events, key=lambda x: x['participation_rate'], reverse=True)
    
    def get_relevant_testimonials(self, grade: str, limit: int = 3) -> List[Dict[str, Any]]:
        """관련성 높은 후기 선별"""
        # 같은 등급 우선, 최신순
        same_grade = [t for t in self.testimonials if t['grade'] == grade]
        other_grade = [t for t in self.testimonials if t['grade'] != grade]
        
        relevant = same_grade + other_grade
        return relevant[:limit]
    
    def get_dynamic_social_proof(self) -> Dict[str, Any]:
        """실시간 사회적 증명 데이터"""
        # 실시간 업데이트를 시뮬레이션
        import random
        
        # 약간의 랜덤 변동 추가 (실제로는 실시간 데이터)
        base_stats = self.usage_stats.copy()
        
        # 최근 활동 시뮬레이션
        recent_activity = {
            'new_signups_today': random.randint(45, 85),
            'consultations_in_progress': random.randint(35, 55),
            'avg_response_time_minutes': random.randint(12, 28),
            'success_rate_today': random.uniform(91.5, 96.8)
        }
        
        return {
            **base_stats,
            **recent_activity,
            **self.social_proof_data
        }
    
    def track_event_participation(self, event_id: str, user_data: Dict[str, Any]) -> bool:
        """이벤트 참여 추적"""
        try:
            participation_data = {
                'event_id': event_id,
                'user_id': user_data.get('id'),
                'user_grade': user_data.get('grade'),
                'timestamp': datetime.now().isoformat(),
                'source': 'ai_advisor_cta'
            }
            
            # 이벤트 참여 데이터 저장
            filename = 'event_participations.json'
            participations = []
            
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    participations = json.load(f)
            except FileNotFoundError:
                pass
            
            participations.append(participation_data)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(participations, f, ensure_ascii=False, indent=2)
            
            # 참여자 수 업데이트
            for event in self.current_events:
                if event['id'] == event_id:
                    event['current_participants'] += 1
                    break
            
            return True
            
        except Exception as e:
            logger.error(f"이벤트 참여 추적 실패: {e}")
            return False

class ConversionOptimizer:
    """전환율 최적화"""
    
    def __init__(self):
        self.ab_tests = {
            'cta_button_color': {'red': 0.23, 'blue': 0.19, 'green': 0.21, 'orange': 0.25},
            'urgency_message': {'high': 0.31, 'medium': 0.24, 'low': 0.18},
            'social_proof': {'with': 0.28, 'without': 0.20},
            'price_emphasis': {'free_highlighted': 0.26, 'benefit_focused': 0.22, 'none': 0.18},
            'testimonial_position': {'top': 0.29, 'middle': 0.24, 'bottom': 0.19}
        }
        
        self.conversion_tracking = []
        self.user_segments = {
            'risk_averse': {'colors': ['blue', 'green'], 'urgency': 'low', 'emphasis': 'benefit_focused'},
            'risk_neutral': {'colors': ['blue', 'orange'], 'urgency': 'medium', 'emphasis': 'free_highlighted'},
            'risk_seeking': {'colors': ['red', 'orange'], 'urgency': 'high', 'emphasis': 'benefit_focused'}
        }
    
    def get_optimized_cta_config(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """사용자별 최적화된 CTA 설정"""
        
        risk_level = user_profile.get('risk_level', 'MEDIUM')
        investment_amount = user_profile.get('investment_amount', '1천만원 미만')
        grade = user_profile.get('grade', 'BASIC')
        portfolio_info = user_profile.get('portfolio_info', {})
        
        # 기본 설정
        config = {
            'button_color': 'blue',
            'urgency_level': 'medium',
            'show_social_proof': True,
            'price_emphasis': 'free_highlighted',
            'scarcity_message': False,
            'testimonial_position': 'top',
            'animation_style': 'subtle'
        }
        
        # 리스크 성향별 최적화
        if risk_level == 'HIGH':
            segment_config = self.user_segments['risk_averse']
            config.update({
                'button_color': segment_config['colors'][0],
                'urgency_level': 'high',
                'scarcity_message': True,
                'primary_cta': '🆘 긴급 전문가 상담 (완전무료)',
                'secondary_message': '큰 손실 방지를 위해 즉시 상담받으세요!',
                'highlight_safety': True
            })
        elif risk_level == 'LOW':
            segment_config = self.user_segments['risk_seeking']
            config.update({
                'button_color': segment_config['colors'][1],
                'urgency_level': 'high',
                'primary_cta': '🚀 수익 극대화 전략 상담',
                'secondary_message': '더 높은 수익 기회를 놓치지 마세요!',
                'highlight_opportunity': True
            })
        else:  # MEDIUM
            segment_config = self.user_segments['risk_neutral']
            config.update({
                'button_color': segment_config['colors'][0],
                'urgency_level': 'medium',
                'primary_cta': '📞 맞춤 투자 상담 신청',
                'secondary_message': '더 나은 투자 성과를 위한 전문가 조언',
                'highlight_balance': True
            })
        
        # 투자 금액별 최적화
        if '1억원' in investment_amount or '5억원' in investment_amount:
            config.update({
                'show_vip_badge': True,
                'vip_message': '🏆 VIP 고객 전용 서비스',
                'price_emphasis': 'benefit_focused',  # 고액 고객은 무료 강조 안함
                'premium_styling': True
            })
        else:
            config.update({
                'show_vip_badge': False,
                'price_emphasis': 'free_highlighted',
                'free_emphasis': '💯 완전 무료'
            })
        
        # 등급별 추가 최적화
        if grade == 'VIP':
            config.update({
                'exclusive_message': '💎 VIP 전용 프리미엄 서비스',
                'urgency_level': 'high',
                'show_exclusive_badge': True
            })
        
        # 포트폴리오 상태별 최적화
        if portfolio_info:
            profit_rate = portfolio_info.get('profit_rate', 0)
            if profit_rate < -10:
                config.update({
                    'crisis_mode': True,
                    'primary_cta': '🚨 손실 방지 긴급 상담',
                    'button_color': 'red',
                    'urgency_level': 'high'
                })
            elif profit_rate > 20:
                config.update({
                    'success_mode': True,
                    'primary_cta': '📈 수익 확대 전략 상담',
                    'highlight_success': True
                })
        
        return config
    
    def get_personalized_messaging(self, user_profile: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """개인화된 메시징"""
        
        messages = {
            'urgency_messages': {
                'high': [
                    "⏰ 지금 바로 행동하세요!",
                    "🔥 한정된 기회입니다!",
                    "⚡ 즉시 전문가와 연결됩니다!"
                ],
                'medium': [
                    "📞 전문가가 기다리고 있습니다",
                    "💡 더 나은 투자 성과를 위해",
                    "🎯 맞춤 전략을 제안해드립니다"
                ],
                'low': [
                    "📊 전문가 조언을 받아보세요",
                    "💼 투자 전략을 개선해보세요",
                    "📈 안정적인 수익을 추구하세요"
                ]
            },
            'social_proof_messages': [
                f"✅ 지난 24시간 동안 {127}명이 상담 신청",
                f"⭐ 만족도 {4.7}/5.0 (15,420명 평가)",
                f"💰 평균 수익률 개선 {18.5}%",
                f"🏆 VIP 전환율 {12.8}%"
            ],
            'benefit_messages': {
                'BASIC': [
                    "✅ 투자 기초부터 차근차근",
                    "✅ 초보자도 이해하기 쉬운 설명",
                    "✅ 리스크 관리 노하우 전수"
                ],
                'STANDARD': [
                    "✅ 포트폴리오 최적화 전략",
                    "✅ 세금 절약 투자 방법",
                    "✅ 중급자를 위한 실전 노하우"
                ],
                'PREMIUM': [
                    "✅ 고수익 투자 기회 제공",
                    "✅ 전문가급 포트폴리오 관리",
                    "✅ 프리미엄 투자 정보 액세스"
                ],
                'VIP': [
                    "✅ VIP 전담 PB 서비스",
                    "✅ 독점 투자 상품 우선 제공",
                    "✅ 24시간 프리미엄 지원"
                ]
            }
        }
        
        grade = user_profile.get('grade', 'BASIC')
        urgency = config.get('urgency_level', 'medium')
        
        return {
            'urgency_message': messages['urgency_messages'][urgency][0],
            'social_proof': messages['social_proof_messages'][:2],
            'benefits': messages['benefit_messages'][grade],
            'call_to_action': config.get('primary_cta', '📞 전문가 상담 신청')
        }
    
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
            },
            'page_context': user_data.get('page_context', 'unknown')
        }
        
        self.conversion_tracking.append(conversion_event)
        self._save_conversion_data(conversion_event)
        
        # A/B 테스트 결과 업데이트
        self._update_ab_test_results(cta_config, event_type == 'consultation_request')
    
    def _update_ab_test_results(self, cta_config: Dict[str, Any], converted: bool) -> None:
        """A/B 테스트 결과 업데이트"""
        try:
            # 실제로는 더 정교한 통계 분석 필요
            button_color = cta_config.get('button_color', 'blue')
            urgency = cta_config.get('urgency_level', 'medium')
            
            if converted:
                # 성공적 전환 시 해당 설정의 성과 개선
                if button_color in self.ab_tests['cta_button_color']:
                    self.ab_tests['cta_button_color'][button_color] += 0.001
                
                if urgency in self.ab_tests['urgency_message']:
                    self.ab_tests['urgency_message'][urgency] += 0.001
            
        except Exception as e:
            logger.error(f"A/B 테스트 결과 업데이트 실패: {e}")
    
    def _save_conversion_data(self, event: Dict[str, Any]) -> None:
        """전환 데이터 저장"""
        try:
            filename = f"conversions_{datetime.now().strftime('%Y%m')}.json"
            
            conversions = []
            
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    conversions = json.load(f)
            except FileNotFoundError:
                pass
            
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
        event_participations = len([e for e in self.conversion_tracking if e['event_type'] == 'event_participation'])
        
        # 전환율 계산
        conversion_rate = (consultation_requests / total_events * 100) if total_events > 0 else 0
        
        # 등급별 전환율
        grade_conversions = {}
        for event in self.conversion_tracking:
            if event['event_type'] == 'consultation_request':
                grade = event['user_profile'].get('grade', 'UNKNOWN')
                if grade not in grade_conversions:
                    grade_conversions[grade] = 0
                grade_conversions[grade] += 1
        
        return {
            'total_events': total_events,
            'consultation_requests': consultation_requests,
            'document_downloads': document_downloads,
            'event_participations': event_participations,
            'conversion_rate': round(conversion_rate, 2),
            'grade_conversion_distribution': grade_conversions,
            'top_performing_cta': self._get_top_performing_cta(),
            'best_converting_time': self._get_best_converting_time(),
            'ab_test_results': self._get_ab_test_summary()
        }
    
    def _get_top_performing_cta(self) -> Dict[str, Any]:
        """최고 성과 CTA 분석"""
        cta_performance = {}
        
        for event in self.conversion_tracking:
            if event['event_type'] == 'consultation_request':
                button_color = event['cta_config'].get('button_color', 'unknown')
                urgency = event['cta_config'].get('urgency_level', 'unknown')
                
                key = f"{button_color}_{urgency}"
                if key not in cta_performance:
                    cta_performance[key] = 0
                cta_performance[key] += 1
        
        if cta_performance:
            best_cta = max(cta_performance, key=cta_performance.get)
            return {
                'config': best_cta,
                'conversions': cta_performance[best_cta],
                'performance_details': cta_performance
            }
        
        return {'config': 'orange_high', 'conversions': 0, 'performance_details': {}}
    
    def _get_best_converting_time(self) -> Dict[str, Any]:
        """최고 전환 시간대 분석"""
        time_conversions = {}
        
        for event in self.conversion_tracking:
            if event['event_type'] == 'consultation_request':
                timestamp = datetime.fromisoformat(event['timestamp'].replace('Z', '+00:00'))
                hour = timestamp.hour
                
                if hour not in time_conversions:
                    time_conversions[hour] = 0
                time_conversions[hour] += 1
        
        if time_conversions:
            best_hour = max(time_conversions, key=time_conversions.get)
            return {
                'best_hour': best_hour,
                'conversions': time_conversions[best_hour],
                'hourly_distribution': time_conversions
            }
        
        return {'best_hour': 14, 'conversions': 0, 'hourly_distribution': {}}
    
    def _get_ab_test_summary(self) -> Dict[str, Any]:
        """A/B 테스트 요약"""
        return {
            'button_colors': self.ab_tests['cta_button_color'],
            'urgency_levels': self.ab_tests['urgency_message'],
            'social_proof_impact': self.ab_tests['social_proof'],
            'recommendations': self._get_optimization_recommendations()
        }
    
    def _get_optimization_recommendations(self) -> List[str]:
        """최적화 권장사항"""
        recommendations = []
        
        # 최고 성과 버튼 색상
        best_color = max(self.ab_tests['cta_button_color'], key=self.ab_tests['cta_button_color'].get)
        recommendations.append(f"버튼 색상은 '{best_color}'가 가장 효과적입니다")
        
        # 최고 성과 긴급도
        best_urgency = max(self.ab_tests['urgency_message'], key=self.ab_tests['urgency_message'].get)
        recommendations.append(f"긴급도 메시지는 '{best_urgency}' 레벨이 최적입니다")
        
        # 사회적 증명 효과
        if self.ab_tests['social_proof']['with'] > self.ab_tests['social_proof']['without']:
            recommendations.append("사회적 증명 요소를 반드시 포함하세요")
        
        return recommendations

class RevenueCalculator:
    """수익 구조 계산기"""
    
    def __init__(self):
        # 미래에셋증권 수익 구조 (실제 데이터 기반)
        self.revenue_sources = {
            'trading_commission': 0.00015,  # 0.015% 수수료
            'fund_management_fee': 0.015,   # 1.5% 연간
            'premium_service_fee': 50000,   # 월 5만원
            'foreign_trading_fee': 0.0025,  # 0.25% 해외주식
            'margin_interest': 0.06,        # 6% 연간 (신용거래)
            'advisory_fee': 0.005,          # 0.5% 연간 (투자자문)
            'structured_product_fee': 0.01  # 1% (구조화상품)
        }
        
        self.customer_segments = {
            'VIP': {
                'avg_portfolio': 500000000,     # 5억
                'trading_frequency': 20,        # 월 20회
                'premium_service_rate': 0.8,    # 80%가 프리미엄 서비스
                'foreign_investment_rate': 0.6, # 60%가 해외투자
                'margin_usage_rate': 0.3,       # 30%가 신용거래
                'advisory_usage_rate': 0.7,     # 70%가 투자자문
                'structured_product_rate': 0.4  # 40%가 구조화상품
            },
            'PREMIUM': {
                'avg_portfolio': 100000000,     # 1억
                'trading_frequency': 15,
                'premium_service_rate': 0.5,
                'foreign_investment_rate': 0.4,
                'margin_usage_rate': 0.2,
                'advisory_usage_rate': 0.4,
                'structured_product_rate': 0.2
            },
            'STANDARD': {
                'avg_portfolio': 30000000,      # 3천만원
                'trading_frequency': 10,
                'premium_service_rate': 0.2,
                'foreign_investment_rate': 0.2,
                'margin_usage_rate': 0.1,
                'advisory_usage_rate': 0.1,
                'structured_product_rate': 0.05
            },
            'BASIC': {
                'avg_portfolio': 10000000,      # 1천만원
                'trading_frequency': 5,
                'premium_service_rate': 0.05,
                'foreign_investment_rate': 0.1,
                'margin_usage_rate': 0.05,
                'advisory_usage_rate': 0.02,
                'structured_product_rate': 0.01
            }
        }
        
        # 마케팅 채널별 비용 및 전환율
        self.marketing_channels = {
            'ai_advisor_cta': {
                'cost_per_lead': 15000,
                'conversion_rate': 0.12,
                'cost_per_acquisition': 125000
            },
            'organic_search': {
                'cost_per_lead': 8000,
                'conversion_rate': 0.08,
                'cost_per_acquisition': 100000
            },
            'paid_advertising': {
                'cost_per_lead': 25000,
                'conversion_rate': 0.15,
                'cost_per_acquisition': 166667
            },
            'referral': {
                'cost_per_lead': 30000,
                'conversion_rate': 0.25,
                'cost_per_acquisition': 120000
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
        
        monthly_advisory_fee = (
            portfolio_value * 
            segment['advisory_usage_rate'] * 
            self.revenue_sources['advisory_fee'] / 12
        )
        
        monthly_structured_fee = (
            portfolio_value * 
            segment['structured_product_rate'] * 
            self.revenue_sources['structured_product_fee'] / 12
        )
        
        monthly_total = (
            monthly_trading_commission + 
            monthly_fund_fee + 
            monthly_premium_fee + 
            monthly_foreign_fee + 
            monthly_margin_interest + 
            monthly_advisory_fee + 
            monthly_structured_fee
        )
        
        # 연간 및 생애 가치
        annual_revenue = monthly_total * 12
        
        # 등급별 고객 생애주기 차별화
        lifecycle_years = {
            'VIP': 8,      # VIP는 장기 고객
            'PREMIUM': 6,
            'STANDARD': 4,
            'BASIC': 3
        }
        
        lifetime_value = annual_revenue * lifecycle_years.get(grade, 3)
        
        return {
            'monthly_revenue': monthly_total,
            'annual_revenue': annual_revenue,
            'lifetime_value': lifetime_value,
            'portfolio_value': portfolio_value,
            'grade': grade,
            'lifecycle_years': lifecycle_years.get(grade, 3),
            'revenue_breakdown': {
                'trading_commission': monthly_trading_commission,
                'fund_management': monthly_fund_fee,
                'premium_service': monthly_premium_fee,
                'foreign_trading': monthly_foreign_fee,
                'margin_interest': monthly_margin_interest,
                'advisory_fee': monthly_advisory_fee,
                'structured_product': monthly_structured_fee
            },
            'profit_margin': self._calculate_profit_margin(monthly_total, grade)
        }
    
    def _calculate_profit_margin(self, monthly_revenue: float, grade: str) -> Dict[str, Any]:
        """수익률 계산"""
        # 등급별 서비스 비용
        service_costs = {
            'VIP': monthly_revenue * 0.4,      # 40% (고비용 서비스)
            'PREMIUM': monthly_revenue * 0.35,  # 35%
            'STANDARD': monthly_revenue * 0.25, # 25%
            'BASIC': monthly_revenue * 0.20     # 20%
        }
        
        cost = service_costs.get(grade, monthly_revenue * 0.25)
        profit = monthly_revenue - cost
        margin_rate = (profit / monthly_revenue * 100) if monthly_revenue > 0 else 0
        
        return {
            'gross_revenue': monthly_revenue,
            'service_cost': cost,
            'net_profit': profit,
            'margin_rate': margin_rate
        }
    
    def calculate_marketing_roi(self, marketing_cost: float, acquired_customers: List[Dict[str, Any]], 
                              channel: str = 'ai_advisor_cta') -> Dict[str, Any]:
        """마케팅 ROI 계산"""
        
        total_customer_value = 0
        total_annual_revenue = 0
        grade_distribution = {'VIP': 0, 'PREMIUM': 0, 'STANDARD': 0, 'BASIC': 0}
        
        for customer in acquired_customers:
            grade = customer.get('grade', 'BASIC')
            customer_value = self.calculate_customer_value(grade, customer.get('portfolio_info'))
            total_customer_value += customer_value['lifetime_value']
            total_annual_revenue += customer_value['annual_revenue']
            grade_distribution[grade] += 1
        
        # ROI 계산
        roi_ratio = (total_customer_value / marketing_cost) if marketing_cost > 0 else 0
        roi_percentage = (roi_ratio - 1) * 100
        
        # 채널 효율성
        channel_info = self.marketing_channels.get(channel, self.marketing_channels['ai_advisor_cta'])
        actual_conversion_rate = (len(acquired_customers) / (marketing_cost / channel_info['cost_per_lead'])) if marketing_cost > 0 else 0
        
        # 투자 회수 기간
        payback_months = self._calculate_payback_period(marketing_cost, acquired_customers)
        
        return {
            'marketing_cost': marketing_cost,
            'total_customer_ltv': total_customer_value,
            'total_annual_revenue': total_annual_revenue,
            'roi_ratio': roi_ratio,
            'roi_percentage': roi_percentage,
            'acquired_customers': len(acquired_customers),
            'avg_customer_ltv': total_customer_value / len(acquired_customers) if acquired_customers else 0,
            'grade_distribution': grade_distribution,
            'payback_period_months': payback_months,
            'channel_performance': {
                'channel': channel,
                'expected_conversion_rate': channel_info['conversion_rate'],
                'actual_conversion_rate': actual_conversion_rate,
                'efficiency_ratio': actual_conversion_rate / channel_info['conversion_rate'] if channel_info['conversion_rate'] > 0 else 0
            },
            'profitability_analysis': self._analyze_profitability(marketing_cost, total_customer_value, total_annual_revenue)
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
    
    def _analyze_profitability(self, marketing_cost: float, total_ltv: float, 
                             annual_revenue: float) -> Dict[str, Any]:
        """수익성 분석"""
        
        # 수익성 지표
        if marketing_cost > 0:
            ltv_to_cac_ratio = total_ltv / marketing_cost
            break_even_months = marketing_cost / (annual_revenue / 12) if annual_revenue > 0 else float('inf')
        else:
            ltv_to_cac_ratio = float('inf')
            break_even_months = 0
        
        # 수익성 등급
        if ltv_to_cac_ratio >= 5:
            profitability_grade = 'EXCELLENT'
        elif ltv_to_cac_ratio >= 3:
            profitability_grade = 'GOOD'
        elif ltv_to_cac_ratio >= 2:
            profitability_grade = 'ACCEPTABLE'
        else:
            profitability_grade = 'POOR'
        
        return {
            'ltv_to_cac_ratio': ltv_to_cac_ratio,
            'break_even_months': break_even_months,
            'profitability_grade': profitability_grade,
            'recommendation': self._get_profitability_recommendation(profitability_grade, ltv_to_cac_ratio)
        }
    
    def _get_profitability_recommendation(self, grade: str, ratio: float) -> str:
        """수익성 기반 권장사항"""
        recommendations = {
            'EXCELLENT': f"뛰어난 ROI ({ratio:.1f}x)! 마케팅 예산을 확대하세요.",
            'GOOD': f"좋은 성과 ({ratio:.1f}x)입니다. 현재 전략을 유지하세요.",
            'ACCEPTABLE': f"수용 가능한 수준 ({ratio:.1f}x)입니다. 전환율 개선이 필요합니다.",
            'POOR': f"수익성이 낮습니다 ({ratio:.1f}x). 타겟팅과 메시징을 재검토하세요."
        }
        return recommendations.get(grade, "데이터가 부족합니다.")

class IntegratedCTAManager:
    """통합 CTA 관리 시스템"""
    
    def __init__(self):
        self.lead_scoring = LeadScoringEngine()
        self.product_engine = ProductRecommendationEngine()
        self.follow_up = AutomatedFollowUp()
        self.marketing_content = MarketingContent()
        self.optimizer = ConversionOptimizer()
        self.revenue_calc = RevenueCalculator()
        
        # 세션 데이터 관리
        self.session_data = {}
        
    def process_consultation_request(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """상담 신청 처리 전체 플로우"""
        
        # 1. 리드 스코어링
        lead_score = self.lead_scoring.calculate_lead_score(form_data)
        
        # 2. 개인화된 상품 추천
        product_recommendations = self.product_engine.get_personalized_recommendations(form_data, lead_score)
        
        # 3. 수익 가치 계산
        customer_value = self.revenue_calc.calculate_customer_value(
            lead_score['grade'], 
            form_data.get('portfolio_info')
        )
        
        # 4. 자동 후속 조치 (상품 추천 포함)
        follow_up_success = self.follow_up.send_follow_up(form_data, lead_score, product_recommendations)
        
        # 5. 전환 추적
        cta_config = self.optimizer.get_optimized_cta_config(form_data)
        self.optimizer.track_conversion('consultation_request', form_data, cta_config)
        
        # 6. 결과 통합
        result = {
            'success': True,
            'consultation_id': form_data.get('id'),
            'lead_score': lead_score,
            'customer_value': customer_value,
            'product_recommendations': product_recommendations,
            'follow_up_sent': follow_up_success,
            'next_steps': self._get_comprehensive_next_steps(lead_score, product_recommendations),
            'estimated_contact_time': self.follow_up._calculate_contact_time(lead_score['priority']),
            'personalized_benefits': self._get_personalized_benefits(lead_score['grade'], customer_value),
            'exclusive_offers': self._get_exclusive_offers(form_data, lead_score)
        }
        
        # 7. 세션 데이터 저장
        self.session_data[form_data.get('session_id', 'anonymous')] = result
        
        return result
    
    def get_personalized_cta_experience(self, user_profile: Dict[str, Any], 
                                      portfolio_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """개인화된 전체 CTA 경험 제공"""
        
        # 사용자 프로필 보강
        enhanced_profile = self._enhance_user_profile(user_profile, portfolio_info)
        
        # 최적화된 CTA 설정
        cta_config = self.optimizer.get_optimized_cta_config(enhanced_profile)
        
        # 개인화된 메시징
        personalized_messaging = self.optimizer.get_personalized_messaging(enhanced_profile, cta_config)
        
        # 관련 이벤트 및 프로모션
        relevant_events = self.marketing_content.get_personalized_events(enhanced_profile.get('grade', 'BASIC'))
        
        # 사회적 증명
        social_proof = self.marketing_content.get_dynamic_social_proof()
        relevant_testimonials = self.marketing_content.get_relevant_testimonials(enhanced_profile.get('grade', 'BASIC'))
        
        # 상품 추천 (간단한 버전)
        if enhanced_profile.get('grade'):
            # 임시 리드 스코어 생성
            temp_lead_score = {'grade': enhanced_profile['grade']}
            product_preview = self.product_engine.get_personalized_recommendations(enhanced_profile, temp_lead_score)
        else:
            product_preview = None
        
        return {
            'cta_config': cta_config,
            'messaging': personalized_messaging,
            'events': relevant_events[:2],  # 상위 2개만
            'social_proof': {
                'stats': social_proof,
                'testimonials': relevant_testimonials
            },
            'product_preview': product_preview,
            'ui_elements': self._generate_ui_elements(cta_config, personalized_messaging),
            'tracking_data': {
                'user_segment': self._determine_user_segment(enhanced_profile),
                'session_id': enhanced_profile.get('session_id'),
                'page_context': enhanced_profile.get('page_context', 'main')
            }
        }
    
    def _enhance_user_profile(self, user_profile: Dict[str, Any], 
                            portfolio_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """사용자 프로필 보강"""
        
        enhanced = user_profile.copy()
        
        # 포트폴리오 정보 통합
        if portfolio_info:
            enhanced['portfolio_info'] = portfolio_info
            
            # 리스크 레벨 자동 추정
            if not enhanced.get('risk_level'):
                profit_rate = portfolio_info.get('profit_rate', 0)
                if profit_rate < -15:
                    enhanced['risk_level'] = 'HIGH'  # 손실 위험
                elif profit_rate > 25:
                    enhanced['risk_level'] = 'LOW'   # 공격적 투자 가능
                else:
                    enhanced['risk_level'] = 'MEDIUM'
        
        # 등급 자동 추정 (리드 스코어링 없이)
        if not enhanced.get('grade'):
            investment_amount = enhanced.get('investment_amount', '1천만원 미만')
            if '5억원 이상' in investment_amount:
                enhanced['grade'] = 'VIP'
            elif '1억원' in investment_amount:
                enhanced['grade'] = 'PREMIUM'
            elif '5천만원' in investment_amount:
                enhanced['grade'] = 'STANDARD'
            else:
                enhanced['grade'] = 'BASIC'
        
        # 세션 ID 생성
        if not enhanced.get('session_id'):
            enhanced['session_id'] = str(uuid.uuid4())[:8]
        
        return enhanced
    
    def _determine_user_segment(self, user_profile: Dict[str, Any]) -> str:
        """사용자 세그먼트 결정"""
        risk_level = user_profile.get('risk_level', 'MEDIUM')
        grade = user_profile.get('grade', 'BASIC')
        
        if grade == 'VIP':
            return 'vip_customer'
        elif risk_level == 'HIGH':
            return 'risk_averse'
        elif risk_level == 'LOW' and grade in ['PREMIUM', 'STANDARD']:
            return 'growth_focused'
        else:
            return 'balanced_investor'
    
    def _generate_ui_elements(self, cta_config: Dict[str, Any], 
                            messaging: Dict[str, Any]) -> Dict[str, Any]:
        """UI 요소 생성"""
        
        return {
            'primary_button': {
                'text': messaging['call_to_action'],
                'color': cta_config['button_color'],
                'style': 'gradient' if cta_config.get('premium_styling') else 'solid',
                'animation': cta_config.get('animation_style', 'subtle')
            },
            'urgency_banner': {
                'show': cta_config.get('scarcity_message', False),
                'text': messaging.get('urgency_message', ''),
                'style': 'pulsing' if cta_config.get('urgency_level') == 'high' else 'static'
            },
            'social_proof_section': {
                'position': cta_config.get('testimonial_position', 'top'),
                'items': messaging.get('social_proof', [])
            },
            'benefits_list': {
                'items': messaging.get('benefits', []),
                'style': 'checkmarks'
            },
            'special_badges': self._get_special_badges(cta_config)
        }
    
    def _get_special_badges(self, cta_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """특별 배지 생성"""
        badges = []
        
        if cta_config.get('show_vip_badge'):
            badges.append({
                'type': 'vip',
                'text': cta_config.get('vip_message', '🏆 VIP 서비스'),
                'color': 'gold'
            })
        
        if cta_config.get('show_exclusive_badge'):
            badges.append({
                'type': 'exclusive',
                'text': '💎 독점 서비스',
                'color': 'purple'
            })
        
        if cta_config.get('free_emphasis'):
            badges.append({
                'type': 'free',
                'text': cta_config['free_emphasis'],
                'color': 'green'
            })
        
        return badges
    
    def _get_comprehensive_next_steps(self, lead_score: Dict[str, Any], 
                                    product_recommendations: Dict[str, Any]) -> List[str]:
        """종합적인 다음 단계"""
        
        priority = lead_score['priority']
        grade = lead_score['grade']
        
        # 기본 다음 단계
        base_steps = {
            'URGENT': [
                "📞 30분 내 전문가 직통 연결",
                "🚨 긴급 포트폴리오 위험 진단",
                "🛡️ 즉시 실행 가능한 리스크 관리 방안",
                "📈 손실 최소화 전략 수립"
            ],
            'HIGH': [
                "📞 2시간 내 우선 상담 연결",
                "📊 개인 맞춤 포트폴리오 분석",
                "💼 최적화된 투자 전략 제안",
                "🎯 목표 수익률 달성 로드맵"
            ],
            'MEDIUM': [
                "📞 24시간 내 전문가 상담",
                "📄 맞춤 투자 가이드 제공",
                "💡 포트폴리오 개선 제안",
                "📚 투자 교육 자료 안내"
            ],
            'LOW': [
                "📧 상세 투자 자료 이메일 발송",
                "📱 투자 앱 가이드 제공",
                "📞 편한 시간 상담 예약",
                "🔔 맞춤 투자 정보 알림 설정"
            ]
        }
        
        steps = base_steps.get(priority, base_steps['MEDIUM']).copy()
        
        # 상품 추천 기반 추가 단계
        if product_recommendations:
            primary_rec = product_recommendations.get('primary_recommendation')
            if primary_rec == 'vip_exclusive':
                steps.append("💎 VIP 전용 투자 상품 안내")
            elif primary_rec == 'aggressive':
                steps.append("🚀 고수익 투자 기회 제공")
            elif primary_rec == 'conservative':
                steps.append("🛡️ 안전한 자산 보전 방안")
        
        # 등급별 추가 혜택
        if grade == 'VIP':
            steps.append("🏆 VIP 전담 PB 서비스 연결")
        elif grade == 'PREMIUM':
            steps.append("⭐ 프리미엄 고객 우대 서비스")
        
        return steps
    
    def _get_personalized_benefits(self, grade: str, customer_value: Dict[str, Any]) -> List[str]:
        """개인화된 혜택 목록"""
        
        base_benefits = [
            "✅ 100% 무료 전문가 상담",
            "✅ AI 기반 포트폴리오 분석",
            "✅ 개인 맞춤 투자 전략"
        ]
        
        grade_benefits = {
            'VIP': [
                "✅ VIP 전담 PB 무료 배정",
                "✅ 독점 투자 상품 우선 제공",
                "✅ 24시간 프리미엄 지원",
                f"✅ 연간 예상 수익: {customer_value['annual_revenue']:,.0f}원"
            ],
            'PREMIUM': [
                "✅ 프리미엄 투자 정보 제공",
                "✅ 우선 상담 및 빠른 응답",
                "✅ 고수익 상품 우선 안내",
                f"✅ 월 예상 수익: {customer_value['monthly_revenue']:,.0f}원"
            ],
            'STANDARD': [
                "✅ 체계적인 포트폴리오 관리",
                "✅ 정기적인 투자 리포트",
                "✅ 세금 절약 투자 가이드"
            ],
            'BASIC': [
                "✅ 투자 기초 교육 제공",
                "✅ 단계별 투자 가이드",
                "✅ 리스크 관리 노하우"
            ]
        }
        
        return base_benefits + grade_benefits.get(grade, grade_benefits['BASIC'])
    
    def _get_exclusive_offers(self, form_data: Dict[str, Any], lead_score: Dict[str, Any]) -> List[Dict[str, Any]]:
        """독점 제안 생성"""
        
        offers = []
        grade = lead_score['grade']
        
        # 신규 고객 혜택
        if form_data.get('source') == 'ai_investment_advisor':
            offers.append({
                'type': 'new_customer',
                'title': '🎯 AI 어드바이저 특별 혜택',
                'description': '첫 3개월 거래 수수료 50% 할인',
                'validity': '48시간 한정',
                'urgency': 'high'
            })
        
        # 등급별 특별 혜택
        if grade == 'VIP':
            offers.append({
                'type': 'vip_exclusive',
                'title': '💎 VIP 전용 프리미엄 패키지',
                'description': '사모펀드 우선 참여 + 전담 PB + 수수료 면제',
                'validity': '즉시 적용',
                'urgency': 'medium'
            })
        elif grade == 'PREMIUM':
            offers.append({
                'type': 'premium_upgrade',
                'title': '⭐ 프리미엄 고객 특별 혜택',
                'description': '해외 투자 수수료 30% 할인 + 프리미엄 리포트',
                'validity': '1주일 내 연락 시',
                'urgency': 'medium'
            })
        
        # 포트폴리오 상태별 긴급 혜택
        portfolio_info = form_data.get('portfolio_info', {})
        if portfolio_info.get('profit_rate', 0) < -10:
            offers.append({
                'type': 'emergency_support',
                'title': '🚨 긴급 손실 방지 패키지',
                'description': '무료 긴급 진단 + 손실 최소화 전략 + 우선 상담',
                'validity': '즉시',
                'urgency': 'high'
            })
        
        return offers
    
    def get_dashboard_metrics(self) -> Dict[str, Any]:
        """통합 CTA 성과 대시보드"""
        
        # 전환 분석
        conversion_analytics = self.optimizer.get_conversion_analytics()
        
        # 사회적 증명 데이터
        social_proof = self.marketing_content.get_dynamic_social_proof()
        
        # 예시 고객 데이터 (실제로는 DB에서 조회)
        sample_customers = [
            {'grade': 'VIP', 'portfolio_info': {'current_value': 300000000}},
            {'grade': 'PREMIUM', 'portfolio_info': {'current_value': 80000000}},
            {'grade': 'STANDARD', 'portfolio_info': {'current_value': 25000000}},
            {'grade': 'BASIC', 'portfolio_info': {'current_value': 8000000}}
        ]
        
        # 마케팅 ROI
        marketing_roi = self.revenue_calc.calculate_marketing_roi(2000000, sample_customers, 'ai_advisor_cta')
        
        # 상품 추천 성과
        product_performance = self._analyze_product_recommendation_performance()
        
        # 이벤트 참여 현황
        event_metrics = self._get_event_metrics()
        
        return {
            'conversion_metrics': conversion_analytics,
            'revenue_impact': marketing_roi,
            'social_proof_stats': social_proof,
            'product_recommendation_performance': product_performance,
            'event_participation': event_metrics,
            'active_leads': 247,
            'vip_conversion_rate': 12.8,
            'avg_customer_value': marketing_roi['avg_customer_ltv'],
            'total_pipeline_value': marketing_roi['total_customer_ltv'],
            'optimization_recommendations': self._get_comprehensive_recommendations()
        }
    
    def _analyze_product_recommendation_performance(self) -> Dict[str, Any]:
        """상품 추천 성과 분석"""
        
        # 실제로는 DB에서 조회할 데이터
        mock_data = {
            'total_recommendations': 1247,
            'conversion_by_product': {
                'conservative': {'recommendations': 412, 'conversions': 89, 'rate': 21.6},
                'balanced': {'recommendations': 623, 'conversions': 156, 'rate': 25.0},
                'aggressive': {'recommendations': 189, 'conversions': 52, 'rate': 27.5},
                'vip_exclusive': {'recommendations': 23, 'conversions': 8, 'rate': 34.8}
            },
            'avg_recommendation_accuracy': 87.3,
            'customer_satisfaction': 4.6
        }
        
        return mock_data
    
    def _get_event_metrics(self) -> Dict[str, Any]:
        """이벤트 참여 현황"""
        
        total_participants = sum(event['current_participants'] for event in self.marketing_content.current_events)
        
        return {
            'total_active_events': len(self.marketing_content.current_events),
            'total_participants': total_participants,
            'participation_by_grade': {
                'VIP': 23,
                'PREMIUM': 245,
                'STANDARD': 534,
                'BASIC': 412
            },
            'most_popular_event': 'portfolio_diagnosis_2025',
            'conversion_rate_from_events': 18.7
        }
    
    def _get_comprehensive_recommendations(self) -> List[Dict[str, str]]:
        """종합 최적화 권장사항"""
        
        recommendations = []
        
        # 전환율 최적화
        conversion_data = self.optimizer.get_conversion_analytics()
        if conversion_data.get('conversion_rate', 0) < 15:
            recommendations.append({
                'category': '전환율 개선',
                'action': 'CTA 버튼 색상을 오렌지로 변경하고 긴급도 메시지 강화',
                'priority': 'high',
                'expected_impact': '+3-5% 전환율 증가'
            })
        
        # 상품 추천 최적화
        recommendations.append({
            'category': '상품 추천',
            'action': 'VIP 고객 대상 독점 상품 추천 비중 확대',
            'priority': 'medium',
            'expected_impact': '+10% VIP 전환율 증가'
        })
        
        # 이벤트 최적화
        recommendations.append({
            'category': '이벤트 마케팅',
            'action': '포트폴리오 진단 이벤트 참여율이 높으니 비슷한 이벤트 추가 기획',
            'priority': 'medium',
            'expected_impact': '+15% 신규 고객 유치'
        })
        
        # 알림 서비스 개선
        recommendations.append({
            'category': '고객 유지',
            'action': '개인화된 알림 서비스 고도화로 고객 만족도 향상',
            'priority': 'low',
            'expected_impact': '+8% 고객 유지율 증가'
        })
        
        return recommendations

# Streamlit 통합 함수들

def init_integrated_cta_system():
    """통합 CTA 시스템 초기화"""
    if 'integrated_cta_manager' not in st.session_state:
        st.session_state.integrated_cta_manager = IntegratedCTAManager()
    
    return st.session_state.integrated_cta_manager

def show_comprehensive_cta_experience(user_profile: Dict[str, Any] = None, 
                                    portfolio_info: Dict[str, Any] = None,
                                    page_context: str = "main"):
    """종합 CTA 경험 표시"""
    
    cta_manager = init_integrated_cta_system()
    
    # 기본 사용자 프로필 설정
    if not user_profile:
        user_profile = {
            'session_id': st.session_state.get('session_id', str(uuid.uuid4())[:8]),
            'page_context': page_context
        }
    
    # 개인화된 CTA 경험 생성
    cta_experience = cta_manager.get_personalized_cta_experience(user_profile, portfolio_info)
    
    # 1. 사회적 증명 섹션
    _render_social_proof_section(cta_experience['social_proof'])
    
    # 2. 메인 CTA 섹션
    _render_main_cta_section(cta_experience)
    
    # 3. 상품 추천 섹션
    if cta_experience['product_preview']:
        _render_product_preview_section(cta_experience['product_preview'])
    
    # 4. 이벤트 및 프로모션
    _render_events_section(cta_experience['events'])
    
    # 5. 상담 신청 폼 (버튼 클릭 시)
    if st.session_state.get('show_consultation_form', False):
        _render_consultation_form(cta_manager, user_profile)
    
    # 전환 추적
    cta_manager.optimizer.track_conversion('page_view', user_profile, cta_experience['cta_config'])

def _render_social_proof_section(social_proof_data: Dict[str, Any]):
    """사회적 증명 섹션 렌더링"""
    
    stats = social_proof_data['stats']
    testimonials = social_proof_data['testimonials']
    
    st.markdown("### 📊 실시간 서비스 현황")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("누적 사용자", f"{stats['total_users']:,}명", f"+{stats.get('new_signups_today', 67)}")
    
    with col2:
        st.metric("만족도", f"{stats['average_satisfaction']}/5.0", f"{stats.get('success_rate_today', 94.2):.1f}%")
    
    with col3:
        st.metric("수익 개선률", f"{stats['profit_users_ratio']}%", f"+{stats['average_profit_rate']}%")
    
    with col4:
        st.metric("현재 상담 중", f"{stats.get('consultations_in_progress', 43)}명", 
                 f"평균 {stats.get('avg_response_time_minutes', 18)}분")
    
    # 실시간 활동 표시
    if stats.get('new_signups_today', 0) > 50:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #00b894 0%, #00cec9 100%); 
                    color: white; padding: 0.5rem; border-radius: 0.3rem; margin: 0.5rem 0; text-align: center;">
            🔥 <strong>인기 급상승!</strong> 오늘만 {new_signups}명이 새로 가입했습니다!
        </div>
        """.format(new_signups=stats.get('new_signups_today', 67)), unsafe_allow_html=True)
    
    # 사용자 후기 (간단 버전)
    if testimonials:
        with st.expander("💬 실제 사용자 후기", expanded=False):
            for testimonial in testimonials[:2]:  # 상위 2개만
                st.markdown(f"""
                <div style="background: #f8f9fa; padding: 1rem; border-radius: 0.5rem; margin: 0.5rem 0;">
                    <div style="display: flex; justify-content: space-between;">
                        <strong>{testimonial['user']}</strong>
                        <span style="color: #f39c12;">{'⭐' * testimonial['rating']}</span>
                    </div>
                    <p style="margin: 0.5rem 0;">"{testimonial['comment']}"</p>
                    <small style="color: #6c757d;">수익: {testimonial['profit']} ({testimonial['period']})</small>
                </div>
                """, unsafe_allow_html=True)

def _render_main_cta_section(cta_experience: Dict[str, Any]):
    """메인 CTA 섹션 렌더링"""
    
    config = cta_experience['cta_config']
    messaging = cta_experience['messaging']
    ui_elements = cta_experience['ui_elements']
    
    # 긴급도 배너
    if ui_elements['urgency_banner']['show']:
        urgency_style = "animation: blink 2s infinite;" if ui_elements['urgency_banner']['style'] == 'pulsing' else ""
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%); 
                    color: white; padding: 1rem; border-radius: 0.5rem; margin: 1rem 0; 
                    text-align: center; {urgency_style}">
            ⏰ <strong>{ui_elements['urgency_banner']['text']}</strong>
        </div>
        """, unsafe_allow_html=True)
    
    # 메인 CTA 컨테이너
    button_color = ui_elements['primary_button']['color']
    
    if button_color == 'red':
        gradient = "linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%)"
    elif button_color == 'orange':
        gradient = "linear-gradient(135deg, #fd79a8 0%, #fdcb6e 100%)"
    elif button_color == 'green':
        gradient = "linear-gradient(135deg, #00b894 0%, #00cec9 100%)"
    else:  # blue
        gradient = "linear-gradient(135deg, #74b9ff 0%, #0984e3 100%)"
    
    # 특별 배지들
    badges_html = ""
    for badge in ui_elements.get('special_badges', []):
        badge_color = {
            'gold': '#f39c12',
            'purple': '#9b59b6', 
            'green': '#27ae60'
        }.get(badge['color'], '#3498db')
        
        badges_html += f"""
        <div style="background: {badge_color}; color: white; padding: 0.3rem 0.8rem; 
                    border-radius: 1rem; display: inline-block; margin: 0.2rem; font-size: 0.9rem;">
            {badge['text']}
        </div>
        """
    
    st.markdown(f"""
    <div style="{gradient} padding: 2rem; border-radius: 1rem; margin: 1rem 0; text-align: center; color: white;">
        <h3 style="margin: 0 0 0.5rem 0;">{messaging['call_to_action']}</h3>
        <p style="margin: 0 0 1rem 0; font-size: 1.1rem;">{messaging.get('urgency_message', '')}</p>
        
        {badges_html}
        
        <div style="margin: 1rem 0;">
            {''.join([f'<div style="margin: 0.3rem 0;">✅ {benefit}</div>' for benefit in messaging.get('benefits', [])[:3]])}
        </div>
        
        <div style="margin: 1rem 0; font-size: 0.9rem; opacity: 0.9;">
            {'<br>'.join(messaging.get('social_proof', []))}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 메인 CTA 버튼
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(
            f"🎯 {messaging['call_to_action']}", 
            type="primary", 
            use_container_width=True,
            key="main_cta_button"
        ):
            st.session_state.show_consultation_form = True
            st.rerun()

def _render_product_preview_section(product_preview: Dict[str, Any]):
    """상품 미리보기 섹션"""
    
    if not product_preview or not product_preview.get('products'):
        return
    
    st.markdown("### 🎯 맞춤 투자 상품 미리보기")
    
    primary_rec = product_preview['primary_recommendation']
    product = product_preview['products'][primary_rec]
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); 
                    padding: 1.5rem; border-radius: 1rem;">
            <h4 style="margin: 0 0 0.5rem 0; color: #2d3436;">
                🏆 {product['name']}
            </h4>
            <p style="margin: 0 0 1rem 0; color: #636e72;">
                {product['description']}
            </p>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; font-size: 0.9rem;">
                <div>
                    <strong>예상 수익률:</strong> {product['expected_return']}<br>
                    <strong>위험 수준:</strong> {product['risk_level']}
                </div>
                <div>
                    <strong>최소 투자:</strong> {product['min_investment']:,}원<br>
                    <strong>추천 상품:</strong> {', '.join(product['products'][:2])}...
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if st.button("📊 상세 상품 정보", use_container_width=True):
            st.info("전문가 상담 시 모든 상품 정보를 자세히 안내해드립니다.")
        
        if st.button("💰 수익 시뮬레이션", use_container_width=True):
            st.info("개인별 투자 금액에 따른 예상 수익을 계산해드립니다.")

def _render_events_section(events: List[Dict[str, Any]]):
    """이벤트 섹션 렌더링"""
    
    if not events:
        return
    
    st.markdown("### 🎉 진행 중인 특별 이벤트")
    
    for event in events:
        participation_rate = event.get('participation_rate', 0)
        
        # 참여율에 따른 스타일
        if participation_rate > 80:
            bg_color = "linear-gradient(135deg, #ff7675 0%, #fd79a8 100%)"
            urgency_text = "🔥 마감 임박!"
        elif participation_rate > 50:
            bg_color = "linear-gradient(135deg, #fdcb6e 0%, #e17055 100%)"
            urgency_text = "⏰ 인기 상승 중"
        else:
            bg_color = "linear-gradient(135deg, #74b9ff 0%, #0984e3 100%)"
            urgency_text = "✨ 참여 가능"
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"""
            <div style="background: {bg_color}; color: white; padding: 1rem; border-radius: 0.5rem; margin: 0.5rem 0;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h4 style="margin: 0;">{event['title']}</h4>
                    <span style="background: rgba(255,255,255,0.2); padding: 0.2rem 0.5rem; border-radius: 0.3rem; font-size: 0.8rem;">
                        {urgency_text}
                    </span>
                </div>
                <p style="margin: 0.5rem 0; font-size: 0.9rem;">{event['description']}</p>
                <div style="font-size: 0.8rem; opacity: 0.9;">
                    📅 {event['period']} | 🎁 {event['benefit']} | 👥 {event['current_participants']}/{event['max_participants']}명 참여
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if st.button(event['cta'], key=f"event_{event['id']}", use_container_width=True):
                st.success(f"'{event['title']}' 이벤트 참여 신청이 완료되었습니다!")
                # 이벤트 참여 추적
                cta_manager = st.session_state.get('integrated_cta_manager')
                if cta_manager:
                    cta_manager.marketing_content.track_event_participation(
                        event['id'], 
                        {'id': st.session_state.get('session_id')}
                    )

def _render_consultation_form(cta_manager: IntegratedCTAManager, user_profile: Dict[str, Any]):
    """상담 신청 폼 렌더링"""
    
    st.markdown("---")
    st.markdown("### 📋 전문가 상담 신청")
    
    with st.form("integrated_consultation_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("이름 *", placeholder="홍길동")
            phone = st.text_input("연락처 *", placeholder="010-1234-5678")
            
        with col2:
            email = st.text_input("이메일", placeholder="hong@example.com")
            preferred_contact = st.selectbox("선호 연락 방법", 
                                           ["전화", "이메일", "SMS", "카카오톡"])
        
        investment_experience = st.selectbox(
            "투자 경험",
            ["초보 (1년 미만)", "초급 (1-3년)", "중급 (3-10년)", "고급 (10년 이상)"]
        )
        
        investment_amount = st.selectbox(
            "투자 예정 금액",
            ["1천만원 미만", "1천-5천만원", "5천만원-1억원", "1억원-5억원", "5억원 이상"]
        )
        
        # 관심 분야 (다중 선택)
        consultation_topics = st.multiselect(
            "상담 희망 분야",
            ["포트폴리오 최적화", "리스크 관리", "세금 절약", "연금 투자", "해외 투자", "ESG 투자"],
            default=["포트폴리오 최적화"]
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
        col1, col2 = st.columns(2)
        with col1:
            privacy_agreed = st.checkbox("개인정보 수집 및 이용 동의 (필수)", value=False)
        with col2:
            marketing_agreed = st.checkbox("마케팅 정보 수신 동의 (선택)", value=True)
        
        submitted = st.form_submit_button("🎯 상담 신청하기", type="primary", use_container_width=True)
        
        if submitted:
            if not name or not phone:
                st.error("이름과 연락처는 필수 입력 사항입니다.")
            elif not privacy_agreed:
                st.error("개인정보 수집 및 이용에 동의해주세요.")
            else:
                # 폼 데이터 구성
                form_data = {
                    'id': str(uuid.uuid4()),
                    'name': name,
                    'phone': phone,
                    'email': email,
                    'preferred_contact': preferred_contact,
                    'investment_experience': investment_experience,
                    'investment_amount': investment_amount,
                    'consultation_topic': consultation_topics,
                    'consultation_time': consultation_time,
                    'additional_info': additional_info,
                    'privacy_agreed': privacy_agreed,
                    'marketing_agreed': marketing_agreed,
                    'timestamp': datetime.now().isoformat(),
                    'source': 'ai_investment_advisor',
                    'session_id': user_profile.get('session_id'),
                    'portfolio_info': user_profile.get('portfolio_info'),
                    'risk_level': user_profile.get('risk_level', 'MEDIUM')
                }
                
                # 상담 신청 처리
                try:
                    result = cta_manager.process_consultation_request(form_data)
                    
                    if result['success']:
                        st.success("✅ 상담 신청이 완료되었습니다!")
                        
                        # 결과 정보 표시
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.info(f"""
                            📋 **신청 정보**
                            - 신청 번호: {result['consultation_id'][:8]}
                            - 고객 등급: {result['lead_score']['grade']}
                            - 우선 순위: {result['lead_score']['priority']}
                            """)
                        
                        with col2:
                            st.info(f"""
                            📞 **연락 예정**
                            - 예상 연락 시간: {result['estimated_contact_time']}
                            - 예상 고객 가치: {result['customer_value']['annual_revenue']:,.0f}원/년
                            """)
                        
                        # 다음 단계 안내
                        st.markdown("### 🎯 다음 단계")
                        for step in result['next_steps'][:4]:
                            st.write(f"**{step}**")
                        
                        # 개인화된 혜택 표시
                        if result.get('personalized_benefits'):
                            with st.expander("🎁 맞춤 혜택 미리보기"):
                                for benefit in result['personalized_benefits'][:5]:
                                    st.write(benefit)
                        
                        # 독점 제안
                        if result.get('exclusive_offers'):
                            st.markdown("### 💎 특별 제안")
                            for offer in result['exclusive_offers']:
                                urgency_color = {
                                    'high': '#e74c3c',
                                    'medium': '#f39c12',
                                    'low': '#27ae60'
                                }.get(offer['urgency'], '#3498db')
                                
                                st.markdown(f"""
                                <div style="border-left: 4px solid {urgency_color}; 
                                            background: #f8f9fa; padding: 1rem; margin: 0.5rem 0;">
                                    <h5 style="margin: 0 0 0.5rem 0; color: {urgency_color};">
                                        {offer['title']}
                                    </h5>
                                    <p style="margin: 0 0 0.5rem 0;">{offer['description']}</p>
                                    <small style="color: #6c757d;">유효기간: {offer['validity']}</small>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        # 폼 숨기기
                        st.session_state.show_consultation_form = False
                        
                        # 즉시 연락 옵션
                        st.markdown("### 📞 즉시 연락을 원하시나요?")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if st.button("📞 지금 전화 연결", use_container_width=True):
                                st.info("🕐 고객센터 운영시간: 평일 9:00-18:00\n📞 1588-6666")
                        
                        with col2:
                            if st.button("💬 카카오톡 상담", use_container_width=True):
                                st.info("💬 카카오톡에서 '미래에셋증권' 검색 후 친구추가")
                    
                    else:
                        st.error("신청 처리 중 오류가 발생했습니다. 다시 시도해주세요.")
                        
                except Exception as e:
                    st.error(f"시스템 오류가 발생했습니다: {str(e)}")
                    logger.error(f"상담 신청 처리 오류: {e}")

def display_integrated_cta_dashboard():
    """통합 CTA 성과 대시보드 (관리자용)"""
    
    if not st.secrets.get("ADMIN_MODE", False):
        return
    
    cta_manager = init_integrated_cta_system()
    metrics = cta_manager.get_dashboard_metrics()
    
    st.markdown("## 🎯 통합 CTA 성과 대시보드")
    
    # 핵심 지표
    st.markdown("### 📊 핵심 성과 지표")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "전환율", 
            f"{metrics['conversion_metrics']['conversion_rate']}%",
            delta=f"+{2.3}%" if metrics['conversion_metrics']['conversion_rate'] > 12 else f"-{1.1}%"
        )
    
    with col2:
        st.metric("활성 리드", metrics['active_leads'], delta="+23")
    
    with col3:
        st.metric("VIP 전환율", f"{metrics['vip_conversion_rate']}%", delta="+0.8%")
    
    with col4:
        st.metric(
            "평균 고객가치", 
            f"{metrics['avg_customer_value']:,.0f}원",
            delta=f"+{245000:,.0f}원"
        )
    
    # 수익 영향 분석
    st.markdown("### 💰 수익 영향 분석")
    roi_data = metrics['revenue_impact']
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("마케팅 ROI", f"{roi_data['roi_percentage']:+.1f}%")
        st.caption(f"투자: {roi_data['marketing_cost']:,}원")
    
    with col2:
        st.metric("총 파이프라인 가치", f"{roi_data['total_customer_ltv']:,.0f}원")
        st.caption(f"고객 {roi_data['acquired_customers']}명")
    
    with col3:
        st.metric("투자회수기간", f"{roi_data['payback_period_months']:.1f}개월")
        st.caption(f"연간 수익: {roi_data['total_annual_revenue']:,.0f}원")
    
    # 등급별 분포
    st.markdown("### 👥 고객 등급 분포")
    grade_dist = roi_data['grade_distribution']
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("VIP", f"{grade_dist['VIP']}명")
    with col2:
        st.metric("PREMIUM", f"{grade_dist['PREMIUM']}명")
    with col3:
        st.metric("STANDARD", f"{grade_dist['STANDARD']}명")
    with col4:
        st.metric("BASIC", f"{grade_dist['BASIC']}명")
    
    # 상품 추천 성과
    st.markdown("### 🎯 상품 추천 성과")
    product_perf = metrics['product_recommendation_performance']
    
    for product_type, data in product_perf['conversion_by_product'].items():
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.write(f"**{product_type.title()}**")
        with col2:
            st.metric("추천 수", f"{data['recommendations']}건")
        with col3:
            st.metric("전환율", f"{data['rate']}%")
    
    # 이벤트 참여 현황
    st.markdown("### 🎉 이벤트 성과")
    event_metrics = metrics['event_participation']
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("진행 중인 이벤트", f"{event_metrics['total_active_events']}개")
    
    with col2:
        st.metric("총 참여자", f"{event_metrics['total_participants']}명")
    
    with col3:
        st.metric("이벤트 전환율", f"{event_metrics['conversion_rate_from_events']}%")
    
    # A/B 테스트 결과
    st.markdown("### 🧪 A/B 테스트 결과")
    
    conversion_analytics = metrics['conversion_metrics']
    ab_results = conversion_analytics.get('ab_test_results', {})
    
    if ab_results:
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**버튼 색상 성과**")
            for color, rate in ab_results.get('button_colors', {}).items():
                st.write(f"• {color.title()}: {rate:.1%}")
        
        with col2:
            st.write("**긴급도 메시지 성과**")
            for urgency, rate in ab_results.get('urgency_levels', {}).items():
                st.write(f"• {urgency.title()}: {rate:.1%}")
    
    # 최적화 권장사항
    st.markdown("### 🚀 최적화 권장사항")
    
    recommendations = metrics['optimization_recommendations']
    
    for rec in recommendations:
        priority_color = {
            'high': '🔴',
            'medium': '🟡', 
            'low': '🟢'
        }.get(rec['priority'], '🔵')
        
        with st.expander(f"{priority_color} {rec['category']} - {rec['priority'].upper()} 우선순위"):
            st.write(f"**조치 사항:** {rec['action']}")
            st.write(f"**예상 효과:** {rec['expected_impact']}")
    
    # 실시간 모니터링
    st.markdown("### 📈 실시간 모니터링")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**오늘의 활동**")
        social_stats = metrics['social_proof_stats']
        st.write(f"• 신규 가입: {social_stats.get('new_signups_today', 67)}명")
        st.write(f"• 진행 중 상담: {social_stats.get('consultations_in_progress', 43)}건")
        st.write(f"• 평균 응답 시간: {social_stats.get('avg_response_time_minutes', 18)}분")
    
    with col2:
        st.markdown("**시간대별 전환율**")
        time_data = conversion_analytics.get('best_converting_time', {})
        if time_data:
            st.write(f"• 최고 성과 시간: {time_data.get('best_hour', 14)}시")
            st.write(f"• 해당 시간 전환: {time_data.get('conversions', 0)}건")
    
    # 채널 성과 분석
    if 'channel_performance' in roi_data:
        st.markdown("### 📢 채널 성과 분석")
        channel_perf = roi_data['channel_performance']
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("채널", channel_perf['channel'])
        
        with col2:
            st.metric(
                "실제 전환율", 
                f"{channel_perf['actual_conversion_rate']:.1%}",
                delta=f"{channel_perf['actual_conversion_rate'] - channel_perf['expected_conversion_rate']:+.1%}"
            )
        
        with col3:
            efficiency = channel_perf['efficiency_ratio']
            st.metric(
                "효율성", 
                f"{efficiency:.1f}x",
                delta="효율적" if efficiency > 1 else "개선 필요"
            )

# 편의 함수들

def show_risk_based_cta(portfolio_info: Dict[str, Any]):
    """리스크 기반 맞춤 CTA"""
    
    if not portfolio_info:
        return
    
    profit_rate = portfolio_info.get('profit_rate', 0)
    
    if profit_rate < -15:
        context = "high_loss"
        user_profile = {'risk_level': 'HIGH', 'portfolio_info': portfolio_info}
    elif profit_rate > 25:
        context = "high_profit" 
        user_profile = {'risk_level': 'LOW', 'portfolio_info': portfolio_info}
    else:
        context = "balanced"
        user_profile = {'risk_level': 'MEDIUM', 'portfolio_info': portfolio_info}
    
    show_comprehensive_cta_experience(user_profile, portfolio_info, context)

def track_user_journey(action: str, user_data: Dict[str, Any] = None):
    """사용자 여정 추적"""
    
    cta_manager = st.session_state.get('integrated_cta_manager')
    if cta_manager and user_data:
        cta_config = cta_manager.optimizer.get_optimized_cta_config(user_data)
        cta_manager.optimizer.track_conversion(action, user_data, cta_config)

def get_personalized_recommendations(user_profile: Dict[str, Any]) -> Dict[str, Any]:
    """개인화된 추천 정보 반환"""
    
    cta_manager = init_integrated_cta_system()
    
    # 임시 리드 스코어 생성
    temp_lead_score = {'grade': user_profile.get('grade', 'BASIC')}
    
    return cta_manager.product_engine.get_personalized_recommendations(user_profile, temp_lead_score)

# 시스템 설정 및 초기화

def setup_cta_system_config():
    """CTA 시스템 설정"""
    
    if 'cta_system_config' not in st.session_state:
        st.session_state.cta_system_config = {
            'ab_testing_enabled': True,
            'personalization_level': 'high',
            'real_time_optimization': True,
            'social_proof_enabled': True,
            'event_tracking_enabled': True,
            'admin_mode': st.secrets.get("ADMIN_MODE", False)
        }
    
    return st.session_state.cta_system_config

def initialize_session_tracking():
    """세션 추적 초기화"""
    
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())[:8]
    
    if 'page_views' not in st.session_state:
        st.session_state.page_views = 0
    
    if 'session_start_time' not in st.session_state:
        st.session_state.session_start_time = datetime.now()
    
    # 페이지 뷰 증가
    st.session_state.page_views += 1
    
    return {
        'session_id': st.session_state.session_id,
        'page_views': st.session_state.page_views,
        'session_duration': (datetime.now() - st.session_state.session_start_time).seconds
    }

# 메인 실행 함수

def run_integrated_cta_system(user_profile: Dict[str, Any] = None, 
                             portfolio_info: Dict[str, Any] = None,
                             page_context: str = "main"):
    """통합 CTA 시스템 실행"""
    
    # 시스템 설정
    config = setup_cta_system_config()
    
    # 세션 추적
    session_data = initialize_session_tracking()
    
    # 사용자 프로필에 세션 데이터 추가
    if user_profile:
        user_profile.update(session_data)
        user_profile['page_context'] = page_context
    else:
        user_profile = {**session_data, 'page_context': page_context}
    
    # 관리자 대시보드 (조건부)
    if config['admin_mode'] and st.sidebar.checkbox("관리자 대시보드 표시"):
        display_integrated_cta_dashboard()
        st.markdown("---")
    
    # 메인 CTA 경험
    show_comprehensive_cta_experience(user_profile, portfolio_info, page_context)
    
    # 사용자 여정 추적
    track_user_journey('page_view', user_profile)
    
    return user_profile

# 사용 예시 및 테스트 함수

def test_cta_system():
    """CTA 시스템 테스트"""
    
    st.markdown("## 🧪 CTA 시스템 테스트")
    
    # 테스트 시나리오 선택
    test_scenario = st.selectbox(
        "테스트 시나리오 선택",
        [
            "신규 사용자 (기본)",
            "고위험 포트폴리오 고객",
            "고수익 달성 고객", 
            "VIP 고객",
            "손실 우려 고객"
        ]
    )
    
    # 시나리오별 테스트 데이터
    test_profiles = {
        "신규 사용자 (기본)": {
            'grade': 'BASIC',
            'risk_level': 'MEDIUM',
            'investment_amount': '1천만원 미만'
        },
        "고위험 포트폴리오 고객": {
            'grade': 'STANDARD',
            'risk_level': 'HIGH',
            'investment_amount': '5천만원-1억원',
            'portfolio_info': {'current_value': 50000000, 'profit_rate': -18.5}
        },
        "고수익 달성 고객": {
            'grade': 'PREMIUM',
            'risk_level': 'LOW',
            'investment_amount': '1억원-5억원',
            'portfolio_info': {'current_value': 150000000, 'profit_rate': 28.3}
        },
        "VIP 고객": {
            'grade': 'VIP',
            'risk_level': 'MEDIUM',
            'investment_amount': '5억원 이상',
            'portfolio_info': {'current_value': 800000000, 'profit_rate': 15.2}
        },
        "손실 우려 고객": {
            'grade': 'STANDARD',
            'risk_level': 'HIGH',
            'investment_amount': '1천-5천만원',
            'portfolio_info': {'current_value': 25000000, 'profit_rate': -25.8}
        }
    }
    
    selected_profile = test_profiles[test_scenario]
    
    st.markdown(f"**선택된 시나리오:** {test_scenario}")
    st.json(selected_profile)
    
    # 테스트 실행
    if st.button("🚀 테스트 실행"):
        st.markdown("---")
        run_integrated_cta_system(
            user_profile=selected_profile,
            portfolio_info=selected_profile.get('portfolio_info'),
            page_context="test"
        )

if __name__ == "__main__":
    # 개발 환경에서 테스트 실행
    test_cta_system()
