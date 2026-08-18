"""Tests for current-folder file listing."""

from __future__ import annotations

from pathlib import Path

from harrix_swiss_knife.actions.files.list_files_current_folder import format_current_folder_listing


def test_format_current_folder_listing_includes_dirs_and_files(tmp_path: Path) -> None:
    (tmp_path / "readme.md").write_text("x", encoding="utf-8")
    (tmp_path / "icons").mkdir()
    (tmp_path / "icons" / "nested.svg").write_text("<svg/>", encoding="utf-8")

    listing = format_current_folder_listing(tmp_path)
    assert "icons/" in listing
    assert "readme.md" in listing
    assert "nested.svg" not in listing
    assert listing.index("icons/") < listing.index("readme.md")


def test_format_current_folder_listing_empty_folder(tmp_path: Path) -> None:
    listing = format_current_folder_listing(tmp_path)
    assert "(empty folder)" in listing
    assert str(tmp_path) in listing
