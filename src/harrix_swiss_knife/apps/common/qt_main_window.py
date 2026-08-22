"""Shared helpers for app-level `QMainWindow` implementations.

Provides `AppWindowMixin` with methods that were previously duplicated in
`finance/main.py`, `fitness/main.py`, `food/main.py`, and `habits/main.py`:

- `_setup_window_size_and_position`
- `_place_menu_bar_on_tab_row`
- `_copy_table_selection_to_clipboard`
- `_validate_database_connection`
- `_handle_ctrl_c_for_tables`
- Exit / About menu actions
- Show database in folder (File menu)

"""

from __future__ import annotations

import logging
import tomllib
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar, cast

import harrix_pylib as h
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QMenu,
    QMenuBar,
    QSizePolicy,
    QTableView,
    QTabWidget,
    QWidget,
)

from harrix_swiss_knife.apps.common import message_box
from harrix_swiss_knife.apps.common.ui_helpers import reveal_in_file_explorer
from harrix_swiss_knife.qt_emoji_icon import apply_leading_emoji_icons

if TYPE_CHECKING:
    from PySide6.QtGui import QCloseEvent, QKeyEvent
    from PySide6.QtWidgets import QMainWindow


logger = logging.getLogger(__name__)

_STANDARD_ASPECT_RATIO = 2.0
_TITLE_BAR_HEIGHT = 30
_WINDOWS_TASK_BAR_HEIGHT = 48


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

    def _place_menu_bar_on_tab_row(self) -> None:
        """Put the main menu on the same row as tabs (left of the tab bar).

        Moves menus from the `QMainWindow` menu bar into a bold compact
        `QMenuBar` with a vertical separator, set as the `QTabWidget`
        top-left corner widget, then collapses the original menu bar row.

        """
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
        action = QAction("📂 Show database in folder", cast("QWidget", self))
        action.setObjectName("actionShowDatabaseInFolder")
        action.triggered.connect(self.on_reveal_database)
        menu.insertAction(self.actionExit, action)

    def _setup_window_size_and_position(self, *, standard_width: int = 1920) -> None:
        """Set window size and position based on screen resolution and characteristics.

        Args:

        - `standard_width` (`int`): Reference width used to decide between

        `showMaximized` and a fixed layout. Defaults to `1920`.

        """
        apply_app_window_size_and_position(cast("QWidget", self), standard_width=standard_width)

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


def apply_app_window_size_and_position(widget: QWidget, *, standard_width: int = 1920) -> None:
    """Set widget size and position like food/finance/habits main Windows.

    On a standard-aspect screen at least `standard_width` wide, maximize.
    Otherwise center a window of width `standard_width` and height equal to
    the screen height minus title bar and task bar.

    """
    screen = QApplication.primaryScreen()
    if screen is None:
        return
    screen_geometry = screen.geometry()
    screen_width = screen_geometry.width()
    screen_height = screen_geometry.height()

    aspect_ratio = screen_width / screen_height
    is_standard_aspect = aspect_ratio <= _STANDARD_ASPECT_RATIO

    if is_standard_aspect and screen_width >= standard_width:
        widget.showMaximized()
        return

    window_width = standard_width
    window_height = screen_height - _TITLE_BAR_HEIGHT - _WINDOWS_TASK_BAR_HEIGHT
    screen_center = screen_geometry.center()
    widget.setGeometry(
        screen_center.x() - window_width // 2,
        _TITLE_BAR_HEIGHT,
        window_width,
        window_height,
    )


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
