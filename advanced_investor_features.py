"""
advanced_investor_features.py - 실전 투자자를 위한 고급 기능 모듈
AI Festival 2025 - 실제 주식 투자자를 위한 전문 도구
"""

import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from datetime import datetime, timedelta
import requests
import ta
from typing import Dict, List, Optional, Tuple
import math
import warnings
warnings.filterwarnings('ignore')

class AdvancedPortfolioManager:
    """고급 포트폴리오 관리 시스템"""
    
    def __init__(self):
        self.portfolio = []
        self.watchlist = []
        
    def add_holding(self, ticker: str, shares: int, avg_price: float, 
                   purchase_date: str = None, notes: str = ""):
        """보유 종목 추가"""
        holding = {
            'ticker': ticker,
            'shares': shares,
            'avg_price': avg_price,
            'purchase_date': purchase_date or datetime.now().strftime('%Y-%m-%d'),
            'notes': notes,
            'current_price': 0,
            'market_value': 0,
            'total_return': 0,
            'daily_change': 0
        }
        self.portfolio.append(holding)
    
    def calculate_portfolio_metrics(self):
        """포트폴리오 상세 지표 계산"""
        if not self.portfolio:
            return None
            
        total_invested = 0
        total_current_value = 0
        daily_pnl = 0
        
        for holding in self.portfolio:
            # 현재가 조회
            current_price = self._get_current_price(holding['ticker'])
            if current_price:
                holding['current_price'] = current_price
                holding['market_value'] = current_price * holding['shares']
                holding['total_return'] = holding['market_value'] - (holding['avg_price'] * holding['shares'])
                
                # 전일 대비 변동
                yesterday_close = self._get_previous_close(holding['ticker'])
                if yesterday_close:
                    daily_change = (current_price - yesterday_close) / yesterday_close * 100
                    holding['daily_change'] = daily_change
                    daily_pnl += (current_price - yesterday_close) * holding['shares']
                
                total_invested += holding['avg_price'] * holding['shares']
                total_current_value += holding['market_value']
        
        return {
            'holdings': self.portfolio,
            'total_invested': total_invested,
            'total_current_value': total_current_value,
            'total_return': total_current_value - total_invested,
            'total_return_pct': ((total_current_value - total_invested) / total_invested * 100) if total_invested > 0 else 0,
            'daily_pnl': daily_pnl,
            'daily_pnl_pct': (daily_pnl / total_current_value * 100) if total_current_value > 0 else 0
        }
    
    def _get_current_price(self, ticker: str) -> float:
        """현재가 조회"""
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(period="1d")
            if not data.empty:
                return data['Close'].iloc[-1]
        except:
            pass
        return 0
    
    def _get_previous_close(self, ticker: str) -> float:
        """전일 종가 조회"""
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(period="2d")
            if len(data) >= 2:
                return data['Close'].iloc[-2]
        except:
            pass
        return 0

