"""Tests for BotHub text-translate-to-local prompt helpers."""

from __future__ import annotations

import pytest

from harrix_swiss_knife.integrations.bothub.text_translate import (
    build_text_translate_prompt,
    get_text_translate_prompt_template,
)


def test_get_text_translate_prompt_template() -> None:
    config = {"prompts": {"text_translate_to_local": "Translate into {{LOCAL_LANGUAGE}}: {{TEXT}}"}}
    assert get_text_translate_prompt_template(config) == "Translate into {{LOCAL_LANGUAGE}}: {{TEXT}}"
    assert get_text_translate_prompt_template({}) is None


def test_build_text_translate_prompt_requires_api_key() -> None:
    config = {
        "prompts": {
            "text_translate_to_local": "Translate into {{LOCAL_LANGUAGE}} ({{LOCAL_LANGUAGE_CODE}}):\n{{TEXT}}"
        },
        "bothub": {"api_key": ""},
        "apps": {"local_language": "ru"},
    }
    with pytest.raises(ValueError, match="API key"):
        build_text_translate_prompt("Hello", config)
