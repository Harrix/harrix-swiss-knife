"""Exercises tab splitter keeps a near-equal two-pane layout."""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QApplication, QSplitter, QTableView, QWidget

from harrix_swiss_knife.apps.fitness import layout_chrome


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_exercises_splitter_recovers_from_tiny_left_pane(qapp: QApplication, monkeypatch: pytest.MonkeyPatch) -> None:
    assert qapp is not None
    monkeypatch.setattr(layout_chrome, "load_splitter_sizes", lambda _key, _default: [80, 1200])
    host = QWidget()
    host.resize(1280, 800)
    splitter = QSplitter(Qt.Orientation.Horizontal, host)
    left = QWidget(splitter)
    right = QWidget(splitter)
    splitter.addWidget(left)
    splitter.addWidget(right)
    host.splitter_2 = splitter
    host.widget_top = left
    host.widget_bottom = right
    host._is_closing = False

    layout_chrome._configure_exercises_splitter(host)
    apply = host._apply_fitness_exercises_splitter_sizes
    # Pretend the tab finally got a real width after being hidden.
    splitter.resize(1280, 800)
    apply()
    sizes = splitter.sizes()
    assert len(sizes) == 2
    assert sizes[0] >= layout_chrome._CONTENT_MIN
    ratio = sizes[0] / max(sum(sizes), 1)
    assert layout_chrome._EQUAL_MIN_RATIO <= ratio <= layout_chrome._EQUAL_MAX_RATIO
    host.close()


def test_compact_table_keeps_thumbnail_row_height(qapp: QApplication) -> None:
    assert qapp is not None
    table = QTableView()
    table.setIconSize(QSize(64, 64))
    layout_chrome._compact_table(table)
    assert table.verticalHeader().defaultSectionSize() >= 72
    table.close()


def test_apply_exercises_splitter_sizes_noops_without_wire(qapp: QApplication) -> None:
    assert qapp is not None
    layout_chrome.apply_exercises_splitter_sizes(SimpleNamespace())
