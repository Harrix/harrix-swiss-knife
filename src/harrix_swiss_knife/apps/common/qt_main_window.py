"""Shared helpers for app-level `QMainWindow` implementations.

Provides `AppWindowMixin` with methods that were previously duplicated in
`finance/main.py`, `fitness/main.py`, `food/main.py`, and `habits/main.py`:

- `_setup_window_size_and_position`
- `_show_placed_window`
- `_place_menu_bar_on_tab_row`
- `_copy_table_selection_to_clipboard`
- `_validate_database_connection`
- `_handle_ctrl_c_for_tables`
- Exit / About menu actions
- Show database in folder (File menu)

"""

from __future__ import annotations

import ctypes
import logging
import sys
import tomllib
from ctypes import wintypes
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar, cast

import harrix_pylib as h
from PySide6.QtCore import QEvent, QObject, QRect, Qt, QTimer
from PySide6.QtGui import QAction, QCursor, QGuiApplication, QScreen, QWindowStateChangeEvent
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QMenu,
    QMenuBar,
    QSizePolicy,
    QStyle,
    QTableView,
    QTabWidget,
    QWidget,
)
from shiboken6 import isValid

from harrix_swiss_knife.apps.common import message_box
from harrix_swiss_knife.apps.common.ui_helpers import reveal_in_file_explorer
from harrix_swiss_knife.apps.common.word_wrap_header import install_word_wrap_headers
from harrix_swiss_knife.qt_app_font import apply_ui_font_scale
from harrix_swiss_knife.qt_emoji_icon import apply_leading_emoji_icons, set_action_text_with_emoji_icon

if TYPE_CHECKING:
    from PySide6.QtGui import QCloseEvent, QKeyEvent
    from PySide6.QtWidgets import QMainWindow


