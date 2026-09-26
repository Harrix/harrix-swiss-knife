"""Windows 11 caption row: icon, menu, tabs, and the window buttons.

The native title bar is removed. Dragging empty space in this row, resizing
from the edges, and double-click maximize stay with the system via `WM_NCHITTEST`
and `WM_NCCALCSIZE`.

"""

from __future__ import annotations

import ctypes
import logging
import sys
from ctypes import wintypes
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import QByteArray, QEvent, QObject, QPoint, QRect, QRectF, QSize, Qt
from PySide6.QtGui import QColor, QFont, QFontMetrics, QIcon, QPainter, QPalette, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QAbstractButton,
    QBoxLayout,
    QHBoxLayout,
    QMainWindow,
    QMenuBar,
    QSizePolicy,
    QTabBar,
    QTabWidget,
    QToolButton,
    QWidget,
)

from harrix_swiss_knife.apps.common.qt_main_window import resolve_window_menu_bar
from harrix_swiss_knife.installer.icon_assets import apply_window_icon, asset_candidates
from harrix_swiss_knife.qt_frameless_window import frameless_hit_test, native_local_point, read_native_windows_message
from harrix_swiss_knife.win11_backdrop import try_apply_system_backdrop

if TYPE_CHECKING:
    from collections.abc import Callable

    from PySide6.QtGui import QEnterEvent, QMouseEvent, QPaintEvent

logger = logging.getLogger(__name__)

CAPTION_BUTTON_WIDTH = 46
CAPTION_BUTTON_HEIGHT = 32
CAPTION_GLYPH_SIZE = 16
CAPTION_ICON_SIZE = 16

HTCLIENT = 1
HTCAPTION = 2
HTTOP = 12
HTRIGHT = 11

CLOSE_HOVER_COLOR = QColor("#C42B1C")
CLOSE_PRESSED_COLOR = QColor("#C83C32")
MINMAX_HOVER_LIGHT = QColor(0, 0, 0, 0x0D)
MINMAX_PRESSED_LIGHT = QColor(0, 0, 0, 0x1A)
MINMAX_HOVER_DARK = QColor(255, 255, 255, 0x0D)
MINMAX_PRESSED_DARK = QColor(255, 255, 255, 0x1A)
REST_GLYPH_LIGHT = QColor(0, 0, 0, 0xE4)
REST_GLYPH_DARK = QColor(255, 255, 255)
INACTIVE_GLYPH_LIGHT = QColor(0, 0, 0, 0x5C)
INACTIVE_GLYPH_DARK = QColor(255, 255, 255, 0x5C)
CLOSE_GLYPH_COLOR = QColor(255, 255, 255)

_GLYPH_FILES = {
    "dismiss": "dismiss_16_regular",
    "subtract": "subtract_16_regular",
    "maximize": "maximize_16_regular",
    "square_multiple": "square_multiple_16_regular",
}
_BUTTON_KINDS = {
    "minimize": ("subtract", "captionMinimizeButton", "Minimize"),
    "maximize": ("maximize", "captionMaximizeButton", "Maximize"),
    "close": ("dismiss", "captionCloseButton", "Close"),
}
_FONT_FLOOR_PT = 6.0
_FONT_FLOOR_PX = 8
_CAPTION_FONT_SLACK = 4
_CAPTION_MENU_HPAD = 8
_CAPTION_TAB_HPAD = 12
_SUITE_NAME = "Harrix Swiss Knife"
_LIGHTNESS_THRESHOLD = 128

_WM_NCCALCSIZE = 0x0083
_WM_NCHITTEST = 0x0084
_WM_SYSCOMMAND = 0x0112
_WM_NULL = 0x0000
_GWL_STYLE = -16
_WS_THICKFRAME = 0x00040000
_WS_SYSMENU = 0x00080000
_WS_MINIMIZEBOX = 0x00020000
_WS_MAXIMIZEBOX = 0x00010000
_WS_CAPTION = 0x00C00000
_STYLE_BITS = _WS_THICKFRAME | _WS_CAPTION | _WS_SYSMENU | _WS_MINIMIZEBOX | _WS_MAXIMIZEBOX
_SWP_NOSIZE = 0x0001
_SWP_NOMOVE = 0x0002
_SWP_NOZORDER = 0x0004
_SWP_NOACTIVATE = 0x0010
_SWP_FRAMECHANGED = 0x0020
_SWP_FLAGS = _SWP_NOSIZE | _SWP_NOMOVE | _SWP_NOZORDER | _SWP_NOACTIVATE | _SWP_FRAMECHANGED
_DWMWA_WINDOW_CORNER_PREFERENCE = 33
_DWMWCP_ROUND = 2
_POINTER_BYTES_64 = 8
_MONITOR_DEFAULTTONEAREST = 2
_TPM_RIGHTBUTTON = 0x0002
_TPM_RETURNCMD = 0x0100
_MF_BYCOMMAND = 0x0000
_MF_GRAYED = 0x0001
_MF_ENABLED = 0x0000
_SC_SIZE = 0xF000
_SC_MOVE = 0xF010
_SC_MINIMIZE = 0xF020
_SC_MAXIMIZE = 0xF030
_SC_CLOSE = 0xF060
_SC_RESTORE = 0xF120

