# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

<!-- AUTO-MANAGED: project-description -->
## Overview

**Act Operator** is a production-ready CLI tool that scaffolds structured LangGraph 1.0+ projects ("Act" projects) with built-in AI collaboration capabilities.

Key features:
- Generate modular LangGraph project structures via `act new`
- Add new graph components ("Casts") via `act cast`
- Multi-language template support (English/Korean)
- Built-in Claude Code skills for architecture, development, and testing

<!-- END AUTO-MANAGED -->

<!-- AUTO-MANAGED: build-commands -->
## Build & Development Commands

```bash
# Install dependencies
uv sync

# Run CLI directly
uv run act new              # Create new Act project
uv run act cast             # Add Cast to existing project

# Run tests (ignores scaffold templates)
uv run pytest

# Lint and format
pre-commit run --all-files  # Run all pre-commit hooks
ruff check --fix            # Lint with auto-fix
ruff format                 # Format code

# Build package
uv build
```

<!-- END AUTO-MANAGED -->

<!-- AUTO-MANAGED: architecture -->
## Architecture

```
act-operator/
├── act_operator/                    # Package root (contains pyproject.toml)
│   ├── pyproject.toml              # Package config (hatchling build)
│   ├── uv.lock                     # Dependency lock file
│   └── act_operator/               # Source code
│       ├── __init__.py             # Version: __version__
│       ├── __main__.py             # Entry point
│       ├── cli.py                  # Typer CLI commands (new, cast)
│       ├── utils.py                # Name normalization, cookiecutter rendering
│       ├── version.py              # Version utilities
│       ├── scaffold/               # Cookiecutter template
│       │   ├── cookiecutter.json   # Template variables
│       │   └── {{ cookiecutter.act_slug }}/  # Template directory
│       │       ├── casts/          # Graph modules
│       │       ├── tests/          # Test structure
│       │       ├── .claude/skills/ # AI collaboration skills
│       │       └── ...
│       └── tests/                  # Unit & integration tests
├── .claude/skills/                 # CLI tool's own skills
├── .pre-commit-config.yaml         # Pre-commit hooks (ruff, uv-lock)
├── CONTRIBUTING.md                 # Contribution guide
└── README.md                       # Project documentation
```

**Data Flow:**
1. User runs `act new` → CLI prompts for act/cast names
2. `build_name_variants()` normalizes names (slug, snake, title, pascal)
3. `render_cookiecutter_template()` generates project from scaffold
4. Post-processing normalizes cast directories to snake_case

<!-- END AUTO-MANAGED -->

<!-- AUTO-MANAGED: conventions -->
## Code Conventions

- **Naming**: snake_case for functions/variables, PascalCase for classes
- **Type hints**: Required on all function signatures
- **Imports**: Sorted by ruff (isort rules), `from __future__ import annotations` first
- **Docstrings**: Google-style with Args/Returns/Raises sections
- **Private functions**: Prefixed with `_` (e.g., `_resolve_path`, `_validate_name`)
- **Constants**: UPPER_SNAKE_CASE at module level
- **Dataclasses**: Use `slots=True, frozen=True` for immutable data
- **Enums**: Use `str, Enum` base for string enums (e.g., `Language`)
- **Error handling**: Raise `typer.Exit(code=EXIT_CODE_ERROR)` for CLI errors

<!-- END AUTO-MANAGED -->

<!-- AUTO-MANAGED: patterns -->
## Detected Patterns

- **CLI Pattern**: Typer with callback for root command, subcommands via `@app.command()`
- **Name Normalization**: `NameVariants` dataclass holds slug/snake/title/pascal variants
- **Template Rendering**: Cookiecutter with post-processing for directory normalization
- **Validation**: Early validation with immediate user feedback via Rich console
- **Language Support**: `Language` enum with `from_string()` class method for flexible parsing
- **File Updates**: JSON/TOML manipulation for langgraph.json and pyproject.toml

<!-- END AUTO-MANAGED -->

<!-- AUTO-MANAGED: git-insights -->
## Git Insights

- **Main branch**: `main`
- **Commit style**: Conventional commits (fix:, feat:, chore:, etc.)
- **Pre-commit hooks**: uv-lock, ruff (lint + format)

<!-- END AUTO-MANAGED -->

<!-- AUTO-MANAGED: best-practices -->
## Best Practices

- Always run `uv sync` after modifying dependencies
- Run `pre-commit run --all-files` before committing
- Keep scaffold templates in sync with CLI logic changes
- Test CLI commands with both interactive and non-interactive modes
- Validate name inputs early to provide clear error messages

<!-- END AUTO-MANAGED -->

<!-- MANUAL -->
# Claude Code Configuration - Claude Flow V3

## Behavioral Rules (Always Enforced)

- Do what has been asked; nothing more, nothing less
- NEVER create files unless they're absolutely necessary for achieving your goal
- ALWAYS prefer editing an existing file to creating a new one
- NEVER proactively create documentation files (*.md) or README files unless explicitly requested
- NEVER save working files, text/mds, or tests to the root folder
- Never continuously check status after spawning a swarm — wait for results
- ALWAYS read a file before editing it
- NEVER commit secrets, credentials, or .env files

## File Organization

- NEVER save to root folder — use the directories below
- Use `/src` for source code files
- Use `/tests` for test files
- Use `/docs` for documentation and markdown files
- Use `/config` for configuration files
- Use `/scripts` for utility scripts
- Use `/examples` for example code

## Project Architecture

- Follow Domain-Driven Design with bounded contexts
- Keep files under 500 lines
- Use typed interfaces for all public APIs
- Prefer TDD London School (mock-first) for new code
- Use event sourcing for state changes
- Ensure input validation at system boundaries

### Project Config

