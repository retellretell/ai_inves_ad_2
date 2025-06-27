import os
import requests
import streamlit as st
from datetime import datetime
import yfinance as yf
import plotly.graph_objects as go

# 앱 설정
st.set_page_config(page_title="HyperCLOVA X 기반 AI 투자 어드바이저")
st.title("HyperCLOVA X 기반 AI 투자 어드바이저")

# ----- 환경 설정 -----
HYPERCLOVA_API_KEY = os.getenv("HYPERCLOVA_API_KEY", st.secrets.get("HYPERCLOVA_API_KEY", ""))
HYPERCLOVA_ENDPOINT = os.getenv("HYPERCLOVA_ENDPOINT", st.secrets.get("HYPERCLOVA_ENDPOINT", ""))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", st.secrets.get("OPENAI_API_KEY", ""))
NEWS_API_KEY = os.getenv("NEWS_API_KEY", st.secrets.get("NEWS_API_KEY", ""))
FMP_API_KEY = os.getenv("FMP_API_KEY", st.secrets.get("FMP_API_KEY", ""))
# ---------------------

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
            res = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=10)
            res.raise_for_status()
            data = res.json()["choices"][0]["message"]["content"].strip()
            return data
        except Exception as e:
            st.error(f"AI 응답 오류: {e}")

    return "AI API 설정이 필요합니다."


def sample_esg_info() -> str:
    """Return sample ESG analysis for Samsung Electronics."""
    return (
        "삼성전자 ESG 분석 예시:\n"
        "- 환경(E) 점수: 80/100\n"
        "- 사회(S) 점수: 75/100\n"
        "- 지배구조(G) 점수: 78/100"
    )


def sample_news() -> list[str]:
    """Return sample financial news."""
    return [
        "한국은행, 기준금리 동결 발표",
        "삼성전자, 2분기 실적 발표 예정",
        "미국 증시, 금리 인상 우려로 하락 마감"
    ]


def sample_market_analysis() -> str:
    """Return market impact analysis sample."""
    return (
        "최근 시장은 인플레이션 우려와 금리 인상 가능성에 따라 하락세를 보이고 있습니다. "
        "기술주는 비교적 안정적인 모습을 보이고 있으며, ESG 기준을 만족하는 종목들이 주목받고 있습니다."
    )


def fetch_stock_quote(symbol: str):
    """Fetch stock quote summary."""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        return None, {
            "현재가": info.get("regularMarketPrice"),
            "시가총액": info.get("marketCap"),
            "52주 최고": info.get("fiftyTwoWeekHigh"),
            "52주 최저": info.get("fiftyTwoWeekLow"),
        }
    except Exception as e:
        return str(e), None


def get_esg_info(symbol: str) -> str:
    """Fetch ESG data from FMP API."""
    try:
        if not FMP_API_KEY:
            return "FMP API 키가 필요합니다."

        base_symbol = symbol.split(".")[0]
        url = f"https://financialmodelingprep.com/api/v4/esg-environmental-social-governance-data?symbol={base_symbol}&apikey={FMP_API_KEY}"
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        data = res.json()

        if not data:
            return "ESG 데이터를 찾을 수 없습니다."

        item = data[0]
        return (
            f"- 환경 점수: {item.get('environmentalScore', 'N/A')}\n"
            f"- 사회 점수: {item.get('socialScore', 'N/A')}\n"
            f"- 지배구조 점수: {item.get('governanceScore', 'N/A')}"
        )
    except Exception as e:
        return f"ESG 정보를 가져오는 중 오류 발생: {e}"


def get_news(symbol: str) -> list[str]:
    """Fetch latest news using NewsAPI."""
    try:
        if not NEWS_API_KEY:
            return ["News API 키가 필요합니다."]
        query = f"{symbol} 주가"
        url = f"https://newsapi.org/v2/everything?q={query}&language=ko&apiKey={NEWS_API_KEY}"
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        articles = res.json().get("articles", [])
        return [article["title"] for article in articles[:5]]
    except Exception as e:
        return [f"뉴스를 불러오는 중 오류 발생: {e}"]


def get_market_chart(symbol: str):
    """Return 3-month stock chart."""
    try:
        data = yf.download(symbol, period="3mo")
        if data.empty:
            return None
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data.index, y=data["Close"], mode="lines", name="Close"))
        fig.update_layout(title=f"{symbol} 최근 3개월 주가", xaxis_title="날짜", yaxis_title="종가")
        return fig
    except Exception as e:
        st.warning(f"주가 데이터를 가져올 수 없습니다: {e}")
        return None


# ----- Streamlit UI -----
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
