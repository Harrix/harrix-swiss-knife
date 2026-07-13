"""Main window module for Harrix Swiss Knife application.

Displays tray command picker as grouped icon cards with search.
"""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QPoint, Qt, QTimer
from PySide6.QtGui import QAction, QCloseEvent, QFont, QResizeEvent, QShowEvent
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QScrollArea,
    QSizePolicy,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife.cli_menu import get_cli_copy_command, show_copy_cli_menu
from harrix_swiss_knife.keyboard_layout_search import command_matches_search
from harrix_swiss_knife.qt_action_card_grid import CARD_GRID_CELL_HEIGHT, configure_action_card_grid
from harrix_swiss_knife.qt_emoji_icon import create_emoji_icon
from harrix_swiss_knife.win11_backdrop import SystemBackdrop, try_apply_system_backdrop


class MainWindow(QMainWindow):
    """Tray-click window: icon grid of commands with search filter."""

    def __init__(self, menu: QMenu) -> None:
        """Initialize the main window from the tray menu structure.

        Args:

        - `menu` (`QMenu`): Tray menu whose actions are shown as icon cards.

        """
        super().__init__()

        self.setWindowTitle("Harrix Swiss Knife")
        self.resize(1024, 800)
        try_apply_system_backdrop(self, backdrop=SystemBackdrop.MICA)

        self._sections: list[_CommandSection] = []
        self._all_actions: list[QAction] = []

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(12, 12, 12, 12)
        root_layout.setSpacing(12)

        root_layout.addLayout(self._build_search_bar())

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        root_layout.addWidget(self._scroll, stretch=1)

        self._content = QWidget()
        self._content_layout = QVBoxLayout(self._content)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(8)
        self._scroll.setWidget(self._content)

        self._grouped_widget = QWidget()
        self._grouped_layout = QVBoxLayout(self._grouped_widget)
        self._grouped_layout.setContentsMargins(0, 0, 0, 0)
        self._grouped_layout.setSpacing(12)
        self._content_layout.addWidget(self._grouped_widget)

        self._search_grid = QListWidget()
        configure_action_card_grid(self._search_grid)
        self._search_grid.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._search_grid.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._search_grid.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._search_grid.itemClicked.connect(self._on_item_clicked)
        self._search_grid.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._search_grid.customContextMenuRequested.connect(
            lambda pos: self._on_grid_context_menu(self._search_grid, pos),
        )
        self._search_grid.hide()
        self._content_layout.addWidget(self._search_grid)

        self._build_sections_from_menu(menu)
        self._setup_window_size_and_position()

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        """Hide the window instead of closing the application."""
        event.ignore()
        self.hide()

    def focus_search(self) -> None:
        """Move keyboard focus to the search field."""
        self._search_edit.setFocus(Qt.FocusReason.ActiveWindowFocusReason)
        self._search_edit.selectAll()

    def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        """Refit icon grid heights when the window width changes."""
        super().resizeEvent(event)
        QTimer.singleShot(0, self._fit_visible_grids)

    def showEvent(self, event: QShowEvent) -> None:  # noqa: N802
        """Focus the search field when the window is shown."""
        super().showEvent(event)
        QTimer.singleShot(0, self.focus_search)

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

    def _build_search_bar(self) -> QHBoxLayout:
        search_row = QHBoxLayout()
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

        return search_row

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
        grid.itemClicked.connect(self._on_item_clicked)
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
        grid.doItemsLayout()
        content_height = grid.contentsSize().height()
        padding = 8
        min_height = CARD_GRID_CELL_HEIGHT
        grid.setFixedHeight(max(content_height + padding, min_height if grid.count() else 0))

    def _fit_visible_grids(self) -> None:
        if self._search_grid.isVisible():
            self._fit_grid_height(self._search_grid)
            return
        for section in self._sections:
            if section.grid is not None and section.grid.isVisible():
                self._fit_grid_height(section.grid)

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

    def _on_item_clicked(self, item: QListWidgetItem) -> None:
        action = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(action, QAction):
            action.trigger()

    def _on_search_changed(self, text: str) -> None:
        query = text.strip()
        self._clear_button.setVisible(bool(text))

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
