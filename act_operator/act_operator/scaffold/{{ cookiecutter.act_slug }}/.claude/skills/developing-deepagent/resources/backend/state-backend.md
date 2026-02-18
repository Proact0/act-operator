# StateBackend

Ephemeral in-state filesystem backend. This is the **default** backend when no backend is specified.

## Overview

- Files are stored in LangGraph graph state
- Only persists for a **single thread** — files are lost when the conversation ends
- No disk access, no persistence across threads
- Ideal for stateless tasks and prototyping

## Implicit Usage (Default)

```python
# casts.{cast_name}.modules.agents
from deepagents import create_deep_agent
from .models import get_deep_agent_model

def set_deep_agent():
    """StateBackend is the default — no need to specify."""
    return create_deep_agent(
        model=get_deep_agent_model(),
    )
```

## Explicit Usage

```python
# casts.{cast_name}.modules.utils
from deepagents.backends import StateBackend

def create_state_backend(runtime):
    """Create explicit StateBackend from runtime."""
    return StateBackend(runtime)
```

```python
# casts.{cast_name}.modules.agents
from deepagents import create_deep_agent
from .utils import create_state_backend

def set_deep_agent():
    return create_deep_agent(
        model=get_deep_agent_model(),
        backend=create_state_backend,
    )
```

## Seeding Files

With StateBackend, seed initial files via the `files` key using `create_file_data()`:

```python
# casts.{cast_name}.modules.utils
from deepagents.backends.utils import create_file_data

def create_seed_files():
    """Prepare seed files for StateBackend."""
    return {
        "/config.json": create_file_data('{"key": "value"}'),
        "/skills/my-skill/SKILL.md": create_file_data("---\nname: my-skill\n---\n# My Skill"),
    }
```

> **Important**: Raw strings are not supported for `files`. Always use `create_file_data()`.

## BackendFactory Pattern

StateBackend requires runtime access, so it uses the factory pattern:

```python
# casts.{cast_name}.modules.utils

# ✅ Factory (callable that receives runtime)
def create_state_backend(runtime):
    return StateBackend(runtime)

# ❌ Instance — this won't work:
# backend = StateBackend()  # Missing runtime
```

## When to Use

- Prototyping and development
- Stateless single-turn tasks
- When no filesystem persistence is needed
- As the default backend in a CompositeBackend

## When NOT to Use

- Need files to persist across threads → use `StoreBackend`
- Need real disk access → use `FilesystemBackend`
- Need code execution → use a sandbox backend
- Need hybrid storage → use `CompositeBackend`
