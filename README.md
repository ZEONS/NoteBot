# 🤖 NoteBot

> **지능형 지식 비서 — 사용자의 노트를 기반으로 대답하는 스마트 챗봇**

**NoteBot**은 사용자가 업로드한 문서(PDF, Markdown, Text)를 분석하여 질문에 답변하는 RAG(Retrieval-Augmented Generation) 기반의 AI 지식 비서입니다. Google Gemini API와 로컬 LLM(Ollama)을 결합한 하이브리드 구성을 지원하며, 현대적인 웹 인터페이스를 통해 직관적인 사용자 경험을 제공합니다.

---

## ✨ 핵심 기능 (Key Features)

- **📄 멀티 파싱 RAG**: PDF, MD, TXT 등 다양한 형식의 문서를 실시간으로 분석하여 컨텍스트로 활용합니다.
- **🔍 정확한 출처 표기**: 모든 답변 하단에 참조한 파일명 또는 노트 제목을 명시하여 신뢰도를 높입니다. ([Source: 파일명])
- **🖥️ 하이브리드 UI 지원**: 
    - **Web App**: FastAPI 기반의 고성능 채팅 인터페이스 (Port: 8001).
    - **Streamlit**: 데이터 분석 및 빠른 프로토타이핑을 위한 대안 인터페이스.
- **⚙️ 다이나믹 모델 설정**: 웹 UI 내에서 직접 API 키와 모델을 관리하고 실시간으로 반영할 수 있습니다.
- **🚀 하이브리드 AI 전략**: `antigravity.config.json`을 통해 클라우드(Gemini)와 로컬(Ollama) 모델을 유연하게 전환합니다.

---

## 🛠 기술 스택 (Tech Stack)

- **Backend:** Python, FastAPI, Uvicorn
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla), Streamlit
- **AI Engine:** Google Generative AI (Gemini), Ollama (Gemma 4)
- **Document Processing:** PyMuPDF (fitz)
- **Environment:** python-dotenv, set_key

---

## 📂 프로젝트 구조 (Structure)

```text
NoteBot/
├── my_notes/           # 챗봇이 참조할 지식 소스 (PDF, MD, TXT 저장)
├── static/             # 웹 프론트엔드 자원 (index.html, app.js, style.css)
├── server.py           # FastAPI 메인 백엔드 서버
├── app.py              # Streamlit 기반 대체 인터페이스
├── antigravity.config.json # AI 모델 하이브리드 설정 파일
├── .env                # API 키 및 기본 모델 설정 값
├── requirements.txt    # 설치 필요 라이브러리 목록
└── 지식비서_실행.bat     # 윈도우 환경 원클릭 실행 스크립트
```

---

## 🚀 시작하기 (Getting Started)

### 1. 환경 설정
본 저장소를 클론한 후, 필요한 패키지를 설치합니다.
```bash
pip install -r requirements.txt
```

### 2. API 키 설정
`.env.example` 파일을 복사하여 `.env` 파일을 생성하고, 발급받은 `GEMINI_API_KEY`를 입력합니다.
```text
GEMINI_API_KEY=your_actual_api_key_here
```

### 3. 서버 실행
- **Windows**: `지식비서_실행.bat` 파일을 실행합니다.
- **Manual**: 다음 명령어를 입력합니다.
  ```bash
  python server.py
  ```
- 서버 실행 후 브라우저에서 `http://localhost:8001`에 접속합니다.

---

## ⚙️ AI 컨피규레이션 (Antigravity Config)

`antigravity.config.json` 파일을 통해 다음과 같이 모델을 제어할 수 있습니다:
- **Default**: 클라우드 모델 (`gemini-3-flash`) 우선 사용.
- **Local Fallback**: 네트워크 문제 발생 시 로컬 Ollama 모델(`gemma4:latest`)로 자동 전환 요청 처리 가능.

---

&copy; 2026 NoteBot Project. All rights reserved.
