# Act Operator 2주차: 핵심 로직 구현과 v1 패턴 적용

## 📊 소스 분석 요약

- **핵심 주제**: developing-cast 스킬, 모듈별 구현 워크플로우, LangChain v1 `create_agent` 패턴
- **핵심 메시지**: "state → 의존성 모듈 → nodes → graph" 순서를 지키면 체계적 구현 가능
- **대상 청중**: Act Operator 구조를 이해한 개발자 (1주차 수료자)
- **포맷**: Presenter Slides
- **총 슬라이드 수**: 10장
- **예상 발표 시간**: 약 10분

---

## 🎨 디자인 컨셉: Friendly Learning

**컨셉 요약**: 코드 중심 교육 콘텐츠를 직관적 시각 요소와 밝은 색감으로 전달하는 학습 스타일

### 색상 팔레트

| 용도 | 색상 | HEX |
|:---:|---|---|
| 배경 | ██ 화이트 | `#FFFFFF` |
| 텍스트 | ██ 차콜 | `#2D3436` |
| 강조 | ██ 소프트 블루 | `#0984E3` |
| 서브 강조 | ██ 코랄 | `#FF7043` |
| 배경 (Sub) | ██ 연한 블루 | `#E3F2FD` |

### 타이포그래피

| 용도 | 폰트 | 크기 |
|:---:|---|---|
| 제목 | Nunito Bold | 44pt |
| 부제 | Nunito SemiBold | 28pt |
| 본문 | Pretendard | 18pt |
| 코드 | Fira Code | 16pt |

### 레이아웃

- 여백 60px, 좌측 정렬, 둥근 모서리 12px, 듀오톤 아이콘

---

## 📝 슬라이드 스크립트

---

### 슬라이드 1: 타이틀

**슬라이드 내용**
- **2주차: 핵심 로직 구현과 v1 패턴 적용**
- Implementation & LangChain v1
- CLAUDE.md의 설계를 실제 코드로 구현합니다

**시각적 제안**
- 중앙 정렬 타이틀, 연한 블루 그라디언트 배경, ⚙️ 기어 아이콘

---

### 슬라이드 2: 어젠다

**슬라이드 내용**
- ① developing-cast 스킬
- ② 구현 순서 (매우 중요!)
- ③ State 정의 — 데이터의 모양
- ④ 도구 · 모델 · 프롬프트
- ⑤ create_agent — v1 패턴
- ⑥ 노드 구현 — 비즈니스 로직
- ⑦ 그래프 조립

**시각적 제안**
- 번호 리스트 + 파일 아이콘(`.py`), ② "구현 순서"에 코랄 하이라이트

---

### 슬라이드 3: 정해진 구현 순서

**슬라이드 내용**

```
1. state.py       ← 🏗️ 기초 (데이터 스키마)
   ↓
2. 의존성 모듈     ← 🔧 부품 (tools, models, prompts, agents)
   ↓
3. nodes.py       ← ⚙️ 핵심 로직
   ↓
4. graph.py       ← 🏭 조립
```

> 각 모듈이 이전 모듈에 **의존**하므로 순서 필수

**시각적 제안**
- 수직 플로우차트 중앙, 단계별 이모지+화살표, 하단 코랄 강조 문구

---

### 슬라이드 4: State — 세 가지 클래스

**슬라이드 내용**

```
외부 ──InputState──▶ [내부: State] ──OutputState──▶ 외부
(query만)            (전체 상태)       (result만)
```

| 클래스 | 역할 |
|:---:|---|
| `InputState` | 외부 → 그래프 (최소 입력) |
| `OutputState` | 그래프 → 외부 (최소 출력) |
| `State` | 그래프 내부 (모든 필드) |

**시각적 제안**
- 수평 파이프라인 다이어그램, 3개 박스 블루 톤 구분

---

### 슬라이드 5: 도구 · 모델 · 프롬프트

**슬라이드 내용**

| 파일 | 역할 | 핵심 |
|:---:|---|---|
| `tools.py` | 외부 상호작용 | `@tool` + 타입힌트 + Docstring |
| `models.py` | LLM 설정 | `ChatOpenAI(model="gpt-4o")` |
| `prompts.py` | 시스템 메시지 | 딕셔너리 또는 Message 객체 |

> 세 모듈이 합쳐져 → `agents.py`의 재료

**시각적 제안**
- 3열 카드(🔧🤖💬) + agents.py로 화살표가 모이는 다이어그램

---

### 슬라이드 6: create_agent — v1 패턴

**슬라이드 내용**

```diff
- from langchain.agents import create_react_agent  # ❌ 기존
+ from langchain.agents import create_agent         # ✅ v1
```

```python
agent = create_agent(
    model=get_chat_model(),
    tools=[web_search],
    system_prompt="...",
)
```

> 내부적으로 **ReAct 루프** 실행: 분석 → 도구 호출 → 관찰 → 반복/종료

**시각적 제안**
- 상단 diff 블록 + 하단 ReAct 순환 다이어그램

---

### 슬라이드 7: 노드 구현 — BaseNode

**슬라이드 내용**

```python
class SearchNode(BaseNode):
    def __init__(self):
        super().__init__()
        self.agent = set_search_agent()

    def execute(self, state):
        result = self.agent.invoke(...)
        return {"messages": ..., "result": ...}
```

**3가지 핵심 규칙:**
1. `execute()` → 반드시 **dict 반환**
2. 반환 키 = **State 필드와 일치**
3. 등록 시 **인스턴스** 전달 (`MyNode()`)

**시각적 제안**
- 좌측 코드 + 우측 규칙 카드, 코랄 번호 서클

---

### 슬라이드 8: 그래프 조립 — 4단계

**슬라이드 내용**

| 단계 | 코드 | 설명 |
|:---:|---|---|
| ① | `StateGraph(State, input=..., output=...)` | 그래프 생성 |
| ② | `builder.add_node("name", Node())` | 인스턴스 등록 |
| ③ | `builder.add_edge(START, "first")` | 엣지 연결 |
| ④ | `builder.compile()` | 컴파일 |

**시각적 제안**
- 테이블 + 하단 `START → input → search → END` 플로우

---

### 슬라이드 9: 흔한 실수 모음

**슬라이드 내용**

| ❌ 실수 | ✅ 올바른 방법 |
|---|---|
| `add_node("n", MyNode)` | `add_node("n", MyNode())` |
| `add_edge("START", "n")` | `add_edge(START, "n")` |
| `class MyGraph:` | `class MyGraph(BaseGraph):` |
| Reducer 없이 리스트 상태 | `Annotated[list, add]` |

> 클래스 vs 인스턴스, 문자열 vs 상수!

**시각적 제안**
- 2열 비교(빨간 배경|초록 배경), 인스턴스 행 하이라이트

---

### 슬라이드 10: Key Takeaways

**슬라이드 내용**
1. **구현 순서**: `state` → 의존성 → `nodes` → `graph`
2. **State 3분류**: InputState / State / OutputState
3. **create_agent**: v1 새 패턴 (ReAct 루프 내장)
4. **노드 규칙**: `execute()` → dict 반환 → 인스턴스 등록
5. **그래프 4단계**: 생성 → 등록 → 연결 → 컴파일

**시각적 제안**
- 번호 리스트, 블루 서클 번호, 키워드 볼드, 연한 블루 배경
