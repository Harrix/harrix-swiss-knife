"""Tests for keyboard-shortcuts help helpers."""

from __future__ import annotations

from harrix_swiss_knife.apps.common.keyboard_shortcuts import (
    ShortcutHelpEntry,
    key_sequence_display,
    merge_shortcut_help,
    sort_shortcut_help,
)


def test_key_sequence_display_ctrl_f() -> None:
    text = key_sequence_display("Ctrl+F")
    assert "F" in text
    assert text


def test_merge_shortcut_help_dedupes() -> None:
    left = [ShortcutHelpEntry("Ctrl+C", "Copy", "Tables")]
    right = [
        ShortcutHelpEntry("Ctrl+C", "Copy", "Tables"),
        ShortcutHelpEntry("Delete", "Remove", "Tables"),
    ]
    merged = merge_shortcut_help(left, right)
    assert len(merged) == 2
    assert merged[1].keys == "Delete"


def test_sort_shortcut_help_orders_category_then_keys() -> None:
    rows = [
        ShortcutHelpEntry("Ctrl+V", "Paste", "Grid"),
        ShortcutHelpEntry("Ctrl+C", "Copy", "Grid"),
        ShortcutHelpEntry("F1", "Help", "Help"),
    ]
    sorted_rows = sort_shortcut_help(rows)
    assert [item.category for item in sorted_rows] == ["Grid", "Grid", "Help"]
    assert sorted_rows[0].keys == "Ctrl+C"
