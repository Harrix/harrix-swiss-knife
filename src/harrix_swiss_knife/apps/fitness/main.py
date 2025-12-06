"""Fitness tracker GUI.

This module contains a single `MainWindow` class that provides a Qt-based GUI for a
SQLite database with exercises, exercise types, body weight and daily process
(records of performed exercises).
"""

from __future__ import annotations

import calendar
import colorsys
import contextlib
import io
import math
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from functools import partial
from pathlib import Path
from typing import TYPE_CHECKING

import harrix_pylib as h
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.ticker import MultipleLocator
from PIL import Image
from PySide6.QtCore import QDate, QDateTime, QModelIndex, QPoint, QSize, QSortFilterProxyModel, Qt, QTimer
from PySide6.QtGui import (
    QBrush,
    QCloseEvent,
    QColor,
    QFont,
    QIcon,
    QKeyEvent,
    QMouseEvent,
    QMovie,
    QPainter,
    QPixmap,
    QResizeEvent,
    QStandardItem,
    QStandardItemModel,
    QTextDocument,
)
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QListView,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QMessageBox,
    QRadioButton,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife import resources_rc  # noqa: F401
from harrix_swiss_knife.apps.fitness import database_manager, window
from harrix_swiss_knife.apps.fitness.mixins import (
    AutoSaveOperations,
    ChartOperations,
    DateOperations,
    TableOperations,
    ValidationOperations,
    requires_database,
)

if TYPE_CHECKING:
    from collections.abc import Callable


config = h.dev.load_config("config/config.json")


class ExerciseSelectionDialog(QDialog):
    """Modal dialog for selecting an exercise via AVIF previews."""

    def __init__(
        self,
        parent: QWidget | None,
        *,
        exercises: list[str],
        icon_provider: Callable[[str], QIcon | None],
        preview_size: QSize,
        current_selection: str | None,
    ) -> None:
        """Initialize the ExerciseSelectionDialog.

        Args:

        - `parent` (`QWidget | None`): Parent widget.
        - `exercises` (`list[str]`): List of exercise names to display.
        - `icon_provider` (`Callable[[str], QIcon | None]`): Function that returns an icon for a given exercise name.
        - `preview_size` (`QSize`): Size for icon previews.
        - `current_selection` (`str | None`): Currently selected exercise, if any.

        """
        super().__init__(parent)
        self.setWindowTitle("Select Exercise")
        self.setModal(True)
        self.selected_exercise: str | None = current_selection
        self._icon_provider = icon_provider

        layout = QVBoxLayout(self)

        self.list_widget = QListWidget(self)
        self.list_widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.list_widget.setViewMode(QListWidget.ViewMode.IconMode)
        self.list_widget.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.list_widget.setMovement(QListWidget.Movement.Static)
        self.list_widget.setSpacing(16)
        self.list_widget.setIconSize(preview_size)
        self.list_widget.setWordWrap(True)
        self.list_widget.setUniformItemSizes(False)
        layout.addWidget(self.list_widget)

        for exercise in exercises:
            item = QListWidgetItem(exercise, self.list_widget)
            item.setData(Qt.ItemDataRole.UserRole, exercise)
            item.setTextAlignment(Qt.AlignmentFlag.AlignHCenter)

            icon = self._icon_provider(exercise)
            if icon is not None and not icon.isNull():
                item.setIcon(icon)

            if current_selection and exercise == current_selection:
                self.list_widget.setCurrentItem(item)

        self.list_widget.itemSelectionChanged.connect(self._on_selection_changed)
        self.list_widget.itemDoubleClicked.connect(self._on_item_double_clicked)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, self)
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def _on_accept(self) -> None:
        if self.list_widget.currentItem() is None and self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(0)
        self._on_selection_changed()

        if self.selected_exercise:
            self.accept()
        else:
            self.reject()

    def _on_item_double_clicked(self, item: QListWidgetItem) -> None:
        self.selected_exercise = item.data(Qt.ItemDataRole.UserRole)
        self.accept()

    def _on_selection_changed(self) -> None:
        item = self.list_widget.currentItem()
        self.selected_exercise = item.data(Qt.ItemDataRole.UserRole) if item else None


