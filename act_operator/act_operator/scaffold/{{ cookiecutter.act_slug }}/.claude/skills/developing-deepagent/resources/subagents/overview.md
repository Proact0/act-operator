# Subagents Overview

Deep agents can create subagents to delegate work. Subagents provide **context isolation** — keeping the main agent's context clean while going deep on a task.

## Contents

- Architecture
- Subagent Types
- Passing Subagents to create_deep_agent
- Skills Inheritance
- Key Notes

## Architecture

```
Main Agent ──(task tool)──> Subagent
                              │
                ┌─────────────┼─────────────┐
                │             │             │
           Research        Code         General
                │             │             │
           (isolated)    (isolated)    (isolated)
                │             │             │
                └─────────────┼─────────────┘
                              │
                        Final Result ──> Main Agent
```

## Subagent Types

### General-Purpose Subagent (Built-in)

- Automatically available — no configuration needed
- Has the same instructions and tools as the main agent
- Inherits skills from the main agent
- Primary purpose: context isolation for complex tasks

### Custom Subagents (Dict Definition)

```python
# casts.{cast_name}.modules.agents
def get_subagents():
    return [
        {
            "name": "researcher",
            "description": "Conducts web research",
            "system_prompt": "You are a research specialist.",
            "tools": [web_search_tool],
            "model": "gpt-4.1",                    # Optional: different model
            "middleware": [],                        # Optional: custom middleware
            "skills": ["/skills/research/"],         # Optional: subagent-specific skills
        }
    ]
```

### CompiledSubAgent (LangGraph Graph Wrapper)

```python
# casts.{cast_name}.modules.agents
from deepagents import CompiledSubAgent

def get_compiled_subagent(compiled_graph):
    return CompiledSubAgent(
        name="analyzer",
        description="Specialized data analysis",
        runnable=compiled_graph,  # Must have "messages" state key
    )
```

## Passing Subagents to create_deep_agent

```python
# casts.{cast_name}.modules.agents
from deepagents import create_deep_agent, CompiledSubAgent
from .models import get_deep_agent_model
from .tools import get_tools

def get_subagents():
    return [
        {
            "name": "writer",
            "description": "Writes polished reports",
            "system_prompt": "You are a technical writer.",
            "tools": [],
        },
    ]

def set_deep_agent():
    return create_deep_agent(
        model=get_deep_agent_model(),
        tools=get_tools(),
        subagents=get_subagents(),
    )
```

## Skills Inheritance

- **General-purpose subagent**: Automatically inherits main agent's skills
- **Custom subagents**: Do NOT inherit. Must specify their own via `skills` parameter
- **Skill state is fully isolated**: Main agent's skills are not visible to subagents, and vice versa

## Key Notes

- The `description` field is critical — the main agent uses it to decide which subagent to invoke
- Subagents are stateless: they execute once and return a single result
- Subagent context is fully isolated from the main agent
- Multiple subagents can run concurrently
