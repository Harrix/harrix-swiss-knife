"""Tests for BotHub image OCR + translate prompt helpers."""

from __future__ import annotations

import pytest

from harrix_swiss_knife.integrations.bothub.image_ocr_translate import (
    build_image_ocr_translate_prompt,
    get_image_ocr_translate_prompt_template,
)


def test_get_image_ocr_translate_prompt_template() -> None:
    config = {"prompts": {"image_ocr_translate": "OCR and translate {{LOCAL_LANGUAGE}}"}}
    assert get_image_ocr_translate_prompt_template(config) == "OCR and translate {{LOCAL_LANGUAGE}}"
    assert get_image_ocr_translate_prompt_template({}) is None


def test_build_image_ocr_translate_prompt_requires_api_key() -> None:
    config = {
        "prompts": {"image_ocr_translate": "OCR into {{LOCAL_LANGUAGE}} ({{LOCAL_LANGUAGE_CODE}})"},
        "bothub": {"api_key": ""},
        "apps": {"local_language": "ru"},
    }
    with pytest.raises(ValueError, match="API key"):
        build_image_ocr_translate_prompt(config)
