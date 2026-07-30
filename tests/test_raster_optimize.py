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


def test_is_flat_graphic_detects_solid_background_diagram() -> None:
    image = Image.new("RGB", (200, 120), (255, 255, 255))
    for x in range(40, 160):
        image.putpixel((x, 60), (0, 0, 0))
        image.putpixel((x, 61), (30, 90, 200))
    assert raster_optimize._is_flat_graphic(image) is True


def test_is_flat_graphic_rejects_noisy_many_color_image() -> None:
    image = Image.new("RGB", (64, 64))
    for y in range(64):
        for x in range(64):
            image.putpixel((x, y), (x * 3 % 256, y * 5 % 256, (x + y) * 7 % 256))
    assert raster_optimize._is_flat_graphic(image) is False


@patch("harrix_swiss_knife.actions.common.raster_optimize._convert_to_avif")
def test_process_png_compare_uses_hq_avif_for_flat_graphic(mock_convert: object, tmp_path: Path) -> None:
    source = tmp_path / "diagram.png"
    output_folder = tmp_path / "output"
    Image.new("RGB", (80, 60), (255, 255, 255)).save(source, format="PNG")

    convert_kwargs: dict[str, object] = {}

    def fake_convert(_source_path: Path, output_path: Path, *_args: object, **kwargs: object) -> None:
        convert_kwargs.update(kwargs)
        output_path.write_bytes(b"x" * 100_000)

    mock_convert.side_effect = fake_convert

    message = raster_optimize.process_png_compare(source, output_folder, tmp_path)
    assert convert_kwargs.get("quality") is True
    assert convert_kwargs.get("pix_fmt") == raster_optimize._PIX_FMT_FLAT_GRAPHIC
    assert (output_folder / "diagram.png").exists()
    assert not (output_folder / "diagram.avif").exists()
    assert "kept as PNG" in message
    assert "high-quality AVIF" in message


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
