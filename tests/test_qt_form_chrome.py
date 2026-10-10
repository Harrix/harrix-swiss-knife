"""Tests for app-wide dialog surface and Lucide toggle polish."""

from __future__ import annotations

from PySide6.QtCore import QEvent
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication, QCheckBox, QDialog, QRadioButton

from harrix_swiss_knife.apps.common.ui_chrome import SURFACE, apply_white_surface_palette, button_idle_qss
from harrix_swiss_knife.qt_form_chrome import install_form_chrome
from harrix_swiss_knife.qt_lucide_checkbox import LucideToggleStyle


def _qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_button_idle_qss_uses_white_surface() -> None:
    sheet = button_idle_qss()
    assert SURFACE in sheet
    assert "min-height: 28px" in sheet


def test_apply_white_surface_palette_sets_window_base() -> None:
    assert _qapp() is not None
    dialog = QDialog()
    apply_white_surface_palette(dialog)
    white = QColor(SURFACE)
    assert dialog.palette().color(QPalette.ColorRole.Window) == white
    assert dialog.palette().color(QPalette.ColorRole.Base) == white
    assert dialog.autoFillBackground()
    dialog.close()


def test_install_form_chrome_polishes_toggles_and_dialogs() -> None:
    app = _qapp()
    install_form_chrome(app)
    dialog = QDialog()
    box = QCheckBox("Check", dialog)
    radio = QRadioButton("Radio", dialog)
    app.sendEvent(dialog, QEvent(QEvent.Type.Polish))
    app.sendEvent(box, QEvent(QEvent.Type.Polish))
    app.sendEvent(radio, QEvent(QEvent.Type.Polish))
    assert dialog.palette().color(QPalette.ColorRole.Window) == QColor(SURFACE)
    assert isinstance(box.style(), LucideToggleStyle)
    assert isinstance(radio.style(), LucideToggleStyle)
    dialog.close()
