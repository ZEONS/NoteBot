# NoteBot 디자인 시스템 (Design System)

NoteBot의 디자인은 **"지능적이고 전문적인 지식 도구(Intelligent & Professional Knowledge Tool)"**를 지향합니다. 사용자가 방대한 정보 속에서 핵심 맥락을 놓치지 않도록 차분한 다크 테마와 세밀한 타이포그래피 계층을 제공합니다.

---

## 🎨 1. 시각적 테마 (Visual Theme)

NoteBot은 최신 개발 도구 및 생산성 앱(SaaS)의 미학을 따르며, 정보 밀도가 높으면서도 가독성이 뛰어난 인터페이스를 제공하는 것을 목표로 합니다.

- **핵심 감성**: 전문성, 정밀함, 신뢰, 몰입.
- **주요 특징**: 다크 모드(Deep Dark), 부드러운 하이라이트, 블러 백드롭(Blur Backdrop), 세밀한 보더 라인.

---

## 🎨 2. 색상 시스템 (Color Palette)

시각적 일관성을 유지하기 위해 시스템 전반에 걸쳐 CSS 변수 기반의 색상 체계를 사용합니다.

| 분류 | 색상명 | 값 | 용도 |
| :--- | :--- | :--- | :--- |
| **Foundation** | **Background** | `#0F1117` | 전체 앱의 메인 배경색 |
| | **Sidebar BG** | `#13161F` | 좌측 지식 소스 영역 배경 |
| | **Surface** | `#1A1D2E` | 카드, 모달, 입력창 배경 |
| **Action** | **Primary** | `#4D7EFF` | 브랜드 핵심 컬러, 전송 버튼, 활성 상태 |
| | **Primary Dark** | `#1A2D5E` | 아바타 배경, 버튼 호버 시 대조색 |
| **Typography** | **Text Primary** | `#E2E4F0` | 헤드라인, 메인 메시지 본문 |
| | **Text Secondary**| `#8B90AD` | 서브 타이틀, 파일 이름, 힌트 |
| | **Text Muted** | `#5A5F7A` | 타임스탬프, 비활성 텍스트 |
| **Status** | **Success** | `#22C55E` | 온라인/연결됨 상태 표시 |
| | **Danger** | `#EF4444` | 삭제 버튼, 에러 메시지 |

---

## ✍️ 3. 타이포그래피 (Typography)

정보의 위계와 가독성을 최우선으로 고려한 폰트 조합을 사용합니다.

- **기본 폰트**: `Inter`, `Noto Sans KR` (Sans-serif 계열)
- **계층 구조**:
    - **Logo & Title**: `font-weight: 700` (Bold)
    - **Body Text**: `font-weight: 400` (Regular), `line-height: 1.5`
    - **Metatext**: `font-size: 11px`, `color: var(--text-secondary)`

---

## 🧱 4. 컴포넌트 표준 (Component Standards)

### 💬 메시지 버블 (Message Bubbles)
사용자와 AI의 발화를 명확히 구분하기 위해 서로 다른 스타일을 적용합니다.
- **AI(Bot)**: 수평적 배열, 좌측 정렬, `--surface` 배경, 상단 왼쪽 곡률 `4px`.
- **User**: 우측 정렬, `--user-msg` 배경, 상단 오른쪽 곡률 `4px`.
- **Common**: `border-radius: 12px`, `padding: 14px 16px`.

### 📂 내비게이션 및 사이드바 (Navigation & Sidebar)
- **구조**: `270px` 표준 너비를 가지며, 사용자의 필요에 따라 가로 너비 조절(Resize) 및 접기(Collapse)가 가능합니다.
- **지식 소스**: 파일 확장자별 아이콘 색상을 구분하여 시인성을 높입니다. (PDF: Red, MD: Blue, TXT: Green)

### 🧊 모달 및 오버레이 (Modals)
- **백드롭**: `rgba(0, 0, 0, 0.55)` 배경과 `backdrop-filter: blur(6px)`를 사용하여 전면 작업에 몰입하게 합니다.
- **모서리**: `16px` (XL) 곡률을 사용하여 현대적인 느낌을 줍니다.

---

## ✨ 5. 인터랙션 및 UX 원칙

1.  **반응형 피드백**: 모든 버튼 및 입력 필드는 호버(`:hover`) 및 포커스(`:focus`) 시 명확한 색상 변화나 테두리 강조 효과를 제공합니다.
2.  **부드러운 전환**: 사이드바 개폐, 메시지 로딩 시 `0.2s~0.3s`의 짧고 부드러운 애니메이션을 적용하여 사용자 피로도를 낮춥니다.
3.  **데이터 무결성**: 삭제와 같은 파괴적인 액션은 항상 확인 모달(Confirm Modal)을 거치도록 설계되었습니다.

---

&copy; 2026 NoteBot Design Guide.
