# General-Purpose Subagent

The general-purpose (GP) subagent is a built-in subagent available to every deep agent. It requires no configuration.

## Overview

- Automatically available — always present alongside any custom subagents
- Has the same instructions and tools as the main agent
- Inherits skills from the main agent when `skills` is passed to `create_deep_agent`
- Primary purpose: **context isolation**

## Skills Inheritance

```python
# casts.{cast_name}.modules.agents
from deepagents import create_deep_agent

def set_deep_agent():
    return create_deep_agent(
        model=get_deep_agent_model(),
        skills=["./skills/"],  # GP subagent inherits these automatically
    )
```

This is different from custom subagents, which require their own `skills` parameter.

## Key Characteristics

| Property | Value |
|----------|-------|
| Name | `"general-purpose"` |
| Configuration | None required |
| Tools | Same as main agent |
| Skills | Inherited from main agent |
| Model | Same as main agent |
| Context | Isolated from main agent |
| Returns | Single final report |

## When to Rely on GP vs Custom Subagents

**Use GP subagent when:**
- Task just needs context isolation (not specialized tools)
- Subtask uses the same tools as the main agent

**Use custom subagents when:**
- Subtask needs different tools or a different model
- Subtask needs specialized system prompt or its own skills
