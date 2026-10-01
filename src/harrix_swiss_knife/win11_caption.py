"""Windows 11 caption row: icon, title, tabs, menu, and the window buttons.

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

from PySide6.QtCore import QByteArray, QEvent, QObject, QPoint, QRect, QRectF, QSize, Qt, QTimer
from PySide6.QtGui import QColor, QCursor, QFont, QFontMetrics, QIcon, QPainter, QPaintEvent, QPalette, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QAbstractButton,
    QAbstractSpinBox,
    QBoxLayout,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMenuBar,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QStackedWidget,
    QTabBar,
    QTabWidget,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife.apps.common.qt_main_window import resolve_window_menu_bar
from harrix_swiss_knife.installer.icon_assets import apply_window_icon, asset_candidates
from harrix_swiss_knife.qt_flat_scrollbar import apply_flat_scrollbars_to_styled_item_views
from harrix_swiss_knife.qt_frameless_window import frameless_hit_test, native_local_point, read_native_windows_message
from harrix_swiss_knife.qt_lucide_icon import apply_lucide_button_icon
from harrix_swiss_knife.win11_backdrop import try_apply_system_backdrop

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

    from PySide6.QtGui import QEnterEvent, QMouseEvent

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
_WINDOW_BACKGROUND = QColor(255, 255, 255)
_WHITE_SURFACE_MARK = "hsk-white-surfaces"
_SPLITTER_HANDLE_PX = 17
_SPLITTER_HANDLE_STYLE = f"""
QSplitter::handle:horizontal {{
    width: {_SPLITTER_HANDLE_PX}px;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #ffffff, stop:0.46 #ffffff, stop:0.49 #c0c0c0, stop:0.51 #c0c0c0,
        stop:0.54 #ffffff, stop:1 #ffffff);
}}
QSplitter::handle:vertical {{
    height: {_SPLITTER_HANDLE_PX}px;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #ffffff, stop:0.46 #ffffff, stop:0.49 #c0c0c0, stop:0.51 #c0c0c0,
        stop:0.54 #ffffff, stop:1 #ffffff);
}}
QSplitter::handle:hover {{ background: #c0c0c0; }}
"""
_WHITE_SURFACE_STYLE = f"""
/* hsk-white-surfaces */
QGroupBox {{
 background-color: #ffffff;
 border: none;
 border-bottom: 1px solid #c0c0c0;
 border-radius: 0;
 margin-top: 0.8em;
 padding-top: 4px;
 padding-bottom: 6px;
}}
QGroupBox::title {{
 subcontrol-origin: margin;
 subcontrol-position: top left;
 left: 0px;
 padding: 0;
 background-color: #ffffff;
}}
QMenu {{ background-color: #ffffff; border: 1px solid #e0e0e0; color: #202020; }}
QMenu::item {{ color: #202020; background-color: transparent; }}
QMenu::item:selected {{ color: #202020; background-color: #f2f2f2; }}
QMenu::item:disabled {{ color: #767676; }}
QStatusBar {{ background: #ffffff; }}
QStatusBar QLabel {{ color: #202020; }}
{_SPLITTER_HANDLE_STYLE}
"""

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
_CAPTION_MENU_ARROW_PAD = 16
_CAPTION_TAB_HPAD = 12
_TITLE_ATTR = "_hsk_caption_title"
_BUTTONS_ATTR = "_hsk_caption_buttons"
_MENU_HOVER_ATTR = "_hsk_menu_hover_reset"
_TITLE_COLOR = "#2e333d"
_NAV_COLOR = "#404654"
_TAB_ACTIVE_COLOR = "#2e86b7"
_TAB_LINE_COLOR = "#dbdbdb"
_TAB_HOVER_BG = "#f2f8fb"
_TAB_RADIUS = 4
_TAB_TOP_GAP = 4
_TAB_CONTENT_GAP = 8
_MENU_CHEVRON_ATTR = "_hsk_menu_chevron"
_FITTING_ATTR = "_hsk_caption_fitting"
_MENU_BUTTON_NAME = "captionMenuButton"
_TAB_LINE_ATTR = "_hsk_caption_tab_line"
_SUITE_NAME = "Harrix Swiss Knife"
_LIGHTNESS_THRESHOLD = 128

_WM_NCCALCSIZE = 0x0083
_WM_NCHITTEST = 0x0084
_WM_MOUSEMOVE = 0x0200
_WM_NCMOUSEMOVE = 0x00A0
_WM_MOUSELEAVE = 0x02A3
_WM_NCMOUSELEAVE = 0x02A2
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


class _CaptionEdgeLine(QWidget):
    """1px rule along the bottom of a caption corner, above its children."""

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setObjectName("captionEdgeLine")
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, on=True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, on=True)
        parent.installEventFilter(self)
        self.place()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802, ARG002
        """Keep the rule on the bottom edge after the corner lays out."""
        if event.type() in {QEvent.Type.Resize, QEvent.Type.Show, QEvent.Type.LayoutRequest}:
            self.place()
        return False

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Draw the corner's share of the caption rule."""
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(_TAB_LINE_COLOR))

    def place(self) -> None:
        """Stretch the rule to the corner and keep it above the caption controls."""
        parent = self.parentWidget()
        if parent is None:
            return
        self.setGeometry(0, max(0, parent.height() - 1), parent.width(), 1)
        self.raise_()
        self.update()


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


class _CaptionMenuChevron(QObject):
    """Paint a down arrow on each caption menu so it does not read as a tab."""

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._painting = False

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Draw the arrows after the menu bar paints its titles."""
        if event.type() != QEvent.Type.Paint or not isinstance(watched, QMenuBar):
            return False
        if not isinstance(event, QPaintEvent) or self._painting:
            return False
        self._painting = True
        try:
            watched.paintEvent(event)
        finally:
            self._painting = False
        _paint_menu_chevrons(watched)
        return True


class _CaptionTabLine(QObject):
    """Draw the caption rule on the tab bar, open under the active tab."""

    def __init__(self, tab_bar: QTabBar) -> None:
        super().__init__(tab_bar)
        self._painting = False
        tab_bar.installEventFilter(self)
        tab_bar.currentChanged.connect(tab_bar.update)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Paint the tab bar, then the rule in the tab bar's own coordinates."""
        if event.type() != QEvent.Type.Paint or not isinstance(watched, QTabBar) or self._painting:
            return False
        if not isinstance(event, QPaintEvent):
            return False
        self._painting = True
        try:
            watched.paintEvent(event)
        finally:
            self._painting = False
        if watched.count() > 0:
            _paint_tab_bar_line(watched)
        return True


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
            _place_caption_title(window)
            _fit_caption_overflow(window)
        elif event_type == QEvent.Type.Resize:
            _place_caption_title(window)
            _fit_caption_overflow(window)
        elif event_type == QEvent.Type.WindowStateChange:
            _apply_win32_frame(window, full=False)
            _sync_zoom_glyph(window)
        elif event_type in {QEvent.Type.WindowActivate, QEvent.Type.WindowDeactivate}:
            _sync_caption_active(window)
        elif event_type == QEvent.Type.PaletteChange:
            _apply_white_window_background(window)
            _sync_caption_palette(window)
        elif event_type == QEvent.Type.FontChange:
            _fit_caption_fonts(window)
            _style_caption_chrome(window)
            _place_caption_title(window)
            _fit_caption_overflow(window)
        elif event_type == QEvent.Type.WindowIconChange:
            _sync_caption_icon(window)
        elif event_type == QEvent.Type.WindowTitleChange:
            _sync_caption_icon_tooltip(window)
            _place_caption_title(window)
            _fit_caption_overflow(window)
        return False

    def minimize(self) -> None:
        """Minimize the caption's window."""
        self._window.showMinimized()

    def reset_button_hover(self) -> None:
        """Restore caption-button hover after a menu popup closes."""
        window = self._window
        QTimer.singleShot(0, lambda: _sync_caption_button_hover(window))

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


def install_win11_caption(
    window: QWidget,
    *,
    trailing_widgets: Sequence[QWidget] | None = None,
) -> bool:
    """Replace the native title bar with the caption row plus Windows 11 buttons.

    From the left: icon, bold app name, then tabs. From the right: optional
    trailing controls (search, sort, …), the menu, then the window buttons.
    No-op outside Windows. The window title string stays for the taskbar.

    Args:

    - `window` (`QWidget`): Main window, tabbed app, or any window with a box
      layout (for example Quick paste). Tabbed apps already have `tabWidget`.
    - `trailing_widgets` (`Sequence[QWidget] | None`): Extra controls placed
      in the caption before the menu and window buttons. Used by the tray
      command window for search and sort, and by layout captions for menus.

    Returns:

    - `bool`: `True` when the caption row was installed.

    """
    if sys.platform != "win32" or getattr(window, _INSTALLED_ATTR, False):
        return False
    tab_widget = getattr(window, "tabWidget", None)
    light = _palette_is_light(window)
    controller = _Win11CaptionController(window)
    setattr(window, _CONTROLLER_ATTR, controller)
    if isinstance(tab_widget, QTabWidget):
        _build_caption_row(window, tab_widget, controller, light=light)
    elif isinstance(window, QMainWindow):
        _build_menu_caption(window, controller, light=light, trailing_widgets=trailing_widgets)
    elif window.layout() is None or isinstance(window.layout(), QBoxLayout):
        _build_layout_caption(window, controller, light=light, trailing_widgets=trailing_widgets)
    else:
        logger.warning("Win11 caption needs a tabWidget, main window menu, or box layout")
        return False

    _install_menu_chevrons(window)
    _ensure_caption_title(window)
    _flush_caption_to_frame(window)
    _fit_caption_fonts(window)
    _apply_white_window_background(window)
    apply_flat_scrollbars_to_styled_item_views(window)
    _sync_caption_palette(window)
    window.installEventFilter(controller)
    setattr(window, _INSTALLED_ATTR, True)
    _set_frameless_window_flags(window)
    _collapse_native_menu_bar(window)
    _sync_caption_icon(window)
    _sync_zoom_glyph(window)
    _place_caption_title(window)
    _bind_caption_menu_hover(window, controller)
    setattr(window, _BUTTONS_ATTR, window.findChildren(CaptionButton))
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
    if msg.message in {_WM_MOUSEMOVE, _WM_NCMOUSEMOVE}:
        _sync_caption_button_hover(window)
        return None
    if msg.message in {_WM_MOUSELEAVE, _WM_NCMOUSELEAVE}:
        _clear_caption_button_hover(window)
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


def _apply_caption_title_style(label: QLabel) -> None:
    rule = (
        f"QLabel#captionTitleLabel {{ color: {_TITLE_COLOR}; background: transparent; "
        f"font-weight: 700; padding: 0px 12px 0px 2px; }}"
    )
    if label.styleSheet() != rule:
        label.setStyleSheet(rule)


def _apply_maximized_nccalcsize(window: QWidget, lparam: int) -> None:
    hwnd = int(window.winId())
    if hwnd == 0 or not bool(_user32().IsZoomed(hwnd)):
        return
    work = _monitor_work_area(hwnd)
    if work is None:
        return
    write_nccalcsize_client_rect(_pointer_address(lparam), *work)


def _apply_white_surfaces(window: QWidget) -> None:
    """Paint panels, tab pages, and popup menus white without restyling controls.

    The same group-box, menu, status-bar, and splitter-handle colors live on
    `QMainWindow` in each app `window.ui`. This appends them only when the form
    did not. A stylesheet that matches every child makes Qt drop the Windows 11
    scrollbar, button, and header drawing. Each plain container gets a rule for
    its own object name only, unless that form widget already has a white background.

    """
    sheet = window.styleSheet()
    if _WHITE_SURFACE_MARK not in sheet:
        window.setStyleSheet(f"{sheet}\n{_WHITE_SURFACE_STYLE}")
    _whiten_main_containers(window)


def _apply_white_window_background(window: QWidget) -> None:
    """Use white for the window, its panels, menus, and caption."""
    palette = window.palette()
    if palette.color(QPalette.ColorRole.Window) != _WINDOW_BACKGROUND:
        palette.setColor(QPalette.ColorRole.Window, _WINDOW_BACKGROUND)
        window.setPalette(palette)
    window.setAutoFillBackground(True)
    _apply_white_surfaces(window)


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


def _bind_caption_menu_hover(window: QWidget, controller: _Win11CaptionController) -> None:
    """Refresh caption-button hover when a menu popup closes."""
    menu_bar = resolve_window_menu_bar(window)
    if menu_bar is None:
        return
    for action in menu_bar.actions():
        menu = action.menu()
        if isinstance(menu, QMenu):
            _bind_menu_hover_reset(menu, controller)


def _bind_menu_hover_reset(menu: QMenu, controller: _Win11CaptionController) -> None:
    if getattr(menu, _MENU_HOVER_ATTR, False):
        return
    menu.aboutToHide.connect(controller.reset_button_hover)
    for action in menu.actions():
        child = action.menu()
        if isinstance(child, QMenu):
            _bind_menu_hover_reset(child, controller)
    setattr(menu, _MENU_HOVER_ATTR, True)


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
    _move_tab_menu_beside_buttons(tab_widget, controller, light=light, window=window)
    left = tab_widget.cornerWidget(Qt.Corner.TopLeftCorner)
    left_layout = left.layout() if left is not None else None
    if isinstance(left_layout, QBoxLayout):
        _insert_caption_title(window, left_layout)


def _build_layout_caption(
    window: QWidget,
    controller: _Win11CaptionController,
    *,
    light: bool,
    trailing_widgets: Sequence[QWidget] | None = None,
) -> None:
    """Insert a caption strip at the top of `window`'s box layout."""
    host = QWidget(window)
    host.setObjectName("captionBar")
    host.setFixedHeight(CAPTION_BUTTON_HEIGHT)
    layout = QHBoxLayout(host)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)

    icon_button = _CaptionIconButton(controller.show_system_menu, host)
    icon_button.setIcon(window.windowIcon())
    icon_button.setToolTip(_caption_icon_tooltip(window))
    layout.addWidget(icon_button)
    _insert_caption_title(window, layout)

    trailing = list(trailing_widgets) if trailing_widgets else []
    has_expanding = any(widget.sizePolicy().horizontalPolicy() == QSizePolicy.Policy.Expanding for widget in trailing)
    if not has_expanding:
        layout.addStretch(1)
    for widget in trailing:
        stretch = 1 if widget.sizePolicy().horizontalPolicy() == QSizePolicy.Policy.Expanding else 0
        layout.addWidget(widget, stretch=stretch)

    layout.addWidget(_make_caption_button_row(host, controller, light=light))

    root = window.layout()
    if not isinstance(root, QBoxLayout):
        root = QVBoxLayout(window)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
    root.insertWidget(0, host)


def _build_menu_caption(
    window: QMainWindow,
    controller: _Win11CaptionController,
    *,
    light: bool,
    trailing_widgets: Sequence[QWidget] | None = None,
) -> None:
    host = QWidget(window)
    host.setObjectName("captionBar")
    host.setFixedHeight(CAPTION_BUTTON_HEIGHT)
    layout = QHBoxLayout(host)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)

    icon_button = _CaptionIconButton(controller.show_system_menu, host)
    icon_button.setIcon(window.windowIcon())
    icon_button.setToolTip(_caption_icon_tooltip(window))
    layout.addWidget(icon_button)
    _insert_caption_title(window, layout)

    trailing = list(trailing_widgets) if trailing_widgets else []
    has_expanding = any(widget.sizePolicy().horizontalPolicy() == QSizePolicy.Policy.Expanding for widget in trailing)
    if not has_expanding:
        layout.addStretch(1)
    for widget in trailing:
        stretch = 1 if widget.sizePolicy().horizontalPolicy() == QSizePolicy.Policy.Expanding else 0
        layout.addWidget(widget, stretch=stretch)

    # Do not call window.menuBar() here: it installs a QMenuBar as the menu
    # widget and would replace the caption host we are about to set.
    native = _existing_main_window_menu_bar(window)
    menu_actions = list(native.actions()) if native is not None else []
    if menu_actions and native is not None:
        menu = QMenuBar(host)
        menu.setNativeMenuBar(False)
        menu.setFixedHeight(CAPTION_BUTTON_HEIGHT)
        menu.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        for action in menu_actions:
            native.removeAction(action)
            menu.addAction(action)
            # Menus stay children of the old bar. setMenuWidget deletes that bar.
            # setParent(parent) clears Popup, so the menu would show inline.
            submenu = action.menu()
            if isinstance(submenu, QWidget):
                submenu.setParent(menu, Qt.WindowType.Popup)
                submenu.hide()
        layout.addWidget(menu)
        layout.addWidget(_make_caption_menu_button(window, controller, host))
    layout.addWidget(_make_caption_button_row(host, controller, light=light))
    window.setMenuWidget(host)


def _caption_available_width(window: QWidget) -> int:
    """Return the width the caption row can use."""
    host = _caption_host(window)
    if host is not None and host.width() > 0:
        return host.width()
    tab_widget = getattr(window, "tabWidget", None)
    if isinstance(tab_widget, QTabWidget) and tab_widget.width() > 0:
        return tab_widget.width()
    return window.width()


def _caption_buttons(window: QWidget) -> list[CaptionButton]:
    cached = getattr(window, _BUTTONS_ATTR, None)
    if isinstance(cached, list):
        return [button for button in cached if isinstance(button, CaptionButton)]
    buttons = window.findChildren(CaptionButton)
    setattr(window, _BUTTONS_ATTR, buttons)
    return buttons


def _caption_control_at(window: QWidget, local: QPoint) -> bool:
    child = window.childAt(local)
    while child is not None and child is not window:
        if isinstance(child, (QAbstractButton, QLineEdit, QComboBox, QAbstractSpinBox)):
            return True
        if isinstance(child, QTabBar):
            return child.tabAt(child.mapFrom(window, local)) >= 0
        if isinstance(child, QMenuBar):
            return child.actionAt(child.mapFrom(window, local)) is not None
        child = child.parentWidget()
    return False


def _caption_host(window: QWidget) -> QWidget | None:
    host = window.findChild(QWidget, "captionBar")
    if isinstance(host, QWidget):
        return host
    if isinstance(window, QMainWindow):
        menu_widget = window.menuWidget()
        if isinstance(menu_widget, QWidget) and menu_widget.objectName() == "captionBar":
            return menu_widget
    return None


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
    host = _caption_host(window)
    anchor: QWidget | None = host
    if anchor is None:
        tab_widget = getattr(window, "tabWidget", None)
        if isinstance(tab_widget, QTabWidget):
            anchor = tab_widget.tabBar()
    if anchor is None:
        return QRect()
    top_left = anchor.mapTo(window, QPoint(0, 0))
    height = max(anchor.height(), CAPTION_BUTTON_HEIGHT)
    return QRect(0, top_left.y(), window.width(), height)


def _caption_title_parent(window: QWidget) -> QWidget | None:
    tab_widget = getattr(window, "tabWidget", None)
    if isinstance(tab_widget, QTabWidget):
        corner = tab_widget.cornerWidget(Qt.Corner.TopLeftCorner)
        if corner is not None:
            return corner
        return tab_widget
    return _caption_host(window)


def _caption_title_width(label: QLabel) -> int:
    """Return the title width, including the caption padding."""
    text = label.text()
    if not text:
        return 0
    return QFontMetrics(label.font()).horizontalAdvance(text) + 14


def _clear_caption_button_hover(window: QWidget) -> None:
    for button in _caption_buttons(window):
        try:
            hovered = button.testAttribute(Qt.WidgetAttribute.WA_UnderMouse)
        except RuntimeError:
            continue
        if not hovered:
            continue
        button.setAttribute(Qt.WidgetAttribute.WA_UnderMouse, on=False)
        button.update()


def _collapse_native_menu_bar(window: QWidget) -> None:
    if _caption_host(window) is not None:
        return
    bar = _existing_main_window_menu_bar(window)
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


def _ensure_caption_base_line(tab_widget: QTabWidget) -> None:
    """Run the caption rule across the window when tabs are showing."""
    if tab_widget.count() == 0:
        return
    tab_bar = tab_widget.tabBar()
    if getattr(tab_bar, _TAB_LINE_ATTR, None) is None:
        setattr(tab_bar, _TAB_LINE_ATTR, _CaptionTabLine(tab_bar))
    for corner in (Qt.Corner.TopLeftCorner, Qt.Corner.TopRightCorner):
        widget = tab_widget.cornerWidget(corner)
        if widget is None or widget.findChild(_CaptionEdgeLine, "captionEdgeLine") is not None:
            continue
        _CaptionEdgeLine(widget)


def _ensure_caption_title(window: QWidget, parent: QWidget | None = None) -> QLabel | None:
    """Create the bold caption title, parented to the left side of the row."""
    existing = getattr(window, _TITLE_ATTR, None)
    if isinstance(existing, QLabel):
        return existing
    host = parent if parent is not None else _caption_title_parent(window)
    if host is None:
        return None
    label = QLabel(host)
    label.setObjectName("captionTitleLabel")
    label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
    label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, on=True)
    label.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    label.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
    font = QFont(window.font())
    font.setBold(True)
    label.setFont(font)
    _apply_caption_title_style(label)
    setattr(window, _TITLE_ATTR, label)
    return label


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


def _existing_main_window_menu_bar(window: QWidget) -> QMenuBar | None:
    """Return an already-created main-window menu bar without calling `menuBar()`."""
    menu_bar = getattr(window, "menuBar", None)
    if isinstance(menu_bar, QMenuBar):
        return menu_bar
    for child in window.children():
        if isinstance(child, QMenuBar):
            return child
    if isinstance(window, QMainWindow):
        menu_widget = window.menuWidget()
        if isinstance(menu_widget, QMenuBar):
            return menu_widget
    return None


def _extend_frame_for_shadow(hwnd: int) -> None:
    margins = _MARGINS(0, 0, 0, 1)
    _dwmapi().DwmExtendFrameIntoClientArea(hwnd, ctypes.byref(margins))


def _fill_caption_overflow_menu(window: QWidget, popup: QMenu) -> None:
    """Copy the caption menu bar into the hamburger popup."""
    popup.clear()
    menu = resolve_window_menu_bar(window)
    if menu is None:
        return
    for action in menu.actions():
        popup.addAction(action)


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
    label = getattr(window, _TITLE_ATTR, None)
    if isinstance(label, QLabel):
        font = QFont(window.font())
        font.setBold(True)
        label.setFont(font)
        _fit_widget_font(label, CAPTION_BUTTON_HEIGHT - _CAPTION_FONT_SLACK)


def _fit_caption_overflow(window: QWidget) -> None:
    """Hide the title first, then fold the menu into a hamburger."""
    if getattr(window, _FITTING_ATTR, False):
        return
    available = _caption_available_width(window)
    if available <= 0:
        return
    setattr(window, _FITTING_ATTR, True)
    try:
        title = getattr(window, _TITLE_ATTR, None)
        menu = resolve_window_menu_bar(window)
        button = window.findChild(QToolButton, _MENU_BUTTON_NAME)
        icon = window.findChild(QToolButton, "captionIconButton")
        buttons = window.findChild(QWidget, "captionButtonRow")
        icon_width = icon.width() if isinstance(icon, QToolButton) and icon.width() > 0 else CAPTION_BUTTON_HEIGHT
        button_width = (
            buttons.width() if isinstance(buttons, QWidget) and buttons.width() > 0 else CAPTION_BUTTON_WIDTH * 3
        )
        tabs_width = _tab_strip_width(getattr(window, "tabWidget", None))
        if tabs_width is None:
            return
        title_width = _caption_title_width(title) if isinstance(title, QLabel) else 0
        menu_width = _menu_bar_width(menu) if isinstance(menu, QMenuBar) else 0
        tools_width = 0
        host = _caption_host(window)
        tools = host.findChild(QWidget, "captionTools") if host is not None else None
        if isinstance(tools, QWidget) and tools.isVisibleTo(window):
            tools_width = max(tools.minimumSizeHint().width(), tools.sizeHint().width())
        show_title = title_width > 0
        show_menu = menu_width > 0
        if icon_width + title_width + tabs_width + menu_width + tools_width + button_width > available:
            show_title = False
        if show_menu and icon_width + tabs_width + menu_width + tools_width + button_width > available:
            show_menu = False
        if isinstance(title, QLabel) and title.isVisible() != show_title:
            title.setVisible(show_title)
        if isinstance(menu, QMenuBar) and menu_width > 0 and menu.isVisible() != show_menu:
            menu.setVisible(show_menu)
        if isinstance(button, QToolButton):
            show_button = not show_menu and menu_width > 0
            if button.isVisible() != show_button:
                button.setVisible(show_button)
    finally:
        setattr(window, _FITTING_ATTR, False)


def _fit_widget_font(widget: QWidget, max_height: int) -> None:
    fitted = _shrunk_font(widget.font(), max_height)
    current = widget.font()
    if fitted.pointSizeF() == current.pointSizeF() and fitted.pixelSize() == current.pixelSize():
        return
    widget.setFont(fitted)


def _flush_caption_to_frame(window: QWidget) -> None:
    if not isinstance(window, QMainWindow):
        return
    if not isinstance(getattr(window, "tabWidget", None), QTabWidget):
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


def _insert_caption_title(window: QWidget, layout: QBoxLayout) -> None:
    parent = layout.parentWidget()
    if not isinstance(parent, QWidget):
        return
    label = _ensure_caption_title(window, parent)
    if label is None or layout.indexOf(label) >= 0:
        return
    layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
    layout.insertWidget(1 if layout.count() else 0, label)
    _place_caption_title(window)


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


def _install_menu_chevrons(window: QWidget) -> None:
    menu = resolve_window_menu_bar(window)
    if menu is None or getattr(menu, _MENU_CHEVRON_ATTR, False):
        return
    menu.installEventFilter(_CaptionMenuChevron(menu))
    setattr(menu, _MENU_CHEVRON_ATTR, True)


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


def _make_caption_button_row(
    parent: QWidget,
    controller: _Win11CaptionController,
    *,
    light: bool,
) -> QWidget:
    row = QWidget(parent)
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
    return row


def _make_caption_menu_button(
    window: QWidget,
    controller: _Win11CaptionController,
    parent: QWidget,
) -> QToolButton:
    """Build the hamburger that replaces the caption menu when it no longer fits."""
    button = QToolButton(parent)
    button.setObjectName(_MENU_BUTTON_NAME)
    button.setFixedSize(CAPTION_BUTTON_HEIGHT, CAPTION_BUTTON_HEIGHT)
    button.setAutoRaise(True)
    button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    button.setAutoFillBackground(False)
    button.setToolTip("Menu")
    button.setCursor(Qt.CursorShape.ArrowCursor)
    button.setVisible(False)
    apply_lucide_button_icon(button, "menu", icon_size=CAPTION_ICON_SIZE, color=_NAV_COLOR)
    popup = QMenu(button)
    popup.setObjectName("captionOverflowMenu")
    popup.aboutToShow.connect(lambda: _fill_caption_overflow_menu(window, popup))
    popup.aboutToHide.connect(controller.reset_button_hover)
    button.clicked.connect(lambda: popup.popup(button.mapToGlobal(QPoint(0, button.height()))))
    return button


def _menu_bar_width(menu: QMenuBar) -> int:
    """Return the width of the caption menu titles."""
    actions = [action for action in menu.actions() if action.isVisible()]
    if not actions:
        return 0
    metrics = QFontMetrics(menu.font())
    estimated = 0
    for action in actions:
        label = action.text().replace("&", "")
        estimated += metrics.horizontalAdvance(label) + _CAPTION_MENU_HPAD + _CAPTION_MENU_ARROW_PAD
    return max(menu.sizeHint().width(), estimated)


def _menu_glyph_center_y(menu: QMenuBar, rect: QRect) -> int:
    """Return the vertical center of the menu title letters, not the item box."""
    metrics = QFontMetrics(menu.font())
    box_top = rect.top() + (rect.height() - metrics.height()) // 2
    baseline = box_top + metrics.ascent()
    return baseline - max(metrics.capHeight(), 1) // 2


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


def _move_tab_menu_beside_buttons(
    tab_widget: QTabWidget,
    controller: _Win11CaptionController,
    *,
    light: bool,
    window: QWidget,
) -> None:
    """Put the main menu on the right, immediately before the window buttons."""
    left = tab_widget.cornerWidget(Qt.Corner.TopLeftCorner)
    menu: QMenuBar | None = None
    if left is not None:
        found = left.findChildren(QMenuBar)
        menu = found[0] if found else None
        layout = left.layout()
        if isinstance(layout, QBoxLayout):
            if menu is not None:
                layout.removeWidget(menu)
            _remove_caption_separators(layout)
    right = QWidget(tab_widget)
    right.setObjectName("captionRightCluster")
    right.setFixedHeight(CAPTION_BUTTON_HEIGHT)
    right_layout = QHBoxLayout(right)
    right_layout.setContentsMargins(0, 0, 0, 0)
    right_layout.setSpacing(0)
    if menu is not None:
        menu.setParent(right)
        menu.setFixedHeight(CAPTION_BUTTON_HEIGHT)
        menu.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        right_layout.addWidget(menu)
        right_layout.addWidget(_make_caption_menu_button(window, controller, right))
    right_layout.addWidget(_make_caption_button_row(right, controller, light=light))
    tab_widget.setCornerWidget(right, Qt.Corner.TopRightCorner)


def _owned_by_native_control(widget: QWidget) -> bool:
    parent = widget.parentWidget()
    while parent is not None:
        if any(
            parent.inherits(name)
            for name in (
                "QAbstractButton",
                "QAbstractItemView",
                "QAbstractSpinBox",
                "QComboBox",
                "QHeaderView",
                "QScrollBar",
                "QTabBar",
                "QMenu",
            )
        ):
            return True
        parent = parent.parentWidget()
    return False


def _paint_container_white(widget: QWidget) -> None:
    name = widget.objectName()
    if not name:
        name = f"hskWhiteSurface{id(widget)}"
        widget.setObjectName(name)
    rule = f"QWidget#{name} {{ background-color: #ffffff; }}"
    sheet = widget.styleSheet()
    if rule in sheet or (f"#{name}" in sheet and "#ffffff" in sheet):
        return
    widget.setStyleSheet(f"{sheet}\n{rule}" if sheet else rule)


def _paint_menu_chevrons(menu: QMenuBar) -> None:
    painter = QPainter(menu)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, on=True)
    pen = painter.pen()
    pen.setWidthF(1.3)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    for action in menu.actions():
        if not action.isVisible() or action.menu() is None:
            continue
        rect = menu.actionGeometry(action)
        if rect.width() < _CAPTION_MENU_ARROW_PAD:
            continue
        pen.setColor(QColor(_NAV_COLOR if action.isEnabled() else "#767676"))
        painter.setPen(pen)
        center_x = rect.right() - _CAPTION_MENU_ARROW_PAD // 2
        center_y = _menu_glyph_center_y(menu, rect)
        span = 3
        painter.drawPolyline(
            [
                QPoint(center_x - span, center_y - 2),
                QPoint(center_x, center_y + 2),
                QPoint(center_x + span, center_y - 2),
            ]
        )
    painter.end()


def _paint_tab_bar_line(tab_bar: QTabBar) -> None:
    """Draw the rule across the tab bar, leaving the active tab's bottom open."""
    painter = QPainter(tab_bar)
    color = QColor(_TAB_LINE_COLOR)
    y = tab_bar.height() - 1
    painter.fillRect(0, y, tab_bar.width(), 1, color)
    index = tab_bar.currentIndex()
    if index < 0:
        return
    rect = tab_bar.tabRect(index)
    opening = rect.width() - 2
    if opening <= 0:
        return
    fill = tab_bar.palette().color(QPalette.ColorRole.Window)
    painter.fillRect(rect.x() + 1, y, opening, 1, fill)


def _palette_is_light(window: QWidget) -> bool:
    return window.palette().color(QPalette.ColorRole.Window).lightness() >= _LIGHTNESS_THRESHOLD


def _place_caption_title(window: QWidget) -> None:
    """Keep the caption title equal to the icon tooltip."""
    label = getattr(window, _TITLE_ATTR, None)
    if not isinstance(label, QLabel):
        return
    full = _caption_icon_tooltip(window)
    if label.text() != full:
        label.setText(full)
    if label.toolTip() != full:
        label.setToolTip(full)
    label.show()


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


def _remove_caption_separators(layout: QBoxLayout) -> None:
    for index in range(layout.count() - 1, -1, -1):
        item = layout.itemAt(index)
        if item is None:
            continue
        widget = item.widget()
        if isinstance(widget, QFrame) and widget.frameShape() == QFrame.Shape.VLine:
            layout.removeWidget(widget)
            widget.setParent(None)
            widget.deleteLater()


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
    tab_widget = getattr(window, "tabWidget", None)
    if isinstance(tab_widget, QTabWidget):
        name = tab_widget.objectName() or "tabWidget"
        if not tab_widget.objectName():
            tab_widget.setObjectName(name)
        tab_widget.setStyleSheet(
            f"QTabWidget#{name} {{ background-color: {rgb}; border: none; }}"
            f"QTabWidget::pane {{ border: none; margin: 0px; margin-top: {_TAB_CONTENT_GAP}px; background: {rgb}; }}"
        )
        _fill_widget(tab_widget, color)
        for index in range(tab_widget.count()):
            page = tab_widget.widget(index)
            if isinstance(page, QWidget):
                _fill_widget(page, color)
        tab_bar = tab_widget.tabBar()
        tab_bar.setDrawBase(False)
        text_height = QFontMetrics(tab_bar.font()).height()
        pad = max(0, (CAPTION_BUTTON_HEIGHT - _TAB_TOP_GAP - text_height - 2) // 2)
        tab_bar.setStyleSheet(
            f"""
            QTabBar {{
                background: {rgb};
                border: none;
            }}
            QTabBar::tab {{
                background: transparent;
                color: {_NAV_COLOR};
                border: 1px solid transparent;
                border-top-left-radius: {_TAB_RADIUS}px;
                border-top-right-radius: {_TAB_RADIUS}px;
                margin-top: {_TAB_TOP_GAP}px;
                margin-right: 0px;
                margin-bottom: 0px;
                margin-left: 0px;
                padding: {pad}px {_CAPTION_TAB_HPAD}px;
            }}
            QTabBar::tab:hover:!selected {{
                background: {_TAB_HOVER_BG};
                color: {_TAB_ACTIVE_COLOR};
            }}
            QTabBar::tab:selected {{
                background: {rgb};
                color: {_TAB_ACTIVE_COLOR};
                border: 1px solid {_TAB_LINE_COLOR};
                border-bottom: 1px solid {rgb};
                margin-top: {_TAB_TOP_GAP}px;
                margin-bottom: -1px;
            }}
            """
        )
        _ensure_caption_base_line(tab_widget)
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
            font-weight: 400;
        }}
        QMenuBar::item {{
            background: transparent;
            color: {_NAV_COLOR};
            padding: {pad}px {_CAPTION_MENU_ARROW_PAD}px {pad}px {_CAPTION_MENU_HPAD}px;
            margin: 0px;
        }}
        QMenuBar::item:selected {{
            background: {hover};
            color: {_NAV_COLOR};
        }}
        """
    )
    button = window.findChild(QToolButton, _MENU_BUTTON_NAME)
    if isinstance(button, QToolButton):
        button.setStyleSheet(
            f"QToolButton#{_MENU_BUTTON_NAME} {{ background: transparent; border: none; }}"
            f"QToolButton#{_MENU_BUTTON_NAME}:hover {{ background: {hover}; }}"
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
    label = getattr(window, _TITLE_ATTR, None)
    if isinstance(label, QLabel):
        _apply_caption_title_style(label)


def _sync_caption_button_hover(window: QWidget, global_pos: QPoint | None = None) -> None:
    """Paint caption-button hover from the pointer, even after a menu steals it."""
    try:
        if not window.isVisible():
            return
    except RuntimeError:
        return
    point = QCursor.pos() if global_pos is None else global_pos
    for button in _caption_buttons(window):
        try:
            inside = button.isVisible() and button.rect().contains(button.mapFromGlobal(point))
            hovered = button.testAttribute(Qt.WidgetAttribute.WA_UnderMouse)
        except RuntimeError:
            continue
        if hovered == inside:
            continue
        button.setAttribute(Qt.WidgetAttribute.WA_UnderMouse, on=inside)
        button.update()


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
    host = _caption_host(window)
    if host is not None:
        _fill_widget(host, color)
    row = window.findChild(QWidget, "captionButtonRow")
    if isinstance(row, QWidget):
        _fill_widget(row, color)
    tab_widget = getattr(window, "tabWidget", None)
    if isinstance(tab_widget, QTabWidget):
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


def _tab_strip_width(tab_widget: QWidget | None) -> int | None:
    """Return the width of every tab, or `None` before the bar has been laid out."""
    if not isinstance(tab_widget, QTabWidget) or tab_widget.count() == 0:
        return 0
    tab_bar = tab_widget.tabBar()
    total = 0
    for index in range(tab_bar.count()):
        width = tab_bar.tabRect(index).width()
        if width <= 0:
            return None
        total += width
    return total


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


def _whiten_main_containers(window: QWidget) -> None:
    """Fill tab pages and layout panels white while leaving controls on the native style."""
    for widget in window.findChildren(QWidget):
        if isinstance(widget, QScrollArea):
            viewport = widget.viewport()
            if type(viewport) is QWidget and not _owned_by_native_control(viewport):
                _paint_container_white(viewport)
        if type(widget) not in {QWidget, QFrame, QSplitter, QStackedWidget}:
            continue
        if isinstance(widget, _CaptionEdgeLine):
            continue
        if _owned_by_native_control(widget):
            continue
        _paint_container_white(widget)


def _window_is_zoomed(window: QWidget) -> bool:
    state = window.windowState()
    return bool(state & (Qt.WindowState.WindowMaximized | Qt.WindowState.WindowFullScreen))
