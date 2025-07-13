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
  - [⚙️ Method `apply_filter`](#%EF%B8%8F-method-apply_filter)
  - [⚙️ Method `clear_filter`](#%EF%B8%8F-method-clear_filter)
  - [⚙️ Method `closeEvent`](#%EF%B8%8F-method-closeevent)
  - [⚙️ Method `delete_record`](#%EF%B8%8F-method-delete_record)
  - [⚙️ Method `generate_pastel_colors_mathematical`](#%EF%B8%8F-method-generate_pastel_colors_mathematical)
  - [⚙️ Method `keyPressEvent`](#%EF%B8%8F-method-keypressevent)
  - [⚙️ Method `on_add_exercise`](#%EF%B8%8F-method-on_add_exercise)
  - [⚙️ Method `on_add_record`](#%EF%B8%8F-method-on_add_record)
  - [⚙️ Method `on_add_type`](#%EF%B8%8F-method-on_add_type)
  - [⚙️ Method `on_add_weight`](#%EF%B8%8F-method-on_add_weight)
  - [⚙️ Method `on_chart_exercise_changed`](#%EF%B8%8F-method-on_chart_exercise_changed)
  - [⚙️ Method `on_check_steps`](#%EF%B8%8F-method-on_check_steps)
  - [⚙️ Method `on_exercise_name_changed`](#%EF%B8%8F-method-on_exercise_name_changed)
  - [⚙️ Method `on_exercise_selection_changed`](#%EF%B8%8F-method-on_exercise_selection_changed)
  - [⚙️ Method `on_exercise_selection_changed_list`](#%EF%B8%8F-method-on_exercise_selection_changed_list)
  - [⚙️ Method `on_export_csv`](#%EF%B8%8F-method-on_export_csv)
  - [⚙️ Method `on_process_selection_changed`](#%EF%B8%8F-method-on_process_selection_changed)
  - [⚙️ Method `on_refresh_statistics`](#%EF%B8%8F-method-on_refresh_statistics)
  - [⚙️ Method `on_show_last_exercises`](#%EF%B8%8F-method-on_show_last_exercises)
  - [⚙️ Method `on_statistics_selection_changed`](#%EF%B8%8F-method-on_statistics_selection_changed)
  - [⚙️ Method `on_tab_changed`](#%EF%B8%8F-method-on_tab_changed)
  - [⚙️ Method `on_weight_selection_changed`](#%EF%B8%8F-method-on_weight_selection_changed)
  - [⚙️ Method `set_chart_all_time`](#%EF%B8%8F-method-set_chart_all_time)
  - [⚙️ Method `set_chart_last_month`](#%EF%B8%8F-method-set_chart_last_month)
  - [⚙️ Method `set_chart_last_year`](#%EF%B8%8F-method-set_chart_last_year)
  - [⚙️ Method `set_today_date`](#%EF%B8%8F-method-set_today_date)
  - [⚙️ Method `set_weight_all_time`](#%EF%B8%8F-method-set_weight_all_time)
  - [⚙️ Method `set_weight_last_month`](#%EF%B8%8F-method-set_weight_last_month)
  - [⚙️ Method `set_weight_last_year`](#%EF%B8%8F-method-set_weight_last_year)
  - [⚙️ Method `set_yesterday_date`](#%EF%B8%8F-method-set_yesterday_date)
  - [⚙️ Method `show_sets_chart`](#%EF%B8%8F-method-show_sets_chart)
  - [⚙️ Method `show_tables`](#%EF%B8%8F-method-show_tables)
  - [⚙️ Method `update_all`](#%EF%B8%8F-method-update_all)
  - [⚙️ Method `update_chart_comboboxes`](#%EF%B8%8F-method-update_chart_comboboxes)
  - [⚙️ Method `update_chart_type_combobox`](#%EF%B8%8F-method-update_chart_type_combobox)
  - [⚙️ Method `update_exercise_chart`](#%EF%B8%8F-method-update_exercise_chart)
  - [⚙️ Method `update_filter_comboboxes`](#%EF%B8%8F-method-update_filter_comboboxes)
  - [⚙️ Method `update_filter_type_combobox`](#%EF%B8%8F-method-update_filter_type_combobox)
  - [⚙️ Method `update_sets_count_today`](#%EF%B8%8F-method-update_sets_count_today)
  - [⚙️ Method `update_weight_chart`](#%EF%B8%8F-method-update_weight_chart)
  - [⚙️ Method `_check_for_new_records`](#%EF%B8%8F-method-_check_for_new_records)
  - [⚙️ Method `_connect_signals`](#%EF%B8%8F-method-_connect_signals)
  - [⚙️ Method `_connect_table_auto_save_signals`](#%EF%B8%8F-method-_connect_table_auto_save_signals)
  - [⚙️ Method `_connect_table_selection_signals`](#%EF%B8%8F-method-_connect_table_selection_signals)
  - [⚙️ Method `_connect_table_signals_for_table`](#%EF%B8%8F-method-_connect_table_signals_for_table)
  - [⚙️ Method `_copy_table_selection_to_clipboard`](#%EF%B8%8F-method-_copy_table_selection_to_clipboard)
  - [⚙️ Method `_create_colored_process_table_model`](#%EF%B8%8F-method-_create_colored_process_table_model)
  - [⚙️ Method `_create_colored_table_model`](#%EF%B8%8F-method-_create_colored_table_model)
  - [⚙️ Method `_create_table_model`](#%EF%B8%8F-method-_create_table_model)
  - [⚙️ Method `_dispose_models`](#%EF%B8%8F-method-_dispose_models)
  - [⚙️ Method `_get_current_selected_exercise`](#%EF%B8%8F-method-_get_current_selected_exercise)
  - [⚙️ Method `_get_exercise_avif_path`](#%EF%B8%8F-method-_get_exercise_avif_path)
  - [⚙️ Method `_get_exercise_name_by_id`](#%EF%B8%8F-method-_get_exercise_name_by_id)
  - [⚙️ Method `_get_last_weight`](#%EF%B8%8F-method-_get_last_weight)
  - [⚙️ Method `_get_selected_exercise_from_statistics_table`](#%EF%B8%8F-method-_get_selected_exercise_from_statistics_table)
  - [⚙️ Method `_get_selected_exercise_from_table`](#%EF%B8%8F-method-_get_selected_exercise_from_table)
  - [⚙️ Method `_get_selected_row_id`](#%EF%B8%8F-method-_get_selected_row_id)
  - [⚙️ Method `_init_database`](#%EF%B8%8F-method-_init_database)
  - [⚙️ Method `_init_exercise_chart_controls`](#%EF%B8%8F-method-_init_exercise_chart_controls)
  - [⚙️ Method `_init_exercises_list`](#%EF%B8%8F-method-_init_exercises_list)
  - [⚙️ Method `_init_filter_controls`](#%EF%B8%8F-method-_init_filter_controls)
  - [⚙️ Method `_init_sets_count_display`](#%EF%B8%8F-method-_init_sets_count_display)
  - [⚙️ Method `_init_weight_chart_controls`](#%EF%B8%8F-method-_init_weight_chart_controls)
  - [⚙️ Method `_init_weight_controls`](#%EF%B8%8F-method-_init_weight_controls)
  - [⚙️ Method `_load_default_exercise_chart`](#%EF%B8%8F-method-_load_default_exercise_chart)
  - [⚙️ Method `_load_default_statistics`](#%EF%B8%8F-method-_load_default_statistics)
  - [⚙️ Method `_load_exercise_avif`](#%EF%B8%8F-method-_load_exercise_avif)
  - [⚙️ Method `_load_initial_avifs`](#%EF%B8%8F-method-_load_initial_avifs)
  - [⚙️ Method `_next_avif_frame`](#%EF%B8%8F-method-_next_avif_frame)
  - [⚙️ Method `_on_table_data_changed`](#%EF%B8%8F-method-_on_table_data_changed)
  - [⚙️ Method `_refresh_table`](#%EF%B8%8F-method-_refresh_table)
  - [⚙️ Method `_select_exercise_in_list`](#%EF%B8%8F-method-_select_exercise_in_list)
  - [⚙️ Method `_setup_ui`](#%EF%B8%8F-method-_setup_ui)
  - [⚙️ Method `_show_record_congratulations`](#%EF%B8%8F-method-_show_record_congratulations)
  - [⚙️ Method `_update_charts_avif`](#%EF%B8%8F-method-_update_charts_avif)
  - [⚙️ Method `_update_comboboxes`](#%EF%B8%8F-method-_update_comboboxes)
  - [⚙️ Method `_update_exercises_avif`](#%EF%B8%8F-method-_update_exercises_avif)
  - [⚙️ Method `_update_form_from_process_selection`](#%EF%B8%8F-method-_update_form_from_process_selection)
  - [⚙️ Method `_update_statistics_avif`](#%EF%B8%8F-method-_update_statistics_avif)
  - [⚙️ Method `_update_types_avif`](#%EF%B8%8F-method-_update_types_avif)
  - [⚙️ Method `_validate_database_connection`](#%EF%B8%8F-method-_validate_database_connection)

</details>

## 🏛️ Class `MainWindow`

```python
class MainWindow(QMainWindow, window.Ui_MainWindow, TableOperations, ChartOperations, DateOperations, AutoSaveOperations, ValidationOperations)
```

Main application window for the fitness tracking application.

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

<details>
<summary>Code:</summary>

```python
class MainWindow(
    QMainWindow,
    window.Ui_MainWindow,
    TableOperations,
    ChartOperations,
    DateOperations,
    AutoSaveOperations,
    ValidationOperations,
):

    _SAFE_TABLES: frozenset[str] = frozenset(
        {"process", "exercises", "types", "weight"},
    )

    def __init__(self) -> None:  # noqa: D107  (inherited from Qt widgets)
        super().__init__()
        self.setupUi(self)
        self._setup_ui()

        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        # Center window on screen
        screen_center = QApplication.primaryScreen().geometry().center()
        self.setGeometry(
            screen_center.x() - self.width() // 2, screen_center.y() - self.height() // 2, self.width(), self.height()
        )

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

        # Table models dictionary
        self.models: dict[str, QSortFilterProxyModel | None] = {
            "process": None,
            "exercises": None,
            "types": None,
            "weight": None,
            "statistics": None,
        }

        # Chart configuration
        self.max_count_points_in_charts = 40
        self.id_steps = 39  # ID for steps exercise

        # Statistics table mode tracking
        self.current_statistics_mode = None  # 'records', 'last_exercises', 'check_steps'

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
            "statistics": (self.tableView_statistics, "statistics", ["Exercise", "Type", "Value", "Unit", "Date"]),
        }

        # Define colors for different exercises (expanded palette)
        self.exercise_colors = self.generate_pastel_colors_mathematical(50)

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

        # Configure header with mixed approach after applying filter
        header = self.tableView_process.horizontalHeader()
        # Set first columns to interactive (resizable)
        for i in range(header.count() - 1):
            header.setSectionResizeMode(i, header.ResizeMode.Interactive)
        # Set last column to stretch to fill remaining space
        header.setSectionResizeMode(header.count() - 1, header.ResizeMode.Stretch)
        # Restore default column widths for resizable columns
        self.tableView_process.setColumnWidth(0, 200)  # Exercise
        self.tableView_process.setColumnWidth(1, 150)  # Exercise Type
        self.tableView_process.setColumnWidth(2, 120)  # Quantity
        # Date column will stretch automatically

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
            elif table_name == "types":
                success = self.db_manager.delete_exercise_type(record_id)
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
    def on_add_exercise(self) -> None:
        """Insert a new exercise using database manager."""
        exercise = self.lineEdit_exercise_name.text().strip()
        unit = self.lineEdit_exercise_unit.text().strip()

        if not exercise:
            QMessageBox.warning(self, "Error", "Enter exercise name")
            return

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        # Get checkbox value
        is_type_required = self.check_box_is_type_required.isChecked()

        try:
            if self.db_manager.add_exercise(exercise, unit, is_type_required=is_type_required):
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

            if self.db_manager.add_exercise_type(ex_id, type_name):
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
    def on_chart_exercise_changed(self, _index: int = -1) -> None:
        """Handle chart exercise combobox selection change.

        Args:

        - `_index` (`int`): Index from Qt signal (ignored, but required for signal compatibility). Defaults to `-1`.

        """
        self._update_charts_avif()

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
            yesterday = datetime.now(tz=timezone.utc).date() - timedelta(days=1)

            try:
                first_date = datetime.strptime(first_date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc).date()
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
                current_date += timedelta(days=1)

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
                    date_obj = datetime.strptime(missing_date, "%Y-%m-%d").replace(tzinfo=timezone.utc).date()
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
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc).date()
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

    def on_exercise_name_changed(self, _index: int = -1) -> None:
        """Handle exercise name combobox selection change.

        Args:

        - `_index` (`int`): Index from Qt signal (ignored, but required for signal compatibility). Defaults to `-1`.

        """
        self._update_types_avif()

    def on_exercise_selection_changed(self, _current: QModelIndex, _previous: QModelIndex) -> None:
        """Update form fields when exercise selection changes in the table.

        Synchronizes the form fields (name, unit, is_type_required checkbox)
        with the currently selected exercise in the table.

        Args:

        - `_current` (`QModelIndex`): Currently selected index.
        - `_previous` (`QModelIndex`): Previously selected index.

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
        if model is None:
            return
        name = model.data(model.index(row, 0)) or ""
        unit = model.data(model.index(row, 1)) or ""
        is_required = model.data(model.index(row, 2)) or "0"

        self.lineEdit_exercise_name.setText(name)
        self.lineEdit_exercise_unit.setText(unit)
        self.check_box_is_type_required.setChecked(is_required == "1")

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
                    date_obj = datetime.strptime(last_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
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

        except Exception as e:
            print(f"Error in exercise selection changed: {e}")
            self.comboBox_type.setEnabled(False)
            self.label_unit.setText("Error loading data")
            self.label_last_date_count_today.setText("Error loading data")

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

            # Get statistics data using database manager
            rows = self.db_manager.get_statistics_data()

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

            # Calculate date one year ago
            one_year_ago = datetime.now(tz=timezone.utc) - timedelta(days=365)
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
            today = QDateTime.currentDateTime().toString("yyyy-MM-dd")
            yesterday = (QDateTime.currentDateTime().addDays(-1)).toString("yyyy-MM-dd")
            span_info = []

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

                # Determine how many rows we need (max of both groups, up to 8)
                max_rows = min(max(len(entries), len(year_entries)), 8)

                for i in range(max_rows):
                    # Get all-time data if available
                    if i < len(entries):
                        ex_name, tp_name, val, date = entries[i]
                        unit = self.db_manager.get_exercise_unit(ex_name)
                        val_str = f"{val:g}"
                        if date == today:
                            date_display = f"{date} ← 🏆TODAY 📅"
                        elif date == yesterday:
                            date_display = f"{date} ← 🏆YESTERDAY 📅"
                        else:
                            date_display = date
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
                        if year_date == today:
                            year_date_display = f"{year_date} ← 🏆TODAY 📅"
                        elif year_date == yesterday:
                            year_date_display = f"{year_date} ← 🏆YESTERDAY 📅"
                        else:
                            year_date_display = year_date
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
                    if "TODAY" in str(value) or "YESTERDAY" in str(value):
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
            today = datetime.now(tz=timezone.utc).date()
            table_data = []

            for exercise_name, last_date_str in exercise_dates:
                try:
                    last_date = datetime.strptime(last_date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc).date()
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
        index_tab_weight = 2
        index_tab_charts = 3
        index_tab_statistics = 4

        if index == 0:  # Main tab
            self.update_filter_comboboxes()
        elif index == 1:  # Exercises tab
            # Update exercises AVIF when switching to exercises tab
            self._update_exercises_avif()
            self._update_types_avif()
        elif index == index_tab_charts:  # Exercise Chart tab
            self.update_chart_comboboxes()
            self._load_default_exercise_chart()
            self._update_charts_avif()
        elif index == index_tab_weight:  # Weight tab
            self.set_weight_all_time()
        elif index == index_tab_statistics:  # Statistics tab
            self._load_default_statistics()

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
        self.update_exercise_chart()

    def set_chart_last_month(self) -> None:
        """Set chart date range to last month."""
        self._set_date_range(self.dateEdit_chart_from, self.dateEdit_chart_to, months=1)
        self.update_exercise_chart()

    def set_chart_last_year(self) -> None:
        """Set chart date range to last year."""
        self._set_date_range(self.dateEdit_chart_from, self.dateEdit_chart_to, years=1)
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
                date_obj = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
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

        if not grouped_data:
            self._show_no_data_label(self.verticalLayout_charts_content, "No data to display")
            return

        # Prepare chart data
        chart_data = list(grouped_data.items())

        # For sets chart, respect the selected date range
        # But don't extend beyond today
        today = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
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
                # Transform exercises data:
                # [id, name, unit, is_type_required] -> [name, unit, is_type_required, id, color]
                transformed_row = [row[1], row[2], str(row[3]), row[0], light_green]
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
                # Transform types data: [id, exercise_name, type_name] -> [exercise_name, type_name, id, color]
                transformed_row = [row[1], row[2], row[0], light_orange]
                types_transformed_data.append(transformed_row)

            self.models["types"] = self._create_colored_table_model(
                types_transformed_data, self.table_config["types"][2]
            )
            self.tableView_exercise_types.setModel(self.models["types"])

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

            # Get process data and transform it
            process_rows = self.db_manager.get_all_process_records()
            transformed_process_data = transform_process_data(process_rows)

            # Create process table model with coloring
            self.models["process"] = self._create_colored_process_table_model(
                transformed_process_data, self.table_config["process"][2]
            )
            self.tableView_process.setModel(self.models["process"])

            # Configure process table header - mixed approach: interactive + stretch last
            process_header = self.tableView_process.horizontalHeader()
            # Set first columns to interactive (resizable)
            for i in range(process_header.count() - 1):
                process_header.setSectionResizeMode(i, process_header.ResizeMode.Interactive)
            # Set last column to stretch to fill remaining space
            process_header.setSectionResizeMode(process_header.count() - 1, process_header.ResizeMode.Stretch)
            # Set default column widths for resizable columns
            self.tableView_process.setColumnWidth(0, 200)  # Exercise
            self.tableView_process.setColumnWidth(1, 150)  # Exercise Type
            self.tableView_process.setColumnWidth(2, 120)  # Quantity
            # Date column will stretch automatically

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
            # Type Required column will stretch automatically

            # Configure exercise types table header - mixed approach: interactive + stretch last
            exercise_types_header = self.tableView_exercise_types.horizontalHeader()
            # Set first column to interactive (resizable)
            exercise_types_header.setSectionResizeMode(0, exercise_types_header.ResizeMode.Interactive)
            # Set last column to stretch to fill remaining space
            exercise_types_header.setSectionResizeMode(1, exercise_types_header.ResizeMode.Stretch)
            # Set default width for resizable column
            self.tableView_exercise_types.setColumnWidth(0, 200)  # Exercise
            # Exercise Type column will stretch automatically

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
        """Refresh tables, list view and (optionally) dates.

        Updates all UI elements with the latest data from the database.

        Args:

        - `is_skip_date_update` (`bool`): If `True`, date fields won't be reset to today. Defaults to `False`.
        - `is_preserve_selections` (`bool`): If `True`, tries to maintain current selections. Defaults to `False`.
        - `current_exercise` (`str | None`): Exercise to keep selected. Defaults to `None`.
        - `current_type` (`str | None`): Exercise type to keep selected. Defaults to `None`.

        """
        if not self._validate_database_connection():
            print("Database connection not available for update_all")
            return

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

        # Clear the exercise addition form after updating
        self.lineEdit_exercise_name.clear()
        self.lineEdit_exercise_unit.clear()
        self.check_box_is_type_required.setChecked(False)

        # Load AVIF for the currently selected exercise
        current_exercise_name = self._get_current_selected_exercise()
        if current_exercise_name:
            self._load_exercise_avif(current_exercise_name, "main")

        # Update other AVIFs
        self._update_exercises_avif()
        self._update_types_avif()
        self._update_charts_avif()

    @requires_database(is_show_warning=False)
    def update_chart_comboboxes(self) -> None:
        """Update exercise and type comboboxes for charts."""
        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            # Update exercise combobox - sort by frequency like in comboBox_type
            exercises = self.db_manager.get_exercises_by_frequency(500)

            self.comboBox_chart_exercise.blockSignals(True)  # noqa: FBT003
            self.comboBox_chart_exercise.clear()
            if exercises:
                self.comboBox_chart_exercise.addItems(exercises)
            self.comboBox_chart_exercise.blockSignals(False)  # noqa: FBT003

            # Update type combobox
            self.update_chart_type_combobox()

        except Exception as e:
            print(f"Error updating chart comboboxes: {e}")

    @requires_database(is_show_warning=False)
    def update_chart_type_combobox(self, _index: int = -1) -> None:
        """Update chart type combobox based on selected exercise.

        Args:

        - `_index` (`int`): Index from Qt signal (ignored, but required for signal compatibility). Defaults to `-1`.

        """
        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            self.comboBox_chart_type.clear()
            self.comboBox_chart_type.addItem("All types")

            exercise = self.comboBox_chart_exercise.currentText()
            if exercise:
                ex_id = self.db_manager.get_id("exercises", "name", exercise)
                if ex_id is not None:
                    types = self.db_manager.get_exercise_types(ex_id)
                    self.comboBox_chart_type.addItems(types)

        except Exception as e:
            print(f"Error updating chart type combobox: {e}")

    @requires_database()
    def update_exercise_chart(self) -> None:
        """Update the exercise chart using database manager."""
        exercise = self.comboBox_chart_exercise.currentText()
        exercise_type = self.comboBox_chart_type.currentText()
        period = self.comboBox_chart_period.currentText()
        date_from = self.dateEdit_chart_from.date().toString("yyyy-MM-dd")
        date_to = self.dateEdit_chart_to.date().toString("yyyy-MM-dd")
        use_max_value = self.checkBox_max_value.isChecked()  # Check if max value mode is enabled

        if not exercise:
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
                date_obj = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                value = float(value_str)
                datetime_data.append((date_obj, value))
            except (ValueError, TypeError):
                continue

        if not datetime_data:
            self._show_no_data_label(self.verticalLayout_charts_content, "No data found for the selected filters")
            return

        # Group data by period with aggregation based on checkbox
        if use_max_value:
            grouped_data = self._group_data_by_period_with_max(rows, period, value_type="float")
        else:
            grouped_data = self._group_data_by_period(rows, period, value_type="float")

        if not grouped_data:
            self._show_no_data_label(self.verticalLayout_charts_content, "No data to display")
            return

        # Prepare chart data
        chart_data = list(grouped_data.items())

        # Determine the actual date range for zero filling:
        # - Start: max of (earliest exercise date, selected from date)
        # - End: min of (today, selected to date)

        earliest_exercise_date = self.db_manager.get_earliest_exercise_date(
            exercise_name=exercise, exercise_type=exercise_type if exercise_type != "All types" else None
        )

        today = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")

        # Use the later of: earliest exercise date or selected from date
        chart_date_from = max(earliest_exercise_date, date_from) if earliest_exercise_date else date_from

        # Use the earlier of: today or selected to date
        chart_date_to = min(today, date_to)

        # Build chart title with aggregation type
        aggregation_type = "Max" if use_max_value else "Total"
        chart_title = f"{exercise}"
        if exercise_type and exercise_type != "All types":
            chart_title += f" - {exercise_type}"
        chart_title += f" ({aggregation_type}, {period})"

        # Define custom statistics formatter
        def format_exercise_stats(values: list) -> str:
            min_val = min(values)
            max_val = max(values)
            avg_val = sum(values) / len(values)
            unit_suffix = f" {exercise_unit}" if exercise_unit else ""

            if use_max_value:
                # For max values, don't show total (it doesn't make sense)
                return (
                    f"Min: {min_val:.1f}{unit_suffix} | Max: {max_val:.1f}{unit_suffix} | "
                    f"Avg: {avg_val:.1f}{unit_suffix}"
                )
            # For sum values, show total
            total_val = sum(values)
            return (
                f"Min: {min_val:.1f}{unit_suffix} | Max: {max_val:.1f}{unit_suffix} | "
                f"Avg: {avg_val:.1f}{unit_suffix} | Total: {total_val:.1f}{unit_suffix}"
            )

        # Create chart configuration
        y_label = f"{aggregation_type} Value ({exercise_unit})" if exercise_unit else f"{aggregation_type} Value"

        chart_config = {
            "title": chart_title,
            "xlabel": "Date",
            "ylabel": y_label,
            "color": "blue",
            "show_stats": True,
            "period": period,
            "stats_formatter": format_exercise_stats,
            "fill_zero_periods": True,  # Enable zero filling
            "date_from": chart_date_from,  # Use calculated start date
            "date_to": chart_date_to,  # Use calculated end date
        }

        self._create_chart(self.verticalLayout_charts_content, chart_data, chart_config)

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
        chart_data = [(datetime.strptime(row[1], "%Y-%m-%d").replace(tzinfo=timezone.utc), row[0]) for row in rows]

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
            one_year_ago = datetime.now(tz=timezone.utc) - timedelta(days=365)
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

        # Stats & export
        self.pushButton_statistics_refresh.clicked.connect(self.on_refresh_statistics)
        self.pushButton_last_exercises.clicked.connect(self.on_show_last_exercises)
        self.pushButton_check_steps.clicked.connect(self.on_check_steps)
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
        self.comboBox_chart_exercise.currentIndexChanged.connect(self.on_chart_exercise_changed)

        # Filter signals
        self.comboBox_filter_exercise.currentIndexChanged.connect(self.update_filter_type_combobox)
        self.pushButton_apply_filter.clicked.connect(self.apply_filter)
        self.pushButton_clear_filter.clicked.connect(self.clear_filter)

        # Exercise name combobox for types
        self.comboBox_exercise_name.currentIndexChanged.connect(self.on_exercise_name_changed)

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

        # Connect statistics table selection
        selection_model = self.tableView_statistics.selectionModel()
        if selection_model:
            selection_model.currentRowChanged.connect(self.on_statistics_selection_changed)

        # Connect process table selection
        self._connect_table_signals_for_table("process", self.on_process_selection_changed)

        # Connect weight table selection
        self._connect_table_signals_for_table("weight", self.on_weight_selection_changed)

    def _connect_table_signals_for_table(
        self, table_name: str, selection_handler: Callable[[QModelIndex, QModelIndex], None]
    ) -> None:
        """Connect selection change signal for a specific table.

        Args:

        - `table_name` (`str`): Name of the table.
        - `selection_handler` (`Callable[[QModelIndex, QModelIndex], None]`): Handler function for selection changes.

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
        If creation fails or no database is available, prompts the user to select a database file.
        If no database is selected or an error occurs, the application exits.
        """
        filename = Path(config["sqlite_fitness"])

        if not filename.exists():
            # Try to create database from recover.sql in application directory
            app_dir = Path(__file__).parent  # Directory where this script is located
            recover_sql_path = app_dir / "recover.sql"

            if recover_sql_path.exists():
                print(f"Database not found at {filename}")
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

        # Initialize exercise combobox
        self.update_chart_comboboxes()

    def _init_exercises_list(self) -> None:
        """Initialize the exercises list view with a model and connect signals."""
        self.exercises_list_model = QStandardItemModel()
        self.listView_exercises.setModel(self.exercises_list_model)

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

    def _load_default_exercise_chart(self) -> None:
        """Load default exercise chart on first set to charts tab."""
        if not hasattr(self, "_charts_initialized"):
            self._charts_initialized = True

            if self.db_manager is None:
                print("❌ Database manager is not initialized")
                return

            # Set period to Months
            self.comboBox_chart_period.setCurrentText("Months")

            # Try to set exercise with _id = self.id_steps
            if self._validate_database_connection():
                rows = self.db_manager.get_rows(f"SELECT name FROM exercises WHERE _id = {self.id_steps}")
                if rows:
                    exercise_name = rows[0][0]
                    index = self.comboBox_chart_exercise.findText(exercise_name)
                    if index >= 0:
                        self.comboBox_chart_exercise.setCurrentIndex(index)

            # Load chart with all time data
            self.set_chart_all_time()

    def _load_default_statistics(self) -> None:
        """Load default statistics on first visit to statistics tab."""
        if not hasattr(self, "_statistics_initialized"):
            self._statistics_initialized = True
            # Automatically refresh statistics on first visit
            self.on_refresh_statistics()

    def _load_exercise_avif(self, exercise_name: str, label_key: str = "main") -> None:  # noqa: PLR0911
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

        # Stop current animation if exists
        if self.avif_data[label_key]["timer"]:
            self.avif_data[label_key]["timer"].stop()
            self.avif_data[label_key]["timer"] = None

        self.avif_data[label_key]["frames"] = []
        self.avif_data[label_key]["current_frame"] = 0
        self.avif_data[label_key]["exercise"] = exercise_name

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
                    self.avif_data[label_key]["frames"] = []
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
                            self.avif_data[label_key]["frames"].append(scaled_pixmap)

                    if self.avif_data[label_key]["frames"]:
                        # Show first frame
                        label_widget.setPixmap(self.avif_data[label_key]["frames"][0])

                        # Start animation timer
                        self.avif_data[label_key]["timer"] = QTimer()
                        self.avif_data[label_key]["timer"].timeout.connect(lambda: self._next_avif_frame(label_key))

                        # Get frame duration (default 100ms if not available)
                        try:
                            duration = pil_image.info.get("duration", 100)
                        except Exception:
                            duration = 100

                        self.avif_data[label_key]["timer"].start(duration)
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
        if current_exercise_name:
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

    def _next_avif_frame(self, label_key: str) -> None:
        """Show next frame in AVIF animation for specific label.

        Args:

        - `label_key` (`str`): Key identifying which label to update.

        """
        if not self.avif_data[label_key]["frames"]:
            return

        self.avif_data[label_key]["current_frame"] = (self.avif_data[label_key]["current_frame"] + 1) % len(
            self.avif_data[label_key]["frames"]
        )

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
            label_widget.setPixmap(self.avif_data[label_key]["frames"][self.avif_data[label_key]["current_frame"]])

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

    def _refresh_table(
        self, table_name: str, data_getter: Callable[[], Any], data_transformer: Callable[[Any], Any] | None = None
    ) -> None:
        """Refresh a table with data.

        Args:

        - `table_name` (`str`): Name of the table to refresh.
        - `data_getter` (`Callable[[], Any]`): Function to get data from database.
        - `data_transformer` (`Callable[[Any], Any] | None`): Optional function to transform raw data.
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
        """Set up additional UI elements after basic initialization."""
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
        self.pushButton_last_exercises.setText(f"📅 {self.pushButton_last_exercises.text()}")
        self.pushButton_check_steps.setText(f"👟 {self.pushButton_check_steps.text()}")
        self.pushButton_show_sets_chart.setText(f"📈 {self.pushButton_show_sets_chart.text()}")
        self.pushButton_update_chart.setText(f"🔄 {self.pushButton_update_chart.text()}")
        self.pushButton_chart_last_month.setText(f"📅 {self.pushButton_chart_last_month.text()}")
        self.pushButton_chart_last_year.setText(f"📅 {self.pushButton_chart_last_year.text()}")
        self.pushButton_chart_all_time.setText(f"📅 {self.pushButton_chart_all_time.text()}")
        self.pushButton_weight_last_month.setText(f"📅 {self.pushButton_weight_last_month.text()}")
        self.pushButton_weight_last_year.setText(f"📅 {self.pushButton_weight_last_year.text()}")
        self.pushButton_weight_all_time.setText(f"📅 {self.pushButton_weight_all_time.text()}")
        self.pushButton_update_weight_chart.setText(f"🔄 {self.pushButton_update_weight_chart.text()}")

        # Configure splitter proportions
        self.splitter.setStretchFactor(0, 3)  # tableView gets more space
        self.splitter.setStretchFactor(1, 1)  # listView gets less space
        self.splitter.setStretchFactor(2, 0)  # frame with fixed size

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

    def _update_charts_avif(self) -> None:
        """Update AVIF for charts combobox selection."""
        exercise_name = self.comboBox_chart_exercise.currentText()
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

            # Update types AVIF after combobox update
            self._update_types_avif()

        except Exception as e:
            print(f"Error updating comboboxes: {e}")

    def _update_exercises_avif(self) -> None:
        """Update AVIF for exercises table selection."""
        exercise_name = self._get_selected_exercise_from_table("exercises")
        if exercise_name:
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

    def _update_statistics_avif(self) -> None:
        """Update AVIF for statistics table based on current mode."""
        if self.current_statistics_mode == "check_steps":
            # Always show Steps exercise for check_steps mode
            steps_exercise_name = self._get_exercise_name_by_id(self.id_steps)
            if steps_exercise_name:
                self._load_exercise_avif(steps_exercise_name, "statistics")
        else:
            # For other modes, use selected exercise from statistics table
            exercise_name = self._get_selected_exercise_from_statistics_table()
            if exercise_name:
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
def __init__(self) -> None:  # noqa: D107  (inherited from Qt widgets)
        super().__init__()
        self.setupUi(self)
        self._setup_ui()

        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        # Center window on screen
        screen_center = QApplication.primaryScreen().geometry().center()
        self.setGeometry(
            screen_center.x() - self.width() // 2, screen_center.y() - self.height() // 2, self.width(), self.height()
        )

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

        # Table models dictionary
        self.models: dict[str, QSortFilterProxyModel | None] = {
            "process": None,
            "exercises": None,
            "types": None,
            "weight": None,
            "statistics": None,
        }

        # Chart configuration
        self.max_count_points_in_charts = 40
        self.id_steps = 39  # ID for steps exercise

        # Statistics table mode tracking
        self.current_statistics_mode = None  # 'records', 'last_exercises', 'check_steps'

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
            "statistics": (self.tableView_statistics, "statistics", ["Exercise", "Type", "Value", "Unit", "Date"]),
        }

        # Define colors for different exercises (expanded palette)
        self.exercise_colors = self.generate_pastel_colors_mathematical(50)

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
```

</details>

### ⚙️ Method `apply_filter`

```python
def apply_filter(self) -> None
```

Apply combo-box/date filters to the process table.

<details>
<summary>Code:</summary>

```python
def apply_filter(self) -> None:
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

        # Configure header with mixed approach after applying filter
        header = self.tableView_process.horizontalHeader()
        # Set first columns to interactive (resizable)
        for i in range(header.count() - 1):
            header.setSectionResizeMode(i, header.ResizeMode.Interactive)
        # Set last column to stretch to fill remaining space
        header.setSectionResizeMode(header.count() - 1, header.ResizeMode.Stretch)
        # Restore default column widths for resizable columns
        self.tableView_process.setColumnWidth(0, 200)  # Exercise
        self.tableView_process.setColumnWidth(1, 150)  # Exercise Type
        self.tableView_process.setColumnWidth(2, 120)  # Quantity
```

</details>

### ⚙️ Method `clear_filter`

```python
def clear_filter(self) -> None
```

Reset all process-table filters.

Clears all filter selections and resets date ranges to default values:

- Clears exercise and type selections
- Disables date filtering
- Resets date range to the last month
- Refreshes the table view

<details>
<summary>Code:</summary>

```python
def clear_filter(self) -> None:
        self.comboBox_filter_exercise.setCurrentIndex(0)
        self.comboBox_filter_type.setCurrentIndex(0)
        self.checkBox_use_date_filter.setChecked(False)

        current_date = QDateTime.currentDateTime().date()
        self.dateEdit_filter_from.setDate(current_date.addMonths(-1))
        self.dateEdit_filter_to.setDate(current_date)

        self.show_tables()
```

</details>

### ⚙️ Method `closeEvent`

```python
def closeEvent(self, event: QCloseEvent) -> None
```

Handle application close event.

Args:

- `event` (`QCloseEvent`): The close event.

<details>
<summary>Code:</summary>

```python
def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
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
```

</details>

### ⚙️ Method `delete_record`

```python
def delete_record(self, table_name: str) -> None
```

Delete selected row from table using database manager methods.

Args:

- `table_name` (`str`): Name of the table to delete from. Must be in \_SAFE_TABLES.

Raises:

- `ValueError`: If table_name is not in \_SAFE_TABLES.

<details>
<summary>Code:</summary>

```python
def delete_record(self, table_name: str) -> None:
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
            elif table_name == "types":
                success = self.db_manager.delete_exercise_type(record_id)
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
```

</details>

### ⚙️ Method `generate_pastel_colors_mathematical`

```python
def generate_pastel_colors_mathematical(self, count: int = 100) -> list[QColor]
```

Generate pastel colors using mathematical distribution.

Args:

- `count` (`int`): Number of colors to generate. Defaults to `100`.

Returns:

- `list[QColor]`: List of pastel QColor objects.

<details>
<summary>Code:</summary>

```python
def generate_pastel_colors_mathematical(self, count: int = 100) -> list[QColor]:
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
```

</details>

### ⚙️ Method `keyPressEvent`

```python
def keyPressEvent(self, event: QKeyEvent) -> None
```

Handle key press events for the main window.

Args:

- `event` (`QKeyEvent`): The key press event.

<details>
<summary>Code:</summary>

```python
def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
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
```

</details>

### ⚙️ Method `on_add_exercise`

```python
def on_add_exercise(self) -> None
```

Insert a new exercise using database manager.

<details>
<summary>Code:</summary>

```python
def on_add_exercise(self) -> None:
        exercise = self.lineEdit_exercise_name.text().strip()
        unit = self.lineEdit_exercise_unit.text().strip()

        if not exercise:
            QMessageBox.warning(self, "Error", "Enter exercise name")
            return

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        # Get checkbox value
        is_type_required = self.check_box_is_type_required.isChecked()

        try:
            if self.db_manager.add_exercise(exercise, unit, is_type_required=is_type_required):
                self.update_all()
            else:
                QMessageBox.warning(self, "Error", "Failed to add exercise")
        except Exception as e:
            QMessageBox.warning(self, "Database Error", f"Failed to add exercise: {e}")
```

</details>

### ⚙️ Method `on_add_record`

```python
def on_add_record(self) -> None
```

Insert a new process record using database manager.

<details>
<summary>Code:</summary>

```python
def on_add_record(self) -> None:
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
```

</details>

### ⚙️ Method `on_add_type`

```python
def on_add_type(self) -> None
```

Insert a new exercise type using database manager.

<details>
<summary>Code:</summary>

```python
def on_add_type(self) -> None:
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

            if self.db_manager.add_exercise_type(ex_id, type_name):
                self.update_all()
            else:
                QMessageBox.warning(self, "Error", "Failed to add exercise type")

        except Exception as e:
            QMessageBox.warning(self, "Database Error", f"Failed to add type: {e}")
```

</details>

### ⚙️ Method `on_add_weight`

```python
def on_add_weight(self) -> None
```

Insert a new weight measurement using database manager.

<details>
<summary>Code:</summary>

```python
def on_add_weight(self) -> None:
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
```

</details>

### ⚙️ Method `on_chart_exercise_changed`

```python
def on_chart_exercise_changed(self, _index: int = -1) -> None
```

Handle chart exercise combobox selection change.

Args:

- `_index` (`int`): Index from Qt signal (ignored, but required for signal compatibility). Defaults to `-1`.

<details>
<summary>Code:</summary>

```python
def on_chart_exercise_changed(self, _index: int = -1) -> None:
        self._update_charts_avif()
```

</details>

### ⚙️ Method `on_check_steps`

```python
def on_check_steps(self) -> None
```

Check for missing days and duplicate days in steps records.

<details>
<summary>Code:</summary>

```python
def on_check_steps(self) -> None:
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
            yesterday = datetime.now(tz=timezone.utc).date() - timedelta(days=1)

            try:
                first_date = datetime.strptime(first_date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc).date()
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
                current_date += timedelta(days=1)

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
                    date_obj = datetime.strptime(missing_date, "%Y-%m-%d").replace(tzinfo=timezone.utc).date()
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
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc).date()
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
```

</details>

### ⚙️ Method `on_exercise_name_changed`

```python
def on_exercise_name_changed(self, _index: int = -1) -> None
```

Handle exercise name combobox selection change.

Args:

- `_index` (`int`): Index from Qt signal (ignored, but required for signal compatibility). Defaults to `-1`.

<details>
<summary>Code:</summary>

```python
def on_exercise_name_changed(self, _index: int = -1) -> None:
        self._update_types_avif()
```

</details>

### ⚙️ Method `on_exercise_selection_changed`

```python
def on_exercise_selection_changed(self, _current: QModelIndex, _previous: QModelIndex) -> None
```

Update form fields when exercise selection changes in the table.

Synchronizes the form fields (name, unit, is_type_required checkbox)
with the currently selected exercise in the table.

Args:

- `_current` (`QModelIndex`): Currently selected index.
- `_previous` (`QModelIndex`): Previously selected index.

<details>
<summary>Code:</summary>

```python
def on_exercise_selection_changed(self, _current: QModelIndex, _previous: QModelIndex) -> None:
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
        if model is None:
            return
        name = model.data(model.index(row, 0)) or ""
        unit = model.data(model.index(row, 1)) or ""
        is_required = model.data(model.index(row, 2)) or "0"

        self.lineEdit_exercise_name.setText(name)
        self.lineEdit_exercise_unit.setText(unit)
        self.check_box_is_type_required.setChecked(is_required == "1")

        # Update exercises AVIF
        self._update_exercises_avif()
```

</details>

### ⚙️ Method `on_exercise_selection_changed_list`

```python
def on_exercise_selection_changed_list(self) -> None
```

Handle exercise selection change in the list view.

<details>
<summary>Code:</summary>

```python
def on_exercise_selection_changed_list(self) -> None:
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
                    date_obj = datetime.strptime(last_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
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

        except Exception as e:
            print(f"Error in exercise selection changed: {e}")
            self.comboBox_type.setEnabled(False)
            self.label_unit.setText("Error loading data")
            self.label_last_date_count_today.setText("Error loading data")
```

</details>

### ⚙️ Method `on_export_csv`

```python
def on_export_csv(self) -> None
```

Save current `process` view to a CSV file (semicolon-separated).

Opens a file save dialog and exports the current process table view
to a CSV file with semicolon-separated values.

<details>
<summary>Code:</summary>

```python
def on_export_csv(self) -> None:
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
```

</details>

### ⚙️ Method `on_process_selection_changed`

```python
def on_process_selection_changed(self, current: QModelIndex, _previous: QModelIndex) -> None
```

Handle process table selection change and update form fields.

Updates the form fields (exercise, quantity, type, AVIF image) based on
the currently selected process record in the table.

Args:

- `current` (`QModelIndex`): Currently selected index.
- `_previous` (`QModelIndex`): Previously selected index.

<details>
<summary>Code:</summary>

```python
def on_process_selection_changed(self, current: QModelIndex, _previous: QModelIndex) -> None:
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
```

</details>

### ⚙️ Method `on_refresh_statistics`

```python
def on_refresh_statistics(self) -> None
```

Populate the statistics table view with records data using database manager.

<details>
<summary>Code:</summary>

```python
def on_refresh_statistics(self) -> None:
        # Set current mode to records
        self.current_statistics_mode = "records"

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            # Clear any existing spans before creating new view
            self.tableView_statistics.clearSpans()

            # Get statistics data using database manager
            rows = self.db_manager.get_statistics_data()

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

            # Calculate date one year ago
            one_year_ago = datetime.now(tz=timezone.utc) - timedelta(days=365)
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
            today = QDateTime.currentDateTime().toString("yyyy-MM-dd")
            yesterday = (QDateTime.currentDateTime().addDays(-1)).toString("yyyy-MM-dd")
            span_info = []

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

                # Determine how many rows we need (max of both groups, up to 8)
                max_rows = min(max(len(entries), len(year_entries)), 8)

                for i in range(max_rows):
                    # Get all-time data if available
                    if i < len(entries):
                        ex_name, tp_name, val, date = entries[i]
                        unit = self.db_manager.get_exercise_unit(ex_name)
                        val_str = f"{val:g}"
                        if date == today:
                            date_display = f"{date} ← 🏆TODAY 📅"
                        elif date == yesterday:
                            date_display = f"{date} ← 🏆YESTERDAY 📅"
                        else:
                            date_display = date
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
                        if year_date == today:
                            year_date_display = f"{year_date} ← 🏆TODAY 📅"
                        elif year_date == yesterday:
                            year_date_display = f"{year_date} ← 🏆YESTERDAY 📅"
                        else:
                            year_date_display = year_date
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
                    if "TODAY" in str(value) or "YESTERDAY" in str(value):
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
```

</details>

### ⚙️ Method `on_show_last_exercises`

```python
def on_show_last_exercises(self) -> None
```

Show last execution dates for all exercises in the statistics table.

<details>
<summary>Code:</summary>

```python
def on_show_last_exercises(self) -> None:
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
            today = datetime.now(tz=timezone.utc).date()
            table_data = []

            for exercise_name, last_date_str in exercise_dates:
                try:
                    last_date = datetime.strptime(last_date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc).date()
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
```

</details>

### ⚙️ Method `on_statistics_selection_changed`

```python
def on_statistics_selection_changed(self, _current: QModelIndex, _previous: QModelIndex) -> None
```

Handle statistics table selection change and update AVIF.

Args:

- `_current` (`QModelIndex`): Currently selected index.
- `_previous` (`QModelIndex`): Previously selected index.

<details>
<summary>Code:</summary>

```python
def on_statistics_selection_changed(self, _current: QModelIndex, _previous: QModelIndex) -> None:
        # Only update AVIF if not in check_steps mode (since check_steps always shows Steps exercise)
        if self.current_statistics_mode != "check_steps":
            self._update_statistics_avif()
```

</details>

### ⚙️ Method `on_tab_changed`

```python
def on_tab_changed(self, index: int) -> None
```

React to `QTabWidget` index change.

Args:

- `index` (`int`): The index of the newly selected tab.

<details>
<summary>Code:</summary>

```python
def on_tab_changed(self, index: int) -> None:
        index_tab_weight = 2
        index_tab_charts = 3
        index_tab_statistics = 4

        if index == 0:  # Main tab
            self.update_filter_comboboxes()
        elif index == 1:  # Exercises tab
            # Update exercises AVIF when switching to exercises tab
            self._update_exercises_avif()
            self._update_types_avif()
        elif index == index_tab_charts:  # Exercise Chart tab
            self.update_chart_comboboxes()
            self._load_default_exercise_chart()
            self._update_charts_avif()
        elif index == index_tab_weight:  # Weight tab
            self.set_weight_all_time()
        elif index == index_tab_statistics:  # Statistics tab
            self._load_default_statistics()
```

</details>

### ⚙️ Method `on_weight_selection_changed`

```python
def on_weight_selection_changed(self, _current: QModelIndex, _previous: QModelIndex) -> None
```

Update form fields when weight selection changes in the table.

Synchronizes the form fields (weight value and date) with the currently
selected weight record in the table.

Args:

- `_current` (`QModelIndex`): Currently selected index.
- `_previous` (`QModelIndex`): Previously selected index.

<details>
<summary>Code:</summary>

```python
def on_weight_selection_changed(self, _current: QModelIndex, _previous: QModelIndex) -> None:
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
```

</details>

### ⚙️ Method `set_chart_all_time`

```python
def set_chart_all_time(self) -> None
```

Set chart date range to all available data using database manager.

<details>
<summary>Code:</summary>

```python
def set_chart_all_time(self) -> None:
        self._set_date_range(self.dateEdit_chart_from, self.dateEdit_chart_to, is_all_time=True)
        self.update_exercise_chart()
```

</details>

### ⚙️ Method `set_chart_last_month`

```python
def set_chart_last_month(self) -> None
```

Set chart date range to last month.

<details>
<summary>Code:</summary>

```python
def set_chart_last_month(self) -> None:
        self._set_date_range(self.dateEdit_chart_from, self.dateEdit_chart_to, months=1)
        self.update_exercise_chart()
```

</details>

### ⚙️ Method `set_chart_last_year`

```python
def set_chart_last_year(self) -> None
```

Set chart date range to last year.

<details>
<summary>Code:</summary>

```python
def set_chart_last_year(self) -> None:
        self._set_date_range(self.dateEdit_chart_from, self.dateEdit_chart_to, years=1)
        self.update_exercise_chart()
```

</details>

### ⚙️ Method `set_today_date`

```python
def set_today_date(self) -> None
```

Set today's date in the date edit fields and last weight value.

Sets both the main date input field (QDateEdit) and the weight date input field
(now also QDateEdit) to today's date. Also sets the weight spinbox to the last recorded weight.

<details>
<summary>Code:</summary>

```python
def set_today_date(self) -> None:
        today_qdate = QDate.currentDate()

        # Set the main QDateEdit to today's date
        self.dateEdit.setDate(today_qdate)

        # Set the weight QDateEdit to today's date
        self.dateEdit_weight.setDate(today_qdate)

        # Set the weight spinbox to the last recorded weight
        last_weight = self._get_last_weight()
        self.doubleSpinBox_weight.setValue(last_weight)
```

</details>

### ⚙️ Method `set_weight_all_time`

```python
def set_weight_all_time(self) -> None
```

Set weight chart date range to all available data using database manager.

<details>
<summary>Code:</summary>

```python
def set_weight_all_time(self) -> None:
        self._set_date_range(self.dateEdit_weight_from, self.dateEdit_weight_to, is_all_time=True)
        self.update_weight_chart()
```

</details>

### ⚙️ Method `set_weight_last_month`

```python
def set_weight_last_month(self) -> None
```

Set weight chart date range to last month.

<details>
<summary>Code:</summary>

```python
def set_weight_last_month(self) -> None:
        self._set_date_range(self.dateEdit_weight_from, self.dateEdit_weight_to, months=1)
        self.update_weight_chart()
```

</details>

### ⚙️ Method `set_weight_last_year`

```python
def set_weight_last_year(self) -> None
```

Set weight chart date range to last year.

<details>
<summary>Code:</summary>

```python
def set_weight_last_year(self) -> None:
        self._set_date_range(self.dateEdit_weight_from, self.dateEdit_weight_to, years=1)
        self.update_weight_chart()
```

</details>

### ⚙️ Method `set_yesterday_date`

```python
def set_yesterday_date(self) -> None
```

Set yesterday's date in the main date edit field.

Sets the dateEdit widget to yesterday's date for convenient entry
of exercise records from the previous day.

<details>
<summary>Code:</summary>

```python
def set_yesterday_date(self) -> None:
        yesterday = QDate.currentDate().addDays(-1)
        self.dateEdit.setDate(yesterday)
```

</details>

### ⚙️ Method `show_sets_chart`

```python
def show_sets_chart(self) -> None
```

Show chart of total sets using database manager.

<details>
<summary>Code:</summary>

```python
def show_sets_chart(self) -> None:
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
                date_obj = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
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

        if not grouped_data:
            self._show_no_data_label(self.verticalLayout_charts_content, "No data to display")
            return

        # Prepare chart data
        chart_data = list(grouped_data.items())

        # For sets chart, respect the selected date range
        # But don't extend beyond today
        today = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
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
```

</details>

### ⚙️ Method `show_tables`

```python
def show_tables(self) -> None
```

Populate all QTableViews using database manager methods.

<details>
<summary>Code:</summary>

```python
def show_tables(self) -> None:
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
                # Transform exercises data:
                # [id, name, unit, is_type_required] -> [name, unit, is_type_required, id, color]
                transformed_row = [row[1], row[2], str(row[3]), row[0], light_green]
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
                # Transform types data: [id, exercise_name, type_name] -> [exercise_name, type_name, id, color]
                transformed_row = [row[1], row[2], row[0], light_orange]
                types_transformed_data.append(transformed_row)

            self.models["types"] = self._create_colored_table_model(
                types_transformed_data, self.table_config["types"][2]
            )
            self.tableView_exercise_types.setModel(self.models["types"])

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

            # Get process data and transform it
            process_rows = self.db_manager.get_all_process_records()
            transformed_process_data = transform_process_data(process_rows)

            # Create process table model with coloring
            self.models["process"] = self._create_colored_process_table_model(
                transformed_process_data, self.table_config["process"][2]
            )
            self.tableView_process.setModel(self.models["process"])

            # Configure process table header - mixed approach: interactive + stretch last
            process_header = self.tableView_process.horizontalHeader()
            # Set first columns to interactive (resizable)
            for i in range(process_header.count() - 1):
                process_header.setSectionResizeMode(i, process_header.ResizeMode.Interactive)
            # Set last column to stretch to fill remaining space
            process_header.setSectionResizeMode(process_header.count() - 1, process_header.ResizeMode.Stretch)
            # Set default column widths for resizable columns
            self.tableView_process.setColumnWidth(0, 200)  # Exercise
            self.tableView_process.setColumnWidth(1, 150)  # Exercise Type
            self.tableView_process.setColumnWidth(2, 120)  # Quantity
            # Date column will stretch automatically

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
            # Type Required column will stretch automatically

            # Configure exercise types table header - mixed approach: interactive + stretch last
            exercise_types_header = self.tableView_exercise_types.horizontalHeader()
            # Set first column to interactive (resizable)
            exercise_types_header.setSectionResizeMode(0, exercise_types_header.ResizeMode.Interactive)
            # Set last column to stretch to fill remaining space
            exercise_types_header.setSectionResizeMode(1, exercise_types_header.ResizeMode.Stretch)
            # Set default width for resizable column
            self.tableView_exercise_types.setColumnWidth(0, 200)  # Exercise
            # Exercise Type column will stretch automatically

            # Connect selection change signals after models are set
            self._connect_table_selection_signals()

            # Connect auto-save signals after all models are created
            self._connect_table_auto_save_signals()

            # Update sets count for today
            self.update_sets_count_today()

        except Exception as e:
            print(f"Error showing tables: {e}")
            QMessageBox.warning(self, "Database Error", f"Failed to load tables: {e}")
```

</details>

### ⚙️ Method `update_all`

```python
def update_all(self) -> None
```

Refresh tables, list view and (optionally) dates.

Updates all UI elements with the latest data from the database.

Args:

- `is_skip_date_update` (`bool`): If `True`, date fields won't be reset to today. Defaults to `False`.
- `is_preserve_selections` (`bool`): If `True`, tries to maintain current selections. Defaults to `False`.
- `current_exercise` (`str | None`): Exercise to keep selected. Defaults to `None`.
- `current_type` (`str | None`): Exercise type to keep selected. Defaults to `None`.

<details>
<summary>Code:</summary>

```python
def update_all(
        self,
        *,
        is_skip_date_update: bool = False,
        is_preserve_selections: bool = False,
        current_exercise: str | None = None,
        current_type: str | None = None,
    ) -> None:
        if not self._validate_database_connection():
            print("Database connection not available for update_all")
            return

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

        # Clear the exercise addition form after updating
        self.lineEdit_exercise_name.clear()
        self.lineEdit_exercise_unit.clear()
        self.check_box_is_type_required.setChecked(False)

        # Load AVIF for the currently selected exercise
        current_exercise_name = self._get_current_selected_exercise()
        if current_exercise_name:
            self._load_exercise_avif(current_exercise_name, "main")

        # Update other AVIFs
        self._update_exercises_avif()
        self._update_types_avif()
        self._update_charts_avif()
```

</details>

### ⚙️ Method `update_chart_comboboxes`

```python
def update_chart_comboboxes(self) -> None
```

Update exercise and type comboboxes for charts.

<details>
<summary>Code:</summary>

```python
def update_chart_comboboxes(self) -> None:
        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            # Update exercise combobox - sort by frequency like in comboBox_type
            exercises = self.db_manager.get_exercises_by_frequency(500)

            self.comboBox_chart_exercise.blockSignals(True)  # noqa: FBT003
            self.comboBox_chart_exercise.clear()
            if exercises:
                self.comboBox_chart_exercise.addItems(exercises)
            self.comboBox_chart_exercise.blockSignals(False)  # noqa: FBT003

            # Update type combobox
            self.update_chart_type_combobox()

        except Exception as e:
            print(f"Error updating chart comboboxes: {e}")
```

</details>

### ⚙️ Method `update_chart_type_combobox`

```python
def update_chart_type_combobox(self, _index: int = -1) -> None
```

Update chart type combobox based on selected exercise.

Args:

- `_index` (`int`): Index from Qt signal (ignored, but required for signal compatibility). Defaults to `-1`.

<details>
<summary>Code:</summary>

```python
def update_chart_type_combobox(self, _index: int = -1) -> None:
        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            self.comboBox_chart_type.clear()
            self.comboBox_chart_type.addItem("All types")

            exercise = self.comboBox_chart_exercise.currentText()
            if exercise:
                ex_id = self.db_manager.get_id("exercises", "name", exercise)
                if ex_id is not None:
                    types = self.db_manager.get_exercise_types(ex_id)
                    self.comboBox_chart_type.addItems(types)

        except Exception as e:
            print(f"Error updating chart type combobox: {e}")
```

</details>

### ⚙️ Method `update_exercise_chart`

```python
def update_exercise_chart(self) -> None
```

Update the exercise chart using database manager.

<details>
<summary>Code:</summary>

```python
def update_exercise_chart(self) -> None:
        exercise = self.comboBox_chart_exercise.currentText()
        exercise_type = self.comboBox_chart_type.currentText()
        period = self.comboBox_chart_period.currentText()
        date_from = self.dateEdit_chart_from.date().toString("yyyy-MM-dd")
        date_to = self.dateEdit_chart_to.date().toString("yyyy-MM-dd")
        use_max_value = self.checkBox_max_value.isChecked()  # Check if max value mode is enabled

        if not exercise:
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
                date_obj = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                value = float(value_str)
                datetime_data.append((date_obj, value))
            except (ValueError, TypeError):
                continue

        if not datetime_data:
            self._show_no_data_label(self.verticalLayout_charts_content, "No data found for the selected filters")
            return

        # Group data by period with aggregation based on checkbox
        if use_max_value:
            grouped_data = self._group_data_by_period_with_max(rows, period, value_type="float")
        else:
            grouped_data = self._group_data_by_period(rows, period, value_type="float")

        if not grouped_data:
            self._show_no_data_label(self.verticalLayout_charts_content, "No data to display")
            return

        # Prepare chart data
        chart_data = list(grouped_data.items())

        # Determine the actual date range for zero filling:
        # - Start: max of (earliest exercise date, selected from date)
        # - End: min of (today, selected to date)

        earliest_exercise_date = self.db_manager.get_earliest_exercise_date(
            exercise_name=exercise, exercise_type=exercise_type if exercise_type != "All types" else None
        )

        today = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")

        # Use the later of: earliest exercise date or selected from date
        chart_date_from = max(earliest_exercise_date, date_from) if earliest_exercise_date else date_from

        # Use the earlier of: today or selected to date
        chart_date_to = min(today, date_to)

        # Build chart title with aggregation type
        aggregation_type = "Max" if use_max_value else "Total"
        chart_title = f"{exercise}"
        if exercise_type and exercise_type != "All types":
            chart_title += f" - {exercise_type}"
        chart_title += f" ({aggregation_type}, {period})"

        # Define custom statistics formatter
        def format_exercise_stats(values: list) -> str:
            min_val = min(values)
            max_val = max(values)
            avg_val = sum(values) / len(values)
            unit_suffix = f" {exercise_unit}" if exercise_unit else ""

            if use_max_value:
                # For max values, don't show total (it doesn't make sense)
                return (
                    f"Min: {min_val:.1f}{unit_suffix} | Max: {max_val:.1f}{unit_suffix} | "
                    f"Avg: {avg_val:.1f}{unit_suffix}"
                )
            # For sum values, show total
            total_val = sum(values)
            return (
                f"Min: {min_val:.1f}{unit_suffix} | Max: {max_val:.1f}{unit_suffix} | "
                f"Avg: {avg_val:.1f}{unit_suffix} | Total: {total_val:.1f}{unit_suffix}"
            )

        # Create chart configuration
        y_label = f"{aggregation_type} Value ({exercise_unit})" if exercise_unit else f"{aggregation_type} Value"

        chart_config = {
            "title": chart_title,
            "xlabel": "Date",
            "ylabel": y_label,
            "color": "blue",
            "show_stats": True,
            "period": period,
            "stats_formatter": format_exercise_stats,
            "fill_zero_periods": True,  # Enable zero filling
            "date_from": chart_date_from,  # Use calculated start date
            "date_to": chart_date_to,  # Use calculated end date
        }

        self._create_chart(self.verticalLayout_charts_content, chart_data, chart_config)
```

</details>

### ⚙️ Method `update_filter_comboboxes`

```python
def update_filter_comboboxes(self) -> None
```

Refresh `exercise` and `type` combo-boxes in the filter group.

Updates the exercise and type comboboxes in the filter section with
the latest data from the database, attempting to preserve the current
selections.

<details>
<summary>Code:</summary>

```python
def update_filter_comboboxes(self) -> None:
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
```

</details>

### ⚙️ Method `update_filter_type_combobox`

```python
def update_filter_type_combobox(self, _index: int = -1) -> None
```

Populate `type` filter based on the `exercise` filter selection.

Updates the exercise type combobox in the filter section based on the
currently selected exercise, attempting to preserve the current type
selection if possible.

Args:

- `_index` (`int`): Index from Qt signal (ignored, but required for signal compatibility). Defaults to `-1`.

<details>
<summary>Code:</summary>

```python
def update_filter_type_combobox(self, _index: int = -1) -> None:
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
```

</details>

### ⚙️ Method `update_sets_count_today`

```python
def update_sets_count_today(self) -> None
```

Update the label showing count of sets done today.

<details>
<summary>Code:</summary>

```python
def update_sets_count_today(self) -> None:
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
```

</details>

### ⚙️ Method `update_weight_chart`

```python
def update_weight_chart(self) -> None
```

Update the weight chart using database manager.

<details>
<summary>Code:</summary>

```python
def update_weight_chart(self) -> None:
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
        chart_data = [(datetime.strptime(row[1], "%Y-%m-%d").replace(tzinfo=timezone.utc), row[0]) for row in rows]

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
```

</details>

### ⚙️ Method `_check_for_new_records`

```python
def _check_for_new_records(self, ex_id: int, type_id: int, current_value: float, type_name: str) -> dict | None
```

Check if the current value would be a new all-time or yearly record.

Args:

- `ex_id` (`int`): Exercise ID.
- `type_id` (`int`): Type ID.
- `current_value` (`float`): Current value to check.
- `type_name` (`str`): Type name.

Returns:

- `dict | None`: Record information if new record is found, None otherwise.

<details>
<summary>Code:</summary>

```python
def _check_for_new_records(self, ex_id: int, type_id: int, current_value: float, type_name: str) -> dict | None:
        if not self._validate_database_connection() or self.db_manager is None:
            return None

        try:
            # Calculate date one year ago
            one_year_ago = datetime.now(tz=timezone.utc) - timedelta(days=365)
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
```

</details>

### ⚙️ Method `_connect_signals`

```python
def _connect_signals(self) -> None
```

Wire Qt widgets to their Python slots.

Connects all UI elements to their respective handler methods, including:

- Button click events for adding and deleting records
- Tab change events
- Statistics and export functionality
- Auto-save signals for table data changes

<details>
<summary>Code:</summary>

```python
def _connect_signals(self) -> None:
        self.pushButton_add.clicked.connect(self.on_add_record)
        self.spinBox_count.lineEdit().returnPressed.connect(self.pushButton_add.click)

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

        # Stats & export
        self.pushButton_statistics_refresh.clicked.connect(self.on_refresh_statistics)
        self.pushButton_last_exercises.clicked.connect(self.on_show_last_exercises)
        self.pushButton_check_steps.clicked.connect(self.on_check_steps)
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
        self.comboBox_chart_exercise.currentIndexChanged.connect(self.on_chart_exercise_changed)

        # Filter signals
        self.comboBox_filter_exercise.currentIndexChanged.connect(self.update_filter_type_combobox)
        self.pushButton_apply_filter.clicked.connect(self.apply_filter)
        self.pushButton_clear_filter.clicked.connect(self.clear_filter)

        # Exercise name combobox for types
        self.comboBox_exercise_name.currentIndexChanged.connect(self.on_exercise_name_changed)
```

</details>

### ⚙️ Method `_connect_table_auto_save_signals`

```python
def _connect_table_auto_save_signals(self) -> None
```

Connect dataChanged signals for auto-save functionality.

This method should be called after models are created and set to table views.

<details>
<summary>Code:</summary>

```python
def _connect_table_auto_save_signals(self) -> None:
        # Connect auto-save signals for each table
        for table_name in self._SAFE_TABLES:
            if self.models[table_name] is not None:
                # Use partial to properly bind table_name
                handler = partial(self._on_table_data_changed, table_name)
                model = self.models[table_name]
                if model is not None and hasattr(model, "sourceModel") and model.sourceModel() is not None:
                    model.sourceModel().dataChanged.connect(handler)
```

</details>

### ⚙️ Method `_connect_table_selection_signals`

```python
def _connect_table_selection_signals(self) -> None
```

Connect selection change signals for all tables.

<details>
<summary>Code:</summary>

```python
def _connect_table_selection_signals(self) -> None:
        # Connect exercises table selection
        self._connect_table_signals_for_table("exercises", self.on_exercise_selection_changed)

        # Connect statistics table selection
        selection_model = self.tableView_statistics.selectionModel()
        if selection_model:
            selection_model.currentRowChanged.connect(self.on_statistics_selection_changed)

        # Connect process table selection
        self._connect_table_signals_for_table("process", self.on_process_selection_changed)

        # Connect weight table selection
        self._connect_table_signals_for_table("weight", self.on_weight_selection_changed)
```

</details>

### ⚙️ Method `_connect_table_signals_for_table`

```python
def _connect_table_signals_for_table(self, table_name: str, selection_handler: Callable[[QModelIndex, QModelIndex], None]) -> None
```

Connect selection change signal for a specific table.

Args:

- `table_name` (`str`): Name of the table.
- `selection_handler` (`Callable[[QModelIndex, QModelIndex], None]`): Handler function for selection changes.

<details>
<summary>Code:</summary>

```python
def _connect_table_signals_for_table(
        self, table_name: str, selection_handler: Callable[[QModelIndex, QModelIndex], None]
    ) -> None:
        if table_name in self.table_config:
            view = self.table_config[table_name][0]
            selection_model = view.selectionModel()
            if selection_model:
                selection_model.currentRowChanged.connect(selection_handler)
```

</details>

### ⚙️ Method `_copy_table_selection_to_clipboard`

```python
def _copy_table_selection_to_clipboard(self, table_view: QTableView) -> None
```

Copy selected cells from table to clipboard as tab-separated text.

Args:

- `table_view` (`QTableView`): The table view to copy data from.

<details>
<summary>Code:</summary>

```python
def _copy_table_selection_to_clipboard(self, table_view: QTableView) -> None:
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
```

</details>

### ⚙️ Method `_create_colored_process_table_model`

```python
def _create_colored_process_table_model(self, data: list[list], headers: list[str], _id_column: int = 4) -> QSortFilterProxyModel
```

Return a proxy model filled with colored process data.

Args:

- `data` (`list[list]`): The table data with color information.
- `headers` (`list[str]`): Column header names.
- `_id_column` (`int`): Index of the ID column. Defaults to `4`.

Returns:

- `QSortFilterProxyModel`: A filterable and sortable model with colored data.

<details>
<summary>Code:</summary>

```python
def _create_colored_process_table_model(
        self,
        data: list[list],
        headers: list[str],
        _id_column: int = 4,  # ID is now at index 4 in transformed data
    ) -> QSortFilterProxyModel:
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
```

</details>

### ⚙️ Method `_create_colored_table_model`

```python
def _create_colored_table_model(self, data: list[list], headers: list[str], id_column: int = -2) -> QSortFilterProxyModel
```

Return a proxy model filled with colored table data.

Args:

- `data` (`list[list]`): The table data with color information.
- `headers` (`list[str]`): Column header names.
- `id_column` (`int`): Index of the ID column. Defaults to `-2` (second-to-last).

Returns:

- `QSortFilterProxyModel`: A filterable and sortable model with colored data.

<details>
<summary>Code:</summary>

```python
def _create_colored_table_model(
        self,
        data: list[list],
        headers: list[str],
        id_column: int = -2,
    ) -> QSortFilterProxyModel:
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
```

</details>

### ⚙️ Method `_create_table_model`

```python
def _create_table_model(self, data: list[list[str]], headers: list[str], id_column: int = 0) -> QSortFilterProxyModel
```

Return a proxy model filled with `data`.

Args:

- `data` (`list[list[str]]`): The table data as a list of rows.
- `headers` (`list[str]`): Column header names.
- `id_column` (`int`): Index of the ID column. Defaults to `0`.

Returns:

- `QSortFilterProxyModel`: A filterable and sortable model with the data.

<details>
<summary>Code:</summary>

```python
def _create_table_model(
        self,
        data: list[list[str]],
        headers: list[str],
        id_column: int = 0,
    ) -> QSortFilterProxyModel:
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
```

</details>

### ⚙️ Method `_dispose_models`

```python
def _dispose_models(self) -> None
```

Detach all models from QTableView and delete them.

<details>
<summary>Code:</summary>

```python
def _dispose_models(self) -> None:
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
```

</details>

### ⚙️ Method `_get_current_selected_exercise`

```python
def _get_current_selected_exercise(self) -> str | None
```

Get the currently selected exercise from the list view.

Returns:

- `str | None`: The name of the selected exercise, or None if nothing is selected.

<details>
<summary>Code:</summary>

```python
def _get_current_selected_exercise(self) -> str | None:
        selection_model = self.listView_exercises.selectionModel()
        if not selection_model or not self.exercises_list_model:
            return None

        current_index = selection_model.currentIndex()
        if not current_index.isValid():
            return None

        item = self.exercises_list_model.itemFromIndex(current_index)
        return item.text() if item else None
```

</details>

### ⚙️ Method `_get_exercise_avif_path`

```python
def _get_exercise_avif_path(self, exercise_name: str) -> Path | None
```

Get the path to the AVIF file for the given exercise.

Args:

- `exercise_name` (`str`): Name of the exercise.

Returns:

- `Path | None`: Path to the AVIF file if it exists, None otherwise.

<details>
<summary>Code:</summary>

```python
def _get_exercise_avif_path(self, exercise_name: str) -> Path | None:
        if not exercise_name or not self.db_manager:
            return None

        # Form path to AVIF file using exercise name directly
        db_path = Path(config["sqlite_fitness"])
        avif_dir = db_path.parent / "fitness_img"
        avif_path = avif_dir / f"{exercise_name}.avif"

        return avif_path if avif_path.exists() else None
```

</details>

### ⚙️ Method `_get_exercise_name_by_id`

```python
def _get_exercise_name_by_id(self, exercise_id: int) -> str | None
```

Get exercise name by ID.

Args:

- `exercise_id` (`int`): Exercise ID.

Returns:

- `str | None`: Exercise name or None if not found.

<details>
<summary>Code:</summary>

```python
def _get_exercise_name_by_id(self, exercise_id: int) -> str | None:
        if not self._validate_database_connection() or self.db_manager is None:
            return None

        return self.db_manager.get_exercise_name_by_id(exercise_id)
```

</details>

### ⚙️ Method `_get_last_weight`

```python
def _get_last_weight(self) -> float
```

Get the last recorded weight value from database.

Returns:

- `float`: The last recorded weight value, or 89.0 as default.

<details>
<summary>Code:</summary>

```python
def _get_last_weight(self) -> float:
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
```

</details>

### ⚙️ Method `_get_selected_exercise_from_statistics_table`

```python
def _get_selected_exercise_from_statistics_table(self) -> str | None
```

Get selected exercise name from statistics table.

Returns:

- `str | None`: Exercise name or None if nothing selected.

<details>
<summary>Code:</summary>

```python
def _get_selected_exercise_from_statistics_table(self) -> str | None:
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
```

</details>

### ⚙️ Method `_get_selected_exercise_from_table`

```python
def _get_selected_exercise_from_table(self, table_name: str) -> str | None
```

Get selected exercise name from a table.

Args:

- `table_name` (`str`): Name of the table ('exercises' or 'statistics').

Returns:

- `str | None`: Exercise name or None if nothing selected.

<details>
<summary>Code:</summary>

```python
def _get_selected_exercise_from_table(self, table_name: str) -> str | None:
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
```

</details>

### ⚙️ Method `_get_selected_row_id`

```python
def _get_selected_row_id(self, table_name: str) -> int | None
```

Get the database ID of the currently selected row.

Args:

- `table_name` (`str`): Name of the table.

Returns:

- `int | None`: Database ID of selected row or None if no selection.

<details>
<summary>Code:</summary>

```python
def _get_selected_row_id(self, table_name: str) -> int | None:
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
```

</details>

### ⚙️ Method `_init_database`

```python
def _init_database(self) -> None
```

Open the SQLite file from `config` (create from recover.sql if missing).

Attempts to open the database file specified in the configuration.
If the file doesn't exist, tries to create it from recover.sql file located
in the application directory.
If creation fails or no database is available, prompts the user to select a database file.
If no database is selected or an error occurs, the application exits.

<details>
<summary>Code:</summary>

```python
def _init_database(self) -> None:
        filename = Path(config["sqlite_fitness"])

        if not filename.exists():
            # Try to create database from recover.sql in application directory
            app_dir = Path(__file__).parent  # Directory where this script is located
            recover_sql_path = app_dir / "recover.sql"

            if recover_sql_path.exists():
                print(f"Database not found at {filename}")
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
```

</details>

### ⚙️ Method `_init_exercise_chart_controls`

```python
def _init_exercise_chart_controls(self) -> None
```

Initialize exercise chart controls.

<details>
<summary>Code:</summary>

```python
def _init_exercise_chart_controls(self) -> None:
        current_date = QDate.currentDate()
        self.dateEdit_chart_from.setDate(current_date.addMonths(-1))
        self.dateEdit_chart_to.setDate(current_date)

        # Initialize exercise combobox
        self.update_chart_comboboxes()
```

</details>

### ⚙️ Method `_init_exercises_list`

```python
def _init_exercises_list(self) -> None
```

Initialize the exercises list view with a model and connect signals.

<details>
<summary>Code:</summary>

```python
def _init_exercises_list(self) -> None:
        self.exercises_list_model = QStandardItemModel()
        self.listView_exercises.setModel(self.exercises_list_model)

        # Initialize labels with default values
        self.label_exercise.setText("No exercise selected")
        self.label_unit.setText("")
        self.label_last_date_count_today.setText("")

        # Connect selection change signal after model is set
        selection_model = self.listView_exercises.selectionModel()
        if selection_model:
            selection_model.currentChanged.connect(self.on_exercise_selection_changed_list)
```

</details>

### ⚙️ Method `_init_filter_controls`

```python
def _init_filter_controls(self) -> None
```

Prepare widgets on the `Filters` group box.

Initializes the filter controls with default values:

- Sets the date range to the last month
- Disables date filtering by default
- Connects filter-related signals to their handlers

<details>
<summary>Code:</summary>

```python
def _init_filter_controls(self) -> None:
        current_date = QDateTime.currentDateTime().date()
        self.dateEdit_filter_from.setDate(current_date.addMonths(-1))
        self.dateEdit_filter_to.setDate(current_date)

        self.checkBox_use_date_filter.setChecked(False)
```

</details>

### ⚙️ Method `_init_sets_count_display`

```python
def _init_sets_count_display(self) -> None
```

Initialize the sets count display.

<details>
<summary>Code:</summary>

```python
def _init_sets_count_display(self) -> None:
        self.update_sets_count_today()
```

</details>

### ⚙️ Method `_init_weight_chart_controls`

```python
def _init_weight_chart_controls(self) -> None
```

Initialize weight chart date controls.

<details>
<summary>Code:</summary>

```python
def _init_weight_chart_controls(self) -> None:
        current_date = QDate.currentDate()
        self.dateEdit_weight_from.setDate(current_date.addMonths(-1))
        self.dateEdit_weight_to.setDate(current_date)
```

</details>

### ⚙️ Method `_init_weight_controls`

```python
def _init_weight_controls(self) -> None
```

Initialize weight input controls with last recorded values.

<details>
<summary>Code:</summary>

```python
def _init_weight_controls(self) -> None:
        last_weight = self._get_last_weight()
        self.doubleSpinBox_weight.setValue(last_weight)
        self.dateEdit_weight.setDate(QDate.currentDate())
```

</details>

### ⚙️ Method `_load_default_exercise_chart`

```python
def _load_default_exercise_chart(self) -> None
```

Load default exercise chart on first set to charts tab.

<details>
<summary>Code:</summary>

```python
def _load_default_exercise_chart(self) -> None:
        if not hasattr(self, "_charts_initialized"):
            self._charts_initialized = True

            if self.db_manager is None:
                print("❌ Database manager is not initialized")
                return

            # Set period to Months
            self.comboBox_chart_period.setCurrentText("Months")

            # Try to set exercise with _id = self.id_steps
            if self._validate_database_connection():
                rows = self.db_manager.get_rows(f"SELECT name FROM exercises WHERE _id = {self.id_steps}")
                if rows:
                    exercise_name = rows[0][0]
                    index = self.comboBox_chart_exercise.findText(exercise_name)
                    if index >= 0:
                        self.comboBox_chart_exercise.setCurrentIndex(index)

            # Load chart with all time data
            self.set_chart_all_time()
```

</details>

### ⚙️ Method `_load_default_statistics`

```python
def _load_default_statistics(self) -> None
```

Load default statistics on first visit to statistics tab.

<details>
<summary>Code:</summary>

```python
def _load_default_statistics(self) -> None:
        if not hasattr(self, "_statistics_initialized"):
            self._statistics_initialized = True
            # Automatically refresh statistics on first visit
            self.on_refresh_statistics()
```

</details>

### ⚙️ Method `_load_exercise_avif`

```python
def _load_exercise_avif(self, exercise_name: str, label_key: str = "main") -> None
```

Load and display AVIF animation for the given exercise using Pillow with AVIF support.

Args:

- `exercise_name` (`str`): Name of the exercise to load AVIF for.
- `label_key` (`str`): Key identifying which label to update
  ('main', 'exercises', 'types', 'charts', 'statistics'). Defaults to `"main"`.

<details>
<summary>Code:</summary>

```python
def _load_exercise_avif(self, exercise_name: str, label_key: str = "main") -> None:  # noqa: PLR0911
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

        # Stop current animation if exists
        if self.avif_data[label_key]["timer"]:
            self.avif_data[label_key]["timer"].stop()
            self.avif_data[label_key]["timer"] = None

        self.avif_data[label_key]["frames"] = []
        self.avif_data[label_key]["current_frame"] = 0
        self.avif_data[label_key]["exercise"] = exercise_name

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
                    self.avif_data[label_key]["frames"] = []
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
                            self.avif_data[label_key]["frames"].append(scaled_pixmap)

                    if self.avif_data[label_key]["frames"]:
                        # Show first frame
                        label_widget.setPixmap(self.avif_data[label_key]["frames"][0])

                        # Start animation timer
                        self.avif_data[label_key]["timer"] = QTimer()
                        self.avif_data[label_key]["timer"].timeout.connect(lambda: self._next_avif_frame(label_key))

                        # Get frame duration (default 100ms if not available)
                        try:
                            duration = pil_image.info.get("duration", 100)
                        except Exception:
                            duration = 100

                        self.avif_data[label_key]["timer"].start(duration)
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
```

</details>

### ⚙️ Method `_load_initial_avifs`

```python
def _load_initial_avifs(self) -> None
```

Load AVIF for all labels after complete UI initialization.

<details>
<summary>Code:</summary>

```python
def _load_initial_avifs(self) -> None:
        # Load main exercise AVIF
        current_exercise_name = self._get_current_selected_exercise()
        if current_exercise_name:
            self._load_exercise_avif(current_exercise_name, "main")
            # Trigger the selection change to update labels
            self.on_exercise_selection_changed_list()

        # Load exercises table AVIF (first row by default)
        self._update_exercises_avif()

        # Load types combobox AVIF
        self._update_types_avif()

        # Load charts combobox AVIF
        self._update_charts_avif()
```

</details>

### ⚙️ Method `_next_avif_frame`

```python
def _next_avif_frame(self, label_key: str) -> None
```

Show next frame in AVIF animation for specific label.

Args:

- `label_key` (`str`): Key identifying which label to update.

<details>
<summary>Code:</summary>

```python
def _next_avif_frame(self, label_key: str) -> None:
        if not self.avif_data[label_key]["frames"]:
            return

        self.avif_data[label_key]["current_frame"] = (self.avif_data[label_key]["current_frame"] + 1) % len(
            self.avif_data[label_key]["frames"]
        )

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
            label_widget.setPixmap(self.avif_data[label_key]["frames"][self.avif_data[label_key]["current_frame"]])
```

</details>

### ⚙️ Method `_on_table_data_changed`

```python
def _on_table_data_changed(self, table_name: str, top_left: QModelIndex, bottom_right: QModelIndex, _roles: list | None = None) -> None
```

Handle data changes in table models and auto-save to database.

Args:

- `table_name` (`str`): Name of the table that was modified.
- `top_left` (`QModelIndex`): Top-left index of the changed area.
- `bottom_right` (`QModelIndex`): Bottom-right index of the changed area.
- `_roles` (`list | None`): List of roles that changed. Defaults to `None`.

<details>
<summary>Code:</summary>

```python
def _on_table_data_changed(
        self, table_name: str, top_left: QModelIndex, bottom_right: QModelIndex, _roles: list | None = None
    ) -> None:
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
```

</details>

### ⚙️ Method `_refresh_table`

```python
def _refresh_table(self, table_name: str, data_getter: Callable[[], Any], data_transformer: Callable[[Any], Any] | None = None) -> None
```

Refresh a table with data.

Args:

- `table_name` (`str`): Name of the table to refresh.
- `data_getter` (`Callable[[], Any]`): Function to get data from database.
- `data_transformer` (`Callable[[Any], Any] | None`): Optional function to transform raw data.
  Defaults to `None`.

Raises:

- `ValueError`: If the table name is unknown.

<details>
<summary>Code:</summary>

```python
def _refresh_table(
        self, table_name: str, data_getter: Callable[[], Any], data_transformer: Callable[[Any], Any] | None = None
    ) -> None:
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
```

</details>

### ⚙️ Method `_select_exercise_in_list`

```python
def _select_exercise_in_list(self, exercise_name: str) -> None
```

Select an exercise in the list view by name.

Args:

- `exercise_name` (`str`): Name of the exercise to select.

<details>
<summary>Code:</summary>

```python
def _select_exercise_in_list(self, exercise_name: str) -> None:
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
```

</details>

### ⚙️ Method `_setup_ui`

```python
def _setup_ui(self) -> None
```

Set up additional UI elements after basic initialization.

<details>
<summary>Code:</summary>

```python
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
        self.pushButton_last_exercises.setText(f"📅 {self.pushButton_last_exercises.text()}")
        self.pushButton_check_steps.setText(f"👟 {self.pushButton_check_steps.text()}")
        self.pushButton_show_sets_chart.setText(f"📈 {self.pushButton_show_sets_chart.text()}")
        self.pushButton_update_chart.setText(f"🔄 {self.pushButton_update_chart.text()}")
        self.pushButton_chart_last_month.setText(f"📅 {self.pushButton_chart_last_month.text()}")
        self.pushButton_chart_last_year.setText(f"📅 {self.pushButton_chart_last_year.text()}")
        self.pushButton_chart_all_time.setText(f"📅 {self.pushButton_chart_all_time.text()}")
        self.pushButton_weight_last_month.setText(f"📅 {self.pushButton_weight_last_month.text()}")
        self.pushButton_weight_last_year.setText(f"📅 {self.pushButton_weight_last_year.text()}")
        self.pushButton_weight_all_time.setText(f"📅 {self.pushButton_weight_all_time.text()}")
        self.pushButton_update_weight_chart.setText(f"🔄 {self.pushButton_update_weight_chart.text()}")

        # Configure splitter proportions
        self.splitter.setStretchFactor(0, 3)  # tableView gets more space
        self.splitter.setStretchFactor(1, 1)  # listView gets less space
        self.splitter.setStretchFactor(2, 0)  # frame with fixed size
```

</details>

### ⚙️ Method `_show_record_congratulations`

```python
def _show_record_congratulations(self, exercise: str, record_info: dict) -> None
```

Show congratulations message for new records.

Args:

- `exercise` (`str`): Exercise name.
- `record_info` (`dict`): Record information from `_check_for_new_records`.

<details>
<summary>Code:</summary>

```python
def _show_record_congratulations(self, exercise: str, record_info: dict) -> None:
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
```

</details>

### ⚙️ Method `_update_charts_avif`

```python
def _update_charts_avif(self) -> None
```

Update AVIF for charts combobox selection.

<details>
<summary>Code:</summary>

```python
def _update_charts_avif(self) -> None:
        exercise_name = self.comboBox_chart_exercise.currentText()
        if exercise_name:
            self._load_exercise_avif(exercise_name, "charts")
```

</details>

### ⚙️ Method `_update_comboboxes`

```python
def _update_comboboxes(self) -> None
```

Refresh exercise list and type combo-box (optionally keep a selection).

Args:

- `selected_exercise` (`str | None`): Exercise to keep selected. Defaults to `None`.
- `selected_type` (`str | None`): Exercise type to keep selected. Defaults to `None`.

<details>
<summary>Code:</summary>

```python
def _update_comboboxes(
        self,
        *,
        selected_exercise: str | None = None,
        selected_type: str | None = None,
    ) -> None:
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

            # Update types AVIF after combobox update
            self._update_types_avif()

        except Exception as e:
            print(f"Error updating comboboxes: {e}")
```

</details>

### ⚙️ Method `_update_exercises_avif`

```python
def _update_exercises_avif(self) -> None
```

Update AVIF for exercises table selection.

<details>
<summary>Code:</summary>

```python
def _update_exercises_avif(self) -> None:
        exercise_name = self._get_selected_exercise_from_table("exercises")
        if exercise_name:
            self._load_exercise_avif(exercise_name, "exercises")
```

</details>

### ⚙️ Method `_update_form_from_process_selection`

```python
def _update_form_from_process_selection(self, _exercise_name: str, type_name: str, value_str: str) -> None
```

Update form fields after process selection change.

Args:

- `_exercise_name` (`str`): Name of the selected exercise.
- `type_name` (`str`): Type of the selected exercise.
- `value_str` (`str`): Value as string from the selected record.

<details>
<summary>Code:</summary>

```python
def _update_form_from_process_selection(self, _exercise_name: str, type_name: str, value_str: str) -> None:
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
```

</details>

### ⚙️ Method `_update_statistics_avif`

```python
def _update_statistics_avif(self) -> None
```

Update AVIF for statistics table based on current mode.

<details>
<summary>Code:</summary>

```python
def _update_statistics_avif(self) -> None:
        if self.current_statistics_mode == "check_steps":
            # Always show Steps exercise for check_steps mode
            steps_exercise_name = self._get_exercise_name_by_id(self.id_steps)
            if steps_exercise_name:
                self._load_exercise_avif(steps_exercise_name, "statistics")
        else:
            # For other modes, use selected exercise from statistics table
            exercise_name = self._get_selected_exercise_from_statistics_table()
            if exercise_name:
                self._load_exercise_avif(exercise_name, "statistics")
```

</details>

### ⚙️ Method `_update_types_avif`

```python
def _update_types_avif(self) -> None
```

Update AVIF for types combobox selection.

<details>
<summary>Code:</summary>

```python
def _update_types_avif(self) -> None:
        exercise_name = self.comboBox_exercise_name.currentText()
        if exercise_name:
            self._load_exercise_avif(exercise_name, "types")
```

</details>

### ⚙️ Method `_validate_database_connection`

```python
def _validate_database_connection(self) -> bool
```

Validate that database connection is available and open.

Returns:

- `bool`: True if database connection is valid, False otherwise.

<details>
<summary>Code:</summary>

```python
def _validate_database_connection(self) -> bool:
        if not self.db_manager:
            print("Database manager is None")
            return False

        if not self.db_manager.is_database_open():
            print("Database connection is not open")
            return False

        return True
```

</details>
