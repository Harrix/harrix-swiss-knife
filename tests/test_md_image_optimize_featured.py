"""Tests that Markdown image optimisation keeps root featured-image assets in place."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from PIL import Image

from harrix_swiss_knife.actions.common.md_image_optimize import (
    optimize_image_file,
    process_markdown_image_line,
)


def _fake_run_image_optimize(
    temp_folder: str,
    *,
    ext: str,
    is_convert_png_to_avif: bool = False,
    is_compare_png_avif_sizes: bool = False,
    max_size: int | None = None,
) -> Path:
    del ext, is_convert_png_to_avif, is_compare_png_avif_sizes, max_size
    temp_path = Path(temp_folder)
    output_dir = temp_path / "temp"
    output_dir.mkdir(parents=True, exist_ok=True)
    for source in temp_path.iterdir():
        if source.is_file():
            (output_dir / f"{source.stem}.avif").write_bytes(b"avif")
    return output_dir


@patch(
    "harrix_swiss_knife.actions.common.md_image_optimize._run_image_optimize",
    side_effect=_fake_run_image_optimize,
)
def test_optimize_image_file_keeps_root_featured_image(mock_optimize: object, tmp_path: Path) -> None:
    featured = tmp_path / "featured-image.jpg"
    Image.new("RGB", (32, 32), (10, 20, 30)).save(featured, format="JPEG")

    result = optimize_image_file(
        featured,
        md_dir=tmp_path,
        image_path="featured-image.jpg",
        is_compare_png_avif_sizes=True,
    )

    assert result is not None
    new_path, new_rel = result
    assert new_path == tmp_path / "featured-image.avif"
    assert new_rel == "featured-image.avif"
    assert new_path.is_file()
    assert not (tmp_path / "img" / "featured-image.avif").exists()
    assert not featured.exists()
    assert mock_optimize.called


@patch(
    "harrix_swiss_knife.actions.common.md_image_optimize._run_image_optimize",
    side_effect=_fake_run_image_optimize,
)
def test_optimize_image_file_still_moves_regular_root_image_to_img(mock_optimize: object, tmp_path: Path) -> None:
    photo = tmp_path / "photo.jpg"
    Image.new("RGB", (32, 32), (40, 50, 60)).save(photo, format="JPEG")

    result = optimize_image_file(
        photo,
        md_dir=tmp_path,
        image_path="photo.jpg",
        is_compare_png_avif_sizes=True,
    )

    assert result is not None
    new_path, new_rel = result
    assert new_path == tmp_path / "img" / "photo.avif"
    assert new_rel == "img/photo.avif"
    assert new_path.is_file()
    assert mock_optimize.called


@patch(
    "harrix_swiss_knife.actions.common.md_image_optimize._run_image_optimize",
    side_effect=_fake_run_image_optimize,
)
def test_process_markdown_line_keeps_featured_image_link_in_root(mock_optimize: object, tmp_path: Path) -> None:
    featured = tmp_path / "featured-image.png"
    Image.new("RGB", (24, 24), (1, 2, 3)).save(featured, format="PNG")
    md_file = tmp_path / "note.md"
    md_file.write_text("![Featured image](featured-image.png)\n", encoding="utf-8")

    line = process_markdown_image_line(
        "![Featured image](featured-image.png)",
        md_file,
        is_compare_png_avif_sizes=True,
    )

    assert line == "![Featured image](featured-image.avif)"
    assert (tmp_path / "featured-image.avif").is_file()
    assert not (tmp_path / "img" / "featured-image.avif").exists()
    assert mock_optimize.called