class AppWindowMixin:
    """Mixin with common `QMainWindow` helpers shared across apps."""

    about_app_name: ClassVar[str] = "Harrix Swiss Knife"
    about_description: ClassVar[str] = ""

    actionAbout: QAction  # noqa: N815
    actionExit: QAction  # noqa: N815
    db_manager: Any
    _hide_on_close: bool

    def on_about(self) -> None:
        """Show the About dialog with app information."""
        version = self._get_version_from_pyproject()
        description = type(self).about_description
        github_url = "https://github.com/harrix/harrix-swiss-knife"
        lines = [
            type(self).about_app_name,
            "",
            f"Version: {version}",
            "",
        ]
        if description:
            lines.extend([description, ""])
        lines.extend(
            [
                "Part of Harrix Swiss Knife.",
                "",
                "Author: Anton Sergienko (Harrix)",
                "License: MIT License",
                f"GitHub: {github_url}",
            ],
        )
        plain_text = "\n".join(lines)
        html_text = "<br>".join([*lines[:-1], f'GitHub: <a href="{github_url}">{github_url}</a>'])
        message_box.information(
            cast("QWidget", self),
            "About",
            html_text,
            rich_text=True,
            clipboard_text=plain_text,
        )

    def on_exit(self) -> None:
        """Close the application window."""
        self.close()  # type: ignore[attr-defined]

    def on_reveal_database(self) -> None:
        """Open the system file manager with this app's SQLite database selected."""
        db_path = self._resolve_database_path()
        if db_path is None:
            message_box.warning(
                cast("QWidget", self),
                "Database",
                "Database path is not available.",
            )
            return
        if not db_path.is_file():
            message_box.warning(
                cast("QWidget", self),
                "Database",
                f"Database file was not found:\n{db_path}",
            )
            return
        try:
            reveal_in_file_explorer(db_path)
        except (FileNotFoundError, OSError) as exc:
            message_box.warning(cast("QWidget", self), "Database", str(exc))

    def _apply_exit_about_menu_emojis(self) -> None:
        """Prefix Exit and About with emoji, then turn menu-bar prefixes into icons."""
        self.actionExit.setText(f"🚪 {self.actionExit.text()}")
        self.actionAbout.setText(f"ℹ️ {self.actionAbout.text()}")  # noqa: RUF001
        self._apply_menu_bar_emoji_icons()

    def _apply_menu_bar_emoji_icons(self) -> None:
        """Move leading emoji from File / Commands / Help action text onto icons."""
        menu_bar = resolve_window_menu_bar(cast("QWidget", self))
        if menu_bar is not None:
            apply_leading_emoji_icons(menu_bar)
        for name in ("menuFile", "menuCommands", "menuCommanda", "menuHelp"):
            menu = getattr(self, name, None)
            if isinstance(menu, QMenu):
                apply_leading_emoji_icons(menu)

    def _connect_exit_about_actions(self) -> None:
        """Wire Exit and About menu actions to their handlers."""
        self.actionExit.triggered.connect(self.on_exit)
        self.actionAbout.triggered.connect(self.on_about)
        self._setup_reveal_database_action()

    def _copy_table_selection_to_clipboard(self, table_view: QTableView) -> None:
        """Copy selected cells from `table_view` to clipboard as tab-separated text.

        Args:

        - `table_view` (`QTableView`): The table view to copy data from.

        """
        selection_model = table_view.selectionModel()
        if not selection_model or not selection_model.hasSelection():
            return

        selected_indexes = selection_model.selectedIndexes()
        if not selected_indexes:
            return

        selected_indexes.sort(key=lambda index: (index.row(), index.column()))

        rows_data: dict[int, dict[int, str]] = {}
        for index in selected_indexes:
            row = index.row()
            if row not in rows_data:
                rows_data[row] = {}

            cell_data = table_view.model().data(index, Qt.ItemDataRole.DisplayRole)
            rows_data[row][index.column()] = str(cell_data) if cell_data is not None else ""

        clipboard_text: list[str] = []
        for row in sorted(rows_data.keys()):
            row_data = rows_data[row]
            if row_data:
                min_col = min(row_data.keys())
                max_col = max(row_data.keys())
                clipboard_text.append("\t".join([row_data.get(col, "") for col in range(min_col, max_col + 1)]))

        if clipboard_text:
            final_text = "\n".join(clipboard_text)
            clipboard = QApplication.clipboard()
            if clipboard is not None:
                clipboard.setText(final_text)
                logger.info("%s", f"Copied {len(clipboard_text)} rows to clipboard")

    def _get_version_from_pyproject(self) -> str:
        """Get version from `pyproject.toml`.

        Returns:

        - `str`: Version string, or `Unknown` if it cannot be read.

        """
        try:
            pyproject_path = h.dev.get_project_root() / "pyproject.toml"
            with pyproject_path.open("rb") as f:
                data = tomllib.load(f)
            return data.get("project", {}).get("version", "Unknown")
        except Exception:
            logger.exception("⚠️ Warning: Could not read version from pyproject.toml")
            return "Unknown"

    def _handle_ctrl_c_for_tables(self, event: QKeyEvent, table_views: list[QTableView]) -> bool:
        """Copy table selection to clipboard on Ctrl+C if a table is focused.

        Args:

        - `event` (`QKeyEvent`): Key press event.
        - `table_views` (`list[QTableView]`): Candidate table views.

        Returns:

        - `bool`: `True` if the shortcut was handled, `False` otherwise.

        """
        if not (event.key() == Qt.Key.Key_C and event.modifiers() == Qt.KeyboardModifier.ControlModifier):
            return False

        focused_widget = QApplication.focusWidget()
        for table_view in table_views:
            if focused_widget == table_view:
                self._copy_table_selection_to_clipboard(table_view)
                return True

        for table_view in table_views:
            if focused_widget and table_view.isAncestorOf(focused_widget):
                self._copy_table_selection_to_clipboard(table_view)
                return True

        return False

    def _hide_instead_of_close(self, event: QCloseEvent) -> bool:
        """Hide the window and return `True` when the launcher reuses this instance.

        Args:

        - `event` (`QCloseEvent`): The close event.

        Returns:

        - `bool`: `True` when the window was hidden instead of closed.

        """
        if not getattr(self, "_hide_on_close", False):
            return False
        event.ignore()
        self.hide()  # type: ignore[attr-defined]
        return True

    def _init_hide_on_close(self, *, hide_on_close: bool) -> None:
        """Remember close behavior; delete on close only when the window is not reused.

        Args:

        - `hide_on_close` (`bool`): When `True`, close hides the window for reuse.

        """
        self._hide_on_close = hide_on_close
        if not hide_on_close:
            self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)  # type: ignore[attr-defined]

    def _install_word_wrap_table_headers(
        self,
        *,
        skip: set[QTableView] | frozenset[QTableView] | None = None,
    ) -> None:
        """Enable wrapping titles on every `QTableView` in this window."""
        install_word_wrap_headers(cast("QWidget", self), skip=skip)

    def _place_menu_bar_on_tab_row(self) -> None:
        """Put the main menu on the same row as tabs (left of the tab bar).

        Moves menus from the `QMainWindow` menu bar into a bold compact
        `QMenuBar` with a vertical separator, set as the `QTabWidget`
        top-left corner widget, then collapses the original menu bar row.

        """
        apply_ui_font_scale(cast("QWidget", self))
        main_window = cast("QMainWindow", self)
        tab_widget = getattr(self, "tabWidget", None)
        if not isinstance(tab_widget, QTabWidget):
            return

        # UI files name the bar `menuBar`, which shadows `QMainWindow.menuBar()`.
        menu_bar = getattr(main_window, "menuBar", None)
        if isinstance(menu_bar, QMenuBar):
            old_bar = menu_bar
        elif callable(menu_bar):
            old_bar = menu_bar()
        else:
            return
        if old_bar is None:
            return

        corner_bar = QMenuBar()
        corner_bar.setNativeMenuBar(False)
        corner_bar.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        corner_bar.setStyleSheet(
            """
            QMenuBar {
                spacing: 0px;
                padding: 0px 2px;
                font-size: 9pt;
                font-weight: 700;
            }
            QMenuBar::item {
                padding: 2px 8px;
                margin: 0px;
                background: transparent;
            }
            """,
        )

        for action in list(old_bar.actions()):
            old_bar.removeAction(action)
            corner_bar.addAction(action)

        # Bold menu + vertical rule so it reads as chrome, not another tab.
        corner = QWidget(tab_widget)
        corner_layout = QHBoxLayout(corner)
        corner_layout.setContentsMargins(0, 0, 8, 0)
        corner_layout.setSpacing(4)
        corner_layout.addWidget(corner_bar)

        separator = QFrame(corner)
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setFixedWidth(6)
        corner_layout.addWidget(separator)

        tab_widget.setCornerWidget(corner, Qt.Corner.TopLeftCorner)

        # Keep the original bar as the QMainWindow menuBar (do not replace/delete it),
        # but collapse the reserved row.
        old_bar.hide()
        old_bar.setFixedHeight(0)

    def _resolve_database_path(self) -> Path | None:
        """Return the open SQLite database path when the app has one.

        Returns:

        - `Path | None`: Absolute path to the database file, or `None`.

        """
        db_manager = getattr(self, "db_manager", None)
        if db_manager is None:
            return None
        filename = getattr(db_manager, "_db_filename", None)
        if not filename:
            return None
        return Path(str(filename)).expanduser()

    def _setup_reveal_database_action(self) -> None:
        """Add File → Show database in folder for tracker apps with SQLite."""
        if not hasattr(self, "db_manager"):
            return
        menu_file = getattr(self, "menuFile", None)
        if menu_file is None:
            return
        menu = cast("QMenu", menu_file)
        action = QAction("Show database in folder", cast("QWidget", self))
        action.setObjectName("actionShowDatabaseInFolder")
        action.triggered.connect(self.on_reveal_database)
        menu.insertAction(self.actionExit, action)
        set_action_text_with_emoji_icon(action, "📂 Show database in folder")

    def _setup_window_size_and_position(self, *, standard_width: int = 1920) -> None:
        """Set window size and position based on screen resolution and characteristics.

        Args:

        - `standard_width` (`int`): Reference width used to decide between

        `showMaximized` and a fixed layout. Defaults to `1920`.

        """
        apply_app_window_size_and_position(cast("QWidget", self), standard_width=standard_width)

    def _show_placed_window(self, *, standard_width: int = 1920) -> None:
        """Show the window, then place or maximize it on the screen under the cursor."""
        widget = cast("QWidget", self)
        widget.show()
        apply_app_window_size_and_position(widget, standard_width=standard_width)

    def _validate_database_connection(self) -> bool:
        """Validate that database connection is available and open.

        Returns:

        - `bool`: `True` if database connection is valid, `False` otherwise.

        """
        if not getattr(self, "db_manager", None):
            logger.info("Database manager is None")
            return False

        if not self.db_manager.is_database_open():
            logger.warning("Database connection is not open")
            return False

        return True


