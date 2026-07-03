import os
import streamlit as st
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq

# .env 파일에서 환경 변수 로드 (GROQ_API_KEY 등)
load_dotenv()

# 세션 상태 초기화 — 앱이 새로고침돼도 생성 기록 유지
if "history" not in st.session_state:
    st.session_state.history = []


def getLLMResponse(form_input, email_sender, email_recipient, language, tone):
    # Groq 클라우드 LLM 초기화 (.env의 GROQ_API_KEY 자동 참조)
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.7,
        api_key=os.getenv("GROQ_API_KEY"),
    )

    # 언어·말투에 따라 AI에게 보낼 질문 틀 선택
    if language == "한국어":
        tone_text = "격식체(존댓말)" if tone == "격식체" else "비격식체(친근한 말투)"
        template = """
        {email_topic} 주제를 포함한 이메일을 {tone}로 작성해 주세요.
        보낸 사람: {sender}
        받는 사람: {recipient}
        전부 {language}로 작성해주세요. 한문은 내용에서 제외해주세요.

        이메일 내용:
        """
    else:
        tone_text = "formal" if tone == "격식체" else "informal and friendly"
        template = """
        Write an email including the topic {email_topic} in a {tone} tone.
        Sender: {sender}
        Recipient: {recipient}
        Please write the entire email in {language}.

        Email content:
        """

    prompt = PromptTemplate(
        input_variables=["email_topic", "sender", "recipient", "language", "tone"],
        template=template,
    )

    # 프롬프트 → LLM → 문자열 파싱 체인 구성
    chain = prompt | llm | StrOutputParser()

    response = chain.invoke({
        "email_topic": form_input,
        "sender": email_sender,
        "recipient": email_recipient,
        "language": language,
        "tone": tone_text,
    })

    return response


# ── 페이지 설정 ──────────────────────────────────────
st.set_page_config(
    page_title="이메일 생성기 📮",
    page_icon="📮",
    layout="centered",
    initial_sidebar_state="collapsed",
)
st.header("이메일 생성기 📮")

# API 키 미설정 시 경고 표시
if not os.getenv("GROQ_API_KEY"):
    st.error("⚠️ GROQ_API_KEY가 설정되지 않았습니다. .env 파일에 키를 입력하세요.")
    st.stop()

# ── 입력 UI ──────────────────────────────────────────
language_choice = st.selectbox("이메일을 작성할 언어를 선택하세요:", ["한국어", "English"])
tone_choice = st.selectbox("말투를 선택하세요:", ["격식체", "비격식체"])
form_input = st.text_area("이메일 주제를 입력하세요", height=100)

col1, col2 = st.columns(2)
with col1:
    email_sender = st.text_input("보낸 사람 이름")
with col2:
    email_recipient = st.text_input("받는 사람 이름")

submit = st.button("생성하기", type="primary")

# ── 생성 및 기록 저장 ─────────────────────────────────
if submit:
    if not form_input or not email_sender or not email_recipient:
        st.warning("주제, 보낸 사람, 받는 사람을 모두 입력해주세요.")
    else:
        with st.spinner("생성 중입니다..."):
            response = getLLMResponse(
                form_input, email_sender, email_recipient, language_choice, tone_choice
            )
            # 생성 기록을 세션에 누적 저장
            st.session_state.history.append({
                "주제": form_input,
                "보낸 사람": email_sender,
                "받는 사람": email_recipient,
                "언어": language_choice,
                "말투": tone_choice,
                "이메일": response,
            })

# ── 최신 결과 표시 ────────────────────────────────────
if st.session_state.history:
    latest = st.session_state.history[-1]

    st.divider()
    st.subheader("✉️ 생성된 이메일")
    st.markdown(latest["이메일"])

    # 복사 버튼 — st.code()의 우상단 복사 아이콘 활용
    st.caption("아래에서 전체 복사 가능합니다:")
    st.code(latest["이메일"], language=None)

# ── 이전 생성 기록 ────────────────────────────────────
if len(st.session_state.history) > 1:
    st.divider()
    st.subheader("📋 이전 생성 기록")

    # 최신순으로 나열
    for i, item in enumerate(reversed(st.session_state.history[:-1])):
        label = f"#{len(st.session_state.history) - 1 - i}  {item['주제']} ({item['말투']} / {item['언어']})"
        with st.expander(label):
            st.markdown(item["이메일"])
            st.code(item["이메일"], language=None)
