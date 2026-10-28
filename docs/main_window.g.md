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
  - [⚙️ Method `nativeEvent`](#%EF%B8%8F-method-nativeevent)
  - [⚙️ Method `on_item_clicked`](#%EF%B8%8F-method-on_item_clicked)
  - [⚙️ Method `resizeEvent`](#%EF%B8%8F-method-resizeevent)
  - [⚙️ Method `showEvent`](#%EF%B8%8F-method-showevent)
  - [⚙️ Method `show_window`](#%EF%B8%8F-method-show_window)

</details>

## 🏛️ Class `MainWindow`

```python
class MainWindow(QMainWindow)
```

Tray-click window with a command list and Fluent command cards.

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
        apply_window_icon(self)
        enable_fluent_theme(self)

        self._sections: list[_CommandSection] = []
        self._recent_section: _CommandSection | None = None
        self._all_actions: list[QAction] = []
        self._action_sections: dict[QAction, str] = {}
        self._sort_mode = get_main_window_sort_mode()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        caption_tools = self._build_caption_tools()
        self._caption_tools = caption_tools
        if not install_win11_caption(self, trailing_widgets=[caption_tools]):
            root_layout.addWidget(caption_tools)
        root_layout.addWidget(self._build_body_widget(), stretch=1)
        self._build_sections_from_menu(menu)
        self._sync_sort_combo()
        self._apply_catalog_view()
        self._setup_window_size_and_position()
        bind_theme(self, self._refresh_theme_icons)
        self._refresh_theme_icons()

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        """Hide the window instead of closing the application."""
        event.ignore()
        self.hide()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Refit Recent when the cards pane resizes."""
        if event.type() == QEvent.Type.Resize and watched is self._scroll.viewport():
            QTimer.singleShot(0, self._on_cards_layout_changed)
        return super().eventFilter(watched, event)

    def focus_initial_input(self) -> None:
        """Focus the search field."""
        self.focus_search()

    def focus_search(self) -> None:
        """Move keyboard focus to the search field."""
        self._search_edit.setFocus(Qt.FocusReason.ActiveWindowFocusReason)
        self._search_edit.selectAll()

    def nativeEvent(self, event_type, message) -> tuple[bool, int]:  # noqa: ANN001, N802
        """Drag, resize, and size the client area for the custom caption bar."""
        handled = try_handle_win11_caption_native_event(self, event_type, message)
        if handled is not None:
            return handled
        return cast("tuple[bool, int]", super().nativeEvent(event_type, message))

    def on_item_clicked(self, item: QListWidgetItem) -> None:
        """Handle click on a command or section header in the list pane."""
        data = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(data, QAction):
            self._run_listed_action(data)
            return
        if isinstance(data, str) and data:
            self._scroll_to_section(data)

    def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        """Refit Recent when the window width changes."""
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
        item.setData(Qt.ItemDataRole.UserRole, title)
        item.setToolTip(f"Scroll to {title}")
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
            self._search_grid.add_card(self._create_card(action, show_added_at=newest, show_section=True))
        self._search_grid.show()

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
        last_section = ""
        for action in self._ordered_catalog_actions(query):
            section = self._action_sections.get(action, "")
            if section and section != last_section:
                self._add_list_section_header(section)
                last_section = section
            self._add_list_action_item(action, indent_level=1 if section else 0)

    def _build_body_widget(self) -> QWidget:
        splitter = FluentSplitter()
        splitter.setObjectName("commandWindowSplitter")
        splitter.setAutoFillBackground(False)
        splitter.addWidget(self._build_list_pane())
        splitter.addWidget(self._build_cards_pane())
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([_LIST_PANE_WIDTH, _CARDS_PANE_WIDTH])
        return splitter

    def _build_caption_tools(self) -> QWidget:
        """Build compact search, sort, and theme controls for the caption row."""
        tools = QWidget()
        tools.setObjectName("captionTools")
        tools.setFixedHeight(CAPTION_BUTTON_HEIGHT)
        tools.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        row = QHBoxLayout(tools)
        row.setContentsMargins(SPACE_S, 0, SPACE_S, 0)
        row.setSpacing(SPACE_XS)

        self._search_edit = FluentSearchLineEdit(tools, placeholder="Search commands…", compact=True)
        self._search_edit.setObjectName("captionSearchEdit")
        self._search_edit.setMinimumWidth(_CAPTION_SEARCH_MIN_WIDTH)
        self._search_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._search_edit.textChanged.connect(self._on_search_changed)
        row.addWidget(self._search_edit, stretch=1)

        self._sort_combo = FluentComboBox(tools, compact=True)
        self._sort_combo.setObjectName("captionSortCombo")
        for mode, label, _icon in _SORT_MODES:
            self._sort_combo.addItem(label, mode)
        self._sort_combo.setToolTip("Sort commands by menu structure or date added")
        self._sort_combo.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self._sort_combo.currentIndexChanged.connect(self._on_sort_mode_changed)
        row.addWidget(self._sort_combo)

        self._theme_button = FluentIconButton("moon", tools)
        self._theme_button.setObjectName("themeToggleButton")
        self._theme_button.clicked.connect(self._on_theme_toggled)
        row.addWidget(self._theme_button)

        return tools

    def _build_cards_pane(self) -> QWidget:
        layer = FluentLayerPanel()
        layer_layout = QVBoxLayout(layer)
        layer_layout.setContentsMargins(1, 1, 0, 0)
        layer_layout.setSpacing(0)

        self._scroll = FluentScrollArea(layer)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.viewport().installEventFilter(self)
        layer_layout.addWidget(self._scroll)

        self._content = QWidget()
        self._content.setObjectName("commandCardContent")
        self._content.setAutoFillBackground(False)
        self._content.setStyleSheet("QWidget#commandCardContent { background: transparent; }")
        self._content_layout = QVBoxLayout(self._content)
        self._content_layout.setContentsMargins(SPACE_XL, SPACE_L, SPACE_XL, SPACE_XL)
        self._content_layout.setSpacing(SPACE_XL)
        self._content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._scroll.setWidget(self._content)

        self._grouped_widget = QWidget(self._content)
        self._grouped_layout = QVBoxLayout(self._grouped_widget)
        self._grouped_layout.setContentsMargins(0, 0, 0, 0)
        self._grouped_layout.setSpacing(SPACE_XL)
        self._grouped_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._content_layout.addWidget(self._grouped_widget)

        self._search_grid = FluentCardGrid(self._content)
        self._search_grid.hide()
        self._content_layout.addWidget(self._search_grid)
        self._content_layout.addStretch(1)

        return layer

    def _build_list_pane(self) -> QWidget:
        list_pane = QWidget()
        list_pane.setObjectName("commandListPane")
        list_pane.setAutoFillBackground(False)
        list_pane.setStyleSheet("QWidget#commandListPane { background: transparent; }")
        list_layout = QVBoxLayout(list_pane)
        list_layout.setContentsMargins(SPACE_XS, SPACE_XS, 0, SPACE_M)
        list_layout.setSpacing(SPACE_S)

        self.list_widget = FluentListWidget(list_pane)
        self.list_widget.itemClicked.connect(self.on_item_clicked)
        self.list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self._on_list_context_menu)
        list_layout.addWidget(self.list_widget, stretch=1)

        self._startup_checkbox = FluentCheckBox("Show at program startup", list_pane)
        self._startup_checkbox.setToolTip("Open this window when Harrix Swiss Knife starts")
        self._startup_checkbox.setChecked(get_show_main_window_on_startup())
        self._startup_checkbox.toggled.connect(self._on_show_on_startup_toggled)
        list_layout.addWidget(self._startup_checkbox)
        list_layout.setAlignment(self._startup_checkbox, Qt.AlignmentFlag.AlignLeft)
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
        for title, actions in sorted(submenu_sections, key=lambda item: item[0].casefold()):
            self._create_section(title, actions)
        self._recent_section = self._create_section(
            "Recent",
            self._recent_gui_actions(),
            track_in_all=False,
            insert_at=0,
            show_in_list=False,
        )

    def _create_card(
        self,
        action: QAction,
        *,
        show_added_at: bool = False,
        show_section: bool = False,
    ) -> FluentCommandCard:
        """Build a command card that runs `action` and offers its copy menu."""
        overline_parts: list[str] = []
        if show_section:
            section = self._action_sections.get(action, "")
            if section:
                overline_parts.append(section)
        if show_added_at:
            parts = get_action_identity_parts(action)
            date_text = format_added_at_date(added_at_for(parts.class_name)) if parts is not None else ""
            if date_text:
                overline_parts.append(f"Added {date_text}")
        icon_name = getattr(action, "icon_name", "") or ""
        icon = create_menu_icon(icon_name, CARD_ICON_SIZE) if icon_name else None
        card = FluentCommandCard(
            action.text(),
            getattr(action, "action_description", "") or "",
            icon=icon if icon is not None and not icon.isNull() else None,
            overline=" · ".join(overline_parts),
            user_data=action,
        )
        card.clicked.connect(lambda listed=action: self._run_listed_action(listed))
        card.context_menu_requested.connect(
            lambda global_pos, listed=action: show_action_item_context_menu(
                parent=self,
                global_pos=global_pos,
                action=listed,
            ),
        )
        return card

    def _create_section(
        self,
        title: str,
        actions: list[QAction],
        *,
        track_in_all: bool = True,
        insert_at: int | None = None,
        show_in_list: bool = True,
    ) -> _CommandSection:
        section_widget = QWidget(self._grouped_widget)
        section_layout = QVBoxLayout(section_widget)
        section_layout.setContentsMargins(0, 0, 0, 0)
        section_layout.setSpacing(SPACE_M)
        label = SubtitleLabel(title, section_widget)
        section_layout.addWidget(label)

        grid = FluentCardGrid(section_widget)
        for action in actions:
            grid.add_card(self._create_card(action))
            if track_in_all:
                self._all_actions.append(action)
                self._action_sections[action] = title
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
        return section

    def _is_newest_sort(self) -> bool:
        return self._sort_mode == MAIN_WINDOW_SORT_MODE_NEWEST

    def _on_cards_layout_changed(self) -> None:
        """Size Recent to one row of the catalog grid."""
        if not self._is_newest_sort() and not self._search_edit.text().strip():
            self._refresh_recent_section()

    def _on_list_context_menu(self, pos: QPoint) -> None:
        """Show copy name/class/path and CLI command for the list item under the cursor."""
        self._show_list_item_context_menu(self.list_widget, pos)

    def _on_search_changed(self, text: str) -> None:
        query = text.strip()
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
            message_box.warning(self, "Settings", f"Could not save config-temp.json:\n{exc}")
            return
        self._apply_catalog_view()

    def _on_theme_toggled(self) -> None:
        """Flip light / dark and persist `ui_theme` to `config.json`."""
        try:
            FluentTheme.instance().toggle(persist=True)
        except (OSError, TypeError, ValueError) as exc:
            message_box.warning(self, "Settings", f"Could not save config.json:\n{exc}")

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
        """Return how many command cards fit in one row of the cards pane."""
        width = self._grouped_widget.width()
        if width <= 0:
            margins = self._content_layout.contentsMargins()
            width = self._scroll.viewport().width() - margins.left() - margins.right()
        return max(1, (width + CARD_GRID_SPACING) // (COMMAND_CARD_WIDTH + CARD_GRID_SPACING))

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
        if section.actions == actions and section.grid.count() == len(actions):
            return
        section.actions = actions
        section.grid.clear()
        for action in actions:
            section.grid.add_card(self._create_card(action))

    def _refresh_theme_icons(self) -> None:
        """Re-tint the sort and theme glyphs for the current palette."""
        palette = palette_for(self)
        for index, (_mode, _label, icon_name) in enumerate(_SORT_MODES):
            self._sort_combo.setItemIcon(index, themed_icon(icon_name, palette))
        dark = palette.dark
        self.setStyleSheet(wallpaper_qss(palette))
        self.setPalette(to_qpalette(palette, self.palette()))
        self.setAutoFillBackground(False)
        body = self.centralWidget()
        if body is not None:
            body.setObjectName("commandWindowBody")
            body.setAutoFillBackground(False)
            body.setStyleSheet("QWidget#commandWindowBody { background: transparent; }")
        self._theme_button.set_icon_name("sun" if dark else "moon")
        tooltip = "Switch to light theme" if dark else "Switch to dark theme"
        self._theme_button.setToolTip(tooltip)
        self._theme_button.setAccessibleName(tooltip)

    def _run_listed_action(self, action: QAction) -> None:
        """Run a catalog action and refresh the Recent section."""
        action.trigger()
        if not self._is_newest_sort() and not self._search_edit.text().strip():
            self._refresh_recent_section()

    def _scroll_cards_to_widget(self, widget: QWidget) -> None:
        """Scroll the cards pane so `widget` sits at the top of the viewport."""
        content = self._scroll.widget()
        if content is None:
            return
        y = widget.mapTo(content, QPoint(0, 0)).y()
        bar = self._scroll.verticalScrollBar()
        bar.setValue(max(0, min(y, bar.maximum())))

    def _scroll_to_section(self, title: str) -> None:
        """Scroll the cards pane to the section named `title` (or its first card)."""
        target: QWidget | None = None
        if not self._grouped_widget.isHidden():
            for section in self._sections:
                if section.title != title:
                    continue
                if section.widget is not None and not section.widget.isHidden():
                    target = section.widget
                break
        elif not self._search_grid.isHidden():
            for card in self._search_grid.cards():
                action = getattr(card, "user_data", None)
                if isinstance(action, QAction) and self._action_sections.get(action) == title:
                    target = card
                    break
        if target is not None:
            self._scroll_cards_to_widget(target)

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

- [`menu`](qt_split_menu_button.g.md#%EF%B8%8F-method-menu) (`QMenu`): Tray menu whose actions are shown in the window.

<details>
<summary>Code:</summary>

```python
def __init__(self, menu: QMenu) -> None:
        super().__init__()

        self.setWindowTitle("Harrix Swiss Knife")
        apply_window_icon(self)
        enable_fluent_theme(self)

        self._sections: list[_CommandSection] = []
        self._recent_section: _CommandSection | None = None
        self._all_actions: list[QAction] = []
        self._action_sections: dict[QAction, str] = {}
        self._sort_mode = get_main_window_sort_mode()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        caption_tools = self._build_caption_tools()
        self._caption_tools = caption_tools
        if not install_win11_caption(self, trailing_widgets=[caption_tools]):
            root_layout.addWidget(caption_tools)
        root_layout.addWidget(self._build_body_widget(), stretch=1)
        self._build_sections_from_menu(menu)
        self._sync_sort_combo()
        self._apply_catalog_view()
        self._setup_window_size_and_position()
        bind_theme(self, self._refresh_theme_icons)
        self._refresh_theme_icons()
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

Refit Recent when the cards pane resizes.

<details>
<summary>Code:</summary>

```python
def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        if event.type() == QEvent.Type.Resize and watched is self._scroll.viewport():
            QTimer.singleShot(0, self._on_cards_layout_changed)
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

### ⚙️ Method `nativeEvent`

```python
def nativeEvent(self, event_type, message) -> tuple[bool, int]
```

Drag, resize, and size the client area for the custom caption bar.

<details>
<summary>Code:</summary>

```python
def nativeEvent(self, event_type, message) -> tuple[bool, int]:  # noqa: ANN001, N802
        handled = try_handle_win11_caption_native_event(self, event_type, message)
        if handled is not None:
            return handled
        return cast("tuple[bool, int]", super().nativeEvent(event_type, message))
```

</details>

### ⚙️ Method `on_item_clicked`

```python
def on_item_clicked(self, item: QListWidgetItem) -> None
```

Handle click on a command or section header in the list pane.

<details>
<summary>Code:</summary>

```python
def on_item_clicked(self, item: QListWidgetItem) -> None:
        data = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(data, QAction):
            self._run_listed_action(data)
            return
        if isinstance(data, str) and data:
            self._scroll_to_section(data)
```

</details>

### ⚙️ Method `resizeEvent`

```python
def resizeEvent(self, event: QResizeEvent) -> None
```

Refit Recent when the window width changes.

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
