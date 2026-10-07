from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from typer.testing import CliRunner

from act_operator.cli import app

runner = CliRunner()


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(_read(path))


def _create_project(tmp_path: Path, *, lang: str = "en") -> Path:
    """Create a reusable baseline Act project for cast-related integration tests."""
    # Given a temporary workspace for integration testing
    target_dir = tmp_path / "sample-act"

    # When a baseline Act project is scaffolded for reuse
    result = runner.invoke(
        app,
        [
            "--path",
            str(target_dir),
            "--act-name",
            "Sample Act",
            "--cast-name",
            "Primary Cast",
            "--lang",
            lang,
        ],
    )

    # Then the setup command should succeed before the test continues
    assert result.exit_code == 0, result.stdout
    return target_dir


def test_init_creates_scaffold(tmp_path: Path) -> None:
    """Test that the root CLI invocation creates the initial Act scaffold."""
    # Given root CLI arguments for a new Act project
    target_dir = _create_project(tmp_path)

    # When the scaffold is created through the root command
    project_pyproject = target_dir / "pyproject.toml"
    cast_readme = target_dir / "casts" / "primary_cast" / "README.md"

    # Then the project files and initial Cast README should exist
    assert project_pyproject.exists()
    assert cast_readme.exists()
    assert "Sample Act" in _read(project_pyproject)
    assert "Primary Cast" in _read(cast_readme)


def test_new_command_creates_scaffold(tmp_path: Path) -> None:
    """Test that the explicit `new` subcommand matches root command behavior."""
    # Given explicit `new` subcommand arguments for a new Act project
    target_dir = tmp_path / "sample-act"

    # When the `new` command is executed
    result = runner.invoke(
        app,
        [
            "new",
            "--path",
            str(target_dir),
            "--act-name",
            "Sample Act",
            "--cast-name",
            "Primary Cast",
            "--lang",
            "en",
        ],
    )

    # Then it should produce the same core scaffold as the root command
    assert result.exit_code == 0, result.stdout
    assert (target_dir / "pyproject.toml").exists()
    assert (target_dir / "casts" / "primary_cast" / "README.md").exists()


def test_init_derives_act_name_from_path(tmp_path: Path) -> None:
    """Test that the Act name is derived from the target path when omitted."""
    # Given a target path but no explicit Act name
    target_dir = tmp_path / "custom-act"

    # When project creation runs
    result = runner.invoke(
        app,
        [
            "--path",
            str(target_dir),
            "--cast-name",
            "Primary Cast",
            "--lang",
            "en",
        ],
    )
    assert result.exit_code == 0, result.stdout

    # Then the project metadata should derive the Act name from the path
    project_pyproject = target_dir / "pyproject.toml"
    assert "custom-act" in _read(project_pyproject)


def test_upgrade_replaces_skills(tmp_path: Path) -> None:
    """Test that `act upgrade` restores scaffolded skills after local corruption."""
    # Given a valid Act project with a corrupted skill file
    target_dir = _create_project(tmp_path)
    skill_file = target_dir / ".claude" / "skills" / "testing-cast" / "SKILL.md"
    assert skill_file.exists()

    original = _read(skill_file)
    skill_file.write_text("corrupted content", encoding="utf-8")
    assert _read(skill_file) == "corrupted content"

    # When the upgrade command is executed
    result = runner.invoke(app, ["upgrade", "--path", str(target_dir)])
    combined = (result.stdout or "") + (result.stderr or "")

    # Then the original scaffold content should be restored
    assert result.exit_code == 0, combined
    assert "upgraded successfully" in combined
    assert _read(skill_file) == original


def test_upgrade_creates_backup(tmp_path: Path) -> None:
    """Test that `act upgrade` creates a backup of the existing skills directory."""
    # Given a valid Act project with scaffolded skills
    target_dir = _create_project(tmp_path)
    skills_dir = target_dir / ".claude" / "skills"
    assert skills_dir.exists()

    # When the upgrade command is executed
    result = runner.invoke(app, ["upgrade", "--path", str(target_dir)])

    # Then the previous skills should exist in .claude/skills.bak
    assert result.exit_code == 0, result.stdout

    backup_dir = target_dir / ".claude" / "skills.bak"
    assert backup_dir.exists()
    assert (backup_dir / "testing-cast").exists()


def test_upgrade_fails_on_invalid_project(tmp_path: Path) -> None:
    """Test that `act upgrade` fails for paths that are not valid Act projects."""
    # Given a directory that is not an Act project
    invalid_dir = tmp_path / "not-a-project"
    invalid_dir.mkdir()

    # When the upgrade command is executed against that path
    result = runner.invoke(app, ["upgrade", "--path", str(invalid_dir)])

    # Then the command should fail
    assert result.exit_code != 0


