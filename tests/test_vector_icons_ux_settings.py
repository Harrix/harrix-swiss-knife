"""Tests for Vector Icons settings persistence and empty-grid CTA."""

from __future__ import annotations

from typing import Any

import harrix_pylib as h

from harrix_swiss_knife.apps.icons import settings
from harrix_swiss_knife.apps.icons.main import empty_grid_cta
from harrix_swiss_knife.apps.icons.settings import (
    LEFT_SPLITTER_SIZES_DEFAULT,
    LEFT_SPLITTER_SIZES_KEY,
    SPLITTER_SIZES_DEFAULT,
    SPLITTER_SIZES_KEY,
    VARIANT_VIEW_MODE_KEY,
    load_left_splitter_sizes,
    load_splitter_sizes,
    load_variant_view_mode,
    save_left_splitter_sizes,
    save_splitter_sizes,
    save_variant_view_mode,
)


def test_empty_grid_cta_no_folder() -> None:
    mode, message, primary, secondary = empty_grid_cta(
        has_folder=False,
        entry_count=0,
        search_query="",
        has_meta_filter=False,
    )
    assert mode == "no_folder"
    assert "Open folder" in (primary or "")
    assert secondary is None
    assert "folder" in message.casefold()


def test_empty_grid_cta_search_and_meta() -> None:
    mode, _message, primary, secondary = empty_grid_cta(
        has_folder=True,
        entry_count=0,
        search_query="robot",
        has_meta_filter=True,
    )
    assert mode == "no_search"
    assert primary == "Clear search"
    assert secondary == "Clear all filters"


def test_empty_grid_cta_has_tiles() -> None:
    mode, _message, primary, secondary = empty_grid_cta(
        has_folder=True,
        entry_count=3,
        search_query="x",
        has_meta_filter=True,
    )
    assert mode is None
    assert primary is None
    assert secondary is None


def test_variant_view_and_splitter_settings_roundtrip(monkeypatch: Any) -> None:
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

    assert load_variant_view_mode() == "featured"
    assert save_variant_view_mode("color") == "color"
    assert store[VARIANT_VIEW_MODE_KEY] == "color"
    assert load_variant_view_mode() == "color"

    assert load_splitter_sizes() == list(SPLITTER_SIZES_DEFAULT)
    assert save_splitter_sizes([180, 1000, 280]) == [180, 1000, 280]
    assert store[SPLITTER_SIZES_KEY] == [180, 1000, 280]
    assert load_splitter_sizes() == [180, 1000, 280]
    assert save_splitter_sizes([1]) == list(SPLITTER_SIZES_DEFAULT)

    assert load_left_splitter_sizes() == list(LEFT_SPLITTER_SIZES_DEFAULT)
    assert save_left_splitter_sizes([100, 200]) == [100, 200]
    assert store[LEFT_SPLITTER_SIZES_KEY] == [100, 200]
    assert load_left_splitter_sizes() == [100, 200]
