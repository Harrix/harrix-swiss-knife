---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `main.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `MainWindow`](#%EF%B8%8F-class-mainwindow)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `closeEvent`](#%EF%B8%8F-method-closeevent)
- [🔧 Function `main`](#-function-main)

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
    about_description = "Browse and drag SVG icon families from Harrix-Vector-Icons."

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
        self._stop_thumb_refresh()
        super().closeEvent(event)

    def _apply_filters(self) -> None:
        if self._catalog is None or self._repo_root is None:
            self.icon_list.clear()
            self.variants_panel.clear_variants()
            self.count_label.setText("0 icons")
            return
        query = self.search_edit.text()
        families = self._catalog.filter_icons(category=self._current_category, query=query)
        self.icon_list.set_family_items(families, pixmaps=self._pixmaps, placeholder=self._placeholder)
        for index in range(self.icon_list.count()):
            item = self.icon_list.item(index)
            if item is None:
                continue
            family = item.data(Qt.ItemDataRole.UserRole)
            if not isinstance(family, IconFamily):
                continue
            featured = family.featured_path(self._repo_root)
            if featured is None and family.variants:
                featured = family.variants[0].absolute_path(self._repo_root, family.folder)
            if featured is not None:
                item.setData(Qt.ItemDataRole.UserRole + 1, str(featured))
        self.count_label.setText(f"{len(families)} icons")
        self.statusBar().showMessage(f"Showing {len(families)} / {len(self._catalog.icons)}")
        self._restore_or_clear_selection(families)

    def _apply_icon_size(self, size: int) -> None:
        """Apply display size to grids without writing config."""
        self._icon_size = size
        self._placeholder = placeholder_pixmap(size)
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

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search icons (title, tags, id)…")
        self.search_edit.textChanged.connect(self._apply_filters)
        toolbar.addWidget(self.search_edit, stretch=1)

        self.refresh_btn = QPushButton("Refresh catalog")
        self.refresh_btn.clicked.connect(self._on_refresh_catalog)
        toolbar.addWidget(self.refresh_btn)
        root.addLayout(toolbar)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.category_list = QListWidget()
        self.category_list.setMinimumWidth(160)
        self.category_list.setMaximumWidth(260)
        self.category_list.currentTextChanged.connect(self._on_category_changed)
        splitter.addWidget(self.category_list)

        center = QWidget()
        center_layout = QVBoxLayout(center)
        center_layout.setContentsMargins(0, 0, 0, 0)
        self.count_label = QLabel("")
        center_layout.addWidget(self.count_label)
        self.icon_list = DraggableIconList(icon_size=self._icon_size)
        self.icon_list.family_selected.connect(self._on_family_selected)
        center_layout.addWidget(self.icon_list)
        splitter.addWidget(center)

        self.variants_panel = VariantsPanel(thumb_size=self._variant_thumb_size(self._icon_size))
        self.variants_panel.setMinimumWidth(220)
        splitter.addWidget(self.variants_panel)

        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 0)
        splitter.setSizes([200, 900, 320])
        root.addWidget(splitter)

        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Ready")

        file_menu = self.menuBar().addMenu("&File")
        refresh_action = file_menu.addAction("Refresh catalog")
        refresh_action.triggered.connect(self._on_refresh_catalog)
        file_menu.addSeparator()
        exit_action = file_menu.addAction("E&xit")
        exit_action.triggered.connect(self.close)
        help_menu = self.menuBar().addMenu("&Help")
        about_action = help_menu.addAction("&About")
        about_action.triggered.connect(self.on_about)

    def _load_from_config(self) -> None:
        config: dict[str, Any] = h.dev.config_load(get_config_path_str())
        raw = str(config.get("path_vector_icons") or "").strip()
        if not raw or raw.startswith("<"):
            QMessageBox.warning(
                self,
                "Vector Icons",
                "Set `path_vector_icons` in config.json to the Harrix-Vector-Icons repository root.",
            )
            self.statusBar().showMessage("path_vector_icons is not configured")
            return
        repo = Path(raw)
        if not repo.is_dir():
            QMessageBox.warning(self, "Vector Icons", f"Folder not found:\n{repo}")
            return
        self._repo_root = repo
        try:
            if not (repo / "catalog.json").is_file() and (repo / "icons").is_dir():
                self._catalog = rebuild_catalog(repo)
            else:
                self._catalog = load_catalog(repo)
        except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
            QMessageBox.critical(self, "Vector Icons", f"Failed to load catalog:\n{exc}")
            return
        self._prime_pixmaps_from_cache()
        self._populate_categories()
        self._apply_filters()
        self._start_thumb_refresh()

    def _on_category_changed(self, text: str) -> None:
        self._current_category = None if text == ALL_CATEGORIES or not text else text
        self._apply_filters()

    def _on_family_selected(self, family: object) -> None:
        if family is None:
            self._selected_family_id = None
            self.variants_panel.clear_variants()
            return
        if not isinstance(family, IconFamily) or self._repo_root is None:
            return
        self._selected_family_id = family.id
        self.variants_panel.show_family(family, self._repo_root)
        self.statusBar().showMessage(f"{family.id}: {len(family.variants)} variants")

    def _on_icon_size_changed(self, value: int) -> None:
        self._apply_icon_size(value)
        self._icon_size_save_timer.start()

    def _on_refresh_catalog(self) -> None:
        if self._repo_root is None:
            self._load_from_config()
            return
        try:
            self._catalog = rebuild_catalog(self._repo_root)
        except OSError as exc:
            QMessageBox.critical(self, "Vector Icons", f"Failed to rebuild catalog:\n{exc}")
            return
        self._prime_pixmaps_from_cache()
        self._populate_categories()
        self._apply_filters()
        self._start_thumb_refresh()

    def _on_thumb_finished(self, updated: int) -> None:
        total = len(self._catalog.icons) if self._catalog else 0
        self.statusBar().showMessage(f"Thumbnails ready ({updated} updated, {total} total)")

    def _on_thumb_progress(self, family_id: str, thumb_path: str) -> None:
        pixmap = QPixmap(thumb_path)
        if pixmap.isNull():
            return
        self._pixmaps[family_id] = pixmap
        self.icon_list.update_family_pixmap(family_id, pixmap)

    def _persist_icon_size(self) -> None:
        self._icon_size_save_timer.stop()
        save_icon_size(self.size_slider.value())

    def _populate_categories(self) -> None:
        self.category_list.blockSignals(True)  # noqa: FBT003
        self.category_list.clear()
        self.category_list.addItem(ALL_CATEGORIES)
        if self._catalog is not None:
            for name in self._catalog.categories():
                self.category_list.addItem(name)
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

    def _restore_or_clear_selection(self, families: list[IconFamily]) -> None:
        """Keep selection if the family is still visible; otherwise clear variants."""
        if self._selected_family_id is None:
            self.variants_panel.clear_variants()
            return
        for index, family in enumerate(families):
            if family.id != self._selected_family_id:
                continue
            item = self.icon_list.item(index)
            if item is not None:
                self.icon_list.setCurrentItem(item)
            return
        self._selected_family_id = None
        self.variants_panel.clear_variants()

    def _start_thumb_refresh(self) -> None:
        if self._catalog is None:
            return
        self._stop_thumb_refresh()
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

    @staticmethod
    def _variant_thumb_size(icon_size: int) -> int:
        return max(ICON_SIZE_MIN, min(icon_size, (icon_size * 3) // 4 or icon_size))
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
