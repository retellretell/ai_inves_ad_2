"""
enhanced_features.py - 고급 기능 및 개선사항
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
from data_collector import get_real_time_market_data
from config import Config

class PortfolioAnalyzer:
    """포트폴리오 고급 분석 클래스"""
    
    def __init__(self):
        self.portfolio_data = {}
        self.market_data = get_real_time_market_data()
    
    def calculate_portfolio_metrics(self, holdings):
        """포트폴리오 종합 지표 계산"""
        total_value = 0
        total_invested = 0
        portfolio_items = []
        
        for holding in holdings:
            ticker = holding.get('ticker')
            shares = holding.get('shares', 0)
            buy_price = holding.get('buy_price', 0)
            
            # 현재가 조회
            current_price = self._get_current_price(ticker)
            if current_price:
                current_value = current_price * shares
                invested_amount = buy_price * shares
                profit_loss = current_value - invested_amount
                profit_rate = (profit_loss / invested_amount * 100) if invested_amount > 0 else 0
                
                portfolio_items.append({
                    'stock': holding.get('stock', ''),
                    'ticker': ticker,
                    'shares': shares,
                    'buy_price': buy_price,
                    'current_price': current_price,
                    'invested_amount': invested_amount,
                    'current_value': current_value,
                    'profit_loss': profit_loss,
                    'profit_rate': profit_rate,
                    'weight': 0  # 나중에 계산
                })
                
                total_value += current_value
                total_invested += invested_amount
        
        # 비중 계산
        for item in portfolio_items:
            item['weight'] = (item['current_value'] / total_value * 100) if total_value > 0 else 0
        
        return {
            'items': portfolio_items,
            'total_value': total_value,
            'total_invested': total_invested,
            'total_profit_loss': total_value - total_invested,
            'total_profit_rate': ((total_value - total_invested) / total_invested * 100) if total_invested > 0 else 0
        }
    
    def _get_current_price(self, ticker):
        """현재가 조회"""
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1d")
            if not hist.empty:
                return hist['Close'].iloc[-1]
        except:
            pass
        return None
    
    def create_portfolio_dashboard(self, portfolio_metrics):
        """포트폴리오 대시보드 생성"""
        if not portfolio_metrics or not portfolio_metrics['items']:
            st.info("포트폴리오 데이터가 없습니다.")
            return
        
        st.markdown("### 📊 포트폴리오 대시보드")
        
        # 전체 요약
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("총 투자금액", f"{portfolio_metrics['total_invested']:,.0f}원")
        with col2:
            st.metric("현재 평가액", f"{portfolio_metrics['total_value']:,.0f}원")
        with col3:
            st.metric("총 손익", f"{portfolio_metrics['total_profit_loss']:,.0f}원", 
                     delta=f"{portfolio_metrics['total_profit_rate']:.2f}%")
        with col4:
            diversification_score = self._calculate_diversification_score(portfolio_metrics['items'])
            st.metric("분산도 점수", f"{diversification_score:.1f}/10")
        
        # 포트폴리오 구성 차트
        col1, col2 = st.columns(2)
        
        with col1:
            self._create_portfolio_pie_chart(portfolio_metrics['items'])
        
        with col2:
            self._create_profit_loss_chart(portfolio_metrics['items'])
        
        # 상세 테이블
        self._create_portfolio_table(portfolio_metrics['items'])
    
    def _calculate_diversification_score(self, items):
        """분산투자 점수 계산 (0-10점)"""
        if len(items) == 0:
            return 0
        
        # 종목 수 점수 (최대 5점)
        stock_count_score = min(len(items) * 1.25, 5)
        
        # 비중 분산 점수 (최대 5점)
        weights = [item['weight'] for item in items]
        if len(weights) > 1:
            weight_std = np.std(weights)
            # 표준편차가 낮을수록 고른 분산
            weight_score = max(0, 5 - (weight_std / 10))
        else:
            weight_score = 0
        
        return stock_count_score + weight_score
    
    def _create_portfolio_pie_chart(self, items):
        """포트폴리오 구성 파이 차트"""
        labels = [item['stock'] for item in items]
        values = [item['current_value'] for item in items]
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57', '#FF9FF3', '#54A0FF']
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.3,
            marker_colors=colors[:len(labels)]
        )])
        
        fig.update_layout(
            title="포트폴리오 구성 비중",
            height=400,
            showlegend=True,
            legend=dict(orientation="v", yanchor="middle", y=0.5)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _create_profit_loss_chart(self, items):
        """수익률 바 차트"""
        stocks = [item['stock'] for item in items]
        profit_rates = [item['profit_rate'] for item in items]
        colors = ['green' if rate >= 0 else 'red' for rate in profit_rates]
        
        fig = go.Figure(data=[
            go.Bar(
                x=stocks,
                y=profit_rates,
                marker_color=colors,
                text=[f"{rate:+.1f}%" for rate in profit_rates],
                textposition='outside'
            )
        ])
        
        fig.update_layout(
            title="종목별 수익률",
            yaxis_title="수익률 (%)",
            height=400,
            xaxis_tickangle=-45
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _create_portfolio_table(self, items):
        """포트폴리오 상세 테이블"""
        st.markdown("### 📋 보유 종목 상세")
        
        df = pd.DataFrame(items)
        if not df.empty:
            # 필요한 컬럼만 선택하고 형식 지정
            display_df = df[['stock', 'shares', 'buy_price', 'current_price', 
                           'invested_amount', 'current_value', 'profit_loss', 
                           'profit_rate', 'weight']].copy()
            
            # 컬럼명 한글화
            display_df.columns = ['종목명', '보유주수', '매수가', '현재가', 
                                '투자금액', '평가금액', '손익', '수익률(%)', '비중(%)']
            
            # 숫자 형식 지정
            for col in ['매수가', '현재가', '투자금액', '평가금액', '손익']:
                display_df[col] = display_df[col].apply(lambda x: f"{x:,.0f}원")
            
            display_df['수익률(%)'] = display_df['수익률(%)'].apply(lambda x: f"{x:+.2f}%")
            display_df['비중(%)'] = display_df['비중(%)'].apply(lambda x: f"{x:.1f}%")
            
            st.dataframe(display_df, use_container_width=True)

class MarketSentimentAnalyzer:
    """시장 심리 분석 클래스"""
    
    def __init__(self):
        self.fear_greed_index = self._calculate_fear_greed_index()
    
    def _calculate_fear_greed_index(self):
        """공포탐욕지수 계산 (간단 버전)"""
        try:
            market_data = get_real_time_market_data()
            
            # 주요 지수들의 변동률로 간단 계산
            changes = []
            for name, data in market_data.items():
                if name in ['KOSPI', 'NASDAQ', 'S&P 500']:
                    changes.append(data.get('change', 0))
            
            if changes:
                avg_change = np.mean(changes)
                # -5% ~ +5% 범위를 0~100으로 매핑
                normalized_score = max(0, min(100, (avg_change + 5) * 10))
                return {
                    'score': normalized_score,
                    'label': self._get_sentiment_label(normalized_score),
                    'color': self._get_sentiment_color(normalized_score)
                }
        except:
            pass
        
        return {'score': 50, 'label': '중립', 'color': 'yellow'}
    
    def _get_sentiment_label(self, score):
        """심리 라벨 반환"""
        if score < 20:
            return "극도 공포"
        elif score < 40:
            return "공포"
        elif score < 60:
            return "중립"
        elif score < 80:
            return "탐욕"
        else:
            return "극도 탐욕"
    
    def _get_sentiment_color(self, score):
        """심리 색상 반환"""
        if score < 20:
            return "#FF0000"  # 빨강
        elif score < 40:
            return "#FF6B00"  # 주황
        elif score < 60:
            return "#FFFF00"  # 노랑
        elif score < 80:
            return "#9AFF00"  # 연두
        else:
            return "#00FF00"  # 초록
    
    def render_sentiment_widget(self):
        """시장 심리 위젯 렌더링"""
        st.markdown("### 🎭 시장 심리 지수")
        
        col1, col2 = st.columns([2, 3])
        
        with col1:
            # 게이지 차트
            fig = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = self.fear_greed_index['score'],
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "공포/탐욕 지수"},
                delta = {'reference': 50},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': self.fear_greed_index['color']},
                    'steps': [
                        {'range': [0, 20], 'color': "lightgray"},
                        {'range': [20, 40], 'color': "gray"},
                        {'range': [40, 60], 'color': "lightblue"},
                        {'range': [60, 80], 'color': "lightgreen"},
                        {'range': [80, 100], 'color': "green"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': self.fear_greed_index['score']
                    }
                }
            ))
            
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.metric(
                "현재 시장 심리",
                self.fear_greed_index['label'],
                f"{self.fear_greed_index['score']:.0f}/100"
            )
            
            # 해석 가이드
            if self.fear_greed_index['score'] < 40:
                st.info("💡 **매수 기회**: 공포 상황에서는 우량주 매수 기회가 될 수 있습니다.")
            elif self.fear_greed_index['score'] > 70:
                st.warning("⚠️ **주의**: 과도한 탐욕 상황에서는 차익실현을 고려해보세요.")
            else:
                st.success("✅ **균형**: 적절한 시장 심리 상태입니다.")

class TechnicalAnalyzer:
    """기술적 분석 클래스"""
    
    def calculate_technical_indicators(self, ticker, period="3mo"):
        """기술적 지표 계산"""
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(period=period)
            
            if data.empty:
                return None
            
            # 이동평균선
            data['MA5'] = data['Close'].rolling(window=5).mean()
            data['MA20'] = data['Close'].rolling(window=20).mean()
            data['MA60'] = data['Close'].rolling(window=60).mean()
            
            # RSI 계산
            data['RSI'] = self._calculate_rsi(data['Close'])
            
            # MACD 계산
            exp1 = data['Close'].ewm(span=12).mean()
            exp2 = data['Close'].ewm(span=26).mean()
            data['MACD'] = exp1 - exp2
            data['Signal'] = data['MACD'].ewm(span=9).mean()
            
            # 볼린저 밴드
            rolling_mean = data['Close'].rolling(window=20).mean()
            rolling_std = data['Close'].rolling(window=20).std()
            data['BB_Upper'] = rolling_mean + (rolling_std * 2)
            data['BB_Lower'] = rolling_mean - (rolling_std * 2)
            
            return data
            
        except Exception as e:
            st.error(f"기술적 분석 오류: {e}")
            return None
    
    def _calculate_rsi(self, prices, window=14):
        """RSI 계산"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def create_technical_chart(self, data, ticker):
        """기술적 분석 차트 생성"""
        if data is None or data.empty:
            st.error("차트 데이터가 없습니다.")
            return
        
        # 서브플롯 생성
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.1,
            subplot_titles=(f'{ticker} 주가 및 이동평균', 'RSI', 'MACD'),
            row_width=[0.2, 0.2, 0.7]
        )
        
        # 캔들스틱과 이동평균
        fig.add_trace(
            go.Candlestick(
                x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name="Price"
            ), row=1, col=1
        )
        
        # 이동평균선
        fig.add_trace(go.Scatter(x=data.index, y=data['MA5'], name='MA5', line=dict(color='red')), row=1, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=data['MA20'], name='MA20', line=dict(color='blue')), row=1, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=data['MA60'], name='MA60', line=dict(color='green')), row=1, col=1)
        
        # 볼린저 밴드
        fig.add_trace(go.Scatter(x=data.index, y=data['BB_Upper'], name='BB Upper', line=dict(color='gray', dash='dash')), row=1, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=data['BB_Lower'], name='BB Lower', line=dict(color='gray', dash='dash')), row=1, col=1)
        
        # RSI
        fig.add_trace(go.Scatter(x=data.index, y=data['RSI'], name='RSI', line=dict(color='purple')), row=2, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
        
        # MACD
        fig.add_trace(go.Scatter(x=data.index, y=data['MACD'], name='MACD', line=dict(color='blue')), row=3, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=data['Signal'], name='Signal', line=dict(color='red')), row=3, col=1)
        
        fig.update_layout(
            title=f"{ticker} 기술적 분석",
            height=800,
            showlegend=False,
            xaxis_rangeslider_visible=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def get_technical_signals(self, data):
        """기술적 신호 분석"""
        if data is None or data.empty:
            return {}
        
        latest = data.iloc[-1]
        signals = {}
        
        # 이동평균 신호
        if latest['Close'] > latest['MA5'] > latest['MA20']:
            signals['ma_signal'] = "강한 상승 추세"
            signals['ma_color'] = "green"
        elif latest['Close'] < latest['MA5'] < latest['MA20']:
            signals['ma_signal'] = "강한 하락 추세"
            signals['ma_color'] = "red"
        else:
            signals['ma_signal'] = "횡보 또는 혼재"
            signals['ma_color'] = "orange"
        
        # RSI 신호
        rsi = latest['RSI']
        if rsi > 70:
            signals['rsi_signal'] = f"과매수 구간 (RSI: {rsi:.1f})"
            signals['rsi_color'] = "red"
        elif rsi < 30:
            signals['rsi_signal'] = f"과매도 구간 (RSI: {rsi:.1f})"
            signals['rsi_color'] = "green"
        else:
            signals['rsi_signal'] = f"정상 구간 (RSI: {rsi:.1f})"
            signals['rsi_color'] = "blue"
        
        # MACD 신호
        if latest['MACD'] > latest['Signal']:
            signals['macd_signal'] = "매수 신호"
            signals['macd_color'] = "green"
        else:
            signals['macd_signal'] = "매도 신호"
            signals['macd_color'] = "red"
        
        # 볼린저 밴드 신호
        if latest['Close'] > latest['BB_Upper']:
            signals['bb_signal'] = "상단 돌파 (과매수 주의)"
            signals['bb_color'] = "red"
        elif latest['Close'] < latest['BB_Lower']:
            signals['bb_signal'] = "하단 이탈 (과매도 반등 가능)"
            signals['bb_color'] = "green"
        else:
            signals['bb_signal'] = "정상 구간"
            signals['bb_color'] = "blue"
        
        return signals

class NewsAnalyzer:
    """뉴스 감정 분석 클래스"""
    
    def __init__(self):
        self.positive_keywords = ['상승', '증가', '성장', '호조', '개선', '긍정', '상향', '확대']
        self.negative_keywords = ['하락', '감소', '둔화', '부진', '악화', '우려', '하향', '축소']
    
    def analyze_news_sentiment(self, news_data):
        """뉴스 감정 분석"""
        if not news_data:
            return {'score': 0, 'label': '중립', 'details': []}
        
        sentiment_scores = []
        details = []
        
        for article in news_data[:10]:  # 최근 10개 뉴스
            title = article.get('title', '')
            summary = article.get('summary', '')
            text = f"{title} {summary}".lower()
            
            positive_count = sum(1 for keyword in self.positive_keywords if keyword in text)
            negative_count = sum(1 for keyword in self.negative_keywords if keyword in text)
            
            if positive_count > negative_count:
                score = 1
                sentiment = "긍정적"
            elif negative_count > positive_count:
                score = -1
                sentiment = "부정적"
            else:
                score = 0
                sentiment = "중립"
            
            sentiment_scores.append(score)
            details.append({
                'title': title[:50] + '...' if len(title) > 50 else title,
                'sentiment': sentiment,
                'score': score
            })
        
        overall_score = np.mean(sentiment_scores) if sentiment_scores else 0
        
        if overall_score > 0.3:
            label = "긍정적"
        elif overall_score < -0.3:
            label = "부정적"
        else:
            label = "중립"
        
        return {
            'score': overall_score,
            'label': label,
            'details': details
        }
    
    def render_news_sentiment(self, news_data):
        """뉴스 감정 분석 결과 렌더링"""
        st.markdown("### 📰 뉴스 감정 분석")
        
        sentiment_result = self.analyze_news_sentiment(news_data)
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            score = sentiment_result['score']
            color = "green" if score > 0 else "red" if score < 0 else "gray"
            
            st.metric(
                "뉴스 감정 점수",
                sentiment_result['label'],
                f"{score:+.2f}"
            )
            
            # 감정 게이지
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = score * 100,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "감정 지수"},
                gauge = {
                    'axis': {'range': [-100, 100]},
                    'bar': {'color': color},
                    'steps': [
                        {'range': [-100, -30], 'color': "lightcoral"},
                        {'range': [-30, 30], 'color': "lightgray"},
                        {'range': [30, 100], 'color': "lightgreen"}
                    ]
                }
            ))
            
            fig.update_layout(height=250)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("**개별 뉴스 감정 분석**")
            for detail in sentiment_result['details'][:5]:
                sentiment_color = "🟢" if detail['score'] > 0 else "🔴" if detail['score'] < 0 else "🟡"
                st.write(f"{sentiment_color} {detail['sentiment']}: {detail['title']}")