_INSTALLED_ATTR = "_hsk_win11_caption"
_CONTROLLER_ATTR = "_hsk_win11_caption_controller"
_FRAME_GUARD_ATTR = "_hsk_win11_frame_applying"
_ICON_CACHE: dict[tuple[str, int, float], QIcon] = {}


class CaptionButton(QToolButton):
    """One Windows 11 caption button painted with a Fluent glyph."""

    def __init__(self, *, kind: str, light: bool, parent: QWidget | None = None) -> None:  # noqa: D107
        super().__init__(parent)
        glyph, object_name, tooltip = _BUTTON_KINDS[kind]
        self._kind = kind
        self._glyph = glyph
        self._light = light
        self._window_active = True
        self.setObjectName(object_name)
        self.setToolTip(tooltip)
        self.setAccessibleName(tooltip)
        self.setFixedSize(CAPTION_BUTTON_WIDTH, CAPTION_BUTTON_HEIGHT)
        self.setAutoRaise(True)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, on=True)
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

    def enterEvent(self, event: QEnterEvent) -> None:  # noqa: N802
        """Repaint so the Windows hover fill appears."""
        super().enterEvent(event)
        self.update()

    def glyph_name(self) -> str:
        """Return the Fluent glyph stem currently painted on this button."""
        return self._glyph

    def hover_background(self) -> QColor:
        """Return the Windows 11 hover fill for this button."""
        if self._kind == "close":
            return CLOSE_HOVER_COLOR
        if self._light:
            return MINMAX_HOVER_LIGHT
        return MINMAX_HOVER_DARK

    def leaveEvent(self, event: QEvent) -> None:  # noqa: N802
        """Repaint after the pointer leaves the button."""
        super().leaveEvent(event)
        self.update()

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Repaint the pressed fill, then let the button emit `clicked`."""
        super().mousePressEvent(event)
        self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Repaint once the pressed fill should clear."""
        super().mouseReleaseEvent(event)
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802, ARG002
        """Fill the button and draw a 16 px glyph centered in it."""
        painter = QPainter(self)
        if self.isDown():
            fill = self.pressed_background()
        elif self.underMouse():
            fill = self.hover_background()
        else:
            fill = self._rest_background()
        painter.fillRect(self.rect(), fill)
        icon = caption_glyph_icon(self._glyph, self._glyph_color(), self.devicePixelRatioF())
        if icon.isNull():
            painter.end()
            return
        side = CAPTION_GLYPH_SIZE
        x = (self.width() - side) // 2
        y = (self.height() - side) // 2
        icon.paint(painter, QRect(x, y, side, side))
        painter.end()

    def pressed_background(self) -> QColor:
        """Return the Windows 11 pressed fill for this button."""
        if self._kind == "close":
            return CLOSE_PRESSED_COLOR
        if self._light:
            return MINMAX_PRESSED_LIGHT
        return MINMAX_PRESSED_DARK

    def set_glyph(self, name: str) -> None:
        """Switch the centered Fluent glyph.

        Args:

        - `name` (`str`): Stem such as `maximize` or `square_multiple`.

        """
        if self._glyph == name:
            return
        self._glyph = name
        if name == "square_multiple":
            self.setToolTip("Restore")
            self.setAccessibleName("Restore")
        elif name == "maximize":
            self.setToolTip("Maximize")
            self.setAccessibleName("Maximize")
        self.update()

    def set_light(self, *, light: bool) -> None:
        """Use light or dark caption colors.

        Args:

        - `light` (`bool`): `True` when the window background is light.

        """
        if self._light == light:
            return
        self._light = light
        self.update()

    def set_window_active(self, *, active: bool) -> None:
        """Dim the glyph while the window is inactive.

        Args:

        - `active` (`bool`): Whether the top-level window is active.

        """
        if self._window_active == active:
            return
        self._window_active = active
        self.update()

    def _glyph_color(self) -> QColor:
        if self._kind == "close" and (self.underMouse() or self.isDown()):
            return CLOSE_GLYPH_COLOR
        if not self._window_active:
            return INACTIVE_GLYPH_LIGHT if self._light else INACTIVE_GLYPH_DARK
        return REST_GLYPH_LIGHT if self._light else REST_GLYPH_DARK

    def _rest_background(self) -> QColor:
        parent = self.parentWidget()
        source = parent if parent is not None else self
        return source.palette().color(QPalette.ColorRole.Window)