class _MaximizeOnFirstShowFilter(QObject):
    """Maximize after the first `Show` so Windows maps the HWND on the target screen."""

    def __init__(self, widget: QWidget) -> None:
        super().__init__(widget)
        self._widget = widget

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        widget = self._widget
        if watched is widget and event.type() == QEvent.Type.Show:
            QTimer.singleShot(0, lambda w=widget: _maximize_when_mapped(w))
            widget.removeEventFilter(self)
            self.deleteLater()
        return False


class _RestoreFromMaximizeFilter(QObject):
    """Keep the title bar on-screen after Restore from a maximize pin."""

    def __init__(self, widget: QWidget, *, standard_width: int) -> None:
        super().__init__(widget)
        self._widget = widget
        self._standard_width = standard_width

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        widget = self._widget
        if watched is not widget or event.type() != QEvent.Type.WindowStateChange:
            return False
        if not isValid(widget) or widget.isMinimized() or widget.isMaximized() or widget.isFullScreen():
            return False
        old_state = event.oldState() if isinstance(event, QWindowStateChangeEvent) else Qt.WindowState.WindowNoState
        if not (old_state & Qt.WindowState.WindowMaximized):
            return False
        if not window_frame_escapes_work_area(widget.frameGeometry(), _widget_work_area(widget)):
            return False
        apply_restored_app_window_geometry(widget, standard_width=self._standard_width)
        return False

    def set_standard_width(self, standard_width: int) -> None:
        """Remember the width used to compute restore geometry."""
        self._standard_width = standard_width


