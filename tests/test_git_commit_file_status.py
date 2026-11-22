"""Lucide glyphs for porcelain file status in the Git commit window."""

from __future__ import annotations

from harrix_swiss_knife.apps.git_commit.window import _file_status_glyph


def test_deleted_uses_square_minus() -> None:
    """Deleted paths use `square-minus`."""
    assert _file_status_glyph(" D") == ("square-minus", "critical", "Deleted")
    assert _file_status_glyph("D ") == ("square-minus", "critical", "Deleted")


def test_modified_uses_square_letter_m() -> None:
    """Staged and unstaged edits use `square-letter-m`."""
    assert _file_status_glyph(" M") == ("square-letter-m", "caution", "Modified")
    assert _file_status_glyph("M ") == ("square-letter-m", "caution", "Modified")
    assert _file_status_glyph("MM") == ("square-letter-m", "caution", "Modified")


def test_untracked_and_added_use_square_plus() -> None:
    """New paths use `square-plus`."""
    assert _file_status_glyph("??") == ("square-plus", "success", "Untracked")
    assert _file_status_glyph("A ") == ("square-plus", "success", "Added")
