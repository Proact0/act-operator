# AGENTS.md

This file provides comprehensive guidance to AI coding assistants and human developers working in the **act-operator** repository.

---

## 1. Project Overview & Philosophy

**Act Operator** (`act-operator`) is a production-ready CLI scaffolding tool for bootstrapping modular, enterprise-grade LangGraph 1.0+ projects ("Act" projects) with built-in AI collaboration capabilities (Agent Skills, Executable SSOT, Harness Pattern).

### 1.1 Core Concepts
- **Harness Pattern**: A structured environment consisting of scaffolding, executable knowledge, and feedback loops that guide both humans and AI agents to produce consistent, reliable code across sessions.
- **Context Gap Resolution**: Eliminates the variance between different users/agents by encoding architectural conventions, explicit module boundaries, and persistent memory directly into the codebase.
- **Act vs. Cast**:
  - **Act**: The top-level harness instance / LangGraph monorepo project repository.
  - **Cast**: A discrete graph unit within an Act (one `StateGraph` = one Cast). An Act can host multiple Casts as independent, composable packages.

### 1.2 CLI Capabilities
- `act new`: Bootstraps a complete Act project structure from cookiecutter templates.
- `act cast`: Scaffolds a new Cast (StateGraph module) into an existing Act project.
- `act upgrade`: Upgrades `.claude/skills/` and agent assets in an existing Act project to the latest version.
- **Multi-language**: Supports both English (`en`) and Korean (`kr`) scaffolding blueprints.

---

## 2. Repository Architecture & Layout

```
act-operator/
├── .agent/                         # Agent workflows and slash command specs
│   └── workflows/                  # e.g., notebooklm-slide.md
├── .github/                        # GitHub Actions CI/CD workflows and assets
│   ├── workflows/                  # CI, release, and linting pipelines
│   └── images/                     # Documentation diagrams and badges
├── .pre-commit-config.yaml         # Pre-commit hook definitions (ruff, uv-lock)
├── CONTRIBUTING.md                 # Contribution guide (English)
├── CONTRIBUTING_KR.md              # Contribution guide (Korean)
├── README.md                       # Main documentation (English)
├── README_KR.md                    # Main documentation (Korean)
├── CLAUDE.md                       # Claude Code guidance & agent configuration
├── AGENTS.md                       # AI Agent & Assistant reference (this file)
├── study/                          # 8-week curriculum guides and slide decks
└── act_operator/                   # Python Package Root
    ├── pyproject.toml              # Project dependencies & build config (Hatchling)
    ├── uv.lock                     # UV dependency lockfile
    └── act_operator/               # Core Python Package
        ├── __init__.py             # Version definition (__version__)
        ├── __main__.py             # CLI execution entry point
        ├── cli.py                  # Typer CLI application & command definitions
        ├── cli_options.py          # Reusable Typer options and arguments
        ├── cli_prompts.py          # Interactive Rich/Typer prompt handlers
        ├── project_scaffolder.py   # 'act new' orchestration logic
        ├── cast_scaffolder.py      # 'act cast' orchestration logic
        ├── upgrade_scaffolder.py   # 'act upgrade' logic for project skills
        ├── utils.py                # Name normalization, cookiecutter rendering, file I/O
        ├── version.py              # CLI & project version utilities
        ├── scaffold/               # Cookiecutter project blueprint templates
        │   ├── cookiecutter.json   # Template variables
        │   └── {{ cookiecutter.act_slug }}/ # Scaffolding directory tree
        │       ├── casts/          # Cast modules directory
        │       │   └── {{ cookiecutter.cast_snake }}/ # Initial Cast module
        │       │       ├── modules/        # Graph components (nodes, state, tools, middlewares)
        │       │       ├── graph.py        # StateGraph definition & entrypoint
        │       │       ├── README.md       # Cast-level documentation
        │       │       └── pyproject.toml  # Cast-level package metadata
        │       ├── tests/          # Act project test suite template
        │       ├── .claude/skills/ # Agent skills bundled in new projects
        │       │   ├── architecting-act/
        │       │   ├── developing-cast/
        │       │   ├── engineering-act/
        │       │   ├── testing-cast/
        │       │   └── publishing-act/
        │       ├── langgraph.json  # LangGraph studio / server configuration
        │       └── pyproject.toml  # Scaffolding root project config
        └── tests/                  # Act Operator internal test suite
            ├── unit/               # Unit tests
            └── integration/        # CLI & scaffolding integration tests
```

---

## 3. Bundled Agent Skills in Scaffolding

When `act new` generates a project, it bundles the following Claude / AI Agent skills into `.claude/skills/`:

| Skill | Role | Key Capabilities |
|---|---|---|
| **`architecting-act`** | Requirements & Topology Design | 20-Questions interview process, State schema drafting, CLAUDE.md spec synchronization |
| **`developing-cast`** | Graph Implementation | LangChain v1 `create_agent` patterns, node implementation, tools, and middleware integration |
| **`engineering-act`** | Operations & Monorepo Mgmt | Multi-cast dependency resolution, `langgraph.json` registration, sub-graph linking |
| **`testing-cast`** | Test Generation & Quality | Unit test generation, checkpointer mocking, State validation, pytest test suite setup |
| **`publishing-act`** | Deployment & Packaging | LangGraph Cloud readiness, Docker packaging, PyPI distribution |

