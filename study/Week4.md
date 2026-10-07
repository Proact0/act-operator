# 4주차: 엔지니어링 및 운영 최적화 (Engineering & Operations)

> **목표**: 여러 Cast를 하나의 uv workspace에서 관리하고, 서브그래프·pytest·LangSmith를 결합해 변경에 강하고 관측 가능한 Act를 만듭니다.
>
> **최종 확인일**: 2026-08-26 · 현재 Act Operator scaffold와 최신 공식 문서 기준

## 📋 학습 체크리스트

- [ ] Step 1: Act 모노레포와 uv workspace 이해
- [ ] Step 2: `act cast`로 Cast 추가
- [ ] Step 3: Cast별 의존성과 workspace 의존성 관리
- [ ] Step 4: `langgraph.json` 그래프 등록 확인
- [ ] Step 5: 서브그래프 연결과 persistence 모드 선택
- [ ] Step 6: `testing-cast`와 테스트 구조 이해
- [ ] Step 7: 노드 단위 테스트 작성
- [ ] Step 8: 그래프·라우팅·체크포인터 테스트 작성
- [ ] Step 9: 외부 의존성 모킹과 커버리지 측정
- [ ] Step 10: LangSmith tracing·모니터링 구성
- [ ] Step 11: 데이터 전처리 Cast 통합 실습
- [ ] 마무리: 운영 점검과 복습 퀴즈

---

## 시작하기 전에

```bash
uv sync
uv run act --help
uv run pytest
```

> [!IMPORTANT]
> 현재 scaffold의 언어 코드는 `en`과 `kr`입니다. 예전 자료의 `--lang ko`는 사용하지 않습니다.

---

## Step 1: Act 모노레포와 uv workspace

Act는 여러 Cast 패키지를 한 저장소에서 관리하는 uv workspace입니다. 각 Cast는 하나의 LangGraph 그래프 단위이며 자체 `pyproject.toml`을 갖습니다.

```text
my-act/
├── pyproject.toml                 # workspace 및 공통 개발 도구 설정
├── uv.lock                        # workspace 전체가 공유하는 단일 lockfile
├── langgraph.json                 # 실행할 그래프 진입점 등록
├── .env                           # 로컬 환경 변수; 커밋 금지
├── casts/
│   ├── base_graph.py
│   ├── base_node.py
│   ├── chatbot/
│   │   ├── pyproject.toml
│   │   ├── graph.py
│   │   └── modules/
│   └── data_preprocessor/
│       ├── pyproject.toml
│       ├── graph.py
│       └── modules/
└── tests/
    ├── conftest.py                # 공유 fixture가 필요할 때 생성
    ├── cast_tests/                # 그래프 단위 테스트
    └── node_tests/                # 노드 단위 테스트
```

```toml
[tool.uv.workspace]
members = ["casts/*"]
exclude = [
    "casts/__pycache__",
    "casts/**/__pycache__",
    "casts/**/.venv",
]
```

| 항목 | 동작 |
|---|---|
| lockfile | 모든 Cast가 루트 `uv.lock` 하나를 공유 |
| `uv lock` | workspace 전체 의존성을 한 번에 해석 |
| `uv sync` | 기본적으로 workspace 루트 환경을 동기화 |
| `uv run --package <name>` | 특정 workspace 멤버 컨텍스트에서 명령 실행 |
| 패키지 격리 | Python 환경은 완전히 격리되지 않으므로 선언 누락을 테스트로 잡아야 함 |

> [!WARNING]
> Cast마다 `pyproject.toml`이 있어도 각각 독립 가상환경을 얻는 것은 아닙니다. 서로 양립할 수 없는 버전을 요구하면 단일 lockfile 해석이 실패합니다.

---

## Step 2: 새로운 Cast 추가

```bash
uv run act cast

uv run act cast \
  --path ./my-act \
  --cast-name "Data Preprocessor" \
  --lang kr
```

CLI는 `casts/data_preprocessor/`, `tests/cast_tests/data_preprocessor_test.py`를 만들고 `langgraph.json`에 그래프 진입점을 등록합니다.

```bash
uv sync
uv run pytest tests/cast_tests/data_preprocessor_test.py -v
```

> [!NOTE]
> `act cast`는 기존 파일을 덮어쓰지 않습니다. 같은 이름의 비어 있지 않은 Cast 디렉터리나 테스트 파일이 있으면 중단됩니다.

---

## Step 3: 의존성 관리

