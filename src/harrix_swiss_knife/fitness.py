import os
import sys
from collections import defaultdict

import harrix_pylib as h
from PySide6.QtCore import QDateTime, QSortFilterProxyModel, Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtSql import QSqlDatabase, QSqlQuery
from PySide6.QtWidgets import QApplication, QFileDialog, QMainWindow, QMessageBox

from harrix_swiss_knife import fitness_window

config = h.dev.load_config("config/config.json")


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

    def get_all_exercises(self):
        query_text = "SELECT name FROM exercises"
        query = self.execute_query(query_text)
        exercises = []
        while query.next():
            exercises.append(query.value(0))
        return exercises

    def get_exercise_id(self, exercise_name):
        query_text = "SELECT _id FROM exercises WHERE name = :name"
        params = {"name": exercise_name}
        query = self.execute_query(query_text, params)
        if query and query.next():
            return query.value(0)
        else:
            print("Exercise not found")
            return None

    def get_exercise_name(self, exercise_id):
        query_text = "SELECT name FROM exercises WHERE _id = :exercise_id"
        params = {"exercise_id": exercise_id}
        query = self.execute_query(query_text, params)
        if query and query.next():
            return query.value(0)
        else:
            return None

    def get_exercise_unit(self, exercise_id):
        query_text = "SELECT unit FROM exercises WHERE _id = :exercise_id"
        params = {"exercise_id": exercise_id}
        query = self.execute_query(query_text, params)
        if query and query.next():
            unit = query.value(0)
            return unit if unit else "times"
        else:
            return "times"

    def get_type_id(self, type_name, exercise_id):
        query_text = """
            SELECT _id FROM types
            WHERE type = :type AND _id_exercises = :exercise_id
        """
        params = {"type": type_name, "exercise_id": exercise_id}
        query = self.execute_query(query_text, params)
        if query and query.next():
            return query.value(0)
        else:
            return -1

    def get_type_name(self, type_id, exercise_id):
        if type_id == -1:
            return "[No Type]"
        query_text = """
            SELECT type FROM types
            WHERE _id = :type_id AND _id_exercises = :exercise_id
        """
        params = {"type_id": type_id, "exercise_id": exercise_id}
        query = self.execute_query(query_text, params)
        if query and query.next():
            return query.value(0)
        else:
            return "[No Type]"


