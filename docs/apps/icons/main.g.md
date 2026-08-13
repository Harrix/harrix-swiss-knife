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

    def __init__(self, parent: QWidget | None, title: str, data: list[tuple[str, str]]) -> None:
        """Initialize the dialog."""
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(600, 400)

        layout = QVBoxLayout(self)

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

        layout.addWidget(self.table)

        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

    def _copy_value(self, value: str) -> None:
        QApplication.clipboard().setText(value)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None, title: str, data: list[tuple[str, str]]) -> None
```

Initialize the dialog.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None, title: str, data: list[tuple[str, str]]) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(600, 400)

        layout = QVBoxLayout(self)

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

        layout.addWidget(self.table)

        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)
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
        self._selected_family_id: str | None = None
        self._category_icons = load_category_icons()
        self._default_category_family_ids: dict[str, str] = {}
        self._variant_view_mode = MODE_FEATURED
        self._variant_pixmaps: dict[str, QPixmap] = {}
        self._variant_progress_toast: toast_progress_notification.ToastProgressNotification | None = None
        self._thumb_progress_toast: toast_progress_notification.ToastProgressNotification | None = None
        self._thumb_refresh_done = 0
        self._thumb_refresh_total = 0
        self._icon_size_save_timer = QTimer(self)
        self._icon_size_save_timer.setSingleShot(True)
        self._icon_size_save_timer.setInterval(300)
        self._icon_size_save_timer.timeout.connect(self._persist_icon_size)

        self._build_ui()
        self._load_from_config()
        self._setup_window_size_and_position()

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        """Stop background work and optionally hide instead of closing."""
        self._persist_icon_size()
        if self._hide_instead_of_close(event):
            return
        self._close_variant_progress_toast()
        self._stop_thumb_refresh()
        super().closeEvent(event)

    def _apply_filters(self) -> None:
        if self._catalog is None or self._repo_root is None:
            self.icon_list.clear()
            self.variants_panel.clear_variants()
            self.count_label.setText("0 icons")
            return
        selected_id = self._selected_family_id
        query = self.search_edit.text()
        families = self._catalog.filter_icons(category=self._current_category, query=query)
        entries = build_grid_entries(families, repo_root=self._repo_root, mode=self._variant_view_mode)
        pixmaps_by_path = self._pixmaps_for_entries(entries)
        self.icon_list.set_grid_entries(
            entries,
            pixmaps_by_path=pixmaps_by_path,
            placeholder=self._placeholder,
        )
        matched = sum(1 for entry in entries if not entry.is_fallback)
        fallback = sum(1 for entry in entries if entry.is_fallback)
        if fallback:
            self.count_label.setText(f"{len(entries)} tiles ({matched} match, {fallback} fallback)")
        else:
            self.count_label.setText(f"{len(entries)} tiles / {len(families)} families")
        self.statusBar().showMessage(
            f"Showing {len(entries)} tiles ({len(families)} families) / {len(self._catalog.icons)}",
        )
        self._selected_family_id = selected_id
        self._restore_or_clear_selection([entry.family for entry in entries])

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

        toolbar.addWidget(QLabel("View"))
        self.variant_view_combo = QComboBox()
        self.variant_view_combo.setMinimumWidth(220)
        for mode_id, label in VARIANT_VIEW_MODES:
            self.variant_view_combo.addItem(label, mode_id)
        self.variant_view_combo.setCurrentIndex(0)
        self.variant_view_combo.currentIndexChanged.connect(self._on_variant_view_changed)
        toolbar.addWidget(self.variant_view_combo)

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search icons (title, tags, id)…")
        self.search_edit.textChanged.connect(self._apply_filters)
        toolbar.addWidget(self.search_edit, stretch=1)

        self.refresh_btn = QPushButton("🔄 Refresh catalog")
        self.refresh_btn.clicked.connect(self._on_refresh_catalog)
        toolbar.addWidget(self.refresh_btn)
        root.addLayout(toolbar)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.category_list = QListWidget()
        self.category_list.setMinimumWidth(160)
        self.category_list.setMaximumWidth(260)
        self.category_list.setIconSize(QSize(CATEGORY_LIST_ICON_SIZE, CATEGORY_LIST_ICON_SIZE))
        self.category_list.currentTextChanged.connect(self._on_category_changed)
        splitter.addWidget(self.category_list)

        center = QWidget()
        center_layout = QVBoxLayout(center)
        center_layout.setContentsMargins(0, 0, 0, 0)
        self.count_label = QLabel("")
        center_layout.addWidget(self.count_label)
        self.icon_list = DraggableIconList(icon_size=self._icon_size, dual_line_labels=True)
        self.icon_list.family_selected.connect(self._on_family_selected)
        self._wire_icon_list_actions(self.icon_list)
        center_layout.addWidget(self.icon_list)
        splitter.addWidget(center)

        self.variants_panel = VariantsPanel(thumb_size=self._variant_thumb_size(self._icon_size))
        self.variants_panel.setMinimumWidth(220)
        self._wire_icon_list_actions(self.variants_panel.list)
        splitter.addWidget(self.variants_panel)

        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 0)
        splitter.setSizes([200, 900, 320])
        root.addWidget(splitter)

        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Ready")

        file_menu = self.menuBar().addMenu("&File")
        open_folder_action = file_menu.addAction("📂 Open folder…")
        open_folder_action.triggered.connect(self._on_open_folder)
        pin_action = file_menu.addAction("📌 Pin current folder")
        pin_action.triggered.connect(self._on_pin_current_folder)
        self._pinned_menu = file_menu.addMenu("📌 Pinned folders")
        self._recent_menu = file_menu.addMenu("🕒 Recent folders")
        file_menu.addSeparator()
        refresh_action = file_menu.addAction("🔄 Refresh catalog")
        refresh_action.triggered.connect(self._on_refresh_catalog)
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

    def _category_family_id(self, category: str) -> str | None:
        if self._catalog is None:
            return None
        assigned = self._category_icons.get(category)
        if assigned:
            for family in self._catalog.icons:
                if family.id == assigned and category in family.categories:
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

    def _close_thumb_progress_toast(self) -> None:
        toast = self._thumb_progress_toast
        self._thumb_progress_toast = None
        if toast is not None:
            toast.close()

    def _close_variant_progress_toast(self) -> None:
        toast = self._variant_progress_toast
        self._variant_progress_toast = None
        if toast is not None:
            toast.close()

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

    def _load_from_config(self) -> None:
        config: dict[str, Any] = h.dev.config_load(get_config_path_str())
        candidates: list[Path] = []
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

    def _on_category_changed(self, text: str) -> None:
        self._current_category = None if text == ALL_CATEGORIES or not text else text
        self._apply_filters()

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
        try:
            mime.setText(path.read_text(encoding="utf-8"))
        except OSError:
            mime.setText(str(path.resolve()))
        clipboard = QApplication.clipboard()
        if clipboard is None:
            QMessageBox.warning(self, "Vector Icons", "Clipboard is not available.")
            return
        clipboard.setMimeData(mime)
        self.statusBar().showMessage(f"Copied `{path.name}`")

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
        if self._selected_family_id == family.id:
            self._selected_family_id = None
        self._on_refresh_catalog(allow_empty=True)
        self.statusBar().showMessage(f"Deleted `{family.id}`")

    def _on_family_selected(self, family: object) -> None:
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
        self.variants_panel.show_family(chosen, self._repo_root)
        self.statusBar().showMessage(f"{chosen.id}: {len(chosen.variants)} variants")

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

    def _on_icon_details(self, family: object, svg_path: str) -> None:
        if not isinstance(family, IconFamily):
            return
        note = family.note_path(self._repo_root) if self._repo_root is not None else None
        source = self._resolve_source_file(family, svg_path)
        variants = "\n".join(f"  - {variant.name} ({variant.file})" for variant in family.variants) or "  —"

        data = [
            ("ID", str(family.id)),
            ("Title", str(family.title)),
            ("Date", str(family.date or "—")),
            ("Categories", ", ".join(family.categories) or "—"),
            ("Tags", ", ".join(family.tags) or "—"),
            ("Folder", str(family.folder)),
            ("Note", str(note if note is not None else "—")),
            ("Source", str(source if source is not None else "—")),
            ("Featured", str(family.featured or "—")),
            ("Featured hash", str(family.featured_hash or "—")),
            ("Selected SVG", str(svg_path)),
            (f"Variants ({len(family.variants)})", variants),
        ]

        dialog = KeyValueTableDialog(self, "Icon details", data)
        dialog.exec()

    def _on_icon_size_changed(self, value: int) -> None:
        self._apply_icon_size(value)
        self._icon_size_save_timer.start()

    def _on_open_folder(self) -> None:
        start = str(self._repo_root) if self._repo_root is not None else ""
        chosen = QFileDialog.getExistingDirectory(self, "Open icons folder", start)
        if not chosen:
            return
        self._open_folder(Path(chosen))

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

    def _on_refresh_catalog(self, *, allow_empty: bool = False) -> None:
        if self._repo_root is None:
            self._load_from_config()
            return
        root = self._repo_root
        try:
            if self._catalog is not None and self._catalog.kind == "flat":
                catalog = open_icons_folder(root)
            else:
                catalog = rebuild_catalog(root)
        except FileNotFoundError as exc:
            if allow_empty and self._catalog is not None and self._catalog.kind == "flat":
                catalog = IconCatalog(version=1, generated_at="", icons=[], repo_root=root, kind="flat")
            else:
                QMessageBox.critical(self, "Vector Icons", f"Failed to refresh catalog:\n{exc}")
                return
        except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
            QMessageBox.critical(self, "Vector Icons", f"Failed to refresh catalog:\n{exc}")
            return
        self._catalog = catalog
        self._repo_root = catalog.repo_root
        self._variant_pixmaps.clear()
        self._thumb_cache = ThumbnailCache(cache_dir=cache_dir_for_root(catalog.repo_root), size=DEFAULT_THUMB_SIZE)
        self._prime_pixmaps_from_cache()
        self._populate_categories()
        self._apply_filters()
        self._start_thumb_refresh()

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
        toast = self._thumb_progress_toast
        if toast is not None:
            toast.set_progress(updated, self._thumb_refresh_total)
        self._close_thumb_progress_toast()
        total = len(self._catalog.icons) if self._catalog else 0
        self.statusBar().showMessage(f"Thumbnails ready ({updated} updated, {total} total)")
        self._refresh_category_icons()

    def _on_thumb_progress(self, family_id: str, thumb_path: str) -> None:
        self._thumb_refresh_done += 1
        if self._thumb_progress_toast is not None:
            self._thumb_progress_toast.set_progress(self._thumb_refresh_done, self._thumb_refresh_total)
        pixmap = QPixmap(thumb_path)
        if pixmap.isNull():
            return
        self._pixmaps[family_id] = pixmap
        self.icon_list.update_family_pixmap(family_id, pixmap)
        if family_id in self._category_icons.values() or family_id in self._default_category_family_ids.values():
            self._refresh_category_icons()

    def _on_toggle_trademark(self, family: object) -> None:
        if not isinstance(family, IconFamily) or not self._repo_root:
            return

        md_path = self._repo_root / family.folder / f"{family.id}.md"
        if not md_path.is_file():
            return

        text = md_path.read_text(encoding="utf-8")
        match = re.match(r"^---\s*\n(.*?)\n---\s*\n?", text, re.DOTALL)
        if not match:
            return

        fm = match.group(1)
        is_trademark = getattr(family, "trademark", False)

        if is_trademark:
            new_fm_lines = [line for line in fm.splitlines() if not line.startswith("trademark:")]
            new_fm = "\n".join(new_fm_lines) + "\n"
        else:
            new_fm = fm.strip() + "\ntrademark: true\n"

        new_text = "---\n" + new_fm + "---\n" + text[match.end() :]
        md_path.write_text(new_text, encoding="utf-8")

        self._on_refresh_catalog()
        self.statusBar().showMessage(
            f"Trademark warning {'removed from' if is_trademark else 'added to'} `{family.id}`"
        )

    def _on_variant_view_changed(self, _index: int) -> None:
        mode = self.variant_view_combo.currentData()
        self._variant_view_mode = str(mode) if mode else MODE_FEATURED
        self._apply_filters()

    def _open_folder(self, path: Path, *, remember: bool = True) -> None:
        """Load a note-folder repo or flat icon dump and refresh the UI."""
        try:
            catalog = open_icons_folder(path)
        except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
            QMessageBox.critical(self, "Vector Icons", f"Failed to open folder:\n{exc}")
            return
        self._stop_thumb_refresh()
        self._close_variant_progress_toast()
        self._repo_root = catalog.repo_root
        self._catalog = catalog
        self._selected_family_id = None
        self._current_category = None
        self._variant_pixmaps.clear()
        self._thumb_cache = ThumbnailCache(cache_dir=cache_dir_for_root(catalog.repo_root), size=DEFAULT_THUMB_SIZE)
        if remember:
            remember_recent_folder(catalog.repo_root)
        self.setWindowTitle(f"Vector Icons — {catalog.repo_root.name}")
        self._prime_pixmaps_from_cache()
        self._populate_categories()
        self._apply_filters()
        self._start_thumb_refresh()
        self._sync_folder_combo()
        self._rebuild_folder_menus()
        kind = "flat dump" if catalog.kind == "flat" else "note repo"
        self.statusBar().showMessage(f"Opened {kind}: {catalog.repo_root} ({len(catalog.icons)} icons)")

    def _persist_icon_size(self) -> None:
        self._icon_size_save_timer.stop()
        save_icon_size(self.size_slider.value())

    def _pixmaps_for_entries(self, entries: list[GridEntry]) -> dict[str, QPixmap]:
        result: dict[str, QPixmap] = {}
        pending: list[Path] = []
        pending_keys: set[str] = set()

        for entry in entries:
            key = str(entry.svg_path)
            if key in result or key in pending_keys:
                continue
            featured = entry.family.featured_path(self._repo_root) if self._repo_root is not None else None
            if self._variant_view_mode == MODE_FEATURED or (
                featured is not None and entry.svg_path.resolve() == featured.resolve()
            ):
                cached = self._pixmaps.get(entry.family.id)
                if cached is not None and not cached.isNull():
                    result[key] = cached
                    continue
            session = self._variant_pixmaps.get(key)
            if session is not None and not session.isNull():
                result[key] = session
                continue
            pending.append(entry.svg_path)
            pending_keys.add(key)

        if not pending:
            return result

        toast: toast_progress_notification.ToastProgressNotification | None = None
        if len(pending) >= VARIANT_PROGRESS_TOAST_MIN:
            self._close_variant_progress_toast()
            toast = toast_progress_notification.ToastProgressNotification(
                "Rendering icon previews…",
                total=len(pending),
                parent=self,
            )
            self._variant_progress_toast = toast
            toast.start_countdown()
            toast.set_progress(0, len(pending))
            QApplication.processEvents(QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents)

        try:
            for index, svg_path in enumerate(pending, start=1):
                key = str(svg_path)
                image = render_icon_to_image(svg_path, self._icon_size)
                if image is not None:
                    pixmap = QPixmap.fromImage(image)
                    self._variant_pixmaps[key] = pixmap
                    result[key] = pixmap
                if toast is not None:
                    toast.set_progress(index, len(pending))
                    if index == len(pending) or index % VARIANT_RENDER_CHUNK == 0:
                        QApplication.processEvents(QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents)
        finally:
            self._close_variant_progress_toast()
        return result

    def _populate_categories(self) -> None:
        self.category_list.blockSignals(True)  # noqa: FBT003
        self.category_list.clear()
        self._default_category_family_ids.clear()
        all_item = QListWidgetItem(QIcon(":/assets/logo.svg"), ALL_CATEGORIES)
        self.category_list.addItem(all_item)
        if self._catalog is not None:
            for name in self._catalog.categories():
                families = self._catalog.filter_icons(category=name)
                if families:
                    self._default_category_family_ids[name] = families[0].id
                item = QListWidgetItem(name)
                item.setIcon(self._category_pixmap_icon(name))
                self.category_list.addItem(item)
        self.category_list.setCurrentRow(0)
        self.category_list.blockSignals(False)  # noqa: FBT003
        self._current_category = None

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

    def _restore_or_clear_selection(self, families: list[IconFamily]) -> None:
        """Keep selection if the family is still visible; otherwise select the first tile."""
        target_id = self._selected_family_id
        if target_id is None and families:
            target_id = families[0].id
        if target_id is None:
            self.variants_panel.clear_variants()
            return
        for index, family in enumerate(families):
            if family.id != target_id:
                continue
            item = self.icon_list.item(index)
            if item is None:
                break
            self.icon_list.blockSignals(True)  # noqa: FBT003
            self.icon_list.setCurrentItem(item)
            self.icon_list.blockSignals(False)  # noqa: FBT003
            self._on_family_selected(family)
            return
        self._selected_family_id = None
        self.variants_panel.clear_variants()

    def _start_thumb_refresh(self) -> None:
        if self._catalog is None:
            return
        self._stop_thumb_refresh()
        self._thumb_refresh_done = 0
        self._thumb_refresh_total = sum(not self._thumb_cache.is_fresh(family) for family in self._catalog.icons)
        if self._thumb_refresh_total:
            self._thumb_progress_toast = toast_progress_notification.ToastProgressNotification(
                "Refreshing icon thumbnails…",
                total=self._thumb_refresh_total,
                parent=self,
            )
            self._thumb_progress_toast.start_countdown()
        self.statusBar().showMessage("Refreshing thumbnails in background…")
        self._thumb_thread, self._thumb_worker = start_thumbnail_refresh(
            self._catalog,
            self._thumb_cache,
            on_progress=self._on_thumb_progress,
            on_finished=self._on_thumb_finished,
        )

    def _stop_thumb_refresh(self) -> None:
        if self._thumb_worker is not None:
            self._thumb_worker.cancel()
        if self._thumb_thread is not None and self._thumb_thread.isRunning():
            self._thumb_thread.quit()
            self._thumb_thread.wait(3000)
        self._thumb_thread = None
        self._thumb_worker = None
        self._close_thumb_progress_toast()

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

    def _target_category_for_icon(self, family: IconFamily) -> str | None:
        if self._current_category and self._current_category in family.categories:
            return self._current_category
        return family.categories[0] if family.categories else None

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
        icon_list.copy_path_requested.connect(self._on_copy_path)
        icon_list.open_note_requested.connect(self._on_open_note_in_editor)
        icon_list.set_category_icon_requested.connect(self._on_set_as_category_icon)
        icon_list.toggle_trademark_requested.connect(self._on_toggle_trademark)
        icon_list.reveal_source_requested.connect(self._on_reveal_source)
        icon_list.open_source_requested.connect(self._on_open_source)
        icon_list.delete_requested.connect(self._on_delete_icon)
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
        self._selected_family_id: str | None = None
        self._category_icons = load_category_icons()
        self._default_category_family_ids: dict[str, str] = {}
        self._variant_view_mode = MODE_FEATURED
        self._variant_pixmaps: dict[str, QPixmap] = {}
        self._variant_progress_toast: toast_progress_notification.ToastProgressNotification | None = None
        self._thumb_progress_toast: toast_progress_notification.ToastProgressNotification | None = None
        self._thumb_refresh_done = 0
        self._thumb_refresh_total = 0
        self._icon_size_save_timer = QTimer(self)
        self._icon_size_save_timer.setSingleShot(True)
        self._icon_size_save_timer.setInterval(300)
        self._icon_size_save_timer.timeout.connect(self._persist_icon_size)

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
        self._persist_icon_size()
        if self._hide_instead_of_close(event):
            return
        self._close_variant_progress_toast()
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
