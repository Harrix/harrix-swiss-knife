"""Tests for wrapped table column headers."""

from __future__ import annotations

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QFontMetrics, QPalette, QStandardItemModel
from PySide6.QtWidgets import QApplication, QTableView, QWidget

from harrix_swiss_knife.apps.common.day_bands import table_surface_color
from harrix_swiss_knife.apps.common.word_wrap_header import (
    WordWrapHeaderView,
    _header_title_is_numeric,
    install_word_wrap_header,
    wrapped_header_text_size,
)
from harrix_swiss_knife.apps.habits.layout_chrome import _polish_all
from harrix_swiss_knife.fluent.app_chrome import install_fluent_app_window, style_fluent_table
from harrix_swiss_knife.fluent.theme import FluentTheme, ThemeMode, enable_fluent_theme, palette_for

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


def test_header_title_numeric_heuristic_matches_amount_columns() -> None:
    assert _header_title_is_numeric("Amount")
    assert _header_title_is_numeric("Rate")
    assert _header_title_is_numeric("kcal/100g")
    assert not _header_title_is_numeric("Description")
    assert not _header_title_is_numeric("Total per day")


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


def test_install_word_wrap_header_replaces_default_header(qapp: QApplication) -> None:
    """App tables get a wrapping header that also wraps the first column."""
    assert qapp is not None
    table = QTableView()
    model = QStandardItemModel()
    model.setHorizontalHeaderLabels([_LONG_HABIT_NAME, "Date"])
    table.setModel(model)

    header = install_word_wrap_header(table, wrap_width=86)
    assert header is table.horizontalHeader()
    first = header.sectionSizeFromContents(0)
    expected = wrapped_header_text_size(_LONG_HABIT_NAME, 86, header.fontMetrics())
    assert first.width() == expected.width()
    assert first.height() == expected.height()


def test_install_word_wrap_header_keeps_dark_fluent_chrome(qapp: QApplication) -> None:
    """Replacing the header must not leave a white light-mode section strip."""
    assert qapp is not None
    theme = FluentTheme.instance()
    previous = theme.mode()
    theme.set_mode(ThemeMode.DARK, persist=False)
    host = QWidget()
    enable_fluent_theme(host)
    install_fluent_app_window(host)
    try:
        table = QTableView(host)
        table.setObjectName("tableView_process_habits")
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Date", "Sport"])
        table.setModel(model)
        style_fluent_table(table)
        header = install_word_wrap_header(table, wrap_width=86, wrap_first_section=False)
        surface = table_surface_color(palette_for(host))
        assert header.palette().color(QPalette.ColorRole.Button).rgb() == surface.rgb()
        assert header.palette().color(QPalette.ColorRole.ButtonText).lightness() > 140
        assert "#ffffff" not in (table.styleSheet() or "").casefold()
    finally:
        theme.set_mode(previous, persist=False)
        host.close()


def test_habits_layout_chrome_does_not_wipe_process_table_sheet(qapp: QApplication) -> None:
    """Process table must keep Fluent header QSS after Habits layout polish."""
    assert qapp is not None
    theme = FluentTheme.instance()
    previous = theme.mode()
    theme.set_mode(ThemeMode.DARK, persist=False)
    host = QWidget()
    enable_fluent_theme(host)
    install_fluent_app_window(host)
    try:
        table = QTableView(host)
        table.setObjectName("tableView_process_habits")
        host.tableView_process_habits = table
        host._is_closing = False
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Date", "Sport"])
        table.setModel(model)
        install_word_wrap_header(table, wrap_width=86, wrap_first_section=False)
        style_fluent_table(table)
        _polish_all(host)
        assert "QHeaderView::section" in (table.styleSheet() or "")
        assert table.objectName() == "tableView_process_habits"
        assert table.horizontalHeader().palette().color(QPalette.ColorRole.Button).lightness() < 80
    finally:
        theme.set_mode(previous, persist=False)
        host.close()


def test_word_wrap_header_finds_interactive_column_boundary(qapp: QApplication) -> None:
    """The resize mark sits on an interactive edge and skips the table's outer edge."""
    assert qapp is not None
    table = QTableView()
    model = QStandardItemModel()
    model.setHorizontalHeaderLabels(["A", "B", "C"])
    table.setModel(model)
    header = install_word_wrap_header(table)
    table.resize(360, 180)
    table.show()
    qapp.processEvents()
    for section in range(header.count()):
        header.setSectionResizeMode(section, header.ResizeMode.Interactive)
        header.resizeSection(section, 80)
    qapp.processEvents()

    edge = header.sectionViewportPosition(0) + header.sectionSize(0)
    assert header._boundary_x_at(edge) == edge
    assert header._boundary_x_at(edge + 40) is None
    last_edge = header.sectionViewportPosition(header.count() - 1) + header.sectionSize(header.count() - 1)
    assert header._boundary_x_at(last_edge) is None