class MainWindow(QMainWindow, fitness_window.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.db_manager = None
        self.model_process = None
        self.model_exercises = None
        self.model_types = None
        self.model_weight = None

        self.init_database()
        self.update_all()
        self.connect_signals()

    def connect_signals(self):
        self.comboBox.currentIndexChanged.connect(self.on_exercise_changed)
        self.pushButton_add.clicked.connect(self.on_add_record)
        self.pushButton_delete.clicked.connect(self.on_delete_record)
        self.pushButton_update.clicked.connect(self.on_update_record)
        self.pushButton_refresh.clicked.connect(self.update_all)
        self.pushButton_exercise_add.clicked.connect(self.on_add_exercise)
        self.pushButton_exercise_delete.clicked.connect(self.on_delete_exercise)
        self.pushButton_exercise_update.clicked.connect(self.on_update_exercise)
        self.pushButton_exercise_refresh.clicked.connect(self.update_all)
        self.pushButton_type_add.clicked.connect(self.on_add_type)
        self.pushButton_type_delete.clicked.connect(self.on_delete_type)
        self.pushButton_type_update.clicked.connect(self.on_update_type)
        self.pushButton_type_refresh.clicked.connect(self.update_all)
        self.pushButton_weight_add.clicked.connect(self.on_add_weight)
        self.pushButton_weight_delete.clicked.connect(self.on_delete_weight)
        self.pushButton_weight_update.clicked.connect(self.on_update_weight)
        self.pushButton_weight_refresh.clicked.connect(self.update_all)
        self.pushButton_statistics_refresh.clicked.connect(self.on_refresh_statistics)
        self.pushButton_export_csv.clicked.connect(self.on_export_csv)

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

    def on_add_exercise(self):
        exercise = self.lineEdit_4.text()
        unit = self.lineEdit_5.text()

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

    def on_add_record(self):
        exercise_name = self.comboBox.currentText()
        type_name = self.comboBox_2.currentText()
        value = str(self.spinBox.value())
        date = self.lineEdit.text()

        exercise_id = self.db_manager.get_exercise_id(exercise_name)
        if exercise_id is None:
            return

        if type_name != "[No Type]":
            type_id = self.db_manager.get_type_id(type_name, exercise_id)
        else:
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
            self.update_all()
        else:
            QMessageBox.warning(self, "Error", "Failed to add record")

    def on_add_type(self):
        exercise_name = self.comboBox_3.currentText()
        type_name = self.lineEdit_6.text()

        if not type_name:
            QMessageBox.warning(self, "Error", "Enter type name")
            return

        exercise_id = self.db_manager.get_exercise_id(exercise_name)
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

    def on_add_weight(self):
        value = str(self.doubleSpinBox.value())
        date = self.lineEdit_3.text()

        if not date:
            QMessageBox.warning(self, "Error", "Enter date")
            return

        query_text = "INSERT INTO weight (value, date) VALUES (:value, :date)"
        params = {"value": value, "date": date}
        result = self.db_manager.execute_query(query_text, params)
        if result:
            print("Weight added")
            self.update_all()
        else:
            QMessageBox.warning(self, "Error", "Failed to add weight")

    def on_delete_exercise(self):
        index = self.tableView_2.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "Error", "Select an exercise to delete")
            return

        row = index.row()
        _id = self.model_exercises.sourceModel().verticalHeaderItem(row).text()

        query_text = "DELETE FROM exercises WHERE _id = :id"
        params = {"id": _id}
        result = self.db_manager.execute_query(query_text, params)
        if result:
            print("Exercise deleted")
            self.update_all()
        else:
            QMessageBox.warning(self, "Error", "Failed to delete exercise")

    def on_delete_record(self):
        index = self.tableView.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "Error", "Select a record to delete")
            return

        row = index.row()
        _id = self.model_process.sourceModel().verticalHeaderItem(row).text()

        query_text = "DELETE FROM process WHERE _id = :id"
        params = {"id": _id}
        result = self.db_manager.execute_query(query_text, params)
        if result:
            print("Record deleted")
            self.update_all()
        else:
            QMessageBox.warning(self, "Error", "Failed to delete record")

    def on_delete_type(self):
        index = self.tableView_3.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "Error", "Select a type to delete")
            return

        row = index.row()
        _id = self.model_types.sourceModel().verticalHeaderItem(row).text()

        query_text = "DELETE FROM types WHERE _id = :id"
        params = {"id": _id}
        result = self.db_manager.execute_query(query_text, params)
        if result:
            print("Type deleted")
            self.update_all()
        else:
            QMessageBox.warning(self, "Error", "Failed to delete type")

    def on_delete_weight(self):
        index = self.tableView_4.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "Error", "Select a weight record to delete")
            return

        row = index.row()
        _id = self.model_weight.sourceModel().verticalHeaderItem(row).text()

        query_text = "DELETE FROM weight WHERE _id = :id"
        params = {"id": _id}
        result = self.db_manager.execute_query(query_text, params)
        if result:
            print("Weight record deleted")
            self.update_all()
        else:
            QMessageBox.warning(self, "Error", "Failed to delete weight record")

    def on_exercise_changed(self):
        exercise_name = self.comboBox.currentText()
        exercise_id = self.db_manager.get_exercise_id(exercise_name)
        if exercise_id is None:
            return

        query_text = "SELECT type FROM types WHERE _id_exercises = :exercise_id"
        params = {"exercise_id": exercise_id}
        query = self.db_manager.execute_query(query_text, params)

        self.comboBox_2.clear()
        self.comboBox_2.addItem("[No Type]")

        while query.next():
            type_name = query.value(0)
            self.comboBox_2.addItem(type_name)

    def on_export_csv(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save Table", "", "CSV (*.csv)")
        if filename:
            self.save_as_csv(filename)

    def on_refresh_statistics(self):
        self.textEdit.clear()

        query_text = "SELECT * FROM process ORDER BY _id DESC"
        query = self.db_manager.execute_query(query_text)
        if not query:
            print("Error displaying 'process' table")
            return

        data = defaultdict(list)

        while query.next():
            exercise_id = query.value(1)
            type_id = query.value(2)
            value = query.value(3)
            date = query.value(4)

            exercise_name = self.db_manager.get_exercise_name(exercise_id)
            type_name = self.db_manager.get_type_name(type_id, exercise_id)

            key = f"{exercise_name} {type_name}"
            data[key].append(SetOfExercise(exercise_name, type_name, value, date))

        result_text = ""
        for key, exercises in data.items():
            result_text += key + "\n"
            exercises.sort(reverse=True)
            for i, exercise in enumerate(exercises):
                now = QDateTime.currentDateTime()
                today = now.toString("yyyy-MM-dd")
                today_marker = " <--- TODAY" if exercise.date == today else ""
                result_text += f"{exercise}{today_marker}\n"
                if i >= 3:
                    break
            result_text += "--------\n"

        self.textEdit.setText(result_text)

    def on_update_exercise(self):
        index = self.tableView_2.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "Error", "Select an exercise to update")
            return

        row = index.row()
        _id = self.model_exercises.sourceModel().verticalHeaderItem(row).text()

        model_index_name = self.model_exercises.index(row, 0)
        name = self.model_exercises.data(model_index_name)

        model_index_unit = self.model_exercises.index(row, 1)
        unit = self.model_exercises.data(model_index_unit)

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
        index = self.tableView.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "Error", "Select a record to update")
            return

        row = index.row()
        _id = self.model_process.sourceModel().verticalHeaderItem(row).text()

        model_index_date = self.model_process.index(row, 3)
        date = self.model_process.data(model_index_date)

        model_index_value = self.model_process.index(row, 2)
        value_raw = self.model_process.data(model_index_value)
        value = value_raw.split(" ")[0]

        model_index_exercise = self.model_process.index(row, 0)
        exercise = self.model_process.data(model_index_exercise)

        model_index_type = self.model_process.index(row, 1)
        type_name = self.model_process.data(model_index_type)

        exercise_id = self.db_manager.get_exercise_id(exercise)
        if exercise_id is None:
            return

        if type_name != "[No Type]":
            type_id = self.db_manager.get_type_id(type_name, exercise_id)
        else:
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
        index = self.tableView_3.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "Error", "Select a type to update")
            return

        row = index.row()
        _id = self.model_types.sourceModel().verticalHeaderItem(row).text()

        model_index_type = self.model_types.index(row, 1)
        type_name = self.model_types.data(model_index_type)

        model_index_exercise = self.model_types.index(row, 0)
        exercise_name = self.model_types.data(model_index_exercise)

        exercise_id = self.db_manager.get_exercise_id(exercise_name)
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
        index = self.tableView_4.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "Error", "Select a weight record to update")
            return

        row = index.row()
        _id = self.model_weight.sourceModel().verticalHeaderItem(row).text()

        model_index_value = self.model_weight.index(row, 0)
        value = self.model_weight.data(model_index_value)

        model_index_date = self.model_weight.index(row, 1)
        date = self.model_weight.data(model_index_date)

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

    def save_as_csv(self, filename):
        if not filename:
            return

        model = self.model_process.sourceModel()

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

    def show_exercises(self):
        query_text = "SELECT * FROM exercises"
        query = self.db_manager.execute_query(query_text)
        if not query:
            print("Error displaying 'exercises' table")
            return

        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Exercise", "Unit of Measurement"])

        i = 0
        while query.next():
            _id = query.value(0)
            name = query.value(1)
            unit = query.value(2)

            item_name = QStandardItem(name)
            item_unit = QStandardItem(unit)

            model.appendRow([item_name, item_unit])
            model.setVerticalHeaderItem(i, QStandardItem(str(_id)))
            i += 1

        self.model_exercises = QSortFilterProxyModel()
        self.model_exercises.setSourceModel(model)
        self.tableView_2.setModel(self.model_exercises)
        self.tableView_2.resizeColumnsToContents()

    def show_process(self):
        query_text = "SELECT * FROM process ORDER BY _id DESC"
        query = self.db_manager.execute_query(query_text)
        if not query:
            print("Error displaying 'process' table")
            return

        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Exercise", "Exercise Type", "Quantity", "Date"])

        i = 0
        while query.next():
            _id = query.value(0)
            exercise_id = query.value(1)
            type_id = query.value(2)
            value = query.value(3)
            date = query.value(4)

            exercise_name = self.db_manager.get_exercise_name(exercise_id)
            unit = self.db_manager.get_exercise_unit(exercise_id)
            type_name = self.db_manager.get_type_name(type_id, exercise_id)

            item_exercise = QStandardItem(exercise_name)
            item_type = QStandardItem(type_name)
            item_value = QStandardItem(f"{value} {unit}")
            item_date = QStandardItem(date)

            model.appendRow([item_exercise, item_type, item_value, item_date])
            model.setVerticalHeaderItem(i, QStandardItem(str(_id)))
            i += 1

        self.model_process = QSortFilterProxyModel()
        self.model_process.setSourceModel(model)
        self.tableView.setModel(self.model_process)
        self.tableView.resizeColumnsToContents()

    def show_types(self):
        query_text = "SELECT * FROM types"
        query = self.db_manager.execute_query(query_text)
        if not query:
            print("Error displaying 'types' table")
            return

        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Exercise", "Exercise Type"])

        i = 0
        while query.next():
            _id = query.value(0)
            exercise_id = query.value(1)
            type_name = query.value(2)

            exercise_name = self.db_manager.get_exercise_name(exercise_id)

            item_exercise = QStandardItem(exercise_name)
            item_type = QStandardItem(type_name)

            model.appendRow([item_exercise, item_type])
            model.setVerticalHeaderItem(i, QStandardItem(str(_id)))
            i += 1

        self.model_types = QSortFilterProxyModel()
        self.model_types.setSourceModel(model)
        self.tableView_3.setModel(self.model_types)
        self.tableView_3.resizeColumnsToContents()

    def show_weight(self):
        query_text = "SELECT * FROM weight"
        query = self.db_manager.execute_query(query_text)
        if not query:
            print("Error displaying 'weight' table")
            return

        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Weight", "Date"])

        i = 0
        while query.next():
            _id = query.value(0)
            value = query.value(1)
            date = query.value(2)

            item_value = QStandardItem(str(value))
            item_date = QStandardItem(str(date))

            model.appendRow([item_value, item_date])
            model.setVerticalHeaderItem(i, QStandardItem(str(_id)))
            i += 1

        self.model_weight = QSortFilterProxyModel()
        self.model_weight.setSourceModel(model)
        self.tableView_4.setModel(self.model_weight)
        self.tableView_4.resizeColumnsToContents()

    def update_all(self):
        self.show_process()
        self.show_exercises()
        self.show_types()
        self.show_weight()

        exercises = self.db_manager.get_all_exercises()

        self.comboBox.clear()
        self.comboBox_3.clear()

        for name in exercises:
            self.comboBox.addItem(name)
            self.comboBox_3.addItem(name)

        now = QDateTime.currentDateTime()
        date = now.toString("yyyy-MM-dd")
        self.lineEdit.setText(date)
        self.lineEdit_3.setText(date)
        self.on_exercise_changed()


class SetOfExercise:
    def __init__(self, name_exercises, type_types, value, date):
        self.name_exercises = name_exercises
        self.type_types = type_types
        self.value = float(value)
        self.date = date

    def __lt__(self, other):
        return self.value < other.value

    def __str__(self):
        return f"{self.date}: {self.name_exercises} {self.type_types} {self.value}"


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
