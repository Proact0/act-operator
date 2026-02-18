# Deep Agent Harness

The harness is the set of built-in capabilities every deep agent gets automatically.

## Contents

- Built-in Tools
- Prompt Assembly Order
- Virtual Filesystem Structure
- Cast Module Mapping
- Key Differences from Cast (LangGraph)

## Built-in Tools

Every deep agent has access to these filesystem tools via the backend:

| Tool | Description |
|------|-------------|
| `ls` | List files in a directory with metadata (size, modified time) |
| `read_file` | Read file contents with line numbers, supports offset/limit. Also reads images as multimodal content |
| `write_file` | Create new files |
| `edit_file` | Perform exact string replacements (with global replace mode) |
| `glob` | Find files matching patterns (e.g., `**/*.py`) |
| `grep` | Search file contents with multiple output modes |
| `execute` | Run shell commands (**only available with sandbox backends**) |
| `write_todos` | Create and manage to-do lists for task planning |
| `task` | Delegate work to subagents |

## Prompt Assembly Order

The final deep agent prompt is assembled from these parts (in order):

1. **Custom `system_prompt`** (if provided)
2. **Base agent prompt** — core instructions for tool calling loop
3. **To-do list prompt** — instructions for planning with to-do lists
4. **Memory prompt** — AGENTS.md + memory usage guidelines (only when memory provided)
5. **Skills prompt** — skill locations + frontmatter list (only when skills provided)
6. **Virtual filesystem prompt** — filesystem + execute tool docs
7. **Subagent prompt** — task tool usage instructions
8. **Middleware prompts** — custom middleware system prompts
9. **HITL prompt** — interrupt instructions (when `interrupt_on` is set)

## Virtual Filesystem Structure

```
Deep Agent
    ├── /workspace/          # Working files (ephemeral by default)
    │   ├── plan.md          # Agent's task plan
    │   ├── notes.md         # Research notes
    │   └── output.py        # Generated code
    ├── /memories/           # Long-term storage (if CompositeBackend)
    │   └── preferences.md   # Persisted across threads
    └── /skills/             # Skill definitions (read-only)
        └── my-skill/
            └── SKILL.md
```

The filesystem backend determines where files actually live:

- **StateBackend**: In graph state (ephemeral, single thread)
- **FilesystemBackend**: On local disk
- **StoreBackend**: In LangGraph Store (persistent, cross-thread)
- **CompositeBackend**: Routes different paths to different backends
- **Sandbox backends**: Isolated environment with `execute` tool

## Cast Module Mapping

In an Act project, the harness capabilities map to cast modules:

```
Cast Module               → Harness Capability
──────────────────────    ──────────────────────
modules/tools.py          → Custom tools passed to create_deep_agent
modules/agents.py         → create_deep_agent assembly + subagent definitions
modules/prompts.py        → system_prompt content
modules/middlewares.py    → Middleware configuration
modules/utils.py          → Backend factory functions
modules/state.py          → Not needed (harness manages its own state)
modules/nodes.py          → Not needed (harness provides the agent loop)
```

## Key Differences from Cast (LangGraph)

| Aspect | Cast (LangGraph) | Deep Agent |
|--------|-------------------|------------|
| State | Custom TypedDict | Managed by harness |
| Nodes | Manual definition | Built-in agent loop |
| Edges | Manual routing | Automatic tool calling |
| Planning | Manual implementation | Built-in write_todos |
| Filesystem | Not included | Built-in with backends |
| Subagents | Manual subgraph wiring | Built-in task tool |
| Memory | Manual Store integration | Built-in CompositeBackend |
