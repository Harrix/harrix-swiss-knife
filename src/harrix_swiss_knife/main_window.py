"""Main window module for Harrix Swiss Knife application.

Displays tray commands as a list on the left and action cards on the right.
Search filters both panes.

"""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QEvent, QObject, QPoint, Qt, QTimer
from PySide6.QtGui import QAction, QCloseEvent, QCursor, QResizeEvent, QShowEvent
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
    QSplitter,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife.action_usage import RECENT_GUI_ACTIONS_LIMIT, list_recent_gui_action_names
from harrix_swiss_knife.apps.common.qt_main_window import apply_app_window_size_and_position
from harrix_swiss_knife.cli_menu import get_action_identity_parts, show_action_item_context_menu
from harrix_swiss_knife.keyboard_layout_search import command_matches_search
from harrix_swiss_knife.qt_command_section import (
    apply_opaque_white,
    create_command_section,
    fit_icon_grid_height,
    prepare_icon_grid,
)
from harrix_swiss_knife.qt_described_choice_cards import (
    add_described_action_card,
    configure_described_choice_card_grid,
    sync_described_choice_card_grid,
)
from harrix_swiss_knife.qt_emoji_icon import create_emoji_icon
from harrix_swiss_knife.win11_backdrop import SystemBackdrop, try_apply_system_backdrop