class _WindowPlacement(ctypes.Structure):
    """Win32 `WINDOWPLACEMENT` used to seed restore geometry."""

    _fields_ = (
        ("length", wintypes.UINT),
        ("flags", wintypes.UINT),
        ("showCmd", wintypes.UINT),
        ("ptMinPosition", wintypes.POINT),
        ("ptMaxPosition", wintypes.POINT),
        ("rcNormalPosition", wintypes.RECT),
    )


def apply_app_window_size_and_position(widget: QWidget, *, standard_width: int = 1920) -> None:
    """Set widget size and position like food/finance/habits main Windows.

    On a standard-aspect work area, maximize. On ultrawide screens, fit a
    `standard_width` window into the available geometry and center it
    horizontally. Uses the screen under the cursor so a scaled or secondary
    display does not pin the window to the left.

    `showMaximized()` on a hidden window often opens as a normal window on the
    primary monitor. Pin the client rect to the target screen first, and only
    maximize after the native window is mapped.

    That pin is the full work area, so Windows restore would place the title
    bar above the screen. A `WindowStateChange` filter snaps the frame back.

    """
    _install_restore_from_maximize_filter(widget, standard_width=standard_width)
    screen = QGuiApplication.screenAt(QCursor.pos()) or widget.screen() or QApplication.primaryScreen()
    if screen is None:
        return
    if isinstance(screen, QScreen):
        widget.setScreen(screen)
    available = screen.availableGeometry()
    left, top, right, bottom = window_frame_margins(widget)
    target = compute_app_window_geometry(
        available,
        standard_width=standard_width,
        frame_left=left,
        frame_top=top,
        frame_right=right,
        frame_bottom=bottom,
    )
    if target is None:
        widget.setGeometry(compute_maximize_pin_geometry(available))
        if widget.isVisible():
            QTimer.singleShot(0, lambda w=widget: _maximize_when_mapped(w))
        else:
            _install_maximize_on_first_show(widget)
        return
    widget.setWindowState(widget.windowState() & ~Qt.WindowState.WindowMaximized)
    widget.setGeometry(target)


