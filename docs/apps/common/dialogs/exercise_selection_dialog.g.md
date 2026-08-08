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
        icon_provider: Callable[[str], QIcon | None],
        preview_size: QSize,
        current_selection: str | None,
        avif_manager: AvifManager | None = None,
        name_locals: dict[str, str] | None = None,
    ) -> None:
        """Initialize the ExerciseSelectionDialog.

        Args:

        - `parent` (`QWidget | None`): Parent widget.
        - `exercises` (`list[str]`): List of exercise names to display.
        - `icon_provider` (`Callable[[str], QIcon | None]`): Returns an icon for a given exercise name.
        - `preview_size` (`QSize`): Size for icon previews.
        - `current_selection` (`str | None`): Currently selected exercise, if any.
        - `avif_manager` (`AvifManager | None`): AVIF manager for loading animations. Defaults to `None`.
        - `name_locals` (`dict[str, str] | None`): Optional English→local name map.

        """
        super().__init__(parent)
        self.setWindowTitle("Select Exercise")
        qt_modality.set_owner_window_modal(self)
        self.selected_exercise: str | None = current_selection
        self._icon_provider = icon_provider
        self._avif_manager = avif_manager
        self._name_locals = name_locals or {}
        self._preview_size = preview_size
        self._hovered_tile: _ExercisePreviewTile | None = None
        has_any_local = any(self._name_locals.get(name, "").strip() for name in exercises)
        text_area_height = 54 if has_any_local else 36

        layout = QVBoxLayout(self)

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

        for exercise in exercises:
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, exercise)
            item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)

            static_pixmap = self._static_pixmap_for(exercise)
            name_local = self._name_locals.get(exercise, "").strip()
            tile = _ExercisePreviewTile(
                exercise_name=exercise,
                name_local=name_local,
                static_pixmap=static_pixmap,
                preview_size=preview_size,
                text_area_height=text_area_height,
            )
            item.setSizeHint(tile.sizeHint())
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, tile)

            tile.clicked.connect(lambda row_item=item: self._on_tile_clicked(row_item))
            tile.double_clicked.connect(lambda row_item=item: self._on_tile_double_clicked(row_item))
            tile.hover_entered.connect(lambda row_tile=tile: self._on_tile_hover_entered(row_tile))
            tile.hover_left.connect(lambda row_tile=tile: self._on_tile_hover_left(row_tile))

            if current_selection and exercise == current_selection:
                self.list_widget.setCurrentItem(item)
                item.setSelected(True)
                tile.set_selected(selected=True)

        self.list_widget.itemSelectionChanged.connect(self._on_selection_changed)
        self.list_widget.installEventFilter(self)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, self)
        apply_emoji_dialog_buttons(button_box)
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

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

    def _static_pixmap_for(self, exercise_name: str) -> QPixmap | None:
        icon = self._icon_provider(exercise_name)
        if icon is None or icon.isNull():
            return None
        pixmap = icon.pixmap(self._preview_size)
        return None if pixmap.isNull() else pixmap

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
def __init__(self, parent: QWidget | None, *, exercises: list[str], icon_provider: Callable[[str], QIcon | None], preview_size: QSize, current_selection: str | None, avif_manager: AvifManager | None = None, name_locals: dict[str, str] | None = None) -> None
```

Initialize the ExerciseSelectionDialog.

Args:

- `parent` (`QWidget | None`): Parent widget.
- `exercises` (`list[str]`): List of exercise names to display.
- `icon_provider` (`Callable[[str], QIcon | None]`): Returns an icon for a given exercise name.
- `preview_size` (`QSize`): Size for icon previews.
- `current_selection` (`str | None`): Currently selected exercise, if any.
- `avif_manager` (`AvifManager | None`): AVIF manager for loading animations. Defaults to `None`.
- `name_locals` (`dict[str, str] | None`): Optional English→local name map.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        parent: QWidget | None,
        *,
        exercises: list[str],
        icon_provider: Callable[[str], QIcon | None],
        preview_size: QSize,
        current_selection: str | None,
        avif_manager: AvifManager | None = None,
        name_locals: dict[str, str] | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Select Exercise")
        qt_modality.set_owner_window_modal(self)
        self.selected_exercise: str | None = current_selection
        self._icon_provider = icon_provider
        self._avif_manager = avif_manager
        self._name_locals = name_locals or {}
        self._preview_size = preview_size
        self._hovered_tile: _ExercisePreviewTile | None = None
        has_any_local = any(self._name_locals.get(name, "").strip() for name in exercises)
        text_area_height = 54 if has_any_local else 36

        layout = QVBoxLayout(self)

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

        for exercise in exercises:
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, exercise)
            item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)

            static_pixmap = self._static_pixmap_for(exercise)
            name_local = self._name_locals.get(exercise, "").strip()
            tile = _ExercisePreviewTile(
                exercise_name=exercise,
                name_local=name_local,
                static_pixmap=static_pixmap,
                preview_size=preview_size,
                text_area_height=text_area_height,
            )
            item.setSizeHint(tile.sizeHint())
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, tile)

            tile.clicked.connect(lambda row_item=item: self._on_tile_clicked(row_item))
            tile.double_clicked.connect(lambda row_item=item: self._on_tile_double_clicked(row_item))
            tile.hover_entered.connect(lambda row_tile=tile: self._on_tile_hover_entered(row_tile))
            tile.hover_left.connect(lambda row_tile=tile: self._on_tile_hover_left(row_tile))

            if current_selection and exercise == current_selection:
                self.list_widget.setCurrentItem(item)
                item.setSelected(True)
                tile.set_selected(selected=True)

        self.list_widget.itemSelectionChanged.connect(self._on_selection_changed)
        self.list_widget.installEventFilter(self)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, self)
        apply_emoji_dialog_buttons(button_box)
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
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
