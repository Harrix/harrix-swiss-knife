"""Tests for shared app window helpers."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication, QMenuBar, QWidget

from harrix_swiss_knife.apps.common.qt_main_window import resolve_window_menu_bar
from harrix_swiss_knife.qt_emoji_icon import apply_leading_emoji_icons


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_resolve_window_menu_bar_when_attribute_shadows_method(qapp: QApplication) -> None:
    """UI files assign `menuBar` to a widget, so `window.menuBar()` must not be called."""
    assert qapp is not None
    window = QWidget()
    bar = QMenuBar(window)
    window.menuBar = bar
    action = bar.addAction("🚪 Exit")
    resolved = resolve_window_menu_bar(window)
    assert resolved is bar
    apply_leading_emoji_icons(resolved)
    assert action.text() == "Exit"
    assert not action.icon().isNull()
