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
  - [⚙️ Method `is_workout_session_active`](#%EF%B8%8F-method-is_workout_session_active)
  - [⚙️ Method `notify_workout_progress`](#%EF%B8%8F-method-notify_workout_progress)
  - [⚙️ Method `refresh`](#%EF%B8%8F-method-refresh)
  - [⚙️ Method `select_workout_by_id`](#%EF%B8%8F-method-select_workout_by_id)
  - [⚙️ Method `set_database_manager`](#%EF%B8%8F-method-set_database_manager)
  - [⚙️ Method `stop_workout_session`](#%EF%B8%8F-method-stop_workout_session)
  - [⚙️ Method `update_exercise_icon`](#%EF%B8%8F-method-update_exercise_icon)
- [🔧 Function `estimate_workout_item_kcal`](#-function-estimate_workout_item_kcal)

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
    item_done_requested = Signal(int, bool)
    exercise_lightbox_requested = Signal(int)
    items_reloading = Signal()
    workout_session_started = Signal(int)

    def __init__(self, parent: QWidget | None = None) -> None:
        """Build the workouts UI; call `set_database_manager` before loading data."""
        super().__init__(parent)
        self._db: DatabaseManager | None = None
        self._current_workout_id: int | None = None
        self._item_ids: list[int] = []
        self._item_calories_per_unit: list[float] = []
        self._item_calories_modifier: list[float] = []
        self._filling_items = False
        self._icon_getter: Callable[[str], QIcon | None] | None = None
        self._icon_size = _DEFAULT_TABLE_ICON_SIZE
        self._session_active = False
        self._session_workout_id: int | None = None
        self._session_elapsed = QElapsedTimer()
        self._session_timer = QTimer(self)
        self._session_timer.setInterval(1000)
        self._session_timer.timeout.connect(self._tick_session_timer)
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

    def is_workout_session_active(self) -> bool:
        """Return whether a workout session timer is running."""
        return self._session_active

    def notify_workout_progress(self) -> None:
        """After an item is marked done, finish the session or open the next exercise."""
        if not self._session_active or self._session_workout_id != self._current_workout_id:
            return
        if self._all_items_done():
            self.stop_workout_session(completed=True)
            return
        next_item_id = self._first_incomplete_item_id()
        if next_item_id is not None:
            self.workout_session_started.emit(next_item_id)

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

    def stop_workout_session(self, *, completed: bool = False) -> None:
        """Stop the workout session timer and restore the normal UI."""
        if not self._session_active:
            return
        elapsed_seconds = self._session_elapsed_seconds()
        self._session_active = False
        self._session_workout_id = None
        self._session_timer.stop()
        self._session_bar.hide()
        self._update_start_button()
        self._update_session_ui_locked()
        if completed:
            message_box.information(
                self,
                "Workout complete",
                f"All exercises finished in {format_mm_ss(elapsed_seconds)}.",
            )

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
            self._apply_row_background(row)

    def _all_items_done(self) -> bool:
        if self._db is None or self._current_workout_id is None:
            return False
        items = self._db.get_workout_items(self._current_workout_id)
        return bool(items) and all(item.is_done for item in items)

    def _apply_image_column_metrics(self) -> None:
        self.table_items.setIconSize(QSize(self._icon_size, self._icon_size))
        self.table_items.verticalHeader().setDefaultSectionSize(self._icon_size + 8)
        header = self.table_items.horizontalHeader()
        header.setSectionResizeMode(_COL_DONE, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(_COL_IMAGE, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(_COL_EXERCISE, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(_COL_TYPE, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(_COL_VALUE, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(_COL_UNIT, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(_COL_KCAL, QHeaderView.ResizeMode.Interactive)
        header.setStretchLastSection(False)
        self.table_items.setColumnWidth(_COL_DONE, _DONE_COLUMN_WIDTH)
        self.table_items.setColumnWidth(_COL_IMAGE, self._icon_size + 12)
        self.table_items.setColumnWidth(_COL_TYPE, _COL_TYPE_WIDTH)
        self.table_items.setColumnWidth(_COL_VALUE, _COL_VALUE_WIDTH)
        self.table_items.setColumnWidth(_COL_UNIT, _COL_UNIT_WIDTH)
        self.table_items.setColumnWidth(_COL_KCAL, _COL_VALUE_WIDTH)

    def _apply_row_background(self, row: int) -> None:
        color = _ROW_COLOR_ODD if row % 2 else _ROW_COLOR_EVEN
        brush = QBrush(color)
        for column in range(_ITEM_COLUMN_COUNT):
            item = self.table_items.item(row, column)
            if item is not None:
                item.setBackground(brush)
        cell = self.table_items.cellWidget(row, _COL_DONE)
        if cell is not None:
            palette = cell.palette()
            palette.setColor(QPalette.ColorRole.Window, color)
            cell.setAutoFillBackground(True)
            cell.setPalette(palette)

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        font_12_bold = QFont()
        font_12_bold.setPointSize(12)
        font_12_bold.setBold(True)
        font_title = QFont()
        font_title.setPointSize(14)
        font_title.setBold(True)
        font_timer = QFont()
        font_timer.setPointSize(28)
        font_timer.setBold(True)

        self._session_bar = QFrame()
        self._session_bar.setObjectName("workoutsSessionBar")
        self._session_bar.setStyleSheet(_SESSION_BAR_STYLE)
        session_layout = QHBoxLayout(self._session_bar)
        session_layout.setContentsMargins(12, 8, 12, 8)
        session_layout.setSpacing(16)
        session_layout.addStretch(1)
        self.label_session_timer = QLabel("0:00")
        self.label_session_timer.setFont(font_timer)
        self.label_session_timer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_session_timer.setMinimumWidth(140)
        session_layout.addWidget(self.label_session_timer)
        self.button_stop = QPushButton("Stop")
        self.button_stop.setIcon(create_emoji_icon("⏹"))
        self.button_stop.setMinimumHeight(41)
        self.button_stop.setMinimumWidth(110)
        self.button_stop.setFont(font_12_bold)
        self.button_stop.setStyleSheet(_STOP_BUTTON_STYLE)
        self.button_stop.clicked.connect(lambda: self.stop_workout_session(completed=False))
        session_layout.addWidget(self.button_stop)
        session_layout.addStretch(1)
        self._session_bar.hide()
        root.addWidget(self._session_bar)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        root.addWidget(splitter, 1)

        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(8, 8, 8, 8)
        left_layout.addWidget(QLabel("Workouts"))
        self.button_new = QPushButton("New")
        self.button_new.setIcon(create_emoji_icon("➕"))  # noqa: RUF001
        self.button_new.setMinimumHeight(41)
        self.button_new.setFont(font_12_bold)
        self.button_new.setStyleSheet(_GREEN_BUTTON_STYLE)
        self.button_new.clicked.connect(self.generate_requested.emit)
        left_layout.addWidget(self.button_new)
        self.list_workouts = QListView()
        self.list_workouts.setStyleSheet(_LIST_STYLE)
        self._list_model = QStandardItemModel(self.list_workouts)
        self.list_workouts.setModel(self._list_model)
        self.list_workouts.clicked.connect(self._on_workout_clicked)
        self.list_workouts.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_workouts.customContextMenuRequested.connect(self._show_workouts_context_menu)
        left_layout.addWidget(self.list_workouts, 1)
        splitter.addWidget(left)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(8, 8, 8, 8)
        title_row = QHBoxLayout()
        self.label_title = QLabel("Select a workout")
        self.label_title.setFont(font_title)
        title_row.addWidget(self.label_title, 1)
        self.button_start = QPushButton("Start")
        self.button_start.setIcon(create_emoji_icon("▶"))
        self.button_start.setMinimumHeight(41)
        self.button_start.setMinimumWidth(120)
        self.button_start.setFont(font_12_bold)
        self.button_start.setStyleSheet(_GREEN_BUTTON_STYLE)
        self.button_start.clicked.connect(self._start_workout_session)
        title_row.addWidget(self.button_start)
        right_layout.addLayout(title_row)
        self.label_meta = QLabel("")
        right_layout.addWidget(self.label_meta)
        duration_row = QHBoxLayout()
        duration_row.addWidget(QLabel("Duration:"))
        self.label_duration = QLabel("")
        duration_row.addWidget(self.label_duration)
        duration_row.addStretch()
        right_layout.addLayout(duration_row)

        self.table_items = QTableWidget(0, _ITEM_COLUMN_COUNT)
        self.table_items.setObjectName("workoutsItemsTable")
        self.table_items.setHorizontalHeaderLabels(["Done", "", "Exercise", "Type", "Value", "Unit", "kcal"])
        self.table_items.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_items.setAlternatingRowColors(False)
        self.table_items.setEditTriggers(
            QAbstractItemView.EditTrigger.DoubleClicked | QAbstractItemView.EditTrigger.SelectedClicked,
        )
        self.table_items.verticalHeader().setVisible(False)
        self.table_items.setItemDelegateForColumn(_COL_IMAGE, _WorkoutImageDelegate(self.table_items))
        self.table_items.itemChanged.connect(self._on_table_item_changed)
        self.table_items.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table_items.customContextMenuRequested.connect(self._show_items_context_menu)
        self.table_items.doubleClicked.connect(self._on_item_double_clicked)
        self._apply_image_column_metrics()
        right_layout.addWidget(self.table_items, 1)
        self.label_totals = QLabel("")
        right_layout.addWidget(self.label_totals)
        QShortcut(QKeySequence.StandardKey.Delete, self.table_items, self._remove_selected_items)
        splitter.addWidget(right)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)

    def _can_start_workout(self) -> bool:
        return self._current_workout_id is not None and self._db is not None and not self._all_items_done()

    def _clear_detail(self) -> None:
        if self._session_active:
            self.stop_workout_session(completed=False)
        self.items_reloading.emit()
        self._current_workout_id = None
        self._item_ids = []
        self._item_calories_per_unit = []
        self._item_calories_modifier = []
        self.label_title.setText("Select a workout")
        self.label_meta.setText("")
        self.label_duration.setText("")
        self.label_totals.setText("")
        self.table_items.setRowCount(0)
        self._update_start_button()

    def _collect_duration_items(self) -> list[tuple[str, str]]:
        items: list[tuple[str, str]] = []
        for row in range(self.table_items.rowCount()):
            value_item = self.table_items.item(row, _COL_VALUE)
            unit_item = self.table_items.item(row, _COL_UNIT)
            if value_item is None or unit_item is None:
                continue
            items.append((value_item.text().strip(), unit_item.text().strip()))
        return items

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
        return estimate_workout_item_kcal(
            item.target_value,
            calories_per_unit=item.calories_per_unit,
            calories_modifier=item.calories_modifier,
        )

    def _fill_items(self, items: list[WorkoutItemRow]) -> None:
        self.items_reloading.emit()
        self._filling_items = True
        self.table_items.blockSignals(True)  # noqa: FBT003
        self.table_items.setRowCount(0)
        self._item_ids = []
        self._item_calories_per_unit = []
        self._item_calories_modifier = []
        total_kcal = 0.0
        try:
            for item in items:
                row = self.table_items.rowCount()
                self.table_items.insertRow(row)
                self._item_ids.append(item.id)
                self._item_calories_per_unit.append(item.calories_per_unit)
                self._item_calories_modifier.append(item.calories_modifier)
                checkbox = QCheckBox()
                checkbox.setChecked(item.is_done)
                checkbox.clicked.connect(
                    lambda checked, item_id=item.id: self._on_done_toggled(item_id=item_id, checked=checked),
                )
                self.table_items.setCellWidget(row, _COL_DONE, _make_done_cell(checkbox))
                image_item = QTableWidgetItem()
                image_item.setFlags(image_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                icon = self._icon_getter(item.exercise_name) if self._icon_getter is not None else None
                if icon is not None and not icon.isNull():
                    image_item.setIcon(icon)
                self.table_items.setItem(row, _COL_IMAGE, image_item)
                self._set_readonly_item(row, _COL_EXERCISE, item.exercise_name)
                self._set_readonly_item(row, _COL_TYPE, item.type_name)
                value_item = QTableWidgetItem(item.target_value)
                if item.is_done:
                    value_item.setFlags(value_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table_items.setItem(row, _COL_VALUE, value_item)
                unit = item.unit or "times"
                self._set_readonly_item(row, _COL_UNIT, unit)
                kcal = self._estimated_kcal(item)
                total_kcal += kcal
                self._set_readonly_item(row, _COL_KCAL, f"{kcal:.1f}")
                self._apply_row_background(row)
            self.label_totals.setText(f"Estimated: {total_kcal:.0f} kcal")
            self._sync_duration_from_items()
            self._update_start_button()
        finally:
            self.table_items.blockSignals(False)  # noqa: FBT003
            self._filling_items = False

    def _first_incomplete_item_id(self) -> int | None:
        if self._db is None or self._current_workout_id is None:
            return None
        for item in self._db.get_workout_items(self._current_workout_id):
            if not item.is_done:
                return item.id
        return None

    def _load_workout(self, workout_id: int) -> None:
        if self._session_active and self._session_workout_id != workout_id:
            return
        if self._db is None:
            return
        workout = self._db.get_workout_by_id(workout_id)
        if workout is None:
            return
        self._current_workout_id = workout.id
        self.label_title.setText(workout.name)
        self.label_meta.setText(f"{workout.gender} · {workout.created_date}")
        items = self._db.get_workout_items(workout_id)
        self._fill_items(items)

    def _on_done_toggled(self, *, item_id: int, checked: bool) -> None:
        self.item_done_requested.emit(item_id, checked)

    def _on_item_double_clicked(self, index: QModelIndex) -> None:
        if index.column() == _COL_VALUE:
            value_item = self.table_items.item(index.row(), _COL_VALUE)
            if value_item is not None and value_item.flags() & Qt.ItemFlag.ItemIsEditable:
                self.table_items.editItem(value_item)
            return
        row = index.row()
        if 0 <= row < len(self._item_ids):
            self.exercise_lightbox_requested.emit(self._item_ids[row])

    def _on_table_item_changed(self, item: QTableWidgetItem) -> None:
        if self._filling_items or item.column() != _COL_VALUE:
            return
        row = item.row()
        if row < 0 or row >= len(self._item_ids):
            return
        new_value = item.text().strip()
        item_id = self._item_ids[row]
        if self._db is not None and not self._db.update_workout_item_target_value(item_id, new_value):
            message_box.warning(self, "Error", "Failed to update workout value")
            stored = self._db.get_workout_item_by_id(item_id)
            self._filling_items = True
            item.setText(stored.target_value if stored is not None else "")
            self._filling_items = False
            return
        self._update_row_kcal(row)
        self._sync_duration_from_items()
        self.workouts_changed.emit()

    def _on_workout_clicked(self, index: QModelIndex) -> None:
        if self._session_active:
            return
        item = self._list_model.itemFromIndex(index)
        if item is None:
            return
        workout_id = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(workout_id, int):
            self._load_workout(workout_id)

    def _refresh_kcal_totals(self) -> None:
        total_kcal = 0.0
        for row in range(self.table_items.rowCount()):
            kcal_item = self.table_items.item(row, _COL_KCAL)
            if kcal_item is None:
                continue
            try:
                total_kcal += float(kcal_item.text())
            except ValueError:
                continue
        self.label_totals.setText(f"Estimated: {total_kcal:.0f} kcal")

    def _refresh_list_duration_label(self, duration_min: int) -> None:
        workout_id = self._current_workout_id
        if workout_id is None:
            return
        name = self.label_title.text()
        for row in range(self._list_model.rowCount()):
            item = self._list_model.item(row)
            if item is not None and item.data(Qt.ItemDataRole.UserRole) == workout_id:
                item.setText(f"{name} (~{duration_min} min)")
                return

    def _reload_list(self, *, keep_selection: bool) -> None:
        selected_id = self._current_workout_id if keep_selection else None
        self._list_model.clear()
        if self._db is None:
            return
        workouts: list[WorkoutRow] = self._db.get_all_workouts()
        for workout in workouts:
            item = QStandardItem(f"{workout.name} (~{workout.duration_min} min)")
            item.setData(workout.id, Qt.ItemDataRole.UserRole)
            item.setEditable(False)
            self._list_model.appendRow(item)
        if selected_id is not None:
            self.select_workout_by_id(selected_id)
        elif workouts:
            self.select_workout_by_id(workouts[0].id)

    def _remove_selected_items(self) -> None:
        if self._db is None or self._current_workout_id is None:
            message_box.warning(self, "Error", "Select a workout first")
            return
        item_ids = self._selected_item_ids()
        if not item_ids:
            message_box.warning(self, "Error", "Select a row to remove")
            return
        names = self._selected_exercise_names()
        label = ", ".join(names) if names else "selected row(s)"
        reply = message_box.question(
            self,
            "Remove exercise?",
            f"Remove {label} from this workout?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        workout_id = self._current_workout_id
        for item_id in item_ids:
            if not self._db.delete_workout_item(item_id):
                message_box.warning(self, "Error", "Failed to remove workout row")
                self._load_workout(workout_id)
                return
        self._load_workout(workout_id)
        self.workouts_changed.emit()

    def _selected_exercise_names(self) -> list[str]:
        names: list[str] = []
        for row in self._selected_rows():
            name_item = self.table_items.item(row, _COL_EXERCISE)
            if name_item is not None and name_item.text().strip():
                names.append(name_item.text().strip())
        return names

    def _selected_item_ids(self) -> list[int]:
        return [self._item_ids[row] for row in self._selected_rows() if 0 <= row < len(self._item_ids)]

    def _selected_rows(self) -> list[int]:
        return sorted({index.row() for index in self.table_items.selectedIndexes()})

    def _session_elapsed_seconds(self) -> int:
        if not self._session_elapsed.isValid():
            return 0
        return max(0, self._session_elapsed.elapsed() // 1000)

    def _set_duration_label(self, duration_min: int) -> None:
        self.label_duration.setText(f"~{duration_min} min")

    def _set_readonly_item(self, row: int, column: int, text: str) -> None:
        cell = QTableWidgetItem(text)
        cell.setFlags(cell.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.table_items.setItem(row, column, cell)

    def _show_items_context_menu(self, position: QPoint) -> None:
        index = self.table_items.indexAt(position)
        if index.isValid() and not self.table_items.selectionModel().isSelected(index):
            self.table_items.selectRow(index.row())
        context_menu = QMenu(self)
        lightbox_action = context_menu.addAction(LABEL_OPEN_LIGHTBOX)
        delete_action = add_delete_action(context_menu)
        apply_leading_emoji_icons(context_menu)
        action = context_menu.exec_(self.table_items.mapToGlobal(position))
        if action == lightbox_action:
            target = index if index.isValid() else self.table_items.currentIndex()
            if target.isValid():
                self._on_item_double_clicked(target)
        elif action == delete_action:
            self._remove_selected_items()

    def _show_workouts_context_menu(self, position: QPoint) -> None:
        index = self.list_workouts.indexAt(position)
        if index.isValid():
            self.list_workouts.setCurrentIndex(index)
            item = self._list_model.itemFromIndex(index)
            if item is not None:
                workout_id = item.data(Qt.ItemDataRole.UserRole)
                if isinstance(workout_id, int):
                    self._load_workout(workout_id)
        context_menu = QMenu(self)
        new_action = context_menu.addAction("➕ New")  # noqa: RUF001
        delete_action = add_delete_action(context_menu)
        delete_action.setEnabled(self._current_workout_id is not None)
        if self._session_active:
            new_action.setEnabled(False)
            delete_action.setEnabled(False)
        apply_leading_emoji_icons(context_menu)
        action = context_menu.exec_(self.list_workouts.mapToGlobal(position))
        if action == new_action:
            self.generate_requested.emit()
        elif action == delete_action:
            self._delete_workout()

    def _start_workout_session(self) -> None:
        if self._session_active:
            return
        if not self._can_start_workout():
            if self._current_workout_id is None:
                message_box.warning(self, "Error", "Select a workout first")
            elif self._all_items_done():
                message_box.information(self, "Workout", "All exercises are already done")
            return
        first_item_id = self._first_incomplete_item_id()
        if first_item_id is None:
            message_box.information(self, "Workout", "All exercises are already done")
            return
        self._session_active = True
        self._session_workout_id = self._current_workout_id
        self._session_elapsed.start()
        self._update_session_timer_label()
        self._session_bar.show()
        self._update_start_button()
        self._update_session_ui_locked()
        self._session_timer.start()
        self.workout_session_started.emit(first_item_id)

    def _sync_duration_from_items(self) -> None:
        if self._current_workout_id is None:
            self.label_duration.setText("")
            return
        duration = estimate_workout_duration_min(self._collect_duration_items())
        self._set_duration_label(duration)
        if self._db is not None and not self._db.update_workout_duration(self._current_workout_id, duration):
            message_box.warning(self, "Error", "Failed to update workout duration")
            return
        self._refresh_list_duration_label(duration)

    def _tick_session_timer(self) -> None:
        if self._session_active:
            self._update_session_timer_label()

    def _update_row_kcal(self, row: int) -> None:
        value_item = self.table_items.item(row, _COL_VALUE)
        kcal_item = self.table_items.item(row, _COL_KCAL)
        if value_item is None or kcal_item is None:
            return
        if row >= len(self._item_calories_per_unit) or row >= len(self._item_calories_modifier):
            return
        kcal = estimate_workout_item_kcal(
            value_item.text(),
            calories_per_unit=self._item_calories_per_unit[row],
            calories_modifier=self._item_calories_modifier[row],
        )
        self._filling_items = True
        kcal_item.setText(f"{kcal:.1f}")
        self._filling_items = False
        self._apply_row_background(row)
        self._refresh_kcal_totals()

    def _update_session_timer_label(self) -> None:
        self.label_session_timer.setText(format_mm_ss(self._session_elapsed_seconds()))

    def _update_session_ui_locked(self) -> None:
        locked = self._session_active
        self.list_workouts.setEnabled(not locked)
        self.button_new.setEnabled(not locked)

    def _update_start_button(self) -> None:
        can_start = self._can_start_workout() and not self._session_active
        self.button_start.setEnabled(can_start)
        self.button_start.setVisible(not self._session_active)
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
        self._item_calories_per_unit: list[float] = []
        self._item_calories_modifier: list[float] = []
        self._filling_items = False
        self._icon_getter: Callable[[str], QIcon | None] | None = None
        self._icon_size = _DEFAULT_TABLE_ICON_SIZE
        self._session_active = False
        self._session_workout_id: int | None = None
        self._session_elapsed = QElapsedTimer()
        self._session_timer = QTimer(self)
        self._session_timer.setInterval(1000)
        self._session_timer.timeout.connect(self._tick_session_timer)
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

### ⚙️ Method `is_workout_session_active`

```python
def is_workout_session_active(self) -> bool
```

Return whether a workout session timer is running.

<details>
<summary>Code:</summary>

```python
def is_workout_session_active(self) -> bool:
        return self._session_active
```

</details>

### ⚙️ Method `notify_workout_progress`

```python
def notify_workout_progress(self) -> None
```

After an item is marked done, finish the session or open the next exercise.

<details>
<summary>Code:</summary>

```python
def notify_workout_progress(self) -> None:
        if not self._session_active or self._session_workout_id != self._current_workout_id:
            return
        if self._all_items_done():
            self.stop_workout_session(completed=True)
            return
        next_item_id = self._first_incomplete_item_id()
        if next_item_id is not None:
            self.workout_session_started.emit(next_item_id)
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

### ⚙️ Method `stop_workout_session`

```python
def stop_workout_session(self, *, completed: bool = False) -> None
```

Stop the workout session timer and restore the normal UI.

<details>
<summary>Code:</summary>

```python
def stop_workout_session(self, *, completed: bool = False) -> None:
        if not self._session_active:
            return
        elapsed_seconds = self._session_elapsed_seconds()
        self._session_active = False
        self._session_workout_id = None
        self._session_timer.stop()
        self._session_bar.hide()
        self._update_start_button()
        self._update_session_ui_locked()
        if completed:
            message_box.information(
                self,
                "Workout complete",
                f"All exercises finished in {format_mm_ss(elapsed_seconds)}.",
            )
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
            self._apply_row_background(row)
```

</details>

## 🔧 Function `estimate_workout_item_kcal`

```python
def estimate_workout_item_kcal(value_text: str, *, calories_per_unit: float, calories_modifier: float) -> float
```

Return estimated kcal for a workout item value.

<details>
<summary>Code:</summary>

```python
def estimate_workout_item_kcal(
    value_text: str,
    *,
    calories_per_unit: float,
    calories_modifier: float,
) -> float:
    try:
        value = float(value_text)
    except (TypeError, ValueError):
        return 0.0
    return value * calories_per_unit * calories_modifier
```

</details>