```bash
# 외부 패키지를 특정 Cast에 추가
uv add --package data-preprocessor pandas
uv add --package chatbot langchain-openai

# 테스트 도구는 루트 dependency group에 추가
uv add --group test pytest-cov pytest-mock

```

현재 scaffold의 Cast `pyproject.toml`에는 `[build-system]`이 없습니다. 따라서 Cast 코드는 Act 루트에서 `casts.<cast_name>` namespace로 import되지만, workspace 멤버 자체가 독립 설치 패키지로 빌드되지는 않습니다.

Cast를 독립 배포 가능한 패키지로 전환한 뒤 다른 Cast의 정식 의존성으로 사용할 때만 다음 source 선언을 추가합니다.

```toml
# casts/chatbot/pyproject.toml
[project]
dependencies = ["data-preprocessor"]

[tool.uv.sources]
data-preprocessor = { workspace = true }
```

```bash
uv lock --check
uv sync
uv tree
uv run --package chatbot python -c "import casts.data_preprocessor"
```

이 경우 대상 Cast에 실제 package layout과 `[build-system]`도 먼저 구성해야 합니다. 생성 직후의 기본 scaffold에 `uv add ... --workspace`만 실행하면 uv가 빌드할 패키지가 없어 실패할 수 있습니다.

의존성 충돌이 나면 `uv tree --invert --package <package>`로 요구 주체를 찾고 공통 버전 범위를 정합니다. 진짜 격리가 필요하면 프로세스나 배포 단위를 분리합니다.

---

## Step 4: `langgraph.json` 그래프 등록

`act cast`는 새 그래프를 자동 등록합니다.

```json
{
  "dependencies": ["."],
  "graphs": {
    "chatbot": "./casts/chatbot/graph.py:chatbot_graph",
    "data-preprocessor": "./casts/data_preprocessor/graph.py:data_preprocessor_graph"
  },
  "env": ".env"
}
```

현재 scaffold의 `<cast>_graph`는 `BaseGraph` 인스턴스이며 `__call__()`이 컴파일된 그래프를 반환합니다.

```python
data_preprocessor_graph = DataPreprocessorGraph()
```

```bash
uv run langgraph dev
```

> [!TIP]
> `langgraph.json`의 키는 외부 그래프 ID, 콜론 뒤 이름은 Python 모듈에 실제 존재하는 진입점입니다. 이름 변경 시 둘을 함께 갱신하세요.

---

## Step 5: 서브그래프 연결과 persistence

서브그래프는 컴파일된 그래프를 상위 그래프의 노드처럼 재사용하는 패턴입니다.

```mermaid
flowchart LR
    START --> PREP[입력 준비]
    PREP --> SUB[[data_preprocessor 서브그래프]]
    SUB --> ANSWER[응답 생성]
    ANSWER --> END
```

### 5.1 상태 키를 공유할 때: 그래프를 노드로 등록

```python
from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from casts.data_preprocessor.graph import data_preprocessor_graph


preprocessing_subgraph = data_preprocessor_graph()

builder = StateGraph(State)
builder.add_node("preprocess", preprocessing_subgraph)
builder.add_node("answer", AnswerNode())
builder.add_edge(START, "preprocess")
builder.add_edge("preprocess", "answer")
builder.add_edge("answer", END)
```

부모와 자식이 공유하는 키의 타입과 reducer가 호환되어야 합니다.

### 5.2 상태 스키마가 다를 때: 어댑터 노드에서 호출

```python
from __future__ import annotations

from casts.base_node import BaseNode
from casts.data_preprocessor.graph import data_preprocessor_graph


class PreprocessNode(BaseNode):
    """부모 State와 전처리 Cast State 사이를 변환합니다."""

    def __init__(self) -> None:
        super().__init__()
        self.subgraph = data_preprocessor_graph()

    def execute(self, state: State) -> dict[str, object]:
        result = self.subgraph.invoke({"query": state["query"]})
        return {"processed_query": result["result"]}
```

### 5.3 최신 persistence 모드

서브그래프를 `compile()`할 때 `checkpointer` 값으로 내부 상태 보존 범위를 선택합니다.

| 설정 | 의미 | 권장 상황 |
|---|---|---|
| `None` 또는 생략 | 호출별 격리, 부모 checkpointer 상속 | 대부분의 일회성 서브그래프 |
| `True` | 같은 thread에서 호출 간 내부 상태 유지 | 멀티턴 전문 에이전트 |
| `False` | checkpointing 비활성화 | 중단·복구가 필요 없는 순수 계산 |

