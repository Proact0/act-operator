# CompositeBackend

A flexible router backend that maps different filesystem paths to different backends.

## Contents

- Basic Usage
- Parameters
- Path Routing
- Common Patterns
- When to Use / NOT to Use

## Basic Usage

```python
# casts.{cast_name}.modules.utils
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend
from langgraph.store.memory import InMemoryStore

def create_composite_backend(runtime):
    """Create backend with ephemeral workspace + persistent memory."""
    return CompositeBackend(
        default=StateBackend(runtime),
        routes={"/memories/": StoreBackend(runtime)},
    )

def create_store():
    return InMemoryStore()
```

```python
# casts.{cast_name}.modules.agents
from deepagents import create_deep_agent
from .models import get_deep_agent_model
from .utils import create_composite_backend, create_store

def set_deep_agent():
    return create_deep_agent(
        model=get_deep_agent_model(),
        backend=create_composite_backend,
        store=create_store(),
    )
```

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `default` | `BackendProtocol` | Backend for paths that don't match any route |
| `routes` | `dict[str, BackendProtocol]` | Mapping of path prefixes to backends |

## Path Routing

- Routes file operations based on path prefix
- Longer prefixes win (e.g., `/memories/projects/` overrides `/memories/`)
- `ls`, `glob`, `grep` aggregate results and show original path prefixes

```
/workspace/plan.md      → StateBackend (ephemeral)
/workspace/output.py    → StateBackend (ephemeral)
/memories/prefs.md      → StoreBackend (persistent)
/memories/knowledge.md  → StoreBackend (persistent)
/docs/reference.md      → FilesystemBackend (local disk)
```

## Common Patterns

### Ephemeral + Persistent Memory

```python
# casts.{cast_name}.modules.utils
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend

def create_memory_backend(runtime):
    """Working files ephemeral, memories persist across threads."""
    return CompositeBackend(
        default=StateBackend(runtime),
        routes={"/memories/": StoreBackend(runtime)},
    )
```

### Ephemeral + Local Disk

```python
# casts.{cast_name}.modules.utils
from deepagents.backends import CompositeBackend, StateBackend, FilesystemBackend

def create_project_backend(runtime):
    """Working files ephemeral, project files on local disk."""
    return CompositeBackend(
        default=StateBackend(runtime),
        routes={
            "/project/": FilesystemBackend(root_dir="/path/to/project", virtual_mode=True),
        },
    )
```

### Multiple Persistent Routes

```python
# casts.{cast_name}.modules.utils
def create_multi_route_backend(runtime):
    """Different persistent stores for different purposes."""
    return CompositeBackend(
        default=StateBackend(runtime),
        routes={
            "/memories/": StoreBackend(runtime),
            "/docs/": FilesystemBackend(root_dir="/path/to/docs", virtual_mode=True),
        },
    )
```

## When to Use

- Need both ephemeral and cross-thread storage
- Multiple sources of information in a single filesystem
- Long-term memories under `/memories/` with ephemeral working files

## When NOT to Use

- Only need ephemeral storage → use `StateBackend`
- Only need disk access → use `FilesystemBackend`
- Only need persistent storage → use `StoreBackend`
