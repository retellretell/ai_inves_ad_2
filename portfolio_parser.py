"""
portfolio_parser.py - 사용자 질문에서 포트폴리오 정보 추출
"""

import re
from config import Config

def parse_user_portfolio(question):
    """사용자 질문에서 포트폴리오 정보 추출"""
    portfolio_info = {}
    
    # 종목명 추출
    for korean_name, ticker in Config.DEFAULT_STOCKS.items():
        if korean_name.lower() in question.lower():
            portfolio_info['stock'] = korean_name
            portfolio_info['ticker'] = ticker
            break
    
    # 매수가 추출 (만원, 천원, 원 단위)
    price_patterns = [
        r'(\d+)만원',  # 6만원
        r'(\d+)천원',  # 75천원  
        r'(\d+,?\d*\.?\d*)원',  # 60,000원, 75000원
        r'(\d+,?\d*\.?\d*)'  # 단순 숫자
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
                    # 가격 범위로 단위 추정
                    if price < 1000:  # 100 이하면 만원 단위로 추정
                        portfolio_info['buy_price'] = price * 10000
                    else:
                        portfolio_info['buy_price'] = price
                break
            except:
                continue
    
    # 보유 주식 수 추출
    share_patterns = [
        r'(\d+)주',
        r'(\d+)개',
        r'(\d+)장'
    ]
    
    for pattern in share_patterns:
        matches = re.findall(pattern, question)
        if matches:
            try:
                portfolio_info['shares'] = int(matches[0])
                break
            except:
                continue
    
    return portfolio_info

def calculate_portfolio_metrics(portfolio_info, current_price):
    """포트폴리오 수익률 및 손익 계산"""
    if not all([portfolio_info.get('buy_price'), 
                portfolio_info.get('shares'), 
                current_price]):
        return None
    
    buy_price = portfolio_info['buy_price']
    shares = portfolio_info['shares']
    
    metrics = {
        'invested_amount': buy_price * shares,
        'current_value': current_price * shares,
        'profit_loss': (current_price - buy_price) * shares,
        'profit_rate': ((current_price - buy_price) / buy_price) * 100,
        'current_price': current_price,
        'buy_price': buy_price,
        'shares': shares
    }
    
    return metrics

def format_portfolio_context(portfolio_info, metrics):
    """포트폴리오 정보를 컨텍스트 문자열로 포맷"""
    if not metrics:
        return ""
    
    return f"""
=== 👤 사용자 포트폴리오 분석 ===
보유 종목: {portfolio_info.get('stock', '알 수 없음')}
매수가: {metrics['buy_price']:,.0f}원
보유 주식: {metrics['shares']:,}주
현재가: {metrics['current_price']:,.0f}원
투자금액: {metrics['invested_amount']:,.0f}원
현재가치: {metrics['current_value']:,.0f}원
평가손익: {metrics['profit_loss']:,.0f}원 ({metrics['profit_rate']:+.2f}%)
    """
