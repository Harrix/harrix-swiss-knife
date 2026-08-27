---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `workouts_widget.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `WorkoutsWidget`](#%EF%B8%8F-class-workoutswidget)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `configure_exercise_images`](#%EF%B8%8F-method-configure_exercise_images)
  - [⚙️ Method `exercise_at_image`](#%EF%B8%8F-method-exercise_at_image)
  - [⚙️ Method `refresh`](#%EF%B8%8F-method-refresh)
  - [⚙️ Method `select_workout_by_id`](#%EF%B8%8F-method-select_workout_by_id)
  - [⚙️ Method `set_database_manager`](#%EF%B8%8F-method-set_database_manager)
  - [⚙️ Method `update_exercise_icon`](#%EF%B8%8F-method-update_exercise_icon)

</details>

## 🏛️ Class `WorkoutsWidget`

```python
class WorkoutsWidget(QWidget)
```

Split view: saved workouts on the left, items and Done checkboxes on the right.

<details>
<summary>Code:</summary>

```python
class WorkoutsWidget(QWidget):

    generate_requested = Signal()
    workouts_changed = Signal()
    item_done_requested = Signal(int)
    exercise_lightbox_requested = Signal(str)
    items_reloading = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        """Build the workouts UI; call `set_database_manager` before loading data."""
        super().__init__(parent)
        self._db: DatabaseManager | None = None
        self._current_workout_id: int | None = None
        self._item_ids: list[int] = []
        self._icon_getter: Callable[[str], QIcon | None] | None = None
        self._icon_size = _DEFAULT_TABLE_ICON_SIZE
        self._build_ui()

    def configure_exercise_images(
        self,
        *,
        icon_size: int,
        icon_getter: Callable[[str], QIcon | None] | None,
    ) -> None:
        """Set thumbnail size and the callback that loads exercise icons."""
        self._icon_size = max(icon_size, 1)
        self._icon_getter = icon_getter
        self._apply_image_column_metrics()

    def exercise_at_image(self, pos: QPoint) -> str | None:
        """Return the exercise name when `pos` is over a workout-row thumbnail."""
        return exercise_at_table_image(
            self.table_items,
            pos,
            image_column=_COL_IMAGE,
            name_column=_COL_EXERCISE,
        )

    def refresh(self) -> None:
        """Reload the workout list, keeping the current selection when possible."""
        self._reload_list(keep_selection=True)

    def select_workout_by_id(self, workout_id: int) -> None:
        """Select a workout in the list after a refresh."""
        for row in range(self._list_model.rowCount()):
            item = self._list_model.item(row)
            if item is not None and item.data(Qt.ItemDataRole.UserRole) == workout_id:
                self.list_workouts.setCurrentIndex(self._list_model.indexFromItem(item))
                self._load_workout(workout_id)
                return

    def set_database_manager(self, db_manager: DatabaseManager | None) -> None:
        """Attach the fitness database and refresh the list."""
        self._db = db_manager
        self.refresh()

    def update_exercise_icon(self, exercise_name: str, icon: QIcon | None) -> None:
        """Refresh the image-column icon for every row of `exercise_name`."""
        if not exercise_name:
            return
        resolved = icon if icon is not None else QIcon()
        for row in range(self.table_items.rowCount()):
            name_item = self.table_items.item(row, _COL_EXERCISE)
            if name_item is None or name_item.text().strip() != exercise_name:
                continue
            image_item = self.table_items.item(row, _COL_IMAGE)
            if image_item is None:
                image_item = QTableWidgetItem()
                image_item.setFlags(image_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table_items.setItem(row, _COL_IMAGE, image_item)
            image_item.setIcon(resolved)

    def _apply_image_column_metrics(self) -> None:
        self.table_items.setIconSize(QSize(self._icon_size, self._icon_size))
        self.table_items.verticalHeader().setDefaultSectionSize(self._icon_size + 8)
        header = self.table_items.horizontalHeader()
        header.setSectionResizeMode(_COL_DONE, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(_COL_IMAGE, QHeaderView.ResizeMode.Fixed)
        self.table_items.setColumnWidth(_COL_DONE, _DONE_COLUMN_WIDTH)
        self.table_items.setColumnWidth(_COL_IMAGE, self._icon_size + 12)

    def _build_ui(self) -> None:
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        root.addWidget(splitter)

        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(8, 8, 8, 8)
        left_layout.addWidget(QLabel("Workouts"))
        self.list_workouts = QListView()
        self._list_model = QStandardItemModel(self.list_workouts)
        self.list_workouts.setModel(self._list_model)
        self.list_workouts.clicked.connect(self._on_workout_clicked)
        left_layout.addWidget(self.list_workouts, 1)
        buttons = QHBoxLayout()
        self.button_new = make_emoji_push_button("New", "➕")  # noqa: RUF001
        self.button_delete = make_emoji_push_button("Delete", "🗑️")
        self.button_new.clicked.connect(self.generate_requested.emit)
        self.button_delete.clicked.connect(self._delete_workout)
        buttons.addWidget(self.button_new)
        buttons.addWidget(self.button_delete)
        left_layout.addLayout(buttons)
        splitter.addWidget(left)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(8, 8, 8, 8)
        self.label_title = QLabel("Select a workout")
        self.label_meta = QLabel("")
        right_layout.addWidget(self.label_title)
        right_layout.addWidget(self.label_meta)

        self.table_items = QTableWidget(0, _ITEM_COLUMN_COUNT)
        self.table_items.setHorizontalHeaderLabels(["Done", "", "Exercise", "Type", "Value", "Unit", "kcal"])
        self.table_items.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_items.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_items.doubleClicked.connect(self._on_item_double_clicked)
        self._apply_image_column_metrics()
        right_layout.addWidget(self.table_items, 1)
        self.label_totals = QLabel("")
        right_layout.addWidget(self.label_totals)
        splitter.addWidget(right)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)

    def _clear_detail(self) -> None:
        self.items_reloading.emit()
        self._current_workout_id = None
        self._item_ids = []
        self.label_title.setText("Select a workout")
        self.label_meta.setText("")
        self.label_totals.setText("")
        self.table_items.setRowCount(0)

    def _delete_workout(self) -> None:
        if self._db is None or self._current_workout_id is None:
            message_box.warning(self, "Error", "Select a workout to delete")
            return
        workout_id = self._current_workout_id
        name = self.label_title.text()
        reply = message_box.question(
            self,
            "Delete workout?",
            f"Delete '{name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        if not self._db.delete_workout(workout_id):
            message_box.warning(self, "Error", "Failed to delete workout")
            return
        self._clear_detail()
        self._reload_list(keep_selection=False)
        self.workouts_changed.emit()

    def _estimated_kcal(self, item: WorkoutItemRow) -> float:
        try:
            value = float(item.target_value)
        except (TypeError, ValueError):
            return 0.0
        return value * item.calories_per_unit * item.calories_modifier

    def _fill_items(self, items: list[WorkoutItemRow]) -> None:
        self.items_reloading.emit()
        self.table_items.setRowCount(0)
        self._item_ids = []
        total_kcal = 0.0
        for item in items:
            row = self.table_items.rowCount()
            self.table_items.insertRow(row)
            self._item_ids.append(item.id)
            checkbox = QCheckBox()
            checkbox.setChecked(item.is_done)
            checkbox.setEnabled(not item.is_done)
            if not item.is_done:
                checkbox.clicked.connect(
                    lambda checked, item_id=item.id: self._on_done_toggled(item_id=item_id, checked=checked),
                )
            self.table_items.setCellWidget(row, _COL_DONE, checkbox)
            image_item = QTableWidgetItem()
            image_item.setFlags(image_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            icon = self._icon_getter(item.exercise_name) if self._icon_getter is not None else None
            if icon is not None and not icon.isNull():
                image_item.setIcon(icon)
            self.table_items.setItem(row, _COL_IMAGE, image_item)
            self.table_items.setItem(row, _COL_EXERCISE, QTableWidgetItem(item.exercise_name))
            self.table_items.setItem(row, _COL_TYPE, QTableWidgetItem(item.type_name))
            self.table_items.setItem(row, _COL_VALUE, QTableWidgetItem(item.target_value))
            unit = item.unit or "times"
            self.table_items.setItem(row, _COL_UNIT, QTableWidgetItem(unit))
            kcal = self._estimated_kcal(item)
            total_kcal += kcal
            self.table_items.setItem(row, _COL_KCAL, QTableWidgetItem(f"{kcal:.1f}"))
        self.label_totals.setText(f"Estimated: {total_kcal:.0f} kcal")

    def _load_workout(self, workout_id: int) -> None:
        if self._db is None:
            return
        workout = self._db.get_workout_by_id(workout_id)
        if workout is None:
            return
        self._current_workout_id = workout.id
        self.label_title.setText(workout.name)
        self.label_meta.setText(f"{workout.gender} · {workout.duration_min} min · {workout.created_date}")
        items = self._db.get_workout_items(workout_id)
        self._fill_items(items)

    def _on_done_toggled(self, *, item_id: int, checked: bool) -> None:
        if not checked:
            return
        self.item_done_requested.emit(item_id)

    def _on_item_double_clicked(self, index: QModelIndex) -> None:
        row = index.row()
        name_item = self.table_items.item(row, _COL_EXERCISE)
        if name_item is None:
            return
        name = name_item.text().strip()
        if name:
            self.exercise_lightbox_requested.emit(name)

    def _on_workout_clicked(self, index: QModelIndex) -> None:
        item = self._list_model.itemFromIndex(index)
        if item is None:
            return
        workout_id = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(workout_id, int):
            self._load_workout(workout_id)

    def _reload_list(self, *, keep_selection: bool) -> None:
        selected_id = self._current_workout_id if keep_selection else None
        self._list_model.clear()
        if self._db is None:
            return
        workouts: list[WorkoutRow] = self._db.get_all_workouts()
        for workout in workouts:
            item = QStandardItem(f"{workout.name} ({workout.duration_min} min)")
            item.setData(workout.id, Qt.ItemDataRole.UserRole)
            item.setEditable(False)
            self._list_model.appendRow(item)
        if selected_id is not None:
            self.select_workout_by_id(selected_id)
        elif workouts:
            self.select_workout_by_id(workouts[0].id)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Build the workouts UI; call `set_database_manager` before loading data.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._db: DatabaseManager | None = None
        self._current_workout_id: int | None = None
        self._item_ids: list[int] = []
        self._icon_getter: Callable[[str], QIcon | None] | None = None
        self._icon_size = _DEFAULT_TABLE_ICON_SIZE
        self._build_ui()
```

</details>

### ⚙️ Method `configure_exercise_images`

```python
def configure_exercise_images(self, *, icon_size: int, icon_getter: Callable[[str], QIcon | None] | None) -> None
```

Set thumbnail size and the callback that loads exercise icons.

<details>
<summary>Code:</summary>

```python
def configure_exercise_images(
        self,
        *,
        icon_size: int,
        icon_getter: Callable[[str], QIcon | None] | None,
    ) -> None:
        self._icon_size = max(icon_size, 1)
        self._icon_getter = icon_getter
        self._apply_image_column_metrics()
```

</details>

### ⚙️ Method `exercise_at_image`

```python
def exercise_at_image(self, pos: QPoint) -> str | None
```

Return the exercise name when `pos` is over a workout-row thumbnail.

<details>
<summary>Code:</summary>

```python
def exercise_at_image(self, pos: QPoint) -> str | None:
        return exercise_at_table_image(
            self.table_items,
            pos,
            image_column=_COL_IMAGE,
            name_column=_COL_EXERCISE,
        )
```

</details>

### ⚙️ Method `refresh`

```python
def refresh(self) -> None
```

Reload the workout list, keeping the current selection when possible.

<details>
<summary>Code:</summary>

```python
def refresh(self) -> None:
        self._reload_list(keep_selection=True)
```

</details>

### ⚙️ Method `select_workout_by_id`

```python
def select_workout_by_id(self, workout_id: int) -> None
```

Select a workout in the list after a refresh.

<details>
<summary>Code:</summary>

```python
def select_workout_by_id(self, workout_id: int) -> None:
        for row in range(self._list_model.rowCount()):
            item = self._list_model.item(row)
            if item is not None and item.data(Qt.ItemDataRole.UserRole) == workout_id:
                self.list_workouts.setCurrentIndex(self._list_model.indexFromItem(item))
                self._load_workout(workout_id)
                return
```

</details>

### ⚙️ Method `set_database_manager`

```python
def set_database_manager(self, db_manager: DatabaseManager | None) -> None
```

Attach the fitness database and refresh the list.

<details>
<summary>Code:</summary>

```python
def set_database_manager(self, db_manager: DatabaseManager | None) -> None:
        self._db = db_manager
        self.refresh()
```

</details>

### ⚙️ Method `update_exercise_icon`

```python
def update_exercise_icon(self, exercise_name: str, icon: QIcon | None) -> None
```

Refresh the image-column icon for every row of `exercise_name`.

<details>
<summary>Code:</summary>

```python
def update_exercise_icon(self, exercise_name: str, icon: QIcon | None) -> None:
        if not exercise_name:
            return
        resolved = icon if icon is not None else QIcon()
        for row in range(self.table_items.rowCount()):
            name_item = self.table_items.item(row, _COL_EXERCISE)
            if name_item is None or name_item.text().strip() != exercise_name:
                continue
            image_item = self.table_items.item(row, _COL_IMAGE)
            if image_item is None:
                image_item = QTableWidgetItem()
                image_item.setFlags(image_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table_items.setItem(row, _COL_IMAGE, image_item)
            image_item.setIcon(resolved)
```

</details>
