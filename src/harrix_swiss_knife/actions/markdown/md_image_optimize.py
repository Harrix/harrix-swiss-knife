"""Shared Markdown image optimisation helpers."""

from __future__ import annotations

import re
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

import harrix_pylib as h
from PIL import Image

from harrix_swiss_knife.actions.images.image_optimize import optimize_images_in_folder

SUPPORTED_IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".webp", ".gif", ".mp4", ".png", ".svg", ".avif"]
REMOTE_IMAGE_PATTERN = re.compile(r"^\!\[(.*?)\]\((http.*?)\)$")
LOCAL_IMAGE_PATTERN = re.compile(r"^\!\[(.*?)\]\((.*?)\)$")


def optimize_image_file(
    image_filename: Path,
    *,
    md_dir: Path,
    image_path: str,
    image_folder: str = "img",
    is_convert_png_to_avif: bool = False,
    is_compare_png_avif_sizes: bool = False,
    max_size: int | None = None,
) -> tuple[Path, str] | None:
    """Optimize a local image file and copy it to the target location.

    Returns:

    - `tuple[Path, str] | None`: New absolute path and relative Markdown path, or
    `None` when optimisation did not produce output.

    """
    ext = image_filename.suffix.lower()
    if ext not in SUPPORTED_IMAGE_EXTENSIONS:
        return None

    if _is_already_optimized(image_filename, ext):
        return None

    with TemporaryDirectory() as temp_folder:
        temp_folder_path = Path(temp_folder)
        temp_image_filename = temp_folder_path / image_filename.name
        shutil.copy(image_filename, temp_image_filename)

        optimized_images_dir = _run_image_optimize(
            temp_folder,
            ext=ext,
            is_convert_png_to_avif=is_convert_png_to_avif,
            is_compare_png_avif_sizes=is_compare_png_avif_sizes,
            max_size=max_size,
        )

        new_ext = _determine_new_extension(
            ext,
            optimized_images_dir=optimized_images_dir,
            image_stem=image_filename.stem,
            is_convert_png_to_avif=is_convert_png_to_avif,
            is_compare_png_avif_sizes=is_compare_png_avif_sizes,
        )
        optimized_image = optimized_images_dir / f"{image_filename.stem}{new_ext}"
        if not optimized_image.exists():
            return None

        if Path(image_path).is_absolute():
            new_image_path = image_filename.with_suffix(new_ext)
            new_image_rel_path = str(new_image_path)
        else:
            img_folder_path = md_dir / image_folder
            img_folder_path.mkdir(exist_ok=True)
            new_image_path = img_folder_path / f"{image_filename.stem}{new_ext}"
            new_image_rel_path = f"{image_folder}/{image_filename.stem}{new_ext}"

        if image_filename.exists():
            image_filename.unlink()
        shutil.copy(optimized_image, new_image_path)
        return new_image_path, new_image_rel_path


def optimize_images_in_md_file(
    filename: Path | str,
    *,
    is_convert_png_to_avif: bool = False,
    is_compare_png_avif_sizes: bool = False,
    max_size: int | None = None,
    filter_names: set[str] | None = None,
) -> str:
    """Optimise images in a Markdown file and write changes when content differs."""
    path = Path(filename)
    document = path.read_text(encoding="utf-8")
    document_new = transform_markdown_content(
        document,
        path.parent,
        filter_names=filter_names,
        is_convert_png_to_avif=is_convert_png_to_avif,
        is_compare_png_avif_sizes=is_compare_png_avif_sizes,
        max_size=max_size,
    )
    if document != document_new:
        path.write_text(document_new, encoding="utf-8")
        return f"✅ File {path} applied."
    return "File is not changed."


def optimize_single_image_for_template(
    image_path: str,
    image_save_dir: Path,
    max_size: int | None = None,
    image_folder: str = "img",
) -> str:
    """Optimise one image for template workflows and return the new relative path."""
    image_filename = Path(image_path) if Path(image_path).is_absolute() else (image_save_dir / image_path)
    if not image_filename.exists():
        return image_path

    result = optimize_image_file(
        image_filename,
        md_dir=image_save_dir,
        image_path=image_path,
        image_folder=image_folder,
        is_compare_png_avif_sizes=True,
        max_size=max_size,
    )
    if result is None:
        return image_path

    _new_image_path, new_image_rel_path = result
    return new_image_rel_path.replace("\\", "/")