```python
subgraph = subgraph_builder.compile()
stateful_subgraph = subgraph_builder.compile(checkpointer=True)
stateless_subgraph = subgraph_builder.compile(checkpointer=False)
```

상위 그래프에 persistence 기능을 사용하려면 부모도 checkpointer와 `thread_id`를 가져야 합니다.

```python
from langgraph.checkpoint.memory import InMemorySaver

graph = builder.compile(checkpointer=InMemorySaver())
config = {"configurable": {"thread_id": "week4-demo"}}
```

> [!WARNING]
> `checkpointer=True`인 동일 서브그래프 인스턴스를 한 노드에서 병렬 또는 반복 호출하면 checkpoint namespace 충돌이 날 수 있습니다. 독립 작업은 기본값인 호출별 persistence를 우선 사용하세요.

---

## Step 6: `testing-cast`와 테스트 구조

현재 scaffold에는 `.claude/skills/testing-cast/`가 포함됩니다.

```text
.claude/skills/testing-cast/
├── SKILL.md
└── resources/
    ├── testing-nodes.md
    ├── testing-graphs.md
    ├── mocking.md
    ├── fixtures.md
    └── coverage.md
```

```text
@testing-cast를 사용해 data_preprocessor Cast의 노드 단위 테스트와
그래프 통합 테스트를 작성하고, 외부 API 호출은 모킹해 줘.
```

| 위치 | 이름 규칙 | 범위 |
|---|---|---|
| `tests/cast_tests/<cast_snake>_test.py` | 접미사 `_test.py` | 전체 그래프 호출 |
| `tests/node_tests/test_<name>.py` | 접두사 `test_` | 개별 노드 동작 |
| `tests/conftest.py` | 고정 | 공유 fixture |

`act cast`가 만드는 Cast 테스트 이름은 `test_<cast>.py`가 아니라 `<cast>_test.py`입니다.

```bash
uv run pytest --collect-only -q
uv run pytest tests/node_tests/ -v
uv run pytest tests/cast_tests/ -v
```

---

## Step 7: 노드 단위 테스트

노드 테스트는 그래프 전체가 아니라 입력 State에 대한 업데이트만 검증합니다.

```python
from __future__ import annotations

import pytest

from casts.data_preprocessor.modules.nodes import CleanTextNode


@pytest.mark.parametrize(
    ("raw_text", "expected"),
    [
        ("  hello    world  ", "hello world"),
        ("", ""),
        ("한글   공백", "한글 공백"),
    ],
)
def test_clean_text_node(raw_text: str, expected: str) -> None:
    node = CleanTextNode()

    result = node({"raw_text": raw_text})

    assert result == {"cleaned_text": expected}
```

`node.execute(...)` 대신 `node(...)`를 호출하면 `BaseNode.__call__()`의 반환 타입 검증까지 함께 확인할 수 있습니다. 순수 비즈니스 로직만 격리하려면 `execute()`를 직접 테스트해도 됩니다.

```python
from __future__ import annotations

import pytest

from casts.data_preprocessor.modules.nodes import FetchMetadataNode


@pytest.mark.asyncio
async def test_fetch_metadata_node() -> None:
    node = FetchMetadataNode()

    result = await node({"document_id": "doc-1"})

    assert result["metadata"]["document_id"] == "doc-1"
```

테스트는 구현 세부사항보다 관찰 가능한 계약을 검증합니다.

- 반환값은 State 전체 복사본이 아니라 변경할 키의 업데이트인가?
- 빈 입력과 잘못된 입력에서 의도한 오류가 발생하는가?
- 같은 입력에 대해 결정적인 결과를 내는가?

---

## Step 8: 그래프·라우팅·체크포인터 테스트

### 8.1 그래프 호출

현재 scaffold가 자동 생성하는 테스트는 그래프 팩터리 역할을 하는 `BaseGraph` 인스턴스를 호출합니다.

```python
from __future__ import annotations

from casts.data_preprocessor.graph import data_preprocessor_graph


def test_graph_normalizes_text() -> None:
    graph = data_preprocessor_graph()

    result = graph.invoke({"query": "  Hello    Act  "})

    assert result["result"] == "Hello Act"
```

### 8.2 각 테스트에서 새 checkpointer 사용

상태 누출을 막기 위해 테스트마다 새 그래프와 새 `InMemorySaver`를 만듭니다.