class _CaptionIconButton(QToolButton):
    """App icon at the left of the caption. Click opens the system menu."""

    def __init__(self, on_menu: Callable[[], None], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._on_menu = on_menu
        self.setObjectName("captionIconButton")
        self.setFixedSize(CAPTION_BUTTON_HEIGHT, CAPTION_BUTTON_HEIGHT)
        self.setIconSize(QSize(CAPTION_ICON_SIZE, CAPTION_ICON_SIZE))
        self.setAutoRaise(True)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setAutoFillBackground(False)
        self.setStyleSheet("QToolButton { background: transparent; border: none; }")
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Open the system menu on left or right click, like the Windows icon."""
        if event.button() in {Qt.MouseButton.LeftButton, Qt.MouseButton.RightButton}:
            self._on_menu()
            event.accept()
            return
        super().mousePressEvent(event)


class _MARGINS(ctypes.Structure):
    """Win32 `MARGINS` for `DwmExtendFrameIntoClientArea`."""

    _fields_ = (
        ("cxLeftWidth", ctypes.c_int),
        ("cxRightWidth", ctypes.c_int),
        ("cyTopHeight", ctypes.c_int),
        ("cyBottomHeight", ctypes.c_int),
    )


class _MONITORINFO(ctypes.Structure):
    """Win32 `MONITORINFO`."""

    _fields_ = (
        ("cbSize", wintypes.DWORD),
        ("rcMonitor", wintypes.RECT),
        ("rcWork", wintypes.RECT),
        ("dwFlags", wintypes.DWORD),
    )


class _Win11CaptionController(QObject):
    """Keeps caption glyphs, colors, and the Win32 frame in sync with the window."""

    def __init__(self, window: QWidget) -> None:
        super().__init__(window)
        self._window = window

    def close_window(self) -> None:
        """Close the caption's window."""
        self._window.close()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Apply the frame on show and refresh caption chrome when state changes."""
        window = getattr(self, "_window", None)
        if not isinstance(window, QWidget) or watched is not window:
            return False
        event_type = event.type()
        if event_type in {QEvent.Type.Show, QEvent.Type.WinIdChange}:
            _apply_win32_frame(window, full=True)
            _sync_caption_icon(window)
            _sync_zoom_glyph(window)
            _sync_caption_active(window)
        elif event_type == QEvent.Type.WindowStateChange:
            _apply_win32_frame(window, full=False)
            _sync_zoom_glyph(window)
        elif event_type in {QEvent.Type.WindowActivate, QEvent.Type.WindowDeactivate}:
            _sync_caption_active(window)
        elif event_type == QEvent.Type.PaletteChange:
            _sync_caption_palette(window)
        elif event_type == QEvent.Type.FontChange:
            _fit_caption_fonts(window)
            _style_caption_chrome(window)
        elif event_type == QEvent.Type.WindowIconChange:
            _sync_caption_icon(window)
        elif event_type == QEvent.Type.WindowTitleChange:
            _sync_caption_icon_tooltip(window)
        return False

    def minimize(self) -> None:
        """Minimize the caption's window."""
        self._window.showMinimized()

    def show_system_menu(self) -> None:
        """Pop the Win32 system menu under the pointer."""
        _popup_system_menu(self._window)

    def toggle_zoom(self) -> None:
        """Maximize or restore the caption's window."""
        window = self._window
        if window.isMaximized():
            window.showNormal()
        else:
            window.showMaximized()


def caption_glyph_icon(name: str, color: QColor, dpr: float) -> QIcon:
    """Paint one Fluent caption glyph.

    Args:

    - `name` (`str`): Glyph stem (`dismiss`, `subtract`, `maximize`, `square_multiple`).
    - `color` (`QColor`): Fill color, including alpha.
    - `dpr` (`float`): Device pixel ratio of the button.

    Returns:

    - `QIcon`: A 16 px icon, or a null icon when the SVG is missing.

    """
    ratio = dpr if dpr > 0 else 1.0
    key = (name, color.rgba(), round(ratio, 2))
    cached = _ICON_CACHE.get(key)
    if cached is not None:
        return cached
    svg_bytes = _svg_bytes(name, color)
    if svg_bytes is None:
        return QIcon()
    icon = _icon_from_svg(svg_bytes, ratio, label=name)
    if not icon.isNull():
        _ICON_CACHE[key] = icon
    return icon


def caption_hit_test(
    local: QPoint,
    size: QSize,
    *,
    caption: QRect,
    interactive: list[QRect],
    maximized: bool,
) -> int:
    """Return the Win32 hit code for a point on a custom-caption window.

    Edges resize, except over a caption control. Empty caption space drags the
    window. A maximized window does not resize from its edges.

    Args:

    - `local` (`QPoint`): Point in the window's logical coordinates.
    - `size` (`QSize`): Window size in logical pixels.
    - `caption` (`QRect`): The icon/menu/tab/button row.
    - `interactive` (`list[QRect]`): Buttons, menu items, and tabs that must stay clickable.
    - `maximized` (`bool`): Whether the window is maximized or full screen.

    Returns:

    - `int`: `HTCLIENT`, `HTCAPTION`, or an edge code.

    """
    on_control = any(rect.contains(local) for rect in interactive)
    if not maximized:
        edge = frameless_hit_test(local, size)
        if edge != HTCLIENT:
            if on_control:
                return HTCLIENT
            return edge
    if caption.isValid() and not caption.isEmpty() and caption.contains(local) and not on_control:
        return HTCAPTION
    return HTCLIENT


def install_win11_caption(window: QWidget) -> bool:
    """Replace the native title bar with the tab row plus Windows 11 buttons.

    No-op outside Windows. The window title string is left in place for the taskbar.

    Args:

    - `window` (`QWidget`): Main window that already has `tabWidget`.

    Returns:

    - `bool`: `True` when the caption row was installed.

    """
    if sys.platform != "win32" or getattr(window, _INSTALLED_ATTR, False):
        return False
    tab_widget = getattr(window, "tabWidget", None)
    if not isinstance(tab_widget, QTabWidget):
        logger.warning("Win11 caption needs a tabWidget")
        return False

    light = _palette_is_light(window)
    controller = _Win11CaptionController(window)
    setattr(window, _CONTROLLER_ATTR, controller)
    _build_caption_row(window, tab_widget, controller, light=light)
    _flush_caption_to_frame(window)
    _fit_caption_fonts(window)
    _sync_caption_palette(window)
    window.installEventFilter(controller)
    setattr(window, _INSTALLED_ATTR, True)
    _set_frameless_window_flags(window)
    _collapse_native_menu_bar(window)
    _sync_caption_icon(window)
    _sync_zoom_glyph(window)
    return True


def try_handle_win11_caption_native_event(
    window: QWidget,
    event_type: bytes | bytearray | memoryview | QByteArray | str,
    message: Any,
) -> tuple[bool, int] | None:
    """Handle caption drag, edge resize, and the borderless client area.

    Args:

    - `window` (`QWidget`): Window that installed the caption.
    - `event_type`: Qt native-event type tag.
    - `message` (`Any`): Platform message pointer.

    Returns:

    - `tuple[bool, int] | None`: Qt `nativeEvent` result, or `None` to keep the default.

    """
    if sys.platform != "win32" or not getattr(window, _INSTALLED_ATTR, False):
        return None
    msg = read_native_windows_message(event_type, message)
    if msg is None:
        return None
    if msg.message == _WM_NCCALCSIZE and msg.wParam:
        _apply_maximized_nccalcsize(window, int(msg.lParam))
        return True, 0
    if msg.message != _WM_NCHITTEST:
        return None
    global_x = ctypes.c_short(msg.lParam & 0xFFFF).value
    global_y = ctypes.c_short((msg.lParam >> 16) & 0xFFFF).value
    local = native_local_point(window, global_x, global_y)
    if local is None:
        return None
    return True, _live_caption_hit_test(window, local)


def write_nccalcsize_client_rect(address: int, left: int, top: int, right: int, bottom: int) -> None:
    """Overwrite `NCCALCSIZE_PARAMS.rgrc[0]` at `address`.

    Args:

    - `address` (`int`): Address of an `NCCALCSIZE_PARAMS` block.
    - `left` / `top` / `right` / `bottom` (`int`): Client rectangle in native pixels.

    """
    rect = wintypes.RECT(left, top, right, bottom)
    ctypes.memmove(address, ctypes.byref(rect), ctypes.sizeof(rect))


def _apply_maximized_nccalcsize(window: QWidget, lparam: int) -> None:
    hwnd = int(window.winId())
    if hwnd == 0 or not bool(_user32().IsZoomed(hwnd)):
        return
    work = _monitor_work_area(hwnd)
    if work is None:
        return
    write_nccalcsize_client_rect(_pointer_address(lparam), *work)


def _apply_win32_frame(window: QWidget, *, full: bool) -> None:
    if sys.platform != "win32" or getattr(window, _FRAME_GUARD_ATTR, False):
        return
    setattr(window, _FRAME_GUARD_ATTR, True)
    try:
        hwnd = int(window.winId())
        if hwnd == 0:
            return
        _ensure_win32_style(hwnd)
        if not full:
            return
        _extend_frame_for_shadow(hwnd)
        _round_window_corners(hwnd)
        try_apply_system_backdrop(window)
        apply_window_icon(window)
    except Exception:
        logger.exception("Could not apply the Win11 caption frame")
    finally:
        setattr(window, _FRAME_GUARD_ATTR, False)


def _build_caption_row(
    window: QWidget,
    tab_widget: QTabWidget,
    controller: _Win11CaptionController,
    *,
    light: bool,
) -> None:
    tab_bar = tab_widget.tabBar()
    tab_bar.setExpanding(False)
    tab_bar.setFixedHeight(CAPTION_BUTTON_HEIGHT)
    tab_widget.setDocumentMode(True)
    # Document mode turns the tab-bar base back on. That base is the gray outline.
    tab_bar.setDrawBase(False)

    icon_button = _CaptionIconButton(controller.show_system_menu)
    icon_button.setIcon(window.windowIcon())
    icon_button.setToolTip(_caption_icon_tooltip(window))
    _insert_icon_button(tab_widget, icon_button)

    row = QWidget(tab_widget)
    row.setObjectName("captionButtonRow")
    row.setFixedHeight(CAPTION_BUTTON_HEIGHT)
    layout = QHBoxLayout(row)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)
    buttons = (
        ("minimize", controller.minimize),
        ("maximize", controller.toggle_zoom),
        ("close", controller.close_window),
    )
    for kind, slot in buttons:
        button = CaptionButton(kind=kind, light=light, parent=row)
        button.clicked.connect(slot)
        layout.addWidget(button)
    tab_widget.setCornerWidget(row, Qt.Corner.TopRightCorner)


