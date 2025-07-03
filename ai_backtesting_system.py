"""
ai_backtesting_system.py - AI 기반 백테스팅 및 종목 추천 시스템
실제 투자자를 위한 고급 기능 - 전략 검증 및 AI 추천
"""

import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from datetime import datetime, timedelta
import ta
from typing import Dict, List, Optional, Tuple
import warnings
import math
from dataclasses import dataclass
warnings.filterwarnings('ignore')

@dataclass
class BacktestResult:
    """백테스트 결과 데이터 클래스"""
    total_return: float
    annual_return: float
    volatility: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    total_trades: int
    avg_holding_period: float
    equity_curve: pd.Series
    trades: List[Dict]
    benchmark_return: float

class TradingStrategy:
    """트레이딩 전략 기본 클래스"""
    
    def __init__(self, name: str):
        self.name = name
        self.signals = []
        
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """매매 신호 생성 (하위 클래스에서 구현)"""
        raise NotImplementedError

class MovingAverageCrossStrategy(TradingStrategy):
    """이동평균 교차 전략"""
    
    def __init__(self, short_window: int = 20, long_window: int = 50):
        super().__init__("이동평균 교차 전략")
        self.short_window = short_window
        self.long_window = long_window
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """이동평균 교차 신호 생성"""
        signals = data.copy()
        
        # 이동평균 계산
        signals['MA_Short'] = signals['Close'].rolling(window=self.short_window).mean()
        signals['MA_Long'] = signals['Close'].rolling(window=self.long_window).mean()
        
        # 신호 생성
        signals['Signal'] = 0
        signals['Signal'][self.short_window:] = np.where(
            signals['MA_Short'][self.short_window:] > signals['MA_Long'][self.short_window:], 1, 0
        )
        signals['Position'] = signals['Signal'].diff()
        
        return signals

class RSIStrategy(TradingStrategy):
    """RSI 전략"""
    
    def __init__(self, rsi_period: int = 14, oversold: int = 30, overbought: int = 70):
        super().__init__("RSI 전략")
        self.rsi_period = rsi_period
        self.oversold = oversold
        self.overbought = overbought
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """RSI 기반 신호 생성"""
        signals = data.copy()
        
        # RSI 계산
        signals['RSI'] = ta.momentum.rsi(signals['Close'], window=self.rsi_period)
        
        # 신호 생성
        signals['Signal'] = 0
        signals.loc[signals['RSI'] < self.oversold, 'Signal'] = 1  # 매수
        signals.loc[signals['RSI'] > self.overbought, 'Signal'] = -1  # 매도
        
        # 포지션 계산
        signals['Position'] = signals['Signal'].shift(1).fillna(0)
        
        return signals

class MACDStrategy(TradingStrategy):
    """MACD 전략"""
    
    def __init__(self, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9):
        super().__init__("MACD 전략")
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """MACD 기반 신호 생성"""
        signals = data.copy()
        
        # MACD 계산
        exp1 = signals['Close'].ewm(span=self.fast_period).mean()
        exp2 = signals['Close'].ewm(span=self.slow_period).mean()
        signals['MACD'] = exp1 - exp2
        signals['MACD_Signal'] = signals['MACD'].ewm(span=self.signal_period).mean()
        signals['MACD_Histogram'] = signals['MACD'] - signals['MACD_Signal']
        
        # 신호 생성 (MACD가 시그널선을 돌파할 때)
        signals['Signal'] = 0
        signals['Signal'] = np.where(signals['MACD'] > signals['MACD_Signal'], 1, 0)
        signals['Position'] = signals['Signal'].diff()
        
        return signals

class BollingerBandStrategy(TradingStrategy):
    """볼린저 밴드 전략"""
    
    def __init__(self, window: int = 20, num_std: float = 2):
        super().__init__("볼린저 밴드 전략")
        self.window = window
        self.num_std = num_std
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """볼린저 밴드 기반 신호 생성"""
        signals = data.copy()
        
        # 볼린저 밴드 계산
        signals['BB_Middle'] = signals['Close'].rolling(window=self.window).mean()
        bb_std = signals['Close'].rolling(window=self.window).std()
        signals['BB_Upper'] = signals['BB_Middle'] + (bb_std * self.num_std)
        signals['BB_Lower'] = signals['BB_Middle'] - (bb_std * self.num_std)
        
        # 신호 생성 (밴드 터치 시 역방향 매매)
        signals['Signal'] = 0
        signals.loc[signals['Close'] <= signals['BB_Lower'], 'Signal'] = 1  # 매수
        signals.loc[signals['Close'] >= signals['BB_Upper'], 'Signal'] = -1  # 매도
        
        signals['Position'] = signals['Signal'].shift(1).fillna(0)
        
        return signals

