"""Tests for OCR → Markdown formatting helpers."""

from __future__ import annotations

from pathlib import Path

from harrix_swiss_knife.actions.markdown.ocr_markdown import (
    combine_markdown_sections,
    default_markdown_base,
    format_ocr_body,
    image_link_path,
    ocr_text_to_markdown_section,
    suggest_markdown_filename,
    title_from_image_path,
)


def test_title_from_image_path_uses_date() -> None:
    path = Path("2014/img/2014-01-01-scan.avif")
    assert title_from_image_path(path) == "2014-01-01"


def test_title_from_image_path_falls_back_to_stem() -> None:
    assert title_from_image_path(Path("notes/scan-page-1.png")) == "scan-page-1"


def test_default_markdown_base_uses_year_folder_for_img_subdir() -> None:
    images = [Path("2014/img/2014-01-01-a.avif"), Path("2014/img/2014-01-02-b.avif")]
    assert default_markdown_base(images) == Path("2014")


def test_image_link_path_is_relative_to_base() -> None:
    image = Path("2014/img/2014-01-01-scan.avif")
    assert image_link_path(image, Path("2014")) == "img/2014-01-01-scan.avif"


def test_format_ocr_body_joins_paragraphs() -> None:
    text = "First paragraph\n\nSecond paragraph\n"
    assert format_ocr_body(text) == "First paragraph\n\nSecond paragraph"


def test_ocr_text_to_markdown_section() -> None:
    image = Path("2014/img/2014-01-01-scan.avif")
    section = ocr_text_to_markdown_section("Line one\n\nLine two", image, Path("2014"))
    assert section == ("# 2014-01-01\n\n![2014-01-01-scan](img/2014-01-01-scan.avif)\n\nLine one\n\nLine two\n")


def test_combine_markdown_sections() -> None:
    combined = combine_markdown_sections(["# One\n", "# Two\n"])
    assert combined == "# One\n\n---\n\n# Two"


def test_suggest_markdown_filename_single_image() -> None:
    images = [Path("2014/img/2014-05-15-scan.avif")]
    assert suggest_markdown_filename(images) == "2014-05-15.md"
