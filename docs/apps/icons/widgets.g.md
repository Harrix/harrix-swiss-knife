---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `widgets.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `CategoryDropList`](#%EF%B8%8F-class-categorydroplist)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `dragEnterEvent`](#%EF%B8%8F-method-dragenterevent)
  - [⚙️ Method `dragMoveEvent`](#%EF%B8%8F-method-dragmoveevent)
  - [⚙️ Method `dropEvent`](#%EF%B8%8F-method-dropevent)
- [🏛️ Class `DraggableIconList`](#%EF%B8%8F-class-draggableiconlist)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-1)
  - [⚙️ Method `append_grid_entries`](#%EF%B8%8F-method-append_grid_entries)
  - [⚙️ Method `keyPressEvent`](#%EF%B8%8F-method-keypressevent)
  - [⚙️ Method `preview_paths`](#%EF%B8%8F-method-preview_paths)
  - [⚙️ Method `reset_row_pixmaps`](#%EF%B8%8F-method-reset_row_pixmaps)
  - [⚙️ Method `resizeEvent`](#%EF%B8%8F-method-resizeevent)
  - [⚙️ Method `schedule_viewport_changed`](#%EF%B8%8F-method-schedule_viewport_changed)
  - [⚙️ Method `select_family`](#%EF%B8%8F-method-select_family)
  - [⚙️ Method `selected_file_paths`](#%EF%B8%8F-method-selected_file_paths)
  - [⚙️ Method `selected_keyword_targets`](#%EF%B8%8F-method-selected_keyword_targets)
  - [⚙️ Method `set_display_icon_size`](#%EF%B8%8F-method-set_display_icon_size)
  - [⚙️ Method `set_favorite_family_ids`](#%EF%B8%8F-method-set_favorite_family_ids)
  - [⚙️ Method `set_grid_entries`](#%EF%B8%8F-method-set_grid_entries)
  - [⚙️ Method `set_repo_root`](#%EF%B8%8F-method-set_repo_root)
  - [⚙️ Method `startDrag`](#%EF%B8%8F-method-startdrag)
  - [⚙️ Method `update_row_pixmaps`](#%EF%B8%8F-method-update_row_pixmaps)
  - [⚙️ Method `visible_row_span`](#%EF%B8%8F-method-visible_row_span)
- [🏛️ Class `IconLabelDelegate`](#%EF%B8%8F-class-iconlabeldelegate)
  - [⚙️ Method `paint`](#%EF%B8%8F-method-paint)
  - [⚙️ Method `sizeHint`](#%EF%B8%8F-method-sizehint)
- [🏛️ Class `VariantsPanel`](#%EF%B8%8F-class-variantspanel)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-2)
  - [⚙️ Method `clear_variants`](#%EF%B8%8F-method-clear_variants)
  - [⚙️ Method `current_family (property)`](#%EF%B8%8F-method-current_family-property)
  - [⚙️ Method `resizeEvent`](#%EF%B8%8F-method-resizeevent-1)
  - [⚙️ Method `set_thumb_size`](#%EF%B8%8F-method-set_thumb_size)
  - [⚙️ Method `show_family`](#%EF%B8%8F-method-show_family)
- [🔧 Function `batch_context_action_texts`](#-function-batch_context_action_texts)
- [🔧 Function `decode_family_ids_mime`](#-function-decode_family_ids_mime)
- [🔧 Function `encode_family_ids_mime`](#-function-encode_family_ids_mime)
- [🔧 Function `family_display_filename`](#-function-family_display_filename)
- [🔧 Function `is_svg_icon_path`](#-function-is_svg_icon_path)
- [🔧 Function `read_svg_text`](#-function-read_svg_text)

</details>

## 🏛️ Class `CategoryDropList`

```python
class CategoryDropList(QListWidget)
```

Category sidebar that accepts icon-family drops from the grid.

<details>
<summary>Code:</summary>

```python
class CategoryDropList(QListWidget):

    families_dropped = Signal(str, object)  # category, list[str]

    def __init__(self, parent: QWidget | None = None) -> None:
        """Enable drops of Vector Icons family IDs onto category rows."""
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.viewport().setAcceptDrops(True)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:  # noqa: N802
        """Accept internal icon-family drags."""
        if decode_family_ids_mime(event.mimeData()):
            event.acceptProposedAction()
            return
        event.ignore()

    def dragMoveEvent(self, event: QDragMoveEvent) -> None:  # noqa: N802
        """Allow a drop only when the cursor is over a category row."""
        if self.itemAt(event.position().toPoint()) is None or not decode_family_ids_mime(event.mimeData()):
            event.ignore()
            return
        event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:  # noqa: N802
        """Emit the target category and dropped family IDs."""
        item = self.itemAt(event.position().toPoint())
        family_ids = decode_family_ids_mime(event.mimeData())
        if item is None or not family_ids:
            event.ignore()
            return
        event.acceptProposedAction()
        self.families_dropped.emit(item.text(), family_ids)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Enable drops of Vector Icons family IDs onto category rows.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.viewport().setAcceptDrops(True)
```

</details>

### ⚙️ Method `dragEnterEvent`

```python
def dragEnterEvent(self, event: QDragEnterEvent) -> None
```

Accept internal icon-family drags.

<details>
<summary>Code:</summary>

```python
def dragEnterEvent(self, event: QDragEnterEvent) -> None:  # noqa: N802
        if decode_family_ids_mime(event.mimeData()):
            event.acceptProposedAction()
            return
        event.ignore()
```

</details>

### ⚙️ Method `dragMoveEvent`

```python
def dragMoveEvent(self, event: QDragMoveEvent) -> None
```

Allow a drop only when the cursor is over a category row.

<details>
<summary>Code:</summary>

```python
def dragMoveEvent(self, event: QDragMoveEvent) -> None:  # noqa: N802
        if self.itemAt(event.position().toPoint()) is None or not decode_family_ids_mime(event.mimeData()):
            event.ignore()
            return
        event.acceptProposedAction()
```

</details>

### ⚙️ Method `dropEvent`

```python
def dropEvent(self, event: QDropEvent) -> None
```

Emit the target category and dropped family IDs.

<details>
<summary>Code:</summary>

```python
def dropEvent(self, event: QDropEvent) -> None:  # noqa: N802
        item = self.itemAt(event.position().toPoint())
        family_ids = decode_family_ids_mime(event.mimeData())
        if item is None or not family_ids:
            event.ignore()
            return
        event.acceptProposedAction()
        self.families_dropped.emit(item.text(), family_ids)
