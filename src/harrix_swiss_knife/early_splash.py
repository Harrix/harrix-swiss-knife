"""Native startup splash shown before Qt and heavy package imports.

A Win32 window on a background thread can appear as soon as `pythonw` starts.
The Qt toast cannot: it waits until `QApplication` and the rest of the package
are imported, which is most of the delay on a slow machine.

"""

from __future__ import annotations

import contextlib
import ctypes
import sys
import threading
import time
from ctypes import wintypes
from typing import Any

TRAY_LOADING_TITLE = "Harrix Swiss Knife"
_LOADING_LINE = "Loading..."
_SECONDS_PER_HOUR = 3600
_SECONDS_PER_MINUTE = 60
_WIDTH_DIP = 520
_HEIGHT_DIP = 180
_RADIUS_DIP = 16
_TITLE_PT = 20
_BODY_PT = 16
_WM_CLOSE = 0x0010
_WM_DESTROY = 0x0002
_WM_PAINT = 0x000F
_WM_ERASEBKGND = 0x0014
_WM_DPICHANGED = 0x02E0
_WM_QUIT = 0x0012
_WS_POPUP = 0x80000000
_WS_EX_COMPOSITED = 0x02000000
_WS_EX_NOACTIVATE = 0x08000000
_WS_EX_TOOLWINDOW = 0x00000080
_WS_EX_TOPMOST = 0x00000008
_SW_SHOWNOACTIVATE = 4
_SWP_NOACTIVATE = 0x0010
_HWND_TOPMOST = -1
_PM_REMOVE = 0x0001
_SPI_GETWORKAREA = 0x0030
_IDC_ARROW = 32512
_ERROR_CLASS_ALREADY_EXISTS = 1410
_PS_SOLID = 0
_SRCCOPY = 0x00CC0020
_FW_BOLD = 700
_DEFAULT_CHARSET = 1
_CLEARTYPE_QUALITY = 5
_TRANSPARENT = 1
_DT_CENTER = 0x0001
_DT_SINGLELINE = 0x0020
_DT_VCENTER = 0x0004
_POLL_S = 0.05
_CLASS_NAME = "HskStartupSplash"
_FILL_COLOR = 0x00282828
_BORDER_COLOR = 0x004A4A4A
_TEXT_COLOR = 0x00FFFFFF
_DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2 = -4
_PROCESS_PER_MONITOR_DPI_AWARE = 2

_LRESULT = ctypes.c_ssize_t
_WNDPROC = ctypes.WINFUNCTYPE(_LRESULT, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)


class _PaintStruct(ctypes.Structure):
    _fields_ = (
        ("hdc", wintypes.HDC),
        ("fErase", wintypes.BOOL),
        ("rcPaint", wintypes.RECT),
        ("fRestore", wintypes.BOOL),
        ("fIncUpdate", wintypes.BOOL),
        ("rgbReserved", wintypes.BYTE * 32),
    )


class _SplashRuntime:
    """Mutable splash process state."""

    bg_brush: int = 0
    class_info: Any = None
    hwnd: int = 0
    last_clock: str = ""
    last_rect: tuple[int, int, int, int] = (0, 0, 0, 0)
    started_at: float = 0.0
    stop: threading.Event = threading.Event()
    thread: threading.Thread | None = None
    wndproc: Any = None


class _WndClassW(ctypes.Structure):
    _fields_ = (
        ("style", wintypes.UINT),
        ("lpfnWndProc", _WNDPROC),
        ("cbClsExtra", ctypes.c_int),
        ("cbWndExtra", ctypes.c_int),
        ("hInstance", wintypes.HINSTANCE),
        ("hIcon", wintypes.HANDLE),
        ("hCursor", wintypes.HANDLE),
        ("hbrBackground", wintypes.HBRUSH),
        ("lpszMenuName", wintypes.LPCWSTR),
        ("lpszClassName", wintypes.LPCWSTR),
    )


def close_early_splash() -> None:
    """Close the splash if it is showing."""
    _runtime.stop.set()
    with _lock:
        hwnd = _runtime.hwnd
        thread = _runtime.thread
    if hwnd:
        with contextlib.suppress(OSError):
            _user32().PostMessageW(hwnd, _WM_CLOSE, 0, 0)
    if thread is not None:
        thread.join(timeout=2.0)
    with _lock:
        _runtime.hwnd = 0
        _runtime.thread = None


