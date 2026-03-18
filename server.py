import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import google.generativeai as genai
from dotenv import load_dotenv, set_key
import fitz  # PyMuPDF

# .env 파일 로드
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

app = FastAPI(title="EASYSAFE NoteBot API")

# 데이터 및 경로 설정
NOTES_FILE = "notes.json"
NOTES_DIR = Path("./my_notes")
NOTES_DIR.mkdir(exist_ok=True)
STATIC_DIR = Path(__file__).parent / "static"
STATIC_DIR.mkdir(exist_ok=True)

# 시스템 프롬프트
SYSTEM_PROMPT = """당신은 사용자의 개인 지식 베이스를 기반으로 답변하는 전문 조수입니다.
반드시 아래 규칙을 지키세요:
1. 제공된 <Context> 및 '등록된 노트' 내용에만 근거하여 답변하세요.
2. 정보가 충분하지 않거나 내용이 없으면 "노트에서 관련 정보를 찾을 수 없습니다."라고 정직하게 답변하세요.
3. 답변 끝에 반드시 해당 정보의 출처 파일명 또는 노트 제목을 [Source: 파일명] 또는 [노트: 제목] 형태로 명시하세요.
4. 모든 답변은 친절하고 정중한 한국어로 작성하세요.
5. 외부 지식을 섞지 마세요."""

# 모델
class Note(BaseModel):
    id: Optional[str] = None
    title: str
    content: str
    date: Optional[str] = None
    type: Optional[str] = "json"

class ChatRequest(BaseModel):
    message: str
    history: List[dict]

# 헬퍼 함수
def load_notes():
    """notes.json 파일과 ./my_notes/ 폴더의 파일들을 취합하여 반환."""
    all_notes = {}
    
    # 1. JSON 기반 노트 로드
    if os.path.exists(NOTES_FILE):
        try:
            with open(NOTES_FILE, "r", encoding="utf-8") as f:
                json_data = json.load(f)
                for k, v in json_data.items():
                    all_notes[k] = {**v, "type": "json"}
        except:
            pass

    # 2. 폴더 내 파일 로드 (.md, .txt, .pdf)
    if NOTES_DIR.exists():
        for file_path in NOTES_DIR.glob("*"):
            ext = file_path.suffix.lower()
            if ext in [".md", ".txt"]:
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        all_notes[file_path.name] = {
                            "title": file_path.name,
                            "content": f.read(),
                            "date": datetime.fromtimestamp(file_path.stat().st_mtime).strftime("%Y-%m-%d %H:%M"),
                            "type": "file"
                        }
                except:
                    pass
            elif ext == ".pdf":
                try:
                    doc = fitz.open(file_path)
                    content = "".join([page.get_text() for page in doc])
                    doc.close()
                    if content.strip():
                        all_notes[file_path.name] = {
                            "title": file_path.name,
                            "content": content,
                            "date": datetime.fromtimestamp(file_path.stat().st_mtime).strftime("%Y-%m-%d %H:%M"),
                            "type": "file"
                        }
                except:
                    pass
                    
    return all_notes

def build_context(notes):
    parts = []
    for name, note in notes.items():
        source_label = f"Source: {name}" if note.get("type") == "file" else f"노트: {note.get('title')}"
        parts.append(f"[{source_label}]\n{note['content']}\n")
    return "\n\n".join(parts)

# API 엔드포인트
@app.get("/api/notes")
async def get_notes():
    notes = load_notes()
    result = []
    for k, v in notes.items():
        result.append({"id": k, **v})
    return result

@app.post("/api/chat")
async def chat(request: ChatRequest):
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise HTTPException(status_code=400, detail="API Key is not set")
    
    notes = load_notes()
    context = build_context(notes)
    
    history_text = ""
    for msg in request.history[-10:]:
        role = "사용자" if msg["role"] == "user" else "AI"
        history_text += f"{role}: {msg['content']}\n"
    
    full_prompt = f"""<Context>
{context}
</Context>

<History>
{history_text if history_text else "(없음)"}
</History>

질문: {request.message}"""

    try:
        genai.configure(api_key=api_key)
        target_models = ["gemini-flash-latest", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-pro-latest"]
        
        last_error = ""
        for m_name in target_models:
            try:
                model = genai.GenerativeModel(model_name=m_name, system_instruction=SYSTEM_PROMPT)
                response = model.generate_content(full_prompt)
                return {"answer": response.text}
            except Exception as e:
                last_error = str(e)
                continue
        raise Exception(f"사용 가능한 모델을 찾을 수 없습니다: {last_error}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/models")
async def list_available_models():
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return {"models": []}
    try:
        genai.configure(api_key=api_key)
        models = [m.name for m in genai.list_models() if "generateContent" in m.supported_generation_methods]
        return {"models": models}
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/settings/save")
async def save_settings(data: dict):
    api_key = data.get("api_key")
    if api_key:
        api_key = api_key.strip()
        set_key(str(env_path), "GEMINI_API_KEY", api_key)
        os.environ["GEMINI_API_KEY"] = api_key
        return {"status": "success"}
    return {"status": "failed"}

@app.get("/api/settings")
async def get_settings():
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY", "")
    return {"api_key": api_key}

# 정적 파일 서빙
app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
