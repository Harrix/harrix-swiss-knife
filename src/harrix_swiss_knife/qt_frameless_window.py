"""Helpers for frameless Qt windows that stay resizable on Windows."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import QByteArray, QPoint, Qt

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget

_FRAMELESS_BORDER = 8

if sys.platform == "win32":
    import ctypes
    from ctypes import wintypes

    _WM_NCHITTEST = 0x0084
    _HTCLIENT = 1
    _HTLEFT = 10
    _HTRIGHT = 11
    _HTTOP = 12
    _HTTOPLEFT = 13
    _HTTOPRIGHT = 14
    _HTBOTTOM = 15
    _HTBOTTOMLEFT = 16
    _HTBOTTOMRIGHT = 17


def frameless_stay_on_top_flags() -> Qt.WindowType:
    """Return window flags for a frameless stay-on-top tool window."""
    return Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint


def try_handle_frameless_resize_native_event(
    widget: QWidget,
    event_type: bytes | bytearray | memoryview | QByteArray | str,
    message: Any,
    *,
    border: int = _FRAMELESS_BORDER,
) -> tuple[bool, int] | None:
    """Handle WM_NCHITTEST so a frameless window can be resized from edges on Windows."""
    if sys.platform != "win32" or _event_type_to_bytes(event_type) != b"windows_generic_MSG":
        return None

    address = _message_address(message)
    if address is None:
        return None

    try:
        msg = wintypes.MSG.from_address(address)
    except (TypeError, ValueError, OverflowError):
        return None

    if msg.message != _WM_NCHITTEST:
        return None

    global_x = ctypes.c_short(msg.lParam & 0xFFFF).value
    global_y = ctypes.c_short((msg.lParam >> 16) & 0xFFFF).value
    local = widget.mapFromGlobal(QPoint(global_x, global_y))
    rect = widget.rect()

    on_left = local.x() < border
    on_right = local.x() >= rect.width() - border
    on_top = local.y() < border
    on_bottom = local.y() >= rect.height() - border

    if on_top and on_left:
        return True, _HTTOPLEFT
    if on_top and on_right:
        return True, _HTTOPRIGHT
    if on_bottom and on_left:
        return True, _HTBOTTOMLEFT
    if on_bottom and on_right:
        return True, _HTBOTTOMRIGHT
    if on_left:
        return True, _HTLEFT
    if on_right:
        return True, _HTRIGHT
    if on_top:
        return True, _HTTOP
    if on_bottom:
        return True, _HTBOTTOM
    return True, _HTCLIENT


def _event_type_to_bytes(event_type: bytes | bytearray | memoryview | QByteArray | str) -> bytes:
    if isinstance(event_type, QByteArray):
        return bytes(event_type.data())
    if isinstance(event_type, memoryview):
        return event_type.tobytes()
    if isinstance(event_type, str):
        return event_type.encode("utf-8")
    return bytes(event_type)


def _message_address(message: Any) -> int | None:
    """Convert PySide6 nativeEvent message pointer to an integer address."""
    if isinstance(message, int):
        return message

    for converter in (
        int,
        lambda value: int(value.__int__()),  # Shiboken VoidPtr
        lambda value: ctypes.cast(value, ctypes.c_void_p).value,
    ):
        try:
            address = converter(message)
        except (AttributeError, TypeError, ValueError, OverflowError):
            continue
        if isinstance(address, int) and address:
            return address
    return None
