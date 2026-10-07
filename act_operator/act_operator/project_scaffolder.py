"""Project scaffolding helpers for the Act Operator CLI."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.table import Table

from .cli_prompts import resolve_cast_name, resolve_language, resolve_name, resolve_path
from .utils import (
    CASTS_DIR,
    LANGGRAPH_FILE,
    PYPROJECT_FILE,
    Language,
    NameVariants,
    build_name_variants,
    render_cookiecutter_template,
    select_drawkit_by_language,
)

EXIT_CODE_ERROR = 1
SCAFFOLD_DIR = "scaffold"
ENCODING_UTF8 = "utf-8"

console = Console()


def determine_target_directory(
    base_dir: Path, path_was_custom: bool, act_slug: str
) -> Path:
    """Determine the target directory for the new Act project.

    Args:
        base_dir: Base directory from user input.
        path_was_custom: Whether user specified a custom path.
        act_slug: Hyphenated slug version of Act name.

    Returns:
        Target directory path for the project.
    """
    if not path_was_custom:
        return Path.cwd()

    if base_dir != Path.cwd():
        return base_dir.parent / act_slug
    return Path.cwd() / act_slug


def validate_and_create_directory(target_dir: Path) -> None:
    """Validate and create target directory.

    Args:
        target_dir: Directory to create.

    Raises:
        typer.Exit: If directory exists and is not empty, or creation fails.
    """
    if target_dir.exists() and any(target_dir.iterdir()):
        console.print(
            "❌ The specified directory already exists and is not empty. "
            "Aborting to prevent overwriting files.",
            style="red",
        )
        raise typer.Exit(code=EXIT_CODE_ERROR)

    try:
        target_dir.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        console.print(f"[red]Unable to create target directory: {error}[/red]")
        raise typer.Exit(code=EXIT_CODE_ERROR) from error


def get_scaffold_root() -> Path:
    """Get the scaffold directory path.

    Returns:
        Path to scaffold directory.

    Raises:
        typer.Exit: If scaffold resources not found.
    """
    scaffold_root = Path(__file__).resolve().parent / SCAFFOLD_DIR
    if not scaffold_root.exists():
        console.print("[red]Scaffold resources not found.[/red]")
        raise typer.Exit(code=EXIT_CODE_ERROR)
    return scaffold_root


def build_template_context(
    act: NameVariants,
    cast: NameVariants,
    language: str,
    rag: bool = False,
    template: str = "default",
    vector_db: str = "chroma",
) -> dict[str, Any]:
    """Build the template context for cookiecutter.

    Args:
        act: Act name variants.
        cast: Cast name variants.
        language: Language display name.
        rag: Whether to scaffold with RAG pipeline.
        template: Template type (default|rag).
        vector_db: Vector DB engine (chroma|pgvector|inmemory).

    Returns:
        Dictionary of template context variables.
    """
    return {
        "act_name": act.title,
        "act_slug": act.slug,
        "act_snake": act.snake,
        "cast_name": cast.title,
        "cast_slug": cast.slug,
        "cast_snake": cast.snake,
        "cast_pascal": cast.pascal,
        "language": language,
        "rag": rag,
        "cast_template": template,
        "vector_db": vector_db,
    }


def normalize_cast_directory(target_dir: Path, cast: NameVariants) -> None:
    """Normalize cast directory from hyphenated to snake_case if needed.

    Args:
        target_dir: Root directory of the Act project.
        cast: Cast name variants.

    Raises:
        typer.Exit: If normalization fails.
    """
    casts_dir = target_dir / CASTS_DIR
    old_cast_dir = casts_dir / cast.slug
    new_cast_dir = casts_dir / cast.snake

    if not (old_cast_dir.exists() and not new_cast_dir.exists()):
        return

    try:
        old_cast_dir.rename(new_cast_dir)

        project_pyproject = target_dir / PYPROJECT_FILE
        if project_pyproject.exists():
            content = project_pyproject.read_text(encoding=ENCODING_UTF8)
            content = content.replace(
                f"{CASTS_DIR}/{cast.slug}", f"{CASTS_DIR}/{cast.snake}"
            )
            project_pyproject.write_text(content, encoding=ENCODING_UTF8)

        project_langgraph = target_dir / LANGGRAPH_FILE
        if project_langgraph.exists():
            langgraph_content = project_langgraph.read_text(encoding=ENCODING_UTF8)
            langgraph_content = langgraph_content.replace(
                f'"{cast.slug}"', f'"{cast.snake}"'
            )
            langgraph_content = langgraph_content.replace(
                f"/{CASTS_DIR}/{cast.slug}/",
                f"/{CASTS_DIR}/{cast.snake}/",
            )
            project_langgraph.write_text(langgraph_content, encoding=ENCODING_UTF8)
    except OSError as error:
        console.print(f"[red]Failed to normalize cast directory: {error}[/red]")
        raise typer.Exit(code=EXIT_CODE_ERROR) from error


def display_project_summary(
    act_title: str, cast_title: str, language: str, target_dir: Path
) -> None:
    """Display project creation summary table.

    Args:
        act_title: Act name in title case.
        cast_title: Cast name in title case.
        language: Language code ("en" or "kr").
        target_dir: Project directory path.
    """
    lang_display = Language.from_string(language).display_name
    table = Table(show_header=False)
    table.add_row("Act", act_title)
    table.add_row("Cast", cast_title)
    table.add_row("Language", lang_display)
    table.add_row("Location", str(target_dir))
    console.print(table)
    console.print("[bold green]Act project created successfully![/bold green]")

    try:
        if target_dir.exists():
            entries = ", ".join(sorted(path.name for path in target_dir.iterdir()))
            console.print(f"[dim]act project entries: {entries}[/dim]")
    except Exception:
        pass


def generate_project(
    *,
    path: Path | None,
    act_name: str | None,
    cast_name: str | None,
    language: str | None,
    rag: bool = False,
    template: str = "default",
    vector_db: str = "chroma",
) -> None:
    """Generate a new Act project with initial Cast.

    Args:
        path: Optional path for project creation.
        act_name: Optional Act name.
        cast_name: Optional Cast name.
        language: Optional language code.
        rag: Whether to scaffold with RAG pipeline.
        template: Template type (default|rag).
        vector_db: Vector DB engine (chroma|pgvector|inmemory).

    Raises:
        typer.Exit: If project creation fails.
    """
    base_dir, path_was_custom = resolve_path(path)

    if not path_was_custom and Path.cwd().exists() and any(Path.cwd().iterdir()):
        console.print(
            "❌ The current directory is not empty. "
            "Please use an empty directory to create a new Act.",
            style="red",
        )
        raise typer.Exit(code=EXIT_CODE_ERROR)

    if act_name is None and path_was_custom:
        act_name = base_dir.name or base_dir.resolve().name

    act_raw = resolve_name("🚀 Please enter a name for the new Act", act_name)
    act = build_name_variants(act_raw)

    cast_raw = resolve_cast_name(
        "🌟 Please enter a name for the first Cast(Graph/Workflow/Pipeline/etc.)",
        cast_name,
        act.snake,
        act.title,
    )
    cast = build_name_variants(cast_raw)

    lang = resolve_language(language)

    target_dir = determine_target_directory(base_dir, path_was_custom, act.slug)
    validate_and_create_directory(target_dir)
    scaffold_root = get_scaffold_root()

    console.print("[bold green]Starting Act project scaffolding...[/bold green]")

    context = build_template_context(
        act, cast, lang, rag=rag, template=template, vector_db=vector_db
    )
    try:
        render_cookiecutter_template(scaffold_root, target_dir, context)
    except FileExistsError as error:
        console.print(f"[red]{error}[/red]")
        raise typer.Exit(code=EXIT_CODE_ERROR) from error

    normalize_cast_directory(target_dir, cast)

    try:
        select_drawkit_by_language(target_dir, lang)
    except FileNotFoundError as error:
        console.print(f"[yellow]Warning: {error}[/yellow]")
    except OSError as error:
        console.print(f"[red]Failed to process drawkit file: {error}[/red]")
        raise typer.Exit(code=EXIT_CODE_ERROR) from error

    display_project_summary(act.title, cast.title, lang, target_dir)
