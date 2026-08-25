"""Parse and serialize snippet lists for bulk add and edit-all."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harrix_swiss_knife.apps.snippets.constants import ZONE_COLOR, ZONE_EMOJI, ZONE_PHRASE, ZONE_SYMBOL
from harrix_swiss_knife.keyboard_layout_search import command_matches_search

if TYPE_CHECKING:
    from collections.abc import Sequence

    from harrix_swiss_knife.apps.snippets.database_manager import SnippetItem


def display_text(value: str, hint: str, zone: str) -> str:
    """Return the list label for one item."""
    if zone in {ZONE_SYMBOL, ZONE_COLOR} and hint:
        return f"{value} [{hint}]"
    return value


def hint_tooltip(hint: str, fallback: str = "") -> str:
    """Return hover text without wrapping square brackets."""
    text = strip_wrapping_brackets(hint)
    return text or fallback


def item_matches_search(value: str, hint: str, query: str) -> bool:
    """Return whether value or hint matches `query` (case and layout insensitive)."""
    if command_matches_search(value, query):
        return True
    return bool(hint) and command_matches_search(hint, query)


def parse_bulk_lines(text: str, zone: str) -> list[tuple[str, str]]:
    """Parse a multiline editor payload into `(value, hint)` pairs."""
    items: list[tuple[str, str]] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if zone in {ZONE_PHRASE, ZONE_EMOJI}:
            items.append((line, ""))
            continue
        parsed = parse_value_hint_line(line)
        if parsed is None or not parsed[0]:
            continue
        items.append(parsed)
    return items


def parse_value_hint_line(line: str) -> tuple[str, str] | None:
    """Parse one bulk-edit line into `(value, hint)`.

    Empty lines are skipped (`None`). Phrases and emoji use the whole line as
    the value. Symbols and colors accept `value | hint` or `value: hint`.

    """
    text = line.strip()
    if not text:
        return None
    if " | " in text:
        value, hint = text.split(" | ", 1)
        return value.strip(), hint.strip()
    if text.startswith("#") and ":" in text:
        value, hint = text.split(":", 1)
        return value.strip(), hint.strip()
    return text, ""


def serialize_items(items: Sequence[SnippetItem], zone: str) -> str:
    """Serialize items for the edit-entire-list dialog."""
    lines: list[str] = []
    for item in items:
        if zone in {ZONE_SYMBOL, ZONE_COLOR} and item.hint:
            lines.append(f"{item.value} | {item.hint}")
        else:
            lines.append(item.value)
    return "\n".join(lines)


def strip_wrapping_brackets(text: str) -> str:
    """Remove one pair of surrounding `[]`, if present."""
    value = text.strip()
    if value.startswith("[") and value.endswith("]"):
        return value[1:-1].strip()
    return value
