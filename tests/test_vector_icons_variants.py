"""Tests for Vector Icons catalog variants and the right-hand variants panel."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication, QWidget

from harrix_swiss_knife.apps.icons.catalog import (
    IconFamily,
    IconVariant,
    delete_icon_family,
    is_note_icons_repo,
    load_catalog,
    open_icons_folder,
    rebuild_catalog,
)
from harrix_swiss_knife.apps.icons.lightbox import IconLightboxDialog
from harrix_swiss_knife.apps.icons.trademark_update import TRADEMARK_WARNING, update_trademark_files
from harrix_swiss_knife.apps.icons.variant_view import GridEntry
from harrix_swiss_knife.apps.icons.widgets import (
    DraggableIconList,
    VariantsPanel,
    is_svg_icon_path,
    placeholder_pixmap,
)

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


def _write_svg(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_MIN_SVG, encoding="utf-8")


def _note_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "Harrix-Vector-Icons"
    note = repo / "icons" / "building__garage"
    _write_svg(note / "featured-image.svg")
    _write_svg(note / "img" / "building__garage_01.svg")
    _write_svg(note / "img" / "building__garage_black.svg")
    catalog = {
        "version": 1,
        "generated_at": "2026-01-01T00:00:00Z",
        "icons": [
            {
                "id": "building__garage",
                "title": "Garage",
                "date": "2020-07-19",
                "categories": ["building"],
                "tags": ["garage"],
                "folder": "icons/building__garage",
                "featured": "featured-image.svg",
                "featured_hash": "abc",
                "variants": [
                    {"file": "img/building__garage_01.svg", "name": "building__garage_01", "hash": "1"},
                    {"file": "img/building__garage_black.svg", "name": "building__garage_black", "hash": "2"},
                ],
            },
        ],
    }
    (repo / "catalog.json").write_text(json.dumps(catalog), encoding="utf-8")
    return repo


def test_load_catalog_keeps_variants(tmp_path: Path) -> None:
    repo = _note_repo(tmp_path)
    catalog = load_catalog(repo)
    assert len(catalog.icons) == 1
    family = catalog.icons[0]
    assert family.date == "2020-07-19"
    assert [item.name for item in family.variants] == ["building__garage_01", "building__garage_black"]


def test_open_note_repo_does_not_flatten_nested_svgs(tmp_path: Path) -> None:
    repo = _note_repo(tmp_path)
    catalog = open_icons_folder(repo)
    assert catalog.kind == "note"
    assert len(catalog.icons) == 1
    assert len(catalog.icons[0].variants) == 2


def test_variants_panel_lists_family_files(qapp: QApplication, tmp_path: Path) -> None:  # noqa: ARG001
    repo = _note_repo(tmp_path)
    family = load_catalog(repo).icons[0]
    panel = VariantsPanel(thumb_size=64)
    panel.resize(280, 600)
    panel.show()
    QApplication.processEvents()
    panel.show_family(family, repo)
    QApplication.processEvents()
    assert panel.list.count() == 2
    first = panel.list.item(0)
    assert first is not None
    assert first.text() == "building__garage_01"
    rect = panel.list.visualItemRect(first)
    assert rect.width() > 0
    assert rect.height() > 0


def test_set_grid_entries_does_not_emit_cleared_selection(qapp: QApplication, tmp_path: Path) -> None:  # noqa: ARG001
    repo = _note_repo(tmp_path)
    family = load_catalog(repo).icons[0]
    featured = family.featured_path(repo)
    assert featured is not None
    lst = DraggableIconList(icon_size=64, dual_line_labels=True)
    signals: list[object] = []
    lst.family_selected.connect(signals.append)
    placeholder = placeholder_pixmap(64)
    lst.set_grid_entries(
        [GridEntry(family=family, svg_path=featured)],
        pixmaps_by_path={str(featured): placeholder},
        placeholder=placeholder,
    )
    assert signals == []
    assert lst.currentItem() is None


def test_item_pressed_emits_family_with_variants(qapp: QApplication, tmp_path: Path) -> None:  # noqa: ARG001
    repo = _note_repo(tmp_path)
    family = load_catalog(repo).icons[0]
    featured = family.featured_path(repo)
    assert featured is not None
    lst = DraggableIconList(icon_size=64, dual_line_labels=True)
    received: list[IconFamily] = []
    lst.family_selected.connect(lambda item: received.append(item) if isinstance(item, IconFamily) else None)
    placeholder = placeholder_pixmap(64)
    lst.set_grid_entries(
        [GridEntry(family=family, svg_path=featured)],
        pixmaps_by_path={str(featured): placeholder},
        placeholder=placeholder,
    )
    item = lst.item(0)
    assert item is not None
    lst.itemPressed.emit(item)
    assert received
    assert received[-1].id == family.id
    assert len(received[-1].variants) == 2
    assert received[-1].variants[0].file == "img/building__garage_01.svg"


def test_rebuild_catalog_title_prefers_yaml_then_h1(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    note = repo / "icons" / "clothes__suit"
    _write_svg(note / "featured-image.svg")
    (note / "clothes__suit.md").write_text(
        "---\ndate: 2020-07-19\ncategories: [clothes]\ntags: [suit]\ntitle: Yaml Title\n---\n\n# Suit\n",
        encoding="utf-8",
    )
    catalog = rebuild_catalog(repo)
    assert catalog.icons[0].title == "Yaml Title"
    assert catalog.icons[0].date == "2020-07-19"


def test_rebuild_catalog_title_from_h1(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    note = repo / "icons" / "clothes__suit"
    _write_svg(note / "featured-image.svg")
    (note / "clothes__suit.md").write_text(
        "---\ndate: 2020-07-19\ncategories: [clothes]\ntags: [suit]\n---\n\n# Suit\n",
        encoding="utf-8",
    )
    catalog = rebuild_catalog(repo)
    assert catalog.icons[0].title == "Suit"


def test_rebuild_catalog_title_from_id(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    note = repo / "icons" / "clothes__suit"
    _write_svg(note / "featured-image.svg")
    (note / "clothes__suit.md").write_text(
        "---\ndate: 2020-07-19\ncategories: [clothes]\ntags: [suit]\n---\n\nNo heading.\n",
        encoding="utf-8",
    )
    catalog = rebuild_catalog(repo)
    assert catalog.icons[0].title == "Suit"


def test_rebuild_catalog_nested_category_folder(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    note = repo / "icons" / "clothes" / "clothes__suit"
    _write_svg(note / "featured-image.svg")
    (note / "clothes__suit.md").write_text(
        "---\ndate: 2020-07-19\ncategories: [clothes]\ntags: [suit]\n---\n\n# Suit\n",
        encoding="utf-8",
    )
    catalog = rebuild_catalog(repo)
    assert catalog.icons[0].id == "clothes__suit"
    assert catalog.icons[0].title == "Suit"
    assert catalog.icons[0].folder == "icons/clothes/clothes__suit"
    assert catalog.icons[0].featured_path(repo) == note / "featured-image.svg"


def test_update_trademark_files_changes_only_note_and_catalog_entry(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    note = repo / "icons" / "fiction_robot" / "fiction_robot__marvin"
    _write_svg(note / "featured-image.svg")
    md_path = note / "fiction_robot__marvin.md"
    md_path.write_text(
        "---\ncategories: [fiction_robot]\ntags: [marvin]\n---\n\n"
        "# Robot Marvin\n\n![Featured image](featured-image.svg)\n",
        encoding="utf-8",
    )
    rebuild_catalog(repo)
    catalog_path = repo / "catalog.json"

    update_trademark_files(
        md_path=md_path,
        catalog_path=catalog_path,
        family_id="fiction_robot__marvin",
        enabled=True,
    )

    enabled_text = md_path.read_text(encoding="utf-8")
    assert "trademark: true" in enabled_text
    assert f"# Robot Marvin\n\n{TRADEMARK_WARNING}\n\n" in enabled_text
    enabled_catalog = load_catalog(repo)
    assert enabled_catalog.icons[0].trademark is True

    update_trademark_files(
        md_path=md_path,
        catalog_path=catalog_path,
        family_id="fiction_robot__marvin",
        enabled=False,
    )

    disabled_text = md_path.read_text(encoding="utf-8")
    assert "trademark:" not in disabled_text
    assert TRADEMARK_WARNING not in disabled_text
    assert "# Robot Marvin\n\n![Featured image]" in disabled_text
    disabled_catalog = load_catalog(repo)
    assert disabled_catalog.icons[0].trademark is False


def test_rebuild_catalog_mixed_flat_and_nested(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    nested = repo / "icons" / "clothes" / "clothes__suit"
    flat = repo / "icons" / "building__garage"
    _write_svg(nested / "featured-image.svg")
    _write_svg(flat / "featured-image.svg")
    catalog = rebuild_catalog(repo)
    by_id = {item.id: item for item in catalog.icons}
    assert by_id["clothes__suit"].folder == "icons/clothes/clothes__suit"
    assert by_id["building__garage"].folder == "icons/building__garage"


def test_is_note_icons_repo_nested_without_catalog(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write_svg(repo / "icons" / "building" / "building__garage" / "featured-image.svg")
    assert is_note_icons_repo(repo)
    catalog = open_icons_folder(repo)
    assert catalog.kind == "note"
    assert catalog.icons[0].id == "building__garage"


def test_delete_nested_note_family_prunes_empty_category(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    note = repo / "icons" / "building" / "building__garage"
    sibling = repo / "icons" / "building" / "building__house"
    other = repo / "icons" / "clothes" / "clothes__suit"
    _write_svg(note / "featured-image.svg")
    _write_svg(sibling / "featured-image.svg")
    _write_svg(other / "featured-image.svg")
    catalog = rebuild_catalog(repo)
    family = next(item for item in catalog.icons if item.id == "building__garage")
    delete_icon_family(family, repo, kind="note")
    assert not note.exists()
    assert sibling.is_dir()
    assert (repo / "icons" / "building").is_dir()
    leftover = next(item for item in rebuild_catalog(repo).icons if item.id == "building__house")
    delete_icon_family(leftover, repo, kind="note")
    assert not (repo / "icons" / "building").exists()
    assert other.is_dir()


def test_icon_variant_absolute_path(tmp_path: Path) -> None:
    repo = _note_repo(tmp_path)
    variant = IconVariant(file="img/building__garage_01.svg", name="building__garage_01", hash="1")
    path = variant.absolute_path(repo, "icons/building__garage")
    assert path.is_file()


def test_icon_lightbox_navigates_and_zooms(tmp_path: Path, qapp: QApplication) -> None:  # noqa: ARG001
    first = tmp_path / "first.svg"
    second = tmp_path / "second.svg"
    _write_svg(first)
    _write_svg(second)

    dialog = IconLightboxDialog([first, second], current_index=1)
    dialog.resize(800, 600)
    assert dialog.current_index == 1
    assert dialog.canvas.zoom == 1.0

    dialog.show_next()
    assert dialog.current_index == 0
    dialog.show_previous()
    assert dialog.current_index == 1
    dialog.canvas.zoom_by(2.0)
    assert dialog.canvas.zoom == 2.0
    dialog.close()


def test_icon_lightbox_fits_parent_window(tmp_path: Path, qapp: QApplication) -> None:
    svg = tmp_path / "icon.svg"
    _write_svg(svg)
    owner = QWidget()
    owner.resize(640, 480)
    owner.show()
    qapp.processEvents()

    dialog = IconLightboxDialog([svg], parent=owner)
    assert dialog.size() == owner.size()

    dialog.close()
    owner.close()


def test_icon_lightbox_backdrop_swatches_have_no_labels(tmp_path: Path, qapp: QApplication) -> None:  # noqa: ARG001
    svg = tmp_path / "icon.svg"
    _write_svg(svg)
    dialog = IconLightboxDialog([svg])
    assert dialog._white_backdrop_button.text() == ""
    assert dialog._black_backdrop_button.text() == ""
    dialog._set_backdrop_color("black")
    assert dialog._black_backdrop_button.isChecked()
    dialog.close()


def test_delete_note_family_removes_folder_and_catalog_entry(tmp_path: Path) -> None:
    repo = _note_repo(tmp_path)
    other = repo / "icons" / "building__house"
    _write_svg(other / "featured-image.svg")
    family = load_catalog(repo).icons[0]
    delete_icon_family(family, repo, kind="note")
    assert not (repo / "icons" / "building__garage").exists()
    assert other.is_dir()
    catalog = rebuild_catalog(repo)
    assert [item.id for item in catalog.icons] == ["building__house"]


def test_delete_note_family_rejects_unsafe_folder(tmp_path: Path) -> None:
    repo = _note_repo(tmp_path)
    family = IconFamily(
        id="building__garage",
        title="Garage",
        categories=["building"],
        tags=[],
        folder="icons",
        featured="featured-image.svg",
        featured_hash="",
    )
    with pytest.raises(ValueError, match="unsafe folder"):
        delete_icon_family(family, repo, kind="note")
    assert (repo / "icons" / "building__garage").is_dir()


def test_delete_flat_family_unlinks_files(tmp_path: Path) -> None:
    dump = tmp_path / "dump"
    _write_svg(dump / "foo.svg")
    _write_svg(dump / "bar.svg")
    catalog = open_icons_folder(dump)
    assert catalog.kind == "flat"
    assert len(catalog.icons) == 2
    target = catalog.icons[0]
    delete_icon_family(target, dump, kind="flat")
    remaining = open_icons_folder(dump)
    assert [item.id for item in remaining.icons] == [item.id for item in catalog.icons if item.id != target.id]


def test_is_svg_icon_path() -> None:
    assert is_svg_icon_path(r"D:\icons\building__garage.svg")
    assert is_svg_icon_path("featured-image.SVG")
    assert not is_svg_icon_path(r"D:\icons\building__garage.ai")
    assert not is_svg_icon_path("")
    assert not is_svg_icon_path(None)
