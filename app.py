import streamlit as st
import requests

st.set_page_config(page_title="HyperCLOVA X 기반 AI 투자 어드바이저")

st.title("HyperCLOVA X 기반 AI 투자 어드바이저")

# 간단한 AI 응답 예시 함수
def get_ai_response(question: str) -> str:
    """질문을 받아 HyperCLOVA X 또는 ChatGPT API로부터 답변을 받아오는 예시 함수."""
    # HyperCLOVA X API 호출 예시 (실제 서비스에서는 주석을 수정하여 사용)
    # response = requests.post(
    #     "https://clova-x-api.example.com/v1/generate",
    #     json={"prompt": question}
    # )
    # return response.json()["text"]

    # 데모용 임시 응답
    return f"'{question}'에 대한 HyperCLOVA X AI의 예시 답변입니다."

question = st.text_input("금융 관련 질문을 입력해 주세요:")

if st.button("분석 요청"):
    if not question:
        st.warning("질문을 입력해 주세요.")
    else:
        with st.spinner("AI가 분석 중입니다..."):
            answer = get_ai_response(question)

        st.subheader("요약 답변")
        st.write(answer)

        # ESG 분석
        with st.expander("ESG 분석"):
            st.markdown(
                """
                **삼성전자 ESG 분석 예시**
                - **환경(E)**: 탄소 중립 목표 아래 친환경 공정을 확대하고 있습니다.
                - **사회(S)**: 협력사와의 상생 프로그램, 다양한 사회공헌 활동을 진행 중입니다.
                - **지배구조(G)**: 이사회 독립성과 투명 경영 강화를 추구합니다.
                """
            )

        # 최신 뉴스 요약
        with st.expander("최신 금융 뉴스 요약"):
            st.write("- 미 연준의 금리 동결 가능성이 제기되며 주식 시장에 호재 전망")
            st.write("- 글로벌 공급망 불안 지속으로 반도체 업종 변동성 확대")
            st.write("- 원/달러 환율이 당분간 강세를 보일 것이란 예측")

        # 시장 영향 분석
        with st.expander("시장 영향 분석"):
            st.write(
                "전반적인 시장 변동성은 단기적으로 확대될 수 있으나, "
                "장기적으로는 금리 안정화와 기술주의 실적 개선이 긍정적인 영향을 줄 수 있습니다."
            )
