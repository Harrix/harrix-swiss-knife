---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `exercise_selection_dialog.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ExerciseSelectionDialog`](#%EF%B8%8F-class-exerciseselectiondialog)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `closeEvent`](#%EF%B8%8F-method-closeevent)
  - [⚙️ Method `eventFilter`](#%EF%B8%8F-method-eventfilter)
  - [⚙️ Method `reject`](#%EF%B8%8F-method-reject)
  - [⚙️ Method `showEvent`](#%EF%B8%8F-method-showevent)

</details>

## 🏛️ Class `ExerciseSelectionDialog`

```python
class ExerciseSelectionDialog(QDialog)
```

Modal dialog for selecting an exercise via AVIF previews.

<details>
<summary>Code:</summary>

```python
class ExerciseSelectionDialog(QDialog):

    def __init__(
        self,
        parent: QWidget | None,
        *,
        exercises: list[str],
        pixmap_provider: Callable[[str], QPixmap | None],
        preview_size: QSize,
        current_selection: str | None,
        avif_manager: AvifManager | None = None,
        name_locals: dict[str, str] | None = None,
        display_names: dict[str, str] | None = None,
    ) -> None:
        """Initialize the ExerciseSelectionDialog.

        Args:

        - `parent` (`QWidget | None`): Parent widget.
        - `exercises` (`list[str]`): List of exercise names to display.
        - `pixmap_provider` (`Callable[[str], QPixmap | None]`): Returns a still
          preview pixmap for a given exercise name.
        - `preview_size` (`QSize`): Size for icon previews.
        - `current_selection` (`str | None`): Currently selected exercise, if any.
        - `avif_manager` (`AvifManager | None`): AVIF manager for loading animations. Defaults to `None`.
        - `name_locals` (`dict[str, str] | None`): Optional English→local name map.
        - `display_names` (`dict[str, str] | None`): Optional English→display label map
          (for example a dumbbell icon prefix).

        """
        super().__init__(parent)
        self.setWindowTitle("Select Exercise")
        qt_modality.set_owner_window_modal(self)
        self.selected_exercise: str | None = current_selection
        self._pixmap_provider = pixmap_provider
        self._avif_manager = avif_manager
        self._name_locals = name_locals or {}
        self._display_names = display_names or {}
        self._preview_size = preview_size
        self._hovered_tile: _ExercisePreviewTile | None = None
        self._pending_preview_rows: list[int] = []
        self._preview_load_started = False
        has_any_local = any(self._name_locals.get(name, "").strip() for name in exercises)
        text_area_height = 54 if has_any_local else 36

        layout = QVBoxLayout(self)

        self.filter_edit = QLineEdit(self)
        self.filter_edit.setPlaceholderText("Filter exercises…")
        self.filter_edit.setClearButtonEnabled(True)
        self.filter_edit.textChanged.connect(self._filter_exercises)
        layout.addWidget(self.filter_edit)

        self.list_widget = QListWidget(self)
        self.list_widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.list_widget.setViewMode(QListWidget.ViewMode.IconMode)
        self.list_widget.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.list_widget.setMovement(QListWidget.Movement.Static)
        self.list_widget.setSpacing(16)
        self.list_widget.setUniformItemSizes(True)
        self.list_widget.setMouseTracking(True)
        self.list_widget.setStyleSheet(
            """
            QListWidget {
                outline: none;
            }
            QListWidget::item {
                border: none;
                background: transparent;
                padding: 0px;
                margin: 0px;
            }
            QListWidget::item:selected {
                background: transparent;
            }
            QFrame#exercisePreviewTile {
                border: 2px solid transparent;
                border-radius: 4px;
                background: transparent;
            }
            QFrame#exercisePreviewTile:hover {
                border-color: #0078d4;
            }
            QFrame#exercisePreviewTile[selected="true"],
            QFrame#exercisePreviewTile[selected="true"]:hover {
                border-color: #4CAF50;
            }
            """
        )
        layout.addWidget(self.list_widget)

        self.list_widget.setUpdatesEnabled(False)
        try:
            for exercise in exercises:
                item = QListWidgetItem()
                item.setData(Qt.ItemDataRole.UserRole, exercise)
                item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)

                name_local = self._name_locals.get(exercise, "").strip()
                tile = _ExercisePreviewTile(
                    exercise_name=exercise,
                    display_name=self._display_names.get(exercise, exercise),
                    name_local=name_local,
                    static_pixmap=None,
                    preview_size=preview_size,
                    text_area_height=text_area_height,
                    pixmap_pending=True,
                )
                item.setSizeHint(tile.sizeHint())
                self.list_widget.addItem(item)
                self.list_widget.setItemWidget(item, tile)
                self._pending_preview_rows.append(self.list_widget.count() - 1)

                tile.clicked.connect(lambda row_item=item: self._on_tile_clicked(row_item))
                tile.double_clicked.connect(lambda row_item=item: self._on_tile_double_clicked(row_item))
                tile.hover_entered.connect(lambda row_tile=tile: self._on_tile_hover_entered(row_tile))
                tile.hover_left.connect(lambda row_tile=tile: self._on_tile_hover_left(row_tile))

                if current_selection and exercise == current_selection:
                    self.list_widget.setCurrentItem(item)
                    item.setSelected(True)
                    tile.set_selected(selected=True)
        finally:
            self.list_widget.setUpdatesEnabled(True)

        self.list_widget.itemSelectionChanged.connect(self._on_selection_changed)
        self.list_widget.verticalScrollBar().valueChanged.connect(self._on_list_scrolled)
        self.list_widget.installEventFilter(self)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, self)
        apply_emoji_dialog_buttons(button_box)
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.filter_edit.setFocus()

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        """Handle dialog close event — stop animation."""
        self._stop_animation()
        super().closeEvent(event)

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:  # noqa: N802
        """Handle mouse leave on the list so hover previews stop."""
        if obj == self.list_widget and event.type() == QEvent.Type.Leave:
            self._stop_animation()
            return False

        return super().eventFilter(obj, event)

    def reject(self) -> None:
        """Handle dialog rejection — stop animation."""
        self._stop_animation()
        super().reject()

    def showEvent(self, event: QShowEvent) -> None:  # noqa: N802
        """Start deferred preview loading after the dialog is visible."""
        super().showEvent(event)
        if not self._preview_load_started and self._pending_preview_rows:
            self._preview_load_started = True
            QTimer.singleShot(0, self._decode_next_preview_batch)

    def _decode_next_preview_batch(self) -> None:
        """Decode a time-budgeted batch of still previews, visible rows first."""
        if not self._pending_preview_rows:
            return

        self._prioritize_visible_preview_rows()
        deadline = time.perf_counter() + _PREVIEW_DECODE_BUDGET_S
        while self._pending_preview_rows:
            row = self._pending_preview_rows.pop(0)
            item = self.list_widget.item(row)
            tile = self._tile_for_item(item)
            if tile is None or not tile.pixmap_pending:
                continue
            exercise = item.data(Qt.ItemDataRole.UserRole) if item is not None else None
            name = str(exercise) if exercise else tile.exercise_name
            pixmap = self._pixmap_provider(name)
            tile.set_static_pixmap(pixmap)
            if time.perf_counter() >= deadline:
                break

        if self._pending_preview_rows:
            QTimer.singleShot(0, self._decode_next_preview_batch)

    def _filter_exercises(self, text: str) -> None:
        """Show only tiles whose English or local name matches the query."""
        query = text.strip()
        for row in range(self.list_widget.count()):
            item = self.list_widget.item(row)
            if item is None:
                continue
            exercise = item.data(Qt.ItemDataRole.UserRole)
            name = str(exercise) if exercise else ""
            name_local = self._name_locals.get(name, "").strip()
            matches = (not query) or text_matches_autocomplete(name, query)
            if not matches and name_local:
                matches = text_matches_autocomplete(name_local, query)
            item.setHidden(not matches)
            if not matches:
                tile = self._tile_for_item(item)
                if tile is not None and self._hovered_tile is tile:
                    self._stop_animation()
        if self._pending_preview_rows:
            self._prioritize_visible_preview_rows()

    def _on_accept(self) -> None:
        self._stop_animation()
        item = self.list_widget.currentItem()
        if item is None:
            selected_items = self.list_widget.selectedItems()
            if selected_items:
                item = selected_items[0]
                self.list_widget.setCurrentItem(item)
            elif self.list_widget.count() > 0:
                self.list_widget.setCurrentRow(0)
                item = self.list_widget.currentItem()
        self._update_selected_from_item(item)

        if self.selected_exercise:
            self.accept()
        else:
            self.reject()

    def _on_list_scrolled(self, *_args: object) -> None:
        """Prefer decoding previews that just scrolled into view."""
        if self._pending_preview_rows:
            self._prioritize_visible_preview_rows()

    def _on_selection_changed(self) -> None:
        current = self.list_widget.currentItem()
        for row in range(self.list_widget.count()):
            item = self.list_widget.item(row)
            tile = self._tile_for_item(item)
            if tile is not None and item is not None:
                tile.set_selected(selected=item is current and item.isSelected())
        self._update_selected_from_item(current)

    def _on_tile_clicked(self, item: QListWidgetItem) -> None:
        self.list_widget.setCurrentItem(item)
        item.setSelected(True)
        self._update_selected_from_item(item)

    def _on_tile_double_clicked(self, item: QListWidgetItem) -> None:
        self._stop_animation()
        self.list_widget.setCurrentItem(item)
        item.setSelected(True)
        self._update_selected_from_item(item)
        self.accept()

    def _on_tile_hover_entered(self, tile: _ExercisePreviewTile) -> None:
        """Play animation inside the same QLabel that shows the still preview."""
        if not self._avif_manager:
            return

        if tile.pixmap_pending:
            pixmap = self._pixmap_provider(tile.exercise_name)
            tile.set_static_pixmap(pixmap)
            row = self._row_for_tile(tile)
            if row is not None:
                self._pending_preview_rows = [pending for pending in self._pending_preview_rows if pending != row]

        if self._hovered_tile is not None and self._hovered_tile is not tile:
            self._stop_animation()

        self._hovered_tile = tile
        # Geometry is fixed on the label; no overlay positioning.
        self._avif_manager.load_exercise_avif(
            tile.exercise_name,
            tile.preview_label,
            AvifLabelKey.DIALOG_PREVIEW,
        )

    def _on_tile_hover_left(self, tile: _ExercisePreviewTile) -> None:
        if self._hovered_tile is tile:
            self._stop_animation()

    def _prioritize_visible_preview_rows(self) -> None:
        """Move rows intersecting the viewport to the front of the decode queue."""
        if not self._pending_preview_rows:
            return
        viewport = self.list_widget.viewport().rect()
        visible: list[int] = []
        hidden: list[int] = []
        for row in self._pending_preview_rows:
            item = self.list_widget.item(row)
            if item is None or item.isHidden():
                hidden.append(row)
                continue
            rect = self.list_widget.visualItemRect(item)
            if rect.intersects(viewport):
                visible.append(row)
            else:
                hidden.append(row)
        self._pending_preview_rows = visible + hidden

    def _row_for_tile(self, tile: _ExercisePreviewTile) -> int | None:
        for row in range(self.list_widget.count()):
            item = self.list_widget.item(row)
            if self._tile_for_item(item) is tile:
                return row
        return None

    def _stop_animation(self) -> None:
        """Stop AVIF animation and restore the still preview in the hovered tile."""
        tile = self._hovered_tile
        if self._avif_manager:
            data = self._avif_manager.avif_data.get(AvifLabelKey.DIALOG_PREVIEW)
            if data:
                timer = data.get("timer")
                if timer is not None:
                    timer.stop()
                    data["timer"] = None
                data["frames"] = []
                data["current_frame"] = 0
                data["exercise"] = None

        if tile is not None:
            tile.restore_static_pixmap()
        self._hovered_tile = None

    def _tile_for_item(self, item: QListWidgetItem | None) -> _ExercisePreviewTile | None:
        if item is None:
            return None
        widget = self.list_widget.itemWidget(item)
        return widget if isinstance(widget, _ExercisePreviewTile) else None

    def _update_selected_from_item(self, item: QListWidgetItem | None) -> None:
        if item is None:
            self.selected_exercise = None
            return
        exercise = item.data(Qt.ItemDataRole.UserRole)
        self.selected_exercise = exercise or item.text()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None, *, exercises: list[str], pixmap_provider: Callable[[str], QPixmap | None], preview_size: QSize, current_selection: str | None, avif_manager: AvifManager | None = None, name_locals: dict[str, str] | None = None, display_names: dict[str, str] | None = None) -> None
```

Initialize the ExerciseSelectionDialog.

Args:

- `parent` (`QWidget | None`): Parent widget.
- `exercises` (`list[str]`): List of exercise names to display.
- `pixmap_provider` (`Callable[[str], QPixmap | None]`): Returns a still
  preview pixmap for a given exercise name.
- `preview_size` (`QSize`): Size for icon previews.
- `current_selection` (`str | None`): Currently selected exercise, if any.
- `avif_manager` (`AvifManager | None`): AVIF manager for loading animations. Defaults to `None`.
- `name_locals` (`dict[str, str] | None`): Optional English→local name map.
- `display_names` (`dict[str, str] | None`): Optional English→display label map
  (for example a dumbbell icon prefix).

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        parent: QWidget | None,
        *,
        exercises: list[str],
        pixmap_provider: Callable[[str], QPixmap | None],
        preview_size: QSize,
        current_selection: str | None,
        avif_manager: AvifManager | None = None,
        name_locals: dict[str, str] | None = None,
        display_names: dict[str, str] | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Select Exercise")
        qt_modality.set_owner_window_modal(self)
        self.selected_exercise: str | None = current_selection
        self._pixmap_provider = pixmap_provider
        self._avif_manager = avif_manager
        self._name_locals = name_locals or {}
        self._display_names = display_names or {}
        self._preview_size = preview_size
        self._hovered_tile: _ExercisePreviewTile | None = None
        self._pending_preview_rows: list[int] = []
        self._preview_load_started = False
        has_any_local = any(self._name_locals.get(name, "").strip() for name in exercises)
        text_area_height = 54 if has_any_local else 36

        layout = QVBoxLayout(self)

        self.filter_edit = QLineEdit(self)
        self.filter_edit.setPlaceholderText("Filter exercises…")
        self.filter_edit.setClearButtonEnabled(True)
        self.filter_edit.textChanged.connect(self._filter_exercises)
        layout.addWidget(self.filter_edit)

        self.list_widget = QListWidget(self)
        self.list_widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.list_widget.setViewMode(QListWidget.ViewMode.IconMode)
        self.list_widget.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.list_widget.setMovement(QListWidget.Movement.Static)
        self.list_widget.setSpacing(16)
        self.list_widget.setUniformItemSizes(True)
        self.list_widget.setMouseTracking(True)
        self.list_widget.setStyleSheet(
            """
            QListWidget {
                outline: none;
            }
            QListWidget::item {
                border: none;
                background: transparent;
                padding: 0px;
                margin: 0px;
            }
            QListWidget::item:selected {
                background: transparent;
            }
            QFrame#exercisePreviewTile {
                border: 2px solid transparent;
                border-radius: 4px;
                background: transparent;
            }
            QFrame#exercisePreviewTile:hover {
                border-color: #0078d4;
            }
            QFrame#exercisePreviewTile[selected="true"],
            QFrame#exercisePreviewTile[selected="true"]:hover {
                border-color: #4CAF50;
            }
            """
        )
        layout.addWidget(self.list_widget)

        self.list_widget.setUpdatesEnabled(False)
        try:
            for exercise in exercises:
                item = QListWidgetItem()
                item.setData(Qt.ItemDataRole.UserRole, exercise)
                item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)

                name_local = self._name_locals.get(exercise, "").strip()
                tile = _ExercisePreviewTile(
                    exercise_name=exercise,
                    display_name=self._display_names.get(exercise, exercise),
                    name_local=name_local,
                    static_pixmap=None,
                    preview_size=preview_size,
                    text_area_height=text_area_height,
                    pixmap_pending=True,
                )
                item.setSizeHint(tile.sizeHint())
                self.list_widget.addItem(item)
                self.list_widget.setItemWidget(item, tile)
                self._pending_preview_rows.append(self.list_widget.count() - 1)

                tile.clicked.connect(lambda row_item=item: self._on_tile_clicked(row_item))
                tile.double_clicked.connect(lambda row_item=item: self._on_tile_double_clicked(row_item))
                tile.hover_entered.connect(lambda row_tile=tile: self._on_tile_hover_entered(row_tile))
                tile.hover_left.connect(lambda row_tile=tile: self._on_tile_hover_left(row_tile))

                if current_selection and exercise == current_selection:
                    self.list_widget.setCurrentItem(item)
                    item.setSelected(True)
                    tile.set_selected(selected=True)
        finally:
            self.list_widget.setUpdatesEnabled(True)

        self.list_widget.itemSelectionChanged.connect(self._on_selection_changed)
        self.list_widget.verticalScrollBar().valueChanged.connect(self._on_list_scrolled)
        self.list_widget.installEventFilter(self)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, self)
        apply_emoji_dialog_buttons(button_box)
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.filter_edit.setFocus()
```

</details>

### ⚙️ Method `closeEvent`

```python
def closeEvent(self, event: QCloseEvent) -> None
```

Handle dialog close event — stop animation.

<details>
<summary>Code:</summary>

```python
def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        self._stop_animation()
        super().closeEvent(event)
```

</details>

### ⚙️ Method `eventFilter`

```python
def eventFilter(self, obj: QObject, event: QEvent) -> bool
```

Handle mouse leave on the list so hover previews stop.

<details>
<summary>Code:</summary>

```python
def eventFilter(self, obj: QObject, event: QEvent) -> bool:  # noqa: N802
        if obj == self.list_widget and event.type() == QEvent.Type.Leave:
            self._stop_animation()
            return False

        return super().eventFilter(obj, event)
```

</details>

### ⚙️ Method `reject`

```python
def reject(self) -> None
```

Handle dialog rejection — stop animation.

<details>
<summary>Code:</summary>

```python
def reject(self) -> None:
        self._stop_animation()
        super().reject()
```

</details>

### ⚙️ Method `showEvent`

```python
def showEvent(self, event: QShowEvent) -> None
```

Start deferred preview loading after the dialog is visible.

<details>
<summary>Code:</summary>

```python
def showEvent(self, event: QShowEvent) -> None:  # noqa: N802
        super().showEvent(event)
        if not self._preview_load_started and self._pending_preview_rows:
            self._preview_load_started = True
            QTimer.singleShot(0, self._decode_next_preview_batch)
```

</details>