def _caption_control_at(window: QWidget, local: QPoint) -> bool:
    child = window.childAt(local)
    while child is not None and child is not window:
        if isinstance(child, QAbstractButton):
            return True
        if isinstance(child, QTabBar):
            return child.tabAt(child.mapFrom(window, local)) >= 0
        if isinstance(child, QMenuBar):
            return child.actionAt(child.mapFrom(window, local)) is not None
        child = child.parentWidget()
    return False


def _caption_icon_tooltip(window: QWidget) -> str:
    title = window.windowTitle().strip()
    if not title or title == _SUITE_NAME:
        return _SUITE_NAME
    suffix = f"- {_SUITE_NAME}"
    if title.endswith(suffix):
        return title
    return f"{title} - {_SUITE_NAME}"


def _caption_label_padding(widget: QWidget) -> int:
    text_height = QFontMetrics(widget.font()).height()
    return max(0, (CAPTION_BUTTON_HEIGHT - text_height) // 2)


def _caption_strip_rect(window: QWidget) -> QRect:
    tab_widget = getattr(window, "tabWidget", None)
    if not isinstance(tab_widget, QTabWidget):
        return QRect()
    bar = tab_widget.tabBar()
    top_left = bar.mapTo(window, QPoint(0, 0))
    height = max(bar.height(), CAPTION_BUTTON_HEIGHT)
    return QRect(0, top_left.y(), window.width(), height)


def _collapse_native_menu_bar(window: QWidget) -> None:
    raw = getattr(window, "menuBar", None)
    bar = raw if isinstance(raw, QMenuBar) else raw() if callable(raw) else None
    if not isinstance(bar, QMenuBar):
        return
    tab_widget = getattr(window, "tabWidget", None)
    if isinstance(tab_widget, QTabWidget):
        corner = tab_widget.cornerWidget(Qt.Corner.TopLeftCorner)
        if corner is not None and (bar is corner or corner.isAncestorOf(bar)):
            return
    bar.hide()
    bar.setFixedHeight(0)


def _dwmapi() -> ctypes.WinDLL:
    library = getattr(_dwmapi, "library", None)
    if isinstance(library, ctypes.WinDLL):
        return library
    library = ctypes.WinDLL("dwmapi", use_last_error=True)
    library.DwmExtendFrameIntoClientArea.argtypes = [wintypes.HWND, ctypes.POINTER(_MARGINS)]
    library.DwmExtendFrameIntoClientArea.restype = ctypes.c_long
    library.DwmSetWindowAttribute.argtypes = [wintypes.HWND, wintypes.DWORD, wintypes.LPCVOID, wintypes.DWORD]
    library.DwmSetWindowAttribute.restype = ctypes.c_long
    _dwmapi.library = library  # type: ignore[attr-defined]
    return library


def _ensure_win32_style(hwnd: int) -> None:
    user32 = _user32()
    get_style = user32.GetWindowLongPtrW if _is_64_bit() else user32.GetWindowLongW
    set_style = user32.SetWindowLongPtrW if _is_64_bit() else user32.SetWindowLongW
    style = int(get_style(hwnd, _GWL_STYLE))
    wanted = style | _STYLE_BITS
    if style == wanted:
        return
    set_style(hwnd, _GWL_STYLE, wanted)
    user32.SetWindowPos(hwnd, 0, 0, 0, 0, 0, _SWP_FLAGS)


def _extend_frame_for_shadow(hwnd: int) -> None:
    margins = _MARGINS(0, 0, 0, 1)
    _dwmapi().DwmExtendFrameIntoClientArea(hwnd, ctypes.byref(margins))


def _fill_widget(widget: QWidget, color: QColor) -> None:
    palette = widget.palette()
    palette.setColor(QPalette.ColorRole.Window, color)
    widget.setPalette(palette)
    widget.setAutoFillBackground(True)


def _fit_caption_fonts(window: QWidget) -> None:
    tab_widget = getattr(window, "tabWidget", None)
    if isinstance(tab_widget, QTabWidget):
        _fit_widget_font(tab_widget.tabBar(), CAPTION_BUTTON_HEIGHT - _CAPTION_FONT_SLACK)
    menu = resolve_window_menu_bar(window)
    if menu is not None:
        menu.setFixedHeight(CAPTION_BUTTON_HEIGHT)
        _fit_widget_font(menu, CAPTION_BUTTON_HEIGHT - _CAPTION_FONT_SLACK)


def _fit_widget_font(widget: QWidget, max_height: int) -> None:
    fitted = _shrunk_font(widget.font(), max_height)
    current = widget.font()
    if fitted.pointSizeF() == current.pointSizeF() and fitted.pixelSize() == current.pixelSize():
        return
    widget.setFont(fitted)


def _flush_caption_to_frame(window: QWidget) -> None:
    if not isinstance(window, QMainWindow):
        return
    central = _resolve_central_widget(window)
    tab_widget = getattr(window, "tabWidget", None)
    if central is None or central is tab_widget:
        return
    layout = central.layout()
    if layout is not None:
        layout.setContentsMargins(0, 0, 0, 0)


def _icon_from_svg(svg_bytes: bytes, ratio: float, *, label: str) -> QIcon:
    physical = max(1, round(CAPTION_GLYPH_SIZE * ratio))
    renderer = QSvgRenderer(QByteArray(svg_bytes))
    if not renderer.isValid():
        logger.warning("SVG for `%s` is invalid", label)
        return QIcon()
    pixmap = QPixmap(physical, physical)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, on=True)
    renderer.render(painter, QRectF(0.0, 0.0, float(physical), float(physical)))
    painter.end()
    pixmap.setDevicePixelRatio(ratio)
    icon = QIcon()
    icon.addPixmap(pixmap)
    return icon


