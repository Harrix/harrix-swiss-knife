"""Main window module for Harrix Swiss Knife application.

Displays tray commands as icon cards (default) or classic list with output panel.
Search works in both view modes.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import QPoint, Qt, QTimer
from PySide6.QtGui import QAction, QCloseEvent, QFont, QResizeEvent, QShowEvent
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QTextEdit,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from harrix_swiss_knife.action_output_bus import ActionOutputBus

from harrix_swiss_knife.cli_menu import get_cli_copy_command, show_copy_cli_menu
from harrix_swiss_knife.keyboard_layout_search import command_matches_search
from harrix_swiss_knife.main_window_settings import load_main_window_icon_grid, save_main_window_icon_grid
from harrix_swiss_knife.qt_action_card_grid import CARD_GRID_CELL_HEIGHT, configure_action_card_grid
from harrix_swiss_knife.qt_emoji_icon import create_emoji_icon
from harrix_swiss_knife.win11_backdrop import SystemBackdrop, try_apply_system_backdrop


class MainWindow(QMainWindow):
    """Tray-click window with icon grid or classic list + output panel."""

    def __init__(self, menu: QMenu, *, output_bus: ActionOutputBus | None = None) -> None:
        """Initialize the main window from the tray menu structure.

        Args:

        - `menu` (`QMenu`): Tray menu whose actions are shown in the window.
        - `output_bus` (`ActionOutputBus | None`): Output bus for the classic list view.

        """
        super().__init__()

        self.setWindowTitle("Harrix Swiss Knife")
        self.resize(1024, 800)
        try_apply_system_backdrop(self, backdrop=SystemBackdrop.MICA)

        self._icon_grid_mode = load_main_window_icon_grid()
        self._sections: list[_CommandSection] = []
        self._all_actions: list[QAction] = []
        self.current_content = ""
        self._active_output_path: Path | None = None
        self._output_bus = output_bus

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(12, 12, 12, 12)
        root_layout.setSpacing(12)

        root_layout.addLayout(self._build_header_row())
        root_layout.addWidget(self._build_icon_mode_widget(), stretch=1)
        root_layout.addWidget(self._build_list_mode_widget(menu), stretch=1)
        self._build_sections_from_menu(menu)

        self._apply_view_mode()
        self._setup_window_size_and_position()

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        """Hide the window instead of closing the application."""
        event.ignore()
        self.hide()

    def focus_initial_input(self) -> None:
        """Focus the search field."""
        self.focus_search()

    def focus_search(self) -> None:
        """Move keyboard focus to the search field."""
        self._search_edit.setFocus(Qt.FocusReason.ActiveWindowFocusReason)
        self._search_edit.selectAll()

    def on_item_clicked(self, item: QListWidgetItem) -> None:
        """Handle click on a command in classic list mode."""
        if not item.flags() & Qt.ItemFlag.ItemIsSelectable:
            return

        action = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(action, QAction):
            action.trigger()

    def populate_list(self, actions: list[QAction], indent_level: int = 0) -> None:
        """Populate classic list widget with actions, handling submenus recursively."""
        for action in actions:
            if not action.text():
                continue

            item = QListWidgetItem()
            text = ("    " * indent_level) + action.text()
            item.setText(text)
            tooltip = action.toolTip()
            if tooltip:
                item.setToolTip(tooltip)
            if not action.icon().isNull():
                item.setIcon(action.icon())

            submenu = action.menu()
            if isinstance(submenu, QMenu):
                font = item.font()
                font.setBold(True)
                item.setFont(font)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
                self.list_widget.addItem(item)
                self.populate_list(submenu.actions(), indent_level + 1)
            else:
                item.setData(Qt.ItemDataRole.UserRole, action)
                self.list_widget.addItem(item)

    def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        """Refit icon grid heights when the window width changes."""
        super().resizeEvent(event)
        if self._icon_grid_mode:
            QTimer.singleShot(0, self._fit_visible_grids)

    def showEvent(self, event: QShowEvent) -> None:  # noqa: N802
        """Focus the primary input when the window is shown."""
        super().showEvent(event)
        QTimer.singleShot(0, self.focus_initial_input)

    def show_window(self) -> None:
        """Show the window."""
        self.show()

    def _add_action_item(self, grid: QListWidget, action: QAction) -> None:
        item = QListWidgetItem(action.text(), grid)
        item.setData(Qt.ItemDataRole.UserRole, action)
        item.setTextAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        tooltip = action.toolTip()
        if tooltip:
            item.setToolTip(tooltip)
        icon = action.icon()
        if not icon.isNull():
            item.setIcon(icon)
        grid.addItem(item)

    def _apply_icon_search(self, query: str) -> None:
        if not query:
            self._search_grid.hide()
            self._grouped_widget.show()
            QTimer.singleShot(0, self._fit_visible_grids)
            return

        self._grouped_widget.hide()
        self._search_grid.clear()
        for action in self._all_actions:
            if command_matches_search(action.text(), query):
                self._add_action_item(self._search_grid, action)
        self._search_grid.show()
        QTimer.singleShot(0, lambda: self._fit_grid_height(self._search_grid))

    def _apply_list_search(self, query: str) -> None:
        self.list_widget.clear()
        if not query:
            self.populate_list(self._menu.actions())
            return

        for action in self._all_actions:
            if command_matches_search(action.text(), query):
                item = QListWidgetItem(action.text())
                item.setData(Qt.ItemDataRole.UserRole, action)
                tooltip = action.toolTip()
                if tooltip:
                    item.setToolTip(tooltip)
                if not action.icon().isNull():
                    item.setIcon(action.icon())
                self.list_widget.addItem(item)

    def _apply_view_mode(self) -> None:
        self._icon_mode_widget.setVisible(self._icon_grid_mode)
        self._list_mode_widget.setVisible(not self._icon_grid_mode)
        if self._icon_grid_mode:
            QTimer.singleShot(0, self._fit_visible_grids)
        self._on_search_changed(self._search_edit.text())

    def _build_header_row(self) -> QHBoxLayout:
        header_row = QHBoxLayout()
        header_row.setSpacing(12)

        self._search_row_widget = QWidget()
        search_row = QHBoxLayout(self._search_row_widget)
        search_row.setContentsMargins(0, 0, 0, 0)
        search_row.setSpacing(8)

        search_icon = QLabel()
        search_icon.setPixmap(create_emoji_icon("🔍", 22).pixmap(22, 22))
        search_icon.setFixedSize(24, 24)
        search_row.addWidget(search_icon)

        self._search_edit = QLineEdit()
        self._search_edit.setPlaceholderText("Search commands…")
        self._search_edit.setClearButtonEnabled(False)
        self._search_edit.textChanged.connect(self._on_search_changed)
        search_row.addWidget(self._search_edit, stretch=1)

        self._clear_button = QToolButton()
        self._clear_button.setText("✕")
        self._clear_button.setToolTip("Clear search")
        self._clear_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._clear_button.setAutoRaise(True)
        self._clear_button.clicked.connect(self._search_edit.clear)
        self._clear_button.hide()
        search_row.addWidget(self._clear_button)

        header_row.addWidget(self._search_row_widget, stretch=1)

        self._view_mode_checkbox = QCheckBox("Icon view")
        self._view_mode_checkbox.setToolTip("Show commands as icons. Uncheck for classic list with output panel.")
        self._view_mode_checkbox.setChecked(self._icon_grid_mode)
        self._view_mode_checkbox.toggled.connect(lambda checked: self._on_view_mode_toggled(icon_grid=checked))
        header_row.addWidget(self._view_mode_checkbox)

        return header_row

    def _build_icon_mode_widget(self) -> QWidget:
        self._icon_mode_widget = QWidget()

        icon_layout = QVBoxLayout(self._icon_mode_widget)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.setSpacing(0)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        icon_layout.addWidget(self._scroll)

        self._content = QWidget()
        self._content_layout = QVBoxLayout(self._content)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(8)
        self._scroll.setWidget(self._content)

        self._grouped_widget = QWidget()
        self._grouped_layout = QVBoxLayout(self._grouped_widget)
        self._grouped_layout.setContentsMargins(0, 0, 0, 0)
        self._grouped_layout.setSpacing(12)
        self._grouped_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._content_layout.addWidget(self._grouped_widget)

        self._search_grid = QListWidget()
        configure_action_card_grid(self._search_grid)
        self._search_grid.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._search_grid.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._search_grid.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._search_grid.itemClicked.connect(self._on_icon_item_clicked)
        self._search_grid.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._search_grid.customContextMenuRequested.connect(
            lambda pos: self._on_grid_context_menu(self._search_grid, pos),
        )
        self._search_grid.hide()
        self._content_layout.addWidget(self._search_grid)

        return self._icon_mode_widget

    def _build_list_mode_widget(self, menu: QMenu) -> QWidget:
        self._menu = menu
        self._list_mode_widget = QWidget()
        list_layout = QHBoxLayout(self._list_mode_widget)
        list_layout.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter()
        list_layout.addWidget(splitter)

        self.list_widget = QListWidget()
        splitter.addWidget(self.list_widget)

        self.text_edit = QTextEdit()
        splitter.addWidget(self.text_edit)

        splitter.setSizes([300, 700])

        if self._output_bus is not None:
            self._output_bus.active_output_changed.connect(self._on_active_output_changed)
            self._output_bus.line_appended.connect(self._on_line_appended)
        else:
            self._set_placeholder("No action output yet")

        self.populate_list(menu.actions())
        self.list_widget.itemClicked.connect(self.on_item_clicked)
        self.list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self._on_list_context_menu)

        return self._list_mode_widget

    def _build_sections_from_menu(self, menu: QMenu) -> None:
        submenu_sections: list[tuple[str, list[QAction]]] = []
        top_level_actions: list[QAction] = []

        for action in menu.actions():
            if action.isSeparator() or not action.text():
                continue
            submenu = action.menu()
            if isinstance(submenu, QMenu):
                leaves = _collect_leaf_actions(submenu)
                if leaves:
                    submenu_sections.append((action.text(), leaves))
            else:
                top_level_actions.append(action)

        if top_level_actions:
            self._create_section("Main", top_level_actions)
        for title, actions in submenu_sections:
            self._create_section(title, actions)

    def _create_section(self, title: str, actions: list[QAction]) -> None:
        section_widget = QWidget()
        section_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        section_layout = QVBoxLayout(section_widget)
        section_layout.setContentsMargins(0, 0, 0, 0)
        section_layout.setSpacing(4)

        label = QLabel(title)
        font = QFont(label.font())
        font.setBold(True)
        font.setPointSize(font.pointSize() + 1)
        label.setFont(font)
        section_layout.addWidget(label)

        grid = QListWidget()
        configure_action_card_grid(grid)
        grid.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        grid.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        grid.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        grid.itemClicked.connect(self._on_icon_item_clicked)
        grid.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        grid.customContextMenuRequested.connect(lambda pos, g=grid: self._on_grid_context_menu(g, pos))

        for action in actions:
            self._add_action_item(grid, action)
            self._all_actions.append(action)

        section_layout.addWidget(grid)
        self._grouped_layout.addWidget(section_widget)
        self._sections.append(_CommandSection(title=title, actions=actions, label=label, grid=grid))
        QTimer.singleShot(0, lambda g=grid: self._fit_grid_height(g))

    def _fit_grid_height(self, grid: QListWidget) -> None:
        if not grid.isVisible():
            return
        if grid.count() == 0:
            grid.setFixedHeight(0)
            return

        grid.doItemsLayout()
        item_bottoms = [
            grid.visualItemRect(grid.item(index)).bottom()
            for index in range(grid.count())
            if grid.item(index) is not None
        ]
        content_height = max(item_bottoms, default=CARD_GRID_CELL_HEIGHT - 1) + 1
        grid.setFixedHeight(content_height + 4)

    def _fit_visible_grids(self) -> None:
        if self._search_grid.isVisible():
            self._fit_grid_height(self._search_grid)
            return
        for section in self._sections:
            if section.grid is not None and section.grid.isVisible():
                self._fit_grid_height(section.grid)

    def _on_active_output_changed(self, path_str: str) -> None:
        try:
            path = Path(path_str)
            self._active_output_path = path
            if path.exists():
                output_txt = path.read_text(encoding="utf8")
                self.text_edit.setPlainText(output_txt)
                self.current_content = output_txt
            else:
                self.text_edit.setPlainText("")
                self.current_content = ""
            self.text_edit.verticalScrollBar().setValue(self.text_edit.verticalScrollBar().maximum())
        except Exception as e:
            self._set_placeholder(f"File reading error: {e!s}")

    def _on_grid_context_menu(self, grid: QListWidget, pos: QPoint) -> None:
        """Show Copy CLI command when right-clicking a CLI-enabled card."""
        item = grid.itemAt(pos)
        if item is None:
            return

        action = item.data(Qt.ItemDataRole.UserRole)
        if not isinstance(action, QAction):
            return

        cli_copy_command = get_cli_copy_command(action)
        if cli_copy_command is None:
            return

        show_copy_cli_menu(
            parent=self,
            global_pos=grid.mapToGlobal(pos),
            cli_copy_command=cli_copy_command,
        )

    def _on_icon_item_clicked(self, item: QListWidgetItem) -> None:
        action = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(action, QAction):
            action.trigger()

    def _on_line_appended(self, path_str: str, line: str) -> None:
        if self._active_output_path is None:
            return
        if str(self._active_output_path.resolve()) != path_str:
            return
        self.text_edit.append(line)
        self.current_content = self.text_edit.toPlainText()
        self.text_edit.verticalScrollBar().setValue(self.text_edit.verticalScrollBar().maximum())

    def _on_list_context_menu(self, pos: QPoint) -> None:
        """Show Copy CLI command when right-clicking a CLI-enabled list item."""
        item = self.list_widget.itemAt(pos)
        if item is None:
            return

        action = item.data(Qt.ItemDataRole.UserRole)
        if not isinstance(action, QAction):
            return

        cli_copy_command = get_cli_copy_command(action)
        if cli_copy_command is None:
            return

        show_copy_cli_menu(
            parent=self,
            global_pos=self.list_widget.mapToGlobal(pos),
            cli_copy_command=cli_copy_command,
        )

    def _on_search_changed(self, text: str) -> None:
        query = text.strip()
        self._clear_button.setVisible(bool(text))

        if self._icon_grid_mode:
            self._apply_icon_search(query)
        else:
            self._apply_list_search(query)

    def _on_view_mode_toggled(self, *, icon_grid: bool) -> None:
        self._icon_grid_mode = icon_grid
        save_main_window_icon_grid(icon_grid=icon_grid)
        self._apply_view_mode()
        QTimer.singleShot(0, self.focus_initial_input)

    def _set_placeholder(self, placeholder: str) -> None:
        if placeholder != self.current_content:
            self.text_edit.setPlainText(placeholder)
            self.current_content = placeholder
            self.text_edit.verticalScrollBar().setValue(self.text_edit.verticalScrollBar().maximum())

    def _setup_window_size_and_position(self) -> None:
        """Set window size and position based on screen resolution and characteristics."""
        screen_geometry = QApplication.primaryScreen().geometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        aspect_ratio = screen_width / screen_height
        standard_aspect_ratio = 2.0
        is_standard_aspect = aspect_ratio <= standard_aspect_ratio

        standard_width = 1920
        if is_standard_aspect and screen_width >= standard_width:
            self.setWindowState(Qt.WindowState.WindowMaximized)
        else:
            title_bar_height = 30
            windows_task_bar_height = 48
            window_width = standard_width
            window_height = screen_height - title_bar_height - windows_task_bar_height
            screen_center = screen_geometry.center()
            self.setGeometry(
                screen_center.x() - window_width // 2,
                title_bar_height,
                window_width,
                window_height,
            )


@dataclass
class _CommandSection:
    """One visual block of command cards with a section title."""

    title: str
    actions: list[QAction]
    label: QLabel | None = None
    grid: QListWidget | None = None


def _collect_leaf_actions(menu: QMenu) -> list[QAction]:
    """Collect selectable leaf actions from a menu, flattening nested submenus."""
    leaves: list[QAction] = []
    for action in menu.actions():
        if action.isSeparator() or not action.text():
            continue
        submenu = action.menu()
        if isinstance(submenu, QMenu):
            leaves.extend(_collect_leaf_actions(submenu))
        else:
            leaves.append(action)
    return leaves
