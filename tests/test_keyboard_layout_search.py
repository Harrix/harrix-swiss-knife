"""Tests for EN/RU keyboard layout tolerant command search."""

from harrix_swiss_knife.cli_menu import CLI_MENU_SUFFIX
from harrix_swiss_knife.keyboard_layout_search import (
    command_matches_search,
    normalize_command_title,
    swap_keyboard_layout,
)


def test_swap_keyboard_layout_qwerty_to_russian() -> None:
    assert swap_keyboard_layout("qwerty") == "йцукен"
    assert swap_keyboard_layout("йцукен") == "qwerty"


def test_swap_keyboard_layout_preserves_unknown_chars() -> None:
    assert swap_keyboard_layout("abc 123") == "фис 123"


def test_command_matches_search_case_insensitive() -> None:
    assert command_matches_search(f"Finance{CLI_MENU_SUFFIX}", "finance")
    assert command_matches_search("★ Bold Action", "bold")


def test_command_matches_search_wrong_layout() -> None:
    assert command_matches_search("Привет", "ghbdtn")
    assert command_matches_search("Finance", "аштфтсу")


def test_command_matches_search_empty_query() -> None:
    assert command_matches_search("Anything", "")
    assert command_matches_search("Anything", "   ")


def test_normalize_command_title_strips_prefix_and_cli_suffix() -> None:
    assert normalize_command_title(f"★ Hello{CLI_MENU_SUFFIX}") == "hello"
