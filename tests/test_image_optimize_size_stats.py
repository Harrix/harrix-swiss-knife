"""Tests for shared image optimization size summary helpers."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from PIL import Image

from harrix_swiss_knife.actions.common.image_optimize import (
    OptimizeSizeStats,
    format_byte_size,
    optimize_images_in_folder,
)


def test_format_byte_size_units() -> None:
    assert format_byte_size(500) == "500 B"
    assert format_byte_size(2048) == "2.00 KB"
    assert format_byte_size(2 * 1024 * 1024) == "2.00 MB"


def test_optimize_size_stats_format_summary_saved() -> None:
    stats = OptimizeSizeStats()
    stats.add(10_000, 2_500)
    summary = stats.format_summary()
    assert "1 image:" in summary
    assert "saved" in summary
    assert "75.0%" in summary


def test_optimize_size_stats_format_summary_grew() -> None:
    stats = OptimizeSizeStats()
    stats.add(1_000, 2_000)
    summary = stats.format_summary()
    assert "grew by" in summary


@patch("harrix_swiss_knife.actions.common.image_optimize.optimize_image_file")
def test_optimize_images_in_folder_appends_size_summary(mock_optimize: object, tmp_path: Path) -> None:
    images = tmp_path / "images"
    output = tmp_path / "out"
    images.mkdir()
    source = images / "photo.png"
    Image.new("RGB", (32, 32), (10, 20, 30)).save(source, format="PNG")
    before = source.stat().st_size

    def fake_optimize(src: Path, out_folder: Path, *_args: object, **_kwargs: object) -> str:
        out_folder.mkdir(parents=True, exist_ok=True)
        out = out_folder / f"{src.stem}.avif"
        out.write_bytes(b"x" * max(1, before // 4))
        return f"✅ File {src.name} successfully converted to AVIF."

    mock_optimize.side_effect = fake_optimize

    result = optimize_images_in_folder(images, output, tmp_path)
    assert "✅ File photo.png successfully converted to AVIF." in result
    assert "📊 1 image:" in result
    assert "saved" in result
