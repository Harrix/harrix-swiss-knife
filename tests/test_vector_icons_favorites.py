"""Tests for Vector Icons favorites persistence and sidebar order."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

import harrix_pylib as h

from harrix_swiss_knife.apps.icons import settings
from harrix_swiss_knife.apps.icons.settings import (
    FAVORITES_CATEGORY,
    add_favorites,
    is_favorites_category,
    load_favorites,
    remove_favorites,
    rename_favorite,
    sidebar_category_names,
    toggle_favorite,
)

if TYPE_CHECKING:
    import pytest


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


def test_toggle_favorite_is_per_folder(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_config(monkeypatch)
    first = tmp_path / "repo-a"
    second = tmp_path / "repo-b"
    first.mkdir()
    second.mkdir()

    ids, added = toggle_favorite(first, "building__garage")
    assert added is True
    assert ids == ["building__garage"]
    assert load_favorites(first) == ["building__garage"]
    assert load_favorites(second) == []

    ids, added = toggle_favorite(first, "building__garage")
    assert added is False
    assert ids == []
    assert load_favorites(first) == []


def test_add_and_remove_favorites_keep_order(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_config(monkeypatch)
    folder = tmp_path / "repo"
    folder.mkdir()

    assert add_favorites(folder, ["building__garage", "fiction__ufo"]) == ["building__garage", "fiction__ufo"]
    assert add_favorites(folder, ["fiction__ufo", "clothes__suit"]) == [
        "building__garage",
        "fiction__ufo",
        "clothes__suit",
    ]
    assert remove_favorites(folder, ["fiction__ufo"]) == ["building__garage", "clothes__suit"]


def test_rename_favorite_keeps_position(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_config(monkeypatch)
    folder = tmp_path / "repo"
    folder.mkdir()
    add_favorites(folder, ["old__house", "clothes__suit"])
    assert rename_favorite(folder, "old__house", "furniture__house") == ["furniture__house", "clothes__suit"]
    assert rename_favorite(folder, "missing__id", "other") == ["furniture__house", "clothes__suit"]


def test_sidebar_puts_favorites_first() -> None:
    assert sidebar_category_names(["building", "clothes"]) == [
        FAVORITES_CATEGORY,
        "building",
        "clothes",
    ]
    assert sidebar_category_names(["building", "Favorites", "clothes"]) == [
        FAVORITES_CATEGORY,
        "building",
        "clothes",
    ]
    assert is_favorites_category("favorites")
    assert not is_favorites_category("(All)")
