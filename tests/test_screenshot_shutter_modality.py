"""Tests that shutter controls are embedded child widgets, not separate windows."""

from __future__ import annotations

import pytest
from PySide6.QtCore import QEvent, QPointF, QRect, Qt
from PySide6.QtGui import QKeyEvent, QMouseEvent, QPixmap
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QDialog, QLabel, QPushButton, QWidget

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


def test_adjust_mode_keeps_overlay_open_until_enter(qapp: QApplication) -> None:  # noqa: ARG001
    geo = QApplication.primaryScreen().geometry()
    overlay = RegionOverlay(QPixmap(geo.size()), geo, with_shutter_controls=True)
    panel = overlay.findChild(ShutterPanel)
    assert panel is not None
    panel.findChildren(QPushButton)[1].setChecked(True)
    overlay.show()
    QApplication.processEvents()

    start = QPointF(40, 40)
    end = QPointF(120, 100)
    overlay.mousePressEvent(
        QMouseEvent(
            QMouseEvent.Type.MouseButtonPress,
            start,
            overlay.mapToGlobal(start.toPoint()),
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        )
    )
    overlay.mouseMoveEvent(
        QMouseEvent(
            QMouseEvent.Type.MouseMove,
            end,
            overlay.mapToGlobal(end.toPoint()),
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        )
    )
    overlay.mouseReleaseEvent(
        QMouseEvent(
            QMouseEvent.Type.MouseButtonRelease,
            end,
            overlay.mapToGlobal(end.toPoint()),
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        )
    )
    QApplication.processEvents()

    assert overlay.result() == 0  # still running / not finished
    assert overlay._edit_rect is not None
    assert overlay.cropped_image is None

    enter = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_Return, Qt.KeyboardModifier.NoModifier)
    overlay.keyPressEvent(enter)
    QApplication.processEvents()

    assert overlay.result() == int(QDialog.DialogCode.Accepted)
    assert overlay.cropped_image is not None
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


def test_escape_during_drag_cancels_capture(qapp: QApplication) -> None:  # noqa: ARG001
    overlay = RegionOverlay(QPixmap(200, 200), QApplication.primaryScreen().geometry())
    overlay.show()
    QApplication.processEvents()

    local_pos = QPointF(10, 10)
    press = QMouseEvent(
        QMouseEvent.Type.MouseButtonPress,
        local_pos,
        overlay.mapToGlobal(local_pos.toPoint()),
        Qt.MouseButton.LeftButton,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
    )
    overlay.mousePressEvent(press)
    assert overlay._origin is not None

    escape = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_Escape, Qt.KeyboardModifier.NoModifier)
    overlay.keyPressEvent(escape)
    QApplication.processEvents()

    assert overlay.result() == int(QDialog.DialogCode.Rejected)
    overlay.close()


def test_escape_without_drag_rejects_overlay(qapp: QApplication) -> None:  # noqa: ARG001
    overlay = RegionOverlay(QPixmap(200, 200), QApplication.primaryScreen().geometry())
    overlay.show()
    QApplication.processEvents()

    escape = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_Escape, Qt.KeyboardModifier.NoModifier)
    overlay.keyPressEvent(escape)
    QApplication.processEvents()

    assert overlay.result() == int(QDialog.DialogCode.Rejected)
    overlay.close()


def test_escape_key_cancels_overlay_with_shutter_controls(qapp: QApplication) -> None:  # noqa: ARG001
    overlay = RegionOverlay(
        QPixmap(200, 200),
        QApplication.primaryScreen().geometry(),
        with_shutter_controls=True,
    )
    overlay.show()
    QApplication.processEvents()
    QTest.keyClick(overlay, Qt.Key.Key_Escape)
    QApplication.processEvents()
    assert overlay.result() == int(QDialog.DialogCode.Rejected)
    overlay.close()


def test_overlay_grabs_keyboard_while_visible(qapp: QApplication) -> None:  # noqa: ARG001
    overlay = RegionOverlay(QPixmap(200, 200), QApplication.primaryScreen().geometry())
    overlay.show()
    QApplication.processEvents()
    assert QWidget.keyboardGrabber() is overlay
    overlay.close()
    QApplication.processEvents()
    assert QWidget.keyboardGrabber() is not overlay


def test_escape_clears_editable_frame_then_cancels(
    qapp: QApplication,  # noqa: ARG001
) -> None:
    overlay = RegionOverlay(QPixmap(200, 200), QApplication.primaryScreen().geometry(), with_shutter_controls=True)
    panel = overlay.findChild(ShutterPanel)
    assert panel is not None
    adjust = next(button for button in panel.findChildren(QPushButton) if button.isCheckable())
    adjust.setChecked(True)

    overlay.show()
    QApplication.processEvents()
    overlay._enter_edit_rect(QRect(20, 20, 80, 60))
    assert overlay._edit_rect is not None

    QTest.keyClick(overlay, Qt.Key.Key_Escape)
    QApplication.processEvents()
    assert overlay._edit_rect is None
    assert overlay.isVisible()

    QTest.keyClick(overlay, Qt.Key.Key_Escape)
    QApplication.processEvents()
    assert overlay.result() == int(QDialog.DialogCode.Rejected)
    overlay.close()


def test_enter_confirms_editable_frame(qapp: QApplication) -> None:  # noqa: ARG001
    overlay = RegionOverlay(QPixmap(200, 200), QApplication.primaryScreen().geometry())
    overlay.show()
    QApplication.processEvents()
    overlay._enter_edit_rect(QRect(10, 10, 50, 40))
    QTest.keyClick(overlay, Qt.Key.Key_Return)
    QApplication.processEvents()
    assert overlay.result() == int(QDialog.DialogCode.Accepted)
    assert overlay.cropped_image is not None
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


def test_shutter_panel_shows_hover_hint_caption(qapp: QApplication) -> None:  # noqa: ARG001
    """In-panel captions must appear on hover (QToolTip is hidden under stay-on-top overlays)."""
    panel = ShutterPanel()
    panel.set_mode("selection")
    panel.show()
    QApplication.processEvents()

    mode_button = next(button for button in panel.findChildren(QPushButton) if "Arrange" in (button.toolTip() or ""))
    QApplication.sendEvent(mode_button, QEvent(QEvent.Type.Enter))
    QApplication.processEvents()

    hints = [label for label in panel.findChildren(QLabel) if "Arrange" in label.text()]
    assert hints
    assert hints[0].isVisible()

    QApplication.sendEvent(mode_button, QEvent(QEvent.Type.Leave))
    QApplication.processEvents()
    assert not hints[0].isVisible()
    panel.close()


def test_shutter_panel_shows_edit_key_hints(qapp: QApplication) -> None:  # noqa: ARG001
    panel = ShutterPanel()
    panel.set_mode("selection")
    panel.show()
    QApplication.processEvents()
    panel.set_edit_keys_visible(visible=True)
    labels = [label for label in panel.findChildren(QLabel) if "Shift" in label.text()]
    assert labels
    assert labels[0].isVisible()
    panel.set_edit_keys_visible(visible=False)
    assert not labels[0].isVisible()
    panel.close()
