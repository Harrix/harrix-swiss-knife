---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `main_window.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `MainWindow`](#%EF%B8%8F-class-mainwindow)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `closeEvent`](#%EF%B8%8F-method-closeevent)
  - [⚙️ Method `eventFilter`](#%EF%B8%8F-method-eventfilter)
  - [⚙️ Method `focus_initial_input`](#%EF%B8%8F-method-focus_initial_input)
  - [⚙️ Method `focus_search`](#%EF%B8%8F-method-focus_search)
  - [⚙️ Method `on_item_clicked`](#%EF%B8%8F-method-on_item_clicked)
  - [⚙️ Method `resizeEvent`](#%EF%B8%8F-method-resizeevent)
  - [⚙️ Method `showEvent`](#%EF%B8%8F-method-showevent)
  - [⚙️ Method `show_window`](#%EF%B8%8F-method-show_window)

</details>

## 🏛️ Class `MainWindow`

```python
class MainWindow(QMainWindow)
```

Tray-click window with a command list and action cards.

<details>
<summary>Code:</summary>

```python
class MainWindow(QMainWindow):

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
        self._sort_mode = get_main_window_sort_mode()

        central_widget = QWidget()
        apply_opaque_white(central_widget)
        self.setCentralWidget(central_widget)
        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(12, 12, 12, 12)
        root_layout.setSpacing(12)

        root_layout.addLayout(self._build_header_row())
        root_layout.addWidget(self._build_body_widget(), stretch=1)
        root_layout.addLayout(self._build_footer_row())
        self._build_sections_from_menu(menu)
        self._sync_sort_combo()
        self._apply_catalog_view()
        self._setup_window_size_and_position()

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        """Hide the window instead of closing the application."""
        event.ignore()
        self.hide()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Forward wheel events from icon grids and refit Recent when the cards pane resizes."""
        if event.type() == QEvent.Type.Resize and watched is self._scroll.viewport():
            QTimer.singleShot(0, self._on_cards_layout_changed)
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
        """Refit Recent and icon grid heights when the window width changes."""
        super().resizeEvent(event)
        QTimer.singleShot(0, self._on_cards_layout_changed)

    def showEvent(self, event: QShowEvent) -> None:  # noqa: N802
        """Refresh Recent and focus the primary input when the window is shown."""
        super().showEvent(event)
        QTimer.singleShot(0, self._on_cards_layout_changed)
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

    def _add_action_item(self, grid: QListWidget, action: QAction, *, show_added_at: bool = False) -> None:
        icon_name = getattr(action, "icon_name", "") or ""
        description = getattr(action, "action_description", "") or ""
        if show_added_at:
            parts = get_action_identity_parts(action)
            if parts is not None:
                date_text = format_added_at_date(added_at_for(parts.class_name))
                if date_text:
                    added_line = f"Added {date_text}"
                    description = f"{description}\n{added_line}" if description else added_line
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
        newest = self._is_newest_sort()
        if not query and not newest:
            self._search_grid.hide()
            self._grouped_widget.show()
            QTimer.singleShot(0, self._on_cards_layout_changed)
            return

        self._grouped_widget.hide()
        self._search_grid.clear()
        for action in self._ordered_catalog_actions(query):
            self._add_action_item(self._search_grid, action, show_added_at=newest)
        self._search_grid.show()
        QTimer.singleShot(0, lambda: self._fit_grid_height(self._search_grid))

    def _apply_catalog_view(self) -> None:
        """Refresh list and cards for the current search text and sort mode."""
        query = self._search_edit.text().strip()
        self._apply_list_search(query)
        self._apply_card_search(query)

    def _apply_list_search(self, query: str) -> None:
        if not query and not self._is_newest_sort():
            self._populate_list_from_sections()
            return

        self.list_widget.clear()
        for action in self._ordered_catalog_actions(query):
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
        self._scroll.viewport().installEventFilter(self)
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

    def _build_footer_row(self) -> QHBoxLayout:
        footer_row = QHBoxLayout()
        self._startup_checkbox = QCheckBox("Show at program startup")
        self._startup_checkbox.setToolTip("Open this window when Harrix Swiss Knife starts")
        self._startup_checkbox.setChecked(get_show_main_window_on_startup())
        self._startup_checkbox.toggled.connect(self._on_show_on_startup_toggled)
        footer_row.addWidget(self._startup_checkbox)
        footer_row.addStretch(1)
        return footer_row

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

        self._sort_combo = QComboBox()
        self._sort_combo.addItem("Menu order", MAIN_WINDOW_SORT_MODE_MENU)
        self._sort_combo.addItem("Newest first", MAIN_WINDOW_SORT_MODE_NEWEST)
        self._sort_combo.setToolTip("Sort commands by menu structure or date added")
        self._sort_combo.currentIndexChanged.connect(self._on_sort_mode_changed)
        header_row.addWidget(self._sort_combo)

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
            show_in_list=False,
        )

    def _cards_row_width(self) -> int:
        """Return the catalog card-grid width, not the Recent grid's current contents."""
        for section in self._sections:
            if not section.show_in_list or section.grid is None or not section.grid.isVisible():
                continue
            width = section.grid.viewport().width()
            if width > 0:
                return width
        viewport_width = self._scroll.viewport().width()
        if viewport_width <= 0:
            return 0
        return max(1, viewport_width - 16)

    def _create_section(
        self,
        title: str,
        actions: list[QAction],
        *,
        track_in_all: bool = True,
        insert_at: int | None = None,
        show_in_list: bool = True,
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
        section = _CommandSection(
            title=title,
            actions=actions,
            label=label,
            grid=grid,
            widget=section_widget,
            show_in_list=show_in_list,
        )
        if insert_at is None:
            self._grouped_layout.addWidget(section_widget)
            self._sections.append(section)
        else:
            self._grouped_layout.insertWidget(insert_at, section_widget)
            self._sections.insert(insert_at, section)
        if not actions:
            section_widget.hide()
        if actions:
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

    def _is_newest_sort(self) -> bool:
        return self._sort_mode == MAIN_WINDOW_SORT_MODE_NEWEST

    def _on_card_context_menu(self, user_data: object, global_pos: QPoint) -> None:
        """Show copy name/class/path for the action bound to a command card."""
        if isinstance(user_data, QAction):
            show_action_item_context_menu(parent=self, global_pos=global_pos, action=user_data)

    def _on_cards_layout_changed(self) -> None:
        """Fit catalog cards first, then size Recent to that row width."""
        self._fit_visible_grids()
        if not self._is_newest_sort() and not self._search_edit.text().strip():
            self._refresh_recent_section()

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

    def _on_show_on_startup_toggled(self, checked: bool) -> None:  # noqa: FBT001
        """Persist the startup checkbox to `show_main_window_on_startup`."""
        try:
            set_show_main_window_on_startup(enabled=checked)
        except (OSError, TypeError, ValueError) as exc:
            self._startup_checkbox.blockSignals(True)  # noqa: FBT003
            self._startup_checkbox.setChecked(get_show_main_window_on_startup())
            self._startup_checkbox.blockSignals(False)  # noqa: FBT003
            message_box.warning(self, "Settings", f"Could not save config.json:\n{exc}")

    def _on_sort_mode_changed(self, _index: int) -> None:
        """Persist sort mode and refresh the catalog view."""
        mode = self._sort_combo.currentData()
        if not isinstance(mode, str) or mode == self._sort_mode:
            return
        previous = self._sort_mode
        self._sort_mode = mode
        try:
            set_main_window_sort_mode(mode=mode)
        except (OSError, TypeError, ValueError) as exc:
            self._sort_mode = previous
            self._sync_sort_combo()
            message_box.warning(self, "Settings", f"Could not save config.json:\n{exc}")
            return
        self._apply_catalog_view()

    def _ordered_catalog_actions(self, query: str = "") -> list[QAction]:
        """Return catalog actions, optionally filtered and newest-first."""
        actions = [action for action in self._all_actions if not query or self._action_matches_search(action, query)]
        if not self._is_newest_sort():
            return actions

        def class_name_of(action: QAction) -> str:
            parts = get_action_identity_parts(action)
            return parts.class_name if parts is not None else action.text()

        return sort_items_newest_first(actions, class_name_of=class_name_of)

    def _populate_list_from_sections(self) -> None:
        """Fill the list using the same Main / submenu order as the cards, without Recent."""
        self.list_widget.clear()
        for section in self._sections:
            if not section.show_in_list or not section.actions:
                continue
            self._add_list_section_header(section.title)
            for action in section.actions:
                self._add_list_action_item(action, indent_level=1)

    def _recent_column_count(self) -> int:
        """Return how many Recent cards fit in one catalog row."""
        laid_out = 0
        for section in self._sections:
            if not section.show_in_list or section.grid is None or not section.grid.isVisible():
                continue
            laid_out = max(laid_out, count_icon_grid_first_row(section.grid))
        if laid_out > 0:
            return laid_out
        return described_card_column_count(self._cards_row_width())

    def _recent_gui_actions(self) -> list[QAction]:
        """Return catalog actions last used from the GUI, newest first, one row at most."""
        by_class: dict[str, QAction] = {}
        for action in self._all_actions:
            parts = get_action_identity_parts(action)
            if parts is not None:
                by_class[parts.class_name] = action
        return [
            by_class[name]
            for name in list_recent_gui_action_names(limit=self._recent_column_count())
            if name in by_class
        ]

    def _refresh_recent_section(self) -> None:
        """Rebuild the Recent section from the latest GUI usage timestamps."""
        section = self._recent_section
        if section is None or section.grid is None:
            return
        actions = self._recent_gui_actions()
        if section.widget is not None:
            section.widget.setVisible(bool(actions))
        if not actions:
            section.actions = []
            section.grid.clear()
            return
        if section.actions == actions and section.grid.count() == len(actions):
            if section.grid.isVisible():
                QTimer.singleShot(0, lambda grid=section.grid: self._fit_grid_height(grid))
            return
        section.actions = actions
        section.grid.clear()
        for action in actions:
            self._add_action_item(section.grid, action)
        if section.grid.isVisible():
            QTimer.singleShot(0, lambda grid=section.grid: self._fit_grid_height(grid))

    def _run_listed_action(self, action: QAction) -> None:
        """Run a catalog action and refresh the Recent section."""
        action.trigger()
        if not self._is_newest_sort() and not self._search_edit.text().strip():
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

    def _sync_sort_combo(self) -> None:
        """Select the combo item matching `_sort_mode` without emitting changes."""
        self._sort_combo.blockSignals(True)  # noqa: FBT003
        index = self._sort_combo.findData(self._sort_mode)
        self._sort_combo.setCurrentIndex(max(index, 0))
        self._sort_combo.blockSignals(False)  # noqa: FBT003
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, menu: QMenu) -> None
```

Initialize the main window from the tray menu structure.

Args:

- `menu` (`QMenu`): Tray menu whose actions are shown in the window.

<details>
<summary>Code:</summary>

```python
def __init__(self, menu: QMenu) -> None:
        super().__init__()

        self.setWindowTitle("Harrix Swiss Knife")
        try_apply_system_backdrop(self, backdrop=SystemBackdrop.MICA)

        self._sections: list[_CommandSection] = []
        self._recent_section: _CommandSection | None = None
        self._all_actions: list[QAction] = []
        self._sort_mode = get_main_window_sort_mode()

        central_widget = QWidget()
        apply_opaque_white(central_widget)
        self.setCentralWidget(central_widget)
        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(12, 12, 12, 12)
        root_layout.setSpacing(12)

        root_layout.addLayout(self._build_header_row())
        root_layout.addWidget(self._build_body_widget(), stretch=1)
        root_layout.addLayout(self._build_footer_row())
        self._build_sections_from_menu(menu)
        self._sync_sort_combo()
        self._apply_catalog_view()
        self._setup_window_size_and_position()
