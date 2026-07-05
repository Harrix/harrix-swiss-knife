"""Shared image optimization for all supported formats."""

from __future__ import annotations

import shutil
from typing import TYPE_CHECKING

import harrix_pylib as h

from harrix_swiss_knife.actions.images.raster_optimize import RASTER_EXTENSIONS, optimize_raster_file

if TYPE_CHECKING:
    from pathlib import Path

TOOL_EXTENSIONS = h.img.EXE_RASTER_EXTENSIONS
SUPPORTED_EXTENSIONS = frozenset({".svg", *TOOL_EXTENSIONS, *RASTER_EXTENSIONS})


def optimize_image_file(
    source: Path,
    output_folder: Path,
    project_root: Path,
    *,
    quality: bool = False,
    max_size: int | None = None,
    compare_png_avif: bool = True,
    convert_png_to_avif: bool = False,
) -> str | None:
    """Optimize a single supported image file."""
    ext = source.suffix.lower()
    if ext == ".svg":
        output_path = output_folder / source.name
        content = source.read_text(encoding="utf-8")
        optimized = h.svg_opt.SvgOptimizer().optimize(content)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(optimized, encoding="utf-8")
        return f"✅ File {source.name} successfully optimized."
    if ext in TOOL_EXTENSIONS:
        output_name = source.with_suffix(".avif").name if ext in {".gif", ".mp4"} else source.name
        return h.img.optimize_image_with_tools(
            source,
            output_folder / output_name,
            project_root=project_root,
            quality=quality,
            max_size=max_size,
        )
    if ext in RASTER_EXTENSIONS:
        return optimize_raster_file(
            source,
            output_folder,
            project_root,
            quality=quality,
            max_size=max_size,
            compare_png_avif=compare_png_avif,
            convert_png_to_avif=convert_png_to_avif,
        )
    return None


def optimize_images_in_folder(
    images_folder: Path,
    output_folder: Path,
    project_root: Path,
    *,
    quality: bool = False,
    max_size: int | None = None,
    compare_png_avif: bool = True,
    convert_png_to_avif: bool = False,
    clear_output: bool = True,
) -> str:
    """Optimize all supported images in a folder.

    Args:

    - `images_folder` (`Path`): Source folder with images.
    - `output_folder` (`Path`): Destination folder for optimized images.
    - `project_root` (`Path`): Project root with ffmpeg.exe, avifenc.exe, avifdec.exe.
    - `quality` (`bool`): Use higher quality settings. Defaults to `False`.
    - `max_size` (`int | None`): Maximum width or height in pixels. Defaults to `None`.
    - `compare_png_avif` (`bool`): For PNG, compare optimized PNG vs AVIF. Defaults to `True`.
    - `convert_png_to_avif` (`bool`): For PNG, always convert to AVIF. Defaults to `False`.
    - `clear_output` (`bool`): Clear output folder before processing. Defaults to `True`.

    Returns:

    - `str`: Newline-separated status messages.

    """
    lines: list[str] = []
    if clear_output:
        if output_folder.exists():
            for item in output_folder.iterdir():
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
        else:
            output_folder.mkdir(parents=True, exist_ok=True)
    else:
        output_folder.mkdir(parents=True, exist_ok=True)

    if not images_folder.exists():
        lines.append(f"❌ Images folder not found: {images_folder}")
        return "\n".join(lines)

    for file in sorted(images_folder.iterdir()):
        if not file.is_file():
            continue
        try:
            message = optimize_image_file(
                file,
                output_folder,
                project_root,
                quality=quality,
                max_size=max_size,
                compare_png_avif=compare_png_avif,
                convert_png_to_avif=convert_png_to_avif,
            )
        except (RuntimeError, ValueError) as error:
            lines.append(f"❌ Error while processing file {file.name}: {error}")
            continue
        if message:
            lines.append(message)

    if not lines:
        lines.append("🔵 No supported image files found.")

    return "\n".join(lines)
