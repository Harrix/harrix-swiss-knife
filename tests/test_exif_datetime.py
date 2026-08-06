"""Tests for EXIF date/time helpers."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from PIL import Image
from PIL.ExifTags import IFD, Base

from harrix_swiss_knife.actions.common.exif_datetime import (
    format_exif_datetime,
    iter_exif_image_files,
    set_exif_datetime,
    set_exif_datetime_in_folder,
    summarize_exif_datetime_results,
)


def _naive(year: int, month: int, day: int, hour: int = 0) -> datetime:
    """Build a naive datetime for EXIF (no timezone in the tag)."""
    return datetime(year, month, day, hour, 0, 0)  # noqa: DTZ001


def test_format_exif_datetime() -> None:
    assert format_exif_datetime(_naive(2024, 6, 15, 14)) == "2024:06:15 14:00:00"


def test_set_exif_datetime_writes_jpeg_tags(tmp_path: Path) -> None:
    path = tmp_path / "photo.jpg"
    image = Image.new("RGB", (32, 32), color=(10, 20, 30))
    exif = Image.Exif()
    exif[Base.Make] = "TestCam"
    image.save(path, exif=exif, format="JPEG", quality=90)

    result = set_exif_datetime(path, _naive(2024, 8, 6, 15))
    assert result.status == "updated"
    assert result.detail == "2024:08:06 15:00:00"

    loaded = Image.open(path)
    loaded_exif = loaded.getexif()
    assert loaded_exif.get(Base.DateTime) == "2024:08:06 15:00:00"
    assert loaded_exif.get(Base.Make) == "TestCam"
    exif_ifd = loaded_exif.get_ifd(IFD.Exif)
    assert exif_ifd.get(Base.DateTimeOriginal) == "2024:08:06 15:00:00"
    assert exif_ifd.get(Base.DateTimeDigitized) == "2024:08:06 15:00:00"
    loaded.close()


def test_set_exif_datetime_skips_unsupported_extension(tmp_path: Path) -> None:
    path = tmp_path / "notes.txt"
    path.write_text("no image", encoding="utf-8")
    result = set_exif_datetime(path, _naive(2024, 1, 1))
    assert result.status == "skipped"


def test_set_exif_datetime_in_folder_recursive(tmp_path: Path) -> None:
    nested = tmp_path / "a" / "b"
    nested.mkdir(parents=True)
    jpg = nested / "shot.jpg"
    png = tmp_path / "ignored.png"
    Image.new("RGB", (16, 16), color=(1, 2, 3)).save(jpg, format="JPEG")
    Image.new("RGB", (16, 16), color=(4, 5, 6)).save(png, format="PNG")

    assert iter_exif_image_files(tmp_path) == [jpg]
    results = set_exif_datetime_in_folder(tmp_path, _naive(2025, 1, 2, 9))
    assert len(results) == 1
    assert results[0].status == "updated"

    summary = summarize_exif_datetime_results(results)
    assert "Updated: 1" in summary
    assert "shot.jpg" in summary