def test_upgrade_detects_korean_language_from_readme(tmp_path: Path) -> None:
    """Test that `act upgrade` reports Korean when the project README is Korean."""
    # Given a Korean-language Act project
    target_dir = _create_project(tmp_path, lang="kr")

    # When the upgrade command is executed
    result = runner.invoke(app, ["upgrade", "--path", str(target_dir)])
    combined = (result.stdout or "") + (result.stderr or "")

    # Then the upgrade summary should report the detected Korean language
    assert result.exit_code == 0, combined
    assert "한국어" in combined


def test_upgrade_replaces_existing_backup_directory(tmp_path: Path) -> None:
    """Test that `act upgrade` replaces an existing skills backup with a fresh one."""
    # Given a valid Act project and an existing stale backup directory
    target_dir = _create_project(tmp_path)
    backup_dir = target_dir / ".claude" / "skills.bak"
    backup_dir.mkdir(parents=True)
    stale_file = backup_dir / "stale.txt"
    stale_file.write_text("old backup", encoding="utf-8")

    # When the upgrade command is executed
    result = runner.invoke(app, ["upgrade", "--path", str(target_dir)])

    # Then the stale backup should be replaced by the new backup contents
    assert result.exit_code == 0, result.stdout
    assert backup_dir.exists()
    assert not stale_file.exists()
    assert (backup_dir / "testing-cast").exists()


def test_upgrade_succeeds_with_malformed_langgraph(tmp_path: Path) -> None:
    """Test that `act upgrade` falls back safely when langgraph.json is malformed."""
    # Given a valid Act project with an invalid langgraph.json file
    target_dir = _create_project(tmp_path)
    langgraph_file = target_dir / "langgraph.json"
    langgraph_file.write_text("{ invalid json", encoding="utf-8")

    # When the upgrade command is executed
    result = runner.invoke(app, ["upgrade", "--path", str(target_dir)])
    combined = (result.stdout or "") + (result.stderr or "")

    # Then the upgrade should still succeed using the fallback cast context
    assert result.exit_code == 0, combined
    assert "upgraded successfully" in combined
    assert (target_dir / ".claude" / "skills").exists()


def test_init_aborts_on_non_empty_dir(tmp_path: Path) -> None:
    """Test that project creation aborts when the target directory is not empty."""
    # Given a target directory that already contains files
    target_dir = tmp_path / "existing"
    target_dir.mkdir()
    (target_dir / "existing.txt").write_text("data", encoding="utf-8")

    # When project creation is attempted
    result = runner.invoke(
        app,
        [
            "--path",
            str(target_dir),
            "--cast-name",
            "Primary Cast",
            "--lang",
            "en",
        ],
    )

    # Then the command should abort instead of overwriting existing content
    assert result.exit_code != 0
    combined_output = (result.stdout or "") + (result.stderr or "")
    assert "The specified directory already exists and is not empty" in combined_output


def test_new_rejects_invalid_language_option(tmp_path: Path) -> None:
    """Test that an unsupported `--lang` value is rejected immediately."""
    # Given a `new` command call with an unsupported `--lang` value
    target_dir = tmp_path / "sample-act"

    # When argument validation runs
    result = runner.invoke(
        app,
        [
            "new",
            "--path",
            str(target_dir),
            "--act-name",
            "Sample Act",
            "--cast-name",
            "Primary Cast",
            "--lang",
            "jp",
        ],
    )

    # Then the command should fail immediately with a language error
    assert result.exit_code != 0
    combined_output = (result.stdout or "") + (result.stderr or "")
    assert "Unsupported language" in combined_output


def test_cast_command_adds_new_cast_to_existing_project(tmp_path: Path) -> None:
    """Test that `act cast` adds a cast package, test file, and langgraph entry."""
    # Given an existing Act project and a new Cast name
    target_dir = _create_project(tmp_path)

    # When `act cast` is executed
    result = runner.invoke(
        app,
        [
            "cast",
            "--path",
            str(target_dir),
            "--cast-name",
            "Secondary Cast",
            "--lang",
            "en",
        ],
    )

    assert result.exit_code == 0, result.stdout

    cast_dir = target_dir / "casts" / "secondary_cast"
    cast_test = target_dir / "tests" / "cast_tests" / "secondary_cast_test.py"
    langgraph = _read_json(target_dir / "langgraph.json")
    graphs = langgraph["graphs"]

    # Then the new cast package, copied test, and langgraph entry should exist
    assert cast_dir.exists()
    assert (cast_dir / "graph.py").exists()
    assert (cast_dir / "README.md").exists()
    assert cast_test.exists()
    assert "secondary-cast" in graphs
    assert (
        graphs["secondary-cast"]
        == "./casts/secondary_cast/graph.py:secondary_cast_graph"
    )


