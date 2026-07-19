"""Best-effort Windows 11 system backdrop (Mica/Acrylic) for Qt windows.

This module is intentionally defensive:

- no extra dependencies
- no effect on non-Windows platforms
- safe no-op on Windows versions that don't support the attribute

"""

from __future__ import annotations

import ctypes
import logging
import sys
from ctypes import wintypes
from enum import IntEnum
from typing import Any, ClassVar

logger = logging.getLogger(__name__)

_WINDOWS_11_MIN_BUILD = 22000


class SystemBackdrop(IntEnum):
    """Values for DWMWA_SYSTEMBACKDROP_TYPE (Windows 11)."""

    AUTO = 0
    NONE = 1
    MICA = 2
    ACRYLIC = 3
    TABBED = 4


def try_apply_system_backdrop(window: Any, *, backdrop: SystemBackdrop = SystemBackdrop.MICA) -> bool:
    """Try to apply Windows 11 backdrop to a top-level Qt window.

    Args:

    - `window`: A top-level Qt widget (e.g., QMainWindow, QDialog).
    - `backdrop`: Requested backdrop type.

    Returns:

    - `bool`: `True` if we called DWM successfully, `False` otherwise.

    """
    if not _is_windows_11_or_newer():
        return False

    try:
        hwnd = int(window.winId())  # Qt: sip.voidptr -> int
    except Exception:
        return False

    try:
        dwmapi = ctypes.WinDLL("dwmapi")
    except Exception:
        return False

    # HRESULT DwmSetWindowAttribute(HWND, DWORD, LPCVOID, DWORD)
    dwm_set_window_attribute = dwmapi.DwmSetWindowAttribute
    dwm_set_window_attribute.argtypes = [wintypes.HWND, wintypes.DWORD, wintypes.LPCVOID, wintypes.DWORD]
    dwm_set_window_attribute.restype = ctypes.c_long

    # HRESULT DwmExtendFrameIntoClientArea(HWND, const MARGINS*)
    class _MARGINS(ctypes.Structure):
        _fields_: ClassVar[list[tuple[str, Any]]] = [
            ("cxLeftWidth", ctypes.c_int),
            ("cxRightWidth", ctypes.c_int),
            ("cyTopHeight", ctypes.c_int),
            ("cyBottomHeight", ctypes.c_int),
        ]

    dwm_extend_frame_into_client_area = dwmapi.DwmExtendFrameIntoClientArea
    dwm_extend_frame_into_client_area.argtypes = [wintypes.HWND, ctypes.POINTER(_MARGINS)]
    dwm_extend_frame_into_client_area.restype = ctypes.c_long

    dwmwa_system_backdrop_type = 38

    # Some configurations need the frame extension for the backdrop to show up reliably.
    try:
        margins = _MARGINS(-1, -1, -1, -1)
        dwm_extend_frame_into_client_area(hwnd, ctypes.byref(margins))
    except Exception:
        logger.debug("DwmExtendFrameIntoClientArea failed", exc_info=True)

    value = ctypes.c_int(int(backdrop))
    hr = dwm_set_window_attribute(hwnd, dwmwa_system_backdrop_type, ctypes.byref(value), ctypes.sizeof(value))
    return hr == 0


def _is_windows_11_or_newer() -> bool:
    if sys.platform != "win32":
        return False
    try:
        return sys.getwindowsversion().build >= _WINDOWS_11_MIN_BUILD
    except Exception:
        return False
