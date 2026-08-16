"""Tests for Markdown beautify helpers."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from harrix_swiss_knife.actions.common.python_project import (
    is_python_project,
    reject_python_project_for_md_beautify,
)
from harrix_swiss_knife.actions.markdown.beautify_md import OnBeautifyMd
from harrix_swiss_knife.actions.markdown.regenerate_g_md import OnRegenerateGMd


def test_is_python_project_detects_pyproject(tmp_path: Path) -> None:
    assert not is_python_project(tmp_path)
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'x'\n", encoding="utf-8")
    assert is_python_project(tmp_path)


def test_reject_python_project_for_md_beautify(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'x'\n", encoding="utf-8")
    action = MagicMock()
    assert reject_python_project_for_md_beautify(action, tmp_path, noninteractive=True) is True
    action.add_line.assert_called_once()
    assert "Python project" in action.add_line.call_args.args[0]
    action.show_result.assert_not_called()


def test_delete_generated_g_md_keeps_include(tmp_path: Path) -> None:
    dump = tmp_path / "_Notes.g.md"
    include = tmp_path / "table.include.g.md"
    note = tmp_path / "note.md"
    dump.write_text("dump\n", encoding="utf-8")
    include.write_text("include\n", encoding="utf-8")
    note.write_text("# Note\n", encoding="utf-8")

    message = OnBeautifyMd._delete_generated_g_md_files(tmp_path)

    assert "deleted" in message.lower()
    assert not dump.exists()
    assert include.exists()
    assert note.exists()


def test_beautify_common_default_does_not_delete_g_md(tmp_path: Path) -> None:
    """Callers like ruff-sort-docs must keep freshly generated *.g.md docs."""
    dump = tmp_path / "module.g.md"
    dump.write_text("# Docs\n", encoding="utf-8")
    action = MagicMock()
    action.config = {"paths_notes_for_summaries": []}
    action.prose_wrap = "preserve"
    action.print_width = 80
    action.apply_prose_fixes = False
    action.format_code_blocks = False

    OnBeautifyMd.beautify_markdown_common(
        action,
        str(tmp_path),
        is_include_summaries_and_combine=False,
    )

    assert dump.exists()


def test_regenerate_g_md_does_not_change_source_md(tmp_path: Path) -> None:
    """Regenerate rebuilds `.g.md` dumps and leaves source notes unchanged."""
    original = "---\nlang: ru\n---\n\n# Note\n\nHello world.\n"
    note = tmp_path / "note.md"
    note.write_text(original, encoding="utf-8")
    stale = tmp_path / "_stale.g.md"
    stale.write_text("old dump\n", encoding="utf-8")

    action = MagicMock()
    action.config = {"paths_notes_for_summaries": []}
    action.prose_wrap = "preserve"
    action.print_width = 80
    action.apply_prose_fixes = False
    action.format_code_blocks = False

    OnRegenerateGMd.regenerate_g_md_common(action, str(tmp_path))

    assert note.read_text(encoding="utf-8") == original
    assert not stale.exists()
    combined = tmp_path / f"_{tmp_path.name}.g.md"
    assert combined.exists()
