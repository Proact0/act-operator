# CompiledSubAgent

Wrap an existing LangGraph compiled graph as a subagent for use with deep agents.

## Contents

- Parameters
- Requirements
- Wrapping a LangGraph Cast
- Wrapping a StateGraph
- Wrapping create_agent
- When to Use / NOT to Use

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | `str` | Yes | Unique identifier for the subagent |
| `description` | `str` | Yes | What it does (main agent uses this to decide delegation) |
| `runnable` | `CompiledStateGraph` | Yes | Pre-compiled LangGraph graph |

## Requirements

The wrapped graph **must** have a state key called `"messages"`:

```python
# casts.{cast_name}.modules.state
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

class SubagentState(TypedDict):
    messages: Annotated[list, add_messages]  # Required!
    # ... other state keys
```

## Wrapping a LangGraph Cast

In an Act project, wrap an existing cast as a subagent:

```python
# casts.{cast_name}.modules.agents
from deepagents import CompiledSubAgent

def get_cast_subagent():
    """Wrap another cast's compiled graph as a subagent."""
    from casts.analysis_cast.graph import build as build_analysis

    return CompiledSubAgent(
        name="analysis",
        description="Runs the analysis pipeline on provided data",
        runnable=build_analysis(),
    )
```

## Wrapping a StateGraph

```python
# casts.{cast_name}.modules.agents
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import AIMessage
from deepagents import CompiledSubAgent

def create_weather_subagent():
    """Create a custom StateGraph-based subagent."""
    from .state import SubagentState

    workflow = StateGraph(SubagentState)

    def get_weather(state: dict):
        return {"messages": [AIMessage(content="Weather: Sunny, 72F")]}

    workflow.add_node("weather", get_weather)
    workflow.add_edge(START, "weather")
    workflow.add_edge("weather", END)

    return CompiledSubAgent(
        name="weather",
        description="Gets current weather for cities",
        runnable=workflow.compile(),
    )
```

## Wrapping create_agent

```python
# casts.{cast_name}.modules.agents
from langchain.agents import create_agent
from deepagents import CompiledSubAgent

def create_sql_subagent():
    """Wrap a LangChain create_agent as a CompiledSubAgent."""
    sql_agent = create_agent(
        model="claude-sonnet-4-5-20250929",
        tools=[sql_query_tool, schema_tool],
        prompt="You are a SQL expert.",
    )
    return CompiledSubAgent(
        name="sql-expert",
        description="Executes SQL queries and analyzes database results",
        runnable=sql_agent,
    )
```

## When to Use

- You have an existing LangGraph graph to reuse as a subagent
- Complex subagent logic that requires custom graph topology
- Wrapping an existing cast from your Act project as a subagent

## When NOT to Use

- Simple subagents with just tools and a prompt → use dict-based custom subagents
- Only need context isolation → use the built-in general-purpose subagent