def apply_restored_app_window_geometry(widget: QWidget, *, standard_width: int = 1920) -> None:
    """Place a restored window so its title bar stays inside the work area."""
    available = _widget_work_area(widget)
    if available.width() <= 0 or available.height() <= 0:
        return
    left, top, right, bottom = window_frame_margins(widget)
    widget.setGeometry(
        compute_restore_window_geometry(
            available,
            standard_width=standard_width,
            frame_left=left,
            frame_top=top,
            frame_right=right,
            frame_bottom=bottom,
        ),
    )


def compute_app_window_geometry(
    available: QRect,
    *,
    standard_width: int = 1920,
    frame_left: int = 0,
    frame_top: int = 0,
    frame_right: int = 0,
    frame_bottom: int = 0,
) -> QRect | None:
    """Return a centered client rect, or `None` when the window should maximize.

    `setGeometry` is the client area, so `frame_*` must reserve the title bar
    and borders. Otherwise the caption buttons sit above the work area.

    Args:

    - `available` (`QRect`): Work area of the target screen (excludes the taskbar).
    - `standard_width` (`int`): Preferred window width on ultrawide screens.
      Defaults to `1920`.
    - `frame_left` / `frame_top` / `frame_right` / `frame_bottom` (`int`):
      Window-frame extents in logical pixels.

    Returns:

    - `QRect | None`: Client geometry in global logical coordinates, or `None`
      to maximize.

    """
    if available.width() <= 0 or available.height() <= 0:
        return None

    aspect_ratio = available.width() / available.height()
    # Standard / near-standard screens (incl. scaled 1080p under 1920 logical px)
    # open maximized so the frame fills the work area without side gaps.
    if aspect_ratio <= _STANDARD_ASPECT_RATIO:
        return None

    inner_width = max(1, available.width() - max(0, frame_left) - max(0, frame_right))
    inner_height = max(1, available.height() - max(0, frame_top) - max(0, frame_bottom))
    window_width = min(standard_width, inner_width)
    x = available.x() + max(0, frame_left) + (inner_width - window_width) // 2
    y = available.y() + max(0, frame_top)
    return QRect(x, y, window_width, inner_height)


def compute_maximize_pin_geometry(
    available: QRect,
    *,
    frame_left: int = 0,
    frame_top: int = 0,
    frame_right: int = 0,
    frame_bottom: int = 0,
) -> QRect:
    """Return the work area used to map the HWND onto the target screen.

    Insetting this rect by the window frame caused side gaps after maximize.
    Windows may warn about `setGeometry`; that message is ignored.

    Args:

    - `available` (`QRect`): Work area of the target screen (excludes the taskbar).
    - `frame_left` / `frame_top` / `frame_right` / `frame_bottom` (`int`):
      Unused; kept so older callers still type-check.

    Returns:

    - `QRect`: Client geometry in global logical coordinates.

    """
    _ = (frame_left, frame_top, frame_right, frame_bottom)
    return QRect(available)


def compute_restore_window_geometry(
    available: QRect,
    *,
    standard_width: int = 1920,
    frame_left: int = 0,
    frame_top: int = 0,
    frame_right: int = 0,
    frame_bottom: int = 0,
) -> QRect:
    """Return a client rect that keeps the window frame inside the work area.

    On screens that open maximized, restore still needs a normal size: the
    inner work area after reserving the title bar and borders.

    Args:

    - `available` (`QRect`): Work area of the target screen (excludes the taskbar).
    - `standard_width` (`int`): Preferred window width used on ultrawide screens.
      Defaults to `1920`.
    - `frame_left` / `frame_top` / `frame_right` / `frame_bottom` (`int`):
      Window-frame extents in logical pixels.

    Returns:

    - `QRect`: Client geometry in global logical coordinates.

    """
    target = compute_app_window_geometry(
        available,
        standard_width=standard_width,
        frame_left=frame_left,
        frame_top=frame_top,
        frame_right=frame_right,
        frame_bottom=frame_bottom,
    )
    if target is not None:
        return target
    inner_width = max(1, available.width() - max(0, frame_left) - max(0, frame_right))
    inner_height = max(1, available.height() - max(0, frame_top) - max(0, frame_bottom))
    return QRect(
        available.x() + max(0, frame_left),
        available.y() + max(0, frame_top),
        inner_width,
        inner_height,
    )


