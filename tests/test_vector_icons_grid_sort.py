"""Tests for Vector Icons grid sort helpers and settings."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import harrix_pylib as h
import pytest
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.apps.icons import settings
from harrix_swiss_knife.apps.icons.catalog import IconFamily
from harrix_swiss_knife.apps.icons.settings import (
    GRID_SORT_ALPHA,
    GRID_SORT_DATE,
    GRID_SORT_DEFAULT,
    GRID_SORT_KEY,
    GRID_SORT_LEGACY_REVERSE,
    GRID_SORT_REVERSE_KEY,
    SHOW_NUMBERS_KEY,
    load_grid_sort_mode,
    load_grid_sort_reverse,
    load_show_numbers,
    save_grid_sort_mode,
    save_grid_sort_reverse,
    save_show_numbers,
)
from harrix_swiss_knife.apps.icons.variant_view import GridEntry, sort_icon_families
from harrix_swiss_knife.apps.icons.widgets import ROLE_DATE, DraggableIconList, placeholder_pixmap


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


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
    assert [item.id for item in sort_icon_families(families, GRID_SORT_DEFAULT, reverse=True)] == ["b", "a", "c"]
    assert [item.id for item in sort_icon_families(families, GRID_SORT_ALPHA)] == ["a", "b", "c"]
    assert [item.id for item in sort_icon_families(families, GRID_SORT_ALPHA, reverse=True)] == ["c", "b", "a"]
    assert [item.id for item in sort_icon_families(families, GRID_SORT_DATE)] == ["a", "c", "b"]
    assert [item.id for item in sort_icon_families(families, GRID_SORT_DATE, reverse=True)] == ["c", "a", "b"]


def test_grid_sort_and_numbers_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    store = _patch_config(monkeypatch)
    assert load_grid_sort_mode() == GRID_SORT_DEFAULT
    assert load_grid_sort_reverse() is False
    assert load_show_numbers() is False
    assert save_grid_sort_mode(GRID_SORT_ALPHA) == GRID_SORT_ALPHA
    save_grid_sort_reverse(enabled=True)
    save_show_numbers(enabled=True)
    assert load_grid_sort_mode() == GRID_SORT_ALPHA
    assert load_grid_sort_reverse() is True
    assert load_show_numbers() is True
    assert store[GRID_SORT_KEY] == GRID_SORT_ALPHA
    assert store[GRID_SORT_REVERSE_KEY] is True
    assert store[SHOW_NUMBERS_KEY] is True


def test_legacy_reverse_sort_mode_migrates_to_flag(monkeypatch: pytest.MonkeyPatch) -> None:
    store = _patch_config(monkeypatch)
    store[GRID_SORT_KEY] = GRID_SORT_LEGACY_REVERSE
    assert load_grid_sort_mode() == GRID_SORT_DEFAULT
    assert load_grid_sort_reverse() is True


def test_grid_items_show_date_badge_when_sorted_by_date(tmp_path: Path, qapp: QApplication) -> None:  # noqa: ARG001
    svg = tmp_path / "icon.svg"
    svg.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="8" height="8"><rect width="8" height="8"/></svg>\n',
        encoding="utf-8",
    )
    family = _family("dated", date="2024-06-01")
    icon_list = DraggableIconList(dual_line_labels=True)
    icon_list.set_view_options(show_numbers=False, sort_mode=GRID_SORT_DATE)
    icon_list.append_grid_entries(
        [GridEntry(family=family, svg_path=svg, is_fallback=False)],
        pixmaps_by_path={},
        placeholder=placeholder_pixmap(64),
    )
    item = icon_list.item(0)
    assert item is not None
    assert item.data(ROLE_DATE) == "2024-06-01"

    icon_list.set_view_options(show_numbers=False, sort_mode=GRID_SORT_DEFAULT)
    icon_list.clear()
    icon_list.append_grid_entries(
        [GridEntry(family=family, svg_path=svg, is_fallback=False)],
        pixmaps_by_path={},
        placeholder=placeholder_pixmap(64),
    )
    item = icon_list.item(0)
    assert item is not None
    assert item.data(ROLE_DATE) == ""
