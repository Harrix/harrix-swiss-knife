import os
import re
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from functools import partial
from typing import Callable

import harrix_pylib as h
from PySide6.QtCore import QDateTime, QSortFilterProxyModel, Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QApplication, QFileDialog, QMainWindow, QMessageBox, QTableView

from harrix_swiss_knife import fitness_database_manager, fitness_funcs, fitness_window

config = h.dev.load_config("config/config.json")


class MainWindow(QMainWindow, fitness_window.Ui_MainWindow):
    """
    Main window for the fitness tracking application.

    This class handles the UI interactions, database operations, and display of fitness data.
    It inherits from QMainWindow and the UI class generated from Qt Designer.

    Attributes:

    - `db_manager` (`FitnessDatabaseManager | None`): Manager for database operations. Defaults to `None`.
    - `models` (`dict[str, QSortFilterProxyModel | None]`): Dictionary of table models for different views.
    - `table_config` (`dict[str, tuple[QTableView, str, list[str]]]`): Configuration for tables.
    """

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.db_manager: fitness_database_manager.FitnessDatabaseManager | None = None
        self.models: dict[str, QSortFilterProxyModel | None] = {
            "process": None,
            "exercises": None,
            "types": None,
            "weight": None,
        }

        # Table configurations for generic operations
        self.table_config: dict[str, tuple[QTableView, str, list[str]]] = {
            "process": (self.tableView_process, "process", ["Exercise", "Exercise Type", "Quantity", "Date"]),
            "exercises": (self.tableView_exercises, "exercises", ["Exercise", "Unit of Measurement"]),
            "types": (self.tableView_exercise_types, "types", ["Exercise", "Exercise Type"]),
            "weight": (self.tableView_weight, "weight", ["Weight", "Date"]),
        }

        self.init_database()
        self.connect_signals()
        self.init_filter_controls()
        self.update_all()

    def add_record_generic(self, table_name: str, query_text: str, params: dict) -> bool:
        """
        Generic method for adding records to any table.

        Args:

        - `table_name` (`str`): Name of the table to add the record to.
        - `query_text` (`str`): SQL query for inserting the record.
        - `params` (`dict`): Parameters for the SQL query.

        Returns:

        - `bool`: True if the record was added successfully, False otherwise.
        """
        result = self.db_manager.execute_query(query_text, params)
        if result:
            print(f"{table_name} added")
            self.update_all()
            return True
        else:
            QMessageBox.warning(self, "Error", f"Failed to add {table_name}")
            return False

    def apply_filter(self) -> None:
        """
        Apply the selected filters to the process table.
        """
        exercise = self.comboBox_filter_exercise.currentText()
        exercise_type = self.comboBox_filter_type.currentText()
        use_date_filter = self.checkBox_use_date_filter.isChecked()
        date_from = self.dateEdit_filter_from.date().toString("yyyy-MM-dd") if use_date_filter else ""
        date_to = self.dateEdit_filter_to.date().toString("yyyy-MM-dd") if use_date_filter else ""

        # Build query conditions
        conditions = []
        params = {}

        if exercise:
            conditions.append("e.name = :exercise")
            params["exercise"] = exercise

        if exercise_type:
            conditions.append("t.type = :type")
            params["type"] = exercise_type

        if use_date_filter:
            conditions.append("p.date BETWEEN :date_from AND :date_to")
            params["date_from"] = date_from
            params["date_to"] = date_to

        # Build the full query
        query_text = """
            SELECT p._id, e.name, IFNULL(t.type, ''), p.value, e.unit, p.date
            FROM process p
            JOIN exercises e ON p._id_exercises = e._id
            LEFT JOIN types t ON p._id_types = t._id AND t._id_exercises = e._id
        """

        if conditions:
            query_text += " WHERE " + " AND ".join(conditions)

        query_text += " ORDER BY p._id DESC"

        # Execute the query - используем существующий метод get_rows
        rows = self.db_manager.get_rows(query_text, params)

        # Process data and update the table
        data = [[row[0], row[1], row[2], f"{row[3]} {row[4] or 'times'}", row[5]] for row in rows]
        self.models["process"] = self.create_table_model(data, self.table_config["process"][2])
        self.tableView_process.setModel(self.models["process"])
        self.tableView_process.resizeColumnsToContents()

        # Show filter status in status bar
        filter_description = []
        if exercise:
            filter_description.append(f"Exercise: {exercise}")
        if exercise_type:
            filter_description.append(f"Type: {exercise_type}")
        if use_date_filter:
            filter_description.append(f"Date: {date_from} to {date_to}")

    def clear_filter(self) -> None:
        """
        Clear all filters and reset the process table.
        """
        # Reset filter controls
        self.comboBox_filter_exercise.setCurrentIndex(0)
        self.comboBox_filter_type.setCurrentIndex(0)
        self.checkBox_use_date_filter.setChecked(False)

        # Reset date range to default (last month to today)
        current_date = QDateTime.currentDateTime().date()
        self.dateEdit_filter_from.setDate(current_date.addMonths(-1))
        self.dateEdit_filter_to.setDate(current_date)

        # Refresh the table with no filters
        self.show_tables()

    def connect_signals(self) -> None:
        """
        Connect UI signals to their respective slots.

        This method sets up all event handlers for buttons, comboboxes, and other UI elements.
        """
        # Main tab signals
        self.comboBox_exercise.currentIndexChanged.connect(self.on_exercise_changed)
        self.pushButton_add.clicked.connect(self.on_add_record)

        # Connect signals using a loop and partial functions
        for action, button_prefix in [("delete", "delete"), ("update", "update"), ("refresh", "refresh")]:
            for table in self.table_config.keys():
                button = getattr(
                    self, f"pushButton_{button_prefix if table == 'process' else table + '_' + button_prefix}"
                )
                if action == "delete":
                    button.clicked.connect(partial(self.delete_record, table))
                elif action == "update":
                    button.clicked.connect(getattr(self, f"on_update_{table}"))
                else:  # refresh
                    button.clicked.connect(self.update_all)

        # Add actions
        self.pushButton_exercise_add.clicked.connect(self.on_add_exercise)
        self.pushButton_type_add.clicked.connect(self.on_add_type)
        self.pushButton_weight_add.clicked.connect(self.on_add_weight)

        # Statistics tab signals
        self.pushButton_statistics_refresh.clicked.connect(self.on_refresh_statistics)
        self.pushButton_export_csv.clicked.connect(self.on_export_csv)

        # Tab change signal
        self.tabWidget.currentChanged.connect(self.on_tab_changed)

    def create_table_model(self, data: list, headers: list[str], id_column: int = 0) -> QSortFilterProxyModel:
        """
        Create a table model from data.

        Args:

        - `data` (`list`): Data to populate the model with.
        - `headers` (`list[str]`): Column headers for the model.
        - `id_column` (`int`): Index of the ID column. Defaults to `0`.

        Returns:

        - `QSortFilterProxyModel`: A proxy model containing the data.
        """
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(headers)

        for i, row in enumerate(data):
            # Create row items using list comprehension
            row_items = [
                QStandardItem(str(value if value is not None else "")) for j, value in enumerate(row) if j != id_column
            ]

            model.appendRow(row_items)
            model.setVerticalHeaderItem(i, QStandardItem(str(row[id_column])))

        proxy_model = QSortFilterProxyModel()
        proxy_model.setSourceModel(model)
        return proxy_model

    def delete_record(self, table_name: str) -> None:
        """
        Generic method for deleting records from any table.

        Args:

        - `table_name` (`str`): Name of the table to delete the record from.
        """
        if table_name not in self.table_config:
            return

        table_view, model_key, _ = self.table_config[table_name]
        model = self.models[model_key]

        index = table_view.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "Error", f"Select a record to delete")
            return

        row = index.row()
        _id = model.sourceModel().verticalHeaderItem(row).text()

        result = self.db_manager.execute_query(f"DELETE FROM {table_name} WHERE _id = :id", {"id": _id})

        if result:
            print(f"Record deleted from {table_name}")
            self.update_all()
        else:
            QMessageBox.warning(self, "Error", f"Failed to delete record from {table_name}")

    def init_database(self) -> None:
        """
        Initialize the database connection.

        This method attempts to open the database file specified in the config.
        If the file doesn't exist, it prompts the user to select a database file.
        """
        filename = config["sqlite_fitness"]

        if not os.path.exists(filename):
            filename, _ = QFileDialog.getOpenFileName(
                self, "Open Database", os.path.dirname(filename), "SQLite Database (*.db)"
            )
            if not filename:
                QMessageBox.critical(self, "Error", "No database selected")
                sys.exit(1)

        try:
            self.db_manager = fitness_database_manager.FitnessDatabaseManager(filename)
            print("Database opened successfully")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            sys.exit(1)

    def init_filter_controls(self) -> None:
        """
        Initialize filter controls for the process table.

        This method sets up the filter comboboxes and date selectors.
        """
        # Set up date filter controls
        current_date = QDateTime.currentDateTime().date()
        self.dateEdit_filter_from.setDate(current_date.addMonths(-1))
        self.dateEdit_filter_to.setDate(current_date)

        # Set checkbox state
        self.checkBox_use_date_filter.setChecked(False)

        # Connect filter signals
        self.comboBox_filter_exercise.currentIndexChanged.connect(self.update_filter_type_combobox)
        self.pushButton_apply_filter.clicked.connect(self.apply_filter)
        self.pushButton_clear_filter.clicked.connect(self.clear_filter)

    def is_valid_date(self, date_str: str) -> bool:
        """
        Validates if a date string is in format YYYY-MM-DD and represents a valid date.

        Args:

        - `date_str` (`str`): The date string to validate.

        Returns:

        - `bool`: True if the date is valid, False otherwise.
        """
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
            return False
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def on_add_exercise(self) -> None:
        """
        Handle adding a new exercise to the database.

        This method is triggered when the user clicks the "Add Exercise" button.
        """
        exercise = self.lineEdit_exercise_name.text()
        unit = self.lineEdit_exercise_unit.text()

        if not exercise:
            QMessageBox.warning(self, "Error", "Enter exercise name")
            return

        self.add_record_generic(
            "exercises", "INSERT INTO exercises (name, unit) VALUES (:name, :unit)", {"name": exercise, "unit": unit}
        )

    @fitness_funcs.validate_date
    def on_add_record(self) -> None:
        """
        Handle adding a new fitness record to the database.

        This method is triggered when the user clicks the "Add" button on the main tab.
        It adds a new entry to the process table.
        """
        # Save current selections
        current_exercise = self.comboBox_exercise.currentText()
        current_type = self.comboBox_type.currentText()

        value = str(self.spinBox_count.value())
        date = self.lineEdit_date.text()

        exercise_id = self.db_manager.get_id("exercises", "name", current_exercise)
        if exercise_id is None:
            return

        type_id = -1
        if current_type:
            type_id = (
                self.db_manager.get_id("types", "type", current_type, condition=f"_id_exercises = {exercise_id}") or -1
            )

        params = {
            "exercise_id": exercise_id,
            "type_id": type_id,
            "value": value,
            "date": date,
        }

        if self.add_record_generic(
            "process",
            """INSERT INTO process (_id_exercises, _id_types, value, date)
                                    VALUES (:exercise_id, :type_id, :value, :date)""",
            params,
        ):
            # Update date after adding a record
            self.update_date_after_add()
            # Update the rest of the UI
            self.update_all(
                skip_date_update=True,
                preserve_selections=True,
                current_exercise=current_exercise,
                current_type=current_type,
            )

    def on_add_type(self) -> None:
        """
        Handle adding a new exercise type to the database.

        This method is triggered when the user clicks the "Add Type" button.
        """
        exercise_name = self.comboBox_exercise_name.currentText()
        type_name = self.lineEdit_exercise_type.text()

        if not type_name:
            QMessageBox.warning(self, "Error", "Enter type name")
            return

        exercise_id = self.db_manager.get_id("exercises", "name", exercise_name)
        if exercise_id is None:
            return

        self.add_record_generic(
            "type",
            "INSERT INTO types (_id_exercises, type) VALUES (:exercise_id, :type)",
            {"exercise_id": exercise_id, "type": type_name},
        )

    @fitness_funcs.validate_date
    def on_add_weight(self) -> None:
        """
        Handle adding a new weight record to the database.

        This method is triggered when the user clicks the "Add Weight" button.
        """
        value = str(self.doubleSpinBox_weight.value())
        date = self.lineEdit_weight_date.text()

        self.add_record_generic(
            "weight", "INSERT INTO weight (value, date) VALUES (:value, :date)", {"value": value, "date": date}
        )

    def on_exercise_changed(self) -> None:
        """
        Handle exercise selection change.

        This method updates the exercise type combobox when the selected exercise changes.
        """
        exercise_name = self.comboBox_exercise.currentText()
        if not exercise_name:
            return

        exercise_id = self.db_manager.get_id("exercises", "name", exercise_name)
        if exercise_id is None:
            return

        # Get types for this exercise
        types = self.db_manager.get_items("types", "type", condition=f"_id_exercises = {exercise_id}")

        self.comboBox_type.clear()
        self.comboBox_type.addItem("")
        self.comboBox_type.addItems(types)

    def on_export_csv(self) -> None:
        """
        Export the process table to a CSV file.

        This method is triggered when the user clicks the "Export CSV" button.
        """
        filename, _ = QFileDialog.getSaveFileName(self, "Save Table", "", "CSV (*.csv)")
        if not filename:
            return

        model = self.models["process"].sourceModel()
        with open(filename, "w", encoding="utf-8") as f:
            # Headers using list comprehension
            headers = [model.headerData(i, Qt.Horizontal) or "" for i in range(model.columnCount())]
            f.write(";".join(headers) + "\n")

            # Rows using list comprehension
            for row in range(model.rowCount()):
                row_data = [f'"{model.data(model.index(row, col)) or ""}"' for col in range(model.columnCount())]
                f.write(";".join(row_data) + "\n")
        print("CSV saved")

    def on_refresh_statistics(self) -> None:
        """
        Refresh the statistics display.

        This method queries the database for exercise data and displays statistics in the text edit.
        """
        self.textEdit_statistics.clear()

        query_text = """
            SELECT e.name, IFNULL(t.type, ''), p.value, p.date
            FROM process p
            JOIN exercises e ON p._id_exercises = e._id
            LEFT JOIN types t ON p._id_types = t._id
            ORDER BY p._id DESC
        """
        rows = self.db_manager.get_rows(query_text)

        data = defaultdict(list)
        for row in rows:
            exercise_name, type_name, value, date = row
            key = f"{exercise_name} {type_name}".strip()
            data[key].append([exercise_name, type_name, float(value), date])

        now = QDateTime.currentDateTime()
        today = now.toString("yyyy-MM-dd")

        # Build result text
        result_lines = []
        for key, exercises in data.items():
            # Sort by value (index 2)
            exercises.sort(key=lambda x: x[2], reverse=True)
            result_lines.append(key)

            for ex in exercises[:4]:
                exercise_name, type_name, value, date = ex
                if type_name:
                    formatted = f"{date}: {exercise_name} {type_name} {value}"
                else:
                    formatted = f"{date}: {exercise_name} {value}"

                if date == today:
                    formatted += " <--- TODAY"

                result_lines.append(formatted)

            result_lines.append("--------")

        self.textEdit_statistics.setText("\n".join(result_lines))

    def on_tab_changed(self, index: int) -> None:
        """
        Handle tab change event.

        This method updates the filter comboboxes when the user switches to the main tab.

        Args:
            index (int): Index of the selected tab.
        """
        # If switching to the main tab (index 0), update filter comboboxes
        if index == 0:
            self.update_filter_comboboxes()

    def on_update_exercises(self) -> None:
        """
        Handle updating an exercise record.

        This method is triggered when the user clicks the "Update" button on the exercises tab.
        """
        self.update_record_generic(
            "exercises",
            "exercises",
            """UPDATE exercises SET name = :name, unit = :unit WHERE _id = :id""",
            lambda row, model, _id: {
                "name": model.data(model.index(row, 0)),
                "unit": model.data(model.index(row, 1)),
                "id": _id,
            },
        )

    def on_update_process(self) -> None:
        """
        Handle updating a fitness record.

        This method is triggered when the user clicks the "Update" button on the main tab.
        """
        index = self.tableView_process.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "Error", "Select a record to update")
            return

        row = index.row()
        model = self.models["process"]
        _id = model.sourceModel().verticalHeaderItem(row).text()

        exercise = model.data(model.index(row, 0))
        type_name = model.data(model.index(row, 1))
        value_raw = model.data(model.index(row, 2))
        value = value_raw.split(" ")[0]
        date = model.data(model.index(row, 3))

        if not self.is_valid_date(date):
            QMessageBox.warning(self, "Error", "Invalid date format. Use YYYY-MM-DD")
            return

        exercise_id = self.db_manager.get_id("exercises", "name", exercise)
        if exercise_id is None:
            return

        # Use ternary operator for type_id
        type_id = (
            self.db_manager.get_id("types", "type", type_name, condition=f"_id_exercises = {exercise_id}")
            if type_name
            else -1
        )
        type_id = type_id if type_id is not None else -1

        query_text = """
            UPDATE process
            SET _id_exercises = :exercise_id, _id_types = :type_id, date = :date, value = :value
            WHERE _id = :id
        """
        params = {
            "exercise_id": exercise_id,
            "type_id": type_id,
            "date": date,
            "value": value,
            "id": _id,
        }
        result = self.db_manager.execute_query(query_text, params)
        if result:
            print("Record updated")
            self.update_all()
        else:
            QMessageBox.warning(self, "Error", "Failed to update record")

    def on_update_types(self) -> None:
        """
        Handle updating an exercise type record.

        This method is triggered when the user clicks the "Update" button on the types tab.
        """
        self.update_record_generic(
            "types",
            "types",
            """UPDATE types
                                     SET _id_exercises = :exercise_id, type = :type_name
                                     WHERE _id = :id""",
            lambda row, model, _id: {
                "exercise_id": self.db_manager.get_id("exercises", "name", model.data(model.index(row, 0))),
                "type_name": model.data(model.index(row, 1)),
                "id": _id,
            },
        )

    def on_update_weight(self) -> None:
        """
        Handle updating a weight record.

        This method is triggered when the user clicks the "Update" button on the weight tab.
        """
        self.update_record_generic(
            "weight",
            "weight",
            """UPDATE weight SET value = :value, date = :date WHERE _id = :id""",
            lambda row, model, _id: {
                "value": model.data(model.index(row, 0)),
                "date": model.data(model.index(row, 1)),
                "id": _id,
            },
        )

    def set_current_date(self) -> None:
        """
        Set the current date in date input fields.

        This method sets today's date in the date fields for adding records.
        """
        now = QDateTime.currentDateTime()
        date = now.toString("yyyy-MM-dd")
        self.lineEdit_date.setText(date)
        self.lineEdit_weight_date.setText(date)

    def show_tables(self) -> None:
        """
        Show all tables at once.

        This method fetches data from the database and populates all table views.
        """
        # Show exercises table
        data = self.db_manager.get_rows("SELECT _id, name, unit FROM exercises")
        self.models["exercises"] = self.create_table_model(data, self.table_config["exercises"][2])
        self.tableView_exercises.setModel(self.models["exercises"])
        self.tableView_exercises.resizeColumnsToContents()

        # Show process table
        rows = self.db_manager.get_rows("""
            SELECT p._id, e.name, IFNULL(t.type, ''), p.value, e.unit, p.date
            FROM process p
            JOIN exercises e ON p._id_exercises = e._id
            LEFT JOIN types t ON p._id_types = t._id AND t._id_exercises = e._id
            ORDER BY p._id DESC
        """)

        # Process data using list comprehension
        data = [[row[0], row[1], row[2], f"{row[3]} {row[4] or 'times'}", row[5]] for row in rows]

        self.models["process"] = self.create_table_model(data, self.table_config["process"][2])
        self.tableView_process.setModel(self.models["process"])
        self.tableView_process.resizeColumnsToContents()

        # Show types table
        data = self.db_manager.get_rows("""
            SELECT t._id, e.name, t.type
            FROM types t
            JOIN exercises e ON t._id_exercises = e._id
        """)
        self.models["types"] = self.create_table_model(data, self.table_config["types"][2])
        self.tableView_exercise_types.setModel(self.models["types"])
        self.tableView_exercise_types.resizeColumnsToContents()

        # Show weight table
        data = self.db_manager.get_rows("SELECT _id, value, date FROM weight ORDER BY date DESC")
        self.models["weight"] = self.create_table_model(data, self.table_config["weight"][2])
        self.tableView_weight.setModel(self.models["weight"])
        self.tableView_weight.resizeColumnsToContents()

    def update_all(
        self,
        skip_date_update: bool = False,
        preserve_selections: bool = False,
        current_exercise: str = None,
        current_type: str = None,
    ) -> None:
        """
        Update all UI elements.

        Args:

        - `skip_date_update` (`bool`): Whether to skip updating the date fields. Defaults to `False`.
        - `preserve_selections` (`bool`): Whether to preserve current selections. Defaults to `False`.
        - `current_exercise` (`str`): Current selected exercise to preserve. Defaults to `None`.
        - `current_type` (`str`): Current selected exercise type to preserve. Defaults to `None`.
        """
        # Save current selections if needed
        if preserve_selections and current_exercise is None:
            current_exercise = self.comboBox_exercise.currentText()
            current_type = self.comboBox_type.currentText()

        # Update all tables
        self.show_tables()

        # Update comboboxes with preserved selections if needed
        if preserve_selections and current_exercise:
            self.update_comboboxes(selected_exercise=current_exercise, selected_type=current_type)
        else:
            self.update_comboboxes()

        # Only update date if not skipped
        if not skip_date_update:
            self.set_current_date()

        # Update filter comboboxes
        self.update_filter_comboboxes()

    def update_comboboxes(self, selected_exercise: str = None, selected_type: str = None) -> None:
        """
        Update the exercise and type comboboxes.

        Args:

        - `selected_exercise` (`str`): Exercise to select after update. Defaults to `None`.
        - `selected_type` (`str`): Exercise type to select after update. Defaults to `None`.
        """
        # Get exercises sorted by frequency of use
        exercises = self.db_manager.get_exercises_by_frequency(500)

        # Save current index to restore after update
        current_exercise_index = exercises.index(selected_exercise) if selected_exercise in exercises else -1

        # Clear and populate comboboxes
        self.comboBox_exercise.clear()
        self.comboBox_exercise_name.clear()

        # Add exercises to comboboxes
        self.comboBox_exercise.addItems(exercises)
        self.comboBox_exercise_name.addItems(exercises)

        # Restore selection if needed
        if current_exercise_index >= 0:
            self.comboBox_exercise.setCurrentIndex(current_exercise_index)

            # If we have a type to restore too, we need to make sure types are loaded
            if selected_type:
                exercise_id = self.db_manager.get_id("exercises", "name", selected_exercise)
                if exercise_id is not None:
                    # Get types for this exercise
                    types = self.db_manager.get_items("types", "type", condition=f"_id_exercises = {exercise_id}")

                    self.comboBox_type.clear()
                    self.comboBox_type.addItem("")
                    self.comboBox_type.addItems(types)

                    # Set the selected type
                    type_index = self.comboBox_type.findText(selected_type)
                    if type_index >= 0:
                        self.comboBox_type.setCurrentIndex(type_index)
        else:
            # If no selection to restore, update types for current exercise
            self.on_exercise_changed()

    def update_date_after_add(self) -> None:
        """
        Update the date after adding a record.

        This method increments the date by one day if it's not today's date.
        """
        current_date_str = self.lineEdit_date.text()
        now = QDateTime.currentDateTime()
        today_str = now.toString("yyyy-MM-dd")

        # If invalid date or already today, set to today or leave unchanged
        if not self.is_valid_date(current_date_str):
            self.lineEdit_date.setText(today_str)
            return

        # If current date is already today, leave it
        if current_date_str == today_str:
            return

        # Otherwise, increment by one day
        try:
            current_date = datetime.strptime(current_date_str, "%Y-%m-%d")
            next_date = current_date + timedelta(days=1)
            self.lineEdit_date.setText(next_date.strftime("%Y-%m-%d"))
        except ValueError:
            # If there's any error, set to today's date
            self.lineEdit_date.setText(today_str)

    def update_filter_comboboxes(self) -> None:
        """
        Update filter comboboxes with current data.

        This method populates the exercise filter combobox and updates the type combobox.
        """
        # Save current selections
        current_exercise = self.comboBox_filter_exercise.currentText()

        # Update exercise combobox
        self.comboBox_filter_exercise.blockSignals(True)
        self.comboBox_filter_exercise.clear()
        self.comboBox_filter_exercise.addItem("")  # Empty item for "All exercises"

        # Get unique exercises from the process table
        exercises = self.db_manager.get_items("exercises", "name")
        self.comboBox_filter_exercise.addItems(exercises)

        # Restore previous selection if possible
        if current_exercise:
            index = self.comboBox_filter_exercise.findText(current_exercise)
            if index >= 0:
                self.comboBox_filter_exercise.setCurrentIndex(index)

        self.comboBox_filter_exercise.blockSignals(False)

        # Update type combobox based on selected exercise
        self.update_filter_type_combobox()

    def update_filter_type_combobox(self) -> None:
        """
        Update the exercise type filter combobox based on the selected exercise.
        """
        # Save current selection
        current_type = self.comboBox_filter_type.currentText()

        # Clear and add empty item
        self.comboBox_filter_type.clear()
        self.comboBox_filter_type.addItem("")  # Empty item for "All types"

        # Get exercise id for the selected exercise
        exercise_name = self.comboBox_filter_exercise.currentText()
        if not exercise_name:
            return

        exercise_id = self.db_manager.get_id("exercises", "name", exercise_name)
        if exercise_id is None:
            return

        # Get types for this exercise
        types = self.db_manager.get_items("types", "type", condition=f"_id_exercises = {exercise_id}")
        self.comboBox_filter_type.addItems(types)

        # Restore previous selection if possible
        if current_type:
            index = self.comboBox_filter_type.findText(current_type)
            if index >= 0:
                self.comboBox_filter_type.setCurrentIndex(index)

    def update_record_generic(
        self,
        table_name: str,
        model_key: str,
        query_text: str,
        params_extractor: Callable[[int, QSortFilterProxyModel, str], dict],
    ) -> None:
        """
        Generic method for updating records.

        Args:

        - `table_name` (`str`): Name of the table to update.
        - `model_key` (`str`): Key of the model in the models dictionary.
        - `query_text` (`str`): SQL query for updating the record.
        - `params_extractor` (`Callable`): Function to extract parameters from the selected row.
        """
        table_view = next((tv for tv, mk, _ in self.table_config.values() if mk == model_key), None)
        if not table_view:
            return

        index = table_view.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "Error", f"Select a record to update")
            return

        row = index.row()
        model = self.models[model_key]
        _id = model.sourceModel().verticalHeaderItem(row).text()

        params = params_extractor(row, model, _id)
        if not params:
            return

        result = self.db_manager.execute_query(query_text, params)
        if result:
            print(f"{table_name} updated")
            self.update_all()
        else:
            QMessageBox.warning(self, "Error", f"Failed to update {table_name}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.tabWidget.setCurrentIndex(0)
    window.show()
    sys.exit(app.exec())
