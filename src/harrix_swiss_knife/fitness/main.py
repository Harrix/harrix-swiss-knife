"""Fitness tracker GUI.

This module contains a single `MainWindow` class that provides a Qt-based GUI for a
SQLite data-base with exercises, exercise types, body weight and daily process
(records of performed exercises).  The code is written with readability and
static-analysis friendliness in mind (flake8-family, pylint, mypy, etc.).
"""

from __future__ import annotations

import io
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from functools import partial
from pathlib import Path

import harrix_pylib as h
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PIL import Image
from PySide6.QtCore import QDate, QDateTime, QModelIndex, QSortFilterProxyModel, Qt, QTimer
from PySide6.QtGui import QCloseEvent, QMovie, QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QApplication, QFileDialog, QMainWindow, QMessageBox, QTableView

from harrix_swiss_knife.fitness import database_manager, window

config = h.dev.load_config("config/config.json")


class MainWindow(QMainWindow, window.Ui_MainWindow):
    """Main application window for the fitness tracking application.

    This class implements the main GUI window for the fitness tracker, providing
    functionality to record exercises, weight measurements, and track progress.
    It manages database operations for storing and retrieving fitness data.

    Attributes:

    - `_SAFE_TABLES` (`frozenset[str]`): Set of table names that can be safely modified,
      containing "process", "exercises", "types", and "weight".

    - `db_manager` (`fitness_database_manager.DatabaseManager | None`): Database
      connection manager. Defaults to `None` until initialized.

    - `models` (`dict[str, QSortFilterProxyModel | None]`): Dictionary of table models keyed
      by table name. All values default to `None` until tables are loaded.

    - `table_config` (`dict[str, tuple[QTableView, str, list[str]]]`): Configuration for each
      table, mapping table names to tuples of (table view widget, model key, column headers).

    - `exercises_list_model` (`QStandardItemModel | None`): Model for the exercises list view.

    """

    _SAFE_TABLES: frozenset[str] = frozenset(
        {"process", "exercises", "types", "weight"},
    )

    def __init__(self) -> None:  # noqa: D107  (inherited from Qt widgets)
        super().__init__()
        self.setupUi(self)
        self._setup_ui()

        # Center window on screen
        screen_center = QApplication.primaryScreen().geometry().center()
        self.setGeometry(
            screen_center.x() - self.width() // 2, screen_center.y() - self.height() // 2, self.width(), self.height()
        )

        # Initialize core attributes
        self.db_manager: database_manager.DatabaseManager | None = None
        self.current_movie: QMovie | None = None

        # AVIF animation attributes
        self.avif_frames: list = []
        self.current_frame_index: int = 0
        self.avif_timer: QTimer | None = None

        # Exercise list model
        self.exercises_list_model: QStandardItemModel | None = None

        # Table models dictionary
        self.models: dict[str, QSortFilterProxyModel | None] = {
            "process": None,
            "exercises": None,
            "types": None,
            "weight": None,
        }

        # Chart configuration
        self.max_count_points_in_charts = 40
        self.id_steps = 39  # ID for steps exercise

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
                ["Exercise", "Unit of Measurement", "Type Required"],
            ),
            "types": (
                self.tableView_exercise_types,
                "types",
                ["Exercise", "Exercise Type"],
            ),
            "weight": (self.tableView_weight, "weight", ["Weight", "Date"]),
        }

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

        # Load initial AVIF animation after UI is ready
        QTimer.singleShot(100, self._load_initial_avif)

    def _auto_save_exercises_row(self, model: QStandardItemModel, row: int, row_id: str) -> None:
        """Auto-save changes to exercises table row.

        Args:
        - `model` (`QStandardItemModel`): The source model
        - `row` (`int`): Row index in the model
        - `row_id` (`str`): Database ID of the row

        """
        try:
            name = model.data(model.index(row, 0)) or ""
            unit = model.data(model.index(row, 1)) or ""
            is_type_required_str = model.data(model.index(row, 2)) or "0"

            # Validate exercise name
            if not name.strip():
                QMessageBox.warning(self, "Validation Error", "Exercise name cannot be empty")
                return

            # Convert is_type_required to boolean
            is_type_required = is_type_required_str == "1"

            # Update database using the database manager method
            if not self.db_manager.update_exercise(int(row_id), name.strip(), unit.strip(), is_type_required):
                QMessageBox.warning(self, "Database Error", "Failed to save exercise record")
            else:
                # Update related UI elements
                self._update_comboboxes()
                self.update_filter_comboboxes()

        except Exception as e:
            QMessageBox.warning(self, "Auto-save Error", f"Failed to save exercise row: {e!s}")

    def _auto_save_process_row(self, model: QStandardItemModel, row: int, row_id: str) -> None:
        """Auto-save changes to process table row.

        Args:
        - `model` (`QStandardItemModel`): The source model
        - `row` (`int`): Row index in the model
        - `row_id` (`str`): Database ID of the row

        """
        try:
            exercise = model.data(model.index(row, 0))
            type_name = model.data(model.index(row, 1))
            value_raw = model.data(model.index(row, 2))
            date = model.data(model.index(row, 3))

            # Extract value from "value unit" format
            value = value_raw.split(" ")[0] if value_raw else ""

            # Validate date format
            if not self._is_valid_date(date):
                QMessageBox.warning(self, "Validation Error", "Use YYYY-MM-DD date format")
                return

            # Get exercise ID
            ex_id = self.db_manager.get_id("exercises", "name", exercise)
            if ex_id is None:
                QMessageBox.warning(self, "Validation Error", f"Exercise '{exercise}' not found")
                return

            # Get type ID (can be -1 for no type)
            tp_id = (
                self.db_manager.get_id("types", "type", type_name, condition=f"_id_exercises = {ex_id}")
                if type_name
                else -1
            )

            # Validate numeric value
            try:
                float(value)
            except (ValueError, TypeError):
                QMessageBox.warning(self, "Validation Error", f"Invalid numeric value: {value}")
                return

            # Update database using the database manager method
            if not self.db_manager.update_process_record(int(row_id), ex_id, tp_id or -1, value, date):
                QMessageBox.warning(self, "Database Error", "Failed to save process record")

        except Exception as e:
            QMessageBox.warning(self, "Auto-save Error", f"Failed to save process row: {e!s}")

    def _auto_save_types_row(self, model: QStandardItemModel, row: int, row_id: str) -> None:
        """Auto-save changes to types table row.

        Args:
        - `model` (`QStandardItemModel`): The source model
        - `row` (`int`): Row index in the model
        - `row_id` (`str`): Database ID of the row

        """
        try:
            exercise_name = model.data(model.index(row, 0)) or ""
            type_name = model.data(model.index(row, 1)) or ""

            # Validate inputs
            if not exercise_name.strip():
                QMessageBox.warning(self, "Validation Error", "Exercise name cannot be empty")
                return

            if not type_name.strip():
                QMessageBox.warning(self, "Validation Error", "Type name cannot be empty")
                return

            # Get exercise ID
            ex_id = self.db_manager.get_id("exercises", "name", exercise_name)
            if ex_id is None:
                QMessageBox.warning(self, "Validation Error", f"Exercise '{exercise_name}' not found")
                return

            # Update database using the database manager method
            if not self.db_manager.update_exercise_type(int(row_id), ex_id, type_name.strip()):
                QMessageBox.warning(self, "Database Error", "Failed to save type record")
            else:
                # Update related UI elements
                self._update_comboboxes()
                self.update_filter_comboboxes()

        except Exception as e:
            QMessageBox.warning(self, "Auto-save Error", f"Failed to save type row: {e!s}")

    def _auto_save_weight_row(self, model: QStandardItemModel, row: int, row_id: str) -> None:
        """Auto-save changes to weight table row.

        Args:
        - `model` (`QStandardItemModel`): The source model
        - `row` (`int`): Row index in the model
        - `row_id` (`str`): Database ID of the row

        """
        try:
            weight_str = model.data(model.index(row, 0)) or ""
            date = model.data(model.index(row, 1)) or ""

            # Validate weight value
            try:
                weight_value = float(weight_str)
                if weight_value <= 0:
                    QMessageBox.warning(self, "Validation Error", "Weight must be a positive number")
                    return
            except (ValueError, TypeError):
                QMessageBox.warning(self, "Validation Error", f"Invalid weight value: {weight_str}")
                return

            # Validate date format
            if not self._is_valid_date(date):
                QMessageBox.warning(self, "Validation Error", "Use YYYY-MM-DD date format")
                return

            # Update database using the database manager method
            if not self.db_manager.update_weight_record(int(row_id), weight_value, date):
                QMessageBox.warning(self, "Database Error", "Failed to save weight record")

        except Exception as e:
            QMessageBox.warning(self, "Auto-save Error", f"Failed to save weight row: {e!s}")

    def _connect_signals(self) -> None:
        """Wire Qt widgets to their Python slots.

        Connects all UI elements to their respective handler methods, including:

        - Button click events for adding and deleting records
        - Tab change events
        - Statistics and export functionality
        - Auto-save signals for table data changes

        Note: ListView selection signal is connected later in _init_exercises_list()
        """
        self.pushButton_add.clicked.connect(self.on_add_record)
        self.spinBox_count.lineEdit().returnPressed.connect(self.pushButton_add.click)

        # Connect delete and refresh buttons for all tables
        for table_name in self.table_config:
            # Delete buttons
            delete_btn_name = "pushButton_delete" if table_name == "process" else f"pushButton_{table_name}_delete"
            delete_button = getattr(self, delete_btn_name)
            delete_button.clicked.connect(partial(self.delete_record, table_name))

            # Refresh buttons
            refresh_btn_name = "pushButton_refresh" if table_name == "process" else f"pushButton_{table_name}_refresh"
            refresh_button = getattr(self, refresh_btn_name)
            refresh_button.clicked.connect(self.update_all)

        # Add buttons
        self.pushButton_exercise_add.clicked.connect(self.on_add_exercise)
        self.pushButton_type_add.clicked.connect(self.on_add_type)
        self.pushButton_weight_add.clicked.connect(self.on_add_weight)
        self.pushButton_yesterday.clicked.connect(self.set_yesterday_date)

        # Stats & export
        self.pushButton_statistics_refresh.clicked.connect(self.on_refresh_statistics)
        self.pushButton_export_csv.clicked.connect(self.on_export_csv)

        # Tab change
        self.tabWidget.currentChanged.connect(self.on_tab_changed)

        # Weight chart signals
        self.pushButton_update_weight_chart.clicked.connect(self.update_weight_chart)
        self.pushButton_weight_last_month.clicked.connect(self.set_weight_last_month)
        self.pushButton_weight_last_year.clicked.connect(self.set_weight_last_year)
        self.pushButton_weight_all_time.clicked.connect(self.set_weight_all_time)

        # Exercise chart signals
        self.pushButton_update_chart.clicked.connect(self.update_exercise_chart)
        self.pushButton_show_sets_chart.clicked.connect(self.show_sets_chart)
        self.pushButton_chart_last_month.clicked.connect(self.set_chart_last_month)
        self.pushButton_chart_last_year.clicked.connect(self.set_chart_last_year)
        self.pushButton_chart_all_time.clicked.connect(self.set_chart_all_time)
        self.comboBox_chart_exercise.currentIndexChanged.connect(self.update_chart_type_combobox)

        # Filter signals
        self.comboBox_filter_exercise.currentIndexChanged.connect(self.update_filter_type_combobox)
        self.pushButton_apply_filter.clicked.connect(self.apply_filter)
        self.pushButton_clear_filter.clicked.connect(self.clear_filter)

    def _connect_table_auto_save_signals(self) -> None:
        """Connect dataChanged signals for auto-save functionality.

        This method should be called after models are created and set to table views.
        """
        # Connect auto-save signals for each table
        if self.models["process"]:
            self.models["process"].sourceModel().dataChanged.connect(
                lambda top_left, bottom_right: self._on_table_data_changed("process", top_left, bottom_right)
            )

        if self.models["exercises"]:
            self.models["exercises"].sourceModel().dataChanged.connect(
                lambda top_left, bottom_right: self._on_table_data_changed("exercises", top_left, bottom_right)
            )

        if self.models["types"]:
            self.models["types"].sourceModel().dataChanged.connect(
                lambda top_left, bottom_right: self._on_table_data_changed("types", top_left, bottom_right)
            )

        if self.models["weight"]:
            self.models["weight"].sourceModel().dataChanged.connect(
                lambda top_left, bottom_right: self._on_table_data_changed("weight", top_left, bottom_right)
            )

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

    def _format_chart_x_axis(self, ax: plt.Axes, dates: list, period: str) -> None:
        """Format x-axis for exercise charts based on period and data range."""
        if not dates:
            return

        from matplotlib.ticker import MaxNLocator

        days_in_month = 31
        days_in_year = 365

        if period == "Days":
            # Limit to max 10-15 ticks
            ax.xaxis.set_major_locator(MaxNLocator(nbins=10, prune="both"))

            date_range = (max(dates) - min(dates)).days
            if date_range <= days_in_month or date_range <= days_in_year:
                ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
            else:
                ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))

        elif period == "Months":
            ax.xaxis.set_major_locator(MaxNLocator(nbins=12, prune="both"))
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))

        elif period == "Years":
            ax.xaxis.set_major_locator(MaxNLocator(nbins=10, prune="both"))
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

        # Rotate date labels for better readability
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha="right")

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
        return item.text() if item else None

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

    def _get_last_weight(self) -> float:
        """Get the last recorded weight value from database."""
        initial_weight = 89.0
        if not self.db_manager or not self.db_manager.is_database_open():
            print("Database manager not available or connection not open")
            return initial_weight

        try:
            last_weight = self.db_manager.get_last_weight()
        except Exception as e:
            print(f"Error getting last weight: {e}")
            return initial_weight
        else:
            return last_weight if last_weight is not None else initial_weight

    def _group_exercise_data_by_period(self, rows: list, period: str) -> dict:
        """Group exercise data by the specified period (Days, Months, Years)."""
        grouped = defaultdict(float)

        # Regex pattern for YYYY-MM-DD format
        date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")

        for date_str, value_str in rows:
            # Quick validation without exceptions
            if not date_pattern.match(date_str):
                continue

            try:
                value = float(value_str)
            except (ValueError, TypeError):
                continue

            # Safe date parsing with proper error handling
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            except ValueError:
                # Skip invalid dates (e.g., Feb 30, Apr 31, etc.)
                continue

            if period == "Days":
                key = date_obj
            elif period == "Months":
                key = date_obj.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            elif period == "Years":
                key = date_obj.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            else:
                key = date_obj

            grouped[key] += value

        return dict(sorted(grouped.items()))

    def _group_sets_data_by_period(self, rows: list, period: str) -> dict:
        """Group sets data by the specified period (Days, Months, Years)."""
        grouped = defaultdict(int)

        # Regex pattern for YYYY-MM-DD format
        date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")

        for date_str, count in rows:
            # Quick validation without exceptions
            if not date_pattern.match(date_str):
                continue

            try:
                set_count = int(count)
            except (ValueError, TypeError):
                continue

            # Safe date parsing with proper error handling
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            except ValueError:
                # Skip invalid dates (e.g., Feb 30, Apr 31, etc.)
                continue

            if period == "Days":
                key = date_obj
            elif period == "Months":
                key = date_obj.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            elif period == "Years":
                key = date_obj.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            else:
                key = date_obj

            grouped[key] += set_count

        return dict(sorted(grouped.items()))

    def _increment_date_after_add(self) -> None:
        """Move `date` edit one day forward unless it already shows today.

        After adding a record, this method advances the date in the date edit
        by one day to make it easier to add consecutive daily entries. If the
        current date is already set to today, it remains unchanged.
        """
        current_date = self.dateEdit.date()  # Get the current QDate from dateEdit
        today = QDate.currentDate()  # Get today's date as QDate

        # If current date is today or later, do nothing
        if current_date >= today:
            return

        # Add one day to the current date
        next_date = current_date.addDays(1)

        # Set the new date
        self.dateEdit.setDate(next_date)

    def _init_database(self) -> None:
        """Open the SQLite file from `config` (ask the user if missing).

        Attempts to open the database file specified in the configuration.
        If the file doesn't exist, prompts the user to select a database file.
        If no database is selected or an error occurs, the application exits.
        """
        filename = Path(config["sqlite_fitness"])

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
        except (OSError, RuntimeError) as exc:
            QMessageBox.critical(self, "Error", str(exc))
            sys.exit(1)

    def _init_exercise_chart_controls(self) -> None:
        """Initialize exercise chart controls."""
        current_date = QDate.currentDate()
        self.dateEdit_chart_from.setDate(current_date.addMonths(-1))
        self.dateEdit_chart_to.setDate(current_date)

        # Initialize exercise combobox
        self.update_chart_comboboxes()

    def _init_exercises_list(self) -> None:
        """Initialize the exercises list view with a model and connect signals."""
        self.exercises_list_model = QStandardItemModel()
        self.listView_exercises.setModel(self.exercises_list_model)

        # Initialize labels with default values
        self.label_exercise.setText("No exercise selected")
        self.label_unit_and_last_date.setText("")

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

    @staticmethod
    def _is_valid_date(date_str: str) -> bool:
        """Return `True` if `YYYY-MM-DD` formatted `date_str` is correct.

        Args:

        - `date_str` (`str`): Date string to validate.

        Returns:

        - `bool`: True if the date is in the correct format and represents a valid date.

        """
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date_str):
            return False

        try:
            datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            return False
        else:
            return True

    def _load_default_exercise_chart(self) -> None:
        """Load default exercise chart on first set to charts tab."""
        if not hasattr(self, "_charts_initialized"):
            self._charts_initialized = True

            # Set period to Months
            self.comboBox_chart_period.setCurrentText("Months")

            # Try to set exercise with _id = self.id_steps
            if self.db_manager:
                rows = self.db_manager.get_rows(f"SELECT name FROM exercises WHERE _id = {self.id_steps}")
                if rows:
                    exercise_name = rows[0][0]
                    index = self.comboBox_chart_exercise.findText(exercise_name)
                    if index >= 0:
                        self.comboBox_chart_exercise.setCurrentIndex(index)

            # Load chart with all time data
            self.set_chart_all_time()

    def _load_exercise_avif(self, exercise_name: str) -> None:
        """Load and display AVIF animation for the given exercise using Pillow with AVIF support."""
        # Stop current animation if exists
        if self.current_movie:
            self.current_movie.stop()
            self.current_movie = None

        # Stop AVIF animation if exists
        if self.avif_timer:
            self.avif_timer.stop()
            self.avif_timer = None

        self.avif_frames = []
        self.current_frame_index = 0

        # Clear label and reset alignment
        self.label_exercise_avif.clear()
        self.label_exercise_avif.setAlignment(Qt.AlignCenter)

        if not exercise_name:
            self.label_exercise_avif.setText("No exercise selected")
            return

        # Get path to AVIF
        avif_path = self._get_exercise_avif_path(exercise_name)

        if avif_path is None:
            self.label_exercise_avif.setText(f"No AVIF found for:\n{exercise_name}")
            return

        try:
            # Try Qt native first
            from PySide6.QtGui import QPixmap

            pixmap = QPixmap(str(avif_path))

            if not pixmap.isNull():
                label_size = self.label_exercise_avif.size()
                scaled_pixmap = pixmap.scaled(label_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.label_exercise_avif.setPixmap(scaled_pixmap)
                return

            # Fallback to Pillow with AVIF plugin for animation
            try:
                import pillow_avif  # noqa: F401

                # Open with Pillow
                pil_image = Image.open(avif_path)

                # Handle animated AVIF
                if hasattr(pil_image, "is_animated") and pil_image.is_animated:
                    # Extract all frames
                    self.avif_frames = []
                    label_size = self.label_exercise_avif.size()

                    for frame_index in range(pil_image.n_frames):
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
                            scaled_pixmap = pixmap.scaled(label_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                            self.avif_frames.append(scaled_pixmap)

                    if self.avif_frames:
                        # Show first frame
                        self.label_exercise_avif.setPixmap(self.avif_frames[0])

                        # Start animation timer
                        self.avif_timer = QTimer()
                        self.avif_timer.timeout.connect(self._next_avif_frame)

                        # Get frame duration (default 100ms if not available)
                        try:
                            duration = pil_image.info.get("duration", 100)
                        except Exception:
                            duration = 100

                        self.avif_timer.start(duration)
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
                        label_size = self.label_exercise_avif.size()
                        scaled_pixmap = pixmap.scaled(label_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        self.label_exercise_avif.setPixmap(scaled_pixmap)
                        return

            except ImportError as import_error:
                print(f"Import error: {import_error}")
                self.label_exercise_avif.setText(f"AVIF plugin not available:\n{exercise_name}")
                return
            except Exception as pil_error:
                print(f"Pillow error: {pil_error}")

            self.label_exercise_avif.setText(f"Cannot load AVIF:\n{exercise_name}")

        except Exception as e:
            print(f"General error: {e}")
            self.label_exercise_avif.setText(f"Error loading AVIF:\n{exercise_name}\n{e}")

    def _load_initial_avif(self) -> None:
        """Load AVIF for the first exercise after complete UI initialization."""
        current_exercise_name = self._get_current_selected_exercise()
        if current_exercise_name:
            self._load_exercise_avif(current_exercise_name)
            # Trigger the selection change to update labels
            self.on_exercise_selection_changed_list()

    def _next_avif_frame(self) -> None:
        """Show next frame in AVIF animation."""
        if not self.avif_frames:
            return

        self.current_frame_index = (self.current_frame_index + 1) % len(self.avif_frames)
        self.label_exercise_avif.setPixmap(self.avif_frames[self.current_frame_index])

    def _on_table_data_changed(self, table_name: str, top_left: QModelIndex, bottom_right: QModelIndex) -> None:
        """Handle data changes in table models and auto-save to database.

        Args:
        - `table_name` (`str`): Name of the table that was modified
        - `top_left` (`QModelIndex`): Top-left index of the changed area
        - `bottom_right` (`QModelIndex`): Bottom-right index of the changed area

        """
        if table_name not in self._SAFE_TABLES:
            return

        try:
            model = self.models[table_name].sourceModel()

            # Process each changed row
            for row in range(top_left.row(), bottom_right.row() + 1):
                row_id = model.verticalHeaderItem(row).text()

                if table_name == "process":
                    self._auto_save_process_row(model, row, row_id)
                elif table_name == "exercises":
                    self._auto_save_exercises_row(model, row, row_id)
                elif table_name == "types":
                    self._auto_save_types_row(model, row, row_id)
                elif table_name == "weight":
                    self._auto_save_weight_row(model, row, row_id)

        except Exception as e:
            QMessageBox.warning(self, "Auto-save Error", f"Failed to auto-save changes: {e!s}")

    def _select_exercise_in_list(self, exercise_name: str) -> None:
        """Select an exercise in the list view by name.

        Args:

        - `exercise_name` (`str`): Name of the exercise to select.

        """
        if not self.exercises_list_model or not exercise_name:
            return

        # Find the item with the matching exercise name
        for row in range(self.exercises_list_model.rowCount()):
            item = self.exercises_list_model.item(row)
            if item and item.text() == exercise_name:
                index = self.exercises_list_model.indexFromItem(item)
                selection_model = self.listView_exercises.selectionModel()
                if selection_model:
                    selection_model.setCurrentIndex(index, selection_model.SelectionFlag.ClearAndSelect)
                break

    def _setup_ui(self) -> None:
        # Set emoji for buttons
        self.pushButton_yesterday.setText(f"📅 {self.pushButton_yesterday.text()}")
        self.pushButton_add.setText(f"➕  {self.pushButton_add.text()}")  # noqa: RUF001
        self.pushButton_delete.setText(f"🗑️ {self.pushButton_delete.text()}")
        self.pushButton_refresh.setText(f"🔄 {self.pushButton_refresh.text()}")
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
        self.pushButton_show_sets_chart.setText(f"📈 {self.pushButton_show_sets_chart.text()}")
        self.pushButton_update_chart.setText(f"🔄 {self.pushButton_update_chart.text()}")
        self.pushButton_chart_last_month.setText(f"📅 {self.pushButton_chart_last_month.text()}")
        self.pushButton_chart_last_year.setText(f"📅 {self.pushButton_chart_last_year.text()}")
        self.pushButton_chart_all_time.setText(f"📅 {self.pushButton_chart_all_time.text()}")

        # Configure splitter proportions
        self.splitter.setStretchFactor(0, 3)  # tableView gets more space
        self.splitter.setStretchFactor(1, 1)  # listView gets less space
        self.splitter.setStretchFactor(2, 0)  # frame with fixed size

    def _update_comboboxes(
        self,
        *,
        selected_exercise: str | None = None,
        selected_type: str | None = None,
    ) -> None:
        """Refresh exercise list and type combo-box (optionally keep a selection)."""
        if not self.db_manager or not self.db_manager.is_database_open():
            print("Database manager not available or connection not open")
            return

        try:
            exercises = self.db_manager.get_exercises_by_frequency(500)

            # Block signals during model update
            selection_model = self.listView_exercises.selectionModel()
            if selection_model:
                selection_model.blockSignals(True)  # noqa: FBT003

            # Update exercises list model
            self.exercises_list_model.clear()
            for exercise in exercises:
                item = QStandardItem(exercise)
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

        except Exception as e:
            print(f"Error updating comboboxes: {e}")

    def apply_filter(self) -> None:
        """Apply combo-box/date filters to the process table."""
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

        data = [[row[0], row[1], row[2], f"{row[3]} {row[4] or 'times'}", row[5]] for row in rows]
        self.models["process"] = self._create_table_model(data, self.table_config["process"][2])
        self.tableView_process.setModel(self.models["process"])
        self.tableView_process.resizeColumnsToContents()

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
        """Handle application close event."""
        # Stop animations
        if self.current_movie:
            self.current_movie.stop()
        if self.avif_timer:
            self.avif_timer.stop()

        # Close database connection
        if self.db_manager:
            self.db_manager.close()

        event.accept()

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

        table_view, model_key, _ = self.table_config[table_name]
        model = self.models[model_key]
        if model is None:
            return

        index = table_view.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "Error", "Select a record to delete")
            return

        row = index.row()
        _id = int(model.sourceModel().verticalHeaderItem(row).text())

        # Use appropriate database manager method
        success = False
        if table_name == "process":
            success = self.db_manager.delete_process_record(_id)
        elif table_name == "exercises":
            success = self.db_manager.delete_exercise(_id)
        elif table_name == "types":
            success = self.db_manager.delete_exercise_type(_id)
        elif table_name == "weight":
            success = self.db_manager.delete_weight_record(_id)

        if success:
            self.update_all()
            self.update_sets_count_today()
        else:
            QMessageBox.warning(self, "Error", f"Deletion failed in {table_name}")

    def on_add_exercise(self) -> None:
        """Insert a new exercise using database manager."""
        exercise = self.lineEdit_exercise_name.text().strip()
        unit = self.lineEdit_exercise_unit.text().strip()

        if not exercise:
            QMessageBox.warning(self, "Error", "Enter exercise name")
            return

        # Get checkbox value
        is_type_required = self.check_box_is_type_required.isChecked()

        if self.db_manager.add_exercise(exercise, unit, is_type_required):
            self.update_all()
        else:
            QMessageBox.warning(self, "Error", "Failed to add exercise")

    def on_add_record(self) -> None:
        """Insert a new process record using database manager."""
        exercise = self._get_current_selected_exercise()
        if not exercise:
            QMessageBox.warning(self, "Error", "Please select an exercise")
            return

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
        current_date = self.dateEdit.date()
        value = str(self.spinBox_count.value())
        date_str = current_date.toString("yyyy-MM-dd")

        # Use database manager method
        if self.db_manager.add_process_record(ex_id, type_id or -1, value, date_str):
            # Apply date increment logic
            self._increment_date_after_add()

            # Update UI without resetting the date
            self.show_tables()
            self._update_comboboxes(selected_exercise=exercise, selected_type=type_name)
            self.update_filter_comboboxes()
            self.update_sets_count_today()
        else:
            QMessageBox.warning(self, "Error", "Failed to add process record")

    def on_add_type(self) -> None:
        """Insert a new exercise type using database manager."""
        exercise = self.comboBox_exercise_name.currentText()
        ex_id = self.db_manager.get_id("exercises", "name", exercise)
        if ex_id is None:
            return

        type_name = self.lineEdit_exercise_type.text().strip()
        if not type_name:
            QMessageBox.warning(self, "Error", "Enter type name")
            return

        if self.db_manager.add_exercise_type(ex_id, type_name):
            self.update_all()
        else:
            QMessageBox.warning(self, "Error", "Failed to add exercise type")

    def on_add_weight(self) -> None:
        """Insert a new weight measurement using database manager."""
        weight_value = self.doubleSpinBox_weight.value()
        weight_date = self.dateEdit_weight.date().toString("yyyy-MM-dd")

        # Validate the date
        if not self._is_valid_date(weight_date):
            QMessageBox.warning(self, "Error", "Invalid date format")
            return

        # Store current date before adding record
        current_date = self.dateEdit_weight.date()

        # Use database manager method
        if self.db_manager.add_weight_record(weight_value, weight_date):
            # Apply date increment logic similar to exercise records
            today = QDate.currentDate()

            # If current date is today or later, do nothing
            if current_date >= today:
                pass  # Keep the current date
            else:
                # Add one day to the current date
                next_date = current_date.addDays(1)
                self.dateEdit_weight.setDate(next_date)

            # Update UI without resetting the weight value
            self.show_tables()

            # Update weight chart if we're on the weight tab
            current_tab_index = self.tabWidget.currentIndex()
            weight_tab_index = 3
            if current_tab_index == weight_tab_index:
                self.update_weight_chart()
        else:
            QMessageBox.warning(self, "Error", "Failed to add weight record")

    def on_exercise_selection_changed(self) -> None:
        """Update form fields when exercise selection changes in the table.

        Synchronizes the form fields (name, unit, is_type_required checkbox)
        with the currently selected exercise in the table.
        """
        index = self.tableView_exercises.currentIndex()
        if not index.isValid():
            # Clear the fields if nothing is selected
            self.lineEdit_exercise_name.clear()
            self.lineEdit_exercise_unit.clear()
            self.check_box_is_type_required.setChecked(False)
            return

        model = self.models["exercises"]
        row = index.row()

        # Fill in the fields with data from the selected row
        name = model.data(model.index(row, 0)) or ""
        unit = model.data(model.index(row, 1)) or ""
        is_required = model.data(model.index(row, 2)) or "0"

        self.lineEdit_exercise_name.setText(name)
        self.lineEdit_exercise_unit.setText(unit)
        self.check_box_is_type_required.setChecked(is_required == "1")

    def on_exercise_selection_changed_list(self) -> None:
        """Handle exercise selection change in the list view."""
        exercise = self._get_current_selected_exercise()
        if not exercise:
            self.comboBox_type.setEnabled(False)
            self.label_exercise.setText("No exercise selected")
            self.label_unit_and_last_date.setText("")
            return

        # Check if database manager is available and connection is open
        if not self.db_manager or not self.db_manager.is_database_open():
            print("Database manager not available or connection not open")
            self.comboBox_type.setEnabled(False)
            self.label_exercise.setText("Database error")
            self.label_unit_and_last_date.setText("")
            return

        # Update exercise name label
        self.label_exercise.setText(exercise)

        # Check if a new AVIF needs to be loaded
        current_avif_exercise = getattr(self, "_current_avif_exercise", None)
        if current_avif_exercise != exercise:
            self._current_avif_exercise = exercise
            self._load_exercise_avif(exercise)

        ex_id = self.db_manager.get_id("exercises", "name", exercise)
        if ex_id is None:
            print(f"Exercise '{exercise}' not found in database")
            self.comboBox_type.setEnabled(False)
            self.label_unit_and_last_date.setText("")
            return

        # Get exercise unit
        unit = self.db_manager.get_exercise_unit(exercise)

        # Get last exercise date (regardless of type)
        last_date = self.db_manager.get_last_exercise_date(ex_id)

        # Format the combined label text
        if last_date:
            try:
                date_obj = datetime.strptime(last_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                formatted_date = date_obj.strftime("%b %d, %Y")  # e.g., "Dec 13, 2025"
                unit_text = f"{unit} (Last: {formatted_date})"
            except ValueError:
                unit_text = f"{unit} (Last: {last_date})"
        else:
            unit_text = f"{unit} (Last: Never)"

        self.label_unit_and_last_date.setText(unit_text)

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
                else:  # Other exercises - use last value
                    try:
                        value = int(float(last_value))
                        self.spinBox_count.setValue(value)
                    except (ValueError, TypeError):
                        # If conversion fails, keep default value
                        print(f"Could not convert last value '{last_value}' to int for exercise '{exercise}'")
            elif ex_id == self.id_steps:  # Steps exercise - set to 0 (empty)
                self.spinBox_count.setValue(0)

        except Exception as e:
            print(f"Error getting last exercise record for '{exercise}': {e}")
            # Continue without setting last values

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

        filename = Path(filename_str)
        model = self.models["process"].sourceModel()  # type: ignore[call-arg]
        with filename.open("w", encoding="utf-8") as file:
            headers = [model.headerData(col, Qt.Horizontal, Qt.DisplayRole) or "" for col in range(model.columnCount())]
            file.write(";".join(headers) + "\n")

            for row in range(model.rowCount()):
                row_values = [f'"{model.data(model.index(row, col)) or ""}"' for col in range(model.columnCount())]
                file.write(";".join(row_values) + "\n")

    def on_refresh_statistics(self) -> None:
        """Populate the statistics text-edit using database manager."""
        self.textEdit_statistics.clear()

        # Get statistics data using database manager
        rows = self.db_manager.get_statistics_data()

        grouped: defaultdict[str, list[list]] = defaultdict(list)
        for ex_name, tp_name, val, date in rows:
            key = f"{ex_name} {tp_name}".strip()
            grouped[key].append([ex_name, tp_name, val, date])

        today = QDateTime.currentDateTime().toString("yyyy-MM-dd")
        lines: list[str] = []

        for key, entries in grouped.items():
            entries.sort(key=lambda x: x[2], reverse=True)
            lines.append(key)
            for ex_name, tp_name, val, date in entries[:4]:
                val_str = f"{val:g}"
                msg = f"{date}: {ex_name} {tp_name} {val_str}" if tp_name else f"{date}: {ex_name} {val_str}"
                if date == today:
                    msg += " ← TODAY"
                lines.append(msg)
            lines.append("—" * 8)

        self.textEdit_statistics.setText("\n".join(lines))

    def on_tab_changed(self, index: int) -> None:
        """React to `QTabWidget` index change.

        Args:

        - `index` (`int`): The index of the newly selected tab.

        """
        index_tab_weight = 3
        index_tab_charts = 4

        if index == 0:  # Main tab
            self.update_filter_comboboxes()
        elif index == index_tab_charts:  # Exercise Chart tab
            self.update_chart_comboboxes()
            self._load_default_exercise_chart()
        elif index == index_tab_weight:
            self.set_weight_all_time()

    def on_weight_selection_changed(self) -> None:
        """Update form fields when weight selection changes in the table.

        Synchronizes the form fields (weight value and date) with the currently
        selected weight record in the table.
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
        earliest_date_str = self.db_manager.get_earliest_process_date()

        if earliest_date_str:
            earliest_date = QDate.fromString(earliest_date_str, "yyyy-MM-dd")
            self.dateEdit_chart_from.setDate(earliest_date)
        else:
            # Fallback to one year ago if no data
            current_date = QDate.currentDate()
            self.dateEdit_chart_from.setDate(current_date.addYears(-1))

        self.dateEdit_chart_to.setDate(QDate.currentDate())
        self.update_exercise_chart()

    def set_chart_last_month(self) -> None:
        """Set chart date range to last month."""
        current_date = QDate.currentDate()
        self.dateEdit_chart_from.setDate(current_date.addMonths(-1))
        self.dateEdit_chart_to.setDate(current_date)
        self.update_exercise_chart()

    def set_chart_last_year(self) -> None:
        """Set chart date range to last year."""
        current_date = QDate.currentDate()
        self.dateEdit_chart_from.setDate(current_date.addYears(-1))
        self.dateEdit_chart_to.setDate(current_date)
        self.update_exercise_chart()

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
        earliest_date_str = self.db_manager.get_earliest_weight_date()

        if earliest_date_str:
            earliest_date = QDate.fromString(earliest_date_str, "yyyy-MM-dd")
            self.dateEdit_weight_from.setDate(earliest_date)
        else:
            # Fallback to one year ago if no data
            current_date = QDate.currentDate()
            self.dateEdit_weight_from.setDate(current_date.addYears(-1))

        self.dateEdit_weight_to.setDate(QDate.currentDate())
        self.update_weight_chart()

    def set_weight_last_month(self) -> None:
        """Set weight chart date range to last month."""
        current_date = QDate.currentDate()
        self.dateEdit_weight_from.setDate(current_date.addMonths(-1))
        self.dateEdit_weight_to.setDate(current_date)
        self.update_weight_chart()

    def set_weight_last_year(self) -> None:
        """Set weight chart date range to last year."""
        current_date = QDate.currentDate()
        self.dateEdit_weight_from.setDate(current_date.addYears(-1))
        self.dateEdit_weight_to.setDate(current_date)
        self.update_weight_chart()

    def set_yesterday_date(self) -> None:
        """Set yesterday's date in the main date edit field.

        Sets the dateEdit widget to yesterday's date for convenient entry
        of exercise records from the previous day.
        """
        yesterday = QDate.currentDate().addDays(-1)
        self.dateEdit.setDate(yesterday)

    def show_sets_chart(self) -> None:
        """Show chart of total sets using database manager."""
        period = self.comboBox_chart_period.currentText()
        date_from = self.dateEdit_chart_from.date().toString("yyyy-MM-dd")
        date_to = self.dateEdit_chart_to.date().toString("yyyy-MM-dd")

        # Clear existing chart
        layout = self.verticalLayout_charts_content
        for i in reversed(range(layout.count())):
            child = layout.takeAt(i).widget()
            if child:
                child.setParent(None)

        # Get sets data using database manager
        rows = self.db_manager.get_sets_chart_data(date_from, date_to)

        if not rows:
            from PySide6.QtWidgets import QLabel

            no_data_label = QLabel("No set data found for the selected period")
            no_data_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(no_data_label)
            return

        # Group data by period
        grouped_data = self._group_sets_data_by_period(rows, period)

        if not grouped_data:
            from PySide6.QtWidgets import QLabel

            no_data_label = QLabel("No data to display")
            no_data_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(no_data_label)
            return

        # Create matplotlib figure
        fig = Figure(figsize=(12, 6), dpi=100)
        canvas = FigureCanvas(fig)

        # Create plot
        ax = fig.add_subplot(111)

        # Extract dates and values
        dates = list(grouped_data.keys())
        values = list(grouped_data.values())

        # Plot line with markers if self.max_count_points or fewer data points
        if len(values) <= self.max_count_points_in_charts:
            ax.plot(
                dates,
                values,
                "g-o",  # Green color for sets
                linewidth=2,
                alpha=0.8,
                markersize=6,
                markerfacecolor="green",
                markeredgecolor="darkgreen",
            )

            # Add value labels on points
            for _i, (date, value) in enumerate(zip(dates, values, strict=False)):
                label_text = f"{int(value)} ({date.year})" if period == "Years" else f"{int(value)}"

                ax.annotate(
                    label_text,
                    (date, value),
                    textcoords="offset points",
                    xytext=(0, 10),
                    ha="center",
                    fontsize=9,
                    alpha=0.8,
                )
        else:
            ax.plot(dates, values, "g-", linewidth=2, alpha=0.8)

        # Customize the plot
        ax.set_xlabel("Date", fontsize=12)
        ax.set_ylabel("Number of sets", fontsize=12)

        chart_title = f"Training sets ({period})"
        ax.set_title(chart_title, fontsize=14, fontweight="bold")
        ax.grid(visible=True, alpha=0.3)

        # Format x-axis dates
        self._format_chart_x_axis(ax, dates, period)

        # Add statistics
        if len(values) > 1:
            min_value = int(min(values))
            max_value = int(max(values))
            avg_value = sum(values) / len(values)
            total_value = int(sum(values))

            stats_text = f"Min: {min_value} | Max: {max_value} | Avg: {avg_value:.1f} | Total: {total_value}"
            ax.text(
                0.5,
                0.02,
                stats_text,
                transform=ax.transAxes,
                ha="center",
                va="bottom",
                fontsize=10,
                bbox={"boxstyle": "round,pad=0.3", "facecolor": "lightgreen", "alpha": 0.8},
            )

        # Adjust layout to prevent label cutoff
        fig.tight_layout()

        # Add canvas to layout
        layout.addWidget(canvas)

        # Force update
        canvas.draw()

    def show_tables(self) -> None:
        """Populate all QTableViews using database manager methods."""
        # Exercises table
        rows = self.db_manager.get_all_exercises()
        exercises_headers = ["Exercise", "Unit of Measurement", "Type Required"]
        self.models["exercises"] = self._create_table_model(rows, exercises_headers)
        self.tableView_exercises.setModel(self.models["exercises"])
        self.tableView_exercises.resizeColumnsToContents()

        # Connect selection change signal AFTER setting the model
        selection_model = self.tableView_exercises.selectionModel()
        if selection_model:
            selection_model.currentRowChanged.connect(self.on_exercise_selection_changed)

        # Process table
        rows = self.db_manager.get_all_process_records()
        process_data = [[r[0], r[1], r[2], f"{r[3]} {r[4] or 'times'}", r[5]] for r in rows]
        self.models["process"] = self._create_table_model(process_data, self.table_config["process"][2])
        self.tableView_process.setModel(self.models["process"])
        self.tableView_process.resizeColumnsToContents()

        # Types table
        rows = self.db_manager.get_all_exercise_types()
        self.models["types"] = self._create_table_model(rows, self.table_config["types"][2])
        self.tableView_exercise_types.setModel(self.models["types"])
        self.tableView_exercise_types.resizeColumnsToContents()

        # Weight table
        rows = self.db_manager.get_all_weight_records()
        self.models["weight"] = self._create_table_model(rows, self.table_config["weight"][2])
        self.tableView_weight.setModel(self.models["weight"])
        self.tableView_weight.resizeColumnsToContents()

        # Connect weight selection change signal AFTER setting the model
        weight_selection_model = self.tableView_weight.selectionModel()
        if weight_selection_model:
            weight_selection_model.currentRowChanged.connect(self.on_weight_selection_changed)

        # Connect auto-save signals after all models are created
        self._connect_table_auto_save_signals()

        # Update sets count for today
        self.update_sets_count_today()

    def update_all(
        self,
        *,
        skip_date_update: bool = False,
        preserve_selections: bool = False,
        current_exercise: str | None = None,
        current_type: str | None = None,
    ) -> None:
        """Refresh tables, list view and (optionally) dates.

        Updates all UI elements with the latest data from the database.

        Args:

        - `skip_date_update` (`bool`): If `True`, date fields won't be reset to today. Defaults to `False`.
        - `preserve_selections` (`bool`): If `True`, tries to maintain current selections. Defaults to `False`.
        - `current_exercise` (`str | None`): Exercise to keep selected. Defaults to `None`.
        - `current_type` (`str | None`): Exercise type to keep selected. Defaults to `None`.

        """
        if preserve_selections and current_exercise is None:
            current_exercise = self._get_current_selected_exercise()
            current_type = self.comboBox_type.currentText()

        self.show_tables()

        if preserve_selections and current_exercise:
            self._update_comboboxes(
                selected_exercise=current_exercise,
                selected_type=current_type,
            )
        else:
            self._update_comboboxes()

        if not skip_date_update:
            self.set_today_date()

        self.update_filter_comboboxes()

        # Clear the exercise addition form after updating
        self.lineEdit_exercise_name.clear()
        self.lineEdit_exercise_unit.clear()
        self.check_box_is_type_required.setChecked(False)

        # Load AVIF for the currently selected exercise
        current_exercise_name = self._get_current_selected_exercise()
        if current_exercise_name:
            self._load_exercise_avif(current_exercise_name)

    def update_chart_comboboxes(self) -> None:
        """Update exercise and type comboboxes for charts."""
        # Update exercise combobox
        exercises = self.db_manager.get_items("exercises", "name")

        self.comboBox_chart_exercise.blockSignals(True)  # noqa: FBT003
        self.comboBox_chart_exercise.clear()
        if exercises:
            self.comboBox_chart_exercise.addItems(exercises)
        self.comboBox_chart_exercise.blockSignals(False)  # noqa: FBT003

        # Update type combobox
        self.update_chart_type_combobox()

    def update_chart_type_combobox(self) -> None:
        """Update chart type combobox based on selected exercise."""
        self.comboBox_chart_type.clear()
        self.comboBox_chart_type.addItem("All types")

        exercise = self.comboBox_chart_exercise.currentText()
        if exercise:
            ex_id = self.db_manager.get_id("exercises", "name", exercise)
            if ex_id is not None:
                types = self.db_manager.get_exercise_types(ex_id)
                self.comboBox_chart_type.addItems(types)

    def update_exercise_chart(self) -> None:
        """Update the exercise chart using database manager."""
        exercise = self.comboBox_chart_exercise.currentText()
        exercise_type = self.comboBox_chart_type.currentText()
        period = self.comboBox_chart_period.currentText()
        date_from = self.dateEdit_chart_from.date().toString("yyyy-MM-dd")
        date_to = self.dateEdit_chart_to.date().toString("yyyy-MM-dd")

        # Clear existing chart
        layout = self.verticalLayout_charts_content
        for i in reversed(range(layout.count())):
            child = layout.takeAt(i).widget()
            if child:
                child.setParent(None)

        if not exercise:
            from PySide6.QtWidgets import QLabel

            no_data_label = QLabel("Please select an exercise")
            no_data_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(no_data_label)
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

        if not rows:
            from PySide6.QtWidgets import QLabel

            no_data_label = QLabel("No data found for the selected filters")
            no_data_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(no_data_label)
            return

        # Group data by period
        grouped_data = self._group_exercise_data_by_period(rows, period)

        if not grouped_data:
            from PySide6.QtWidgets import QLabel

            no_data_label = QLabel("No data to display")
            no_data_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(no_data_label)
            return

        # Create matplotlib figure
        fig = Figure(figsize=(12, 6), dpi=100)
        canvas = FigureCanvas(fig)

        # Create plot
        ax = fig.add_subplot(111)

        # Extract dates and values
        dates = list(grouped_data.keys())
        values = list(grouped_data.values())

        # Plot line with markers if self.max_count_points or fewer data points
        if len(values) <= self.max_count_points_in_charts:
            ax.plot(
                dates,
                values,
                "b-o",
                linewidth=2,
                alpha=0.8,
                markersize=6,
                markerfacecolor="blue",
                markeredgecolor="darkblue",
            )

            # Add value labels on points
            for _i, (date, value) in enumerate(zip(dates, values, strict=False)):
                label_text = f"{value:.1f} ({date.year})" if period == "Years" else f"{value:.1f}"

                ax.annotate(
                    label_text,
                    (date, value),
                    textcoords="offset points",
                    xytext=(0, 10),
                    ha="center",
                    fontsize=9,
                    alpha=0.8,
                )
        else:
            ax.plot(dates, values, "b-", linewidth=2, alpha=0.8)

        # Customize the plot
        ax.set_xlabel("Date", fontsize=12)

        # Set Y-axis label with unit
        y_label = f"Total Value ({exercise_unit})" if exercise_unit else "Total Value"
        ax.set_ylabel(y_label, fontsize=12)

        chart_title = f"{exercise}"
        if exercise_type and exercise_type != "All types":
            chart_title += f" - {exercise_type}"
        chart_title += f" ({period})"

        ax.set_title(chart_title, fontsize=14, fontweight="bold")
        ax.grid(visible=True, alpha=0.3)

        # Format x-axis dates
        self._format_chart_x_axis(ax, dates, period)

        # Add statistics
        if len(values) > 1:
            min_value = min(values)
            max_value = max(values)
            avg_value = sum(values) / len(values)
            total_value = sum(values)

            # Include unit in statistics if available
            unit_suffix = f" {exercise_unit}" if exercise_unit else ""
            stats_text = (
                f"Min: {min_value:.1f}{unit_suffix} | Max: {max_value:.1f}{unit_suffix} | "
                f"Avg: {avg_value:.1f}{unit_suffix} | Total: {total_value:.1f}{unit_suffix}"
            )
            ax.text(
                0.5,
                0.02,
                stats_text,
                transform=ax.transAxes,
                ha="center",
                va="bottom",
                fontsize=10,
                bbox={"boxstyle": "round,pad=0.3", "facecolor": "lightgray", "alpha": 0.8},
            )

        # Adjust layout to prevent label cutoff
        fig.tight_layout()

        # Add canvas to layout
        layout.addWidget(canvas)

        # Force update
        canvas.draw()

    def update_filter_comboboxes(self) -> None:
        """Refresh `exercise` and `type` combo-boxes in the filter group.

        Updates the exercise and type comboboxes in the filter section with
        the latest data from the database, attempting to preserve the current
        selections.
        """
        current_exercise = self.comboBox_filter_exercise.currentText()

        self.comboBox_filter_exercise.blockSignals(True)  # noqa: FBT003
        self.comboBox_filter_exercise.clear()
        self.comboBox_filter_exercise.addItem("")  # all exercises
        self.comboBox_filter_exercise.addItems(
            self.db_manager.get_items("exercises", "name"),
        )
        if current_exercise:
            idx = self.comboBox_filter_exercise.findText(current_exercise)
            if idx >= 0:
                self.comboBox_filter_exercise.setCurrentIndex(idx)
        self.comboBox_filter_exercise.blockSignals(False)  # noqa: FBT003

        self.update_filter_type_combobox()

    def update_filter_type_combobox(self) -> None:
        """Populate `type` filter based on the `exercise` filter selection.

        Updates the exercise type combobox in the filter section based on the
        currently selected exercise, attempting to preserve the current type
        selection if possible.
        """
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

    def update_sets_count_today(self) -> None:
        """Update the label showing count of sets done today."""
        if not self.db_manager or not self.db_manager.is_database_open():
            self.label_count_sets_today.setText("0")
            return

        try:
            count = self.db_manager.get_sets_count_today()
            self.label_count_sets_today.setText(str(count))
        except Exception as e:
            print(f"Error getting sets count for today: {e}")
            self.label_count_sets_today.setText("0")

    def update_weight_chart(self) -> None:
        """Update the weight chart using database manager."""
        date_from = self.dateEdit_weight_from.date().toString("yyyy-MM-dd")
        date_to = self.dateEdit_weight_to.date().toString("yyyy-MM-dd")

        # Clear existing chart
        layout = self.verticalLayout_weight_chart_content
        for i in reversed(range(layout.count())):
            child = layout.takeAt(i).widget()
            if child:
                child.setParent(None)

        # Get weight data using database manager
        rows = self.db_manager.get_weight_chart_data(date_from, date_to)

        if not rows:
            from PySide6.QtWidgets import QLabel

            no_data_label = QLabel("No weight data found for the selected period")
            no_data_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(no_data_label)
            return

        # Create matplotlib figure
        fig = Figure(figsize=(12, 6), dpi=100)
        canvas = FigureCanvas(fig)

        # Parse data
        weights = [row[0] for row in rows]
        dates = [datetime.strptime(row[1], "%Y-%m-%d").replace(tzinfo=timezone.utc) for row in rows]

        # Create plot
        ax = fig.add_subplot(111)

        # Plot line with markers if self.max_count_points or fewer data points
        if len(weights) <= self.max_count_points_in_charts:
            ax.plot(
                dates,
                weights,
                "b-o",
                linewidth=2,
                alpha=0.8,
                markersize=6,
                markerfacecolor="blue",
                markeredgecolor="darkblue",
            )

            # Add value labels on points
            for _i, (date, weight) in enumerate(zip(dates, weights, strict=False)):
                ax.annotate(
                    f"{weight:.1f}",
                    (date, weight),
                    textcoords="offset points",
                    xytext=(0, 10),
                    ha="center",
                    fontsize=9,
                    alpha=0.8,
                )
        else:
            ax.plot(
                dates,
                weights,
                "b-",
                linewidth=2,
                alpha=0.8,
            )

        # Customize the plot
        ax.set_xlabel("Date", fontsize=12)
        ax.set_ylabel("Weight (kg)", fontsize=12)
        ax.set_title("Weight Progress", fontsize=14, fontweight="bold")
        ax.grid(visible=True, alpha=0.3)

        # Add more detailed Y-axis grid
        from matplotlib.ticker import MultipleLocator

        ax.yaxis.set_major_locator(MultipleLocator(1))  # Major divisions every 1 kg
        ax.yaxis.set_minor_locator(MultipleLocator(0.5))  # Minor divisions every 0.5 kg
        ax.grid(visible=True, which="major", alpha=0.3)  # Major grid
        ax.grid(visible=True, which="minor", alpha=0.1)  # Minor grid (more transparent)

        # Define constants at the top of your file or function
        days_in_month = 31
        days_in_year = 365

        # Format x-axis dates
        if len(dates) > 0:
            date_range = (max(dates) - min(dates)).days

            if date_range <= days_in_month:  # Less than a month
                ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(dates) // 10)))
                ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
            elif date_range <= days_in_year:  # Less than a year
                ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=max(1, len(dates) // 10)))
                ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
            else:  # More than a year
                ax.xaxis.set_major_locator(mdates.MonthLocator(interval=max(1, date_range // days_in_year)))
                ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))

        # Rotate date labels
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha="right")

        # Add statistics
        if len(weights) > 1:
            min_weight = min(weights)
            max_weight = max(weights)
            avg_weight = sum(weights) / len(weights)
            weight_change = weights[-1] - weights[0]

            stats_text = (
                f"Min: {min_weight:.1f} kg | Max: {max_weight:.1f} kg | "
                f"Avg: {avg_weight:.1f} kg | Change: {weight_change:+.1f} kg"
            )
            ax.text(
                0.5,
                0.02,
                stats_text,
                transform=ax.transAxes,
                ha="center",
                va="bottom",
                fontsize=10,
                bbox={"boxstyle": "round,pad=0.3", "facecolor": "lightgray", "alpha": 0.8},
            )

        # Adjust layout to prevent label cutoff
        fig.tight_layout()

        # Add canvas to layout
        layout.addWidget(canvas)

        # Force update
        canvas.draw()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.tabWidget.setCurrentIndex(0)
    win.show()
    sys.exit(app.exec())
