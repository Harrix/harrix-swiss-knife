"""Smoke tests for the hand-written Fluent widget catalog."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from PySide6.QtCore import QCoreApplication, QEvent
from PySide6.QtWidgets import QApplication, QWidget

from harrix_swiss_knife.fluent import FluentTheme, ThemeMode, is_fluent_themed, palette_for
from harrix_swiss_knife.fluent.gallery import build_gallery
from harrix_swiss_knife.fluent.tokens import DARK_PALETTE, LIGHT_PALETTE
from harrix_swiss_knife.fluent.widgets import (
    FluentCardGrid,
    FluentCommandCard,
    FluentContentDialog,
    FluentMenu,
    FluentMessageBar,
    FluentNavigationBar,
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
    widget.close()
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