def _insert_icon_button(tab_widget: QTabWidget, icon_button: QToolButton) -> None:
    corner = tab_widget.cornerWidget(Qt.Corner.TopLeftCorner)
    if corner is None:
        corner = QWidget(tab_widget)
        layout = QHBoxLayout(corner)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(icon_button)
        tab_widget.setCornerWidget(corner, Qt.Corner.TopLeftCorner)
    else:
        layout = corner.layout()
        if isinstance(layout, QBoxLayout):
            margins = layout.contentsMargins()
            layout.setContentsMargins(0, 0, margins.right(), 0)
            layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
            layout.insertWidget(0, icon_button)
        else:
            icon_button.setParent(corner)
    corner.setFixedHeight(CAPTION_BUTTON_HEIGHT)


def _is_64_bit() -> bool:
    return ctypes.sizeof(ctypes.c_void_p) == _POINTER_BYTES_64


def _live_caption_hit_test(window: QWidget, local: QPoint) -> int:
    caption = _caption_strip_rect(window)
    maximized = _window_is_zoomed(window)
    on_border = not maximized and frameless_hit_test(local, window.size()) != HTCLIENT
    in_caption = caption.contains(local)
    if not on_border and not in_caption:
        return HTCLIENT
    interactive: list[QRect] = []
    if _caption_control_at(window, local):
        interactive.append(QRect(local.x(), local.y(), 1, 1))
    return caption_hit_test(local, window.size(), caption=caption, interactive=interactive, maximized=maximized)


