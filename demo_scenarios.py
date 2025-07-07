# demo_scenarios.py - 공모전 발표용 압도적 데모
"""
미래에셋증권 임직원들을 감동시킬 실전 데모 시나리오
"""

import streamlit as st
import time
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, Any, List
import random

class WowFactorDemo:
    """압도적 임팩트를 위한 데모 시나리오"""
    
    def __init__(self):
        self.demo_scenarios = {
            "crisis_management": {
                "title": "📉 급락장 대응 시나리오",
                "description": "2008년 금융위기 수준의 급락 상황에서 AI가 고객을 어떻게 보호하는가",
                "wow_factor": 9.5
            },
            "whale_customer": {
                "title": "🐋 100억원 고객 맞춤 서비스",
                "description": "초고액 고객의 복잡한 포트폴리오 실시간 관리",
                "wow_factor": 9.8
            },
            "market_crash_prediction": {
                "title": "🚨 시장 붕괴 예측 및 대응",
                "description": "AI가 3일 전에 시장 붕괴를 예측하고 고객 자산을 보호",
                "wow_factor": 10.0
            }
        }
    
    def run_crisis_management_demo(self):
        """급락장 대응 시나리오"""
        st.markdown("## 📉 2008년 수준 급락장 실시간 대응 시뮬레이션")
        st.warning("⚠️ **시장 급락 상황 가정**: 코스피 -8%, 나스닥 -12% 폭락")
        
        # 실시간 포트폴리오 가치 변화
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # 실시간 차트
            self._create_crash_simulation_chart()
        
        with col2:
            # 실시간 알림
            st.markdown("### 🚨 AI 긴급 알림")
            alerts = [
                "15:20 - 급락 감지, 손절매 신호 발생",
                "15:18 - 안전자산 편입 권고",
                "15:15 - 시장 변동성 급증 경고",
                "15:12 - 포트폴리오 리밸런싱 제안"
            ]
            
            for alert in alerts:
                st.error(f"🔴 {alert}")
                time.sleep(0.5)
        
        # AI 대응 전략
        st.markdown("### 🤖 AI 자동 대응 전략")
        
        with st.container():
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.success("✅ **자산 보호 완료**\n- 손실 -2.1% (시장 -8%)\n- 현금 비중 확대\n- 안전자산 편입")
            
            with col2:
                st.info("📊 **리밸런싱 제안**\n- 기술주 50% → 30%\n- 채권 20% → 35%\n- 현금 30% → 35%")
            
            with col3:
                st.warning("⏰ **추가 대응**\n- VIX 지수 모니터링\n- 연준 발표 대기\n- 저가 매수 기회 포착")
        
        # 고객 메시지 시뮬레이션
        st.markdown("### 📱 고객 자동 알림 발송")
        
        message_template = """
        🚨 **긴급 포트폴리오 알림**
        
        안녕하세요 김○○님,
        
        현재 시장 급락 상황에서 AI가 자동으로 포트폴리오를 보호했습니다.
        
        **보호 결과:**
        • 예상 손실: -850만원 → 실제 손실: -180만원
        • **670만원 손실 방지 성공** ✅
        
        **AI 대응 조치:**
        1. 기술주 일부 자동 매도 (15:18)
        2. 안전자산 긴급 편입 (15:20)
        3. 현금 비중 확대 (15:22)
        
        추가 상담이 필요하시면 전문가가 즉시 연결됩니다.
        
        미래에셋증권 AI팀 드림
        """
        
        st.code(message_template)
        
        # ROI 계산
        st.markdown("### 💰 비즈니스 임팩트")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("고객 자산 보호", "670만원", "vs 시장 대비")
        with col2:
            st.metric("고객 만족도", "98%", "+15%p")
        with col3:
            st.metric("AUM 유지율", "94%", "업계 평균 대비 +12%p")
        with col4:
            st.metric("신규 고객 유입", "+340명", "소문 효과")
    
    def run_whale_customer_demo(self):
        """100억원 고객 맞춤 서비스"""
        st.markdown("## 🐋 초고액 고객 (100억원) 맞춤 AI 서비스")
        
        # 복잡한 포트폴리오 구성
        portfolio_composition = {
            "국내주식": 35,
            "해외주식": 25,
            "채권": 20,
            "대체투자": 10,
            "현금": 10
        }
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # 포트폴리오 구성 차트
            fig = go.Figure(data=[go.Pie(
                labels=list(portfolio_composition.keys()),
                values=list(portfolio_composition.values()),
                hole=.3
            )])
            fig.update_layout(
                title="100억원 포트폴리오 구성",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 🎯 맞춤 서비스")
            st.success("✅ 전담 AI 알고리즘")
            st.success("✅ 실시간 리스크 모니터링")
            st.success("✅ 글로벌 이벤트 대응")
            st.success("✅ 세금 최적화 전략")
            st.success("✅ 상속 플래닝 지원")
        
        # 실시간 분석 결과
        st.markdown("### 🔍 AI 심층 분석 결과")
        
        analysis_tabs = st.tabs(["리스크 분석", "수익 최적화", "세금 전략", "시장 전망"])
        
        with analysis_tabs[0]:
            st.markdown("""
            **🛡️ 포트폴리오 리스크 분석**
            
            • **전체 리스크**: 중간 수준 (VaR 1.2%)
            • **집중도 리스크**: 낮음 (최대 비중 12%)
            • **유동성 리스크**: 낮음 (3일 내 현금화 가능 85%)
            • **환율 리스크**: 보통 (헤지 비율 70%)
            
            **⚠️ 주의사항**
            - 미국 기술주 비중이 높아 나스닥 변동성에 민감
            - 중국 관련 자산의 지정학적 리스크 모니터링 필요
            """)
            
            # 리스크 히트맵
            risk_data = pd.DataFrame({
                '자산군': ['국내주식', '해외주식', '채권', '대체투자'],
                '리스크 점수': [6.5, 8.2, 3.1, 7.8],
                '비중': [35, 25, 20, 10]
            })
            
            fig = go.Figure(data=go.Scatter(
                x=risk_data['비중'],
                y=risk_data['리스크 점수'],
                mode='markers+text',
                text=risk_data['자산군'],
                textposition="top center",
                marker=dict(
                    size=risk_data['비중'],
                    color=risk_data['리스크 점수'],
                    colorscale='RdYlGn_r',
                    showscale=True
                )
            ))
            fig.update_layout(
                title="자산군별 리스크-비중 분석",
                xaxis_title="포트폴리오 비중 (%)",
                yaxis_title="리스크 점수 (1-10)",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with analysis_tabs[1]:
            st.markdown("""
            **📈 수익 최적화 전략**
            
            **현재 포트폴리오 효율성**
            • 샤프 비율: 1.34 (우수)
            • 연간 예상 수익률: 8.7%
            • 최대 낙폭: -12.3%
            
            **AI 최적화 제안**
            1. **신흥시장 채권 추가** (+1.2% 수익률 개선)
            2. **리츠 비중 확대** (인플레이션 헤지)
            3. **ESG 펀드 편입** (장기 성장성)
            4. **원자재 ETF 추가** (포트폴리오 분산)
            
            **예상 개선 효과**
            - 연간 수익률: 8.7% → 9.9%
            - 리스크 대비 수익: 1.34 → 1.47
            """)
        
        with analysis_tabs[2]:
            st.markdown("""
            **💰 세금 최적화 전략**
            
            **현재 세금 부담**
            • 배당소득세: 연 2,400만원
            • 양도소득세: 예상 3,800만원
            • 총 세금 부담: 6,200만원
            
            **AI 최적화 방안**
            1. **손익통산 활용**: -1,200만원 절세
            2. **ISA 계좌 활용**: -800만원 절세  
            3. **해외주식 직접투자**: -600만원 절세
            4. **기부금 활용**: -400만원 절세
            
            **총 절세 효과: 3,000만원** ✅
            """)
        
        with analysis_tabs[3]:
            st.markdown("""
            **🔮 향후 6개월 시장 전망**
            
            **AI 예측 결과**
            • 미국 시장: 약세 지속 (확률 65%)
            • 한국 시장: 박스권 등락 (확률 72%)
            • 중국 시장: 반등 가능성 (확률 58%)
            
            **추천 대응 전략**
            1. **현금 비중 확대** (10% → 15%)
            2. **방어주 편입** (유틸리티, 생필품)
            3. **중국 관련 자산 선별 매수**
            4. **변동성 대응 전략 강화**
            """)
    
    def run_market_prediction_demo(self):
        """시장 붕괴 예측 및 대응"""
        st.markdown("## 🚨 AI 시장 붕괴 예측 시뮬레이션")
        st.error("⚠️ **3일 전 AI 예측**: 시장 급락 확률 89% 감지")
        
        # 예측 정확도 시뮬레이션
        prediction_timeline = pd.DataFrame({
            '일자': ['D-3', 'D-2', 'D-1', 'D-Day'],
            'AI 예측 확률': [89, 93, 97, 100],
            '실제 시장 상황': ['정상', '불안', '급락 직전', '폭락']
        })
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=prediction_timeline['일자'],
            y=prediction_timeline['AI 예측 확률'],
            mode='lines+markers',
            name='AI 예측 확률',
            line=dict(color='red', width=3)
        ))
        
        fig.update_layout(
            title="AI 시장 예측 정확도 (3일간)",
            xaxis_title="시점",
            yaxis_title="급락 확률 (%)",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # 고객 자산 보호 결과
        st.markdown("### 🛡️ AI 자동 보호 결과")
        
        protection_results = pd.DataFrame({
            '구분': ['AI 보호 고객', '일반 고객', '시장 평균'],
            '손실률': [-2.1, -8.4, -12.3],
            '보호된 자산': [97.9, 91.6, 87.7]
        })
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = go.Figure(data=[
                go.Bar(
                    x=protection_results['구분'],
                    y=protection_results['손실률'],
                    marker_color=['green', 'orange', 'red']
                )
            ])
            fig.update_layout(title="손실률 비교", yaxis_title="손실률 (%)")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = go.Figure(data=[
                go.Bar(
                    x=protection_results['구분'],
                    y=protection_results['보호된 자산'],
                    marker_color=['green', 'orange', 'red']
                )
            ])
            fig.update_layout(title="자산 보호율", yaxis_title="보호율 (%)")
            st.plotly_chart(fig, use_container_width=True)
        
        # 비즈니스 임팩트
        st.markdown("### 💼 비즈니스 임팩트 시뮬레이션")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "고객 자산 보호액",
                "1,247억원",
                "전체 고객 대상"
            )
        
        with col2:
            st.metric(
                "고객 이탈 방지",
                "12,400명",
                "+89% vs 일반 증권사"
            )
        
        with col3:
            st.metric(
                "AUM 유지율",
                "97.2%",
                "업계 평균 대비 +14%p"
            )
        
        with col4:
            st.metric(
                "브랜드 가치 상승",
                "2,340억원",
                "신뢰도 기반 추정"
            )
        
        # 언론 보도 시뮬레이션
        st.markdown("### 📰 예상 언론 보도")
        
        news_simulation = """
        **📺 KBS 뉴스 9시**
        "미래에셋증권 AI, 시장 급락 3일 전 예측해 고객 자산 1,200억원 보호"
        
        **📰 매일경제**
        "AI가 구한 투자자들... 미래에셋 고객만 웃었다"
        
        **📱 네이버 금융**
        "미래에셋증권 주가 +12% 급등... AI 투자서비스 화제"
        """
        
        st.success(news_simulation)

    def _create_crash_simulation_chart(self):
        """급락 시뮬레이션 차트 생성"""
        
        # 시간대별 포트폴리오 가치 변화
        time_points = pd.date_range(
            start=datetime.now() - timedelta(hours=2),
            end=datetime.now(),
            freq='5min'
        )
        
        # AI 보호 vs 일반 포트폴리오
        ai_protected = []
        normal_portfolio = []
        market_index = []
        
        base_value = 100
        for i, time_point in enumerate(time_points):
            if i < 12:  # 정상 상황
                ai_val = base_value + random.uniform(-0.5, 0.5)
                normal_val = base_value + random.uniform(-0.5, 0.5)
                market_val = base_value + random.uniform(-0.5, 0.5)
            else:  # 급락 상황
                crash_factor = (i - 12) * 0.8
                ai_val = base_value - min(crash_factor * 0.3, 2.1)  # AI 보호
                normal_val = base_value - min(crash_factor * 0.7, 8.4)  # 일반
                market_val = base_value - min(crash_factor, 12.3)  # 시장
            
            ai_protected.append(ai_val)
            normal_portfolio.append(normal_val)
            market_index.append(market_val)
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=time_points,
            y=ai_protected,
            mode='lines',
            name='AI 보호 포트폴리오',
            line=dict(color='green', width=3)
        ))
        
        fig.add_trace(go.Scatter(
            x=time_points,
            y=normal_portfolio,
            mode='lines',
            name='일반 포트폴리오',
            line=dict(color='orange', width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=time_points,
            y=market_index,
            mode='lines',
            name='시장 지수',
            line=dict(color='red', width=2, dash='dash')
        ))
        
        fig.update_layout(
            title="실시간 포트폴리오 가치 변화",
            xaxis_title="시간",
            yaxis_title="포트폴리오 가치 (기준=100)",
            height=400,
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)

class JudgeImpressStrategy:
    """심사위원 감동 전략"""
    
    def __init__(self):
        self.judge_personas = {
            "ceo": {
                "관심사": ["비즈니스 성과", "고객 만족", "브랜드 가치"],
                "감동 포인트": "ROI와 고객 이탈 방지"
            },
            "cto": {
                "관심사": ["기술 혁신", "시스템 안정성", "확장성"],
                "감동 포인트": "실제 시스템 통합 가능성"
            },
            "head_of_digital": {
                "관심사": ["디지털 전환", "고객 경험", "운영 효율성"],
                "감동 포인트": "사용자 경험과 자동화"
            },
            "compliance_officer": {
                "관심사": ["규제 준수", "리스크 관리", "투명성"],
                "감동 포인트": "완벽한 규제 준수 체계"
            }
        }
    
    def create_judge_specific_demo(self, judge_type: str):
        """심사위원별 맞춤 데모"""
        
        if judge_type == "ceo":
            st.markdown("### 💼 CEO 관점: 비즈니스 임팩트")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                **📈 예상 비즈니스 성과 (연간)**
                
                • **신규 고객 획득**: 25,000명
                • **AUM 증가**: 1.2조원
                • **수수료 수익 증가**: 180억원
                • **고객 이탈률 감소**: -40%
                • **브랜드 가치 상승**: 5,000억원
                
                **💰 투자 대비 수익률**
                • 개발 투자: 50억원
                • 1년차 ROI: 360%
                • 3년 누적 ROI: 1,240%
                """)
            
            with col2:
                st.markdown("""
                **🏆 경쟁 우위 확보**
                
                • **업계 최초** AI 개인화 투자 서비스
                • **특허 출원** 7건 (AI 알고리즘)
                • **글로벌 확장** 가능성 (해외 법인)
                • **핀테크 어워드** 수상 예상
                
                **📊 시장 점유율**
                • 온라인 증권: 12% → 18%
                • MZ세대: 15% → 28%
                • 고액 자산가: 8% → 15%
                """)
        
        elif judge_type == "cto":
            st.markdown("### 🔧 CTO 관점: 기술적 우수성")
            
            st.code("""
            # 시스템 아키텍처 개요
            Production Environment:
            ├── Load Balancer (AWS ALB)
            ├── API Gateway (Kong)
            ├── Microservices
            │   ├── AI Analysis Service (HyperCLOVA X)
            │   ├── Portfolio Management Service
            │   ├── Real-time Data Service
            │   └── Notification Service
            ├── Database Cluster (PostgreSQL + Redis)
            ├── Message Queue (Apache Kafka)
            └── Monitoring (ELK Stack + Grafana)
            
            Scalability: 
            - Auto-scaling (50 → 500 instances)
            - 99.99% uptime SLA
            - <200ms response time
            - 1M+ concurrent users support
            """)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                **🛡️ 보안 & 인프라**
                
                • **Zero-Trust 아키텍처**
                • **End-to-End 암호화**
                • **GDPR/개인정보보호법 완전 준수**
                • **ISO 27001 인증 준비**
                • **24/7 모니터링**
                
                **⚡ 성능 최적화**
                • **CDN 활용** (응답시간 60% 단축)
                • **캐싱 전략** (Redis Cluster)
                • **비동기 처리** (Kafka + Workers)
                """)
            
            with col2:
                st.markdown("""
                **🔗 기존 시스템 통합**
                
                • **MTS 연동** (실시간 시세)
                • **CRM 연동** (고객 정보)
                • **백오피스 연동** (계좌 정보)
                • **컴플라이언스 시스템 연동**
                
                **🚀 향후 확장성**
                • **글로벌 멀티 리전** 지원
                • **블록체인 기술** 도입 준비
                • **양자 암호화** 대응
                """)

