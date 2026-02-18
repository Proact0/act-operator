# LocalShellBackend

A local shell backend for development and testing. Provides filesystem tools plus the `execute` tool for running shell commands on the local machine.

## Contents

- Usage
- Parameters
- With HITL Safeguards
- Security Warning
- When to Use / NOT to Use

## Usage

```python
# casts.{cast_name}.modules.utils
from deepagents.backends import LocalShellBackend

def create_local_shell_backend(root_dir: str = ".", env: dict | None = None):
    """Create local shell backend for dev/testing."""
    return LocalShellBackend(
        root_dir=root_dir,
        env=env or {"PATH": "/usr/bin:/bin"},
    )
```

```python
# casts.{cast_name}.modules.agents
from deepagents import create_deep_agent
from .models import get_deep_agent_model
from .utils import create_local_shell_backend

def set_deep_agent():
    return create_deep_agent(
        model=get_deep_agent_model(),
        system_prompt="You are a coding assistant.",
        backend=create_local_shell_backend(),
    )
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `root_dir` | `str` | required | Root directory for filesystem operations |
| `env` | `dict[str, str]` | `None` | Environment variables for shell commands |

## With HITL Safeguards

```python
# casts.{cast_name}.modules.agents
from deepagents import create_deep_agent
from .utils import create_local_shell_backend, create_checkpointer

def set_safe_local_agent():
    """Local shell agent with HITL for write/execute operations."""
    return create_deep_agent(
        backend=create_local_shell_backend(),
        interrupt_on={
            "write_file": True,
            "edit_file": True,
            "execute": True,
            "read_file": False,
        },
        checkpointer=create_checkpointer(),
    )
```

## Security Warning

> **LocalShellBackend provides unrestricted filesystem and shell access. Use only in controlled environments.**

Risks:
- Agent has full access to local filesystem
- Agent can execute any shell command
- No isolation from host system
- File modifications are permanent

Safeguards:
- Use HITL for write/execute operations
- Restrict `env` to limit what commands can access
- Use `root_dir` to scope filesystem access (but `execute` still has full host access)

## When to Use

- Local development and testing
- Quick prototyping before setting up a remote sandbox
- CI/CD pipelines with controlled permissions

## When NOT to Use

- Production environments → use Daytona, Modal, or Runloop
- Untrusted inputs → use remote sandbox
- Web servers or HTTP APIs → use remote sandbox
