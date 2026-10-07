# 4주차: 엔지니어링 및 운영 최적화 (Engineering & Operations)

## 📊 소스 분석 요약

- **핵심 주제**: Act 모노레포(uv workspace), 다중 Cast 관리, 서브그래프(Subgraph), 테스트 자동화(pytest/Mocking), LangSmith 관측성
- **핵심 메시지**: "다중 Cast 모노레포 구조와 체계적인 테스트·관측성(Tracing)으로 견고한 엔터프라이즈 운영 환경을 완성한다"
- **대상 청중**: 중급 개발자 (Act Operator 심화 학습자)
- **포맷**: Presenter Slides
- **총 슬라이드 수**: 10장
- **예상 발표 시간**: 약 15분

---

## 🎨 디자인 컨셉: Tech Minimal

**컨셉 요약**: 다크 모드 기반의 네온 액센트를 활용한 세련되고 간결한 엔지니어링 프리젠테이션 스타일

### 색상 팔레트

| 용도 | 색상 | HEX |
|:---:|---|---|
| 배경 (Primary) | ██ | `#0A0A0A` |
| 텍스트 (Primary) | ██ | `#FFFFFF` |
| 강조 (Accent) | ██ | `#00D4FF` |
| 서브 강조 | ██ | `#7000FF` |
| 배경 (Secondary) | ██ | `#1A1A1A` |

### 타이포그래피

| 용도 | 폰트 | 크기 | 두께 |
|:---:|---|---|---|
| 제목 (H1) | Inter | 44pt | Bold |
| 부제 (H2) | Inter | 28pt | SemiBold |
| 본문 | Roboto | 18pt | Regular |
| 캡션/라벨 | Fira Code | 14pt | Medium |

### 레이아웃 가이드

- **여백**: 상하좌우 최소 48px
- **정렬**: 좌측 정렬 (안정감 강조)
- **이미지/박스 스타일**: 둥근 모서리 8px + 코드 블록 다크 카드
- **아이콘**: 선형(Line) 스타일 (시안/퍼플 액센트)

---

## 📝 슬라이드 스크립트

---

### 슬라이드 1: 타이틀

**슬라이드 내용**
- **4주차: 엔지니어링 및 운영 최적화**
- Engineering & Operations
- 다중 Cast 모노레포, 서브그래프, 테스트 및 LangSmith 관측성

**시각적 제안**
- 중앙 정렬 타이틀, 네온 시안/퍼플 그라디언트 텍스트, 🛠️ 모노레포 아키텍처 다이어그램 카드

**발표자 노트 (스크립트)**
> "안녕하세요! Act Operator 4주차 과정에 오신 것을 환영합니다.
> 지난 1~3주차에서 우리는 단일 Cast의 구조, 로직 구현, 미들웨어 제어를 배웠습니다.
> 이번 4주차는 엔터프라이즈 운영의 핵심인 '다중 Cast 모노레포 관리', '서브그래프 연동', 'pytest 자동화', 그리고 'LangSmith 관측성'을 완성하는 단계입니다."

---

### 슬라이드 2: 어젠다

**슬라이드 내용**
- **오늘 다룰 내용**
  1. Act 모노레포와 uv workspace 구조
  2. `act cast`를 통한 신규 Cast 추가 및 `langgraph.json` 등록
  3. 서브그래프(Subgraph) 연결과 Persistence 모드
  4. `testing-cast` 스킬과 단위/통합 테스트 자동화
  5. 외부 의존성 Mocking 및 테스트 커버리지
  6. LangSmith Tracing과 운영 모니터링

**시각적 제안**
- 2열 그리드 레이아웃, 6개 핵심 카드와 번호 태그

**발표자 노트 (스크립트)**
> "오늘의 핵심 목표는 단일 그래프를 넘어 여러 개의 독립된 Cast를 하나의 Act 프로젝트에서 조화롭게 운영하고,
> 배포 전 자동화된 테스트와 배포 후 실시간 모니터링 체계를 구축하는 것입니다."

