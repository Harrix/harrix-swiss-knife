"""Best-effort Windows 11 system backdrop (Mica/Acrylic) for Qt Windows.

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
from typing import Any

logger = logging.getLogger(__name__)

_WINDOWS_11_MIN_BUILD = 22000
_APP_USER_MODEL_ID = "Harrix.SwissKnife"


class SystemBackdrop(IntEnum):
    """Values for DWMWA_SYSTEMBACKDROP_TYPE (Windows 11)."""

    AUTO = 0
    NONE = 1
    MICA = 2
    ACRYLIC = 3
    TABBED = 4


def ensure_windows_app_user_model_id() -> None:
    """Tell the Windows taskbar this process is Harrix Swiss Knife, not `python.exe`.

    Without an explicit ID, taskbar buttons sometimes take the Python icon and
    sometimes a blank window glyph, depending on which top-level window Windows
    groups the process under. Call this before the first window is created.

    """
    if sys.platform != "win32":
        return
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(_APP_USER_MODEL_ID)
    except Exception:
        logger.debug("SetCurrentProcessExplicitAppUserModelID failed", exc_info=True)


def try_apply_system_backdrop(window: Any, *, backdrop: SystemBackdrop = SystemBackdrop.MICA) -> bool:
    """Try to apply Windows 11 backdrop to a top-level Qt window.

    The frame is not extended over the whole client area. Full-window
    `DwmExtendFrameIntoClientArea` margins make the taskbar drop the window icon
    until the next time Windows redraws the button.

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

    dwmwa_system_backdrop_type = 38
    value = ctypes.c_int(int(backdrop))
    hr = dwm_set_window_attribute(hwnd, dwmwa_system_backdrop_type, ctypes.byref(value), ctypes.sizeof(value))
    if hr == 0:
        _reapply_taskbar_icon(window)
    return hr == 0


def _is_windows_11_or_newer() -> bool:
    if sys.platform != "win32":
        return False
    try:
        return sys.getwindowsversion().build >= _WINDOWS_11_MIN_BUILD
    except Exception:
        return False


def _reapply_taskbar_icon(window: Any) -> None:
    """Put the raster app icon back after DWM creates the native window."""
    try:
        from harrix_swiss_knife.installer.icon_assets import apply_window_icon  # noqa: PLC0415

        apply_window_icon(window)
    except Exception:
        logger.debug("Could not reapply window icon after backdrop", exc_info=True)
