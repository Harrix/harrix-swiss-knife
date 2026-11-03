"""Native startup splash shown before Qt and heavy package imports.

A Win32 window on a background thread can appear as soon as `pythonw` starts.
The Qt toast cannot: it waits until `QApplication` and the rest of the package
are imported, which is most of the delay on a slow machine.

After `AUTO_MINIMIZE_SECONDS`, or when the minimize control is clicked, the
splash collapses into a compact toast at the bottom-right of the work area.
Click the expand control on the toast to restore the centered splash.

"""

from __future__ import annotations

import contextlib
import ctypes
import sys
import threading
import time
from ctypes import wintypes
from pathlib import Path
from typing import Any

TRAY_LOADING_TITLE = "Harrix Swiss Knife"
_LOADING_LINE = "Loading..."
_SECONDS_PER_HOUR = 3600
_SECONDS_PER_MINUTE = 60
_WIDTH_DIP = 400
_HEIGHT_DIP = 160
_TOAST_WIDTH_DIP = 300
_TOAST_HEIGHT_DIP = 72
_TOAST_MARGIN_DIP = 20
_RADIUS_DIP = 8
_LOGO_DIP = 72
_TOAST_LOGO_DIP = 40
_PAD_DIP = 28
_TOAST_PAD_DIP = 14
_GAP_DIP = 20
_BUTTON_DIP = 28
_TITLE_PT = 20
_BODY_PT = 16
_TOAST_TITLE_PT = 14
_TOAST_BODY_PT = 12
AUTO_MINIMIZE_SECONDS = 3.0
_WM_CLOSE = 0x0010
_WM_DESTROY = 0x0002
_WM_PAINT = 0x000F
_WM_ERASEBKGND = 0x0014
_WM_DPICHANGED = 0x02E0
_WM_QUIT = 0x0012
_WM_LBUTTONUP = 0x0202
_WM_MOUSEMOVE = 0x0200
_WM_SETCURSOR = 0x0020
_WM_APP = 0x8000
_WM_SET_MINIMIZED = _WM_APP + 1
_WS_POPUP = 0x80000000
_WS_EX_COMPOSITED = 0x02000000
_WS_EX_NOACTIVATE = 0x08000000
_WS_EX_TOOLWINDOW = 0x00000080
_WS_EX_TOPMOST = 0x00000008
_SW_SHOWNOACTIVATE = 4
_SWP_NOACTIVATE = 0x0010
_HWND_TOPMOST = -1
_HTCLIENT = 1
_PM_REMOVE = 0x0001
_SPI_GETWORKAREA = 0x0030
_IDC_ARROW = 32512
_IDC_HAND = 32649
_ERROR_CLASS_ALREADY_EXISTS = 1410
_PS_SOLID = 0
_SRCCOPY = 0x00CC0020
_FW_BOLD = 700
_DEFAULT_CHARSET = 1
_CLEARTYPE_QUALITY = 5
_TRANSPARENT = 1
_DT_CENTER = 0x0001
_DT_LEFT = 0x0000
_DT_SINGLELINE = 0x0020
_DT_VCENTER = 0x0004
_IMAGE_ICON = 1
_LR_LOADFROMFILE = 0x0010
_DI_NORMAL = 0x0003
_POLL_S = 0.05
_CLASS_NAME = "HskStartupSplash"
_FILL_COLOR = 0x00282828
_BORDER_COLOR = 0x004A4A4A
_BUTTON_HOVER_COLOR = 0x00404040
_TEXT_COLOR = 0x00FFFFFF
_DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2 = -4
_PROCESS_PER_MONITOR_DPI_AWARE = 2
_MINIMIZE_GLYPH = "\u2212"
_EXPAND_GLYPH = "\u25a1"

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
    button_hover: bool = False
    class_info: Any = None
    hwnd: int = 0
    last_clock: str = ""
    last_rect: tuple[int, int, int, int] = (0, 0, 0, 0)
    logo_icon: int = 0
    logo_px: int = 0
    minimized: bool = False
    region_size: tuple[int, int] = (0, 0)
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
        _runtime.minimized = False
        _runtime.button_hover = False


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


def expand_early_splash() -> None:
    """Restore the centered splash from the toast form."""
    _set_minimized(minimized=False)


