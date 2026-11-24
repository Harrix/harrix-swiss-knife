"""Tests for action added-at helpers."""

from __future__ import annotations

from pathlib import Path

from harrix_swiss_knife.action_added_at import sort_items_newest_first, write_action_added_at


def test_sort_items_newest_first_orders_dated_descending(tmp_path: Path) -> None:
    mapping_path = tmp_path / "action_added_at.json"
    write_action_added_at(
        {
            "OnA": "2023-01-01T00:00:00+00:00",
            "OnB": "2025-01-01T00:00:00+00:00",
            "OnC": "2024-01-01T00:00:00+00:00",
        },
        path=mapping_path,
    )
    ordered = sort_items_newest_first(
        ["OnA", "OnB", "OnC"],
        class_name_of=lambda name: name,
        path=mapping_path,
    )
    assert ordered == ["OnB", "OnC", "OnA"]


def test_sort_items_newest_first_puts_missing_dates_first(tmp_path: Path) -> None:
    mapping_path = tmp_path / "action_added_at.json"
    write_action_added_at(
        {
            "OnOld": "2020-01-01T00:00:00+00:00",
            "OnNew": "2024-06-01T00:00:00+00:00",
        },
        path=mapping_path,
    )
    ordered = sort_items_newest_first(
        ["OnOld", "OnMissing", "OnNew", "OnAlsoMissing"],
        class_name_of=lambda name: name,
        path=mapping_path,
    )
    assert ordered[:2] == ["OnAlsoMissing", "OnMissing"]
    assert ordered[2:] == ["OnNew", "OnOld"]
