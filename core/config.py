"""
config.py - 설정 및 환경변수 관리
"""

import streamlit as st
import os
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 페이지 설정
def setup_page_config():
    """Streamlit 페이지 설정"""
    st.set_page_config(
        page_title="HyperCLOVA X AI 투자 어드바이저",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )

# API 키 관리
def get_api_key():
    """CLOVA Studio API 키 가져오기"""
    try:
        return st.secrets.get("CLOVA_STUDIO_API_KEY", "")
    except:
        return os.getenv("CLOVA_STUDIO_API_KEY", "")

def get_dart_api_key():
    """DART API 키 가져오기"""
    try:
        return st.secrets.get("DART_API_KEY", "")
    except:
        return os.getenv("DART_API_KEY", "")

def get_naver_api_keys():
    """네이버 API 키들 가져오기"""
    try:
        client_id = st.secrets.get("NAVER_CLIENT_ID", "")
        client_secret = st.secrets.get("NAVER_CLIENT_SECRET", "")
        return client_id, client_secret
    except:
        return os.getenv("NAVER_CLIENT_ID", ""), os.getenv("NAVER_CLIENT_SECRET", "")

# 하이퍼파라미터 및 설정값
class Config:
    # API 설정
    CLOVA_BASE_URL = "https://clovastudio.stream.ntruss.com"
    CLOVA_MODEL = "HCX-005"
    
    # 캐시 설정 (초)
    MARKET_DATA_TTL = 300  # 5분
    NEWS_DATA_TTL = 1800   # 30분
    DART_DATA_TTL = 3600   # 1시간
    TREND_DATA_TTL = 3600  # 1시간
    
    # AI 모델 파라미터
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
    
    # 기본 주식 매핑
    DEFAULT_STOCKS = {
        # 한국 주요 종목
        "삼성전자": "005930.KS", "삼전": "005930.KS", "samsung": "005930.KS",
        "SK하이닉스": "000660.KS", "하이닉스": "000660.KS", "sk": "000660.KS", "하닉": "000660.KS",
        "네이버": "035420.KS", "NAVER": "035420.KS", "naver": "035420.KS",
        "카카오": "035720.KS", "kakao": "035720.KS",
        "LG화학": "051910.KS", "lg": "051910.KS",
        "현대차": "005380.KS", "현차": "005380.KS", "hyundai": "005380.KS",
        
        # 미국 주요 종목
        "테슬라": "TSLA", "tesla": "TSLA", "테슬": "TSLA",
        "애플": "AAPL", "apple": "AAPL",
        "엔비디아": "NVDA", "nvidia": "NVDA",
        "마이크로소프트": "MSFT", "ms": "MSFT",
        "구글": "GOOGL", "google": "GOOGL",
        
        # 지수
        "KOSPI": "^KS11", "KOSDAQ": "^KQ11", "NASDAQ": "^IXIC", 
        "S&P 500": "^GSPC", "USD/KRW": "KRW=X"
    }