def _monitor_work_area(hwnd: int) -> tuple[int, int, int, int] | None:
    user32 = _user32()
    monitor = user32.MonitorFromWindow(hwnd, _MONITOR_DEFAULTTONEAREST)
    if not monitor:
        return None
    info = _MONITORINFO()
    info.cbSize = ctypes.sizeof(_MONITORINFO)
    if not user32.GetMonitorInfoW(monitor, ctypes.byref(info)):
        return None
    rect = info.rcWork
    return (int(rect.left), int(rect.top), int(rect.right), int(rect.bottom))


def _palette_is_light(window: QWidget) -> bool:
    return window.palette().color(QPalette.ColorRole.Window).lightness() >= _LIGHTNESS_THRESHOLD


def _pointer_address(value: int) -> int:
    bits = 8 * ctypes.sizeof(ctypes.c_void_p)
    return value & ((1 << bits) - 1)


def _popup_system_menu(window: QWidget) -> None:
    if sys.platform != "win32":
        return
    try:
        hwnd = int(window.winId())
        if hwnd == 0:
            return
        user32 = _user32()
        menu = user32.GetSystemMenu(hwnd, False)  # noqa: FBT003
        if not menu:
            return
        zoomed = bool(user32.IsZoomed(hwnd))
        _set_menu_item(user32, menu, _SC_RESTORE, enabled=zoomed)
        _set_menu_item(user32, menu, _SC_MOVE, enabled=not zoomed)
        _set_menu_item(user32, menu, _SC_SIZE, enabled=not zoomed)
        _set_menu_item(user32, menu, _SC_MINIMIZE, enabled=True)
        _set_menu_item(user32, menu, _SC_MAXIMIZE, enabled=not zoomed)
        _set_menu_item(user32, menu, _SC_CLOSE, enabled=True)
        point = wintypes.POINT()
        user32.GetCursorPos(ctypes.byref(point))
        user32.SetForegroundWindow(hwnd)
        command = int(
            user32.TrackPopupMenu(
                menu,
                _TPM_RIGHTBUTTON | _TPM_RETURNCMD,
                int(point.x),
                int(point.y),
                0,
                hwnd,
                None,
            ),
        )
        user32.PostMessageW(hwnd, _WM_NULL, 0, 0)
        if command:
            user32.PostMessageW(hwnd, _WM_SYSCOMMAND, command, 0)
    except Exception:
        logger.exception("Could not open the window system menu")


