# StoreBackend

Persistent filesystem backend that stores files in a LangGraph Store, enabling cross-thread persistence.

## Usage

```python
# casts.{cast_name}.modules.utils
from deepagents.backends import StoreBackend
from langgraph.store.memory import InMemoryStore

def create_store():
    """Create in-memory store. Use DB-backed store in production."""
    return InMemoryStore()

def create_store_backend(runtime):
    """Create StoreBackend from runtime."""
    return StoreBackend(runtime)
```

```python
# casts.{cast_name}.modules.agents
from deepagents import create_deep_agent
from .models import get_deep_agent_model
from .utils import create_store, create_store_backend

def set_deep_agent():
    return create_deep_agent(
        model=get_deep_agent_model(),
        backend=create_store_backend,
        store=create_store(),
    )
```

## How It Works

- Files are stored in the LangGraph Store (key-value persistence layer)
- Persists across threads — files survive when the conversation ends
- Requires a `store` to be passed to `create_deep_agent`
- Uses the factory pattern (receives runtime to access the store)

## Pre-seeding Files

```python
# casts.{cast_name}.modules.utils
from deepagents.backends.utils import create_file_data
from langgraph.store.memory import InMemoryStore

def create_seeded_store():
    """Create store with pre-seeded files."""
    store = InMemoryStore()
    store.put(
        namespace=("filesystem",),
        key="/skills/my-skill/SKILL.md",
        value=create_file_data("---\nname: my-skill\n---\n# Instructions"),
    )
    return store
```

## BackendFactory Pattern

StoreBackend requires runtime to access the store:

```python
# casts.{cast_name}.modules.utils

# ✅ Factory pattern — receives runtime
def create_store_backend(runtime):
    return StoreBackend(runtime)

# ❌ Instance — won't have access to store
# backend = StoreBackend()  # Missing runtime
```

## When to Use

- Files need to persist across multiple threads/conversations
- Storing long-term memories, instructions, or knowledge
- Deployed agents that accumulate knowledge over time
- As a route in `CompositeBackend` for selective persistence

## When NOT to Use

- Ephemeral single-thread tasks → use `StateBackend`
- Need real disk access → use `FilesystemBackend`
- Need code execution → use a sandbox backend
