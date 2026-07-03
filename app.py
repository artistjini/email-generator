# ─────────────────────────────────────────────
# 1. 필요한 도구(라이브러리) 불러오기
# ─────────────────────────────────────────────

# streamlit: 웹 화면(버튼, 입력창 등)을 만들어주는 도구. 'st'라는 별명으로 사용
import streamlit as st

# PromptTemplate: AI에게 보낼 질문 양식(템플릿)을 만드는 도구
from langchain_core.prompts import PromptTemplate

# OllamaLLM: 내 컴퓨터에 설치된 Ollama AI 모델과 대화하는 도구
from langchain_ollama.llms import OllamaLLM


# ─────────────────────────────────────────────
# 2. 이메일 생성 함수 정의
#    - form_input     : 이메일 주제 (예: "회의 일정 안내")
#    - email_sender   : 보낸 사람 이름
#    - email_recipient: 받는 사람 이름
#    - language       : 작성 언어 (한국어 / English)
# ─────────────────────────────────────────────
def getLLMResponse(form_input, email_sender, email_recipient, language):

    # AI 모델 불러오기
    # model="llama3:latest" → 내 컴퓨터에 설치된 llama3 모델 사용
    # temperature=0.7 → AI 창의성 수치 (0: 딱딱하고 일정 / 1: 자유롭고 창의적). 0.7은 중간보다 약간 자유로운 편
    llm = OllamaLLM(model="llama3.1:8b", temperature=0.7)

    # 선택한 언어에 따라 AI에게 보낼 질문 틀(template)을 다르게 설정
    # {email_topic}, {sender} 등은 나중에 실제 값으로 교체될 빈칸 (편지 양식의 "받는 분: ___" 같은 역할)
    if language == "한국어":
        template = """
        {email_topic} 주제를 포함한 이메일을 작성해 주세요.\n\n보낸 사람: {sender}\n받는 사람: {recipient} 전부 {language}로 번역해서 작성해주세요. 한문은 내용에서 제외해주세요.
        \n\n이메일 내용:
        """
    else:
        # 한국어가 아닌 경우(English) 영어 템플릿 사용
        template = """
        Write an email including the topic {email_topic}.\n\nSender: {sender}\nRecipient: {recipient} Please write the entire email in {language}.\n\nEmail content:
        """

    # 템플릿을 공식 질문 양식(PromptTemplate)으로 만들기
    # input_variables: 템플릿 안에 들어갈 빈칸들의 이름 목록
    # template: 위에서 만든 질문 틀
    prompt = PromptTemplate(
        input_variables=["email_topic", "sender", "recipient", "language"],
        template=template,
    )

    # AI에게 질문을 보내고 답변 받기
    # prompt.format(...): 빈칸에 실제 값을 채워 완성된 질문 문장 만들기
    # llm.invoke(...): 완성된 질문을 AI에게 보내고 답변을 response에 저장
    response = llm.invoke(prompt.format(email_topic=form_input, sender=email_sender, recipient=email_recipient, language=language))

    # 터미널(검은 콘솔 창)에도 답변 출력 (개발자 확인용)
    print(response)

    # 함수를 호출한 곳에 AI 답변을 돌려줌
    return response


# ─────────────────────────────────────────────
# 3. 웹 페이지 기본 설정
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="이메일 생성기 📮",   # 브라우저 탭에 표시되는 제목
    page_icon='📮',                   # 탭에 표시되는 아이콘 (파비콘)
    layout='centered',                # 내용을 화면 가운데에 배치
    initial_sidebar_state='collapsed' # 왼쪽 사이드바를 처음엔 접어서 숨김
)

# 페이지 상단에 큰 제목 표시
st.header("이메일 생성기 📮 ")


# ─────────────────────────────────────────────
# 4. 사용자 입력 받기
# ─────────────────────────────────────────────

# 드롭다운 선택 메뉴: 이메일 작성 언어 선택 (한국어 / English)
language_choice = st.selectbox('이메일을 작성할 언어를 선택하세요:', ['한국어', 'English'])

# 여러 줄 입력 가능한 텍스트 박스: 이메일 주제 입력
form_input = st.text_area('이메일 주제를 입력하세요', height=100)

# 화면을 같은 비율의 2열로 나눔 → 보낸 사람과 받는 사람을 나란히 배치
col1, col2 = st.columns([10, 10])
with col1:
    # 왼쪽 열: 보낸 사람 이름 입력창
    email_sender = st.text_input('보낸 사람 이름')
with col2:
    # 오른쪽 열: 받는 사람 이름 입력창
    email_recipient = st.text_input('받는 사람 이름')


# ─────────────────────────────────────────────
# 5. 버튼 클릭 시 이메일 생성 실행
# ─────────────────────────────────────────────

# "생성하기" 버튼 생성. 클릭되면 submit이 True가 됨
submit = st.button("생성하기")

# 버튼이 클릭됐을 때만 아래 코드 실행
if submit:
    # AI가 답변 생성하는 동안 로딩 애니메이션 표시
    with st.spinner('생성 중입니다...'):
        # 위에서 정의한 함수를 호출해서 이메일 생성
        response = getLLMResponse(form_input, email_sender, email_recipient, language_choice)
        # 생성된 이메일을 화면에 출력
        st.write(response)
