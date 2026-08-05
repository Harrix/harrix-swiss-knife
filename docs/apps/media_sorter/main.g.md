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
  - [⚙️ Method `keyPressEvent`](#%EF%B8%8F-method-keypressevent)

</details>

## 🏛️ Class `MainWindow`

```python
class MainWindow(QMainWindow, window.Ui_MainWindow, AppWindowMixin)
```

Main window for sorting media files into destination bins.

<details>
<summary>Code:</summary>

```python
class MainWindow(QMainWindow, window.Ui_MainWindow, AppWindowMixin):

    about_app_name = "Media Sorter"
    about_description = "Sort photos and videos into destination bins from config.json."

    def __init__(self, *, hide_on_close: bool = False) -> None:  # noqa: D107
        super().__init__()
        try_apply_system_backdrop(self, backdrop=SystemBackdrop.MICA)
        self.setupUi(self)
        self.setWindowIcon(QIcon(":/assets/logo.svg"))
        self._init_hide_on_close(hide_on_close=hide_on_close)

        self.db_manager: database_manager.DatabaseManager | None = None
        self._app_config: dict[str, Any] = h.dev.config_load(get_config_path_str())
        self._bins: list[BinConfig] = []
        self._working_folder: Path | None = None
        self._all_media: list[Path] = []
        self._random_deck: list[Path] = []
        self._random_index: int = 0
        self._current_path: Path | None = None
        self._reviewed_cache: set[str] = set()
        self._bin_frames: list[QFrame] = []

        self._replace_random_preview_label()
        self._init_database()
        self._load_bins_from_config()
        self._connect_signals()
        self._setup_explorer_widgets()
        self._setup_window_size_and_position(standard_width=1400)

        default = self._default_folder_from_config()
        if default is not None:
            self._set_working_folder(default)
        else:
            self._update_stats_label()
            self._set_status("Choose a working folder to begin.")

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        """Close database when the window is destroyed."""
        if getattr(self, "_hide_on_close", False):
            event.ignore()
            self.hide()
            return
        if self.db_manager is not None:
            self.db_manager.close()
            self.db_manager = None
        super().closeEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        """Keyboard shortcuts for Random mode."""
        key = event.key()
        if key in (Qt.Key.Key_Right, Qt.Key.Key_Space):
            self._on_next()
            return
        if key == Qt.Key.Key_Delete:
            self._on_delete()
            return
        super().keyPressEvent(event)

    def _after_review_advance(self, path: Path) -> None:
        """After review without removing the file from disk (copy / mark reviewed)."""
        if self.checkBox_unreviewed_only.isChecked():
            self._remove_path_from_ui(path)
        elif self.radioButton_random.isChecked():
            self._on_next()
        self._update_stats_label()

    def _assign_paths_to_bin(self, paths: list[str], bin_config: BinConfig) -> None:
        if self.db_manager is None:
            return
        moved_any = False
        for path in paths:
            if not is_media_path(path):
                continue
            result = assign_to_bin(path, bin_config, self.db_manager)
            if not result.ok:
                message_box.critical(self, "Bin error", result.error or "Unknown error")
                continue
            self._reviewed_cache.add(normalize_media_path(result.source_path))
            if result.dest_path and result.effective_mode == "move":
                self._reviewed_cache.add(normalize_media_path(result.dest_path))
                self._remove_path_from_ui(Path(result.source_path), next_path=Path(result.dest_path))
                moved_any = True
            elif self.radioButton_random.isChecked():
                # Stay on the file so it can be dropped into more bins (copy mode).
                self._show_current_random()
            mode_label = result.effective_mode
            self._set_status(f"{Path(result.source_path).name} → {bin_config.title} ({mode_label})")
        self._refresh_reviewed_cache()
        self._update_stats_label()
        if self.radioButton_explorer.isChecked() and moved_any:
            self._populate_explorer_files()

    def _connect_signals(self) -> None:
        self.actionExit.triggered.connect(self.on_exit)
        self.actionAbout.triggered.connect(self.on_about)
        self.pushButton_browse.clicked.connect(self._on_browse)
        self.pushButton_reload.clicked.connect(self._on_reload)
        self.pushButton_next.clicked.connect(self._on_next)
        self.pushButton_mark_reviewed.clicked.connect(self._on_mark_reviewed)
        self.pushButton_delete.clicked.connect(self._on_delete)
        self.radioButton_random.toggled.connect(self._on_mode_changed)
        self.radioButton_explorer.toggled.connect(self._on_mode_changed)
        self.checkBox_unreviewed_only.toggled.connect(self._on_unreviewed_toggled)
        self.treeWidget_folders.currentItemChanged.connect(self._on_folder_selected)
        self.listWidget_files.itemSelectionChanged.connect(self._on_explorer_selection_changed)
        self.listWidget_files.itemDoubleClicked.connect(self._on_explorer_open)

    def _current_selected_paths(self) -> list[Path]:
        if self.radioButton_explorer.isChecked():
            paths: list[Path] = []
            for item in self.listWidget_files.selectedItems():
                raw = item.data(_PATH_ROLE)
                if raw:
                    paths.append(Path(str(raw)))
            return paths
        if self._current_path is not None:
            return [self._current_path]
        return []

    def _default_folder_from_config(self) -> Path | None:
        media_cfg = self._app_config.get("media_sorter") or {}
        raw = ""
        if isinstance(media_cfg, dict):
            raw = str(media_cfg.get("default_folder") or "").strip()
        if not raw or raw.startswith("<YOUR_"):
            raw = str(self._app_config.get("path_photos") or "").strip()
        if not raw or raw.startswith("<YOUR_"):
            return None
        path = Path(raw).expanduser()
        return path if path.is_dir() else None

    def _fill_tree_children(self, parent_item: QTreeWidgetItem, folder: Path) -> None:
        for sub in list_immediate_subdirs(folder):
            child = QTreeWidgetItem([sub.name])
            child.setData(0, _PATH_ROLE, str(sub.resolve()))
            parent_item.addChild(child)
            self._fill_tree_children(child, sub)

    def _init_database(self) -> None:
        app_dir = Path(__file__).parent
        raw_db = str(self._app_config.get("sqlite_media_sorter") or "").strip()
        if not raw_db or raw_db.startswith("<YOUR_"):
            configured = h.dev.get_project_root() / "data" / "databases" / "media_sorter.db"
        else:
            configured = Path(raw_db)
        self.db_manager = init_tracker_database(
            self,
            configured,
            "media_sorter",
            app_dir / "recover.sql",
            database_manager.DatabaseManager,
            has_required_tables=lambda dm: dm.table_exists("reviewed_files"),
            missing_table_label="reviewed_files table",
        )

    def _load_bins_from_config(self) -> None:
        media_cfg = self._app_config.get("media_sorter")
        self._bins = parse_bins_from_config(media_cfg if isinstance(media_cfg, dict) else None)
        layout = self.verticalLayout_bins
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self._bin_frames.clear()
        if not self._bins:
            empty = QLabel("No bins in config.json\n(media_sorter.bins)")
            empty.setWordWrap(True)
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(empty)
            layout.addStretch(1)
            return
        for bin_config in self._bins:
            frame = self._make_bin_frame(bin_config)
            layout.addWidget(frame)
            self._bin_frames.append(frame)
        layout.addStretch(1)

    def _make_bin_frame(self, bin_config: BinConfig) -> QFrame:
        frame = QFrame()
        frame.setObjectName("binDropFrame")
        frame.setStyleSheet(_BIN_DROP_STYLE)
        outer = QVBoxLayout(frame)
        title = QLabel(f"{bin_config.title}")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = title.font()
        font.setBold(True)
        title.setFont(font)
        meta = QLabel(f"{bin_config.mode} → {bin_config.path}")
        meta.setWordWrap(True)
        meta.setAlignment(Qt.AlignmentFlag.AlignCenter)
        meta.setStyleSheet("color: palette(mid);")
        btn_row = QHBoxLayout()
        send_btn = QPushButton(f"Send here ({bin_config.mode})")
        send_btn.clicked.connect(partial(self._on_send_to_bin, bin_config))
        btn_row.addWidget(send_btn)
        outer.addWidget(title)
        outer.addWidget(meta)
        outer.addLayout(btn_row)
        install_url_drop_handlers(
            frame,
            partial(self._assign_paths_to_bin, bin_config=bin_config),
            filter_path=is_media_path,
        )
        return frame

    def _on_browse(self) -> None:
        start = str(self._working_folder or Path.home())
        chosen = QFileDialog.getExistingDirectory(self, "Select working folder", start)
        if chosen:
            self._set_working_folder(Path(chosen))

    def _on_delete(self) -> None:
        if self.db_manager is None:
            return
        paths = self._current_selected_paths()
        if not paths:
            return
        confirm = QMessageBox.question(
            self,
            "Delete",
            f"Move {len(paths)} file(s) to the Recycle Bin?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return
        for path in paths:
            ok, err = trash_file(path, self.db_manager)
            if not ok:
                message_box.critical(self, "Delete failed", err or "Unknown error")
                continue
            self._reviewed_cache.add(normalize_media_path(path))
            self._remove_path_from_ui(path)
            self._set_status(f"Deleted: {path.name}")
        self._refresh_reviewed_cache()
        self._update_stats_label()

    def _on_explorer_open(self, item: QListWidgetItem) -> None:
        raw = item.data(_PATH_ROLE)
        if not raw:
            return
        path = Path(str(raw))
        if path.is_file():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))

    def _on_explorer_selection_changed(self) -> None:
        items = self.listWidget_files.selectedItems()
        if not items:
            return
        raw = items[0].data(_PATH_ROLE)
        if raw:
            self._current_path = Path(str(raw))

    def _on_folder_selected(self, current: QTreeWidgetItem | None, _previous: QTreeWidgetItem | None) -> None:
        if current is None:
            return
        raw = current.data(0, _PATH_ROLE)
        if raw:
            self._populate_explorer_files(Path(str(raw)))

    def _on_mark_reviewed(self) -> None:
        if self.db_manager is None:
            return
        paths = self._current_selected_paths()
        if not paths:
            return
        for path in paths:
            live = resolve_working_path(path, self.db_manager)
            self.db_manager.mark_reviewed(live)
            self._reviewed_cache.add(normalize_media_path(live))
            self._after_review_advance(live)
        self._update_stats_label()
        self._set_status(f"Marked reviewed: {len(paths)}")

    def _on_mode_changed(self, *_args: object) -> None:
        if self.radioButton_random.isChecked():
            self.stackedWidget_center.setCurrentWidget(self.page_random)
            self.pushButton_next.setEnabled(True)
            self._show_current_random()
        else:
            self.stackedWidget_center.setCurrentWidget(self.page_explorer)
            self.pushButton_next.setEnabled(False)
            self._populate_folder_tree()

    def _on_next(self) -> None:
        if not self.radioButton_random.isChecked():
            return
        if not self._random_deck:
            self._set_status("No media in the random deck.")
            return
        self._random_index = (self._random_index + 1) % len(self._random_deck)
        self._show_current_random()
        self._set_status("Skipped (not marked reviewed)")

    def _on_reload(self) -> None:
        if self._working_folder is not None:
            self._set_working_folder(self._working_folder)

    def _on_send_to_bin(self, bin_config: BinConfig) -> None:
        paths = [str(p) for p in self._current_selected_paths()]
        if not paths:
            self._set_status("Nothing selected to send.")
            return
        self._assign_paths_to_bin(paths, bin_config)

    def _on_unreviewed_toggled(self, *_args: object) -> None:
        self._rebuild_random_deck()
        if self.radioButton_explorer.isChecked():
            self._populate_explorer_files()
        else:
            self._show_current_random()
        self._update_stats_label()

    def _populate_explorer_files(self, folder: Path | None = None) -> None:
        self.listWidget_files.clear()
        if folder is None:
            item = self.treeWidget_folders.currentItem()
            if item is None:
                return
            raw = item.data(0, _PATH_ROLE)
            if not raw:
                return
            folder = Path(str(raw))
        files = list_media_in_folder(folder, recursive=False)
        if self.checkBox_unreviewed_only.isChecked():
            files = [p for p in files if normalize_media_path(p) not in self._reviewed_cache]
        for path in files:
            item = QListWidgetItem()
            item.setData(_PATH_ROLE, str(path.resolve()))
            item.setText(path.name)
            item.setToolTip(str(path))
            thumb = load_media_thumbnail(path, _THUMB_SIZE)
            if thumb is not None:
                item.setIcon(QIcon(thumb))
            elif is_video_path(path):
                item.setText(f"▶ {path.name}")
            item.setSizeHint(QSize(_THUMB_SIZE + 24, _THUMB_SIZE + 36))
            self.listWidget_files.addItem(item)

    def _populate_folder_tree(self) -> None:
        self.treeWidget_folders.clear()
        if self._working_folder is None or not self._working_folder.is_dir():
            return
        root_item = QTreeWidgetItem([self._working_folder.name or str(self._working_folder)])
        root_item.setData(0, _PATH_ROLE, str(self._working_folder.resolve()))
        self.treeWidget_folders.addTopLevelItem(root_item)
        self._fill_tree_children(root_item, self._working_folder)
        root_item.setExpanded(True)
        self.treeWidget_folders.setCurrentItem(root_item)

    def _rebuild_random_deck(self) -> None:
        files = list(self._all_media)
        if self.checkBox_unreviewed_only.isChecked():
            files = [p for p in files if normalize_media_path(p) not in self._reviewed_cache]
        random.shuffle(files)
        self._random_deck = files
        self._random_index = 0
        if self._random_deck:
            self._current_path = self._random_deck[0]
        else:
            self._current_path = None

    def _refresh_reviewed_cache(self) -> None:
        if self.db_manager is None:
            self._reviewed_cache = set()
            return
        self._reviewed_cache = self.db_manager.list_reviewed_paths()

    def _remove_path_from_ui(self, path: Path, *, next_path: Path | None = None) -> None:
        norm = normalize_media_path(path)
        self._all_media = [p for p in self._all_media if normalize_media_path(p) != norm]
        self._random_deck = [p for p in self._random_deck if normalize_media_path(p) != norm]
        if self._random_deck:
            self._random_index %= len(self._random_deck)
            self._current_path = (
                next_path if next_path and next_path.is_file() else self._random_deck[self._random_index]
            )
            if next_path and next_path.is_file() and next_path not in self._random_deck:
                # Moved out of working tree — advance within deck
                self._current_path = self._random_deck[self._random_index]
        else:
            self._current_path = None
        if self.radioButton_random.isChecked():
            self._show_current_random()
        else:
            self._populate_explorer_files()

    def _replace_random_preview_label(self) -> None:
        old = self.label_random_preview
        layout = self.verticalLayout_random
        idx = layout.indexOf(old)
        preview = _DraggablePreviewLabel(self.page_random)
        preview.setObjectName("label_random_preview")
        preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview.setMinimumSize(200, 200)
        preview.setText("Select a folder to begin")
        preview.setScaledContents(False)
        layout.removeWidget(old)
        old.deleteLater()
        layout.insertWidget(idx if idx >= 0 else 1, preview)
        self.label_random_preview = preview  # type: ignore[assignment]

    def _set_status(self, text: str) -> None:
        self.label_status.setText(text)

    def _set_working_folder(self, folder: Path) -> None:
        self._working_folder = folder.resolve()
        self.lineEdit_folder.setText(str(self._working_folder))
        self._refresh_reviewed_cache()
        self._all_media = iter_media_files(self._working_folder)
        self._rebuild_random_deck()
        if self.radioButton_explorer.isChecked():
            self._populate_folder_tree()
        else:
            self.stackedWidget_center.setCurrentWidget(self.page_random)
            self._show_current_random()
        self._update_stats_label()
        self._set_status(f"Loaded {len(self._all_media)} media file(s)")

    def _setup_explorer_widgets(self) -> None:
        self.listWidget_files.setIconSize(QSize(_THUMB_SIZE, _THUMB_SIZE))
        self.listWidget_files.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.listWidget_files.setDragEnabled(True)
        self.listWidget_files.setDefaultDropAction(Qt.DropAction.CopyAction)
        self.treeWidget_folders.setHeaderHidden(True)

    def _show_current_random(self) -> None:
        preview = self.label_random_preview
        if not self._random_deck:
            self._current_path = None
            self.label_random_name.setText("No media")
            if isinstance(preview, _DraggablePreviewLabel):
                preview.set_drag_path(None)
            preview.clear()
            preview.setText("No unreviewed media in this folder")
            preview.setPixmap(QPixmap())
            return
        self._random_index = max(0, min(self._random_index, len(self._random_deck) - 1))
        path = self._random_deck[self._random_index]
        self._current_path = path
        bins_note = ""
        if self.db_manager is not None:
            bin_ids = self.db_manager.get_bin_ids_for_path(path)
            if bin_ids:
                bins_note = f" · bins: {', '.join(sorted(bin_ids))}"
        self.label_random_name.setText(
            f"{path.name}  ({self._random_index + 1}/{len(self._random_deck)}){bins_note}\n{path}",
        )
        thumb = load_media_thumbnail(path, _PREVIEW_MAX)
        if isinstance(preview, _DraggablePreviewLabel):
            preview.set_drag_path(str(path.resolve()))
        if thumb is not None:
            preview.setPixmap(thumb)
            preview.setText("")
        else:
            preview.setPixmap(QPixmap())
            kind = "Video" if is_video_path(path) else "Image"
            preview.setText(f"{kind}\n{path.name}\n(no preview)")

    def _update_stats_label(self) -> None:
        total = len(self._all_media)
        reviewed_in_folder = sum(1 for p in self._all_media if normalize_media_path(p) in self._reviewed_cache)
        remaining = total - reviewed_in_folder
        db_reviewed = self.db_manager.reviewed_count() if self.db_manager else 0
        self.label_stats.setText(
            f"In folder: {total} · Reviewed here: {reviewed_in_folder} · "
            f"Remaining: {remaining} · DB reviewed: {db_reviewed}",
        )
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def __init__(self, *, hide_on_close: bool = False) -> None:  # noqa: D107
        super().__init__()
        try_apply_system_backdrop(self, backdrop=SystemBackdrop.MICA)
        self.setupUi(self)
        self.setWindowIcon(QIcon(":/assets/logo.svg"))
        self._init_hide_on_close(hide_on_close=hide_on_close)

        self.db_manager: database_manager.DatabaseManager | None = None
        self._app_config: dict[str, Any] = h.dev.config_load(get_config_path_str())
        self._bins: list[BinConfig] = []
        self._working_folder: Path | None = None
        self._all_media: list[Path] = []
        self._random_deck: list[Path] = []
        self._random_index: int = 0
        self._current_path: Path | None = None
        self._reviewed_cache: set[str] = set()
        self._bin_frames: list[QFrame] = []

        self._replace_random_preview_label()
        self._init_database()
        self._load_bins_from_config()
        self._connect_signals()
        self._setup_explorer_widgets()
        self._setup_window_size_and_position(standard_width=1400)

        default = self._default_folder_from_config()
        if default is not None:
            self._set_working_folder(default)
        else:
            self._update_stats_label()
            self._set_status("Choose a working folder to begin.")
```

</details>

### ⚙️ Method `closeEvent`

```python
def closeEvent(self, event: QCloseEvent) -> None
```

Close database when the window is destroyed.

<details>
<summary>Code:</summary>

```python
def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        if getattr(self, "_hide_on_close", False):
            event.ignore()
            self.hide()
            return
        if self.db_manager is not None:
            self.db_manager.close()
            self.db_manager = None
        super().closeEvent(event)
```

</details>

### ⚙️ Method `keyPressEvent`

```python
def keyPressEvent(self, event: QKeyEvent) -> None
```

Keyboard shortcuts for Random mode.

<details>
<summary>Code:</summary>

```python
def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        key = event.key()
        if key in (Qt.Key.Key_Right, Qt.Key.Key_Space):
            self._on_next()
            return
        if key == Qt.Key.Key_Delete:
            self._on_delete()
            return
        super().keyPressEvent(event)
```

</details>
