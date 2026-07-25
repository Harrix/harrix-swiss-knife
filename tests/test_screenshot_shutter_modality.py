"""Tests that shutter controls are embedded child widgets, not separate windows."""

from __future__ import annotations

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication, QDialog

from harrix_swiss_knife.screenshot.region_overlay import RESULT_TOGGLE_ARRANGE, RegionOverlay
from harrix_swiss_knife.screenshot.shutter_button import ArrangeModeDialog, ShutterPanel


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_overlay_embeds_shutter_panel_as_child_widget(qapp: QApplication) -> None:  # noqa: ARG001
    """Panel must be a plain child widget so modal exec() of the overlay owns its input."""
    overlay = RegionOverlay(QPixmap(200, 200), QApplication.primaryScreen().geometry(), with_shutter_controls=True)
    panel = overlay.findChild(ShutterPanel)
    assert panel is not None
    assert panel.parent() is overlay
    assert not panel.isWindow()  # embedded, not a separate native window
    overlay.close()


def test_overlay_arrange_button_finishes_with_toggle_code(qapp: QApplication) -> None:  # noqa: ARG001
    overlay = RegionOverlay(QPixmap(200, 200), QApplication.primaryScreen().geometry(), with_shutter_controls=True)
    panel = overlay.findChild(ShutterPanel)
    assert panel is not None

    overlay.show()
    QApplication.processEvents()
    panel.triggered.emit()
    QApplication.processEvents()

    assert overlay.result() == RESULT_TOGGLE_ARRANGE
    overlay.close()


def test_overlay_close_button_rejects(qapp: QApplication) -> None:  # noqa: ARG001
    overlay = RegionOverlay(QPixmap(200, 200), QApplication.primaryScreen().geometry(), with_shutter_controls=True)
    panel = overlay.findChild(ShutterPanel)
    assert panel is not None

    overlay.show()
    QApplication.processEvents()
    panel.cancelled.emit()
    QApplication.processEvents()

    assert overlay.result() == int(QDialog.DialogCode.Rejected)
    overlay.close()


def test_overlay_without_controls_has_no_panel(qapp: QApplication) -> None:  # noqa: ARG001
    overlay = RegionOverlay(QPixmap(200, 200), QApplication.primaryScreen().geometry())
    assert overlay.findChild(ShutterPanel) is None
    overlay.close()


def test_arrange_dialog_accepts_on_camera_and_rejects_on_close(qapp: QApplication) -> None:  # noqa: ARG001
    dialog = ArrangeModeDialog()
    panel = dialog.findChild(ShutterPanel)
    assert panel is not None

    dialog.show()
    QApplication.processEvents()
    panel.triggered.emit()
    assert dialog.result() == int(QDialog.DialogCode.Accepted)
    dialog.close()

    dialog2 = ArrangeModeDialog()
    panel2 = dialog2.findChild(ShutterPanel)
    assert panel2 is not None
    dialog2.show()
    QApplication.processEvents()
    panel2.cancelled.emit()
    assert dialog2.result() == int(QDialog.DialogCode.Rejected)
    dialog2.close()


def test_arrange_dialog_stays_on_top_frameless(qapp: QApplication) -> None:  # noqa: ARG001
    dialog = ArrangeModeDialog()
    flags = dialog.windowFlags()
    assert flags & Qt.WindowType.FramelessWindowHint
    assert flags & Qt.WindowType.WindowStaysOnTopHint
    dialog.close()
