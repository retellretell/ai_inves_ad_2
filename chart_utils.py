"""
chart_utils.py - 차트 및 시각화 유틸리티
"""

import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

def create_stock_chart(data, ticker):
    """주식 차트 생성"""
    fig = go.Figure(data=go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name=ticker
    ))
    
    fig.update_layout(
        title=f"{ticker} 주가 차트 (6개월)",
        yaxis_title="Price",
        xaxis_title="Date",
        template="plotly_white",
        height=500
    )
    
    return fig

def create_market_overview_chart(market_data):
    """시장 개요 차트 생성"""
    if not market_data:
        return None
    
    names = list(market_data.keys())[:8]  # 상위 8개
    changes = [market_data[name]['change'] for name in names]
    
    # 색상 설정 (상승/하락)
    colors = ['green' if change >= 0 else 'red' for change in changes]
    
    fig = go.Figure(data=[
        go.Bar(
            x=names,
            y=changes,
            marker_color=colors,
            text=[f"{change:+.2f}%" for change in changes],
            textposition='outside'
        )
    ])
    
    fig.update_layout(
        title="실시간 시장 현황",
        yaxis_title="변동률 (%)",
        template="plotly_white",
        height=400
    )
    
    return fig

def create_portfolio_pie_chart(portfolio_metrics):
    """포트폴리오 파이 차트 생성"""
    if not portfolio_metrics:
        return None
    
    profit_loss = portfolio_metrics['profit_loss']
    invested = portfolio_metrics['invested_amount']
    
    if profit_loss >= 0:
        labels = ['투자원금', '수익']
        values = [invested, profit_loss]
        colors = ['lightblue', 'green']
    else:
        labels = ['현재가치', '손실']
        values = [invested + profit_loss, abs(profit_loss)]
        colors = ['lightcoral', 'red']
    
    fig = go.Figure(data=[go.Pie(
        labels=labels, 
        values=values,
        marker_colors=colors
    )])
    
    fig.update_layout(
        title="포트폴리오 손익 현황",
        height=400
    )
    
    return fig

def display_market_metrics(market_data):
    """시장 지표를 메트릭 형태로 표시"""
    if not market_data:
        st.info("시장 데이터 로딩 중...")
        return
    
    # 주요 지수들만 선택
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

def display_portfolio_summary(portfolio_info, metrics):
    """포트폴리오 요약 정보 표시"""
    if not metrics:
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "투자금액",
            f"{metrics['invested_amount']:,.0f}원",
            delta=None
        )
    
    with col2:
        st.metric(
            "현재가치", 
            f"{metrics['current_value']:,.0f}원",
            delta=None
        )
    
    with col3:
        profit_color = "normal" if metrics['profit_loss'] >= 0 else "inverse"
        st.metric(
            "평가손익",
            f"{metrics['profit_loss']:,.0f}원",
            delta=f"{metrics['profit_rate']:+.2f}%",
            delta_color=profit_color
        )
    
    with col4:
        st.metric(
            "현재가",
            f"{metrics['current_price']:,.0f}원",
            delta=f"vs 매수가 {metrics['buy_price']:,.0f}원"
        )
