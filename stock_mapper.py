"""
stock_mapper.py - 자동 주식 매핑 시스템
"""

import os
import pickle
import logging
from datetime import datetime, timedelta
from config import Config

logger = logging.getLogger(__name__)

class AutoStockMapper:
    def __init__(self):
        self.stock_list = {}
        self.cache_file = "stock_mapping_cache.pkl"
        self.last_update = None
        
        # 캐시된 데이터 로드 또는 기본 데이터 사용
        self.load_cache()
        
        # 캐시가 없거나 오래된 경우 업데이트
        if self.should_update():
            self.update_stock_list()
    
    def should_update(self):
        """업데이트가 필요한지 확인"""
        if not self.last_update:
            return True
        return datetime.now() - self.last_update > timedelta(days=1)
    
    def load_cache(self):
        """캐시된 주식 리스트 로드"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'rb') as f:
                    cache_data = pickle.load(f)
                    self.stock_list = cache_data.get('stock_list', {})
                    self.last_update = cache_data.get('last_update')
                    logger.info(f"주식 리스트 캐시 로드: {len(self.stock_list)}개 종목")
            else:
                self.use_default_stocks()
        except Exception as e:
            logger.error(f"캐시 로드 오류: {e}")
            self.use_default_stocks()
    
    def save_cache(self):
        """주식 리스트 캐시 저장"""
        try:
            cache_data = {
                'stock_list': self.stock_list,
                'last_update': datetime.now()
            }
            with open(self.cache_file, 'wb') as f:
                pickle.dump(cache_data, f)
            logger.info(f"주식 리스트 캐시 저장: {len(self.stock_list)}개 종목")
        except Exception as e:
            logger.error(f"캐시 저장 오류: {e}")
    
    def update_stock_list(self):
        """주식 리스트 업데이트"""
        try:
            logger.info("주식 리스트 업데이트 시작...")
            
            # 한국 주요 종목 추가
            korean_stocks = {
                # 대형주
                "삼성전자": "005930.KS", "삼전": "005930.KS", "samsung": "005930.KS",
                "SK하이닉스": "000660.KS", "하이닉스": "000660.KS", "sk하이닉스": "000660.KS", 
                "하닉": "000660.KS", "sk": "000660.KS",
                "네이버": "035420.KS", "NAVER": "035420.KS", "naver": "035420.KS",
                "카카오": "035720.KS", "kakao": "035720.KS", "Kakao": "035720.KS",
                "LG화학": "051910.KS", "lg화학": "051910.KS", "lg": "051910.KS",
                "현대차": "005380.KS", "현차": "005380.KS", "hyundai": "005380.KS",
                "기아": "000270.KS", "KIA": "000270.KS", "kia": "000270.KS",
                "POSCO홀딩스": "005490.KS", "포스코": "005490.KS", "posco": "005490.KS",
                "LG전자": "066570.KS", "lg전자": "066570.KS", 
                "신한지주": "055550.KS", "신한": "055550.KS",
                "KB금융": "105560.KS", "kb금융": "105560.KS", "kb": "105560.KS",
                "셀트리온": "068270.KS", "celltrion": "068270.KS",
                "크래프톤": "259960.KS", "krafton": "259960.KS",
                "엔씨소프트": "036570.KS", "nc소프트": "036570.KS", "ncsoft": "036570.KS",
                "위메이드": "112040.KS", "wemade": "112040.KS",
                "펄어비스": "263750.KS", "pearl abyss": "263750.KS",
                
                # 중소형주
                "두산에너빌리티": "034020.KS", "한화시스템": "272210.KS",
                "LIG넥스원": "079550.KS", "대우조선해양": "042660.KS",
                
                # ETF 및 지수
                "KOSPI": "^KS11", "코스피": "^KS11", "kospi": "^KS11",
                "KOSDAQ": "^KQ11", "코스닥": "^KQ11", "kosdaq": "^KQ11",
                "KODEX 200": "069500.KS", "tiger 200": "102110.KS"
            }
            
            # 미국 주요 종목 추가
            us_stocks = {
                "애플": "AAPL", "apple": "AAPL", "AAPL": "AAPL",
                "마이크로소프트": "MSFT", "microsoft": "MSFT", "ms": "MSFT", "MSFT": "MSFT",
                "구글": "GOOGL", "google": "GOOGL", "GOOGL": "GOOGL", "알파벳": "GOOGL",
                "아마존": "AMZN", "amazon": "AMZN", "AMZN": "AMZN",
                "테슬라": "TSLA", "tesla": "TSLA", "TSLA": "TSLA", "테슬": "TSLA",
                "엔비디아": "NVDA", "nvidia": "NVDA", "NVDA": "NVDA",
                "메타": "META", "meta": "META", "META": "META", "페이스북": "META",
                "넷플릭스": "NFLX", "netflix": "NFLX", "NFLX": "NFLX",
                "어도비": "ADBE", "adobe": "ADBE", "ADBE": "ADBE",
                "세일즈포스": "CRM", "salesforce": "CRM", "CRM": "CRM",
                "오라클": "ORCL", "oracle": "ORCL", "ORCL": "ORCL",
                "인텔": "INTC", "intel": "INTC", "INTC": "INTC",
                "AMD": "AMD", "amd": "AMD", "어드밴스드마이크로디바이시스": "AMD",
                "퀄컴": "QCOM", "qualcomm": "QCOM", "QCOM": "QCOM",
                
                # 지수
                "NASDAQ": "^IXIC", "나스닥": "^IXIC", "nasdaq": "^IXIC",
                "S&P 500": "^GSPC", "s&p500": "^GSPC", "sp500": "^GSPC",
                "USD/KRW": "KRW=X", "달러원": "KRW=X", "환율": "KRW=X"
            }
            
            self.stock_list.update(korean_stocks)
            self.stock_list.update(us_stocks)
            
            # 캐시 저장
            self.save_cache()
            self.last_update = datetime.now()
            
            logger.info(f"주식 리스트 업데이트 완료: {len(self.stock_list)}개 종목")
            
        except Exception as e:
            logger.error(f"주식 리스트 업데이트 오류: {e}")
            self.use_default_stocks()
    
    def use_default_stocks(self):
        """기본 주식 리스트 사용"""
        self.stock_list = Config.DEFAULT_STOCKS.copy()
    
    def find_stock(self, query):
        """주식 검색 (퍼지 매칭 포함)"""
        query = query.lower().strip()
        
        # 1. 정확한 매칭
        for name, ticker in self.stock_list.items():
            if query == name.lower():
                return ticker, name, 100
        
        # 2. 부분 매칭
        for name, ticker in self.stock_list.items():
            if query in name.lower() or name.lower() in query:
                return ticker, name, 90
        
        # 3. 유사도 검색 (간단한 방식)
        best_match = None
        best_score = 0
        
        for name, ticker in self.stock_list.items():
            similarity = self.calculate_similarity(query, name.lower())
            if similarity > best_score and similarity >= 70:
                best_match = (ticker, name, similarity)
                best_score = similarity
        
        if best_match:
            return best_match
        
        return None
    
    def calculate_similarity(self, s1, s2):
        """간단한 유사도 계산 (레벤슈타인 거리 기반)"""
        if len(s1) < len(s2):
            return self.calculate_similarity(s2, s1)

        if len(s2) == 0:
            return 0

        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        # 유사도 퍼센트로 변환
        max_len = max(len(s1), len(s2))
        return ((max_len - previous_row[-1]) / max_len) * 100
