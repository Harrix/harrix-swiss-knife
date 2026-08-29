"""Enumerate visible top-level window rectangles for screenshot region snapping."""

from __future__ import annotations

import ctypes
import sys
from ctypes import wintypes
from typing import TYPE_CHECKING

from PySide6.QtCore import QPoint, QRect

if TYPE_CHECKING:
    from collections.abc import Sequence

_MIN_WINDOW_SIDE = 8
_GW_OWNER = 4
_GWL_EXSTYLE = -20
_WS_EX_TOOLWINDOW = 0x00000080
_WS_EX_APPWINDOW = 0x00040000
_DWMWA_EXTENDED_FRAME_BOUNDS = 9
_DWMWA_CLOAKED = 14
_SHELL_CLASSES = frozenset({"Progman", "WorkerW", "Shell_TrayWnd", "Shell_SecondaryTrayWnd"})


class _Point(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]


def list_snappable_window_rects(*, exclude_hwnds: Sequence[int] = ()) -> list[QRect]:
    """Return visible top-level window bounds in Qt logical global coordinates.

    Rectangles are ordered top-most first (same as Win32 `EnumWindows`). Non-Windows
    platforms return an empty list.

    Args:

    - `exclude_hwnds` (`Sequence[int]`): Native window handles to skip (e.g. overlay).

    Returns:

    - `list[QRect]`: Snappable window rectangles in global logical pixels.

    """
    if sys.platform != "win32":
        return []
    excluded = {int(handle) for handle in exclude_hwnds if handle}
    return _list_snappable_window_rects_win32(exclude_hwnds=excluded)


def snap_rect_at_point(point: QPoint, window_rects: Sequence[QRect]) -> QRect | None:
    """Return the top-most rectangle that contains `point`, or `None`.

    Args:

    - `point` (`QPoint`): Cursor position in the same coordinate space as `window_rects`.
    - `window_rects` (`Sequence[QRect]`): Candidates ordered top-most first.

    Returns:

    - `QRect | None`: Matching rectangle, or `None` when the point is outside all Windows.

    """
    for rect in window_rects:
        if rect.contains(point):
            return QRect(rect)
    return None


def _extended_frame_bounds(user32: ctypes.WinDLL, dwmapi: ctypes.WinDLL, hwnd: int) -> tuple[int, int, int, int] | None:
    """Return physical pixel bounds, preferring DWM extended frame over GetWindowRect."""
    dwm_rect = wintypes.RECT()
    dwm_ok = (
        dwmapi.DwmGetWindowAttribute(
            hwnd,
            _DWMWA_EXTENDED_FRAME_BOUNDS,
            ctypes.byref(dwm_rect),
            ctypes.sizeof(dwm_rect),
        )
        == 0
    )
    if dwm_ok:
        return int(dwm_rect.left), int(dwm_rect.top), int(dwm_rect.right), int(dwm_rect.bottom)

    win_rect = wintypes.RECT()
    if not user32.GetWindowRect(hwnd, ctypes.byref(win_rect)):
        return None
    return int(win_rect.left), int(win_rect.top), int(win_rect.right), int(win_rect.bottom)


def _is_alt_tab_window(user32: ctypes.WinDLL, hwnd: int) -> bool:
    """Skip tool Windows, owned popups, and shell helper Windows."""
    if user32.GetWindow(hwnd, _GW_OWNER):
        return False

    ex_style = int(user32.GetWindowLongW(hwnd, _GWL_EXSTYLE))
    if ex_style & _WS_EX_TOOLWINDOW and not (ex_style & _WS_EX_APPWINDOW):
        return False

    class_buf = ctypes.create_unicode_buffer(256)
    user32.GetClassNameW(hwnd, class_buf, 256)
    return class_buf.value not in _SHELL_CLASSES


def _is_cloaked(dwmapi: ctypes.WinDLL, hwnd: int) -> bool:
    cloaked = ctypes.c_int(0)
    result = dwmapi.DwmGetWindowAttribute(
        hwnd,
        _DWMWA_CLOAKED,
        ctypes.byref(cloaked),
        ctypes.sizeof(cloaked),
    )
    return result == 0 and cloaked.value != 0


def _list_snappable_window_rects_win32(*, exclude_hwnds: set[int]) -> list[QRect]:
    user32 = ctypes.windll.user32
    dwmapi = ctypes.windll.dwmapi
    rects: list[QRect] = []

    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    def _enum_proc(hwnd: int, _lparam: int) -> bool:
        if hwnd in exclude_hwnds:
            return True
        if not user32.IsWindowVisible(hwnd):
            return True
        if user32.IsIconic(hwnd):
            return True
        if _is_cloaked(dwmapi, hwnd):
            return True
        if not _is_alt_tab_window(user32, hwnd):
            return True

        bounds = _extended_frame_bounds(user32, dwmapi, hwnd)
        if bounds is None:
            return True
        left, top, right, bottom = bounds
        if right - left < _MIN_WINDOW_SIDE or bottom - top < _MIN_WINDOW_SIDE:
            return True

        logical = _physical_rect_to_logical(user32, hwnd, left, top, right, bottom)
        if logical is None or logical.width() < _MIN_WINDOW_SIDE or logical.height() < _MIN_WINDOW_SIDE:
            return True
        rects.append(logical)
        return True

    user32.EnumWindows(_enum_proc, 0)
    return rects


def _physical_rect_to_logical(
    user32: ctypes.WinDLL,
    hwnd: int,
    left: int,
    top: int,
    right: int,
    bottom: int,
) -> QRect | None:
    top_left = _Point(left, top)
    bottom_right = _Point(right, bottom)
    convert = getattr(user32, "PhysicalToLogicalPointForPerMonitorDPI", None)
    if convert is not None:
        if not convert(hwnd, ctypes.byref(top_left)):
            return None
        if not convert(hwnd, ctypes.byref(bottom_right)):
            return None
    return QRect(
        int(top_left.x),
        int(top_left.y),
        max(0, int(bottom_right.x) - int(top_left.x)),
        max(0, int(bottom_right.y) - int(top_left.y)),
    )
