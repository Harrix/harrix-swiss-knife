"""Fluent message boxes paint rich-text links with Accent text."""

from __future__ import annotations

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QApplication, QLabel, QMessageBox, QWidget

from harrix_swiss_knife.apps.common import message_box
from harrix_swiss_knife.fluent.theme import FluentTheme, ThemeMode, enable_fluent_theme, mix
from harrix_swiss_knife.fluent.tokens import DARK_PALETTE


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_fluent_message_box_links_use_accent_in_dark(qapp: QApplication) -> None:
    assert qapp is not None
    theme = FluentTheme.instance()
    previous = theme.mode()
    theme.set_mode(ThemeMode.DARK, persist=False)
    host = QWidget()
    enable_fluent_theme(host)
    try:
        box = QMessageBox(host)
        box.setTextFormat(Qt.TextFormat.RichText)
        box.setText('GitHub: <a href="https://example.com">https://example.com</a>')
        message_box.prepare_box(box)
        expected = mix(DARK_PALETTE.window_bg, DARK_PALETTE.accent_text)
        labels = [label for label in box.findChildren(QLabel) if "example.com" in label.text()]
        assert labels
        for label in labels:
            assert label.palette().color(QPalette.ColorRole.Link).name() == expected.name()
            assert "a {" in label.styleSheet().casefold()
            assert expected.name().casefold() in label.styleSheet().casefold() or "rgba(" in label.styleSheet()
    finally:
        theme.set_mode(previous, persist=False)
        host.close()
