"""Tests for editing an existing Vector Icons note like Add Vector Image."""

from __future__ import annotations

from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.apps.icons.add_vector_dialog import AddVectorImageDialog
from harrix_swiss_knife.apps.icons.add_vector_meta import (
    NoteMeta,
    RepoMetaDefaults,
    extra_categories_for_family,
    note_meta_from_existing,
    sync_family_id_category,
)
from harrix_swiss_knife.apps.icons.catalog import rebuild_catalog
from harrix_swiss_knife.apps.icons.edit_icon import replace_family_id_in_name, update_icon_note

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


def _write(path: Path, text: str = _MIN_SVG) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _garage_meta(*, category: str = "building", family_id: str = "building__garage") -> NoteMeta:
    return NoteMeta(
        family_id=family_id,
        title="Garage",
        date="2020-07-19",
        category=category,
        tags=["garage"],
        author="Anton Sergienko",
        author_email="anton.b.sergienko@gmail.com",
        license="CC BY 4.0",
        license_url="https://example.com/license",
        permalink=f"https://harrix.dev/en/icons/{category}/{family_id}",
        permalink_source=(
            f"https://github.com/Harrix/Harrix-Vector-Icons/blob/main/icons/{category}/{family_id}/{family_id}.md"
        ),
        lang="en",
        featured_name="featured-image.svg",
    )


def _repo_with_garage(tmp_path: Path) -> Path:
    repo = tmp_path / "Harrix-Vector-Icons"
    note = repo / "icons" / "building" / "building__garage"
    _write(note / "featured-image.svg")
    _write(note / "img" / "building__garage_01.svg")
    _write(note / "img" / "building__garage_black.svg")
    (note / "building__garage.md").write_text(
        "---\n"
        "date: 2020-07-19\n"
        "categories:\n"
        "  - building\n"
        "tags:\n"
        "  - garage\n"
        "author: Anton Sergienko\n"
        "author-email: anton.b.sergienko@gmail.com\n"
        "license: CC BY 4.0\n"
        "license-url: https://example.com/license\n"
        "permalink: https://harrix.dev/en/icons/building/building__garage\n"
        "permalink-source: "
        "https://github.com/Harrix/Harrix-Vector-Icons/blob/main/icons/building/building__garage/building__garage.md\n"
        "lang: en\n"
        "---\n\n"
        "# Garage\n\n![Featured image](featured-image.svg)\n\n## Icons\n\n"
        "- ![building__garage_01](img/building__garage_01.svg)\n"
        "- ![building__garage_black](img/building__garage_black.svg)\n",
        encoding="utf-8",
    )
    return repo


def test_sync_family_id_category() -> None:
    assert sync_family_id_category("building__garage", "furniture") == "furniture__garage"
    assert sync_family_id_category("garage", "building") == "building__garage"
    assert sync_family_id_category("building__garage", "") == "building__garage"


def test_replace_family_id_in_name() -> None:
    assert replace_family_id_in_name("building__garage.md", "building__garage", "furniture__garage") == (
        "furniture__garage.md"
    )
    assert replace_family_id_in_name("building__garage_01.svg", "building__garage", "furniture__garage") == (
        "furniture__garage_01.svg"
    )
    assert replace_family_id_in_name("featured-image.svg", "building__garage", "furniture__garage") == (
        "featured-image.svg"
    )


def test_extra_categories_for_family() -> None:
    assert extra_categories_for_family(["Fiction", "Персонаж"], "fiction_robot__marvin") == ["Fiction", "Персонаж"]
    assert extra_categories_for_family(["building"], "building__garage") == []


def test_update_icon_note_changes_category_and_renames_files(tmp_path: Path) -> None:
    repo = _repo_with_garage(tmp_path)
    family = rebuild_catalog(repo).icons[0]
    meta = _garage_meta(category="furniture", family_id="furniture__garage")
    report = update_icon_note(repo_root=repo, family=family, meta=meta)

    assert report.moved
    assert report.new_family_id == "furniture__garage"
    dest = repo / "icons" / "furniture" / "furniture__garage"
    assert dest.is_dir()
    assert not (repo / "icons" / "building" / "building__garage").exists()
    assert not (repo / "icons" / "building").exists()
    assert (dest / "featured-image.svg").is_file()
    assert (dest / "furniture__garage.md").is_file()
    assert (dest / "img" / "furniture__garage_01.svg").is_file()
    assert (dest / "img" / "furniture__garage_black.svg").is_file()
    markdown = (dest / "furniture__garage.md").read_text(encoding="utf-8")
    assert "  - furniture" in markdown
    assert "img/furniture__garage_01.svg" in markdown
    assert "building__garage" not in markdown
    catalog = rebuild_catalog(repo)
    assert catalog.icons[0].id == "furniture__garage"
    assert catalog.icons[0].categories == ["furniture"]
    assert catalog.icons[0].folder == "icons/furniture/furniture__garage"