def format_splash_clock(seconds: int) -> str:
    """Format elapsed seconds as `MM:SS`, or `HH:MM:SS` after 60 minutes."""
    total = max(0, int(seconds))
    if total >= _SECONDS_PER_HOUR:
        hours, rem = divmod(total, _SECONDS_PER_HOUR)
        minutes, secs = divmod(rem, _SECONDS_PER_MINUTE)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    minutes, secs = divmod(total, _SECONDS_PER_MINUTE)
    return f"{minutes:02d}:{secs:02d}"


def is_early_splash_minimized() -> bool:
    """Return whether the splash is showing as a bottom-right toast."""
    with _lock:
        return bool(_runtime.hwnd) and _runtime.minimized


def minimize_early_splash() -> None:
    """Collapse the splash into a toast at the bottom-right of the work area."""
    _set_minimized(minimized=True)


def splash_logo_path() -> Path | None:
    """Return the ICO used on the splash, if the file exists."""
    path = Path(__file__).resolve().parent / "assets" / "app.ico"
    return path if path.is_file() else None


def splash_status_lines(seconds: int) -> tuple[str, str, str]:
    """Return the three splash lines: title, status, and clock."""
    return TRAY_LOADING_TITLE, _LOADING_LINE, format_splash_clock(seconds)


def _apply_round_region(hwnd: int, width: int, height: int) -> None:
    ellipse = _corner_ellipse(hwnd)
    region = _gdi32().CreateRoundRectRgn(0, 0, width + 1, height + 1, ellipse, ellipse)
    if not region:
        return
    _user32().SetWindowRgn(hwnd, region, True)  # noqa: FBT003
    _runtime.region_size = (width, height)


def _apply_window_geometry(user32: ctypes.WinDLL, hwnd: int) -> bool:
    x, y, width, height = _window_rect(hwnd)
    target = (x, y, width, height)
    current = _current_rect(hwnd)
    if current == target and _runtime.last_rect == target:
        return False
    size_changed = current[2:] != target[2:] or _runtime.last_rect[2:] != target[2:]
    if not user32.SetWindowPos(
        hwnd,
        wintypes.HWND(_HWND_TOPMOST),
        x,
        y,
        width,
        height,
        _SWP_NOACTIVATE,
    ):
        return False
    _runtime.last_rect = target
    if size_changed or _runtime.region_size != (width, height):
        _apply_round_region(hwnd, width, height)
    return True


def _button_rect(hwnd: int) -> wintypes.RECT:
    dpi = _dpi_for_hwnd(hwnd)
    size = _dip(_BUTTON_DIP, dpi)
    pad = _dip(8 if _runtime.minimized else 12, dpi)
    client = _client_rect(hwnd)
    width = int(client.right - client.left)
    return _rect(width - pad - size, pad, size, size)


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


def _corner_ellipse(hwnd: int) -> int:
    """Return the GDI ellipse size for rounded corners (twice the visual radius)."""
    return _dip(_RADIUS_DIP, _dpi_for_hwnd(hwnd)) * 2


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


def _draw_chrome_button(
    user32: ctypes.WinDLL,
    gdi32: ctypes.WinDLL,
    hdc: int,
    hwnd: int,
    font: int,
) -> None:
    box = _button_rect(hwnd)
    if _runtime.button_hover:
        fill = gdi32.CreateSolidBrush(_BUTTON_HOVER_COLOR)
        if fill:
            user32.FillRect(hdc, ctypes.byref(box), fill)
            gdi32.DeleteObject(fill)
    glyph = _EXPAND_GLYPH if _runtime.minimized else _MINIMIZE_GLYPH
    _draw_line(user32, gdi32, hdc, glyph, box, font, align=_DT_CENTER)


def _draw_line(
    user32: ctypes.WinDLL,
    gdi32: ctypes.WinDLL,
    hdc: int,
    text: str,
    box: wintypes.RECT,
    font: int,
    *,
    align: int = _DT_CENTER,
) -> None:
    previous = gdi32.SelectObject(hdc, font) if font else 0
    user32.DrawTextW(hdc, text, -1, ctypes.byref(box), align | _DT_SINGLELINE | _DT_VCENTER)
    if previous:
        gdi32.SelectObject(hdc, previous)


