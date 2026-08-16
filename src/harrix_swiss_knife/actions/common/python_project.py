"""Helpers for detecting Python project folders."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from harrix_pylib.funcs_py import is_python_project

__all__ = ["is_python_project", "reject_python_project_for_md_beautify"]

if TYPE_CHECKING:
    from harrix_swiss_knife.actions.common.base import ActionBase


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