```

</details>

## 🏛️ Class `DraggableIconList`

```python
class DraggableIconList(QListWidget)
```

Icon grid/list that drags the underlying SVG file URL outward.

<details>
<summary>Code:</summary>

```python
class DraggableIconList(QListWidget):

    family_selected = Signal(object)  # IconFamily | None
    reveal_requested = Signal(str)
    details_requested = Signal(object, str)  # IconFamily, svg_path
    copy_requested = Signal(str)
    copy_files_requested = Signal(object)  # list[str]
    copy_contents_requested = Signal(str)
    copy_filename_requested = Signal(str)
    copy_path_requested = Signal(str)
    open_note_requested = Signal(object)  # IconFamily
    edit_keywords_requested = Signal(object, str)  # IconFamily, svg_path
    reveal_source_requested = Signal(object, str)  # IconFamily, svg_path
    open_source_requested = Signal(object, str)  # IconFamily, svg_path
    set_category_icon_requested = Signal(object)  # IconFamily
    delete_requested = Signal(object)  # IconFamily
    toggle_trademark_requested = Signal(object)  # IconFamily
    favorite_toggled = Signal(object)  # IconFamily
    license_requested = Signal(str)
    preview_requested = Signal(str)
    batch_keywords_ai_requested = Signal(object)  # list[tuple[IconFamily, str]]
    batch_favorites_requested = Signal(object)  # (targets, add)
    viewport_changed = Signal()

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        icon_size: int = DEFAULT_THUMB_SIZE,
        emit_family_selection: bool = True,
        dual_line_labels: bool = False,
    ) -> None:
        """Configure icon mode and drag-only outward behavior."""
        super().__init__(parent)
        self._icon_size = icon_size
        self._emit_family_selection = emit_family_selection
        self._dual_line_labels = dual_line_labels
        self._favorite_family_ids: set[str] = set()
        self._repo_root: Path | None = None
        # family_id → first row, so thumbnail updates skip a full list scan.
        self._family_rows: dict[str, int] = {}
        self._viewport_timer = QTimer(self)
        self._viewport_timer.setSingleShot(True)
        self._viewport_timer.setInterval(VIEWPORT_SIGNAL_DEBOUNCE_MS)
        self._viewport_timer.timeout.connect(self.viewport_changed)
        self.setViewMode(QListWidget.ViewMode.IconMode)
        self.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.setMovement(QListWidget.Movement.Static)
        self.setUniformItemSizes(True)
        self.setWrapping(True)
        self.setFlow(QListWidget.Flow.LeftToRight)
        self.setWordWrap(True)
        self.setSpacing(8)
        self.setIconSize(QSize(icon_size, icon_size))
        self.setGridSize(self._grid_size_for(icon_size))
        self.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        # Pixel scrolling keeps the scrollbar value in sync with the grid geometry math.
        self.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setDragEnabled(True)
        self.setDragDropMode(QListWidget.DragDropMode.DragOnly)
        # DragOnly turns drops off; Explorer file drops still need the viewport.
        self.setAcceptDrops(True)
        self.viewport().setAcceptDrops(True)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._on_context_menu)
        self.itemDoubleClicked.connect(self._on_item_double_clicked)
        if dual_line_labels:
            self.setItemDelegate(IconLabelDelegate(self))
        if emit_family_selection:
            self.itemPressed.connect(self._emit_family_from_item)
            self.currentItemChanged.connect(self._on_current_item_changed)
        self.verticalScrollBar().valueChanged.connect(self.schedule_viewport_changed)

    def append_grid_entries(
        self,
        entries: list[GridEntry],
        *,
        pixmaps_by_path: dict[str, QPixmap],
        placeholder: QPixmap,
    ) -> None:
        """Add more variant-view tiles without rebuilding the grid."""
        if not entries:
            return
        self.blockSignals(True)  # noqa: FBT003
        self.setUpdatesEnabled(False)
        try:
            for entry in entries:
                self._add_grid_item(entry, pixmaps_by_path=pixmaps_by_path, placeholder=placeholder)
        finally:
            self.setUpdatesEnabled(True)
            self.blockSignals(False)  # noqa: FBT003

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        """Copy selected icon files when the standard Copy shortcut is pressed."""
        if event.matches(QKeySequence.StandardKey.Copy):
            paths = self.selected_file_paths()
            if paths:
                self.copy_files_requested.emit(paths)
                event.accept()
                return
        super().keyPressEvent(event)

    def preview_paths(self) -> list[Path]:
        """Return all existing icon paths in display order."""
        paths: list[Path] = []
        for index in range(self.count()):
            item = self.item(index)
            if item is None:
                continue
            raw = item.data(ROLE_SVG_PATH)
            if isinstance(raw, str) and raw:
                path = Path(raw)
                if path.is_file():
                    paths.append(path)
        return paths

    def reset_row_pixmaps(self, rows: list[int], *, placeholder: QPixmap) -> None:
        """Drop pixmaps of rows scrolled far away so memory stays bounded."""
        if not rows:
            return
        icon = QIcon(placeholder)
        self.setUpdatesEnabled(False)
        try:
            for row in rows:
                item = self.item(row)
                if item is not None:
                    item.setIcon(icon)
        finally:
            self.setUpdatesEnabled(True)

    def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        """Reflow tiles and ask the owner to reload pixmaps for the new visible rows."""
        super().resizeEvent(event)
        self.schedule_viewport_changed()

    def schedule_viewport_changed(self) -> None:
        """Ask for a debounced `viewport_changed` signal after scrolling or resizing."""
        self._viewport_timer.start()

    def select_family(self, family_id: str) -> bool:
        """Select the first tile for `family_id` and scroll it into view."""
        row = self._family_rows.get(family_id)
        item = self.item(row) if row is not None else None
        if item is None:
            return False
        self.setCurrentItem(item)
        self.scrollToItem(item, QAbstractItemView.ScrollHint.PositionAtCenter)
        return True

    def selected_file_paths(self) -> list[str]:
        """Return file paths of selected tiles, in display order."""
        paths: list[str] = []
        for index in range(self.count()):
            item = self.item(index)
            if item is None or not item.isSelected():
                continue
            raw = item.data(ROLE_SVG_PATH)
            if isinstance(raw, str) and raw:
                paths.append(raw)
        return paths

    def selected_keyword_targets(self) -> list[tuple[IconFamily, str]]:
        """Return unique selected families with an SVG path, in display order."""
        targets: list[tuple[IconFamily, str]] = []
        seen: set[str] = set()
        for index in range(self.count()):
            item = self.item(index)
            if item is None or not item.isSelected():
                continue
            family = item.data(Qt.ItemDataRole.UserRole)
            family_id = getattr(family, "id", None)
            if not isinstance(family_id, str) or family_id in seen:
                continue
            seen.add(family_id)
            path = item.data(ROLE_SVG_PATH)
            targets.append((family, path if isinstance(path, str) else ""))
        return targets

    def set_display_icon_size(self, icon_size: int) -> None:
        """Update icon and grid sizes used by the list."""
        self._icon_size = icon_size
        self.setIconSize(QSize(icon_size, icon_size))
        self.setGridSize(self._grid_size_for(icon_size))

    def set_favorite_family_ids(self, family_ids: set[str] | list[str]) -> None:
        """Update the favorite family IDs used by the context menu labels."""
        self._favorite_family_ids = {str(item).strip() for item in family_ids if str(item).strip()}

    def set_grid_entries(
        self,
        entries: list[GridEntry],
        *,
        pixmaps_by_path: dict[str, QPixmap],
        placeholder: QPixmap,
    ) -> None:
        """Rebuild the grid from variant-view entries and path→pixmap map."""
        self.blockSignals(True)  # noqa: FBT003
        self.clear()
        self._family_rows = {}
        for entry in entries:
            self._add_grid_item(entry, pixmaps_by_path=pixmaps_by_path, placeholder=placeholder)
        self.setCurrentRow(-1)
        self.blockSignals(False)  # noqa: FBT003

    def set_repo_root(self, repo_root: Path | None) -> None:
        """Remember the open icons folder for license lookup from notes."""
        self._repo_root = repo_root

    def startDrag(self, supported_actions: Qt.DropAction) -> None:  # noqa: ARG002, N802
        """Start a drag with family IDs (for Categories) and file URLs (for Explorer)."""
        targets = self.selected_keyword_targets()
        if not targets:
            return
        mime = QMimeData()
        encode_family_ids_mime(mime, [family.id for family, _path in targets])
        urls = [
            QUrl.fromLocalFile(str(Path(svg_path).resolve()))
            for _family, svg_path in targets
            if svg_path and Path(svg_path).is_file()
        ]
        if urls:
            mime.setUrls(urls)
        drag = QDrag(self)
        drag.setMimeData(mime)
        item = self.currentItem()
        if item is not None:
            icon = item.icon()
            if not icon.isNull():
                drag.setPixmap(icon.pixmap(64, 64))
                drag.setHotSpot(QPoint(32, 32))
        drag.exec(Qt.DropAction.CopyAction)

    def update_row_pixmaps(self, pixmaps: dict[int, QPixmap]) -> None:
        """Apply thumbnails for the given rows with a single repaint."""
        if not pixmaps:
            return
        self.setUpdatesEnabled(False)
        try:
            for row, pixmap in pixmaps.items():
                item = self.item(row)
                if item is None:
                    continue
                icon_pixmap = _muted_pixmap(pixmap, FALLBACK_ICON_OPACITY) if bool(item.data(ROLE_FALLBACK)) else pixmap
                item.setIcon(QIcon(icon_pixmap))
        finally:
            self.setUpdatesEnabled(True)

    def visible_row_span(self, margin_lines: int = 1) -> tuple[int, int]:
        """Return the row range currently on screen, padded by `margin_lines` grid lines.

        Tiles live in a fixed grid, so the range is derived from the scroll offset instead of
        hit-testing items, which stays exact even when the point falls between cells.

        """
        count = self.count()
        if count == 0:
            return (0, -1)
        grid = self.gridSize()
        cell_width = max(1, grid.width())
        cell_height = max(1, grid.height())
        viewport = self.viewport()
        columns = max(1, viewport.width() // cell_width)
        lines = viewport.height() // cell_height + 1
        top_line = max(0, self.verticalScrollBar().value() // cell_height)
        first = max(0, (top_line - margin_lines) * columns)
        last = min(count - 1, (top_line + lines + margin_lines) * columns - 1)
        # Hit-test the middle of the viewport as a safety net if the geometry math drifts.
        probe = self.indexAt(QPoint(viewport.width() // 2, viewport.height() // 2))
        if probe.isValid():
            reach = (lines + margin_lines) * columns
            first = min(first, max(0, probe.row() - reach))
            last = max(last, min(count - 1, probe.row() + reach))
        return (first, last)

    def _add_grid_item(
        self,
        entry: GridEntry,
        *,
        pixmaps_by_path: dict[str, QPixmap],
        placeholder: QPixmap,
    ) -> None:
        key = str(entry.svg_path)
        pixmap = pixmaps_by_path.get(key) or placeholder
        title = entry.family.title
        if entry.is_fallback:
            title = f"{entry.family.title} (no match)"
            pixmap = _muted_pixmap(pixmap, FALLBACK_ICON_OPACITY)
        item = QListWidgetItem(QIcon(pixmap), title)
        item.setData(Qt.ItemDataRole.UserRole, entry.family)
        item.setData(ROLE_SVG_PATH, key)
        item.setData(ROLE_SUBTITLE, family_display_filename(entry.family, entry.svg_path))
        item.setData(ROLE_FALLBACK, entry.is_fallback)
        item.setData(ROLE_TRADEMARK, getattr(entry.family, "trademark", False))
        tip = f"{entry.family.id}\n{entry.svg_path.name}"
        if getattr(entry.family, "trademark", False):
            tip += "\n\n⚠️ Editorial Use Only / Trademarked Character"
        if entry.is_fallback:
            tip = f"{tip}\nFallback: family has no selected variant kind"
        item.setToolTip(tip)
        item.setSizeHint(QSize(self._icon_size + 16, self._icon_size + LABEL_EXTRA_HEIGHT))
        self._family_rows.setdefault(entry.family.id, self.count())
        self.addItem(item)

    def _emit_family_from_item(self, item: QListWidgetItem | None) -> None:
        if item is None:
            self.family_selected.emit(None)
            return
        family = item.data(Qt.ItemDataRole.UserRole)
        if family is not None and hasattr(family, "variants"):
            self.family_selected.emit(family)
        else:
            self.family_selected.emit(None)

    def _exec_batch_context_menu(self, pos: QPoint, targets: list[tuple[IconFamily, str]]) -> None:
        menu = QMenu(self)
        selected_ids = {family.id for family, _path in targets}
        all_favorites = bool(selected_ids) and selected_ids.issubset(self._favorite_family_ids)
        labels = batch_context_action_texts(len(targets), all_favorites=all_favorites)
        batch_ai_action = menu.addAction(labels[0])
        favorite_action = menu.addAction(labels[1])
        chosen = menu.exec_(self.mapToGlobal(pos))
        if chosen is batch_ai_action:
            self.batch_keywords_ai_requested.emit(targets)
        elif chosen is favorite_action:
            self.batch_favorites_requested.emit((targets, not all_favorites))

    def _grid_size_for(self, icon_size: int) -> QSize:
        label_h = LABEL_EXTRA_HEIGHT if self._dual_line_labels else 48
        return QSize(icon_size + 24, icon_size + label_h)

    def _on_context_menu(self, pos: QPoint) -> None:
        item = self.itemAt(pos)
        if item is None:
            return
        family = item.data(Qt.ItemDataRole.UserRole)
        if family is None:
            return

        path = item.data(ROLE_SVG_PATH)
        has_path = isinstance(path, str) and bool(path)

        if item not in self.selectedItems():
            self.clearSelection()
            item.setSelected(True)
            self.setCurrentItem(item)

        targets = self.selected_keyword_targets()
        if len(targets) > 1:
            self._exec_batch_context_menu(pos, targets)
            return

        menu = QMenu(self)

        reveal_action = None
        details_action = None
        copy_file_action = None
        copy_contents_action = None
        copy_filename_action = None
        copy_path_action = None

        if has_path:
            reveal_action = menu.addAction(LABEL_REVEAL_IN_EXPLORER)
            details_action = menu.addAction("ℹ️ Icon details")  # noqa: RUF001
            copy_file_action = menu.addAction("📋 Copy file")
            if is_svg_icon_path(path):
                copy_contents_action = menu.addAction("📋 Copy contents")
            copy_filename_action = menu.addAction("📋 Copy filename")
            copy_path_action = menu.addAction("📋 Copy path")
            menu.addSeparator()

        open_note_action = menu.addAction("📝 Open note in editor")
        edit_keywords_action = menu.addAction("✏️ Edit icon…")
        set_category_action = menu.addAction("🏷️ Set as category icon")
        is_favorite = str(getattr(family, "id", "")).strip() in self._favorite_family_ids
        favorite_action = menu.addAction("⭐ Remove from favorites" if is_favorite else "⭐ Add to favorites")

        is_trademark = getattr(family, "trademark", False)
        toggle_trademark_text = "Remove trademark warning" if is_trademark else "Add trademark warning"
        toggle_trademark_action = menu.addAction(f"⚠️ {toggle_trademark_text}")

        menu.addSeparator()

        reveal_source_action = None
        open_source_action = None
        if has_path:
            reveal_source_action = menu.addAction("📂 Reveal source in File Explorer")
            open_source_action = menu.addAction("🎨 Open source")
            menu.addSeparator()

        license_name, license_url = family_license_info(family, self._repo_root)
        license_action = None
        if license_name:
            license_action = menu.addAction(f"📜 License: {license_name}")
            if not is_openable_license_url(license_url):
                license_action.setEnabled(False)

        delete_action = menu.addAction(LABEL_DELETE)
        chosen = menu.exec_(self.mapToGlobal(pos))

        if has_path and chosen is reveal_action:
            self.reveal_requested.emit(path)
        elif has_path and chosen is details_action:
            self.details_requested.emit(family, path)
        elif has_path and chosen is copy_file_action:
            self.copy_requested.emit(path)
        elif has_path and copy_contents_action is not None and chosen is copy_contents_action:
            self.copy_contents_requested.emit(path)
        elif has_path and chosen is copy_filename_action:
            self.copy_filename_requested.emit(path)
        elif has_path and chosen is copy_path_action:
            self.copy_path_requested.emit(path)
        elif chosen is open_note_action:
            self.open_note_requested.emit(family)
        elif chosen is edit_keywords_action:
            self.edit_keywords_requested.emit(family, path if has_path else "")
        elif chosen is set_category_action:
            self.set_category_icon_requested.emit(family)
        elif chosen is favorite_action:
            self.favorite_toggled.emit(family)
        elif license_action is not None and chosen is license_action:
            self.license_requested.emit(license_url)
        elif chosen is toggle_trademark_action:
            self.toggle_trademark_requested.emit(family)
        elif has_path and chosen is reveal_source_action:
            self.reveal_source_requested.emit(family, path)
        elif has_path and chosen is open_source_action:
            self.open_source_requested.emit(family, path)
        elif chosen is delete_action:
            self.delete_requested.emit(family)

    def _on_current_item_changed(
        self,
        current: QListWidgetItem | None,
        _previous: QListWidgetItem | None,
    ) -> None:
        self._emit_family_from_item(current)

    def _on_item_double_clicked(self, item: QListWidgetItem) -> None:
        path = item.data(ROLE_SVG_PATH)
        if isinstance(path, str) and path and Path(path).is_file():
            self.preview_requested.emit(path)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None, *, icon_size: int = DEFAULT_THUMB_SIZE, emit_family_selection: bool = True, dual_line_labels: bool = False) -> None
```

Configure icon mode and drag-only outward behavior.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        parent: QWidget | None = None,
        *,
        icon_size: int = DEFAULT_THUMB_SIZE,
        emit_family_selection: bool = True,
        dual_line_labels: bool = False,
    ) -> None:
        super().__init__(parent)
        self._icon_size = icon_size
        self._emit_family_selection = emit_family_selection
        self._dual_line_labels = dual_line_labels
        self._favorite_family_ids: set[str] = set()
        self._repo_root: Path | None = None
        # family_id → first row, so thumbnail updates skip a full list scan.
        self._family_rows: dict[str, int] = {}
        self._viewport_timer = QTimer(self)
        self._viewport_timer.setSingleShot(True)
        self._viewport_timer.setInterval(VIEWPORT_SIGNAL_DEBOUNCE_MS)
        self._viewport_timer.timeout.connect(self.viewport_changed)
        self.setViewMode(QListWidget.ViewMode.IconMode)
        self.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.setMovement(QListWidget.Movement.Static)
        self.setUniformItemSizes(True)
        self.setWrapping(True)
        self.setFlow(QListWidget.Flow.LeftToRight)
        self.setWordWrap(True)
        self.setSpacing(8)
        self.setIconSize(QSize(icon_size, icon_size))
        self.setGridSize(self._grid_size_for(icon_size))
        self.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        # Pixel scrolling keeps the scrollbar value in sync with the grid geometry math.
        self.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setDragEnabled(True)
        self.setDragDropMode(QListWidget.DragDropMode.DragOnly)
        # DragOnly turns drops off; Explorer file drops still need the viewport.
        self.setAcceptDrops(True)
        self.viewport().setAcceptDrops(True)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._on_context_menu)
        self.itemDoubleClicked.connect(self._on_item_double_clicked)
        if dual_line_labels:
            self.setItemDelegate(IconLabelDelegate(self))
        if emit_family_selection:
            self.itemPressed.connect(self._emit_family_from_item)
            self.currentItemChanged.connect(self._on_current_item_changed)
        self.verticalScrollBar().valueChanged.connect(self.schedule_viewport_changed)
```

</details>

### ⚙️ Method `append_grid_entries`

```python
def append_grid_entries(self, entries: list[GridEntry], *, pixmaps_by_path: dict[str, QPixmap], placeholder: QPixmap) -> None
```

Add more variant-view tiles without rebuilding the grid.

<details>
<summary>Code:</summary>

```python
def append_grid_entries(
        self,
        entries: list[GridEntry],
        *,
        pixmaps_by_path: dict[str, QPixmap],
        placeholder: QPixmap,
    ) -> None:
        if not entries:
            return
        self.blockSignals(True)  # noqa: FBT003
        self.setUpdatesEnabled(False)
        try:
            for entry in entries:
                self._add_grid_item(entry, pixmaps_by_path=pixmaps_by_path, placeholder=placeholder)
        finally:
            self.setUpdatesEnabled(True)
            self.blockSignals(False)  # noqa: FBT003
```

</details>

### ⚙️ Method `keyPressEvent`

```python
def keyPressEvent(self, event: QKeyEvent) -> None
```

Copy selected icon files when the standard Copy shortcut is pressed.

<details>
<summary>Code:</summary>

```python
def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        if event.matches(QKeySequence.StandardKey.Copy):
            paths = self.selected_file_paths()
            if paths:
                self.copy_files_requested.emit(paths)
                event.accept()
                return
        super().keyPressEvent(event)
```

</details>

### ⚙️ Method `preview_paths`

```python
def preview_paths(self) -> list[Path]
```

Return all existing icon paths in display order.

<details>
<summary>Code:</summary>

```python
def preview_paths(self) -> list[Path]:
        paths: list[Path] = []
        for index in range(self.count()):
            item = self.item(index)
            if item is None:
                continue
            raw = item.data(ROLE_SVG_PATH)
            if isinstance(raw, str) and raw:
                path = Path(raw)
                if path.is_file():
                    paths.append(path)
        return paths
```

</details>

### ⚙️ Method `reset_row_pixmaps`

```python
def reset_row_pixmaps(self, rows: list[int], *, placeholder: QPixmap) -> None
```

Drop pixmaps of rows scrolled far away so memory stays bounded.

<details>
<summary>Code:</summary>

```python
def reset_row_pixmaps(self, rows: list[int], *, placeholder: QPixmap) -> None:
        if not rows:
            return
        icon = QIcon(placeholder)
        self.setUpdatesEnabled(False)
        try:
            for row in rows:
                item = self.item(row)
                if item is not None:
                    item.setIcon(icon)
        finally:
            self.setUpdatesEnabled(True)
```

</details>

### ⚙️ Method `resizeEvent`

```python
def resizeEvent(self, event: QResizeEvent) -> None
```

Reflow tiles and ask the owner to reload pixmaps for the new visible rows.

<details>
<summary>Code:</summary>

```python
def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        super().resizeEvent(event)
        self.schedule_viewport_changed()
```

</details>

### ⚙️ Method `schedule_viewport_changed`

```python
def schedule_viewport_changed(self) -> None
```

Ask for a debounced `viewport_changed` signal after scrolling or resizing.

<details>
<summary>Code:</summary>

```python
def schedule_viewport_changed(self) -> None:
        self._viewport_timer.start()
```

</details>

### ⚙️ Method `select_family`

```python
def select_family(self, family_id: str) -> bool
```

Select the first tile for `family_id` and scroll it into view.

<details>
<summary>Code:</summary>

```python
def select_family(self, family_id: str) -> bool:
        row = self._family_rows.get(family_id)
        item = self.item(row) if row is not None else None
        if item is None:
            return False
        self.setCurrentItem(item)
        self.scrollToItem(item, QAbstractItemView.ScrollHint.PositionAtCenter)
        return True
```

</details>

### ⚙️ Method `selected_file_paths`

```python
def selected_file_paths(self) -> list[str]
```

Return file paths of selected tiles, in display order.

<details>
<summary>Code:</summary>

```python
def selected_file_paths(self) -> list[str]:
        paths: list[str] = []
        for index in range(self.count()):
            item = self.item(index)
            if item is None or not item.isSelected():
                continue
            raw = item.data(ROLE_SVG_PATH)
            if isinstance(raw, str) and raw:
                paths.append(raw)
        return paths
```

</details>

### ⚙️ Method `selected_keyword_targets`

```python
def selected_keyword_targets(self) -> list[tuple[IconFamily, str]]
```

Return unique selected families with an SVG path, in display order.

<details>
<summary>Code:</summary>

```python
def selected_keyword_targets(self) -> list[tuple[IconFamily, str]]:
        targets: list[tuple[IconFamily, str]] = []
        seen: set[str] = set()
        for index in range(self.count()):
            item = self.item(index)
            if item is None or not item.isSelected():
                continue
            family = item.data(Qt.ItemDataRole.UserRole)
            family_id = getattr(family, "id", None)
            if not isinstance(family_id, str) or family_id in seen:
                continue
            seen.add(family_id)
            path = item.data(ROLE_SVG_PATH)
            targets.append((family, path if isinstance(path, str) else ""))
        return targets
```

</details>

### ⚙️ Method `set_display_icon_size`

```python
def set_display_icon_size(self, icon_size: int) -> None
```

Update icon and grid sizes used by the list.

<details>
<summary>Code:</summary>

```python
def set_display_icon_size(self, icon_size: int) -> None:
        self._icon_size = icon_size
        self.setIconSize(QSize(icon_size, icon_size))
        self.setGridSize(self._grid_size_for(icon_size))
```

</details>

### ⚙️ Method `set_favorite_family_ids`

```python
def set_favorite_family_ids(self, family_ids: set[str] | list[str]) -> None
```

Update the favorite family IDs used by the context menu labels.

<details>
<summary>Code:</summary>

```python
def set_favorite_family_ids(self, family_ids: set[str] | list[str]) -> None:
        self._favorite_family_ids = {str(item).strip() for item in family_ids if str(item).strip()}
```

</details>

### ⚙️ Method `set_grid_entries`

```python
def set_grid_entries(self, entries: list[GridEntry], *, pixmaps_by_path: dict[str, QPixmap], placeholder: QPixmap) -> None
```

Rebuild the grid from variant-view entries and path→pixmap map.

<details>
<summary>Code:</summary>

```python
def set_grid_entries(
        self,
        entries: list[GridEntry],
        *,
        pixmaps_by_path: dict[str, QPixmap],
        placeholder: QPixmap,
    ) -> None:
        self.blockSignals(True)  # noqa: FBT003
        self.clear()
        self._family_rows = {}
        for entry in entries:
            self._add_grid_item(entry, pixmaps_by_path=pixmaps_by_path, placeholder=placeholder)
        self.setCurrentRow(-1)
        self.blockSignals(False)  # noqa: FBT003
```

</details>

### ⚙️ Method `set_repo_root`

```python
def set_repo_root(self, repo_root: Path | None) -> None
```

Remember the open icons folder for license lookup from notes.

<details>
<summary>Code:</summary>

```python
def set_repo_root(self, repo_root: Path | None) -> None:
        self._repo_root = repo_root
```

</details>

### ⚙️ Method `startDrag`

```python
def startDrag(self, supported_actions: Qt.DropAction) -> None
```

Start a drag with family IDs (for Categories) and file URLs (for Explorer).

<details>
<summary>Code:</summary>

```python
def startDrag(self, supported_actions: Qt.DropAction) -> None:  # noqa: ARG002, N802
        targets = self.selected_keyword_targets()
        if not targets:
            return
        mime = QMimeData()
        encode_family_ids_mime(mime, [family.id for family, _path in targets])
        urls = [
            QUrl.fromLocalFile(str(Path(svg_path).resolve()))
            for _family, svg_path in targets
            if svg_path and Path(svg_path).is_file()
        ]
        if urls:
            mime.setUrls(urls)
        drag = QDrag(self)
        drag.setMimeData(mime)
        item = self.currentItem()
        if item is not None:
            icon = item.icon()
            if not icon.isNull():
                drag.setPixmap(icon.pixmap(64, 64))
                drag.setHotSpot(QPoint(32, 32))
        drag.exec(Qt.DropAction.CopyAction)
```

</details>

### ⚙️ Method `update_row_pixmaps`

```python
def update_row_pixmaps(self, pixmaps: dict[int, QPixmap]) -> None
```

Apply thumbnails for the given rows with a single repaint.

<details>
<summary>Code:</summary>

```python
def update_row_pixmaps(self, pixmaps: dict[int, QPixmap]) -> None:
        if not pixmaps:
            return
        self.setUpdatesEnabled(False)
        try:
            for row, pixmap in pixmaps.items():
                item = self.item(row)
                if item is None:
                    continue
                icon_pixmap = _muted_pixmap(pixmap, FALLBACK_ICON_OPACITY) if bool(item.data(ROLE_FALLBACK)) else pixmap
                item.setIcon(QIcon(icon_pixmap))
        finally:
            self.setUpdatesEnabled(True)
```

</details>

### ⚙️ Method `visible_row_span`

```python
def visible_row_span(self, margin_lines: int = 1) -> tuple[int, int]
```

Return the row range currently on screen, padded by `margin_lines` grid lines.

Tiles live in a fixed grid, so the range is derived from the scroll offset instead of
hit-testing items, which stays exact even when the point falls between cells.

<details>
<summary>Code:</summary>

```python
def visible_row_span(self, margin_lines: int = 1) -> tuple[int, int]:
        count = self.count()
        if count == 0:
            return (0, -1)
        grid = self.gridSize()
        cell_width = max(1, grid.width())
        cell_height = max(1, grid.height())
        viewport = self.viewport()
        columns = max(1, viewport.width() // cell_width)
        lines = viewport.height() // cell_height + 1
        top_line = max(0, self.verticalScrollBar().value() // cell_height)
        first = max(0, (top_line - margin_lines) * columns)
        last = min(count - 1, (top_line + lines + margin_lines) * columns - 1)
        # Hit-test the middle of the viewport as a safety net if the geometry math drifts.
        probe = self.indexAt(QPoint(viewport.width() // 2, viewport.height() // 2))
        if probe.isValid():
            reach = (lines + margin_lines) * columns
            first = min(first, max(0, probe.row() - reach))
            last = max(last, min(count - 1, probe.row() + reach))
        return (first, last)
```

</details>

## 🏛️ Class `IconLabelDelegate`

```python
class IconLabelDelegate(QStyledItemDelegate)
```

Draw title plus a smaller filename under icon-mode items.

<details>
<summary>Code:</summary>

```python
class IconLabelDelegate(QStyledItemDelegate):

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        """Paint icon decoration and two-line label."""
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)
        title = opt.text
        subtitle = index.data(ROLE_SUBTITLE)
        subtitle_text = subtitle if isinstance(subtitle, str) else ""
        opt.text = ""

        widget = opt.widget
        style = widget.style() if widget is not None else None
        if style is not None:
            style.drawControl(QStyle.ControlElement.CE_ItemViewItem, opt, painter, widget)

        text_rect = (
            style.subElementRect(QStyle.SubElement.SE_ItemViewItemText, opt, widget) if style is not None else opt.rect
        )
        if not text_rect.isValid():
            text_rect = QRect(
                opt.rect.left(),
                opt.rect.bottom() - LABEL_EXTRA_HEIGHT,
                opt.rect.width(),
                LABEL_EXTRA_HEIGHT,
            )

        is_fallback = bool(index.data(ROLE_FALLBACK))
        painter.save()
        # Keep label colors unchanged on selection (highlight is only the tile chrome).
        title_color = QColor(opt.palette.color(opt.palette.ColorRole.Text))
        if is_fallback:
            title_color.setAlpha(FALLBACK_TITLE_ALPHA)
        painter.setPen(title_color)

        title_font = QFont(opt.font)
        subtitle_font = _filename_label_font(opt.font)

        painter.setFont(title_font)
        title_height = (
            painter.fontMetrics()
            .boundingRect(
                text_rect,
                int(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop | Qt.TextFlag.TextWordWrap),
                title,
            )
            .height()
        )
        title_rect = QRect(
            text_rect.left(),
            text_rect.top(),
            text_rect.width(),
            min(title_height, painter.fontMetrics().height() * 2),
        )
        painter.drawText(
            title_rect,
            int(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop | Qt.TextFlag.TextWordWrap),
            title,
        )

        if subtitle_text:
            muted = opt.palette.color(opt.palette.ColorRole.PlaceholderText)
            if not muted.isValid() or muted.alpha() == 0:
                muted = QColor(opt.palette.color(opt.palette.ColorRole.Text))
                muted.setAlpha(160)
            if is_fallback:
                muted = QColor(muted)
                muted.setAlpha(FALLBACK_SUBTITLE_ALPHA)
            painter.setPen(muted)
            painter.setFont(subtitle_font)
            subtitle_rect = QRect(
                text_rect.left(),
                title_rect.bottom() + 1,
                text_rect.width(),
                max(0, text_rect.bottom() - title_rect.bottom()),
            )
            painter.drawText(
                subtitle_rect,
                int(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop | Qt.TextFlag.TextWrapAnywhere),
                subtitle_text,
            )

        is_trademark = bool(index.data(ROLE_TRADEMARK))
        if is_trademark:
            icon_rect = (
                style.subElementRect(QStyle.SubElement.SE_ItemViewItemDecoration, opt, widget)
                if style is not None
                else opt.rect
            )
            if icon_rect.isValid():
                painter.setFont(title_font)
                painter.drawText(
                    icon_rect.adjusted(0, 4, -4, 0),
                    int(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop),
                    "⚠️",
                )

        painter.restore()

    def sizeHint(  # noqa: N802
        self,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> QSize:
        """Keep room for icon plus two text lines."""
        base = super().sizeHint(option, index)
        icon_h = option.decorationSize.height() if option.decorationSize.isValid() else DEFAULT_THUMB_SIZE
        width = max(base.width(), icon_h + 16)
        return QSize(width, icon_h + LABEL_EXTRA_HEIGHT)
```

</details>

### ⚙️ Method `paint`

```python
def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> None
```

Paint icon decoration and two-line label.

<details>
<summary>Code:</summary>

```python
def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)
        title = opt.text
        subtitle = index.data(ROLE_SUBTITLE)
        subtitle_text = subtitle if isinstance(subtitle, str) else ""
        opt.text = ""

        widget = opt.widget
        style = widget.style() if widget is not None else None
        if style is not None:
            style.drawControl(QStyle.ControlElement.CE_ItemViewItem, opt, painter, widget)

        text_rect = (
            style.subElementRect(QStyle.SubElement.SE_ItemViewItemText, opt, widget) if style is not None else opt.rect
        )
        if not text_rect.isValid():
            text_rect = QRect(
                opt.rect.left(),
                opt.rect.bottom() - LABEL_EXTRA_HEIGHT,
                opt.rect.width(),
                LABEL_EXTRA_HEIGHT,
            )

        is_fallback = bool(index.data(ROLE_FALLBACK))
        painter.save()
        # Keep label colors unchanged on selection (highlight is only the tile chrome).
        title_color = QColor(opt.palette.color(opt.palette.ColorRole.Text))
        if is_fallback:
            title_color.setAlpha(FALLBACK_TITLE_ALPHA)
        painter.setPen(title_color)

        title_font = QFont(opt.font)
        subtitle_font = _filename_label_font(opt.font)

        painter.setFont(title_font)
        title_height = (
            painter.fontMetrics()
            .boundingRect(
                text_rect,
                int(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop | Qt.TextFlag.TextWordWrap),
                title,
            )
            .height()
        )
        title_rect = QRect(
            text_rect.left(),
            text_rect.top(),
            text_rect.width(),
            min(title_height, painter.fontMetrics().height() * 2),
        )
        painter.drawText(
            title_rect,
            int(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop | Qt.TextFlag.TextWordWrap),
            title,
        )

        if subtitle_text:
            muted = opt.palette.color(opt.palette.ColorRole.PlaceholderText)
            if not muted.isValid() or muted.alpha() == 0:
                muted = QColor(opt.palette.color(opt.palette.ColorRole.Text))
                muted.setAlpha(160)
            if is_fallback:
                muted = QColor(muted)
                muted.setAlpha(FALLBACK_SUBTITLE_ALPHA)
            painter.setPen(muted)
            painter.setFont(subtitle_font)
            subtitle_rect = QRect(
                text_rect.left(),
                title_rect.bottom() + 1,
                text_rect.width(),
                max(0, text_rect.bottom() - title_rect.bottom()),
            )
            painter.drawText(
                subtitle_rect,
                int(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop | Qt.TextFlag.TextWrapAnywhere),
                subtitle_text,
            )

        is_trademark = bool(index.data(ROLE_TRADEMARK))
        if is_trademark:
            icon_rect = (
                style.subElementRect(QStyle.SubElement.SE_ItemViewItemDecoration, opt, widget)
                if style is not None
                else opt.rect
            )
            if icon_rect.isValid():
                painter.setFont(title_font)
                painter.drawText(
                    icon_rect.adjusted(0, 4, -4, 0),
                    int(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop),
                    "⚠️",
                )

        painter.restore()
```

</details>

### ⚙️ Method `sizeHint`

```python
def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> QSize
```

Keep room for icon plus two text lines.

<details>
<summary>Code:</summary>

```python
def sizeHint(  # noqa: N802
        self,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> QSize:
        base = super().sizeHint(option, index)
        icon_h = option.decorationSize.height() if option.decorationSize.isValid() else DEFAULT_THUMB_SIZE
        width = max(base.width(), icon_h + 16)
        return QSize(width, icon_h + LABEL_EXTRA_HEIGHT)
```

</details>

## 🏛️ Class `VariantsPanel`

```python
class VariantsPanel(QWidget)
```

Right-side panel showing SVG variants for the selected icon family.

<details>
<summary>Code:</summary>

```python
class VariantsPanel(QWidget):

    def __init__(self, parent: QWidget | None = None, *, thumb_size: int = VARIANT_THUMB_SIZE) -> None:
        """Build header + draggable variants list."""
        super().__init__(parent)
        self._thumb_size = thumb_size
        self._repo_root: Path | None = None
        self._family: IconFamily | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.header = QLabel("Select an icon to see variants")
        self.header.setWordWrap(True)
        self.header.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        layout.addWidget(self.header)

        self.list = DraggableIconList(icon_size=thumb_size, emit_family_selection=False)
        self.list.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.list, stretch=1)

    def clear_variants(self) -> None:
        """Clear the variants list and reset the header."""
        self._family = None
        self.list.clear()
        self.header.setText("Select an icon to see variants")

    @property
    def current_family(self) -> IconFamily | None:
        """Return the family currently shown in the panel."""
        return self._family

    def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        """Keep IconMode cells narrower than the viewport so tiles stay visible."""
        super().resizeEvent(event)
        viewport_w = self.list.viewport().width()
        if viewport_w <= 0:
            return
        cell_w = self.list.gridSize().width()
        if cell_w <= viewport_w:
            return
        icon_size = max(32, min(self._thumb_size, viewport_w - 24 - self.list.spacing() * 2))
        self.list.set_display_icon_size(icon_size)

    def set_thumb_size(self, thumb_size: int) -> None:
        """Update variant thumbnail size (does not rebuild items)."""
        self._thumb_size = thumb_size
        self.list.set_display_icon_size(thumb_size)

    def show_family(self, family: IconFamily | None, repo_root: Path | None) -> None:
        """Populate the panel with variants of `family`."""
        self._repo_root = repo_root
        self._family = family
        self.list.clear()
        if family is None or repo_root is None:
            self.header.setText("Select an icon to see variants")
            return

        tags = ", ".join(family.tags) if family.tags else "—"
        date_line = f"\nDate: {family.date}" if family.date else ""
        self.header.setText(
            f"{family.title}\n{family.id}{date_line}\nCategories: {', '.join(family.categories)}\nTags: {tags}",
        )
        for variant in family.variants:
            path = variant.absolute_path(repo_root, family.folder)
            try:
                pixmap = self._preview(path, self._thumb_size)
            except (OSError, ValueError, RuntimeError):
                pixmap = placeholder_pixmap(self._thumb_size)
            item = QListWidgetItem(QIcon(pixmap), variant.name)
            item.setData(Qt.ItemDataRole.UserRole, family)
            item.setData(ROLE_SVG_PATH, str(path))
            item.setToolTip(str(path))
            self.list.addItem(item)
        self.list.doItemsLayout()

    @staticmethod
    def _preview(path: Path, size: int) -> QPixmap:
        image = render_icon_to_image(path, size)
        if image is None:
            return placeholder_pixmap(size)
        return QPixmap.fromImage(image)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None, *, thumb_size: int = VARIANT_THUMB_SIZE) -> None
```

Build header + draggable variants list.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None, *, thumb_size: int = VARIANT_THUMB_SIZE) -> None:
        super().__init__(parent)
        self._thumb_size = thumb_size
        self._repo_root: Path | None = None
        self._family: IconFamily | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.header = QLabel("Select an icon to see variants")
        self.header.setWordWrap(True)
        self.header.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        layout.addWidget(self.header)

        self.list = DraggableIconList(icon_size=thumb_size, emit_family_selection=False)
        self.list.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.list, stretch=1)
```

</details>

### ⚙️ Method `clear_variants`

```python
def clear_variants(self) -> None
```

Clear the variants list and reset the header.

<details>
<summary>Code:</summary>

```python
def clear_variants(self) -> None:
        self._family = None
        self.list.clear()
        self.header.setText("Select an icon to see variants")
```

</details>

### ⚙️ Method `current_family (property)`

```python
def current_family(self) -> IconFamily | None
```

Return the family currently shown in the panel.

<details>
<summary>Code:</summary>

```python
def current_family(self) -> IconFamily | None:
        return self._family
```

</details>

### ⚙️ Method `resizeEvent`

```python
def resizeEvent(self, event: QResizeEvent) -> None
```

Keep IconMode cells narrower than the viewport so tiles stay visible.

<details>
<summary>Code:</summary>

```python
def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        super().resizeEvent(event)
        viewport_w = self.list.viewport().width()
        if viewport_w <= 0:
            return
        cell_w = self.list.gridSize().width()
        if cell_w <= viewport_w:
            return
        icon_size = max(32, min(self._thumb_size, viewport_w - 24 - self.list.spacing() * 2))
        self.list.set_display_icon_size(icon_size)
```

</details>

### ⚙️ Method `set_thumb_size`

```python
def set_thumb_size(self, thumb_size: int) -> None
```

Update variant thumbnail size (does not rebuild items).

<details>
<summary>Code:</summary>

```python
def set_thumb_size(self, thumb_size: int) -> None:
        self._thumb_size = thumb_size
        self.list.set_display_icon_size(thumb_size)
```

</details>

### ⚙️ Method `show_family`

```python
def show_family(self, family: IconFamily | None, repo_root: Path | None) -> None
```

Populate the panel with variants of `family`.

<details>
<summary>Code:</summary>

```python
def show_family(self, family: IconFamily | None, repo_root: Path | None) -> None:
        self._repo_root = repo_root
        self._family = family
        self.list.clear()
        if family is None or repo_root is None:
            self.header.setText("Select an icon to see variants")
            return

        tags = ", ".join(family.tags) if family.tags else "—"
        date_line = f"\nDate: {family.date}" if family.date else ""
        self.header.setText(
            f"{family.title}\n{family.id}{date_line}\nCategories: {', '.join(family.categories)}\nTags: {tags}",
        )
        for variant in family.variants:
            path = variant.absolute_path(repo_root, family.folder)
            try:
                pixmap = self._preview(path, self._thumb_size)
            except (OSError, ValueError, RuntimeError):
                pixmap = placeholder_pixmap(self._thumb_size)
            item = QListWidgetItem(QIcon(pixmap), variant.name)
            item.setData(Qt.ItemDataRole.UserRole, family)
            item.setData(ROLE_SVG_PATH, str(path))
            item.setToolTip(str(path))
            self.list.addItem(item)
        self.list.doItemsLayout()
```

</details>

## 🔧 Function `batch_context_action_texts`

```python
def batch_context_action_texts(count: int, *, all_favorites: bool = False) -> list[str]
```

Return labels for the multi-select context menu.

<details>
<summary>Code:</summary>

```python
def batch_context_action_texts(count: int, *, all_favorites: bool = False) -> list[str]:
    favorite_label = (
        f"⭐ Remove from favorites ({count} icons)" if all_favorites else f"⭐ Add to favorites ({count} icons)"
    )
    return [
        f"🤖 Process keywords with AI ({count} icons)…",
        favorite_label,
    ]
```

</details>

## 🔧 Function `decode_family_ids_mime`

```python
def decode_family_ids_mime(mime: QMimeData) -> list[str]
```

Return family IDs encoded by the Vector Icons grid drag.

<details>
<summary>Code:</summary>

```python
def decode_family_ids_mime(mime: QMimeData) -> list[str]:
    if not mime.hasFormat(FAMILY_IDS_MIME):
        return []
    try:
        raw = json.loads(bytes(mime.data(FAMILY_IDS_MIME).data()).decode("utf-8"))
    except (TypeError, ValueError, UnicodeDecodeError):
        return []
    if not isinstance(raw, list):
        return []
    return [str(item).strip() for item in raw if str(item).strip()]
```

</details>

## 🔧 Function `encode_family_ids_mime`

```python
def encode_family_ids_mime(mime: QMimeData, family_ids: list[str]) -> None
```

Store family IDs on a drag so Categories can accept an internal drop.

<details>
<summary>Code:</summary>

```python
def encode_family_ids_mime(mime: QMimeData, family_ids: list[str]) -> None:
    mime.setData(FAMILY_IDS_MIME, json.dumps(family_ids).encode("utf-8"))
```

</details>

## 🔧 Function `family_display_filename`

```python
def family_display_filename(family: IconFamily, svg_path: Path | None = None) -> str
```

Return the filename shown under the family title in the main grid.

<details>
<summary>Code:</summary>

```python
def family_display_filename(family: IconFamily, svg_path: Path | None = None) -> str:
    if svg_path is not None and not svg_path.name.casefold().startswith("featured-image."):
        return svg_path.name
    if family.variants:
        return Path(family.variants[0].file).name
    return f"{family.id}.svg"
```

</details>

## 🔧 Function `is_svg_icon_path`

```python
def is_svg_icon_path(path: object) -> bool
```

Return whether `path` looks like an SVG file path.

<details>
<summary>Code:</summary>

```python
def is_svg_icon_path(path: object) -> bool:
    return isinstance(path, str) and Path(path).suffix.casefold() == ".svg"
```

</details>

## 🔧 Function `read_svg_text`

```python
def read_svg_text(path: Path) -> str
```

Read SVG markup, trying encodings used by export tools.

Raises:

- `OSError`: If the file cannot be read.
- `UnicodeDecodeError`: If the bytes are not valid SVG text.

<details>
<summary>Code:</summary>

```python
def read_svg_text(path: Path) -> str:
    data = path.read_bytes()
    last_error: UnicodeDecodeError | None = None
    for encoding in ("utf-8-sig", "utf-8", "utf-16"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError as exc:
            last_error = exc
    if last_error is not None:
        raise last_error
    return data.decode("utf-8")
```

</details>