def _resolve_central_widget(window: QWidget) -> QWidget | None:
    """Return the central widget, including a UI attribute that shadows the method.

    Generated `window.py` files assign `self.centralWidget` to a `QWidget`, which
    hides `QMainWindow.centralWidget()`.

    """
    raw = getattr(window, "centralWidget", None)
    if isinstance(raw, QWidget):
        return raw
    if callable(raw):
        resolved = raw()
        if isinstance(resolved, QWidget):
            return resolved
    return None


def _round_window_corners(hwnd: int) -> None:
    preference = ctypes.c_int(_DWMWCP_ROUND)
    _dwmapi().DwmSetWindowAttribute(
        hwnd,
        _DWMWA_WINDOW_CORNER_PREFERENCE,
        ctypes.byref(preference),
        ctypes.sizeof(preference),
    )


def _set_frameless_window_flags(window: QWidget) -> None:
    window.setWindowFlag(Qt.WindowType.FramelessWindowHint, on=True)
    window.setWindowFlag(Qt.WindowType.WindowSystemMenuHint, on=True)
    window.setWindowFlag(Qt.WindowType.WindowMinimizeButtonHint, on=True)
    window.setWindowFlag(Qt.WindowType.WindowMaximizeButtonHint, on=True)
    window.setWindowFlag(Qt.WindowType.WindowCloseButtonHint, on=True)


def _set_menu_item(user32: Any, menu: int, command: int, *, enabled: bool) -> None:
    flags = _MF_BYCOMMAND | (_MF_ENABLED if enabled else _MF_GRAYED)
    user32.EnableMenuItem(menu, command, flags)


def _shade_caption_color(color: QColor, *, light: bool, amount: float) -> QColor:
    toward = 0 if light else 255
    return QColor(
        round(color.red() + (toward - color.red()) * amount),
        round(color.green() + (toward - color.green()) * amount),
        round(color.blue() + (toward - color.blue()) * amount),
    )


def _shrunk_font(font: QFont, max_height: int) -> QFont:
    fitted = QFont(font)
    if fitted.pointSizeF() > 0:
        while QFontMetrics(fitted).height() > max_height and fitted.pointSizeF() > _FONT_FLOOR_PT:
            fitted.setPointSizeF(fitted.pointSizeF() - 0.5)
        return fitted
    if fitted.pixelSize() > 0:
        while QFontMetrics(fitted).height() > max_height and fitted.pixelSize() > _FONT_FLOOR_PX:
            fitted.setPixelSize(fitted.pixelSize() - 1)
    return fitted


def _style_caption_chrome(window: QWidget) -> None:
    color = window.palette().color(QPalette.ColorRole.Window)
    rgb = color.name(QColor.NameFormat.HexRgb)
    light = _palette_is_light(window)
    hover = _shade_caption_color(color, light=light, amount=0.06).name(QColor.NameFormat.HexRgb)
    selected = _shade_caption_color(color, light=light, amount=0.08).name(QColor.NameFormat.HexRgb)
    tab_widget = getattr(window, "tabWidget", None)
    if isinstance(tab_widget, QTabWidget):
        tab_widget.setStyleSheet("QTabWidget::pane { border: none; margin: 0px; }")
        tab_bar = tab_widget.tabBar()
        tab_bar.setDrawBase(False)
        pad = _caption_label_padding(tab_bar)
        tab_bar.setStyleSheet(
            f"""
            QTabBar {{
                background: {rgb};
                border: none;
            }}
            QTabBar::tab {{
                background: {rgb};
                color: palette(window-text);
                border: none;
                margin: 0px;
                padding: {pad}px {_CAPTION_TAB_HPAD}px;
            }}
            QTabBar::tab:selected {{
                background: {selected};
            }}
            QTabBar::tab:hover:!selected {{
                background: {hover};
            }}
            """
        )
    menu = resolve_window_menu_bar(window)
    if menu is None:
        return
    pad = _caption_label_padding(menu)
    menu.setStyleSheet(
        f"""
        QMenuBar {{
            background: {rgb};
            spacing: 0px;
            padding: 0px;
            font-weight: 700;
        }}
        QMenuBar::item {{
            background: transparent;
            padding: {pad}px {_CAPTION_MENU_HPAD}px;
            margin: 0px;
        }}
        QMenuBar::item:selected {{
            background: {hover};
        }}
        """
    )


