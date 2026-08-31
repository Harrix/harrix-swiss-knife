"""Enumerate snappable screen rectangles for screenshot region capture.

Mirrors ShareX `WindowsRectangleList`: top-level frames, client areas (window without
chrome), child controls via `EnumChildWindows`, shell surfaces such as the taskbar,
and visible Qt top-level dialogs (owned `QDialog` Windows EnumWindows can miss).

"""

from __future__ import annotations

import ctypes
import sys
import time
from ctypes import wintypes
from dataclasses import dataclass
from typing import TYPE_CHECKING

from PySide6.QtCore import QPoint, QRect
from PySide6.QtWidgets import QApplication, QWidget

from harrix_swiss_knife.screenshot.window_visibility import is_screenshot_ui

if TYPE_CHECKING:
    from collections.abc import Sequence

_MIN_WINDOW_SIDE = 4
_HIDDEN_OPACITY = 0.01
_GWL_EXSTYLE = -20
_WS_EX_TOOLWINDOW = 0x00000080
_WS_EX_NOACTIVATE = 0x08000000
_DWMWA_EXTENDED_FRAME_BOUNDS = 9
_DWMWA_CLOAKED = 14
_ENUM_TIMEOUT_SEC = 3.0
_IGNORE_CLASS_NAMES = frozenset(
    {
        "CEF-OSC-WIDGET",  # NVIDIA GeForce Overlay
    }
)


class _Point(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]


@dataclass(frozen=True, slots=True)
class _SnapCandidate:
    rect: QRect
    is_window: bool


def filter_nested_control_candidates(candidates: Sequence[_SnapCandidate]) -> list[QRect]:
    """Keep top-level frames always; drop controls fully covered by an earlier region.

    ShareX builds the list depth-first (controls before parents). Hit-testing then picks
    the first rectangle that contains the cursor, so smaller regions stay preferred.

    Args:

    - `candidates` (`Sequence[_SnapCandidate]`): Raw snap candidates in discovery order.

    Returns:

    - `list[QRect]`: Filtered rectangles for hover snapping.

    """
    result: list[QRect] = []
    for candidate in candidates:
        if not candidate.is_window and any(existing.contains(candidate.rect) for existing in result):
            continue
        result.append(QRect(candidate.rect))
    return result


def list_snappable_window_rects(*, exclude_hwnds: Sequence[int] = ()) -> list[QRect]:
    """Return snappable regions in Qt logical global coordinates.

    Includes window frames, client areas, child controls, and the taskbar. Ordered so
    the first rectangle containing a point is the most specific match (ShareX-style).

    Args:

    - `exclude_hwnds` (`Sequence[int]`): Native window handles to skip (e.g. overlay).

    Returns:

    - `list[QRect]`: Snappable rectangles in global logical pixels.

    """
    excluded = {int(handle) for handle in exclude_hwnds if handle}
    win32_rects = _list_snappable_window_rects_win32(exclude_hwnds=excluded) if sys.platform == "win32" else []
    return merge_preferred_rects(win32_rects, _list_qt_top_level_rects(exclude_hwnds=excluded))


def merge_preferred_rects(rects: Sequence[QRect], preferred: Sequence[QRect]) -> list[QRect]:
    """Insert `preferred` Windows in front of any larger owner that contains them.

    Win32 `EnumWindows` can miss a Qt owned dialog (`QDialog` + `exec()`). The owner
    frame is then the first hit, so hover snaps to Finance instead of Balance check.
    Preferred rects (Qt top-level frames) are inserted just before that owner.

    Args:

    - `rects` (`Sequence[QRect]`): Snap candidates, most-specific first.
    - `preferred` (`Sequence[QRect]`): Extra window frames that must beat their owner.

    Returns:

    - `list[QRect]`: Combined list for hover snapping.

    """
    result = [QRect(rect) for rect in rects]
    for extra in preferred:
        if not extra.isValid() or extra.width() < _MIN_WINDOW_SIDE or extra.height() < _MIN_WINDOW_SIDE:
            continue
        if any(existing == extra for existing in result):
            continue
        insert_at = next(
            (index for index, existing in enumerate(result) if existing.contains(extra) and existing != extra),
            len(result),
        )
        result.insert(insert_at, QRect(extra))
    return result


def snap_rect_at_point(point: QPoint, window_rects: Sequence[QRect]) -> QRect | None:
    """Return the first rectangle that contains `point`, or `None`.

    Args:

    - `point` (`QPoint`): Cursor position in the same coordinate space as `window_rects`.
    - `window_rects` (`Sequence[QRect]`): Candidates ordered most-specific first.

    Returns:

    - `QRect | None`: Matching rectangle, or `None` when the point is outside all regions.

    """
    for rect in window_rects:
        if rect.contains(point):
            return QRect(rect)
    return None


def _client_rect_logical(user32: ctypes.WinDLL, hwnd: int) -> QRect | None:
    """Map `GetClientRect` to a logical global `QRect`."""
    client = wintypes.RECT()
    if not user32.GetClientRect(hwnd, ctypes.byref(client)):
        return None
    if client.right - client.left < _MIN_WINDOW_SIDE or client.bottom - client.top < _MIN_WINDOW_SIDE:
        return None
    top_left = _Point(0, 0)
    bottom_right = _Point(int(client.right), int(client.bottom))
    if not user32.ClientToScreen(hwnd, ctypes.byref(top_left)):
        return None
    if not user32.ClientToScreen(hwnd, ctypes.byref(bottom_right)):
        return None
    return _physical_points_to_logical(
        user32,
        hwnd,
        int(top_left.x),
        int(top_left.y),
        int(bottom_right.x),
        int(bottom_right.y),
    )


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