def early_splash_hwnd() -> int:
    """Return the splash window handle, or `0` when it is not showing."""
    with _lock:
        return _runtime.hwnd


def ensure_early_splash() -> None:
    """Show a topmost splash as soon as the process starts."""
    if sys.platform != "win32" or _qt_app_exists():
        return
    _enable_dpi_awareness()
    with _lock:
        thread = _runtime.thread
        if thread is not None and thread.is_alive():
            return
    try:
        _start_thread()
    except (OSError, ValueError, AttributeError):
        close_early_splash()


def format_splash_clock(seconds: int) -> str:
    """Format elapsed seconds as `MM:SS`, or `HH:MM:SS` after 60 minutes."""
    total = max(0, int(seconds))
    if total >= _SECONDS_PER_HOUR:
        hours, rem = divmod(total, _SECONDS_PER_HOUR)
        minutes, secs = divmod(rem, _SECONDS_PER_MINUTE)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    minutes, secs = divmod(total, _SECONDS_PER_MINUTE)
    return f"{minutes:02d}:{secs:02d}"


def splash_status_lines(seconds: int) -> tuple[str, str, str]:
    """Return the three splash lines: title, status, and clock."""
    return TRAY_LOADING_TITLE, _LOADING_LINE, format_splash_clock(seconds)


def _apply_window_geometry(user32: ctypes.WinDLL, hwnd: int) -> bool:
    x, y, width, height = _centered_rect(hwnd)
    target = (x, y, width, height)
    current = _current_rect(hwnd)
    if current == target and _runtime.last_rect == target:
        return False
    user32.SetWindowPos(hwnd, _HWND_TOPMOST, x, y, width, height, _SWP_NOACTIVATE)
    _runtime.last_rect = target
    return True


