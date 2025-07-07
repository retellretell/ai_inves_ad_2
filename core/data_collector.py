"""
data_collector.py - 실시간 데이터 수집 모듈
"""

import streamlit as st
import yfinance as yf
import requests
import feedparser
from datetime import datetime, timedelta
import logging

from config import Config, get_dart_api_key, get_naver_api_keys

logger = logging.getLogger(__name__)

@st.cache_data(ttl=Config.MARKET_DATA_TTL)
def get_real_time_market_data():
    """실시간 시장 데이터 수집"""
    try:
        collected_time = datetime.now()
        
        # 주요 지수 데이터
        indices = {
            "KOSPI": "^KS11",
            "KOSDAQ": "^KQ11",
            "삼성전자": "005930.KS",
            "SK하이닉스": "000660.KS",
            "NAVER": "035420.KS",
            "카카오": "035720.KS",
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
                    
                    # 거래량 정보 추가
                    volume = data['Volume'].iloc[-1] if not data['Volume'].empty else 0
                    avg_volume = data['Volume'].mean() if not data['Volume'].empty else 0
                    volume_ratio = (volume / avg_volume * 100) if avg_volume > 0 else 0
                    
                    market_data[name] = {
                        'current': current,
                        'change': change,
                        'volume': volume,
                        'volume_ratio': volume_ratio,
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

@st.cache_data(ttl=Config.NEWS_DATA_TTL)
def get_recent_news():
    """최신 경제 뉴스 수집"""
    try:
        collected_time = datetime.now()
        
        news_sources = [
            'https://feeds.finance.yahoo.com/rss/2.0/headline',
            'https://feeds.reuters.com/reuters/businessNews',
            'https://rss.cnn.com/rss/money_news_international.rss'
        ]
        
        articles = []
        for url in news_sources:
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries[:2]:
                    articles.append({
                        'title': entry.get('title', ''),
                        'summary': entry.get('summary', ''),
                        'published': entry.get('published', ''),
                        'source': feed.feed.get('title', 'News'),
                        'collected_at': collected_time.strftime('%H:%M:%S')
                    })
            except Exception as e:
                logger.warning(f"뉴스 수집 실패 ({url}): {e}")
                continue
        
        return articles[:6]
    except Exception as e:
        logger.error(f"뉴스 수집 오류: {e}")
        return []

@st.cache_data(ttl=Config.DART_DATA_TTL)
def get_dart_disclosure_data():
    """DART 공시 정보 수집"""
    try:
        dart_api_key = get_dart_api_key()
        if not dart_api_key:
            return []
        
        url = "https://opendart.fss.or.kr/api/list.json"
        params = {
            'crtfc_key': dart_api_key,
            'corp_cls': 'Y',
            'bgn_de': (datetime.now() - timedelta(days=3)).strftime('%Y%m%d'),
            'end_de': datetime.now().strftime('%Y%m%d'),
            'page_no': 1,
            'page_count': 50
        }
        
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == '000':
                return data.get('list', [])[:10]
        
        return []
    except Exception as e:
        logger.error(f"DART 공시 데이터 수집 오류: {e}")
        return []

@st.cache_data(ttl=Config.TREND_DATA_TTL)
def get_naver_search_trends():
    """네이버 데이터랩 검색 트렌드"""
    try:
        client_id, client_secret = get_naver_api_keys()
        if not client_id or not client_secret:
            return []
        
        url = "https://openapi.naver.com/v1/datalab/search"
        headers = {
            'X-Naver-Client-Id': client_id,
            'X-Naver-Client-Secret': client_secret,
            'Content-Type': 'application/json'
        }
        
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        keywords = ["주식", "투자", "삼성전자", "반도체", "AI"]
        
        body = {
            "startDate": start_date,
            "endDate": end_date,
            "timeUnit": "week",
            "keywordGroups": [
                {"groupName": keyword, "keywords": [keyword]}
                for keyword in keywords[:5]
            ]
        }
        
        response = requests.post(url, headers=headers, json=body, timeout=10)
        if response.status_code == 200:
            return response.json().get('results', [])
        
        return []
    except Exception as e:
        logger.error(f"네이버 검색 트렌드 수집 오류: {e}")
        return []

@st.cache_data(ttl=7200)
def get_economic_indicators():
    """경제 지표 데이터"""
    try:
        current_time = datetime.now()
        indicators = {
            "base_rate": "기준금리 3.50% 동결",
            "cpi": f"소비자물가지수 전월 대비 0.2% 상승",
            "exchange_rate": "원/달러 환율 1,340원대 안정",
            "trade_balance": "무역수지 흑자 전환",
            "updated_at": current_time.strftime('%H:%M:%S')
        }
        
        return indicators
    except Exception as e:
        logger.error(f"경제지표 수집 오류: {e}")
        return {}

@st.cache_data(ttl=Config.MARKET_DATA_TTL)
def get_stock_data(ticker: str):
    """개별 주식 데이터 수집"""
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period="6mo")
        if data.empty:
            raise ValueError(f"'{ticker}' 데이터를 찾을 수 없습니다.")
        return data
    except Exception as e:
        logger.error(f"주식 데이터 오류: {str(e)}")
        return None