```python
from __future__ import annotations

import pytest
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.state import CompiledStateGraph

from casts.chatbot.graph import build_chatbot_graph


@pytest.fixture
def graph_with_memory() -> CompiledStateGraph:
    return build_chatbot_graph(checkpointer=InMemorySaver())


def test_threads_are_isolated(graph_with_memory: CompiledStateGraph) -> None:
    first = {"configurable": {"thread_id": "user-1"}}
    second = {"configurable": {"thread_id": "user-2"}}

    graph_with_memory.invoke({"query": "first"}, config=first)
    result = graph_with_memory.invoke({"query": "second"}, config=second)

    assert result["query"] == "second"
```

위 `build_chatbot_graph()`는 테스트 가능한 조립 함수의 예시입니다. 현재 `BaseGraph.build()`가 인자를 받지 않으므로 persistence를 테스트해야 한다면 builder 조립 함수를 분리해 checkpointer를 주입하세요.

### 8.3 라우팅 테스트

라우터 함수는 가능한 한 순수 함수로 두고 직접 테스트합니다.

```python
from __future__ import annotations

import pytest

from casts.chatbot.modules.conditions import route_after_validation


@pytest.mark.parametrize(
    ("state", "expected"),
    [
        ({"is_valid": True}, "process"),
        ({"is_valid": False}, "reject"),
    ],
)
def test_route_after_validation(
    state: dict[str, bool],
    expected: str,
) -> None:
    assert route_after_validation(state) == expected
```

스트리밍은 chunk 개수보다 이벤트 계약을 검증합니다. 하위 그래프 스트림이 필요하면 사용 중인 LangGraph runtime의 stream API와 `streaming-cast` 스킬을 기준으로 테스트하세요.

---

## Step 9: 모킹과 커버리지

LLM, HTTP API, 데이터베이스, Store 같은 외부 경계를 모킹하면 비용·지연·비결정성을 제거할 수 있습니다.

```python
from __future__ import annotations

from unittest.mock import Mock

from langchain_core.messages import AIMessage

from casts.chatbot.modules.nodes import AnswerNode


def test_answer_node_uses_model() -> None:
    model = Mock()
    model.invoke.return_value = AIMessage(content="고정 응답")
    node = AnswerNode(model=model)

    result = node({"query": "질문"})

    assert result["answer"] == "고정 응답"
    model.invoke.assert_called_once()
```

의존성을 생성자나 팩터리 인자로 주입하면 내부 속성을 강제로 바꾸는 테스트보다 계약이 명확해집니다.

```python
from __future__ import annotations

from casts.chatbot.modules.nodes import SearchNode


def test_search_boundary(monkeypatch) -> None:
    def fake_search(query: str) -> list[str]:
        return [f"result:{query}"]

    monkeypatch.setattr(
        "casts.chatbot.modules.nodes.search_documents",
        fake_search,
    )

    result = SearchNode()({"query": "act"})

    assert result == {"documents": ["result:act"]}
```

patch 대상은 함수가 정의된 모듈이 아니라 **테스트 대상이 그 이름을 조회하는 모듈**이어야 합니다.

```bash
uv run pytest --cov=casts --cov-branch --cov-report=term-missing
uv run pytest --cov=casts --cov-report=html
```

커버리지는 목표가 아니라 누락을 찾는 신호입니다. 조건부 edge의 모든 분기, 재시도·타임아웃, 외부 쓰기의 중복 실행 방지, interrupt 재개, 서브그래프 변환 실패를 우선 검증합니다.

---

## Step 10: LangSmith 관측 가능성

LangSmith는 한 요청을 **trace**, trace 안의 모델·도구·노드 실행을 **run**, 여러 대화 턴을 **thread**로 구성합니다. 프로젝트는 관련 trace를 묶는 컨테이너입니다.

### 10.1 tracing 활성화

`.env`에 다음 값을 설정합니다.

```dotenv
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=lsv2_pt_replace_me
LANGSMITH_PROJECT=my-act-dev
```

여러 LangSmith workspace에 연결된 키라면 `LANGSMITH_WORKSPACE_ID`도 지정합니다. 자체 호스팅 또는 다른 endpoint를 쓸 때만 `LANGSMITH_ENDPOINT`를 추가합니다.

> [!CAUTION]
> `.env`와 API 키를 Git에 커밋하지 마세요. trace에는 프롬프트, 사용자 입력, 도구 인자와 결과가 포함될 수 있으므로 PII·비밀정보의 수집, 마스킹, 보존 정책을 먼저 정해야 합니다.

