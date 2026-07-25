"""Helpers for detecting Python project folders."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from harrix_swiss_knife.actions.base import ActionBase


def is_python_project(folder_path: Path | str) -> bool:
    """Return whether `folder_path` looks like a Python project (`pyproject.toml`)."""
    return (Path(folder_path) / "pyproject.toml").is_file()


def reject_python_project_for_md_beautify(
    action: ActionBase,
    folder_path: Path | str,
    *,
    noninteractive: bool,
) -> bool:
    """Log an error and return `True` if Markdown beautify must not run on a Python project."""
    path = Path(folder_path)
    if not is_python_project(path):
        return False
    action.add_line(
        f"❌ {path} is a Python project (has pyproject.toml). Use `hsk py ruff-sort-docs` instead.",
    )
    if not noninteractive:
        action.show_result()
    return True