class MainWindow(QMainWindow):
    """Tray-click window with a command list and action cards."""

    def __init__(self, menu: QMenu) -> None:
        """Initialize the main window from the tray menu structure.

        Args:

        - `menu` (`QMenu`): Tray menu whose actions are shown in the window.

        """
        super().__init__()

        self.setWindowTitle("Harrix Swiss Knife")
        try_apply_system_backdrop(self, backdrop=SystemBackdrop.MICA)

        self._sections: list[_CommandSection] = []
        self._recent_section: _CommandSection | None = None
        self._all_actions: list[QAction] = []

        central_widget = QWidget()
        apply_opaque_white(central_widget)
        self.setCentralWidget(central_widget)
        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(12, 12, 12, 12)
        root_layout.setSpacing(12)

        root_layout.addLayout(self._build_header_row())
        root_layout.addWidget(self._build_body_widget(), stretch=1)
        self._build_sections_from_menu(menu)
        self._populate_list_from_sections()
        self._setup_window_size_and_position()

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        """Hide the window instead of closing the application."""
        event.ignore()
        self.hide()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Forward wheel events from icon grids to the outer scroll area."""
        if event.type() == QEvent.Type.Wheel and self._is_icon_grid_wheel_target(watched):
            QApplication.sendEvent(self._scroll.viewport(), event)
            return True
        return super().eventFilter(watched, event)

    def focus_initial_input(self) -> None:
        """Focus the search field."""
        self.focus_search()

    def focus_search(self) -> None:
        """Move keyboard focus to the search field."""
        self._search_edit.setFocus(Qt.FocusReason.ActiveWindowFocusReason)
        self._search_edit.selectAll()

    def on_item_clicked(self, item: QListWidgetItem) -> None:
        """Handle click on a command in the list pane."""
        if not item.flags() & Qt.ItemFlag.ItemIsSelectable:
            return

        action = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(action, QAction):
            self._run_listed_action(action)

    def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        """Refit icon grid heights when the window width changes."""
        super().resizeEvent(event)
        QTimer.singleShot(0, self._fit_visible_grids)

    def showEvent(self, event: QShowEvent) -> None:  # noqa: N802
        """Refresh Recent and focus the primary input when the window is shown."""
        super().showEvent(event)
        self._refresh_recent_section()
        QTimer.singleShot(0, self.focus_initial_input)

    def show_window(self) -> None:
        """Show the window."""
        self.show()

    def _action_matches_search(self, action: QAction, query: str) -> bool:
        """Match title or description in search."""
        if command_matches_search(action.text(), query):
            return True
        description = getattr(action, "action_description", "") or ""
        return bool(description) and command_matches_search(description, query)

    def _add_action_item(self, grid: QListWidget, action: QAction) -> None:
        icon_name = getattr(action, "icon_name", "") or ""
        description = getattr(action, "action_description", "") or ""
        add_described_action_card(
            grid,
            icon=icon_name,
            title=action.text(),
            description=description,
            user_data=action,
            on_select=lambda listed=action: self._run_listed_action(listed),
            on_context_menu=self._on_card_context_menu,
        )

    def _add_list_action_item(self, action: QAction, *, indent_level: int = 0) -> None:
        item = QListWidgetItem(("    " * indent_level) + action.text())
        item.setData(Qt.ItemDataRole.UserRole, action)
        tooltip = action.toolTip()
        if tooltip:
            item.setToolTip(tooltip)
        if not action.icon().isNull():
            item.setIcon(action.icon())
        self.list_widget.addItem(item)

    def _add_list_section_header(self, title: str) -> None:
        item = QListWidgetItem(title)
        font = item.font()
        font.setBold(True)
        item.setFont(font)
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
        self.list_widget.addItem(item)

    def _apply_card_search(self, query: str) -> None:
        if not query:
            self._search_grid.hide()
            self._grouped_widget.show()
            QTimer.singleShot(0, self._fit_visible_grids)
            return

        self._grouped_widget.hide()
        self._search_grid.clear()
        for action in self._all_actions:
            if self._action_matches_search(action, query):
                self._add_action_item(self._search_grid, action)
        self._search_grid.show()
        QTimer.singleShot(0, lambda: self._fit_grid_height(self._search_grid))

    def _apply_list_search(self, query: str) -> None:
        if not query:
            self._populate_list_from_sections()
            return

        self.list_widget.clear()
        for action in self._all_actions:
            if self._action_matches_search(action, query):
                self._add_list_action_item(action)

    def _build_body_widget(self) -> QWidget:
        body = QWidget()
        apply_opaque_white(body)
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter()
        splitter.addWidget(self._build_list_pane())
        splitter.addWidget(self._build_cards_pane())
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([300, 700])
        body_layout.addWidget(splitter)
        return body

    def _build_cards_pane(self) -> QWidget:
        cards_pane = QWidget()
        apply_opaque_white(cards_pane)

        cards_layout = QVBoxLayout(cards_pane)
        cards_layout.setContentsMargins(0, 0, 0, 0)
        cards_layout.setSpacing(0)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        apply_opaque_white(self._scroll)
        apply_opaque_white(self._scroll.viewport())
        cards_layout.addWidget(self._scroll)

        self._content = QWidget()
        apply_opaque_white(self._content)
        self._content_layout = QVBoxLayout(self._content)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(8)
        self._content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._scroll.setWidget(self._content)

        self._grouped_widget = QWidget()
        apply_opaque_white(self._grouped_widget)
        self._grouped_layout = QVBoxLayout(self._grouped_widget)
        self._grouped_layout.setContentsMargins(0, 0, 0, 0)
        self._grouped_layout.setSpacing(12)
        self._grouped_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._content_layout.addWidget(self._grouped_widget, 0, Qt.AlignmentFlag.AlignTop)

        self._search_grid = QListWidget()
        configure_described_choice_card_grid(self._search_grid)
        prepare_icon_grid(self._search_grid, event_filter=self)
        self._search_grid.itemClicked.connect(self._on_icon_item_clicked)
        self._search_grid.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._search_grid.customContextMenuRequested.connect(
            lambda pos: self._on_grid_context_menu(self._search_grid, pos),
        )
        self._search_grid.hide()
        self._content_layout.addWidget(self._search_grid, 0, Qt.AlignmentFlag.AlignTop)
        self._content_layout.addStretch(1)

        return cards_pane

    def _build_header_row(self) -> QHBoxLayout:
        header_row = QHBoxLayout()
        header_row.setSpacing(8)

        search_icon = QLabel()
        search_icon.setPixmap(create_emoji_icon("🔍", 22).pixmap(22, 22))
        search_icon.setFixedSize(24, 24)
        header_row.addWidget(search_icon)

        self._search_edit = QLineEdit()
        self._search_edit.setPlaceholderText("Search commands…")
        self._search_edit.setClearButtonEnabled(False)
        self._search_edit.textChanged.connect(self._on_search_changed)
        header_row.addWidget(self._search_edit, stretch=1)

        self._clear_button = QToolButton()
        self._clear_button.setText("✕")
        self._clear_button.setToolTip("Clear search")
        self._clear_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._clear_button.setAutoRaise(True)
        self._clear_button.clicked.connect(self._search_edit.clear)
        self._clear_button.hide()
        header_row.addWidget(self._clear_button)

        return header_row

    def _build_list_pane(self) -> QWidget:
        list_pane = QWidget()
        apply_opaque_white(list_pane)
        list_layout = QVBoxLayout(list_pane)
        list_layout.setContentsMargins(0, 0, 0, 0)

        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self.on_item_clicked)
        self.list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self._on_list_context_menu)
        list_layout.addWidget(self.list_widget)
        return list_pane

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
        self._recent_section = self._create_section(
            "Recent",
            self._recent_gui_actions(),
            track_in_all=False,
            insert_at=0,
        )

    def _create_section(
        self,
        title: str,
        actions: list[QAction],
        *,
        track_in_all: bool = True,
        insert_at: int | None = None,
    ) -> _CommandSection:
        section_widget, label, section_layout = create_command_section(title=title)

        grid = QListWidget()
        configure_described_choice_card_grid(grid)
        prepare_icon_grid(grid, event_filter=self)
        grid.itemClicked.connect(self._on_icon_item_clicked)
        grid.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        grid.customContextMenuRequested.connect(lambda pos, g=grid: self._on_grid_context_menu(g, pos))

        for action in actions:
            self._add_action_item(grid, action)
            if track_in_all:
                self._all_actions.append(action)

        section_layout.addWidget(grid)
        section = _CommandSection(title=title, actions=actions, label=label, grid=grid, widget=section_widget)
        if insert_at is None:
            self._grouped_layout.addWidget(section_widget)
            self._sections.append(section)
        else:
            self._grouped_layout.insertWidget(insert_at, section_widget)
            self._sections.insert(insert_at, section)
        if not actions:
            section_widget.hide()
        QTimer.singleShot(0, lambda g=grid: self._fit_grid_height(g))
        return section

    def _fit_grid_height(self, grid: QListWidget) -> None:
        """Rescale described cards to the viewport, then fit section height."""
        sync_described_choice_card_grid(grid)
        fit_icon_grid_height(grid)

    def _fit_visible_grids(self) -> None:
        if self._search_grid.isVisible():
            self._fit_grid_height(self._search_grid)
            return
        for section in self._sections:
            if section.grid is not None and section.grid.isVisible():
                self._fit_grid_height(section.grid)

    def _is_icon_grid_wheel_target(self, watched: QObject) -> bool:
        grids = [self._search_grid]
        grids.extend(section.grid for section in self._sections if section.grid is not None)
        return any(watched is grid or watched is grid.viewport() for grid in grids)

    def _on_card_context_menu(self, user_data: object, global_pos: QPoint) -> None:
        """Show copy name/class/path for the action bound to a command card."""
        if isinstance(user_data, QAction):
            show_action_item_context_menu(parent=self, global_pos=global_pos, action=user_data)

    def _on_grid_context_menu(self, grid: QListWidget, pos: QPoint) -> None:
        """Show copy name/class/path and CLI command for the card under the cursor."""
        self._show_list_item_context_menu(grid, pos)

    def _on_icon_item_clicked(self, item: QListWidgetItem) -> None:
        action = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(action, QAction):
            self._run_listed_action(action)

    def _on_list_context_menu(self, pos: QPoint) -> None:
        """Show copy name/class/path and CLI command for the list item under the cursor."""
        self._show_list_item_context_menu(self.list_widget, pos)

    def _on_search_changed(self, text: str) -> None:
        query = text.strip()
        self._clear_button.setVisible(bool(text))
        self._apply_list_search(query)
        self._apply_card_search(query)

    def _populate_list_from_sections(self) -> None:
        """Fill the list using the same Recent / Main / submenu order as the cards."""
        self.list_widget.clear()
        for section in self._sections:
            if not section.actions:
                continue
            self._add_list_section_header(section.title)
            for action in section.actions:
                self._add_list_action_item(action, indent_level=1)

    def _recent_gui_actions(self) -> list[QAction]:
        """Return up to six catalog actions last used from the GUI, newest first."""
        by_class: dict[str, QAction] = {}
        for action in self._all_actions:
            parts = get_action_identity_parts(action)
            if parts is not None:
                by_class[parts.class_name] = action
        return [
            by_class[name] for name in list_recent_gui_action_names(limit=RECENT_GUI_ACTIONS_LIMIT) if name in by_class
        ]

    def _refresh_recent_section(self) -> None:
        """Rebuild the Recent section from the latest GUI usage timestamps."""
        section = self._recent_section
        if section is None or section.grid is None:
            return
        actions = self._recent_gui_actions()
        section.actions = actions
        section.grid.clear()
        for action in actions:
            self._add_action_item(section.grid, action)
        if section.widget is not None:
            section.widget.setVisible(bool(actions))
        if section.grid.isVisible():
            QTimer.singleShot(0, lambda grid=section.grid: self._fit_grid_height(grid))
        if not self._search_edit.text().strip():
            self._populate_list_from_sections()

    def _run_listed_action(self, action: QAction) -> None:
        """Run a catalog action and refresh the Recent section."""
        action.trigger()
        self._refresh_recent_section()

    def _setup_window_size_and_position(self) -> None:
        """Set window size and position based on screen resolution and characteristics."""
        apply_app_window_size_and_position(self)

    def _show_list_item_context_menu(self, list_widget: QListWidget, pos: QPoint) -> None:
        """Show the action copy menu for the list item at `pos`."""
        item = list_widget.itemAt(pos)
        if item is None:
            return
        action = item.data(Qt.ItemDataRole.UserRole)
        if not isinstance(action, QAction):
            return
        show_action_item_context_menu(
            parent=self,
            global_pos=QCursor.pos(),
            action=action,
        )


@dataclass
class _CommandSection:
    """One visual block of command cards with a section title."""

    title: str
    actions: list[QAction]
    label: QLabel | None = None
    grid: QListWidget | None = None
    widget: QWidget | None = None


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
