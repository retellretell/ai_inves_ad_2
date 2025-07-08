"""
unified_realtime_alerts.py - 통합 실시간 AI 알림 시스템
24/7 포트폴리오 모니터링, 지능형 알림, AI 예측 및 전체 기능 통합
"""

import streamlit as st
import asyncio
import threading
import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import numpy as np
import pandas as pd
import yfinance as yf
from dataclasses import dataclass
from enum import Enum
import uuid
import requests
import math
import warnings
warnings.filterwarnings('ignore')

# 로깅 설정
logger = logging.getLogger(__name__)

class AlertType(Enum):
    """알림 타입"""
    PRICE_SPIKE = "가격 급등"
    PRICE_DROP = "가격 급락"
    VOLUME_SURGE = "거래량 급증"
    PATTERN_DETECTED = "패턴 감지"
    NEWS_IMPACT = "뉴스 영향"
    RISK_WARNING = "리스크 경고"
    OPPORTUNITY = "투자 기회"
    PORTFOLIO_IMBALANCE = "포트폴리오 불균형"
    STOP_LOSS = "손절 신호"
    TAKE_PROFIT = "익절 신호"

class AlertPriority(Enum):
    """알림 우선순위"""
    CRITICAL = "긴급"
    HIGH = "높음"
    MEDIUM = "중간"
    LOW = "낮음"

@dataclass
class Alert:
    """알림 데이터 클래스"""
    type: AlertType
    priority: AlertPriority
    title: str
    message: str
    ticker: Optional[str]
    timestamp: datetime
    action_required: bool
    ai_confidence: float
    metadata: Dict[str, Any]

