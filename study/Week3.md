# 3주차: 미들웨어와 제어 흐름 (Middleware & Control Flow)

> **목표**: LangChain v1 미들웨어와 LangGraph 제어 흐름·지속성을 결합해, 사람이 통제할 수 있고 장애에 견디는 에이전트를 구현합니다.
>
> **최종 확인일**: 2026-08-26 · 최신 공식 문서 기준

## 📋 학습 체크리스트

- [ ] Step 1: 미들웨어와 실행 순서
- [ ] Step 2: Human-in-the-Loop 승인 흐름
- [ ] Step 3: 대화 요약과 PII 보호
- [ ] Step 4: 커스텀 미들웨어
- [ ] Step 5: 조건부 분기
- [ ] Step 6: Checkpointer와 Store
- [ ] Step 7: Retry·Fallback·호출 제한
- [ ] Step 8: 승인 기반 이메일 에이전트 실습
- [ ] 마무리: 복습 퀴즈와 운영 점검

---

## 시작하기 전에

```bash
uv sync
uv tree | grep -E "langchain|langgraph"
```

PowerShell에서는 `uv tree | Select-String "langchain|langgraph"`를 사용합니다.

> [!NOTE]
> 스캐폴드는 `langchain>=1.0.0`, `langgraph>=1.0.0`을 사용합니다. 기능별 최소 버전은 공식 문서에서 확인하세요.

---

## Step 1: 미들웨어와 실행 순서

미들웨어는 `create_agent()`의 루프에 입력 검증, 로깅, 재시도, 승인, 요약 같은 횡단 관심사를 삽입합니다.

| 종류 | 훅 | 실행 시점 |
|---|---|---|
| Node-style | `before_agent`, `after_agent` | 실행 전·후 1회 |
| Node-style | `before_model`, `after_model` | 각 모델 호출 전·후 |
| Wrap-style | `wrap_model_call` | 모델 호출을 감쌈 |
| Wrap-style | `wrap_tool_call` | 도구 호출을 감쌈 |

`middleware=[A, B, C]`이면 `before_*`는 A→B→C, `after_*`는 C→B→A입니다. `wrap_*`는 A가 가장 바깥에서 B와 C를 감쌉니다.

### 1.1 가장 많이 사용되는 핵심 미들웨어 Top 5

실무 및 프로덕션 환경에서 가장 널리 사용되는 미들웨어는 다음과 같습니다:

| 순위 | 미들웨어 | 주요 역할 | 핵심 목적 |
|:---:|---|---|---|
| **1** | `HumanInTheLoopMiddleware` | 부작용 도구 실행 전 사람 승인/수정/거절 | 안전성·통제권 확보 |
| **2** | `SummarizationMiddleware` | 토큰 초과 시 오래된 대화 자동 압축/요약 | 컨텍스트·비용 최적화 |
| **3** | `PIIMiddleware` | 카드번호, 주민번호, 이메일, API 키 마스킹/차단 | 보안 및 규제 준수 |
| **4** | `ToolCallLimitMiddleware` | 특정 도구의 실행 횟수 상한(run_limit) 제한 | 무한 루프·과금 방지 |
| **5** | `ModelRetryMiddleware` / `ModelFallbackMiddleware` | 네트워크 재시도 및 백업 모델 전환 | 가용성·장애 복구 |

### 1.2 등록 방법

```python
from __future__ import annotations

from langchain.agents import create_agent


def set_safe_agent():
    """미들웨어가 적용된 에이전트를 생성합니다."""
    return create_agent(
        model=get_chat_model(),
        tools=[search_documents],
        middleware=get_middlewares(),
        system_prompt="근거에 기반하여 답변하세요.",
    )
```

`create_agent()`의 반환값은 컴파일된 LangGraph입니다. 상위 `StateGraph`의 노드나 서브그래프로 넣어도 미들웨어가 유지됩니다.

### 1.3 실무 표준 조합 패턴 (Standard Stack)

실제 프로덕션 환경에서는 보통 아래와 같이 **보안 ➔ 승인 ➔ 호출 제한 ➔ 컨텍스트 요약** 순서로 미들웨어 체인을 구성합니다:

```python
from langchain.agents.middleware import (
    HumanInTheLoopMiddleware,
    PIIMiddleware,
    SummarizationMiddleware,
    ToolCallLimitMiddleware,
)

middlewares = [
    # 1. 개인정보 보호 (입력 단계에서 마스킹)
    PIIMiddleware("credit_card", strategy="mask", apply_to_input=True),
    # 2. 부작용 도구 승인 절차 (HITL)
    HumanInTheLoopMiddleware(
        interrupt_on={"send_email": {"allowed_decisions": ["approve", "edit", "reject"]}},
        description_prefix="이메일 발송 승인 대기 중",
    ),
    # 3. 도구 중복 호출 방지 (최대 1회)
    ToolCallLimitMiddleware(tool_name="send_email", run_limit=1, exit_behavior="error"),
    # 4. 컨텍스트 토큰 초과 시 자동 요약
    SummarizationMiddleware(
        model=get_summary_model(),
        trigger=("tokens", 4_000),
        keep=("messages", 10),
    ),
]
```

