"""Tests for Pillow and ffmpeg raster optimization."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from PIL import Image

from harrix_swiss_knife.actions.common import raster_optimize


def _write_test_png(path: Path, *, size: tuple[int, int] = (120, 80), rgba: bool = True) -> None:
    mode = "RGBA" if rgba else "RGB"
    color = (200, 100, 50, 255) if rgba else (200, 100, 50)
    Image.new(mode, size, color).save(path, format="PNG")


def test_encode_optimized_png_returns_bytes(tmp_path: Path) -> None:
    source = tmp_path / "icon.png"
    _write_test_png(source)
    with Image.open(source) as image:
        png_bytes = raster_optimize._encode_optimized_png(image.convert("RGBA"))
    assert isinstance(png_bytes, bytes)
    assert len(png_bytes) > 0


def test_load_and_resize_does_not_enlarge(tmp_path: Path) -> None:
    source = tmp_path / "small.png"
    _write_test_png(source, size=(50, 40))
    image = raster_optimize._load_and_resize(source, max_size=800)
    assert image.size == (50, 40)


def test_load_and_resize_shrinks_large_image(tmp_path: Path) -> None:
    source = tmp_path / "large.png"
    _write_test_png(source, size=(1600, 900))
    image = raster_optimize._load_and_resize(source, max_size=800)
    assert max(image.size) == 800


def test_optimize_raster_file_rejects_unknown_extension(tmp_path: Path) -> None:
    source = tmp_path / "image.bmp"
    source.write_bytes(b"fake")
    with pytest.raises(ValueError, match="not a supported raster format"):
        raster_optimize.optimize_raster_file(source, tmp_path / "out", tmp_path)


@patch("harrix_swiss_knife.actions.common.raster_optimize._convert_to_avif")
def test_process_png_compare_keeps_single_output_file(mock_convert: object, tmp_path: Path) -> None:
    source = tmp_path / "photo.png"
    output_folder = tmp_path / "output"
    project_root = tmp_path
    _write_test_png(source)

    def fake_convert(_source_path: Path, output_path: Path, *_args: object, **_kwargs: object) -> None:
        output_path.write_bytes(b"x" * 5000)

    mock_convert.side_effect = fake_convert

    message = raster_optimize.process_png_compare(source, output_folder, project_root)
    output_files = list(output_folder.iterdir())
    assert len(output_files) == 1
    assert output_files[0].suffix in {".png", ".avif"}
    assert "KB" in message


@patch("harrix_swiss_knife.actions.common.raster_optimize._convert_to_avif")
def test_process_png_compare_prefers_smaller_png(mock_convert: object, tmp_path: Path) -> None:
    source = tmp_path / "photo.png"
    output_folder = tmp_path / "output"
    _write_test_png(source, size=(32, 32))

    def fake_convert(_source_path: Path, output_path: Path, *_args: object, **_kwargs: object) -> None:
        output_path.write_bytes(b"x" * 100_000)

    mock_convert.side_effect = fake_convert

    message = raster_optimize.process_png_compare(source, output_folder, tmp_path)
    assert (output_folder / "photo.png").exists()
    assert not (output_folder / "photo.avif").exists()
    assert "kept as PNG" in message


@pytest.mark.slow
def test_process_jpg_webp_to_avif_with_ffmpeg(tmp_path: Path) -> None:
    project_root = Path(__file__).resolve().parents[1]
    if not (project_root / "ffmpeg.exe").exists():
        pytest.skip("ffmpeg.exe not available in project root")
    source = tmp_path / "photo.jpg"
    Image.new("RGB", (64, 48), (120, 80, 40)).save(source, format="JPEG", quality=95)
    output_path = tmp_path / "photo.avif"
    message = raster_optimize.process_jpg_webp_to_avif(source, output_path, project_root)
    assert output_path.exists()
    assert output_path.stat().st_size > 0
    assert "converted to AVIF" in message
