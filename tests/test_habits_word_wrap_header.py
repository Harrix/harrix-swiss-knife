"""Tests for wrapped habit names in process-habits column headers."""

from __future__ import annotations

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QFontMetrics, QStandardItemModel
from PySide6.QtWidgets import QApplication, QTableView

from harrix_swiss_knife.apps.habits.word_wrap_header import (
    WordWrapHeaderView,
    wrapped_header_text_size,
)

_LONG_HABIT_NAME = "Read technical documentation about Python every evening"


@pytest.fixture
def qapp() -> QApplication:
    """Ensure a QApplication exists for header widgets."""
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_wrapped_header_text_size_grows_when_width_shrinks(qapp: QApplication) -> None:
    """A long title is taller when forced into a narrow column."""
    assert qapp is not None
    metrics = QFontMetrics(QFont())
    wide = wrapped_header_text_size(_LONG_HABIT_NAME, 400, metrics)
    narrow = wrapped_header_text_size(_LONG_HABIT_NAME, 80, metrics)
    assert narrow.height() > wide.height()


def test_word_wrap_header_sizes_habit_column_to_wrap_width(qapp: QApplication) -> None:
    """Habit columns stay near the wrap width instead of the full title width."""
    assert qapp is not None
    model = QStandardItemModel()
    model.setHorizontalHeaderLabels(["Date", _LONG_HABIT_NAME])

    wrapped_table = QTableView()
    wrapped_header = WordWrapHeaderView(Qt.Orientation.Horizontal, wrapped_table, wrap_width=86)
    wrapped_table.setHorizontalHeader(wrapped_header)
    wrapped_table.setModel(model)
    wrapped_size = wrapped_header.sectionSizeFromContents(1)

    plain_table = QTableView()
    plain_header = WordWrapHeaderView(Qt.Orientation.Horizontal, plain_table)
    plain_table.setHorizontalHeader(plain_header)
    plain_table.setModel(model)
    plain_size = plain_header.sectionSizeFromContents(1)

    assert wrapped_size.width() < plain_size.width()
    assert wrapped_size.height() > plain_size.height()