def _centered_rect(hwnd: int) -> tuple[int, int, int, int]:
    dpi = _dpi_for_hwnd(hwnd)
    width = _dip(_WIDTH_DIP, dpi)
    height = _dip(_HEIGHT_DIP, dpi)
    left, top, right, bottom = _work_area()
    x = left + max(0, (right - left - width) // 2)
    y = top + max(0, (bottom - top - height) // 2)
    return x, y, width, height


def _client_rect(hwnd: int) -> wintypes.RECT:
    rect = wintypes.RECT()
    _user32().GetClientRect(hwnd, ctypes.byref(rect))
    return rect


def _create_font(gdi32: ctypes.WinDLL, *, point_size: int, dpi: int) -> int:
    height = -max(1, round(point_size * dpi / 72))
    return int(
        gdi32.CreateFontW(
            height,
            0,
            0,
            0,
            _FW_BOLD,
            0,
            0,
            0,
            _DEFAULT_CHARSET,
            0,
            0,
            _CLEARTYPE_QUALITY,
            0,
            "Segoe UI",
        )
        or 0,
    )


def _current_rect(hwnd: int) -> tuple[int, int, int, int]:
    rect = wintypes.RECT()
    if not _user32().GetWindowRect(hwnd, ctypes.byref(rect)):
        return (0, 0, 0, 0)
    return (int(rect.left), int(rect.top), int(rect.right - rect.left), int(rect.bottom - rect.top))


def _dip(value: int, dpi: int) -> int:
    return max(1, round(value * dpi / 96))


def _dpi_for_hwnd(hwnd: int) -> int:
    if hwnd:
        with contextlib.suppress(AttributeError, OSError, ValueError):
            dpi = int(_user32().GetDpiForWindow(hwnd))
            if dpi > 0:
                return dpi
    return _system_dpi()


def _draw_line(
    user32: ctypes.WinDLL,
    gdi32: ctypes.WinDLL,
    hdc: int,
    text: str,
    box: wintypes.RECT,
    font: int,
) -> None:
    previous = gdi32.SelectObject(hdc, font) if font else 0
    user32.DrawTextW(hdc, text, -1, ctypes.byref(box), _DT_CENTER | _DT_SINGLELINE | _DT_VCENTER)
    if previous:
        gdi32.SelectObject(hdc, previous)


def _enable_dpi_awareness() -> None:
    user32 = _user32()
    with contextlib.suppress(AttributeError, OSError):
        if user32.SetProcessDpiAwarenessContext(
            ctypes.c_void_p(_DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2),
        ):
            return
    with contextlib.suppress(AttributeError, OSError):
        ctypes.WinDLL("shcore", use_last_error=True).SetProcessDpiAwareness(_PROCESS_PER_MONITOR_DPI_AWARE)
        return
    with contextlib.suppress(AttributeError, OSError):
        user32.SetProcessDPIAware()


def _gdi32() -> ctypes.WinDLL:
    return ctypes.WinDLL("gdi32", use_last_error=True)


def _invalidate_if_clock_changed(user32: ctypes.WinDLL, hwnd: int) -> None:
    clock = format_splash_clock(int(time.monotonic() - _runtime.started_at))
    if clock == _runtime.last_clock:
        return
    user32.InvalidateRect(hwnd, None, False)  # noqa: FBT003


def _kernel32() -> ctypes.WinDLL:
    return ctypes.WinDLL("kernel32", use_last_error=True)


def _paint(hwnd: int) -> None:
    user32 = _user32()
    gdi32 = _gdi32()
    paint = _PaintStruct()
    hdc = user32.BeginPaint(hwnd, ctypes.byref(paint))
    if not hdc:
        return
    try:
        rect = _client_rect(hwnd)
        width = int(rect.right - rect.left)
        height = int(rect.bottom - rect.top)
        mem_dc = gdi32.CreateCompatibleDC(hdc)
        bitmap = gdi32.CreateCompatibleBitmap(hdc, width, height) if mem_dc else 0
        old_bitmap = gdi32.SelectObject(mem_dc, bitmap) if mem_dc and bitmap else 0
        target = mem_dc if mem_dc and bitmap else hdc
        fill = gdi32.CreateSolidBrush(_FILL_COLOR)
        if fill:
            user32.FillRect(target, ctypes.byref(rect), fill)
        pen = gdi32.CreatePen(_PS_SOLID, 1, _BORDER_COLOR)
        old_brush = gdi32.SelectObject(target, fill) if fill else 0
        old_pen = gdi32.SelectObject(target, pen) if pen else 0
        radius = _dip(_RADIUS_DIP, _dpi_for_hwnd(hwnd))
        gdi32.RoundRect(target, 0, 0, width, height, radius, radius)
        if old_brush:
            gdi32.SelectObject(target, old_brush)
        if old_pen:
            gdi32.SelectObject(target, old_pen)
        if pen:
            gdi32.DeleteObject(pen)
        if fill:
            gdi32.DeleteObject(fill)
        gdi32.SetBkMode(target, _TRANSPARENT)
        gdi32.SetTextColor(target, _TEXT_COLOR)
        dpi = _dpi_for_hwnd(hwnd)
        title_font = _create_font(gdi32, point_size=_TITLE_PT, dpi=dpi)
        body_font = _create_font(gdi32, point_size=_BODY_PT, dpi=dpi)
        title, status, clock = splash_status_lines(int(time.monotonic() - _runtime.started_at))
        _runtime.last_clock = clock
        band = max(1, height // 3)
        _draw_line(user32, gdi32, target, title, _rect(0, band // 8, width, band), title_font)
        _draw_line(user32, gdi32, target, status, _rect(0, band, width, band), body_font)
        _draw_line(user32, gdi32, target, clock, _rect(0, band * 2 - band // 8, width, band), body_font)
        if title_font:
            gdi32.DeleteObject(title_font)
        if body_font:
            gdi32.DeleteObject(body_font)
        if mem_dc and bitmap:
            gdi32.BitBlt(hdc, 0, 0, width, height, mem_dc, 0, 0, _SRCCOPY)
            gdi32.SelectObject(mem_dc, old_bitmap)
            gdi32.DeleteObject(bitmap)
            gdi32.DeleteObject(mem_dc)
    finally:
        user32.EndPaint(hwnd, ctypes.byref(paint))


def _pump_once(user32: ctypes.WinDLL, msg: wintypes.MSG) -> bool:
    while user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, _PM_REMOVE):
        if int(msg.message) == _WM_QUIT:
            return False
        user32.TranslateMessage(ctypes.byref(msg))
        user32.DispatchMessageW(ctypes.byref(msg))
    return True


def _qt_app_exists() -> bool:
    qt_widgets = sys.modules.get("PySide6.QtWidgets")
    if qt_widgets is None:
        return False
    instance = getattr(qt_widgets.QApplication, "instance", None)
    if not callable(instance):
        return False
    return instance() is not None


def _rect(x: int, y: int, width: int, height: int) -> wintypes.RECT:
    box = wintypes.RECT()
    box.left = x
    box.top = y
    box.right = x + width
    box.bottom = y + height
    return box


def _register_class(user32: ctypes.WinDLL, instance: int) -> None:
    if _runtime.wndproc is not None:
        return
    wndproc = _WNDPROC(_wndproc)
    class_info = _WndClassW()
    if not _runtime.bg_brush:
        _runtime.bg_brush = int(_gdi32().CreateSolidBrush(_FILL_COLOR) or 0)
    class_info.lpfnWndProc = wndproc
    class_info.hInstance = instance
    class_info.hCursor = user32.LoadCursorW(None, ctypes.c_void_p(_IDC_ARROW))
    class_info.hbrBackground = _runtime.bg_brush
    class_info.lpszClassName = _CLASS_NAME
    _runtime.wndproc = wndproc
    _runtime.class_info = class_info
    if user32.RegisterClassW(ctypes.byref(class_info)):
        return
    if ctypes.get_last_error() != _ERROR_CLASS_ALREADY_EXISTS:
        _runtime.wndproc = None
        _runtime.class_info = None
        msg = "RegisterClassW failed"
        raise OSError(msg)


def _run_message_loop() -> None:
    user32 = _user32()
    instance = int(_kernel32().GetModuleHandleW(None) or 0)
    _register_class(user32, instance)
    x, y, width, height = _centered_rect(0)
    hwnd = int(
        user32.CreateWindowExW(
            _WS_EX_TOPMOST | _WS_EX_TOOLWINDOW | _WS_EX_NOACTIVATE | _WS_EX_COMPOSITED,
            _CLASS_NAME,
            TRAY_LOADING_TITLE,
            _WS_POPUP,
            x,
            y,
            width,
            height,
            None,
            None,
            instance,
            None,
        )
        or 0,
    )
    if not hwnd:
        return
    with _lock:
        _runtime.hwnd = hwnd
    _apply_window_geometry(user32, hwnd)
    user32.UpdateWindow(hwnd)
    user32.ShowWindow(hwnd, _SW_SHOWNOACTIVATE)
    msg = wintypes.MSG()
    while not _runtime.stop.is_set() and _pump_once(user32, msg):
        if _apply_window_geometry(user32, hwnd):
            user32.InvalidateRect(hwnd, None, False)  # noqa: FBT003
        _invalidate_if_clock_changed(user32, hwnd)
        time.sleep(_POLL_S)
    with contextlib.suppress(OSError):
        user32.DestroyWindow(hwnd)
    with _lock:
        if _runtime.hwnd == hwnd:
            _runtime.hwnd = 0


def _start_thread() -> None:
    _runtime.stop = threading.Event()
    _runtime.started_at = time.monotonic()
    thread = threading.Thread(target=_run_message_loop, name="hsk-startup-splash", daemon=True)
    with _lock:
        _runtime.thread = thread
    thread.start()


def _system_dpi() -> int:
    with contextlib.suppress(AttributeError, OSError, ValueError):
        dpi = int(_user32().GetDpiForSystem())
        if dpi > 0:
            return dpi
    return 96


def _user32() -> ctypes.WinDLL:
    lib = ctypes.WinDLL("user32", use_last_error=True)
    lib.DefWindowProcW.restype = _LRESULT
    lib.DefWindowProcW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
    lib.CreateWindowExW.restype = wintypes.HWND
    return lib


def _wndproc(hwnd: int, message: int, wparam: int, lparam: int) -> int:
    user32 = _user32()
    if message == _WM_ERASEBKGND:
        return 1
    if message == _WM_PAINT:
        _paint(int(hwnd))
        return 0
    if message == _WM_DPICHANGED:
        _apply_window_geometry(user32, int(hwnd))
        return 0
    if message == _WM_CLOSE:
        user32.DestroyWindow(hwnd)
        return 0
    if message == _WM_DESTROY:
        user32.PostQuitMessage(0)
        return 0
    return int(user32.DefWindowProcW(hwnd, message, wparam, lparam))


def _work_area() -> tuple[int, int, int, int]:
    rect = wintypes.RECT()
    if not _user32().SystemParametersInfoW(_SPI_GETWORKAREA, 0, ctypes.byref(rect), 0):
        dpi = _system_dpi()
        return 0, 0, _dip(_WIDTH_DIP, dpi), _dip(_HEIGHT_DIP, dpi)
    return int(rect.left), int(rect.top), int(rect.right), int(rect.bottom)


_lock = threading.Lock()
_runtime = _SplashRuntime()