---

### 슬라이드 3: Act 모노레포와 uv Workspace

**슬라이드 내용**
- **단일 lockfile로 관리하는 다중 Cast 모노레포**
- 루트 `pyproject.toml`: `[tool.uv.workspace]`로 하위 Cast 선언
- 단일 `uv.lock`으로 전체 워크스페이스 의존성 일관성 보장
- 각 Cast는 독립된 디렉터리와 자체 `pyproject.toml`을 가짐

**시각적 제안**
- 모노레포 폴더 트리 다이어그램 (`my-act/` → `casts/chatbot`, `casts/data_preprocessor`)

**발표자 노트 (스크립트)**
> "Act는 uv workspace를 기반으로 설계되었습니다.
> 루트 저장소의 단일 uv.lock 파일을 통해 수십 개의 Cast가 서로 다른 패키지를 참조하더라도 충돌 없이 빠르고 결정론적인 빌드를 보장합니다."

---

### 슬라이드 4: `act cast`와 `langgraph.json`

**슬라이드 내용**
- **신규 Cast 스캐폴딩과 그래프 등록**
- CLI 명령어: `uv run act cast --act-path . --cast-name "Data Preprocessor" --lang kr`
- `langgraph.json`에 진입점 그래프 자동/수동 등록:
  ```json
  {
    "graphs": {
      "chatbot": "./casts/chatbot/graph.py:graph",
      "data_preprocessor": "./casts/data_preprocessor/graph.py:graph"
    }
  }
  ```

**시각적 제안**
- CLI 실행 흐름과 `langgraph.json` 매핑 다이어그램

**발표자 노트 (스크립트)**
> "`act cast` 명령어를 실행하면 표준 모듈 템플릿을 갖춘 신규 Cast가 생성됩니다.
> 생성 후 `langgraph.json`에 그래프 경로를 등록하면 LangGraph Studio 및 배포 서버에서 각각의 독립된 엔드포인트로 인식합니다."

---

### 슬라이드 5: 서브그래프 연결과 Persistence 모드

**슬라이드 내용**
- **서브그래프(Subgraph) 패턴 선택 기준**
  - **Shared Memory**: 부모와 동일한 `thread_id` 및 checkpointer 공유 (하나의 트랜잭션 흐름)
  - **Isolated Memory**: 독립된 스레드로 실행하여 서브태스크 상태 격리
- **통합 방법**:
  ```python
  builder.add_node("preprocess", preprocessor_graph)
  ```

**시각적 제안**
- 부모 그래프 노드 안에 중첩된 서브그래프 캡슐화 다이어그램

**발표자 노트 (스크립트)**
> "복잡한 비즈니스 로직은 단일 거대 그래프로 만들지 않고 서브그래프로 분리합니다.
> 상태 공유가 필요한 작업은 Shared Memory 모드를, 독립적인 서브 태스크는 Isolated Memory 모드를 선택하여 부모 그래프에 노드로 연결합니다."

---

### 슬라이드 6: `testing-cast` 스킬과 테스트 아키텍처

**슬라이드 내용**
- **AI 기반 테스트 생성 스킬**
- 노드 단위 테스트 (`test_nodes.py`)
- 그래프 통합 및 라우팅 테스트 (`test_graph.py`)
- 체크포인터 및 HITL 인터럽트 검증 (`test_interrupts.py`)

**시각적 제안**
- 테스트 피라미드 다이어그램 (Node Unit → Graph Routing → Subgraph Integration)

**발표자 노트 (스크립트)**
> "`@testing-cast` 스킬을 활용하면 상태 스키마와 노드 로직을 분석하여 pytest 기반의 테스트 코드를 자동으로 생성합니다.
> 노드 단위의 순수 함수 검증부터 그래프 조건부 라우팅 검증까지 체계적인 테스트 슈트를 구축할 수 있습니다."

