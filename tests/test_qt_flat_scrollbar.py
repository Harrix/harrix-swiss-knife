"""Tests for flat scrollbar stylesheet helpers."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication, QListView, QWidget

from harrix_swiss_knife.qt_flat_scrollbar import (
    FLAT_SCROLLBAR_STYLE,
    apply_flat_scrollbars,
    with_flat_scrollbars,
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


def test_with_flat_scrollbars_appends_once() -> None:
    base = "QListView { border: none; }"
    once = with_flat_scrollbars(base)
    twice = with_flat_scrollbars(once)
    assert once.startswith(base)
    assert "QScrollBar:vertical" in once
    assert "border-radius: 5px" in once
    assert "QAbstractScrollArea::corner" in once
    assert "background: #ffffff" in once
    assert twice == once
    assert with_flat_scrollbars("") == FLAT_SCROLLBAR_STYLE
    assert "QAbstractScrollArea::corner" in FLAT_SCROLLBAR_STYLE


def test_apply_flat_scrollbars_covers_styled_and_plain_views(qapp: QApplication) -> None:
    assert qapp is not None
    root = QWidget()
    styled = QListView(root)
    styled.setStyleSheet("QListView { background: white; }")
    plain = QListView(root)
    apply_flat_scrollbars(root)
    assert "QScrollBar:vertical" in styled.styleSheet()
    assert "QScrollBar:vertical" in plain.styleSheet()
    root.close()
