"""Tests for Vector Icons keyword editing."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.apps.icons.catalog import IconFamily, load_catalog, rebuild_catalog
from harrix_swiss_knife.apps.icons.keywords_dialog import EditKeywordsDialog
from harrix_swiss_knife.apps.icons.keywords_update import (
    parse_keywords_text,
    replace_frontmatter_list,
    update_keywords_files,
)

_MIN_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32"><rect width="32" height="32" fill="#336699"/></svg>'
)
_RU_GARAGE = "гараж"
_RU_ROBOT = "робот"


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_parse_keywords_text_strips_markers_and_dedupes() -> None:
    text = f"- robot\nRobot\n1. {_RU_ROBOT}\n```\ngarage\n"
    assert parse_keywords_text(text) == ["robot", _RU_ROBOT, "garage"]


def test_replace_frontmatter_list_rewrites_inline_and_block() -> None:
    inline = "---\ncategories: [building]\ntags: [garage]\n---\n\n# Garage\n"
    updated = replace_frontmatter_list(inline, "tags", ["garage", _RU_GARAGE])
    assert f"tags:\n  - garage\n  - {_RU_GARAGE}\n" in updated
    assert "# Garage" in updated

    block = "---\ncategories:\n  - building\ntags:\n  - old\n---\n\n# Garage\n"
    updated_block = replace_frontmatter_list(block, "tags", ["new"])
    assert "tags:\n  - new\n" in updated_block
    assert "  - old" not in updated_block
    assert "categories:\n  - building\n" in updated_block


def test_update_keywords_files_writes_note_and_catalog(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    note = repo / "icons" / "building__garage"
    note.mkdir(parents=True)
    (note / "featured-image.svg").write_text(_MIN_SVG, encoding="utf-8")
    md_path = note / "building__garage.md"
    md_path.write_text(
        "---\ncategories: [building]\ntags: [garage]\n---\n\n# Garage\n",
        encoding="utf-8",
    )
    rebuild_catalog(repo)
    catalog_path = repo / "catalog.json"

    update_keywords_files(
        md_path=md_path,
        catalog_path=catalog_path,
        family_id="building__garage",
        tags=["garage", _RU_GARAGE, "building"],
    )

    markdown = md_path.read_text(encoding="utf-8")
    assert "  - garage" in markdown
    assert f"  - {_RU_GARAGE}" in markdown
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    assert catalog["icons"][0]["tags"] == ["garage", _RU_GARAGE, "building"]


def test_rebuild_catalog_reads_block_tags(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    note = repo / "icons" / "building__garage"
    note.mkdir(parents=True)
    (note / "featured-image.svg").write_text(_MIN_SVG, encoding="utf-8")
    (note / "building__garage.md").write_text(
        f"---\ncategories:\n  - building\ntags:\n  - garage\n  - {_RU_GARAGE}\n---\n\n# Garage\n",
        encoding="utf-8",
    )
    catalog = rebuild_catalog(repo)
    assert catalog.icons[0].categories == ["building"]
    assert catalog.icons[0].tags == ["garage", _RU_GARAGE]
    loaded = load_catalog(repo)
    assert loaded.icons[0].tags == ["garage", _RU_GARAGE]


def test_edit_keywords_dialog_returns_textarea_tags(qapp: QApplication) -> None:
    assert qapp is not None
    family = IconFamily(
        id="building__garage",
        title="Garage",
        categories=["building"],
        tags=["garage"],
        folder="icons/building__garage",
        featured="featured-image.svg",
        featured_hash="",
    )
    dialog = EditKeywordsDialog(None, family=family, icon_path=None, app_config={})
    dialog._text_edit.setPlainText(f"garage\n{_RU_GARAGE}\n")
    assert dialog.get_tags() == ["garage", _RU_GARAGE]
    assert not dialog._ai_button.isEnabled()
