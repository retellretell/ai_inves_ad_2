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


question = st.text_input("금융 관련 질문을 입력하세요")

if st.button("분석 요청"):
    if not question:
        st.warning("질문을 입력해주세요.")
    else:
        with st.spinner("AI가 답변을 생성 중입니다..."):
            answer = get_ai_response(question)
        st.write(answer)

        with st.expander("ESG 분석"):
            st.write(sample_esg_info())

        with st.expander("최신 금융 뉴스 요약"):
            for item in sample_news():
                st.write("-", item)

        with st.expander("시장 영향 분석"):
            st.write(sample_market_analysis())