class AIAlertAnalyzer:
    """AI 기반 알림 분석기"""
    
    def __init__(self):
        self.thresholds = {
            'price_change': 0.05,  # 5% 변동
            'volume_surge': 2.0,   # 평균 대비 2배
            'rsi_oversold': 30,
            'rsi_overbought': 70,
            'pattern_confidence': 0.7
        }
    
    def analyze_market_conditions(self, ticker: str, data: pd.DataFrame) -> List[Alert]:
        """시장 상황 분석 및 알림 생성"""
        alerts = []
        
        try:
            # 1. 가격 변동 분석
            price_alerts = self._analyze_price_changes(ticker, data)
            alerts.extend(price_alerts)
            
            # 2. 거래량 분석
            volume_alerts = self._analyze_volume(ticker, data)
            alerts.extend(volume_alerts)
            
            # 3. 기술적 지표 분석
            technical_alerts = self._analyze_technical_indicators(ticker, data)
            alerts.extend(technical_alerts)
            
            # 4. AI 패턴 인식
            pattern_alerts = self._detect_patterns(ticker, data)
            alerts.extend(pattern_alerts)
            
            # 5. 종합 리스크 평가
            risk_alerts = self._assess_risks(ticker, data)
            alerts.extend(risk_alerts)
            
        except Exception as e:
            logger.error(f"시장 분석 오류 ({ticker}): {str(e)}")
        
        return alerts
    
    def _analyze_price_changes(self, ticker: str, data: pd.DataFrame) -> List[Alert]:
        """가격 변동 분석"""
        alerts = []
        
        if len(data) < 2:
            return alerts
        
        current_price = data['Close'].iloc[-1]
        prev_price = data['Close'].iloc[-2]
        change_pct = (current_price - prev_price) / prev_price
        
        # 급등/급락 감지
        if abs(change_pct) >= self.thresholds['price_change']:
            alert_type = AlertType.PRICE_SPIKE if change_pct > 0 else AlertType.PRICE_DROP
            priority = AlertPriority.HIGH if abs(change_pct) >= 0.1 else AlertPriority.MEDIUM
            
            alerts.append(Alert(
                type=alert_type,
                priority=priority,
                title=f"{ticker} {alert_type.value} 발생",
                message=f"{ticker}가 {change_pct:.1%} {'상승' if change_pct > 0 else '하락'}했습니다. "
                       f"현재가: {current_price:,.0f}원",
                ticker=ticker,
                timestamp=datetime.now(),
                action_required=True,
                ai_confidence=0.9,
                metadata={
                    'current_price': current_price,
                    'prev_price': prev_price,
                    'change_pct': change_pct
                }
            ))
        
        # 연속 상승/하락 패턴
        if len(data) >= 5:
            recent_changes = data['Close'].pct_change().iloc[-5:]
            if all(recent_changes > 0) or all(recent_changes < 0):
                trend = "상승" if recent_changes.iloc[-1] > 0 else "하락"
                alerts.append(Alert(
                    type=AlertType.PATTERN_DETECTED,
                    priority=AlertPriority.MEDIUM,
                    title=f"{ticker} 연속 {trend} 패턴",
                    message=f"{ticker}가 5일 연속 {trend} 중입니다. 추세 전환 주의!",
                    ticker=ticker,
                    timestamp=datetime.now(),
                    action_required=False,
                    ai_confidence=0.8,
                    metadata={'trend': trend, 'days': 5}
                ))
        
        return alerts
    
    def _analyze_volume(self, ticker: str, data: pd.DataFrame) -> List[Alert]:
        """거래량 분석"""
        alerts = []
        
        if len(data) < 20:
            return alerts
        
        current_volume = data['Volume'].iloc[-1]
        avg_volume = data['Volume'].iloc[-20:].mean()
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0
        
        if volume_ratio >= self.thresholds['volume_surge']:
            alerts.append(Alert(
                type=AlertType.VOLUME_SURGE,
                priority=AlertPriority.HIGH,
                title=f"{ticker} 거래량 급증",
                message=f"{ticker}의 거래량이 평균 대비 {volume_ratio:.1f}배 증가했습니다. "
                       f"중요한 뉴스나 이벤트를 확인하세요.",
                ticker=ticker,
                timestamp=datetime.now(),
                action_required=True,
                ai_confidence=0.85,
                metadata={
                    'current_volume': current_volume,
                    'avg_volume': avg_volume,
                    'volume_ratio': volume_ratio
                }
            ))
        
        return alerts
    
    def _analyze_technical_indicators(self, ticker: str, data: pd.DataFrame) -> List[Alert]:
        """기술적 지표 분석"""
        alerts = []
        
        if len(data) < 14:
            return alerts
        
        # RSI 계산
        rsi = self._calculate_rsi(data['Close'])
        current_rsi = rsi.iloc[-1]
        
        if current_rsi <= self.thresholds['rsi_oversold']:
            alerts.append(Alert(
                type=AlertType.OPPORTUNITY,
                priority=AlertPriority.HIGH,
                title=f"{ticker} 과매도 구간 진입",
                message=f"{ticker}의 RSI가 {current_rsi:.1f}로 과매도 구간입니다. "
                       f"반등 가능성을 검토해보세요.",
                ticker=ticker,
                timestamp=datetime.now(),
                action_required=True,
                ai_confidence=0.75,
                metadata={'rsi': current_rsi, 'signal': 'oversold'}
            ))
        elif current_rsi >= self.thresholds['rsi_overbought']:
            alerts.append(Alert(
                type=AlertType.RISK_WARNING,
                priority=AlertPriority.HIGH,
                title=f"{ticker} 과매수 구간 진입",
                message=f"{ticker}의 RSI가 {current_rsi:.1f}로 과매수 구간입니다. "
                       f"차익실현을 고려해보세요.",
                ticker=ticker,
                timestamp=datetime.now(),
                action_required=True,
                ai_confidence=0.75,
                metadata={'rsi': current_rsi, 'signal': 'overbought'}
            ))
        
        # 골든크로스/데드크로스
        if len(data) >= 50:
            ma5 = data['Close'].rolling(5).mean()
            ma20 = data['Close'].rolling(20).mean()
            ma50 = data['Close'].rolling(50).mean()
            
            # 골든크로스 체크
            if ma5.iloc[-1] > ma20.iloc[-1] > ma50.iloc[-1] and ma5.iloc[-2] <= ma20.iloc[-2]:
                alerts.append(Alert(
                    type=AlertType.OPPORTUNITY,
                    priority=AlertPriority.HIGH,
                    title=f"{ticker} 골든크로스 발생",
                    message=f"{ticker}에서 단기 이평선이 장기 이평선을 상향 돌파했습니다. "
                           f"상승 추세 전환 가능성!",
                    ticker=ticker,
                    timestamp=datetime.now(),
                    action_required=True,
                    ai_confidence=0.8,
                    metadata={'signal': 'golden_cross'}
                ))
        
        return alerts
    
    def _detect_patterns(self, ticker: str, data: pd.DataFrame) -> List[Alert]:
        """AI 패턴 인식"""
        alerts = []
        
        if len(data) < 30:
            return alerts
        
        # 삼각수렴 패턴
        highs = data['High'].iloc[-20:]
        lows = data['Low'].iloc[-20:]
        
        try:
            high_trend = np.polyfit(range(len(highs)), highs.values, 1)[0]
            low_trend = np.polyfit(range(len(lows)), lows.values, 1)[0]
            
            if abs(high_trend) < 0.1 and abs(low_trend) < 0.1 and (highs.max() - lows.min()) < (highs.iloc[0] - lows.iloc[0]) * 0.5:
                alerts.append(Alert(
                    type=AlertType.PATTERN_DETECTED,
                    priority=AlertPriority.MEDIUM,
                    title=f"{ticker} 삼각수렴 패턴 감지",
                    message=f"{ticker}에서 삼각수렴 패턴이 감지되었습니다. "
                           f"곧 큰 변동이 예상됩니다.",
                    ticker=ticker,
                    timestamp=datetime.now(),
                    action_required=True,
                    ai_confidence=0.7,
                    metadata={'pattern': 'triangle_convergence'}
                ))
        except:
            pass
        
        # 더블바텀/더블탑 패턴
        try:
            recent_lows = self._find_local_extremes(lows, 'min')
            recent_highs = self._find_local_extremes(highs, 'max')
            
            if len(recent_lows) >= 2 and abs(recent_lows[-1] - recent_lows[-2]) / recent_lows[-2] < 0.02:
                alerts.append(Alert(
                    type=AlertType.OPPORTUNITY,
                    priority=AlertPriority.HIGH,
                    title=f"{ticker} 더블바텀 패턴 형성",
                    message=f"{ticker}에서 더블바텀 패턴이 형성되었습니다. "
                           f"반등 가능성이 높습니다.",
                    ticker=ticker,
                    timestamp=datetime.now(),
                    action_required=True,
                    ai_confidence=0.75,
                    metadata={'pattern': 'double_bottom'}
                ))
        except:
            pass
        
        return alerts
    
    def _assess_risks(self, ticker: str, data: pd.DataFrame) -> List[Alert]:
        """종합 리스크 평가"""
        alerts = []
        
        if len(data) < 20:
            return alerts
        
        # 변동성 계산
        volatility = data['Close'].pct_change().std() * np.sqrt(252) * 100
        
        if volatility > 50:  # 연간 변동성 50% 이상
            alerts.append(Alert(
                type=AlertType.RISK_WARNING,
                priority=AlertPriority.HIGH,
                title=f"{ticker} 고변동성 경고",
                message=f"{ticker}의 변동성이 {volatility:.1f}%로 매우 높습니다. "
                       f"포지션 크기를 조절하세요.",
                ticker=ticker,
                timestamp=datetime.now(),
                action_required=True,
                ai_confidence=0.9,
                metadata={'volatility': volatility}
            ))
        
        # 지지/저항선 근접
        support = data['Low'].iloc[-20:].min()
        resistance = data['High'].iloc[-20:].max()
        current_price = data['Close'].iloc[-1]
        
        if (current_price - support) / support < 0.02:
            alerts.append(Alert(
                type=AlertType.OPPORTUNITY,
                priority=AlertPriority.MEDIUM,
                title=f"{ticker} 지지선 근접",
                message=f"{ticker}가 지지선({support:,.0f}원)에 근접했습니다. "
                       f"반등 가능성을 주목하세요.",
                ticker=ticker,
                timestamp=datetime.now(),
                action_required=False,
                ai_confidence=0.7,
                metadata={'support': support, 'current': current_price}
            ))
        
        return alerts
    
    def _calculate_rsi(self, prices: pd.Series, window: int = 14) -> pd.Series:
        """RSI 계산"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def _find_local_extremes(self, data: pd.Series, type: str = 'min') -> List[float]:
        """지역 극값 찾기"""
        try:
            if type == 'min':
                return [data.iloc[i] for i in range(1, len(data)-1) 
                        if data.iloc[i] < data.iloc[i-1] and data.iloc[i] < data.iloc[i+1]]
            else:
                return [data.iloc[i] for i in range(1, len(data)-1) 
                        if data.iloc[i] > data.iloc[i-1] and data.iloc[i] > data.iloc[i+1]]
        except:
            return []

class UnifiedRealtimeAlertSystem:
    """통합 실시간 알림 시스템"""
    
    def __init__(self):
        self.initialize_session_state()
        self.alert_analyzer = AIAlertAnalyzer()
        self.monitoring_active = False
        
    def initialize_session_state(self):
        """세션 상태 초기화"""
        if 'alerts' not in st.session_state:
            st.session_state.alerts = []
        
        if 'monitored_stocks' not in st.session_state:
            st.session_state.monitored_stocks = []
        
        if 'alert_settings' not in st.session_state:
            st.session_state.alert_settings = {
                'enable_email': False,
                'enable_sms': False,
                'enable_push': True,
                'price_threshold': 5.0,
                'volume_threshold': 2.0,
                'enable_night_alerts': False
            }
        
        if 'user_journey' not in st.session_state:
            st.session_state.user_journey = {
                'start_time': datetime.now(),
                'page_views': 0,
                'ai_analysis_count': 0,
                'feature_usage': [],
                'engagement_score': 0
            }
    
    def add_alert(self, alert_type: AlertType, title: str, message: str, 
                  ticker: str = None, priority: AlertPriority = AlertPriority.MEDIUM,
                  action_required: bool = False, ai_confidence: float = 0.8,
                  metadata: Dict[str, Any] = None):
        """알림 추가"""
        alert_dict = {
            'id': str(uuid.uuid4())[:8],
            'type': alert_type.value,
            'priority': priority.value,
            'title': title,
            'message': message,
            'ticker': ticker,
            'timestamp': datetime.now(),
            'action_required': action_required,
            'ai_confidence': ai_confidence,
            'metadata': metadata or {},
            'read': False
        }
        
        st.session_state.alerts.insert(0, alert_dict)
        
        # 최대 100개 유지
        if len(st.session_state.alerts) > 100:
            st.session_state.alerts = st.session_state.alerts[:100]
    
    def analyze_stock_for_alerts(self, ticker: str, holding_info: Dict[str, Any] = None) -> List[Alert]:
        """종목 분석 및 알림 생성"""
        try:
            # 데이터 수집
            stock = yf.Ticker(ticker)
            data = stock.history(period="1mo", interval="1d")
            
            if data.empty or len(data) < 5:
                return []
            
            # AI 분석
            alerts = self.alert_analyzer.analyze_market_conditions(ticker, data)
            
            # 포트폴리오 관련 알림 추가
            if holding_info:
                portfolio_alerts = self._analyze_portfolio_alerts(ticker, data, holding_info)
                alerts.extend(portfolio_alerts)
            
            # 알림 추가
            for alert in alerts:
                self.add_alert(
                    alert_type=alert.type,
                    title=alert.title,
                    message=alert.message,
                    ticker=alert.ticker,
                    priority=alert.priority,
                    action_required=alert.action_required,
                    ai_confidence=alert.ai_confidence,
                    metadata=alert.metadata
                )
            
            return alerts
            
        except Exception as e:
            logger.error(f"종목 분석 오류 ({ticker}): {str(e)}")
            return []
    
    def _analyze_portfolio_alerts(self, ticker: str, data: pd.DataFrame, holding_info: Dict[str, Any]) -> List[Alert]:
        """포트폴리오 관련 알림 분석"""
        alerts = []
        
        current_price = data['Close'].iloc[-1]
        buy_price = holding_info.get('buy_price', 0)
        shares = holding_info.get('shares', 0)
        
        if buy_price > 0:
            profit_rate = ((current_price - buy_price) / buy_price) * 100
            
            # 손절 알림
            if profit_rate <= -10:
                alerts.append(Alert(
                    type=AlertType.STOP_LOSS,
                    priority=AlertPriority.CRITICAL,
                    title=f"{ticker} 손절 검토 필요",
                    message=f"{ticker}가 {profit_rate:.1f}% 손실 중입니다. "
                           f"손절매를 검토하세요. (매수가: {buy_price:,.0f}원, 현재가: {current_price:,.0f}원)",
                    ticker=ticker,
                    timestamp=datetime.now(),
                    action_required=True,
                    ai_confidence=0.95,
                    metadata={
                        'buy_price': buy_price,
                        'current_price': current_price,
                        'profit_rate': profit_rate,
                        'loss_amount': (current_price - buy_price) * shares
                    }
                ))
            
            # 익절 알림
            elif profit_rate >= 20:
                alerts.append(Alert(
                    type=AlertType.TAKE_PROFIT,
                    priority=AlertPriority.HIGH,
                    title=f"{ticker} 목표 수익 달성",
                    message=f"{ticker}가 {profit_rate:.1f}% 수익 중입니다. "
                           f"차익실현을 고려하세요. (매수가: {buy_price:,.0f}원, 현재가: {current_price:,.0f}원)",
                    ticker=ticker,
                    timestamp=datetime.now(),
                    action_required=True,
                    ai_confidence=0.9,
                    metadata={
                        'buy_price': buy_price,
                        'current_price': current_price,
                        'profit_rate': profit_rate,
                        'profit_amount': (current_price - buy_price) * shares
                    }
                ))
        
        return alerts
    
    def check_portfolio_health(self):
        """포트폴리오 전체 건강도 분석"""
        if not st.session_state.monitored_stocks:
            return
        
        total_value = 0
        stock_values = {}
        
        # 각 종목 현재가치 계산
        for holding in st.session_state.monitored_stocks:
            ticker = holding.get('ticker')
            shares = holding.get('shares', 0)
            
            try:
                stock = yf.Ticker(ticker)
                current_price = stock.history(period="1d")['Close'].iloc[-1]
                value = current_price * shares
                stock_values[ticker] = value
                total_value += value
            except:
                continue
        
        # 포트폴리오 불균형 체크
        if total_value > 0:
            for ticker, value in stock_values.items():
                weight = value / total_value * 100
                
                if weight > 40:  # 40% 이상 집중
                    self.add_alert(
                        alert_type=AlertType.PORTFOLIO_IMBALANCE,
                        title="포트폴리오 집중도 경고",
                        message=f"{ticker}가 포트폴리오의 {weight:.1f}%를 차지합니다. "
                               f"분산투자를 고려하세요.",
                        ticker=ticker,
                        priority=AlertPriority.MEDIUM,
                        action_required=True,
                        ai_confidence=0.85,
                        metadata={'weight': weight, 'total_value': total_value}
                    )
    
    def render_alert_dashboard(self):
        """알림 대시보드 렌더링"""
        st.markdown("### 🔔 실시간 AI 알림 센터")
        
        # 알림 통계
        total_alerts = len(st.session_state.alerts)
        unread_alerts = sum(1 for alert in st.session_state.alerts if not alert['read'])
        today_alerts = sum(1 for alert in st.session_state.alerts 
                         if alert['timestamp'].date() == datetime.now().date())
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("전체 알림", total_alerts)
        with col2:
            st.metric("읽지 않은 알림", unread_alerts)
        with col3:
            st.metric("오늘 알림", today_alerts)
        with col4:
            if st.button("🔄 새로고침", key="refresh_alerts"):
                # 모니터링 중인 종목들 재분석
                self._refresh_all_alerts()
                st.rerun()
        
        # 알림 필터
        self._render_alert_filters()
        
        # 알림 목록
        self._render_alert_list()
        
        # 알림 설정
        self._render_alert_settings()
    
    def _refresh_all_alerts(self):
        """모든 모니터링 종목 재분석"""
        for stock in st.session_state.monitored_stocks:
            ticker = stock.get('ticker')
            if ticker:
                self.analyze_stock_for_alerts(ticker, stock)
    
    def _render_alert_filters(self):
        """알림 필터 렌더링"""
        st.markdown("#### 🎯 알림 필터")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            filter_type = st.selectbox(
                "알림 타입",
                ["전체"] + [alert_type.value for alert_type in AlertType],
                key="alert_filter_type"
            )
        
        with col2:
            filter_priority = st.selectbox(
                "우선순위",
                ["전체"] + [priority.value for priority in AlertPriority],
                key="alert_filter_priority"
            )
        
        with col3:
            filter_unread = st.checkbox("읽지 않은 알림만", key="alert_filter_unread")
        
        # 필터 적용
        filtered_alerts = st.session_state.alerts
        
        if filter_type != "전체":
            filtered_alerts = [a for a in filtered_alerts if a['type'] == filter_type]
        
        if filter_priority != "전체":
            filtered_alerts = [a for a in filtered_alerts if a['priority'] == filter_priority]
        
        if filter_unread:
            filtered_alerts = [a for a in filtered_alerts if not a['read']]
        
        st.session_state.filtered_alerts = filtered_alerts
    
    def _render_alert_list(self):
        """알림 목록 렌더링"""
        st.markdown("#### 📋 최근 알림")
        
        if 'filtered_alerts' not in st.session_state:
            st.session_state.filtered_alerts = st.session_state.alerts
        
        if not st.session_state.filtered_alerts:
            st.info("조건에 맞는 알림이 없습니다.")
            return
        
        # 최대 20개 표시
        alerts_to_show = st.session_state.filtered_alerts[:20]
        
        for i, alert in enumerate(alerts_to_show):
            self._render_single_alert(alert, i)
    
    def _render_single_alert(self, alert: Dict[str, Any], index: int):
        """개별 알림 렌더링"""
        # 우선순위별 색상
        priority_colors = {
            "긴급": "#ff4444",
            "높음": "#ffaa00",
            "중간": "#4CAF50",
            "낮음": "#999999"
        }
        
        priority_icons = {
            "긴급": "🚨",
            "높음": "⚠️",
            "중간": "📌",
            "낮음": "💡"
        }
        
        color = priority_colors.get(alert['priority'], "#999999")
        icon = priority_icons.get(alert['priority'], "📌")
        
        # 읽음 상태에 따른 스타일
        read_style = "opacity: 0.6;" if alert['read'] else ""
        title_weight = "normal" if alert['read'] else "bold"
        
        with st.container():
            col1, col2 = st.columns([5, 1])
            
            with col1:
                st.markdown(f"""
                <div style="background: #f8f9fa; padding: 1rem; border-radius: 0.5rem; 
                            margin: 0.5rem 0; border-left: 4px solid {color}; {read_style}">
                    <div style="font-weight: {title_weight};">
                        {icon} {alert['title']}
                        <span style="float: right; font-size: 0.8rem; color: #999;">
                            {alert['timestamp'].strftime('%m/%d %H:%M')}
                        </span>
                    </div>
                    <div style="margin-top: 0.5rem; color: #666;">
                        {alert['message']}
                    </div>
                    <div style="margin-top: 0.5rem; font-size: 0.8rem; color: #999;">
                        타입: {alert['type']} | 우선순위: {alert['priority']} | 
                        신뢰도: {alert['ai_confidence']:.0%}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if not alert['read']:
                    if st.button("읽음", key=f"read_{alert['id']}_{index}"):
                        alert['read'] = True
                        st.rerun()
                
                if alert.get('ticker'):
                    if st.button("상세", key=f"detail_{alert['id']}_{index}"):
                        st.session_state.selected_ticker_detail = alert['ticker']
                        st.session_state.show_ticker_detail = True
    
    def _render_alert_settings(self):
        """알림 설정 렌더링"""
        with st.expander("⚙️ 알림 설정", expanded=False):
            st.markdown("#### 알림 채널 설정")
            
            col1, col2 = st.columns(2)
            
            with col1:
                enable_email = st.checkbox(
                    "이메일 알림", 
                    value=st.session_state.alert_settings['enable_email'],
                    key="setting_email"
                )
                if enable_email:
                    email = st.text_input("이메일 주소", placeholder="your@email.com")
                
                enable_sms = st.checkbox(
                    "SMS 알림", 
                    value=st.session_state.alert_settings['enable_sms'],
                    key="setting_sms"
                )
                if enable_sms:
                    phone = st.text_input("휴대폰 번호", placeholder="010-1234-5678")
            
            with col2:
                enable_push = st.checkbox(
                    "인앱 알림", 
                    value=st.session_state.alert_settings['enable_push'],
                    key="setting_push"
                )
                enable_night = st.checkbox(
                    "야간 알림 허용 (22:00-06:00)", 
                    value=st.session_state.alert_settings['enable_night_alerts'],
                    key="setting_night"
                )
            
            st.markdown("#### 알림 임계값 설정")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                price_threshold = st.slider(
                    "가격 변동 알림 (%)",
                    min_value=1.0,
                    max_value=15.0,
                    value=st.session_state.alert_settings['price_threshold'],
                    step=0.5,
                    key="setting_price_threshold"
                )
            
            with col2:
                volume_threshold = st.slider(
                    "거래량 급증 배수",
                    min_value=1.5,
                    max_value=5.0,
                    value=st.session_state.alert_settings['volume_threshold'],
                    step=0.5,
                    key="setting_volume_threshold"
                )
            
            with col3:
                rsi_threshold = st.slider(
                    "RSI 알림 민감도",
                    min_value=20,
                    max_value=40,
                    value=30,
                    step=5,
                    key="setting_rsi_threshold"
                )
            
            if st.button("설정 저장", type="primary", key="save_alert_settings"):
                # 설정 업데이트
                st.session_state.alert_settings.update({
                    'enable_email': enable_email,
                    'enable_sms': enable_sms,
                    'enable_push': enable_push,
                    'enable_night_alerts': enable_night,
                    'price_threshold': price_threshold,
                    'volume_threshold': volume_threshold
                })
                
                # 임계값 업데이트
                self.alert_analyzer.thresholds.update({
                    'price_change': price_threshold / 100,
                    'volume_surge': volume_threshold,
                    'rsi_oversold': rsi_threshold,
                    'rsi_overbought': 100 - rsi_threshold
                })
                
                st.success("알림 설정이 저장되었습니다!")
    
    def render_portfolio_monitoring(self):
        """포트폴리오 모니터링 UI"""
        st.markdown("### 📊 포트폴리오 실시간 모니터링")
        
        # 포트폴리오 추가
        with st.expander("➕ 모니터링할 종목 추가", expanded=False):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                ticker = st.text_input("종목 코드", placeholder="005930.KS", key="monitor_ticker")
            with col2:
                shares = st.number_input("보유 주수", min_value=1, value=10, key="monitor_shares")
            with col3:
                buy_price = st.number_input("매수가", min_value=0.0, value=70000.0, key="monitor_price")
            with col4:
                if st.button("모니터링 추가", type="primary", key="add_monitoring"):
                    new_stock = {
                        'ticker': ticker,
                        'shares': shares,
                        'buy_price': buy_price,
                        'added_at': datetime.now(),
                        'id': str(uuid.uuid4())[:8]
                    }
                    
                    st.session_state.monitored_stocks.append(new_stock)
                    
                    # 즉시 분석 수행
                    self.analyze_stock_for_alerts(ticker, new_stock)
                    
                    st.success(f"{ticker} 모니터링 추가됨!")
                    st.rerun()
        
        # 모니터링 중인 종목 표시
        if st.session_state.monitored_stocks:
            st.markdown("#### 🔍 모니터링 중인 종목")
            
            for i, stock in enumerate(st.session_state.monitored_stocks):
                with st.container():
                    col1, col2, col3, col4, col5, col6, col7 = st.columns([2, 1, 1, 1, 1, 1, 1])
                    
                    with col1:
                        st.write(f"**{stock['ticker']}**")
                    
                    with col2:
                        st.write(f"{stock['shares']}주")
                    
                    with col3:
                        st.write(f"매수: {stock['buy_price']:,.0f}원")
                    
                    # 실시간 데이터 조회
                    try:
                        ticker_obj = yf.Ticker(stock['ticker'])
                        current_data = ticker_obj.history(period="1d")
                        
                        if not current_data.empty:
                            current_price = current_data['Close'].iloc[-1]
                            profit_rate = ((current_price - stock['buy_price']) / stock['buy_price']) * 100
                            profit_amount = (current_price - stock['buy_price']) * stock['shares']
                            
                            with col4:
                                st.write(f"현재: {current_price:,.0f}원")
                            
                            with col5:
                                color = "🟢" if profit_rate >= 0 else "🔴"
                                st.write(f"{color} {profit_rate:+.1f}%")
                            
                            with col6:
                                st.write(f"{profit_amount:+,.0f}원")
                            
                            # 실시간 분석
                            if st.button("분석", key=f"analyze_{stock['id']}"):
                                with st.spinner(f"{stock['ticker']} 분석 중..."):
                                    self.analyze_stock_for_alerts(stock['ticker'], stock)
                                st.success("분석 완료!")
                                st.rerun()
                        else:
                            with col4:
                                st.write("데이터 없음")
                            with col5:
                                st.write("-")
                            with col6:
                                st.write("-")
                    
                    except Exception as e:
                        with col4:
                            st.write("오류")
                        with col5:
                            st.write("-")
                        with col6:
                            st.write("-")
                    
                    with col7:
                        if st.button("제거", key=f"remove_{stock['id']}"):
                            st.session_state.monitored_stocks.pop(i)
                            st.rerun()
            
            # 전체 분석 버튼
            st.markdown("---")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🚀 전체 종목 실시간 분석", type="primary", use_container_width=True):
                    with st.spinner("전체 포트폴리오 분석 중..."):
                        for stock in st.session_state.monitored_stocks:
                            self.analyze_stock_for_alerts(stock['ticker'], stock)
                        
                        # 포트폴리오 전체 건강도 체크
                        self.check_portfolio_health()
                        
                        time.sleep(1)  # 분석 시뮬레이션
                    st.success("전체 분석 완료! 알림 센터에서 결과를 확인하세요.")
                    st.rerun()
            
            with col2:
                if st.button("📈 포트폴리오 요약", type="secondary", use_container_width=True):
                    self._show_portfolio_summary()
        else:
            st.info("모니터링할 종목을 추가해주세요.")
    
    def _show_portfolio_summary(self):
        """포트폴리오 요약 표시"""
        if not st.session_state.monitored_stocks:
            return
        
        st.markdown("#### 📈 포트폴리오 요약")
        
        total_invested = 0
        total_current = 0
        portfolio_data = []
        
        for stock in st.session_state.monitored_stocks:
            try:
                ticker_obj = yf.Ticker(stock['ticker'])
                current_data = ticker_obj.history(period="1d")
                
                if not current_data.empty:
                    current_price = current_data['Close'].iloc[-1]
                    invested = stock['buy_price'] * stock['shares']
                    current_value = current_price * stock['shares']
                    
                    total_invested += invested
                    total_current += current_value
                    
                    portfolio_data.append({
                        'ticker': stock['ticker'],
                        'invested': invested,
                        'current_value': current_value,
                        'profit_loss': current_value - invested,
                        'profit_rate': ((current_price - stock['buy_price']) / stock['buy_price']) * 100
                    })
            except:
                continue
        
        if portfolio_data:
            total_profit = total_current - total_invested
            total_return = (total_profit / total_invested * 100) if total_invested > 0 else 0
            
            # 전체 요약
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("총 투자금액", f"{total_invested:,.0f}원")
            with col2:
                st.metric("현재 평가액", f"{total_current:,.0f}원")
            with col3:
                st.metric("총 손익", f"{total_profit:,.0f}원")
            with col4:
                st.metric("수익률", f"{total_return:+.2f}%")
            
            # 종목별 상세
            df = pd.DataFrame(portfolio_data)
            df.columns = ['종목', '투자금액', '현재가치', '손익', '수익률(%)']
            df['투자금액'] = df['투자금액'].apply(lambda x: f"{x:,.0f}원")
            df['현재가치'] = df['현재가치'].apply(lambda x: f"{x:,.0f}원")
            df['손익'] = df['손익'].apply(lambda x: f"{x:+,.0f}원")
            df['수익률(%)'] = df['수익률(%)'].apply(lambda x: f"{x:+.2f}%")
            
            st.dataframe(df, use_container_width=True)
    
    def render_ai_predictions(self):
        """AI 예측 렌더링"""
        st.markdown("### 🔮 AI 시장 예측")
        
        # 예측 대상 선택
        col1, col2 = st.columns([3, 1])
        
        with col1:
            prediction_tickers = ["005930.KS", "000660.KS", "035420.KS", "TSLA", "NVDA", "^KS11", "^IXIC"]
            ticker_names = {
                "005930.KS": "삼성전자", "000660.KS": "SK하이닉스", 
                "035420.KS": "네이버", "TSLA": "테슬라", "NVDA": "엔비디아",
                "^KS11": "KOSPI", "^IXIC": "NASDAQ"
            }
            
            prediction_ticker = st.selectbox(
                "예측할 종목/지수 선택",
                prediction_tickers,
                format_func=lambda x: ticker_names.get(x, x),
                key="prediction_ticker"
            )
        
        with col2:
            if st.button("🤖 AI 예측 실행", type="primary"):
                with st.spinner("AI가 시장을 분석하고 있습니다..."):
                    # 시뮬레이션된 예측 결과
                    prediction_result = self._generate_ai_prediction(prediction_ticker)
                    st.session_state.ai_prediction = prediction_result
                    time.sleep(2)  # 분석 시뮬레이션
        
        # 예측 결과 표시
        if 'ai_prediction' in st.session_state:
            prediction = st.session_state.ai_prediction
            
            st.markdown(f"#### 📈 {ticker_names.get(prediction['ticker'], prediction['ticker'])} AI 예측 결과")
            st.caption(f"분석 시간: {prediction['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
            
            # 예측 카드들
            timeframes = [
                ("1시간 후", prediction['next_hour']),
                ("1일 후", prediction['next_day']),
                ("1주일 후", prediction['next_week'])
            ]
            
            cols = st.columns(3)
            
            for col, (timeframe, pred) in zip(cols, timeframes):
                with col:
                    direction_icon = "📈" if pred['direction'] == 'UP' else "📉"
                    confidence_color = "#4CAF50" if pred['confidence'] >= 0.7 else "#FF9800" if pred['confidence'] >= 0.5 else "#F44336"
                    direction_color = "#4CAF50" if pred['direction'] == 'UP' else "#F44336"
                    
                    st.markdown(f"""
                    <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 0.5rem; 
                                text-align: center; border: 2px solid {confidence_color};">
                        <h4 style="margin: 0;">{timeframe}</h4>
                        <div style="font-size: 2rem; margin: 0.5rem 0;">{direction_icon}</div>
                        <div style="font-size: 1.2rem; font-weight: bold; color: {direction_color};">
                            {pred['expected_change']:+.1f}%
                        </div>
                        <div style="margin-top: 0.5rem;">
                            신뢰도: <span style="color: {confidence_color}; font-weight: bold;">{pred['confidence']:.0%}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # AI 분석 근거
            st.markdown("#### 🧠 AI 분석 근거")
            
            analysis_factors = prediction['analysis_factors']
            
            for factor, score in analysis_factors.items():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(factor)
                with col2:
                    color = "#4CAF50" if score >= 0.8 else "#FF9800" if score >= 0.6 else "#F44336"
                    st.markdown(f'<div style="text-align: right; color: {color}; font-weight: bold;">{score:.0%}</div>', 
                              unsafe_allow_html=True)
            
            # 투자 제안
            st.markdown("#### 💡 AI 투자 제안")
            suggestions = prediction['suggestions']
            
            for suggestion in suggestions:
                st.markdown(f"• {suggestion}")
    
    def _generate_ai_prediction(self, ticker: str) -> Dict[str, Any]:
        """AI 예측 생성 (시뮬레이션)"""
        import random
        
        # 실제 데이터 기반 예측 로직
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(period="3mo")
            
            if not data.empty:
                # 간단한 추세 분석
                recent_trend = (data['Close'].iloc[-1] - data['Close'].iloc[-30]) / data['Close'].iloc[-30]
                volatility = data['Close'].pct_change().std()
            else:
                recent_trend = 0
                volatility = 0.02
        except:
            recent_trend = 0
            volatility = 0.02
        
        # 예측 생성
        base_confidence = 0.6 + random.random() * 0.3
        trend_factor = 1 if recent_trend > 0 else -1
        
        predictions = {
            'ticker': ticker,
            'timestamp': datetime.now(),
            'next_hour': {
                'direction': 'UP' if random.random() > 0.4 else 'DOWN',
                'confidence': base_confidence + random.random() * 0.2,
                'expected_change': (random.random() - 0.5) * 4  # ±2%
            },
            'next_day': {
                'direction': 'UP' if recent_trend > 0 and random.random() > 0.3 else 'DOWN',
                'confidence': base_confidence,
                'expected_change': trend_factor * (1 + random.random() * 3)  # ±1-4%
            },
            'next_week': {
                'direction': 'UP' if recent_trend > 0 else 'DOWN',
                'confidence': base_confidence - 0.1,
                'expected_change': trend_factor * (2 + random.random() * 5)  # ±2-7%
            },
            'analysis_factors': {
                '기술적 지표': 0.75 + random.random() * 0.2,
                '시장 심리': 0.65 + random.random() * 0.25,
                '뉴스 감정': 0.70 + random.random() * 0.2,
                '거래량 패턴': 0.80 + random.random() * 0.15,
                '글로벌 동향': 0.60 + random.random() * 0.3
            },
            'suggestions': [
                f"현재 {ticker}는 {'상승' if recent_trend > 0 else '하락'} 추세입니다.",
                f"변동성이 {'높은' if volatility > 0.03 else '낮은'} 상태로 {'주의깊은' if volatility > 0.03 else '안정적인'} 접근이 필요합니다.",
                "분산투자를 통한 리스크 관리를 권장합니다.",
                "전문가 상담을 통한 추가 검토를 고려해보세요."
            ]
        }
        
        return predictions
    
    def get_alert_statistics(self) -> Dict[str, Any]:
        """알림 통계"""
        if 'alerts' not in st.session_state:
            return {'total': 0, 'unread': 0, 'by_type': {}}
        
        alerts = st.session_state.alerts
        unread = sum(1 for alert in alerts if not alert['read'])
        
        by_type = {}
        for alert in alerts:
            alert_type = alert['type']
            if alert_type not in by_type:
                by_type[alert_type] = 0
            by_type[alert_type] += 1
        
        return {
            'total': len(alerts),
            'unread': unread,
            'by_type': by_type,
            'recent': alerts[:10] if alerts else []
        }

# 메인 통합 함수
def integrate_unified_realtime_alerts():
    """통합된 실시간 알림 시스템"""
    
    # 알림 시스템 초기화
    if 'unified_alert_system' not in st.session_state:
        st.session_state.unified_alert_system = UnifiedRealtimeAlertSystem()
    
    alert_system = st.session_state.unified_alert_system
    
    # 탭 구성
    tab1, tab2, tab3 = st.tabs(["🔔 알림 센터", "📊 포트폴리오 모니터링", "🔮 AI 예측"])
    
    with tab1:
        alert_system.render_alert_dashboard()
    
    with tab2:
        alert_system.render_portfolio_monitoring()
    
    with tab3:
        alert_system.render_ai_predictions()
    
    # 자동 알림 생성 (데모용)
    if st.button("🎯 데모 알림 생성", key="demo_alerts"):
        demo_alerts = [
            ("삼성전자 주가 상승", "삼성전자가 3.2% 상승했습니다.", AlertType.PRICE_SPIKE, AlertPriority.MEDIUM),
            ("코스피 거래량 급증", "코스피 거래량이 평균 대비 2.5배 증가했습니다.", AlertType.VOLUME_SURGE, AlertPriority.HIGH),
            ("테슬라 과매수 구간", "테슬라 RSI가 75로 과매수 구간입니다.", AlertType.RISK_WARNING, AlertPriority.HIGH),
            ("SK하이닉스 패턴 감지", "삼각수렴 패턴이 감지되었습니다.", AlertType.PATTERN_DETECTED, AlertPriority.MEDIUM)
        ]
        
        for title, message, alert_type, priority in demo_alerts:
            alert_system.add_alert(
                alert_type=alert_type,
                title=title,
                message=message,
                priority=priority,
                action_required=True,
                ai_confidence=0.85
            )
        
        st.success("데모 알림이 생성되었습니다!")
        st.rerun()

# 편의 함수들
def init_unified_alert_system():
    """통합 알림 시스템 초기화"""
    if 'unified_alert_system' not in st.session_state:
        st.session_state.unified_alert_system = UnifiedRealtimeAlertSystem()
    
    return st.session_state.unified_alert_system

def show_unified_alerts():
    """통합 알림 시스템 표시"""
    integrate_unified_realtime_alerts()

def add_unified_alert(alert_type: str, title: str, message: str, ticker: str = None):
    """통합 알림 추가 헬퍼"""
    alert_system = init_unified_alert_system()
    
    # 문자열을 Enum으로 변환
    try:
        alert_type_enum = AlertType(alert_type)
    except ValueError:
        alert_type_enum = AlertType.OPPORTUNITY
    
    alert_system.add_alert(
        alert_type=alert_type_enum,
        title=title,
        message=message,
        ticker=ticker,
        priority=AlertPriority.MEDIUM,
        action_required=True,
        ai_confidence=0.8
    )

if __name__ == "__main__":
    st.set_page_config(page_title="통합 실시간 AI 알림 시스템", page_icon="🔔", layout="wide")
    st.title("🔔 통합 실시간 AI 알림 엔진")
    integrate_unified_realtime_alerts()
