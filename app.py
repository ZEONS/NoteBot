"""
EASYSAFE NotebookLM Clone — 노트 기반 Q&A 서비스
Google Gemini 1.5 Flash + Streamlit
"""

import json
import os
import uuid
from datetime import datetime
from pathlib import Path

import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv, set_key

# .env 파일 로드 (override=True로 실시간 반영 보장)
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

# ──────────────────────────────────────────────
# Config
# ──────────────────────────────────────────────
NOTES_FILE = Path(__file__).parent / "notes.json"
NOTEBOOK_URL = "https://notebooklm.google.com/notebook/c30ec7fe-17cd-4cca-a213-59ab35542844"

st.set_page_config(
    page_title="📒 EASYSAFE NoteBot",
    page_icon="📒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────
# Custom CSS
# ──────────────────────────────────────────────
st.markdown("""
<style>
    /* 전체 테마 */
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #1a1a2e 50%, #16213e 100%);
        color: #ffffff;
    }

    /* 사이드바 */
    section[data-testid="stSidebar"] {
        background: rgba(22, 33, 62, 0.95);
        border-right: 1px solid rgba(100, 200, 255, 0.1);
    }

    /* 헤더 */
    .main-header {
        text-align: center;
        padding: 1.5rem 0 1rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -0.5px;
    }

    .sub-header {
        text-align: center;
        color: #ccd6f6;
        font-size: 0.95rem;
        margin-top: -0.5rem;
        margin-bottom: 1.5rem;
    }

    /* 노트 카드 */
    .note-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(100, 200, 255, 0.08);
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.75rem;
        transition: all 0.2s ease;
    }

    .note-card:hover {
        background: rgba(255, 255, 255, 0.06);
        border-color: rgba(100, 200, 255, 0.2);
        transform: translateY(-1px);
    }

    .note-title {
        color: #ccd6f6;
        font-weight: 600;
        font-size: 0.95rem;
        margin-bottom: 0.25rem;
    }

    .note-date {
        color: #8892b0;
        font-size: 0.75rem;
    }

    .note-preview {
        color: #a8b2d1;
        font-size: 0.82rem;
        margin-top: 0.35rem;
        line-height: 1.4;
    }

    /* 채팅 메시지 */
    .stChatMessage {
        border-radius: 12px !important;
    }

    /* 출처 뱃지 */
    .source-badge {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        margin: 0.15rem;
    }

    /* 노트 카운트 */
    .note-count {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 1rem;
    }

    /* 빈 상태 */
    .empty-state {
        text-align: center;
        padding: 3rem 1rem;
        color: #a8b2d1;
    }

    .empty-state-icon {
        font-size: 3rem;
        margin-bottom: 0.5rem;
    }

    /* 버튼 스타일 */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease;
    }

    /* Streamlit 네이티브 요소 색상 강제 지정 (가독성 개선) */
    .stApp, .stApp [data-testid="stCaptionContainer"], .stApp label, .stApp p {
        color: #ccd6f6 !important;
    }
    
    .stApp h1, .stApp h2, .stApp h3 {
        color: #ffffff !important;
    }

    /* 입력 필드 레이블 강조 */
    .stApp label p {
        color: #ffffff !important;
        font-weight: 600 !important;
    }

    /* 사이드바 텍스트 */
    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
        color: #a8b2d1 !important;
    }
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# Helper: JSON Note Storage
# ──────────────────────────────────────────────
def _load_notes() -> dict:
    """JSON 파일에서 노트 로드."""
    if NOTES_FILE.exists():
        try:
            with open(NOTES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def _save_notes(notes: dict) -> None:
    """노트를 JSON 파일에 저장."""
    with open(NOTES_FILE, "w", encoding="utf-8") as f:
        json.dump(notes, f, ensure_ascii=False, indent=2)


def add_note(title: str, content: str) -> str:
    """새 노트 추가. 생성된 노트 ID 반환."""
    notes = _load_notes()
    note_id = str(uuid.uuid4())[:8]
    notes[note_id] = {
        "title": title.strip(),
        "content": content.strip(),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }
    _save_notes(notes)
    return note_id


def update_note(note_id: str, title: str, content: str) -> None:
    """기존 노트 수정."""
    notes = _load_notes()
    if note_id in notes:
        notes[note_id]["title"] = title.strip()
        notes[note_id]["content"] = content.strip()
        notes[note_id]["updated_at"] = datetime.now().isoformat()
        _save_notes(notes)


def delete_note(note_id: str) -> None:
    """노트 삭제."""
    notes = _load_notes()
    notes.pop(note_id, None)
    _save_notes(notes)


def get_all_notes() -> dict:
    """모든 노트 반환."""
    return _load_notes()


# ──────────────────────────────────────────────
# Helper: Gemini API
# ──────────────────────────────────────────────
SYSTEM_PROMPT = """당신은 사용자가 등록한 '노트'의 내용에만 근거하여 답변하는 AI 비서입니다.

## 핵심 규칙
1. **반드시 제공된 노트의 내용에만 근거하여 답변**하세요.
2. 노트에 없는 내용에 대해서는 "해당 내용은 등록된 노트에서 찾을 수 없습니다."라고 답하세요.
3. 답변 시 **반드시 참조한 노트의 제목을 [노트 제목] 형태로 출처를 밝히세요.**
4. 여러 노트에서 정보를 종합한 경우, 각 정보마다 해당 출처를 표기하세요.
5. 답변의 마지막에 "📎 참조 노트: [노트1], [노트2]" 형태로 사용된 모든 출처를 요약하세요.
6. 한국어로 답변하세요.

## 답변 형식 예시
질문에 대한 답변 내용... [해당 노트 제목]

추가 설명... [다른 노트 제목]

📎 참조 노트: [해당 노트 제목], [다른 노트 제목]
"""


def build_context(notes: dict) -> str:
    """모든 노트를 하나의 컨텍스트 문자열로 결합."""
    if not notes:
        return "(등록된 노트가 없습니다.)"

    parts = []
    for _id, note in notes.items():
        parts.append(
            f"--- 노트: 「{note['title']}」 ---\n{note['content']}\n"
        )
    return "\n".join(parts)


def build_full_prompt(question: str, notes: dict, chat_history: list) -> str:
    """모든 정보를 결합하여 최종 프롬프트 생성."""
    context = build_context(notes)
    history_text = ""
    if chat_history:
        recent = chat_history[-10:]
        for msg in recent:
            role = "사용자" if msg["role"] == "user" else "AI"
            history_text += f"{role}: {msg['content']}\n"

    return f"""## 등록된 노트 목록
{context}

## 이전 대화 기록
{history_text if history_text else "(없음)"}

## 현재 질문
{question}

위 노트의 내용에만 근거하여 답변하고, 반드시 [노트 제목] 형태로 출처를 밝히세요."""


def ask_gemini(question: str, notes: dict, api_key: str, chat_history: list) -> str:
    """Gemini API를 호출하여 노트 기반 답변 생성."""
    try:
        # API 키 공백 제거 (인코딩 오류 예방)
        api_key = api_key.strip()
        genai.configure(api_key=api_key)
        
        # 시도할 모델 목록 (진단 도구 결과를 바탕으로 최신 모델 우선 배치)
        target_models = [
            "gemini-2.0-flash",
            "gemini-2.5-flash",
            "gemini-2.0-flash-lite",
            "gemini-1.5-flash",
            "gemini-1.5-flash-latest",
            "gemini-pro",
        ]
        
        last_error = ""
        for m_name in target_models:
            try:
                model = genai.GenerativeModel(
                    model_name=m_name,
                    system_instruction=SYSTEM_PROMPT,
                )
                full_prompt = build_full_prompt(question, notes, chat_history)
                response = model.generate_content(full_prompt)
                if response:
                    return response.text
            except Exception as e:
                last_error = str(e)
                if "404" not in last_error: # 404 외의 오류(인증 등)는 즉시 중단
                    raise e
                continue
        
        raise Exception(f"모든 시도 모델에서 404 발생. 마지막 오류: {last_error}")

    except Exception as e:
        error_msg = str(e)
        if "404" in error_msg:
            return (
                f"⚠️ **Gemini 모델 검색 실패 (404)**\n\n"
                f"오류 내용: `{error_msg}`\n\n"
                "**해결 방법:**\n"
                "1. API 키가 `gemini-1.5-flash` 모델 권한을 가지고 있는지 확인해 주세요.\n"
                "2. 아래 **'🛠️ API 진단'** 메뉴에서 '모델 목록 확인'을 눌러 실제 사용 가능한 모델을 확인해 보세요."
            )
        return f"⚠️ API 호출 중 오류가 발생했습니다: {error_msg}"


# ──────────────────────────────────────────────
# Session State Initialization
# ──────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "editing_note" not in st.session_state:
    st.session_state.editing_note = None
if "show_add_form" not in st.session_state:
    st.session_state.show_add_form = False


# ──────────────────────────────────────────────
# Sidebar — Note Management
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📒 NoteBot")
    st.markdown(
        f'<a href="{NOTEBOOK_URL}" target="_blank" '
        f'style="color:#667eea;font-size:0.8rem;">🔗 NotebookLM 열기</a>',
        unsafe_allow_html=True,
    )
    st.divider()

    # API Key
    saved_api_key = os.getenv("GOOGLE_API_KEY", "")
    api_key = st.text_input(
        "🔑 Gemini API Key",
        type="password",
        value=saved_api_key,
        placeholder="AIza...",
        help="Google AI Studio에서 발급받은 API 키를 입력하세요.",
    )
    
    col_key1, col_key2 = st.columns([3, 1])
    with col_key1:
        if api_key:
            st.success("API 키가 설정되었습니다.", icon="✅")
    with col_key2:
        if st.button("💾 저장"):
            if api_key:
                set_key(str(env_path), "GOOGLE_API_KEY", api_key)
                os.environ["GOOGLE_API_KEY"] = api_key  # 현재 세션 즉시 반영
                st.success("저장됨!")
                st.rerun()
            else:
                st.warning("키 필요")
    
    # 모델 진단 도구
    with st.expander("🛠️ API 진단 (404 해결용)"):
        if st.button("사용 가능한 모델 목록 확인"):
            if api_key:
                try:
                    genai.configure(api_key=api_key)
                    models = [m.name for m in genai.list_models() if "generateContent" in m.supported_generation_methods]
                    st.write("**사용 가능한 모델:**")
                    for m in models:
                        st.code(m)
                except Exception as e:
                    st.error(f"목록 확인 실패: {e}")
            else:
                st.warning("API 키를 먼저 입력하세요.")
    st.divider()

    # 노트 통계
    notes = get_all_notes()
    st.markdown(
        f'<div class="note-count">📝 노트 {len(notes)}개</div>',
        unsafe_allow_html=True,
    )

    # 새 노트 추가 버튼
    if st.button("➕ 새 노트 추가", use_container_width=True, type="primary"):
        st.session_state.show_add_form = True
        st.session_state.editing_note = None

    # 새 노트 추가 폼
    if st.session_state.show_add_form:
        st.markdown("### ✏️ 새 노트 작성")
        with st.form("add_note_form", clear_on_submit=True):
            new_title = st.text_input("제목", placeholder="노트 제목을 입력하세요")
            new_content = st.text_area(
                "내용",
                placeholder="노트 내용을 입력하세요...",
                height=200,
            )
            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button(
                    "💾 저장", use_container_width=True, type="primary"
                )
            with col2:
                cancelled = st.form_submit_button(
                    "❌ 취소", use_container_width=True
                )

            if submitted and new_title and new_content:
                add_note(new_title, new_content)
                st.session_state.show_add_form = False
                st.success("노트가 추가되었습니다!", icon="✅")
                st.rerun()
            elif submitted:
                st.warning("제목과 내용을 모두 입력해 주세요.")
            if cancelled:
                st.session_state.show_add_form = False
                st.rerun()

    # ── 파일 업로드로 노트 가져오기 ──
    st.markdown("### 📂 파일에서 노트 가져오기")
    st.caption("NotebookLM에서 복사한 내용을 .txt/.md 파일로 저장 후 업로드하세요.")
    uploaded_files = st.file_uploader(
        "파일 선택",
        type=["txt", "md"],
        accept_multiple_files=True,
        label_visibility="collapsed",
        help="여러 파일을 동시에 업로드할 수 있습니다.",
    )

    if uploaded_files:
        if st.button("📥 선택한 파일을 노트로 등록", use_container_width=True, type="primary"):
            imported_count = 0
            for uploaded_file in uploaded_files:
                try:
                    content = uploaded_file.read().decode("utf-8")
                    if content.strip():
                        # 파일명에서 확장자 제거하여 제목으로 사용
                        title = os.path.splitext(uploaded_file.name)[0]
                        add_note(title, content.strip())
                        imported_count += 1
                except Exception as e:
                    st.error(f"❌ `{uploaded_file.name}` 처리 실패: {e}")

            if imported_count > 0:
                st.success(f"✅ {imported_count}개 파일이 노트로 등록되었습니다!", icon="📥")
                st.rerun()

    st.divider()

    # 기존 노트 목록
    if notes:
        st.markdown("### 📋 노트 목록")
        for note_id, note in sorted(
            notes.items(), key=lambda x: x[1]["updated_at"], reverse=True
        ):
            with st.expander(f"📄 {note['title']}", expanded=False):
                # 수정 모드
                if st.session_state.editing_note == note_id:
                    edit_title = st.text_input(
                        "제목",
                        value=note["title"],
                        key=f"edit_title_{note_id}",
                    )
                    edit_content = st.text_area(
                        "내용",
                        value=note["content"],
                        height=200,
                        key=f"edit_content_{note_id}",
                    )
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button(
                            "💾 저장",
                            key=f"save_{note_id}",
                            use_container_width=True,
                            type="primary",
                        ):
                            update_note(note_id, edit_title, edit_content)
                            st.session_state.editing_note = None
                            st.success("수정 완료!", icon="✅")
                            st.rerun()
                    with col_b:
                        if st.button(
                            "❌ 취소",
                            key=f"cancel_{note_id}",
                            use_container_width=True,
                        ):
                            st.session_state.editing_note = None
                            st.rerun()
                else:
                    # 읽기 모드
                    created = note.get("created_at", "")[:10]
                    st.caption(f"📅 {created}")
                    st.markdown(note["content"][:300] + ("..." if len(note["content"]) > 300 else ""))

                    col_x, col_y = st.columns(2)
                    with col_x:
                        if st.button(
                            "✏️ 수정",
                            key=f"edit_{note_id}",
                            use_container_width=True,
                        ):
                            st.session_state.editing_note = note_id
                            st.session_state.show_add_form = False
                            st.rerun()
                    with col_y:
                        if st.button(
                            "🗑️ 삭제",
                            key=f"delete_{note_id}",
                            use_container_width=True,
                        ):
                            delete_note(note_id)
                            st.success("삭제 완료!", icon="🗑️")
                            st.rerun()
    else:
        st.markdown(
            """<div class="empty-state">
                <div class="empty-state-icon">📝</div>
                <p>아직 등록된 노트가 없습니다.<br>
                왼쪽 상단의 <b>'새 노트 추가'</b> 버튼을<br>
                눌러 시작해 보세요!</p>
            </div>""",
            unsafe_allow_html=True,
        )


# ──────────────────────────────────────────────
# Main Area — Chat Interface
# ──────────────────────────────────────────────
st.markdown('<div class="main-header">📒 EASYSAFE NoteBot</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">등록된 노트를 기반으로 질문에 답변하는 AI 비서</div>',
    unsafe_allow_html=True,
)

# 현재 컨텍스트 요약
notes = get_all_notes()
if notes:
    with st.expander("📚 현재 로드된 노트 목록", expanded=False):
        cols = st.columns(min(len(notes), 4))
        for i, (nid, n) in enumerate(notes.items()):
            with cols[i % min(len(notes), 4)]:
                st.markdown(
                    f"""<div class="note-card">
                        <div class="note-title">📄 {n['title']}</div>
                        <div class="note-preview">{n['content'][:80]}...</div>
                        <div class="note-date">{n.get('updated_at','')[:10]}</div>
                    </div>""",
                    unsafe_allow_html=True,
                )

st.divider()

# 채팅 기록 표시
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"], avatar="🧑‍💻" if msg["role"] == "user" else "🤖"):
        st.markdown(msg["content"])

# 채팅 입력
if prompt := st.chat_input("노트에 대해 궁금한 점을 질문해 보세요..."):
    # 사용자 메시지 표시
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)
    st.session_state.chat_history.append({"role": "user", "content": prompt})

    # API 키 확인
    if not api_key:
        with st.chat_message("assistant", avatar="🤖"):
            st.warning(
                "⚠️ Gemini API 키가 설정되지 않았습니다. "
                "왼쪽 사이드바에서 API 키를 입력해 주세요."
            )
        st.session_state.chat_history.append(
            {
                "role": "assistant",
                "content": "⚠️ API 키가 설정되지 않았습니다.",
            }
        )
    elif not notes:
        with st.chat_message("assistant", avatar="🤖"):
            st.info(
                "📝 등록된 노트가 없습니다. "
                "사이드바에서 노트를 추가한 후 질문해 주세요."
            )
        st.session_state.chat_history.append(
            {
                "role": "assistant",
                "content": "📝 등록된 노트가 없습니다. 노트를 먼저 추가해 주세요.",
            }
        )
    else:
        # Gemini 호출
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("🔍 노트에서 관련 정보를 검색하고 있습니다..."):
                response = ask_gemini(
                    prompt, notes, api_key, st.session_state.chat_history
                )
            st.markdown(response)
        st.session_state.chat_history.append(
            {"role": "assistant", "content": response}
        )

# 하단 정보
st.divider()
col_info1, col_info2, col_info3 = st.columns(3)
with col_info1:
    st.caption(f"📝 등록된 노트: {len(notes)}개")
with col_info2:
    st.caption(f"💬 대화 기록: {len(st.session_state.chat_history)}건")
with col_info3:
    if st.button("🗑️ 대화 초기화", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()
