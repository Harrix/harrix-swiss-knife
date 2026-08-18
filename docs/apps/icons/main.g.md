---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `main.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `KeyValueTableDialog`](#%EF%B8%8F-class-keyvaluetabledialog)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
- [🏛️ Class `MainWindow`](#%EF%B8%8F-class-mainwindow)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-1)
  - [⚙️ Method `closeEvent`](#%EF%B8%8F-method-closeevent)
- [🔧 Function `main`](#-function-main)

</details>

## 🏛️ Class `KeyValueTableDialog`

```python
class KeyValueTableDialog(QDialog)
```

Dialog displaying key-value pairs in a table with a copy button for each row.

<details>
<summary>Code:</summary>

```python
class KeyValueTableDialog(QDialog):

    def __init__(
        self,
        parent: QWidget | None,
        title: str,
        data: list[tuple[str, str]],
        *,
        previews: list[tuple[str, QPixmap]] | None = None,
    ) -> None:
        """Initialize the dialog."""
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(880 if previews else 600, 480 if previews else 400)

        table_column = QVBoxLayout()

        self.table = QTableWidget(len(data), 3)
        self.table.setHorizontalHeaderLabels(["Property", "Value", ""])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(2, 40)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setWordWrap(True)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        for row, (key, value) in enumerate(data):
            key_item = QTableWidgetItem(key)
            self.table.setItem(row, 0, key_item)

            value_item = QTableWidgetItem(value)
            self.table.setItem(row, 1, value_item)

            copy_btn = QPushButton("📋")
            copy_btn.setToolTip("Copy value")
            copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            copy_btn.clicked.connect(lambda _checked, v=value: self._copy_value(v))
            self.table.setCellWidget(row, 2, copy_btn)

        table_column.addWidget(self.table)
        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        btn_box.rejected.connect(self.reject)
        table_column.addWidget(btn_box)

        if previews:
            root = QHBoxLayout(self)
            root.addWidget(_preview_list_widget(previews))
            root.addLayout(table_column, stretch=1)
        else:
            layout = QVBoxLayout(self)
            layout.addLayout(table_column)

    def _copy_value(self, value: str) -> None:
        QApplication.clipboard().setText(value)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None, title: str, data: list[tuple[str, str]], *, previews: list[tuple[str, QPixmap]] | None = None) -> None
```

Initialize the dialog.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        parent: QWidget | None,
        title: str,
        data: list[tuple[str, str]],
        *,
        previews: list[tuple[str, QPixmap]] | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(880 if previews else 600, 480 if previews else 400)

        table_column = QVBoxLayout()

        self.table = QTableWidget(len(data), 3)
        self.table.setHorizontalHeaderLabels(["Property", "Value", ""])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(2, 40)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setWordWrap(True)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        for row, (key, value) in enumerate(data):
            key_item = QTableWidgetItem(key)
            self.table.setItem(row, 0, key_item)

            value_item = QTableWidgetItem(value)
            self.table.setItem(row, 1, value_item)

            copy_btn = QPushButton("📋")
            copy_btn.setToolTip("Copy value")
            copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            copy_btn.clicked.connect(lambda _checked, v=value: self._copy_value(v))
            self.table.setCellWidget(row, 2, copy_btn)

        table_column.addWidget(self.table)
        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        btn_box.rejected.connect(self.reject)
        table_column.addWidget(btn_box)

        if previews:
            root = QHBoxLayout(self)
            root.addWidget(_preview_list_widget(previews))
            root.addLayout(table_column, stretch=1)
        else:
            layout = QVBoxLayout(self)
            layout.addLayout(table_column)
```

</details>

## 🏛️ Class `MainWindow`

```python
class MainWindow(QMainWindow, AppWindowMixin)
```

Browse Harrix Vector Icons with search, categories, cache, and drag-out.

<details>
<summary>Code:</summary>