- **Topology**: hierarchical-mesh
- **Max Agents**: 15
- **Memory**: hybrid
- **HNSW**: Enabled
- **Neural**: Enabled

## Build & Test

```bash
# Build
npm run build

# Test
npm test

# Lint
npm run lint
```

- ALWAYS run tests after making code changes
- ALWAYS verify build succeeds before committing

## Security Rules

- NEVER hardcode API keys, secrets, or credentials in source files
- NEVER commit .env files or any file containing secrets
- Always validate user input at system boundaries
- Always sanitize file paths to prevent directory traversal
- Run `npx @claude-flow/cli@latest security scan` after security-related changes

## Concurrency: 1 MESSAGE = ALL RELATED OPERATIONS

- All operations MUST be concurrent/parallel in a single message
- Use Claude Code's Task tool for spawning agents, not just MCP
- ALWAYS batch ALL todos in ONE TodoWrite call (5-10+ minimum)
- ALWAYS spawn ALL agents in ONE message with full instructions via Task tool
- ALWAYS batch ALL file reads/writes/edits in ONE message
- ALWAYS batch ALL Bash commands in ONE message

## Swarm Orchestration

- MUST initialize the swarm using CLI tools when starting complex tasks
- MUST spawn concurrent agents using Claude Code's Task tool
- Never use CLI tools alone for execution — Task tool agents do the actual work
- MUST call CLI tools AND Task tool in ONE message for complex work

### 3-Tier Model Routing (ADR-026)

| Tier | Handler | Latency | Cost | Use Cases |
|------|---------|---------|------|-----------|
| **1** | Agent Booster (WASM) | <1ms | $0 | Simple transforms (var→const, add types) — Skip LLM |
| **2** | Haiku | ~500ms | $0.0002 | Simple tasks, low complexity (<30%) |
| **3** | Sonnet/Opus | 2-5s | $0.003-0.015 | Complex reasoning, architecture, security (>30%) |

- Always check for `[AGENT_BOOSTER_AVAILABLE]` or `[TASK_MODEL_RECOMMENDATION]` before spawning agents
- Use Edit tool directly when `[AGENT_BOOSTER_AVAILABLE]`

## Swarm Configuration & Anti-Drift

- ALWAYS use hierarchical topology for coding swarms
- Keep maxAgents at 6-8 for tight coordination
- Use specialized strategy for clear role boundaries
- Use `raft` consensus for hive-mind (leader maintains authoritative state)
- Run frequent checkpoints via `post-task` hooks
- Keep shared memory namespace for all agents

```bash
npx @claude-flow/cli@latest swarm init --topology hierarchical --max-agents 8 --strategy specialized
```

## Swarm Execution Rules

- ALWAYS use `run_in_background: true` for all agent Task calls
- ALWAYS put ALL agent Task calls in ONE message for parallel execution
- After spawning, STOP — do NOT add more tool calls or check status
- Never poll TaskOutput or check swarm status — trust agents to return
- When agent results arrive, review ALL results before proceeding

## V3 CLI Commands

### Core Commands

| Command | Subcommands | Description |
|---------|-------------|-------------|
| `init` | 4 | Project initialization |
| `agent` | 8 | Agent lifecycle management |
| `swarm` | 6 | Multi-agent swarm coordination |
| `memory` | 11 | AgentDB memory with HNSW search |
| `task` | 6 | Task creation and lifecycle |
| `session` | 7 | Session state management |
| `hooks` | 17 | Self-learning hooks + 12 workers |
| `hive-mind` | 6 | Byzantine fault-tolerant consensus |

### Quick CLI Examples

```bash
npx @claude-flow/cli@latest init --wizard
npx @claude-flow/cli@latest agent spawn -t coder --name my-coder
npx @claude-flow/cli@latest swarm init --v3-mode
npx @claude-flow/cli@latest memory search --query "authentication patterns"
npx @claude-flow/cli@latest doctor --fix
```

## Available Agents (60+ Types)

### Core Development
`coder`, `reviewer`, `tester`, `planner`, `researcher`

### Specialized
`security-architect`, `security-auditor`, `memory-specialist`, `performance-engineer`

### Swarm Coordination
`hierarchical-coordinator`, `mesh-coordinator`, `adaptive-coordinator`

### GitHub & Repository
`pr-manager`, `code-review-swarm`, `issue-tracker`, `release-manager`

### SPARC Methodology
`sparc-coord`, `sparc-coder`, `specification`, `pseudocode`, `architecture`

## Memory Commands Reference

```bash
# Store (REQUIRED: --key, --value; OPTIONAL: --namespace, --ttl, --tags)
npx @claude-flow/cli@latest memory store --key "pattern-auth" --value "JWT with refresh" --namespace patterns

# Search (REQUIRED: --query; OPTIONAL: --namespace, --limit, --threshold)
npx @claude-flow/cli@latest memory search --query "authentication patterns"

# List (OPTIONAL: --namespace, --limit)
npx @claude-flow/cli@latest memory list --namespace patterns --limit 10

# Retrieve (REQUIRED: --key; OPTIONAL: --namespace)
npx @claude-flow/cli@latest memory retrieve --key "pattern-auth" --namespace patterns
```

## Quick Setup

```bash
claude mcp add claude-flow -- npx -y @claude-flow/cli@latest
npx @claude-flow/cli@latest daemon start
npx @claude-flow/cli@latest doctor --fix
```

## Claude Code vs CLI Tools

- Claude Code's Task tool handles ALL execution: agents, file ops, code generation, git
- CLI tools handle coordination via Bash: swarm init, memory, hooks, routing
- NEVER use CLI tools as a substitute for Task tool agents

## Support

- Documentation: https://github.com/ruvnet/claude-flow
- Issues: https://github.com/ruvnet/claude-flow/issues

<!-- END MANUAL -->
