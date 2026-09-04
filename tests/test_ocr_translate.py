"""Tests for OCR + translate parsing used by screenshot translate."""

# ruff: noqa: RUF001

from __future__ import annotations

from harrix_swiss_knife.actions.common.ocr_translate import (
    OcrTranslateResult,
    parse_ocr_translate_response,
)


def test_parse_ocr_translate_local_language_only() -> None:
    result = parse_ocr_translate_response(
        '{"language":"ru","is_local":true,"original":"Привет","translation":""}',
        local_language_code="ru",
    )
    assert result == OcrTranslateResult(
        language="ru",
        is_local=True,
        original="Привет",
        translation="",
    )
    assert result.display_text == "Привет"


def test_parse_ocr_translate_foreign_with_translation() -> None:
    result = parse_ocr_translate_response(
        """
        ```json
        {
          "language": "en",
          "is_local": false,
          "original": "Hello\\nworld",
          "translation": "Привет\\nмир"
        }
        ```
        """,
        local_language_code="ru",
    )
    assert result.is_local is False
    assert result.original == "Hello\nworld"
    assert result.translation == "Привет\nмир"
    assert result.display_text == "Привет\nмир"


def test_parse_ocr_translate_falls_back_to_plain_text() -> None:
    result = parse_ocr_translate_response("Just plain OCR text", local_language_code="ru")
    assert result.is_local is True
    assert result.original == "Just plain OCR text"
    assert result.translation == ""


def test_parse_ocr_translate_empty_json() -> None:
    result = parse_ocr_translate_response(
        '{"language":"und","is_local":true,"original":"","translation":""}',
        local_language_code="ru",
    )
    assert result.original == ""
    assert result.display_text == ""
