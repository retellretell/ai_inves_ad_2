"""
ai_client.py - HyperCLOVA X AI 클라이언트
"""

import requests
import logging
from datetime import datetime
from config import Config, get_api_key
from data_collector import (
    get_real_time_market_data, get_recent_news, 
    get_dart_disclosure_data, get_naver_search_trends, 
    get_economic_indicators
)

logger = logging.getLogger(__name__)

class EnhancedHyperCLOVAXClient:
    def __init__(self):
        self.api_key = get_api_key()
        self.base_url = Config.CLOVA_BASE_URL
        
    def get_personalized_analysis(self, question: str, portfolio_info: dict = None) -> str:
        """개인화된 실시간 투자 분석"""
        if not self.api_key:
            raise Exception("API 키가 설정되지 않았습니다. .streamlit/secrets.toml 파일에 CLOVA_STUDIO_API_KEY를 설정해주세요.")
        
        # 모든 데이터 소스 수집
        market_data = get_real_time_market_data()
        news_data = get_recent_news()
        dart_data = get_dart_disclosure_data()
        search_trends = get_naver_search_trends()
        economic_data = get_economic_indicators()
        
        # 개인화 분석을 위한 추가 정보
        personalized_context = self._build_portfolio_context(portfolio_info, market_data)
        
        # 통합 컨텍스트 구성
        comprehensive_context = self._build_comprehensive_context(
            market_data, news_data, dart_data, 
            search_trends, economic_data, personalized_context
        )
        
        current_time = datetime.now().strftime('%Y년 %m월 %d일 %H시 %M분')
        
        # 개인화된 시스템 프롬프트
        system_prompt = self._build_system_prompt(current_time, comprehensive_context)
        
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
                        'content': self._build_user_prompt(question, current_time)
                    }
                ],
                **Config.AI_PARAMS
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            
            return self._process_response(response, current_time)
                
        except requests.exceptions.ConnectTimeout:
            raise Exception("네트워크 연결 시간 초과: 인터넷 연결을 확인하고 다시 시도해주세요")
        except requests.exceptions.ConnectionError:
            raise Exception("네트워크 연결 오류: 인터넷 연결 상태를 확인해주세요")
        except Exception as e:
            raise e
    
    def _build_portfolio_context(self, portfolio_info, market_data):
        """포트폴리오 컨텍스트 구성"""
        if not portfolio_info:
            return ""
        
        current_price = None
        if portfolio_info.get('ticker'):
            # 해당 종목의 현재가 찾기
            for name, data in market_data.items():
                # 간단한 매칭 로직 (실제로는 더 정교한 매칭 필요)
                if name.lower() in portfolio_info.get('stock', '').lower():
                    current_price = data['current']
                    break
            
            # 수익률 계산
            if current_price and portfolio_info.get('buy_price') and portfolio_info.get('shares'):
                buy_price = portfolio_info['buy_price']
                shares = portfolio_info['shares']
                
                profit_loss = (current_price - buy_price) * shares
                profit_rate = ((current_price - buy_price) / buy_price) * 100
                current_value = current_price * shares
                invested_amount = buy_price * shares
                
                return f"""
=== 👤 사용자 포트폴리오 분석 ===
보유 종목: {portfolio_info.get('stock', '알 수 없음')}
매수가: {buy_price:,.0f}원
보유 주식: {shares:,}주
현재가: {current_price:,.0f}원
투자금액: {invested_amount:,.0f}원
현재가치: {current_value:,.0f}원
평가손익: {profit_loss:,.0f}원 ({profit_rate:+.2f}%)
                """
        return ""
    
    def _build_comprehensive_context(self, market_data, news_data, dart_data, 
                                   search_trends, economic_data, personalized_context=""):
        """종합 데이터 컨텍스트 구성"""
        context_parts = []
        
        # 개인화 정보가 있으면 최우선 배치
        if personalized_context:
            context_parts.append(personalized_context)
        
        # 1. 실시간 시장 데이터
        if market_data:
            context_parts.append("\n=== 📈 실시간 시장 데이터 ===")
            for name, data in market_data.items():
                collected_time = data.get('collected_at', '알 수 없음')
                change_symbol = "📈" if data['change'] >= 0 else "📉"
                volume_info = f" | 거래량: {data.get('volume_ratio', 0):.0f}%" if data.get('volume_ratio') else ""
                context_parts.append(f"{change_symbol} {name}: {data['current']:.2f} ({data['change']:+.2f}%){volume_info} [수집: {collected_time}]")
        
        # 2. 최신 뉴스
        if news_data:
            context_parts.append("\n=== 📰 최신 경제 뉴스 ===")
            for i, article in enumerate(news_data[:4], 1):
                collected_time = article.get('collected_at', '알 수 없음')
                context_parts.append(f"{i}. {article['title']} [수집: {collected_time}]")
        
        # 3. DART 공시 정보
        if dart_data:
            context_parts.append("\n=== 📋 최신 기업 공시 (DART) ===")
            for i, disclosure in enumerate(dart_data[:3], 1):
                corp_name = disclosure.get('corp_name', '알 수 없음')
                report_nm = disclosure.get('report_nm', '알 수 없음')
                context_parts.append(f"{i}. {corp_name}: {report_nm}")
        
        # 4. 네이버 검색 트렌드
        if search_trends:
            context_parts.append("\n=== 🔍 투자 관련 검색 트렌드 (네이버) ===")
            for trend in search_trends[:4]:
                keyword = trend.get('title', '알 수 없음')
                if trend.get('data') and len(trend['data']) >= 2:
                    recent_ratio = trend['data'][-1]['ratio']
                    prev_ratio = trend['data'][-2]['ratio']
                    change = recent_ratio - prev_ratio
                    change_text = f"({change:+.0f})" if change != 0 else ""
                    context_parts.append(f"• {keyword}: 관심도 {recent_ratio}{change_text}")
        
        # 5. 경제 지표
        if economic_data:
            context_parts.append("\n=== 💹 주요 경제 지표 ===")
            for indicator, value in economic_data.items():
                if indicator != 'updated_at':
                    context_parts.append(f"• {value}")
            if 'updated_at' in economic_data:
                context_parts.append(f"[업데이트: {economic_data['updated_at']}]")
        
        return "\n".join(context_parts)
    
    def _build_system_prompt(self, current_time, comprehensive_context):
        """시스템 프롬프트 구성"""
        return f"""당신은 미래에셋증권 AI Festival 2025 출품작의 전문 AI 투자 어드바이저입니다.

🔴 **개인화 실시간 투자 분석 (현재: {current_time})**

다음 모든 실시간 데이터와 사용자 개인 포트폴리오를 종합적으로 분석하여 맞춤형 투자 조언을 제공해주세요:

{comprehensive_context}

**분석 원칙:**
1. 사용자의 개인 포트폴리오 상황을 최우선 고려
2. 모든 실시간 데이터를 통합적으로 분석
3. 미래에셋증권 수준의 전문적 분석
4. 구체적이고 실행 가능한 조언 제공
5. 과거 참조 절대 금지 (현재 시점 기준)

**답변 형식:**
👤 **개인 포트폴리오 현황** ({current_time})
📊 **실시간 시장 분석** 
💡 **맞춤형 투자 전략**
⚠️ **개인별 리스크 관리**  
📈 **구체적 실행 방안**
🕐 **매매 타이밍 조언**
📋 **분석 근거 요약**

사용자의 개인 상황에 최적화된 전문적 투자 조언을 제공해주세요."""
    
    def _build_user_prompt(self, question, current_time):
        """사용자 프롬프트 구성"""
        return f"""🔴 개인화 실시간 분석 요청 ({current_time})

질문: {question}

⚠️ 위의 실시간 데이터와 개인 포트폴리오 정보를 모두 종합하여 
현재 시점 기준으로 개인 맞춤형 투자 조언을 제공해주세요.
미래에셋증권 수준의 전문적이고 구체적인 실행 방안을 제시해주세요."""
    
    def _process_response(self, response, current_time):
        """AI 응답 처리"""
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
                    return f"""🏆 **미래에셋증권 AI Festival 2025 - 개인화 분석**
📅 분석 시간: {current_time}
🤖 AI 엔진: HyperCLOVA X ({Config.CLOVA_MODEL})

{content}

---
📊 **종합 데이터 출처**:
• 개인 포트폴리오: 사용자 입력 기반 실시간 계산
• 시장 데이터: yfinance API (5분 간격)
• 뉴스: Reuters, Yahoo Finance (30분 간격)
• 공시 정보: DART API (1시간 간격)
• 검색 트렌드: 네이버 데이터랩 (1시간 간격)
• 경제 지표: 공개 데이터 종합
• 분석 시점: {current_time}"""
                else:
                    raise Exception("AI 응답이 비어있습니다.")
            else:
                raise Exception(f"응답 형식 오류: {result}")
                
        elif response.status_code == 401:
            raise Exception("API 키 인증 실패: 네이버 클라우드 플랫폼에서 API 키를 다시 확인해주세요")
        elif response.status_code == 403:
            raise Exception("API 접근 권한 없음: 테스트 앱 'AI투자어드바이저_API'가 제대로 생성되었는지 확인해주세요")
        elif response.status_code == 404:
            raise Exception("API 엔드포인트 없음: HCX-005 모델 URL을 확인해주세요")
        elif response.status_code == 429:
            raise Exception("API 사용량 한도 초과: 잠시 후 다시 시도해주세요")
        else:
            raise Exception(f"API 호출 실패 (HTTP {response.status_code}): {response.text[:200]}")
