"""Tests for photo sync filename allocation."""

from __future__ import annotations

from pathlib import Path

from harrix_swiss_knife.photo_sync.naming import (
    allocate_filename,
    display_name_prefers_copy,
    extension_for_mime,
    stem_from_date_taken_ms,
)


def test_stem_from_date_taken_ms() -> None:
    stem = stem_from_date_taken_ms(1_723_045_197_000)
    assert len(stem) == len("2026-08-07 16.39.57")
    assert stem[4] == "-"
    assert stem[10] == " "
    assert "." in stem


def test_extension_for_mime() -> None:
    assert extension_for_mime("image/jpeg") == "jpg"
    assert extension_for_mime(None, "photo.PNG") == "png"


def test_display_name_prefers_copy() -> None:
    assert display_name_prefers_copy("2026-08-07 16.39.57_copy.jpg")
    assert display_name_prefers_copy("foo_copy2.png")
    assert not display_name_prefers_copy("2026-08-07 16.39.57.jpg")


def test_allocate_filename_copy_on_collision(tmp_path: Path) -> None:
    epoch_ms = 1_577_836_800_000
    base = f"{stem_from_date_taken_ms(epoch_ms)}.jpg"
    (tmp_path / base).write_bytes(b"x")
    name = allocate_filename(
        tmp_path,
        date_taken_epoch_ms=epoch_ms,
        extension="jpg",
        force_copy=False,
    )
    assert "_copy" in name


def test_allocate_filename_force_copy(tmp_path: Path) -> None:
    name = allocate_filename(
        tmp_path,
        date_taken_epoch_ms=1_577_836_800_000,
        extension="jpg",
        force_copy=True,
    )
    assert name.endswith("_copy.jpg")