LangChain/LangGraph 연동은 환경 변수가 설정되면 지원되는 실행을 자동 추적합니다.

```bash
uv run langgraph dev
```

### 10.2 trace에 운영 문맥 추가

```python
config = {
    "configurable": {"thread_id": "conversation-42"},
    "tags": ["week4", "staging"],
    "metadata": {
        "thread_id": "conversation-42",
        "app_version": "0.4.0",
        "cast": "chatbot",
    },
}

result = graph.invoke({"query": "Act란 무엇인가요?"}, config=config)
```

`thread_id`, `session_id`, `conversation_id` 같은 공통 식별자를 metadata에 전달하면 멀티턴 trace를 thread로 연결할 수 있습니다.

### 10.3 관측에서 평가로

| 단계 | 확인 항목 |
|---|---|
| 개별 trace | 잘못된 도구 선택, 프롬프트, 인자, 오류 위치 |
| dashboard | trace 수, 오류율, latency, token 사용량, 비용 추세 |
| feedback | 사용자·검토자의 품질 점수 |
| offline evaluation | 배포 전 회귀·버전 비교 |
| online evaluation | 실제 트래픽의 품질·안전성 감시 |

실패한 production trace를 dataset의 회귀 사례로 추가하면 `관측 → 재현 테스트 → 수정 → 재평가` 피드백 루프를 만들 수 있습니다.

---

## Step 11: 실습 — 데이터 전처리 Cast 연결

### 11.1 목표

- `data_preprocessor` Cast 추가
- 입력 공백 정규화와 단어 수 계산
- `chatbot`에서 서브그래프로 호출
- 노드·그래프 테스트 작성
- LangSmith trace에서 상위·하위 실행 확인

### 11.2 Cast 생성

```bash
uv run act cast --cast-name "Data Preprocessor" --lang kr
uv sync
```

### 11.3 전처리 State와 노드

```python
# casts/data_preprocessor/modules/state.py
from __future__ import annotations

from typing_extensions import TypedDict


class InputState(TypedDict):
    query: str


class OutputState(TypedDict):
    result: str
    word_count: int


class State(InputState, OutputState):
    pass
```

```python
# casts/data_preprocessor/modules/nodes.py
from __future__ import annotations

from casts.base_node import BaseNode
from casts.data_preprocessor.modules.state import State


class NormalizeTextNode(BaseNode):
    """입력 문자열의 앞뒤 및 중복 공백을 정리합니다."""

    def execute(self, state: State) -> dict[str, object]:
        normalized = " ".join(state["query"].split())
        return {
            "result": normalized,
            "word_count": len(normalized.split()),
        }
```

생성된 `graph.py`의 `SampleNode`를 `NormalizeTextNode`로 교체한 뒤 테스트합니다.

```python
# tests/cast_tests/data_preprocessor_test.py
from __future__ import annotations

import pytest

from casts.data_preprocessor.graph import data_preprocessor_graph


@pytest.mark.parametrize(
    ("query", "result", "word_count"),
    [
        ("  Hello    Act  ", "Hello Act", 2),
        ("", "", 0),
        ("한글   테스트", "한글 테스트", 2),
    ],
)
def test_data_preprocessor(
    query: str,
    result: str,
    word_count: int,
) -> None:
    graph = data_preprocessor_graph()

    output = graph.invoke({"query": query})

    assert output == {"result": result, "word_count": word_count}
```

### 11.4 `chatbot`에 서브그래프 연결

`chatbot`의 내부 `State`에 `processed_query: str`, `word_count: int`를 추가하고 어댑터 노드를 만듭니다. 외부 입력·출력 계약에 필요하지 않다면 `InputState`와 `OutputState`에는 이 키를 노출하지 않습니다.

```python
# casts/chatbot/modules/nodes.py
from __future__ import annotations

from casts.base_node import BaseNode
from casts.chatbot.modules.state import State
from casts.data_preprocessor.graph import data_preprocessor_graph


class PreprocessNode(BaseNode):
    """전처리 Cast를 호출해 chatbot의 내부 State를 갱신합니다."""

    def __init__(self) -> None:
        super().__init__()
        self.subgraph = data_preprocessor_graph()

    def execute(self, state: State) -> dict[str, object]:
        result = self.subgraph.invoke({"query": state["query"]})
        return {
            "processed_query": result["result"],
            "word_count": result["word_count"],
        }
```

`chatbot/graph.py`에서는 기존 처리 노드 앞에 어댑터 노드를 연결합니다.