class BacktestEngine:
    """백테스팅 엔진"""
    
    def __init__(self, initial_capital: float = 1000000, commission: float = 0.0015):
        self.initial_capital = initial_capital
        self.commission = commission
        
    def run_backtest(self, data: pd.DataFrame, strategy: TradingStrategy, 
                    benchmark_ticker: str = "^KS11") -> BacktestResult:
        """백테스트 실행"""
        
        # 전략 신호 생성
        signals = strategy.generate_signals(data)
        
        # 벤치마크 데이터 가져오기
        benchmark_data = self._get_benchmark_data(benchmark_ticker, data.index[0], data.index[-1])
        
        # 포트폴리오 계산
        portfolio = self._calculate_portfolio(signals)
        
        # 성과 지표 계산
        results = self._calculate_performance_metrics(portfolio, benchmark_data)
        
        # 거래 내역 생성
        trades = self._generate_trade_log(signals)
        
        return BacktestResult(
            total_return=results['total_return'],
            annual_return=results['annual_return'],
            volatility=results['volatility'],
            sharpe_ratio=results['sharpe_ratio'],
            max_drawdown=results['max_drawdown'],
            win_rate=results['win_rate'],
            profit_factor=results['profit_factor'],
            total_trades=len(trades),
            avg_holding_period=results['avg_holding_period'],
            equity_curve=portfolio['Portfolio_Value'],
            trades=trades,
            benchmark_return=results['benchmark_return']
        )
    
    def _get_benchmark_data(self, ticker: str, start_date, end_date) -> pd.DataFrame:
        """벤치마크 데이터 조회"""
        try:
            benchmark = yf.Ticker(ticker)
            data = benchmark.history(start=start_date, end=end_date)
            return data
        except:
            return pd.DataFrame()
    
    def _calculate_portfolio(self, signals: pd.DataFrame) -> pd.DataFrame:
        """포트폴리오 가치 계산"""
        portfolio = signals.copy()
        
        # 초기 설정
        portfolio['Holdings'] = 0
        portfolio['Cash'] = self.initial_capital
        portfolio['Portfolio_Value'] = self.initial_capital
        portfolio['Returns'] = 0
        
        position = 0
        cash = self.initial_capital
        
        for i in range(1, len(portfolio)):
            # 이전 상태
            prev_position = position
            prev_cash = cash
            
            # 현재 신호
            current_signal = portfolio['Position'].iloc[i]
            current_price = portfolio['Close'].iloc[i]
            
            # 매수 신호
            if current_signal == 1 and position == 0:
                # 전체 현금으로 매수 (수수료 제외)
                shares_to_buy = int((cash * (1 - self.commission)) / current_price)
                if shares_to_buy > 0:
                    position = shares_to_buy
                    cash = cash - (shares_to_buy * current_price * (1 + self.commission))
            
            # 매도 신호
            elif current_signal == -1 and position > 0:
                # 전체 보유주식 매도
                cash = cash + (position * current_price * (1 - self.commission))
                position = 0
            
            # 포트폴리오 가치 계산
            portfolio_value = cash + (position * current_price)
            
            portfolio.loc[portfolio.index[i], 'Holdings'] = position
            portfolio.loc[portfolio.index[i], 'Cash'] = cash
            portfolio.loc[portfolio.index[i], 'Portfolio_Value'] = portfolio_value
            
            # 수익률 계산
            if i > 0:
                prev_value = portfolio['Portfolio_Value'].iloc[i-1]
                returns = (portfolio_value - prev_value) / prev_value
                portfolio.loc[portfolio.index[i], 'Returns'] = returns
        
        return portfolio
    
    def _calculate_performance_metrics(self, portfolio: pd.DataFrame, benchmark: pd.DataFrame) -> Dict:
        """성과 지표 계산"""
        
        # 기본 수익률 계산
        final_value = portfolio['Portfolio_Value'].iloc[-1]
        total_return = (final_value - self.initial_capital) / self.initial_capital
        
        # 연간 수익률
        days = (portfolio.index[-1] - portfolio.index[0]).days
        annual_return = (1 + total_return) ** (365 / days) - 1
        
        # 변동성 (연간)
        daily_returns = portfolio['Returns'].dropna()
        volatility = daily_returns.std() * np.sqrt(252)
        
        # 샤프 비율 (무위험 수익률 3% 가정)
        risk_free_rate = 0.03
        sharpe_ratio = (annual_return - risk_free_rate) / volatility if volatility > 0 else 0
        
        # 최대 낙폭 (Maximum Drawdown)
        running_max = portfolio['Portfolio_Value'].expanding().max()
        drawdown = (portfolio['Portfolio_Value'] - running_max) / running_max
        max_drawdown = drawdown.min()
        
        # 승률 및 손익비
        profitable_trades = (daily_returns > 0).sum()
        total_trade_days = len(daily_returns[daily_returns != 0])
        win_rate = profitable_trades / total_trade_days if total_trade_days > 0 else 0
        
        # 손익비 계산
        winning_returns = daily_returns[daily_returns > 0]
        losing_returns = daily_returns[daily_returns < 0]
        
        avg_win = winning_returns.mean() if len(winning_returns) > 0 else 0
        avg_loss = abs(losing_returns.mean()) if len(losing_returns) > 0 else 0
        profit_factor = avg_win / avg_loss if avg_loss > 0 else 0
        
        # 평균 보유기간 계산
        position_changes = portfolio['Holdings'].diff().abs()
        trades = position_changes[position_changes > 0]
        avg_holding_period = len(portfolio) / len(trades) if len(trades) > 0 else 0
        
        # 벤치마크 수익률
        benchmark_return = 0
        if not benchmark.empty:
            benchmark_start = benchmark['Close'].iloc[0]
            benchmark_end = benchmark['Close'].iloc[-1]
            benchmark_return = (benchmark_end - benchmark_start) / benchmark_start
        
        return {
            'total_return': total_return,
            'annual_return': annual_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'avg_holding_period': avg_holding_period,
            'benchmark_return': benchmark_return
        }
    
    def _generate_trade_log(self, signals: pd.DataFrame) -> List[Dict]:
        """거래 로그 생성"""
        trades = []
        current_trade = None
        
        for i, (date, row) in enumerate(signals.iterrows()):
            if row['Position'] == 1:  # 매수
                current_trade = {
                    'entry_date': date,
                    'entry_price': row['Close'],
                    'type': 'LONG'
                }
            elif row['Position'] == -1 and current_trade:  # 매도
                current_trade.update({
                    'exit_date': date,
                    'exit_price': row['Close'],
                    'holding_days': (date - current_trade['entry_date']).days,
                    'return_pct': (row['Close'] - current_trade['entry_price']) / current_trade['entry_price'] * 100
                })
                trades.append(current_trade)
                current_trade = None
        
        return trades

