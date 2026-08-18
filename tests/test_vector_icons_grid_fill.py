"""Tests for chunked grid filling and viewport-driven thumbnails in Vector Icons."""

from __future__ import annotations

from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.apps.icons.catalog import IconFamily, IconVariant
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


def _entries(tmp_path: Path, count: int) -> list[GridEntry]:
    entries: list[GridEntry] = []
    for index in range(count):
        family_id = f"icon_{index:04d}"
        svg_path = tmp_path / f"{family_id}.svg"
        svg_path.write_text(_MIN_SVG, encoding="utf-8")
        family = IconFamily(
            id=family_id,
            title=family_id,
            categories=[],
            tags=[],
            folder=".",
            featured=svg_path.name,
            featured_hash="",
            variants=[IconVariant(file=svg_path.name, name=family_id, hash="")],
        )
        entries.append(GridEntry(family=family, svg_path=svg_path))
    return entries


def test_append_grid_entries_keeps_all_tiles(qapp: QApplication, tmp_path: Path) -> None:  # noqa: ARG001
    entries = _entries(tmp_path, 40)
    placeholder = placeholder_pixmap(48)
    lst = DraggableIconList(icon_size=48, dual_line_labels=True)
    lst.set_grid_entries(entries[:10], pixmaps_by_path={}, placeholder=placeholder)
    lst.append_grid_entries(entries[10:], pixmaps_by_path={}, placeholder=placeholder)
    assert lst.count() == len(entries)
    assert lst.select_family(entries[-1].family.id)
    assert lst.currentRow() == len(entries) - 1


def test_visible_row_span_covers_only_screenful(qapp: QApplication, tmp_path: Path) -> None:  # noqa: ARG001
    entries = _entries(tmp_path, 400)
    placeholder = placeholder_pixmap(48)
    lst = DraggableIconList(icon_size=48, dual_line_labels=True)
    lst.resize(400, 300)
    lst.set_grid_entries(entries, pixmaps_by_path={}, placeholder=placeholder)
    QApplication.processEvents()
    first, last = lst.visible_row_span(margin_lines=1)
    assert first == 0
    assert last < lst.count() - 1


def test_update_and_reset_row_pixmaps(qapp: QApplication, tmp_path: Path) -> None:  # noqa: ARG001
    entries = _entries(tmp_path, 3)
    placeholder = placeholder_pixmap(48)
    lst = DraggableIconList(icon_size=48, dual_line_labels=True)
    lst.set_grid_entries(entries, pixmaps_by_path={}, placeholder=placeholder)
    thumb = placeholder_pixmap(64)
    lst.update_row_pixmaps({1: thumb})
    item = lst.item(1)
    assert item is not None
    assert item.icon().availableSizes()
    lst.reset_row_pixmaps([1], placeholder=placeholder)
    assert lst.item(1) is not None