def inset_restore_frame_rect(
    left: int,
    top: int,
    right: int,
    bottom: int,
    *,
    frame_x: int,
    title: int,
    frame_y: int,
) -> tuple[int, int, int, int] | None:
    """Inset a Win32 restore frame so the caption stays inside the work area.

    Args:

    - `left` / `top` / `right` / `bottom` (`int`): Current restore frame
      (`WINDOWPLACEMENT.rcNormalPosition`).
    - `frame_x` (`int`): Left/right border thickness in native pixels.
    - `title` (`int`): Title-bar height in native pixels.
    - `frame_y` (`int`): Bottom border thickness in native pixels.

    Returns:

    - `tuple[int, int, int, int] | None`: Inset `(left, top, right, bottom)`,
      or `None` when the rect is too small to inset.

    """
    if right - left <= frame_x * 2 or bottom - top <= title + frame_y:
        return None
    return (left + frame_x, top + title, right - frame_x, bottom - frame_y)


def resolve_window_menu_bar(window: QWidget) -> QMenuBar | None:
    """Return the visible app menu bar, including the tab-row corner bar.

    Generated UI files assign `self.menuBar` to a `QMenuBar`, which shadows
    `QMainWindow.menuBar()`.

    """
    tab_widget = getattr(window, "tabWidget", None)
    if isinstance(tab_widget, QTabWidget):
        corner = tab_widget.cornerWidget(Qt.Corner.TopLeftCorner)
        if corner is not None:
            children = corner.findChildren(QMenuBar)
            if children:
                return children[0]
    menu_bar = getattr(window, "menuBar", None)
    if isinstance(menu_bar, QMenuBar):
        return menu_bar
    if callable(menu_bar):
        resolved = menu_bar()
        if isinstance(resolved, QMenuBar):
            return resolved
    return None


def window_frame_escapes_work_area(frame: QRect, available: QRect) -> bool:
    """Return whether the title bar has moved above or left of the work area.

    A few pixels of DWM shadow around a correctly placed window are ignored.

    Args:

    - `frame` (`QRect`): Outer window rectangle including the title bar.
    - `available` (`QRect`): Work area of the target screen (excludes the taskbar).

    Returns:

    - `bool`: `True` when Restore would hide the caption buttons.

    """
    if available.width() <= 0 or available.height() <= 0:
        return False
    return frame.top() < available.top() - _RESTORE_SNAP_SLACK or frame.left() < available.left() - _RESTORE_SNAP_SLACK


def window_frame_margins(widget: QWidget) -> tuple[int, int, int, int]:
    """Return `(left, top, right, bottom)` window-frame extents in logical pixels.

    Uses the realized frame when the caption is already laid out. Otherwise
    estimates from the widget style so an unshown window still leaves room
    for Close / Maximize.

    """
    flags = widget.windowFlags()
    if flags & Qt.WindowType.FramelessWindowHint:
        return (0, 0, 0, 0)

    if not (widget.windowState() & Qt.WindowState.WindowMaximized):
        frame = widget.frameGeometry()
        client = widget.geometry()
        left = client.x() - frame.x()
        top = client.y() - frame.y()
        right = frame.right() - client.right()
        bottom = frame.bottom() - client.bottom()
        if top > 0:
            return (max(0, left), top, max(0, right), max(0, bottom))

    style = widget.style()
    title = style.pixelMetric(QStyle.PixelMetric.PM_TitleBarHeight, widget=widget)
    border = style.pixelMetric(QStyle.PixelMetric.PM_DefaultFrameWidth, widget=widget)
    if title <= 0:
        title = _FALLBACK_TITLE_BAR_HEIGHT
    border = max(border, 0)
    return (border, title, border, border)