class AIStockRecommender:
    """AI 기반 종목 추천 시스템"""
    
    def __init__(self):
        self.weight_factors = {
            'technical_score': 0.3,
            'momentum_score': 0.25,
            'volatility_score': 0.2,
            'volume_score': 0.15,
            'trend_score': 0.1
        }
    
    def analyze_stock_universe(self, tickers: List[str], period: str = "3mo") -> pd.DataFrame:
        """종목군 분석"""
        
        stock_scores = []
        
        for ticker in tickers:
            try:
                # 주식 데이터 수집
                stock = yf.Ticker(ticker)
                data = stock.history(period=period)
                
                if len(data) < 20:  # 최소 데이터 요구량
                    continue
                
                # 각종 점수 계산
                scores = self._calculate_stock_scores(data, ticker)
                stock_scores.append(scores)
                
            except Exception as e:
                st.warning(f"{ticker} 분석 중 오류: {str(e)}")
                continue
        
        if not stock_scores:
            return pd.DataFrame()
        
        # 데이터프레임으로 변환
        df = pd.DataFrame(stock_scores)
        
        # 종합 점수 계산
        df['total_score'] = (
            df['technical_score'] * self.weight_factors['technical_score'] +
            df['momentum_score'] * self.weight_factors['momentum_score'] +
            df['volatility_score'] * self.weight_factors['volatility_score'] +
            df['volume_score'] * self.weight_factors['volume_score'] +
            df['trend_score'] * self.weight_factors['trend_score']
        )
        
        # 점수 순으로 정렬
        df = df.sort_values('total_score', ascending=False)
        
        return df
    
    def _calculate_stock_scores(self, data: pd.DataFrame, ticker: str) -> Dict:
        """개별 종목 점수 계산"""
        
        # 기술적 지표 계산
        rsi = ta.momentum.rsi(data['Close'], window=14).iloc[-1]
        
        # 이동평균 관련
        sma_20 = data['Close'].rolling(20).mean()
        sma_50 = data['Close'].rolling(50).mean()
        current_price = data['Close'].iloc[-1]
        
        # 볼린저 밴드
        bb_upper = ta.volatility.bollinger_hband(data['Close']).iloc[-1]
        bb_lower = ta.volatility.bollinger_lband(data['Close']).iloc[-1]
        bb_middle = ta.volatility.bollinger_mavg(data['Close']).iloc[-1]
        
        # MACD
        macd_line = ta.trend.macd(data['Close']).iloc[-1]
        macd_signal = ta.trend.macd_signal(data['Close']).iloc[-1]
        
        # 점수 계산
        scores = {
            'ticker': ticker,
            'current_price': current_price,
            'technical_score': self._calculate_technical_score(rsi, current_price, sma_20.iloc[-1], sma_50.iloc[-1]),
            'momentum_score': self._calculate_momentum_score(data['Close']),
            'volatility_score': self._calculate_volatility_score(data['Close']),
            'volume_score': self._calculate_volume_score(data['Volume']),
            'trend_score': self._calculate_trend_score(data['Close']),
            'rsi': rsi,
            'price_vs_sma20': (current_price - sma_20.iloc[-1]) / sma_20.iloc[-1] * 100,
            'price_vs_sma50': (current_price - sma_50.iloc[-1]) / sma_50.iloc[-1] * 100,
            'bb_position': (current_price - bb_lower) / (bb_upper - bb_lower) * 100,
            'macd_signal': 'BUY' if macd_line > macd_signal else 'SELL'
        }
        
        return scores
    
    def _calculate_technical_score(self, rsi: float, current_price: float, sma20: float, sma50: float) -> float:
        """기술적 분석 점수"""
        score = 50  # 기본 점수
        
        # RSI 점수 (30-70 구간이 좋음)
        if 40 <= rsi <= 60:
            score += 20
        elif 30 <= rsi <= 70:
            score += 10
        elif rsi < 30:
            score += 15  # 과매도에서 반등 기대
        
        # 이동평균 점수
        if current_price > sma20 > sma50:
            score += 20  # 상승 추세
        elif current_price > sma20:
            score += 10
        elif current_price < sma20 < sma50:
            score -= 10  # 하락 추세
        
        return min(100, max(0, score))
    
    def _calculate_momentum_score(self, prices: pd.Series) -> float:
        """모멘텀 점수"""
        # 최근 1주일, 1개월 수익률
        returns_1w = (prices.iloc[-1] - prices.iloc[-5]) / prices.iloc[-5] * 100 if len(prices) >= 5 else 0
        returns_1m = (prices.iloc[-1] - prices.iloc[-20]) / prices.iloc[-20] * 100 if len(prices) >= 20 else 0
        
        score = 50
        
        # 단기 모멘텀
        if returns_1w > 5:
            score += 25
        elif returns_1w > 2:
            score += 15
        elif returns_1w < -5:
            score -= 25
        elif returns_1w < -2:
            score -= 15
        
        # 중기 모멘텀
        if returns_1m > 10:
            score += 15
        elif returns_1m > 5:
            score += 10
        elif returns_1m < -10:
            score -= 15
        elif returns_1m < -5:
            score -= 10
        
        return min(100, max(0, score))
    
    def _calculate_volatility_score(self, prices: pd.Series) -> float:
        """변동성 점수 (낮은 변동성이 더 좋은 점수)"""
        returns = prices.pct_change().dropna()
        volatility = returns.std() * np.sqrt(252) * 100  # 연간 변동성 (%)
        
        if volatility < 15:
            return 80
        elif volatility < 25:
            return 60
        elif volatility < 35:
            return 40
        elif volatility < 50:
            return 20
        else:
            return 10
    
    def _calculate_volume_score(self, volumes: pd.Series) -> float:
        """거래량 점수"""
        if len(volumes) < 10:
            return 50
        
        recent_volume = volumes.iloc[-5:].mean()  # 최근 5일 평균
        historical_volume = volumes.iloc[:-5].mean()  # 이전 평균
        
        volume_ratio = recent_volume / historical_volume if historical_volume > 0 else 1
        
        if volume_ratio > 1.5:
            return 80  # 거래량 급증
        elif volume_ratio > 1.2:
            return 70
        elif volume_ratio > 0.8:
            return 60
        else:
            return 40  # 거래량 감소
    
    def _calculate_trend_score(self, prices: pd.Series) -> float:
        """추세 점수"""
        if len(prices) < 20:
            return 50
        
        # 선형 회귀를 이용한 추세 분석
        x = np.arange(len(prices))
        y = prices.values
        
        # 기울기 계산
        slope = np.polyfit(x, y, 1)[0]
        
        # 추세 강도
        price_change = (prices.iloc[-1] - prices.iloc[0]) / prices.iloc[0] * 100
        
        if slope > 0 and price_change > 5:
            return 80  # 강한 상승 추세
        elif slope > 0 and price_change > 2:
            return 70
        elif slope > 0:
            return 60
        elif abs(slope) < 0.1:
            return 50  # 횡보
        else:
            return 30  # 하락 추세

