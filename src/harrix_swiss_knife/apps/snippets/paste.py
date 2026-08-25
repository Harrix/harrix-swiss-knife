"""Paste text into the foreground editor and restore the previous clipboard."""

from __future__ import annotations

import ctypes
import sys
from ctypes import wintypes
from functools import lru_cache
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import QMimeData, QTimer
from PySide6.QtWidgets import QApplication

if TYPE_CHECKING:
    from collections.abc import Callable

_PASTE_DELAY_MS = 120
_RESTORE_DELAY_MS = 180
_INPUT_KEYBOARD = 1
_KEYEVENTF_KEYUP = 0x0002
_VK_CONTROL = 0x11
_VK_V = 0x56
_CTRL_V_EVENT_COUNT = 4


def clone_clipboard_mime() -> QMimeData:
    """Return a copy of the current clipboard contents."""
    clone = QMimeData()
    clipboard = QApplication.clipboard()
    if clipboard is None:
        return clone
    source = clipboard.mimeData()
    if source is None:
        return clone
    for fmt in source.formats():
        clone.setData(fmt, source.data(fmt))
    return clone


def paste_text_then_restore_clipboard(
    text: str,
    saved: QMimeData,
    *,
    on_finished: Callable[[], None] | None = None,
    paste_delay_ms: int = _PASTE_DELAY_MS,
    restore_delay_ms: int = _RESTORE_DELAY_MS,
) -> None:
    """Set clipboard to `text`, paste, then restore `saved`."""

    def restore() -> None:
        restore_clipboard_mime(saved)
        if on_finished is not None:
            on_finished()

    def paste() -> None:
        clipboard = QApplication.clipboard()
        if clipboard is not None:
            clipboard.setText(text)
        send_ctrl_v()
        QTimer.singleShot(restore_delay_ms, restore)

    app = QApplication.instance()
    if app is not None:
        app.processEvents()
    QTimer.singleShot(paste_delay_ms, paste)


def restore_clipboard_mime(mime: QMimeData) -> None:
    """Replace the clipboard with a previously cloned `QMimeData`."""
    clipboard = QApplication.clipboard()
    if clipboard is None:
        return
    clipboard.setMimeData(mime)


def send_ctrl_v() -> bool:
    """Send Ctrl+V to the focused window on Windows."""
    if sys.platform != "win32":
        return False
    send_input, keybd_input = _send_input_types()
    extra = ctypes.c_ulong(0)
    extra_ptr = ctypes.pointer(extra)

    def key_event(vk: int, flags: int = 0) -> Any:
        event = send_input()
        event.type = _INPUT_KEYBOARD
        event.union.ki = keybd_input(vk, 0, flags, 0, extra_ptr)
        return event

    events = (send_input * _CTRL_V_EVENT_COUNT)(
        key_event(_VK_CONTROL),
        key_event(_VK_V),
        key_event(_VK_V, _KEYEVENTF_KEYUP),
        key_event(_VK_CONTROL, _KEYEVENTF_KEYUP),
    )
    sent = ctypes.windll.user32.SendInput(_CTRL_V_EVENT_COUNT, ctypes.byref(events), ctypes.sizeof(send_input))
    return sent == _CTRL_V_EVENT_COUNT


@lru_cache(maxsize=1)
def _send_input_types() -> tuple[type[Any], type[Any]]:
    """Build Win32 INPUT structures in dependency order."""

    class MouseInput(ctypes.Structure):
        _fields_ = (
            ("dx", wintypes.LONG),
            ("dy", wintypes.LONG),
            ("mouseData", wintypes.DWORD),
            ("dwFlags", wintypes.DWORD),
            ("time", wintypes.DWORD),
            ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
        )

    class KeybdInput(ctypes.Structure):
        _fields_ = (
            ("wVk", wintypes.WORD),
            ("wScan", wintypes.WORD),
            ("dwFlags", wintypes.DWORD),
            ("time", wintypes.DWORD),
            ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
        )

    class HardwareInput(ctypes.Structure):
        _fields_ = (
            ("uMsg", wintypes.DWORD),
            ("wParamL", wintypes.WORD),
            ("wParamH", wintypes.WORD),
        )

    class InputUnion(ctypes.Union):
        _fields_ = (("mi", MouseInput), ("ki", KeybdInput), ("hi", HardwareInput))

    class SendInput(ctypes.Structure):
        _fields_ = (("type", wintypes.DWORD), ("union", InputUnion))

    return SendInput, KeybdInput