class TechnicalAnalyzer:
    """고급 기술적 분석 시스템"""
    
    def __init__(self):
        self.indicators = {}
    
    def analyze_stock(self, ticker: str, period: str = "6mo") -> Dict:
        """종목 기술적 분석"""
        try:
            # 데이터 수집
            stock = yf.Ticker(ticker)
            data = stock.history(period=period)
            
            if data.empty:
                return {}
            
            # 기술적 지표 계산
            indicators = self._calculate_indicators(data)
            
            # 매매 신호 생성
            signals = self._generate_signals(data, indicators)
            
            # 지지/저항선 계산
            support_resistance = self._calculate_support_resistance(data)
            
            return {
                'data': data,
                'indicators': indicators,
                'signals': signals,
                'support_resistance': support_resistance,
                'last_price': data['Close'].iloc[-1],
                'analysis_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            st.error(f"기술적 분석 오류 ({ticker}): {str(e)}")
            return {}
    
    def _calculate_indicators(self, data: pd.DataFrame) -> Dict:
        """기술적 지표 계산"""
        indicators = {}
        
        # 이동평균선
        indicators['SMA_5'] = ta.trend.sma_indicator(data['Close'], window=5)
        indicators['SMA_20'] = ta.trend.sma_indicator(data['Close'], window=20)
        indicators['SMA_60'] = ta.trend.sma_indicator(data['Close'], window=60)
        indicators['EMA_12'] = ta.trend.ema_indicator(data['Close'], window=12)
        indicators['EMA_26'] = ta.trend.ema_indicator(data['Close'], window=26)
        
        # 오실레이터
        indicators['RSI'] = ta.momentum.rsi(data['Close'], window=14)
        indicators['STOCH_K'] = ta.momentum.stoch(data['High'], data['Low'], data['Close'])
        indicators['STOCH_D'] = ta.momentum.stoch_signal(data['High'], data['Low'], data['Close'])
        
        # MACD
        macd_line, macd_signal, macd_histogram = ta.trend.MACD(data['Close']).macd(), ta.trend.MACD(data['Close']).macd_signal(), ta.trend.MACD(data['Close']).macd_diff()
        indicators['MACD'] = macd_line
        indicators['MACD_Signal'] = macd_signal
        indicators['MACD_Histogram'] = macd_histogram
        
        # 볼린저 밴드
        bb_upper, bb_lower = ta.volatility.bollinger_hband(data['Close']), ta.volatility.bollinger_lband(data['Close'])
        indicators['BB_Upper'] = bb_upper
        indicators['BB_Lower'] = bb_lower
        indicators['BB_Middle'] = ta.volatility.bollinger_mavg(data['Close'])
        
        # ATR (Average True Range)
        indicators['ATR'] = ta.volatility.average_true_range(data['High'], data['Low'], data['Close'])
        
        # Volume indicators
        indicators['Volume_SMA'] = ta.volume.volume_sma(data['Close'], data['Volume'])
        indicators['OBV'] = ta.volume.on_balance_volume(data['Close'], data['Volume'])
        
        return indicators
    
    def _generate_signals(self, data: pd.DataFrame, indicators: Dict) -> Dict:
        """매매 신호 생성"""
        signals = {}
        latest_idx = -1
        
        # 현재 가격과 지표들
        current_price = data['Close'].iloc[latest_idx]
        current_rsi = indicators['RSI'].iloc[latest_idx] if not indicators['RSI'].empty else 50
        current_macd = indicators['MACD'].iloc[latest_idx] if not indicators['MACD'].empty else 0
        current_signal = indicators['MACD_Signal'].iloc[latest_idx] if not indicators['MACD_Signal'].empty else 0
        
        # RSI 신호
        if current_rsi > 70:
            signals['RSI'] = {'signal': 'SELL', 'strength': 'STRONG', 'reason': f'과매수 (RSI: {current_rsi:.1f})'}
        elif current_rsi < 30:
            signals['RSI'] = {'signal': 'BUY', 'strength': 'STRONG', 'reason': f'과매도 (RSI: {current_rsi:.1f})'}
        else:
            signals['RSI'] = {'signal': 'HOLD', 'strength': 'WEAK', 'reason': f'중립 구간 (RSI: {current_rsi:.1f})'}
        
        # MACD 신호
        if current_macd > current_signal and indicators['MACD'].iloc[-2] <= indicators['MACD_Signal'].iloc[-2]:
            signals['MACD'] = {'signal': 'BUY', 'strength': 'MEDIUM', 'reason': 'MACD 상향 돌파'}
        elif current_macd < current_signal and indicators['MACD'].iloc[-2] >= indicators['MACD_Signal'].iloc[-2]:
            signals['MACD'] = {'signal': 'SELL', 'strength': 'MEDIUM', 'reason': 'MACD 하향 돌파'}
        else:
            signals['MACD'] = {'signal': 'HOLD', 'strength': 'WEAK', 'reason': '신호 없음'}
        
        # 이동평균선 신호
        sma5 = indicators['SMA_5'].iloc[latest_idx] if not indicators['SMA_5'].empty else current_price
        sma20 = indicators['SMA_20'].iloc[latest_idx] if not indicators['SMA_20'].empty else current_price
        
        if current_price > sma5 > sma20:
            signals['MA'] = {'signal': 'BUY', 'strength': 'MEDIUM', 'reason': '가격이 단기 이평선 위에 위치'}
        elif current_price < sma5 < sma20:
            signals['MA'] = {'signal': 'SELL', 'strength': 'MEDIUM', 'reason': '가격이 단기 이평선 아래에 위치'}
        else:
            signals['MA'] = {'signal': 'HOLD', 'strength': 'WEAK', 'reason': '혼재 상황'}
        
        return signals
    
    def _calculate_support_resistance(self, data: pd.DataFrame, window: int = 20) -> Dict:
        """지지/저항선 계산"""
        highs = data['High'].rolling(window=window).max()
        lows = data['Low'].rolling(window=window).min()
        
        # 최근 지지/저항선
        recent_resistance = highs.iloc[-window:].max()
        recent_support = lows.iloc[-window:].min()
        
        return {
            'resistance': recent_resistance,
            'support': recent_support,
            'range_pct': ((recent_resistance - recent_support) / recent_support * 100)
        }

class RiskManager:
    """리스크 관리 시스템"""
    
    def __init__(self):
        self.risk_metrics = {}
    
    def calculate_portfolio_risk(self, portfolio_metrics: Dict) -> Dict:
        """포트폴리오 리스크 계산"""
        if not portfolio_metrics or not portfolio_metrics.get('holdings'):
            return {}
        
        holdings = portfolio_metrics['holdings']
        
        # 집중도 리스크 계산
        concentration_risk = self._calculate_concentration_risk(holdings, portfolio_metrics['total_current_value'])
        
        # 섹터 분산도 계산
        sector_diversification = self._calculate_sector_diversification(holdings)
        
        # VaR (Value at Risk) 계산
        var_analysis = self._calculate_var(holdings)
        
        # 전체 리스크 스코어
        overall_risk_score = self._calculate_overall_risk_score(concentration_risk, sector_diversification, var_analysis)
        
        return {
            'concentration_risk': concentration_risk,
            'sector_diversification': sector_diversification,
            'var_analysis': var_analysis,
            'overall_risk_score': overall_risk_score,
            'risk_recommendations': self._generate_risk_recommendations(concentration_risk, sector_diversification)
        }
    
    def _calculate_concentration_risk(self, holdings: List, total_value: float) -> Dict:
        """집중도 리스크 계산"""
        if total_value == 0:
            return {'level': 'LOW', 'max_position': 0, 'top3_concentration': 0}
        
        # 각 종목의 비중 계산
        weights = [holding['market_value'] / total_value * 100 for holding in holdings]
        weights.sort(reverse=True)
        
        max_position = max(weights) if weights else 0
        top3_concentration = sum(weights[:3]) if len(weights) >= 3 else sum(weights)
        
        # 리스크 레벨 결정
        if max_position > 40:
            level = 'HIGH'
        elif max_position > 25:
            level = 'MEDIUM'
        else:
            level = 'LOW'
        
        return {
            'level': level,
            'max_position': max_position,
            'top3_concentration': top3_concentration,
            'position_weights': weights
        }
    
    def _calculate_sector_diversification(self, holdings: List) -> Dict:
        """섹터 분산도 계산 (간단 버전)"""
        # 실제로는 각 종목의 섹터 정보가 필요하지만, 여기서는 간단화
        num_stocks = len(holdings)
        
        if num_stocks >= 10:
            level = 'HIGH'
        elif num_stocks >= 5:
            level = 'MEDIUM'
        else:
            level = 'LOW'
        
        return {
            'level': level,
            'num_positions': num_stocks,
            'diversification_score': min(num_stocks * 10, 100)
        }
    
    def _calculate_var(self, holdings: List, confidence: float = 0.95) -> Dict:
        """VaR (Value at Risk) 계산"""
        # 간단화된 VaR 계산
        daily_changes = []
        
        for holding in holdings:
            if holding.get('daily_change'):
                daily_changes.append(holding['daily_change'])
        
        if not daily_changes:
            return {'daily_var': 0, 'weekly_var': 0, 'risk_level': 'LOW'}
        
        # 포트폴리오 평균 변동성
        portfolio_volatility = np.std(daily_changes)
        
        # VaR 계산 (정규분포 가정)
        var_multiplier = 1.645 if confidence == 0.95 else 2.33  # 95% 또는 99%
        daily_var = portfolio_volatility * var_multiplier
        weekly_var = daily_var * math.sqrt(5)  # 주간 VaR
        
        # 리스크 레벨
        if daily_var > 5:
            risk_level = 'HIGH'
        elif daily_var > 2:
            risk_level = 'MEDIUM'
        else:
            risk_level = 'LOW'
        
        return {
            'daily_var': daily_var,
            'weekly_var': weekly_var,
            'portfolio_volatility': portfolio_volatility,
            'risk_level': risk_level
        }
    
    def _calculate_overall_risk_score(self, concentration: Dict, diversification: Dict, var: Dict) -> Dict:
        """전체 리스크 스코어 계산"""
        scores = {
            'HIGH': 3,
            'MEDIUM': 2,
            'LOW': 1
        }
        
        concentration_score = scores.get(concentration.get('level', 'LOW'), 1)
        diversification_score = scores.get(diversification.get('level', 'LOW'), 1)
        var_score = scores.get(var.get('risk_level', 'LOW'), 1)
        
        # 가중 평균 (집중도 리스크를 더 높게 가중)
        overall_score = (concentration_score * 0.5 + diversification_score * 0.3 + var_score * 0.2)
        
        if overall_score >= 2.5:
            level = 'HIGH'
            recommendation = '포트폴리오 리스크가 높습니다. 분산투자를 권장합니다.'
        elif overall_score >= 1.8:
            level = 'MEDIUM'
            recommendation = '적정 수준의 리스크입니다. 지속적인 모니터링이 필요합니다.'
        else:
            level = 'LOW'
            recommendation = '보수적인 포트폴리오입니다. 수익 기회 확대를 고려해보세요.'
        
        return {
            'level': level,
            'score': overall_score,
            'recommendation': recommendation
        }
    
    def _generate_risk_recommendations(self, concentration: Dict, diversification: Dict) -> List[str]:
        """리스크 개선 권장사항"""
        recommendations = []
        
        if concentration.get('max_position', 0) > 30:
            recommendations.append(f"⚠️ 최대 비중 종목이 {concentration['max_position']:.1f}%입니다. 25% 이하로 줄이는 것을 권장합니다.")
        
        if diversification.get('num_positions', 0) < 5:
            recommendations.append("📊 종목 수가 부족합니다. 최소 5-10개 종목으로 분산투자를 권장합니다.")
        
        if concentration.get('top3_concentration', 0) > 70:
            recommendations.append("🎯 상위 3개 종목 집중도가 높습니다. 포트폴리오 재조정을 고려해보세요.")
        
        return recommendations

class AlertSystem:
    """지능형 알림 시스템"""
    
    def __init__(self):
        self.alerts = []
        
    def check_alerts(self, portfolio_metrics: Dict, technical_analysis: Dict) -> List[Dict]:
        """포트폴리오 및 기술적 분석 기반 알림 체크"""
        alerts = []
        
        if portfolio_metrics:
            # 포트폴리오 알림
            alerts.extend(self._check_portfolio_alerts(portfolio_metrics))
        
        if technical_analysis:
            # 기술적 분석 알림
            alerts.extend(self._check_technical_alerts(technical_analysis))
        
        return alerts
    
    def _check_portfolio_alerts(self, metrics: Dict) -> List[Dict]:
        """포트폴리오 알림 체크"""
        alerts = []
        
        for holding in metrics.get('holdings', []):
            ticker = holding.get('ticker', '')
            current_price = holding.get('current_price', 0)
            avg_price = holding.get('avg_price', 0)
            daily_change = holding.get('daily_change', 0)
            
            if current_price and avg_price:
                return_pct = (current_price - avg_price) / avg_price * 100
                
                # 큰 손실 알림
                if return_pct <= -20:
                    alerts.append({
                        'type': 'DANGER',
                        'title': f'{ticker} 큰 손실 발생',
                        'message': f'현재 {return_pct:.1f}% 손실입니다. 손절매를 검토하세요.',
                        'priority': 'HIGH'
                    })
                
                # 큰 수익 알림
                elif return_pct >= 30:
                    alerts.append({
                        'type': 'SUCCESS',
                        'title': f'{ticker} 목표 수익 달성',
                        'message': f'현재 {return_pct:.1f}% 수익입니다. 차익실현을 고려하세요.',
                        'priority': 'MEDIUM'
                    })
                
                # 급등/급락 알림
                if abs(daily_change) >= 5:
                    alert_type = 'WARNING' if daily_change < 0 else 'INFO'
                    direction = '급락' if daily_change < 0 else '급등'
                    alerts.append({
                        'type': alert_type,
                        'title': f'{ticker} {direction} 발생',
                        'message': f'당일 {daily_change:+.1f}% 변동했습니다.',
                        'priority': 'MEDIUM'
                    })
        
        return alerts
    
    def _check_technical_alerts(self, analysis: Dict) -> List[Dict]:
        """기술적 분석 알림 체크"""
        alerts = []
        
        signals = analysis.get('signals', {})
        
        # 강한 매매 신호 알림
        for indicator, signal_info in signals.items():
            if signal_info.get('strength') == 'STRONG':
                signal_type = signal_info.get('signal', 'HOLD')
                if signal_type in ['BUY', 'SELL']:
                    alerts.append({
                        'type': 'INFO',
                        'title': f'{indicator} 강한 {signal_type} 신호',
                        'message': signal_info.get('reason', ''),
                        'priority': 'HIGH'
                    })
        
        return alerts

class SmartOrderSystem:
    """스마트 주문 시스템 (모의)"""
    
    def __init__(self):
        self.order_types = ['시장가', '지정가', '조건부지정가', '최유리지정가']
        self.order_conditions = ['즉시체결', '당일유효', 'GTC', 'IOC', 'FOK']
    
    def create_order_plan(self, ticker: str, action: str, analysis: Dict) -> Dict:
        """주문 계획 생성"""
        if not analysis:
            return {}
        
        current_price = analysis.get('last_price', 0)
        support = analysis.get('support_resistance', {}).get('support', 0)
        resistance = analysis.get('support_resistance', {}).get('resistance', 0)
        
        order_plan = {
            'ticker': ticker,
            'action': action,
            'current_price': current_price,
            'analysis_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        if action == 'BUY':
            # 매수 주문 계획
            order_plan.update({
                'entry_price': current_price * 0.99,  # 1% 아래에서 매수
                'stop_loss': support * 0.98 if support > 0 else current_price * 0.95,
                'take_profit': resistance * 0.98 if resistance > 0 else current_price * 1.15,
                'suggested_quantity': self._calculate_position_size(current_price),
                'risk_reward_ratio': 0,
                'order_type': '지정가',
                'condition': '당일유효'
            })
            
            # 리스크/리워드 비율 계산
            if order_plan['stop_loss'] > 0:
                risk = order_plan['entry_price'] - order_plan['stop_loss']
                reward = order_plan['take_profit'] - order_plan['entry_price']
                order_plan['risk_reward_ratio'] = reward / risk if risk > 0 else 0
        
        elif action == 'SELL':
            # 매도 주문 계획
            order_plan.update({
                'exit_price': current_price * 1.01,  # 1% 위에서 매도
                'order_type': '지정가',
                'condition': '당일유효',
                'sell_reason': '기술적 분석 신호 또는 수익실현'
            })
        
        return order_plan
    
    def _calculate_position_size(self, price: float, portfolio_value: float = 1000000) -> int:
        """적정 포지션 크기 계산 (간단 버전)"""
        # 포트폴리오의 5% 이하로 제한
        max_investment = portfolio_value * 0.05
        suggested_shares = int(max_investment / price)
        return max(1, suggested_shares)

class MarketSentimentAnalyzer:
    """시장 심리 분석기"""
    
    def __init__(self):
        self.sentiment_sources = ['news', 'social', 'options', 'insider']
    
    def analyze_market_sentiment(self, market_data: Dict) -> Dict:
        """종합 시장 심리 분석"""
        if not market_data:
            return {'overall_sentiment': 'NEUTRAL', 'confidence': 0}
        
        # 지수 변동률 기반 심리 분석
        index_changes = []
        for name, data in market_data.items():
            if name in ['KOSPI', 'NASDAQ', 'S&P 500']:
                change = data.get('change', 0)
                index_changes.append(change)
        
        if not index_changes:
            return {'overall_sentiment': 'NEUTRAL', 'confidence': 50}
        
        avg_change = np.mean(index_changes)
        volatility = np.std(index_changes) if len(index_changes) > 1 else 0
        
        # 심리 지수 계산
        if avg_change > 2:
            sentiment = 'VERY_BULLISH'
            sentiment_score = min(90, 50 + avg_change * 10)
        elif avg_change > 0.5:
            sentiment = 'BULLISH'
            sentiment_score = 50 + avg_change * 10
        elif avg_change > -0.5:
            sentiment = 'NEUTRAL'
            sentiment_score = 50 + avg_change * 10
        elif avg_change > -2:
            sentiment = 'BEARISH'
            sentiment_score = 50 + avg_change * 10
        else:
            sentiment = 'VERY_BEARISH'
            sentiment_score = max(10, 50 + avg_change * 10)
        
        # 변동성 기반 신뢰도 조정
        confidence = max(30, 100 - volatility * 20)
        
        return {
            'overall_sentiment': sentiment,
            'sentiment_score': sentiment_score,
            'confidence': confidence,
            'market_trend': 'UP' if avg_change > 0 else 'DOWN' if avg_change < 0 else 'SIDEWAYS',
            'volatility_level': 'HIGH' if volatility > 2 else 'MEDIUM' if volatility > 1 else 'LOW'
        }

def render_advanced_features():
    """고급 기능 렌더링"""
    st.markdown("## 🚀 실전 투자자를 위한 고급 도구")
    
    # 기능 선택 탭
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 포트폴리오 관리", "📈 기술적 분석", "⚠️ 리스크 관리", 
        "🔔 스마트 알림", "📋 주문 계획"
    ])
    
    # 포트폴리오 매니저 초기화
    if 'portfolio_manager' not in st.session_state:
        st.session_state.portfolio_manager = AdvancedPortfolioManager()
    
    portfolio_manager = st.session_state.portfolio_manager
    
    with tab1:
        render_portfolio_manager(portfolio_manager)
    
    with tab2:
        render_technical_analyzer()
    
    with tab3:
        render_risk_manager(portfolio_manager)
    
    with tab4:
        render_alert_system(portfolio_manager)
    
    with tab5:
        render_order_system()

def render_portfolio_manager(portfolio_manager):
    """포트폴리오 관리자 렌더링"""
    st.markdown("### 📊 포트폴리오 관리")
    
    # 포트폴리오 추가
    with st.expander("➕ 보유 종목 추가", expanded=False):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            ticker = st.text_input("종목 코드", placeholder="005930.KS")
        with col2:
            shares = st.number_input("보유 주수", min_value=1, value=10)
        with col3:
            avg_price = st.number_input("평균 단가", min_value=0.1, value=100.0)
        with col4:
            notes = st.text_input("메모", placeholder="매수
