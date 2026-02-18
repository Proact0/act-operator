# Custom Subagent

Define specialized subagents with their own tools, model, system prompt, and skills.

## Contents

- Parameters
- Basic Definition
- With Custom Model
- With Middleware
- With Skills
- Key Notes

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | `str` | Yes | Unique name for the subagent |
| `description` | `str` | Yes | What the subagent does (main agent uses this to decide when to delegate) |
| `system_prompt` | `str` | Yes | Instructions for the subagent |
| `tools` | `list[BaseTool]` | Yes | Tools available to the subagent |
| `model` | `str \| BaseChatModel` | No | Override model (defaults to main agent's model) |
| `middleware` | `list[Middleware]` | No | Custom middleware for the subagent |
| `skills` | `list[str]` | No | Subagent-specific skill paths |

## Basic Definition

```python
# casts.{cast_name}.modules.tools
from langchain.tools import tool

@tool
def web_search(query: str) -> str:
    """Search the web for information."""
    return f"Results for: {query}"

@tool
def analyze_data(data: str) -> str:
    """Analyze data and return insights."""
    return f"Analysis of: {data}"
```

```python
# casts.{cast_name}.modules.agents
from deepagents import create_deep_agent
from .models import get_deep_agent_model
from .tools import web_search, analyze_data

def get_subagents():
    return [
        {
            "name": "researcher",
            "description": "Searches the web for information",
            "system_prompt": "You are a research specialist.",
            "tools": [web_search],
        },
        {
            "name": "analyst",
            "description": "Analyzes data and produces insights",
            "system_prompt": "You are a data analyst.",
            "tools": [analyze_data],
            "model": "gpt-4.1",  # Different model for analysis
        },
    ]

def set_deep_agent():
    return create_deep_agent(
        model=get_deep_agent_model(),
        subagents=get_subagents(),
    )
```

## With Custom Model

```python
# casts.{cast_name}.modules.agents
def get_fast_subagent():
    return {
        "name": "fast-worker",
        "description": "Quick tasks that don't need deep reasoning",
        "system_prompt": "Complete the task efficiently.",
        "tools": [simple_tool],
        "model": "claude-haiku-4-5-20251001",  # Cheaper, faster model
    }
```

## With Middleware

```python
# casts.{cast_name}.modules.agents
def get_subagent_with_middleware():
    return {
        "name": "data-processor",
        "description": "Processes and transforms data",
        "system_prompt": "You are a data processing specialist.",
        "tools": [transform_tool],
        "middleware": [retry_middleware, logging_middleware],
    }
```

## With Skills

Custom subagents do NOT inherit the main agent's skills. Specify skills explicitly:

```python
# casts.{cast_name}.modules.agents
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
        skills=["/skills/main/"],         # Main agent + GP subagent get these
        subagents=get_subagents(),         # Researcher gets only its own skills
    )
```

## Key Notes

- The `description` field is critical — the main agent uses it to decide which subagent to invoke
- Subagents are stateless: they execute once and return a result
- Subagent context is fully isolated from the main agent
- Multiple subagents can run concurrently