def _svg_bytes(name: str, color: QColor) -> bytes | None:
    stem = _GLYPH_FILES.get(name)
    if stem is None:
        logger.warning("Unknown caption glyph `%s`", name)
        return None
    path = next((candidate for candidate in asset_candidates("caption", f"{stem}.svg") if candidate.is_file()), None)
    if path is None:
        logger.warning("Missing caption glyph `%s`", stem)
        return None
    rgb = color.name(QColor.NameFormat.HexRgb)
    opacity = f"{color.alphaF():.4f}"
    text = path.read_text(encoding="utf-8").replace('fill="#212121"', f'fill="{rgb}" fill-opacity="{opacity}"')
    return text.encode("utf-8")


def _sync_caption_active(window: QWidget) -> None:
    active = window.isActiveWindow()
    for button in window.findChildren(CaptionButton):
        button.set_window_active(active=active)


def _sync_caption_icon(window: QWidget) -> None:
    button = window.findChild(QToolButton, "captionIconButton")
    if isinstance(button, QToolButton):
        button.setIcon(window.windowIcon())
        button.setIconSize(QSize(CAPTION_ICON_SIZE, CAPTION_ICON_SIZE))
        button.setToolTip(_caption_icon_tooltip(window))


def _sync_caption_icon_tooltip(window: QWidget) -> None:
    button = window.findChild(QToolButton, "captionIconButton")
    if isinstance(button, QToolButton):
        button.setToolTip(_caption_icon_tooltip(window))


def _sync_caption_palette(window: QWidget) -> None:
    light = _palette_is_light(window)
    color = window.palette().color(QPalette.ColorRole.Window)
    for button in window.findChildren(CaptionButton):
        button.set_light(light=light)
    tab_widget = getattr(window, "tabWidget", None)
    if not isinstance(tab_widget, QTabWidget):
        return
    _fill_widget(tab_widget.tabBar(), color)
    for corner in (Qt.Corner.TopLeftCorner, Qt.Corner.TopRightCorner):
        widget = tab_widget.cornerWidget(corner)
        if widget is not None:
            _fill_widget(widget, color)
    menu = resolve_window_menu_bar(window)
    if menu is not None:
        _fill_widget(menu, color)
    _style_caption_chrome(window)


def _sync_zoom_glyph(window: QWidget) -> None:
    button = window.findChild(CaptionButton, "captionMaximizeButton")
    if isinstance(button, CaptionButton):
        button.set_glyph("square_multiple" if _window_is_zoomed(window) else "maximize")


def _user32() -> ctypes.WinDLL:
    library = getattr(_user32, "library", None)
    if isinstance(library, ctypes.WinDLL):
        return library
    library = ctypes.WinDLL("user32", use_last_error=True)
    long_type = ctypes.c_ssize_t if _is_64_bit() else ctypes.c_long
    for name in ("GetWindowLongPtrW", "GetWindowLongW", "SetWindowLongPtrW", "SetWindowLongW"):
        if hasattr(library, name):
            function = getattr(library, name)
            if name.startswith("Get"):
                function.argtypes = [wintypes.HWND, ctypes.c_int]
                function.restype = long_type
            else:
                function.argtypes = [wintypes.HWND, ctypes.c_int, long_type]
                function.restype = long_type
    library.SetWindowPos.argtypes = [
        wintypes.HWND,
        wintypes.HWND,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        wintypes.UINT,
    ]
    library.SetWindowPos.restype = wintypes.BOOL
    library.IsZoomed.argtypes = [wintypes.HWND]
    library.IsZoomed.restype = wintypes.BOOL
    library.MonitorFromWindow.argtypes = [wintypes.HWND, wintypes.DWORD]
    library.MonitorFromWindow.restype = ctypes.c_void_p
    library.GetMonitorInfoW.argtypes = [ctypes.c_void_p, ctypes.POINTER(_MONITORINFO)]
    library.GetMonitorInfoW.restype = wintypes.BOOL
    library.GetSystemMenu.argtypes = [wintypes.HWND, wintypes.BOOL]
    library.GetSystemMenu.restype = ctypes.c_void_p
    library.EnableMenuItem.argtypes = [ctypes.c_void_p, wintypes.UINT, wintypes.UINT]
    library.EnableMenuItem.restype = wintypes.BOOL
    library.GetCursorPos.argtypes = [ctypes.POINTER(wintypes.POINT)]
    library.GetCursorPos.restype = wintypes.BOOL
    library.SetForegroundWindow.argtypes = [wintypes.HWND]
    library.SetForegroundWindow.restype = wintypes.BOOL
    library.TrackPopupMenu.argtypes = [
        ctypes.c_void_p,
        wintypes.UINT,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        wintypes.HWND,
        ctypes.c_void_p,
    ]
    library.TrackPopupMenu.restype = wintypes.UINT
    library.PostMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
    library.PostMessageW.restype = wintypes.BOOL
    _user32.library = library  # type: ignore[attr-defined]
    return library


def _window_is_zoomed(window: QWidget) -> bool:
    state = window.windowState()
    return bool(state & (Qt.WindowState.WindowMaximized | Qt.WindowState.WindowFullScreen))