```python
builder.add_node("PreprocessNode", PreprocessNode())
builder.add_node("SampleNode", SampleNode())
builder.add_edge(START, "PreprocessNode")
builder.add_edge("PreprocessNode", "SampleNode")
builder.add_edge("SampleNode", END)
```

어댑터 계약은 별도 단위 테스트로 확인합니다.

```python
# tests/node_tests/test_chatbot_preprocess.py
from __future__ import annotations

from casts.chatbot.modules.nodes import PreprocessNode


def test_chatbot_preprocess_adapter() -> None:
    result = PreprocessNode()({"query": "  Hello    Act  "})

    assert result == {
        "processed_query": "Hello Act",
        "word_count": 2,
    }
```

### 11.5 검증

```bash
uv run pytest tests/cast_tests/data_preprocessor_test.py -v
uv run pytest --cov=casts --cov-branch --cov-report=term-missing
uv lock --check
uv run langgraph dev
```

LangSmith에서 trace를 열고 다음을 확인합니다.

- [ ] `chatbot` 상위 실행과 전처리 하위 실행이 연결되는가?
- [ ] 입력과 출력 State가 예상한 키만 노출하는가?
- [ ] latency와 오류가 어느 run에서 발생했는지 식별 가능한가?
- [ ] 민감정보가 trace에 남지 않는가?

---

## 운영 전 체크리스트

- [ ] 모든 Cast가 `uv.lock` 하나로 정상 해석되는가?
- [ ] 독립 패키징한 Cast 간 import만 workspace dependency로 선언되어 있는가?
- [ ] 모든 그래프 진입점이 `langgraph.json`에 유효하게 등록되어 있는가?
- [ ] 테스트마다 checkpointer와 thread가 격리되는가?
- [ ] 외부 API·LLM·DB 호출이 단위 테스트에서 모킹되는가?
- [ ] 서브그래프 persistence 모드를 의도적으로 선택했는가?
- [ ] trace에 버전·환경 metadata가 포함되는가?
- [ ] PII와 비밀정보가 로그와 trace에서 보호되는가?
- [ ] 실패한 production trace를 회귀 테스트로 전환할 절차가 있는가?

---

## 🧠 복습 퀴즈

1. uv workspace의 Cast들이 공유하는 파일은?
   **정답:** 루트 `uv.lock`
2. 현재 한국어 scaffold 언어 코드는?
   **정답:** `kr`
3. 부모와 자식의 State 스키마가 다를 때 권장 연결 방식은?
   **정답:** 어댑터 노드에서 입력을 변환해 서브그래프를 호출하고 출력을 부모 State 업데이트로 변환
4. 서브그래프가 같은 thread에서 호출 간 상태를 유지하게 하는 설정은?
   **정답:** `compile(checkpointer=True)`
5. `checkpointer=False`의 제약은?
   **정답:** interrupt, durable execution, checkpoint 기반 상태 조회를 사용할 수 없음
6. Cast 그래프 테스트의 scaffold 기본 경로와 이름은?
   **정답:** `tests/cast_tests/<cast_snake>_test.py`
7. LangSmith에서 한 요청의 전체 실행과 그 내부 단계를 각각 무엇이라 부르는가?
   **정답:** trace와 run

---

## 📚 참고 자료

- [Act Operator README](../README_KR.md)
- [LangGraph Subgraphs](https://docs.langchain.com/oss/python/langgraph/use-subgraphs)
- [LangGraph Testing](https://docs.langchain.com/oss/python/langgraph/test)
- [LangGraph Persistence](https://docs.langchain.com/oss/python/langgraph/persistence)
- [LangGraph Graph API](https://docs.langchain.com/oss/python/langgraph/graph-api)
- [LangSmith Observability](https://docs.langchain.com/langsmith/observability)
- [LangSmith Observability Concepts](https://docs.langchain.com/langsmith/observability-concepts)
- [LangSmith Evaluation](https://docs.langchain.com/langsmith/evaluation)
- [uv Workspaces](https://docs.astral.sh/uv/concepts/projects/workspaces/)
- [uv Dependency Management](https://docs.astral.sh/uv/concepts/projects/dependencies/)
- [pytest Documentation](https://docs.pytest.org/)

## 다음 주차 예고

> **5주차: 외부 연동과 메모리**에서는 MCP와 외부 서비스를 연결하고, Store와 벡터 검색을 사용해 thread를 넘어 유지되는 장기 메모리를 구현합니다.
