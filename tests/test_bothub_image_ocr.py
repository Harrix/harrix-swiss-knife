"""Tests for BotHub image OCR helpers."""

from __future__ import annotations

from pathlib import Path

import pytest

from harrix_swiss_knife.integrations.bothub.image import image_bytes_and_mime, image_mime_from_suffix
from harrix_swiss_knife.integrations.bothub.image_ocr import build_image_ocr_prompt, get_image_ocr_prompt_template


def test_image_mime_from_suffix() -> None:
    assert image_mime_from_suffix(".png") == "image/png"
    assert image_mime_from_suffix(".JPG") == "image/jpeg"
    assert image_mime_from_suffix(".txt") is None


def test_image_bytes_and_mime(tmp_path: Path) -> None:
    image_file = tmp_path / "sample.png"
    image_file.write_bytes(b"\x89PNG\r\n\x1a\n" + b"x" * 32)
    data, mime = image_bytes_and_mime(image_file)
    assert len(data) > 0
    assert mime == "image/png"


def test_image_bytes_and_mime_rejects_empty(tmp_path: Path) -> None:
    image_file = tmp_path / "empty.png"
    image_file.write_bytes(b"")
    with pytest.raises(ValueError, match="empty"):
        image_bytes_and_mime(image_file)


def test_get_image_ocr_prompt_template() -> None:
    config = {"prompts": {"image_ocr_to_markdown": "Recognize text"}}
    assert get_image_ocr_prompt_template(config) == "Recognize text"
    assert get_image_ocr_prompt_template({}) is None


def test_build_image_ocr_prompt_requires_api_key() -> None:
    config = {
        "prompts": {"image_ocr_to_markdown": "Recognize text"},
        "bothub": {"api_key": ""},
    }
    with pytest.raises(ValueError, match="API key"):
        build_image_ocr_prompt(config)