def _draw_logo(user32: ctypes.WinDLL, hdc: int, x: int, y: int, size: int) -> None:
    icon = _ensure_logo_icon(size)
    if not icon:
        return
    user32.DrawIconEx(hdc, x, y, icon, size, size, 0, None, _DI_NORMAL)


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


def _ensure_logo_icon(size: int) -> int:
    if _runtime.logo_icon and _runtime.logo_px == size:
        return _runtime.logo_icon
    path = splash_logo_path()
    if path is None:
        return 0
    if _runtime.logo_icon:
        with contextlib.suppress(OSError):
            _user32().DestroyIcon(_runtime.logo_icon)
        _runtime.logo_icon = 0
    user32 = _user32()
    icon = int(user32.LoadImageW(None, str(path), _IMAGE_ICON, size, size, _LR_LOADFROMFILE) or 0)
    _runtime.logo_icon = icon
    _runtime.logo_px = size if icon else 0
    return icon


def _gdi32() -> ctypes.WinDLL:
    return ctypes.WinDLL("gdi32", use_last_error=True)


def _hit_button(hwnd: int, x: int, y: int) -> bool:
    box = _button_rect(hwnd)
    return int(box.left) <= x < int(box.right) and int(box.top) <= y < int(box.bottom)


def _invalidate_if_clock_changed(user32: ctypes.WinDLL, hwnd: int) -> None:
    clock = format_splash_clock(int(time.monotonic() - _runtime.started_at))
    if clock == _runtime.last_clock:
        return
    user32.InvalidateRect(hwnd, None, False)  # noqa: FBT003


def _kernel32() -> ctypes.WinDLL:
    return ctypes.WinDLL("kernel32", use_last_error=True)


def _maybe_auto_minimize() -> None:
    if _runtime.minimized or not _runtime.hwnd:
        return
    if time.monotonic() - _runtime.started_at < AUTO_MINIMIZE_SECONDS:
        return
    _set_minimized(minimized=True)


def _mouse_point(lparam: int) -> tuple[int, int]:
    x = ctypes.c_short(lparam & 0xFFFF).value
    y = ctypes.c_short((lparam >> 16) & 0xFFFF).value
    return int(x), int(y)


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
        ellipse = _corner_ellipse(hwnd)
        gdi32.RoundRect(target, 0, 0, width, height, ellipse, ellipse)
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
        title, status, clock = splash_status_lines(int(time.monotonic() - _runtime.started_at))
        _runtime.last_clock = clock
        if _runtime.minimized:
            _paint_toast_content(user32, gdi32, target, hwnd, height, dpi, title, status, clock)
        else:
            _paint_full_content(user32, gdi32, target, hwnd, height, dpi, title, status, clock)
        if mem_dc and bitmap:
            gdi32.BitBlt(hdc, 0, 0, width, height, mem_dc, 0, 0, _SRCCOPY)
            gdi32.SelectObject(mem_dc, old_bitmap)
            gdi32.DeleteObject(bitmap)
            gdi32.DeleteObject(mem_dc)
    finally:
        user32.EndPaint(hwnd, ctypes.byref(paint))


