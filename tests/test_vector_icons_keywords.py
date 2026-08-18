"""Tests for Vector Icons keyword editing."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.apps.icons.catalog import IconFamily, load_catalog, rebuild_catalog
from harrix_swiss_knife.apps.icons.keywords_ai import KeywordsBatchRunner
from harrix_swiss_knife.apps.icons.keywords_update import (
    parse_keywords_text,
    replace_frontmatter_list,
    update_keywords_files,
)
from harrix_swiss_knife.apps.icons.variant_view import GridEntry
from harrix_swiss_knife.apps.icons.widgets import (
    DraggableIconList,
    batch_context_action_texts,
    placeholder_pixmap,
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


def _family(family_id: str, tags: list[str] | None = None) -> IconFamily:
    return IconFamily(
        id=family_id,
        title=family_id.rsplit("__", maxsplit=1)[-1].title(),
        categories=[family_id.split("__", 1)[0]],
        tags=tags or [],
        folder=f"icons/{family_id}",
        featured="featured-image.svg",
        featured_hash="",
    )


def test_selected_keyword_targets_are_unique_and_ordered(qapp: QApplication, tmp_path: Path) -> None:
    assert qapp is not None
    first = _family("building__garage", ["garage"])
    second = _family("fiction__ufo", ["ufo"])
    first_svg = tmp_path / "building__garage.svg"
    second_svg = tmp_path / "fiction__ufo.svg"
    first_svg.write_text(_MIN_SVG, encoding="utf-8")
    second_svg.write_text(_MIN_SVG, encoding="utf-8")
    placeholder = placeholder_pixmap(64)
    lst = DraggableIconList(icon_size=64, dual_line_labels=True)
    lst.set_grid_entries(
        [
            GridEntry(family=first, svg_path=first_svg),
            GridEntry(family=first, svg_path=first_svg),
            GridEntry(family=second, svg_path=second_svg),
        ],
        pixmaps_by_path={str(first_svg): placeholder, str(second_svg): placeholder},
        placeholder=placeholder,
    )
    for index in range(lst.count()):
        item = lst.item(index)
        assert item is not None
        item.setSelected(True)
    targets = lst.selected_keyword_targets()
    assert [family.id for family, _path in targets] == ["building__garage", "fiction__ufo"]
    assert lst.selectionMode() == lst.SelectionMode.ExtendedSelection
    assert batch_context_action_texts(len(targets)) == [
        "🤖 Process keywords with AI (2 icons)…",
    ]
    assert len(batch_context_action_texts(len(targets))) == 1


def test_keywords_batch_runner_updates_then_reports_failures(qapp: QApplication, tmp_path: Path) -> None:
    assert qapp is not None
    first = _family("building__garage", ["garage"])
    second = _family("fiction__ufo", ["ufo"])
    first_svg = tmp_path / "a.svg"
    second_svg = tmp_path / "b.svg"
    first_svg.write_text(_MIN_SVG, encoding="utf-8")
    second_svg.write_text(_MIN_SVG, encoding="utf-8")
    updated: list[tuple[str, list[str]]] = []
    finished: list[tuple[int, int, bool]] = []

    def fake_request(
        _parent: object,
        *,
        icon_path: Path,
        on_tags: Callable[[list[str]], None],
        on_error: Callable[[str], None],
        **_kwargs: object,
    ) -> None:
        if icon_path == first_svg:
            on_tags(["garage", _RU_GARAGE])
            return
        on_error("failed")

    runner = KeywordsBatchRunner(
        None,
        app_config={},
        jobs=[(first, first_svg), (second, second_svg)],
        on_item_success=lambda family, tags: updated.append((family.id, tags)),
        on_finished=lambda updated_count, failed, *, cancelled: finished.append((updated_count, failed, cancelled)),
        request_fn=fake_request,
    )
    runner.start()
    assert updated == [("building__garage", ["garage", _RU_GARAGE])]
    assert finished == [(1, 1, False)]
    assert not runner.is_running