```

</details>

### ⚙️ Method `closeEvent`

```python
def closeEvent(self, event: QCloseEvent) -> None
```

Hide the window instead of closing the application.

<details>
<summary>Code:</summary>

```python
def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        event.ignore()
        self.hide()
```

</details>

### ⚙️ Method `eventFilter`

```python
def eventFilter(self, watched: QObject, event: QEvent) -> bool
```

Forward wheel events from icon grids and refit Recent when the cards pane resizes.

<details>
<summary>Code:</summary>

```python
def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        if event.type() == QEvent.Type.Resize and watched is self._scroll.viewport():
            QTimer.singleShot(0, self._on_cards_layout_changed)
        if event.type() == QEvent.Type.Wheel and self._is_icon_grid_wheel_target(watched):
            QApplication.sendEvent(self._scroll.viewport(), event)
            return True
        return super().eventFilter(watched, event)
```

</details>

### ⚙️ Method `focus_initial_input`

```python
def focus_initial_input(self) -> None
```

Focus the search field.

<details>
<summary>Code:</summary>

```python
def focus_initial_input(self) -> None:
        self.focus_search()
```

</details>

### ⚙️ Method `focus_search`

```python
def focus_search(self) -> None
```

Move keyboard focus to the search field.

<details>
<summary>Code:</summary>

```python
def focus_search(self) -> None:
        self._search_edit.setFocus(Qt.FocusReason.ActiveWindowFocusReason)
        self._search_edit.selectAll()
