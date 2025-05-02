import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from functools import partial, wraps

import harrix_pylib as h
from PySide6.QtCore import QDateTime, QSortFilterProxyModel, Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtSql import QSqlDatabase, QSqlQuery
from PySide6.QtWidgets import QApplication, QFileDialog, QMainWindow, QMessageBox

from harrix_swiss_knife import fitness_window

config = h.dev.load_config("config/config.json")

# Constants
EMPTY_TYPE = ""
DATE_FORMAT = "yyyy-MM-dd"


def validate_date(method):
    """Decorator to validate date before executing a method"""

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        date = self.lineEdit_date.text()
        if not self.is_valid_date(date):
            QMessageBox.warning(self, "Error", "Invalid date format. Use YYYY-MM-DD")
            return
        return method(self, *args, **kwargs)

    return wrapper


class DatabaseManager:
    def __init__(self, db_filename):
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName(db_filename)
        if not self.db.open():
            raise Exception("Failed to open the database")

    def _iter_query(self, query):
        """Iterator for query results"""
        if not query:
            return
        while query.next():
            yield query

    def _rows_from_query(self, query):
        """Extract all rows from a query result"""
        result = []
        while query.next():
            result.append([query.value(i) for i in range(query.record().count())])
        return result

    def execute_query(self, query_text, params=None):
        query = QSqlQuery()
        if params:
            query.prepare(query_text)
            for key, value in params.items():
                query.bindValue(f":{key}", value)
        else:
            query.prepare(query_text)
        return query if query.exec() else None

    def get_exercises_by_frequency(self, limit=500):
        """Get exercises ordered by frequency of use in recent records"""
        # Get all exercises
        all_exercises = {row[0]: row[1] for row in self.get_rows("SELECT _id, name FROM exercises")}

        # Get exercise frequency from recent records
        recent_records = self.get_rows(f"SELECT _id_exercises FROM process ORDER BY _id DESC LIMIT {limit}")

        # Count frequency of each exercise
        exercise_counts = Counter(row[0] for row in recent_records)

        # Sort exercises by frequency and add any remaining exercises
        sorted_exercises = [
            all_exercises[ex_id] for ex_id, _ in exercise_counts.most_common() if ex_id in all_exercises
        ]

        # Add any remaining exercises that haven't been used recently
        return sorted_exercises + [name for ex_id, name in all_exercises.items() if name not in sorted_exercises]

    def get_id(self, table, name_column, name_value, id_column="_id", condition=None):
        """Generic method to get ID by name"""
        query_text = f"SELECT {id_column} FROM {table} WHERE {name_column} = :name"
        query_text += f" AND {condition}" if condition else ""
        params = {"name": name_value}
        query = self.execute_query(query_text, params)
        return query.value(0) if query and query.next() else None

    def get_items(self, table, column, condition=None, order_by=None):
        """Generic method to get items from a table"""
        query_text = f"SELECT {column} FROM {table}"
        query_text += f" WHERE {condition}" if condition else ""
        query_text += f" ORDER BY {order_by}" if order_by else ""

        return [query.value(0) for query in self._iter_query(self.execute_query(query_text))]

    def get_rows(self, query_text, params=None):
        """Execute a query and return all rows as a list of tuples"""
        query = self.execute_query(query_text, params)
        return self._rows_from_query(query) if query else []


