"""Tests for targeted catalog hash refresh and variants reload."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.apps.icons.catalog import (
    IconCatalog,
    IconFamily,
    IconVariant,
    refresh_hashes_for_paths,
    reload_family_variants,
    write_catalog_json,
)
from harrix_swiss_knife.apps.icons.widgets import DraggableIconList


def _write_svg(path: Path, mark: str = "black") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24">'
        f'<rect width="24" height="24" fill="{mark}"/></svg>\n',
        encoding="utf-8",
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


def test_refresh_hashes_for_paths_updates_only_touched_family(tmp_path: Path) -> None:
    note = tmp_path / "icons" / "building__garage"
    featured = note / "featured-image.svg"
    variant = note / "img" / "building__garage_01.svg"
    other_variant = note / "img" / "building__garage_02.svg"
    _write_svg(featured, "black")
    _write_svg(variant, "red")
    _write_svg(other_variant, "blue")

    family = IconFamily(
        id="building__garage",
        title="Garage",
        categories=["building"],
        tags=[],
        folder="icons/building__garage",
        featured="featured-image.svg",
        featured_hash="old-featured",
        variants=[
            IconVariant(file="img/building__garage_01.svg", name="building__garage_01", hash="old-01"),
            IconVariant(file="img/building__garage_02.svg", name="building__garage_02", hash="old-02"),
        ],
    )
    untouched = IconFamily(
        id="building__house",
        title="House",
        categories=["building"],
        tags=[],
        folder="icons/building__house",
        featured="featured-image.svg",
        featured_hash="keep-me",
        variants=[],
    )
    catalog = IconCatalog(version=1, generated_at="", icons=[family, untouched], repo_root=tmp_path, kind="note")

    affected = refresh_hashes_for_paths(catalog, [variant])
    assert [item.id for item in affected] == ["building__garage"]
    assert family.variants[0].hash != "old-01"
    assert family.variants[1].hash == "old-02"
    assert family.featured_hash == "old-featured"
    assert untouched.featured_hash == "keep-me"

    write_catalog_json(catalog)
    raw = json.loads((tmp_path / "catalog.json").read_text(encoding="utf-8"))
    garage = next(item for item in raw["icons"] if item["id"] == "building__garage")
    assert garage["variants"][0]["hash"] == family.variants[0].hash
    assert garage["featured_hash"] == "old-featured"


def test_reload_family_variants_picks_up_new_file(tmp_path: Path) -> None:
    note = tmp_path / "icons" / "building__garage"
    _write_svg(note / "featured-image.svg")
    _write_svg(note / "img" / "building__garage_01.svg")
    family = IconFamily(
        id="building__garage",
        title="Garage",
        categories=["building"],
        tags=[],
        folder="icons/building__garage",
        featured="featured-image.svg",
        featured_hash="old",
        variants=[
            IconVariant(file="img/building__garage_01.svg", name="building__garage_01", hash="old-01"),
        ],
    )
    _write_svg(note / "img" / "building__garage_new.svg", "green")
    assert reload_family_variants(family, tmp_path, kind="note")
    assert [item.name for item in family.variants] == ["building__garage_01", "building__garage_new"]
    assert not reload_family_variants(family, tmp_path, kind="note")


def test_variants_context_menu_emits_refresh(
    qapp: QApplication,  # noqa: ARG001
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    family = IconFamily(
        id="building__garage",
        title="Garage",
        categories=[],
        tags=[],
        folder="icons/building__garage",
        featured="featured-image.svg",
        featured_hash="",
        variants=[],
    )
    icon_list = DraggableIconList(variants_context=True)
    icon_list.set_variants_family(family)
    emitted: list[bool] = []
    icon_list.refresh_variants_requested.connect(lambda: emitted.append(True))

    class _FakeMenu:
        def __init__(self, *_args: object, **_kwargs: object) -> None:
            self._actions: list[object] = []

        def addAction(self, text: str) -> object:  # noqa: N802
            action = MagicMock()
            action.text.return_value = text
            self._actions.append(action)
            return action

        def addSeparator(self) -> None:  # noqa: N802
            return None

        def exec_(self, *_args: object) -> object:
            return self._actions[0]

    monkeypatch.setattr("harrix_swiss_knife.apps.icons.widgets.QMenu", _FakeMenu)
    monkeypatch.setattr(
        "harrix_swiss_knife.apps.icons.widgets.apply_leading_chrome_icons",
        lambda *_args, **_kwargs: None,
    )
    icon_list._exec_current_folder_context_menu(icon_list.rect().center())
    assert emitted == [True]


def test_main_grid_context_menu_emits_refresh_icons(
    qapp: QApplication,  # noqa: ARG001
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    icon_list = DraggableIconList(variants_context=False)
    emitted: list[bool] = []
    icon_list.refresh_icons_requested.connect(lambda: emitted.append(True))

    class _FakeMenu:
        def __init__(self, *_args: object, **_kwargs: object) -> None:
            self._actions: list[object] = []

        def addAction(self, text: str) -> object:  # noqa: N802
            action = MagicMock()
            action.text.return_value = text
            self._actions.append(action)
            return action

        def addMenu(self, _text: str) -> object:  # noqa: N802
            return self

        def addSeparator(self) -> None:  # noqa: N802
            return None

        def exec_(self, *_args: object) -> object:
            return next(action for action in self._actions if action.text() == "🔄 Refresh icons")

    monkeypatch.setattr("harrix_swiss_knife.apps.icons.widgets.QMenu", _FakeMenu)
    monkeypatch.setattr(
        "harrix_swiss_knife.apps.icons.widgets.apply_leading_chrome_icons",
        lambda *_args, **_kwargs: None,
    )
    icon_list._exec_current_folder_context_menu(icon_list.rect().center())
    assert emitted == [True]