class StrategyOptimizer:
    """전략 최적화 시스템"""
    
    def __init__(self):
        self.optimization_results = []
    
    def optimize_strategy(self, data: pd.DataFrame, strategy_type: str) -> Dict:
        """전략 매개변수 최적화"""
        
        best_result = None
        best_params = None
        best_sharpe = -999
        
        if strategy_type == "MovingAverage":
            # 이동평균 전략 최적화
            short_range = range(5, 25, 5)
            long_range = range(30, 70, 10)
            
            for short in short_range:
                for long in long_range:
                    if short >= long:
                        continue
                    
                    strategy = MovingAverageCrossStrategy(short, long)
                    engine = BacktestEngine()
                    
                    try:
                        result = engine.run_backtest(data, strategy)
                        
                        if result.sharpe_ratio > best_sharpe:
                            best_sharpe = result.sharpe_ratio
                            best_result = result
                            best_params = {'short_window': short, 'long_window': long}
                    except:
                        continue
        
        elif strategy_type == "RSI":
            # RSI 전략 최적화
            rsi_periods = range(10, 25, 2)
            oversold_levels = range(20, 35, 5)
            overbought_levels = range(65, 80, 5)
            
            for period in rsi_periods:
                for oversold in oversold_levels:
                    for overbought in overbought_levels:
                        strategy = RSIStrategy(period, oversold, overbought)
                        engine = BacktestEngine()
                        
                        try:
                            result = engine.run_backtest(data, strategy)
                            
                            if result.sharpe_ratio > best_sharpe:
                                best_sharpe = result.sharpe_ratio
                                best_result = result
                                best_params = {
                                    'rsi_period': period,
                                    'oversold': oversold,
                                    'overbought': overbought
                                }
                        except:
                            continue
        
        return {
            'best_result': best_result,
            'best_params': best_params,
            'strategy_type': strategy_type
        }

