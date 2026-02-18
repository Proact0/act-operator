# FilesystemBackend

Grants agents direct read/write access to the local machine's filesystem.

## Usage

```python
# casts.{cast_name}.modules.utils
from deepagents.backends import FilesystemBackend

def create_filesystem_backend(root_dir: str = "."):
    """Create filesystem backend with virtual mode for security."""
    return FilesystemBackend(root_dir=root_dir, virtual_mode=True)
```

```python
# casts.{cast_name}.modules.agents
from deepagents import create_deep_agent
from .models import get_deep_agent_model
from .utils import create_filesystem_backend

def set_deep_agent():
    return create_deep_agent(
        model=get_deep_agent_model(),
        backend=create_filesystem_backend(),
    )
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `root_dir` | `str` | required | Absolute or relative path to root directory |
| `virtual_mode` | `bool` | `False` | Enable path-based access restrictions |

## Virtual Mode (Recommended)

Always use `virtual_mode=True` for security:

```python
# casts.{cast_name}.modules.utils

# ✅ Secure — blocks .., ~, and absolute paths outside root
def create_secure_backend():
    return FilesystemBackend(root_dir="/path/to/project", virtual_mode=True)

# ❌ Insecure — agent can access ANY file on the system
# FilesystemBackend(root_dir="/path/to/project")
```

When `virtual_mode=True`: Blocks `..` path traversal, `~` home directory expansion, and absolute paths outside `root_dir`.

## With HITL

```python
# casts.{cast_name}.modules.agents
from deepagents import create_deep_agent
from .utils import create_filesystem_backend, create_checkpointer

def set_deep_agent_with_hitl():
    return create_deep_agent(
        backend=create_filesystem_backend("/path/to/project"),
        interrupt_on={
            "write_file": True,
            "edit_file": True,
            "read_file": False,
        },
        checkpointer=create_checkpointer(),
    )
```

## When to Use

- Local development tools and coding assistants
- CLI agents that need to read/write project files
- CI/CD pipeline agents (with security safeguards)

## When NOT to Use

- Web servers or HTTP APIs → use `StateBackend` or sandbox
- Untrusted environments → use sandbox backend
- Need persistence across threads → use `StoreBackend`
