"""Smoke tests for the hand-written Fluent widget catalog."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from PySide6.QtCore import QCoreApplication, QEvent, QSortFilterProxyModel
from PySide6.QtGui import QFont, QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QApplication, QTableView, QWidget
from shiboken6 import isValid

from harrix_swiss_knife.fluent import FluentTheme, ThemeMode, is_fluent_themed, palette_for
from harrix_swiss_knife.fluent.app_chrome import _sync_record_id_header, _watch_record_id_header
from harrix_swiss_knife.fluent.gallery import build_gallery
from harrix_swiss_knife.fluent.tokens import DARK_PALETTE, LIGHT_PALETTE
from harrix_swiss_knife.fluent.widgets import (
    FluentCardGrid,
    FluentCommandCard,
    FluentContentDialog,
    FluentExpander,
    FluentGroupBox,
    FluentMenu,
    FluentMessageBar,
    FluentNavigationBar,
    FluentSettingCard,
    FluentSettingHyperlinkCard,
    FluentToggleSwitch,
    Severity,
)

if TYPE_CHECKING:
    from collections.abc import Iterator


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


@pytest.fixture
def light_theme(qapp: QApplication) -> Iterator[FluentTheme]:
    theme = FluentTheme.instance()
    previous = theme.mode()
    theme.set_mode(ThemeMode.LIGHT)
    qapp.processEvents()
    yield theme
    for widget in qapp.topLevelWidgets():
        _dispose(qapp, widget)
    theme.set_mode(previous)
    qapp.processEvents()


def _dispose(qapp: QApplication, widget: QWidget) -> None:
    if not isValid(widget):
        return
    widget.close()
    if not isValid(widget):
        return
    widget.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    qapp.processEvents()


def test_gallery_builds_and_toggles_theme(qapp: QApplication, light_theme: FluentTheme) -> None:
    window = build_gallery()
    window.show()
    qapp.processEvents()
    assert is_fluent_themed(window)
    assert palette_for(window) is LIGHT_PALETTE

    for key in ("basic", "text", "display", "cards", "navigation", "views", "dialogs", "pickers", "editors"):
        window.show_page(key)
        qapp.processEvents()
        assert window.navigation.current() == key

    assert window.navigation.property("_hskShowcaseLabel") == "fluentNavigationBar"

    light_theme.set_mode(ThemeMode.DARK)
    qapp.processEvents()
    assert palette_for(window) is DARK_PALETTE
    assert "hsk-white-surfaces" not in window.styleSheet()
    assert window.palette().window().color() == DARK_PALETTE.window_bg
    _dispose(qapp, window)


def test_unthemed_widget_stays_light(qapp: QApplication, light_theme: FluentTheme) -> None:
    light_theme.set_mode(ThemeMode.DARK)
    qapp.processEvents()
    plain = QWidget()
    assert not is_fluent_themed(plain)
    assert palette_for(plain) is LIGHT_PALETTE
    _dispose(qapp, plain)


def test_command_cards_and_navigation(qapp: QApplication, light_theme: FluentTheme) -> None:
    del light_theme
    grid = FluentCardGrid()
    clicked: list[str] = []
    for index in range(5):
        card = FluentCommandCard(f"Command {index}", "Description", icon="terminal", user_data=index)
        card.clicked.connect(lambda name=f"Command {index}": clicked.append(name))
        grid.add_card(card)
    assert grid.count() == 5
    grid.cards()[2].clicked.emit()
    assert clicked == ["Command 2"]
    grid.clear()
    assert grid.count() == 0

    nav = FluentNavigationBar()
    nav.add_item("a", "Alpha", icon="house")
    nav.add_item("b", "Beta", icon="file")
    changed: list[str] = []
    nav.current_changed.connect(changed.append)
    nav.set_current("b")
    qapp.processEvents()
    assert nav.current() == "b"
    assert changed == ["b"]
    _dispose(qapp, grid)
    _dispose(qapp, nav)


def test_setting_cards(qapp: QApplication, light_theme: FluentTheme) -> None:
    del light_theme
    group = FluentGroupBox("System")
    display = FluentSettingCard("Display", "Monitors and brightness", icon="monitor")
    link = FluentSettingHyperlinkCard("Docs", "https://example.com", "Project docs", icon="book-open")
    opened: list[str] = []
    display.clicked.connect(lambda: opened.append(display.title()))
    group.add_widget(display)
    group.add_widget(link)
    assert display.title() == "Display"
    assert display.content() == "Monitors and brightness"
    assert link.url() == "https://example.com"
    display.clicked.emit()
    assert opened == ["Display"]
    _dispose(qapp, group)


def test_expander_trailing_does_not_toggle(qapp: QApplication, light_theme: FluentTheme) -> None:
    del light_theme
    expander = FluentExpander("Advanced", caption="More options", icon="sliders-horizontal")
    toggle = FluentToggleSwitch(on_text="", off_text="")
    expander.trailing_layout.addWidget(toggle)
    expander.show()
    qapp.processEvents()
    assert not expander.is_expanded()
    toggle.click()
    qapp.processEvents()
    assert not expander.is_expanded()
    assert toggle.isChecked()
    expander.toggle()
    qapp.processEvents()
    assert expander.is_expanded()
    _dispose(qapp, expander)


def test_popups_instantiate(qapp: QApplication, light_theme: FluentTheme) -> None:
    del light_theme
    host = build_gallery()
    host.show()
    qapp.processEvents()

    menu = FluentMenu("", host)
    menu.add_lucide_action("Copy", "copy", lambda: None)
    assert len(menu.actions()) == 1

    bar = FluentMessageBar.show_message(host, "Saved", "All good", severity=Severity.SUCCESS, duration_ms=-1)
    assert bar.isVisible()
    bar.close()

    dialog = FluentContentDialog("Title", "Body", host)
    dialog.open()
    qapp.processEvents()
    assert dialog.isVisible()
    dialog.reject()
    qapp.processEvents()
    _dispose(qapp, dialog)
    _dispose(qapp, host)


def test_record_id_header_appears_after_rows_arrive(qapp: QApplication) -> None:
    """An empty table keeps its id column, then shows database ids once rows exist."""
    assert qapp is not None
    table = QTableView()
    table.setFont(QFont("Roboto", 12))
    _watch_record_id_header(table)
    _sync_record_id_header(table)
    assert not table.verticalHeader().isHidden()

    source = QStandardItemModel()
    source.setHorizontalHeaderLabels(["Name"])
    source.appendRow([QStandardItem("Milk")])
    source.setVerticalHeaderItem(0, QStandardItem("42"))
    proxy = QSortFilterProxyModel()
    proxy.setSourceModel(source)
    table.setModel(proxy)
    qapp.processEvents()

    header = table.verticalHeader()
    assert not header.isHidden()
    assert header.minimumWidth() >= 16
    assert header.font().pointSizeF() < table.font().pointSizeF()
    _dispose(qapp, table)


def test_row_number_header_stays_hidden(qapp: QApplication) -> None:
    """Tables without record ids do not keep the default row-number column."""
    assert qapp is not None
    table = QTableView()
    _watch_record_id_header(table)
    model = QStandardItemModel()
    model.setHorizontalHeaderLabels(["Name"])
    model.appendRow([QStandardItem("Milk")])
    table.setModel(model)
    qapp.processEvents()
    assert table.verticalHeader().isHidden()
    _dispose(qapp, table)