def test_update_icon_note_tags_only_keeps_paths(tmp_path: Path) -> None:
    repo = _repo_with_garage(tmp_path)
    family = rebuild_catalog(repo).icons[0]
    meta = _garage_meta()
    meta.tags = ["garage", "car"]
    report = update_icon_note(repo_root=repo, family=family, meta=meta)

    assert not report.moved
    assert report.new_family_id == "building__garage"
    note = repo / "icons" / "building" / "building__garage"
    assert (note / "img" / "building__garage_01.svg").is_file()
    markdown = (note / "building__garage.md").read_text(encoding="utf-8")
    assert "  - car" in markdown
    assert "img/building__garage_01.svg" in markdown


def test_update_icon_note_rejects_existing_destination(tmp_path: Path) -> None:
    repo = _repo_with_garage(tmp_path)
    dest = repo / "icons" / "furniture" / "furniture__garage"
    dest.mkdir(parents=True)
    (dest / "furniture__garage.md").write_text("# Occupied\n", encoding="utf-8")
    family = rebuild_catalog(repo).icons[0]
    meta = _garage_meta(category="furniture", family_id="furniture__garage")
    with pytest.raises(FileExistsError):
        update_icon_note(repo_root=repo, family=family, meta=meta, rebuild=False)
    assert (repo / "icons" / "building" / "building__garage" / "building__garage.md").is_file()


def test_update_icon_note_keeps_extra_categories(tmp_path: Path) -> None:
    repo = tmp_path / "Harrix-Vector-Icons"
    note = repo / "icons" / "fiction_robot" / "fiction_robot__marvin"
    _write(note / "featured-image.svg")
    _write(note / "img" / "fiction_robot__marvin_01.svg")
    (note / "fiction_robot__marvin.md").write_text(
        "---\ncategories:\n  - Fiction\n  - Персонаж\ntags:\n  - marvin\nlang: en\n---\n\n# Marvin\n",
        encoding="utf-8",
    )
    family = rebuild_catalog(repo).icons[0]
    meta = NoteMeta(
        family_id="furniture__marvin",
        title="Marvin",
        date="",
        category="furniture",
        tags=["marvin"],
        author="",
        author_email="",
        license="",
        license_url="",
        permalink="",
        permalink_source="",
        lang="en",
    )
    update_icon_note(repo_root=repo, family=family, meta=meta)
    dest = repo / "icons" / "furniture" / "furniture__marvin"
    markdown = (dest / "furniture__marvin.md").read_text(encoding="utf-8")
    assert "  - furniture" in markdown
    assert "  - Fiction" in markdown
    assert "  - Персонаж" in markdown
    assert (dest / "img" / "furniture__marvin_01.svg").is_file()


def test_add_vector_dialog_edit_mode_syncs_category(qapp: QApplication, tmp_path: Path) -> None:
    assert qapp is not None
    svg = tmp_path / "featured-image.svg"
    _write(svg)
    initial = _garage_meta()
    initial.tags = ["garage", "car"]
    dialog = AddVectorImageDialog(
        None,
        source_path=svg,
        defaults=RepoMetaDefaults(),
        app_config={},
        initial_meta=initial,
        window_title="Edit icon — building__garage",
    )
    assert dialog.windowTitle() == "Edit icon — building__garage"
    assert dialog.get_meta().family_id == "building__garage"
    assert dialog.get_meta().tags == ["garage", "car"]
    dialog._category_edit.setCurrentText("furniture")
    meta = dialog.get_meta()
    assert meta.category == "furniture"
    assert meta.family_id == "furniture__garage"
    assert meta.permalink.endswith("furniture/furniture__garage")


def test_note_meta_from_existing_uses_family_id_prefix() -> None:
    meta = note_meta_from_existing(
        family_id="fiction_robot__marvin",
        title="Marvin",
        categories=["Fiction", "Персонаж"],
        tags=["marvin"],
        featured_name="featured-image.svg",
        frontmatter={"date": "2024-01-02", "lang": "en", "author": "Anton"},
    )
    assert meta.category == "fiction_robot"
    assert meta.date == "2024-01-02"
    assert meta.author == "Anton"
