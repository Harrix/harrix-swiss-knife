"""OCR helpers: recognize text in images and format as Markdown."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
from PIL import Image

if TYPE_CHECKING:
    import easyocr

_DATE_IN_NAME = re.compile(r"(\d{4}-\d{2}-\d{2})")


def combine_markdown_sections(sections: list[str]) -> str:
    """Join per-image Markdown sections with horizontal rules."""
    return "\n\n---\n\n".join(section.strip() for section in sections)


def default_markdown_base(images: list[Path]) -> Path:
    """Pick a folder for relative image links (e.g. year folder when images live in ``img/``)."""
    if not images:
        msg = "images must not be empty"
        raise ValueError(msg)

    parents = {p.parent for p in images}
    if len(parents) == 1:
        parent = next(iter(parents))
        if parent.name == "img":
            return parent.parent
        return parent

    common = Path(os.path.commonpath([str(p.parent) for p in images]))
    if common.name == "img":
        return common.parent
    return common


def format_ocr_body(text: str) -> str:
    """Normalize OCR paragraphs for Markdown body text."""
    paragraphs = [paragraph.strip() for paragraph in text.split("\n") if paragraph.strip()]
    return "\n\n".join(paragraphs)


def image_link_path(image_path: Path, base_folder: Path) -> str:
    """Return a POSIX relative path for a Markdown image link."""
    try:
        return image_path.relative_to(base_folder).as_posix()
    except ValueError:
        return image_path.name


def ocr_image(path: Path, reader: easyocr.Reader) -> str:
    """Run EasyOCR on one image file and return paragraph-joined text."""
    with Image.open(path) as img:
        rgb = img.convert("RGB") if img.mode != "RGB" else img
        arr = np.array(rgb)
    lines = reader.readtext(arr, detail=0, paragraph=True)
    return "\n".join(lines)


def ocr_text_to_markdown_section(ocr_text: str, image_path: Path, base_folder: Path) -> str:
    """Build one Markdown section: heading, image embed, and recognized text."""
    title = title_from_image_path(image_path)
    link = image_link_path(image_path, base_folder)
    alt = image_path.stem
    body = format_ocr_body(ocr_text)
    if not body:
        body = "_No text recognized._"
    return f"# {title}\n\n![{alt}]({link})\n\n{body}\n"


def suggest_markdown_filename(images: list[Path]) -> str:
    """Suggest a default ``.md`` filename for OCR output."""
    if len(images) == 1:
        return f"{title_from_image_path(images[0])}.md"
    return "ocr-scans.md"


def title_from_image_path(path: Path) -> str:
    """Return ``YYYY-MM-DD`` from the filename when present, else the stem."""
    match = _DATE_IN_NAME.search(path.stem)
    return match.group(1) if match else path.stem