def _install_maximize_on_first_show(widget: QWidget) -> None:
    """Run `showMaximized` on the next `Show` if it is not already scheduled."""
    if widget.findChildren(_MaximizeOnFirstShowFilter):
        return
    widget.installEventFilter(_MaximizeOnFirstShowFilter(widget))


def _install_restore_from_maximize_filter(widget: QWidget, *, standard_width: int) -> None:
    """Keep one restore-from-maximize filter on `widget`."""
    existing = widget.findChildren(_RestoreFromMaximizeFilter)
    if existing:
        existing[0].set_standard_width(standard_width)
        return
    widget.installEventFilter(_RestoreFromMaximizeFilter(widget, standard_width=standard_width))


def _maximize_when_mapped(widget: QWidget) -> None:
    """Maximize a window that is already visible on its pinned screen."""
    if not isValid(widget) or not widget.isVisible():
        return
    widget.showMaximized()
    _seed_windows_restore_geometry(widget)


def _seed_windows_restore_geometry(widget: QWidget) -> None:
    """Inset the Win32 restore rect so Restore keeps the title bar on-screen.

    Maximize pins the client to the full work area. Windows then remembers that
    as the normal geometry, so Restore places the caption above the work area.
    Adjust `WINDOWPLACEMENT.rcNormalPosition` in the same coordinate system.

    """
    if sys.platform != "win32" or not isValid(widget):
        return
    hwnd = int(widget.winId())
    if hwnd == 0:
        return

    user32 = ctypes.windll.user32
    placement = _WindowPlacement()
    placement.length = ctypes.sizeof(_WindowPlacement)
    if not user32.GetWindowPlacement(hwnd, ctypes.byref(placement)):
        return

    dpi = 96
    get_dpi = getattr(user32, "GetDpiForWindow", None)
    if callable(get_dpi):
        dpi = int(get_dpi(hwnd)) or 96
    metrics = getattr(user32, "GetSystemMetricsForDpi", None)
    if callable(metrics):
        caption = int(metrics(_SM_CYCAPTION, dpi))
        pad = int(metrics(_SM_CXPADDEDBORDER, dpi))
        frame_x = int(metrics(_SM_CXFRAME, dpi)) + pad
        frame_y = int(metrics(_SM_CYFRAME, dpi)) + pad
    else:
        caption = int(user32.GetSystemMetrics(_SM_CYCAPTION))
        pad = int(user32.GetSystemMetrics(_SM_CXPADDEDBORDER))
        frame_x = int(user32.GetSystemMetrics(_SM_CXFRAME)) + pad
        frame_y = int(user32.GetSystemMetrics(_SM_CYFRAME)) + pad

    inset = inset_restore_frame_rect(
        placement.rcNormalPosition.left,
        placement.rcNormalPosition.top,
        placement.rcNormalPosition.right,
        placement.rcNormalPosition.bottom,
        frame_x=frame_x,
        title=max(caption + pad, frame_y),
        frame_y=frame_y,
    )
    if inset is None:
        return
    placement.rcNormalPosition.left = inset[0]
    placement.rcNormalPosition.top = inset[1]
    placement.rcNormalPosition.right = inset[2]
    placement.rcNormalPosition.bottom = inset[3]
    placement.showCmd = _SW_SHOWMAXIMIZED
    user32.SetWindowPlacement(hwnd, ctypes.byref(placement))


def _widget_work_area(widget: QWidget) -> QRect:
    """Return the work area of the screen that currently owns `widget`."""
    screen = widget.screen() or QGuiApplication.screenAt(widget.geometry().center()) or QApplication.primaryScreen()
    if screen is None:
        return QRect()
    return screen.availableGeometry()


logger = logging.getLogger(__name__)

_STANDARD_ASPECT_RATIO = 2.0
_FALLBACK_TITLE_BAR_HEIGHT = 32
_RESTORE_SNAP_SLACK = 16
_SW_SHOWMAXIMIZED = 3
_SM_CXFRAME = 32
_SM_CYCAPTION = 4
_SM_CYFRAME = 33
_SM_CXPADDEDBORDER = 92