def render_backtesting_system():
    """백테스팅 시스템 렌더링"""
    st.markdown("## 📊 AI 백테스팅 & 전략 검증")
    
    tab1, tab2, tab3, tab4 = st.tabs(["🔬 전략 백테스트", "🤖 AI 종목 추천", "⚙️ 전략 최적화", "📈 성과 비교"])
    
    with tab1:
        render_strategy_backtest()
    
    with tab2:
        render_ai_stock_recommender()
    
    with tab3:
        render_strategy_optimizer()
    
    with tab4:
        render_performance_comparison()

def render_strategy_backtest():
    """전략 백테스트 렌더링"""
    st.markdown("### 🔬 트레이딩 전략 백테스트")
    
    # 백테스트 설정
    col1, col2, col3 = st.columns(3)
    
    with col1:
        ticker = st.text_input("종목 코드", value="005930.KS")
        strategy_type = st.selectbox("전략 선택", 
                                   ["이동평균 교차", "RSI", "MACD", "볼린저 밴드"])
    
    with col2:
        period = st.selectbox("백테스트 기간", ["6mo", "1y", "2y", "3y", "5y"])
        initial_capital = st.number_input("초기 자본 (원)", value=10000000, step=1000000)
    
    with col3:
        commission = st.number_input("수수료 (%)", value=0.15, step=0.01) / 100
        benchmark = st.selectbox("벤치마크", ["^KS11", "^KQ11", "^IXIC"])
    
    # 전략별 매개변수 설정
    strategy_params = {}
    
    if strategy_type == "이동평균 교차":
        col1, col2 = st.columns(2)
        with col1:
            strategy_params['short_window'] = st.slider("단기 이동평균", 5, 30, 20)
        with col2:
            strategy_params['long_window'] = st.slider("장기 이동평균", 30, 100, 50)
    
    elif strategy_type == "RSI":
        col1, col2, col3 = st.columns(3)
        with col1:
            strategy_params['rsi_period'] = st.slider("RSI 기간", 10, 30, 14)
        with col2:
            strategy_params['oversold'] = st.slider("과매도 기준", 15, 35, 30)
        with col3:
            strategy_params['overbought'] = st.slider("과매수 기준", 65, 85, 70)
    
    # 백테스트 실행
    if st.button("백테스트 실행", type="primary"):
        if ticker:
            with st.spinner("백테스트 실행 중..."):
                # 데이터 수집
                stock = yf.Ticker(ticker)
                data = stock.history(period=period)
                
                if not data.empty:
                    # 전략 생성
                    if strategy_type == "이동평균 교차":
                        strategy = MovingAverageCrossStrategy(
                            strategy_params['short_window'], 
                            strategy_params['long_window']
                        )
                    elif strategy_type == "RSI":
                        strategy = RSIStrategy(
                            strategy_params['rsi_period'],
                            strategy_params['oversold'],
                            strategy_params['overbought']
                        )
                    elif strategy_type == "MACD":
                        strategy = MACDStrategy()
                    elif strategy_type == "볼린저 밴드":
                        strategy = BollingerBandStrategy()
                    
                    # 백테스트 엔진 생성
                    engine = BacktestEngine(initial_capital, commission)
                    
                    # 백테스트 실행
                    try:
                        result = engine.run_backtest(data, strategy, benchmark)
                        
                        # 결과 표시
                        display_backtest_results(result, ticker, strategy_type)
                        
                    except Exception as e:
                        st.error(f"백테스트 실행 중 오류: {str(e)}")
                else:
                    st.error("주식 데이터를 가져올 수 없습니다.")

