"""Tests for food log JSON transfer format."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from harrix_swiss_knife.apps.food.food_log_transfer import (
    FORMAT_ID,
    FoodLogTransferItem,
    build_transfer_item_from_log_row,
    group_items_by_date,
    items_to_tsv,
    name_en_lookup,
    parse_transfer_file,
    parse_transfer_payload,
    transfer_filename_for_date,
    write_transfer_files,
)


def test_build_transfer_item_weight_mode() -> None:
    item = build_transfer_item_from_log_row(
        date="2026-09-16",
        name="Oatmeal",
        name_en="Oatmeal",
        weight=150,
        calories_per_100g=350,
        is_drink=False,
    )
    assert item is not None
    assert item.calories_per_100g == 350


def test_build_transfer_item_requires_calories() -> None:
    item = build_transfer_item_from_log_row(
        date="2026-09-16",
        name="Coffee",
        name_en=None,
        weight=250,
        calories_per_100g=None,
        is_drink=True,
    )
    assert item is None


def test_write_and_parse_roundtrip(tmp_path: Path) -> None:
    items = [
        FoodLogTransferItem(
            name="Oatmeal",
            name_en="Oatmeal",
            weight=150,
            is_drink=False,
            calories_per_100g=350,
            date="2026-09-16",
        ),
        FoodLogTransferItem(
            name="Soup",
            name_en=None,
            weight=300,
            is_drink=False,
            calories_per_100g=66.7,
            date="2026-09-17",
        ),
    ]
    written = write_transfer_files(items, directory=tmp_path)
    assert len(written) == 2
    assert written[0].name == "food-log-2026-09-16.json"
    assert written[1].name == "food-log-2026-09-17.json"
    payload = parse_transfer_file(written[0])
    assert payload.default_date == "2026-09-16"
    assert len(payload.items) == 1
    assert payload.items[0].name == "Oatmeal"
    assert name_en_lookup(payload.items)["oatmeal"] == "Oatmeal"


def test_write_single_path(tmp_path: Path) -> None:
    items = [
        FoodLogTransferItem(
            name="Tea",
            weight=200,
            is_drink=True,
            calories_per_100g=2.5,
            date="2026-09-16",
        ),
    ]
    target = tmp_path / "custom.json"
    written = write_transfer_files(items, single_path=target)
    assert written == [target]
    raw = json.loads(target.read_text(encoding="utf-8"))
    assert raw["format"] == FORMAT_ID
    assert raw["default_date"] == "2026-09-16"


def test_items_to_tsv() -> None:
    items = [
        FoodLogTransferItem(
            name="Rice",
            weight=100,
            is_drink=False,
            calories_per_100g=130,
            date="2026-09-16",
        ),
    ]
    assert items_to_tsv(items) == "Rice\t100\t130\tweight\tno"


def test_group_and_filename() -> None:
    items = [
        FoodLogTransferItem(
            name="A",
            weight=1,
            is_drink=False,
            calories_per_100g=1,
            date="2026-01-02",
        ),
        FoodLogTransferItem(
            name="B",
            weight=1,
            is_drink=False,
            calories_per_100g=1,
            date="2026-01-01",
        ),
    ]
    grouped = group_items_by_date(items)
    assert set(grouped) == {"2026-01-01", "2026-01-02"}
    assert transfer_filename_for_date("2026-01-01") == "food-log-2026-01-01.json"


def test_parse_legacy_portion_mode_converts_to_per_100g() -> None:
    payload = parse_transfer_payload(
        {
            "format": "harrix-food-log",
            "version": 1,
            "default_date": "2026-09-16",
            "items": [
                {
                    "name": "Coffee",
                    "weight": 250,
                    "calorie_mode": "portion",
                    "portion_calories": 85,
                    "is_drink": True,
                    "date": "2026-09-16",
                }
            ],
        }
    )
    assert payload.items[0].calories_per_100g == 34.0


def test_parse_rejects_wrong_format() -> None:
    with pytest.raises(ValueError, match="Unsupported format"):
        parse_transfer_payload({"format": "other", "version": 1, "default_date": "2026-01-01", "items": []})
