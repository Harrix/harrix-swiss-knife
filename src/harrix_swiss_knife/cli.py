"""Console entry point for Harrix Swiss Knife actions (Click)."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import cast

import click
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.actions.markdown import OnBeautifyMdFolderAndRegenerateGMd, OnNewMarkdown
from harrix_swiss_knife.actions.python import (
    OnSortIsortFmtDocsPythonCodeFolder,
    OnSortIsortFmtPythonCodeFolder,
)


@click.group()
def cli() -> None:
    """Harrix Swiss Knife CLI."""


@cli.group("markdown")
def markdown_group() -> None:
    """Markdown-related commands."""


@markdown_group.command("beautify-regenerate-g-md")
@click.argument(
    "folder",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
)
def markdown_beautify_regenerate_g_md(folder: Path) -> None:
    """Beautify Markdown under FOLDER and regenerate .g.md (same as tray action)."""
    action = OnBeautifyMdFolderAndRegenerateGMd()
    action(folder_path=folder, noninteractive=True)
    if any(line.startswith("❌ Error") for line in action.result_lines):
        sys.exit(1)


@markdown_group.command("new-note")
def markdown_new_note() -> None:
    """Create a new note (interactive dialogs, same as New Markdown → New note)."""
    _ensure_qt_app()
    action = OnNewMarkdown()
    action.execute_new_note()
    if any(line.startswith("❌ Error") for line in action.result_lines):
        sys.exit(1)


@markdown_group.command("new-note-with-images")
def markdown_new_note_with_images() -> None:
    """Create a new note with images (interactive dialogs, same as New Markdown → New note with images)."""
    _ensure_qt_app()
    action = OnNewMarkdown()
    action.execute_new_note_with_images()
    if any(line.startswith("❌ Error") for line in action.result_lines):
        sys.exit(1)


@cli.group("python")
def python_group() -> None:
    """Python project formatting (isort, ruff, sort)."""


@python_group.command("isort-ruff-sort")
@click.argument(
    "folder",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
)
def python_isort_ruff_sort(folder: Path) -> None:
    """isort, ruff format, sort code in PY files without docs step (same as tray action)."""
    action = OnSortIsortFmtPythonCodeFolder()
    action(folder_path=folder, noninteractive=True)
    if any(line.startswith("❌ Error") for line in action.result_lines):
        sys.exit(1)


@python_group.command("isort-ruff-sort-docs")
@click.argument(
    "folder",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
)
def python_isort_ruff_sort_docs(folder: Path) -> None:
    """isort, ruff format, sort code, generate docs and format Markdown (same as tray action)."""
    action = OnSortIsortFmtDocsPythonCodeFolder()
    action(folder_path=folder, noninteractive=True)
    if any(line.startswith("❌ Error") for line in action.result_lines):
        sys.exit(1)


def _ensure_qt_app() -> QApplication:
    """Ensure a QApplication exists (required for interactive dialogs)."""
    app = cast("QApplication | None", QApplication.instance())
    if app is None:
        app = QApplication(sys.argv)
    return app


def main() -> None:
    """Entry point for ``harrix-swiss-knife-cli``."""
    cli()