def render_ai_stock_recommender():
    """AI 종목 추천 시스템 렌더링"""
    st.markdown("### 🤖 AI 기반 종목 추천")
    
    # 추천 설정
    col1, col2 = st.columns(2)
    
    with col1:
        analysis_universe = st.selectbox("분석 범위", 
                                       ["KOSPI 대형주", "KOSDAQ 성장주", "미국 기술주", "직접 입력"])
        
    with col2:
        recommendation_count = st.slider("추천 종목 수", 5, 20, 10)
    
    # 종목 입력
    if analysis_universe == "직접 입력":
        ticker_input = st.text_area("종목 코드 입력 (쉼표로 구분)", 
                                   placeholder="005930.KS, 035420.KS, 000660.KS")
        tickers = [t.strip() for t in ticker_input.split(',') if t.strip()]
    else:
        # 미리 정의된 종목군
        stock_universes = {
            "KOSPI 대형주": ["005930.KS", "000660.KS", "035420.KS", "035720.KS", "051910.KS", 
                         "005380.KS", "000270.KS", "068270.KS", "005490.KS", "066570.KS"],
            "KOSDAQ 성장주": ["263750.KS", "112040.KS", "036570.KS", "251270.KS", "042700.KS",
                          "214150.KS", "095700.KS", "357780.KS", "240810.KS", "196170.KS"],
            "미국 기술주": ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "NFLX", "ADBE", "CRM"]
        }
        tickers = stock_universes.get(analysis_universe, [])
    
    if st.button("AI 분석 및 추천", type="primary"):
        if tickers:
            recommender = AIStockRecommender()
            
            with st.spinner("AI가 종목을 분석하고 있습니다..."):
                recommendations = recommender.analyze_stock_universe(tickers)
            
            if not recommendations.empty:
                # 상위 추천 종목 표시
                top_recommendations = recommendations.head(recommendation_count)
                
                st.markdown("#### 🏆 AI 추천 종목 (점수 순)")
                
                # 추천 종목 카드 형태로 표시
                for idx, (_, stock) in enumerate(top_recommendations.iterrows()):
                    with st.container():
                        col1, col2, col3, col4 = st.columns([1, 2, 2, 2])
                        
                        with col1:
                            st.markdown(f"### {idx + 1}위")
                        
                        with col2:
                            st.markdown(f"**{stock['ticker']}**")
                            st.caption(f"현재가: {stock['current_price']:,.0f}")
                        
                        with col3:
                            st.metric("AI 점수", f"{stock['total_score']:.1f}/100")
                            st.caption(f"RSI: {stock['rsi']:.1f}")
                        
                        with col4:
                            st.metric("기술적 신호", stock['macd_signal'])
                            st.caption(f"20일선 대비: {stock['price_vs_sma20']:+.1f}%")
                        
                        # 상세 분석 버튼
                        if st.button(f"{stock['ticker']} 상세 분석", key=f"detail_{idx}"):
                            show_detailed_stock_analysis(stock)
                        
                        st.divider()
                
                # 종합 차트
                create_recommendation_chart(top_recommendations)
            else:
                st.warning("분석할 수 있는 종목이 없습니다.")
        else:
            st.warning("분석할 종목을 입력해주세요.")

