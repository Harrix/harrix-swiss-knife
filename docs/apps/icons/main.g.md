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

    def __init__(self, hide_on_close: bool = False) -> None:  # noqa: FBT001, FBT002
        """Build the browser UI and load catalog from config path."""
        super().__init__()
        self._hide_on_close = hide_on_close
        self.setWindowTitle("Vector Icons")
        self.setWindowIcon(QIcon(":/assets/logo.svg"))
        self.resize(1100, 720)

        self._catalog: IconCatalog | None = None
        self._repo_root: Path | None = None
        self._thumb_cache = ThumbnailCache(size=DEFAULT_THUMB_SIZE)
        self._pixmaps: dict[str, QPixmap] = {}
        self._placeholder = placeholder_pixmap(DEFAULT_THUMB_SIZE)
        self._thumb_thread = None
        self._thumb_worker = None
        self._current_category: str | None = None

        self._build_ui()
        try_apply_system_backdrop(self)
        self._load_from_config()

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        """Stop background work and optionally hide instead of closing."""
        self._stop_thumb_refresh()
        if self._hide_on_close:
            event.ignore()
            self.hide()
            return
        super().closeEvent(event)

    def _apply_filters(self) -> None:
        if self._catalog is None or self._repo_root is None:
            self.icon_list.clear()
            self.count_label.setText("0 icons")
            return
        query = self.search_edit.text()
        families = self._catalog.filter_icons(category=self._current_category, query=query)
        self.icon_list.set_family_items(families, pixmaps=self._pixmaps, placeholder=self._placeholder)
        # Attach featured SVG paths for drag-out
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

    def _build_ui(self) -> None:
        central = QWidget(self)
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        toolbar = QHBoxLayout()
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
        self.category_list.setMaximumWidth(220)
        self.category_list.currentTextChanged.connect(self._on_category_changed)
        splitter.addWidget(self.category_list)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        self.count_label = QLabel("")
        right_layout.addWidget(self.count_label)
        self.icon_list = DraggableIconList(icon_size=DEFAULT_THUMB_SIZE)
        self.icon_list.family_activated.connect(self._on_family_activated)
        right_layout.addWidget(self.icon_list)
        splitter.addWidget(right)
        splitter.setStretchFactor(1, 1)
        root.addWidget(splitter)

        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Ready")

        # Simple menu
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

    def _on_family_activated(self, family: object) -> None:
        if not isinstance(family, IconFamily) or self._repo_root is None:
            return
        dialog = VariantsDialog(family, self._repo_root, self)
        dialog.exec()

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
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, hide_on_close: bool = False) -> None
```

Build the browser UI and load catalog from config path.

<details>
<summary>Code:</summary>

```python
def __init__(self, hide_on_close: bool = False) -> None:  # noqa: FBT001, FBT002
        super().__init__()
        self._hide_on_close = hide_on_close
        self.setWindowTitle("Vector Icons")
        self.setWindowIcon(QIcon(":/assets/logo.svg"))
        self.resize(1100, 720)

        self._catalog: IconCatalog | None = None
        self._repo_root: Path | None = None
        self._thumb_cache = ThumbnailCache(size=DEFAULT_THUMB_SIZE)
        self._pixmaps: dict[str, QPixmap] = {}
        self._placeholder = placeholder_pixmap(DEFAULT_THUMB_SIZE)
        self._thumb_thread = None
        self._thumb_worker = None
        self._current_category: str | None = None

        self._build_ui()
        try_apply_system_backdrop(self)
        self._load_from_config()
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
        self._stop_thumb_refresh()
        if self._hide_on_close:
            event.ignore()
            self.hide()
            return
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