def test_cast_command_rejects_non_act_project(tmp_path: Path) -> None:
    """Test that `act cast` rejects paths that are not valid Act projects."""
    # Given a directory that does not contain the required Act project files
    invalid_project_dir = tmp_path / "not-an-act"
    invalid_project_dir.mkdir()

    # When `act cast` is executed against that path
    result = runner.invoke(
        app,
        [
            "cast",
            "--path",
            str(invalid_project_dir),
            "--cast-name",
            "Secondary Cast",
            "--lang",
            "en",
        ],
    )

    # Then the command should reject it as an invalid Act project
    assert result.exit_code != 0
    combined_output = (result.stdout or "") + (result.stderr or "")
    assert "does not look like a valid Act project" in combined_output


def test_cast_command_aborts_when_cast_directory_exists(tmp_path: Path) -> None:
    """Test that `act cast` aborts when the target cast directory already exists."""
    # Given an Act project where the target cast directory already exists
    target_dir = _create_project(tmp_path)

    # When the same Cast is created a second time
    first_result = runner.invoke(
        app,
        [
            "cast",
            "--path",
            str(target_dir),
            "--cast-name",
            "Secondary Cast",
            "--lang",
            "en",
        ],
    )
    assert first_result.exit_code == 0, first_result.stdout

    second_result = runner.invoke(
        app,
        [
            "cast",
            "--path",
            str(target_dir),
            "--cast-name",
            "Secondary Cast",
            "--lang",
            "en",
        ],
    )

    # Then the command should abort instead of overwriting that Cast
    assert second_result.exit_code != 0
    combined_output = (second_result.stdout or "") + (second_result.stderr or "")
    assert "cast directory already exists and is not empty" in combined_output


def test_cast_command_with_rag_flag(tmp_path: Path) -> None:
    """Test that `act cast --rag` generates a RAG-enabled Cast with embeddings & tools."""
    # Given an existing Act project
    target_dir = _create_project(tmp_path)

    # When `act cast` is executed with --rag
    result = runner.invoke(
        app,
        [
            "cast",
            "--path",
            str(target_dir),
            "--cast-name",
            "Knowledge Cast",
            "--rag",
            "--lang",
            "en",
        ],
    )

    assert result.exit_code == 0, result.stdout

    cast_dir = target_dir / "casts" / "knowledge_cast"
    models_file = cast_dir / "modules" / "models.py"
    tools_file = cast_dir / "modules" / "tools.py"
    state_file = cast_dir / "modules" / "state.py"
    test_file = target_dir / "tests" / "cast_tests" / "knowledge_cast_test.py"
    readme_file = cast_dir / "README.md"

    # Then RAG-specific artifacts should be generated
    assert cast_dir.exists()
    assert "get_embedding_model" in _read(models_file)
    assert "retrieve_documents" in _read(tools_file)
    assert "retrieved_docs" in _read(state_file)
    assert "context" in _read(state_file)
    assert "retrieved_docs" in _read(test_file)
    assert "RAG" in _read(readme_file)


def test_new_command_with_rag_flag(tmp_path: Path) -> None:
    """Test that `act new --rag` generates a project with an initial RAG Cast."""
    # Given a target directory and arguments with --rag
    target_dir = tmp_path / "rag-act"

    # When `act new` is executed with --rag
    result = runner.invoke(
        app,
        [
            "new",
            "--path",
            str(target_dir),
            "--act-name",
            "Rag Act",
            "--cast-name",
            "Rag Cast",
            "--rag",
            "--lang",
            "kr",
        ],
    )

    assert result.exit_code == 0, result.stdout

    cast_dir = target_dir / "casts" / "rag_cast"
    models_file = cast_dir / "modules" / "models.py"
    tools_file = cast_dir / "modules" / "tools.py"
    state_file = cast_dir / "modules" / "state.py"

    assert "get_embedding_model" in _read(models_file)
    assert "retrieve_documents" in _read(tools_file)
    assert "retrieved_docs" in _read(state_file)


def test_cast_command_with_template_and_vector_db(tmp_path: Path) -> None:
    """Test `act cast --template rag --vector-db pgvector` scaffolds pgvector setup."""
    # Given an existing Act project
    target_dir = _create_project(tmp_path)

    # When `act cast` is executed with --template rag --vector-db pgvector
    result = runner.invoke(
        app,
        [
            "cast",
            "--path",
            str(target_dir),
            "--cast-name",
            "PolicySearch",
            "--template",
            "rag",
            "--vector-db",
            "pgvector",
            "--lang",
            "kr",
        ],
    )

    assert result.exit_code == 0, result.stdout

    cast_dir = target_dir / "casts" / "policysearch"
    pyproject_file = cast_dir / "pyproject.toml"
    tools_file = cast_dir / "modules" / "tools.py"

    assert cast_dir.exists()
    assert "retrieve_documents" in _read(tools_file)
    assert "pgvector" in _read(pyproject_file)
