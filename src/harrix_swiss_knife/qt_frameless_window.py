"""Helpers for frameless Qt Windows that stay resizable on Windows."""

from __future__ import annotations

import sys
from typing import Any

from PySide6.QtCore import QByteArray, QPoint, QSize, Qt
from PySide6.QtWidgets import QAbstractButton, QWidget

_FRAMELESS_BORDER = 8

_HTCLIENT = 1
_HTLEFT = 10
_HTRIGHT = 11
_HTTOP = 12
_HTTOPLEFT = 13
_HTTOPRIGHT = 14
_HTBOTTOM = 15
_HTBOTTOMLEFT = 16
_HTBOTTOMRIGHT = 17

if sys.platform == "win32":
    import ctypes
    from ctypes import wintypes

    _WM_NCHITTEST = 0x0084


def frameless_hit_test(local: QPoint, size: QSize, *, border: int = _FRAMELESS_BORDER) -> int:
    """Return a Win32 `HT*` code for a local point on a frameless window.

    Args:

    - `local` (`QPoint`): Position in the window's logical coordinates.
    - `size` (`QSize`): Window size in logical pixels.
    - `border` (`int`): Resize strip thickness in logical pixels. Defaults to `8`.

    Returns:

    - `int`: `HTCLIENT` or an edge/corner `HT*` value.

    """
    on_left = local.x() < border
    on_right = local.x() >= size.width() - border
    on_top = local.y() < border
    on_bottom = local.y() >= size.height() - border

    if on_top and on_left:
        return _HTTOPLEFT
    if on_top and on_right:
        return _HTTOPRIGHT
    if on_bottom and on_left:
        return _HTBOTTOMLEFT
    if on_bottom and on_right:
        return _HTBOTTOMRIGHT
    if on_left:
        return _HTLEFT
    if on_right:
        return _HTRIGHT
    if on_top:
        return _HTTOP
    if on_bottom:
        return _HTBOTTOM
    return _HTCLIENT


def frameless_local_from_native(
    *,
    native_x: int,
    native_y: int,
    window_left: int,
    window_top: int,
    device_pixel_ratio: float,
) -> QPoint:
    """Convert a native screen point to logical coordinates inside the window.

    `WM_NCHITTEST` gives physical pixels. Qt layouts and `childAt` use logical
    pixels. Passing native coordinates into `mapFromGlobal` on a scaled display
    inflates the resize strip so it covers the close button.

    """
    dpr = device_pixel_ratio if device_pixel_ratio > 0 else 1.0
    return QPoint(
        round((native_x - window_left) / dpr),
        round((native_y - window_top) / dpr),
    )


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
    local = _nchittest_local_point(widget, global_x, global_y)
    if local is None:
        return None
    if _blocks_frameless_resize(widget, local):
        return True, _HTCLIENT
    return True, frameless_hit_test(local, widget.size(), border=border)


def _blocks_frameless_resize(widget: QWidget, local: QPoint) -> bool:
    """Return whether `local` is over a button that must keep mouse clicks."""
    child = widget.childAt(local)
    while child is not None and child is not widget:
        if isinstance(child, QAbstractButton):
            return True
        child = child.parentWidget()
    return False


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


def _nchittest_local_point(widget: QWidget, native_x: int, native_y: int) -> QPoint | None:
    """Map a native `WM_NCHITTEST` screen point to the widget's logical coords."""
    if sys.platform != "win32":
        return None
    hwnd = int(widget.winId())
    if not hwnd:
        return None
    rect = wintypes.RECT()
    if not ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect)):
        return None
    return frameless_local_from_native(
        native_x=native_x,
        native_y=native_y,
        window_left=int(rect.left),
        window_top=int(rect.top),
        device_pixel_ratio=widget.devicePixelRatioF(),
    )
