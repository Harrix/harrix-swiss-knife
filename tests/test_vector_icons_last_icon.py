"""Tests for remembering the last selected Vector Icons family per folder."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import harrix_pylib as h
import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.apps.icons import settings
from harrix_swiss_knife.apps.icons.catalog import IconFamily
from harrix_swiss_knife.apps.icons.settings import (
    PINNED_FOLDERS_KEY,
    load_last_folder,
    load_last_icon,
    pin_folder,
    save_last_folder,
    save_last_icon,
)
from harrix_swiss_knife.apps.icons.variant_view import GridEntry
from harrix_swiss_knife.apps.icons.widgets import DraggableIconList, placeholder_pixmap

_MIN_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32"><rect width="32" height="32" fill="#336699"/></svg>'
)


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_save_and_load_last_icon_per_folder(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
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

    first = tmp_path / "repo-a"
    second = tmp_path / "repo-b"
    first.mkdir()
    second.mkdir()

    save_last_icon(first, "building__garage")
    save_last_icon(second, "fiction__ufo")
    assert load_last_icon(first) == "building__garage"
    assert load_last_icon(second) == "fiction__ufo"

    save_last_icon(first, "clothes__suit")
    assert load_last_icon(first) == "clothes__suit"
    assert load_last_icon(second) == "fiction__ufo"


def test_save_and_load_last_folder(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
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

    first = tmp_path / "repo-a"
    second = tmp_path / "repo-b"
    first.mkdir()
    second.mkdir()

    save_last_folder(first)
    assert load_last_folder() == first
    save_last_folder(second)
    assert load_last_folder() == second


def test_pin_folder_saves_posix_style_paths(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    store: dict[str, Any] = {}

    def fake_load(_path: str, *, is_temp: bool = False) -> dict[str, Any]:
        _ = is_temp
        return dict(store)

    def fake_update(key: str, value: object, _path: str, *, is_temp: bool = False) -> None:
        _ = is_temp
        store[key] = value

    monkeypatch.setattr(h.dev, "config_load", fake_load)
    monkeypatch.setattr(h.dev, "config_update_value", fake_update)

    first = tmp_path / "repo-a"
    second = tmp_path / "repo-b"
    first.mkdir()
    second.mkdir()
    store[PINNED_FOLDERS_KEY] = [str(second)]

    pin_folder(first)

    raw = store.get(PINNED_FOLDERS_KEY)
    assert isinstance(raw, list)
    assert str(first.resolve().as_posix()) in raw
    assert str(second.resolve().as_posix()) in raw
    assert all("\\" not in item for item in raw if isinstance(item, str))


def test_select_family_scrolls_to_matching_tile(qapp: QApplication, tmp_path: Path) -> None:
    assert qapp is not None
    first = IconFamily(
        id="building__garage",
        title="Garage",
        categories=["building"],
        tags=["garage"],
        folder="icons/building__garage",
        featured="featured-image.svg",
        featured_hash="",
    )
    second = IconFamily(
        id="fiction__ufo",
        title="Ufo",
        categories=["fiction"],
        tags=["ufo"],
        folder="icons/fiction__ufo",
        featured="featured-image.svg",
        featured_hash="",
    )
    first_svg = tmp_path / "building__garage.svg"
    second_svg = tmp_path / "fiction__ufo.svg"
    first_svg.write_text(_MIN_SVG, encoding="utf-8")
    second_svg.write_text(_MIN_SVG, encoding="utf-8")
    placeholder = placeholder_pixmap(64)
    lst = DraggableIconList(icon_size=64, dual_line_labels=True)
    lst.set_grid_entries(
        [
            GridEntry(family=first, svg_path=first_svg),
            GridEntry(family=second, svg_path=second_svg),
        ],
        pixmaps_by_path={str(first_svg): placeholder, str(second_svg): placeholder},
        placeholder=placeholder,
    )
    assert lst.select_family("fiction__ufo")
    current = lst.currentItem()
    assert current is not None
    selected = current.data(Qt.ItemDataRole.UserRole)
    assert getattr(selected, "id", None) == "fiction__ufo"
    assert not lst.select_family("missing__icon")