def _paint_full_content(
    user32: ctypes.WinDLL,
    gdi32: ctypes.WinDLL,
    hdc: int,
    hwnd: int,
    height: int,
    dpi: int,
    title: str,
    status: str,
    clock: str,
) -> None:
    title_font = _create_font(gdi32, point_size=_TITLE_PT, dpi=dpi)
    body_font = _create_font(gdi32, point_size=_BODY_PT, dpi=dpi)
    button_font = _create_font(gdi32, point_size=_BODY_PT, dpi=dpi)
    pad = _dip(_PAD_DIP, dpi)
    logo_size = _dip(_LOGO_DIP, dpi)
    button = _button_rect(hwnd)
    has_logo = bool(_ensure_logo_icon(logo_size))
    text_x = pad
    text_w = max(1, int(button.left) - pad - _dip(8, dpi))
    align = _DT_CENTER
    if has_logo:
        logo_y = max(0, (height - logo_size) // 2)
        _draw_logo(user32, hdc, pad, logo_y, logo_size)
        text_x = pad + logo_size + _dip(_GAP_DIP, dpi)
        text_w = max(1, int(button.left) - text_x - _dip(8, dpi))
        align = _DT_LEFT
    band = max(1, height // 3)
    _draw_line(user32, gdi32, hdc, title, _rect(text_x, band // 8, text_w, band), title_font, align=align)
    _draw_line(user32, gdi32, hdc, status, _rect(text_x, band, text_w, band), body_font, align=align)
    _draw_line(
        user32,
        gdi32,
        hdc,
        clock,
        _rect(text_x, band * 2 - band // 8, text_w, band),
        body_font,
        align=align,
    )
    _draw_chrome_button(user32, gdi32, hdc, hwnd, button_font)
    if title_font:
        gdi32.DeleteObject(title_font)
    if body_font:
        gdi32.DeleteObject(body_font)
    if button_font:
        gdi32.DeleteObject(button_font)


def _paint_toast_content(
    user32: ctypes.WinDLL,
    gdi32: ctypes.WinDLL,
    hdc: int,
    hwnd: int,
    height: int,
    dpi: int,
    title: str,
    status: str,
    clock: str,
) -> None:
    title_font = _create_font(gdi32, point_size=_TOAST_TITLE_PT, dpi=dpi)
    body_font = _create_font(gdi32, point_size=_TOAST_BODY_PT, dpi=dpi)
    button_font = _create_font(gdi32, point_size=_TOAST_BODY_PT, dpi=dpi)
    pad = _dip(_TOAST_PAD_DIP, dpi)
    logo_size = _dip(_TOAST_LOGO_DIP, dpi)
    button = _button_rect(hwnd)
    has_logo = bool(_ensure_logo_icon(logo_size))
    text_x = pad
    if has_logo:
        logo_y = max(0, (height - logo_size) // 2)
        _draw_logo(user32, hdc, pad, logo_y, logo_size)
        text_x = pad + logo_size + _dip(12, dpi)
    text_w = max(1, int(button.left) - text_x - _dip(6, dpi))
    mid = height // 2
    _draw_line(user32, gdi32, hdc, title, _rect(text_x, 4, text_w, mid - 2), title_font, align=_DT_LEFT)
    _draw_line(
        user32,
        gdi32,
        hdc,
        f"{status}  {clock}",
        _rect(text_x, mid - 2, text_w, mid - 2),
        body_font,
        align=_DT_LEFT,
    )
    _draw_chrome_button(user32, gdi32, hdc, hwnd, button_font)
    if title_font:
        gdi32.DeleteObject(title_font)
    if body_font:
        gdi32.DeleteObject(body_font)
    if button_font:
        gdi32.DeleteObject(button_font)


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
        _runtime.minimized = False
        _runtime.button_hover = False
    _apply_window_geometry(user32, hwnd)
    user32.UpdateWindow(hwnd)
    user32.ShowWindow(hwnd, _SW_SHOWNOACTIVATE)
    msg = wintypes.MSG()
    while not _runtime.stop.is_set() and _pump_once(user32, msg):
        _maybe_auto_minimize()
        if _apply_window_geometry(user32, hwnd):
            user32.InvalidateRect(hwnd, None, False)  # noqa: FBT003
        _invalidate_if_clock_changed(user32, hwnd)
        time.sleep(_POLL_S)
    with contextlib.suppress(OSError):
        user32.DestroyWindow(hwnd)
    with _lock:
        if _runtime.hwnd == hwnd:
            _runtime.hwnd = 0
        _runtime.minimized = False
        _runtime.button_hover = False


def _set_button_hover(hwnd: int, *, hover: bool) -> None:
    if _runtime.button_hover == hover:
        return
    _runtime.button_hover = hover
    with contextlib.suppress(OSError):
        _user32().InvalidateRect(hwnd, ctypes.byref(_button_rect(hwnd)), False)  # noqa: FBT003


def _set_minimized(*, minimized: bool) -> None:
    with _lock:
        hwnd = _runtime.hwnd
        thread = _runtime.thread
        if not hwnd:
            return
        if _runtime.minimized == minimized:
            return
        if thread is not None and threading.current_thread() is not thread:
            with contextlib.suppress(OSError):
                _user32().PostMessageW(hwnd, _WM_SET_MINIMIZED, 1 if minimized else 0, 0)
            return
        _runtime.minimized = minimized
        _runtime.button_hover = False
        _runtime.last_rect = (0, 0, 0, 0)
    with contextlib.suppress(OSError):
        user32 = _user32()
        _apply_window_geometry(user32, hwnd)
        user32.InvalidateRect(hwnd, None, False)  # noqa: FBT003


def _start_thread() -> None:
    _runtime.stop = threading.Event()
    _runtime.started_at = time.monotonic()
    _runtime.minimized = False
    _runtime.button_hover = False
    _runtime.last_rect = (0, 0, 0, 0)
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


def _toast_rect(hwnd: int) -> tuple[int, int, int, int]:
    dpi = _dpi_for_hwnd(hwnd)
    width = _dip(_TOAST_WIDTH_DIP, dpi)
    height = _dip(_TOAST_HEIGHT_DIP, dpi)
    margin = _dip(_TOAST_MARGIN_DIP, dpi)
    left, top, right, bottom = _work_area()
    x = max(left + margin, right - width - margin)
    y = max(top + margin, bottom - height - margin)
    return x, y, width, height


def _user32() -> ctypes.WinDLL:
    lib = ctypes.WinDLL("user32", use_last_error=True)
    lib.DefWindowProcW.restype = _LRESULT
    lib.DefWindowProcW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
    lib.CreateWindowExW.restype = wintypes.HWND
    lib.GetCursorPos.argtypes = [ctypes.POINTER(wintypes.POINT)]
    lib.GetCursorPos.restype = wintypes.BOOL
    lib.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
    lib.GetWindowRect.restype = wintypes.BOOL
    lib.ScreenToClient.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.POINT)]
    lib.ScreenToClient.restype = wintypes.BOOL
    lib.SetCursor.argtypes = [wintypes.HANDLE]
    lib.SetCursor.restype = wintypes.HANDLE
    lib.SetWindowPos.argtypes = [
        wintypes.HWND,
        wintypes.HWND,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        wintypes.UINT,
    ]
    lib.SetWindowPos.restype = wintypes.BOOL
    lib.LoadImageW.restype = wintypes.HANDLE
    lib.LoadImageW.argtypes = [
        wintypes.HINSTANCE,
        wintypes.LPCWSTR,
        wintypes.UINT,
        ctypes.c_int,
        ctypes.c_int,
        wintypes.UINT,
    ]
    lib.DrawIconEx.argtypes = [
        wintypes.HDC,
        ctypes.c_int,
        ctypes.c_int,
        wintypes.HANDLE,
        ctypes.c_int,
        ctypes.c_int,
        wintypes.UINT,
        wintypes.HANDLE,
        wintypes.UINT,
    ]
    return lib


def _window_rect(hwnd: int) -> tuple[int, int, int, int]:
    if _runtime.minimized:
        return _toast_rect(hwnd)
    return _centered_rect(hwnd)


def _wndproc(hwnd: int, message: int, wparam: int, lparam: int) -> int:
    user32 = _user32()
    handle = int(hwnd)
    if message == _WM_ERASEBKGND:
        return 1
    if message == _WM_PAINT:
        _paint(handle)
        return 0
    if message == _WM_DPICHANGED:
        _apply_window_geometry(user32, handle)
        return 0
    if message == _WM_MOUSEMOVE:
        x, y = _mouse_point(int(lparam))
        _set_button_hover(handle, hover=_hit_button(handle, x, y))
        return 0
    if message == _WM_LBUTTONUP:
        x, y = _mouse_point(int(lparam))
        if _hit_button(handle, x, y):
            _set_minimized(minimized=not _runtime.minimized)
        return 0
    if message == _WM_SET_MINIMIZED:
        _set_minimized(minimized=bool(int(wparam)))
        return 0
    if message == _WM_SETCURSOR and (int(lparam) & 0xFFFF) == _HTCLIENT:
        point = wintypes.POINT()
        if user32.GetCursorPos(ctypes.byref(point)) and user32.ScreenToClient(handle, ctypes.byref(point)):
            cursor_id = _IDC_HAND if _hit_button(handle, int(point.x), int(point.y)) else _IDC_ARROW
            user32.SetCursor(user32.LoadCursorW(None, ctypes.c_void_p(cursor_id)))
            return 1
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