---

## Step 2: Human-in-the-Loop 승인 흐름

```python
from langchain.agents.middleware import HumanInTheLoopMiddleware

hitl = HumanInTheLoopMiddleware(
    interrupt_on={
        "send_email": {
            "allowed_decisions": ["approve", "edit", "reject"],
        },
        "draft_email": False,
    },
    description_prefix="이메일 전송 승인 대기",
)
```

`interrupt_on`의 키는 도구 이름입니다. 부작용 도구를 거부할 때는 `respond`가 아니라 `reject`를 사용합니다.

### 2.1 중단과 재개

HITL에는 Checkpointer와 안정적인 `thread_id`가 모두 필요합니다.

```python
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

agent = create_agent(
    model=get_chat_model(),
    tools=[send_email],
    middleware=[hitl],
    checkpointer=InMemorySaver(),
)
config = {"configurable": {"thread_id": "email-001"}}
request = {
    "messages": [
        {"role": "user", "content": "team@example.com에 안내 메일을 보내줘."}
    ]
}
pending = agent.invoke(request, config=config, version="v2")
print(pending.interrupts)
agent.invoke(
    Command(resume={"decisions": [{"type": "approve"}]}),
    config=config,
    version="v2",
)
```

`InMemorySaver`는 개발·테스트용입니다. 수정은 `edited_action`, 거절은 `{"type": "reject", "message": ...}`를 결정에 넣습니다. 여러 작업이면 요청과 같은 순서로 결정합니다. 레거시 결과 형식은 `__interrupt__` 키를 사용합니다.

---

## Step 3: 대화 요약과 PII 보호

```python
from langchain.agents.middleware import SummarizationMiddleware

summarizer = SummarizationMiddleware(
    model=get_summary_model(),
    trigger=("tokens", 4_000),
    keep=("messages", 10),
)
```

튜플은 단일 조건, 여러 키를 가진 딕셔너리는 AND, 조건 리스트는 OR입니다. `keep`은 한 종류의 기준만 지정합니다.

### 3.1 PIIMiddleware

```python
from langchain.agents.middleware import PIIMiddleware

pii_middlewares = [
    PIIMiddleware("email", strategy="redact", apply_to_input=True),
    PIIMiddleware("credit_card", strategy="mask", apply_to_input=True),
    PIIMiddleware(
        "internal_api_key",
        detector=r"act_[A-Za-z0-9]{32}",
        strategy="block",
        apply_to_tool_results=True,
    ),
]
```

전략은 `block`, `redact`, `mask`, `hash`입니다. 적용 범위는 입력·출력·도구 결과별로 정합니다. 로그·트레이스·저장소까지 포함한 전체 데이터 경로도 보호해야 합니다.

---

## Step 4: 커스텀 미들웨어

```python
from typing import Any

from langchain.agents.middleware import AgentMiddleware, AgentState, hook_config
from langchain.messages import AIMessage
from langgraph.runtime import Runtime


class MessageLimitMiddleware(AgentMiddleware):
    """메시지 수가 한도를 넘으면 정상 종료합니다."""

    @hook_config(can_jump_to=["end"])
    def before_model(
        self,
        state: AgentState,
        runtime: Runtime,
    ) -> dict[str, Any] | None:
        if len(state["messages"]) < 50:
            return None
        return {
            "messages": [AIMessage("대화 한도에 도달했습니다.")],
            "jump_to": "end",
        }
```

`jump_to`를 반환하려면 `can_jump_to`를 선언합니다.

---

## Step 5: 조건부 분기

미들웨어는 에이전트 내부 루프를, `conditions.py`는 상위 그래프 토폴로지를 제어합니다.

```python
from typing import Literal


def route_by_result(state: State) -> Literal["review", "retry", "complete"]:
    """현재 상태에 따라 다음 단계를 선택합니다."""
    if state.get("needs_review", False):
        return "review"
    if state.get("error") and state.get("retry_count", 0) < 3:
        return "retry"
    return "complete"
```

```python
builder.add_conditional_edges(
    "process",
    route_by_result,
    {"review": "review", "retry": "retry", "complete": END},
)
```

`Literal`과 명시적 경로 맵은 오타를 줄이고 그래프 시각화를 명확하게 합니다.

---

## Step 6: Checkpointer와 Store

| 구분 | Checkpointer | Store |
|---|---|---|
| 저장 대상 | 그래프 상태 스냅샷 | 애플리케이션 데이터 |
| 범위 | 한 `thread_id` | 여러 스레드 |
| 용도 | HITL, 대화 연속성, 복구 | 사용자 선호, 장기 기억 |

