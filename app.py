"""
app.py - 통합 CTA 시스템 적용 메인 애플리케이션
HyperCLOVA X 기반 AI 투자 어드바이저 + 통합 실시간 알림 시스템 + 통합 CTA 마케팅
"""

import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import requests
import feedparser
from datetime import datetime, timedelta
import json
import os
import time
import logging
import uuid
import sys
import traceback

# 통합 실시간 알림 시스템 import
from unified_realtime_alerts import (
    integrate_unified_realtime_alerts,
    init_unified_alert_system,
    add_unified_alert,
    UnifiedRealtimeAlertSystem,
    AlertType,
    AlertPriority
)

# 통합 CTA 마케팅 시스템 import
from integrated_cta_system import (
    IntegratedCTAManager,
    init_integrated_cta_system,
    show_comprehensive_cta_experience,
    show_risk_based_cta,
    track_user_journey,
    display_integrated_cta_dashboard,
    run_integrated_cta_system,
    initialize_session_tracking
)

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 페이지 설정
st.set_page_config(
    page_title="HyperCLOVA X AI 투자 어드바이저 Pro",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 안전한 모듈 로드 함수
def safe_import(module_name, fallback=None):
    """안전한 모듈 import"""
    try:
        if module_name in sys.modules:
            return sys.modules[module_name]
        
        # 동적 import 시도
        module = __import__(module_name)
        return module
    except ImportError as e:
        logger.warning(f"모듈 {module_name} 로드 실패: {e}")
        return fallback

# 기본 설정 클래스
class Config:
    CLOVA_BASE_URL = "https://clovastudio.stream.ntruss.com"
    CLOVA_MODEL = "HCX-005"
    AI_PARAMS = {
        'topP': 0.8,
        'topK': 0,
        'maxTokens': 3000,
        'temperature': 0.2,
        'repeatPenalty': 1.3,
        'stopBefore': [],
        'includeAiFilters': True,
        'seed': 0
    }
    DEFAULT_STOCKS = {
        "삼성전자": "005930.KS", "삼전": "005930.KS", "samsung": "005930.KS",
        "SK하이닉스": "000660.KS", "하이닉스": "000660.KS", "sk": "000660.KS",
        "네이버": "035420.KS", "NAVER": "035420.KS", "naver": "035420.KS",
        "카카오": "035720.KS", "kakao": "035720.KS",
        "테슬라": "TSLA", "tesla": "TSLA", "테슬": "TSLA",
        "애플": "AAPL", "apple": "AAPL",
        "엔비디아": "NVDA", "nvidia": "NVDA",
        "마이크로소프트": "MSFT", "ms": "MSFT",
        "구글": "GOOGL", "google": "GOOGL",
        "KOSPI": "^KS11", "KOSDAQ": "^KQ11", "NASDAQ": "^IXIC", 
        "S&P 500": "^GSPC", "USD/KRW": "KRW=X"
    }

def get_api_key():
    """CLOVA Studio API 키 가져오기"""
    try:
        return st.secrets.get("CLOVA_STUDIO_API_KEY", "")
    except:
        return os.getenv("CLOVA_STUDIO_API_KEY", "")

# CSS 스타일 로드
def load_css():
    """CSS 스타일 로드"""
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .ai-response {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 1rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    .status-good {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .status-bad {
        background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .feature-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2196f3;
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    .feature-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .metric-card {
        background: white;
        border-radius: 0.5rem;
        padding: 1rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        text-align: center;
    }
    .alert-urgent {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
    .mega-cta {
        background: linear-gradient(135deg, #ff6b35 0%, #f7931e 100%);
        color: white;
        padding: 2rem;
        border-radius: 1rem;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(255,107,53,0.3);
        animation: glow 3s ease-in-out infinite alternate;
    }
    @keyframes glow {
        from { box-shadow: 0 8px 25px rgba(255,107,53,0.3); }
        to { box-shadow: 0 12px 35px rgba(255,107,53,0.5); }
    }
    @keyframes blink {
        0%, 50% { opacity: 1; }
        51%, 100% { opacity: 0.7; }
    }
    </style>
    """, unsafe_allow_html=True)

# 기본 데이터 수집 함수들
@st.cache_data(ttl=300)
def get_market_data():
    """실시간 시장 데이터 수집"""
    try:
        collected_time = datetime.now()
        
        indices = {
            "KOSPI": "^KS11",
            "KOSDAQ": "^KQ11",
            "삼성전자": "005930.KS",
            "SK하이닉스": "000660.KS",
            "NASDAQ": "^IXIC", 
            "S&P 500": "^GSPC",
            "USD/KRW": "KRW=X"
        }
        
        market_data = {}
        for name, ticker in indices.items():
            try:
                data = yf.Ticker(ticker).history(period="2d", interval="5m")
                if not data.empty:
                    current = data['Close'].iloc[-1]
                    prev = data['Close'].iloc[0]
                    change = ((current - prev) / prev) * 100
                    
                    market_data[name] = {
                        'current': current,
                        'change': change,
                        'volume': data['Volume'].iloc[-1] if not data['Volume'].empty else 0,
                        'collected_at': collected_time.strftime('%H:%M:%S'),
                        'timestamp': collected_time
                    }
            except Exception as e:
                logger.warning(f"{name} 데이터 수집 실패: {e}")
                continue
        
        return market_data
    except Exception as e:
        logger.error(f"시장 데이터 수집 오류: {e}")
        return {}

@st.cache_data(ttl=1800)
def get_news_data():
    """뉴스 데이터 수집"""
    try:
        collected_time = datetime.now()
        
        news_sources = [
            'https://feeds.finance.yahoo.com/rss/2.0/headline'
        ]
        
        articles = []
        for url in news_sources:
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries[:3]:
                    articles.append({
                        'title': entry.get('title', ''),
                        'summary': entry.get('summary', ''),
                        'published': entry.get('published', ''),
                        'source': feed.feed.get('title', 'News'),
                        'collected_at': collected_time.strftime('%H:%M:%S')
                    })
            except Exception as e:
                logger.warning(f"뉴스 수집 실패: {e}")
                continue
        
        return articles[:6]
    except Exception as e:
        logger.error(f"뉴스 수집 오류: {e}")
        return []

def parse_portfolio(question):
    """포트폴리오 정보 추출"""
    import re
    
    portfolio_info = {}
    
    # 종목명 추출
    for korean_name, ticker in Config.DEFAULT_STOCKS.items():
        if korean_name.lower() in question.lower():
            portfolio_info['stock'] = korean_name
            portfolio_info['ticker'] = ticker
            break
    
    # 매수가 추출
    price_patterns = [
        r'(\d+)만원',
        r'(\d+)천원',
        r'(\d+,?\d*\.?\d*)원',
        r'(\d+,?\d*\.?\d*)'
    ]
    
    for pattern in price_patterns:
        matches = re.findall(pattern, question)
        if matches:
            price_str = matches[0].replace(',', '')
            try:
                if '만원' in question:
                    portfolio_info['buy_price'] = float(price_str) * 10000
                elif '천원' in question:
                    portfolio_info['buy_price'] = float(price_str) * 1000
                else:
                    price = float(price_str)
                    if price < 1000:
                        portfolio_info['buy_price'] = price * 10000
                    else:
                        portfolio_info['buy_price'] = price
                break
            except:
                continue
    
    # 보유 주식 수 추출
    share_patterns = [r'(\d+)주', r'(\d+)개', r'(\d+)장']
    
    for pattern in share_patterns:
        matches = re.findall(pattern, question)
        if matches:
            try:
                portfolio_info['shares'] = int(matches[0])
                break
            except:
                continue
    
    return portfolio_info

def calculate_portfolio_performance(portfolio_info):
    """포트폴리오 성과 계산"""
    if not portfolio_info or not portfolio_info.get('ticker'):
        return None
    
    try:
        stock = yf.Ticker(portfolio_info['ticker'])
        current_data = stock.history(period="1d")
        
        if current_data.empty:
            return None
        
        current_price = current_data['Close'].iloc[-1]
        buy_price = portfolio_info.get('buy_price', current_price)
        shares = portfolio_info.get('shares', 1)
        
        profit_rate = ((current_price - buy_price) / buy_price) * 100
        profit_amount = (current_price - buy_price) * shares
        current_value = current_price * shares
        invested_amount = buy_price * shares
        
        return {
            'current_price': current_price,
            'buy_price': buy_price,
            'profit_rate': profit_rate,
            'profit_amount': profit_amount,
            'current_value': current_value,
            'invested_amount': invested_amount,
            'shares': shares
        }
    except Exception as e:
        logger.error(f"포트폴리오 성과 계산 오류: {e}")
        return None

# AI 클라이언트 클래스
class HyperCLOVAXClient:
    def __init__(self):
        self.api_key = get_api_key()
        self.base_url = Config.CLOVA_BASE_URL
        
    def get_real_time_analysis(self, question: str, market_data: dict, news_data: list) -> str:
        """실시간 데이터 기반 AI 분석"""
        if not self.api_key:
            raise Exception("API 키가 설정되지 않았습니다. .streamlit/secrets.toml 파일에 CLOVA_STUDIO_API_KEY를 설정해주세요.")
        
        # 컨텍스트 구성
        market_context = self._format_market_context(market_data)
        news_context = self._format_news_context(news_data)
        
        system_prompt = f"""당신은 전문적인 AI 투자 어드바이저입니다.
아래 실시간 시장 데이터와 최신 뉴스를 바탕으로 정확하고 실용적인 투자 분석을 제공해주세요.

=== 실시간 시장 데이터 ===
{market_context}

=== 최신 뉴스 ===
{news_context}

=== 분석 형식 ===
📊 **실시간 시장 분석**
[현재 시장 상황 분석]

💡 **투자 기회**  
[실시간 데이터 기반 투자 포인트]

⚠️ **리스크 요인**
[현재 시장 리스크]

📈 **실행 전략**
[구체적 투자 실행 방안]

🕐 **타이밍 분석**
[현재 시점 기준 매매 타이밍]

위 실시간 정보를 적극 활용하여 현재 시점에 최적화된 투자 분석을 제공해주세요."""

        try:
            headers = {
                'X-NCP-CLOVASTUDIO-API-KEY': self.api_key,
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            url = f"{self.base_url}/testapp/v1/chat-completions/{Config.CLOVA_MODEL}"
            
            payload = {
                'messages': [
                    {
                        'role': 'system',
                        'content': system_prompt
                    },
                    {
                        'role': 'user', 
                        'content': f"현재 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n질문: {question}"
                    }
                ],
                **Config.AI_PARAMS
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                
                if 'result' in result:
                    if 'message' in result['result']:
                        content = result['result']['message'].get('content', '')
                    elif 'messages' in result['result'] and len(result['result']['messages']) > 0:
                        content = result['result']['messages'][0].get('content', '')
                    else:
                        content = str(result['result'])
                    
                    if content:
                        return f"🤖 **HyperCLOVA X 실시간 분석** ({datetime.now().strftime('%H:%M:%S')})\n\n{content}"
                    else:
                        raise Exception("AI 응답이 비어있습니다.")
                else:
                    raise Exception(f"응답 형식 오류: {result}")
                    
            elif response.status_code == 401:
                raise Exception("API 키 인증 실패")
            elif response.status_code == 403:
                raise Exception("API 접근 권한 없음")
            elif response.status_code == 429:
                raise Exception("API 사용량 한도 초과")
            else:
                raise Exception(f"API 호출 실패 (HTTP {response.status_code})")
                
        except requests.exceptions.ConnectTimeout:
            raise Exception("네트워크 연결 시간 초과")
        except requests.exceptions.ConnectionError:
            raise Exception("네트워크 연결 오류")
        except Exception as e:
            raise e
    
    def _format_market_context(self, market_data: dict) -> str:
        """시장 데이터 컨텍스트 변환"""
        if not market_data:
            return "시장 데이터를 불러올 수 없습니다."
        
        context = []
        for name, data in market_data.items():
            change_symbol = "📈" if data['change'] >= 0 else "📉"
            context.append(f"{change_symbol} {name}: {data['current']:.2f} ({data['change']:+.2f}%)")
        
        return "\n".join(context)
    
    def _format_news_context(self, news_data: list) -> str:
        """뉴스 데이터 컨텍스트 변환"""
        if not news_data:
            return "최신 뉴스를 불러올 수 없습니다."
        
        context = []
        for i, article in enumerate(news_data[:3], 1):
            context.append(f"{i}. {article['title']}")
            if article.get('summary'):
                context.append(f"   요약: {article['summary'][:100]}...")
        
        return "\n".join(context)

# 고급 기능 클래스들
class AdvancedFeatures:
    """고급 투자자 기능"""
    
    def __init__(self):
        self.cta_manager = init_integrated_cta_system()
    
    def render_portfolio_analyzer(self):
        """포트폴리오 분석기"""
        st.markdown("### 📊 포트폴리오 분석")
        
        # 포트폴리오 입력
        with st.expander("➕ 포트폴리오 추가", expanded=False):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                ticker = st.text_input("종목 코드", placeholder="005930.KS")
            with col2:
                shares = st.number_input("보유 주수", min_value=1, value=10)
            with col3:
                buy_price = st.number_input("매수가", min_value=0.0, value=70000.0)
            with col4:
                if st.button("추가", type="primary"):
                    if 'portfolio' not in st.session_state:
                        st.session_state.portfolio = []
                    
                    new_holding = {
                        'ticker': ticker,
                        'shares': shares,
                        'buy_price': buy_price,
                        'added_at': datetime.now()
                    }
                    
                    st.session_state.portfolio.append(new_holding)
                    
                    # 통합 알림 시스템에 자동 알림 생성
                    try:
                        alert_system = init_unified_alert_system()
                        alert_system.analyze_stock_for_alerts(ticker, new_holding)
                        add_unified_alert(
                            alert_type="투자 기회",
                            title=f"{ticker} 포트폴리오 추가됨",
                            message=f"{ticker}가 포트폴리오에 추가되었습니다. 실시간 모니터링이 시작됩니다.",
                            ticker=ticker
                        )
                    except Exception as e:
                        logger.warning(f"알림 생성 실패: {e}")
                    
                    st.success(f"{ticker} 추가됨!")
        
        # 포트폴리오 표시
        if 'portfolio' in st.session_state and st.session_state.portfolio:
            st.markdown("#### 📋 현재 포트폴리오")
            
            total_invested = 0
            total_current = 0
            portfolio_performance = []
            
            for i, holding in enumerate(st.session_state.portfolio):
                col1, col2, col3, col4, col5, col6 = st.columns([2, 1, 1, 1, 1, 1])
                
                with col1:
                    st.write(f"**{holding['ticker']}**")
                
                with col2:
                    st.write(f"{holding['shares']}주")
                
                with col3:
                    st.write(f"매수: {holding['buy_price']:,.0f}원")
                
                # 현재가 조회
                try:
                    stock = yf.Ticker(holding['ticker'])
                    current_price = stock.history(period="1d")['Close'].iloc[-1]
                    invested_amount = holding['buy_price'] * holding['shares']
                    current_value = current_price * holding['shares']
                    profit_rate = ((current_price - holding['buy_price']) / holding['buy_price']) * 100
                    
                    total_invested += invested_amount
                    total_current += current_value
                    
                    portfolio_performance.append({
                        'ticker': holding['ticker'],
                        'current_value': current_value,
                        'profit_rate': profit_rate
                    })
                    
                    with col4:
                        st.write(f"현재: {current_price:,.0f}원")
                    
                    with col5:
                        color = "🟢" if profit_rate >= 0 else "🔴"
                        st.write(f"{color} {profit_rate:+.1f}%")
                        
                        # 큰 변동 시 자동 알림
                        if abs(profit_rate) >= 10:
                            try:
                                alert_type = "투자 기회" if profit_rate > 0 else "리스크 경고"
                                add_unified_alert(
                                    alert_type=alert_type,
                                    title=f"{holding['ticker']} 큰 변동 감지",
                                    message=f"{holding['ticker']}가 {profit_rate:+.1f}% 변동했습니다.",
                                    ticker=holding['ticker']
                                )
                            except:
                                pass
                    
                    with col6:
                        if st.button("제거", key=f"remove_{i}"):
                            st.session_state.portfolio.pop(i)
                            st.rerun()
                            
                except Exception as e:
                    with col4:
                        st.write("데이터 없음")
                    with col5:
                        st.write("-")
                    with col6:
                        if st.button("제거", key=f"remove_{i}"):
                            st.session_state.portfolio.pop(i)
                            st.rerun()
            
            # 전체 요약
            if total_invested > 0:
                total_profit = total_current - total_invested
                total_return_pct = (total_profit / total_invested) * 100
                
                st.markdown("#### 📈 포트폴리오 요약")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("총 투자금액", f"{total_invested:,.0f}원")
                with col2:
                    st.metric("현재 평가액", f"{total_current:,.0f}원")
                with col3:
                    st.metric("총 손익", f"{total_profit:,.0f}원")
                with col4:
                    st.metric("수익률", f"{total_return_pct:+.2f}%")
                
                # 포트폴리오 정보 추출
            portfolio_info = parse_portfolio(st.session_state.user_question)
            
            # 포트폴리오 정보 표시
            if portfolio_info:
                st.markdown("### 👤 감지된 포트폴리오 정보")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if portfolio_info.get('stock'):
                        st.metric("종목", portfolio_info['stock'])
                
                with col2:
                    if portfolio_info.get('buy_price'):
                        st.metric("매수가", f"{portfolio_info['buy_price']:,.0f}원")
                
                with col3:
                   if portfolio_info.get('shares'):
                       st.metric("보유 수량", f"{portfolio_info['shares']}주")
            
            # 진행률 표시
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            steps = [
                ("🔍 질문 분석 중...", 0.2),
                ("📊 실시간 시장 데이터 수집...", 0.4),
                ("📰 최신 뉴스 분석...", 0.6),
                ("🤖 AI 분석 실행...", 0.8),
                ("✅ 분석 완료!", 1.0)
            ]
            
            for step, progress in steps:
                status_text.text(step)
                progress_bar.progress(progress)
                time.sleep(0.5)
            
            try:
                # AI 분석 수행
                with st.spinner("🤖 HyperCLOVA X가 실시간 분석 중입니다..."):
                    response = self.ai_client.get_real_time_analysis(
                        st.session_state.user_question,
                        market_data,
                        news_data
                    )
                
                # 진행률 제거
                progress_bar.empty()
                status_text.empty()
                
                # 응답 표시
                st.markdown('<div class="ai-response">', unsafe_allow_html=True)
                st.markdown(response)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # 분석 완료 알림 생성
                try:
                    add_unified_alert(
                        alert_type="투자 기회",
                        title="AI 분석 완료",
                        message=f"'{st.session_state.user_question[:30]}...' 질문에 대한 AI 분석이 완료되었습니다.",
                        ticker=portfolio_info.get('ticker') if portfolio_info else None
                    )
                except:
                    pass
                
                # 분석 요약
                st.markdown(f"""
                <div style="background: #e8f5e8; padding: 0.5rem; border-radius: 0.3rem; margin: 0.5rem 0;">
                    📊 분석 완료: {datetime.now().strftime('%Y년 %m월 %d일 %H시 %M분 %S초')}<br>
                    🔄 데이터 소스: 실시간 시장 + 최신 뉴스 + AI 분석<br>
                    🤖 AI 엔진: HyperCLOVA X (네이버 클라우드 플랫폼)
                </div>
                """, unsafe_allow_html=True)
                
                # 차트 표시 (포트폴리오 종목이 있는 경우)
                if portfolio_info and portfolio_info.get('ticker'):
                    st.markdown("### 📈 종목 차트")
                    try:
                        stock = yf.Ticker(portfolio_info['ticker'])
                        stock_data = stock.history(period="6mo")
                        
                        if not stock_data.empty:
                            fig = go.Figure(data=go.Candlestick(
                                x=stock_data.index,
                                open=stock_data['Open'],
                                high=stock_data['High'],
                                low=stock_data['Low'],
                                close=stock_data['Close'],
                                name=portfolio_info['ticker']
                            ))
                            
                            fig.update_layout(
                                title=f"{portfolio_info['ticker']} 주가 차트 (6개월)",
                                yaxis_title="Price",
                                xaxis_title="Date",
                                template="plotly_white",
                                height=500
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                    except Exception as e:
                        st.warning(f"차트를 불러올 수 없습니다: {str(e)}")
                
                # 포트폴리오 성과 계산 및 맞춤 CTA 표시
                if portfolio_info:
                    performance = calculate_portfolio_performance(portfolio_info)
                    if performance:
                        try:
                            # 손익 기반 알림 생성
                            profit_rate = performance['profit_rate']
                            if profit_rate < -15:
                                add_unified_alert(
                                    alert_type="리스크 경고",
                                    title=f"{portfolio_info['ticker']} 큰 손실",
                                    message=f"{portfolio_info['ticker']}에서 {profit_rate:.1f}% 손실이 발생했습니다.",
                                    ticker=portfolio_info['ticker']
                                )
                            elif profit_rate > 25:
                                add_unified_alert(
                                    alert_type="투자 기회",
                                    title=f"{portfolio_info['ticker']} 목표 수익",
                                    message=f"{portfolio_info['ticker']}에서 {profit_rate:.1f}% 수익을 달성했습니다.",
                                    ticker=portfolio_info['ticker']
                                )
                            
                            # 성과 기반 맞춤 CTA 표시
                            user_profile = {
                                'risk_level': 'HIGH' if profit_rate < -15 else 'LOW' if profit_rate > 25 else 'MEDIUM',
                                'investment_amount': self._estimate_investment_amount(performance['invested_amount']),
                                'portfolio_info': performance,
                                'session_id': st.session_state.session_id,
                                'page_context': 'ai_analysis'
                            }
                            
                            show_comprehensive_cta_experience(user_profile, performance, "ai_analysis")
                            
                        except Exception as e:
                            logger.warning(f"맞춤 CTA 표시 실패: {e}")
                            self._show_basic_cta()
                else:
                    # 기본 CTA 표시
                    user_profile = {
                        'session_id': st.session_state.session_id,
                        'page_context': 'ai_analysis'
                    }
                    show_comprehensive_cta_experience(user_profile, None, "ai_analysis")
                
                # 사용자 여정 추적
                track_user_journey("ai_analysis_completed", {
                    "question": st.session_state.user_question,
                    "portfolio_detected": bool(portfolio_info)
                })
                
            except Exception as e:
                progress_bar.empty()
                status_text.empty()
                
                st.markdown('<div class="error-message">', unsafe_allow_html=True)
                st.markdown(f"🚨 **분석 중 오류 발생**\n\n{str(e)}")
                st.markdown('</div>', unsafe_allow_html=True)
                
                # 오류 알림 생성
                try:
                    add_unified_alert(
                        alert_type="리스크 경고",
                        title="AI 분석 오류",
                        message=f"AI 분석 중 오류가 발생했습니다: {str(e)[:50]}...",
                        ticker=None
                    )
                except:
                    pass
                
                # 문제 해결 가이드
                st.markdown("### 🔧 문제 해결 방법")
                st.markdown("""
                1. **API 키 확인**: 사이드바에서 API 연결 상태 확인
                2. **네트워크 확인**: 인터넷 연결 상태 확인
                3. **질문 단순화**: 더 간단한 질문으로 재시도
                4. **페이지 새로고침**: 브라우저 새로고침 후 재시도
                """)
                
                # 오류 시에도 기본 CTA 표시
                self._show_basic_cta()
        
        # 샘플 질문
        if not st.session_state.user_question:
            st.markdown("### 💡 샘플 질문")
            
            sample_questions = [
                "삼성전자 65,000원에 150주 보유 중, 지금 매도해야 할까요?",
                "오늘 시장 상황 어떤가요? 매수하기 좋은 타이밍인가요?",
                "반도체 섹터 전망은 어떤가요?",
                "현재 가장 주목해야 할 투자 테마는?",
                "달러 환율이 계속 오르는데 어떻게 대응해야 할까요?",
                "AI 관련주 투자 전략 알려주세요"
            ]
            
            cols = st.columns(2)
            for i, question in enumerate(sample_questions):
                with cols[i % 2]:
                    if st.button(question, key=f"sample_{i}"):
                        st.session_state.selected_question = question
                        track_user_journey("sample_question_selected", {"question": question})
                        st.rerun()
    
    def _render_cta_marketing_content(self):
        """통합 CTA 마케팅 콘텐츠 렌더링"""
        st.markdown("### 🎯 마케팅 CTA 시스템")
        
        # 관리자 모드 확인
        admin_mode = st.secrets.get("ADMIN_MODE", False)
        
        if admin_mode:
            # 관리자 대시보드
            display_integrated_cta_dashboard()
            st.markdown("---")
        
        # CTA 테스트 섹션
        st.markdown("#### 🧪 CTA 시스템 테스트")
        
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
        
        with st.expander("시나리오 상세 정보", expanded=False):
            st.json(selected_profile)
        
        # 테스트 실행
        if st.button("🚀 CTA 테스트 실행", type="primary"):
            st.markdown("---")
            st.markdown(f"### 📋 {test_scenario} CTA 미리보기")
            
            try:
                # 통합 CTA 시스템 실행
                user_profile = selected_profile.copy()
                user_profile['session_id'] = st.session_state.session_id
                user_profile['page_context'] = 'cta_test'
                
                show_comprehensive_cta_experience(
                    user_profile=user_profile,
                    portfolio_info=selected_profile.get('portfolio_info'),
                    page_context="cta_test"
                )
                
                # 테스트 추적
                track_user_journey("cta_test_executed", {"scenario": test_scenario})
                
            except Exception as e:
                st.error(f"CTA 테스트 실행 중 오류: {e}")
                # 기본 CTA 표시
                self._show_basic_cta()
        
        # CTA 성과 요약 (관리자가 아닌 경우에도 기본 정보 표시)
        if not admin_mode:
            st.markdown("#### 📊 CTA 성과 요약")
            try:
                basic_metrics = self.cta_manager.get_dashboard_metrics()
                conversion_rate = basic_metrics.get('conversion_metrics', {}).get('conversion_rate', 0)
                active_leads = basic_metrics.get('active_leads', 0)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("현재 전환율", f"{conversion_rate}%")
                with col2:
                    st.metric("활성 리드", f"{active_leads}개")
                    
            except Exception as e:
                st.info("CTA 성과 데이터를 불러오는 중입니다...")
    
    def _estimate_investment_amount(self, invested_amount: float) -> str:
        """투자 금액을 카테고리로 변환"""
        if invested_amount >= 500000000:  # 5억 이상
            return '5억원 이상'
        elif invested_amount >= 100000000:  # 1억 이상
            return '1억원-5억원'
        elif invested_amount >= 50000000:  # 5천만원 이상
            return '5천만원-1억원'
        elif invested_amount >= 10000000:  # 1천만원 이상
            return '1천-5천만원'
        else:
            return '1천만원 미만'
    
    def _show_basic_cta(self):
        """기본 CTA 표시 (통합 시스템 오류 시 대비)"""
        st.markdown("""
        <div class="mega-cta">
            <h3 style="margin: 0 0 0.5rem 0;">📞 1:1 투자 상담</h3>
            <p style="margin: 0 0 1rem 0; font-size: 1.1rem;">AI 분석과 함께 전문가 상담으로 완벽한 투자전략을 세워보세요.</p>
            <p style="margin: 0; font-size: 0.9rem; opacity: 0.9;">
                ✅ 무료 상담 ✅ 개인별 맞춤 전략 ✅ 실시간 포트폴리오 분석
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🎯 전문가 상담 신청하기", type="primary", use_container_width=True, key="basic_cta"):
                st.success("상담 신청이 접수되었습니다! 24시간 내 연락드리겠습니다.")
                st.info("📞 즉시 상담: 1588-6666")
    
    def _show_disclaimer(self):
        """면책조항"""
        st.markdown("""
        <div style="background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%); border: 2px solid #ff6b35; border-radius: 0.8rem; padding: 1.5rem; margin: 1rem 0;">
            <h4 style="color: #d63031; margin: 0 0 1rem 0;">⚠️ 투자 위험 고지 및 면책사항</h4>
            <div style="color: #2d3436; font-size: 0.9rem; line-height: 1.6;">
                <p><strong>🚨 중요한 투자 위험 안내</strong></p>
                <ul style="margin: 0.5rem 0; padding-left: 1.5rem;">
                    <li>본 AI 분석은 <strong>정보 제공 목적</strong>이며, 투자 권유나 매매 신호가 아닙니다.</li>
                    <li>모든 투자에는 <strong>원금 손실 위험</strong>이 있으며, 과거 성과가 미래 수익을 보장하지 않습니다.</li>
                    <li>투자 결정은 <strong>본인의 판단과 책임</strong>하에 이루어져야 합니다.</li>
                    <li>중요한 투자 결정 전에는 <strong>전문가 상담</strong>을 받으시기 바랍니다.</li>
                    <li>AI 분석 결과의 <strong>정확성을 보장하지 않으며</strong>, 시장 상황에 따라 예측이 빗나갈 수 있습니다.</li>
                    <li>실시간 알림 시스템과 CTA는 <strong>참고용</strong>이며, 투자 결정의 유일한 근거로 사용하지 마세요.</li>
                </ul>
                <p style="margin-top: 1rem;"><strong>📞 투자 상담:</strong> 미래에셋증권 고객센터 1588-6666</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_creator_info(self):
        """만든이 정보 렌더링"""
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border-radius: 1rem; margin: 2rem 0;">
            <p style="margin: 0; font-size: 1rem; color: #495057;">🏆 <strong>AI Festival 2025</strong> 출품작</p>
            <p style="margin: 1rem 0; font-size: 1.4rem;">
                💻 Created by <span style="color: #667eea; font-size: 1.2rem; font-weight: bold;">Rin.C</span>
            </p>
            <div style="font-size: 0.8rem; color: #6c757d; margin-top: 1rem;">
                🤖 HyperCLOVA X • 📊 Real-time Market Data • 🔴 Live Analysis • 🔔 Unified Alert System • 🎯 Integrated CTA Marketing • 🚀 All Features Active
            </div>
        </div>
        """, unsafe_allow_html=True)

def main():
    """메인 함수"""
    try:
        # 통합 투자 어드바이저 실행
        app = IntegratedInvestmentAdvisor()
        app.run()
        
    except Exception as e:
        logger.critical(f"치명적 오류 발생: {str(e)}")
        st.error("🚨 시스템에 치명적인 오류가 발생했습니다.")
        
        st.markdown("### 🔧 문제 해결 방법")
        st.markdown("""
        1. **페이지 새로고침**: F5 키를 눌러 페이지를 새로고침하세요
        2. **브라우저 캐시 삭제**: Ctrl+Shift+Delete로 캐시를 삭제하세요
        3. **다른 브라우저 시도**: Chrome, Firefox, Edge 등 다른 브라우저로 접속해보세요
        4. **인터넷 연결 확인**: 네트워크 연결 상태를 확인하세요
        5. **잠시 후 재시도**: 서버가 일시적으로 과부하일 수 있습니다
        """)

if __name__ == "__main__":
    main()
폴리오 상태 기반 통합 CTA 표시
                portfolio_info = {
                    'current_value': total_current,
                    'profit_rate': total_return_pct,
                    'total_profit': total_profit
                }
                
                # 포트폴리오 성과 기반 맞춤 CTA
                show_risk_based_cta(portfolio_info)
                
                # 포트폴리오 상태 기반 자동 알림
                try:
                    if total_return_pct <= -15:
                        add_unified_alert(
                            alert_type="리스크 경고",
                            title="포트폴리오 큰 손실",
                            message=f"전체 포트폴리오가 {total_return_pct:.1f}% 손실 상태입니다.",
                            ticker=None
                        )
                    elif total_return_pct >= 25:
                        add_unified_alert(
                            alert_type="투자 기회",
                            title="포트폴리오 목표 수익 달성",
                            message=f"전체 포트폴리오가 {total_return_pct:.1f}% 수익 상태입니다.",
                            ticker=None
                        )
                except:
                    pass
    
    def render_technical_analysis(self):
        """기술적 분석"""
        st.markdown("### 📈 기술적 분석")
        
        # 종목 선택
        ticker = st.selectbox(
            "분석할 종목 선택",
            options=["005930.KS", "000660.KS", "035420.KS", "TSLA", "NVDA"],
            format_func=lambda x: {
                "005930.KS": "삼성전자", "000660.KS": "SK하이닉스", 
                "035420.KS": "네이버", "TSLA": "테슬라", "NVDA": "엔비디아"
            }.get(x, x)
        )
        
        if ticker:
            try:
                # 데이터 수집
                stock = yf.Ticker(ticker)
                data = stock.history(period="6mo")
                
                if not data.empty:
                    # 기술적 지표 계산
                    data['MA5'] = data['Close'].rolling(5).mean()
                    data['MA20'] = data['Close'].rolling(20).mean()
                    data['MA60'] = data['Close'].rolling(60).mean()
                    
                    # RSI 계산
                    delta = data['Close'].diff()
                    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                    rs = gain / loss
                    data['RSI'] = 100 - (100 / (1 + rs))
                    
                    # 차트 생성
                    fig = go.Figure()
                    
                    # 캔들스틱
                    fig.add_trace(go.Candlestick(
                        x=data.index,
                        open=data['Open'],
                        high=data['High'],
                        low=data['Low'],
                        close=data['Close'],
                        name="Price"
                    ))
                    
                    # 이동평균선
                    fig.add_trace(go.Scatter(x=data.index, y=data['MA5'], name='MA5', line=dict(color='red')))
                    fig.add_trace(go.Scatter(x=data.index, y=data['MA20'], name='MA20', line=dict(color='blue')))
                    fig.add_trace(go.Scatter(x=data.index, y=data['MA60'], name='MA60', line=dict(color='green')))
                    
                    fig.update_layout(
                        title=f"{ticker} 기술적 분석",
                        yaxis_title="Price",
                        height=500,
                        showlegend=True
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # 기술적 신호
                    current_price = data['Close'].iloc[-1]
                    current_rsi = data['RSI'].iloc[-1]
                    ma5 = data['MA5'].iloc[-1]
                    ma20 = data['MA20'].iloc[-1]
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        trend = "상승" if current_price > ma5 > ma20 else "하락" if current_price < ma5 < ma20 else "횡보"
                        st.metric("추세", trend)
                    
                    with col2:
                        rsi_signal = "과매수" if current_rsi > 70 else "과매도" if current_rsi < 30 else "중립"
                        st.metric("RSI", f"{current_rsi:.1f} ({rsi_signal})")
                        
                        # RSI 기반 자동 알림
                        try:
                            if current_rsi > 70:
                                add_unified_alert(
                                    alert_type="리스크 경고",
                                    title=f"{ticker} 과매수 구간",
                                    message=f"{ticker}의 RSI가 {current_rsi:.1f}로 과매수 구간입니다.",
                                    ticker=ticker
                                )
                            elif current_rsi < 30:
                                add_unified_alert(
                                    alert_type="투자 기회",
                                    title=f"{ticker} 과매도 구간",
                                    message=f"{ticker}의 RSI가 {current_rsi:.1f}로 과매도 구간입니다.",
                                    ticker=ticker
                                )
                        except:
                            pass
                    
                    with col3:
                        volatility = data['Close'].pct_change().std() * 100
                        st.metric("변동성", f"{volatility:.2f}%")
                        
            except Exception as e:
                st.error(f"기술적 분석 오류: {e}")

class BacktestingEngine:
    """백테스팅 시스템"""
    
    def __init__(self):
        self.cta_manager = init_integrated_cta_system()
    
    def render_backtesting(self):
        """백테스팅 인터페이스"""
        st.markdown("### 📊 전략 백테스팅")
        
        # 백테스트 설정
        col1, col2, col3 = st.columns(3)
        
        with col1:
            ticker = st.text_input("백테스트 종목", value="005930.KS")
            strategy = st.selectbox("전략 선택", ["이동평균 교차", "RSI 전략", "볼린저 밴드"])
        
        with col2:
            period = st.selectbox("백테스트 기간", ["6mo", "1y", "2y", "3y"])
            initial_capital = st.number_input("초기 자본", value=10000000, step=1000000)
        
        with col3:
            if strategy == "이동평균 교차":
                short_ma = st.slider("단기 이동평균", 5, 30, 5)
                long_ma = st.slider("장기 이동평균", 20, 100, 20)
            elif strategy == "RSI 전략":
                rsi_period = st.slider("RSI 기간", 10, 30, 14)
                oversold = st.slider("과매도 기준", 20, 40, 30)
                overbought = st.slider("과매수 기준", 60, 80, 70)
        
        if st.button("백테스트 실행", type="primary"):
            with st.spinner("백테스트 실행 중..."):
                try:
                    # 데이터 수집
                    stock = yf.Ticker(ticker)
                    data = stock.history(period=period)
                    
                    if not data.empty:
                        # 전략별 신호 생성
                        if strategy == "이동평균 교차":
                            data['MA_Short'] = data['Close'].rolling(short_ma).mean()
                            data['MA_Long'] = data['Close'].rolling(long_ma).mean()
                            data['Signal'] = 0
                            data.loc[data['MA_Short'] > data['MA_Long'], 'Signal'] = 1
                            data.loc[data['MA_Short'] <= data['MA_Long'], 'Signal'] = 0
                        
                        elif strategy == "RSI 전략":
                            delta = data['Close'].diff()
                            gain = (delta.where(delta > 0, 0)).rolling(window=rsi_period).mean()
                            loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_period).mean()
                            rs = gain / loss
                            data['RSI'] = 100 - (100 / (1 + rs))
                            data['Signal'] = 0
                            data.loc[data['RSI'] < oversold, 'Signal'] = 1
                            data.loc[data['RSI'] > overbought, 'Signal'] = -1
                        
                        # 백테스트 수행
                        results = self._run_backtest(data, initial_capital)
                        
                        # 결과 표시
                        self._display_backtest_results(results, ticker, strategy)
                        
                        # 백테스트 결과 기반 자동 알림
                        try:
                            if results['total_return'] > 20:
                                add_unified_alert(
                                    alert_type="투자 기회",
                                    title=f"{strategy} 전략 성공",
                                    message=f"{ticker}에서 {strategy} 전략으로 {results['total_return']:.1f}% 수익 가능",
                                    ticker=ticker
                                )
                        except:
                            pass
                        
                        # 백테스트 결과 기반 맞춤 CTA
                        backtest_info = {
                            'profit_rate': results['total_return'],
                            'num_trades': results['num_trades'],
                            'final_value': results['final_value']
                        }
                        show_risk_based_cta(backtest_info)
                        
                except Exception as e:
                    st.error(f"백테스트 오류: {e}")
    
    def _run_backtest(self, data, initial_capital):
        """백테스트 실행"""
        portfolio_value = initial_capital
        position = 0
        trades = []
        portfolio_history = []
        
        for i in range(1, len(data)):
            current_price = data['Close'].iloc[i]
            signal = data['Signal'].iloc[i]
            prev_signal = data['Signal'].iloc[i-1]
            
            # 매수 신호
            if signal == 1 and prev_signal != 1 and position == 0:
                shares = int(portfolio_value / current_price)
                if shares > 0:
                    position = shares
                    portfolio_value -= shares * current_price
                    trades.append({
                        'type': 'BUY',
                        'price': current_price,
                        'shares': shares,
                        'date': data.index[i]
                    })
            
            # 매도 신호
            elif (signal == -1 or signal == 0) and prev_signal == 1 and position > 0:
                portfolio_value += position * current_price
                trades.append({
                    'type': 'SELL',
                    'price': current_price,
                    'shares': position,
                    'date': data.index[i]
                })
                position = 0
            
            # 포트폴리오 가치 계산
            total_value = portfolio_value + (position * current_price)
            portfolio_history.append({
                'date': data.index[i],
                'value': total_value,
                'price': current_price
            })
        
        # 최종 정산
        if position > 0:
            final_price = data['Close'].iloc[-1]
            portfolio_value += position * final_price
        
        total_return = (portfolio_value - initial_capital) / initial_capital * 100
        
        return {
            'final_value': portfolio_value,
            'total_return': total_return,
            'trades': trades,
            'portfolio_history': portfolio_history,
            'num_trades': len(trades)
        }
    
    def _display_backtest_results(self, results, ticker, strategy):
        """백테스트 결과 표시"""
        st.markdown("#### 📈 백테스트 결과")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("최종 자산", f"{results['final_value']:,.0f}원")
        with col2:
            st.metric("총 수익률", f"{results['total_return']:+.2f}%")
        with col3:
            st.metric("거래 횟수", f"{results['num_trades']}회")
        with col4:
            if results['num_trades'] > 0:
                win_trades = sum(1 for i in range(1, len(results['trades']), 2) 
                               if i < len(results['trades']) and 
                               results['trades'][i]['price'] > results['trades'][i-1]['price'])
                win_rate = (win_trades / (results['num_trades'] // 2)) * 100 if results['num_trades'] > 1 else 0
                st.metric("승률", f"{win_rate:.1f}%")
        
        # 포트폴리오 가치 변화 차트
        if results['portfolio_history']:
            portfolio_df = pd.DataFrame(results['portfolio_history'])
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=portfolio_df['date'],
                y=portfolio_df['value'],
                mode='lines',
                name='포트폴리오 가치',
                line=dict(color='blue', width=2)
            ))
            
            fig.update_layout(
                title=f"{ticker} - {strategy} 백테스트 결과",
                xaxis_title="날짜",
                yaxis_title="포트폴리오 가치 (원)",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # 거래 내역
        if results['trades']:
            st.markdown("#### 📋 거래 내역 (최근 10건)")
            trades_df = pd.DataFrame(results['trades'][-10:])
            if not trades_df.empty:
                st.dataframe(trades_df)

# 메인 애플리케이션 클래스
class IntegratedInvestmentAdvisor:
    """통합된 투자 어드바이저"""
    
    def __init__(self):
        self.session_id = self._init_session()
        self.ai_client = HyperCLOVAXClient()
        self.advanced_features = AdvancedFeatures()
        self.backtesting = BacktestingEngine()
        
        # 통합 알림 시스템 초기화
        self.alert_system = init_unified_alert_system()
        
        # 통합 CTA 시스템 초기화
        self.cta_manager = init_integrated_cta_system()
        
    def _init_session(self) -> str:
        """세션 초기화"""
        if 'session_id' not in st.session_state:
            st.session_state.session_id = str(uuid.uuid4())
        
        if 'session_start' not in st.session_state:
            st.session_state.session_start = datetime.now()
            
        if 'user_question' not in st.session_state:
            st.session_state.user_question = ""
            
        if 'selected_question' not in st.session_state:
            st.session_state.selected_question = ""
        
        # 통합 CTA 세션 추적 초기화
        initialize_session_tracking()
        
        return st.session_state.session_id
    
    def run(self):
        """메인 애플리케이션 실행"""
        try:
            # CSS 로드
            load_css()
            
            # 메인 애플리케이션 렌더링
            self._render_main_app()
            
        except Exception as e:
            logger.error(f"메인 애플리케이션 오류: {str(e)}")
            st.error(f"오류 발생: {str(e)}")
            st.markdown("### 🔧 문제 해결 방법")
            st.markdown("""
            1. **페이지 새로고침**: F5 키를 눌러 페이지를 새로고침하세요
            2. **브라우저 캐시 삭제**: 브라우저 설정에서 캐시를 삭제하세요  
            3. **다른 브라우저 시도**: Chrome, Firefox, Edge 등 다른 브라우저로 접속해보세요
            """)
    
    def _render_main_app(self):
        """메인 애플리케이션 렌더링"""
        # 헤더 렌더링
        current_time = datetime.now()
        self._render_header(current_time)
        
        # 실시간 데이터 로드
        with st.spinner("📊 실시간 시장 데이터 로딩 중..."):
            market_data = get_market_data()
            news_data = get_news_data()
        
        # 사이드바 렌더링
        self._render_sidebar(market_data)
        
        # 메인 탭 구성 - 통합 CTA 시스템 포함
        main_tabs = st.tabs([
            "🏠 홈", 
            "🤖 AI 분석", 
            "🔔 통합 알림 센터", 
            "🎯 마케팅 CTA",
            "🚀 고급 기능", 
            "📊 백테스팅",
            "📈 기술적 분석"
        ])
        
        # 탭 콘텐츠 렌더링
        with main_tabs[0]:
            self._render_home_content(market_data, news_data)
        
        with main_tabs[1]:
            self._render_ai_analysis_content(market_data, news_data)
        
        with main_tabs[2]:
            # 통합 실시간 알림 시스템
            integrate_unified_realtime_alerts()
        
        with main_tabs[3]:
            # 통합 CTA 마케팅 시스템
            self._render_cta_marketing_content()
        
        with main_tabs[4]:
            self.advanced_features.render_portfolio_analyzer()
        
        with main_tabs[5]:
            self.backtesting.render_backtesting()
        
        with main_tabs[6]:
            self.advanced_features.render_technical_analysis()
        
        # 면책조항
        self._show_disclaimer()
        
        # 만든이 정보
        self._render_creator_info()
    
    def _render_header(self, current_time):
        """헤더 렌더링"""
        st.markdown('<div class="main-header">🤖 HyperCLOVA X AI 투자 어드바이저</div>', unsafe_allow_html=True)
        
        # 알림 개수 및 CTA 상태 표시
        try:
            alert_stats = self.alert_system.get_alert_statistics()
            unread_count = alert_stats.get('unread', 0)
            alert_badge = f" 🔔 {unread_count}개 알림" if unread_count > 0 else ""
            
            # CTA 성과 간단 표시
            cta_metrics = self.cta_manager.get_dashboard_metrics()
            conversion_rate = cta_metrics.get('conversion_metrics', {}).get('conversion_rate', 0)
            cta_badge = f" 🎯 전환율 {conversion_rate}%" if conversion_rate > 0 else ""
        except:
            alert_badge = ""
            cta_badge = ""
        
        st.markdown(f"""
        <p style="text-align: center; color: #666; font-size: 1.1rem;">
            🔴 실시간 분석 • 📊 Live Market Data • 🎯 통합 CTA 시스템 • 🚀 모든 기능 활성화{alert_badge}{cta_badge}
        </p>
        <p style="text-align: center; color: #999; font-size: 0.9rem;">
            📅 {current_time.strftime("%Y년 %m월 %d일 %H시 %M분 %S초")}
        </p>
        """, unsafe_allow_html=True)
    
    def _render_sidebar(self, market_data):
        """사이드바 렌더링"""
        with st.sidebar:
            st.header("🏆 AI Festival 2025")
            
            # API 상태
            if self.ai_client.api_key:
                st.markdown('<div class="status-good">🔴 LIVE - HyperCLOVA X 연결됨</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="status-bad">❌ API 키 미설정</div>', unsafe_allow_html=True)
            
            # 알림 상태
            try:
                alert_stats = self.alert_system.get_alert_statistics()
                total_alerts = alert_stats.get('total', 0)
                unread_alerts = alert_stats.get('unread', 0)
                
                if unread_alerts > 0:
                    st.markdown(f'<div class="status-good">🔔 새 알림 {unread_alerts}개</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="status-good">✅ 알림 시스템 활성화</div>', unsafe_allow_html=True)
            except:
                st.markdown('<div class="status-good">✅ 알림 시스템 준비</div>', unsafe_allow_html=True)
            
            # CTA 시스템 상태
            try:
                cta_metrics = self.cta_manager.get_dashboard_metrics()
                active_leads = cta_metrics.get('active_leads', 0)
                if active_leads > 0:
                    st.markdown(f'<div class="status-good">🎯 활성 리드 {active_leads}개</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="status-good">🎯 CTA 시스템 활성화</div>', unsafe_allow_html=True)
            except:
                st.markdown('<div class="status-good">🎯 CTA 시스템 준비</div>', unsafe_allow_html=True)
            
            st.markdown("---")
            
            # 실시간 시장 현황
            st.markdown("### 📊 실시간 시장 현황")
            if market_data:
                for name, data in market_data.items():
                    change_color = "normal" if abs(data['change']) < 2 else "inverse"
                    st.metric(
                        name,
                        f"{data['current']:.2f}",
                        f"{data['change']:+.2f}%",
                        delta_color=change_color
                    )
                    
                    # 큰 변동 시 자동 알림
                    if abs(data['change']) >= 3:
                        try:
                            alert_type = "투자 기회" if data['change'] > 0 else "리스크 경고"
                            add_unified_alert(
                                alert_type=alert_type,
                                title=f"{name} 큰 변동",
                                message=f"{name}이 {data['change']:+.1f}% 변동했습니다.",
                                ticker=name
                            )
                        except:
                            pass
            else:
                st.info("시장 데이터 로딩 중...")
            
            st.markdown("---")
            
            # 인기 질문
            st.markdown("### 💡 인기 질문")
            popular_questions = [
                "현재 시장 상황 분석",
                "오늘 매매 타이밍은?", 
                "지금 주목해야 할 섹터",
                "실시간 리스크 요인"
            ]
            
            for question in popular_questions:
                if st.button(question, key=f"sidebar_{question}", use_container_width=True):
                    st.session_state.selected_question = question
                    # 사용자 여정 추적
                    track_user_journey("question_selected", {"question": question})
                    st.rerun()
            
            st.markdown("---")
            
            # 빠른 알림 생성 (데모용)
            if st.button("🎯 데모 알림 생성", key="quick_demo", use_container_width=True):
                try:
                    add_unified_alert(
                        alert_type="투자 기회",
                        title="데모 알림",
                        message=f"테스트 알림이 생성되었습니다. ({datetime.now().strftime('%H:%M:%S')})",
                        ticker="DEMO"
                    )
                    st.success("데모 알림 생성됨!")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"알림 생성 실패: {e}")
            
            st.caption(f"🔴 실시간 업데이트: {datetime.now().strftime('%H:%M:%S')}")
    
    def _render_home_content(self, market_data, news_data):
        """홈 화면 렌더링"""
        st.markdown("### 🏠 AI 투자 어드바이저 홈")
        
        # 기능 소개 카드
        st.markdown("#### 🌟 주요 기능")
        
        feature_cols = st.columns(5)
        
        features = [
            {
                "icon": "🤖",
                "title": "AI 실시간 분석",
                "desc": "HyperCLOVA X 기반 맞춤 분석"
            },
            {
                "icon": "🔔",
                "title": "통합 알림 센터",
                "desc": "24/7 포트폴리오 모니터링"
            },
            {
                "icon": "🎯",
                "title": "통합 CTA 시스템",
                "desc": "개인화된 투자 상담 및 추천"
            },
            {
                "icon": "📊",
                "title": "백테스팅",
                "desc": "전략 검증 및 최적화"
            },
            {
                "icon": "📈",
                "title": "기술적 분석",
                "desc": "차트 패턴 및 지표 분석"
            }
        ]
        
        for col, feature in zip(feature_cols, features):
            with col:
                st.markdown(f"""
                <div class="feature-card">
                    <div style="font-size: 2rem; text-align: center;">{feature["icon"]}</div>
                    <h4 style="text-align: center; margin: 0.5rem 0;">{feature["title"]}</h4>
                    <p style="text-align: center; color: #666;">{feature["desc"]}</p>
                </div>
                """, unsafe_allow_html=True)
        
        # 시장 개요
        if market_data:
            st.markdown("#### 📈 오늘의 시장")
            key_indices = ["KOSPI", "KOSDAQ", "NASDAQ", "S&P 500"]
            cols = st.columns(len(key_indices))
            
            for i, index_name in enumerate(key_indices):
                if index_name in market_data:
                    data = market_data[index_name]
                    with cols[i]:
                        st.metric(
                            label=index_name,
                            value=f"{data['current']:.2f}",
                            delta=f"{data['change']:+.2f}%",
                            delta_color="normal"
                        )
        
        # 최신 뉴스
        if news_data:
            st.markdown("#### 📰 최신 뉴스")
            for article in news_data[:3]:
                with st.container():
                    st.markdown(f"**{article['title']}**")
                    if article.get('summary'):
                        st.caption(f"{article['summary'][:100]}...")
                    st.caption(f"출처: {article.get('source', 'News')} | {article.get('published', '최근')}")
        
        # 최근 알림 미리보기
        try:
            alert_stats = self.alert_system.get_alert_statistics()
            recent_alerts = alert_stats.get('recent', [])
            
            if recent_alerts:
                st.markdown("#### 🔔 최근 알림")
                for alert in recent_alerts[:3]:
                    priority_icons = {"긴급": "🚨", "높음": "⚠️", "중간": "📌", "낮음": "💡"}
                    icon = priority_icons.get(alert.get('priority', '중간'), "📌")
                    
                    st.markdown(f"""
                    <div style="background: #f8f9fa; padding: 0.8rem; border-radius: 0.5rem; 
                                margin: 0.3rem 0; border-left: 3px solid #2196f3;">
                        {icon} {alert.get('title', '')}
                        <span style="float: right; font-size: 0.8rem; color: #999;">
                            {alert.get('timestamp', datetime.now()).strftime('%H:%M') if hasattr(alert.get('timestamp', ''), 'strftime') else '최근'}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
        except:
            pass
        
        # 홈 화면용 통합 CTA 표시
        try:
            user_profile = {
                'session_id': st.session_state.session_id,
                'page_context': 'home'
            }
            show_comprehensive_cta_experience(user_profile, None, "home")
        except Exception as e:
            logger.warning(f"CTA 표시 실패: {e}")
            # 기본 CTA 표시
            self._show_basic_cta()
    
    def _render_ai_analysis_content(self, market_data, news_data):
        """AI 분석 콘텐츠 렌더링"""
        st.markdown("### 💬 실시간 AI 투자 분석")
        
        # 실시간 데이터 표시
        if market_data or news_data:
            with st.expander("📊 현재 사용 중인 실시간 데이터", expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**시장 지수**")
                    for name, data in market_data.items():
                        st.write(f"• {name}: {data['current']:.2f} ({data['change']:+.2f}%)")
                
                with col2:
                    st.markdown("**최신 뉴스**")
                    for i, article in enumerate(news_data[:3], 1):
                        st.write(f"• {article['title'][:50]}...")
        
        # 선택된 질문 업데이트
        if st.session_state.selected_question:
            st.session_state.user_question = st.session_state.selected_question
            st.session_state.selected_question = ""
        
        # 질문 입력
        user_question = st.text_area(
            "",
            value=st.session_state.user_question,
            placeholder="예: 삼성전자 70,000원에 100주 보유 중인데 계속 들고 있는 게 맞을까요?",
            height=100,
            label_visibility="collapsed",
            key="question_input"
        )
        
        if user_question != st.session_state.user_question:
            st.session_state.user_question = user_question
        
        # 분석 버튼
        if st.button("🔴 실시간 AI 분석 시작", type="primary", use_container_width=True):
            if not self.ai_client.api_key:
                st.error("⚠️ API 키가 설정되지 않았습니다.")
                return
            
            if not st.session_state.user_question.strip():
                st.warning("💬 분석할 질문을 입력해주세요.")
                return
            
            # 사용자 여정 추적
            track_user_journey("ai_analysis_started", {"question": st.session_state.user_question})
            
            # 포트
