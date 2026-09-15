"""Tests for capture hotkey long-press and the action picker."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QDialog

from harrix_swiss_knife.capture_action_picker import (
    CAPTURE_PICKER_ACTIONS,
    CaptureActionPickerDialog,
    choose_capture_hotkey_action,
)
from harrix_swiss_knife.capture_hotkey import CAPTURE_HOTKEY_ACTIONS, CAPTURE_HOTKEY_LONG_PRESS_MS
from harrix_swiss_knife.global_hotkey import GlobalHotkeyManager


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_capture_hotkey_action_set() -> None:
    assert CAPTURE_HOTKEY_LONG_PRESS_MS >= 100
    assert {
        "OnScreenshotRegion",
        "OnScreenshotRegionClipboard",
        "OnScreenshotRegionTranslate",
        "OnRecordRegion",
    } == CAPTURE_HOTKEY_ACTIONS
    assert {cls.__name__ for cls in CAPTURE_PICKER_ACTIONS} == CAPTURE_HOTKEY_ACTIONS


def test_hold_short_press_emits_action_triggered(qapp: QApplication) -> None:
    manager = GlobalHotkeyManager(qapp)
    manager.set_long_press_actions({"OnScreenshotRegion"}, hold_ms=200)
    triggered: list[str] = []
    long_presses: list[str] = []
    manager.action_triggered.connect(triggered.append)
    manager.action_long_press.connect(long_presses.append)

    with patch("harrix_swiss_knife.global_hotkey.is_virtual_key_down", return_value=False):
        manager._begin_hold("OnScreenshotRegion", vk=0x33)
        manager._on_hold_poll()

    assert triggered == ["OnScreenshotRegion"]
    assert long_presses == []
    manager.unregister_all()
    manager.deleteLater()


def test_hold_long_press_emits_action_long_press(qapp: QApplication) -> None:
    manager = GlobalHotkeyManager(qapp)
    manager.set_long_press_actions({"OnScreenshotRegion"}, hold_ms=50)
    triggered: list[str] = []
    long_presses: list[str] = []
    manager.action_triggered.connect(triggered.append)
    manager.action_long_press.connect(long_presses.append)

    clock = MagicMock()
    clock.elapsed.return_value = 100

    with patch("harrix_swiss_knife.global_hotkey.is_virtual_key_down", return_value=True):
        manager._begin_hold("OnScreenshotRegion", vk=0x33)
        manager._hold_clock = clock
        manager._on_hold_poll()

    assert long_presses == ["OnScreenshotRegion"]
    assert triggered == []
    manager.unregister_all()
    manager.deleteLater()


def test_capture_picker_lists_four_actions(qapp: QApplication) -> None:  # noqa: ARG001
    dialog = CaptureActionPickerDialog()
    try:
        assert dialog._list.count() == len(CAPTURE_PICKER_ACTIONS)
        names = [
            dialog._list.item(index).data(Qt.ItemDataRole.UserRole) for index in range(dialog._list.count())
        ]
        assert set(names) == CAPTURE_HOTKEY_ACTIONS
    finally:
        dialog.close()
        dialog.deleteLater()


def test_capture_picker_accepts_selected_action(qapp: QApplication) -> None:  # noqa: ARG001
    dialog = CaptureActionPickerDialog()
    try:
        dialog._accept_action("OnRecordRegion")
        assert dialog.selected_action_name() == "OnRecordRegion"
        assert dialog.result() == QDialog.DialogCode.Accepted
    finally:
        dialog.close()
        dialog.deleteLater()


def test_choose_capture_hotkey_action_returns_none_on_cancel(qapp: QApplication) -> None:  # noqa: ARG001
    with patch.object(CaptureActionPickerDialog, "exec", return_value=QDialog.DialogCode.Rejected):
        assert choose_capture_hotkey_action() is None


def test_native_hotkey_starts_hold_for_capture_action(qapp: QApplication) -> None:
    manager = GlobalHotkeyManager(qapp)
    manager.set_long_press_actions({"OnScreenshotRegion"}, hold_ms=500)
    manager._id_to_action[1] = "OnScreenshotRegion"
    manager._id_to_vk[1] = 0x33

    begun: list[tuple[str, int]] = []
    with patch.object(manager, "_begin_hold", side_effect=lambda action, vk: begun.append((action, vk))):
        manager._on_native_hotkey(1)
        qapp.processEvents()

    assert begun == [("OnScreenshotRegion", 0x33)]
    manager.unregister_all()
    manager.deleteLater()