def create_presentation_flow():
    """발표용 플로우 생성"""
    
    st.markdown("# 🏆 미래에셋증권 AI Festival 2025 - 1등 전략 데모")
    
    demo = WowFactorDemo()
    judge_strategy = JudgeImpressStrategy()
    
    # 발표 플로우 선택
    presentation_mode = st.selectbox(
        "발표 모드 선택",
        [
            "📈 전체 발표 플로우",
            "📉 급락장 대응 시나리오", 
            "🐋 100억원 고객 서비스",
            "🚨 시장 예측 & 보호",
            "💼 CEO 관점 데모",
            "🔧 CTO 관점 데모"
        ]
    )
    
    if presentation_mode == "📈 전체 발표 플로우":
        st.markdown("""
        ## 🎯 발표 구성 (10분)
        
        **1분: 문제 정의**
        - 현재 투자자들의 고민
        - 기존 서비스의 한계
        
        **2분: 솔루션 소개**
        - HyperCLOVA X 기반 AI 투자 어드바이저
        - 핵심 차별화 포인트
        
        **4분: 라이브 데모**
        - 급락장 대응 시나리오
        - 실시간 포트폴리오 보호
        
        **2분: 비즈니스 임팩트**
        - ROI 계산
        - 시장 확대 효과
        
        **1분: 향후 계획**
        - 상용화 로드맵
        - 글로벌 확장 계획
        """)
        
        if st.button("🚀 전체 데모 시작", type="primary"):
            demo.run_market_prediction_demo()
            st.markdown("---")
            demo.run_crisis_management_demo()
    
    elif presentation_mode == "📉 급락장 대응 시나리오":
        demo.run_crisis_management_demo()
    
    elif presentation_mode == "🐋 100억원 고객 서비스":
        demo.run_whale_customer_demo()
    
    elif presentation_mode == "🚨 시장 예측 & 보호":
        demo.run_market_prediction_demo()
    
    elif presentation_mode == "💼 CEO 관점 데모":
        judge_strategy.create_judge_specific_demo("ceo")
    
    elif presentation_mode == "🔧 CTO 관점 데모":
        judge_strategy.create_judge_specific_demo("cto")

if __name__ == "__main__":
    create_presentation_flow()