```python
class MainWindow(QMainWindow, AppWindowMixin):

    about_app_name = "Vector Icons"
    about_description = "Browse and drag SVG/AI/PDF/EPS icon folders (Harrix-Vector-Icons or flat dumps)."

    def __init__(self, *, hide_on_close: bool = False) -> None:
        """Build the browser UI and load catalog from config path."""
        super().__init__()
        try_apply_system_backdrop(self, backdrop=SystemBackdrop.MICA)
        self.setWindowTitle("Vector Icons")
        self.setWindowIcon(QIcon(":/assets/logo.svg"))
        self._init_hide_on_close(hide_on_close=hide_on_close)

        self._icon_size = load_icon_size()
        self._catalog: IconCatalog | None = None
        self._repo_root: Path | None = None
        self._thumb_cache = ThumbnailCache(size=DEFAULT_THUMB_SIZE)
        self._pixmaps: dict[str, QPixmap] = {}
        self._placeholder = placeholder_pixmap(self._icon_size)
        self._thumb_thread = None
        self._thumb_worker = None
        self._current_category: str | None = None
        self._current_folder: str | None = None
        self._nav_source: Literal["folder", "category"] | None = None
        self._nav_syncing = False
        self._selected_family_id: str | None = None
        self._category_icons = load_category_icons()
        self._favorite_ids: list[str] = []
        self._default_category_family_ids: dict[str, str] = {}
        self._variant_view_mode = MODE_FEATURED
        self._variant_pixmaps: dict[str, QPixmap] = {}
        self._load_progress_toast: toast_progress_notification.ToastProgressNotification | None = None
        self._catalog_load_thread: QThread | None = None
        self._catalog_load_worker: CatalogLoadWorker | None = None
        self._catalog_load_generation = 0
        self._pending_open_remember = False
        self._pending_catalog_refresh = False
        self._pending_catalog_allow_empty = False
        self._pending_refresh_category: str | None = None
        self._pending_refresh_folder: str | None = None
        self._visible_families: list[IconFamily] = []
        self._trademark_progress_toast: toast_progress_notification.ToastProgressNotification | None = None
        self._trademark_thread: QThread | None = None
        self._trademark_worker: TrademarkUpdateWorker | None = None
        self._maintenance_progress_toast: toast_progress_notification.ToastProgressNotification | None = None
        self._maintenance_thread: QThread | None = None
        self._maintenance_worker: RepoMaintenanceWorker | None = None
        self._maintenance_kind: MaintenanceKind | None = None
        self._keywords_batch_runner: KeywordsBatchRunner | None = None
        self._thumb_refresh_done = 0
        self._thumb_refresh_total = 0
        self._thumb_dirty_families: set[str] = set()
        self._thumb_flush_timer = QTimer(self)
        self._thumb_flush_timer.setSingleShot(True)
        self._thumb_flush_timer.setInterval(THUMB_UPDATE_FLUSH_MS)
        self._thumb_flush_timer.timeout.connect(self._flush_thumb_updates)
        self._grid_entries: list[GridEntry] = []
        self._pending_grid_entries: list[GridEntry] = []
        self._loaded_rows: set[int] = set()
        self._viewport_pixmap_timer = QTimer(self)
        self._viewport_pixmap_timer.setSingleShot(True)
        self._viewport_pixmap_timer.setInterval(0)
        self._viewport_pixmap_timer.timeout.connect(self._refresh_viewport_pixmaps)
        self._visible_family_ids: set[str] = set()
        self._grid_total_entries = 0
        self._grid_total_families = 0
        self._grid_matched = 0
        self._grid_fallback = 0
        self._grid_fill_timer = QTimer(self)
        self._grid_fill_timer.setInterval(15)
        self._grid_fill_timer.timeout.connect(self._fill_next_grid_chunk)
        self._icon_size_save_timer = QTimer(self)
        self._icon_size_save_timer.setSingleShot(True)
        self._icon_size_save_timer.setInterval(300)
        self._icon_size_save_timer.timeout.connect(self._persist_icon_size)
        self._search_filter_timer = QTimer(self)
        self._search_filter_timer.setSingleShot(True)
        self._search_filter_timer.setInterval(SEARCH_DEBOUNCE_MS)
        self._search_filter_timer.timeout.connect(self._apply_filters)

        self._build_ui()
        self._load_from_config()
        self._setup_window_size_and_position()

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        """Stop background work and optionally hide instead of closing."""
        self._search_filter_timer.stop()
        self._persist_icon_size()
        if self._hide_instead_of_close(event):
            return
        self._stop_grid_fill()
        self._stop_catalog_load()
        self._stop_trademark_update()
        self._stop_maintenance()
        self._stop_keywords_batch()
        self._stop_thumb_refresh()
        super().closeEvent(event)

    def _activate_category(self, text: str) -> None:
        if self._nav_syncing:
            return
        category = None if text == ALL_CATEGORIES or not text else text
        if is_favorites_category(category):
            category = FAVORITES_CATEGORY
        changed = (
            category != self._current_category or self._current_folder is not None or self._nav_source != "category"
        )
        self._nav_source = "category"
        self._current_category = category
        self._select_all_folders()
        if not changed:
            return
        self._apply_filters()
        self._start_thumb_refresh()

    def _activate_folder(self, prefix: str) -> None:
        if self._nav_syncing:
            return
        folder = prefix or None
        changed = folder != self._current_folder or self._current_category is not None or self._nav_source != "folder"
        self._nav_source = "folder"
        self._current_folder = folder
        self._select_all_categories()
        if not changed:
            return
        self._apply_filters()
        self._start_thumb_refresh()

    def _add_variants_to_family(self, sources: list[Path], *, family: IconFamily) -> None:
        if self._repo_root is None:
            return
        collisions = 0
        img_dir = self._repo_root / family.folder / "img"
        for source in sources:
            dest = img_dir / variant_dest_name(source, family_id=family.id)
            if dest.is_file():
                collisions += 1
        policy = self._ask_collision_policy(collisions)
        if policy is None:
            return
        self.statusBar().showMessage(f"Adding {len(sources)} variant(s) to `{family.id}`…")
        QApplication.processEvents()
        try:
            report = add_variants_to_family(
                sources,
                repo_root=self._repo_root,
                family_id=family.id,
                note_folder=family.folder,
                collision_policy=policy,
                rebuild=False,
            )
        except (OSError, ValueError, RuntimeError) as exc:
            QMessageBox.critical(self, "Vector Icons", f"Failed to add variants:\n{exc}")
            return
        self._on_refresh_catalog()
        if self._catalog is not None:
            refreshed = next((item for item in self._catalog.icons if item.id == family.id), None)
            if refreshed is not None:
                self._on_family_selected(refreshed, persist=False)
        self._show_vector_report(report)

    def _after_favorites_changed(self) -> None:
        if self._favorite_ids:
            self._default_category_family_ids[FAVORITES_CATEGORY] = self._favorite_ids[0]
        else:
            self._default_category_family_ids.pop(FAVORITES_CATEGORY, None)
        self._sync_favorite_ids_to_lists()
        leave_favorites = is_favorites_category(self._current_category) and not self._favorite_ids
        preferred = "" if leave_favorites else self._current_category
        was_favorites = is_favorites_category(self._current_category)
        self._populate_categories(preferred_category=preferred)
        if was_favorites or is_favorites_category(self._current_category):
            self._apply_filters()

    def _apply_filters(self) -> None:
        self._search_filter_timer.stop()
        self._stop_grid_fill()
        if self._catalog is None or self._repo_root is None:
            self.icon_list.clear()
            self.variants_panel.clear_variants()
            self.count_label.setText("0 icons")
            self._grid_entries = []
            self._loaded_rows = set()
            self._sync_variant_view_combo([])
            return
        selected_id = self._selected_family_id
        query = self.search_edit.text()
        folder, category = exclusive_sidebar_filters(
            source=self._nav_source,
            folder=self._current_folder,
            category=self._current_category,
        )
        if is_favorites_category(category):
            category = None
        scope = self._catalog.filter_icons(category=category, folder=folder, query="")
        if self._nav_source == "category" and is_favorites_category(self._current_category):
            by_id = {family.id: family for family in scope}
            scope = [by_id[family_id] for family_id in self._favorite_ids if family_id in by_id]
        self._sync_variant_view_combo(scope)
        families = self._catalog.filter_icons(
            category=category,
            folder=folder,
            query=query,
        )
        if self._nav_source == "category" and is_favorites_category(self._current_category):
            by_id = {family.id: family for family in families}
            families = [by_id[family_id] for family_id in self._favorite_ids if family_id in by_id]
        entries = build_grid_entries(families, repo_root=self._repo_root, mode=self._variant_view_mode)
        self._grid_entries = entries
        self._grid_total_entries = len(entries)
        self._grid_total_families = len(families)
        self._grid_matched = sum(1 for entry in entries if not entry.is_fallback)
        self._grid_fallback = self._grid_total_entries - self._grid_matched
        first_chunk = entries[:GRID_FIRST_CHUNK]
        self._pending_grid_entries = entries[GRID_FIRST_CHUNK:]
        self._loaded_rows = set()
        self.icon_list.set_grid_entries(
            first_chunk,
            pixmaps_by_path={},
            placeholder=self._placeholder,
        )
        self._visible_families = []
        self._visible_family_ids = set()
        self._collect_visible_families(first_chunk)
        self._update_grid_counters()
        self._selected_family_id = selected_id
        self._restore_or_clear_selection(
            [entry.family for entry in first_chunk],
            allow_defer=bool(self._pending_grid_entries),
        )
        self._refresh_viewport_pixmaps()
        if self._pending_grid_entries:
            self._grid_fill_timer.start()

    def _apply_icon_size(self, size: int) -> None:
        """Apply display size to grids without writing config."""
        self._icon_size = size
        self._placeholder = placeholder_pixmap(size)
        self._variant_pixmaps.clear()
        self.icon_list.set_display_icon_size(size)
        self.variants_panel.set_thumb_size(self._variant_thumb_size(size))
        self.size_value_label.setText(str(size))
        selected_id = self._selected_family_id
        self._apply_filters()
        if selected_id is not None and self._catalog is not None and self._repo_root is not None:
            family = next((item for item in self._catalog.icons if item.id == selected_id), None)
            if family is not None:
                self._selected_family_id = selected_id
                self.variants_panel.show_family(family, self._repo_root)

    def _apply_loaded_catalog(self, catalog: IconCatalog) -> None:
        remember = self._pending_open_remember
        refresh = self._pending_catalog_refresh
        previous_category = self._pending_refresh_category
        previous_folder = self._pending_refresh_folder
        self._stop_thumb_refresh()
        self._stop_grid_fill()
        self._repo_root = catalog.repo_root
        self._catalog = catalog
        self._variant_pixmaps.clear()
        self._thumb_cache = ThumbnailCache(cache_dir=cache_dir_for_root(catalog.repo_root), size=DEFAULT_THUMB_SIZE)
        self._favorite_ids = load_favorites(catalog.repo_root)
        self._sync_favorite_ids_to_lists()
        self._sync_repo_root_to_lists()
        self._close_load_progress_toast()
        if len(catalog.icons) <= PRIME_PIXMAP_LIMIT:
            self._prime_pixmaps_from_cache()
        if refresh:
            if previous_folder:
                self._populate_folders(preferred_folder=previous_folder)
                self._populate_categories(preferred_category="")
            else:
                self._populate_folders(preferred_folder="")
                self._populate_categories(preferred_category=previous_category)
        else:
            self._selected_family_id = load_last_icon(catalog.repo_root)
            self._current_category = None
            self._current_folder = None
            if len(catalog.icons) > LARGE_CATALOG_LIMIT:
                folder = preferred_sidebar_folder(catalog, self._selected_family_id)
                self._current_folder = folder or None
            if remember:
                remember_recent_folder(catalog.repo_root)
            save_last_folder(catalog.repo_root)
            self.setWindowTitle(f"Vector Icons — {catalog.repo_root.name}")
            self._populate_folders()
            self._populate_categories()
            self._sync_folder_combo()
            self._rebuild_folder_menus()
            self._sync_add_vector_menu_title()
        self._sync_sidebar_source()
        self._apply_filters()
        self._close_load_progress_toast()
        self._refresh_category_icons()
        self._start_thumb_refresh()
        if refresh:
            category_count = len(catalog.categories())
            self.statusBar().showMessage(
                f"Catalog refreshed: {len(catalog.icons)} icons, {category_count} categories",
            )
            return
        kind = "flat dump" if catalog.kind == "flat" else "note repo"
        self.statusBar().showMessage(f"Opened {kind}: {catalog.repo_root} ({len(catalog.icons)} icons)")

    def _ask_collision_policy(self, collision_count: int) -> CollisionPolicy | None:
        """Ask how to handle filename collisions. Return `None` on cancel."""
        if collision_count <= 0:
            return "rename"
        box = QMessageBox(self)
        box.setWindowTitle("Vector name collisions")
        box.setIcon(QMessageBox.Icon.Question)
        box.setText(
            f"{collision_count} file(s) already exist with different content.\nHow should collisions be handled?"
        )
        rename_btn = box.addButton("Add as new variant", QMessageBox.ButtonRole.AcceptRole)
        replace_btn = box.addButton("Replace existing", QMessageBox.ButtonRole.DestructiveRole)
        skip_btn = box.addButton("Skip collisions", QMessageBox.ButtonRole.ActionRole)
        box.addButton(QMessageBox.StandardButton.Cancel)
        box.exec()
        clicked = box.clickedButton()
        if clicked is None or clicked == box.button(QMessageBox.StandardButton.Cancel):
            return None
        if clicked is replace_btn:
            return "replace"
        if clicked is skip_btn:
            return "skip"
        if clicked is rename_btn:
            return "rename"
        return None

    def _build_ui(self) -> None:
        central = QWidget(self)
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        toolbar = QHBoxLayout()
        toolbar.addWidget(QLabel("Folder"))
        self.folder_combo = QComboBox()
        self.folder_combo.setMinimumWidth(220)
        self.folder_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.folder_combo.currentIndexChanged.connect(self._on_folder_combo_changed)
        toolbar.addWidget(self.folder_combo, stretch=1)

        toolbar.addWidget(QLabel("Icon size"))
        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setRange(ICON_SIZE_MIN, ICON_SIZE_MAX)
        self.size_slider.setValue(self._icon_size)
        self.size_slider.setMaximumWidth(280)
        self.size_slider.setFixedHeight(24)
        self.size_slider.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.size_slider.valueChanged.connect(self._on_icon_size_changed)
        toolbar.addWidget(self.size_slider)
        self.size_value_label = QLabel(str(self._icon_size))
        self.size_value_label.setMinimumWidth(28)
        toolbar.addWidget(self.size_value_label)

        self._variant_view_label = QLabel("View")
        toolbar.addWidget(self._variant_view_label)
        self.variant_view_combo = QComboBox()
        self.variant_view_combo.setMinimumWidth(220)
        for mode_id, label in VARIANT_VIEW_MODES:
            self.variant_view_combo.addItem(label, mode_id)
        self.variant_view_combo.setCurrentIndex(0)
        self.variant_view_combo.currentIndexChanged.connect(self._on_variant_view_changed)
        self._variant_view_label.setVisible(False)
        self.variant_view_combo.setVisible(False)
        toolbar.addWidget(self.variant_view_combo)

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search icons (title, tags, id)…")
        self.search_edit.textChanged.connect(self._schedule_search_filter)
        self.search_edit.returnPressed.connect(self._apply_filters)
        toolbar.addWidget(self.search_edit, stretch=1)

        self.refresh_btn = QPushButton("🔄 Refresh catalog")
        self.refresh_btn.clicked.connect(self._on_refresh_catalog)
        toolbar.addWidget(self.refresh_btn)
        root.addLayout(toolbar)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        left_splitter = QSplitter(Qt.Orientation.Vertical)
        left_splitter.setMinimumWidth(160)
        left_splitter.setMaximumWidth(260)

        self.folder_tree = QTreeWidget()
        self.folder_tree.setHeaderHidden(True)
        self.folder_tree.setRootIsDecorated(True)
        self.folder_tree.setUniformRowHeights(True)
        self.folder_tree.setIconSize(QSize(FOLDER_TREE_ICON_SIZE, FOLDER_TREE_ICON_SIZE))
        self.folder_tree.setIndentation(12)
        self.folder_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.folder_tree.customContextMenuRequested.connect(self._on_folder_tree_context_menu)
        self.folder_tree.currentItemChanged.connect(self._on_folder_tree_changed)
        self.folder_tree.itemClicked.connect(self._on_folder_item_clicked)
        left_splitter.addWidget(self._sidebar_panel("Folders:", self.folder_tree))

        self.category_list = CategoryDropList()
        self.category_list.setIconSize(QSize(CATEGORY_LIST_ICON_SIZE, CATEGORY_LIST_ICON_SIZE))
        self.category_list.currentTextChanged.connect(self._on_category_changed)
        self.category_list.itemClicked.connect(self._on_category_item_clicked)
        self.category_list.families_dropped.connect(self._on_families_dropped_on_category)
        left_splitter.addWidget(self._sidebar_panel("Categories:", self.category_list))

        left_splitter.setStretchFactor(0, 1)
        left_splitter.setStretchFactor(1, 1)
        left_splitter.setSizes([220, 280])
        splitter.addWidget(left_splitter)

        center = QWidget()
        center_layout = QVBoxLayout(center)
        center_layout.setContentsMargins(0, 0, 0, 0)
        self.count_label = QLabel("")
        center_layout.addWidget(self.count_label)
        self.icon_list = DraggableIconList(icon_size=self._icon_size, dual_line_labels=True)
        self.icon_list.family_selected.connect(self._on_family_selected)
        self.icon_list.viewport_changed.connect(self._schedule_viewport_pixmaps)
        self._wire_icon_list_actions(self.icon_list)
        install_url_drop_handlers(self.icon_list, self._on_icon_files_dropped, filter_path=_is_vector_drop_path)
        center_layout.addWidget(self.icon_list)
        splitter.addWidget(center)

        self.variants_panel = VariantsPanel(thumb_size=self._variant_thumb_size(self._icon_size))
        self.variants_panel.setMinimumWidth(220)
        self._wire_icon_list_actions(self.variants_panel.list)
        install_url_drop_handlers(
            self.variants_panel.list,
            self._on_variant_files_dropped,
            filter_path=_is_vector_drop_path,
        )
        install_url_drop_handlers(
            self.variants_panel,
            self._on_variant_files_dropped,
            filter_path=_is_vector_drop_path,
        )
        splitter.addWidget(self.variants_panel)

        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 0)
        splitter.setSizes([200, 900, 320])
        root.addWidget(splitter)

        status = QStatusBar()
        self.setStatusBar(status)
        status.showMessage("Ready")
        self._thumb_status_label = QLabel("Thumbnails")
        self._thumb_status_label.hide()
        self._thumb_status_bar = QProgressBar()
        self._thumb_status_bar.setMaximumWidth(160)
        self._thumb_status_bar.setMaximumHeight(14)
        self._thumb_status_bar.setTextVisible(True)
        self._thumb_status_bar.setFormat("%v / %m")
        self._thumb_status_bar.hide()
        status.addPermanentWidget(self._thumb_status_label)
        status.addPermanentWidget(self._thumb_status_bar)

        file_menu = self.menuBar().addMenu("&File")
        open_folder_action = file_menu.addAction("📂 Open folder…")
        open_folder_action.triggered.connect(self._on_open_folder)
        pin_action = file_menu.addAction("📌 Pin current folder")
        pin_action.triggered.connect(self._on_pin_current_folder)
        self._pinned_menu = file_menu.addMenu("📌 Pinned folders")
        self._recent_menu = file_menu.addMenu("🕒 Recent folders")
        file_menu.addSeparator()
        self._add_vector_action = file_menu.addAction("📥 Add Vector Image…")
        self._add_vector_action.triggered.connect(self._on_add_vector_images)
        self._add_variants_action = file_menu.addAction("📥 Add icon variants…")
        self._add_variants_action.triggered.connect(self._on_add_icon_variants)
        refresh_action = file_menu.addAction("🔄 Refresh catalog")
        refresh_action.triggered.connect(self._on_refresh_catalog)
        file_menu.addSeparator()
        self._check_images_action = file_menu.addAction("🚧 Check images")
        self._check_images_action.triggered.connect(self._on_check_images)
        self._beautify_optimize_action = file_menu.addAction("💎 Beautify and optimize icons")
        self._beautify_optimize_action.triggered.connect(self._on_beautify_and_optimize)
        file_menu.addSeparator()
        open_cache_action = file_menu.addAction("📂 Open thumbs cache")
        open_cache_action.triggered.connect(self._on_open_thumbs_cache)
        cache_stats_action = file_menu.addAction("📊 Cache statistics")
        cache_stats_action.triggered.connect(self._on_cache_statistics)
        file_menu.addSeparator()
        self.actionExit = file_menu.addAction("E&xit")
        help_menu = self.menuBar().addMenu("&Help")
        self.actionAbout = help_menu.addAction("&About")
        self._connect_exit_about_actions()
        self._apply_exit_about_menu_emojis()
        self._rebuild_folder_menus()
        self._sync_folder_combo()
        self._sync_add_vector_menu_title()

    @staticmethod
    def _cache_pixmap(cache: dict[str, QPixmap], key: str, pixmap: QPixmap) -> None:
        """Store a pixmap, dropping the oldest entries so caches stay bounded."""
        cache[key] = pixmap
        overflow = len(cache) - PIXMAP_CACHE_MAX
        if overflow <= 0:
            return
        for stale_key in list(cache)[:overflow]:
            cache.pop(stale_key, None)

    def _category_family_id(self, category: str) -> str | None:
        if self._catalog is None:
            return None
        assigned = self._category_icons.get(category)
        if assigned:
            for family in self._catalog.icons:
                if family.id != assigned:
                    continue
                if is_favorites_category(category) or category in family.categories:
                    return assigned
        return self._default_category_family_ids.get(category)

    def _category_pixmap_icon(self, category: str) -> QIcon:
        family_id = self._category_family_id(category)
        if family_id is None:
            return QIcon()
        pixmap = self._pixmaps.get(family_id)
        if pixmap is None or pixmap.isNull():
            return QIcon(self._placeholder)
        return QIcon(
            pixmap.scaled(
                CATEGORY_LIST_ICON_SIZE,
                CATEGORY_LIST_ICON_SIZE,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            ),
        )

    def _close_load_progress_toast(self) -> None:
        toast = self._load_progress_toast
        self._load_progress_toast = None
        if toast is not None:
            toast.mark_completed()
            toast.close()

    def _close_maintenance_progress_toast(self) -> None:
        toast = self._maintenance_progress_toast
        self._maintenance_progress_toast = None
        if toast is not None:
            toast.close()

    def _close_trademark_progress_toast(self) -> None:
        toast = self._trademark_progress_toast
        self._trademark_progress_toast = None
        if toast is not None:
            toast.close()

    def _collect_visible_families(self, entries: list[GridEntry]) -> None:
        """Track unique families of already rendered tiles for thumbnail refresh."""
        for entry in entries:
            if entry.family.id in self._visible_family_ids:
                continue
            self._visible_family_ids.add(entry.family.id)
            self._visible_families.append(entry.family)

    def _entry_pixmap(self, entry: GridEntry) -> QPixmap | None:
        """Return the thumbnail for one tile, from memory, disk cache, or a fresh render."""
        key = str(entry.svg_path)
        featured = entry.family.featured_path(self._repo_root) if self._repo_root is not None else None
        is_featured_tile = self._variant_view_mode == MODE_FEATURED or (
            featured is not None and entry.svg_path.resolve() == featured.resolve()
        )
        if is_featured_tile:
            cached = self._pixmaps.get(entry.family.id)
            if cached is None:
                cached = self._thumb_cache.load_pixmap(entry.family.id)
                if cached is not None:
                    self._cache_pixmap(self._pixmaps, entry.family.id, cached)
            if cached is not None and not cached.isNull():
                return cached
        # No disk thumbnail yet: render now so the tile is not stuck on a placeholder
        # while the background worker walks through the rest of the folder.
        session = self._variant_pixmaps.get(key)
        if session is not None and not session.isNull():
            return session
        image = render_icon_to_image(entry.svg_path, self._icon_size)
        if image is None:
            return None
        pixmap = QPixmap.fromImage(image)
        self._cache_pixmap(self._variant_pixmaps, key, pixmap)
        return pixmap

    def _evict_offscreen_rows(self, first: int, last: int) -> None:
        if len(self._loaded_rows) <= LOADED_ROWS_MAX:
            return
        span = max(1, last - first + 1)
        low = first - 2 * span
        high = last + 2 * span
        stale = [row for row in self._loaded_rows if row < low or row > high]
        if not stale:
            return
        self.icon_list.reset_row_pixmaps(stale, placeholder=self._placeholder)
        self._loaded_rows.difference_update(stale)

    def _fill_next_grid_chunk(self) -> None:
        """Append more tiles, but give the event loop a turn once the time budget is spent."""
        deadline = time.monotonic() + GRID_FILL_BUDGET_S
        while self._pending_grid_entries and time.monotonic() < deadline:
            chunk = self._pending_grid_entries[:GRID_CHUNK_SIZE]
            del self._pending_grid_entries[:GRID_CHUNK_SIZE]
            self.icon_list.append_grid_entries(
                chunk,
                pixmaps_by_path={},
                placeholder=self._placeholder,
            )
            self._collect_visible_families(chunk)
        self._update_grid_counters()
        if not self._pending_grid_entries:
            self._finish_grid_fill()

    def _finish_grid_fill(self) -> None:
        self._grid_fill_timer.stop()
        self._pending_grid_entries = []
        self._update_grid_counters()
        if self._selected_family_id is not None and self.icon_list.currentItem() is None:
            self._restore_or_clear_selection(self._visible_families)
        self._refresh_viewport_pixmaps()
        self._start_thumb_refresh()

    def _flush_thumb_updates(self) -> None:
        """Apply thumbnails finished since the last flush with a single repaint."""
        families = self._thumb_dirty_families
        self._thumb_dirty_families = set()
        self._update_thumb_status_progress(self._thumb_refresh_done, self._thumb_refresh_total)
        if not families:
            return
        for family_id in families:
            self._pixmaps.pop(family_id, None)
        self._refresh_viewport_pixmaps(force_families=families)
        category_ids = set(self._category_icons.values()) | set(self._default_category_family_ids.values())
        if category_ids & families:
            self._refresh_category_icons()

    @staticmethod
    def _folder_display_name(path: Path) -> str:
        r"""Short label for folder combo/menus; `src` shows parent\src."""
        try:
            resolved = path.resolve()
        except OSError:
            resolved = path
        name = resolved.name
        parent_name = resolved.parent.name
        if name.casefold() == "src" and parent_name:
            return str(Path(parent_name) / name)
        return name

    def _folder_label(self, path: Path) -> str:
        try:
            resolved = path.resolve()
        except OSError:
            resolved = path
        return f"{self._folder_display_name(resolved)} — {resolved}"

    @staticmethod
    def _format_byte_size(total_bytes: int) -> str:
        kib = 1024
        mib = kib * kib
        if total_bytes >= mib:
            return f"{total_bytes / mib:.2f} MB"
        if total_bytes >= kib:
            return f"{total_bytes / kib:.1f} KB"
        return f"{total_bytes} B"

    def _hide_thumb_status_progress(self) -> None:
        self._thumb_status_label.hide()
        self._thumb_status_bar.hide()
        self._thumb_status_bar.reset()

    def _icon_detail_previews(self, family: IconFamily, svg_path: str) -> list[tuple[str, QPixmap]]:
        """Build left-side thumbnails for the Icon details dialog."""
        previews: list[tuple[str, QPixmap]] = []
        for label, path in collect_icon_detail_preview_paths(family, self._repo_root, svg_path):
            pixmap = self._preview_pixmap_for_path(family, path)
            if pixmap is None or pixmap.isNull():
                pixmap = placeholder_pixmap(_DETAILS_PREVIEW_SIZE)
            previews.append((label, pixmap))
        return previews

    def _import_vector_sources(self, sources: list[Path]) -> None:
        """Import vector files into the open flat folder or note repository."""
        if self._repo_root is None:
            return
        if self._is_note_repo_open():
            self._import_vector_sources_as_notes(sources)
            return
        collisions = sum(1 for source in sources if (self._repo_root / source.name).is_file())
        policy = self._ask_collision_policy(collisions)
        if policy is None:
            return
        self.statusBar().showMessage(f"Copying {len(sources)} vector file(s)…")
        QApplication.processEvents()
        try:
            report = copy_vectors_to_flat_folder(
                sources,
                dest_dir=self._repo_root,
                collision_policy=policy,
            )
        except (OSError, ValueError, RuntimeError) as exc:
            QMessageBox.critical(self, "Vector Icons", f"Failed to copy files:\n{exc}")
            return
        self._on_refresh_catalog()
        self._show_vector_report(report)

    def _import_vector_sources_as_notes(self, sources: list[Path]) -> None:
        if self._repo_root is None:
            return
        defaults = scan_repo_meta_defaults(self._repo_root)
        config: dict[str, Any] = h.dev.config_load(get_config_path_str())
        messages: list[str] = []
        created_any = False
        for source in sources:
            dialog = AddVectorImageDialog(self, source_path=source, defaults=defaults, app_config=config)
            if dialog.exec() != QDialog.DialogCode.Accepted:
                messages.append(f"Skipped `{source.name}` (cancelled)")
                continue
            meta = dialog.get_meta()
            if not meta.family_id:
                messages.append(f"Skipped `{source.name}` (empty filename)")
                continue
            existing = note_exists_for_family(self._repo_root, family_id=meta.family_id, category=meta.category)
            if existing is not None:
                answer = QMessageBox.question(
                    self,
                    "Vector Icons",
                    f"Note `{meta.family_id}` already exists.\nAdd `{source.name}` as a variant instead?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.Yes,
                )
                if answer != QMessageBox.StandardButton.Yes:
                    messages.append(f"Skipped `{source.name}` (note exists)")
                    continue
                family = IconFamily(
                    id=meta.family_id,
                    title=meta.title,
                    categories=[meta.category] if meta.category else [],
                    tags=meta.tags,
                    folder=str(existing.relative_to(self._repo_root)).replace("\\", "/"),
                    featured="",
                    featured_hash="",
                )
                self._add_variants_to_family([source], family=family)
                created_any = True
                continue
            try:
                report = create_note_from_meta(
                    source,
                    repo_root=self._repo_root,
                    meta=meta,
                    collision_policy="rename",
                    rebuild=False,
                )
            except (OSError, ValueError, RuntimeError) as exc:
                messages.append(f"Error for `{source.name}`: {exc}")
                continue
            created_any = True
            messages.extend(item.message for item in report.results)
        if created_any:
            self._on_refresh_catalog()
        if messages:
            preview = "\n".join(messages[:ADD_SVGS_RESULT_PREVIEW_LIMIT])
            if len(messages) > ADD_SVGS_RESULT_PREVIEW_LIMIT:
                preview += f"\n… and {len(messages) - ADD_SVGS_RESULT_PREVIEW_LIMIT} more"
            QMessageBox.information(self, "Vector Icons", preview)
            self.statusBar().showMessage(messages[0])

    def _is_note_repo_open(self) -> bool:
        if self._repo_root is None:
            return False
        if self._catalog is not None and self._catalog.kind == "flat":
            return False
        return is_note_icons_repo(self._repo_root)

    def _load_from_config(self) -> None:
        config: dict[str, Any] = h.dev.config_load(get_config_path_str())
        candidates: list[Path] = []
        last_folder = load_last_folder()
        if last_folder is not None and last_folder.is_dir():
            candidates.append(last_folder)
        raw = str(config.get("path_vector_icons") or "").strip()
        if raw and not raw.startswith("<"):
            default_path = Path(raw)
            if default_path.is_dir():
                candidates.append(default_path)
        for pinned in load_pinned_folders():
            if pinned not in candidates:
                candidates.append(pinned)
        for recent in load_recent_folders():
            if recent not in candidates:
                candidates.append(recent)
        for path in candidates:
            if path.is_dir():
                self._open_folder(path, remember=False)
                return
        QMessageBox.warning(
            self,
            "Vector Icons",
            "Set `path_vector_icons` or `path_vector_icons_pinned` in config.json,\nor use File → Open folder…",
        )
        self.statusBar().showMessage("No icon folder configured")
        self._sync_folder_combo()
        self._rebuild_folder_menus()

    def _on_add_icon_variants(self) -> None:
        """Pick vector files and add them as variants of an existing note."""
        if self._repo_root is None or self._catalog is None:
            QMessageBox.warning(self, "Vector Icons", "No icons folder is open.")
            return
        if self._catalog.kind != "note" or not is_note_icons_repo(self._repo_root):
            QMessageBox.warning(
                self, "Vector Icons", "Add icon variants works only with a note-folder icons repository."
            )
            return
        start = str(self._repo_root.parent if self._repo_root.parent.is_dir() else self._repo_root)
        chosen, _filter = QFileDialog.getOpenFileNames(
            self,
            "Select variant files",
            start,
            _VECTOR_FILE_FILTER,
        )
        if not chosen:
            return
        sources = collect_vector_sources(chosen)
        if not sources:
            QMessageBox.information(self, "Vector Icons", "No SVG/AI/PDF/EPS files selected.")
            return
        family = self.variants_panel.current_family
        if family is None and self._selected_family_id is not None:
            family = next((item for item in self._catalog.icons if item.id == self._selected_family_id), None)
        if family is None:
            dialog = ChooseIconFamilyDialog(self, catalog=self._catalog)
            if dialog.exec() != QDialog.DialogCode.Accepted:
                return
            family = dialog.selected_family()
        if family is None:
            return
        self._add_variants_to_family(sources, family=family)

    def _on_add_svgs(self) -> None:
        """Import SVGs from a folder into note folders of the open icons repo."""
        self._on_add_vector_images()

    def _on_add_vector_images(self) -> None:
        """Add vector files via file picker into the open folder."""
        if self._repo_root is None:
            QMessageBox.warning(self, "Vector Icons", "No icons folder is open.")
            return
        start = str(self._repo_root.parent if self._repo_root.parent.is_dir() else self._repo_root)
        title = "Select vector image" if self._is_note_repo_open() else "Select vector images"
        chosen, _filter = QFileDialog.getOpenFileNames(self, title, start, _VECTOR_FILE_FILTER)
        if not chosen:
            return
        sources = collect_vector_sources(chosen)
        if not sources:
            QMessageBox.information(self, "Vector Icons", "No SVG/AI/PDF/EPS files selected.")
            return
        self._import_vector_sources(sources)

    def _on_batch_favorites(self, payload: object) -> None:
        if self._repo_root is None or not isinstance(payload, tuple) or len(payload) != _KEYWORD_TARGET_PAIR_LEN:
            return
        targets, add = payload
        if not isinstance(targets, list):
            return
        should_add = bool(add)
        family_ids: list[str] = []
        for item in targets:
            if not isinstance(item, tuple) or len(item) != _KEYWORD_TARGET_PAIR_LEN:
                continue
            family = item[0]
            if isinstance(family, IconFamily):
                family_ids.append(family.id)
        if not family_ids:
            return
        if should_add:
            self._favorite_ids = add_favorites(self._repo_root, family_ids)
            self.statusBar().showMessage(f"Added {len(family_ids)} icon(s) to favorites")
        else:
            self._favorite_ids = remove_favorites(self._repo_root, family_ids)
            self.statusBar().showMessage(f"Removed {len(family_ids)} icon(s) from favorites")
        self._after_favorites_changed()

    def _on_batch_keywords_ai(self, targets: object) -> None:
        if not isinstance(targets, list) or self._repo_root is None:
            return
        if self._keywords_batch_runner is not None and self._keywords_batch_runner.is_running:
            QMessageBox.information(self, "Vector Icons", "Keyword AI batch is already running.")
            return

        jobs: list[tuple[IconFamily, Path]] = []
        for item in targets:
            if not isinstance(item, tuple) or len(item) != _KEYWORD_TARGET_PAIR_LEN:
                continue
            family, svg_path = item
            if not isinstance(family, IconFamily):
                continue
            icon_path = Path(svg_path) if isinstance(svg_path, str) and svg_path else None
            if icon_path is None or not icon_path.is_file():
                icon_path = family.featured_path(self._repo_root)
            if icon_path is None or not icon_path.is_file():
                continue
            if family.note_path(self._repo_root) is None:
                continue
            jobs.append((family, icon_path))

        if len(jobs) < _MIN_BATCH_KEYWORD_ICONS:
            QMessageBox.warning(self, "Vector Icons", "Need at least two icons with notes and preview files.")
            return

        answer = QMessageBox.question(
            self,
            "Vector Icons",
            f"Process keywords with AI for {len(jobs)} selected icons?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return

        config: dict[str, Any] = h.dev.config_load(get_config_path_str())
        self._keywords_batch_runner = KeywordsBatchRunner(
            self,
            app_config=config,
            jobs=jobs,
            on_item_success=self._on_batch_keywords_item,
            on_finished=self._on_batch_keywords_finished,
        )
        self._keywords_batch_runner.start()

    def _on_batch_keywords_finished(self, updated: int, failed: int, *, cancelled: bool) -> None:
        self._keywords_batch_runner = None
        self._apply_filters()
        if cancelled:
            message = f"Keyword AI cancelled. Updated {updated}, failed {failed}."
        else:
            message = f"Keyword AI finished. Updated {updated}, failed {failed}."
        self.statusBar().showMessage(message)
        toast = toast_notification.ToastNotification(message, duration=3000, parent=self)
        toast.present()

    def _on_batch_keywords_item(self, family: IconFamily, tags: list[str]) -> None:
        if self._repo_root is None:
            return
        note_path = family.note_path(self._repo_root)
        if note_path is None:
            return
        try:
            update_keywords_files(
                md_path=note_path,
                catalog_path=self._repo_root / "catalog.json",
                family_id=family.id,
                tags=tags,
            )
        except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
            logger.exception("Failed to save batch keywords for %s", family.id)
            QMessageBox.critical(self, "Vector Icons", f"Failed to save keywords for `{family.id}`:\n{exc}")
            return
        family.tags = tags
        family.refresh_search_blob()

    def _on_beautify_and_optimize(self) -> None:
        self._start_maintenance("beautify_optimize", "Beautify and optimize icons…")

    def _on_cache_statistics(self) -> None:
        stats = self._thumb_cache.stats(self._catalog)
        total_bytes = int(stats["total_bytes"])
        size_text = self._format_byte_size(total_bytes)

        data = [
            ("Cache folder", str(stats["cache_dir"])),
            ("PNG files", str(stats["png_files"])),
            ("Total size", f"{size_text} ({total_bytes} bytes)"),
            ("Meta entries", str(stats["meta_entries"])),
            ("Thumb size", f"{stats['thumb_size']} px"),
            ("Format version", str(stats["format_version"])),
        ]
        if int(stats["catalog_icons"]) > 0:
            data.extend(
                [
                    ("Catalog icons", str(stats["catalog_icons"])),
                    ("Fresh", str(stats["fresh"])),
                    ("Stale", str(stats["stale"])),
                    ("Missing", str(stats["missing"])),
                ]
            )

        dialog = KeyValueTableDialog(self, "Cache statistics", data)
        dialog.exec()

    def _on_cancel_catalog_load(self) -> None:
        if self._catalog_load_worker is not None:
            self._catalog_load_worker.request_cancel()
        self._catalog_load_generation += 1
        self._load_progress_toast = None
        self.statusBar().showMessage("Opening cancelled")

    def _on_catalog_load_cancelled(self, generation: int) -> None:
        if generation != self._catalog_load_generation:
            return
        self._close_load_progress_toast()
        self.statusBar().showMessage("Opening cancelled")

    def _on_catalog_load_failed(self, message: str, generation: int) -> None:
        if generation != self._catalog_load_generation:
            return
        if self._pending_catalog_allow_empty and self._catalog is not None and self._catalog.kind == "flat":
            root = self._repo_root or Path()
            self._apply_loaded_catalog(
                IconCatalog(version=1, generated_at="", icons=[], repo_root=root, kind="flat"),
            )
            return
        self._close_load_progress_toast()
        title = "Failed to refresh catalog" if self._pending_catalog_refresh else "Failed to open folder"
        QMessageBox.critical(self, "Vector Icons", f"{title}:\n{message}")

    def _on_catalog_load_finished(self) -> None:
        sender = self.sender()
        if self._catalog_load_thread is not None and sender is not self._catalog_load_thread:
            return
        self._catalog_load_thread = None
        self._catalog_load_worker = None

    def _on_catalog_load_succeeded(self, catalog: object, generation: int) -> None:
        if generation != self._catalog_load_generation:
            return
        if not isinstance(catalog, IconCatalog):
            self._on_catalog_load_failed("Catalog loader returned an unexpected result", generation)
            return
        self._apply_loaded_catalog(catalog)

    def _on_category_changed(self, text: str) -> None:
        self._activate_category(text)

    def _on_category_item_clicked(self, item: QListWidgetItem) -> None:
        self._activate_category(item.text())

    def _on_check_images(self) -> None:
        self._start_maintenance("check", "Checking images…")

    def _on_copy_contents(self, svg_path: str) -> None:
        path = Path(svg_path)
        if path.suffix.casefold() != ".svg":
            QMessageBox.warning(self, "Vector Icons", "Copy contents is available only for SVG files.")
            return
        if not path.is_file():
            QMessageBox.warning(self, "Vector Icons", f"File not found:\n{path}")
            return
        clipboard = QApplication.clipboard()
        if clipboard is None:
            QMessageBox.warning(self, "Vector Icons", "Clipboard is not available.")
            return
        try:
            clipboard.setText(read_svg_text(path))
        except (OSError, UnicodeDecodeError) as exc:
            QMessageBox.warning(self, "Vector Icons", f"Failed to read `{path.name}`:\n{exc}")
            return
        self.statusBar().showMessage(f"Copied contents of `{path.name}`")

    def _on_copy_filename(self, svg_path: str) -> None:
        name = Path(svg_path).name
        clipboard = QApplication.clipboard()
        if clipboard is None:
            QMessageBox.warning(self, "Vector Icons", "Clipboard is not available.")
            return
        clipboard.setText(name)
        self.statusBar().showMessage(f"Copied filename `{name}`")

    def _on_copy_path(self, svg_path: str) -> None:
        path = str(Path(svg_path).resolve())
        clipboard = QApplication.clipboard()
        if clipboard is None:
            QMessageBox.warning(self, "Vector Icons", "Clipboard is not available.")
            return
        clipboard.setText(path)
        self.statusBar().showMessage(f"Copied path `{path}`")

    def _on_copy_svg(self, svg_path: str) -> None:
        path = Path(svg_path)
        if not path.is_file():
            QMessageBox.warning(self, "Vector Icons", f"File not found:\n{path}")
            return
        mime = QMimeData()
        mime.setUrls([QUrl.fromLocalFile(str(path.resolve()))])
        clipboard = QApplication.clipboard()
        if clipboard is None:
            QMessageBox.warning(self, "Vector Icons", "Clipboard is not available.")
            return
        clipboard.setMimeData(mime)
        self.statusBar().showMessage(f"Copied file `{path.name}`")

    def _on_delete_icon(self, family: object) -> None:
        if not isinstance(family, IconFamily) or self._repo_root is None or self._catalog is None:
            return
        kind = self._catalog.kind
        if kind == "note":
            detail = f"This will permanently remove the note folder `{family.folder}` and all variants."
        else:
            detail = "This will permanently remove the icon file(s) from disk."
        reply = message_box.question(
            self,
            "Vector Icons",
            f"Delete icon `{family.title}` ({family.id})?\n\n{detail}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        self._stop_thumb_refresh()
        try:
            delete_icon_family(family, self._repo_root, kind=kind)
        except (OSError, ValueError) as exc:
            QMessageBox.critical(self, "Vector Icons", f"Failed to delete icon:\n{exc}")
            return
        self._pixmaps.pop(family.id, None)
        self._thumb_cache.forget(family.id)
        self._favorite_ids = remove_favorites(self._repo_root, [family.id])
        self._sync_favorite_ids_to_lists()
        if self._selected_family_id == family.id:
            self._selected_family_id = None
        self._on_refresh_catalog(allow_empty=True)
        self.statusBar().showMessage(f"Deleted `{family.id}`")

    def _on_edit_keywords(self, family: object, svg_path: str) -> None:
        if not isinstance(family, IconFamily):
            return
        if self._repo_root is None:
            QMessageBox.warning(self, "Vector Icons", "Icons repository is not loaded.")
            return
        note_path = family.note_path(self._repo_root)
        if note_path is None:
            QMessageBox.warning(self, "Vector Icons", f"Markdown note not found for `{family.id}`.")
            return

        icon_path = Path(svg_path) if svg_path else None
        if icon_path is None or not icon_path.is_file():
            icon_path = family.featured_path(self._repo_root)
        preview_path = icon_path if icon_path is not None and icon_path.is_file() else note_path

        try:
            frontmatter = parse_note_frontmatter(note_path.read_text(encoding="utf-8"))
        except OSError as exc:
            QMessageBox.critical(self, "Vector Icons", f"Failed to read note:\n{exc}")
            return
        initial = note_meta_from_existing(
            family_id=family.id,
            title=family.title,
            categories=family.categories,
            tags=family.tags,
            featured_name=family.featured or "featured-image.svg",
            frontmatter=frontmatter,
        )
        defaults = scan_repo_meta_defaults(self._repo_root)
        config: dict[str, Any] = h.dev.config_load(get_config_path_str())
        dialog = AddVectorImageDialog(
            self,
            source_path=preview_path,
            defaults=defaults,
            app_config=config,
            initial_meta=initial,
            window_title=f"Edit icon — {family.id}",
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        meta = dialog.get_meta()
        if not meta.family_id:
            QMessageBox.warning(self, "Vector Icons", "Filename is empty.")
            return
        if meta.category.strip():
            meta = note_meta_with_category(meta, meta.category)
        try:
            report = update_icon_note(repo_root=self._repo_root, family=family, meta=meta)
        except (OSError, ValueError, TypeError, FileExistsError) as exc:
            QMessageBox.critical(self, "Vector Icons", f"Failed to save icon:\n{exc}")
            return

        self._pixmaps.pop(report.old_family_id, None)
        self._thumb_cache.forget(report.old_family_id)
        if report.old_family_id != report.new_family_id:
            self._favorite_ids = rename_favorite(self._repo_root, report.old_family_id, report.new_family_id)
            self._sync_favorite_ids_to_lists()
        self._selected_family_id = report.new_family_id
        if meta.category.strip():
            self._current_category = meta.category.strip()
            self._current_folder = None
            self._nav_source = "category"
        self._on_refresh_catalog()
        message = f"Updated `{report.new_family_id}`"
        self.statusBar().showMessage(message)
        toast = toast_notification.ToastNotification(message, duration=2000, parent=self)
        toast.present()

    def _on_families_dropped_on_category(self, category: str, family_ids: object) -> None:
        if not isinstance(family_ids, list):
            return
        ids = [str(item).strip() for item in family_ids if str(item).strip()]
        if not ids or category == ALL_CATEGORIES or is_favorites_category(category):
            return
        if self._repo_root is None or self._catalog is None or not self._is_note_repo_open():
            QMessageBox.warning(
                self,
                "Vector Icons",
                "Category moves work only in a Vector Icons note repository.",
            )
            return
        by_id = {family.id: family for family in self._catalog.icons}
        moved = 0
        skipped = 0
        errors: list[str] = []
        last_id: str | None = None
        for family_id in ids:
            family = by_id.get(family_id)
            if family is None:
                continue
            try:
                report = reassign_icon_category(
                    repo_root=self._repo_root,
                    family=family,
                    category=category,
                    rebuild=False,
                )
            except (OSError, ValueError, TypeError, FileExistsError) as exc:
                errors.append(f"{family_id}: {exc}")
                continue
            if report is None:
                skipped += 1
                continue
            self._pixmaps.pop(report.old_family_id, None)
            self._thumb_cache.forget(report.old_family_id)
            if report.old_family_id != report.new_family_id:
                self._favorite_ids = rename_favorite(
                    self._repo_root,
                    report.old_family_id,
                    report.new_family_id,
                )
            last_id = report.new_family_id
            moved += 1
        if moved:
            self._sync_favorite_ids_to_lists()
            if last_id is not None:
                self._selected_family_id = last_id
            self._current_category = category
            self._current_folder = None
            self._nav_source = "category"
            self._on_refresh_catalog()
            message = f"Moved {moved} icon(s) to `{category}`"
            self.statusBar().showMessage(message)
            toast = toast_notification.ToastNotification(message, duration=2500, parent=self)
            toast.present()
        elif skipped and not errors:
            self.statusBar().showMessage(f"Already in `{category}`")
        if errors:
            preview = "\n".join(errors[:ADD_SVGS_RESULT_PREVIEW_LIMIT])
            QMessageBox.warning(self, "Vector Icons", f"Failed to move some icons:\n{preview}")

    def _on_family_selected(self, family: object, *, persist: bool = True) -> None:
        if family is None:
            self._selected_family_id = None
            self.variants_panel.clear_variants()
            return
        if not isinstance(family, IconFamily) or self._repo_root is None:
            return
        chosen = family
        if self._catalog is not None:
            match = next((item for item in self._catalog.icons if item.id == family.id), None)
            if match is not None:
                chosen = match
        self._selected_family_id = chosen.id
        if persist:
            save_last_icon(self._repo_root, chosen.id)
        self.variants_panel.show_family(chosen, self._repo_root)
        self.statusBar().showMessage(f"{chosen.id}: {len(chosen.variants)} variants")

    def _on_favorite_toggled(self, family: object) -> None:
        if not isinstance(family, IconFamily) or self._repo_root is None:
            return
        self._favorite_ids, added = toggle_favorite(self._repo_root, family.id)
        self._after_favorites_changed()
        verb = "Added" if added else "Removed"
        direction = "to" if added else "from"
        self.statusBar().showMessage(f"{verb} `{family.id}` {direction} favorites")

    def _on_folder_combo_changed(self, index: int) -> None:
        if index < 0:
            return
        raw = self.folder_combo.itemData(index)
        if not raw:
            return
        path = Path(str(raw))
        if self._repo_root is not None:
            try:
                if path.resolve() == self._repo_root.resolve():
                    return
            except OSError:
                if path == self._repo_root:
                    return
        self._open_folder(path)

    def _on_folder_item_clicked(self, item: QTreeWidgetItem, _column: int) -> None:
        self._activate_folder(str(item.data(0, Qt.ItemDataRole.UserRole) or ""))

    def _on_folder_tree_changed(self, current: QTreeWidgetItem | None, _previous: QTreeWidgetItem | None) -> None:
        path = ""
        if current is not None:
            path = str(current.data(0, Qt.ItemDataRole.UserRole) or "")
        self._activate_folder(path)

    def _on_folder_tree_context_menu(self, pos: QPoint) -> None:
        item = self.folder_tree.itemAt(pos)
        if item is None or self._repo_root is None:
            return
        menu = QMenu(self.folder_tree)
        reveal_action = menu.addAction("📂 Reveal in File Explorer")
        chosen = menu.exec_(self.folder_tree.mapToGlobal(pos))
        if chosen is reveal_action:
            prefix = str(item.data(0, Qt.ItemDataRole.UserRole) or "")
            self._on_reveal_in_explorer(str(folder_disk_path(self._repo_root, prefix)))

    def _on_icon_details(self, family: object, svg_path: str) -> None:
        if not isinstance(family, IconFamily):
            return
        note = family.note_path(self._repo_root) if self._repo_root is not None else None
        source = self._resolve_source_file(family, svg_path)
        variants = "\n".join(f"  - {variant.name} ({variant.file})" for variant in family.variants) or "  —"
        license_name, license_url = family_license_info(family, self._repo_root)

        data = [
            ("ID", str(family.id)),
            ("Title", str(family.title)),
            ("Date", str(family.date or "—")),
            ("Categories", ", ".join(family.categories) or "—"),
            ("Tags", ", ".join(family.tags) or "—"),
            ("License", license_name or "—"),
            ("License URL", license_url or "—"),
            ("Folder", str(family.folder)),
            ("Note", str(note if note is not None else "—")),
            ("Source", str(source if source is not None else "—")),
            ("Featured", str(family.featured or "—")),
            ("Featured hash", str(family.featured_hash or "—")),
            ("Selected SVG", str(svg_path)),
            (f"Variants ({len(family.variants)})", variants),
        ]

        dialog = KeyValueTableDialog(
            self,
            "Icon details",
            data,
            previews=self._icon_detail_previews(family, svg_path),
        )
        dialog.exec()

    def _on_icon_files_dropped(self, paths: list[str]) -> None:
        """Run Add Vector Image for files dropped onto the main icon grid."""
        if self._repo_root is None:
            QMessageBox.warning(self, "Vector Icons", "No icons folder is open.")
            return
        skip = (self._repo_root / "icons") if self._is_note_repo_open() else None
        sources = collect_vector_sources(paths, skip_under=skip)
        if not sources:
            QMessageBox.information(
                self,
                "Vector Icons",
                "Drop SVG/AI/PDF/EPS files or a folder with them to add them.",
            )
            return
        self._import_vector_sources(sources)

    def _on_icon_size_changed(self, value: int) -> None:
        self._apply_icon_size(value)
        self._icon_size_save_timer.start()

    def _on_maintenance_failed(self, message: str) -> None:
        self._close_maintenance_progress_toast()
        QMessageBox.critical(self, "Vector Icons", f"Maintenance failed:\n{message}")

    def _on_maintenance_finished(self) -> None:
        self._close_maintenance_progress_toast()
        self._maintenance_thread = None
        self._maintenance_worker = None
        self._maintenance_kind = None

    def _on_maintenance_progress(self, done: int, total: int, message: str) -> None:
        if self._maintenance_progress_toast is not None:
            self._maintenance_progress_toast.set_progress(done, total)
        if message:
            self.statusBar().showMessage(message)

    def _on_maintenance_succeeded(self, text: str) -> None:
        kind = self._maintenance_kind
        title = "Check images" if kind == "check" else "Beautify and optimize icons"
        self._close_maintenance_progress_toast()
        toast = toast_notification.ToastNotification(f"{title} completed", duration=2500, parent=self)
        toast.present()
        self.statusBar().showMessage(f"{title} completed")
        if kind == "beautify_optimize":
            self._on_refresh_catalog()
        self._show_text_result(title, text)

    def _on_open_folder(self) -> None:
        start = str(self._repo_root) if self._repo_root is not None else ""
        chosen = QFileDialog.getExistingDirectory(self, "Open icons folder", start)
        if not chosen:
            return
        self._open_folder(Path(chosen))

    def _on_open_license(self, url: object) -> None:
        text = str(url or "").strip()
        if not is_openable_license_url(text):
            QMessageBox.warning(self, "Vector Icons", "License URL is missing or is not an http(s) link.")
            return
        QDesktopServices.openUrl(QUrl(text))

    def _on_open_note_in_editor(self, family: object) -> None:
        if not isinstance(family, IconFamily):
            return
        if self._repo_root is None:
            QMessageBox.warning(self, "Vector Icons", "Icons repository is not loaded.")
            return
        note_path = family.note_path(self._repo_root)
        if note_path is None:
            QMessageBox.warning(self, "Vector Icons", f"Markdown note not found for `{family.id}`.")
            return
        config: dict[str, Any] = h.dev.config_load(get_config_path_str())
        editor = str(config.get("editor-notes") or "").strip()
        if not editor or editor.startswith("<"):
            QMessageBox.warning(
                self,
                "Vector Icons",
                "Set `editor-notes` in config.json (for example `code-insiders`).",
            )
            return
        workspace = str(config.get("path_vector_icons") or self._repo_root).strip() or str(self._repo_root)
        try:
            open_in_editor(editor, workspace, note_path)
        except (OSError, ValueError) as exc:
            QMessageBox.critical(self, "Vector Icons", f"Failed to open note in editor:\n{exc}")
            return
        self.statusBar().showMessage(f"Opened `{note_path.name}` in {editor}")

    def _on_open_source(self, family: object, svg_path: str) -> None:
        source = self._resolve_source_file(family, svg_path)
        if source is None:
            self._warn_source_not_found(family, svg_path)
            return
        config: dict[str, Any] = h.dev.config_load(get_config_path_str())
        raw_app = str(config.get("path_vector_icons_source_app") or "").strip()
        if not raw_app or raw_app.startswith("<"):
            QMessageBox.warning(
                self,
                "Vector Icons",
                "Set `path_vector_icons_source_app` in config.json "
                "to Adobe Illustrator (or another vector app) executable.",
            )
            return
        app_path = Path(raw_app)
        if not app_path.is_file():
            QMessageBox.warning(self, "Vector Icons", f"Source app not found:\n{app_path}")
            return
        try:
            subprocess.Popen([str(app_path), str(source)], shell=False)
        except OSError as exc:
            QMessageBox.critical(self, "Vector Icons", f"Failed to open source:\n{exc}")
            return
        self.statusBar().showMessage(f"Opened `{source.name}` in {app_path.name}")

    def _on_open_thumbs_cache(self) -> None:
        path = default_cache_dir()
        path.mkdir(parents=True, exist_ok=True)
        h.file.open_file_or_folder(path)
        self.statusBar().showMessage(f"Opened `{path}`")

    def _on_pin_current_folder(self) -> None:
        if self._repo_root is None:
            QMessageBox.warning(self, "Vector Icons", "No folder is open.")
            return
        pin_folder(self._repo_root)
        self._sync_folder_combo()
        self._rebuild_folder_menus()
        self.statusBar().showMessage(f"Pinned `{self._repo_root}`")

    def _on_preview_icon(self, svg_path: str, source: DraggableIconList) -> None:
        """Open the clicked icon in a lightbox using the source list order."""
        selected = Path(svg_path)
        paths = source.preview_paths()
        if selected not in paths:
            if not selected.is_file():
                return
            paths = [selected]
        dialog = IconLightboxDialog(paths, current_index=paths.index(selected), parent=self)
        dialog.exec()

    def _on_refresh_catalog(self, *_args: object, allow_empty: bool = False) -> None:
        if self._repo_root is None:
            self._load_from_config()
            return
        self._start_catalog_load(
            self._repo_root,
            remember=False,
            rebuild=self._catalog is None or self._catalog.kind != "flat",
            allow_empty=allow_empty,
            refresh=True,
        )

    def _on_reveal_in_explorer(self, svg_path: str) -> None:
        path = Path(svg_path)
        try:
            reveal_in_file_explorer(path)
        except (OSError, FileNotFoundError) as exc:
            QMessageBox.warning(self, "Vector Icons", str(exc))
            return
        self.statusBar().showMessage(f"Revealed `{path.name}`")

    def _on_reveal_source(self, family: object, svg_path: str) -> None:
        source = self._resolve_source_file(family, svg_path)
        if source is None:
            self._warn_source_not_found(family, svg_path)
            return
        try:
            reveal_in_file_explorer(source)
        except (OSError, FileNotFoundError) as exc:
            QMessageBox.warning(self, "Vector Icons", str(exc))
            return
        self.statusBar().showMessage(f"Revealed source `{source.name}`")

    def _on_set_as_category_icon(self, family: object) -> None:
        if not isinstance(family, IconFamily):
            return
        category = self._target_category_for_icon(family)
        if category is None:
            QMessageBox.warning(self, "Vector Icons", "Icon has no category to assign.")
            return
        self._category_icons = set_category_icon(category, family.id)
        self._refresh_category_icons()
        self.statusBar().showMessage(f"Category `{category}` icon set to `{family.id}`")

    def _on_thumb_finished(self, updated: int) -> None:
        if self.sender() is not self._thumb_worker:
            return
        self._thumb_flush_timer.stop()
        self._flush_thumb_updates()
        self._hide_thumb_status_progress()
        self._refresh_category_icons()
        if updated <= 0:
            return
        total = len(self._catalog.icons) if self._catalog else 0
        self.statusBar().showMessage(f"Thumbnails ready ({updated} updated, {total} total)", 4000)

    def _on_thumb_progress(self, family_id: str, thumb_path: str) -> None:
        if self.sender() is not self._thumb_worker:
            return
        self._thumb_refresh_done += 1
        if thumb_path:
            self._thumb_dirty_families.add(family_id)
        if not self._thumb_flush_timer.isActive():
            self._thumb_flush_timer.start()

    def _on_toggle_trademark(self, family: object) -> None:
        if not isinstance(family, IconFamily) or not self._repo_root:
            return
        if self._trademark_thread is not None and self._trademark_thread.isRunning():
            self.statusBar().showMessage("A trademark warning update is already running")
            return

        md_path = self._repo_root / family.folder / f"{family.id}.md"
        if not md_path.is_file():
            QMessageBox.warning(self, "Vector Icons", f"Markdown note not found:\n{md_path}")
            return

        enabled = not family.trademark
        self._trademark_progress_toast = toast_progress_notification.ToastProgressNotification(
            "Updating trademark warning…",
            total=1,
            parent=self,
        )
        self._trademark_progress_toast.start_countdown()
        self._trademark_progress_toast.set_progress(0, 1)

        thread = QThread(self)
        worker = TrademarkUpdateWorker(
            md_path=md_path,
            catalog_path=self._repo_root / "catalog.json",
            family_id=family.id,
            enabled=enabled,
        )
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.succeeded.connect(self._on_trademark_update_succeeded)
        worker.failed.connect(self._on_trademark_update_failed)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(self._on_trademark_update_finished)
        thread.finished.connect(thread.deleteLater)
        self._trademark_thread = thread
        self._trademark_worker = worker
        self.statusBar().showMessage(f"Updating trademark warning for `{family.id}`…")
        thread.start()

    def _on_trademark_update_failed(self, message: str) -> None:
        QMessageBox.critical(self, "Vector Icons", f"Failed to update trademark warning:\n{message}")

    def _on_trademark_update_finished(self) -> None:
        self._close_trademark_progress_toast()
        self._trademark_thread = None
        self._trademark_worker = None

    def _on_trademark_update_succeeded(self, family_id: str, enabled: bool) -> None:  # noqa: FBT001
        if self._catalog is None:
            return
        family = next((item for item in self._catalog.icons if item.id == family_id), None)
        if family is None:
            return
        family.trademark = enabled
        self._apply_filters()
        action = "added to" if enabled else "removed from"
        message = f"Trademark warning {action} `{family_id}`"
        self.statusBar().showMessage(message)
        toast = toast_notification.ToastNotification(message, duration=2000, parent=self)
        toast.present()

    def _on_variant_files_dropped(self, paths: list[str]) -> None:
        """Add dropped files as variants of the family shown in the panel."""
        if self._repo_root is None or not self._is_note_repo_open():
            QMessageBox.warning(self, "Vector Icons", "Variants can be added only in a note-folder icons repository.")
            return
        family = self.variants_panel.current_family
        if family is None:
            QMessageBox.warning(self, "Vector Icons", "Select an icon first so variants have a target.")
            return
        sources = collect_vector_sources(paths, skip_under=self._repo_root / "icons")
        if not sources:
            QMessageBox.information(self, "Vector Icons", "Drop SVG/AI/PDF/EPS files to add variants.")
            return
        self._add_variants_to_family(sources, family=family)

    def _on_variant_view_changed(self, _index: int) -> None:
        mode = self.variant_view_combo.currentData()
        self._variant_view_mode = str(mode) if mode else MODE_FEATURED
        self._apply_filters()

    def _open_folder(self, path: Path, *, remember: bool = True) -> None:
        """Load a note-folder repo or flat icon dump and refresh the UI."""
        self._start_catalog_load(path, remember=remember, rebuild=False, allow_empty=False, refresh=False)

    def _persist_icon_size(self) -> None:
        self._icon_size_save_timer.stop()
        save_icon_size(self.size_slider.value())

    def _populate_categories(self, *, preferred_category: str | None = None) -> None:
        previous = preferred_category if preferred_category is not None else self._current_category
        self.category_list.setUpdatesEnabled(False)
        self.category_list.blockSignals(True)  # noqa: FBT003
        self.category_list.clear()
        self._default_category_family_ids.clear()
        all_item = QListWidgetItem(QIcon(":/assets/logo.svg"), ALL_CATEGORIES)
        self.category_list.addItem(all_item)
        names: list[str] = []
        if self._catalog is not None:
            names = sidebar_category_names(self._catalog.categories(), has_favorites=bool(self._favorite_ids))
            if self._favorite_ids:
                self._default_category_family_ids[FAVORITES_CATEGORY] = self._favorite_ids[0]
            for name in names:
                if not is_favorites_category(name):
                    families = self._catalog.filter_icons(category=name)
                    if families:
                        self._default_category_family_ids[name] = families[0].id
                item = QListWidgetItem(name)
                item.setIcon(self._category_pixmap_icon(name))
                self.category_list.addItem(item)
        select_row = 0
        if previous and is_favorites_category(previous) and FAVORITES_CATEGORY in names:
            select_row = names.index(FAVORITES_CATEGORY) + 1
            self._current_category = FAVORITES_CATEGORY
        elif previous and previous in names:
            select_row = names.index(previous) + 1
            self._current_category = previous
        else:
            self._current_category = None
        self.category_list.setCurrentRow(select_row)
        self.category_list.blockSignals(False)  # noqa: FBT003
        self.category_list.setUpdatesEnabled(True)
        self.category_list.viewport().update()

    def _populate_folders(self, *, preferred_folder: str | None = None) -> None:
        previous = preferred_folder if preferred_folder is not None else self._current_folder
        self.folder_tree.setUpdatesEnabled(False)
        self.folder_tree.blockSignals(True)  # noqa: FBT003
        self.folder_tree.clear()
        all_item = QTreeWidgetItem([ALL_FOLDERS])
        all_item.setData(0, Qt.ItemDataRole.UserRole, "")
        all_item.setIcon(0, QIcon(":/assets/logo.svg"))
        self.folder_tree.addTopLevelItem(all_item)

        prefixes: list[str] = []
        if self._catalog is not None:
            prefixes = self._catalog.folder_prefixes()
        folder_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon)
        items: dict[str, QTreeWidgetItem] = {}
        for prefix in prefixes:
            name = prefix.rsplit("/", 1)[-1]
            parent_path = prefix.rsplit("/", 1)[0] if "/" in prefix else ""
            item = QTreeWidgetItem([name])
            item.setData(0, Qt.ItemDataRole.UserRole, prefix)
            item.setIcon(0, folder_icon)
            parent = items.get(parent_path)
            if parent is None:
                self.folder_tree.addTopLevelItem(item)
            else:
                parent.addChild(item)
            items[prefix] = item

        self.folder_tree.expandAll()
        selected = all_item
        if previous and previous in items:
            selected = items[previous]
            self._current_folder = previous
        else:
            self._current_folder = None
        self.folder_tree.setCurrentItem(selected)
        self.folder_tree.blockSignals(False)  # noqa: FBT003
        self.folder_tree.setUpdatesEnabled(True)
        self.folder_tree.viewport().update()

    def _preview_pixmap_for_path(self, family: IconFamily, path: Path) -> QPixmap | None:
        """Return a cached or freshly rendered thumbnail for `path`."""
        featured = family.featured_path(self._repo_root) if self._repo_root is not None else None
        try:
            resolved = path.resolve()
        except OSError:
            resolved = path
        if featured is not None:
            try:
                featured_resolved = featured.resolve()
            except OSError:
                featured_resolved = featured
            if resolved == featured_resolved:
                cached = self._pixmaps.get(family.id)
                if cached is None:
                    cached = self._thumb_cache.load_pixmap(family.id)
                if cached is not None and not cached.isNull():
                    return cached
        session = self._variant_pixmaps.get(str(path)) or self._variant_pixmaps.get(str(resolved))
        if session is not None and not session.isNull():
            return session
        image = render_icon_to_image(path, _DETAILS_PREVIEW_SIZE)
        if image is None:
            return None
        return QPixmap.fromImage(image)

    def _prime_pixmaps_from_cache(self) -> None:
        if self._catalog is None:
            return
        self._pixmaps.clear()
        for family in self._catalog.icons:
            pixmap = self._thumb_cache.load_pixmap(family.id)
            if pixmap is not None:
                self._pixmaps[family.id] = pixmap

    def _rebuild_folder_menus(self) -> None:
        if not hasattr(self, "_pinned_menu"):
            return
        self._pinned_menu.clear()
        pinned = load_pinned_folders()
        if not pinned:
            empty = self._pinned_menu.addAction("(none in config.json)")
            empty.setEnabled(False)
        else:
            for path in pinned:
                action = self._pinned_menu.addAction(self._folder_label(path))
                action.triggered.connect(lambda _checked=False, target=path: self._open_folder(target))
        self._recent_menu.clear()
        recent = load_recent_folders()
        if not recent:
            empty_recent = self._recent_menu.addAction("(empty)")
            empty_recent.setEnabled(False)
        else:
            for path in recent:
                action = self._recent_menu.addAction(self._folder_label(path))
                action.triggered.connect(lambda _checked=False, target=path: self._open_folder(target))

    def _refresh_category_icons(self) -> None:
        for index in range(self.category_list.count()):
            item = self.category_list.item(index)
            if item is None:
                continue
            name = item.text()
            if name == ALL_CATEGORIES:
                item.setIcon(QIcon(":/assets/logo.svg"))
                continue
            item.setIcon(self._category_pixmap_icon(name))

    def _refresh_viewport_pixmaps(self, *, force_families: set[str] | None = None) -> None:
        """Load thumbnails for tiles near the viewport and drop the ones scrolled far away."""
        if not self._grid_entries:
            return
        first, last = self.icon_list.visible_row_span(VIEWPORT_MARGIN_LINES)
        last = min(last, self.icon_list.count() - 1, len(self._grid_entries) - 1)
        deadline = time.monotonic() + VIEWPORT_LOAD_BUDGET_S
        updates: dict[int, QPixmap] = {}
        unfinished = False
        for row in range(first, last + 1):
            entry = self._grid_entries[row]
            if row in self._loaded_rows and (force_families is None or entry.family.id not in force_families):
                continue
            if time.monotonic() >= deadline:
                unfinished = True
                break
            self._loaded_rows.add(row)
            pixmap = self._entry_pixmap(entry)
            if pixmap is not None and not pixmap.isNull():
                updates[row] = pixmap
        self.icon_list.update_row_pixmaps(updates)
        self._evict_offscreen_rows(first, last)
        if unfinished:
            self._viewport_pixmap_timer.start()

    def _require_note_repo_for_add_svgs(self) -> Path | None:
        """Return the open note-folder repo, or show a warning and return `None`."""
        if not self._is_note_repo_open() or self._repo_root is None:
            QMessageBox.warning(
                self,
                "Vector Icons",
                "Current folder is not a Vector Icons note repository.",
            )
            return None
        return self._repo_root

    def _resolve_source_file(self, family: object, svg_path: str) -> Path | None:
        if not isinstance(family, IconFamily) or self._repo_root is None:
            return None
        selected = Path(svg_path)
        if selected.is_file() and selected.suffix.casefold() in {".ai", ".pdf", ".eps"}:
            return selected
        featured = family.featured_path(self._repo_root)
        if featured is not None and featured.suffix.casefold() in {".ai", ".pdf", ".eps"}:
            return featured
        config: dict[str, Any] = h.dev.config_load(get_config_path_str())
        ai_root = resolve_external_ai_root(config.get("path_vector_icons_ai"))
        note_dir = self._repo_root / family.folder if family.folder else self._repo_root
        return find_icon_source_file(
            family_id=family.id,
            note_dir=note_dir,
            svg_path=selected if selected.is_file() else None,
            external_ai_root=ai_root,
        )

    def _restore_or_clear_selection(self, families: list[IconFamily], *, allow_defer: bool = False) -> None:
        """Keep selection if the family is still visible; otherwise select the first tile.

        With `allow_defer` the selection is kept untouched when the family is not rendered yet,
        so a retry after the grid finishes filling can still find it.

        """
        target_id = self._selected_family_id
        if target_id is None and families:
            target_id = families[0].id
        if target_id is None:
            self.variants_panel.clear_variants()
            return
        for family in families:
            if family.id != target_id:
                continue
            self.icon_list.blockSignals(True)  # noqa: FBT003
            selected = self.icon_list.select_family(family.id)
            self.icon_list.blockSignals(False)  # noqa: FBT003
            if selected:
                self._on_family_selected(family, persist=False)
                return
            break
        if allow_defer:
            return
        self._selected_family_id = None
        self.variants_panel.clear_variants()

    def _schedule_search_filter(self) -> None:
        """Restart debounce so the grid filters after typing pauses."""
        self._search_filter_timer.start()

    def _schedule_viewport_pixmaps(self) -> None:
        self._viewport_pixmap_timer.start()

    def _select_all_categories(self) -> None:
        if self.category_list.currentRow() == 0 and self._current_category is None:
            return
        self._nav_syncing = True
        try:
            self.category_list.setCurrentRow(0)
            self._current_category = None
        finally:
            self._nav_syncing = False

    def _select_all_folders(self) -> None:
        if not self._current_folder and self.folder_tree.currentItem() is self.folder_tree.topLevelItem(0):
            return
        self._nav_syncing = True
        try:
            all_item = self.folder_tree.topLevelItem(0)
            if all_item is not None:
                self.folder_tree.setCurrentItem(all_item)
            self._current_folder = None
        finally:
            self._nav_syncing = False

    def _show_text_result(self, title: str, text: str) -> None:
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.resize(900, 640)
        layout = QVBoxLayout(dialog)
        editor = QPlainTextEdit()
        editor.setReadOnly(True)
        editor.setPlainText(text)
        layout.addWidget(editor)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttons.accepted.connect(dialog.accept)
        layout.addWidget(buttons)
        dialog.exec()

    def _show_vector_report(self, report: object) -> None:
        summary_lines = getattr(report, "summary_lines", None)
        results = getattr(report, "results", [])
        summary = "\n".join(summary_lines) if summary_lines else "Done."
        detail_lines = [item.message for item in results[:ADD_SVGS_RESULT_PREVIEW_LIMIT]]
        if len(results) > ADD_SVGS_RESULT_PREVIEW_LIMIT:
            detail_lines.append(f"… and {len(results) - ADD_SVGS_RESULT_PREVIEW_LIMIT} more")
        detail = "\n".join(detail_lines)
        QMessageBox.information(self, "Vector Icons", f"{summary}\n\n{detail}" if detail else summary)
        self.statusBar().showMessage(summary_lines[0] if summary_lines else "Done")

    @staticmethod
    def _sidebar_panel(title: str, widget: QWidget) -> QWidget:
        """Return a labeled sidebar pane for the left vertical splitter."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(4, 4, 0, 0)
        layout.setSpacing(4)
        layout.addWidget(QLabel(title))
        layout.addWidget(widget)
        return panel

    def _start_catalog_load(
        self,
        path: Path,
        *,
        remember: bool,
        rebuild: bool,
        allow_empty: bool,
        refresh: bool,
    ) -> None:
        self._stop_thumb_refresh()
        self._stop_grid_fill()
        self._catalog_load_generation += 1
        generation = self._catalog_load_generation
        self._pending_open_remember = remember
        self._pending_catalog_allow_empty = allow_empty
        self._pending_catalog_refresh = refresh
        self._pending_refresh_category = self._current_category if refresh else None
        self._pending_refresh_folder = self._current_folder if refresh else None
        message = "Refreshing catalog…" if refresh else "Opening folder…"
        self._update_load_toast(message)
        self.statusBar().showMessage(message)
        thread = QThread(self)
        worker = CatalogLoadWorker(path, rebuild=rebuild, generation=generation)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.succeeded.connect(self._on_catalog_load_succeeded, Qt.ConnectionType.QueuedConnection)
        worker.failed.connect(self._on_catalog_load_failed, Qt.ConnectionType.QueuedConnection)
        worker.cancelled.connect(self._on_catalog_load_cancelled, Qt.ConnectionType.QueuedConnection)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(self._on_catalog_load_finished)
        thread.finished.connect(thread.deleteLater)
        self._catalog_load_thread = thread
        self._catalog_load_worker = worker
        thread.start()

    def _start_maintenance(self, kind: MaintenanceKind, toast_message: str) -> None:
        if self._repo_root is None or not self._is_note_repo_open():
            QMessageBox.warning(
                self,
                "Vector Icons",
                "Check and beautify work only with a note-folder icons repository.",
            )
            return
        if self._maintenance_thread is not None and self._maintenance_thread.isRunning():
            QMessageBox.information(self, "Vector Icons", "A maintenance job is already running.")
            return
        self._maintenance_kind = kind
        self._maintenance_progress_toast = toast_progress_notification.ToastProgressNotification(
            toast_message,
            total=0,
            parent=self,
        )
        self._maintenance_progress_toast.start_countdown()
        thread = QThread(self)
        worker = RepoMaintenanceWorker(self._repo_root, kind)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.progress.connect(self._on_maintenance_progress)
        worker.succeeded.connect(self._on_maintenance_succeeded)
        worker.failed.connect(self._on_maintenance_failed)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(self._on_maintenance_finished)
        thread.finished.connect(thread.deleteLater)
        self._maintenance_thread = thread
        self._maintenance_worker = worker
        self.statusBar().showMessage(toast_message)
        thread.start()

    def _start_thumb_refresh(self) -> None:
        if self._catalog is None:
            return
        self._stop_thumb_refresh()
        self._thumb_refresh_done = 0
        families = self._visible_families or (
            list(self._catalog.icons) if len(self._catalog.icons) <= LARGE_CATALOG_LIMIT else []
        )
        if not families:
            return
        stale = self._thumb_cache.stale_families(families)
        self._thumb_refresh_total = len(stale)
        if not stale:
            return
        self._update_thumb_status_progress(0, self._thumb_refresh_total)
        self._thumb_thread, self._thumb_worker = start_thumbnail_refresh(
            self._catalog,
            self._thumb_cache,
            families=stale,
            on_progress=self._on_thumb_progress,
            on_finished=self._on_thumb_finished,
        )

    def _stop_catalog_load(self) -> None:
        self._catalog_load_generation += 1
        if self._catalog_load_worker is not None:
            self._catalog_load_worker.request_cancel()
        thread = self._catalog_load_thread
        if thread is not None and thread.isRunning():
            thread.wait(3000)
        self._catalog_load_thread = None
        self._catalog_load_worker = None
        self._close_load_progress_toast()

    def _stop_grid_fill(self) -> None:
        self._grid_fill_timer.stop()
        self._viewport_pixmap_timer.stop()
        self._pending_grid_entries = []

    def _stop_keywords_batch(self) -> None:
        runner = self._keywords_batch_runner
        if runner is not None and runner.is_running:
            runner.cancel()
        self._keywords_batch_runner = None

    def _stop_maintenance(self) -> None:
        thread = self._maintenance_thread
        if thread is not None and thread.isRunning():
            thread.quit()
            thread.wait(3000)
        self._maintenance_thread = None
        self._maintenance_worker = None
        self._maintenance_kind = None
        self._close_maintenance_progress_toast()

    def _stop_thumb_refresh(self) -> None:
        self._thumb_flush_timer.stop()
        self._thumb_dirty_families = set()
        if self._thumb_worker is not None:
            self._thumb_worker.cancel()
        if self._thumb_thread is not None and self._thumb_thread.isRunning():
            self._thumb_thread.quit()
            self._thumb_thread.wait(3000)
        self._thumb_thread = None
        self._thumb_worker = None
        self._hide_thumb_status_progress()

    def _stop_trademark_update(self) -> None:
        thread = self._trademark_thread
        if thread is not None and thread.isRunning():
            thread.quit()
            thread.wait(3000)
        self._trademark_thread = None
        self._trademark_worker = None
        self._close_trademark_progress_toast()

    def _sync_add_vector_menu_title(self) -> None:
        if not hasattr(self, "_add_vector_action"):
            return
        if self._is_note_repo_open():
            self._add_vector_action.setText("📥 Add Vector Image…")
            self._add_variants_action.setEnabled(True)
            note_repo = True
        else:
            self._add_vector_action.setText("📥 Add Vector Images…")
            self._add_variants_action.setEnabled(False)
            note_repo = False
        if hasattr(self, "_check_images_action"):
            self._check_images_action.setEnabled(note_repo)
            self._beautify_optimize_action.setEnabled(note_repo)

    def _sync_favorite_ids_to_lists(self) -> None:
        ids = set(self._favorite_ids)
        if hasattr(self, "icon_list"):
            self.icon_list.set_favorite_family_ids(ids)
        if hasattr(self, "variants_panel"):
            self.variants_panel.list.set_favorite_family_ids(ids)

    def _sync_folder_combo(self) -> None:
        if not hasattr(self, "folder_combo"):
            return
        self.folder_combo.blockSignals(True)  # noqa: FBT003
        self.folder_combo.clear()
        pinned = load_pinned_folders()
        seen: set[str] = set()
        current_key = ""
        if self._repo_root is not None:
            try:
                current_key = str(self._repo_root.resolve())
            except OSError:
                current_key = str(self._repo_root)
        for path in pinned:
            try:
                key = str(path.resolve())
            except OSError:
                key = str(path)
            if key in seen:
                continue
            seen.add(key)
            self.folder_combo.addItem(self._folder_display_name(path), str(path))
        if self._repo_root is not None and current_key not in seen:
            label = f"{self._folder_display_name(self._repo_root)} (current)"
            self.folder_combo.insertItem(0, label, str(self._repo_root))
        # Select current folder when present.
        selected = -1
        for index in range(self.folder_combo.count()):
            raw = str(self.folder_combo.itemData(index) or "")
            try:
                key = str(Path(raw).resolve()) if raw else ""
            except OSError:
                key = raw
            if key == current_key:
                selected = index
                break
        if selected >= 0:
            self.folder_combo.setCurrentIndex(selected)
        self.folder_combo.blockSignals(False)  # noqa: FBT003

    def _sync_repo_root_to_lists(self) -> None:
        if hasattr(self, "icon_list"):
            self.icon_list.set_repo_root(self._repo_root)
        if hasattr(self, "variants_panel"):
            self.variants_panel.list.set_repo_root(self._repo_root)

    def _sync_sidebar_source(self) -> None:
        if self._current_folder:
            self._nav_source = "folder"
        elif self._current_category:
            self._nav_source = "category"
        else:
            self._nav_source = None

    def _sync_variant_view_combo(self, families: list[IconFamily]) -> None:
        """Show only View modes that exist in the current folder or category."""
        if not hasattr(self, "variant_view_combo"):
            return
        available = available_variant_view_modes(families)
        if self._variant_view_mode not in available:
            self._variant_view_mode = MODE_FEATURED
        only_featured = available == (MODE_FEATURED,)
        self._variant_view_label.setVisible(not only_featured)
        self.variant_view_combo.setVisible(not only_featured)
        if only_featured:
            return
        labels = dict(VARIANT_VIEW_MODES)
        self.variant_view_combo.blockSignals(True)  # noqa: FBT003
        self.variant_view_combo.clear()
        selected = 0
        for mode_id in available:
            self.variant_view_combo.addItem(labels.get(mode_id, mode_id), mode_id)
            if mode_id == self._variant_view_mode:
                selected = self.variant_view_combo.count() - 1
        self.variant_view_combo.setCurrentIndex(selected)
        self.variant_view_combo.blockSignals(False)  # noqa: FBT003

    def _target_category_for_icon(self, family: IconFamily) -> str | None:
        if is_favorites_category(self._current_category):
            return FAVORITES_CATEGORY
        if self._current_category and self._current_category in family.categories:
            return self._current_category
        return family.categories[0] if family.categories else None

    def _update_grid_counters(self) -> None:
        loaded = self.icon_list.count()
        total = self._grid_total_entries
        complete = loaded >= total
        shown = str(total) if complete else f"{loaded} of {total}"
        if self._grid_fallback:
            self.count_label.setText(f"{shown} tiles ({self._grid_matched} match, {self._grid_fallback} fallback)")
        else:
            self.count_label.setText(f"{shown} tiles / {self._grid_total_families} families")
        catalog_total = len(self._catalog.icons) if self._catalog is not None else 0
        suffix = "" if complete else " — loading…"
        self.statusBar().showMessage(
            f"Showing {shown} tiles ({self._grid_total_families} families) / {catalog_total}{suffix}",
        )

    def _update_load_toast(
        self,
        message: str,
        *,
        done: int = 0,
        total: int = 0,
    ) -> toast_progress_notification.ToastProgressNotification:
        toast = self._load_progress_toast
        if toast is None:
            toast = toast_progress_notification.ToastProgressNotification(
                message,
                total=total,
                parent=self,
                cancellable=True,
            )
            self._load_progress_toast = toast
            toast.cancel_requested.connect(self._on_cancel_catalog_load)
            toast.start_countdown()
        else:
            toast.message = message
        toast.set_progress(done, total)
        toast.pump_events()
        return toast

    def _update_thumb_status_progress(self, done: int, total: int) -> None:
        self._thumb_status_bar.setRange(0, max(1, total))
        self._thumb_status_bar.setValue(min(max(done, 0), max(total, 1)))
        self._thumb_status_label.show()
        self._thumb_status_bar.show()

    @staticmethod
    def _variant_thumb_size(icon_size: int) -> int:
        return max(ICON_SIZE_MIN, min(icon_size, (icon_size * 3) // 4 or icon_size))

    def _warn_source_not_found(self, family: object, svg_path: str) -> None:
        if not isinstance(family, IconFamily) or self._repo_root is None:
            QMessageBox.warning(self, "Vector Icons", "Source file not found.")
            return
        config: dict[str, Any] = h.dev.config_load(get_config_path_str())
        ai_root = resolve_external_ai_root(config.get("path_vector_icons_ai"))
        note_dir = self._repo_root / family.folder
        stems = ", ".join(candidate_source_stems(family.id, Path(svg_path)))
        dirs = "\n".join(f"  - {path}" for path in source_search_directories(note_dir, ai_root)) or "  —"
        hint = ""
        if ai_root is None:
            hint = (
                "\n\nSet `path_vector_icons_ai` in config.json (for example Harrix-Vector-Icons-ai or its src folder)."
            )
        QMessageBox.warning(
            self,
            "Vector Icons",
            f"Source file not found for `{family.id}`.\n\nTried stems: {stems}\nSearch folders:\n{dirs}{hint}",
        )

    def _wire_icon_list_actions(self, icon_list: DraggableIconList) -> None:
        icon_list.reveal_requested.connect(self._on_reveal_in_explorer)
        icon_list.details_requested.connect(self._on_icon_details)
        icon_list.copy_requested.connect(self._on_copy_svg)
        icon_list.copy_contents_requested.connect(self._on_copy_contents)
        icon_list.copy_filename_requested.connect(self._on_copy_filename)
        icon_list.copy_path_requested.connect(self._on_copy_path)
        icon_list.open_note_requested.connect(self._on_open_note_in_editor)
        icon_list.edit_keywords_requested.connect(self._on_edit_keywords)
        icon_list.batch_keywords_ai_requested.connect(self._on_batch_keywords_ai)
        icon_list.batch_favorites_requested.connect(self._on_batch_favorites)
        icon_list.set_category_icon_requested.connect(self._on_set_as_category_icon)
        icon_list.favorite_toggled.connect(self._on_favorite_toggled)
        icon_list.license_requested.connect(self._on_open_license)
        icon_list.toggle_trademark_requested.connect(self._on_toggle_trademark)
        icon_list.reveal_source_requested.connect(self._on_reveal_source)
        icon_list.open_source_requested.connect(self._on_open_source)
        icon_list.delete_requested.connect(self._on_delete_icon)
        icon_list.preview_requested.connect(
            lambda path, source=icon_list: self._on_preview_icon(path, source),
        )
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, *, hide_on_close: bool = False) -> None
```

