# Skills for Subagents

Configure which skills each subagent type has access to.

## Contents

- Inheritance Rules
- General-Purpose Subagent
- Custom Subagents with Skills
- Skill Isolation
- Multiple Subagents with Different Skills
- Key Notes

## Inheritance Rules

| Subagent Type | Inherits Main Agent's Skills? | Custom Skills? |
|---------------|-------------------------------|----------------|
| General-purpose | Yes (automatic) | No |
| Custom (dict) | No | Yes (via `skills` parameter) |
| CompiledSubAgent | No | No (uses its own graph) |

## General-Purpose Subagent

Automatically inherits skills from the main agent:

```python
# casts.{cast_name}.modules.agents
from deepagents import create_deep_agent

def set_deep_agent():
    return create_deep_agent(
        model=get_deep_agent_model(),
        skills=["/skills/main/"],  # GP subagent gets these automatically
    )
```

## Custom Subagents with Skills

Custom subagents do **NOT** inherit the main agent's skills. Specify explicitly:

```python
# casts.{cast_name}.modules.agents
from deepagents import create_deep_agent
from .tools import web_search

def get_subagents():
    return [
        {
            "name": "researcher",
            "description": "Research assistant with specialized skills",
            "system_prompt": "You are a researcher.",
            "tools": [web_search],
            "skills": ["/skills/research/", "/skills/web-search/"],
        }
    ]

def set_deep_agent():
    return create_deep_agent(
        model=get_deep_agent_model(),
        skills=["/skills/main/"],             # Main agent + GP subagent
        subagents=get_subagents(),             # Researcher gets only its own skills
    )
```

## Skill Isolation

Skill state is **fully isolated**:

```
Main Agent ── skills: ["/skills/main/"]
    │
    ├── GP Subagent ── skills: ["/skills/main/"]  (inherited)
    │
    ├── Researcher ── skills: ["/skills/research/"]  (explicit)
    │
    └── Writer ── skills: ["/skills/writing/"]  (explicit)

No cross-visibility between any of these
```

## Multiple Subagents with Different Skills

```python
# casts.{cast_name}.modules.agents
from .tools import web_search, run_code

def get_subagents():
    return [
        {
            "name": "researcher",
            "description": "Conducts web research",
            "system_prompt": "You are a researcher.",
            "tools": [web_search],
            "skills": ["/skills/research/"],
        },
        {
            "name": "coder",
            "description": "Writes code",
            "system_prompt": "You are a developer.",
            "tools": [run_code],
            "skills": ["/skills/coding/", "/skills/testing/"],
        },
        {
            "name": "writer",
            "description": "Writes reports",
            "system_prompt": "You are a writer.",
            "tools": [],
            "skills": ["/skills/writing/"],
        },
    ]
```

## Key Notes

- GP subagent skill inheritance is automatic — don't duplicate skills in subagent definitions
- Custom subagents with no `skills` parameter get no skills at all
- CompiledSubAgent wraps a graph directly — skill handling is up to the wrapped graph
