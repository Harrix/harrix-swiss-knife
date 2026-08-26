"""Tests that toasts stay draggable and clickable during UI-thread work."""

from __future__ import annotations

import pytest
from PySide6.QtCore import QEvent, QPointF, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QApplication, QWidget

from harrix_swiss_knife.toast_countdown_notification import ToastCountdownNotification
from harrix_swiss_knife.toast_notification_base import (
    ToastNotificationBase,
    _AllowWidgetInputFilter,
    event_targets_widget,
)
from harrix_swiss_knife.toast_progress_notification import ToastProgressNotification


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def _mouse_event(event_type: QEvent.Type, widget: QWidget, *, global_offset: int = 0) -> QMouseEvent:
    local = QPointF(8, 8)
    global_pos = widget.mapToGlobal(local.toPoint())
    global_pos.setX(global_pos.x() + global_offset)
    global_pos.setY(global_pos.y() + global_offset)
    return QMouseEvent(
        event_type,
        local,
        global_pos,
        Qt.MouseButton.LeftButton,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
    )


def test_toast_label_lets_mouse_through_to_dialog(qapp: QApplication) -> None:  # noqa: ARG001
    toast = ToastNotificationBase("Hello")
    assert toast.label.testAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
    toast.close()


def test_progress_toast_chrome_lets_mouse_through(qapp: QApplication) -> None:  # noqa: ARG001
    toast = ToastProgressNotification("Rendering icon previews…", total=10)
    assert toast._progress_container.testAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
    assert toast.progress_bar.testAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
    toast.close()


def test_event_targets_widget_accepts_toast_children(qapp: QApplication) -> None:  # noqa: ARG001
    toast = ToastNotificationBase("Hello")
    other = QWidget()
    assert event_targets_widget(toast, toast)
    assert event_targets_widget(toast.label, toast)
    assert event_targets_widget(toast._collapse_button, toast)
    assert not event_targets_widget(other, toast)
    toast.close()
    other.close()


def test_input_filter_blocks_other_widgets_but_keeps_toast_interactive(qapp: QApplication) -> None:  # noqa: ARG001
    toast = ToastNotificationBase("Hello")
    other = QWidget()
    event_filter = _AllowWidgetInputFilter(toast)
    press = _mouse_event(QEvent.Type.MouseButtonPress, toast)
    assert event_filter.eventFilter(toast, press) is False
    assert event_filter.eventFilter(toast._collapse_button, press) is False
    assert event_filter.eventFilter(other, press) is True
    assert event_filter.eventFilter(other, QEvent(QEvent.Type.Paint)) is False
    toast.close()
    other.close()


def test_drag_marks_toast_as_user_moved(qapp: QApplication) -> None:  # noqa: ARG001
    toast = ToastNotificationBase("Hello")
    toast.present()
    QApplication.processEvents()
    toast.mousePressEvent(_mouse_event(QEvent.Type.MouseButtonPress, toast))
    toast.mouseMoveEvent(_mouse_event(QEvent.Type.MouseMove, toast, global_offset=40))
    assert toast.user_moved is True
    assert toast not in ToastNotificationBase.stack_members(pinned=False)
    toast.close()


def test_countdown_toast_can_start_collapsed_without_focus(qapp: QApplication) -> None:
    assert qapp is not None
    toast = ToastCountdownNotification("Adding exercises…")
    toast.start_countdown(pinned=True, activate=False)
    assert toast.is_pinned
    assert toast.isVisible()
    toast.set_message("Adding exercises… (2)")
    assert "Adding exercises… (2)" in toast.label.text()
    assert toast.elapsed_seconds == 0
    toast.close()