---

### 슬라이드 7: Mocking과 테스트 커버리지

**슬라이드 내용**
- **비용 없는 결정론적 테스트 작성**
- `unittest.mock` 및 `pytest-mock`을 활용한 LLM & 외부 API 모킹
- 실행 명령어:
  ```bash
  uv run pytest --cov=casts --cov-report=term-missing
  ```
- 핵심 비즈니스 로직 커버리지 80% 이상 유지

**시각적 제안**
- Mocking 계층 구조 및 커버리지 리포트 터미널 스니펫

**발표자 노트 (스크립트)**
> "테스트 실행 시 매번 유료 LLM API나 외부 서비스를 호출할 수는 없습니다.
> Mock 객체를 통해 예상 응답을 반환하도록 설정하고, pytest-cov로 누락된 분기 경로를 지속적으로 점검합니다."

---

### 슬라이드 8: LangSmith Tracing과 운영 모니터링

**슬라이드 내용**
- **프로덕션 관측성(Observability) 확보**
- 환경 변수 설정만으로 전체 트레이싱 활성화:
  ```bash
  LANGSMITH_TRACING=true
  LANGSMITH_API_KEY=lsv2_pt_...
  LANGSMITH_PROJECT=my-act-prod
  ```
- 노드별 입출력, 레이턴시, 토큰 소모량 실시간 시각화 및 디버깅

**시각적 제안**
- LangSmith UI 트레이스 타임라인 목업 카드

**발표자 노트 (스크립트)**
> "LangSmith Tracing을 활성화하면 그래프의 각 노드 실행 시간, 토큰 소모량, 실패한 에러 스택을 실시간으로 추적할 수 있습니다.
> 복잡한 멀티 에이전트 시스템의 병목을 진단하는 필수 도구입니다."

---

### 슬라이드 9: 종합 실습 — 데이터 전처리 Cast 서브그래프 통합

**슬라이드 내용**
- **실습 파이프라인 완성**
  1. `act cast`로 `data_preprocessor` Cast 생성
  2. `clean_text` 및 `validate_schema` 노드 구현
  3. 메인 `weekly_reporter` Cast에 서브그래프로 연결
  4. Mock 데이터를 활용한 E2E 통합 테스트 검증

**시각적 제안**
- Raw Data → Data Preprocessor (Subgraph) → Weekly Reporter (Main Graph) → Approved Report 흐름도

**발표자 노트 (스크립트)**
> "오늘의 실습 과제는 데이터 전처리 Cast를 생성하여 주간 보고서 그래프의 선행 노드로 연결하는 것입니다.
> 독립된 패키지로 개발하고, 최종적으로 부모 그래프에서 매끄럽게 통합 테스트를 통과시키는 과정을 실습합니다."

---

### 슬라이드 10: 4주차 정리 및 Part 1 수료

**슬라이드 내용**
- **Part 1 핵심 요약**:
  - 1주차: `Act vs Cast` & `architecting-act`
  - 2주차: `create_agent` & 3-State 분리
  - 3주차: 미들웨어(HITL, PII, Summarize) & 제어 흐름
  - 4주차: 다중 Cast 모노레포, pytest & LangSmith
- **다음 주 예고 (Part 2)**: 5주차 지능형 웹 리서치 에이전트 구축!

**시각적 제안**
- Part 1 수료 배지 및 5~8주차 Part 2 실전 프로젝트 로드맵 미리보기

**발표자 노트 (스크립트)**
> "이것으로 Act Operator의 핵심 기초를 다루는 Part 1(1~4주차)을 완주하셨습니다!
> 다음 5주차부터는 본격적인 실전 프로젝트로 진입하여 Tavily 검색과 대화 요약을 결합한 '지능형 웹 리서치 에이전트'를 구축해 보겠습니다. 수고하셨습니다!"
