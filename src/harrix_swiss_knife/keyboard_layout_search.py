"""Search helpers that tolerate EN/RU keyboard layout mistakes."""

from __future__ import annotations

from harrix_pylib.funcs_text import autocomplete_match_tier, swap_keyboard_layout, text_matches_autocomplete

from harrix_swiss_knife.action_title import strip_md_inline_code_markers
from harrix_swiss_knife.cli_menu import CLI_MENU_SUFFIX

__all__ = [
    "autocomplete_match_tier",
    "command_matches_search",
    "normalize_command_title",
    "swap_keyboard_layout",
    "text_matches_autocomplete",
]

_BOLD_TITLE_PREFIX = "★ "


def command_matches_search(title: str, query: str) -> bool:
    """Return `True` if query matches title, including EN/RU layout mistakes.

    Empty query matches everything.

    """
    needle = query.strip()
    if not needle:
        return True

    haystack = normalize_command_title(title)
    needle_fold = needle.casefold()
    swapped_fold = swap_keyboard_layout(needle).casefold()
    return needle_fold in haystack or swapped_fold in haystack


def normalize_command_title(title: str) -> str:
    """Normalize a menu title for search comparison."""
    text = strip_md_inline_code_markers(title.strip())
    text = text.removeprefix(_BOLD_TITLE_PREFIX)
    if CLI_MENU_SUFFIX and text.endswith(CLI_MENU_SUFFIX):
        text = text[: -len(CLI_MENU_SUFFIX)]
    return text.strip().casefold()
