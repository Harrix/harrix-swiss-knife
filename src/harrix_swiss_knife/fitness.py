import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from functools import wraps

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


class DatabaseManager:
    def __init__(self, db_filename):
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName(db_filename)
        if not self.db.open():
            raise Exception("Failed to open the database")

    def execute_query(self, query_text, params=None):
        query = QSqlQuery()
        if params:
            query.prepare(query_text)
            for key, value in params.items():
                query.bindValue(f":{key}", value)
        else:
            query.prepare(query_text)
        if not query.exec():
            print(f"Error executing query: {query.lastError().text()}")
            return None
        return query

    def get_exercises_by_frequency(self, limit=500):
        """Get exercises ordered by frequency of use in recent records"""
        # Get all exercises
        all_exercises = {row[0]: row[1] for row in self.get_rows("SELECT _id, name FROM exercises")}

        # Get exercise frequency from recent records
        recent_records = self.get_rows(f"SELECT _id_exercises FROM process ORDER BY _id DESC LIMIT {limit}")

        # Count frequency of each exercise
        exercise_counts = Counter(row[0] for row in recent_records)

        # Sort exercises by frequency
        sorted_exercises = []

        # First add exercises that have been used recently
        for exercise_id, count in exercise_counts.most_common():
            if exercise_id in all_exercises:
                sorted_exercises.append(all_exercises[exercise_id])

        # Then add any remaining exercises that haven't been used recently
        for exercise_id, name in all_exercises.items():
            if name not in sorted_exercises:
                sorted_exercises.append(name)

        return sorted_exercises

    def get_id(self, table, name_column, name_value, id_column="_id"):
        """Generic method to get ID by name"""
        query_text = f"SELECT {id_column} FROM {table} WHERE {name_column} = :name"
        params = {"name": name_value}
        query = self.execute_query(query_text, params)
        if query and query.next():
            return query.value(0)
        return None

    def get_items(self, table, column, condition=None, order_by=None):
        """Generic method to get items from a table"""
        query_text = f"SELECT {column} FROM {table}"
        if condition:
            query_text += f" WHERE {condition}"
        if order_by:
            query_text += f" ORDER BY {order_by}"

        query = self.execute_query(query_text)
        items = []
        while query and query.next():
            items.append(query.value(0))
        return items

    def get_rows(self, query_text, params=None):
        """Execute a query and return all rows as a list of tuples"""
        query = self.execute_query(query_text, params)
        if not query:
            return []

        results = []
        while query.next():
            row = []
            for i in range(query.record().count()):
                row.append(query.value(i))
            results.append(row)
        return results