```

</details>

### ⚙️ Method `on_item_clicked`

```python
def on_item_clicked(self, item: QListWidgetItem) -> None
```

Handle click on a command in the list pane.

<details>
<summary>Code:</summary>

```python
def on_item_clicked(self, item: QListWidgetItem) -> None:
        if not item.flags() & Qt.ItemFlag.ItemIsSelectable:
            return

        action = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(action, QAction):
            self._run_listed_action(action)
```

</details>

### ⚙️ Method `resizeEvent`

```python
def resizeEvent(self, event: QResizeEvent) -> None
```

Refit Recent and icon grid heights when the window width changes.

<details>
<summary>Code:</summary>

```python
def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        super().resizeEvent(event)
        QTimer.singleShot(0, self._on_cards_layout_changed)
```

</details>

### ⚙️ Method `showEvent`

```python
def showEvent(self, event: QShowEvent) -> None
```

Refresh Recent and focus the primary input when the window is shown.

<details>
<summary>Code:</summary>

```python
def showEvent(self, event: QShowEvent) -> None:  # noqa: N802
        super().showEvent(event)
        QTimer.singleShot(0, self._on_cards_layout_changed)
        QTimer.singleShot(0, self.focus_initial_input)
```

</details>

### ⚙️ Method `show_window`

```python
def show_window(self) -> None
```

Show the window.

<details>
<summary>Code:</summary>

```python
def show_window(self) -> None:
        self.show()
```

</details>