class AlertSystem:
    """알림 시스템 클래스"""
    
    def __init__(self):
        self.alerts = []
    
    def check_portfolio_alerts(self, portfolio_metrics):
        """포트폴리오 알림 체크"""
        alerts = []
        
        if portfolio_metrics and portfolio_metrics.get('items'):
            for item in portfolio_metrics['items']:
                # 큰 손실 알림
                if item['profit_rate'] <= -20:
                    alerts.append({
                        'type': 'danger',
                        'title': f"{item['stock']} 큰 손실 발생",
                        'message': f"현재 {item['profit_rate']:.1f}% 손실 상태입니다. 손절매를 고려해보세요.",
                        'action': "손절매 검토"
                    })
                
                # 큰 수익 알림
                elif item['profit_rate'] >= 30:
                    alerts.append({
                        'type': 'success',
                        'title': f"{item['stock']} 큰 수익 달성",
                        'message': f"현재 {item['profit_rate']:.1f}% 수익 상태입니다. 차익실현을 고려해보세요.",
                        'action': "차익실현 검토"
                    })
                
                # 집중투자 경고
                if item['weight'] > 40:
                    alerts.append({
                        'type': 'warning',
                        'title': f"{item['stock']} 집중투자 위험",
                        'message': f"포트폴리오의 {item['weight']:.1f}%를 차지하고 있습니다. 분산투자를 고려해보세요.",
                        'action': "분산투자 검토"
                    })
        
        return alerts
    
    def check_market_alerts(self):
        """시장 알림 체크"""
        alerts = []
        market_data = get_real_time_market_data()
        
        for name, data in market_data.items():
            change = data.get('change', 0)
            
            # 급락 알림
            if change <= -5:
                alerts.append({
                    'type': 'danger',
                    'title': f"{name} 급락 발생",
                    'message': f"현재 {change:.2f}% 하락 중입니다.",
                    'action': "시장 모니터링"
                })
            
            # 급등 알림
            elif change >= 5:
                alerts.append({
                    'type': 'success',
                    'title': f"{name} 급등 발생",
                    'message': f"현재 {change:.2f}% 상승 중입니다.",
                    'action': "수익실현 고려"
                })
        
        return alerts
    
    def render_alerts(self, portfolio_metrics=None):
        """알림 렌더링"""
        portfolio_alerts = self.check_portfolio_alerts(portfolio_metrics) if portfolio_metrics else []
        market_alerts = self.check_market_alerts()
        
        all_alerts = portfolio_alerts + market_alerts
        
        if not all_alerts:
            return
        
        st.markdown("### 🚨 실시간 알림")
        
        for alert in all_alerts[:5]:  # 최대 5개까지
            if alert['type'] == 'danger':
                st.error(f"⚠️ **{alert['title']}**: {alert['message']} ({alert['action']})")
            elif alert['type'] == 'warning':
                st.warning(f"⚠️ **{alert['title']}**: {alert['message']} ({alert['action']})")
            else:
                st.success(f"✅ **{alert['title']}**: {alert['message']} ({alert['action']})")

