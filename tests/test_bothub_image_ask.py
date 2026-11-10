"""Tests for BotHub screenshot Ask AI helpers."""

from __future__ import annotations

import pytest

from harrix_swiss_knife.integrations.bothub.image_ask import (
    build_image_ask_prompt,
    get_image_ask_prompt_template,
)


def test_get_image_ask_prompt_template() -> None:
    config = {"ai": {"prompts": {"image_ask": "Answer {{NOTE}}"}}}
    assert get_image_ask_prompt_template(config) == "Answer {{NOTE}}"
    assert get_image_ask_prompt_template({"prompts": {"image_ask": "Legacy {{NOTE}}"}}) == "Legacy {{NOTE}}"
    assert get_image_ask_prompt_template({}) is None


def test_build_image_ask_prompt_requires_api_key() -> None:
    config = {
        "prompts": {"image_ask": "Answer {{NOTE}}"},
        "bothub": {"api_key": ""},
    }
    with pytest.raises(ValueError, match="API key"):
        build_image_ask_prompt(config, "solve this")


def test_build_image_ask_prompt_inserts_note() -> None:
    config = {
        "prompts": {"image_ask": "Note:\n{{NOTE}}"},
        "bothub_api_key": "test-key",
    }
    assert build_image_ask_prompt(config, "  focus on step 2  ") == "Note:\nfocus on step 2"
    assert "none — answer based only on the screenshot" in build_image_ask_prompt(config, "   ")