class MainWindow(
    QMainWindow,
    window.Ui_MainWindow,
    TableOperations,
    ChartOperations,
    DateOperations,
    AutoSaveOperations,
    ValidationOperations,
):
    """Main application window for the fitness tracking application.

    This class implements the main GUI window for the fitness tracker, providing
    functionality to record exercises, weight measurements, and track progress.
    It manages database operations for storing and retrieving fitness data.

    Attributes:

    - `_SAFE_TABLES` (`frozenset[str]`): Set of table names that can be safely modified,
      containing "process", "exercises", "types", and "weight".

    - `db_manager` (`database_manager.DatabaseManager | None`): Database
      connection manager. Defaults to `None` until initialized.

    - `models` (`dict[str, QSortFilterProxyModel | None]`): Dictionary of table models keyed
      by table name. All values default to `None` until tables are loaded.

    - `table_config` (`dict[str, tuple[QTableView, str, list[str]]]`): Configuration for each
      table, mapping table names to tuples of (table view widget, model key, column headers).

    - `exercises_list_model` (`QStandardItemModel | None`): Model for the exercises list view.
      Defaults to `None` until initialized.

    """

    _SAFE_TABLES: frozenset[str] = frozenset(
        {"process", "exercises", "types", "weight"},
    )

    def __init__(self) -> None:  # noqa: D107  (inherited from Qt widgets)
        super().__init__()
        self.setupUi(self)
        self._setup_ui()

        # Set window icon
        self.setWindowIcon(QIcon(":/assets/logo.svg"))

        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        # Initialize core attributes
        self.db_manager: database_manager.DatabaseManager | None = None
        self.current_movie: QMovie | None = None

        # AVIF animation attributes for multiple labels
        self.avif_data = {
            "main": {"frames": [], "current_frame": 0, "timer": None, "exercise": None},
            "exercises": {"frames": [], "current_frame": 0, "timer": None, "exercise": None},
            "types": {"frames": [], "current_frame": 0, "timer": None, "exercise": None},
            "charts": {"frames": [], "current_frame": 0, "timer": None, "exercise": None},
            "statistics": {"frames": [], "current_frame": 0, "timer": None, "exercise": None},
        }

        # Exercise list model
        self.exercises_list_model: QStandardItemModel | None = None

        # Cache of exercise icons keyed by exercise name
        self._exercise_icon_cache: dict[str, tuple[float, QIcon | None]] = {}

        # Table models dictionary
        self.models: dict[str, QSortFilterProxyModel | None] = {
            "process": None,
            "exercises": None,
            "types": None,
            "weight": None,
            "statistics": None,
        }

        # Process table display mode flag
        self.count_records_to_show = 5000
        self.show_all_records = False
        self.icon_size = 64

        # Store default UI metrics for responsive adjustments
        self._default_label_exercise_avif_min_height = self.label_exercise_avif.minimumHeight()
        self._default_label_exercise_avif_max_height = self.label_exercise_avif.maximumHeight()
        inferred_height = max(self.label_exercise_avif.height(), self.label_exercise_avif.sizeHint().height(), 1)
        self._default_label_exercise_avif_height = inferred_height

        base_font = self.label_count_sets_today.font()
        self._default_count_sets_font = QFont(base_font)
        self._small_count_sets_font = QFont(base_font)
        if base_font.pointSizeF() > 0:
            reduced_point_size = max(base_font.pointSizeF() * 0.4, 1.0)
            self._small_count_sets_font.setPointSizeF(reduced_point_size)
        elif base_font.pixelSize() > 0:
            reduced_pixel_size = max(int(base_font.pixelSize() * 0.4), 1)
            self._small_count_sets_font.setPixelSize(reduced_pixel_size)
        self._is_small_window_layout: bool | None = None

        # Chart configuration
        self.max_count_points_in_charts = 40
        self.id_steps = 39  # ID for steps exercise

        # Statistics table mode tracking
        self.current_statistics_mode = None  # 'records', 'last_exercises', 'check_steps'

        # Flag to prevent recursive selection changes between list views
        self._syncing_selection = False

        # Table configuration mapping
        self.table_config: dict[str, tuple[QTableView, str, list[str]]] = {
            "process": (
                self.tableView_process,
                "process",
                ["Exercise", "Exercise Type", "Quantity", "Date"],
            ),
            "exercises": (
                self.tableView_exercises,
                "exercises",
                ["Exercise", "Unit of Measurement", "Type Required", "Calories per Unit"],
            ),
            "types": (
                self.tableView_exercise_types,
                "types",
                ["Exercise", "Exercise Type", "Calories Modifier"],
            ),
            "weight": (self.tableView_weight, "weight", ["Weight", "Date"]),
            "statistics": (self.tableView_statistics, "statistics", ["Exercise", "Type", "Value", "Unit", "Date"]),
        }

        # Define colors for different exercises (expanded palette)
        self.exercise_colors = self.generate_pastel_colors_mathematical(50)

        # For charts
        self._chart_update_timer = QTimer(self)
        self._chart_update_timer.setSingleShot(True)
        self._chart_update_timer.timeout.connect(self._update_chart_based_on_radio_button)

        # Initialize application
        self._init_database()
        self._connect_signals()
        self._init_filter_controls()
        self._init_weight_chart_controls()
        self._init_weight_controls()
        self._init_exercise_chart_controls()
        self._init_exercises_list()
        self._init_sets_count_display()
        self.update_all()

        # Load initial AVIF animations after UI is ready
        QTimer.singleShot(100, self._load_initial_avifs)

        # Set window size and position based on screen resolution
        self._setup_window_size_and_position()

        # Adjust table column widths and show window after UI is fully initialized
        QTimer.singleShot(200, self._finish_window_initialization)

    @requires_database()
    def apply_filter(self) -> None:
        """Apply combo-box/date filters to the process table."""
        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        exercise = self.comboBox_filter_exercise.currentText()
        exercise_type = self.comboBox_filter_type.currentText()
        use_date_filter = self.checkBox_use_date_filter.isChecked()
        date_from = self.dateEdit_filter_from.date().toString("yyyy-MM-dd") if use_date_filter else None
        date_to = self.dateEdit_filter_to.date().toString("yyyy-MM-dd") if use_date_filter else None

        # Use database manager method
        rows = self.db_manager.get_filtered_process_records(
            exercise_name=exercise if exercise else None,
            exercise_type=exercise_type if exercise_type else None,
            date_from=date_from,
            date_to=date_to,
        )

        # Get unique dates and assign colors
        unique_dates = list({row[5] for row in rows if row[5]})  # row[5] is date
        date_to_color = {}

        for idx, date_str in enumerate(sorted(unique_dates, reverse=True)):
            color_index = idx % len(self.exercise_colors)
            date_to_color[date_str] = self.exercise_colors[color_index]

        # Transform data with colors
        transformed_data = []
        for row in rows:
            date_str = row[5]
            date_color = date_to_color.get(date_str, QColor(255, 255, 255))

            transformed_row = [row[1], row[2], f"{row[3]} {row[4] or 'times'}", row[5], row[0], date_color]
            transformed_data.append(transformed_row)

        self.models["process"] = self._create_colored_process_table_model(
            transformed_data, self.table_config["process"][2]
        )
        self.tableView_process.setModel(self.models["process"])

        # Configure header with interactive mode for all columns
        header = self.tableView_process.horizontalHeader()
        # Set all columns to interactive (resizable)
        for i in range(header.count()):
            header.setSectionResizeMode(i, header.ResizeMode.Interactive)
        # Set proportional column widths for all columns
        self._adjust_process_table_columns()

    def clear_filter(self) -> None:
        """Reset all process-table filters.

        Clears all filter selections and resets date ranges to default values:

        - Clears exercise and type selections
        - Disables date filtering
        - Resets date range to the last month
        - Refreshes the table view
        """
        self.comboBox_filter_exercise.setCurrentIndex(0)
        self.comboBox_filter_type.setCurrentIndex(0)
        self.checkBox_use_date_filter.setChecked(False)

        current_date = QDateTime.currentDateTime().date()
        self.dateEdit_filter_from.setDate(current_date.addMonths(-1))
        self.dateEdit_filter_to.setDate(current_date)

        self.show_tables()

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        """Handle application close event.

        Args:

        - `event` (`QCloseEvent`): The close event.

        """
        # Stop animations for all labels
        if self.current_movie:
            self.current_movie.stop()

        for label_key in self.avif_data:
            if self.avif_data[label_key]["timer"]:
                self.avif_data[label_key]["timer"].stop()

        # Dispose Models
        self._dispose_models()

        # Close DB
        if self.db_manager:
            self.db_manager.close()
            self.db_manager = None

        super().closeEvent(event)

    @requires_database()
    def delete_record(self, table_name: str) -> None:
        """Delete selected row from table using database manager methods.

        Args:

        - `table_name` (`str`): Name of the table to delete from. Must be in _SAFE_TABLES.

        Raises:

        - `ValueError`: If table_name is not in _SAFE_TABLES.

        """
        if table_name not in self._SAFE_TABLES:
            error_message = f"Illegal table name: {table_name}"
            raise ValueError(error_message)

        record_id = self._get_selected_row_id(table_name)
        if record_id is None:
            QMessageBox.warning(self, "Error", "Select a record to delete")
            return

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        # Use appropriate database manager method
        success = False
        try:
            if table_name == "process":
                success = self.db_manager.delete_process_record(record_id)
            elif table_name == "exercises":
                success = self.db_manager.delete_exercise(record_id)
                if success:
                    self._mark_exercises_changed()
            elif table_name == "types":
                success = self.db_manager.delete_exercise_type(record_id)
                if success:
                    self._mark_exercises_changed()
            elif table_name == "weight":
                success = self.db_manager.delete_weight_record(record_id)
        except Exception as e:
            QMessageBox.warning(self, "Database Error", f"Failed to delete record: {e}")
            return

        if success:
            self.update_all()
            self.update_sets_count_today()
        else:
            QMessageBox.warning(self, "Error", f"Deletion failed in {table_name}")

    def generate_pastel_colors_mathematical(self, count: int = 100) -> list[QColor]:
        """Generate pastel colors using mathematical distribution.

        Args:

        - `count` (`int`): Number of colors to generate. Defaults to `100`.

        Returns:

        - `list[QColor]`: List of pastel QColor objects.

        """
        colors = []

        for i in range(count):
            # Use golden ratio for even hue distribution
            hue = (i * 0.618033988749895) % 1.0  # Golden ratio

            # Lower saturation and higher lightness for very light pastel effect
            saturation = 0.6  # Very low saturation
            lightness = 0.95  # Very high lightness

            # Convert HSL to RGB
            r, g, b = colorsys.hls_to_rgb(hue, lightness, saturation)

            # Convert to 0-255 range and create QColor
            color = QColor(int(r * 255), int(g * 255), int(b * 255))
            colors.append(color)

        return colors

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        """Handle key press events for the main window.

        Args:

        - `event` (`QKeyEvent`): The key press event.

        """
        # Handle Enter key when pushButton_add is focused
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            focused_widget = QApplication.focusWidget()
            if focused_widget == self.pushButton_add:
                self.pushButton_add.click()
                return

        # Handle Ctrl+C for copying table selections
        if event.key() == Qt.Key.Key_C and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            # Determine which table is currently focused
            focused_widget = QApplication.focusWidget()

            # Check if the focused widget is one of our table views
            table_views = [
                self.tableView_process,
                self.tableView_exercises,
                self.tableView_exercise_types,
                self.tableView_weight,
                self.tableView_statistics,
            ]

            for table_view in table_views:
                if focused_widget == table_view:
                    self._copy_table_selection_to_clipboard(table_view)
                    return

            # If focused widget is a child of a table view (like the viewport)
            for table_view in table_views:
                if focused_widget and table_view.isAncestorOf(focused_widget):
                    self._copy_table_selection_to_clipboard(table_view)
                    return

        # Call parent implementation for other key events
        super().keyPressEvent(event)

    @requires_database()
    def load_process_table(self) -> None:
        """Load process table data with appropriate limit based on show_all_records flag."""

        def transform_process_data(rows: list[list]) -> list[list]:
            """Refresh process table with data transformation and coloring.

            Args:

            - `rows` (`list[list]`): Raw process data from database.

            Returns:

            - `list[list]`: Transformed process data.

            """
            # Get all unique dates and assign colors
            unique_dates = list({row[5] for row in rows if row[5]})  # row[5] is date
            date_to_color = {}

            for idx, date_str in enumerate(sorted(unique_dates, reverse=True)):
                color_index = idx % len(self.exercise_colors)
                date_to_color[date_str] = self.exercise_colors[color_index]

            # Transform data and add color information
            transformed_rows = []
            for row in rows:
                # Original transformation:
                # [id, exercise, type, value, unit, date] -> [exercise, type, "value unit", date]
                transformed_row = [row[1], row[2], f"{row[3]} {row[4] or 'times'}", row[5]]

                # Add color information based on date
                date_str = row[5]
                date_color = date_to_color.get(date_str, QColor(255, 255, 255))  # White as fallback

                # Add original ID and color to the row for later use
                transformed_row.extend([row[0], date_color])  # [exercise, type, "value unit", date, id, color]
                transformed_rows.append(transformed_row)

            return transformed_rows

        # Get process data based on current mode
        if self.show_all_records:
            process_rows = self.db_manager.get_all_process_records()
        else:
            process_rows = self.db_manager.get_limited_process_records(self.count_records_to_show)

        transformed_process_data = transform_process_data(process_rows)

        # Create process table model with coloring
        self.models["process"] = self._create_colored_process_table_model(
            transformed_process_data, self.table_config["process"][2]
        )
        self.tableView_process.setModel(self.models["process"])

        # Configure process table header - interactive mode for all columns
        process_header = self.tableView_process.horizontalHeader()
        # Set all columns to interactive (resizable)
        for i in range(process_header.count()):
            process_header.setSectionResizeMode(i, process_header.ResizeMode.Interactive)
        # Set proportional column widths for all columns
        self._adjust_process_table_columns()

    @requires_database()
    def on_add_exercise(self) -> None:
        """Insert a new exercise using database manager."""
        exercise = self.lineEdit_exercise_name.text().strip()
        unit = self.lineEdit_exercise_unit.text().strip()
        calories_per_unit = self.doubleSpinBox_calories_per_unit.value()

        if not exercise:
            QMessageBox.warning(self, "Error", "Enter exercise name")
            return

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        # Get checkbox value
        is_type_required = self.check_box_is_type_required.isChecked()

        try:
            if self.db_manager.add_exercise(
                exercise, unit, is_type_required=is_type_required, calories_per_unit=calories_per_unit
            ):
                self._mark_exercises_changed()
                self.update_all()
            else:
                QMessageBox.warning(self, "Error", "Failed to add exercise")
        except Exception as e:
            QMessageBox.warning(self, "Database Error", f"Failed to add exercise: {e}")

    @requires_database()
    def on_add_record(self) -> None:
        """Insert a new process record using database manager."""
        exercise = self._get_current_selected_exercise()
        if not exercise:
            QMessageBox.warning(self, "Error", "Please select an exercise")
            return

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            ex_id = self.db_manager.get_id("exercises", "name", exercise)
            if ex_id is None:
                QMessageBox.warning(self, "Error", f"Exercise '{exercise}' not found in database")
                return

            type_name = self.comboBox_type.currentText()

            # Check if exercise type is required
            if self.db_manager.is_exercise_type_required(ex_id) and not type_name.strip():
                QMessageBox.warning(self, "Error", f"Exercise type is required for '{exercise}'. Please select a type.")
                return

            type_id = (
                self.db_manager.get_id("types", "type", type_name, condition=f"_id_exercises = {ex_id}")
                if type_name
                else -1
            )

            # Store current date before adding record
            value = str(self.spinBox_count.value())
            date_str = self.dateEdit.date().toString("yyyy-MM-dd")

            # Get current value as float for record checking
            current_value = float(value)

            # Check for records before adding the new record
            record_info = self._check_for_new_records(
                ex_id, type_id if type_id is not None else -1, current_value, type_name
            )

            # Use database manager method
            if self.db_manager.add_process_record(ex_id, type_id or -1, value, date_str):
                # Show congratulations if new record was set
                if record_info:
                    self._show_record_congratulations(exercise, record_info)

                # Apply date increment logic
                self._increment_date_widget(self.dateEdit)

                # Update UI without resetting the date
                self.show_tables()
                self._update_comboboxes(selected_exercise=exercise, selected_type=type_name)
                self.update_filter_comboboxes()
                self.update_sets_count_today()

                # Update the exercise info to reflect today's new total
                self.on_exercise_selection_changed_list()
            else:
                QMessageBox.warning(self, "Error", "Failed to add process record")

        except Exception as e:
            QMessageBox.warning(self, "Database Error", f"Failed to add record: {e}")

    @requires_database()
    def on_add_type(self) -> None:
        """Insert a new exercise type using database manager."""
        exercise = self.comboBox_exercise_name.currentText()
        if not exercise:
            QMessageBox.warning(self, "Error", "Select an exercise")
            return

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            ex_id = self.db_manager.get_id("exercises", "name", exercise)
            if ex_id is None:
                QMessageBox.warning(self, "Error", f"Exercise '{exercise}' not found")
                return

            type_name = self.lineEdit_exercise_type.text().strip()
            if not type_name:
                QMessageBox.warning(self, "Error", "Enter type name")
                return

            calories_modifier = self.doubleSpinBox_calories_modifier.value()

            if self.db_manager.add_exercise_type(ex_id, type_name, calories_modifier):
                self._mark_exercises_changed()
                self.update_all()
            else:
                QMessageBox.warning(self, "Error", "Failed to add exercise type")

        except Exception as e:
            QMessageBox.warning(self, "Database Error", f"Failed to add type: {e}")

    @requires_database()
    def on_add_weight(self) -> None:
        """Insert a new weight measurement using database manager."""
        weight_value = self.doubleSpinBox_weight.value()
        weight_date = self.dateEdit_weight.date().toString("yyyy-MM-dd")

        # Validate the date
        if not self._is_valid_date(weight_date):
            QMessageBox.warning(self, "Error", "Invalid date format")
            return

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            # Use database manager method
            if self.db_manager.add_weight_record(weight_value, weight_date):
                # Apply date increment logic
                self._increment_date_widget(self.dateEdit_weight)

                # Update UI without resetting the weight value
                self.show_tables()

                # Update weight chart if we're on the weight tab
                current_tab_index = self.tabWidget.currentIndex()
                weight_tab_index = 2
                if current_tab_index == weight_tab_index:
                    self.update_weight_chart()
            else:
                QMessageBox.warning(self, "Error", "Failed to add weight record")

        except Exception as e:
            QMessageBox.warning(self, "Database Error", f"Failed to add weight: {e}")

    @requires_database()
    def on_chart_exercise_changed(
        self, current: QModelIndex | None = None, previous: QModelIndex | None = None
    ) -> None:
        """Handle chart exercise list view selection change.

        Args:

        - `current` (`QModelIndex | None`): Currently selected index. Defaults to invalid index.
        - `previous` (`QModelIndex | None`): Previously selected index. Defaults to invalid index.

        """
        if current is None:
            current = QModelIndex()
        if previous is None:
            previous = QModelIndex()
        self._update_charts_avif()
        exercise_name = self._get_selected_chart_exercise()
        if exercise_name:
            self._sync_exercise_selection(exercise_name, source="chart")

    @requires_database()
    def on_chart_type_changed(self, current: QModelIndex | None = None, previous: QModelIndex | None = None) -> None:
        """Handle chart type list view selection change.

        Args:

        - `current` (`QModelIndex | None`): Currently selected index. Defaults to invalid index.
        - `previous` (`QModelIndex | None`): Previously selected index. Defaults to invalid index.

        """
        if current is None:
            current = QModelIndex()
        if previous is None:
            previous = QModelIndex()
        self._schedule_chart_update(50)

    @requires_database()
    def on_check_steps(self) -> None:
        """Check for missing days and duplicate days in steps records."""
        # Set current mode to check_steps
        self.current_statistics_mode = "check_steps"

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            # Clear any existing spans from previous statistics view
            self.tableView_statistics.clearSpans()

            # Get steps exercise ID
            steps_exercise_id = self.id_steps

            # Check if steps exercise exists using database manager
            if not self.db_manager.check_exercise_exists(steps_exercise_id):
                QMessageBox.warning(
                    self, "Steps Exercise Not Found", f"Exercise with ID {steps_exercise_id} not found in database."
                )
                return

            steps_exercise_name = self.db_manager.get_exercise_name_by_id(steps_exercise_id)
            if not steps_exercise_name:
                return

            # Get steps records using database manager
            steps_records = self.db_manager.get_exercise_steps_records(steps_exercise_id)

            if not steps_records:
                # Show empty table with message
                empty_data = [
                    ["No Data", "", f"No records found for exercise: {steps_exercise_name}", 0, QColor(255, 255, 255)]
                ]

                self.models["statistics"] = self._create_colored_table_model(
                    empty_data, ["Issue Type", "Date", "Details"]
                )
                self.tableView_statistics.setModel(self.models["statistics"])

                # Update statistics AVIF
                self._update_statistics_avif()
                return

            # Get date range: from first record to yesterday
            first_date_str = steps_records[0][0]
            yesterday = datetime.now(timezone.utc).astimezone().date() - timedelta(days=1)

            try:
                first_date = datetime.fromisoformat(first_date_str).date()
            except ValueError:
                QMessageBox.warning(
                    self, "Invalid Date Format", f"Invalid date format in first record: {first_date_str}"
                )
                return

            # Create a set of dates that have records
            recorded_dates = {record[0] for record in steps_records}

            # Find missing days
            missing_days = []
            current_date = first_date

            while current_date <= yesterday:
                date_str = current_date.strftime("%Y-%m-%d")
                if date_str not in recorded_dates:
                    missing_days.append(date_str)
                current_date = current_date + timedelta(days=1)

            # Find duplicate days (days with multiple records)
            duplicate_days = []
            for date_str, count, step_values in steps_records:
                if count > 1:
                    duplicate_days.append((date_str, count, step_values))

            # Prepare table data
            table_data = []

            # Add missing days
            for missing_date in missing_days:
                try:
                    date_obj = datetime.fromisoformat(missing_date).date()
                    formatted_date = date_obj.strftime("%Y-%m-%d (%b %d)")

                    # Calculate days ago
                    days_ago = (yesterday - date_obj).days
                    details = f"Missing record ({days_ago} days ago)"

                    table_data.append(
                        [
                            "Missing Day",
                            formatted_date,
                            details,
                            0,  # Dummy ID
                            QColor(255, 182, 193),  # Light pink for missing days
                        ]
                    )
                except ValueError:
                    continue

            # Add duplicate days
            for date_str, count, step_values in duplicate_days:
                try:
                    date_obj = datetime.fromisoformat(date_str).date()
                    formatted_date = date_obj.strftime("%Y-%m-%d (%b %d)")

                    # Calculate days ago
                    days_ago = (yesterday - date_obj).days
                    details = f"{count} records: {step_values} ({days_ago} days ago)"

                    table_data.append(
                        [
                            "Duplicate Day",
                            formatted_date,
                            details,
                            0,  # Dummy ID
                            QColor(255, 255, 182),  # Light yellow for duplicate days
                        ]
                    )
                except ValueError:
                    continue

            # Sort by date (most recent issues first)
            table_data.sort(key=lambda x: x[1], reverse=True)

            if not table_data:
                # No issues found
                table_data = [
                    [
                        "✅ All Good",
                        "",
                        f"No missing or duplicate days found for {steps_exercise_name}",
                        0,  # Dummy ID
                        QColor(144, 238, 144),  # Light green
                    ]
                ]

            # Create model using the standard method
            self.models["statistics"] = self._create_colored_table_model(table_data, ["Issue Type", "Date", "Details"])
            self.tableView_statistics.setModel(self.models["statistics"])

            # Connect selection signal for statistics table
            self._connect_table_signals_for_table("statistics", self.on_statistics_selection_changed)

            # Configure header with mixed approach: interactive + stretch last
            header = self.tableView_statistics.horizontalHeader()
            # Set first columns to interactive (resizable)
            for i in range(header.count() - 1):
                header.setSectionResizeMode(i, header.ResizeMode.Interactive)
            # Set last column to stretch to fill remaining space
            header.setSectionResizeMode(header.count() - 1, header.ResizeMode.Stretch)
            # Set default column widths for resizable columns
            for i in range(header.count() - 1):
                self.tableView_statistics.setColumnWidth(i, 150)

            # Disable alternating row colors since we have custom colors
            self.tableView_statistics.setAlternatingRowColors(False)

            # Update statistics AVIF
            self._update_statistics_avif()

        except Exception as e:
            QMessageBox.warning(self, "Steps Check Error", f"Failed to check steps: {e}")

    @requires_database()
    def on_compare_last_months(self) -> None:
        """Show comparison chart of exercise progress over the last few months.

        Creates a chart showing cumulative exercise values for the selected exercise
        over the last N months (where N is determined by spinBox_compare_last).
        The current month is highlighted in red, while previous months are shown
        in different shades of blue.
        """
        exercise = self._get_selected_chart_exercise()
        exercise_type = self._get_selected_chart_type()
        months_count = self.spinBox_compare_last.value()

        if not exercise:
            # Clear chart before showing message
            self._clear_layout(self.verticalLayout_charts_content)
            self._show_no_data_label(self.verticalLayout_charts_content, "Please select an exercise")
            return

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        # Get exercise unit for Y-axis label
        exercise_unit = self.db_manager.get_exercise_unit(exercise)

        # Use local time for current date
        today = datetime.now(timezone.utc).astimezone()

        monthly_data = []
        colors = []
        labels = []

        # Color palette for non-current months
        color_palette = [
            "blue",
            "green",
            "orange",
            "purple",
            "brown",
            "pink",
            "gray",
            "olive",
            "cyan",
            "magenta",
            "teal",
            "navy",
            "maroon",
            "lime",
            "indigo",
            "coral",
        ]

        for i in range(months_count):
            # Compute approximate month start/end
            # Note: month stepping is approximate (30 days), kept to match original logic
            # Calculate month i months ago
            month_date = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            for _ in range(i):
                if month_date.month == 1:
                    month_date = month_date.replace(year=month_date.year - 1, month=12)
                else:
                    month_date = month_date.replace(month=month_date.month - 1)
            month_start = month_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if i == 0:
                month_end = today
            else:
                last_day = calendar.monthrange(month_start.year, month_start.month)[1]
                month_end = month_start.replace(day=last_day, hour=23, minute=59, second=59, microsecond=999999)

            # Format for DB
            date_from = month_start.strftime("%Y-%m-%d")
            date_to = month_end.strftime("%Y-%m-%d")

            # Query data
            rows = self.db_manager.get_exercise_chart_data(
                exercise_name=exercise,
                exercise_type=exercise_type if exercise_type != "All types" else None,
                date_from=date_from,
                date_to=date_to,
            )

            # Build cumulative data for this month
            cumulative_data = []
            if rows:
                cumulative_value = 0.0
                for date_str, value_str in rows:
                    try:
                        date_obj = datetime.fromisoformat(date_str).replace(tzinfo=timezone.utc)
                        value = float(value_str)
                        cumulative_value += value
                        # Use day of month for X axis
                        day_of_month = date_obj.day
                        cumulative_data.append((day_of_month, cumulative_value))
                    except (ValueError, TypeError):
                        continue

                # Extend horizontally to the end-of-visualization day (cosmetic)
                if cumulative_data:
                    last_day = cumulative_data[-1][0]
                    last_value = cumulative_data[-1][1]
                    max_day = min(today.day, 31) if i == 0 else 31
                    if last_day < max_day:
                        cumulative_data.append((max_day, last_value))

            # IMPORTANT: append month entry even if it is empty
            monthly_data.append(cumulative_data)

            # Build label/color for every month regardless of data presence
            if i == 0:
                colors.append("red")
                labels.append(f"{month_start.strftime('%B %Y')} (Current)")
            else:
                color_index = (i - 1) % len(color_palette)
                colors.append(color_palette[color_index])
                labels.append(f"{month_start.strftime('%B %Y')}")

        # In on_compare_last_months, right before the early return where 'all months are empty'
        if all(len(d) == 0 for d in monthly_data):
            self._clear_layout(self.verticalLayout_charts_content)
            self._show_no_data_label(self.verticalLayout_charts_content, "No data found for the selected period")
            # Explicitly say last N months:
            months_count = self.spinBox_compare_last.value()
            self._set_no_data_info_label(f"No data for the last {months_count} months.")
            return

        # Clear existing chart
        self._clear_layout(self.verticalLayout_charts_content)

        # Create matplotlib figure
        fig = Figure(figsize=(12, 6), dpi=100)
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)

        # Plot non-current months first
        current_month_data = None
        current_month_color = None
        current_month_label = None

        for i, (data, color, label) in enumerate(zip(monthly_data, colors, labels, strict=False)):
            if not data:
                continue

            x_values = [item[0] for item in data]
            y_values = [item[1] for item in data]

            if i == 0:
                # Defer current month (draw on top)
                current_month_data = (x_values, y_values)
                current_month_color = color
                current_month_label = label
                continue

            # Plot non-current months
            line_style = "--"
            line_width = 2
            max_points = 10

            ax.plot(
                x_values,
                y_values,
                color=color,
                linestyle=line_style,
                linewidth=line_width,
                alpha=0.8,
                label=label,
                marker="o" if len(x_values) <= max_points else None,
                markersize=4,
            )

            # Annotate last point
            if x_values and y_values:
                last_x = x_values[-1]
                last_y = y_values[-1]
                month_year = label.replace(" (Current)", "")
                value_str = f"{last_y:.1f}".rstrip("0").rstrip(".")
                label_text = f"{month_year}: {value_str}"

                ax.annotate(
                    label_text,
                    (last_x, last_y),
                    textcoords="offset points",
                    xytext=(0, 10),
                    ha="center",
                    fontsize=9,
                    alpha=0.8,
                    bbox={"boxstyle": "round,pad=0.2", "facecolor": "white", "edgecolor": "none", "alpha": 0.7},
                )

        # Plot current month last to appear on top
        if current_month_data:
            x_values, y_values = current_month_data
            line_style = "-"
            line_width = 3
            max_points = 10

            ax.plot(
                x_values,
                y_values,
                color=current_month_color,
                linestyle=line_style,
                linewidth=line_width,
                alpha=0.8,
                label=current_month_label,
                marker="o" if len(x_values) <= max_points else None,
                markersize=4,
            )

            # Annotate last point for current month
            if x_values and y_values:
                last_x = x_values[-1]
                last_y = y_values[-1]
                month_year = current_month_label.replace(" (Current)", "")
                value_str = f"{last_y:.1f}".rstrip("0").rstrip(".")
                label_text = f"{month_year}: {value_str}"

                ax.annotate(
                    label_text,
                    (last_x, last_y),
                    textcoords="offset points",
                    xytext=(0, 10),
                    ha="center",
                    fontsize=9,
                    alpha=0.8,
                    bbox={"boxstyle": "round,pad=0.2", "facecolor": "white", "edgecolor": "none", "alpha": 0.7},
                )

        # Customize plot
        ax.set_xlabel("Day of Month", fontsize=12)
        y_label = f"Cumulative Value ({exercise_unit})" if exercise_unit else "Cumulative Value"
        ax.set_ylabel(y_label, fontsize=12)

        chart_title = f"{exercise}"
        if exercise_type and exercise_type != "All types":
            chart_title += f" - {exercise_type}"
        chart_title += f" (Last {months_count} months comparison)"
        ax.set_title(chart_title, fontsize=14, fontweight="bold")

        ax.grid(visible=True, alpha=0.3)
        ax.legend(loc="upper left", fontsize=10)

        # X axis range and ticks
        ax.set_xlim(1, 31)
        ax.set_xticks(range(1, 32, 2))

        fig.tight_layout()
        self.verticalLayout_charts_content.addWidget(canvas)
        canvas.draw()

        # Add recommendations based on prepared monthly_data
        self._add_exercise_recommendations_to_label(exercise, exercise_type, monthly_data, months_count, exercise_unit)

    @requires_database()
    def on_compare_same_months(self) -> None:
        """Show comparison chart of exercise progress for the same month across different years.

        Creates a chart showing cumulative exercise values for the selected exercise
        for the same month across different years. The current year is highlighted in red,
        while previous years are shown in different colors.
        """
        exercise = self._get_selected_chart_exercise()
        exercise_type = self._get_selected_chart_type()
        years_count = self.spinBox_compare_last.value()

        if not exercise:
            # Clear existing chart before showing no data message
            self._clear_layout(self.verticalLayout_charts_content)
            self._show_no_data_label(self.verticalLayout_charts_content, "Please select an exercise")
            return

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        # Get exercise unit for Y-axis label
        exercise_unit = self.db_manager.get_exercise_unit(exercise)

        # Get selected month and current year
        selected_month_index = self.comboBox_compare_same_months.currentIndex()
        selected_month_index = max(selected_month_index, 0)  # Default to January if nothing selected

        today = datetime.now(timezone.utc).astimezone()
        selected_month = selected_month_index + 1  # Convert 0-11 to 1-12
        current_year = today.year

        # Get data for each year
        yearly_data = []
        colors = []
        labels = []

        # Define a color palette for different years (excluding red for current year)
        color_palette = [
            "blue",
            "green",
            "orange",
            "purple",
            "brown",
            "pink",
            "gray",
            "olive",
            "cyan",
            "magenta",
            "teal",
            "navy",
            "maroon",
            "lime",
            "indigo",
            "coral",
        ]

        for _i in range(years_count):
            # Calculate year
            year = current_year - _i

            # Calculate start and end of the same month for this year
            month_start = datetime(year, selected_month, 1, tzinfo=timezone.utc)
            last_day = calendar.monthrange(month_start.year, month_start.month)[1]
            month_end = month_start.replace(day=last_day, hour=23, minute=59, second=59, microsecond=999999)

            # For current year, limit to today only if we're in the selected month or past it
            if year == current_year:
                # Check if the selected month has already started this year
                if today.month >= selected_month:
                    # If we're in the selected month, limit to today
                    if today.month == selected_month:
                        month_end = today
                else:
                    # If the selected month hasn't started yet this year, skip this year
                    continue

            # Format dates for database query
            date_from = month_start.strftime("%Y-%m-%d")
            date_to = month_end.strftime("%Y-%m-%d")

            # Get exercise data for this month
            rows = self.db_manager.get_exercise_chart_data(
                exercise_name=exercise,
                exercise_type=exercise_type if exercise_type != "All types" else None,
                date_from=date_from,
                date_to=date_to,
            )

            if rows:
                # Convert to datetime objects and calculate cumulative values
                cumulative_data = []
                cumulative_value = 0.0

                for date_str, value_str in rows:
                    try:
                        date_obj = datetime.fromisoformat(date_str).replace(tzinfo=timezone.utc)
                        value = float(value_str)
                        cumulative_value += value

                        # Calculate day of month (1-31) for x-axis
                        day_of_month = date_obj.day
                        cumulative_data.append((day_of_month, cumulative_value))
                    except (ValueError, TypeError):
                        continue

                if cumulative_data:
                    # Extend the line horizontally to the end of the month if needed
                    last_day = cumulative_data[-1][0] if cumulative_data else 1
                    last_value = cumulative_data[-1][1] if cumulative_data else 0.0

                    # For current year, extend to today or end of month, whichever is earlier
                    max_day = min(today.day, 31) if year == current_year else 31

                    # Add horizontal extension if needed
                    if last_day < max_day:
                        cumulative_data.append((max_day, last_value))

                    yearly_data.append(cumulative_data)

                    # Determine color based on whether it's current year or not
                    # Note: i represents the year offset, but we need to check if this year actually has data
                    if year == current_year:  # Current year
                        colors.append("red")  # Current year in red
                        labels.append(f"{month_start.strftime('%B %Y')} (Current)")
                    else:
                        # Use different colors from palette for other years
                        color_index = (len(yearly_data) - 2) % len(color_palette)  # -2 because current year uses red
                        colors.append(color_palette[color_index])
                        labels.append(f"{month_start.strftime('%B %Y')}")

        # In on_compare_same_months, right before early return on 'not yearly_data'
        if not yearly_data:
            self._clear_layout(self.verticalLayout_charts_content)
            self._show_no_data_label(self.verticalLayout_charts_content, "No data found for the selected period")
            years_count = self.spinBox_compare_last.value()
            # Tailored message for 'same months' mode:
            selected_month_name = self.comboBox_compare_same_months.currentText()
            self._set_no_data_info_label(f"No data for {selected_month_name.lower()} in the last {years_count} years.")
            return

        # Clear existing chart
        self._clear_layout(self.verticalLayout_charts_content)

        # Create matplotlib figure
        fig = Figure(figsize=(12, 6), dpi=100)
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)

        # Plot each year's data
        # First, plot all non-current years (to ensure current year appears on top)
        current_year_data = None
        current_year_color = None
        current_year_label = None

        for _i, (data, color, label) in enumerate(zip(yearly_data, colors, labels, strict=False)):
            if data:
                x_values = [item[0] for item in data]
                y_values = [item[1] for item in data]

                # Check if this is the current year by looking at the label
                is_current_year = "(Current)" in label

                if is_current_year:
                    # Store current year data to plot last
                    current_year_data = (x_values, y_values)
                    current_year_color = color
                    current_year_label = label
                    continue

                # Plot non-current years first
                line_style = "--"  # Dashed for non-current years
                line_width = 2
                max_points = 10

                ax.plot(
                    x_values,
                    y_values,
                    color=color,
                    linestyle=line_style,
                    linewidth=line_width,
                    alpha=0.8,
                    label=label,
                    marker="o" if len(x_values) <= max_points else None,  # Markers only for few points
                    markersize=4,
                )

                # Add value labels for the last point of each line
                if x_values and y_values:
                    last_x = x_values[-1]
                    last_y = y_values[-1]

                    # Format label with month and year and final value
                    month_year = label.replace(" (Current)", "")  # Remove "(Current)" suffix
                    # Format number without .0 for whole numbers
                    value_str = f"{last_y:.1f}".rstrip("0").rstrip(".")
                    label_text = f"{month_year}: {value_str}"

                    ax.annotate(
                        label_text,
                        (last_x, last_y),
                        textcoords="offset points",
                        xytext=(0, 10),
                        ha="center",
                        fontsize=9,
                        alpha=0.8,
                        bbox={"boxstyle": "round,pad=0.2", "facecolor": "white", "edgecolor": "none", "alpha": 0.7},
                    )

        # Now plot the current year last (so it appears on top)
        if current_year_data:
            x_values, y_values = current_year_data
            line_style = "-"  # Solid for current year
            line_width = 3  # Thicker for current year
            max_points = 10

            ax.plot(
                x_values,
                y_values,
                color=current_year_color,
                linestyle=line_style,
                linewidth=line_width,
                alpha=0.8,
                label=current_year_label,
                marker="o" if len(x_values) <= max_points else None,  # Markers only for few points
                markersize=4,
            )

            # Add value labels for the last point of current year line
            if x_values and y_values:
                last_x = x_values[-1]
                last_y = y_values[-1]

                # Format label with month and year and final value
                month_year = current_year_label.replace(" (Current)", "")  # Remove "(Current)" suffix
                # Format number without .0 for whole numbers
                value_str = f"{last_y:.1f}".rstrip("0").rstrip(".")
                label_text = f"{month_year}: {value_str}"

                ax.annotate(
                    label_text,
                    (last_x, last_y),
                    textcoords="offset points",
                    xytext=(0, 10),
                    ha="center",
                    fontsize=9,
                    alpha=0.8,
                    bbox={"boxstyle": "round,pad=0.2", "facecolor": "white", "edgecolor": "none", "alpha": 0.7},
                )

        # Customize plot
        ax.set_xlabel("Day of Month", fontsize=12)
        y_label = f"Cumulative Value ({exercise_unit})" if exercise_unit else "Cumulative Value"
        ax.set_ylabel(y_label, fontsize=12)

        # Build title
        selected_month_name = self.comboBox_compare_same_months.currentText()
        chart_title = f"{exercise}"
        if exercise_type and exercise_type != "All types":
            chart_title += f" - {exercise_type}"
        chart_title += f" ({selected_month_name} comparison - last {years_count} years)"
        ax.set_title(chart_title, fontsize=14, fontweight="bold")

        ax.grid(visible=True, alpha=0.3)
        ax.legend(loc="upper left", fontsize=10)

        # Set x-axis to show days 1-31
        ax.set_xlim(1, 31)
        ax.set_xticks(range(1, 32, 2))  # Show every other day for readability

        fig.tight_layout()
        self.verticalLayout_charts_content.addWidget(canvas)
        canvas.draw()

        # Add same months recommendations to label_chart_info
        self._add_same_months_recommendations_to_label(exercise, exercise_type, exercise_unit, yearly_data, years_count)

    def on_exercise_name_changed(self, _index: int = -1) -> None:
        """Handle exercise name combobox selection change.

        Args:

        - `_index` (`int`): Index from Qt signal (ignored, but required for signal compatibility). Defaults to `-1`.

        """
        self._update_types_avif()

    def on_exercise_selection_changed(self, _current: QModelIndex, _previous: QModelIndex) -> None:
        """Update form fields when exercise selection changes in the table."""
        index = self.tableView_exercises.currentIndex()
        if not index.isValid():
            # Clear the fields if nothing is selected
            self.lineEdit_exercise_name.clear()
            self.lineEdit_exercise_unit.clear()
            self.check_box_is_type_required.setChecked(False)
            self.doubleSpinBox_calories_per_unit.setValue(0.0)
            return

        model = self.models["exercises"]
        row = index.row()

        # Fill in the fields with data from the selected row
        if model is None:
            return
        name = model.data(model.index(row, 0)) or ""
        unit = model.data(model.index(row, 1)) or ""
        is_required = model.data(model.index(row, 2)) or "0"
        calories_per_unit = model.data(model.index(row, 3)) or "0"

        self.lineEdit_exercise_name.setText(name)
        self.lineEdit_exercise_unit.setText(unit)
        self.check_box_is_type_required.setChecked(is_required == "1")

        try:
            self.doubleSpinBox_calories_per_unit.setValue(float(calories_per_unit))
        except (ValueError, TypeError):
            self.doubleSpinBox_calories_per_unit.setValue(0.0)

        # Update exercises AVIF
        self._update_exercises_avif()

    def on_exercise_selection_changed_list(self) -> None:
        """Handle exercise selection change in the list view."""
        exercise = self._get_current_selected_exercise()
        if not exercise:
            self.comboBox_type.setEnabled(False)
            self.label_exercise.setText("No exercise selected")
            self.label_unit.setText("")
            self.label_last_date_count_today.setText("")
            return

        # Check if database manager is available and connection is open
        if not self._validate_database_connection():
            print("Database manager not available or connection not open")
            self.comboBox_type.setEnabled(False)
            self.label_exercise.setText("Database error")
            self.label_unit.setText("")
            self.label_last_date_count_today.setText("")
            return

        # Update exercise name label
        self.label_exercise.setText(exercise)

        # Check if a new AVIF needs to be loaded
        current_avif_exercise = self.avif_data["main"]["exercise"]
        if current_avif_exercise != exercise:
            self._load_exercise_avif(exercise, "main")

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            ex_id = self.db_manager.get_id("exercises", "name", exercise)
            if ex_id is None:
                print(f"Exercise '{exercise}' not found in database")
                self.comboBox_type.setEnabled(False)
                self.label_unit.setText("")
                self.label_last_date_count_today.setText("")
                return

            # Get exercise unit and display it in separate label
            unit = self.db_manager.get_exercise_unit(exercise)
            self.label_unit.setText(unit)

            # Get last exercise date (regardless of type)
            last_date = self.db_manager.get_last_exercise_date(ex_id)

            # Get total value for today
            total_today = self.db_manager.get_exercise_total_today(ex_id)

            # Format the date and count text for separate label
            date_parts = []

            if last_date:
                try:
                    date_obj = datetime.fromisoformat(last_date).replace(tzinfo=timezone.utc)
                    formatted_date = date_obj.strftime("%b %d, %Y")  # e.g., "Dec 13, 2025"
                    date_parts.append(f"Last: {formatted_date}")
                except ValueError:
                    date_parts.append(f"Last: {last_date}")
            else:
                date_parts.append("Last: Never")

            # Add today's total if it's greater than 0
            if total_today > 0:
                # Format total based on whether it's an integer or float
                if total_today == int(total_today):
                    total_text = f"Today: {int(total_today)} {unit}"
                else:
                    total_text = f"Today: {total_today:.1f} {unit}"
                date_parts.append(total_text)

            # Join parts with comma and space
            self.label_last_date_count_today.setText(", ".join(date_parts))

            # Get all types for this exercise
            types = self.db_manager.get_exercise_types(ex_id)

            # Clear and populate the combobox
            self.comboBox_type.clear()
            self.comboBox_type.addItem("")
            self.comboBox_type.addItems(types)

            # Enable/disable comboBox_type based on whether types are available
            self.comboBox_type.setEnabled(len(types) > 0)

            # Find the most recently used type and value for this exercise
            try:
                last_record = self.db_manager.get_last_exercise_record(ex_id)

                if last_record:
                    last_type, last_value = last_record

                    # Find and select this type in the combobox
                    type_index = self.comboBox_type.findText(last_type)
                    if type_index >= 0:
                        self.comboBox_type.setCurrentIndex(type_index)

                    # Set spinBox_count value based on exercise _id
                    if ex_id == self.id_steps:  # Steps exercise - set to 0 (empty)
                        self.spinBox_count.setValue(0)

                        # For Steps exercise, set date to first day without records
                        current_date = self.dateEdit.date()
                        today = QDate.currentDate()
                        if current_date == today:
                            first_empty_date = self._get_first_day_without_steps_record(ex_id)
                            self.dateEdit.setDate(first_empty_date)
                    else:  # Other exercises - use last value
                        try:
                            value = int(float(last_value))
                            self.spinBox_count.setValue(value)
                        except (ValueError, TypeError):
                            # If conversion fails, keep default value
                            print(f"Could not convert last value '{last_value}' to int for exercise '{exercise}'")
                elif ex_id == self.id_steps:  # Steps exercise - set to 0 (empty)
                    self.spinBox_count.setValue(0)

                    # For Steps exercise, set date to first day without records
                    current_date = self.dateEdit.date()
                    today = QDate.currentDate()
                    if current_date == today:
                        first_empty_date = self._get_first_day_without_steps_record(ex_id)
                        self.dateEdit.setDate(first_empty_date)

            except Exception as e:
                print(f"Error getting last exercise record for '{exercise}': {e}")
                # Continue without setting last values

        except Exception as e:
            print(f"Error in exercise selection changed: {e}")
            self.comboBox_type.setEnabled(False)
            self.label_unit.setText("Error loading data")
            self.label_last_date_count_today.setText("Error loading data")

        if exercise:
            # Sync selection across widgets
            self._sync_exercise_selection(exercise, source="list")

            # Move focus to spinBox_count and select all text
            QTimer.singleShot(0, self._focus_and_select_spinbox_count)

    def on_exercise_type_changed(self, _index: int = -1) -> None:
        """Handle exercise type combobox selection change and sync with statistics.

        Args:

        - `_index` (`int`): Index from Qt signal (ignored, but required for signal compatibility). Defaults to `-1`.

        """
        # Get current exercise from list view
        current_exercise = self._get_current_selected_exercise()
        if not current_exercise:
            return

        # Update statistics exercise combobox if statistics tab is initialized
        if hasattr(self, "_statistics_initialized"):
            # Block signals to prevent recursive updates
            self.comboBox_records_select_exercise.blockSignals(True)  # noqa: FBT003

            # Find and select the current exercise in statistics combobox
            index = self.comboBox_records_select_exercise.findText(current_exercise)
            if index >= 0:
                self.comboBox_records_select_exercise.setCurrentIndex(index)

            # Unblock signals
            self.comboBox_records_select_exercise.blockSignals(False)  # noqa: FBT003

    def on_exercise_type_selection_changed(self, _current: QModelIndex, _previous: QModelIndex) -> None:
        """Update form fields when exercise type selection changes in the table."""
        index = self.tableView_exercise_types.currentIndex()
        if not index.isValid():
            # Clear the fields if nothing is selected
            self.doubleSpinBox_calories_modifier.setValue(1.0)
            return

        model = self.models["types"]
        row = index.row()

        # Fill in the fields with data from the selected row
        if model is None:
            return

        calories_modifier = model.data(model.index(row, 2)) or "1.0"

        try:
            self.doubleSpinBox_calories_modifier.setValue(float(calories_modifier))
        except (ValueError, TypeError):
            self.doubleSpinBox_calories_modifier.setValue(1.0)

    def on_export_csv(self) -> None:
        """Save current `process` view to a CSV file (semicolon-separated).

        Opens a file save dialog and exports the current process table view
        to a CSV file with semicolon-separated values.
        """
        filename_str, _ = QFileDialog.getSaveFileName(
            self,
            "Save Table",
            "",
            "CSV (*.csv)",
        )
        if not filename_str:
            return

        try:
            filename = Path(filename_str)
            model = self.models["process"].sourceModel()  # type: ignore[call-arg]
            with filename.open("w", encoding="utf-8") as file:
                headers = [
                    model.headerData(col, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole) or ""
                    for col in range(model.columnCount())
                ]
                file.write(";".join(headers) + "\n")

                for row in range(model.rowCount()):
                    row_values = [f'"{model.data(model.index(row, col)) or ""}"' for col in range(model.columnCount())]
                    file.write(";".join(row_values) + "\n")

        except Exception as e:
            QMessageBox.warning(self, "Export Error", f"Failed to export CSV: {e}")

    @requires_database()
    def on_process_selection_changed(self, current: QModelIndex, _previous: QModelIndex) -> None:
        """Handle process table selection change and update form fields.

        Updates the form fields (exercise, quantity, type, AVIF image) based on
        the currently selected process record in the table.

        Args:

        - `current` (`QModelIndex`): Currently selected index.
        - `_previous` (`QModelIndex`): Previously selected index.

        """
        if not current.isValid():
            # If no selection, keep current form state
            return

        try:
            model = self.models["process"]
            if not model:
                return

            row = current.row()

            # Get data from the selected row
            exercise_name = model.data(model.index(row, 0)) or ""  # Exercise column
            type_name = model.data(model.index(row, 1)) or ""  # Type column
            value_with_unit = model.data(model.index(row, 2)) or ""  # Quantity column (e.g., "100 times")

            # Extract numeric value from "value unit" format
            value_str = value_with_unit.split()[0] if value_with_unit else "0"

            # Update exercise selection in list view
            if exercise_name:
                self._select_exercise_in_list(exercise_name)

                # This will trigger on_exercise_selection_changed_list() which updates:
                # - label_exercise
                # - label_unit
                # - label_last_date_count_today
                # - comboBox_type options
                # - AVIF image

                # Wait for the exercise selection to complete, then update specific fields
                QTimer.singleShot(
                    50, lambda: self._update_form_from_process_selection(exercise_name, type_name, value_str)
                )

        except Exception as e:
            print(f"Error in process selection changed: {e}")

    def on_radio_button_changed(self) -> None:
        """Handle radio button selection change in chart type group."""
        btn = self.sender()
        if isinstance(btn, QRadioButton) and not btn.isChecked():
            return
        self._schedule_chart_update(50)

    @requires_database()
    def on_refresh_statistics(self) -> None:
        """Populate the statistics table view with records data using database manager."""
        # Set current mode to records
        self.current_statistics_mode = "records"

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            # Clear any existing spans before creating new view
            self.tableView_statistics.clearSpans()

            # Get selected exercise from comboBox_records_select_exercise
            selected_exercise = self.comboBox_records_select_exercise.currentText()

            # Get statistics data using database manager with optional filtering
            rows = self.db_manager.get_filtered_statistics_data(
                exercise_name=selected_exercise if selected_exercise else None
            )

            if not rows:
                # If no data, show empty table
                empty_model = QStandardItemModel()
                empty_model.setHorizontalHeaderLabels(
                    [
                        "Exercise",
                        "Type",
                        "All-Time Value",
                        "All-Time Unit",
                        "All-Time Date",
                        "Year Value",
                        "Year Unit",
                        "Year Date",
                    ]
                )
                self.tableView_statistics.setModel(empty_model)
                self.models["statistics"] = None  # Clear the model reference

                # Set up stretching for empty table too
                header = self.tableView_statistics.horizontalHeader()
                header.setSectionResizeMode(0, header.ResizeMode.Stretch)  # Exercise - stretches
                header.setSectionResizeMode(1, header.ResizeMode.Stretch)  # Type - stretches
                header.setSectionResizeMode(2, header.ResizeMode.ResizeToContents)  # All-Time Value - compact
                header.setSectionResizeMode(3, header.ResizeMode.ResizeToContents)  # All-Time Unit - compact
                header.setSectionResizeMode(4, header.ResizeMode.Stretch)  # All-Time Date - stretches
                header.setSectionResizeMode(5, header.ResizeMode.ResizeToContents)  # Year Value - compact
                header.setSectionResizeMode(6, header.ResizeMode.ResizeToContents)  # Year Unit - compact
                header.setSectionResizeMode(7, header.ResizeMode.Stretch)  # Year Date - stretches
                header.setStretchLastSection(False)

                # Update statistics AVIF
                self._update_statistics_avif()
                return

            # Calculate key date boundaries relative to local time
            local_now = datetime.now(timezone.utc).astimezone()
            today_date = local_now.date()
            yesterday_date = today_date - timedelta(days=1)
            thirty_days_ago = today_date - timedelta(days=30)
            year_days_ago = today_date - timedelta(days=365)

            today = today_date.strftime("%Y-%m-%d")
            yesterday = yesterday_date.strftime("%Y-%m-%d")

            one_year_ago = local_now - timedelta(days=365)
            one_year_ago_str = one_year_ago.strftime("%Y-%m-%d")

            # Group data by exercise and type combination
            grouped: defaultdict[str, list[tuple]] = defaultdict(list)
            grouped_year: defaultdict[str, list[tuple]] = defaultdict(list)

            for ex_name, tp_name, val, date in rows:
                _key = f"{ex_name} {tp_name}".strip()
                grouped[_key].append((ex_name, tp_name, val, date))

                # Add to year group if within last year
                if date >= one_year_ago_str:
                    grouped_year[_key].append((ex_name, tp_name, val, date))

            # Prepare table data
            table_data = []
            span_info = []

            def _decorate_record_date(date_str: str, *, include_last_year_marker: bool = True) -> str:
                """Decorate record date with recency markers."""
                if not date_str:
                    return ""

                if date_str == today:
                    return f"{date_str} ← 🏆TODAY 📅"
                if date_str == yesterday:
                    return f"{date_str} ← 🏆YESTERDAY 📅"

                try:
                    record_date = datetime.fromisoformat(date_str).date()
                except ValueError:
                    return date_str

                if record_date >= thirty_days_ago:
                    return f"{date_str} ← 🏆LAST 30 DAYS 📅"
                if include_last_year_marker and record_date >= year_days_ago:
                    return f"{date_str} ← 🏆LAST 365 DAYS 📅"

                return date_str

            # Define base column colors
            base_column_colors = [
                QColor(240, 248, 255),  # Exercise column - Alice Blue
                QColor(248, 255, 240),  # Type column - Honeydew
                QColor(255, 248, 240),  # All-Time Value column - Seashell
                QColor(255, 248, 240),  # All-Time Unit column - Seashell
                QColor(255, 248, 240),  # All-Time Date column - Seashell
                QColor(248, 240, 255),  # Year Value column - Lavender
                QColor(248, 240, 255),  # Year Unit column - Lavender
                QColor(248, 240, 255),  # Year Date column - Lavender
            ]

            current_row = 0

            for exercise_group_index, (_key, entries) in enumerate(grouped.items()):
                # Sort all-time entries: first by value (descending), then by date (descending)
                entries.sort(key=lambda x: (x[2], x[3]), reverse=True)

                # Get year entries for this group and sort the same way
                year_entries = grouped_year.get(_key, [])
                year_entries.sort(key=lambda x: (x[2], x[3]), reverse=True)

                group_start_row = current_row

                # Determine if this exercise group should be light (even) or dark (odd)
                is_light_group = exercise_group_index % 2 == 0

                # Determine how many rows we need (max of both groups, up to spinBox_record_count value)
                record_count = self.spinBox_record_count.value()
                max_rows = min(max(len(entries), len(year_entries)), record_count)

                for i in range(max_rows):
                    # Get all-time data if available
                    if i < len(entries):
                        ex_name, tp_name, val, date = entries[i]
                        unit = self.db_manager.get_exercise_unit(ex_name)
                        val_str = f"{val:g}"
                        date_display = _decorate_record_date(date)
                    else:
                        ex_name, tp_name = entries[0][:2] if entries else ("", "")
                        unit = ""
                        val_str = ""
                        date_display = ""

                    # Get year data if available
                    if i < len(year_entries):
                        _, _, year_val, year_date = year_entries[i]
                        year_unit = self.db_manager.get_exercise_unit(ex_name) if ex_name else ""
                        year_val_str = f"{year_val:g}"
                        year_date_display = _decorate_record_date(year_date, include_last_year_marker=False)
                    else:
                        year_val_str = ""
                        year_unit = ""
                        year_date_display = ""

                    # For the first row of each group, include exercise and type names
                    # For subsequent rows, use empty strings (they will be spanned)
                    if i == 0:
                        exercise_display = ex_name
                        type_display = tp_name if tp_name else ""
                    else:
                        exercise_display = ""
                        type_display = ""

                    # Add row to table data
                    table_data.append(
                        [
                            exercise_display,
                            type_display,
                            val_str,
                            unit,
                            date_display,
                            year_val_str,
                            year_unit,
                            year_date_display,
                            is_light_group,  # Group brightness flag
                        ]
                    )

                    current_row += 1

                # Store span information for this group
                if max_rows > 1:
                    span_info.append((group_start_row, max_rows, ex_name, tp_name if tp_name else ""))

            # Create and populate model
            model = QStandardItemModel()
            model.setHorizontalHeaderLabels(
                [
                    "Exercise",
                    "Type",
                    "All-Time Value",
                    "All-Time Unit",
                    "All-Time Date",
                    "Year Value",
                    "Year Unit",
                    "Year Date",
                ]
            )

            for row_data in table_data:
                items = []
                is_light_group = row_data[8]  # Group brightness flag

                # Create items for all columns except the brightness flag
                for col_idx, value in enumerate(row_data[:8]):  # Only first 8 elements (exclude flag)
                    item = QStandardItem(str(value))

                    # Get base column color
                    base_color = base_column_colors[col_idx]

                    # Modify color based on exercise group brightness
                    if is_light_group:
                        # Light group - use base color as is
                        final_color = base_color
                    else:
                        # Dark group - make color darker
                        final_color = QColor(
                            int(base_color.red() * 0.85), int(base_color.green() * 0.85), int(base_color.blue() * 0.85)
                        )

                    item.setBackground(QBrush(final_color))

                    # For "TODAY" or "YESTERDAY" entries, make text bold
                    if any(marker in str(value) for marker in ("TODAY", "YESTERDAY", "LAST 30 DAYS", "LAST 365 DAYS")):
                        font = item.font()
                        font.setBold(True)
                        item.setFont(font)

                    items.append(item)

                model.appendRow(items)

            # Set model to table view
            self.tableView_statistics.setModel(model)
            self.models["statistics"] = None  # Clear the model reference since it's not a proxy model

            # Connect selection signal for statistics table
            selection_model = self.tableView_statistics.selectionModel()
            if selection_model:
                selection_model.currentRowChanged.connect(self.on_statistics_selection_changed)

            # Apply spans after setting the model
            for start_row, row_count, exercise_name, type_name in span_info:
                # Always span the Exercise column (column 0)
                self.tableView_statistics.setSpan(start_row, 0, row_count, 1)

                # Always span the Type column (column 1)
                self.tableView_statistics.setSpan(start_row, 1, row_count, 1)

                # Determine if this group is light or dark for spanned cells
                is_light_for_span = table_data[start_row][8]

                # Set the text for the spanned cells with proper background
                exercise_item = QStandardItem(exercise_name)
                type_item = QStandardItem(type_name)

                if is_light_for_span:
                    exercise_item.setBackground(QBrush(base_column_colors[0]))  # Light Exercise column color
                    type_item.setBackground(QBrush(base_column_colors[1]))  # Light Type column color
                else:
                    # Dark versions
                    dark_exercise_color = QColor(
                        int(base_column_colors[0].red() * 0.85),
                        int(base_column_colors[0].green() * 0.85),
                        int(base_column_colors[0].blue() * 0.85),
                    )
                    dark_type_color = QColor(
                        int(base_column_colors[1].red() * 0.85),
                        int(base_column_colors[1].green() * 0.85),
                        int(base_column_colors[1].blue() * 0.85),
                    )
                    exercise_item.setBackground(QBrush(dark_exercise_color))
                    type_item.setBackground(QBrush(dark_type_color))

                model.setItem(start_row, 0, exercise_item)
                model.setItem(start_row, 1, type_item)

            # Custom column width setup for statistics table
            header = self.tableView_statistics.horizontalHeader()

            # Set specific resize modes for each column
            header.setSectionResizeMode(0, header.ResizeMode.Interactive)  # Exercise - fixed width, resizable
            header.setSectionResizeMode(1, header.ResizeMode.Interactive)  # Type - fixed width, resizable
            header.setSectionResizeMode(2, header.ResizeMode.ResizeToContents)  # All-Time Value - compact
            header.setSectionResizeMode(3, header.ResizeMode.ResizeToContents)  # All-Time Unit - compact
            header.setSectionResizeMode(4, header.ResizeMode.Interactive)  # All-Time Date - fixed width, resizable
            header.setSectionResizeMode(5, header.ResizeMode.ResizeToContents)  # Year Value - compact
            header.setSectionResizeMode(6, header.ResizeMode.ResizeToContents)  # Year Unit - compact
            header.setSectionResizeMode(7, header.ResizeMode.Stretch)  # Year Date - stretches to fill remaining

            # Set specific widths for columns
            self.tableView_statistics.setColumnWidth(0, 120)  # Exercise - shorter
            self.tableView_statistics.setColumnWidth(1, 100)  # Type - shorter
            self.tableView_statistics.setColumnWidth(2, 80)  # All-Time Value - compact
            self.tableView_statistics.setColumnWidth(3, 60)  # All-Time Unit - compact
            self.tableView_statistics.setColumnWidth(4, 200)  # All-Time Date - wider
            self.tableView_statistics.setColumnWidth(5, 80)  # Year Value - compact
            self.tableView_statistics.setColumnWidth(6, 60)  # Year Unit - compact
            # Year Date column (7) will stretch to fill remaining space

            # Disable automatic last section stretching since we set it manually
            header.setStretchLastSection(True)

            # Set minimum widths for compact columns to ensure readability
            self.tableView_statistics.setColumnWidth(2, 80)  # All-Time Value
            self.tableView_statistics.setColumnWidth(3, 60)  # All-Time Unit
            self.tableView_statistics.setColumnWidth(5, 80)  # Year Value
            self.tableView_statistics.setColumnWidth(6, 60)  # Year Unit

            # Disable alternating row colors since we have custom colors
            self.tableView_statistics.setAlternatingRowColors(False)

            # Update statistics AVIF
            self._update_statistics_avif()

            # Trigger initial AVIF load for first row if no selection
            QTimer.singleShot(100, self._update_statistics_avif)

        except Exception as e:
            QMessageBox.warning(self, "Statistics Error", f"Failed to load statistics: {e}")

    def on_select_exercise_button_clicked(self) -> None:
        """Open a modal dialog to select an exercise with AVIF previews."""
        if not self._validate_database_connection() or self.db_manager is None:
            QMessageBox.warning(self, "Database Error", "Database connection is not available.")
            return

        try:
            exercises = self.db_manager.get_exercises_by_frequency(500)
        except Exception as exc:
            QMessageBox.warning(self, "Database Error", f"Failed to load exercises: {exc}")
            return

        if not exercises:
            QMessageBox.information(self, "No Exercises", "No exercises are available to select.")
            return

        label_height = self.label_exercise_avif.height()
        preview_edge = max(0, label_height)
        preview_edge = max(min(preview_edge, 512), 160)
        preview_size = QSize(preview_edge, preview_edge)

        current_selection = self._get_current_selected_exercise()

        dialog = ExerciseSelectionDialog(
            self,
            exercises=exercises,
            icon_provider=lambda name: self._get_exercise_preview_icon(name, preview_size),
            preview_size=preview_size,
            current_selection=current_selection,
        )

        dialog_width = max(int(self.width() * 0.95), preview_size.width())
        dialog_height = max(int(self.height() * 0.95), preview_size.height())
        dialog.resize(dialog_width, dialog_height)
        dialog.setMinimumSize(preview_size)

        if dialog.exec() == QDialog.DialogCode.Accepted and dialog.selected_exercise:
            selected_exercise = dialog.selected_exercise
            if not self._select_exercise_in_list(selected_exercise):
                self._update_comboboxes(selected_exercise=selected_exercise)

            selection_model = self.listView_exercises.selectionModel()
            if selection_model:
                current_index = selection_model.currentIndex()
                if current_index.isValid():
                    self.listView_exercises.scrollTo(
                        current_index,
                        QAbstractItemView.ScrollHint.PositionAtCenter,
                    )

    def on_show_exercise_goal_recommendations(self) -> None:
        """Show exercise goal recommendations for all exercises in the statistics table.

        This method generates a table showing goal recommendations for each exercise
        based on the compare_last functionality, displaying how much more is needed
        to reach previous month's goals and maximum goals over the last N months.
        """
        # Set current mode to exercise_goal_recommendations
        self.current_statistics_mode = "exercise_goal_recommendations"

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            # Clear any existing spans from previous statistics view
            self.tableView_statistics.clearSpans()

            # Get all exercises from database
            exercises_data = self.db_manager.get_all_exercises()

            if not exercises_data:
                # If no exercises, show empty table
                empty_model = QStandardItemModel()
                empty_model.setHorizontalHeaderLabels(
                    [
                        "Exercise",
                        "Unit",
                        "Current Progress",
                        "Last Month Goal",
                        "Max Goal",
                        "Remaining to Last Month",
                        "Remaining to Max",
                        "Daily Needed (Last Month)",
                        "Daily Needed (Max)",
                    ]
                )
                self.tableView_statistics.setModel(empty_model)
                self.models["statistics"] = None

                # Configure header
                header = self.tableView_statistics.horizontalHeader()
                for i in range(header.count() - 1):
                    header.setSectionResizeMode(i, header.ResizeMode.Interactive)
                header.setSectionResizeMode(header.count() - 1, header.ResizeMode.Stretch)
                for i in range(header.count() - 1):
                    self.tableView_statistics.setColumnWidth(i, 150)

                self._update_statistics_avif()
                return

            # Get months count from spinBox_compare_last
            months_count = self.spinBox_compare_last.value()

            # Generate recommendations for each exercise
            table_data = []

            for exercise_record in exercises_data:
                # Extract exercise data from the record [_id, name, unit, is_type_required, calories_per_unit]
                exercise_name = exercise_record[1]  # name is at index 1
                exercise_unit = exercise_record[2]  # unit is at index 2
                unit_text = f" {exercise_unit}" if exercise_unit else ""

                try:
                    # Get monthly data for this exercise (similar to compare_last logic)
                    monthly_data = self._get_monthly_data_for_exercise(exercise_name, months_count)

                    if not monthly_data or not any(month_data for month_data in monthly_data):
                        # No data for this exercise
                        table_data.append(
                            [
                                exercise_name,
                                exercise_unit or "",
                                "0",
                                "No data",
                                "No data",
                                "N/A",
                                "N/A",
                                "N/A",
                                "N/A",
                                2,  # Dark red - no data
                            ]
                        )
                        continue

                    # Calculate goals and recommendations
                    recommendations = self._calculate_exercise_recommendations(
                        exercise_name, monthly_data, months_count, exercise_unit
                    )

                    # Determine exercise status for color coding
                    # 0 = green (all goals achieved), 1 = orange (incomplete goals), 2 = dark red (no data)
                    if recommendations["last_month_value"] <= 0 and recommendations["max_value"] <= 0:
                        color_priority = 2  # Dark red - no data
                    elif recommendations["remaining_to_last_month"] <= 0 and recommendations["remaining_to_max"] <= 0:
                        color_priority = 0  # Green - all goals achieved
                    else:
                        color_priority = 1  # Orange - incomplete goals

                    # Add row to table data with color information
                    table_data.append(
                        [
                            exercise_name,
                            exercise_unit or "",
                            f"{int(recommendations['current_progress'])}{unit_text}",
                            f"{int(recommendations['last_month_value'])}{unit_text}"
                            if recommendations["last_month_value"] > 0
                            else "No data",
                            f"{int(recommendations['max_value'])}{unit_text}",
                            f"{int(recommendations['remaining_to_last_month'])}{unit_text}"
                            if recommendations["remaining_to_last_month"] > 0
                            else "✅",
                            f"{int(recommendations['remaining_to_max'])}{unit_text}"
                            if recommendations["remaining_to_max"] > 0
                            else "✅",
                            f"{int(recommendations['daily_needed_last_month'])}{unit_text}"
                            if recommendations["daily_needed_last_month"] > 0
                            else "✅",
                            f"{int(recommendations['daily_needed_max'])}{unit_text}"
                            if recommendations["daily_needed_max"] > 0
                            else "✅",
                            color_priority,  # Add color priority as last element
                        ]
                    )

                except Exception as e:
                    print(f"❌ Error processing exercise {exercise_name}: {e}")
                    # Add error row
                    table_data.append(
                        [
                            exercise_name,
                            "Error",
                            "Error",
                            "Error",
                            "Error",
                            "Error",
                            "Error",
                            "Error",
                            "Error",
                            2,  # Dark red - error
                        ]
                    )
                    continue

            # Sort table data by color priority: green (0), orange (1), dark red (2)
            table_data.sort(key=lambda x: x[-1])

            # Create and populate model
            model = QStandardItemModel()
            model.setHorizontalHeaderLabels(
                [
                    "Exercise",
                    "Unit",
                    "Current Progress",
                    "Last Month Goal",
                    "Max Goal",
                    "Remaining to Last Month",
                    "Remaining to Max",
                    "Daily Needed (Last Month)",
                    "Daily Needed (Max)",
                ]
            )

            color_priority_green = 0
            color_priority_orange = 1
            color_priority_dark_red = 2

            for row_data in table_data:
                items = []
                color_priority = row_data[-1]  # Get color priority from last element

                # Create items for display columns only (exclude the color priority)
                for _col_idx, value in enumerate(row_data[:-1]):  # Exclude last element (color priority)
                    item = QStandardItem(str(value))

                    # Apply color based on priority
                    if color_priority == color_priority_green:  # Green - all goals achieved
                        item.setBackground(QBrush(QColor(200, 255, 200)))  # Light green background
                    elif color_priority == color_priority_orange:  # Orange - incomplete goals
                        item.setBackground(QBrush(QColor(255, 200, 150)))  # Light orange background
                    elif color_priority == color_priority_dark_red:  # Dark red - no data or error
                        item.setBackground(QBrush(QColor(255, 150, 150)))  # Dark red background

                    items.append(item)
                model.appendRow(items)

            # Set model to table view
            self.tableView_statistics.setModel(model)
            self.models["statistics"] = None

            # Connect selection signal for statistics table
            self._connect_table_signals_for_table("statistics", self.on_statistics_selection_changed)

            # Configure header with mixed approach: interactive + stretch last
            header = self.tableView_statistics.horizontalHeader()
            # Set first columns to interactive (resizable)
            for i in range(header.count() - 1):
                header.setSectionResizeMode(i, header.ResizeMode.Interactive)
            # Set last column to stretch to fill remaining space
            header.setSectionResizeMode(header.count() - 1, header.ResizeMode.Stretch)
            # Set default column widths for resizable columns
            for i in range(header.count() - 1):
                self.tableView_statistics.setColumnWidth(i, 120)

            # Disable alternating row colors since we have custom color coding
            self.tableView_statistics.setAlternatingRowColors(False)

            # Update statistics AVIF
            self._update_statistics_avif()

            # Trigger initial AVIF load for first row if no selection
            QTimer.singleShot(100, self._update_statistics_avif)

        except Exception as e:
            QMessageBox.warning(
                self, "Exercise Goal Recommendations Error", f"Failed to load exercise goal recommendations: {e}"
            )

    @requires_database()
    def on_show_last_exercises(self) -> None:
        """Show last execution dates for all exercises in the statistics table."""
        # Set current mode to last_exercises
        self.current_statistics_mode = "last_exercises"

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            # Clear any existing spans from previous statistics view
            self.tableView_statistics.clearSpans()

            # Get last exercise dates using database manager
            exercise_dates = self.db_manager.get_last_exercise_dates()

            if not exercise_dates:
                # If no data, show empty table
                empty_model = QStandardItemModel()
                empty_model.setHorizontalHeaderLabels(["Exercise", "Last Execution Date", "Days Ago"])
                self.tableView_statistics.setModel(empty_model)
                self.models["statistics"] = None  # Clear the model reference

                # Configure header with mixed approach: interactive + stretch last
                header = self.tableView_statistics.horizontalHeader()
                # Set first columns to interactive (resizable)
                for i in range(header.count() - 1):
                    header.setSectionResizeMode(i, header.ResizeMode.Interactive)
                # Set last column to stretch to fill remaining space
                header.setSectionResizeMode(header.count() - 1, header.ResizeMode.Stretch)
                # Set default column widths for resizable columns
                for i in range(header.count() - 1):
                    self.tableView_statistics.setColumnWidth(i, 150)

                # Update statistics AVIF
                self._update_statistics_avif()
                return

            # Calculate days ago for each exercise
            today = datetime.now(timezone.utc).astimezone().date()
            table_data = []

            for exercise_name, last_date_str in exercise_dates:
                try:
                    last_date = datetime.fromisoformat(last_date_str).date()
                    days_ago = (today - last_date).days

                    # Format the display date
                    formatted_date = last_date.strftime("%Y-%m-%d (%b %d)")

                    # Add emoji for recent activities
                    days_in_week = 7
                    days_in_month = 30
                    if days_ago == 0:
                        days_display = "Today 🔥"
                        row_color = QColor(144, 238, 144)  # Light green for today
                    elif days_ago == 1:
                        days_display = "1 day ago 👍"
                        row_color = QColor(173, 216, 230)  # Light blue for yesterday
                    elif days_ago <= days_in_week:
                        days_display = f"{days_ago} days ago ✅"
                        row_color = QColor(255, 255, 224)  # Light yellow for this week
                    elif days_ago <= days_in_month:
                        days_display = f"{days_ago} days ago ⚠️"
                        row_color = QColor(255, 228, 196)  # Light orange for this month
                    else:
                        days_display = f"{days_ago} days ago ❗"
                        row_color = QColor(255, 192, 203)  # Light pink for longer periods

                    table_data.append([exercise_name, formatted_date, days_display, row_color])

                except ValueError:
                    # Skip invalid dates
                    continue

            # Sort by days ago (ascending - most recent first)
            table_data.sort(key=lambda x: int(x[2].split()[0]) if x[2].split()[0].isdigit() else 0)

            # Create and populate model
            model = QStandardItemModel()
            model.setHorizontalHeaderLabels(["Exercise", "Last Execution Date", "Days Ago"])

            for row_data in table_data:
                items = []
                row_color = row_data[3]  # Get the color from the last element

                # Create items for display columns only (first 3 elements)
                for col_idx, value in enumerate(row_data[:3]):  # Only first 3 elements (exclude color)
                    item = QStandardItem(str(value))

                    # Set background color for the item
                    item.setBackground(QBrush(row_color))

                    # Make "Today" entries bold
                    id_col_date = 2
                    if col_idx == id_col_date and "Today" in str(value):
                        font = item.font()
                        font.setBold(True)
                        item.setFont(font)

                    items.append(item)

                model.appendRow(items)

            # Set model to table view
            self.tableView_statistics.setModel(model)
            self.models["statistics"] = None  # Clear the model reference

            # Connect selection signal for statistics table
            self._connect_table_signals_for_table("statistics", self.on_statistics_selection_changed)

            # Configure header with mixed approach: interactive + stretch last
            header = self.tableView_statistics.horizontalHeader()
            # Set first columns to interactive (resizable)
            for i in range(header.count() - 1):
                header.setSectionResizeMode(i, header.ResizeMode.Interactive)
            # Set last column to stretch to fill remaining space
            header.setSectionResizeMode(header.count() - 1, header.ResizeMode.Stretch)
            # Set default column widths for resizable columns
            for i in range(header.count() - 1):
                self.tableView_statistics.setColumnWidth(i, 150)

            # Disable alternating row colors since we have custom colors
            self.tableView_statistics.setAlternatingRowColors(False)

            # Update statistics AVIF
            self._update_statistics_avif()

            # Trigger initial AVIF load for first row if no selection
            QTimer.singleShot(100, self._update_statistics_avif)

        except Exception as e:
            QMessageBox.warning(self, "Last Exercises Error", f"Failed to load last exercises: {e}")

    def on_statistics_exercise_combobox_changed(self, _index: int = -1) -> None:
        """Handle statistics exercise combobox selection change."""
        exercise_name = self.comboBox_records_select_exercise.currentText().strip()
        if exercise_name:
            self._sync_exercise_selection(exercise_name, source="combo")

    def on_statistics_selection_changed(self, _current: QModelIndex, _previous: QModelIndex) -> None:
        """Handle statistics table selection change and update AVIF.

        Args:

        - `_current` (`QModelIndex`): Currently selected index.
        - `_previous` (`QModelIndex`): Previously selected index.

        """
        # Only update AVIF if not in check_steps mode (since check_steps always shows Steps exercise)
        if self.current_statistics_mode != "check_steps":
            self._update_statistics_avif()

    def on_tab_changed(self, index: int) -> None:
        """React to `QTabWidget` index change.

        Args:

        - `index` (`int`): The index of the newly selected tab.

        """
        index_tab_charts = 1
        index_tab_exercises = 2
        index_tab_weight = 3
        index_tab_statistics = 4

        # Note: Main tab (index 0) needs no updates - data loaded on startup
        if index == index_tab_charts:  # Exercise Chart tab
            self.update_chart_comboboxes()
            self._load_default_exercise_chart()
            if not self._get_selected_chart_exercise():
                self._select_last_executed_exercise()
            self._update_charts_avif()
        elif index == index_tab_exercises:  # Exercises tab
            # Update exercises AVIF when switching to exercises tab
            self._update_exercises_avif()
            self._update_types_avif()
        elif index == index_tab_weight:  # Weight tab
            self.set_weight_all_time()
        elif index == index_tab_statistics:  # Statistics tab
            self._load_default_statistics()
            # If statistics is already initialized, update with current exercise
            if hasattr(self, "_statistics_initialized"):
                current_exercise = self._get_current_selected_exercise()
                if current_exercise:
                    # Block signals to prevent recursive updates
                    self.comboBox_records_select_exercise.blockSignals(True)  # noqa: FBT003

                    # Find and select the current exercise in statistics combobox
                    index = self.comboBox_records_select_exercise.findText(current_exercise)
                    if index >= 0:
                        self.comboBox_records_select_exercise.setCurrentIndex(index)

                    # Unblock signals
                    self.comboBox_records_select_exercise.blockSignals(False)  # noqa: FBT003

                    # Refresh statistics with the selected exercise
                    self.on_refresh_statistics()

    @requires_database()
    def on_toggle_show_all_records(self) -> None:
        """Toggle between showing all records and limited records (self.count_records_to_show).

        When show_all_records is False (default), shows only the last self.count_records_to_show records.
        When True, shows all records from the database.
        """
        # Toggle the flag
        self.show_all_records = not self.show_all_records

        # Update button text to reflect current state
        if self.show_all_records:
            self.pushButton_show_all_records.setText(f"📋 Show Last {self.count_records_to_show}")
        else:
            self.pushButton_show_all_records.setText("📋 Show All Records")

        # Reload the process table with the appropriate data
        self.load_process_table()

    def on_weight_selection_changed(self, _current: QModelIndex, _previous: QModelIndex) -> None:
        """Update form fields when weight selection changes in the table.

        Synchronizes the form fields (weight value and date) with the currently
        selected weight record in the table.

        Args:

        - `_current` (`QModelIndex`): Currently selected index.
        - `_previous` (`QModelIndex`): Previously selected index.

        """
        index = self.tableView_weight.currentIndex()
        if not index.isValid():
            # Clear the fields if nothing is selected - use last weight
            last_weight = self._get_last_weight()
            self.doubleSpinBox_weight.setValue(last_weight)
            self.dateEdit_weight.setDate(QDate.currentDate())
            return

        model = self.models["weight"]
        row = index.row()

        # Fill in the fields with data from the selected row
        if model is None:
            return
        weight_value = model.data(model.index(row, 0)) or str(self._get_last_weight())
        weight_date = model.data(model.index(row, 1)) or QDate.currentDate().toString("yyyy-MM-dd")

        try:
            self.doubleSpinBox_weight.setValue(float(weight_value))
        except (ValueError, TypeError):
            self.doubleSpinBox_weight.setValue(self._get_last_weight())

        # Parse and set the date
        try:
            date_obj = QDate.fromString(weight_date, "yyyy-MM-dd")
            if date_obj.isValid():
                self.dateEdit_weight.setDate(date_obj)
            else:
                self.dateEdit_weight.setDate(QDate.currentDate())
        except Exception:
            self.dateEdit_weight.setDate(QDate.currentDate())

    def set_chart_all_time(self) -> None:
        """Set chart date range to all available data using database manager."""
        self._set_date_range(self.dateEdit_chart_from, self.dateEdit_chart_to, is_all_time=True)
        self._schedule_chart_update(50)

    def set_chart_last_month(self) -> None:
        """Set chart date range to last month."""
        self._set_date_range(self.dateEdit_chart_from, self.dateEdit_chart_to, months=1)
        self._schedule_chart_update(50)

    def set_chart_last_year(self) -> None:
        """Set chart date range to last year."""
        self._set_date_range(self.dateEdit_chart_from, self.dateEdit_chart_to, years=1)
        self._schedule_chart_update(50)

    def set_today_date(self) -> None:
        """Set today's date in the date edit fields and last weight value.

        Sets both the main date input field (QDateEdit) and the weight date input field
        (now also QDateEdit) to today's date. Also sets the weight spinbox to the last recorded weight.
        """
        today_qdate = QDate.currentDate()

        # Set the main QDateEdit to today's date
        self.dateEdit.setDate(today_qdate)

        # Set the weight QDateEdit to today's date
        self.dateEdit_weight.setDate(today_qdate)

        # Set the weight spinbox to the last recorded weight
        last_weight = self._get_last_weight()
        self.doubleSpinBox_weight.setValue(last_weight)

    def set_weight_all_time(self) -> None:
        """Set weight chart date range to all available data using database manager."""
        self._set_date_range(self.dateEdit_weight_from, self.dateEdit_weight_to, is_all_time=True)
        self.update_weight_chart()

    def set_weight_last_month(self) -> None:
        """Set weight chart date range to last month."""
        self._set_date_range(self.dateEdit_weight_from, self.dateEdit_weight_to, months=1)
        self.update_weight_chart()

    def set_weight_last_year(self) -> None:
        """Set weight chart date range to last year."""
        self._set_date_range(self.dateEdit_weight_from, self.dateEdit_weight_to, years=1)
        self.update_weight_chart()

    def set_yesterday_date(self) -> None:
        """Set yesterday's date in the main date edit field.

        Sets the dateEdit widget to yesterday's date for convenient entry
        of exercise records from the previous day.
        """
        yesterday = QDate.currentDate().addDays(-1)
        self.dateEdit.setDate(yesterday)

    @requires_database()
    def show_kcal_chart(self) -> None:
        """Show chart of total calories using database manager."""
        period = self.comboBox_chart_period.currentText()
        date_from = self.dateEdit_chart_from.date().toString("yyyy-MM-dd")
        date_to = self.dateEdit_chart_to.date().toString("yyyy-MM-dd")
        use_max_value = self.checkBox_max_value.isChecked()  # Check if max value mode is enabled

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        # Get calories data using database manager
        rows = self.db_manager.get_kcal_chart_data(date_from, date_to)

        # Convert to datetime objects for processing
        datetime_data = []
        for date_str, calories in rows:
            try:
                date_obj = datetime.fromisoformat(date_str).replace(tzinfo=timezone.utc)
                datetime_data.append((date_obj, float(calories)))
            except (ValueError, TypeError):
                continue

        # Group data by period with aggregation based on checkbox
        if use_max_value:
            # For calories chart, we need to convert the data format for max grouping
            # Convert from (date_str, calories) to (date_str, calories_str)
            string_rows = [(date_str, str(calories)) for date_str, calories in rows]
            grouped_data = self._group_data_by_period_with_max(string_rows, period, value_type="float")
        else:
            grouped_data = self._group_data_by_period(rows, period, value_type="float")

        # In show_kcal_chart, on no grouped_data
        if not grouped_data:
            self._clear_layout(self.verticalLayout_charts_content)
            self._show_no_data_label(self.verticalLayout_charts_content, "No calories data to display")
            self._set_no_data_info_label("No data for the selected period.")
            return

        # Prepare chart data
        chart_data = list(grouped_data.items())

        # For calories chart, respect the selected date range
        # But don't extend beyond today
        today = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d")
        chart_date_from = date_from
        chart_date_to = min(today, date_to)

        # Build chart title with aggregation type
        aggregation_type = "Max" if use_max_value else "Total"
        chart_title = f"Calories burned ({aggregation_type}, {period})"

        # Define custom statistics formatter for calories with aggregation type
        def format_calories_stats(values: list) -> str:
            min_val = min(values)
            max_val = max(values)
            avg_val = sum(values) / len(values)

            if use_max_value:
                # For max values, don't show total (it doesn't make sense)
                return f"Min: {min_val:.1f} kcal | Max: {max_val:.1f} kcal | Avg: {avg_val:.1f} kcal"
            # For sum values, show total
            total_val = sum(values)
            return (
                f"Min: {min_val:.1f} kcal | Max: {max_val:.1f} kcal | "
                f"Avg: {avg_val:.1f} kcal | Total: {total_val:.1f} kcal"
            )

        # Create chart configuration
        chart_config = {
            "title": chart_title,
            "xlabel": "Date",
            "ylabel": f"{aggregation_type} calories (kcal)",
            "color": "orange",
            "show_stats": True,
            "period": period,
            "stats_formatter": format_calories_stats,
            "fill_zero_periods": True,  # Enable zero filling
            "date_from": chart_date_from,  # Use selected start date
            "date_to": chart_date_to,  # Don't go beyond today
        }

        self._create_chart(self.verticalLayout_charts_content, chart_data, chart_config)

        # Add calories recommendations to label_chart_info
        self._add_calories_recommendations_to_label()

    @requires_database()
    def show_sets_chart(self) -> None:
        """Show chart of total sets using database manager."""
        period = self.comboBox_chart_period.currentText()
        date_from = self.dateEdit_chart_from.date().toString("yyyy-MM-dd")
        date_to = self.dateEdit_chart_to.date().toString("yyyy-MM-dd")
        use_max_value = self.checkBox_max_value.isChecked()  # Check if max value mode is enabled

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        # Get sets data using database manager
        rows = self.db_manager.get_sets_chart_data(date_from, date_to)

        # Convert to datetime objects for processing
        datetime_data = []
        for date_str, count in rows:
            try:
                date_obj = datetime.fromisoformat(date_str).replace(tzinfo=timezone.utc)
                datetime_data.append((date_obj, int(count)))
            except (ValueError, TypeError):
                continue

        # Group data by period with aggregation based on checkbox
        if use_max_value:
            # For sets chart, we need to convert the data format for max grouping
            # Convert from (date_str, count) to (date_str, count_str)
            string_rows = [(date_str, str(count)) for date_str, count in rows]
            grouped_data = self._group_data_by_period_with_max(string_rows, period, value_type="int")
        else:
            grouped_data = self._group_data_by_period(rows, period, value_type="int")

        # In show_sets_chart, on no grouped_data
        if not grouped_data:
            self._clear_layout(self.verticalLayout_charts_content)
            self._show_no_data_label(self.verticalLayout_charts_content, "No data to display")
            self._set_no_data_info_label("No data for the selected period.")
            return

        # Prepare chart data
        chart_data = list(grouped_data.items())

        # For sets chart, respect the selected date range
        # But don't extend beyond today
        today = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d")
        chart_date_from = date_from
        chart_date_to = min(today, date_to)

        # Build chart title with aggregation type
        aggregation_type = "Max" if use_max_value else "Total"
        chart_title = f"Training sets ({aggregation_type}, {period})"

        # Define custom statistics formatter for sets with aggregation type
        def format_sets_stats(values: list) -> str:
            min_val = int(min(values))
            max_val = int(max(values))
            avg_val = sum(values) / len(values)

            if use_max_value:
                # For max values, don't show total (it doesn't make sense)
                return f"Min: {min_val} | Max: {max_val} | Avg: {avg_val:.1f}"
            # For sum values, show total
            total_val = int(sum(values))
            return f"Min: {min_val} | Max: {max_val} | Avg: {avg_val:.1f} | Total: {total_val}"

        # Create chart configuration
        chart_config = {
            "title": chart_title,
            "xlabel": "Date",
            "ylabel": f"{aggregation_type} number of sets",
            "color": "green",
            "show_stats": True,
            "period": period,
            "stats_formatter": format_sets_stats,
            "fill_zero_periods": True,  # Enable zero filling
            "date_from": chart_date_from,  # Use selected start date
            "date_to": chart_date_to,  # Don't go beyond today
        }

        self._create_chart(self.verticalLayout_charts_content, chart_data, chart_config)

        # Add sets recommendations to label_chart_info
        self._add_sets_recommendations_to_label()

    def show_tables(self) -> None:
        """Populate all QTableViews using database manager methods."""
        if not self._validate_database_connection():
            print("Database connection not available for showing tables")
            return

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            # Refresh exercises table with light green background
            exercises_data = self.db_manager.get_all_exercises()
            exercises_transformed_data = []
            light_green = QColor(240, 255, 240)  # Light green background

            for row in exercises_data:
                transformed_row = [row[1], row[2], str(row[3]), f"{row[4]:.1f}", row[0], light_green]
                exercises_transformed_data.append(transformed_row)

            self.models["exercises"] = self._create_colored_table_model(
                exercises_transformed_data, self.table_config["exercises"][2]
            )
            self.tableView_exercises.setModel(self.models["exercises"])

            # Refresh exercise types table with light orange background
            types_data = self.db_manager.get_all_exercise_types()
            types_transformed_data = []
            light_orange = QColor(255, 248, 220)  # Light orange background

            for row in types_data:
                transformed_row = [row[1], row[2], f"{row[3]:.1f}", row[0], light_orange]
                types_transformed_data.append(transformed_row)

            self.models["types"] = self._create_colored_table_model(
                types_transformed_data, self.table_config["types"][2]
            )
            self.tableView_exercise_types.setModel(self.models["types"])

            # Load process table data with appropriate limit
            self.load_process_table()

            # Refresh weight table (keeping original implementation)
            self._refresh_table("weight", self.db_manager.get_all_weight_records)

            # Configure weight table header - mixed approach: interactive + stretch last
            weight_header = self.tableView_weight.horizontalHeader()
            # Set first column to interactive (resizable)
            weight_header.setSectionResizeMode(0, weight_header.ResizeMode.Interactive)
            # Set last column to stretch to fill remaining space
            weight_header.setSectionResizeMode(1, weight_header.ResizeMode.Stretch)
            # Set default width for resizable column
            self.tableView_weight.setColumnWidth(0, 100)  # Weight
            # Date column will stretch automatically

            # Configure exercises table header - mixed approach: interactive + stretch last
            exercises_header = self.tableView_exercises.horizontalHeader()
            # Set first columns to interactive (resizable)
            for i in range(exercises_header.count() - 1):
                exercises_header.setSectionResizeMode(i, exercises_header.ResizeMode.Interactive)
            # Set last column to stretch to fill remaining space
            exercises_header.setSectionResizeMode(exercises_header.count() - 1, exercises_header.ResizeMode.Stretch)
            # Set default column widths for resizable columns
            self.tableView_exercises.setColumnWidth(0, 200)  # Exercise name
            self.tableView_exercises.setColumnWidth(1, 120)  # Unit
            self.tableView_exercises.setColumnWidth(2, 100)  # Type Required
            # Calories per Unit column will stretch automatically

            # Configure exercise types table header - mixed approach: interactive + stretch last
            exercise_types_header = self.tableView_exercise_types.horizontalHeader()
            # Set first columns to interactive (resizable)
            for i in range(exercise_types_header.count() - 1):
                exercise_types_header.setSectionResizeMode(i, exercise_types_header.ResizeMode.Interactive)
            # Set last column to stretch to fill remaining space
            exercise_types_header.setSectionResizeMode(
                exercise_types_header.count() - 1, exercise_types_header.ResizeMode.Stretch
            )
            # Set default column widths for resizable columns
            self.tableView_exercise_types.setColumnWidth(0, 200)  # Exercise
            self.tableView_exercise_types.setColumnWidth(1, 150)  # Exercise Type
            # Calories Modifier column will stretch automatically

            # Connect selection change signals after models are set
            self._connect_table_selection_signals()

            # Connect auto-save signals after all models are created
            self._connect_table_auto_save_signals()

            # Update sets count for today
            self.update_sets_count_today()

        except Exception as e:
            print(f"Error showing tables: {e}")
            QMessageBox.warning(self, "Database Error", f"Failed to load tables: {e}")

    def update_all(
        self,
        *,
        is_skip_date_update: bool = False,
        is_preserve_selections: bool = False,
        current_exercise: str | None = None,
        current_type: str | None = None,
    ) -> None:
        """Refresh tables, list view and (optionally) dates."""
        if not self._validate_database_connection():
            print("Database connection not available for update_all")
            return

        # Reset show_all_records flag to default (show limited records)
        self.show_all_records = False
        self.pushButton_show_all_records.setText("📋 Show All Records")

        if is_preserve_selections and current_exercise is None:
            current_exercise = self._get_current_selected_exercise()
            current_type = self.comboBox_type.currentText()

        self.show_tables()

        if is_preserve_selections and current_exercise:
            self._update_comboboxes(
                selected_exercise=current_exercise,
                selected_type=current_type,
            )
        else:
            self._update_comboboxes()

        if not is_skip_date_update:
            self.set_today_date()

        self.update_filter_comboboxes()

        # Update statistics exercise combobox if statistics tab is initialized
        if hasattr(self, "_statistics_initialized"):
            self.update_statistics_exercise_combobox()

        # Clear the exercise addition form after updating
        self.lineEdit_exercise_name.clear()
        self.lineEdit_exercise_unit.clear()
        self.check_box_is_type_required.setChecked(False)
        self.doubleSpinBox_calories_per_unit.setValue(0.0)

        # Clear the type addition form after updating
        self.lineEdit_exercise_type.clear()
        self.doubleSpinBox_calories_modifier.setValue(1.0)

        # Load AVIF for the currently selected exercise
        current_exercise_name = self._get_current_selected_exercise()
        if isinstance(current_exercise_name, str):
            self._load_exercise_avif(current_exercise_name, "main")

        # Update other AVIFs
        self._update_exercises_avif()
        self._update_types_avif()
        self._update_charts_avif()

    @requires_database(is_show_warning=False)
    def update_chart_comboboxes(self) -> None:
        """Update exercise and type list views for charts."""
        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            previous_exercise = self._get_selected_chart_exercise()
            # Update exercise list view - sort by last execution date
            exercises = self.db_manager.get_exercises_by_last_execution()

            # Create model for exercise list view
            exercise_model = QStandardItemModel()
            if exercises:
                for exercise in exercises:
                    # Get today's goal info for this exercise
                    goal_info = self._get_exercise_today_goal_info(exercise)

                    # Create display text with goal info if available
                    display_text = f"{exercise} {goal_info}" if goal_info else exercise
                    item = QStandardItem(display_text)

                    # Store original exercise name in item data for later retrieval
                    item.setData(exercise, Qt.UserRole)
                    exercise_model.appendRow(item)

            self.listView_chart_exercise.setModel(exercise_model)

            # Connect signals after setting model (disconnect first to avoid duplicates)
            selection_model = self.listView_chart_exercise.selectionModel()
            if selection_model:
                with contextlib.suppress(TypeError):
                    selection_model.currentChanged.disconnect()
                selection_model.currentChanged.connect(self.update_chart_type_listview)
                selection_model.currentChanged.connect(self.on_chart_exercise_changed)

            # Restore previous selection if possible, otherwise select the first item
            if previous_exercise:
                if not self._select_exercise_in_chart_list(previous_exercise) and exercise_model.rowCount() > 0:
                    self.listView_chart_exercise.setCurrentIndex(exercise_model.index(0, 0))
            elif exercise_model.rowCount() > 0:
                self.listView_chart_exercise.setCurrentIndex(exercise_model.index(0, 0))

            # Update type list view
            self.update_chart_type_listview()

        except Exception as e:
            print(f"Error updating chart list views: {e}")

    @requires_database(is_show_warning=False)
    def update_chart_type_listview(
        self, current: QModelIndex | None = None, previous: QModelIndex | None = None
    ) -> None:
        """Update chart type list view based on selected exercise.

        Args:

        - `current` (`QModelIndex | None`): Currently selected index. Defaults to invalid index.
        - `previous` (`QModelIndex | None`): Previously selected index. Defaults to invalid index.

        """
        # Avoid mutable or function call defaults; set to None and handle inside
        if current is None:
            current = QModelIndex()
        if previous is None:
            previous = QModelIndex()

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            # Create model for type list view
            type_model = QStandardItemModel()

            # Add "All types" option
            all_types_item = QStandardItem("All types")
            type_model.appendRow(all_types_item)

            # Get selected exercise from list view
            exercise = self._get_selected_chart_exercise()
            if exercise:
                ex_id = self.db_manager.get_id("exercises", "name", exercise)
                if ex_id is not None:
                    types = self.db_manager.get_exercise_types(ex_id)
                    for type_name in types:
                        item = QStandardItem(type_name)
                        type_model.appendRow(item)

            self.listView_chart_type.setModel(type_model)

            # Connect signals after setting model
            selection_model = self.listView_chart_type.selectionModel()
            if selection_model:
                with contextlib.suppress(TypeError):
                    selection_model.currentChanged.disconnect()
                selection_model.currentChanged.connect(self.on_chart_type_changed)

            # Select first item by default (All types)
            if type_model.rowCount() > 0:
                self.listView_chart_type.setCurrentIndex(type_model.index(0, 0))

        except Exception as e:
            print(f"Error updating chart type list view: {e}")

    @requires_database()
    def update_exercise_chart(self) -> None:
        """Update the exercise chart using database manager."""
        exercise = self._get_selected_chart_exercise()
        exercise_type = self._get_selected_chart_type()
        period = self.comboBox_chart_period.currentText()
        date_from = self.dateEdit_chart_from.date().toString("yyyy-MM-dd")
        date_to = self.dateEdit_chart_to.date().toString("yyyy-MM-dd")
        use_max_value = self.checkBox_max_value.isChecked()  # Check if max value mode is enabled

        if not exercise:
            # Clear existing chart before showing no data message
            self._clear_layout(self.verticalLayout_charts_content)
            self._show_no_data_label(self.verticalLayout_charts_content, "Please select an exercise")
            return

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        # Get exercise unit for Y-axis label
        exercise_unit = self.db_manager.get_exercise_unit(exercise)

        # Get chart data using database manager
        rows = self.db_manager.get_exercise_chart_data(
            exercise_name=exercise,
            exercise_type=exercise_type if exercise_type != "All types" else None,
            date_from=date_from,
            date_to=date_to,
        )

        # Convert to datetime objects for processing
        datetime_data = []
        for date_str, value_str in rows:
            try:
                date_obj = datetime.fromisoformat(date_str).replace(tzinfo=timezone.utc)
                value = float(value_str)
                datetime_data.append((date_obj, value))
            except (ValueError, TypeError):
                continue

        # In update_exercise_chart, before every 'return' that indicates no data:
        if not datetime_data:
            self._clear_layout(self.verticalLayout_charts_content)
            self._show_no_data_label(self.verticalLayout_charts_content, "No data found for the selected filters")
            self._set_no_data_info_label("No data for the selected period.")
            return

        # Group data by period with aggregation based on checkbox
        if use_max_value:
            grouped_data = self._group_data_by_period_with_max(rows, period, value_type="float")
        else:
            grouped_data = self._group_data_by_period(rows, period, value_type="float")

        if not grouped_data:
            # Clear existing chart before showing no data message
            self._clear_layout(self.verticalLayout_charts_content)
            self._show_no_data_label(self.verticalLayout_charts_content, "No data found for the selected period")
            return

        # Prepare chart data
        chart_data = list(grouped_data.items())

        # For exercise chart, respect the selected date range
        # But don't extend beyond today
        today = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d")
        chart_date_from = date_from
        chart_date_to = min(today, date_to)

        # Build chart title with aggregation type
        aggregation_type = "Max" if use_max_value else "Total"
        chart_title = f"{exercise}"
        if exercise_type and exercise_type != "All types":
            chart_title += f" - {exercise_type}"
        chart_title += f" ({aggregation_type}, {period})"

        # Define custom statistics formatter for exercise with aggregation type
        def format_exercise_stats(values: list) -> str:
            min_val = min(values)
            max_val = max(values)
            avg_val = sum(values) / len(values)

            if use_max_value:
                # For max values, don't show total (it doesn't make sense)
                return f"Min: {min_val:.1f} | Max: {max_val:.1f} | Avg: {avg_val:.1f}"
            # For sum values, show total
            total_val = sum(values)
            return f"Min: {min_val:.1f} | Max: {max_val:.1f} | Avg: {avg_val:.1f} | Total: {total_val:.1f}"

        # Create chart configuration
        chart_config = {
            "title": chart_title,
            "xlabel": "Date",
            "ylabel": f"{aggregation_type} value ({exercise_unit})" if exercise_unit else f"{aggregation_type} value",
            "color": "blue",
            "show_stats": True,
            "period": period,
            "stats_formatter": format_exercise_stats,
            "fill_zero_periods": True,  # Enable zero filling
            "date_from": chart_date_from,  # Use selected start date
            "date_to": chart_date_to,  # Don't go beyond today
        }

        self._create_chart(self.verticalLayout_charts_content, chart_data, chart_config)

        # Add exercise recommendations to label_chart_info using the same method as compare_last
        self._add_exercise_recommendations_to_label_for_standard_chart(exercise, exercise_type, exercise_unit)

    @requires_database(is_show_warning=False)
    def update_filter_comboboxes(self) -> None:
        """Refresh `exercise` and `type` combo-boxes in the filter group.

        Updates the exercise and type comboboxes in the filter section with
        the latest data from the database, attempting to preserve the current
        selections.
        """
        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            current_exercise = self.comboBox_filter_exercise.currentText()

            self.comboBox_filter_exercise.blockSignals(True)  # noqa: FBT003
            self.comboBox_filter_exercise.clear()
            self.comboBox_filter_exercise.addItem("")  # all exercises
            exercises = self.db_manager.get_exercises_by_frequency(500)
            self.comboBox_filter_exercise.addItems(exercises)
            if current_exercise:
                idx = self.comboBox_filter_exercise.findText(current_exercise)
                if idx >= 0:
                    self.comboBox_filter_exercise.setCurrentIndex(idx)
            self.comboBox_filter_exercise.blockSignals(False)  # noqa: FBT003

            self.update_filter_type_combobox()

        except Exception as e:
            print(f"Error updating filter comboboxes: {e}")

    @requires_database(is_show_warning=False)
    def update_filter_type_combobox(self, _index: int = -1) -> None:
        """Populate `type` filter based on the `exercise` filter selection.

        Updates the exercise type combobox in the filter section based on the
        currently selected exercise, attempting to preserve the current type
        selection if possible.

        Args:

        - `_index` (`int`): Index from Qt signal (ignored, but required for signal compatibility). Defaults to `-1`.

        """
        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            current_type = self.comboBox_filter_type.currentText()
            self.comboBox_filter_type.clear()
            self.comboBox_filter_type.addItem("")

            exercise = self.comboBox_filter_exercise.currentText()
            if exercise:
                ex_id = self.db_manager.get_id("exercises", "name", exercise)
                if ex_id is not None:
                    types = self.db_manager.get_exercise_types(ex_id)
                    self.comboBox_filter_type.addItems(types)

            if current_type:
                idx = self.comboBox_filter_type.findText(current_type)
                if idx >= 0:
                    self.comboBox_filter_type.setCurrentIndex(idx)

        except Exception as e:
            print(f"Error updating filter type combobox: {e}")

    def update_sets_count_today(self) -> None:
        """Update the label showing count of sets done today."""
        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        if not self._validate_database_connection():
            self.label_count_sets_today.setText("0")
            return

        try:
            count = self.db_manager.get_sets_count_today()
            self.label_count_sets_today.setText(str(count))
        except Exception as e:
            print(f"Error getting sets count for today: {e}")
            self.label_count_sets_today.setText("0")

    @requires_database(is_show_warning=False)
    def update_statistics_exercise_combobox(self, _index: int = -1) -> None:
        """Update statistics exercise combobox with available exercises.

        Args:

        - `_index` (`int`): Index from Qt signal (ignored, but required for signal compatibility). Defaults to `-1`.

        """
        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            # Get exercises sorted by frequency
            exercises = self.db_manager.get_exercises_by_frequency(500)

            # Block signals during update
            self.comboBox_records_select_exercise.blockSignals(True)  # noqa: FBT003

            # Store current selection
            current_exercise = self.comboBox_records_select_exercise.currentText()

            # Clear and populate combobox
            self.comboBox_records_select_exercise.clear()
            self.comboBox_records_select_exercise.addItem("")  # Empty option for all exercises
            self.comboBox_records_select_exercise.addItems(exercises)

            # Restore selection if it still exists
            if current_exercise:
                index = self.comboBox_records_select_exercise.findText(current_exercise)
                if index >= 0:
                    self.comboBox_records_select_exercise.setCurrentIndex(index)

            # Unblock signals
            self.comboBox_records_select_exercise.blockSignals(False)  # noqa: FBT003

        except Exception as e:
            print(f"Error updating statistics exercise combobox: {e}")

    @requires_database()
    def update_weight_chart(self) -> None:
        """Update the weight chart using database manager."""
        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        date_from = self.dateEdit_weight_from.date().toString("yyyy-MM-dd")
        date_to = self.dateEdit_weight_to.date().toString("yyyy-MM-dd")

        # Get weight data using database manager
        rows = self.db_manager.get_weight_chart_data(date_from, date_to)

        if not rows:
            self._show_no_data_label(
                self.verticalLayout_weight_chart_content, "No weight data found for the selected period"
            )
            return

        # Parse data - convert to datetime objects for chart
        chart_data = [(datetime.fromisoformat(row[1]).replace(tzinfo=timezone.utc), row[0]) for row in rows]

        # Define custom statistics formatter for weight
        def format_weight_stats(values: list) -> str:
            min_weight = min(values)
            max_weight = max(values)
            avg_weight = sum(values) / len(values)
            weight_change = values[-1] - values[0] if len(values) > 1 else 0

            return (
                f"Min: {min_weight:.1f} kg | Max: {max_weight:.1f} kg | "
                f"Avg: {avg_weight:.1f} kg | Change: {weight_change:+.1f} kg"
            )

        # Create chart configuration
        chart_config = {
            "title": "Weight Progress",
            "xlabel": "Date",
            "ylabel": "Weight (kg)",
            "color": "blue",
            "show_stats": True,
            "stats_unit": "kg",
            "period": "Days",  # Weight chart always shows days
            "stats_formatter": format_weight_stats,
        }

        # Clear existing chart and create new one
        self._clear_layout(self.verticalLayout_weight_chart_content)

        # Create matplotlib figure with custom Y-axis formatting
        fig = Figure(figsize=(12, 6), dpi=100)
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)

        # Extract data
        x_values = [item[0] for item in chart_data]
        y_values = [item[1] for item in chart_data]

        # Plot data
        self._plot_data(ax, x_values, y_values, chart_config.get("color", "b"), period="Days")

        # Customize plot
        ax.set_xlabel(chart_config.get("xlabel", "X"), fontsize=12)
        ax.set_ylabel(chart_config.get("ylabel", "Y"), fontsize=12)
        ax.set_title(chart_config.get("title", "Chart"), fontsize=14, fontweight="bold")
        ax.grid(visible=True, alpha=0.3)

        # Add more detailed Y-axis grid for weight chart
        ax.yaxis.set_major_locator(MultipleLocator(1))  # Major divisions every 1 kg
        ax.yaxis.set_minor_locator(MultipleLocator(0.5))  # Minor divisions every 0.5 kg
        ax.grid(visible=True, which="major", alpha=0.3)  # Major grid
        ax.grid(visible=True, which="minor", alpha=0.1)  # Minor grid (more transparent)

        # Format x-axis dates
        self._format_chart_x_axis(ax, x_values, "Days")

        # Add statistics
        if len(y_values) > 1:
            stats_text = format_weight_stats(y_values)
            self._add_stats_box(ax, stats_text)

        fig.tight_layout()
        self.verticalLayout_weight_chart_content.addWidget(canvas)
        canvas.draw()

    def _add_calories_recommendations_to_label(self) -> None:
        """Add calories recommendations to label_chart_info.

        Shows information about calories burned for current month, last month, and max month.
        """
        if self.db_manager is None:
            self.label_chart_info.setText("")
            return

        # Get current month data
        today = datetime.now(timezone.utc).astimezone()
        current_month = today.month
        current_year = today.year

        # Calculate date ranges for current month
        month_start = today.replace(day=1)
        month_end = today

        # Get calories data for current month
        current_month_calories = self.db_manager.get_kcal_chart_data(
            month_start.strftime("%Y-%m-%d"), month_end.strftime("%Y-%m-%d")
        )
        current_calories = sum(float(calories) for _, calories in current_month_calories)

        # Get calories for today
        calories_today = self.db_manager.get_kcal_today()

        # Get data for last N months (from spinBox_compare_last)
        months_count = self.spinBox_compare_last.value()
        monthly_calories_data = []

        for i in range(months_count):
            # Calculate start and end of month
            # Calculate month i months ago
            month_date = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            for _ in range(i):
                if month_date.month == 1:
                    month_date = month_date.replace(year=month_date.year - 1, month=12)
                else:
                    month_date = month_date.replace(month=month_date.month - 1)
            month_start_i = month_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if i == 0:
                month_end_i = today
            else:
                last_day = calendar.monthrange(month_start_i.year, month_start_i.month)[1]
                month_end_i = month_start_i.replace(day=last_day, hour=23, minute=59, second=59, microsecond=999999)

            # Get calories data for this month
            month_calories = self.db_manager.get_kcal_chart_data(
                month_start_i.strftime("%Y-%m-%d"), month_end_i.strftime("%Y-%m-%d")
            )
            month_total = sum(float(calories) for _, calories in month_calories)
            monthly_calories_data.append(month_total)

        if not monthly_calories_data or all(calories == 0 for calories in monthly_calories_data):
            months_count = self.spinBox_compare_last.value()
            self._set_no_data_info_label(f"No data for the last {months_count} months.")
            return

        # Find max and last month values
        max_calories = max(monthly_calories_data)
        last_month_calories = monthly_calories_data[1] if len(monthly_calories_data) > 1 else 0
        max_month_index = monthly_calories_data.index(max_calories)

        # Calculate remaining days
        days_in_month = calendar.monthrange(current_year, current_month)[1]
        remaining_days = days_in_month - today.day
        total_days_including_current = remaining_days + 1

        # Calculate remaining calories needed
        remaining_to_max = max_calories - current_calories
        remaining_to_last_month = 0
        if last_month_calories > 0:
            remaining_to_last_month = last_month_calories - current_calories

        # Build recommendation text
        recommendation_text = "<b>📊 Calories Goal Recommendations</b><br><br>"
        recommendation_text += f"📈 Current calories this month: <b>{int(current_calories)} kcal</b><br>"

        # Add last month goal information first (only if it's different from max month)
        if last_month_calories > 0 and max_month_index != 1:
            recommendation_text += f"📅 Last month calories: <b>{int(last_month_calories)} kcal</b><br>"
            if remaining_to_last_month > 0:
                recommendation_text += f"📊 Remaining to last month: <b>{int(remaining_to_last_month)} kcal</b><br>"
                if remaining_days > 0:
                    daily_needed_last = remaining_to_last_month / remaining_days
                    daily_needed_last_rounded = int(daily_needed_last) + (1 if daily_needed_last % 1 > 0 else 0)
                    recommendation_text += (
                        f"📅 Needed per day for last month "
                        f"({remaining_days} left): "
                        f"<b>{daily_needed_last_rounded} kcal</b>"
                    )
                else:
                    recommendation_text += "⏰ Month ending - reach last month goal today!"
            else:
                recommendation_text += "🎉 Last month goal already achieved!"
            recommendation_text += "<br>"

        # Add max goal information second
        recommendation_text += f"🎯 Max calories over last {months_count} months: <b>{int(max_calories)} kcal</b><br>"
        if remaining_to_max > 0:
            recommendation_text += f"⬆️ Remaining to max: <b>{int(remaining_to_max)} kcal</b><br>"

            # Add daily goal including current day (second to last)
            if total_days_including_current > 0:
                # Calculate daily needed based on remaining amount
                daily_needed_including_current = remaining_to_max / total_days_including_current
                daily_needed_including_current_rounded = int(daily_needed_including_current) + (
                    1 if daily_needed_including_current % 1 > 0 else 0
                )
                recommendation_text += (
                    f"📊 Needed per day including today "
                    f"({total_days_including_current} days total): "
                    f"<b>{daily_needed_including_current_rounded} kcal</b><br>"
                )

                # Add remaining for today calculation
                remaining_for_today = daily_needed_including_current_rounded - calories_today
                if remaining_for_today > 0:
                    recommendation_text += f"🔥 Still needed today: <b>{int(remaining_for_today)} kcal</b><br>"
                else:
                    recommendation_text += f"✅ Today's goal achieved! (burned {int(calories_today)} kcal)<br>"

            # Add daily goal for max (last)
            if remaining_days > 0:
                daily_needed_max = remaining_to_max / remaining_days
                daily_needed_max_rounded = int(daily_needed_max) + (1 if daily_needed_max % 1 > 0 else 0)
                recommendation_text += (
                    f"📅 Needed per day for max ({remaining_days} left): <b>{daily_needed_max_rounded} kcal</b>"
                )
            else:
                recommendation_text += "⏰ Month ending - reach max goal today!"
        else:
            recommendation_text += "🎉 Max goal already achieved!"

        # Set text
        self.label_chart_info.setText(recommendation_text)
        self.label_chart_info.setStyleSheet("""
            margin: 5px 0px;
            padding: 10px;
            background-color: #F8F9FA;
            border: 1px solid #E9ECEF;
            border-radius: 5px;
            font-size: 13px;
            line-height: 1.2;
        """)

    def _add_exercise_recommendations_to_label(
        self, exercise: str, exercise_type: str | None, monthly_data: list, months_count: int, exercise_unit: str
    ) -> None:
        """Add exercise recommendations to label_chart_info.

        Args:

        - `exercise` (`str`): Name of the selected exercise.
        - `exercise_type` (`str | None`): Type of the exercise or None.
        - `monthly_data` (`list`): List of monthly data from on_compare_last_months.
        - `months_count` (`int`): Number of months to compare.
        - `exercise_unit` (`str`): Unit of measurement.

        """
        if not monthly_data:
            months_count = self.spinBox_compare_last.value()
            self._set_no_data_info_label(f"No data for the last {months_count} months.")
            return

        # Find the maximum final value from all months and last month value
        max_value = 0.0
        last_month_value = 0.0
        max_month_index = 0
        for i, month_data in enumerate(monthly_data):
            if month_data:
                # Get the last (final) value from each month's data
                final_value = month_data[-1][1]  # (day, cumulative_value)
                if final_value > max_value:
                    max_value = final_value
                    max_month_index = i
                # Last month is the second item (index 1) if it exists
                if i == 1:
                    last_month_value = final_value

        if max_value <= 0 and not any(month_data for month_data in monthly_data):
            months_count = self.spinBox_compare_last.value()
            self._set_no_data_info_label(f"No data for the last {months_count} months.")
            return

        # Get current month progress
        today = datetime.now(timezone.utc).astimezone()
        current_month_data = monthly_data[0] if monthly_data else []  # First item is current month
        current_progress = current_month_data[-1][1] if current_month_data else 0.0

        # Get today's progress for this specific exercise
        # We need to get the exercise ID first
        exercise_id = None
        if self.db_manager:
            exercise_id = self.db_manager.get_id("exercises", "name", exercise)

        today_progress = 0.0
        if exercise_id:
            # For exercises with types, we need to filter by type
            if exercise_type and exercise_type != "All types":
                # Get today's data for this specific exercise and type
                today_data = self.db_manager.get_exercise_chart_data(
                    exercise_name=exercise,
                    exercise_type=exercise_type,
                    date_from=today.strftime("%Y-%m-%d"),
                    date_to=today.strftime("%Y-%m-%d"),
                )
                today_progress = sum(float(value) for _, value in today_data)
            else:
                today_progress = self.db_manager.get_exercise_total_today(exercise_id)

        # Calculate how much more is needed to reach the max value
        remaining_to_max = max_value - current_progress

        # Calculate how much more is needed to reach the last month value
        remaining_to_last_month = 0.0
        if last_month_value > 0:
            remaining_to_last_month = last_month_value - current_progress

        # Calculate remaining days in current month
        current_month = today.month
        current_year = today.year
        days_in_month = calendar.monthrange(current_year, current_month)[1]
        remaining_days = days_in_month - today.day

        # Calculate total days including current day
        total_days_including_current = remaining_days + 1

        # Get unit
        unit_text = f" {exercise_unit}" if exercise_unit else ""

        # Build recommendation text with integer values
        recommendation_text = "<b>📊 Exercise Goal Recommendations</b><br><br>"
        recommendation_text += f"📈 Current progress: <b>{int(current_progress)}{unit_text}</b><br>"

        # Add last month goal information first (only if it's different from max month)
        if last_month_value > 0 and max_month_index != 1:
            recommendation_text += f"📅 Last month result: <b>{int(last_month_value)}{unit_text}</b><br>"
            if remaining_to_last_month > 0:
                recommendation_text += (
                    f"📊 Remaining to last month: <b>{int(remaining_to_last_month)}{unit_text}</b><br>"
                )
                if remaining_days > 0:
                    daily_needed_last = remaining_to_last_month / remaining_days
                    daily_needed_last_rounded = int(daily_needed_last) + (
                        1 if daily_needed_last % 1 > 0 else 0
                    )  # Round up to integer
                    recommendation_text += (
                        f"📅 Needed per day for last month "
                        f"({remaining_days} left): "
                        f"<b>{daily_needed_last_rounded}{unit_text}</b>"
                    )
                else:
                    recommendation_text += "⏰ Month ending - reach last month goal today!"
            else:
                recommendation_text += "🎉 Last month goal already achieved!"
            recommendation_text += "<br>"

        # Add max goal information second
        recommendation_text += f"🎯 Max over last {months_count} months: <b>{int(max_value)}{unit_text}</b><br>"
        if remaining_to_max > 0:
            recommendation_text += f"⬆️ Remaining to max: <b>{int(remaining_to_max)}{unit_text}</b><br>"

            # Add daily goal including current day (second to last)
            if total_days_including_current > 0:
                # Calculate daily needed based on remaining amount
                daily_needed_including_current = remaining_to_max / total_days_including_current
                daily_needed_including_current_rounded = int(daily_needed_including_current) + (
                    1 if daily_needed_including_current % 1 > 0 else 0
                )  # Round up to integer
                recommendation_text += (
                    f"📊 Needed per day including today "
                    f"({total_days_including_current} days total): "
                    f"<b>{daily_needed_including_current_rounded}{unit_text}</b><br>"
                )

                # Add remaining for today calculation
                remaining_for_today = daily_needed_including_current_rounded - today_progress
                if remaining_for_today > 0:
                    recommendation_text += f"🔥 Still needed today: <b>{int(remaining_for_today)}{unit_text}</b><br>"
                else:
                    recommendation_text += f"✅ Today's goal achieved! (completed {int(today_progress)}{unit_text})<br>"

            # Add daily goal for max (last)
            if remaining_days > 0:
                daily_needed_max = remaining_to_max / remaining_days
                daily_needed_max_rounded = int(daily_needed_max) + (
                    1 if daily_needed_max % 1 > 0 else 0
                )  # Round up to integer
                recommendation_text += (
                    f"📅 Needed per day for max ({remaining_days} left): <b>{daily_needed_max_rounded}{unit_text}</b>"
                )
            else:
                recommendation_text += "⏰ Month ending - reach max goal today!"
        else:
            recommendation_text += "🎉 Max goal already achieved!"

        # Set text
        self.label_chart_info.setText(recommendation_text)
        self.label_chart_info.setStyleSheet("""
            margin: 5px 0px;
            padding: 10px;
            background-color: #F8F9FA;
            border: 1px solid #E9ECEF;
            border-radius: 5px;
            font-size: 13px;
            line-height: 1.2;
        """)

    def _add_exercise_recommendations_to_label_for_standard_chart(
        self, exercise: str, exercise_type: str | None, exercise_unit: str
    ) -> None:
        """Add exercise recommendations to label_chart_info for standard chart.

        Uses the same logic as compare_last but for the selected exercise.

        Args:

        - `exercise` (`str`): Name of the exercise.
        - `exercise_type` (`str | None`): Type of the exercise or None.
        - `exercise_unit` (`str`): Unit of measurement.

        """
        if self.db_manager is None:
            self.label_chart_info.setText("")
            return

        # Get data for last N months (from spinBox_compare_last) in the same format as compare_last
        months_count = self.spinBox_compare_last.value()
        monthly_data = []

        today = datetime.now(timezone.utc).astimezone()

        for i in range(months_count):
            # Calculate start and end of month
            # Calculate month i months ago
            month_date = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            for _ in range(i):
                if month_date.month == 1:
                    month_date = month_date.replace(year=month_date.year - 1, month=12)
                else:
                    month_date = month_date.replace(month=month_date.month - 1)
            month_start_i = month_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if i == 0:
                month_end_i = today
            else:
                last_day = calendar.monthrange(month_start_i.year, month_start_i.month)[1]
                month_end_i = month_start_i.replace(day=last_day, hour=23, minute=59, second=59, microsecond=999999)

            # Get exercise data for this month
            month_data = self.db_manager.get_exercise_chart_data(
                exercise_name=exercise,
                exercise_type=exercise_type if exercise_type != "All types" else None,
                date_from=month_start_i.strftime("%Y-%m-%d"),
                date_to=month_end_i.strftime("%Y-%m-%d"),
            )

            # Convert to cumulative data format like in compare_last
            cumulative_data = []
            cumulative_value = 0.0
            for date_str, value_str in month_data:
                cumulative_value += float(value_str)
                # Convert date to day number in month using datetime
                day = datetime.fromisoformat(date_str).day
                cumulative_data.append((day, cumulative_value))

            monthly_data.append(cumulative_data)

        # Use the existing function with the same data format
        self._add_exercise_recommendations_to_label(exercise, exercise_type, monthly_data, months_count, exercise_unit)

    def _add_one_day_to_main(self) -> None:
        """Add one day to the current date in main date field."""
        current_date = self.dateEdit.date()
        new_date = current_date.addDays(1)
        self.dateEdit.setDate(new_date)

    def _add_same_months_recommendations_to_label(
        self, exercise: str, exercise_type: str | None, exercise_unit: str, yearly_data: list, years_count: int
    ) -> None:
        """Add same months recommendations to label_chart_info.

        Shows information about exercise progress for the same month across different years.

        Args:

        - `exercise` (`str`): Name of the exercise.
        - `exercise_type` (`str | None`): Type of the exercise or None.
        - `exercise_unit` (`str`): Unit of measurement.
        - `yearly_data` (`list`): List of yearly data.
        - `years_count` (`int`): Number of years to compare.

        """
        if not yearly_data:
            self.label_chart_info.setText("")
            return

        # Find the maximum final value from all years and last year value
        max_value = 0.0
        last_year_value = 0.0
        max_year_index = 0
        current_year_value = 0.0

        for i, year_data in enumerate(yearly_data):
            if year_data:
                # Get the last (final) value from each year's data
                final_value = year_data[-1][1]  # (day, cumulative_value)
                if final_value > max_value:
                    max_value = final_value
                    max_year_index = i
                # Last year is the second item (index 1) if it exists
                if i == 1:
                    last_year_value = final_value
                # Current year is the first item (index 0)
                if i == 0:
                    current_year_value = final_value

        if max_value <= 0:
            years_count = self.spinBox_compare_last.value()
            selected_month_name = self.comboBox_compare_same_months.currentText()
            self._set_no_data_info_label(f"No data for {selected_month_name.lower()} in the last {years_count} years.")
            return

        # Get current progress (current year value)
        current_progress = current_year_value

        # Get today's progress for this specific exercise
        # We need to get the exercise ID first
        exercise_id = None
        if self.db_manager:
            exercise_id = self.db_manager.get_id("exercises", "name", exercise)

        today_progress = 0.0
        if exercise_id:
            # For exercises with types, we need to filter by type
            if exercise_type and exercise_type != "All types":
                # Get today's date
                today = datetime.now(timezone.utc).astimezone()
                # Get today's data for this specific exercise and type
                today_data = self.db_manager.get_exercise_chart_data(
                    exercise_name=exercise,
                    exercise_type=exercise_type,
                    date_from=today.strftime("%Y-%m-%d"),
                    date_to=today.strftime("%Y-%m-%d"),
                )
                today_progress = sum(float(value) for _, value in today_data)
            else:
                today_progress = self.db_manager.get_exercise_total_today(exercise_id)

        # Calculate remaining days in current month
        today = datetime.now(timezone.utc).astimezone()
        current_month = today.month
        current_year = today.year
        days_in_month = calendar.monthrange(current_year, current_month)[1]
        remaining_days = days_in_month - today.day
        total_days_including_current = remaining_days + 1

        # Calculate how much more is needed to reach the max value
        remaining_to_max = max_value - current_progress

        # Calculate how much more is needed to reach the last year value
        remaining_to_last_year = 0.0
        if last_year_value > 0:
            remaining_to_last_year = last_year_value - current_progress

        # Get unit
        unit_text = f" {exercise_unit}" if exercise_unit else ""

        # Get selected month name
        selected_month_name = self.comboBox_compare_same_months.currentText()

        # Build recommendation text with integer values
        recommendation_text = f"<b>📊 {selected_month_name} Goal Recommendations</b><br><br>"
        recommendation_text += (
            f"📈 Current {selected_month_name.lower()} progress: <b>{int(current_progress)}{unit_text}</b><br>"
        )

        # Add last year goal information first (only if it's different from max year)
        if last_year_value > 0 and max_year_index != 1:
            recommendation_text += (
                f"📅 Last year {selected_month_name.lower()}: <b>{int(last_year_value)}{unit_text}</b><br>"
            )
            if remaining_to_last_year > 0:
                recommendation_text += f"📊 Remaining to last year: <b>{int(remaining_to_last_year)}{unit_text}</b><br>"
                if remaining_days > 0:
                    daily_needed_last = remaining_to_last_year / remaining_days
                    daily_needed_last_rounded = int(daily_needed_last) + (
                        1 if daily_needed_last % 1 > 0 else 0
                    )  # Round up to integer
                    recommendation_text += (
                        f"📅 Needed per day for last year ({remaining_days} left): "
                        f"<b>{daily_needed_last_rounded}{unit_text}</b>"
                    )
                else:
                    recommendation_text += "⏰ Month ending - reach last year goal today!"
            else:
                recommendation_text += "🎉 Last year goal already achieved!"
            recommendation_text += "<br>"

        # Add max goal information second
        recommendation_text += (
            f"🎯 Max {selected_month_name.lower()} over last {years_count} years: "
            f"<b>{int(max_value)}{unit_text}</b><br>"
        )
        if remaining_to_max > 0:
            recommendation_text += f"⬆️ Remaining to max: <b>{int(remaining_to_max)}{unit_text}</b><br>"

            # Add daily goal including current day (second to last)
            if total_days_including_current > 0:
                # Calculate daily needed based on remaining amount
                daily_needed_including_current = remaining_to_max / total_days_including_current
                daily_needed_including_current_rounded = int(daily_needed_including_current) + (
                    1 if daily_needed_including_current % 1 > 0 else 0
                )  # Round up to integer
                recommendation_text += (
                    f"📊 Needed per day including today "
                    f"({total_days_including_current} days total): "
                    f"<b>{daily_needed_including_current_rounded}{unit_text}</b><br>"
                )

                # Add remaining for today calculation
                remaining_for_today = daily_needed_including_current_rounded - today_progress
                if remaining_for_today > 0:
                    recommendation_text += f"🔥 Still needed today: <b>{int(remaining_for_today)}{unit_text}</b><br>"
                else:
                    recommendation_text += f"✅ Today's goal achieved! (completed {int(today_progress)}{unit_text})<br>"

            # Add daily goal for max (last)
            if remaining_days > 0:
                daily_needed_max = remaining_to_max / remaining_days
                daily_needed_max_rounded = int(daily_needed_max) + (
                    1 if daily_needed_max % 1 > 0 else 0
                )  # Round up to integer
                recommendation_text += (
                    f"📅 Needed per day for max ({remaining_days} left): <b>{daily_needed_max_rounded}{unit_text}</b>"
                )
            else:
                recommendation_text += "⏰ Month ending - reach max goal today!"
        else:
            recommendation_text += "🎉 Max goal already achieved!"

        # Set text
        self.label_chart_info.setText(recommendation_text)
        self.label_chart_info.setStyleSheet("""
            margin: 5px 0px;
            padding: 10px;
            background-color: #F8F9FA;
            border: 1px solid #E9ECEF;
            border-radius: 5px;
            font-size: 13px;
            line-height: 1.2;
        """)

    def _add_sets_recommendations_to_label(self) -> None:
        """Add sets recommendations to label_chart_info.

        Shows information about sets count for current month, last month, and max month.
        """
        if self.db_manager is None:
            self.label_chart_info.setText("")
            return

        # Get current month data
        today = datetime.now(timezone.utc).astimezone()
        current_month = today.month
        current_year = today.year

        # Calculate date ranges for current month
        month_start = today.replace(day=1)
        month_end = today

        # Get sets data for current month
        current_month_sets = self.db_manager.get_sets_chart_data(
            month_start.strftime("%Y-%m-%d"), month_end.strftime("%Y-%m-%d")
        )
        current_sets = sum(int(count) for _, count in current_month_sets)

        # Get sets count for today
        sets_today = self.db_manager.get_sets_count_today()

        # Get data for last N months (from spinBox_compare_last)
        months_count = self.spinBox_compare_last.value()
        monthly_sets_data = []

        for i in range(months_count):
            # Calculate start and end of month
            # Calculate month i months ago
            month_date = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            for _ in range(i):
                if month_date.month == 1:
                    month_date = month_date.replace(year=month_date.year - 1, month=12)
                else:
                    month_date = month_date.replace(month=month_date.month - 1)
            month_start_i = month_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if i == 0:
                month_end_i = today
            else:
                last_day = calendar.monthrange(month_start_i.year, month_start_i.month)[1]
                month_end_i = month_start_i.replace(day=last_day, hour=23, minute=59, second=59, microsecond=999999)

            # Get sets data for this month
            month_sets = self.db_manager.get_sets_chart_data(
                month_start_i.strftime("%Y-%m-%d"), month_end_i.strftime("%Y-%m-%d")
            )
            month_total = sum(int(count) for _, count in month_sets)
            monthly_sets_data.append(month_total)

        if not monthly_sets_data or all(sets == 0 for sets in monthly_sets_data):
            months_count = self.spinBox_compare_last.value()
            self._set_no_data_info_label(f"No data for the last {months_count} months.")
            return

        # Find max and last month values
        max_sets = max(monthly_sets_data)
        last_month_sets = monthly_sets_data[1] if len(monthly_sets_data) > 1 else 0
        max_month_index = monthly_sets_data.index(max_sets)

        # Calculate remaining days
        days_in_month = calendar.monthrange(current_year, current_month)[1]
        remaining_days = days_in_month - today.day
        total_days_including_current = remaining_days + 1

        # Calculate remaining sets needed
        remaining_to_max = max_sets - current_sets
        remaining_to_last_month = 0
        if last_month_sets > 0:
            remaining_to_last_month = last_month_sets - current_sets

        # Build recommendation text
        recommendation_text = "<b>📊 Sets Goal Recommendations</b><br><br>"
        recommendation_text += f"📈 Current sets this month: <b>{current_sets}</b><br>"

        # Add last month goal information first (only if it's different from max month)
        if last_month_sets > 0 and max_month_index != 1:
            recommendation_text += f"📅 Last month sets: <b>{last_month_sets}</b><br>"
            if remaining_to_last_month > 0:
                recommendation_text += f"📊 Remaining to last month: <b>{remaining_to_last_month}</b><br>"
                if remaining_days > 0:
                    daily_needed_last = remaining_to_last_month / remaining_days
                    daily_needed_last_rounded = int(daily_needed_last) + (1 if daily_needed_last % 1 > 0 else 0)
                    recommendation_text += (
                        f"📅 Needed per day for last month ({remaining_days} left): <b>{daily_needed_last_rounded}</b>"
                    )
                else:
                    recommendation_text += "⏰ Month ending - reach last month goal today!"
            else:
                recommendation_text += "🎉 Last month goal already achieved!"
            recommendation_text += "<br>"

        # Add max goal information second
        recommendation_text += f"🎯 Max sets over last {months_count} months: <b>{max_sets}</b><br>"
        if remaining_to_max > 0:
            recommendation_text += f"⬆️ Remaining to max: <b>{remaining_to_max}</b><br>"

            # Add daily goal including current day (second to last)
            if total_days_including_current > 0:
                # Calculate daily needed based on remaining amount
                daily_needed_including_current = remaining_to_max / total_days_including_current
                daily_needed_including_current_rounded = int(daily_needed_including_current) + (
                    1 if daily_needed_including_current % 1 > 0 else 0
                )
                recommendation_text += (
                    f"📊 Needed per day including today "
                    f"({total_days_including_current} days total): "
                    f"<b>{daily_needed_including_current_rounded}</b><br>"
                )

                # Add remaining for today calculation
                remaining_for_today = daily_needed_including_current_rounded - sets_today
                if remaining_for_today > 0:
                    recommendation_text += f"🔥 Still needed today: <b>{int(remaining_for_today)} sets</b><br>"
                else:
                    recommendation_text += f"✅ Today's goal achieved! (completed {int(sets_today)} sets)<br>"

            # Add daily goal for max (last)
            if remaining_days > 0:
                daily_needed_max = remaining_to_max / remaining_days
                daily_needed_max_rounded = int(daily_needed_max) + (1 if daily_needed_max % 1 > 0 else 0)
                recommendation_text += (
                    f"📅 Needed per day for max ({remaining_days} left): <b>{daily_needed_max_rounded}</b>"
                )
            else:
                recommendation_text += "⏰ Month ending - reach max goal today!"
        else:
            recommendation_text += "🎉 Max goal already achieved!"

        # Set text
        self.label_chart_info.setText(recommendation_text)
        self.label_chart_info.setStyleSheet("""
            margin: 5px 0px;
            padding: 10px;
            background-color: #F8F9FA;
            border: 1px solid #E9ECEF;
            border-radius: 5px;
            font-size: 13px;
            line-height: 1.2;
        """)

    def _adjust_process_table_columns(self) -> None:
        """Adjust process table column widths proportionally to window size."""
        if not hasattr(self, "tableView_process") or not self.tableView_process.model():
            return

        # Get current table width
        table_width = self.tableView_process.width()
        if table_width <= 0:
            # Fallback to window width if table width is not available
            table_width = self.width() * 0.7  # Assume table takes ~70% of window width

        # Ensure minimum table width for better appearance
        table_width = max(table_width, 800)

        # Reserve space for vertical headers, scrollbar, and borders
        vertical_header_width = self.tableView_process.verticalHeader().width()
        scrollbar_width = 20  # Approximate scrollbar width
        borders_and_margins = 10  # Space for borders and margins

        available_width = table_width - vertical_header_width - scrollbar_width - borders_and_margins

        # Define proportional distribution of available width
        # Total: 100% = 40% + 25% + 20% + 15%
        proportions = [0.40, 0.25, 0.20, 0.15]  # Exercise, Exercise Type, Quantity, Date

        # Calculate widths based on proportions of available width
        column_widths = [int(available_width * prop) for prop in proportions]

        # Apply widths to all columns
        for i, width in enumerate(column_widths):
            self.tableView_process.setColumnWidth(i, width)

    def _calculate_exercise_recommendations(
        self, _exercise_name: str, monthly_data: list, _months_count: int, _exercise_unit: str
    ) -> dict:
        """Calculate exercise recommendations based on monthly data.

        Args:

        - `_exercise_name` (`str`): Name of the exercise.
        - `monthly_data` (`list`): Monthly data from _get_monthly_data_for_exercise.
        - `_months_count` (`int`): Number of months analyzed.
        - `_exercise_unit` (`str`): Unit of measurement.

        Returns:

        - `dict`: Dictionary containing all recommendation values.

        """
        # Find the maximum final value from all months and last month value
        max_value = 0.0
        last_month_value = 0.0

        for i, month_data in enumerate(monthly_data):
            if month_data:
                final_value = month_data[-1][1]
                max_value = max(max_value, final_value)
                # Last month is the second item (index 1) if it exists
                if i == 1:
                    last_month_value = final_value

        # Get current month progress
        today = datetime.now(timezone.utc).astimezone()
        current_month_data = monthly_data[0] if monthly_data else []
        current_progress = current_month_data[-1][1] if current_month_data else 0.0

        # Calculate remaining amounts
        remaining_to_max = max(0, max_value - current_progress)
        remaining_to_last_month = max(0, last_month_value - current_progress) if last_month_value > 0 else 0

        # Calculate remaining days in current month
        current_month = today.month
        current_year = today.year
        days_in_month = calendar.monthrange(current_year, current_month)[1]
        remaining_days = days_in_month - today.day

        # Calculate daily needed amounts
        daily_needed_max = (
            int(remaining_to_max / remaining_days) + (1 if remaining_to_max % remaining_days > 0 else 0)
            if remaining_days > 0
            else 0
        )
        daily_needed_last_month = (
            int(remaining_to_last_month / remaining_days) + (1 if remaining_to_last_month % remaining_days > 0 else 0)
            if remaining_days > 0
            else 0
        )

        return {
            "current_progress": current_progress,
            "last_month_value": last_month_value,
            "max_value": max_value,
            "remaining_to_last_month": remaining_to_last_month,
            "remaining_to_max": remaining_to_max,
            "daily_needed_last_month": daily_needed_last_month,
            "daily_needed_max": daily_needed_max,
        }

    def _check_for_new_records(self, ex_id: int, type_id: int, current_value: float, type_name: str) -> dict | None:
        """Check if the current value would be a new all-time or yearly record.

        Args:

        - `ex_id` (`int`): Exercise ID.
        - `type_id` (`int`): Type ID.
        - `current_value` (`float`): Current value to check.
        - `type_name` (`str`): Type name.

        Returns:

        - `dict | None`: Record information if new record is found, None otherwise.

        """
        if not self._validate_database_connection() or self.db_manager is None:
            return None

        try:
            # Calculate date one year ago
            one_year_ago = datetime.now(timezone.utc).astimezone() - timedelta(days=365)
            one_year_ago_str = one_year_ago.strftime("%Y-%m-%d")

            # Use database manager method
            all_time_max, yearly_max = self.db_manager.get_exercise_max_values(ex_id, type_id, one_year_ago_str)

            # Check for new records
            is_all_time_record = current_value > all_time_max
            is_yearly_record = current_value > yearly_max and not is_all_time_record

            if is_all_time_record or is_yearly_record:
                return {
                    "is_all_time": is_all_time_record,
                    "is_yearly": is_yearly_record,
                    "current_value": current_value,
                    "previous_all_time": all_time_max,
                    "previous_yearly": yearly_max,
                    "type_name": type_name,
                }
        except Exception as e:
            print(f"Error checking for new records: {e}")
            # Don't show error to user for first-time records, just return None

        return None

    def _connect_signals(self) -> None:
        """Wire Qt widgets to their Python slots.

        Connects all UI elements to their respective handler methods, including:

        - Button click events for adding and deleting records
        - Tab change events
        - Statistics and export functionality
        - Auto-save signals for table data changes
        """
        self.pushButton_add.clicked.connect(self.on_add_record)
        self.spinBox_count.lineEdit().returnPressed.connect(self.pushButton_add.click)

        # Connect window resize event for automatic column resizing
        self.resizeEvent = self._on_window_resize

        # Connect delete and refresh buttons for all tables (except statistics)
        tables_with_controls = {"process", "exercises", "types", "weight"}
        for table_name in tables_with_controls:
            # Delete buttons
            delete_btn_name = "pushButton_delete" if table_name == "process" else f"pushButton_{table_name}_delete"
            delete_button = getattr(self, delete_btn_name)
            delete_button.clicked.connect(partial(self.delete_record, table_name))

            # Refresh buttons
            refresh_btn_name = "pushButton_refresh" if table_name == "process" else f"pushButton_{table_name}_refresh"
            refresh_button = getattr(self, refresh_btn_name)
            refresh_button.clicked.connect(self.update_all)

        # Connect process table selection change signal
        # Note: This will be connected later in show_tables() after model is created

        # Add buttons
        self.pushButton_exercise_add.clicked.connect(self.on_add_exercise)
        self.pushButton_type_add.clicked.connect(self.on_add_type)
        self.pushButton_weight_add.clicked.connect(self.on_add_weight)
        self.pushButton_yesterday.clicked.connect(self.set_yesterday_date)
        self.pushButton_select_exercise.clicked.connect(self.on_select_exercise_button_clicked)

        # Add context menu for yesterday button
        self.pushButton_yesterday.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.pushButton_yesterday.customContextMenuRequested.connect(self._show_yesterday_context_menu)

        # Stats & export
        self.pushButton_statistics_refresh.clicked.connect(self.on_refresh_statistics)
        self.pushButton_last_exercises.clicked.connect(self.on_show_last_exercises)
        self.pushButton_check_steps.clicked.connect(self.on_check_steps)
        self.pushButton_export_csv.clicked.connect(self.on_export_csv)
        self.pushButton_show_all_records.clicked.connect(self.on_toggle_show_all_records)
        self.pushButton_exercise_goal_recommendations.clicked.connect(self.on_show_exercise_goal_recommendations)

        # Tab change
        self.tabWidget.currentChanged.connect(self.on_tab_changed)

        # Weight chart signals
        self.pushButton_update_weight_chart.clicked.connect(self.update_weight_chart)
        self.pushButton_weight_last_month.clicked.connect(self.set_weight_last_month)
        self.pushButton_weight_last_year.clicked.connect(self.set_weight_last_year)
        self.pushButton_weight_all_time.clicked.connect(self.set_weight_all_time)

        # Exercise chart signals - only one update button now
        self.pushButton_update_chart.clicked.connect(self._update_chart_based_on_radio_button)
        self.pushButton_chart_last_month.clicked.connect(self.set_chart_last_month)
        self.pushButton_chart_last_year.clicked.connect(self.set_chart_last_year)
        self.pushButton_chart_all_time.clicked.connect(self.set_chart_all_time)

        # Radio button signals for chart type selection
        self.radioButton_type_of_chart_standart.toggled.connect(self.on_radio_button_changed)
        self.radioButton_type_of_chart_show_sets_chart.toggled.connect(self.on_radio_button_changed)
        self.radioButton_type_of_chart_kcal.toggled.connect(self.on_radio_button_changed)
        self.radioButton_type_of_chart_compare_last.toggled.connect(self.on_radio_button_changed)
        self.radioButton_type_of_chart_compare_same_months.toggled.connect(self.on_radio_button_changed)

        # Filter signals
        self.comboBox_filter_exercise.currentIndexChanged.connect(self.update_filter_type_combobox)
        self.pushButton_apply_filter.clicked.connect(self.apply_filter)
        self.pushButton_clear_filter.clicked.connect(self.clear_filter)

        # Exercise name combobox for types
        self.comboBox_exercise_name.currentIndexChanged.connect(self.on_exercise_name_changed)

        # Exercise type combobox for statistics sync
        self.comboBox_type.currentIndexChanged.connect(self.on_exercise_type_changed)

        # Statistics exercise combobox
        self.comboBox_records_select_exercise.currentIndexChanged.connect(self.update_statistics_exercise_combobox)
        self.comboBox_records_select_exercise.currentIndexChanged.connect(self._update_statistics_avif)
        self.comboBox_records_select_exercise.currentIndexChanged.connect(self.on_statistics_exercise_combobox_changed)

        # Connect double-click signal for exercises list to open statistics tab
        self.listView_exercises.doubleClicked.connect(self._on_exercises_list_double_clicked)

        # Connect double-click signal for chart exercise list to open Sets tab
        self.listView_chart_exercise.doubleClicked.connect(self._on_chart_exercise_list_double_clicked)

        # Add context menu for process table
        self.tableView_process.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tableView_process.customContextMenuRequested.connect(self._show_process_context_menu)

        # Add context menu for statistics table
        self.tableView_statistics.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tableView_statistics.customContextMenuRequested.connect(self._show_statistics_context_menu)

        # Add context menu for exercises table
        self.tableView_exercises.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

        # Add double-click handler for chart info label to copy text to clipboard
        self.label_chart_info.mouseDoubleClickEvent = self._on_chart_info_double_clicked
        self.tableView_exercises.customContextMenuRequested.connect(self._show_exercises_context_menu)

        # Add context menu for exercise types table
        self.tableView_exercise_types.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tableView_exercise_types.customContextMenuRequested.connect(self._show_exercise_types_context_menu)

        # Add context menu for weight table
        self.tableView_weight.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tableView_weight.customContextMenuRequested.connect(self._show_weight_context_menu)

    def _connect_table_auto_save_signals(self) -> None:
        """Connect dataChanged signals for auto-save functionality.

        This method should be called after models are created and set to table views.
        """
        # Connect auto-save signals for each table
        for table_name in self._SAFE_TABLES:
            if self.models[table_name] is not None:
                # Use partial to properly bind table_name
                handler = partial(self._on_table_data_changed, table_name)
                model = self.models[table_name]
                if model is not None and hasattr(model, "sourceModel") and model.sourceModel() is not None:
                    model.sourceModel().dataChanged.connect(handler)

    def _connect_table_selection_signals(self) -> None:
        """Connect selection change signals for all tables."""
        # Connect exercises table selection
        self._connect_table_signals_for_table("exercises", self.on_exercise_selection_changed)

        # Connect exercise types table selection
        self._connect_table_signals_for_table("types", self.on_exercise_type_selection_changed)

        # Connect statistics table selection
        selection_model = self.tableView_statistics.selectionModel()
        if selection_model:
            selection_model.currentRowChanged.connect(self.on_statistics_selection_changed)

        # Connect process table selection
        self._connect_table_signals_for_table("process", self.on_process_selection_changed)

        # Connect weight table selection
        self._connect_table_signals_for_table("weight", self.on_weight_selection_changed)

    def _connect_table_signals_for_table(self, table_name: str, selection_handler: Callable) -> None:
        """Connect selection change signal for a specific table.

        Args:

        - `table_name` (`str`): Name of the table.
        - `selection_handler` (`Callable`): Handler function for selection changes.

        """
        if table_name in self.table_config:
            view = self.table_config[table_name][0]
            selection_model = view.selectionModel()
            if selection_model:
                selection_model.currentRowChanged.connect(selection_handler)

    def _copy_table_selection_to_clipboard(self, table_view: QTableView) -> None:
        """Copy selected cells from table to clipboard as tab-separated text.

        Args:

        - `table_view` (`QTableView`): The table view to copy data from.

        """
        selection_model = table_view.selectionModel()
        if not selection_model or not selection_model.hasSelection():
            return

        # Get selected indexes and sort them by row and column
        selected_indexes = selection_model.selectedIndexes()
        if not selected_indexes:
            return

        # Sort indexes by row first, then by column
        selected_indexes.sort(key=lambda index: (index.row(), index.column()))

        # Group indexes by row
        rows_data = {}
        for index in selected_indexes:
            row = index.row()
            if row not in rows_data:
                rows_data[row] = {}

            # Get cell data
            cell_data = table_view.model().data(index, Qt.ItemDataRole.DisplayRole)
            rows_data[row][index.column()] = str(cell_data) if cell_data is not None else ""

        # Build clipboard text
        clipboard_text = []
        for row in sorted(rows_data.keys()):
            row_data = rows_data[row]
            # Get all columns for this row and fill missing ones with empty strings
            if row_data:
                min_col = min(row_data.keys())
                max_col = max(row_data.keys())
                clipboard_text.append("\t".join([row_data.get(col, "") for col in range(min_col, max_col + 1)]))

        # Copy to clipboard
        if clipboard_text:
            final_text = "\n".join(clipboard_text)
            clipboard = QApplication.clipboard()
            clipboard.setText(final_text)
            print(f"Copied {len(clipboard_text)} rows to clipboard")

    def _create_colored_process_table_model(
        self,
        data: list[list],
        headers: list[str],
        _id_column: int = 4,  # ID is now at index 4 in transformed data
    ) -> QSortFilterProxyModel:
        """Return a proxy model filled with colored process data.

        Args:

        - `data` (`list[list]`): The table data with color information.
        - `headers` (`list[str]`): Column header names.
        - `_id_column` (`int`): Index of the ID column. Defaults to `4`.

        Returns:

        - `QSortFilterProxyModel`: A filterable and sortable model with colored data.

        """
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(headers)

        for row_idx, row in enumerate(data):
            # Extract color information (last element) and ID
            row_color = row[5]  # Color is at index 5
            row_id = row[4]  # ID is at index 4

            # Create items for display columns only (first 4 elements)
            items = []
            for col_idx, value in enumerate(row[:4]):  # Only first 4 elements for display
                item = QStandardItem(str(value) if value is not None else "")

                # Set background color for the item
                item.setBackground(QBrush(row_color))

                # Check if this is today's record and make it bold
                today = QDateTime.currentDateTime().toString("yyyy-MM-dd")
                id_col_date = 3
                if col_idx == id_col_date and str(value) == today:  # Date column
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)

                items.append(item)

            model.appendRow(items)

            # Set the ID in vertical header
            model.setVerticalHeaderItem(
                row_idx,
                QStandardItem(str(row_id)),
            )

        proxy = QSortFilterProxyModel()
        proxy.setSourceModel(model)
        return proxy

    def _create_colored_table_model(
        self,
        data: list[list],
        headers: list[str],
        id_column: int = -2,
    ) -> QSortFilterProxyModel:
        """Return a proxy model filled with colored table data.

        Args:

        - `data` (`list[list]`): The table data with color information.
        - `headers` (`list[str]`): Column header names.
        - `id_column` (`int`): Index of the ID column. Defaults to `-2` (second-to-last).

        Returns:

        - `QSortFilterProxyModel`: A filterable and sortable model with colored data.

        """
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(headers)

        for row_idx, row in enumerate(data):
            # Extract color information (last element) and ID (second-to-last element)
            row_color = row[-1]  # Color is at the last position
            row_id = row[id_column]  # ID is at second-to-last position

            # Create items for display columns only (exclude ID and color)
            items = []
            display_data = row[:-2]  # Exclude last two elements (ID and color)

            for _col_idx, value in enumerate(display_data):
                item = QStandardItem(str(value) if value is not None else "")

                # Set background color for the item
                item.setBackground(QBrush(row_color))

                items.append(item)

            model.appendRow(items)

            # Set the ID in vertical header
            model.setVerticalHeaderItem(
                row_idx,
                QStandardItem(str(row_id)),
            )

        proxy = QSortFilterProxyModel()
        proxy.setSourceModel(model)
        return proxy

    def _create_table_model(
        self,
        data: list[list[str]],
        headers: list[str],
        id_column: int = 0,
    ) -> QSortFilterProxyModel:
        """Return a proxy model filled with `data`.

        Args:

        - `data` (`list[list[str]]`): The table data as a list of rows.
        - `headers` (`list[str]`): Column header names.
        - `id_column` (`int`): Index of the ID column. Defaults to `0`.

        Returns:

        - `QSortFilterProxyModel`: A filterable and sortable model with the data.

        """
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(headers)

        for row_idx, row in enumerate(data):
            items = [
                QStandardItem(str(value) if value is not None else "")
                for col_idx, value in enumerate(row)
                if col_idx != id_column
            ]
            model.appendRow(items)
            model.setVerticalHeaderItem(
                row_idx,
                QStandardItem(str(row[id_column])),
            )

        proxy = QSortFilterProxyModel()
        proxy.setSourceModel(model)
        return proxy

    def _dispose_models(self) -> None:
        """Detach all models from QTableView and delete them."""
        for key, model in self.models.items():
            view = self.table_config[key][0]
            view.setModel(None)
            if model is not None:
                model.deleteLater()
            self.models[key] = None

        # list-view
        self.listView_exercises.setModel(None)
        if self.exercises_list_model is not None:
            self.exercises_list_model.deleteLater()
        self.exercises_list_model = None

    def _finish_window_initialization(self) -> None:
        """Finish window initialization by showing the window and adjusting columns."""
        self.show()
        # Adjust columns after window is shown and has proper dimensions
        QTimer.singleShot(50, self._adjust_process_table_columns)
        QTimer.singleShot(55, self._update_layout_for_window_size)

    def _focus_and_select_spinbox_count(self) -> None:
        """Move focus to spinBox_count and select all text.

        This method is called after exercise selection to provide better UX
        by automatically focusing the count input field and selecting its content.
        """
        try:
            # Set focus to spinBox_count
            self.spinBox_count.setFocus()

            # Select all text in the spinbox
            self.spinBox_count.selectAll()
        except Exception as e:
            print(f"Error focusing spinBox_count: {e}")

    def _get_current_selected_exercise(self) -> str | None:
        """Get the currently selected exercise from the list view.

        Returns:

        - `str | None`: The name of the selected exercise, or None if nothing is selected.

        """
        selection_model = self.listView_exercises.selectionModel()
        if not selection_model or not self.exercises_list_model:
            return None

        current_index = selection_model.currentIndex()
        if not current_index.isValid():
            return None

        item = self.exercises_list_model.itemFromIndex(current_index)
        if item:
            # Try to get original exercise name from UserRole first
            original_name = item.data(Qt.UserRole)
            if original_name:
                return original_name
            # Fallback to display text
            return item.text()
        return None

    def _get_exercise_avif_path(self, exercise_name: str) -> Path | None:
        """Get the path to the AVIF file for the given exercise.

        Args:

        - `exercise_name` (`str`): Name of the exercise.

        Returns:

        - `Path | None`: Path to the AVIF file if it exists, None otherwise.

        """
        if not exercise_name or not self.db_manager:
            return None

        # Form path to AVIF file using exercise name directly
        db_path = Path(config["sqlite_fitness"])
        avif_dir = db_path.parent / "fitness_img"
        avif_path = avif_dir / f"{exercise_name}.avif"

        return avif_path if avif_path.exists() else None

    def _get_exercise_icon(self, exercise_name: str) -> QIcon | None:
        """Return a cached icon for the exercise, loading it from AVIF if needed."""
        if not exercise_name:
            return None

        cache_entry = self._exercise_icon_cache.get(exercise_name)
        avif_path = self._get_exercise_avif_path(exercise_name)

        if avif_path is None:
            if cache_entry is None or cache_entry[0] != -1.0:
                self._exercise_icon_cache[exercise_name] = (-1.0, None)
            return None

        try:
            mtime = avif_path.stat().st_mtime
        except OSError:
            self._exercise_icon_cache[exercise_name] = (-1.0, None)
            return None

        if cache_entry is not None and cache_entry[0] == mtime:
            return cache_entry[1]

        pixmap = self._load_avif_pixmap(avif_path)
        icon: QIcon | None = None
        if pixmap and not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(
                self.icon_size,
                self.icon_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            final_pixmap = QPixmap(self.icon_size, self.icon_size)
            final_pixmap.fill(Qt.GlobalColor.white)
            painter = QPainter(final_pixmap)
            x_offset = max((self.icon_size - scaled_pixmap.width()) // 2, 0)
            y_offset = max((self.icon_size - scaled_pixmap.height()) // 2, 0)
            painter.drawPixmap(x_offset, y_offset, scaled_pixmap)
            painter.end()
            icon = QIcon(final_pixmap)

        self._exercise_icon_cache[exercise_name] = (mtime, icon)
        return icon

    def _get_exercise_name_by_id(self, exercise_id: int) -> str | None:
        """Get exercise name by ID.

        Args:

        - `exercise_id` (`int`): Exercise ID.

        Returns:

        - `str | None`: Exercise name or None if not found.

        """
        if not self._validate_database_connection() or self.db_manager is None:
            return None

        return self.db_manager.get_exercise_name_by_id(exercise_id)

    def _get_exercise_preview_icon(self, exercise_name: str, target_size: QSize) -> QIcon | None:
        """Create a preview-sized icon for the exercise."""
        avif_path = self._get_exercise_avif_path(exercise_name)
        if avif_path is None:
            return None

        pixmap = self._load_avif_pixmap(avif_path)
        if pixmap is None or pixmap.isNull():
            return None

        scaled_pixmap = pixmap.scaled(
            target_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        if scaled_pixmap.isNull():
            return None

        final_pixmap = QPixmap(target_size)
        final_pixmap.fill(Qt.GlobalColor.white)

        painter = QPainter(final_pixmap)
        x_offset = max((target_size.width() - scaled_pixmap.width()) // 2, 0)
        y_offset = max((target_size.height() - scaled_pixmap.height()) // 2, 0)
        painter.drawPixmap(x_offset, y_offset, scaled_pixmap)
        painter.end()

        return QIcon(final_pixmap)

    def _get_exercise_today_goal_info(self, exercise: str) -> str:
        """Get today's goal information for an exercise.

        Args:

        - `exercise` (`str`): Name of the exercise.

        Returns:

        - `str`: Empty string if no data, checkmark with count if goal achieved,
          or remaining count if goal not achieved.

        """
        if self.db_manager is None:
            return ""

        # Get exercise ID
        exercise_id = self.db_manager.get_id("exercises", "name", exercise)
        if exercise_id is None:
            return ""

        # Get months count for comparison
        months_count = self.spinBox_compare_last.value()

        # Get data for last N months
        today = datetime.now(timezone.utc).astimezone()
        monthly_data = []

        for i in range(months_count):
            # Calculate start and end of month
            # Calculate month i months ago
            month_date = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            for _ in range(i):
                if month_date.month == 1:
                    month_date = month_date.replace(year=month_date.year - 1, month=12)
                else:
                    month_date = month_date.replace(month=month_date.month - 1)
            month_start_i = month_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if i == 0:
                month_end_i = today
            else:
                last_day = calendar.monthrange(month_start_i.year, month_start_i.month)[1]
                month_end_i = month_start_i.replace(day=last_day, hour=23, minute=59, second=59, microsecond=999999)

            # Get data for this month
            month_data = self.db_manager.get_exercise_chart_data(
                exercise_name=exercise,
                exercise_type=None,  # All types
                date_from=month_start_i.strftime("%Y-%m-%d"),
                date_to=month_end_i.strftime("%Y-%m-%d"),
            )

            if month_data:
                monthly_data.append(month_data)
            else:
                monthly_data.append([])

        if not monthly_data or not any(month_data for month_data in monthly_data):
            return ""

        def _monthly_total(data: list[tuple]) -> float:
            return sum(float(value) for _, value in data) if data else 0.0

        # Find the maximum final value from all months
        max_value = 0.0
        for month_data in monthly_data:
            total = _monthly_total(month_data)
            max_value = max(max_value, total)

        current_month_data = monthly_data[0] if monthly_data else []
        current_progress = _monthly_total(current_month_data)

        target_value = max_value
        if exercise_id == self.id_steps or exercise.strip().lower() == "oculus move":
            target_value = _monthly_total(monthly_data[1]) if len(monthly_data) > 1 else current_progress

            if target_value <= 0:
                target_value = max_value

        if target_value <= 0:
            return ""

        # Get today's progress
        today_progress = self.db_manager.get_exercise_total_today(exercise_id)

        # Calculate remaining days in current month
        days_in_month = calendar.monthrange(today.year, today.month)[1]
        remaining_days = days_in_month - today.day
        total_days_including_current = remaining_days + 1

        # Calculate daily needed
        remaining_to_goal = target_value - current_progress
        if total_days_including_current > 0 and remaining_to_goal > 0:
            daily_needed = remaining_to_goal / total_days_including_current
            daily_needed_rounded = math.ceil(daily_needed)

            # Calculate remaining for today
            remaining_for_today = daily_needed_rounded - today_progress

            if remaining_for_today > 0:
                # Goal not achieved - show how much more is needed
                return f"(+{int(remaining_for_today)})"
            # Goal achieved - show checkmark and completed amount
            return f"✅ ({int(today_progress)})"
        if remaining_to_goal <= 0:
            # Max goal already achieved
            return f"✅ ({int(today_progress)})"

        return ""

    def _get_first_day_without_steps_record(self, exercise_id: int) -> QDate:
        """Get the first day without Steps records (next day after last record).

        Args:

        - `exercise_id` (`int`): Exercise ID for Steps.

        Returns:

        - `QDate`: The first day without Steps records.

        """
        if self.db_manager is None:
            return QDate.currentDate()

        last_date_str = self.db_manager.get_last_exercise_date(exercise_id)
        if last_date_str:
            last_date = QDate.fromString(last_date_str, "yyyy-MM-dd")
            if QDate.isValid(last_date.year(), last_date.month(), last_date.day()):
                return last_date.addDays(1)

        return QDate.currentDate()

    def _get_last_weight(self) -> float:
        """Get the last recorded weight value from database.

        Returns:

        - `float`: The last recorded weight value, or 89.0 as default.

        """
        initial_weight = 89.0
        if not self._validate_database_connection():
            print("Database manager not available or connection not open")
            return initial_weight
        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return initial_weight

        try:
            last_weight = self.db_manager.get_last_weight()
        except Exception as e:
            print(f"Error getting last weight: {e}")
            return initial_weight
        else:
            return last_weight if last_weight is not None else initial_weight

    def _get_monthly_data_for_exercise(self, exercise_name: str, months_count: int) -> list:
        """Get monthly data for a specific exercise using the same logic as compare_last.

        Args:

        - `exercise_name` (`str`): Name of the exercise.
        - `months_count` (`int`): Number of months to analyze.

        Returns:

        - `list`: Monthly data in the same format as compare_last.

        """
        monthly_data = []
        today = datetime.now(timezone.utc).astimezone()

        for i in range(months_count):
            # Calculate start and end of month (same logic as compare_last)
            # Calculate month i months ago
            month_date = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            for _ in range(i):
                if month_date.month == 1:
                    month_date = month_date.replace(year=month_date.year - 1, month=12)
                else:
                    month_date = month_date.replace(month=month_date.month - 1)
            month_start = month_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if i == 0:
                month_end = today
            else:
                last_day = calendar.monthrange(month_start.year, month_start.month)[1]
                month_end = month_start.replace(day=last_day, hour=23, minute=59, second=59, microsecond=999999)

            # Format for DB
            date_from = month_start.strftime("%Y-%m-%d")
            date_to = month_end.strftime("%Y-%m-%d")

            # Query data for this exercise (all types)
            rows = self.db_manager.get_exercise_chart_data(
                exercise_name=exercise_name,
                exercise_type=None,  # Get all types
                date_from=date_from,
                date_to=date_to,
            )

            # Build cumulative data for this month
            cumulative_data = []
            if rows:
                cumulative_value = 0.0
                for date_str, value_str in rows:
                    try:
                        date_obj = datetime.fromisoformat(date_str).replace(tzinfo=timezone.utc)
                        value = float(value_str)
                        cumulative_value += value
                        day_of_month = date_obj.day
                        cumulative_data.append((day_of_month, cumulative_value))
                    except (ValueError, TypeError):
                        continue

                # Extend horizontally to the end-of-visualization day
                if cumulative_data:
                    last_day = cumulative_data[-1][0]
                    last_value = cumulative_data[-1][1]
                    max_day = min(today.day, 31) if i == 0 else 31
                    if last_day < max_day:
                        cumulative_data.append((max_day, last_value))

            monthly_data.append(cumulative_data)

        return monthly_data

    def _get_selected_chart_exercise(self) -> str:
        """Get the currently selected exercise from the chart exercise list view."""
        current_index = self.listView_chart_exercise.currentIndex()
        if current_index.isValid():
            model = self.listView_chart_exercise.model()
            if model:
                # Try to get original exercise name from UserRole first
                original_name = model.data(current_index, Qt.UserRole)
                if original_name:
                    return original_name
                # Fallback to display text
                return model.data(current_index) or ""
        return ""

    def _get_selected_chart_type(self) -> str:
        """Get the currently selected type from the chart type list view."""
        current_index = self.listView_chart_type.currentIndex()
        if current_index.isValid():
            model = self.listView_chart_type.model()
            if model:
                return model.data(current_index) or ""
        return ""

    def _get_selected_exercise_from_statistics_table(self) -> str | None:
        """Get selected exercise name from statistics table.

        Returns:

        - `str | None`: Exercise name or None if nothing selected.

        """
        current_index = self.tableView_statistics.currentIndex()

        if not current_index.isValid():
            # Get first row exercise name as default
            model = self.tableView_statistics.model()
            if model and model.rowCount() > 0:
                first_index = model.index(0, 0)
                exercise_name = model.data(first_index, Qt.ItemDataRole.DisplayRole)
                return exercise_name.strip() if exercise_name else None
            return None

        # Get exercise name from selected row (first column)
        model = self.tableView_statistics.model()
        if model:
            exercise_index = model.index(current_index.row(), 0)
            exercise_name = model.data(exercise_index, Qt.ItemDataRole.DisplayRole)
            return exercise_name.strip() if exercise_name else None

        return None

    def _get_selected_exercise_from_table(self, table_name: str) -> str | None:
        """Get selected exercise name from a table.

        Args:

        - `table_name` (`str`): Name of the table ('exercises' or 'statistics').

        Returns:

        - `str | None`: Exercise name or None if nothing selected.

        """
        if table_name not in self.table_config:
            return None

        table_view = self.table_config[table_name][0]
        current_index = table_view.currentIndex()

        if not current_index.isValid():
            # Get first row exercise name as default
            model = self.models[table_name]
            if model and model.rowCount() > 0:
                first_index = model.index(0, 0)
                return model.data(first_index, Qt.ItemDataRole.DisplayRole)
            return None

        # Get exercise name from selected row (first column)
        model = self.models[table_name]
        if model:
            exercise_index = model.index(current_index.row(), 0)
            return model.data(exercise_index, Qt.ItemDataRole.DisplayRole)

        return None

    def _get_selected_row_id(self, table_name: str) -> int | None:
        """Get the database ID of the currently selected row.

        Args:

        - `table_name` (`str`): Name of the table.

        Returns:

        - `int | None`: Database ID of selected row or None if no selection.

        """
        try:
            table_view, model_key, _ = self.table_config[table_name]
            model = self.models[model_key]

            if model is None:
                return None

            index = table_view.currentIndex()
            if not index.isValid():
                return None

            source_model = model.sourceModel()
            if not isinstance(source_model, QStandardItemModel):
                return None

            vertical_header_item = source_model.verticalHeaderItem(index.row())
            return int(vertical_header_item.text()) if vertical_header_item else None

        except (KeyError, ValueError, TypeError, AttributeError):
            return None

    def _init_database(self) -> None:
        """Open the SQLite file from `config` (create from recover.sql if missing).

        Attempts to open the database file specified in the configuration.
        If the file doesn't exist, tries to create it from recover.sql file located
        in the application directory.
        If the file exists but doesn't contain the required table (process),
        creates the missing table from recover.sql.
        If creation fails or no database is available, prompts the user to select a database file.
        If no database is selected or an error occurs, the application exits.
        """
        filename = Path(config["sqlite_fitness"])

        # Try to open existing database first
        if filename.exists():
            try:
                temp_db_manager = database_manager.DatabaseManager(str(filename))

                # Check if process table exists
                if temp_db_manager.table_exists("process"):
                    print(f"Database opened successfully: {filename}")
                    self.db_manager = temp_db_manager
                    return
                print(f"Database exists but process table is missing at {filename}")
                temp_db_manager.close()
            except Exception as e:
                print(f"Failed to open existing database: {e}")
                # Continue to create new database

        # Database doesn't exist or is missing required table - create from recover.sql
        app_dir = Path(__file__).parent  # Directory where this script is located
        recover_sql_path = app_dir / "recover.sql"

        if recover_sql_path.exists():
            print(f"Database not found or missing process table at {filename}")
            print(f"Attempting to create database from {recover_sql_path}")

            if database_manager.DatabaseManager.create_database_from_sql(str(filename), str(recover_sql_path)):
                print("Database created successfully from recover.sql")
            else:
                QMessageBox.warning(
                    self,
                    "Database Creation Failed",
                    f"Failed to create database from {recover_sql_path}\nPlease select an existing database file.",
                )
        else:
            QMessageBox.information(
                self,
                "Database Not Found",
                f"Database file not found: {filename}\n"
                f"recover.sql file not found: {recover_sql_path}\n"
                "Please select an existing database file.",
            )

        # If database still doesn't exist, ask user to select one
        if not filename.exists():
            filename_str, _ = QFileDialog.getOpenFileName(
                self,
                "Open Database",
                str(filename.parent),
                "SQLite Database (*.db)",
            )
            if not filename_str:
                QMessageBox.critical(self, "Error", "No database selected")
                sys.exit(1)
            filename = Path(filename_str)

        try:
            self.db_manager = database_manager.DatabaseManager(
                str(filename),
            )
            print(f"Database opened successfully: {filename}")
        except (OSError, RuntimeError, ConnectionError) as exc:
            QMessageBox.critical(self, "Error", f"Failed to open database: {exc}")
            sys.exit(1)

    def _init_exercise_chart_controls(self) -> None:
        """Initialize exercise chart controls."""
        current_date = QDate.currentDate()
        self.dateEdit_chart_from.setDate(current_date.addMonths(-1))
        self.dateEdit_chart_to.setDate(current_date)

        # Make listView_chart_exercise items non-editable
        self.listView_chart_exercise.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        # Initialize exercise and type list views
        self.update_chart_comboboxes()

        # Initialize same months comparison combobox
        self.comboBox_compare_same_months.clear()
        months = [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ]
        self.comboBox_compare_same_months.addItems(months)

        # Set current month as default
        current_month_index = current_date.month() - 1  # QDate.month() returns 1-12, we need 0-11
        self.comboBox_compare_same_months.setCurrentIndex(current_month_index)

        # Set default radio button
        self.radioButton_type_of_chart_compare_last.setChecked(True)

        # Set default value for compare last spinbox
        self.spinBox_compare_last.setValue(12)

    def _init_exercises_list(self) -> None:
        """Initialize the exercises list view with a model and connect signals."""
        self.exercises_list_model = QStandardItemModel()
        self.listView_exercises.setModel(self.exercises_list_model)
        self.listView_exercises.setIconSize(QSize(self.icon_size, self.icon_size))

        # Disable editing for exercises list
        self.listView_exercises.setEditTriggers(QListView.EditTrigger.NoEditTriggers)

        # Initialize labels with default values
        self.label_exercise.setText("No exercise selected")
        self.label_unit.setText("")
        self.label_last_date_count_today.setText("")

        # Connect selection change signal after model is set
        selection_model = self.listView_exercises.selectionModel()
        if selection_model:
            selection_model.currentChanged.connect(self.on_exercise_selection_changed_list)

    def _init_filter_controls(self) -> None:
        """Prepare widgets on the `Filters` group box.

        Initializes the filter controls with default values:

        - Sets the date range to the last month
        - Disables date filtering by default
        - Connects filter-related signals to their handlers
        """
        current_date = QDateTime.currentDateTime().date()
        self.dateEdit_filter_from.setDate(current_date.addMonths(-1))
        self.dateEdit_filter_to.setDate(current_date)

        self.checkBox_use_date_filter.setChecked(False)

    def _init_sets_count_display(self) -> None:
        """Initialize the sets count display."""
        self.update_sets_count_today()

    def _init_weight_chart_controls(self) -> None:
        """Initialize weight chart date controls."""
        current_date = QDate.currentDate()
        self.dateEdit_weight_from.setDate(current_date.addMonths(-1))
        self.dateEdit_weight_to.setDate(current_date)

    def _init_weight_controls(self) -> None:
        """Initialize weight input controls with last recorded values."""
        last_weight = self._get_last_weight()
        self.doubleSpinBox_weight.setValue(last_weight)
        self.dateEdit_weight.setDate(QDate.currentDate())

    def _load_avif_pixmap(self, avif_path: Path) -> QPixmap | None:
        """Load a pixmap from an AVIF file, falling back to Pillow if needed."""
        pixmap = QPixmap(str(avif_path))
        if not pixmap.isNull():
            return pixmap

        try:
            import pillow_avif  # noqa: F401, PLC0415
        except ModuleNotFoundError:
            return None

        try:
            with Image.open(avif_path) as pil_image:
                if getattr(pil_image, "is_animated", False):
                    pil_image.seek(0)
                frame = pil_image.convert("RGBA")
                buffer = io.BytesIO()
                frame.save(buffer, format="PNG")
                buffer.seek(0)
                pixmap = QPixmap()
                pixmap.loadFromData(buffer.getvalue())
                return pixmap if not pixmap.isNull() else None
        except Exception as exc:  # pragma: no cover - fallback path
            print(f"Failed to load AVIF pixmap from {avif_path}: {exc}")
        return None

    def _load_default_exercise_chart(self) -> None:
        """Load default exercise chart on first set to charts tab."""
        if not hasattr(self, "_charts_initialized"):
            self._charts_initialized = True

            if self.db_manager is None:
                print("❌ Database manager is not initialized")
                return

            # Set period to Months
            self.comboBox_chart_period.setCurrentText("Months")

            # Try to get the last executed exercise from process table
            if self._validate_database_connection():
                last_exercise_name = self.db_manager.get_last_executed_exercise()

                if last_exercise_name:
                    # Find and select the last executed exercise in the list view
                    if self._select_exercise_in_chart_list(last_exercise_name):
                        # Update type list view after selecting exercise
                        self.update_chart_type_listview()
                else:
                    # Fallback to Steps exercise if no records found
                    rows = self.db_manager.get_rows(f"SELECT name FROM exercises WHERE _id = {self.id_steps}")
                    if rows:
                        exercise_name = rows[0][0]
                        # Find and select the exercise in the list view
                        if self._select_exercise_in_chart_list(exercise_name):
                            # Update type list view after selecting exercise
                            self.update_chart_type_listview()

            # Load chart with all time data
            self.set_chart_all_time()

    def _load_default_statistics(self) -> None:
        """Load default statistics on first visit to statistics tab."""
        if not hasattr(self, "_statistics_initialized"):
            self._statistics_initialized = True
            # Initialize statistics exercise combobox
            self.update_statistics_exercise_combobox()

            # Get current exercise from main tab and set it in statistics combobox
            current_exercise = self._get_current_selected_exercise()
            if current_exercise:
                # Block signals to prevent recursive updates
                self.comboBox_records_select_exercise.blockSignals(True)  # noqa: FBT003

                # Find and select the current exercise in statistics combobox
                index = self.comboBox_records_select_exercise.findText(current_exercise)
                if index >= 0:
                    self.comboBox_records_select_exercise.setCurrentIndex(index)

                # Unblock signals
                self.comboBox_records_select_exercise.blockSignals(False)  # noqa: FBT003

            # Automatically refresh statistics on first visit
            self.on_refresh_statistics()

    def _load_exercise_avif(self, exercise_name: str, label_key: str = "main") -> None:
        """Load and display AVIF animation for the given exercise using Pillow with AVIF support.

        Args:

        - `exercise_name` (`str`): Name of the exercise to load AVIF for.
        - `label_key` (`str`): Key identifying which label to update
          ('main', 'exercises', 'types', 'charts', 'statistics'). Defaults to `"main"`.

        """
        # Get the appropriate label widget
        label_widgets = {
            "main": self.label_exercise_avif,
            "exercises": self.label_exercise_avif_2,
            "types": self.label_exercise_avif_3,
            "charts": self.label_exercise_avif_4,
            "statistics": self.label_exercise_avif_5,
        }

        label_widget = label_widgets.get(label_key)
        if not label_widget:
            print(f"Unknown label key: {label_key}")
            return

        # Get reference to data dict for this label
        data = self.avif_data[label_key]

        # Stop current animation if exists
        timer = data["timer"]
        if timer is not None and isinstance(timer, QTimer):
            timer.stop()
            data["timer"] = None

        data["frames"] = []
        data["current_frame"] = 0
        data["exercise"] = exercise_name

        # Clear label and reset alignment
        label_widget.clear()
        label_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if not exercise_name:
            label_widget.setText("No exercise selected")
            return

        # Get path to AVIF
        avif_path = self._get_exercise_avif_path(exercise_name)

        if avif_path is None:
            label_widget.setText(f"No AVIF found for:\n{exercise_name}")
            return

        try:
            # Try Qt native first
            pixmap = QPixmap(str(avif_path))

            if not pixmap.isNull():
                label_size = label_widget.size()
                scaled_pixmap = pixmap.scaled(
                    label_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
                )
                label_widget.setPixmap(scaled_pixmap)
                return

            # Fallback to Pillow with AVIF plugin for animation
            try:
                import pillow_avif  # noqa: F401, PLC0415

                # Open with Pillow
                pil_image = Image.open(avif_path)

                # Handle animated AVIF
                if getattr(pil_image, "is_animated", False):
                    # Extract all frames
                    frames: list[QPixmap] = []
                    label_size = label_widget.size()

                    for frame_index in range(getattr(pil_image, "n_frames", 1)):
                        pil_image.seek(frame_index)

                        # Create a copy of the frame
                        frame = pil_image.copy()

                        # Convert to RGB if needed
                        if frame.mode in ("RGBA", "LA", "P"):
                            background = Image.new("RGB", frame.size, (255, 255, 255))
                            if frame.mode == "P":
                                frame = frame.convert("RGBA")
                            if frame.mode in ("RGBA", "LA"):
                                background.paste(frame, mask=frame.split()[-1])
                            else:
                                background.paste(frame)
                            frame = background
                        elif frame.mode != "RGB":
                            frame = frame.convert("RGB")

                        # Convert PIL image to QPixmap
                        buffer = io.BytesIO()
                        frame.save(buffer, format="PNG")
                        buffer.seek(0)

                        pixmap = QPixmap()
                        pixmap.loadFromData(buffer.getvalue())

                        if not pixmap.isNull():
                            scaled_pixmap = pixmap.scaled(
                                label_size,
                                Qt.AspectRatioMode.KeepAspectRatio,
                                Qt.TransformationMode.SmoothTransformation,
                            )
                            frames.append(scaled_pixmap)

                    if frames:
                        # Store frames in data dict
                        data["frames"] = frames

                        # Show first frame
                        label_widget.setPixmap(frames[0])

                        # Start animation timer
                        new_timer = QTimer()
                        new_timer.timeout.connect(lambda: self._next_avif_frame(label_key))
                        data["timer"] = new_timer

                        # Get frame duration (default 100ms if not available)
                        try:
                            duration = pil_image.info.get("duration", 100)
                        except Exception:
                            duration = 100

                        new_timer.start(duration)
                        return
                else:
                    # Static image
                    frame = pil_image

                    # Convert to RGB if needed
                    if frame.mode in ("RGBA", "LA", "P"):
                        background = Image.new("RGB", frame.size, (255, 255, 255))
                        if frame.mode == "P":
                            frame = frame.convert("RGBA")
                        if frame.mode in ("RGBA", "LA"):
                            background.paste(frame, mask=frame.split()[-1])
                        else:
                            background.paste(frame)
                        frame = background
                    elif frame.mode != "RGB":
                        frame = frame.convert("RGB")

                    # Convert PIL image to QPixmap
                    buffer = io.BytesIO()
                    frame.save(buffer, format="PNG")
                    buffer.seek(0)

                    pixmap = QPixmap()
                    pixmap.loadFromData(buffer.getvalue())

                    if not pixmap.isNull():
                        label_size = label_widget.size()
                        scaled_pixmap = pixmap.scaled(
                            label_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
                        )
                        label_widget.setPixmap(scaled_pixmap)
                        return

            except ImportError as import_error:
                print(f"Import error: {import_error}")
                label_widget.setText(f"AVIF plugin not available:\n{exercise_name}")
                return
            except Exception as pil_error:
                print(f"Pillow error: {pil_error}")

            label_widget.setText(f"Cannot load AVIF:\n{exercise_name}")

        except Exception as e:
            print(f"General error: {e}")
            label_widget.setText(f"Error loading AVIF:\n{exercise_name}\n{e}")

    def _load_initial_avifs(self) -> None:
        """Load AVIF for all labels after complete UI initialization."""
        # Load main exercise AVIF
        current_exercise_name = self._get_current_selected_exercise()
        if isinstance(current_exercise_name, str):
            self._load_exercise_avif(current_exercise_name, "main")
            # Trigger the selection change to update labels
            self.on_exercise_selection_changed_list()

        # Load exercises table AVIF (first row by default)
        self._update_exercises_avif()

        # Load types combobox AVIF
        self._update_types_avif()

        # Load charts combobox AVIF
        self._update_charts_avif()

        # Statistics AVIF will be loaded when statistics tab is accessed

    def _mark_exercises_changed(self) -> None:
        """Mark that exercises data has changed and needs refresh."""
        self._exercises_changed = True

    def _next_avif_frame(self, label_key: str) -> None:
        """Show next frame in AVIF animation for specific label.

        Args:

        - `label_key` (`str`): Key identifying which label to update.

        """
        frames = self.avif_data[label_key]["frames"]
        if not frames or not isinstance(frames, list):
            return

        current_frame_index = self.avif_data[label_key]["current_frame"]
        if not isinstance(current_frame_index, int):
            return

        current_frame = (current_frame_index + 1) % len(frames)
        self.avif_data[label_key]["current_frame"] = current_frame

        # Get the appropriate label widget
        label_widgets = {
            "main": self.label_exercise_avif,
            "exercises": self.label_exercise_avif_2,
            "types": self.label_exercise_avif_3,
            "charts": self.label_exercise_avif_4,
            "statistics": self.label_exercise_avif_5,
        }

        label_widget = label_widgets.get(label_key)
        if label_widget:
            label_widget.setPixmap(frames[current_frame])

    def _on_chart_exercise_list_double_clicked(self, _index: QModelIndex) -> None:
        """Handle double-click on chart exercise list to open Sets tab.

        Args:

        - `_index` (`QModelIndex`): Index of the double-clicked item.

        """
        # Find the Sets tab index (first tab with name "Sets")
        sets_tab_index = self.tabWidget.indexOf(self.tab)
        if sets_tab_index >= 0:
            self.tabWidget.setCurrentIndex(sets_tab_index)

    def _on_chart_info_double_clicked(self, _event: QMouseEvent) -> None:
        """Handle double-click on chart info label to copy text to clipboard.

        Args:

        - `_event` (`QMouseEvent`): Mouse event.

        """
        # Get the text from the label
        html_text = self.label_chart_info.text()
        if html_text.strip():  # Only copy if there's actual text
            # Convert HTML to plain text
            doc = QTextDocument()
            doc.setHtml(html_text)
            plain_text = doc.toPlainText()

            # Create clipboard data
            clipboard = QApplication.clipboard()
            clipboard.setText(plain_text)

            # Optional: Show a brief notification (you can remove this if not needed)
            # You could add a toast notification here if you have one

    def _on_exercises_list_double_clicked(self, index: QModelIndex) -> None:
        """Handle double-click on exercises list to open Exercise Chart tab.

        Args:

        - `index` (`QModelIndex`): Index of the double-clicked item.

        """
        # Get exercise name from the clicked item
        if not index.isValid() or not self.exercises_list_model:
            return

        item = self.exercises_list_model.itemFromIndex(index)
        if not item:
            return

        # Try to get original exercise name from UserRole first
        exercise_name = item.data(Qt.UserRole)
        if not exercise_name:
            # Fallback to display text
            exercise_name = item.text()

        if not exercise_name:
            return

        # Find the Exercise Chart tab index
        chart_tab_index = self.tabWidget.indexOf(self.tab_charts)
        if chart_tab_index >= 0:
            # Switch to Exercise Chart tab
            self.tabWidget.setCurrentIndex(chart_tab_index)

            # Update chart comboboxes first to ensure listView_chart_exercise is populated
            self.update_chart_comboboxes()

            # Select the exercise in chart exercise list view
            if self._select_exercise_in_chart_list(exercise_name):
                # Update type list view after selecting exercise
                self.update_chart_type_listview()
                # Update chart and label_chart_info
                self._update_chart_based_on_radio_button()

    def _on_table_data_changed(
        self, table_name: str, top_left: QModelIndex, bottom_right: QModelIndex, _roles: list | None = None
    ) -> None:
        """Handle data changes in table models and auto-save to database.

        Args:

        - `table_name` (`str`): Name of the table that was modified.
        - `top_left` (`QModelIndex`): Top-left index of the changed area.
        - `bottom_right` (`QModelIndex`): Bottom-right index of the changed area.
        - `_roles` (`list | None`): List of roles that changed. Defaults to `None`.

        """
        if table_name not in self._SAFE_TABLES:
            return

        if not self._validate_database_connection():
            return

        try:
            proxy_model = self.models[table_name]
            if proxy_model is None:
                return
            model = proxy_model.sourceModel()
            if not isinstance(model, QStandardItemModel):
                return

            # Process each changed row
            for row in range(top_left.row(), bottom_right.row() + 1):
                row_id = model.verticalHeaderItem(row).text()
                self._auto_save_row(table_name, model, row, row_id)

        except Exception as e:
            QMessageBox.warning(self, "Auto-save Error", f"Failed to auto-save changes: {e!s}")

    def _on_window_resize(self, event: QResizeEvent) -> None:
        """Handle window resize event and adjust table column widths proportionally.

        Args:

        - `event` (`QResizeEvent`): The resize event.

        """
        # Call parent resize event first
        super().resizeEvent(event)

        # Adjust process table column widths based on window size
        self._adjust_process_table_columns()
        self._update_layout_for_window_size()

    def _refresh_table(self, table_name: str, data_getter: Callable, data_transformer: Callable | None = None) -> None:
        """Refresh a table with data.

        Args:

        - `table_name` (`str`): Name of the table to refresh.
        - `data_getter` (`Callable`): Function to get data from database.
        - `data_transformer` (`Callable | None`): Optional function to transform raw data.
          Defaults to `None`.

        Raises:

        - `ValueError`: If the table name is unknown.

        """
        if table_name not in self.table_config:
            error_msg = f"❌ Unknown table: {table_name}"
            raise ValueError(error_msg)

        rows = data_getter()
        if data_transformer:
            rows = data_transformer(rows)

        view, model_key, headers = self.table_config[table_name]
        self.models[model_key] = self._create_table_model(rows, headers)
        view.setModel(self.models[model_key])
        view.resizeColumnsToContents()

    def _schedule_chart_update(self, delay_ms: int = 50) -> None:
        """Schedule a chart update with the specified delay.

        Args:

        - `delay_ms` (`int`): Delay in milliseconds before updating the chart. Defaults to `50`.

        """
        # Ensure timer exists (defensive programming)
        if not hasattr(self, "_chart_update_timer") or self._chart_update_timer is None:
            self._chart_update_timer = QTimer(self)
            self._chart_update_timer.setSingleShot(True)
            self._chart_update_timer.timeout.connect(self._update_chart_based_on_radio_button)

        self._chart_update_timer.start(delay_ms)

    def _select_exercise_in_chart_list(self, exercise_name: str) -> bool:
        """Select an exercise in the chart exercise list view by name.

        Args:

        - `exercise_name` (`str`): Name of the exercise to select.

        Returns:

        - `bool`: Whether the selection was changed.

        """
        if not exercise_name:
            return False

        model = self.listView_chart_exercise.model()
        if not model:
            return False

        target_name = exercise_name.strip()

        # Find the item with the matching exercise name
        for row in range(model.rowCount()):
            index = model.index(row, 0)
            original_name = model.data(index, Qt.UserRole)
            display_name = model.data(index, Qt.ItemDataRole.DisplayRole)

            if original_name == target_name or (original_name is None and display_name == target_name):
                selection_model = self.listView_chart_exercise.selectionModel()
                if selection_model:
                    selection_model.setCurrentIndex(index, selection_model.SelectionFlag.ClearAndSelect)
                else:
                    self.listView_chart_exercise.setCurrentIndex(index)
                return True

        return False

    def _select_exercise_in_list(self, exercise_name: str) -> bool:
        """Select an exercise in the list view by name.

        Args:

        - `exercise_name` (`str`): Name of the exercise to select.

        Returns:

        - `bool`: Whether the selection was changed.

        """
        if not self.exercises_list_model or not exercise_name:
            return False

        # Find the item with the matching exercise name
        for row in range(self.exercises_list_model.rowCount()):
            item = self.exercises_list_model.item(row)
            if item:
                # Check UserRole first (original name), then fallback to text
                original_name = item.data(Qt.UserRole)
                item_name = original_name if original_name else item.text()

                if item_name == exercise_name:
                    index = self.exercises_list_model.indexFromItem(item)
                    selection_model = self.listView_exercises.selectionModel()
                    if selection_model:
                        selection_model.setCurrentIndex(index, selection_model.SelectionFlag.ClearAndSelect)
                    else:
                        self.listView_exercises.setCurrentIndex(index)
                    return True

        return False

    def _select_exercise_in_statistics_combobox(self, exercise_name: str) -> bool:
        """Select an exercise in the statistics combobox by name.

        Args:

        - `exercise_name` (`str`): Name of the exercise to select.

        Returns:

        - `bool`: Whether the selection was changed.

        """
        if not exercise_name:
            return False

        combobox = self.comboBox_records_select_exercise
        target_index = combobox.findText(exercise_name)

        if target_index < 0 or combobox.currentIndex() == target_index:
            return False

        combobox.blockSignals(True)  # noqa: FBT003
        try:
            combobox.setCurrentIndex(target_index)
        finally:
            combobox.blockSignals(False)  # noqa: FBT003

        return True

    def _select_last_executed_exercise(self) -> None:
        """Select the last executed exercise in the chart exercise list view."""
        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        if not self._validate_database_connection():
            return

        try:
            last_exercise_name = self.db_manager.get_last_executed_exercise()

            if last_exercise_name and self._select_exercise_in_chart_list(last_exercise_name):
                # Update type list view after selecting exercise
                self.update_chart_type_listview()
        except Exception as e:
            print(f"Error selecting last executed exercise: {e}")

    # Add to MainWindow class (near other small helpers)
    def _set_no_data_info_label(self, text: str | None = None) -> None:
        """Set a unified 'no data' message into label_chart_info.

        Args:

        - `text` (`str | None`): Message text to display. If None, uses default message based
          on spinBox_compare_last value. Defaults to `None`.

        """
        # Default message uses the spinner value for months when appropriate
        if text is None:
            months = self.spinBox_compare_last.value() if hasattr(self, "spinBox_compare_last") else 0
            text = f"No data for the last {months} months." if months > 0 else "No data for the selected period."

        self.label_chart_info.setText(text)
        self.label_chart_info.setStyleSheet("""
            margin: 5px 0px;
            padding: 10px;
            background-color: #F8F9FA;
            border: 1px solid #E9ECEF;
            border-radius: 5px;
            font-size: 13px;
            line-height: 1.2;
        """)

    def _set_today_date_in_main(self) -> None:
        """Set today's date in the main date field."""
        today = QDate.currentDate()
        self.dateEdit.setDate(today)

    def _setup_ui(self) -> None:
        """Set up additional UI elements after basic initialization."""
        # Set emoji for buttons
        self.pushButton_yesterday.setText(f"📅 {self.pushButton_yesterday.text()}")
        self.pushButton_add.setText(f"➕  {self.pushButton_add.text()}")  # noqa: RUF001
        self.pushButton_delete.setText(f"🗑️ {self.pushButton_delete.text()}")
        self.pushButton_refresh.setText(f"🔄 {self.pushButton_refresh.text()}")
        self.pushButton_show_all_records.setText(f"📋 {self.pushButton_show_all_records.text()}")
        self.pushButton_export_csv.setText(f"📤 {self.pushButton_export_csv.text()}")
        self.pushButton_clear_filter.setText(f"🧹 {self.pushButton_clear_filter.text()}")
        self.pushButton_apply_filter.setText(f"✔️ {self.pushButton_apply_filter.text()}")
        self.pushButton_exercise_add.setText(f"➕ {self.pushButton_exercise_add.text()}")  # noqa: RUF001
        self.pushButton_exercises_delete.setText(f"🗑️ {self.pushButton_exercises_delete.text()}")
        self.pushButton_exercises_refresh.setText(f"🔄 {self.pushButton_exercises_refresh.text()}")
        self.pushButton_type_add.setText(f"➕ {self.pushButton_type_add.text()}")  # noqa: RUF001
        self.pushButton_types_delete.setText(f"🗑️ {self.pushButton_types_delete.text()}")
        self.pushButton_types_refresh.setText(f"🔄 {self.pushButton_types_refresh.text()}")
        self.pushButton_weight_add.setText(f"➕ {self.pushButton_weight_add.text()}")  # noqa: RUF001
        self.pushButton_weight_delete.setText(f"🗑️ {self.pushButton_weight_delete.text()}")
        self.pushButton_weight_refresh.setText(f"🔄 {self.pushButton_weight_refresh.text()}")
        self.pushButton_statistics_refresh.setText(f"🏆 {self.pushButton_statistics_refresh.text()}")
        self.pushButton_last_exercises.setText(f"📅 {self.pushButton_last_exercises.text()}")
        self.pushButton_check_steps.setText(f"👟 {self.pushButton_check_steps.text()}")
        self.pushButton_update_chart.setText(f"🔄 {self.pushButton_update_chart.text()}")
        self.pushButton_chart_last_month.setText(f"📅 {self.pushButton_chart_last_month.text()}")
        self.pushButton_chart_last_year.setText(f"📅 {self.pushButton_chart_last_year.text()}")
        self.pushButton_chart_all_time.setText(f"📅 {self.pushButton_chart_all_time.text()}")
        self.pushButton_weight_last_month.setText(f"📅 {self.pushButton_weight_last_month.text()}")
        self.pushButton_weight_last_year.setText(f"📅 {self.pushButton_weight_last_year.text()}")
        self.pushButton_weight_all_time.setText(f"📅 {self.pushButton_weight_all_time.text()}")
        self.pushButton_update_weight_chart.setText(f"🔄 {self.pushButton_update_weight_chart.text()}")
        self.pushButton_exercise_goal_recommendations.setText(
            f"🎯 {self.pushButton_exercise_goal_recommendations.text()}"
        )

        # Configure splitter proportions
        self.splitter.setStretchFactor(0, 0)  # frame with fixed size
        self.splitter.setStretchFactor(1, 1)  # listView gets less space
        self.splitter.setStretchFactor(2, 3)  # tableView gets more space

        # Initialize calories spinboxes
        self.doubleSpinBox_calories_per_unit.setDecimals(1)
        self.doubleSpinBox_calories_per_unit.setMinimum(0.0)
        self.doubleSpinBox_calories_per_unit.setMaximum(999.9)
        self.doubleSpinBox_calories_per_unit.setValue(0.0)

        self.doubleSpinBox_calories_modifier.setDecimals(1)
        self.doubleSpinBox_calories_modifier.setMinimum(0.1)
        self.doubleSpinBox_calories_modifier.setMaximum(10.0)
        self.doubleSpinBox_calories_modifier.setValue(1.0)

    def _setup_window_size_and_position(self) -> None:
        """Set window size and position based on screen resolution and characteristics."""
        screen_geometry = QApplication.primaryScreen().geometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        # Determine window size and position based on screen characteristics
        aspect_ratio = screen_width / screen_height
        standard_aspect_ratio = 2.0
        is_standard_aspect = aspect_ratio <= standard_aspect_ratio  # Standard aspect ratio (16:9, 16:10, etc.)

        standart_width = 1920
        if is_standard_aspect and screen_width >= standart_width:
            # For standard aspect ratios with width >= standart_width, maximize window
            self.showMaximized()
        else:
            title_bar_height = 30  # Approximate title bar height
            windows_task_bar_height = 48  # Approximate windows task bar height
            # For other cases, use fixed width and full height minus title bar
            window_width = standart_width
            window_height = screen_height - title_bar_height - windows_task_bar_height
            # Position window on screen
            screen_center = screen_geometry.center()
            # Center horizontally, position at top vertically with title bar offset
            self.setGeometry(
                screen_center.x() - window_width // 2,
                title_bar_height,  # Position below title bar
                window_width,
                window_height,
            )

    def _show_exercise_types_context_menu(self, position: QPoint) -> None:
        """Show context menu for exercise types table.

        Args:

        - `position` (`QPoint`): Position where context menu should appear.

        """
        context_menu = QMenu(self)
        export_action = context_menu.addAction("📤 Export to CSV")

        action = context_menu.popup(self.tableView_exercise_types.mapToGlobal(position))

        if action == export_action:
            print("🔧 Context menu: Export to CSV action triggered")
            self.on_export_csv()

    def _show_exercises_context_menu(self, position: QPoint) -> None:
        """Show context menu for exercises table.

        Args:

        - `position` (`QPoint`): Position where context menu should appear.

        """
        context_menu = QMenu(self)
        export_action = context_menu.addAction("📤 Export to CSV")

        action = context_menu.popup(self.tableView_exercises.mapToGlobal(position))

        if action == export_action:
            print("🔧 Context menu: Export to CSV action triggered")
            self.on_export_csv()

    def _show_process_context_menu(self, position: QPoint) -> None:
        """Show context menu for process table.

        Args:

        - `position` (`QPoint`): Position where context menu should appear.

        """
        context_menu = QMenu(self)
        export_action = context_menu.addAction("📤 Export to CSV")
        context_menu.addSeparator()
        delete_action = context_menu.addAction("🗑 Delete selected row")

        # Execute the context menu and get the selected action
        action = context_menu.exec_(self.tableView_process.mapToGlobal(position))

        # Process the action only if it was actually selected (not None)
        if action is None:
            # User clicked outside the menu or pressed Esc - do nothing
            return

        if action == export_action:
            print("🔧 Context menu: Export to CSV action triggered")
            self.on_export_csv()
        elif action == delete_action:
            # Check that a row is selected
            if self.tableView_process.currentIndex().isValid():
                print("🔧 Context menu: Delete action triggered")
                self.pushButton_delete.click()
            else:
                print("⚠️ Context menu: No row selected for deletion")

    def _show_record_congratulations(self, exercise: str, record_info: dict) -> None:
        """Show congratulations message for new records.

        Args:

        - `exercise` (`str`): Exercise name.
        - `record_info` (`dict`): Record information from `_check_for_new_records`.

        """
        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            # Get exercise unit for display
            unit = self.db_manager.get_exercise_unit(exercise)
            unit_text = f" {unit}" if unit else ""

            # Build the message
            title = "🏆 NEW RECORD! 🏆"

            # Build exercise display name with type if applicable
            exercise_display = exercise
            if record_info["type_name"]:
                exercise_display += f" - {record_info['type_name']}"

            current_value = record_info["current_value"]

            if record_info["is_all_time"]:
                previous_value = record_info["previous_all_time"]
                improvement = current_value - previous_value

                # Check if this is the first record for this exercise
                if previous_value == 0.0:
                    message = (
                        f"🎉 Congratulations! You've set your FIRST ALL-TIME RECORD! 🎉\n\n"
                        f"Exercise: {exercise_display}\n"
                        f"First Record: {current_value:g}{unit_text}\n\n"
                        f"🚀 Great start! Keep up the momentum! 🚀"
                    )
                else:
                    message = (
                        f"🎉 Congratulations! You've set a new ALL-TIME RECORD! 🎉\n\n"
                        f"Exercise: {exercise_display}\n"
                        f"New Record: {current_value:g}{unit_text}\n"
                        f"Previous Best: {previous_value:g}{unit_text}\n"
                        f"Improvement: +{improvement:g}{unit_text}\n\n"
                        f"🔥 Amazing achievement! Keep up the great work! 🔥"
                    )
            elif record_info["is_yearly"]:
                previous_value = record_info["previous_yearly"]
                improvement = current_value - previous_value

                # Check if this is the first yearly record
                if previous_value == 0.0:
                    message = (
                        f"🎊 Congratulations! You've set your FIRST YEARLY RECORD! 🎊\n\n"
                        f"Exercise: {exercise_display}\n"
                        f"First Year Record: {current_value:g}{unit_text}\n\n"
                        f"⭐ Excellent start to the year! ⭐"
                    )
                else:
                    message = (
                        f"🎊 Congratulations! You've set a new YEARLY RECORD! 🎊\n\n"
                        f"Exercise: {exercise_display}\n"
                        f"New Record: {current_value:g}{unit_text}\n"
                        f"Previous Year Best: {previous_value:g}{unit_text}\n"
                        f"Improvement: +{improvement:g}{unit_text}\n\n"
                        f"⭐ Excellent progress this year! ⭐"
                    )
            else:
                return  # Should not happen, but just in case

            # Show the congratulations message
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle(title)
            msg_box.setText(message)
            msg_box.setIcon(QMessageBox.Icon.Information)

            # Make the message box more prominent
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: #f0f8ff;
                    font-size: 12px;
                }
                QMessageBox QLabel {
                    color: #2e8b57;
                    font-weight: bold;
                }
            """)

            msg_box.exec()

        except Exception as e:
            print(f"Error showing record congratulations: {e}")

    def _show_statistics_context_menu(self, position: QPoint) -> None:
        """Show context menu for statistics table.

        Args:

        - `position` (`QPoint`): Position where context menu should appear.

        """
        context_menu = QMenu(self)
        export_action = context_menu.addAction("📤 Export to CSV")

        action = context_menu.popup(self.tableView_statistics.mapToGlobal(position))

        if action == export_action:
            print("🔧 Context menu: Export to CSV action triggered")
            self.on_export_csv()

    def _show_weight_context_menu(self, position: QPoint) -> None:
        """Show context menu for weight table.

        Args:

        - `position` (`QPoint`): Position where context menu should appear.

        """
        context_menu = QMenu(self)
        export_action = context_menu.addAction("📤 Export to CSV")

        action = context_menu.popup(self.tableView_weight.mapToGlobal(position))

        if action == export_action:
            print("🔧 Context menu: Export to CSV action triggered")
            self.on_export_csv()

    def _show_yesterday_context_menu(self, position: QPoint) -> None:
        """Show context menu for yesterday button with date options.

        Args:

        - `position` (`QPoint`): Position where context menu should appear.

        """
        context_menu = QMenu(self)

        # Today's date
        today_action = context_menu.addAction("📅 Today's date")
        today_action.triggered.connect(self._set_today_date_in_main)

        # Add separator
        context_menu.addSeparator()

        # Plus 1 day
        plus_one_action = context_menu.addAction("➕ Add 1 day")  # noqa: RUF001
        plus_one_action.triggered.connect(self._add_one_day_to_main)

        # Minus 1 day
        minus_one_action = context_menu.addAction("➖ Subtract 1 day")  # noqa: RUF001
        minus_one_action.triggered.connect(self._subtract_one_day_from_main)

        # Show context menu at cursor position
        context_menu.popup(self.pushButton_yesterday.mapToGlobal(position))


    def _subtract_one_day_from_main(self) -> None:
        """Subtract one day from the current date in main date field."""
        current_date = self.dateEdit.date()
        new_date = current_date.addDays(-1)
        self.dateEdit.setDate(new_date)

    def _sync_exercise_selection(self, exercise_name: str, *, source: str) -> None:
        """Synchronize exercise selection across widgets.

        Args:

        - `exercise_name` (`str`): Name of the exercise to synchronize.
        - `source` (`str`): Identifier of the widget initiating the sync.

        """
        if not exercise_name or self._syncing_selection:
            return

        self._syncing_selection = True
        try:
            if source != "list":
                self._select_exercise_in_list(exercise_name)
            if source != "chart":
                self._select_exercise_in_chart_list(exercise_name)
            if source != "combo":
                selection_changed = self._select_exercise_in_statistics_combobox(exercise_name)
                if selection_changed and hasattr(self, "_statistics_initialized"):
                    self._update_statistics_avif()
        finally:
            self._syncing_selection = False

    def _update_chart_based_on_radio_button(self) -> None:
        """Update chart based on selected radio button."""
        if self.radioButton_type_of_chart_standart.isChecked():
            self.update_exercise_chart()
        elif self.radioButton_type_of_chart_show_sets_chart.isChecked():
            self.show_sets_chart()
        elif self.radioButton_type_of_chart_kcal.isChecked():
            self.show_kcal_chart()
        elif self.radioButton_type_of_chart_compare_last.isChecked():
            self.on_compare_last_months()
        elif self.radioButton_type_of_chart_compare_same_months.isChecked():
            self.on_compare_same_months()

    def _update_charts_avif(self) -> None:
        """Update AVIF for charts list view selection."""
        exercise_name = self._get_selected_chart_exercise()
        if exercise_name:
            self._load_exercise_avif(exercise_name, "charts")

    def _update_comboboxes(
        self,
        *,
        selected_exercise: str | None = None,
        selected_type: str | None = None,
    ) -> None:
        """Refresh exercise list and type combo-box (optionally keep a selection).

        Args:

        - `selected_exercise` (`str | None`): Exercise to keep selected. Defaults to `None`.
        - `selected_type` (`str | None`): Exercise type to keep selected. Defaults to `None`.

        """
        if not self._validate_database_connection():
            print("Database manager not available or connection not open")
            return

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            exercises = self.db_manager.get_exercises_by_frequency(500)

            # Block signals during model update
            selection_model = self.listView_exercises.selectionModel()
            if selection_model:
                selection_model.blockSignals(True)  # noqa: FBT003

            # Update exercises list model
            if self.exercises_list_model is not None:
                self.exercises_list_model.clear()
                for exercise in exercises:
                    # Get today's goal info for this exercise
                    goal_info = self._get_exercise_today_goal_info(exercise)

                    # Create display text with goal info if available
                    display_text = f"{exercise} {goal_info}" if goal_info else exercise
                    item = QStandardItem(display_text)

                    icon = self._get_exercise_icon(exercise)
                    if icon is not None and not icon.isNull():
                        item.setIcon(icon)

                    # Store original exercise name in item data for later retrieval
                    item.setData(exercise, Qt.UserRole)
                    self.exercises_list_model.appendRow(item)

            # Unblock signals
            if selection_model:
                selection_model.blockSignals(False)  # noqa: FBT003

            # Update comboBox_exercise_name for adding types
            self.comboBox_exercise_name.clear()
            self.comboBox_exercise_name.addItems(exercises)

            if selected_exercise and selected_exercise in exercises:
                # Select the exercise in the list view
                self._select_exercise_in_list(selected_exercise)

                if selected_type:
                    ex_id = self.db_manager.get_id("exercises", "name", selected_exercise)
                    if ex_id is not None:
                        types = self.db_manager.get_exercise_types(ex_id)
                        self.comboBox_type.clear()
                        self.comboBox_type.addItem("")
                        self.comboBox_type.addItems(types)
                        t_idx = self.comboBox_type.findText(selected_type)
                        if t_idx >= 0:
                            self.comboBox_type.setCurrentIndex(t_idx)
            # If no specific selection, select the first exercise by default
            elif exercises:
                self._select_exercise_in_list(exercises[0])

            # Update types AVIF after combobox update
            self._update_types_avif()

        except Exception as e:
            print(f"Error updating comboboxes: {e}")

    def _update_exercises_avif(self) -> None:
        """Update AVIF for exercises table selection."""
        exercise_name = self._get_selected_exercise_from_table("exercises")
        if isinstance(exercise_name, str):
            self._load_exercise_avif(exercise_name, "exercises")

    def _update_form_from_process_selection(self, _exercise_name: str, type_name: str, value_str: str) -> None:
        """Update form fields after process selection change.

        Args:

        - `_exercise_name` (`str`): Name of the selected exercise.
        - `type_name` (`str`): Type of the selected exercise.
        - `value_str` (`str`): Value as string from the selected record.

        """
        try:
            # Update spinBox_count with the selected value
            try:
                value = int(float(value_str))
                self.spinBox_count.setValue(value)
            except (ValueError, TypeError):
                print(f"Could not convert value '{value_str}' to int")

            # Update comboBox_type selection
            if type_name:
                type_index = self.comboBox_type.findText(type_name)
                if type_index >= 0:
                    self.comboBox_type.setCurrentIndex(type_index)
                else:
                    # If type not found, clear selection
                    self.comboBox_type.setCurrentIndex(0)
            else:
                # No type, select empty option
                self.comboBox_type.setCurrentIndex(0)

        except Exception as e:
            print(f"Error updating form from process selection: {e}")

    def _update_layout_for_window_size(self) -> None:
        """Adjust key widgets based on current window height."""
        small_window_threshold = 911
        is_small = self.height() < small_window_threshold
        if self._is_small_window_layout == is_small:
            return

        self._is_small_window_layout = is_small

        if is_small:
            new_height = max(int(self._default_label_exercise_avif_height / 2), 1)
            self.label_exercise_avif.setMinimumHeight(new_height)
            self.label_exercise_avif.setMaximumHeight(new_height)
            self.label_count_sets_today.setFont(self._small_count_sets_font)
        else:
            self.label_exercise_avif.setMinimumHeight(self._default_label_exercise_avif_min_height)
            self.label_exercise_avif.setMaximumHeight(self._default_label_exercise_avif_max_height)
            self.label_count_sets_today.setFont(self._default_count_sets_font)

        self.label_exercise_avif.updateGeometry()
        current_exercise = self.avif_data["main"]["exercise"]
        if isinstance(current_exercise, str):
            self._load_exercise_avif(current_exercise, "main")

    def _update_statistics_avif(self) -> None:
        """Update AVIF for statistics table based on current mode."""
        if self.current_statistics_mode == "check_steps":
            # Always show Steps exercise for check_steps mode
            steps_exercise_name = self._get_exercise_name_by_id(self.id_steps)
            if isinstance(steps_exercise_name, str):
                self._load_exercise_avif(steps_exercise_name, "statistics")
        elif self.current_statistics_mode == "records":
            # For records mode, use selected exercise from comboBox_records_select_exercise
            selected_exercise = self.comboBox_records_select_exercise.currentText()
            if selected_exercise:
                self._load_exercise_avif(selected_exercise, "statistics")
            else:
                # If no exercise selected in combobox, use selected exercise from table
                exercise_name = self._get_selected_exercise_from_statistics_table()
                if isinstance(exercise_name, str):
                    self._load_exercise_avif(exercise_name, "statistics")
        else:
            # For other modes, use selected exercise from statistics table
            exercise_name = self._get_selected_exercise_from_statistics_table()
            if isinstance(exercise_name, str):
                self._load_exercise_avif(exercise_name, "statistics")

    def _update_types_avif(self) -> None:
        """Update AVIF for types combobox selection."""
        exercise_name = self.comboBox_exercise_name.currentText()
        if exercise_name:
            self._load_exercise_avif(exercise_name, "types")

    def _validate_database_connection(self) -> bool:
        """Validate that database connection is available and open.

        Returns:

        - `bool`: True if database connection is valid, False otherwise.

        """
        if not self.db_manager:
            print("Database manager is None")
            return False

        if not self.db_manager.is_database_open():
            print("Database connection is not open")
            return False

        return True


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(":/assets/logo.svg"))
    win = MainWindow()
    win.tabWidget.setCurrentIndex(0)
    # Window will be shown after initialization in _finish_window_initialization
    sys.exit(app.exec())
