# Sync

Sync environment after clone or pyproject.toml changes.

```bash
uv sync --all-packages              # All casts + dev
uv sync --package <cast>            # Specific cast
uv sync --all-packages --no-dev     # Production
uv sync --reinstall --all-packages  # Force reinstall
```