```python
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore

graph = builder.compile(
    checkpointer=InMemorySaver(),
    store=InMemoryStore(),
)
config = {"configurable": {"thread_id": "conversation-001"}}
```

운영 환경은 Postgres 등 내구성 있는 Checkpointer를 사용합니다. Agent Server에서는 서버가 지속성 인프라를 관리합니다.

---

## Step 7: Retry·Fallback·호출 제한

```python
from langchain.agents.middleware import (
    ModelCallLimitMiddleware,
    ModelFallbackMiddleware,
    ModelRetryMiddleware,
    ToolCallLimitMiddleware,
)
```

```python
reliability = [
    ModelRetryMiddleware(
        max_retries=3,
        retry_on=(ConnectionError, TimeoutError),
        on_failure="error",
    ),
    ModelFallbackMiddleware(
        get_first_fallback_model(),
        get_second_fallback_model(),
    ),
    ModelCallLimitMiddleware(run_limit=8, exit_behavior="end"),
    ToolCallLimitMiddleware(
        tool_name="send_email",
        run_limit=1,
        exit_behavior="error",
    ),
]
```

`max_retries`는 최초 호출 이후의 추가 시도 횟수입니다. 대체 모델은 같은 도구·출력 요구사항을 지원해야 하며, 모델 ID는 실제 사용 가능한 값으로 교체합니다.

---

## Step 8: 승인 기반 이메일 에이전트 실습

요구사항:

- 초안은 자동 작성하되 실제 전송은 승인 필요
- 입력의 카드 번호를 마스킹
- 4,000토큰에서 오래된 대화를 요약
- 한 실행에서 이메일 전송은 최대 1회
- 개발 환경은 `InMemorySaver` 사용

> [!WARNING]
> `send_email`은 모의 도구입니다. 실제 연동 시 멱등성 키, 감사 로그, 전송 결과 저장을 설계하세요.

```python
from langchain.tools import tool


@tool
def send_email(to: str, subject: str, body: str) -> str:
    """승인된 이메일 전송을 모의 실행합니다."""
    return f"전송 완료: {to} / {subject}"
```

### 8.1 에이전트 조립

```python
email_agent = create_agent(
    model=get_chat_model(),
    tools=[send_email],
    middleware=[
        PIIMiddleware("credit_card", strategy="mask"),
        hitl,
        ToolCallLimitMiddleware(
            tool_name="send_email",
            run_limit=1,
            exit_behavior="error",
        ),
        summarizer,
    ],
    checkpointer=InMemorySaver(),
    system_prompt="실제 전송은 승인 결과를 따르세요.",
)
```

검증 항목:

- [ ] `send_email` 실행 전에 중단되는가?
- [ ] 같은 `thread_id`로 승인·수정·거절할 수 있는가?
- [ ] 승인 시 한 번만 전송되고 거절 시 실행되지 않는가?
- [ ] PII 마스킹과 요약이 각각 동작하는가?

---

## 🧩 복습 퀴즈

1. `middleware=[A, B, C]`의 `after_model` 순서는?
   **정답:** C → B → A
2. HITL 재개에 필요한 두 요소는?
   **정답:** Checkpointer와 동일한 `thread_id`
3. 사용자 장기 선호와 현재 대화 상태는 어디에 저장하는가?
   **정답:** 각각 Store와 Checkpointer
4. `trigger={"tokens": 4000, "messages": 10}`의 논리는?
   **정답:** AND

## 운영 전 체크리스트

- [ ] 부작용 도구에 HITL 또는 동등한 정책이 있는가?
- [ ] 외부 쓰기 도구가 멱등한가?
- [ ] 운영용 내구성 Checkpointer를 사용하는가?
- [ ] PII가 로그·트레이스·저장소에 노출되지 않는가?
- [ ] Retry 대상과 호출 상한이 제한되어 있는가?

---

## 📚 참고 자료

- [Middleware 개요](https://docs.langchain.com/oss/python/langchain/middleware/overview)
- [내장 Middleware](https://docs.langchain.com/oss/python/langchain/middleware/built-in)
- [Custom Middleware](https://docs.langchain.com/oss/python/langchain/middleware/custom)
- [Human-in-the-Loop](https://docs.langchain.com/oss/python/langchain/human-in-the-loop)
- [Guardrails와 PII](https://docs.langchain.com/oss/python/langchain/guardrails)
- [LangGraph Interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts)
- [LangGraph Persistence](https://docs.langchain.com/oss/python/langgraph/persistence)
- [LangGraph Graph API](https://docs.langchain.com/oss/python/langgraph/graph-api)

## 다음 주차 예고

> **4주차: 엔지니어링 및 운영 최적화**에서는 여러 Cast의 의존성과 `langgraph.json`을 관리하고, pytest와 LangSmith로 품질과 관측성을 확보합니다.