class MainWindow(QMainWindow, fitness_window.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.db_manager = None
        self.models = {"process": None, "exercises": None, "types": None, "weight": None}

        self.init_database()
        self.connect_signals()
        self.update_all()

    def connect_signals(self):
        # Main tab signals
        self.comboBox_exercise.currentIndexChanged.connect(self.on_exercise_changed)
        self.pushButton_add.clicked.connect(self.on_add_record)
        self.pushButton_delete.clicked.connect(lambda: self.delete_record("process"))
        self.pushButton_update.clicked.connect(self.on_update_record)
        self.pushButton_refresh.clicked.connect(self.update_all)

        # Exercise tab signals
        self.pushButton_exercise_add.clicked.connect(self.on_add_exercise)
        self.pushButton_exercise_delete.clicked.connect(lambda: self.delete_record("exercises"))
        self.pushButton_exercise_update.clicked.connect(self.on_update_exercise)
        self.pushButton_exercise_refresh.clicked.connect(self.update_all)

        # Type tab signals
        self.pushButton_type_add.clicked.connect(self.on_add_type)
        self.pushButton_type_delete.clicked.connect(lambda: self.delete_record("types"))
        self.pushButton_type_update.clicked.connect(self.on_update_type)
        self.pushButton_type_refresh.clicked.connect(self.update_all)

        # Weight tab signals
        self.pushButton_weight_add.clicked.connect(self.on_add_weight)
        self.pushButton_weight_delete.clicked.connect(lambda: self.delete_record("weight"))
        self.pushButton_weight_update.clicked.connect(self.on_update_weight)
        self.pushButton_weight_refresh.clicked.connect(self.update_all)

        # Statistics tab signals
        self.pushButton_statistics_refresh.clicked.connect(self.on_refresh_statistics)
        self.pushButton_export_csv.clicked.connect(self.on_export_csv)

    def create_table_model(self, data, headers, id_column=0):
        """Create a table model from data"""
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(headers)

        for i, row in enumerate(data):
            row_items = []
            for j, value in enumerate(row):
                if j != id_column:  # Skip ID column in display
                    row_items.append(QStandardItem(str(value if value is not None else "")))
            model.appendRow(row_items)
            model.setVerticalHeaderItem(i, QStandardItem(str(row[id_column])))

        proxy_model = QSortFilterProxyModel()
        proxy_model.setSourceModel(model)
        return proxy_model

    def delete_record(self, table_name):
        """Generic method for deleting records from any table"""
        table_config = {
            "process": (self.tableView_process, self.models["process"]),
            "exercises": (self.tableView_exercises, self.models["exercises"]),
            "types": (self.tableView_exercise_types, self.models["types"]),
            "weight": (self.tableView_weight, self.models["weight"]),
        }

        if table_name not in table_config:
            return

        table_view, model = table_config[table_name]

        index = table_view.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "Error", f"Select a record to delete")
            return

        row = index.row()
        _id = model.sourceModel().verticalHeaderItem(row).text()

        query_text = f"DELETE FROM {table_name} WHERE _id = :id"
        params = {"id": _id}
        result = self.db_manager.execute_query(query_text, params)
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

        query_text = "INSERT INTO exercises (name, unit) VALUES (:name, :unit)"
        params = {"name": exercise, "unit": unit}
        result = self.db_manager.execute_query(query_text, params)
        if result:
            print("Exercise added")
            self.update_all()
        else:
            QMessageBox.warning(self, "Error", "Failed to add exercise")

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
            type_id = self.db_manager.get_id("types", "type", current_type, condition=f"_id_exercises = {exercise_id}")
            if type_id is None:
                type_id = -1

        query_text = """
            INSERT INTO process (_id_exercises, _id_types, value, date)
            VALUES (:exercise_id, :type_id, :value, :date)
        """
        params = {
            "exercise_id": exercise_id,
            "type_id": type_id,
            "value": value,
            "date": date,
        }
        result = self.db_manager.execute_query(query_text, params)
        if result:
            print("Record added")
            # Update date after adding a record
            self.update_date_after_add()
            # Update the rest of the UI
            self.update_all(
                skip_date_update=True,
                preserve_selections=True,
                current_exercise=current_exercise,
                current_type=current_type,
            )
        else:
            QMessageBox.warning(self, "Error", "Failed to add record")

    def on_add_type(self):
        exercise_name = self.comboBox_exercise_name.currentText()
        type_name = self.lineEdit_exercise_type.text()

        if not type_name:
            QMessageBox.warning(self, "Error", "Enter type name")
            return

        exercise_id = self.db_manager.get_id("exercises", "name", exercise_name)
        if exercise_id is None:
            return

        query_text = "INSERT INTO types (_id_exercises, type) VALUES (:exercise_id, :type)"
        params = {"exercise_id": exercise_id, "type": type_name}
        result = self.db_manager.execute_query(query_text, params)
        if result:
            print("Type added")
            self.update_all()
        else:
            QMessageBox.warning(self, "Error", "Failed to add type")

    @validate_date
    def on_add_weight(self):
        value = str(self.doubleSpinBox_weight.value())
        date = self.lineEdit_weight_date.text()

        query_text = "INSERT INTO weight (value, date) VALUES (:value, :date)"
        params = {"value": value, "date": date}
        result = self.db_manager.execute_query(query_text, params)
        if result:
            print("Weight added")
            self.update_all()
        else:
            QMessageBox.warning(self, "Error", "Failed to add weight")

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

        for type_name in types:
            self.comboBox_type.addItem(type_name)

    def on_export_csv(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save Table", "", "CSV (*.csv)")
        if filename:
            model = self.models["process"].sourceModel()
            with open(filename, "w", encoding="utf-8") as f:
                # Headers
                headers = [model.headerData(i, Qt.Horizontal) for i in range(model.columnCount())]
                headers = [header if header is not None else "" for header in headers]
                f.write(";".join(headers) + "\n")

                for row in range(model.rowCount()):
                    row_data = []
                    for column in range(model.columnCount()):
                        index = model.index(row, column)
                        data = model.data(index)
                        data = data if data is not None else ""
                        row_data.append(f'"{data}"')
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
            exercise_name = row[0]
            type_name = row[1]
            value = row[2]
            date = row[3]

            key = f"{exercise_name} {type_name}".strip()
            data[key].append(SetOfExercise(exercise_name, type_name, value, date))

        result_text = ""
        now = QDateTime.currentDateTime()
        today = now.toString(DATE_FORMAT)

        for key, exercises in data.items():
            result_text += key + "\n"
            exercises.sort(reverse=True)
            for i, exercise in enumerate(exercises[:4]):
                today_marker = " <--- TODAY" if exercise.date == today else ""
                result_text += f"{exercise}{today_marker}\n"
            result_text += "--------\n"

        self.textEdit_statistics.setText(result_text)

    def on_update_exercise(self):
        index = self.tableView_exercises.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "Error", "Select an exercise to update")
            return

        row = index.row()
        _id = self.models["exercises"].sourceModel().verticalHeaderItem(row).text()

        model_index_name = self.models["exercises"].index(row, 0)
        name = self.models["exercises"].data(model_index_name)

        model_index_unit = self.models["exercises"].index(row, 1)
        unit = self.models["exercises"].data(model_index_unit)

        query_text = """
            UPDATE exercises
            SET name = :name, unit = :unit
            WHERE _id = :id
        """
        params = {"name": name, "unit": unit, "id": _id}
        result = self.db_manager.execute_query(query_text, params)
        if result:
            print("Exercise updated")
            self.update_all()
        else:
            QMessageBox.warning(self, "Error", "Failed to update exercise")

    def on_update_record(self):
        index = self.tableView_process.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "Error", "Select a record to update")
            return

        row = index.row()
        _id = self.models["process"].sourceModel().verticalHeaderItem(row).text()

        model_index_exercise = self.models["process"].index(row, 0)
        exercise = self.models["process"].data(model_index_exercise)

        model_index_type = self.models["process"].index(row, 1)
        type_name = self.models["process"].data(model_index_type)

        model_index_value = self.models["process"].index(row, 2)
        value_raw = self.models["process"].data(model_index_value)
        value = value_raw.split(" ")[0]

        model_index_date = self.models["process"].index(row, 3)
        date = self.models["process"].data(model_index_date)

        if not self.is_valid_date(date):
            QMessageBox.warning(self, "Error", "Invalid date format. Use YYYY-MM-DD")
            return

        exercise_id = self.db_manager.get_id("exercises", "name", exercise)
        if exercise_id is None:
            return

        type_id = -1
        if type_name:
            type_id = self.db_manager.get_id("types", "type", type_name, condition=f"_id_exercises = {exercise_id}")
            if type_id is None:
                type_id = -1

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

    def on_update_type(self):
        index = self.tableView_exercise_types.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "Error", "Select a type to update")
            return

        row = index.row()
        _id = self.models["types"].sourceModel().verticalHeaderItem(row).text()

        model_index_exercise = self.models["types"].index(row, 0)
        exercise_name = self.models["types"].data(model_index_exercise)

        model_index_type = self.models["types"].index(row, 1)
        type_name = self.models["types"].data(model_index_type)

        exercise_id = self.db_manager.get_id("exercises", "name", exercise_name)
        if exercise_id is None:
            return

        query_text = """
            UPDATE types
            SET _id_exercises = :exercise_id, type = :type_name
            WHERE _id = :id
        """
        params = {"exercise_id": exercise_id, "type_name": type_name, "id": _id}
        result = self.db_manager.execute_query(query_text, params)
        if result:
            print("Type updated")
            self.update_all()
        else:
            QMessageBox.warning(self, "Error", "Failed to update type")

    def on_update_weight(self):
        index = self.tableView_weight.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "Error", "Select a weight record to update")
            return

        row = index.row()
        _id = self.models["weight"].sourceModel().verticalHeaderItem(row).text()

        model_index_value = self.models["weight"].index(row, 0)
        value = self.models["weight"].data(model_index_value)

        model_index_date = self.models["weight"].index(row, 1)
        date = self.models["weight"].data(model_index_date)

        if not self.is_valid_date(date):
            QMessageBox.warning(self, "Error", "Invalid date format. Use YYYY-MM-DD")
            return

        query_text = """
            UPDATE weight
            SET value = :value, date = :date
            WHERE _id = :id
        """
        params = {"value": value, "date": date, "id": _id}
        result = self.db_manager.execute_query(query_text, params)
        if result:
            print("Weight record updated")
            self.update_all()
        else:
            QMessageBox.warning(self, "Error", "Failed to update weight record")

    def set_current_date(self):
        now = QDateTime.currentDateTime()
        date = now.toString(DATE_FORMAT)
        self.lineEdit_date.setText(date)
        self.lineEdit_weight_date.setText(date)

    def show_tables(self):
        """Show all tables at once"""
        # Show exercises table
        query_text = "SELECT _id, name, unit FROM exercises"
        data = self.db_manager.get_rows(query_text)
        self.models["exercises"] = self.create_table_model(data, ["Exercise", "Unit of Measurement"])
        self.tableView_exercises.setModel(self.models["exercises"])
        self.tableView_exercises.resizeColumnsToContents()

        # Show process table
        query_text = """
            SELECT p._id, e.name, IFNULL(t.type, ''), p.value, e.unit, p.date
            FROM process p
            JOIN exercises e ON p._id_exercises = e._id
            LEFT JOIN types t ON p._id_types = t._id AND t._id_exercises = e._id
            ORDER BY p._id DESC
        """
        rows = self.db_manager.get_rows(query_text)
        data = []
        for row in rows:
            _id = row[0]
            exercise_name = row[1]
            type_name = row[2]
            value = row[3]
            unit = row[4] or "times"
            date = row[5]
            formatted_value = f"{value} {unit}"
            data.append([_id, exercise_name, type_name, formatted_value, date])

        self.models["process"] = self.create_table_model(data, ["Exercise", "Exercise Type", "Quantity", "Date"])
        self.tableView_process.setModel(self.models["process"])
        self.tableView_process.resizeColumnsToContents()

        # Show types table
        query_text = """
            SELECT t._id, e.name, t.type
            FROM types t
            JOIN exercises e ON t._id_exercises = e._id
        """
        data = self.db_manager.get_rows(query_text)
        self.models["types"] = self.create_table_model(data, ["Exercise", "Exercise Type"])
        self.tableView_exercise_types.setModel(self.models["types"])
        self.tableView_exercise_types.resizeColumnsToContents()

        # Show weight table
        query_text = "SELECT _id, value, date FROM weight ORDER BY date DESC"
        data = self.db_manager.get_rows(query_text)
        self.models["weight"] = self.create_table_model(data, ["Weight", "Date"])
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
        current_exercise_index = -1
        if selected_exercise:
            current_exercise_index = exercises.index(selected_exercise) if selected_exercise in exercises else -1

        self.comboBox_exercise.clear()
        self.comboBox_exercise_name.clear()

        for name in exercises:
            self.comboBox_exercise.addItem(name)
            self.comboBox_exercise_name.addItem(name)

        # Restore selection if needed
        if current_exercise_index >= 0:
            self.comboBox_exercise.setCurrentIndex(current_exercise_index)

            # If we have a type to restore too, we need to make sure types are loaded
            if selected_type:
                # Make sure types for this exercise are loaded
                exercise_id = self.db_manager.get_id("exercises", "name", selected_exercise)
                if exercise_id is not None:
                    # Get types for this exercise
                    types = self.db_manager.get_items("types", "type", condition=f"_id_exercises = {exercise_id}")

                    self.comboBox_type.clear()
                    self.comboBox_type.addItem(EMPTY_TYPE)

                    for type_name in types:
                        self.comboBox_type.addItem(type_name)

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

        # Validate current date format
        if not self.is_valid_date(current_date_str):
            now = QDateTime.currentDateTime()
            self.lineEdit_date.setText(now.toString(DATE_FORMAT))
            return

        # Get today's date
        now = QDateTime.currentDateTime()
        today_str = now.toString(DATE_FORMAT)

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


class SetOfExercise:
    def __init__(self, name_exercises, type_types, value, date):
        self.name_exercises = name_exercises
        self.type_types = type_types
        self.value = float(value)
        self.date = date

    def __lt__(self, other):
        return self.value < other.value

    def __str__(self):
        # Format the string to avoid showing empty type
        if self.type_types:
            return f"{self.date}: {self.name_exercises} {self.type_types} {self.value}"
        else:
            return f"{self.date}: {self.name_exercises} {self.value}"


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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.tabWidget.setCurrentIndex(0)
    window.show()
    sys.exit(app.exec())