def _is_cloaked(dwmapi: ctypes.WinDLL, hwnd: int) -> bool:
    cloaked = ctypes.c_int(0)
    result = dwmapi.DwmGetWindowAttribute(
        hwnd,
        _DWMWA_CLOAKED,
        ctypes.byref(cloaked),
        ctypes.sizeof(cloaked),
    )
    return result == 0 and cloaked.value != 0


def _is_ignored_top_level(user32: ctypes.WinDLL, dwmapi: ctypes.WinDLL, hwnd: int) -> bool:
    """ShareX-style filters for top-level Windows only."""
    if user32.IsIconic(hwnd):
        return True
    if _is_cloaked(dwmapi, hwnd):
        return True

    class_buf = ctypes.create_unicode_buffer(256)
    user32.GetClassNameW(hwnd, class_buf, 256)
    if class_buf.value in _IGNORE_CLASS_NAMES:
        return True

    ex_style = int(user32.GetWindowLongW(hwnd, _GWL_EXSTYLE))
    # Non-activatable tool overlays (tiling managers, system auxiliaries).
    return bool(ex_style & _WS_EX_TOOLWINDOW and ex_style & _WS_EX_NOACTIVATE)


def _list_qt_top_level_rects(*, exclude_hwnds: set[int]) -> list[QRect]:
    """Return visible Qt window frames so owned dialogs stay snappable."""
    app = QApplication.instance()
    if app is None:
        return []
    rects: list[QRect] = []
    for widget in app.topLevelWidgets():
        if not isinstance(widget, QWidget) or not widget.isVisible() or is_screenshot_ui(widget):
            continue
        if widget.windowOpacity() <= _HIDDEN_OPACITY:
            continue
        try:
            handle = int(widget.winId())
        except (AttributeError, RuntimeError, TypeError, ValueError):
            handle = 0
        if handle and handle in exclude_hwnds:
            continue
        frame = QRect(widget.frameGeometry())
        if frame.isValid() and frame.width() >= _MIN_WINDOW_SIDE and frame.height() >= _MIN_WINDOW_SIDE:
            rects.append(frame)
        client = QRect(widget.geometry())
        if (
            client.isValid()
            and client != frame
            and client.width() >= _MIN_WINDOW_SIDE
            and client.height() >= _MIN_WINDOW_SIDE
        ):
            rects.append(client)
    return rects


def _list_snappable_window_rects_win32(*, exclude_hwnds: set[int]) -> list[QRect]:
    user32 = ctypes.windll.user32
    dwmapi = ctypes.windll.dwmapi
    candidates: list[_SnapCandidate] = []
    visited_parents: set[int] = set()
    deadline = time.monotonic() + _ENUM_TIMEOUT_SEC

    def check_handle(hwnd: int, clip_rect: QRect | None) -> bool:
        if time.monotonic() > deadline:
            return False
        if hwnd in exclude_hwnds or hwnd in visited_parents:
            return True
        if not user32.IsWindowVisible(hwnd):
            return True

        is_window = clip_rect is None
        if is_window and _is_ignored_top_level(user32, dwmapi, hwnd):
            return True

        if is_window:
            bounds = _extended_frame_bounds(user32, dwmapi, hwnd)
            if bounds is None:
                return True
            left, top, right, bottom = bounds
            rect = _physical_points_to_logical(user32, hwnd, left, top, right, bottom)
        else:
            win_rect = wintypes.RECT()
            if not user32.GetWindowRect(hwnd, ctypes.byref(win_rect)):
                return True
            rect = _physical_points_to_logical(
                user32,
                hwnd,
                int(win_rect.left),
                int(win_rect.top),
                int(win_rect.right),
                int(win_rect.bottom),
            )
            if rect is not None and clip_rect is not None:
                rect = rect.intersected(clip_rect)

        if rect is None or not rect.isValid() or rect.width() < _MIN_WINDOW_SIDE or rect.height() < _MIN_WINDOW_SIDE:
            return True

        if hwnd not in visited_parents:
            visited_parents.add(hwnd)

            @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
            def _enum_child(child: int, _lparam: int) -> bool:
                return check_handle(child, rect)

            user32.EnumChildWindows(hwnd, _enum_child, 0)

        if is_window:
            client = _client_rect_logical(user32, hwnd)
            if client is not None and client != rect and client.isValid():
                candidates.append(_SnapCandidate(rect=client, is_window=False))

        candidates.append(_SnapCandidate(rect=rect, is_window=is_window))
        return True

    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    def _enum_top(hwnd: int, _lparam: int) -> bool:
        return check_handle(hwnd, None)

    user32.EnumWindows(_enum_top, 0)
    foreground = int(user32.GetForegroundWindow() or 0)
    if foreground:
        check_handle(foreground, None)
    return filter_nested_control_candidates(candidates)


def _physical_points_to_logical(
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
        converted_left = bool(convert(hwnd, ctypes.byref(top_left)))
        converted_right = bool(convert(hwnd, ctypes.byref(bottom_right)))
        if not (converted_left and converted_right):
            top_left = _Point(left, top)
            bottom_right = _Point(right, bottom)
    width = max(0, int(bottom_right.x) - int(top_left.x))
    height = max(0, int(bottom_right.y) - int(top_left.y))
    if width < _MIN_WINDOW_SIDE or height < _MIN_WINDOW_SIDE:
        return None
    return QRect(int(top_left.x), int(top_left.y), width, height)