def render_strategy_optimizer():
    """전략 최적화 렌더링"""
    st.markdown("### ⚙️ 전략 최적화")
    
    st.info("AI가 최적의 매개변수를 찾아드립니다!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        ticker = st.text_input("최적화할 종목", value="005930.KS")
        strategy_type = st.selectbox("최적화할 전략", ["MovingAverage", "RSI"])
    
    with col2:
        period = st.selectbox("최적화 기간", ["1y", "2y", "3y"])
        metric = st.selectbox("최적화 기준", ["샤프 비율", "총 수익률", "최대 낙폭"])
    
    if st.button("전략 최적화 실행", type="primary"):
        optimizer = StrategyOptimizer()
        
        with st.spinner("AI가 최적 매개변수를 찾고 있습니다..."):
            # 데이터 수집
            stock = yf.Ticker(ticker)
            data = stock.history(period=period)
            
            if not data.empty:
                # 최적화 실행
                optimization_result = optimizer.optimize_strategy(data, strategy_type)
                
                if optimization_result['best_result']:
                    result = optimization_result['best_result']
                    params = optimization_result['best_params']
                    
                    st.success("최적화 완료!")
                    
                    # 최적 매개변수 표시
                    st.markdown("#### 🎯 최적 매개변수")
                    
                    param_cols = st.columns(len(params))
                    for i, (param_name, param_value) in enumerate(params.items()):
                        with param_cols[i]:
                            st.metric(param_name.replace('_', ' ').title(), str(param_value))
                    
                    # 최적화 결과 표시
                    display_backtest_results(result, ticker, f"최적화된 {strategy_type}")
                else:
                    st.error("최적화에 실패했습니다.")
            else:
                st.error("데이터를 가져올 수 없습니다.")

def render_performance_comparison():
    """성과 비교 렌더링"""
    st.markdown("### 📈 전략별 성과 비교")
    
    st.info("여러 전략의 성과를 동시에 비교해보세요!")
    
    # 비교할 전략들 설정
    ticker = st.text_input("비교할 종목", value="005930.KS")
    period = st.selectbox("비교 기간", ["1y", "2y", "3y"])
    
    strategies_to_compare = st.multiselect(
        "비교할 전략 선택",
        ["이동평균 교차", "RSI", "MACD", "볼린저 밴드"],
        default=["이동평균 교차", "RSI"]
    )
    
    if st.button("성과 비교 실행", type="primary"):
        if ticker and strategies_to_compare:
            with st.spinner("전략별 백테스트 실행 중..."):
                # 데이터 수집
                stock = yf.Ticker(ticker)
                data = stock.history(period=period)
                
                if not data.empty:
                    results = {}
                    
                    # 각 전략별 백테스트 실행
                    for strategy_name in strategies_to_compare:
                        strategy = create_strategy(strategy_name)
                        engine = BacktestEngine()
                        
                        try:
                            result = engine.run_backtest(data, strategy)
                            results[strategy_name] = result
                        except Exception as e:
                            st.warning(f"{strategy_name} 전략 실행 실패: {str(e)}")
                    
                    if results:
                        # 비교 차트 생성
                        create_performance_comparison_chart(results)
                        
                        # 성과 요약 테이블
                        create_performance_summary_table(results)
                else:
                    st.error("데이터를 가져올 수 없습니다.")

def display_backtest_results(result: BacktestResult, ticker: str, strategy_name: str):
    """백테스트 결과 표시"""
    st.markdown(f"#### 📊 {ticker} - {strategy_name} 백테스트 결과")
    
    # 주요 성과 지표
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("총 수익률", f"{result.total_return:.2%}")
    with col2:
        st.metric("연간 수익률", f"{result.annual_return:.2%}")
    with col3:
        st.metric("샤프 비율", f"{result.sharpe_ratio:.2f}")
    with col4:
        st.metric("최대 낙폭", f"{result.max_drawdown:.2%}")
    
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        st.metric("승률", f"{result.win_rate:.1%}")
    with col6:
        st.metric("손익비", f"{result.profit_factor:.2f}")
    with col7:
        st.metric("총 거래 횟수", f"{result.total_trades}")
    with col8:
        st.metric("평균 보유기간", f"{result.avg_holding_period:.1f}일")
    
    # 벤치마크 비교
    if result.benchmark_return != 0:
        outperformance = result.total_return - result.benchmark_return
        st.metric("벤치마크 대비 초과수익", f"{outperformance:.2%}")
    
    # 수익 곡선 차트
    create_equity_curve_chart(result.equity_curve, result.benchmark_return)
    
    # 거래 내역
    if result.trades:
        st.markdown("#### 📋 거래 내역 (최근 10건)")
        trades_df = pd.DataFrame(result.trades[-10:])
        if not trades_df.empty:
            st.dataframe(trades_df)

def show_detailed_stock_analysis(stock_data: Dict):
    """종목 상세 분석 표시"""
    st.markdown(f"#### 📊 {stock_data['ticker']} 상세 분석")
    
    # 점수 분해
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**세부 점수**")
        scores = {
            '기술적 분석': stock_data['technical_score'],
            '모멘텀': stock_data['momentum_score'],
            '변동성': stock_data['volatility_score'],
            '거래량': stock_data['volume_score'],
            '추세': stock_data['trend_score']
        }
        
        for score_name, score_value in scores.items():
            st.metric(score_name, f"{score_value:.1f}/100")
    
    with col2:
        st.markdown("**기술적 지표**")
        st.metric("RSI", f"{stock_data['rsi']:.1f}")
        st.metric("20일선 대비", f"{stock_data['price_vs_sma20']:+.1f}%")
        st.metric("50일선 대비", f"{stock_data['price_vs_sma50']:+.1f}%")
        st.metric("볼린저밴드 위치", f"{stock_data['bb_position']:.1f}%")

def create_strategy(strategy_name: str):
    """전략 객체 생성"""
    if strategy_name == "이동평균 교차":
        return MovingAverageCrossStrategy()
    elif strategy_name == "RSI":
        return RSIStrategy()
    elif strategy_name == "MACD":
        return MACDStrategy()
    elif strategy_name == "볼린저 밴드":
        return BollingerBandStrategy()

def create_equity_curve_chart(equity_curve: pd.Series, benchmark_return: float):
    """수익 곡선 차트 생성"""
    fig = go.Figure()
    
    # 전략 수익 곡선
    fig.add_trace(go.Scatter(
        x=equity_curve.index,
        y=equity_curve.values,
        mode='lines',
        name='전략 수익',
        line=dict(color='blue', width=2)
    ))
    
    # 벤치마크 비교선 (단순화)
    if benchmark_return != 0:
        initial_value = equity_curve.iloc[0]
        final_benchmark_value = initial_value * (1 + benchmark_return)
        
        benchmark_line = np.linspace(initial_value, final_benchmark_value, len(equity_curve))
        
        fig.add_trace(go.Scatter(
            x=equity_curve.index,
            y=benchmark_line,
            mode='lines',
            name='벤치마크',
            line=dict(color='red', width=1, dash='dash')
        ))
    
    fig.update_layout(
        title="포트폴리오 가치 변화",
        xaxis_title="날짜",
        yaxis_title="포트폴리오 가치 (원)",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_recommendation_chart(recommendations: pd.DataFrame):
    """추천 종목 차트 생성"""
    if recommendations.empty:
        return
    
    fig = go.Figure()
    
    # 점수별 막대 차트
    fig.add_trace(go.Bar(
        x=recommendations['ticker'],
        y=recommendations['total_score'],
        text=recommendations['total_score'].round(1),
        textposition='outside',
        marker_color=px.colors.sequential.Blues_r
    ))
    
    fig.update_layout(
        title="AI 추천 점수",
        xaxis_title="종목",
        yaxis_title="AI 점수",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 세부 점수 비교 차트
    score_categories = ['technical_score', 'momentum_score', 'volatility_score', 'volume_score', 'trend_score']
    
    fig2 = go.Figure()
    
    for category in score_categories:
        fig2.add_trace(go.Scatter(
            x=recommendations['ticker'],
            y=recommendations[category],
            mode='lines+markers',
            name=category.replace('_score', '').title(),
            line=dict(width=2)
        ))
    
    fig2.update_layout(
        title="세부 점수 비교",
        xaxis_title="종목",
        yaxis_title="점수",
        height=400,
        showlegend=True
    )
    
    st.plotly_chart(fig2, use_container_width=True)

def create_performance_comparison_chart(results: Dict[str, BacktestResult]):
    """성과 비교 차트 생성"""
    # 수익 곡선 비교
    fig = go.Figure()
    
    colors = ['blue', 'red', 'green', 'orange', 'purple']
    
    for i, (strategy_name, result) in enumerate(results.items()):
        # 수익률로 정규화
        normalized_curve = result.equity_curve / result.equity_curve.iloc[0] * 100
        
        fig.add_trace(go.Scatter(
            x=result.equity_curve.index,
            y=normalized_curve,
            mode='lines',
            name=strategy_name,
            line=dict(color=colors[i % len(colors)], width=2)
        ))
    
    fig.update_layout(
        title="전략별 수익 곡선 비교 (정규화)",
        xaxis_title="날짜",
        yaxis_title="수익률 (%)",
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_performance_summary_table(results: Dict[str, BacktestResult]):
    """성과 요약 테이블 생성"""
    summary_data = []
    
    for strategy_name, result in results.items():
        summary_data.append({
            '전략': strategy_name,
            '총 수익률': f"{result.total_return:.2%}",
            '연간 수익률': f"{result.annual_return:.2%}",
            '변동성': f"{result.volatility:.2%}",
            '샤프 비율': f"{result.sharpe_ratio:.2f}",
            '최대 낙폭': f"{result.max_drawdown:.2%}",
            '승률': f"{result.win_rate:.1%}",
            '거래 횟수': result.total_trades
        })
    
    summary_df = pd.DataFrame(summary_data)
    st.markdown("#### 📋 전략별 성과 요약")
    st.dataframe(summary_df, use_container_width=True)
    
    # 최고 성과 전략 하이라이트
    best_strategy = max(results.items(), key=lambda x: x[1].sharpe_ratio)
    st.success(f"🏆 최고 성과 전략: **{best_strategy[0]}** (샤프 비율: {best_strategy[1].sharpe_ratio:.2f})")

# 포트폴리오 시뮬레이터 추가
class PortfolioSimulator:
    """포트폴리오 시뮬레이터"""
    
    def __init__(self):
        self.simulation_results = []
    
    def monte_carlo_simulation(self, returns: pd.Series, days: int = 252, simulations: int = 1000) -> Dict:
        """몬테카를로 시뮬레이션"""
        
        mean_return = returns.mean()
        std_return = returns.std()
        
        simulation_results = []
        
        for _ in range(simulations):
            # 랜덤 수익률 생성
            random_returns = np.random.normal(mean_return, std_return, days)
            
            # 누적 수익률 계산
            cumulative_returns = (1 + random_returns).cumprod()
            final_return = cumulative_returns[-1] - 1
            
            simulation_results.append(final_return)
        
        simulation_results = np.array(simulation_results)
        
        return {
            'mean_return': simulation_results.mean(),
            'std_return': simulation_results.std(),
            'percentile_5': np.percentile(simulation_results, 5),
            'percentile_95': np.percentile(simulation_results, 95),
            'probability_positive': (simulation_results > 0).mean(),
            'var_5': np.percentile(simulation_results, 5),
            'simulation_data': simulation_results
        }

def render_portfolio_simulator():
    """포트폴리오 시뮬레이터 렌더링"""
    st.markdown("### 🎲 포트폴리오 시뮬레이션")
    
    ticker = st.text_input("시뮬레이션할 종목", value="005930.KS")
    days = st.slider("시뮬레이션 기간 (일)", 30, 365, 252)
    simulations = st.slider("시뮬레이션 횟수", 100, 5000, 1000)
    
    if st.button("몬테카를로 시뮬레이션 실행"):
        with st.spinner("시뮬레이션 실행 중..."):
            # 데이터 수집
            stock = yf.Ticker(ticker)
            data = stock.history(period="2y")
            
            if not data.empty:
                returns = data['Close'].pct_change().dropna()
                
                simulator = PortfolioSimulator()
                results = simulator.monte_carlo_simulation(returns, days, simulations)
                
                # 결과 표시
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("예상 수익률", f"{results['mean_return']:.2%}")
                with col2:
                    st.metric("수익 확률", f"{results['probability_positive']:.1%}")
                with col3:
                    st.metric("5% VaR", f"{results['var_5']:.2%}")
                with col4:
                    st.metric("95% 신뢰구간", f"{results['percentile_95']:.2%}")
                
                # 시뮬레이션 결과 히스토그램
                fig = go.Figure(data=[go.Histogram(x=results['simulation_data'])])
                fig.update_layout(
                    title=f"{ticker} {days}일 수익률 분포",
                    xaxis_title="수익률",
                    yaxis_title="빈도",
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

# 메인 통합 함수
def integrate_backtesting_features():
    """백테스팅 기능을 메인 앱에 통합"""
    if st.session_state.get('show_backtesting', False):
        render_backtesting_system()
        st.markdown("---")
        render_portfolio_simulator()

if __name__ == "__main__":
    render_backtesting_system()
