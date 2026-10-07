"""Cast scaffolding helpers for the Act Operator CLI."""

from __future__ import annotations

import shutil
from pathlib import Path

import typer
from rich.console import Console

from .cli_prompts import normalize_lang
from .project_scaffolder import get_scaffold_root
from .utils import (
    CASTS_DIR,
    LANGGRAPH_FILE,
    PYPROJECT_FILE,
    build_name_variants,
    render_cookiecutter_cast_subproject,
    update_langgraph_registry,
)

EXIT_CODE_ERROR = 1
BASE_NODE_FILE = "base_node.py"
BASE_GRAPH_FILE = "base_graph.py"

console = Console()


def ensure_act_project(act_path: Path) -> None:
    """Validate that the path is a valid Act project.

    Args:
        act_path: Path to validate.

    Raises:
        typer.Exit: If path is not a valid Act project.
    """
    expected = [
        act_path / PYPROJECT_FILE,
        act_path / LANGGRAPH_FILE,
        act_path / CASTS_DIR,
        act_path / CASTS_DIR / BASE_NODE_FILE,
        act_path / CASTS_DIR / BASE_GRAPH_FILE,
    ]
    for path in expected:
        if not path.exists():
            console.print(
                f"[red]The path does not look like a valid Act project: {path}[/red]"
            )
            raise typer.Exit(code=EXIT_CODE_ERROR)


def validate_cast_directory(target_dir: Path) -> None:
    """Validate that cast directory doesn't exist or is empty.

    Args:
        target_dir: Cast directory to validate.

    Raises:
        typer.Exit: If directory exists and is not empty.
    """
    if target_dir.exists() and any(target_dir.iterdir()):
        console.print(
            "❌ The specified cast directory already exists and is not empty. "
            "Aborting to prevent overwriting files.",
            style="red",
        )
        raise typer.Exit(code=EXIT_CODE_ERROR)


def _copy_cast_test(rendered_root: Path, act_path: Path, cast_snake: str) -> None:
    """Copy rendered cast test into the project tests directory."""
    template_test = rendered_root / "tests" / "cast_tests" / f"{cast_snake}_test.py"
    if not template_test.exists():
        console.print(
            "[red]Generated cast test template not found. Aborting cast creation.[/red]"
        )
        raise typer.Exit(code=EXIT_CODE_ERROR)

    dest_dir = act_path / "tests" / "cast_tests"
    dest_dir.mkdir(parents=True, exist_ok=True)
    destination = dest_dir / template_test.name

    if destination.exists():
        console.print(
            f"[red]Cast test '{destination.name}' already exists. "
            "Remove it or rename before creating a new cast.[/red]"
        )
        raise typer.Exit(code=EXIT_CODE_ERROR)

    shutil.copy2(template_test, destination)
    console.print(
        f"[green]Cast test '{destination.name}' created in tests/cast_tests.[/green]"
    )


def generate_cast_project(
    *,
    act_path: Path,
    cast_name: str,
    language: str,
    rag: bool = False,
    template: str = "default",
    vector_db: str = "chroma",
) -> None:
    """Generate a new Cast within an existing Act project.

    Args:
        act_path: Path to the Act project.
        cast_name: Name of the new Cast.
        language: Language code for the Cast.
        rag: Whether to scaffold a RAG-enabled Cast.
        template: Template type (default|rag).
        vector_db: Vector DB engine (chroma|pgvector|inmemory).

    Raises:
        typer.Exit: If Cast creation fails.
    """
    act_variants = build_name_variants(act_path.name)
    cast_variants = build_name_variants(cast_name)

    casts_dir = act_path / CASTS_DIR
    target_dir = casts_dir / cast_variants.snake

    validate_cast_directory(target_dir)

    scaffold_root = get_scaffold_root()

    render_cookiecutter_cast_subproject(
        scaffold_root,
        target_dir,
        {
            "act_name": act_variants.title,
            "act_slug": act_variants.slug,
            "act_snake": act_variants.snake,
            "cast_name": cast_variants.title,
            "cast_slug": cast_variants.slug,
            "cast_snake": cast_variants.snake,
            "cast_pascal": cast_variants.pascal,
            "language": normalize_lang(language),
            "rag": rag,
            "cast_template": template,
            "vector_db": vector_db,
        },
        post_process=lambda rendered_root: _copy_cast_test(
            rendered_root, act_path, cast_variants.snake
        ),
    )

    try:
        update_langgraph_registry(
            act_path / LANGGRAPH_FILE,
            cast_variants.slug,
            cast_variants.snake,
        )
    except RuntimeError as error:
        console.print(f"[red]Failed to update langgraph.json: {error}[/red]")
        raise typer.Exit(code=EXIT_CODE_ERROR) from error

    if rag:
        console.print(
            f"[bold cyan]🔍 RAG pipeline configured for '{cast_variants.snake}' (Backend: {vector_db})[/bold cyan]"
        )

    console.print(
        f"[bold green]Cast '{cast_variants.snake}' added successfully![/bold green]"
    )
