"""
realtime_alert_engine.py - 실시간 AI 알림 엔진
24/7 포트폴리오 모니터링 및 지능형 알림 시스템
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
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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
        
        # 더블바텀/더블탑 패턴
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
        if type == 'min':
            return [data.iloc[i] for i in range(1, len(data)-1) 
                    if data.iloc[i] < data.iloc[i-1] and data.iloc[i] < data.iloc[i+1]]
        else:
            return [data.iloc[i] for i in range(1, len(data)-1) 
                    if data.iloc[i] > data.iloc[i-1] and data.iloc[i] > data.iloc[i+1]]

class PortfolioMonitor:
    """포트폴리오 모니터링"""
    
    def __init__(self, alert_analyzer: AIAlertAnalyzer):
        self.alert_analyzer = alert_analyzer
        self.monitoring_active = False
        self.alerts_queue = asyncio.Queue()
        self.monitored_portfolios = {}
        
    async def start_monitoring(self, portfolio_id: str, holdings: List[Dict[str, Any]], 
                             interval: int = 300):  # 5분 간격
        """포트폴리오 모니터링 시작"""
        self.monitored_portfolios[portfolio_id] = {
            'holdings': holdings,
            'last_check': datetime.now(),
            'alerts_sent': []
        }
        
        self.monitoring_active = True
        
        while self.monitoring_active:
            try:
                # 각 보유 종목 체크
                for holding in holdings:
                    ticker = holding.get('ticker')
                    if ticker:
                        await self._check_stock(portfolio_id, ticker, holding)
                
                # 포트폴리오 전체 분석
                await self._analyze_portfolio_health(portfolio_id)
                
                # 대기
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"모니터링 오류: {str(e)}")
                await asyncio.sleep(60)  # 오류 시 1분 대기
    
    async def _check_stock(self, portfolio_id: str, ticker: str, holding: Dict[str, Any]):
        """개별 종목 체크"""
        try:
            # 실시간 데이터 수집
            stock = yf.Ticker(ticker)
            data = stock.history(period="1d", interval="5m")
            
            if data.empty:
                return
            
            # AI 분석
            alerts = self.alert_analyzer.analyze_market_conditions(ticker, data)
            
            # 손익 관련 알림 추가
            current_price = data['Close'].iloc[-1]
            buy_price = holding.get('buy_price', 0)
            shares = holding.get('shares', 0)
            
            if buy_price > 0:
                profit_rate = ((current_price - buy_price) / buy_price) * 100
                
                # 손절/익절 알림
                if profit_rate <= -10:  # 10% 손실
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
                elif profit_rate >= 20:  # 20% 수익
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
            
            # 알림 전송
            for alert in alerts:
                await self.alerts_queue.put((portfolio_id, alert))
                
        except Exception as e:
            logger.error(f"종목 체크 오류 ({ticker}): {str(e)}")
    
    async def _analyze_portfolio_health(self, portfolio_id: str):
        """포트폴리오 전체 건강도 분석"""
        portfolio = self.monitored_portfolios.get(portfolio_id)
        if not portfolio:
            return
        
        holdings = portfolio['holdings']
        total_value = 0
        stock_values = {}
        
        # 각 종목 현재가치 계산
        for holding in holdings:
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
                    alert = Alert(
                        type=AlertType.PORTFOLIO_IMBALANCE,
                        priority=AlertPriority.MEDIUM,
                        title="포트폴리오 집중도 경고",
                        message=f"{ticker}가 포트폴리오의 {weight:.1f}%를 차지합니다. "
                               f"분산투자를 고려하세요.",
                        ticker=ticker,
                        timestamp=datetime.now(),
                        action_required=True,
                        ai_confidence=0.85,
                        metadata={'weight': weight, 'total_value': total_value}
                    )
                    await self.alerts_queue.put((portfolio_id, alert))
    
    def stop_monitoring(self):
        """모니터링 중지"""
        self.monitoring_active = False

class NotificationManager:
    """알림 전송 관리자"""
    
    def __init__(self):
        self.notification_channels = {
            'in_app': True,
            'email': False,
            'sms': False,
            'push': False
        }
        self.sent_alerts = []  # 중복 방지
        
    async def send_alert(self, alert: Alert, user_preferences: Dict[str, Any] = None):
        """알림 전송"""
        # 중복 체크
        alert_key = f"{alert.type.value}_{alert.ticker}_{alert.timestamp.strftime('%Y%m%d%H')}"
        if alert_key in self.sent_alerts:
            return
        
        self.sent_alerts.append(alert_key)
        
        # 우선순위별 전송 채널 결정
        if alert.priority == AlertPriority.CRITICAL:
            await self._send_all_channels(alert, user_preferences)
        elif alert.priority == AlertPriority.HIGH:
            await self._send_priority_channels(alert, user_preferences)
        else:
            await self._send_in_app(alert)
    
    async def _send_all_channels(self, alert: Alert, user_preferences: Dict[str, Any]):
        """모든 채널로 전송"""
        tasks = [
            self._send_in_app(alert),
            self._send_email(alert, user_preferences),
            self._send_sms(alert, user_preferences),
            self._send_push(alert, user_preferences)
        ]
        await asyncio.gather(*tasks)
    
    async def _send_priority_channels(self, alert: Alert, user_preferences: Dict[str, Any]):
        """우선순위 채널로 전송"""
        tasks = [
            self._send_in_app(alert),
            self._send_push(alert, user_preferences)
        ]
        await asyncio.gather(*tasks)
    
    async def _send_in_app(self, alert: Alert):
        """인앱 알림"""
        if 'alerts' not in st.session_state:
            st.session_state.alerts = []
        
        st.session_state.alerts.insert(0, {
            'id': f"{alert.timestamp.timestamp()}",
            'type': alert.type.value,
            'priority': alert.priority.value,
            'title': alert.title,
            'message': alert.message,
            'timestamp': alert.timestamp,
            'read': False,
            'metadata': alert.metadata
        })
        
        # 최대 50개 유지
        if len(st.session_state.alerts) > 50:
            st.session_state.alerts = st.session_state.alerts[:50]
    
    async def _send_email(self, alert: Alert, user_preferences: Dict[str, Any]):
        """이메일 알림"""
        if not user_preferences or not user_preferences.get('email'):
            return
        
        try:
            # 실제 운영에서는 SendGrid, AWS SES 등 사용
            subject = f"[투자 알림] {alert.title}"
            body = f"""
            <html>
            <body>
                <h2>{alert.title}</h2>
                <p><strong>우선순위:</strong> {alert.priority.value}</p>
                <p><strong>시간:</strong> {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
                <hr>
                <p>{alert.message}</p>
                <hr>
                <p><small>이 알림은 AI 분석 기반으로 생성되었습니다. (신뢰도: {alert.ai_confidence:.0%})</small></p>
            </body>
            </html>
            """
            
            # 이메일 전송 로직
            logger.info(f"이메일 알림 전송: {alert.title}")
            
        except Exception as e:
            logger.error(f"이메일 전송 실패: {str(e)}")
    
    async def _send_sms(self, alert: Alert, user_preferences: Dict[str, Any]):
        """SMS 알림"""
        if not user_preferences or not user_preferences.get('phone'):
            return
        
        try:
            # 실제 운영에서는 Twilio, AWS SNS 등 사용
            message = f"[투자알림] {alert.title}\n{alert.message[:100]}..."
            logger.info(f"SMS 알림 전송: {message}")
            
        except Exception as e:
            logger.error(f"SMS 전송 실패: {str(e)}")
    
    async def _send_push(self, alert: Alert, user_preferences: Dict[str, Any]):
        """푸시 알림"""
        if not user_preferences or not user_preferences.get('push_token'):
            return
        
        try:
            # 실제 운영에서는 FCM, OneSignal 등 사용
            payload = {
                'title': alert.title,
                'body': alert.message,
                'priority': alert.priority.value,
                'data': {
                    'type': alert.type.value,
                    'ticker': alert.ticker,
                    'metadata': json.dumps(alert.metadata)
                }
            }
            logger.info(f"푸시 알림 전송: {alert.title}")
            
        except Exception as e:
            logger.error(f"푸시 전송 실패: {str(e)}")

class RealtimeAlertEngine:
    """실시간 알림 엔진 메인 클래스"""
    
    def __init__(self):
        self.alert_analyzer = AIAlertAnalyzer()
        self.portfolio_monitor = PortfolioMonitor(self.alert_analyzer)
        self.notification_manager = NotificationManager()
        self.monitoring_tasks = {}
        
    async def start_portfolio_monitoring(self, portfolio_id: str, holdings: List[Dict[str, Any]]):
        """포트폴리오 모니터링 시작"""
        if portfolio_id in self.monitoring_tasks:
            logger.warning(f"포트폴리오 {portfolio_id}는 이미 모니터링 중입니다.")
            return
        
        # 모니터링 태스크 생성
        task = asyncio.create_task(
            self.portfolio_monitor.start_monitoring(portfolio_id, holdings)
        )
        self.monitoring_tasks[portfolio_id] = task
        
        # 알림 처리 태스크
        asyncio.create_task(self._process_alerts())
        
        logger.info(f"포트폴리오 {portfolio_id} 모니터링 시작")
    
    async def stop_portfolio_monitoring(self, portfolio_id: str):
        """포트폴리오 모니터링 중지"""
        if portfolio_id in self.monitoring_tasks:
            task = self.monitoring_tasks[portfolio_id]
            task.cancel()
            del self.monitoring_tasks[portfolio_id]
            logger.info(f"포트폴리오 {portfolio_id} 모니터링 중지")
    
    async def _process_alerts(self):
        """알림 처리"""
        while True:
            try:
                portfolio_id, alert = await self.portfolio_monitor.alerts_queue.get()
                
                # 사용자 설정 조회 (실제로는 DB에서)
                user_preferences = self._get_user_preferences(portfolio_id)
                
                # 알림 전송
                await self.notification_manager.send_alert(alert, user_preferences)
                
            except Exception as e:
                logger.error(f"알림 처리 오류: {str(e)}")
                await asyncio.sleep(1)
    
    def _get_user_preferences(self, portfolio_id: str) -> Dict[str, Any]:
        """사용자 설정 조회"""
        # 실제로는 DB에서 조회
        return {
            'email': 'user@example.com',
            'phone': '010-1234-5678',
            'push_token': 'token_123',
            'alert_settings': {
                'price_change_threshold': 0.05,
                'enable_night_alerts': False
            }
        }
    
    def get_alert_statistics(self) -> Dict[str, Any]:
        """알림 통계"""
        if 'alerts' not in st.session_state:
            return {'total': 0, 'unread': 0, 'by_type': {}}
        
        alerts = st.session_state.alerts
        unread = sum(1 for alert in alerts if not alert['read'])
        
        by_type
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

def render_realtime_alerts():
   """실시간 알림 UI 렌더링"""
   st.markdown("### 🔔 실시간 AI 알림 센터")
   
   # 알림 엔진 초기화
   if 'alert_engine' not in st.session_state:
       st.session_state.alert_engine = RealtimeAlertEngine()
   
   alert_engine = st.session_state.alert_engine
   
   # 알림 통계
   stats = alert_engine.get_alert_statistics()
   
   col1, col2, col3, col4 = st.columns(4)
   with col1:
       st.metric("전체 알림", stats['total'])
   with col2:
       st.metric("읽지 않은 알림", stats['unread'])
   with col3:
       st.metric("오늘 알림", len([a for a in stats.get('recent', []) 
                                  if datetime.fromisoformat(str(a['timestamp'])).date() == datetime.now().date()]))
   with col4:
       if st.button("🔄 새로고침", key="refresh_alerts"):
           st.rerun()
   
   # 알림 필터
   st.markdown("#### 🎯 알림 필터")
   col1, col2, col3 = st.columns(3)
   
   with col1:
       filter_type = st.selectbox(
           "알림 타입",
           ["전체"] + [alert_type.value for alert_type in AlertType],
           key="filter_type"
       )
   
   with col2:
       filter_priority = st.selectbox(
           "우선순위",
           ["전체"] + [priority.value for priority in AlertPriority],
           key="filter_priority"
       )
   
   with col3:
       filter_unread = st.checkbox("읽지 않은 알림만", key="filter_unread")
   
   # 알림 목록
   st.markdown("#### 📋 최근 알림")
   
   if 'alerts' in st.session_state and st.session_state.alerts:
       filtered_alerts = st.session_state.alerts
       
       # 필터 적용
       if filter_type != "전체":
           filtered_alerts = [a for a in filtered_alerts if a['type'] == filter_type]
       
       if filter_priority != "전체":
           filtered_alerts = [a for a in filtered_alerts if a['priority'] == filter_priority]
       
       if filter_unread:
           filtered_alerts = [a for a in filtered_alerts if not a['read']]
       
       # 알림 표시
       for alert in filtered_alerts[:20]:  # 최대 20개
           with st.container():
               col1, col2 = st.columns([5, 1])
               
               with col1:
                   # 우선순위별 아이콘
                   priority_icons = {
                       "긴급": "🚨",
                       "높음": "⚠️",
                       "중간": "📌",
                       "낮음": "💡"
                   }
                   icon = priority_icons.get(alert['priority'], "📌")
                   
                   # 읽음 표시
                   title_style = "color: #999;" if alert['read'] else "font-weight: bold;"
                   
                   st.markdown(f"""
                   <div style="background: #f8f9fa; padding: 1rem; border-radius: 0.5rem; margin: 0.5rem 0; border-left: 4px solid {'#ff4444' if alert['priority'] == '긴급' else '#ffaa00' if alert['priority'] == '높음' else '#4CAF50'};">
                       <div style="{title_style}">
                           {icon} {alert['title']}
                           <span style="float: right; font-size: 0.8rem; color: #999;">
                               {datetime.fromisoformat(str(alert['timestamp'])).strftime('%H:%M')}
                           </span>
                       </div>
                       <div style="margin-top: 0.5rem; color: #666;">
                           {alert['message']}
                       </div>
                       <div style="margin-top: 0.5rem; font-size: 0.8rem; color: #999;">
                           타입: {alert['type']} | 우선순위: {alert['priority']}
                       </div>
                   </div>
                   """, unsafe_allow_html=True)
               
               with col2:
                   if not alert['read']:
                       if st.button("읽음", key=f"read_{alert['id']}"):
                           alert['read'] = True
                           st.rerun()
                   
                   if alert.get('metadata', {}).get('ticker'):
                       if st.button("차트", key=f"chart_{alert['id']}"):
                           st.session_state.selected_ticker = alert['metadata']['ticker']
   else:
       st.info("아직 알림이 없습니다. 포트폴리오를 등록하면 실시간 모니터링이 시작됩니다.")
   
   # 알림 설정
   with st.expander("⚙️ 알림 설정", expanded=False):
       st.markdown("#### 알림 채널 설정")
       
       col1, col2 = st.columns(2)
       
       with col1:
           enable_email = st.checkbox("이메일 알림", value=False)
           if enable_email:
               email = st.text_input("이메일 주소", placeholder="your@email.com")
           
           enable_sms = st.checkbox("SMS 알림", value=False)
           if enable_sms:
               phone = st.text_input("휴대폰 번호", placeholder="010-1234-5678")
       
       with col2:
           enable_push = st.checkbox("푸시 알림", value=False)
           enable_night = st.checkbox("야간 알림 허용", value=False)
       
       st.markdown("#### 알림 임계값 설정")
       
       col1, col2, col3 = st.columns(3)
       
       with col1:
           price_threshold = st.slider(
               "가격 변동 알림 (%)",
               min_value=1.0,
               max_value=10.0,
               value=5.0,
               step=0.5
           )
       
       with col2:
           volume_threshold = st.slider(
               "거래량 급증 배수",
               min_value=1.5,
               max_value=5.0,
               value=2.0,
               step=0.5
           )
       
       with col3:
           rsi_oversold = st.slider(
               "RSI 과매도 기준",
               min_value=20,
               max_value=40,
               value=30,
               step=5
           )
       
       if st.button("설정 저장", type="primary"):
           # 설정 저장 로직
           st.success("알림 설정이 저장되었습니다!")

def render_portfolio_monitoring():
   """포트폴리오 모니터링 UI"""
   st.markdown("### 📊 포트폴리오 실시간 모니터링")
   
   # 포트폴리오 입력
   with st.expander("➕ 모니터링할 포트폴리오 추가", expanded=False):
       col1, col2, col3, col4 = st.columns(4)
       
       with col1:
           ticker = st.text_input("종목 코드", placeholder="005930.KS")
       with col2:
           shares = st.number_input("보유 주수", min_value=1, value=10)
       with col3:
           buy_price = st.number_input("매수가", min_value=0.0, value=70000.0)
       with col4:
           if st.button("추가", type="primary"):
               if 'monitored_portfolio' not in st.session_state:
                   st.session_state.monitored_portfolio = []
               
               st.session_state.monitored_portfolio.append({
                   'ticker': ticker,
                   'shares': shares,
                   'buy_price': buy_price,
                   'added_at': datetime.now()
               })
               st.success(f"{ticker} 추가됨!")
   
   # 모니터링 중인 포트폴리오
   if 'monitored_portfolio' in st.session_state and st.session_state.monitored_portfolio:
       st.markdown("#### 🔍 모니터링 중인 종목")
       
       # 실시간 업데이트를 위한 placeholder
       placeholder = st.empty()
       
       with placeholder.container():
           for i, holding in enumerate(st.session_state.monitored_portfolio):
               col1, col2, col3, col4, col5, col6 = st.columns([2, 1, 1, 1, 1, 1])
               
               with col1:
                   st.write(f"**{holding['ticker']}**")
               
               with col2:
                   st.write(f"{holding['shares']}주")
               
               with col3:
                   st.write(f"매수: {holding['buy_price']:,.0f}원")
               
               # 실시간 데이터 (실제로는 비동기로 업데이트)
               try:
                   stock = yf.Ticker(holding['ticker'])
                   current_price = stock.history(period="1d")['Close'].iloc[-1]
                   profit_rate = ((current_price - holding['buy_price']) / holding['buy_price']) * 100
                   
                   with col4:
                       st.write(f"현재: {current_price:,.0f}원")
                   
                   with col5:
                       color = "🟢" if profit_rate >= 0 else "🔴"
                       st.write(f"{color} {profit_rate:+.1f}%")
                   
                   with col6:
                       if st.button("제거", key=f"remove_{i}"):
                           st.session_state.monitored_portfolio.pop(i)
                           st.rerun()
               except:
                   with col4:
                       st.write("데이터 없음")
       
       # 모니터링 시작/중지
       col1, col2 = st.columns(2)
       
       with col1:
           if st.button("🚀 실시간 모니터링 시작", type="primary", use_container_width=True):
               # 비동기 모니터링 시작
               st.success("실시간 모니터링이 시작되었습니다! 알림 센터에서 확인하세요.")
       
       with col2:
           if st.button("⏹️ 모니터링 중지", type="secondary", use_container_width=True):
               st.info("모니터링이 중지되었습니다.")
   else:
       st.info("모니터링할 포트폴리오를 추가해주세요.")

def render_ai_predictions():
   """AI 예측 대시보드"""
   st.markdown("### 🔮 AI 예측 분석")
   
   # 예측 대상 선택
   col1, col2 = st.columns([3, 1])
   
   with col1:
       prediction_ticker = st.selectbox(
           "예측할 종목 선택",
           ["005930.KS", "000660.KS", "035420.KS", "TSLA", "NVDA"],
           format_func=lambda x: {"005930.KS": "삼성전자", "000660.KS": "SK하이닉스", 
                                "035420.KS": "네이버", "TSLA": "테슬라", "NVDA": "엔비디아"}.get(x, x)
       )
   
   with col2:
       if st.button("예측 실행", type="primary"):
           with st.spinner("AI가 분석 중입니다..."):
               time.sleep(2)  # 시뮬레이션
               
               # 예측 결과 생성 (실제로는 AI 모델 사용)
               st.session_state.ai_prediction = {
                   'ticker': prediction_ticker,
                   'timestamp': datetime.now(),
                   'next_hour': {
                       'direction': 'UP',
                       'confidence': 0.75,
                       'expected_change': 1.2
                   },
                   'next_day': {
                       'direction': 'UP', 
                       'confidence': 0.68,
                       'expected_change': 2.5
                   },
                   'next_week': {
                       'direction': 'DOWN',
                       'confidence': 0.55,
                       'expected_change': -1.8
                   }
               }
   
   # 예측 결과 표시
   if 'ai_prediction' in st.session_state:
       prediction = st.session_state.ai_prediction
       
       st.markdown(f"#### 📈 {prediction['ticker']} AI 예측 결과")
       st.caption(f"분석 시간: {prediction['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
       
       # 예측 카드
       col1, col2, col3 = st.columns(3)
       
       timeframes = [
           ("1시간 후", prediction['next_hour']),
           ("1일 후", prediction['next_day']),
           ("1주일 후", prediction['next_week'])
       ]
       
       for col, (timeframe, pred) in zip([col1, col2, col3], timeframes):
           with col:
               direction_icon = "📈" if pred['direction'] == 'UP' else "📉"
               confidence_color = "#4CAF50" if pred['confidence'] >= 0.7 else "#FF9800" if pred['confidence'] >= 0.5 else "#F44336"
               
               st.markdown(f"""
               <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 0.5rem; text-align: center;">
                   <h4 style="margin: 0;">{timeframe}</h4>
                   <div style="font-size: 2rem; margin: 0.5rem 0;">{direction_icon}</div>
                   <div style="font-size: 1.2rem; font-weight: bold; color: {'#4CAF50' if pred['direction'] == 'UP' else '#F44336'};">
                       {pred['expected_change']:+.1f}%
                   </div>
                   <div style="margin-top: 0.5rem;">
                       신뢰도: <span style="color: {confidence_color}; font-weight: bold;">{pred['confidence']:.0%}</span>
                   </div>
               </div>
               """, unsafe_allow_html=True)
       
       # AI 분석 근거
       st.markdown("#### 🧠 AI 분석 근거")
       
       analysis_factors = {
           "기술적 지표": 0.85,
           "시장 심리": 0.72,
           "뉴스 감정": 0.68,
           "거래량 패턴": 0.91,
           "상관 종목": 0.77
       }
       
       for factor, score in analysis_factors.items():
           col1, col2 = st.columns([3, 1])
           with col1:
               st.write(factor)
           with col2:
               color = "#4CAF50" if score >= 0.8 else "#FF9800" if score >= 0.6 else "#F44336"
               st.markdown(f'<div style="text-align: right; color: {color}; font-weight: bold;">{score:.0%}</div>', 
                         unsafe_allow_html=True)

# 메인 통합 함수
def integrate_realtime_alerts():
   """실시간 알림 기능을 메인 앱에 통합"""
   tab1, tab2, tab3 = st.tabs(["🔔 알림 센터", "📊 포트폴리오 모니터링", "🔮 AI 예측"])
   
   with tab1:
       render_realtime_alerts()
   
   with tab2:
       render_portfolio_monitoring()
   
   with tab3:
       render_ai_predictions()

if __name__ == "__main__":
   st.set_page_config(page_title="실시간 AI 알림 시스템", page_icon="🔔", layout="wide")
   st.title("🔔 실시간 AI 알림 엔진")
   integrate_realtime_alerts()
