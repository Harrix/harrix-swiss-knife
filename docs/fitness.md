---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# File `fitness.py`

<details>
<summary>📖 Contents</summary>

## Contents

- [Class `MainWindow`](#class-mainwindow)
  - [Method `__init__`](#method-__init__)
  - [Method `_connect_signals`](#method-_connect_signals)
  - [Method `_create_table_model`](#method-_create_table_model)
  - [Method `_increment_date_after_add`](#method-_increment_date_after_add)
  - [Method `_init_database`](#method-_init_database)
  - [Method `_init_filter_controls`](#method-_init_filter_controls)
  - [Method `_is_valid_date`](#method-_is_valid_date)
  - [Method `_update_comboboxes`](#method-_update_comboboxes)
  - [Method `_update_record_generic`](#method-_update_record_generic)
  - [Method `add_record_generic`](#method-add_record_generic)
  - [Method `apply_filter`](#method-apply_filter)
  - [Method `clear_filter`](#method-clear_filter)
  - [Method `delete_record`](#method-delete_record)
  - [Method `on_add_exercise`](#method-on_add_exercise)
  - [Method `on_add_record`](#method-on_add_record)
  - [Method `on_add_type`](#method-on_add_type)
  - [Method `on_add_weight`](#method-on_add_weight)
  - [Method `on_exercise_changed`](#method-on_exercise_changed)
  - [Method `on_export_csv`](#method-on_export_csv)
  - [Method `on_refresh_statistics`](#method-on_refresh_statistics)
  - [Method `on_tab_changed`](#method-on_tab_changed)
  - [Method `on_update_exercises`](#method-on_update_exercises)
  - [Method `on_update_process`](#method-on_update_process)
  - [Method `on_update_types`](#method-on_update_types)
  - [Method `on_update_weight`](#method-on_update_weight)
  - [Method `set_current_date`](#method-set_current_date)
  - [Method `show_tables`](#method-show_tables)
  - [Method `update_all`](#method-update_all)
  - [Method `update_filter_comboboxes`](#method-update_filter_comboboxes)
  - [Method `update_filter_type_combobox`](#method-update_filter_type_combobox)

</details>

## Class `MainWindow`

```python
class MainWindow(QMainWindow, fitness_window.Ui_MainWindow)
```

Main application window for the fitness tracking application.

This class implements the main GUI window for the fitness tracker, providing
functionality to record exercises, weight measurements, and track progress.
It manages database operations for storing and retrieving fitness data.

Attributes:

- `_SAFE_TABLES` (`frozenset[str]`): Set of table names that can be safely modified,
  containing "process", "exercises", "types", and "weight".

- `db_manager` (`fitness_database_manager.FitnessDatabaseManager | None`): Database
  connection manager. Defaults to `None` until initialized.

- `models` (`dict[str, QSortFilterProxyModel | None]`): Dictionary of table models keyed
  by table name. All values default to `None` until tables are loaded.

- `table_config` (`dict[str, tuple[QTableView, str, list[str]]]`): Configuration for each
  table, mapping table names to tuples of (table view widget, model key, column headers).

<details>
<summary>Code:</summary>

```python
class MainWindow(QMainWindow, fitness_window.Ui_MainWindow):

    _SAFE_TABLES: frozenset[str] = frozenset(
        {"process", "exercises", "types", "weight"},
    )

    def __init__(self) -> None:  # noqa: D107  (inherited from Qt widgets)
        super().__init__()
        self.setupUi(self)

        self.db_manager: fitness_database_manager.FitnessDatabaseManager | None = None

        self.models: dict[str, QSortFilterProxyModel | None] = {
            "process": None,
            "exercises": None,
            "types": None,
            "weight": None,
        }

        self.table_config: dict[str, tuple[QTableView, str, list[str]]] = {
            "process": (
                self.tableView_process,
                "process",
                ["Exercise", "Exercise Type", "Quantity", "Date"],
            ),
            "exercises": (
                self.tableView_exercises,
                "exercises",
                ["Exercise", "Unit of Measurement"],
            ),
            "types": (
                self.tableView_exercise_types,
                "types",
                ["Exercise", "Exercise Type"],
            ),
            "weight": (self.tableView_weight, "weight", ["Weight", "Date"]),
        }

        self._init_database()
        self._connect_signals()
        self._init_filter_controls()
        self.update_all()

    def _connect_signals(self) -> None:
        """Wire Qt widgets to their Python slots.

        Connects all UI elements to their respective handler methods, including:

        - ComboBox change events
        - Button click events for adding, updating, and deleting records
        - Tab change events
        - Statistics and export functionality
        """
        self.comboBox_exercise.currentIndexChanged.connect(
            self.on_exercise_changed,
        )
        self.pushButton_add.clicked.connect(self.on_add_record)

        for action, button_prefix in [
            ("delete", "delete"),
            ("update", "update"),
            ("refresh", "refresh"),
        ]:
            for table_name in self.table_config:
                btn_name = (
                    f"pushButton_{button_prefix}"
                    if table_name == "process"
                    else f"pushButton_{table_name}_{button_prefix}"
                )
                button = getattr(self, btn_name)
                if action == "delete":
                    button.clicked.connect(partial(self.delete_record, table_name))
                elif action == "update":
                    button.clicked.connect(getattr(self, f"on_update_{table_name}"))
                else:
                    button.clicked.connect(self.update_all)

        # Add buttons
        self.pushButton_exercise_add.clicked.connect(self.on_add_exercise)
        self.pushButton_type_add.clicked.connect(self.on_add_type)
        self.pushButton_weight_add.clicked.connect(self.on_add_weight)

        # Stats & export
        self.pushButton_statistics_refresh.clicked.connect(
            self.on_refresh_statistics,
        )
        self.pushButton_export_csv.clicked.connect(self.on_export_csv)

        # Tab change
        self.tabWidget.currentChanged.connect(self.on_tab_changed)

    def _create_table_model(
        self,
        data: list[list[str]],
        headers: list[str],
        id_column: int = 0,
    ) -> QSortFilterProxyModel:
        """Return a proxy model filled with *data*.

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

    def _increment_date_after_add(self) -> None:
        """Move *date* edit one day forward unless it already shows today.

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
        """Open the SQLite file from *config* (ask the user if missing).

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
            self.db_manager = fitness_database_manager.FitnessDatabaseManager(
                str(filename),
            )
        except (OSError, RuntimeError) as exc:
            QMessageBox.critical(self, "Error", str(exc))
            sys.exit(1)

    def _init_filter_controls(self) -> None:
        """Prepare widgets on the *Filters* group box.

        Initializes the filter controls with default values:

        - Sets the date range to the last month
        - Disables date filtering by default
        - Connects filter-related signals to their handlers
        """
        current_date = QDateTime.currentDateTime().date()
        self.dateEdit_filter_from.setDate(current_date.addMonths(-1))
        self.dateEdit_filter_to.setDate(current_date)

        self.checkBox_use_date_filter.setChecked(False)

        self.comboBox_filter_exercise.currentIndexChanged.connect(
            self.update_filter_type_combobox,
        )
        self.pushButton_apply_filter.clicked.connect(self.apply_filter)
        self.pushButton_clear_filter.clicked.connect(self.clear_filter)

    @staticmethod
    def _is_valid_date(date_str: str) -> bool:
        """Return *True* if `YYYY-MM-DD` formatted *date_str* is correct.

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

    def _update_comboboxes(
        self,
        *,
        selected_exercise: str | None = None,
        selected_type: str | None = None,
    ) -> None:
        """Refresh exercise/type combo-boxes (optionally keep a selection).

        Updates the exercise and exercise type comboboxes with current data from the database.
        Can optionally maintain the current selections.

        Args:

        - `selected_exercise` (`str | None`): Exercise name to select after refresh. Defaults to `None`.
        - `selected_type` (`str | None`): Exercise type to select after refresh. Defaults to `None`.

        """
        exercises = self.db_manager.get_exercises_by_frequency(500)

        self.comboBox_exercise.blockSignals(True)  # noqa: FBT003
        self.comboBox_exercise.clear()
        self.comboBox_exercise.addItems(exercises)
        self.comboBox_exercise.blockSignals(False)  # noqa: FBT003

        self.comboBox_exercise_name.clear()
        self.comboBox_exercise_name.addItems(exercises)

        if selected_exercise and selected_exercise in exercises:
            idx = exercises.index(selected_exercise)
            self.comboBox_exercise.setCurrentIndex(idx)

            if selected_type:
                ex_id = self.db_manager.get_id("exercises", "name", selected_exercise)
                if ex_id is not None:
                    types = self.db_manager.get_items(
                        "types",
                        "type",
                        condition=f"_id_exercises = {ex_id}",
                    )
                    self.comboBox_type.clear()
                    self.comboBox_type.addItem("")
                    self.comboBox_type.addItems(types)
                    t_idx = self.comboBox_type.findText(selected_type)
                    if t_idx >= 0:
                        self.comboBox_type.setCurrentIndex(t_idx)
        else:
            self.on_exercise_changed()

    def _update_record_generic(
        self,
        table_name: str,
        model_key: str,
        query_text: str,
        params_extractor: Callable[
            [int, QSortFilterProxyModel, str],
            dict,
        ],
    ) -> None:
        """Low-level generic UPDATE handler.

        Args:

        - `table_name` (`str`): Name of the table being updated (for error messages).
        - `model_key` (`str`): Key for accessing the model in the models dictionary.
        - `query_text` (`str`): SQL update query with placeholders.
        - `params_extractor` (`Callable`): Function to extract parameters from the selected row.

        """
        table_view = next(tv for tv, mkey, _ in self.table_config.values() if mkey == model_key)
        index = table_view.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "Error", "Select a record to update")
            return

        model = self.models[model_key]
        row = index.row()
        _id = model.sourceModel().verticalHeaderItem(row).text()
        params = params_extractor(row, model, _id)

        if self.db_manager.execute_query(query_text, params):
            self.update_all()
        else:
            QMessageBox.warning(self, "Error", f"Failed to update {table_name}")

    def add_record_generic(
        self,
        table_name: str,
        query_text: str,
        params: dict,
    ) -> bool:
        """Add a single row to *any* table.

        Args:

        - `table_name` (`str`): Target table (must be one of `self._SAFE_TABLES`).
        - `query_text` (`str`): SQL *INSERT* statement with named placeholders.
        - `params` (`dict`): Mapping for the placeholders.

        Returns:

        - `bool`: *True* if the row was written successfully.

        Raises:

        - `ValueError`: If table_name is not in _SAFE_TABLES.

        """
        if table_name not in self._SAFE_TABLES:
            error_message = f"Illegal table name: {table_name}"
            raise ValueError(error_message)

        result = self.db_manager.execute_query(query_text, params)
        if result:
            self.update_all()
            return True

        QMessageBox.warning(self, "Error", f"Failed to add to {table_name}")
        return False

    def apply_filter(self) -> None:
        """Apply combo-box/date filters to the *process* table.

        Applies the currently selected filters to the process table:

        - Exercise filter
        - Exercise type filter
        - Date range filter (if enabled)

        Updates the process table view with the filtered results.
        """
        exercise = self.comboBox_filter_exercise.currentText()
        exercise_type = self.comboBox_filter_type.currentText()
        use_date_filter = self.checkBox_use_date_filter.isChecked()
        date_from = self.dateEdit_filter_from.date().toString("yyyy-MM-dd") if use_date_filter else ""
        date_to = self.dateEdit_filter_to.date().toString("yyyy-MM-dd") if use_date_filter else ""

        conditions: list[str] = []
        params: dict[str, str] = {}

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

        query_text = """
            SELECT p._id,
                   e.name,
                   IFNULL(t.type, ''),
                   p.value,
                   e.unit,
                   p.date
            FROM process p
            JOIN exercises e ON p._id_exercises = e._id
            LEFT JOIN types t
                 ON p._id_types = t._id
                AND t._id_exercises = e._id
        """

        if conditions:
            query_text += " WHERE " + " AND ".join(conditions)

        query_text += " ORDER BY p._id DESC"

        rows = self.db_manager.get_rows(query_text, params)
        data = [[row[0], row[1], row[2], f"{row[3]} {row[4] or 'times'}", row[5]] for row in rows]
        self.models["process"] = self._create_table_model(
            data,
            self.table_config["process"][2],
        )
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

    def delete_record(self, table_name: str) -> None:
        """Delete selected row from *table_name* (must be safe).

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
        _id = model.sourceModel().verticalHeaderItem(row).text()

        # Explicitly use a constant query and bind the identifier
        query = f"DELETE FROM {table_name} WHERE _id = :id"
        if self.db_manager.execute_query(query, {"id": _id}):
            self.update_all()
        else:
            QMessageBox.warning(self, "Error", f"Deletion failed in {table_name}")

    def on_add_exercise(self) -> None:
        """Insert a new exercise.

        Adds a new exercise to the database using the name and unit values
        from the input fields. Shows an error message if the exercise name is empty.
        """
        exercise = self.lineEdit_exercise_name.text().strip()
        unit = self.lineEdit_exercise_unit.text().strip()

        if not exercise:
            QMessageBox.warning(self, "Error", "Enter exercise name")
            return

        self.add_record_generic(
            "exercises",
            "INSERT INTO exercises (name, unit) VALUES (:name, :unit)",
            {"name": exercise, "unit": unit},
        )

    def on_add_record(self) -> None:
        """Insert a new *process* row.

        Adds a new exercise record to the process table using the currently selected
        exercise, type, count, and date values. Automatically advances the date
        after successful addition.
        """
        exercise = self.comboBox_exercise.currentText()
        ex_id = self.db_manager.get_id("exercises", "name", exercise)
        if ex_id is None:
            return

        type_name = self.comboBox_type.currentText()
        type_id = (
            self.db_manager.get_id(
                "types",
                "type",
                type_name,
                condition=f"_id_exercises = {ex_id}",
            )
            if type_name
            else -1
        )

        # Store current date before adding record
        current_date = self.dateEdit.date()

        params = {
            "exercise_id": ex_id,
            "type_id": type_id or -1,
            "value": str(self.spinBox_count.value()),
            "date": current_date.toString("yyyy-MM-dd"),
        }

        # Execute the query directly instead of using add_record_generic
        # to avoid triggering update_all() which resets the date
        query_text = (
            "INSERT INTO process (_id_exercises, _id_types, value, date) VALUES (:exercise_id, :type_id, :value, :date)"
        )

        result = self.db_manager.execute_query(query_text, params)
        if result:
            # Apply date increment logic
            self._increment_date_after_add()

            # Update UI without resetting the date
            self.show_tables()
            self._update_comboboxes(
                selected_exercise=exercise,
                selected_type=type_name,
            )
            self.update_filter_comboboxes()
        else:
            QMessageBox.warning(self, "Error", "Failed to add to process")

    def on_add_type(self) -> None:
        """Insert a new exercise *type* for the selected exercise.

        Adds a new exercise type for the selected exercise. Shows an error
        message if the type name is empty.
        """
        exercise = self.comboBox_exercise_name.currentText()
        ex_id = self.db_manager.get_id("exercises", "name", exercise)
        if ex_id is None:
            return

        type_name = self.lineEdit_exercise_type.text().strip()
        if not type_name:
            QMessageBox.warning(self, "Error", "Enter type name")
            return

        self.add_record_generic(
            "types",
            "INSERT INTO types (_id_exercises, type) VALUES (:ex, :tp)",
            {"ex": ex_id, "tp": type_name},
        )

    def on_add_weight(self) -> None:
        """Insert a new weight measurement.

        Adds a new weight record to the database using the current weight value
        and date from the input fields.
        """
        self.add_record_generic(
            "weight",
            "INSERT INTO weight (value, date) VALUES (:val, :dt)",
            {
                "val": str(self.doubleSpinBox_weight.value()),
                "dt": self.lineEdit_weight_date.text(),
            },
        )

    def on_exercise_changed(self) -> None:
        """Load exercise types for the newly selected exercise in *comboBox_type*.

        Updates the exercise type combo box with the types associated with the
        currently selected exercise.
        """
        exercise = self.comboBox_exercise.currentText()
        ex_id = self.db_manager.get_id("exercises", "name", exercise)
        if ex_id is None:
            return
        types = self.db_manager.get_items(
            "types",
            "type",
            condition=f"_id_exercises = {ex_id}",
        )
        self.comboBox_type.clear()
        self.comboBox_type.addItem("")
        self.comboBox_type.addItems(types)

    def on_export_csv(self) -> None:
        """Save current *process* view to a CSV file (semicolon-separated).

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
        """Populate the statistics text-edit with the four best results per key.

        Retrieves exercise data from the database and displays the top four
        results for each exercise/type combination in the statistics text edit.
        Highlights today's entries.
        """
        self.textEdit_statistics.clear()

        rows = self.db_manager.get_rows(
            """
            SELECT e.name,
                   IFNULL(t.type, ''),
                   p.value,
                   p.date
            FROM process p
            JOIN exercises e ON p._id_exercises = e._id
            LEFT JOIN types t ON p._id_types = t._id
            ORDER BY p._id DESC
        """,
        )

        grouped: defaultdict[str, list[list]] = defaultdict(list)
        for ex_name, tp_name, val, date in rows:
            key = f"{ex_name} {tp_name}".strip()
            grouped[key].append([ex_name, tp_name, float(val), date])

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
        if index == 0:  # Main tab
            self.update_filter_comboboxes()

    def on_update_exercises(self) -> None:
        """Update the selected exercise row.

        Updates the name and unit of the currently selected exercise in the
        exercises table.
        """
        self._update_record_generic(
            "exercises",
            "exercises",
            "UPDATE exercises SET name = :n, unit = :u WHERE _id = :id",
            lambda r, m, _id: {
                "n": m.data(m.index(r, 0)),
                "u": m.data(m.index(r, 1)),
                "id": _id,
            },
        )

    def on_update_process(self) -> None:
        """Update the selected process row.

        Updates the exercise, type, value, and date of the currently selected
        record in the process table.
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
        date = model.data(model.index(row, 3))
        value = value_raw.split(" ")[0]  # remove unit

        if not self._is_valid_date(date):
            QMessageBox.warning(self, "Error", "Use YYYY-MM-DD date format")
            return

        ex_id = self.db_manager.get_id("exercises", "name", exercise)
        if ex_id is None:
            return
        tp_id = (
            self.db_manager.get_id(
                "types",
                "type",
                type_name,
                condition=f"_id_exercises = {ex_id}",
            )
            if type_name
            else -1
        )

        self.db_manager.execute_query(
            """
            UPDATE process
               SET _id_exercises = :ex,
                   _id_types     = :tp,
                   date          = :dt,
                   value         = :val
             WHERE _id = :id
        """,
            {
                "ex": ex_id,
                "tp": tp_id or -1,
                "dt": date,
                "val": value,
                "id": _id,
            },
        )
        self.update_all()

    def on_update_types(self) -> None:
        """Update the selected *types* row.

        Updates the exercise and type of the currently selected record in the
        types table.
        """
        self._update_record_generic(
            "types",
            "types",
            """
            UPDATE types
               SET _id_exercises = :ex,
                   type          = :tp
             WHERE _id = :id
        """,
            lambda r, m, _id: {
                "ex": self.db_manager.get_id("exercises", "name", m.data(m.index(r, 0))),
                "tp": m.data(m.index(r, 1)),
                "id": _id,
            },
        )

    def on_update_weight(self) -> None:
        """Update the selected weight entry.

        Updates the value and date of the currently selected record in the
        weight table.
        """
        self._update_record_generic(
            "weight",
            "weight",
            "UPDATE weight SET value = :v, date = :d WHERE _id = :id",
            lambda r, m, _id: {
                "v": m.data(m.index(r, 0)),
                "d": m.data(m.index(r, 1)),
                "id": _id,
            },
        )

    def set_current_date(self) -> None:
        """Set today's date in the date edit fields.

        Sets both the main date input field (QDateEdit) and the weight date input field
        (assuming it's still a QLineEdit) to today's date.
        """
        today_qdate = QDate.currentDate()
        today_str = today_qdate.toString("yyyy-MM-dd")

        # Set the QDateEdit to today's date
        self.dateEdit.setDate(today_qdate)

        # Assuming lineEdit_weight_date is still a QLineEdit
        self.lineEdit_weight_date.setText(today_str)

    def show_tables(self) -> None:
        """Populate all four `QTableView`s from the database.

        Loads data from the database into all table views:

        - Process table (exercise records)
        - Exercises table
        - Exercise types table
        - Weight table
        """
        # exercises
        rows = self.db_manager.get_rows("SELECT _id, name, unit FROM exercises")
        self.models["exercises"] = self._create_table_model(
            rows,
            self.table_config["exercises"][2],
        )
        self.tableView_exercises.setModel(self.models["exercises"])
        self.tableView_exercises.resizeColumnsToContents()

        # process
        rows = self.db_manager.get_rows(
            """
            SELECT p._id,
                   e.name,
                   IFNULL(t.type, ''),
                   p.value,
                   e.unit,
                   p.date
            FROM process p
            JOIN exercises e ON p._id_exercises = e._id
            LEFT JOIN types t
                   ON p._id_types = t._id
                  AND t._id_exercises = e._id
            ORDER BY p._id DESC
        """,
        )
        process_data = [[r[0], r[1], r[2], f"{r[3]} {r[4] or 'times'}", r[5]] for r in rows]
        self.models["process"] = self._create_table_model(
            process_data,
            self.table_config["process"][2],
        )
        self.tableView_process.setModel(self.models["process"])
        self.tableView_process.resizeColumnsToContents()

        # types
        rows = self.db_manager.get_rows(
            """
            SELECT t._id, e.name, t.type
              FROM types t
              JOIN exercises e ON t._id_exercises = e._id
        """,
        )
        self.models["types"] = self._create_table_model(
            rows,
            self.table_config["types"][2],
        )
        self.tableView_exercise_types.setModel(self.models["types"])
        self.tableView_exercise_types.resizeColumnsToContents()

        # weight
        rows = self.db_manager.get_rows(
            "SELECT _id, value, date FROM weight ORDER BY date DESC",
        )
        self.models["weight"] = self._create_table_model(
            rows,
            self.table_config["weight"][2],
        )
        self.tableView_weight.setModel(self.models["weight"])
        self.tableView_weight.resizeColumnsToContents()

    # NOTE: keyword-only boolean parameters silence FBT00{1,2}
    def update_all(
        self,
        *,
        skip_date_update: bool = False,
        preserve_selections: bool = False,
        current_exercise: str | None = None,
        current_type: str | None = None,
    ) -> None:
        """Refresh tables, combo-boxes and (optionally) dates.

        Updates all UI elements with the latest data from the database.

        Args:

        - `skip_date_update` (`bool`): If `True`, date fields won't be reset to today. Defaults to `False`.
        - `preserve_selections` (`bool`): If `True`, tries to maintain current selections. Defaults to `False`.
        - `current_exercise` (`str | None`): Exercise to keep selected. Defaults to `None`.
        - `current_type` (`str | None`): Exercise type to keep selected. Defaults to `None`.

        """
        if preserve_selections and current_exercise is None:
            current_exercise = self.comboBox_exercise.currentText()
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
            self.set_current_date()

        self.update_filter_comboboxes()

    def update_filter_comboboxes(self) -> None:
        """Refresh *exercise* and *type* combo-boxes in the filter group.

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
        """Populate *type* filter based on the *exercise* filter selection.

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
                types = self.db_manager.get_items(
                    "types",
                    "type",
                    condition=f"_id_exercises = {ex_id}",
                )
                self.comboBox_filter_type.addItems(types)

        if current_type:
            idx = self.comboBox_filter_type.findText(current_type)
            if idx >= 0:
                self.comboBox_filter_type.setCurrentIndex(idx)
```

</details>

### Method `__init__`

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

        self.db_manager: fitness_database_manager.FitnessDatabaseManager | None = None

        self.models: dict[str, QSortFilterProxyModel | None] = {
            "process": None,
            "exercises": None,
            "types": None,
            "weight": None,
        }

        self.table_config: dict[str, tuple[QTableView, str, list[str]]] = {
            "process": (
                self.tableView_process,
                "process",
                ["Exercise", "Exercise Type", "Quantity", "Date"],
            ),
            "exercises": (
                self.tableView_exercises,
                "exercises",
                ["Exercise", "Unit of Measurement"],
            ),
            "types": (
                self.tableView_exercise_types,
                "types",
                ["Exercise", "Exercise Type"],
            ),
            "weight": (self.tableView_weight, "weight", ["Weight", "Date"]),
        }

        self._init_database()
        self._connect_signals()
        self._init_filter_controls()
        self.update_all()
```

</details>

### Method `_connect_signals`

```python
def _connect_signals(self) -> None
```

Wire Qt widgets to their Python slots.

Connects all UI elements to their respective handler methods, including:

- ComboBox change events
- Button click events for adding, updating, and deleting records
- Tab change events
- Statistics and export functionality

<details>
<summary>Code:</summary>

```python
def _connect_signals(self) -> None:
        self.comboBox_exercise.currentIndexChanged.connect(
            self.on_exercise_changed,
        )
        self.pushButton_add.clicked.connect(self.on_add_record)

        for action, button_prefix in [
            ("delete", "delete"),
            ("update", "update"),
            ("refresh", "refresh"),
        ]:
            for table_name in self.table_config:
                btn_name = (
                    f"pushButton_{button_prefix}"
                    if table_name == "process"
                    else f"pushButton_{table_name}_{button_prefix}"
                )
                button = getattr(self, btn_name)
                if action == "delete":
                    button.clicked.connect(partial(self.delete_record, table_name))
                elif action == "update":
                    button.clicked.connect(getattr(self, f"on_update_{table_name}"))
                else:
                    button.clicked.connect(self.update_all)

        # Add buttons
        self.pushButton_exercise_add.clicked.connect(self.on_add_exercise)
        self.pushButton_type_add.clicked.connect(self.on_add_type)
        self.pushButton_weight_add.clicked.connect(self.on_add_weight)

        # Stats & export
        self.pushButton_statistics_refresh.clicked.connect(
            self.on_refresh_statistics,
        )
        self.pushButton_export_csv.clicked.connect(self.on_export_csv)

        # Tab change
        self.tabWidget.currentChanged.connect(self.on_tab_changed)
```

</details>

### Method `_create_table_model`

```python
def _create_table_model(self, data: list[list[str]], headers: list[str], id_column: int = 0) -> QSortFilterProxyModel
```

Return a proxy model filled with _data_.

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

### Method `_increment_date_after_add`

```python
def _increment_date_after_add(self) -> None
```

Move _date_ edit one day forward unless it already shows today.

After adding a record, this method advances the date in the date edit
by one day to make it easier to add consecutive daily entries. If the
current date is already set to today, it remains unchanged.

<details>
<summary>Code:</summary>

```python
def _increment_date_after_add(self) -> None:
        current_date = self.dateEdit.date()  # Get the current QDate from dateEdit
        today = QDate.currentDate()  # Get today's date as QDate

        # If current date is today or later, do nothing
        if current_date >= today:
            return

        # Add one day to the current date
        next_date = current_date.addDays(1)

        # Set the new date
        self.dateEdit.setDate(next_date)
```

</details>

### Method `_init_database`

```python
def _init_database(self) -> None
```

Open the SQLite file from _config_ (ask the user if missing).

Attempts to open the database file specified in the configuration.
If the file doesn't exist, prompts the user to select a database file.
If no database is selected or an error occurs, the application exits.

<details>
<summary>Code:</summary>

```python
def _init_database(self) -> None:
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
            self.db_manager = fitness_database_manager.FitnessDatabaseManager(
                str(filename),
            )
        except (OSError, RuntimeError) as exc:
            QMessageBox.critical(self, "Error", str(exc))
            sys.exit(1)
```

</details>

### Method `_init_filter_controls`

```python
def _init_filter_controls(self) -> None
```

Prepare widgets on the _Filters_ group box.

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

        self.comboBox_filter_exercise.currentIndexChanged.connect(
            self.update_filter_type_combobox,
        )
        self.pushButton_apply_filter.clicked.connect(self.apply_filter)
        self.pushButton_clear_filter.clicked.connect(self.clear_filter)
```

</details>

### Method `_is_valid_date`

```python
def _is_valid_date(date_str: str) -> bool
```

Return _True_ if `YYYY-MM-DD` formatted _date_str_ is correct.

Args:

- `date_str` (`str`): Date string to validate.

Returns:

- `bool`: True if the date is in the correct format and represents a valid date.

<details>
<summary>Code:</summary>

```python
def _is_valid_date(date_str: str) -> bool:
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date_str):
            return False

        try:
            datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            return False
        else:
            return True
```

</details>

### Method `_update_comboboxes`

```python
def _update_comboboxes(self) -> None
```

Refresh exercise/type combo-boxes (optionally keep a selection).

Updates the exercise and exercise type comboboxes with current data from the database.
Can optionally maintain the current selections.

Args:

- `selected_exercise` (`str | None`): Exercise name to select after refresh. Defaults to `None`.
- `selected_type` (`str | None`): Exercise type to select after refresh. Defaults to `None`.

<details>
<summary>Code:</summary>

```python
def _update_comboboxes(
        self,
        *,
        selected_exercise: str | None = None,
        selected_type: str | None = None,
    ) -> None:
        exercises = self.db_manager.get_exercises_by_frequency(500)

        self.comboBox_exercise.blockSignals(True)  # noqa: FBT003
        self.comboBox_exercise.clear()
        self.comboBox_exercise.addItems(exercises)
        self.comboBox_exercise.blockSignals(False)  # noqa: FBT003

        self.comboBox_exercise_name.clear()
        self.comboBox_exercise_name.addItems(exercises)

        if selected_exercise and selected_exercise in exercises:
            idx = exercises.index(selected_exercise)
            self.comboBox_exercise.setCurrentIndex(idx)

            if selected_type:
                ex_id = self.db_manager.get_id("exercises", "name", selected_exercise)
                if ex_id is not None:
                    types = self.db_manager.get_items(
                        "types",
                        "type",
                        condition=f"_id_exercises = {ex_id}",
                    )
                    self.comboBox_type.clear()
                    self.comboBox_type.addItem("")
                    self.comboBox_type.addItems(types)
                    t_idx = self.comboBox_type.findText(selected_type)
                    if t_idx >= 0:
                        self.comboBox_type.setCurrentIndex(t_idx)
        else:
            self.on_exercise_changed()
```

</details>

### Method `_update_record_generic`

```python
def _update_record_generic(self, table_name: str, model_key: str, query_text: str, params_extractor: Callable[[int, QSortFilterProxyModel, str], dict]) -> None
```

Low-level generic UPDATE handler.

Args:

- `table_name` (`str`): Name of the table being updated (for error messages).
- `model_key` (`str`): Key for accessing the model in the models dictionary.
- `query_text` (`str`): SQL update query with placeholders.
- `params_extractor` (`Callable`): Function to extract parameters from the selected row.

<details>
<summary>Code:</summary>

```python
def _update_record_generic(
        self,
        table_name: str,
        model_key: str,
        query_text: str,
        params_extractor: Callable[
            [int, QSortFilterProxyModel, str],
            dict,
        ],
    ) -> None:
        table_view = next(tv for tv, mkey, _ in self.table_config.values() if mkey == model_key)
        index = table_view.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "Error", "Select a record to update")
            return

        model = self.models[model_key]
        row = index.row()
        _id = model.sourceModel().verticalHeaderItem(row).text()
        params = params_extractor(row, model, _id)

        if self.db_manager.execute_query(query_text, params):
            self.update_all()
        else:
            QMessageBox.warning(self, "Error", f"Failed to update {table_name}")
```

</details>

### Method `add_record_generic`

```python
def add_record_generic(self, table_name: str, query_text: str, params: dict) -> bool
```

Add a single row to _any_ table.

Args:

- `table_name` (`str`): Target table (must be one of `self._SAFE_TABLES`).
- `query_text` (`str`): SQL _INSERT_ statement with named placeholders.
- `params` (`dict`): Mapping for the placeholders.

Returns:

- `bool`: _True_ if the row was written successfully.

Raises:

- `ValueError`: If table_name is not in \_SAFE_TABLES.

<details>
<summary>Code:</summary>

```python
def add_record_generic(
        self,
        table_name: str,
        query_text: str,
        params: dict,
    ) -> bool:
        if table_name not in self._SAFE_TABLES:
            error_message = f"Illegal table name: {table_name}"
            raise ValueError(error_message)

        result = self.db_manager.execute_query(query_text, params)
        if result:
            self.update_all()
            return True

        QMessageBox.warning(self, "Error", f"Failed to add to {table_name}")
        return False
```

</details>

### Method `apply_filter`

```python
def apply_filter(self) -> None
```

Apply combo-box/date filters to the _process_ table.

Applies the currently selected filters to the process table:

- Exercise filter
- Exercise type filter
- Date range filter (if enabled)

Updates the process table view with the filtered results.

<details>
<summary>Code:</summary>

```python
def apply_filter(self) -> None:
        exercise = self.comboBox_filter_exercise.currentText()
        exercise_type = self.comboBox_filter_type.currentText()
        use_date_filter = self.checkBox_use_date_filter.isChecked()
        date_from = self.dateEdit_filter_from.date().toString("yyyy-MM-dd") if use_date_filter else ""
        date_to = self.dateEdit_filter_to.date().toString("yyyy-MM-dd") if use_date_filter else ""

        conditions: list[str] = []
        params: dict[str, str] = {}

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

        query_text = """
            SELECT p._id,
                   e.name,
                   IFNULL(t.type, ''),
                   p.value,
                   e.unit,
                   p.date
            FROM process p
            JOIN exercises e ON p._id_exercises = e._id
            LEFT JOIN types t
                 ON p._id_types = t._id
                AND t._id_exercises = e._id
        """

        if conditions:
            query_text += " WHERE " + " AND ".join(conditions)

        query_text += " ORDER BY p._id DESC"

        rows = self.db_manager.get_rows(query_text, params)
        data = [[row[0], row[1], row[2], f"{row[3]} {row[4] or 'times'}", row[5]] for row in rows]
        self.models["process"] = self._create_table_model(
            data,
            self.table_config["process"][2],
        )
        self.tableView_process.setModel(self.models["process"])
        self.tableView_process.resizeColumnsToContents()
```

</details>

### Method `clear_filter`

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

### Method `delete_record`

```python
def delete_record(self, table_name: str) -> None
```

Delete selected row from _table_name_ (must be safe).

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

        table_view, model_key, _ = self.table_config[table_name]
        model = self.models[model_key]
        if model is None:
            return

        index = table_view.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "Error", "Select a record to delete")
            return

        row = index.row()
        _id = model.sourceModel().verticalHeaderItem(row).text()

        # Explicitly use a constant query and bind the identifier
        query = f"DELETE FROM {table_name} WHERE _id = :id"
        if self.db_manager.execute_query(query, {"id": _id}):
            self.update_all()
        else:
            QMessageBox.warning(self, "Error", f"Deletion failed in {table_name}")
```

</details>

### Method `on_add_exercise`

```python
def on_add_exercise(self) -> None
```

Insert a new exercise.

Adds a new exercise to the database using the name and unit values
from the input fields. Shows an error message if the exercise name is empty.

<details>
<summary>Code:</summary>

```python
def on_add_exercise(self) -> None:
        exercise = self.lineEdit_exercise_name.text().strip()
        unit = self.lineEdit_exercise_unit.text().strip()

        if not exercise:
            QMessageBox.warning(self, "Error", "Enter exercise name")
            return

        self.add_record_generic(
            "exercises",
            "INSERT INTO exercises (name, unit) VALUES (:name, :unit)",
            {"name": exercise, "unit": unit},
        )
```

</details>

### Method `on_add_record`

```python
def on_add_record(self) -> None
```

Insert a new _process_ row.

Adds a new exercise record to the process table using the currently selected
exercise, type, count, and date values. Automatically advances the date
after successful addition.

<details>
<summary>Code:</summary>

```python
def on_add_record(self) -> None:
        exercise = self.comboBox_exercise.currentText()
        ex_id = self.db_manager.get_id("exercises", "name", exercise)
        if ex_id is None:
            return

        type_name = self.comboBox_type.currentText()
        type_id = (
            self.db_manager.get_id(
                "types",
                "type",
                type_name,
                condition=f"_id_exercises = {ex_id}",
            )
            if type_name
            else -1
        )

        # Store current date before adding record
        current_date = self.dateEdit.date()

        params = {
            "exercise_id": ex_id,
            "type_id": type_id or -1,
            "value": str(self.spinBox_count.value()),
            "date": current_date.toString("yyyy-MM-dd"),
        }

        # Execute the query directly instead of using add_record_generic
        # to avoid triggering update_all() which resets the date
        query_text = (
            "INSERT INTO process (_id_exercises, _id_types, value, date) VALUES (:exercise_id, :type_id, :value, :date)"
        )

        result = self.db_manager.execute_query(query_text, params)
        if result:
            # Apply date increment logic
            self._increment_date_after_add()

            # Update UI without resetting the date
            self.show_tables()
            self._update_comboboxes(
                selected_exercise=exercise,
                selected_type=type_name,
            )
            self.update_filter_comboboxes()
        else:
            QMessageBox.warning(self, "Error", "Failed to add to process")
```

</details>

### Method `on_add_type`

```python
def on_add_type(self) -> None
```

Insert a new exercise _type_ for the selected exercise.

Adds a new exercise type for the selected exercise. Shows an error
message if the type name is empty.

<details>
<summary>Code:</summary>

```python
def on_add_type(self) -> None:
        exercise = self.comboBox_exercise_name.currentText()
        ex_id = self.db_manager.get_id("exercises", "name", exercise)
        if ex_id is None:
            return

        type_name = self.lineEdit_exercise_type.text().strip()
        if not type_name:
            QMessageBox.warning(self, "Error", "Enter type name")
            return

        self.add_record_generic(
            "types",
            "INSERT INTO types (_id_exercises, type) VALUES (:ex, :tp)",
            {"ex": ex_id, "tp": type_name},
        )
```

</details>

### Method `on_add_weight`

```python
def on_add_weight(self) -> None
```

Insert a new weight measurement.

Adds a new weight record to the database using the current weight value
and date from the input fields.

<details>
<summary>Code:</summary>

```python
def on_add_weight(self) -> None:
        self.add_record_generic(
            "weight",
            "INSERT INTO weight (value, date) VALUES (:val, :dt)",
            {
                "val": str(self.doubleSpinBox_weight.value()),
                "dt": self.lineEdit_weight_date.text(),
            },
        )
```

</details>

### Method `on_exercise_changed`

```python
def on_exercise_changed(self) -> None
```

Load exercise types for the newly selected exercise in _comboBox_type_.

Updates the exercise type combo box with the types associated with the
currently selected exercise.

<details>
<summary>Code:</summary>

```python
def on_exercise_changed(self) -> None:
        exercise = self.comboBox_exercise.currentText()
        ex_id = self.db_manager.get_id("exercises", "name", exercise)
        if ex_id is None:
            return
        types = self.db_manager.get_items(
            "types",
            "type",
            condition=f"_id_exercises = {ex_id}",
        )
        self.comboBox_type.clear()
        self.comboBox_type.addItem("")
        self.comboBox_type.addItems(types)
```

</details>

### Method `on_export_csv`

```python
def on_export_csv(self) -> None
```

Save current _process_ view to a CSV file (semicolon-separated).

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

        filename = Path(filename_str)
        model = self.models["process"].sourceModel()  # type: ignore[call-arg]
        with filename.open("w", encoding="utf-8") as file:
            headers = [model.headerData(col, Qt.Horizontal, Qt.DisplayRole) or "" for col in range(model.columnCount())]
            file.write(";".join(headers) + "\n")

            for row in range(model.rowCount()):
                row_values = [f'"{model.data(model.index(row, col)) or ""}"' for col in range(model.columnCount())]
                file.write(";".join(row_values) + "\n")
```

</details>

### Method `on_refresh_statistics`

```python
def on_refresh_statistics(self) -> None
```

Populate the statistics text-edit with the four best results per key.

Retrieves exercise data from the database and displays the top four
results for each exercise/type combination in the statistics text edit.
Highlights today's entries.

<details>
<summary>Code:</summary>

```python
def on_refresh_statistics(self) -> None:
        self.textEdit_statistics.clear()

        rows = self.db_manager.get_rows(
            """
            SELECT e.name,
                   IFNULL(t.type, ''),
                   p.value,
                   p.date
            FROM process p
            JOIN exercises e ON p._id_exercises = e._id
            LEFT JOIN types t ON p._id_types = t._id
            ORDER BY p._id DESC
        """,
        )

        grouped: defaultdict[str, list[list]] = defaultdict(list)
        for ex_name, tp_name, val, date in rows:
            key = f"{ex_name} {tp_name}".strip()
            grouped[key].append([ex_name, tp_name, float(val), date])

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
```

</details>

### Method `on_tab_changed`

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
        if index == 0:  # Main tab
            self.update_filter_comboboxes()
```

</details>

### Method `on_update_exercises`

```python
def on_update_exercises(self) -> None
```

Update the selected exercise row.

Updates the name and unit of the currently selected exercise in the
exercises table.

<details>
<summary>Code:</summary>

```python
def on_update_exercises(self) -> None:
        self._update_record_generic(
            "exercises",
            "exercises",
            "UPDATE exercises SET name = :n, unit = :u WHERE _id = :id",
            lambda r, m, _id: {
                "n": m.data(m.index(r, 0)),
                "u": m.data(m.index(r, 1)),
                "id": _id,
            },
        )
```

</details>

### Method `on_update_process`

```python
def on_update_process(self) -> None
```

Update the selected process row.

Updates the exercise, type, value, and date of the currently selected
record in the process table.

<details>
<summary>Code:</summary>

```python
def on_update_process(self) -> None:
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
        date = model.data(model.index(row, 3))
        value = value_raw.split(" ")[0]  # remove unit

        if not self._is_valid_date(date):
            QMessageBox.warning(self, "Error", "Use YYYY-MM-DD date format")
            return

        ex_id = self.db_manager.get_id("exercises", "name", exercise)
        if ex_id is None:
            return
        tp_id = (
            self.db_manager.get_id(
                "types",
                "type",
                type_name,
                condition=f"_id_exercises = {ex_id}",
            )
            if type_name
            else -1
        )

        self.db_manager.execute_query(
            """
            UPDATE process
               SET _id_exercises = :ex,
                   _id_types     = :tp,
                   date          = :dt,
                   value         = :val
             WHERE _id = :id
        """,
            {
                "ex": ex_id,
                "tp": tp_id or -1,
                "dt": date,
                "val": value,
                "id": _id,
            },
        )
        self.update_all()
```

</details>

### Method `on_update_types`

```python
def on_update_types(self) -> None
```

Update the selected _types_ row.

Updates the exercise and type of the currently selected record in the
types table.

<details>
<summary>Code:</summary>

```python
def on_update_types(self) -> None:
        self._update_record_generic(
            "types",
            "types",
            """
            UPDATE types
               SET _id_exercises = :ex,
                   type          = :tp
             WHERE _id = :id
        """,
            lambda r, m, _id: {
                "ex": self.db_manager.get_id("exercises", "name", m.data(m.index(r, 0))),
                "tp": m.data(m.index(r, 1)),
                "id": _id,
            },
        )
```

</details>

### Method `on_update_weight`

```python
def on_update_weight(self) -> None
```

Update the selected weight entry.

Updates the value and date of the currently selected record in the
weight table.

<details>
<summary>Code:</summary>

```python
def on_update_weight(self) -> None:
        self._update_record_generic(
            "weight",
            "weight",
            "UPDATE weight SET value = :v, date = :d WHERE _id = :id",
            lambda r, m, _id: {
                "v": m.data(m.index(r, 0)),
                "d": m.data(m.index(r, 1)),
                "id": _id,
            },
        )
```

</details>

### Method `set_current_date`

```python
def set_current_date(self) -> None
```

Set today's date in the date edit fields.

Sets both the main date input field (QDateEdit) and the weight date input field
(assuming it's still a QLineEdit) to today's date.

<details>
<summary>Code:</summary>

```python
def set_current_date(self) -> None:
        today_qdate = QDate.currentDate()
        today_str = today_qdate.toString("yyyy-MM-dd")

        # Set the QDateEdit to today's date
        self.dateEdit.setDate(today_qdate)

        # Assuming lineEdit_weight_date is still a QLineEdit
        self.lineEdit_weight_date.setText(today_str)
```

</details>

### Method `show_tables`

```python
def show_tables(self) -> None
```

Populate all four `QTableView`s from the database.

Loads data from the database into all table views:

- Process table (exercise records)
- Exercises table
- Exercise types table
- Weight table

<details>
<summary>Code:</summary>

```python
def show_tables(self) -> None:
        # exercises
        rows = self.db_manager.get_rows("SELECT _id, name, unit FROM exercises")
        self.models["exercises"] = self._create_table_model(
            rows,
            self.table_config["exercises"][2],
        )
        self.tableView_exercises.setModel(self.models["exercises"])
        self.tableView_exercises.resizeColumnsToContents()

        # process
        rows = self.db_manager.get_rows(
            """
            SELECT p._id,
                   e.name,
                   IFNULL(t.type, ''),
                   p.value,
                   e.unit,
                   p.date
            FROM process p
            JOIN exercises e ON p._id_exercises = e._id
            LEFT JOIN types t
                   ON p._id_types = t._id
                  AND t._id_exercises = e._id
            ORDER BY p._id DESC
        """,
        )
        process_data = [[r[0], r[1], r[2], f"{r[3]} {r[4] or 'times'}", r[5]] for r in rows]
        self.models["process"] = self._create_table_model(
            process_data,
            self.table_config["process"][2],
        )
        self.tableView_process.setModel(self.models["process"])
        self.tableView_process.resizeColumnsToContents()

        # types
        rows = self.db_manager.get_rows(
            """
            SELECT t._id, e.name, t.type
              FROM types t
              JOIN exercises e ON t._id_exercises = e._id
        """,
        )
        self.models["types"] = self._create_table_model(
            rows,
            self.table_config["types"][2],
        )
        self.tableView_exercise_types.setModel(self.models["types"])
        self.tableView_exercise_types.resizeColumnsToContents()

        # weight
        rows = self.db_manager.get_rows(
            "SELECT _id, value, date FROM weight ORDER BY date DESC",
        )
        self.models["weight"] = self._create_table_model(
            rows,
            self.table_config["weight"][2],
        )
        self.tableView_weight.setModel(self.models["weight"])
        self.tableView_weight.resizeColumnsToContents()
```

</details>

### Method `update_all`

```python
def update_all(self) -> None
```

Refresh tables, combo-boxes and (optionally) dates.

Updates all UI elements with the latest data from the database.

Args:

- `skip_date_update` (`bool`): If `True`, date fields won't be reset to today. Defaults to `False`.
- `preserve_selections` (`bool`): If `True`, tries to maintain current selections. Defaults to `False`.
- `current_exercise` (`str | None`): Exercise to keep selected. Defaults to `None`.
- `current_type` (`str | None`): Exercise type to keep selected. Defaults to `None`.

<details>
<summary>Code:</summary>

```python
def update_all(
        self,
        *,
        skip_date_update: bool = False,
        preserve_selections: bool = False,
        current_exercise: str | None = None,
        current_type: str | None = None,
    ) -> None:
        if preserve_selections and current_exercise is None:
            current_exercise = self.comboBox_exercise.currentText()
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
            self.set_current_date()

        self.update_filter_comboboxes()
```

</details>

### Method `update_filter_comboboxes`

```python
def update_filter_comboboxes(self) -> None
```

Refresh _exercise_ and _type_ combo-boxes in the filter group.

Updates the exercise and type comboboxes in the filter section with
the latest data from the database, attempting to preserve the current
selections.

<details>
<summary>Code:</summary>

```python
def update_filter_comboboxes(self) -> None:
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
```

</details>

### Method `update_filter_type_combobox`

```python
def update_filter_type_combobox(self) -> None
```

Populate _type_ filter based on the _exercise_ filter selection.

Updates the exercise type combobox in the filter section based on the
currently selected exercise, attempting to preserve the current type
selection if possible.

<details>
<summary>Code:</summary>

```python
def update_filter_type_combobox(self) -> None:
        current_type = self.comboBox_filter_type.currentText()
        self.comboBox_filter_type.clear()
        self.comboBox_filter_type.addItem("")

        exercise = self.comboBox_filter_exercise.currentText()
        if exercise:
            ex_id = self.db_manager.get_id("exercises", "name", exercise)
            if ex_id is not None:
                types = self.db_manager.get_items(
                    "types",
                    "type",
                    condition=f"_id_exercises = {ex_id}",
                )
                self.comboBox_filter_type.addItems(types)

        if current_type:
            idx = self.comboBox_filter_type.findText(current_type)
            if idx >= 0:
                self.comboBox_filter_type.setCurrentIndex(idx)
```

</details>
