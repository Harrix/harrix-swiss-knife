"""Workouts tab: saved plans, generate, and mark sets done."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from PySide6.QtCore import QModelIndex, Qt, Signal
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QListView,
    QMessageBox,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife.apps.common import message_box
from harrix_swiss_knife.qt_emoji_icon import make_emoji_push_button

if TYPE_CHECKING:
    from harrix_swiss_knife.apps.fitness.database_manager import DatabaseManager, WorkoutItemRow, WorkoutRow

logger = logging.getLogger(__name__)

_COL_DONE = 0
_COL_EXERCISE = 1
_COL_TYPE = 2
_COL_VALUE = 3
_COL_UNIT = 4
_COL_KCAL = 5


class WorkoutsWidget(QWidget):
    """Split view: saved workouts on the left, items and Done checkboxes on the right."""

    generate_requested = Signal()
    workouts_changed = Signal()
    item_done_requested = Signal(int)
    exercise_lightbox_requested = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        """Build the workouts UI; call `set_database_manager` before loading data."""
        super().__init__(parent)
        self._db: DatabaseManager | None = None
        self._current_workout_id: int | None = None
        self._item_ids: list[int] = []
        self._build_ui()

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

        self.table_items = QTableWidget(0, 6)
        self.table_items.setHorizontalHeaderLabels(["Done", "Exercise", "Type", "Value", "Unit", "kcal"])
        self.table_items.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_items.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_items.doubleClicked.connect(self._on_item_double_clicked)
        right_layout.addWidget(self.table_items, 1)
        self.label_totals = QLabel("")
        right_layout.addWidget(self.label_totals)
        splitter.addWidget(right)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)

    def _clear_detail(self) -> None:
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
