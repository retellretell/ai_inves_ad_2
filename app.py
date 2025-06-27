import os
from datetime import datetime

import requests
import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

# ----- 설정 -----
# API 키 및 엔드포인트는 환경변수 또는 Streamlit secrets에서 불러옵니다.
HYPERCLOVA_API_KEY = os.getenv("HYPERCLOVA_API_KEY", st.secrets.get("HYPERCLOVA_API_KEY", ""))
HYPERCLOVA_ENDPOINT = os.getenv("HYPERCLOVA_ENDPOINT", st.secrets.get("HYPERCLOVA_ENDPOINT", ""))

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", st.secrets.get("OPENAI_API_KEY", ""))
NEWS_API_KEY = os.getenv("NEWS_API_KEY", st.secrets.get("NEWS_API_KEY", ""))
FMP_API_KEY = os.getenv("FMP_API_KEY", st.secrets.get("FMP_API_KEY", ""))  # FinancialModelingPrep ESG
# ----------------

st.set_page_config(page_title="HyperCLOVA X 기반 AI 투자 어드바이저")
st.title("HyperCLOVA X 기반 AI 투자 어드바이저")


def get_ai_response(question: str) -> str:
    """HyperCLOVA X 또는 ChatGPT API를 통해 답변을 반환합니다."""
    if HYPERCLOVA_API_KEY and HYPERCLOVA_ENDPOINT:
        try:
            headers = {"Authorization": f"Bearer {HYPERCLOVA_API_KEY}"}
            payload = {"prompt": question, "max_tokens": 300}
            res = requests.post(HYPERCLOVA_ENDPOINT, headers=headers, json=payload, timeout=10)
            res.raise_for_status()
            data = res.json()
            if isinstance(data, dict) and data.get("text"):
                return data["text"].strip()
        except Exception as e:
            st.warning(f"HyperCLOVA X API 오류: {e}")

    if OPENAI_API_KEY:
        try:
            headers = {
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": question}],
            }
            res = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=10,
            )
            res.raise_for_status()
            data = res.json()
            return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            return f"AI 응답을 가져올 수 없습니다: {e}"
    return "AI API 설정이 필요합니다."


def get_esg_info(symbol: str) -> str:
    """FinancialModelingPrep API를 이용해 ESG 정보를 가져옵니다."""
    if not symbol:
        return "종목 코드가 필요합니다."
    if not FMP_API_KEY:
        return "ESG API 키가 설정되지 않았습니다."
    url = "https://financialmodelingprep.com/api/v4/esg-environmental-social-governance-data"
    params = {"symbol": symbol, "apikey": FMP_API_KEY}
    try:
        res = requests.get(url, params=params, timeout=10)
        res.raise_for_status()
        data = res.json()
        if data:
            esg = data[0]
            return (
                f"환경 점수: {esg.get('environmentalScore')} | "
                f"사회 점수: {esg.get('socialScore')} | "
                f"지배구조 점수: {esg.get('governanceScore')}"
            )
    except Exception as e:
        return f"ESG 정보를 가져올 수 없습니다: {e}"
    return "해당 종목의 ESG 정보가 없습니다."


def get_news(query: str):
    """News API를 통해 최신 뉴스를 반환합니다."""
    if not NEWS_API_KEY:
        return ["NEWS API 키가 설정되지 않았습니다."]
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "apiKey": NEWS_API_KEY,
        "language": "ko",
        "pageSize": 5,
        "sortBy": "publishedAt",
    }
    try:
        res = requests.get(url, params=params, timeout=10)
        res.raise_for_status()
        articles = res.json().get("articles", [])
        return [f"[{a['title']}]({a['url']})" for a in articles]
    except Exception as e:
        return [f"뉴스를 가져올 수 없습니다: {e}"]


def get_market_chart(symbol: str):
    """yfinance 데이터를 이용한 주가 시각화 그래프를 반환합니다."""
    try:
        data = yf.download(symbol, period="3mo", progress=False)
        if data.empty:
            return None
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(x=data.index, y=data["Close"], mode="lines", name="Close")
        )
        fig.update_layout(title=f"{symbol} 최근 3개월 주가", xaxis_title="날짜", yaxis_title="종가")
        return fig
    except Exception as e:
        st.warning(f"주가 데이터를 가져올 수 없습니다: {e}")
        return None


question = st.text_input("금융 관련 질문을 입력하세요")
symbol = st.text_input("종목 코드 (예: 005930.KS)", value="005930.KS")

if st.button("분석 요청"):
    if not question:
        st.warning("질문을 입력해주세요.")
    else:
        with st.spinner("AI가 응답을 생성 중입니다..."):
            answer = get_ai_response(question)

        tabs = st.tabs(["요약 답변", "ESG 분석", "최신 뉴스", "시장 영향"])
        with tabs[0]:
            st.write(answer)
        with tabs[1]:
            st.write(get_esg_info(symbol))
        with tabs[2]:
            for line in get_news(symbol.split(".")[0]):
                st.write("-", line)
        with tabs[3]:
            fig = get_market_chart(symbol)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.write("주가 정보를 표시할 수 없습니다.")
