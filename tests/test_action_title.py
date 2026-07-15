"""Tests for Markdown inline-code stripping in action titles."""

from harrix_swiss_knife.action_title import strip_md_inline_code_markers
from harrix_swiss_knife.keyboard_layout_search import normalize_command_title


def test_strip_md_inline_code_markers() -> None:
    assert strip_md_inline_code_markers("Open `config.json`") == "Open config.json"
    assert strip_md_inline_code_markers("No markers") == "No markers"
    assert strip_md_inline_code_markers("`a` and `b`") == "a and b"


def test_normalize_command_title_strips_backticks() -> None:
    assert normalize_command_title("Open `config.json`") == "open config.json"
