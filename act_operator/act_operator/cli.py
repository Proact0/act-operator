"""Act Operator CLI entrypoints for managing Act projects and Casts."""

from __future__ import annotations

from pathlib import Path

import typer

from .cast_scaffolder import ensure_act_project, generate_cast_project
from .cli_options import (
    ACT_NAME_OPTION,
    CAST_ACT_PATH_OPTION,
    CAST_NAME_OPTION,
    LANG_OPTION,
    NEW_CAST_LANG_OPTION,
    NEW_CAST_NAME_OPTION,
    NEW_CAST_RAG_OPTION,
    NEW_CAST_TEMPLATE_OPTION,
    NEW_CAST_VECTOR_DB_OPTION,
    PATH_OPTION,
    RAG_OPTION,
    TEMPLATE_OPTION,
    VECTOR_DB_OPTION,
)
from .cli_prompts import resolve_cast_name
from .project_scaffolder import generate_project
from .upgrade_scaffolder import upgrade_skills_project
from .utils import build_name_variants

app = typer.Typer(help="Act Operator", invoke_without_command=True)


@app.callback()
def root(
    ctx: typer.Context,
    path: Path | None = PATH_OPTION,
    act_name: str | None = ACT_NAME_OPTION,
    cast_name: str | None = CAST_NAME_OPTION,
    lang: str | None = LANG_OPTION,
    rag: bool = RAG_OPTION,
    template: str = TEMPLATE_OPTION,
    vector_db: str = VECTOR_DB_OPTION,
) -> None:
    """Act Operator root command callback.

    Args:
        ctx: Typer context for command invocation.
        path: Optional path for project creation.
        act_name: Optional Act name.
        cast_name: Optional Cast name.
        lang: Optional language code.
        rag: Whether to scaffold with RAG pipeline.
        template: Template type (default|rag).
        vector_db: Vector DB engine (chroma|pgvector|inmemory).
    """
    is_rag = rag or (template.lower() == "rag")
    ctx.obj = {
        "path": path,
        "act_name": act_name,
        "cast_name": cast_name,
        "lang": lang,
        "rag": is_rag,
        "template": template,
        "vector_db": vector_db,
    }
    if ctx.invoked_subcommand is not None:
        return
    generate_project(
        path=path,
        act_name=act_name,
        cast_name=cast_name,
        language=lang,
        rag=is_rag,
        template=template,
        vector_db=vector_db,
    )


@app.command("new")
def new_command(
    ctx: typer.Context,
    path: Path | None = PATH_OPTION,
    act_name: str | None = ACT_NAME_OPTION,
    cast_name: str | None = CAST_NAME_OPTION,
    lang: str | None = LANG_OPTION,
    rag: bool = RAG_OPTION,
    template: str = TEMPLATE_OPTION,
    vector_db: str = VECTOR_DB_OPTION,
) -> None:
    """Create a new Act project (explicit command).

    Args:
        ctx: Typer context for command invocation.
        path: Optional path for project creation.
        act_name: Optional Act name.
        cast_name: Optional Cast name.
        lang: Optional language code.
        rag: Whether to scaffold with RAG pipeline.
        template: Template type (default|rag).
        vector_db: Vector DB engine (chroma|pgvector|inmemory).
    """
    parent = ctx.parent.obj if ctx.parent and ctx.parent.obj else {}
    path = path or parent.get("path")
    act_name = act_name or parent.get("act_name")
    cast_name = cast_name or parent.get("cast_name")
    lang = lang or parent.get("lang")
    template_val = (
        template if template != "default" else parent.get("template", "default")
    )
    is_rag = rag or (template_val.lower() == "rag") or parent.get("rag", False)
    vector_db_val = (
        vector_db if vector_db != "chroma" else parent.get("vector_db", "chroma")
    )
    generate_project(
        path=path,
        act_name=act_name,
        cast_name=cast_name,
        language=lang,
        rag=is_rag,
        template=template_val,
        vector_db=vector_db_val,
    )


@app.command("cast")
def cast_command(
    act_path: Path = CAST_ACT_PATH_OPTION,
    cast_name: str | None = NEW_CAST_NAME_OPTION,
    lang: str = NEW_CAST_LANG_OPTION,
    rag: bool = NEW_CAST_RAG_OPTION,
    template: str = NEW_CAST_TEMPLATE_OPTION,
    vector_db: str = NEW_CAST_VECTOR_DB_OPTION,
) -> None:
    """Add a new Cast to an existing Act project.

    Args:
        act_path: Path to the existing Act project.
        cast_name: Optional Cast name.
        lang: Language code for the Cast.
        rag: Whether to scaffold a RAG-enabled Cast.
        template: Template type (default|rag).
        vector_db: Vector DB engine (chroma|pgvector|inmemory).
    """
    act_path = act_path.resolve()
    ensure_act_project(act_path)

    act_variants = build_name_variants(act_path.name)
    cast_raw = resolve_cast_name(
        "🌟 Please enter a name for the new Cast",
        cast_name,
        act_variants.snake,
        act_variants.title,
    )
    is_rag = rag or (template.lower() == "rag")
    generate_cast_project(
        act_path=act_path,
        cast_name=cast_raw,
        language=lang,
        rag=is_rag,
        template=template,
        vector_db=vector_db,
    )


@app.command("upgrade")
def upgrade_command(
    act_path: Path = CAST_ACT_PATH_OPTION,
) -> None:
    """Upgrade .claude/skills/ in an existing Act project to the latest version.

    Args:
        act_path: Path to the existing Act project.
    """
    upgrade_skills_project(act_path)


def main() -> None:
    """Entry point for the Act Operator CLI."""
    app()
