import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog
from PySide6.QtSql import QSqlDatabase, QSqlQuery
from PySide6.QtCore import Qt, QDateTime, QSortFilterProxyModel
from PySide6.QtGui import QStandardItemModel, QStandardItem
from collections import defaultdict

import harrix_pylib as h
import harrix_swiss_knife as hsk


config = h.dev.load_config("config/config.json")

class SetOfExercise:
    def __init__(self, name_exercises, type_types, value, date):
        self.name_exercises = name_exercises
        self.type_types = type_types
        self.value = value
        self.date = date

    def __lt__(self, other):
        return self.value < other.value

    def __str__(self):
        return f"{self.date}: {self.name_exercises} {self.type_types} {self.value}"

def compare(set1, set2):
    return set1.value < set2.value

class MainWindow(QMainWindow, hsk.sport_window.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.db = None
        self.model_process = None
        self.model_exercises = None
        self.model_types = None
        self.model_weight = None

        self.init_database()
        self.update_all()

        self.comboBox.currentIndexChanged.connect(self.on_comboBox_currentIndexChanged)
        self.pushButton_add.clicked.connect(self.on_pushButton_add_clicked)
        self.pushButton_delete.clicked.connect(self.on_pushButton_delete_clicked)
        self.pushButton_update.clicked.connect(self.on_pushButton_update_clicked)
        self.pushButton_refresh.clicked.connect(self.on_pushButton_refresh_clicked)
        self.pushButton_exercise_add.clicked.connect(self.on_pushButton_exercise_add_clicked)
        self.pushButton_exercise_delete.clicked.connect(self.on_pushButton_exercise_delete_clicked)
        self.pushButton_exercise_update.clicked.connect(self.on_pushButton_exercise_update_clicked)
        self.pushButton_exercise_refresh.clicked.connect(self.on_pushButton_exercise_refresh_clicked)
        self.pushButton_type_add.clicked.connect(self.on_pushButton_type_add_clicked)
        self.pushButton_type_delete.clicked.connect(self.on_pushButton_type_delete_clicked)
        self.pushButton_type_update.clicked.connect(self.on_pushButton_type_update_clicked)
        self.pushButton_type_refresh.clicked.connect(self.on_pushButton_type_refresh_clicked)
        self.pushButton_weight_add.clicked.connect(self.on_pushButton_weight_add_clicked)
        self.pushButton_weight_delete.clicked.connect(self.on_pushButton_weight_delete_clicked)
        self.pushButton_weight_update.clicked.connect(self.on_pushButton_weight_update_clicked)
        self.pushButton_weight_refresh.clicked.connect(self.on_pushButton_weight_refresh_clicked)
        self.pushButton_statistics_refresh.clicked.connect(self.on_pushButton_statistics_refresh_clicked)
        self.pushButton_export_csv.clicked.connect(self.on_pushButton_export_csv_clicked)

    def init_database(self):
        filename = config["sqlite_sport"]

        if not os.path.exists(filename):
            filename, _ = QFileDialog.getOpenFileName(self, "Открыть базу данных", filename.parent, "База данных SQLite (*.db)")

        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName(filename)

        if self.db.open():
            print("База данных открылась")
        else:
            print("База данных не открылась")

    def update_all(self):
        self.show_process()
        self.show_exercises()
        self.show_types()
        self.show_weight()
        self.for_add()

    def for_add(self):
        query = QSqlQuery()
        query_text = "SELECT * FROM exercises"
        if not query.exec(query_text):
            print("Ошибка при работе с таблицей «exercises»")
            return

        self.comboBox.clear()
        self.comboBox_3.clear()

        while query.next():
            name = query.value(1)
            self.comboBox.addItem(name)
            self.comboBox_3.addItem(name)

        now = QDateTime.currentDateTime()
        date = now.toString("yyyy-MM-dd")
        self.lineEdit.setText(date)
        self.lineEdit_3.setText(date)

    def show_process(self):
        query = QSqlQuery()
        subquery = QSqlQuery()
        query_text = "SELECT * FROM process ORDER BY _id DESC"
        if not query.exec(query_text):
            print("Ошибка при показе таблицы «process»")
            return

        model = QStandardItemModel()

        # Заголовки
        model.setHorizontalHeaderLabels(["Упражнение", "Тип упражнения", "Сколько сделал", "Дата"])

        i = 0
        while query.next():
            # Получаем значения из запроса
            _id = query.value(0)
            _id_exercises = query.value(1)
            _id_types = query.value(2)
            value = query.value(3)
            date = query.value(4)

            # Преобразуем в строки, если необходимо
            _id_exercises = str(_id_exercises)
            _id_types = str(_id_types)
            value = str(value)
            date = str(date)

            # Получаем название упражнения
            subquery_text = f"SELECT name, unit FROM exercises WHERE _id = {_id_exercises}"
            if not subquery.exec(subquery_text):
                print(f"Ошибка при получении упражнения с _id = {_id_exercises}")
                continue
            subquery.next()
            name_exercises = subquery.value(0)
            unit_exercises = subquery.value(1)
            if not unit_exercises:
                unit_exercises = "раз"

            # Получаем тип упражнения
            if _id_types and _id_types != "-1":
                subquery_text = f"SELECT type FROM types WHERE _id = {_id_types} AND _id_exercises = {_id_exercises}"
                if not subquery.exec(subquery_text):
                    print(f"Ошибка при получении типа с _id = {_id_types}")
                    type_types = "[Без типа]"
                else:
                    if subquery.next():
                        type_types = subquery.value(0)
                    else:
                        type_types = "[Без типа]"
            else:
                type_types = "[Без типа]"

            # Добавляем в модель
            item_exercise = QStandardItem(name_exercises)
            item_type = QStandardItem(type_types)
            item_value = QStandardItem(f"{value} {unit_exercises}")
            item_date = QStandardItem(date)

            model.appendRow([item_exercise, item_type, item_value, item_date])
            model.setVerticalHeaderItem(i, QStandardItem(str(_id)))
            i += 1

        self.model_process = QSortFilterProxyModel()
        self.model_process.setSourceModel(model)
        self.tableView.setModel(self.model_process)
        self.tableView.resizeColumnsToContents()

        # Подключаем сигнал для dataChanged
        self.model_process.dataChanged.connect(self.onDataChanged)

    def show_exercises(self):
        query = QSqlQuery()
        query_text = "SELECT * FROM exercises"
        if not query.exec(query_text):
            print("Ошибка при показе таблицы «exercises»")
            return

        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Упражнение", "Единица измерения"])

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

    def show_types(self):
        query = QSqlQuery()
        subquery = QSqlQuery()
        query_text = "SELECT * FROM types"
        if not query.exec(query_text):
            print("Ошибка при показе таблицы «types»")
            return

        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Упражнение", "Тип упражнения"])

        i = 0
        while query.next():
            _id = query.value(0)
            _id_exercises = query.value(1)
            type_name = query.value(2)

            # Получаем название упражнения
            subquery_text = f"SELECT name FROM exercises WHERE _id = {_id_exercises}"
            if not subquery.exec(subquery_text):
                print(f"Ошибка при получении упражнения с _id = {_id_exercises}")
                continue
            subquery.next()
            name_exercises = subquery.value(0)

            item_exercise = QStandardItem(name_exercises)
            item_type = QStandardItem(type_name)

            model.appendRow([item_exercise, item_type])
            model.setVerticalHeaderItem(i, QStandardItem(str(_id)))
            i += 1

        self.model_types = QSortFilterProxyModel()
        self.model_types.setSourceModel(model)
        self.tableView_3.setModel(self.model_types)
        self.tableView_3.resizeColumnsToContents()

    def show_weight(self):
        query = QSqlQuery()
        query_text = "SELECT * FROM weight"
        if not query.exec(query_text):
            print("Ошибка при показе таблицы «weight»")
            return

        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Вес", "Дата"])

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

    def on_comboBox_currentIndexChanged(self):
        arg1 = self.comboBox.currentText()
        query = QSqlQuery()
        subquery = QSqlQuery()
        query_text = f"SELECT * FROM exercises WHERE name = '{arg1}'"
        if query.exec(query_text):
            if query.next():
                _id = query.value(0)
                subquery_text = f"SELECT * FROM types WHERE _id_exercises = {_id}"
                if subquery.exec(subquery_text):
                    self.comboBox_2.clear()
                    self.comboBox_2.addItem("[Без типа]")
                    while subquery.next():
                        type_name = subquery.value(2)
                        self.comboBox_2.addItem(type_name)
            else:
                print("Упражнение не найдено")
        else:
            print("Ошибка при работе с таблицей «exercises»")

    def onDataChanged(self, topLeft, bottomRight):
        # Обработка изменения данных в таблице
        pass  # Можно добавить ваш код, если нужно

    def on_pushButton_add_clicked(self):
        exercise = self.comboBox.currentText()
        type_name = self.comboBox_2.currentText()
        value = str(self.spinBox.value())
        date = self.lineEdit.text()

        query = QSqlQuery()
        subquery = QSqlQuery()

        # Получаем _id_exercises
        query_text = f"SELECT * FROM exercises WHERE name = '{exercise}'"
        if query.exec(query_text):
            if query.next():
                _id_exercises = query.value(0)
            else:
                print("Упражнение не найдено")
                return
        else:
            print("Ошибка при получении _id_exercises")
            return

        # Получаем _id_types
        if type_name != "[Без типа]":
            subquery_text = f"SELECT * FROM types WHERE type = '{type_name}' AND _id_exercises = {_id_exercises}"
            subquery.exec(subquery_text)
            if subquery.next():
                _id_types = subquery.value(0)
            else:
                _id_types = "-1"
        else:
            _id_types = "-1"

        # Вставляем новую запись в process
        insert_text = f"INSERT INTO process (_id_exercises, _id_types, value, date) VALUES({_id_exercises}, '{_id_types}', '{value}', '{date}')"
        if query.exec(insert_text):
            print("Запись добавлена")
        else:
            print("Ошибка при добавлении записи")

        self.update_all()

    def on_pushButton_delete_clicked(self):
        index = self.tableView.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "Ошибка", "Выберите запись для удаления")
            return

        row = index.row()
        _id = self.model_process.sourceModel().verticalHeaderItem(row).text()

        query = QSqlQuery()
        delete_text = f"DELETE FROM process WHERE _id = {_id}"
        if query.exec(delete_text):
            print("Запись удалена")
        else:
            print("Ошибка при удалении записи")

        self.update_all()

    def on_pushButton_update_clicked(self):
        index = self.tableView.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "Ошибка", "Выберите запись для обновления")
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

        query = QSqlQuery()
        subquery = QSqlQuery()

        # Получаем _id_exercises
        query_text = f"SELECT * FROM exercises WHERE name = '{exercise}'"
        if query.exec(query_text):
            if query.next():
                _id_exercises = query.value(0)
            else:
                print("Упражнение не найдено")
                return
        else:
            print("Ошибка при получении _id_exercises")
            return

        # Получаем _id_types
        if type_name and type_name != "[Без типа]":
            subquery_text = f"SELECT * FROM types WHERE type = '{type_name}' AND _id_exercises = {_id_exercises}"
            subquery.exec(subquery_text)
            if subquery.next():
                _id_types = subquery.value(0)
            else:
                _id_types = "-1"
        else:
            _id_types = "-1"

        # Обновляем запись
        update_text = f"UPDATE process SET _id_exercises = {_id_exercises}, _id_types = {_id_types}, date = '{date}', value = '{value}' WHERE _id = {_id}"
        if query.exec(update_text):
            print("Запись обновлена")
        else:
            print("Ошибка при обновлении записи")

        self.update_all()

    def on_pushButton_refresh_clicked(self):
        self.update_all()

    def on_pushButton_exercise_add_clicked(self):
        exercise = self.lineEdit_4.text()
        unit = self.lineEdit_5.text()

        if not exercise:
            QMessageBox.warning(self, "Ошибка", "Введите название упражнения")
            return

        query = QSqlQuery()
        insert_text = f"INSERT INTO exercises (name, unit) VALUES('{exercise}', '{unit}')"
        if query.exec(insert_text):
            print("Упражнение добавлено")
        else:
            print("Ошибка при добавлении упражнения")

        self.update_all()

    def on_pushButton_exercise_delete_clicked(self):
        index = self.tableView_2.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "Ошибка", "Выберите упражнение для удаления")
            return

        row = index.row()
        _id = self.model_exercises.sourceModel().verticalHeaderItem(row).text()

        query = QSqlQuery()
        delete_text = f"DELETE FROM exercises WHERE _id = {_id}"
        if query.exec(delete_text):
            print("Упражнение удалено")
        else:
            print("Ошибка при удалении упражнения")

        self.update_all()

    def on_pushButton_exercise_refresh_clicked(self):
        self.update_all()

    def on_pushButton_type_refresh_clicked(self):
        self.update_all()

    def on_pushButton_weight_refresh_clicked(self):
        self.update_all()

    def on_pushButton_type_delete_clicked(self):
        index = self.tableView_3.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "Ошибка", "Выберите тип для удаления")
            return

        row = index.row()
        _id = self.model_types.sourceModel().verticalHeaderItem(row).text()

        query = QSqlQuery()
        delete_text = f"DELETE FROM types WHERE _id = {_id}"
        if query.exec(delete_text):
            print("Тип удален")
        else:
            print("Ошибка при удалении типа")

        self.update_all()

    def on_pushButton_weight_delete_clicked(self):
        index = self.tableView_4.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "Ошибка", "Выберите запись веса для удаления")
            return

        row = index.row()
        _id = self.model_weight.sourceModel().verticalHeaderItem(row).text()

        query = QSqlQuery()
        delete_text = f"DELETE FROM weight WHERE _id = {_id}"
        if query.exec(delete_text):
            print("Запись веса удалена")
        else:
            print("Ошибка при удалении записи веса")

        self.update_all()

    def on_pushButton_exercise_update_clicked(self):
        index = self.tableView_2.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "Ошибка", "Выберите упражнение для обновления")
            return

        row = index.row()
        _id = self.model_exercises.sourceModel().verticalHeaderItem(row).text()

        model_index_name = self.model_exercises.index(row, 0)
        name = self.model_exercises.data(model_index_name)

        model_index_unit = self.model_exercises.index(row, 1)
        unit = self.model_exercises.data(model_index_unit)

        query = QSqlQuery()
        update_text = f"UPDATE exercises SET name = '{name}', unit = '{unit}' WHERE _id = {_id}"
        if query.exec(update_text):
            print("Упражнение обновлено")
        else:
            print("Ошибка при обновлении упражнения")

        self.update_all()

    def on_pushButton_weight_add_clicked(self):
        value = str(self.doubleSpinBox.value())
        date = self.lineEdit_3.text()

        if not date:
            QMessageBox.warning(self, "Ошибка", "Введите дату")
            return

        query = QSqlQuery()
        insert_text = f"INSERT INTO weight (value, date) VALUES('{value}', '{date}')"
        if query.exec(insert_text):
            print("Вес добавлен")
        else:
            print("Ошибка при добавлении веса")

        self.update_all()

    def on_pushButton_weight_update_clicked(self):
        index = self.tableView_4.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "Ошибка", "Выберите запись веса для обновления")
            return

        row = index.row()
        _id = self.model_weight.sourceModel().verticalHeaderItem(row).text()

        model_index_value = self.model_weight.index(row, 0)
        value = self.model_weight.data(model_index_value)

        model_index_date = self.model_weight.index(row, 1)
        date = self.model_weight.data(model_index_date)

        query = QSqlQuery()
        update_text = f"UPDATE weight SET value = '{value}', date = '{date}' WHERE _id = {_id}"
        if query.exec(update_text):
            print("Запись веса обновлена")
        else:
            print("Ошибка при обновлении записи веса")

        self.update_all()

    def on_pushButton_type_add_clicked(self):
        exercise = self.comboBox_3.currentText()
        type_name = self.lineEdit_6.text()

        if not type_name:
            QMessageBox.warning(self, "Ошибка", "Введите название типа")
            return

        query = QSqlQuery()
        subquery = QSqlQuery()

        # Получаем _id_exercises
        query_text = f"SELECT * FROM exercises WHERE name = '{exercise}'"
        if query.exec(query_text):
            if query.next():
                _id_exercises = query.value(0)
            else:
                print("Упражнение не найдено")
                return
        else:
            print("Ошибка при получении _id_exercises")
            return

        insert_text = f"INSERT INTO types (_id_exercises, type) VALUES({_id_exercises}, '{type_name}')"
        if query.exec(insert_text):
            print("Тип добавлен")
        else:
            print("Ошибка при добавлении типа")

        self.update_all()

    def on_pushButton_type_update_clicked(self):
        index = self.tableView_3.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "Ошибка", "Выберите тип для обновления")
            return

        row = index.row()
        _id = self.model_types.sourceModel().verticalHeaderItem(row).text()

        model_index_type = self.model_types.index(row, 1)
        type_name = self.model_types.data(model_index_type)

        model_index_exercise = self.model_types.index(row, 0)
        exercise = self.model_types.data(model_index_exercise)

        query = QSqlQuery()
        subquery = QSqlQuery()

        # Получаем _id_exercises
        query_text = f"SELECT * FROM exercises WHERE name = '{exercise}'"
        if query.exec(query_text):
            if query.next():
                _id_exercises = query.value(0)
            else:
                print("Упражнение не найдено")
                return
        else:
            print("Ошибка при получении _id_exercises")
            return

        update_text = f"UPDATE types SET _id_exercises = {_id_exercises}, type = '{type_name}' WHERE _id = {_id}"
        if query.exec(update_text):
            print("Тип обновлен")
        else:
            print("Ошибка при обновлении типа")

        self.update_all()

    def save_as_csv(self, filename):
        if not filename:
            return

        model = self.model_process.sourceModel()

        with open(filename, 'w', encoding='utf-8') as f:
            # Заголовки
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
        print("CSV сохранен")

    def on_pushButton_export_csv_clicked(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Сохранить таблицу", "", "CSV (*.csv)")
        if filename:
            self.save_as_csv(filename)

    def on_pushButton_statistics_refresh_clicked(self):
        self.textEdit.clear()

        query = QSqlQuery()
        subquery = QSqlQuery()
        query_text = "SELECT * FROM process ORDER BY _id DESC"
        if not query.exec(query_text):
            print("Ошибка при показе таблицы «process»")
            return

        data = defaultdict(list)

        while query.next():
            _id = query.value(0)
            _id_exercises = query.value(1)
            _id_types = query.value(2)
            value = query.value(3)
            date = query.value(4)

            # Получаем название упражнения
            subquery_text = f"SELECT name, unit FROM exercises WHERE _id = {_id_exercises}"
            if not subquery.exec(subquery_text):
                print(f"Ошибка при получении упражнения с _id = {_id_exercises}")
                continue
            subquery.next()
            name_exercises = subquery.value(0)
            unit_exercises = subquery.value(1)
            if not unit_exercises:
                unit_exercises = "раз"

            # Получаем тип упражнения
            if _id_types and _id_types != -1:
                subquery_text = f"SELECT type FROM types WHERE _id = {_id_types}"
                if not subquery.exec(subquery_text):
                    print(f"Ошибка при получении типа с _id = {_id_types}")
                    type_types = "[Без типа]"
                else:
                    if subquery.next():
                        type_types = subquery.value(0)
                    else:
                        type_types = "[Без типа]"
            else:
                type_types = "[Без типа]"

            key = f"{name_exercises} {type_types}"
            data[key].append(SetOfExercise(name_exercises, type_types, value, date))

        result_text = ""
        for key, exercises in data.items():
            result_text += key + "\n"
            exercises.sort(key=lambda x: x.value, reverse=True)
            for i, exercise in enumerate(exercises):
                now = QDateTime.currentDateTime()
                today = now.toString("yyyy-MM-dd")
                today_marker = " <------------------------ TODAY" if exercise.date == today else ""
                result_text += f"{exercise}{today_marker}\n"
                if i >= 3:
                    break
            result_text += "--------\n"

        self.textEdit.setText(result_text)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