Build the browser UI and load catalog from config path.

<details>
<summary>Code:</summary>

```python
def __init__(self, *, hide_on_close: bool = False) -> None:
        super().__init__()
        try_apply_system_backdrop(self, backdrop=SystemBackdrop.MICA)
        self.setWindowTitle("Vector Icons")
        self.setWindowIcon(QIcon(":/assets/logo.svg"))
        self._init_hide_on_close(hide_on_close=hide_on_close)

        self._icon_size = load_icon_size()
        self._catalog: IconCatalog | None = None
        self._repo_root: Path | None = None
        self._thumb_cache = ThumbnailCache(size=DEFAULT_THUMB_SIZE)
        self._pixmaps: dict[str, QPixmap] = {}
        self._placeholder = placeholder_pixmap(self._icon_size)
        self._thumb_thread = None
        self._thumb_worker = None
        self._current_category: str | None = None
        self._current_folder: str | None = None
        self._nav_source: Literal["folder", "category"] | None = None
        self._nav_syncing = False
        self._selected_family_id: str | None = None
        self._category_icons = load_category_icons()
        self._favorite_ids: list[str] = []
        self._default_category_family_ids: dict[str, str] = {}
        self._variant_view_mode = MODE_FEATURED
        self._variant_pixmaps: dict[str, QPixmap] = {}
        self._load_progress_toast: toast_progress_notification.ToastProgressNotification | None = None
        self._catalog_load_thread: QThread | None = None
        self._catalog_load_worker: CatalogLoadWorker | None = None
        self._catalog_load_generation = 0
        self._pending_open_remember = False
        self._pending_catalog_refresh = False
        self._pending_catalog_allow_empty = False
        self._pending_refresh_category: str | None = None
        self._pending_refresh_folder: str | None = None
        self._visible_families: list[IconFamily] = []
        self._trademark_progress_toast: toast_progress_notification.ToastProgressNotification | None = None
        self._trademark_thread: QThread | None = None
        self._trademark_worker: TrademarkUpdateWorker | None = None
        self._maintenance_progress_toast: toast_progress_notification.ToastProgressNotification | None = None
        self._maintenance_thread: QThread | None = None
        self._maintenance_worker: RepoMaintenanceWorker | None = None
        self._maintenance_kind: MaintenanceKind | None = None
        self._keywords_batch_runner: KeywordsBatchRunner | None = None
        self._thumb_refresh_done = 0
        self._thumb_refresh_total = 0
        self._thumb_dirty_families: set[str] = set()
        self._thumb_flush_timer = QTimer(self)
        self._thumb_flush_timer.setSingleShot(True)
        self._thumb_flush_timer.setInterval(THUMB_UPDATE_FLUSH_MS)
        self._thumb_flush_timer.timeout.connect(self._flush_thumb_updates)
        self._grid_entries: list[GridEntry] = []
        self._pending_grid_entries: list[GridEntry] = []
        self._loaded_rows: set[int] = set()
        self._viewport_pixmap_timer = QTimer(self)
        self._viewport_pixmap_timer.setSingleShot(True)
        self._viewport_pixmap_timer.setInterval(0)
        self._viewport_pixmap_timer.timeout.connect(self._refresh_viewport_pixmaps)
        self._visible_family_ids: set[str] = set()
        self._grid_total_entries = 0
        self._grid_total_families = 0
        self._grid_matched = 0
        self._grid_fallback = 0
        self._grid_fill_timer = QTimer(self)
        self._grid_fill_timer.setInterval(15)
        self._grid_fill_timer.timeout.connect(self._fill_next_grid_chunk)
        self._icon_size_save_timer = QTimer(self)
        self._icon_size_save_timer.setSingleShot(True)
        self._icon_size_save_timer.setInterval(300)
        self._icon_size_save_timer.timeout.connect(self._persist_icon_size)
        self._search_filter_timer = QTimer(self)
        self._search_filter_timer.setSingleShot(True)
        self._search_filter_timer.setInterval(SEARCH_DEBOUNCE_MS)
        self._search_filter_timer.timeout.connect(self._apply_filters)

        self._build_ui()
        self._load_from_config()
        self._setup_window_size_and_position()
```

</details>

### ⚙️ Method `closeEvent`

```python
def closeEvent(self, event: QCloseEvent) -> None
```

Stop background work and optionally hide instead of closing.

<details>
<summary>Code:</summary>

```python
def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        self._search_filter_timer.stop()
        self._persist_icon_size()
        if self._hide_instead_of_close(event):
            return
        self._stop_grid_fill()
        self._stop_catalog_load()
        self._stop_trademark_update()
        self._stop_maintenance()
        self._stop_keywords_batch()
        self._stop_thumb_refresh()
        super().closeEvent(event)
```

</details>

## 🔧 Function `main`

```python
def main() -> None
```

Run the Vector Icons app standalone.

<details>
<summary>Code:</summary>

```python
def main() -> None:
    run_app_main(MainWindow, set_tab_index_zero=False)
```

</details>
