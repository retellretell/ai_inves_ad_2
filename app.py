import os
import requests
import streamlit as st

# 앱 설정
st.set_page_config(page_title="HyperCLOVA X 기반 AI 투자 어드바이저")
st.title("HyperCLOVA X 기반 AI 투자 어드바이저")

# ----- 환경 설정 -----
# 실제 서비스에서는 환경변수 또는 Streamlit secrets를 이용해 API 키와
# 엔드포인트를 관리합니다.
HYPERCLOVA_API_KEY = os.getenv("HYPERCLOVA_API_KEY", "")
HYPERCLOVA_ENDPOINT = os.getenv("HYPERCLOVA_ENDPOINT", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
# ---------------------


def load_tickers(path: str = "tickers.txt") -> list[str]:
    """Return a list of stock tickers from a text file."""
    tickers: list[str] = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for row in f:
                t = row.strip()
                if t:
                    tickers.append(t)
    except FileNotFoundError:
        st.warning("tickers.txt 파일을 찾을 수 없습니다.")
    return tickers


def fetch_stock_quote(ticker: str) -> tuple[str | None, dict | None]:
    """Fetch latest quote data from Yahoo Finance."""
    try:
        url = "https://query1.finance.yahoo.com/v7/finance/quote"
        res = requests.get(url, params={"symbols": ticker}, timeout=5)
        res.raise_for_status()
        data = res.json().get("quoteResponse", {}).get("result", [])
        if not data:
            return "데이터가 없습니다.", None
        q = data[0]
        return None, {
            "가격": q.get("regularMarketPrice"),
            "변동률": q.get("regularMarketChangePercent"),
            "시장상태": q.get("marketState"),
        }
    except Exception as e:
        return str(e), None


def get_ai_response(question: str) -> str:
    """HyperCLOVA X API가 우선, 없으면 ChatGPT 예시 답변을 반환."""
    if HYPERCLOVA_API_KEY and HYPERCLOVA_ENDPOINT:
        try:
            headers = {"Authorization": f"Bearer {HYPERCLOVA_API_KEY}"}
            payload = {"prompt": question, "max_tokens": 300}
            # 실제 사용 시 주석을 해제하여 호출합니다.
            # res = requests.post(HYPERCLOVA_ENDPOINT, headers=headers, json=payload, timeout=10)
            # res.raise_for_status()
            # data = res.json().get("text", "").strip()
            # return data if data else "응답이 없습니다."
            return f"[예시] HyperCLOVA X가 '{question}'에 대해 생성한 답변입니다."
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
            # res = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=10)
            # res.raise_for_status()
            # data = res.json()["choices"][0]["message"]["content"].strip()
            # return data
            return f"[예시] ChatGPT가 '{question}'에 대해 제공한 답변입니다."
        except Exception as e:
            return f"AI 응답을 가져올 수 없습니다: {e}"
    return "AI API 설정이 필요합니다."


def analyze_question(question: str) -> str:
    """질문을 분석하여 핵심 키워드를 추출하는 AI 호출 예시."""
    prompt = f"다음 질문에서 핵심 금융 키워드를 추출해 주세요: {question}"
    return get_ai_response(prompt)


def summarize_answer(answer: str) -> str:
    """AI를 사용해 답변을 요약하는 예시."""
    prompt = f"다음 내용을 세 문장 이내로 요약해 주세요:\n{answer}"
    return get_ai_response(prompt)


def sample_esg_info() -> str:
    """삼성전자 ESG 분석 예시."""
    return (
        "삼성전자 ESG 분석 예시:\n"
        "- 환경(E) 점수: 80/100\n"
        "- 사회(S) 점수: 75/100\n"
        "- 지배구조(G) 점수: 78/100"
    )


def sample_news() -> list[str]:
    """샘플 금융 뉴스 데이터."""
    return [
        "삼성전자가 최신 반도체 기술 로드맵을 공개했습니다.",
        "국내 증시가 글로벌 금리 변동에 따라 변동성을 보이고 있습니다.",
        "환경 규제 강화로 친환경 사업 투자 수요가 증가하고 있습니다.",
    ]


def sample_market_analysis() -> str:
    """시장 영향 분석 예시."""
    return (
        "최근 금리 인상 기조와 공급망 이슈로 인해 전반적인 IT 업종의 단기 조정이 예상됩니다. "
        "다만 장기적으로는 반도체 수요 회복과 ESG 투자 확대가 긍정적인 요인으로 작용할 수 있습니다."
    )


tickers = load_tickers()
selected_ticker = st.selectbox("주식 티커를 선택하세요", tickers)
question = st.text_input("금융 관련 질문을 입력하세요")

if st.button("분석 요청"):
    if not question:
        st.warning("질문을 입력해주세요.")
    else:
        q = f"{selected_ticker} 관련 질문: {question}"
        with st.spinner("질문을 분석 중입니다..."):
            analysis = analyze_question(q)
        with st.spinner("AI가 답변을 생성 중입니다..."):
            answer = get_ai_response(q)
        with st.spinner("답변을 요약 중입니다..."):
            summary = summarize_answer(answer)

        st.subheader("질문 분석")
        st.write(analysis)

        st.subheader("AI 답변 요약")
        st.write(summary)

        st.subheader("AI 원문 답변")
        st.write(answer)

        with st.expander("주가 정보"):
            err, info = fetch_stock_quote(selected_ticker)
            if err:
                st.write(f"주가 정보를 가져올 수 없습니다: {err}")
            else:
                for k, v in info.items():
                    st.write(f"{k}: {v}")

        with st.expander("ESG 분석"):
            st.write(sample_esg_info())

        with st.expander("최신 금융 뉴스 요약"):
            for item in sample_news():
                st.write("-", item)

        with st.expander("시장 영향 분석"):
            st.write(sample_market_analysis())
