import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
from pathlib import Path
import fitz  # PyMuPDF

# ──────────────────────────────────────────────
# 1. Environment Setup
# ──────────────────────────────────────────────
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# ──────────────────────────────────────────────
# 2. Note Loader Logic
# ──────────────────────────────────────────────
NOTES_DIR = Path("./my_notes")
NOTES_DIR.mkdir(exist_ok=True)

def load_notes_from_folder(directory: Path):
    """지정된 폴더에서 .md, .txt, .pdf 파일을 읽어 컨텍스트 문자열 생성."""
    all_content = ""
    file_list = []
    if directory.exists():
        for file_path in directory.glob("*"):
            ext = file_path.suffix.lower()
            if ext in [".md", ".txt"]:
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        # 출처 인식을 위한 구조화
                        all_content = all_content + f"[Source: {file_path.name}]\n{content}\n\n"
                        file_list.append(file_path.name)
                except Exception as e:
                    st.error(f"파일 읽기 오류 ({file_path.name}): {e}")
            elif ext == ".pdf":
                try:
                    doc = fitz.open(file_path)
                    content = ""
                    for page in doc:
                        content += page.get_text()
                    doc.close()
                    
                    if content.strip():
                        all_content = all_content + f"[Source: {file_path.name}]\n{content}\n\n"
                        file_list.append(file_path.name)
                except Exception as e:
                    st.error(f"PDF 읽기 오류 ({file_path.name}): {e}")
    return all_content, file_list

# ──────────────────────────────────────────────
# 3. Streamlit UI Strategy
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="NotebookLM 지식 비서",
    page_icon="📒",
    layout="centered"
)

# 사이드바: 로드된 파일 리스트 표시
with st.sidebar:
    st.title("🗒️ 로드된 노트")
    context_text, loaded_files = load_notes_from_folder(NOTES_DIR)
    
    if loaded_files:
        st.success(f"{len(loaded_files)}개의 파일을 로드했습니다.")
        for f in loaded_files:
            st.caption(f"- {f}")
    else:
        st.warning("`./my_notes/` 폴더에 .md 또는 .txt 파일이 없습니다.")
        st.info("파일을 해당 폴더에 넣고 새로고침 하세요.")

st.title("📒 나만의 지식 베이스 챗봇")
st.caption("Gemini 1.5 Flash 기반의 NotebookLM 스타일 비서")

# ──────────────────────────────────────────────
# 4. LLM & Chat Logic
# ──────────────────────────────────────────────
SYSTEM_INSTRUCTION = (
    "당신은 사용자의 개인 노트를 기반으로 답변하는 지식 비서입니다. "
    "제공된 <Context> 안의 내용에만 근거하여 답변하세요. "
    "노트에 없는 내용은 절대 지어내지 말고 모른다고 답하세요. "
    "답변 끝에는 참조한 파일명을 반드시 명시하세요."
)

# 세션 상태 초기화 (대화 기록 유지)
if "messages" not in st.session_state:
    st.session_state.messages = []

# 대화 기록 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 채팅 입력 및 답변 생성
if prompt := st.chat_input("노트 내용에 대해 궁금한 점을 질문하세요..."):
    # 사용자 메시지 표시 및 저장
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # API 키 확인
    if not GEMINI_API_KEY:
        st.error("API 키를 찾을 수 없습니다. `.env` 파일에 `GEMINI_API_KEY`를 설정해 주세요.")
    elif not context_text:
        st.warning("사용할 수 있는 노트 컨텍스트가 없습니다. 노트를 먼저 추가해 주세요.")
    else:
        # 답변 생성 UI
        with st.chat_message("assistant"):
            with st.spinner("노트를 분석하여 답변을 생성 중입니다..."):
                try:
                    # 사용 가능한 모델 시도 (범용적인 Flash Latest 우선)
                    target_models = ["gemini-flash-latest", "gemini-1.5-flash-latest", "gemini-pro-latest", "gemini-2.0-flash"]
                    
                    model = None
                    last_error = ""
                    
                    for m_name in target_models:
                        try:
                            model = genai.GenerativeModel(
                                model_name=m_name,
                                system_instruction=SYSTEM_INSTRUCTION
                            )
                            # 모델 객체 생성 확인 (실제 호출은 아래에서)
                            break
                        except Exception as e:
                            last_error = str(e)
                            continue
                    
                    if not model:
                        raise Exception(f"사용 가능한 모델을 찾을 수 없습니다. ({last_error})")
                    
                    # 컨텍스트와 질문 결합
                    full_prompt = f"<Context>\n{context_text}\n</Context>\n\n질문: {prompt}"
                    response = model.generate_content(full_prompt)
                    
                    answer = response.text
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                except Exception as e:
                    st.error(f"Gemini API 호출 중 오류가 발생했습니다: {e}")