class AdvancedAnalytics:
    """고급 분석 통합 클래스"""
    
    def __init__(self):
        self.portfolio_analyzer = PortfolioAnalyzer()
        self.sentiment_analyzer = MarketSentimentAnalyzer()
        self.technical_analyzer = TechnicalAnalyzer()
        self.news_analyzer = NewsAnalyzer()
        self.alert_system = AlertSystem()
    
    def render_advanced_dashboard(self, portfolio_data=None, news_data=None):
        """고급 대시보드 렌더링"""
        st.markdown("## 🚀 고급 분석 대시보드")
        
        # 탭 생성
        tab1, tab2, tab3, tab4 = st.tabs(["📊 포트폴리오", "🎭 시장심리", "📈 기술분석", "📰 뉴스분석"])
        
        with tab1:
            if portfolio_data:
                portfolio_metrics = self.portfolio_analyzer.calculate_portfolio_metrics(portfolio_data)
                self.portfolio_analyzer.create_portfolio_dashboard(portfolio_metrics)
                
                # 알림 표시
                self.alert_system.render_alerts(portfolio_metrics)
            else:
                st.info("포트폴리오 데이터를 입력하시면 상세 분석을 제공합니다.")
        
        with tab2:
            self.sentiment_analyzer.render_sentiment_widget()
            
            # 시장 알림
            market_alerts = self.alert_system.check_market_alerts()
            if market_alerts:
                st.markdown("### 🚨 시장 알림")
                for alert in market_alerts[:3]:
                    if alert['type'] == 'danger':
                        st.error(f"⚠️ {alert['title']}: {alert['message']}")
                    else:
                        st.success(f"✅ {alert['title']}: {alert['message']}")
        
        with tab3:
            st.markdown("### 📈 기술적 분석")
            
            # 종목 선택
            ticker_input = st.selectbox(
                "분석할 종목을 선택하세요:",
                options=list(Config.DEFAULT_STOCKS.values()),
                format_func=lambda x: next(k for k, v in Config.DEFAULT_STOCKS.items() if v == x)
            )
            
            if ticker_input:
                with st.spinner("기술적 분석 중..."):
                    tech_data = self.technical_analyzer.calculate_technical_indicators(ticker_input)
                    
                    if tech_data is not None:
                        # 기술적 신호
                        signals = self.technical_analyzer.get_technical_signals(tech_data)
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("이동평균", signals.get('ma_signal', 'N/A'))
                        with col2:
                            st.metric("RSI", signals.get('rsi_signal', 'N/A'))
                        with col3:
                            st.metric("MACD", signals.get('macd_signal', 'N/A'))
                        with col4:
                            st.metric("볼린저밴드", signals.get('bb_signal', 'N/A'))
                        
                        # 차트
                        self.technical_analyzer.create_technical_chart(tech_data, ticker_input)
        
        with tab4:
            if news_data:
                self.news_analyzer.render_news_sentiment(news_data)
            else:
                st.info("뉴스 데이터를 불러오는 중...")

def integrate_advanced_features():
    """고급 기능을 메인 앱에 통합"""
    if 'advanced_analytics' not in st.session_state:
        st.session_state.advanced_analytics = AdvancedAnalytics()
    
    return st.session_state.advanced_analytics
