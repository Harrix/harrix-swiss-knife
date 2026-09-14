"""Tests for Vector Icons grid sort helpers and settings."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import harrix_pylib as h

from harrix_swiss_knife.apps.icons import settings
from harrix_swiss_knife.apps.icons.catalog import IconFamily
from harrix_swiss_knife.apps.icons.settings import (
    GRID_SORT_ALPHA,
    GRID_SORT_DATE,
    GRID_SORT_DEFAULT,
    GRID_SORT_KEY,
    GRID_SORT_REVERSE,
    SHOW_NUMBERS_KEY,
    load_grid_sort_mode,
    load_show_numbers,
    save_grid_sort_mode,
    save_show_numbers,
)
from harrix_swiss_knife.apps.icons.variant_view import sort_icon_families

if TYPE_CHECKING:
    import pytest


def _family(family_id: str, *, title: str = "", date: str = "") -> IconFamily:
    return IconFamily(
        id=family_id,
        title=title or family_id,
        categories=["misc"],
        tags=[],
        folder=f"icons/misc/{family_id}",
        featured="featured-image.svg",
        featured_hash="",
        date=date,
    )


def _patch_config(monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    store: dict[str, Any] = {}

    def fake_load(_path: str, *, is_temp: bool = False) -> dict[str, Any]:
        _ = is_temp
        return dict(store)

    def fake_update(key: str, value: object, _path: str, *, is_temp: bool = False) -> None:
        _ = is_temp
        store[key] = value

    monkeypatch.setattr(h.dev, "config_load", fake_load)
    monkeypatch.setattr(h.dev, "config_update_value", fake_update)
    monkeypatch.setattr(settings, "_ensure_temp_config", lambda: None)
    return store


def test_sort_icon_families_modes() -> None:
    families = [
        _family("c", title="Charlie", date="2020-01-01"),
        _family("a", title="Alpha", date="2024-06-01"),
        _family("b", title="Bravo", date=""),
    ]
    assert [item.id for item in sort_icon_families(families, GRID_SORT_DEFAULT)] == ["c", "a", "b"]
    assert [item.id for item in sort_icon_families(families, GRID_SORT_ALPHA)] == ["a", "b", "c"]
    assert [item.id for item in sort_icon_families(families, GRID_SORT_DATE)] == ["a", "c", "b"]
    assert [item.id for item in sort_icon_families(families, GRID_SORT_REVERSE)] == ["b", "a", "c"]


def test_grid_sort_and_numbers_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    store = _patch_config(monkeypatch)
    assert load_grid_sort_mode() == GRID_SORT_DEFAULT
    assert load_show_numbers() is False
    assert save_grid_sort_mode(GRID_SORT_ALPHA) == GRID_SORT_ALPHA
    save_show_numbers(enabled=True)
    assert load_grid_sort_mode() == GRID_SORT_ALPHA
    assert load_show_numbers() is True
    assert store[GRID_SORT_KEY] == GRID_SORT_ALPHA
    assert store[SHOW_NUMBERS_KEY] is True