def process_markdown_image_line(
    markdown_line: str,
    path_md: Path | str,
    *,
    filter_names: set[str] | None = None,
    image_folder: str = "img",
    is_convert_png_to_avif: bool = False,
    is_compare_png_avif_sizes: bool = False,
    max_size: int | None = None,
) -> str:
    """Process a single Markdown line and optimise any matching local image reference."""
    if REMOTE_IMAGE_PATTERN.search(markdown_line.strip()):
        return markdown_line

    local_match = LOCAL_IMAGE_PATTERN.search(markdown_line.strip())
    if not local_match:
        return markdown_line

    alt_text = local_match.group(1)
    image_path = local_match.group(2)
    if image_path.startswith("http"):
        return markdown_line

    md_dir = _resolve_md_dir(path_md)
    image_filename = Path(image_path) if Path(image_path).is_absolute() else md_dir / image_path
    if not image_filename.exists():
        return markdown_line
    if filter_names is not None and image_filename.name not in filter_names:
        return markdown_line

    result = optimize_image_file(
        image_filename,
        md_dir=md_dir,
        image_path=image_path,
        image_folder=image_folder,
        is_convert_png_to_avif=is_convert_png_to_avif,
        is_compare_png_avif_sizes=is_compare_png_avif_sizes,
        max_size=max_size,
    )
    if result is None:
        return markdown_line

    _new_image_path, new_image_rel_path = result
    return f"![{alt_text}]({new_image_rel_path})"


def transform_markdown_content(
    markdown_text: str,
    path_md: Path | str,
    *,
    filter_names: set[str] | None = None,
    image_folder: str = "img",
    is_convert_png_to_avif: bool = False,
    is_compare_png_avif_sizes: bool = False,
    max_size: int | None = None,
) -> str:
    """Optimise local images referenced in Markdown content, preserving YAML and code blocks."""
    yaml_md, content_md = h.md.split_yaml_content(markdown_text)

    new_lines = []
    lines = content_md.split("\n")
    for line_content, is_code_block in h.md.identify_code_blocks(lines):
        if is_code_block:
            new_lines.append(line_content)
            continue
        new_lines.append(
            process_markdown_image_line(
                line_content,
                path_md,
                filter_names=filter_names,
                image_folder=image_folder,
                is_convert_png_to_avif=is_convert_png_to_avif,
                is_compare_png_avif_sizes=is_compare_png_avif_sizes,
                max_size=max_size,
            )
        )
    content_md = "\n".join(new_lines)
    return yaml_md + "\n\n" + content_md


def _determine_new_extension(
    ext: str,
    *,
    optimized_images_dir: Path,
    image_stem: str,
    is_convert_png_to_avif: bool = False,
    is_compare_png_avif_sizes: bool = False,
) -> str:
    new_ext = ext
    if ext in [".jpg", ".jpeg", ".webp", ".gif", ".mp4"] or (
        ext == ".png"
        and (
            (is_compare_png_avif_sizes and (optimized_images_dir / f"{image_stem}.avif").exists())
            or is_convert_png_to_avif
        )
    ):
        new_ext = ".avif"
    return new_ext


def _is_already_optimized(image_filename: Path, ext: str) -> bool:
    """Return `True` if the image is already in the pipeline's output form."""
    if ext == ".avif":
        return True
    if ext == ".png":
        try:
            with Image.open(image_filename) as img:
                return img.mode == "P"
        except (OSError, ValueError):
            return False
    return False


def _resolve_md_dir(path_md: Path | str) -> Path:
    path = Path(path_md) if isinstance(path_md, str) else path_md
    return path.parent if path.is_file() else path


def _run_image_optimize(
    temp_folder: str,
    *,
    ext: str,
    is_convert_png_to_avif: bool = False,
    is_compare_png_avif_sizes: bool = False,
    max_size: int | None = None,
) -> Path:
    """Optimize images in a temporary folder and return the output directory."""
    temp_path = Path(temp_folder)
    output_dir = temp_path / "temp"
    project_root = h.dev.get_project_root()
    compare_png_avif = is_compare_png_avif_sizes and ext == ".png"
    convert_png_to_avif = is_convert_png_to_avif and ext == ".png" and not compare_png_avif
    optimize_images_in_folder(
        temp_path,
        output_dir,
        project_root,
        max_size=max_size,
        compare_png_avif=compare_png_avif,
        convert_png_to_avif=convert_png_to_avif,
    )
    return output_dir
