"""Fluent list views keep readable item text in dark theme."""

from __future__ import annotations

import pytest
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QApplication, QListView, QWidget

from harrix_swiss_knife.fluent.app_chrome import install_fluent_app_window, style_fluent_item_view
from harrix_swiss_knife.fluent.theme import FluentTheme, ThemeMode, mix


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_style_fluent_item_view_keeps_light_text_in_dark_theme(qapp: QApplication) -> None:
    assert qapp is not None
    theme = FluentTheme.instance()
    previous = theme.mode()
    theme.set_mode(ThemeMode.DARK, persist=False)
    try:
        host = QWidget()
        view = QListView(host)
        view.setObjectName("list_chart_categories")
        install_fluent_app_window(host)
        # Layout chrome used to clear the sheet and leave system black ink.
        view.setStyleSheet("")
        style_fluent_item_view(view)
        text = view.palette().color(QPalette.ColorRole.Text)
        expected = mix(theme.palette().window_bg, theme.palette().text_primary)
        assert text.lightness() > 180
        assert text.name() == expected.name()
        assert "color:" in view.styleSheet().lower()
        host.close()
    finally:
        theme.set_mode(previous, persist=False)
