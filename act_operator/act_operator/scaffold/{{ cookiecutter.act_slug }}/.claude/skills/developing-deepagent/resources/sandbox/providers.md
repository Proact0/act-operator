# Sandbox Providers

Deep agents support pluggable sandbox providers for isolated code execution.

## Contents

- Daytona
- Modal
- Runloop
- CLI Usage
- Security Notes

## Daytona

Full Linux VM environment.

### Install

```bash
uv add langchain-daytona
```

### Setup

```bash
export DAYTONA_API_KEY="your-key"
```

### Usage

```python
# casts.{cast_name}.modules.utils
from daytona import Daytona
from langchain_daytona import DaytonaSandbox

def create_daytona_sandbox():
    """Create and return a Daytona sandbox backend."""
    sandbox = Daytona().create()
    return DaytonaSandbox(sandbox=sandbox), sandbox

def stop_sandbox(sandbox):
    """Stop a running Daytona sandbox."""
    sandbox.stop()
```

```python
# casts.{cast_name}.modules.agents
from deepagents import create_deep_agent
from .models import get_deep_agent_model
from .utils import create_daytona_sandbox

def set_deep_agent():
    backend, _sandbox = create_daytona_sandbox()
    return create_deep_agent(
        model=get_deep_agent_model(),
        system_prompt="You are a Python coding assistant with sandbox access.",
        backend=backend,
    )
```

---

## Modal

Scalable cloud container execution.

### Install

```bash
uv add langchain-modal
```

### Setup

```bash
modal setup
```

### Usage

```python
# casts.{cast_name}.modules.utils
import modal
from langchain_modal import ModalSandbox

def create_modal_sandbox(app_name: str = "your-app"):
    """Create and return a Modal sandbox backend."""
    app = modal.App.lookup(app_name)
    sandbox = modal.Sandbox.create(app=app)
    return ModalSandbox(sandbox=sandbox), sandbox

def stop_modal_sandbox(sandbox):
    """Terminate a running Modal sandbox."""
    sandbox.terminate()
```

```python
# casts.{cast_name}.modules.agents
from deepagents import create_deep_agent
from .models import get_deep_agent_model
from .utils import create_modal_sandbox

def set_deep_agent():
    backend, _sandbox = create_modal_sandbox()
    return create_deep_agent(
        model=get_deep_agent_model(),
        system_prompt="You are a Python coding assistant with sandbox access.",
        backend=backend,
    )
```

---

## Runloop

Managed execution environment.

### Install

```bash
uv add langchain-runloop
```

### Setup

```bash
export RUNLOOP_API_KEY="your-key"
```

### Usage

```python
# casts.{cast_name}.modules.utils
from langchain_runloop import RunloopSandbox

def create_runloop_sandbox():
    """Create and return a Runloop sandbox backend."""
    sandbox = RunloopSandbox.create()
    return sandbox, sandbox

def stop_runloop_sandbox(sandbox):
    """Stop a running Runloop sandbox."""
    sandbox.stop()
```

```python
# casts.{cast_name}.modules.agents
from deepagents import create_deep_agent
from .models import get_deep_agent_model
from .utils import create_runloop_sandbox

def set_deep_agent():
    backend, _sandbox = create_runloop_sandbox()
    return create_deep_agent(
        model=get_deep_agent_model(),
        system_prompt="You are a coding assistant.",
        backend=backend,
    )
```

---

## CLI Usage

When using the deep agents CLI, specify sandbox via command-line flags:

```bash
# Runloop
uvx deepagents-cli --sandbox runloop --sandbox-setup ./setup.sh

# Daytona
uvx deepagents-cli --sandbox daytona --sandbox-setup ./setup.sh

# Modal
uvx deepagents-cli --sandbox modal --sandbox-setup ./setup.sh
```

## Security Notes

- Sandboxes isolate code execution, but agents remain vulnerable to prompt injection
- Use HITL approval for sensitive operations
- Use short-lived secrets and trusted setup scripts only
