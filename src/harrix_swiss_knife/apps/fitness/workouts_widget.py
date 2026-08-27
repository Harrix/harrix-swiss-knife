"""Workouts tab: saved plans, generate, and mark sets done."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from PySide6.QtCore import QModelIndex, QPoint, QSize, Qt, Signal
from PySide6.QtGui import QIcon, QKeySequence, QPainter, QShortcut, QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QListView,
    QMenu,
    QMessageBox,
    QSpinBox,
    QSplitter,
    QStyle,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife.apps.common import message_box
from harrix_swiss_knife.apps.common.table_context_menu import LABEL_OPEN_LIGHTBOX, add_delete_action
from harrix_swiss_knife.apps.common.widgets.exercise_list_hover_preview import exercise_at_table_image
from harrix_swiss_knife.apps.fitness.workouts_ai import (
    MAX_WORKOUT_DURATION_MIN,
    MIN_WORKOUT_DURATION_MIN,
    recalculate_workout_duration,
)
from harrix_swiss_knife.qt_emoji_icon import apply_leading_emoji_icons, make_emoji_push_button

if TYPE_CHECKING:
    from collections.abc import Callable

    from PySide6.QtCore import QPersistentModelIndex

    from harrix_swiss_knife.apps.fitness.database_manager import DatabaseManager, WorkoutItemRow, WorkoutRow

logger = logging.getLogger(__name__)

_COL_DONE = 0
_COL_IMAGE = 1
_COL_EXERCISE = 2
_COL_TYPE = 3
_COL_VALUE = 4
_COL_UNIT = 5
_COL_KCAL = 6
_DEFAULT_TABLE_ICON_SIZE = 64
_ITEM_COLUMN_COUNT = 7
_DONE_COLUMN_WIDTH = 56


class WorkoutsWidget(QWidget):
    """Split view: saved workouts on the left, items and Done checkboxes on the right."""

    generate_requested = Signal()
    workouts_changed = Signal()
    item_done_requested = Signal(int)
    exercise_lightbox_requested = Signal(int)
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
        duration_row = QHBoxLayout()
        duration_row.addWidget(QLabel("Duration:"))
        self.spin_duration = QSpinBox()
        self.spin_duration.setRange(MIN_WORKOUT_DURATION_MIN, MAX_WORKOUT_DURATION_MIN)
        self.spin_duration.setSuffix(" min")
        self.spin_duration.setEnabled(False)
        self.spin_duration.editingFinished.connect(self._save_duration)
        duration_row.addWidget(self.spin_duration)
        duration_row.addStretch()
        right_layout.addLayout(duration_row)

        self.table_items = QTableWidget(0, _ITEM_COLUMN_COUNT)
        self.table_items.setObjectName("workoutsItemsTable")
        self.table_items.setHorizontalHeaderLabels(["Done", "", "Exercise", "Type", "Value", "Unit", "kcal"])
        self.table_items.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_items.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_items.verticalHeader().setVisible(False)
        self.table_items.setItemDelegateForColumn(_COL_IMAGE, _WorkoutImageDelegate(self.table_items))
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

    def _clear_detail(self) -> None:
        self.items_reloading.emit()
        self._current_workout_id = None
        self._item_ids = []
        self.label_title.setText("Select a workout")
        self.label_meta.setText("")
        self.spin_duration.blockSignals(True)  # noqa: FBT003
        self.spin_duration.setValue(MIN_WORKOUT_DURATION_MIN)
        self.spin_duration.setEnabled(False)
        self.spin_duration.blockSignals(False)  # noqa: FBT003
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
            self.table_items.setCellWidget(row, _COL_DONE, _make_done_cell(checkbox))
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
        self.label_meta.setText(f"{workout.gender} · {workout.created_date}")
        self.spin_duration.blockSignals(True)  # noqa: FBT003
        self.spin_duration.setEnabled(True)
        self.spin_duration.setValue(workout.duration_min)
        self.spin_duration.blockSignals(False)  # noqa: FBT003
        items = self._db.get_workout_items(workout_id)
        self._fill_items(items)

    def _on_done_toggled(self, *, item_id: int, checked: bool) -> None:
        if not checked:
            return
        self.item_done_requested.emit(item_id)

    def _on_item_double_clicked(self, index: QModelIndex) -> None:
        row = index.row()
        if 0 <= row < len(self._item_ids):
            self.exercise_lightbox_requested.emit(self._item_ids[row])

    def _on_workout_clicked(self, index: QModelIndex) -> None:
        item = self._list_model.itemFromIndex(index)
        if item is None:
            return
        workout_id = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(workout_id, int):
            self._load_workout(workout_id)

    def _refresh_list_duration_label(self) -> None:
        workout_id = self._current_workout_id
        if workout_id is None:
            return
        name = self.label_title.text()
        duration = self.spin_duration.value()
        for row in range(self._list_model.rowCount()):
            item = self._list_model.item(row)
            if item is not None and item.data(Qt.ItemDataRole.UserRole) == workout_id:
                item.setText(f"{name} ({duration} min)")
                return

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
        previous_count = len(self._item_ids)
        previous_duration = self.spin_duration.value()
        for item_id in item_ids:
            if not self._db.delete_workout_item(item_id):
                message_box.warning(self, "Error", "Failed to remove workout row")
                self._load_workout(workout_id)
                return
        remaining_count = previous_count - len(item_ids)
        new_duration = recalculate_workout_duration(
            previous_duration,
            remaining_count=remaining_count,
            previous_count=previous_count,
        )
        if not self._db.update_workout_duration(workout_id, new_duration):
            message_box.warning(self, "Error", "Failed to update workout duration")
        self._load_workout(workout_id)
        self._refresh_list_duration_label()
        self.workouts_changed.emit()

    def _save_duration(self) -> None:
        if self._db is None or self._current_workout_id is None or not self.spin_duration.isEnabled():
            return
        duration = self.spin_duration.value()
        if not self._db.update_workout_duration(self._current_workout_id, duration):
            message_box.warning(self, "Error", "Failed to update workout duration")
            return
        self._refresh_list_duration_label()
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


class _WorkoutImageDelegate(QStyledItemDelegate):
    """Paint exercise thumbnails without the row-selection blue fill."""

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        """Draw the icon on the normal table background even when the row is selected."""
        option = QStyleOptionViewItem(option)
        option.state &= ~QStyle.StateFlag.State_Selected
        option.state &= ~QStyle.StateFlag.State_HasFocus
        super().paint(painter, option, index)


def _make_done_cell(checkbox: QCheckBox) -> QWidget:
    """Wrap a Done checkbox so row selection does not paint blue behind it."""
    cell = QWidget()
    cell.setAutoFillBackground(True)
    layout = QHBoxLayout(cell)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.addWidget(checkbox, alignment=Qt.AlignmentFlag.AlignCenter)
    return cell
