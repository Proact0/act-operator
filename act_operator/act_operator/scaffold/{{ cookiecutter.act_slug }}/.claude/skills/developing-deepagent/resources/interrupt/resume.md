# Resuming After Interrupt

After a HITL interrupt, resume execution by sending a `Command` with decisions.

## Contents

- Basic Resume (Approve / Reject)
- Advanced Resume (Multiple Interrupts)
- Decision Types
- Inspecting Interrupt State
- Key Notes

## Basic Resume (Approve / Reject)

```python
# casts.{cast_name}.modules.utils
from langgraph.types import Command

def resume_with_approve(agent, config: dict):
    """Approve the interrupted tool call as-is."""
    return agent.invoke(Command(resume=True), config=config)

def resume_with_reject(agent, config: dict):
    """Reject the tool call — agent receives feedback."""
    return agent.invoke(Command(resume=False), config=config)
```

## Advanced Resume (Multiple Interrupts)

When multiple tool calls are interrupted, use interrupt IDs:

```python
# casts.{cast_name}.modules.utils
from langgraph.types import Command

def build_resume_decisions(interrupts: list, overrides: dict | None = None):
    """Build resume decisions from interrupt list.

    Args:
        interrupts: List of interrupt objects from agent state.
        overrides: Dict mapping tool names to decision dicts.
                   If not provided, defaults to approve all.
    """
    resume = {}
    for interrupt in interrupts:
        action_request = interrupt.value["action_requests"][0]
        tool_name = action_request["name"]

        if overrides and tool_name in overrides:
            resume[interrupt.id] = overrides[tool_name]
        else:
            resume[interrupt.id] = {"decisions": [{"type": "approve"}]}

    return resume

def resume_with_decisions(agent, config: dict, resume: dict):
    """Resume agent with per-interrupt decisions."""
    return agent.invoke(Command(resume=resume), config=config)
```

## Decision Types

### Approve

```python
# casts.{cast_name}.modules.utils
def create_approve_decision():
    return {"decisions": [{"type": "approve"}]}
```

### Edit

```python
# casts.{cast_name}.modules.utils
def create_edit_decision(interrupt, new_args: dict):
    """Create edit decision with modified tool arguments."""
    edited_action = interrupt.value["action_requests"][0].copy()
    edited_action["args"].update(new_args)
    return {"decisions": [{"type": "edit", "edited_action": edited_action}]}
```

### Reject

```python
# casts.{cast_name}.modules.utils
def create_reject_decision():
    return {"decisions": [{"type": "reject"}]}
```

## Inspecting Interrupt State

```python
# casts.{cast_name}.modules.utils
def get_pending_interrupts(agent, config: dict) -> list:
    """Get all pending interrupts from agent state."""
    state = agent.get_state(config)
    interrupts = []
    for task in state.tasks:
        if task.interrupts:
            for interrupt in task.interrupts:
                interrupts.append({
                    "id": interrupt.id,
                    "tool": interrupt.value.get("action_requests", [{}])[0].get("name"),
                    "args": interrupt.value.get("action_requests", [{}])[0].get("args"),
                })
    return interrupts
```

## Key Notes

- `Command(resume=True)` and `Command(resume=False)` are shortcuts for single-interrupt approve/reject
- For multiple interrupts, use the dict form with interrupt IDs
- The `edited_action` in edit decisions must include the full action (name + args)
- After resume, the agent continues from where it was interrupted
- Checkpointer must be configured for interrupts to work
