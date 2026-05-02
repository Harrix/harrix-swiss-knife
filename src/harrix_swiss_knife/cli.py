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
    _exit_if_action_failed(action)


@markdown_group.command("new-note")
@click.option(
    "--folder",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=None,
    help="Target folder; with --name, skips save/template dialogs (first beginning template).",
)
@click.option(
    "--name",
    type=str,
    default=None,
    help="Note stem (without .md); requires --folder.",
)
def markdown_new_note(folder: Path | None, name: str | None) -> None:
    """Create a new note (interactive, or --folder + --name for VS Code / automation)."""
    _ensure_qt_app()
    action = OnNewMarkdown()
    if folder is not None:
        if not name or not name.strip():
            raise click.UsageError(_USAGE_NAME_WITH_FOLDER)
        action.execute_new_note_at(folder, name.strip(), is_with_images=False)
    else:
        if name:
            raise click.UsageError(_USAGE_FOLDER_WITH_NAME)
        action.execute_new_note()
    _exit_if_action_failed(action)


@markdown_group.command("new-note-with-images")
@click.option(
    "--folder",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=None,
    help="Target folder; with --name, skips save/template dialogs (first beginning template).",
)
@click.option(
    "--name",
    type=str,
    default=None,
    help="Note stem (without .md); requires --folder.",
)
def markdown_new_note_with_images(folder: Path | None, name: str | None) -> None:
    """Create a new note with images (interactive, or --folder + --name)."""
    _ensure_qt_app()
    action = OnNewMarkdown()
    if folder is not None:
        if not name or not name.strip():
            raise click.UsageError(_USAGE_NAME_WITH_FOLDER)
        action.execute_new_note_at(folder, name.strip(), is_with_images=True)
    else:
        if name:
            raise click.UsageError(_USAGE_FOLDER_WITH_NAME)
        action.execute_new_note_with_images()
    _exit_if_action_failed(action)


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
    _exit_if_action_failed(action)


@python_group.command("isort-ruff-sort-docs")
@click.argument(
    "folder",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
)
def python_isort_ruff_sort_docs(folder: Path) -> None:
    """isort, ruff format, sort code, generate docs and format Markdown (same as tray action)."""
    action = OnSortIsortFmtDocsPythonCodeFolder()
    action(folder_path=folder, noninteractive=True)
    _exit_if_action_failed(action)


def _cli_action_failed(result_lines: list[object]) -> bool:
    """Return whether any output line reports failure (❌ prefix, same as tray actions)."""
    return any(isinstance(line, str) and line.strip().startswith("❌") for line in result_lines)


def _ensure_qt_app() -> QApplication:
    """Ensure a QApplication exists (required for interactive dialogs)."""
    app = cast("QApplication | None", QApplication.instance())
    if app is None:
        app = QApplication(sys.argv)
    return app


def _exit_if_action_failed(action: object) -> None:
    """Exit with code 1 and print action lines to stderr when any line starts with ❌."""
    lines = getattr(action, "result_lines", [])
    if not _cli_action_failed(lines):
        return
    for line in lines:
        print(line, file=sys.stderr)
    sys.exit(1)


def main() -> None:
    """Entry point for ``harrix-swiss-knife-cli``."""
    # When spawned from GUI apps (VS Code/Cursor), stdio can be non-UTF on Windows.
    # Make CLI resilient to emoji/status lines.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")  # type: ignore[attr-defined]
        sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")  # type: ignore[attr-defined]
    except Exception as e:
        # Best-effort only; avoid failing CLI if stdio is not reconfigurable.
        print(f"⚠️ Could not reconfigure stdio to UTF-8: {e}", file=sys.stderr)
    cli()


_USAGE_NAME_WITH_FOLDER = "--name is required when --folder is set."
_USAGE_FOLDER_WITH_NAME = "--folder is required when --name is set."