class MainWindow(QMainWindow, fitness_window.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.db_manager = None
        self.models = {"process": None, "exercises": None, "types": None, "weight": None}

        # Table configurations for generic operations
        self.table_config = {
            "process": (self.tableView_process, "process", ["Exercise", "Exercise Type", "Quantity", "Date"]),
            "exercises": (self.tableView_exercises, "exercises", ["Exercise", "Unit of Measurement"]),
            "types": (self.tableView_exercise_types, "types", ["Exercise", "Exercise Type"]),
            "weight": (self.tableView_weight, "weight", ["Weight", "Date"]),
        }

        self.init_database()
        self.connect_signals()
        self.update_all()

    def add_record_generic(self, table_name, query_text, params):
        """Generic method for adding records to any table"""
        result = self.db_manager.execute_query(query_text, params)
        if result:
            print(f"{table_name} added")
            self.update_all()
            return True
        else:
            QMessageBox.warning(self, "Error", f"Failed to add {table_name}")
            return False

    def connect_signals(self):
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

    def create_table_model(self, data, headers, id_column=0):
        """Create a table model from data"""
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

    def delete_record(self, table_name):
        """Generic method for deleting records from any table"""
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

    def init_database(self):
        filename = config["sqlite_fitness"]

        if not os.path.exists(filename):
            filename, _ = QFileDialog.getOpenFileName(
                self, "Open Database", os.path.dirname(filename), "SQLite Database (*.db)"
            )
            if not filename:
                QMessageBox.critical(self, "Error", "No database selected")
                sys.exit(1)

        try:
            self.db_manager = DatabaseManager(filename)
            print("Database opened successfully")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            sys.exit(1)

    def is_valid_date(self, date_str):
        """Validates if a date string is in format YYYY-MM-DD and represents a valid date"""
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
            return False
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def on_add_exercise(self):
        exercise = self.lineEdit_exercise_name.text()
        unit = self.lineEdit_exercise_unit.text()

        if not exercise:
            QMessageBox.warning(self, "Error", "Enter exercise name")
            return

        self.add_record_generic(
            "exercises", "INSERT INTO exercises (name, unit) VALUES (:name, :unit)", {"name": exercise, "unit": unit}
        )

    @validate_date
    def on_add_record(self):
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

    def on_add_type(self):
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

    @validate_date
    def on_add_weight(self):
        value = str(self.doubleSpinBox_weight.value())
        date = self.lineEdit_weight_date.text()

        self.add_record_generic(
            "weight", "INSERT INTO weight (value, date) VALUES (:value, :date)", {"value": value, "date": date}
        )

    def on_exercise_changed(self):
        exercise_name = self.comboBox_exercise.currentText()
        if not exercise_name:
            return

        exercise_id = self.db_manager.get_id("exercises", "name", exercise_name)
        if exercise_id is None:
            return

        # Get types for this exercise
        types = self.db_manager.get_items("types", "type", condition=f"_id_exercises = {exercise_id}")

        self.comboBox_type.clear()
        self.comboBox_type.addItem(EMPTY_TYPE)
        self.comboBox_type.addItems(types)

    def on_export_csv(self):
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

    def on_refresh_statistics(self):
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
            exercise_name, type_name, value, date = row  # Unpack directly
            key = f"{exercise_name} {type_name}".strip()
            data[key].append(SetOfExercise(exercise_name, type_name, value, date))

        now = QDateTime.currentDateTime()
        today = now.toString(DATE_FORMAT)

        # Build result text using list comprehension and join
        result_lines = []
        for key, exercises in data.items():
            exercises.sort(reverse=True)
            result_lines.append(key)
            result_lines.extend(
                [f"{ex}{' <--- TODAY' if ex.date == today else ''}" for i, ex in enumerate(exercises[:4])]
            )
            result_lines.append("--------")

        self.textEdit_statistics.setText("\n".join(result_lines))

    def on_update_exercises(self):
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

    def on_update_process(self):
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

    def on_update_types(self):
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

    def on_update_weight(self):
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

    def set_current_date(self):
        now = QDateTime.currentDateTime()
        date = now.toString(DATE_FORMAT)
        self.lineEdit_date.setText(date)
        self.lineEdit_weight_date.setText(date)

    def show_tables(self):
        """Show all tables at once"""
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

    def update_all(self, skip_date_update=False, preserve_selections=False, current_exercise=None, current_type=None):
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

    def update_comboboxes(self, selected_exercise=None, selected_type=None):
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
                    self.comboBox_type.addItem(EMPTY_TYPE)
                    self.comboBox_type.addItems(types)

                    # Set the selected type
                    type_index = self.comboBox_type.findText(selected_type)
                    if type_index >= 0:
                        self.comboBox_type.setCurrentIndex(type_index)
        else:
            # If no selection to restore, update types for current exercise
            self.on_exercise_changed()

    def update_date_after_add(self):
        """Update the date after adding a record"""
        current_date_str = self.lineEdit_date.text()
        now = QDateTime.currentDateTime()
        today_str = now.toString(DATE_FORMAT)

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

    def update_record_generic(self, table_name, model_key, query_text, params_extractor):
        """Generic method for updating records"""
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


class SetOfExercise:
    def __init__(self, name_exercises, type_types, value, date):
        self.name_exercises = name_exercises
        self.type_types = type_types
        self.value = float(value)
        self.date = date

    def __lt__(self, other):
        return self.value < other.value

    def __str__(self):
        # Use ternary operator to format string
        return (
            f"{self.date}: {self.name_exercises} {self.type_types} {self.value}"
            if self.type_types
            else f"{self.date}: {self.name_exercises} {self.value}"
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.tabWidget.setCurrentIndex(0)
    window.show()
    sys.exit(app.exec())