---

## 4. Technology Stack

- **Runtime**: Python `>=3.11`
- **Package & Dependency Manager**: [`uv`](https://github.com/astral-sh/uv)
- **Build Backend**: `hatchling`
- **CLI Framework**: [`typer`](https://typer.tiangolo.com/) (`>=0.19.2`)
- **Terminal UI & Styling**: [`rich`](https://rich.readthedocs.io/) (`>=14.1.0`)
- **Project Templating**: [`cookiecutter`](https://cookiecutter.readthedocs.io/) (`>=2.6.0`)
- **Testing**: `pytest`, `pytest-cov`, `pytest-mock`, `pytest-subprocess`
- **Linting & Formatting**: `ruff`, `mypy`, `pre-commit`

---

## 5. Development & Build Commands

All development commands should be executed with `uv` inside the repository:

```bash
# 1. Install dependencies & synchronize environment
uv sync

# 2. Run CLI locally in development mode
uv run act --help
uv run act new --path ./my-act --act-name "My Act" --cast-name "My Cast" --lang en
uv run act cast --act-path ./my-act --cast-name "Second Cast" --lang en
uv run act upgrade --act-path ./my-act

# 3. Run test suite
uv run pytest
# Run specific test file
uv run pytest act_operator/act_operator/tests/integration/test_cli.py

# 4. Code Formatting & Linting
ruff check --fix            # Lint and apply automatic fixes
ruff format                 # Format codebase
pre-commit run --all-files  # Run all pre-commit hooks

# 5. Build Distribution Packages (Wheel & sdist)
uv build
```

---

## 6. Coding Standards & Conventions

### 6.1 Python Language Rules
- **Type Annotations**: All function signatures must include comprehensive type annotations.
- **Future Imports**: Always place `from __future__ import annotations` at the top of Python files.
- **Docstrings**: Use Google-style docstrings (`Args:`, `Returns:`, `Raises:`).
- **Naming Conventions**:
  - Modules & Functions: `snake_case`
  - Classes & Enums: `PascalCase`
  - Constants: `UPPER_SNAKE_CASE`
  - Private Helpers: Prefix with single underscore `_function_name`
- **Data Modeling**:
  - Use `@dataclass(slots=True, frozen=True)` for immutable data transfer structures (e.g., `NameVariants`).
  - Use `(str, Enum)` inheritance for string enumerations (e.g., `Language`).
- **Error Handling**:
  - Raise `ValueError` or custom domain errors with descriptive messages in utility and scaffolder layers.
  - In CLI command handlers, catch expected exceptions and exit cleanly using `raise typer.Exit(code=...)` with clear Rich console error messages.

### 6.2 Scaffolding & Jinja2 Template Rules
- The `act_operator/act_operator/scaffold/` directory contains Jinja2-templated files used by `cookiecutter`.
- **Do not** apply linting or formatting directly to `scaffold/` (configured as ignored in `ruff` and `pytest`).
- When modifying scaffold templates, ensure variable placeholders match `cookiecutter.json` (e.g., `{{ cookiecutter.act_slug }}`, `{{ cookiecutter.cast_snake }}`).

---

## 7. Key Subsystems & Design Patterns

### 7.1 Name Normalization (`NameVariants`)
Input names for Acts and Casts are normalized into four canonical representations using `build_name_variants(raw_name)` in `utils.py`:
- `slug`: kebab-case (e.g., `my-workflow`)
- `snake`: snake_case (e.g., `my_workflow`)
- `title`: Title Case with spaces (e.g., `My Workflow`)
- `pascal`: PascalCase (e.g., `MyWorkflow`)

### 7.2 Scaffolding Flow
1. **CLI Prompt / Arguments**: Parse CLI options or prompt interactively via `rich.prompt`.
2. **Validation**: Check directory existence, project boundaries (`ensure_act_project`), and name syntax.
3. **Cookiecutter Rendering**: Render blueprint into a temporary directory or directly into target location.
4. **Post-Processing**: Normalize directories to snake_case and update configuration files (`langgraph.json`, `pyproject.toml`).

### 7.3 Multi-Language Template Selection
- `Language.ENGLISH` (`en`) / `Language.KOREAN` (`kr`)
- Template copy and translation mappings are handled cleanly through language parameters passed to cookiecutter context.

---

## 8. Instructions for AI Agents

When assisting with this codebase, AI agents must adhere to the following rules:

1. **Precision & Scope**: Focus directly on the user's objective without making unauthorized or out-of-scope modifications.
2. **File Preservation**: Always inspect and understand an existing file before making edits. Prefer editing over creating redundant files.
3. **Scaffold Integrity**: Be cautious when editing files within `act_operator/act_operator/scaffold/`. Test project generation after making any template changes.
4. **Verification**: Run `uv run pytest` and `ruff check` after any code modifications to guarantee stability.
5. **Security & Secrets**: Never add hardcoded credentials, API keys, or personal tokens to the codebase.
6. **No Poll Loops**: Do not poll tasks in loops. Leverage reactive wakeups.

