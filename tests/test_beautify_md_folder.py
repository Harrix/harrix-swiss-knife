"""Tests for Markdown beautify folder helpers."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from harrix_swiss_knife.actions.markdown.beautify_md_folder import OnBeautifyMdFolder


def test_delete_generated_g_md_keeps_include(tmp_path: Path) -> None:
    dump = tmp_path / "_Notes.g.md"
    include = tmp_path / "table.include.g.md"
    note = tmp_path / "note.md"
    dump.write_text("dump\n", encoding="utf-8")
    include.write_text("include\n", encoding="utf-8")
    note.write_text("# Note\n", encoding="utf-8")

    message = OnBeautifyMdFolder._delete_generated_g_md_files(tmp_path)

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

    OnBeautifyMdFolder.beautify_markdown_common(
        action,
        str(tmp_path),
        is_include_summaries_and_combine=False,
    )

    assert dump.exists()
