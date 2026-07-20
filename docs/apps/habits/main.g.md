---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `main.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `MainWindow`](#️-class-mainwindow)
  - [⚙️ Method `__init__`](#️-method-__init__)
  - [⚙️ Method `closeEvent`](#️-method-closeevent)
  - [⚙️ Method `delete_record`](#️-method-delete_record)
  - [⚙️ Method `keyPressEvent`](#️-method-keypressevent)
  - [⚙️ Method `load_process_habits_table`](#️-method-load_process_habits_table)
  - [⚙️ Method `on_add_habit`](#️-method-on_add_habit)
  - [⚙️ Method `on_export_habits_csv`](#️-method-on_export_habits_csv)
  - [⚙️ Method `on_habit_filter_clicked`](#️-method-on_habit_filter_clicked)
  - [⚙️ Method `on_habit_filter_selection_changed`](#️-method-on_habit_filter_selection_changed)
  - [⚙️ Method `on_habit_filter_selection_changed_slot`](#️-method-on_habit_filter_selection_changed_slot)
  - [⚙️ Method `on_habit_selection_changed`](#️-method-on_habit_selection_changed)
  - [⚙️ Method `on_habit_year_changed`](#️-method-on_habit_year_changed)
  - [⚙️ Method `on_habit_year_selection_changed`](#️-method-on_habit_year_selection_changed)
  - [⚙️ Method `on_toggle_show_all_habits_records`](#️-method-on_toggle_show_all_habits_records)
  - [⚙️ Method `refresh_habits_and_process_habits`](#️-method-refresh_habits_and_process_habits)
  - [⚙️ Method `refresh_process_habits_table`](#️-method-refresh_process_habits_table)
  - [⚙️ Method `resizeEvent`](#️-method-resizeevent)
  - [⚙️ Method `show_tables`](#️-method-show_tables)
  - [⚙️ Method `update_all`](#️-method-update_all)
  - [⚙️ Method `update_habit_calendar_heatmap`](#️-method-update_habit_calendar_heatmap)
  - [⚙️ Method `update_habits_filter_combobox`](#️-method-update_habits_filter_combobox)
  - [⚙️ Method `update_habits_year_combobox`](#️-method-update_habits_year_combobox)

</details>

## 🏛️ Class `MainWindow`

```python
class MainWindow(QMainWindow, window.Ui_MainWindow, AppWindowMixin, TableOperations, ChartOperations, DateOperations, AutoSaveOperations, ValidationOperations)
```

Main application window for the habits tracking application.

This class implements the main GUI window for the habit tracker, providing
functionality to record habits and track progress. It manages database
operations for storing and retrieving habits data.

Attributes:

- `_SAFE_TABLES` (`frozenset[str]`): Set of table names that can be safely modified,
  containing `habits` and `process_habits`.
- `db_manager` (`database_manager.DatabaseManager | None`): Database
  connection manager. Defaults to `None` until initialized.
- `models` (`dict[str, QSortFilterProxyModel | None]`): Dictionary of table models keyed
  by table name. All values default to `None` until tables are loaded.
- `table_config` (`dict[str, tuple[QTableView, str, list[str]]]`): Configuration for each
  table, mapping table names to tuples of (table view widget, model key, column headers).

<details>
<summary>Code:</summary>

```python
class MainWindow(
    QMainWindow,
    window.Ui_MainWindow,
    AppWindowMixin,
    TableOperations,
    ChartOperations,
    DateOperations,
    AutoSaveOperations,
    ValidationOperations,
):

    _SAFE_TABLES: frozenset[str] = frozenset(
        {"habits", "process_habits"},
    )

    def __init__(self, *, hide_on_close: bool = False) -> None:  # noqa: D107  (inherited from Qt widgets)
        super().__init__()
        try_apply_system_backdrop(self, backdrop=SystemBackdrop.MICA)
        self.setupUi(self)
        self._setup_ui()

        # Set window icon
        self.setWindowIcon(QIcon(":/assets/logo.svg"))

        self._hide_on_close = hide_on_close
        if not hide_on_close:
            self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        # Initialize core attributes
        self._is_closing = False
        self._habits_heatmap_label: QLabel | None = None
        self.db_manager: database_manager.DatabaseManager | None = None
        self._app_config: dict[str, Any] = h.dev.config_load(get_config_path_str())
        self._is_small_window_layout: bool | None = None  # Used by _update_layout_for_window_size

        # Habits filter list model
        self.habits_filter_list_model: QStandardItemModel | None = None
        # Habits year list model
        self.habits_year_list_model: QStandardItemModel | None = None

        # Table models dictionary
        self.models: dict[str, QSortFilterProxyModel | None] = {
            "habits": None,
            "process_habits": None,
        }

        # Process habits table display mode flag
        self.count_records_to_show = 5000
        self.show_all_records = False
        # Habits list view filter flag
        self.show_archived_habits = False
        # Boolean habit column indexes in process_habits pivot (1-based habit columns)
        self._process_habits_bool_columns: set[int] = set()
        self._process_habits_int_columns: set[int] = set()
        self._process_habit_bool_delegate: ProcessHabitBoolDelegate | None = None
        self._process_habit_int_delegate: ProcessHabitIntDelegate | None = None

        # Define colors for different dates (used in process_habits table)
        self.exercise_colors = generate_pastel_qcolors(50)

        # Chart configuration (for heatmap / ChartOperations mixin)
        self.max_count_points_in_charts = 40

        # Table configuration mapping
        self.table_config: dict[str, tuple[QTableView, str, list[str]]] = {
            "habits": (self.tableView_habits, "habits", ["Habit", "Is Boolean", "Is Archived"]),
            "process_habits": (
                self.tableView_process_habits,
                "process_habits",
                [],  # Headers are now dynamic (Date + all habits)
            ),
        }

        # Initialize application
        self._init_database()
        self._connect_signals()
        self._init_habits_table_delegates()
        self._init_habits_filter_list()
        self._init_habits_year_list()
        self.update_all()

        # Set window size and position based on screen resolution
        self._setup_window_size_and_position()

        # Adjust table column widths and show window after UI is fully initialized
        QTimer.singleShot(200, self._finish_window_initialization)

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        """Handle application close event.

        Args:

        - `event` (`QCloseEvent`): The close event.

        """
        if self._hide_on_close:
            self._is_closing = True
            refresh_timer = getattr(self, "_habits_refresh_timer", None)
            if refresh_timer is not None:
                refresh_timer.stop()
            event.ignore()
            self.hide()
            self._is_closing = False
            return

        self._shutdown_window_resources()
        super().closeEvent(event)

    @requires_database()
    def delete_record(self, table_name: str) -> None:
        """Delete selected row from table using database manager methods.

        Args:

        - `table_name` (`str`): Name of the table to delete from. Must be in `_SAFE_TABLES`.

        Raises:

        - `ValueError`: If table_name is not in `_SAFE_TABLES`.

        """
        if table_name not in self._SAFE_TABLES:
            error_message = f"Illegal table name: {table_name}"
            raise ValueError(error_message)

        record_id = self._get_selected_row_id(table_name)
        if record_id is None:
            message_box.warning(self, "Error", "Select a record to delete")
            return

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        success = False
        try:
            if table_name == "habits":
                success = self.db_manager.delete_habit(record_id)
            elif table_name == "process_habits":
                success = self.db_manager.delete_process_habit_record(record_id)
        except Exception as e:
            message_box.warning(self, "Database Error", f"Failed to delete record: {e}")
            return

        if success:
            self.update_all()
        else:
            message_box.warning(self, "Error", f"Deletion failed in {table_name}")

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        """Handle key press events for the main window.

        Args:

        - `event` (`QKeyEvent`): The key press event.

        """
        # Handle Enter key when habit Add button is focused
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            focused_widget = QApplication.focusWidget()
            if focused_widget == self.pushButton_habit_add_new:
                self.pushButton_habit_add_new.click()
                return

        if self._handle_ctrl_c_for_tables(
            event,
            [
                self.tableView_habits,
                self.tableView_process_habits,
            ],
        ):
            return

        super().keyPressEvent(event)

    @requires_database()
    def load_process_habits_table(self, *, ignore_filter: bool = False) -> None:
        """Load process habits table as pivot table (dates as rows, habits as columns).

        Args:

        - `ignore_filter` (`bool`): If `True`, ignore habit filter and load all records. Defaults to `False`.

        """
        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        min_habit_row_columns = 2
        min_process_habit_row_columns = 4

        # Get habits (columns), optionally including archived ones
        habits_data = self.db_manager.get_habits(include_archived=self.show_archived_habits)
        habits = []  # List of (habit_id, habit_name, is_bool) tuples
        habit_id_to_index = {}  # Map habit_id to column index
        is_bool_column_index = 2

        for idx, row in enumerate(habits_data):
            if len(row) >= min_habit_row_columns:
                habit_id = row[0]
                habit_name = row[1] or ""
                is_bool = len(row) > is_bool_column_index and row[is_bool_column_index] == 1
                habits.append((habit_id, habit_name, is_bool))
                habit_id_to_index[habit_id] = idx

        # Apply filters if set (unless ignore_filter is True)
        if ignore_filter:
            habit_filter = ""
            use_date_filter = False
            date_from = None
            date_to = None
        else:
            try:
                habit_filter = self._get_selected_habit_filter()
                use_date_filter = False  # Date filter checkbox removed
                date_from = None
                date_to = None
            except AttributeError:
                # Filters not available yet
                habit_filter = ""
                use_date_filter = False
                date_from = None
                date_to = None

        # Always load all process habits records to show all columns
        # Filter will be applied to rows (dates) only, not to columns
        if use_date_filter:
            # Only apply date filter if explicitly set
            process_habits_rows = self.db_manager.get_filtered_process_habits_records(
                habit_name=None,  # Don't filter by habit - show all columns
                date_from=date_from,
                date_to=date_to,
            )
        elif self.show_all_records:
            process_habits_rows = self.db_manager.get_all_process_habits_records()
        else:
            process_habits_rows = self.db_manager.get_limited_process_habits_records(self.count_records_to_show)

        min_process_habits_name_columns = 2

        # When archived habits are hidden, also drop rows related to archived habits
        if not self.show_archived_habits:
            allowed_names = {name for _id, name, _is_bool in habits}
            process_habits_rows = [
                r for r in process_habits_rows if len(r) >= min_process_habits_name_columns and r[1] in allowed_names
            ]

        # Create a dictionary: date -> {habit_id: (record_id, value)}
        date_data = {}  # date -> {habit_id: (record_id, value)}
        unique_dates = set()
        filtered_dates = set()  # Dates that match the habit filter (if any)

        for row in process_habits_rows:
            if len(row) < min_process_habit_row_columns:
                continue
            record_id = row[0]
            habit_name = row[1]
            value = row[2]
            date_str = row[3]

            # Find habit_id by name
            habit_id = None
            for h_id, h_name, _is_bool in habits:
                if h_name == habit_name:
                    habit_id = h_id
                    break

            if habit_id is None:
                continue

            unique_dates.add(date_str)
            if date_str not in date_data:
                date_data[date_str] = {}
            date_data[date_str][habit_id] = (record_id, value)

            # If habit filter is set, track dates that have data for the filtered habit
            if habit_filter and habit_name == habit_filter:
                filtered_dates.add(date_str)

        # Apply habit filter to dates (rows) only - show all columns but filter rows
        if habit_filter and filtered_dates:
            # Only show dates that have data for the filtered habit
            sorted_dates = sorted(filtered_dates, reverse=True)
        else:
            # Show all dates
            sorted_dates = sorted(unique_dates, reverse=True)

        # Add empty rows for dates between last record and today (if no date filter is applied and no habit filter)
        # When habit filter is applied, we only show dates with data for that habit, so don't add empty dates
        if not use_date_filter and not habit_filter and sorted_dates:
            # Get the most recent date (first in sorted_dates as it's sorted descending)
            last_date_str = sorted_dates[0]
            try:
                last_date = QDate.fromString(last_date_str, "yyyy-MM-dd")
                today = QDate.currentDate()

                # Add dates from last_date + 1 day to today (inclusive)
                if last_date < today:
                    current_date = last_date.addDays(1)
                    missing_dates = []
                    while current_date <= today:
                        date_str = current_date.toString("yyyy-MM-dd")
                        if date_str not in unique_dates:
                            missing_dates.append(date_str)
                        current_date = current_date.addDays(1)

                    # Add missing dates to sorted_dates (maintain descending order)
                    if missing_dates:
                        # Sort missing dates descending and prepend to sorted_dates
                        missing_dates.sort(reverse=True)
                        sorted_dates = missing_dates + sorted_dates
            except Exception as e:
                print(f"Error adding missing dates: {e}")

        # Assign colors to dates
        date_to_color = {}
        for idx, date_str in enumerate(sorted_dates):
            color_index = idx % len(self.exercise_colors)
            date_to_color[date_str] = self.exercise_colors[color_index]

        # Create headers: Date + all habit names
        headers = ["Date"] + [h_name for _, h_name, _is_bool in habits]

        # Create model
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(headers)

        # Fill model with data
        for row_idx, date_str in enumerate(sorted_dates):
            row_color = date_to_color.get(date_str, QColor(255, 255, 255))

            # Date column (not editable)
            date_item = QStandardItem(date_str)
            date_item.setBackground(QBrush(row_color))
            date_item.setEditable(False)
            model.setItem(row_idx, 0, date_item)

            # Habit columns
            for col_idx, (habit_id, _habit_name, is_bool_habit) in enumerate(habits, start=1):
                record_id, value = date_data.get(date_str, {}).get(habit_id, (None, None))

                # Create item with value or empty
                item = QStandardItem(str(value)) if value is not None else QStandardItem("")

                item.setBackground(QBrush(row_color))
                item.setEditable(not is_bool_habit)

                # Store record_id and habit_id in UserRole for auto-save
                # Format: (record_id, habit_id, date_str) or None if no record exists
                if record_id is not None:
                    item.setData((record_id, habit_id, date_str), Qt.ItemDataRole.UserRole)
                else:
                    item.setData((None, habit_id, date_str), Qt.ItemDataRole.UserRole)

                model.setItem(row_idx, col_idx, item)

        # Create proxy model for sorting/filtering
        proxy = QSortFilterProxyModel()
        proxy.setSourceModel(model)

        self.models["process_habits"] = proxy
        self.tableView_process_habits.setModel(proxy)
        # Reconnect auto-save signal after model is created
        self._connect_table_auto_save_signal("process_habits")

        # Recreate per-column delegates each load (detach old viewport hooks first)
        self._cleanup_process_habit_delegates()
        self._process_habit_bool_delegate = ProcessHabitBoolDelegate(self.tableView_process_habits)
        self._process_habit_int_delegate = ProcessHabitIntDelegate(self.tableView_process_habits)
        self._process_habits_bool_columns = set()
        self._process_habits_int_columns = set()
        for col_idx, (_habit_id, _habit_name, is_bool_habit) in enumerate(habits, start=1):
            if is_bool_habit:
                self._process_habits_bool_columns.add(col_idx)
                self.tableView_process_habits.setItemDelegateForColumn(col_idx, self._process_habit_bool_delegate)
            else:
                self._process_habits_int_columns.add(col_idx)
                self.tableView_process_habits.setItemDelegateForColumn(col_idx, self._process_habit_int_delegate)

        # Make table editable
        self.tableView_process_habits.setEditTriggers(
            QAbstractItemView.EditTrigger.DoubleClicked | QAbstractItemView.EditTrigger.SelectedClicked
        )

        # Configure header (habit value columns need room for hover picker UI)
        _min_habit_value_column_width = 86
        process_habits_header = self.tableView_process_habits.horizontalHeader()
        process_habits_header.setMinimumSectionSize(_min_habit_value_column_width)
        for i in range(process_habits_header.count()):
            process_habits_header.setSectionResizeMode(i, process_habits_header.ResizeMode.Interactive)
        self.tableView_process_habits.resizeColumnsToContents()
        for col_idx in self._process_habits_bool_columns | self._process_habits_int_columns:
            if process_habits_header.sectionSize(col_idx) < _min_habit_value_column_width:
                process_habits_header.resizeSection(col_idx, _min_habit_value_column_width)

    @requires_database()
    @requires_database()
    @requires_database()
    def on_add_habit(self) -> None:
        """Insert a new habit using database manager."""
        habit_name = self.lineEdit_habit_name.text().strip()
        is_bool = self.checkBox_habit_is_bool.isChecked() or None

        if not habit_name:
            message_box.warning(self, "Error", "Enter habit name")
            return

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            if self.db_manager.add_habit(habit_name, is_bool=is_bool):
                self.update_all()
                self.lineEdit_habit_name.clear()
                self.checkBox_habit_is_bool.setChecked(False)
            else:
                message_box.warning(self, "Error", "Failed to add habit")
        except Exception as e:
            message_box.warning(self, "Database Error", f"Failed to add habit: {e}")

    @requires_database()
    @requires_database()
    @requires_database()
    @requires_database()
    @requires_database()
    @requires_database()
    @requires_database()
    @requires_database()
    def on_export_habits_csv(self) -> None:
        """Export process habits table to CSV file."""
        if self.models.get("process_habits") is None:
            message_box.warning(self, "Error", "No data to export")
            return

        filename, _ = QFileDialog.getSaveFileName(self, "Export Habits to CSV", "", "CSV Files (*.csv);;All Files (*)")
        if not filename:
            return

        try:
            model = cast("QSortFilterProxyModel", self.models["process_habits"])
            with Path(filename).open("w", encoding="utf-8") as f:
                # Write headers
                headers = self.table_config["process_habits"][2]
                f.write(",".join(headers) + "\n")

                # Write data
                for row in range(model.rowCount()):
                    row_data = []
                    for col in range(model.columnCount()):
                        index = model.index(row, col)
                        value = model.data(index)
                        row_data.append(str(value) if value is not None else "")
                    f.write(",".join(row_data) + "\n")

            message_box.information(self, "Success", f"Exported to {filename}")
        except Exception as e:
            message_box.warning(self, "Error", f"Failed to export: {e}")

    def on_habit_filter_clicked(self, index: QModelIndex) -> None:
        """Handle habit filter list view click or activation.

        Args:

        - `index` (`QModelIndex`): Clicked/activated index.

        """
        if index.isValid() and self.habits_filter_list_model:
            item = self.habits_filter_list_model.itemFromIndex(index)
            habit_name = (item.data(Qt.ItemDataRole.UserRole) if item is not None else None) or (
                self.habits_filter_list_model.data(index) or ""
            )
            if habit_name and habit_name.strip():
                # Get selected year from list view
                selected_text = self._get_selected_habit_year()
                year = None
                if selected_text != "Last 365 days":
                    try:
                        year = int(selected_text)
                    except ValueError:
                        year = None
                # Apply filter to process_habits table
                self.load_process_habits_table(ignore_filter=False)
                # Directly update heatmap - this is the most reliable way
                self.update_habit_calendar_heatmap(habit_name, year=year)

    def on_habit_filter_selection_changed(self, current: QModelIndex, _previous: QModelIndex) -> None:
        """Handle habit filter list view selection change.

        Args:

        - `current` (`QModelIndex`): Current selected index.
        - `_previous` (`QModelIndex`): Previous selected index.

        """
        if current.isValid() and self.habits_filter_list_model:
            item = self.habits_filter_list_model.itemFromIndex(current)
            habit_name = (item.data(Qt.ItemDataRole.UserRole) if item is not None else None) or (
                self.habits_filter_list_model.data(current) or ""
            )
            if habit_name and habit_name.strip():
                # Get selected year from list view
                selected_text = self._get_selected_habit_year()
                year = None
                if selected_text != "Last 365 days":
                    try:
                        year = int(selected_text)
                    except ValueError:
                        year = None
                # Apply filter to process_habits table
                self.load_process_habits_table(ignore_filter=False)
                # Update heatmap with selected habit
                self.update_habit_calendar_heatmap(habit_name, year=year)

    def on_habit_filter_selection_changed_slot(self, selected: QItemSelection, _deselected: QItemSelection) -> None:
        """Handle habit filter list view selection changed signal.

        Args:

        - `selected` (`QItemSelection`): Selected items.
        - `_deselected` (`QItemSelection`): Deselected items.

        """
        indexes = selected.indexes()
        if indexes and self.habits_filter_list_model:
            index = indexes[0]
            if index.isValid():
                item = self.habits_filter_list_model.itemFromIndex(index)
                habit_name = (item.data(Qt.ItemDataRole.UserRole) if item is not None else None) or (
                    self.habits_filter_list_model.data(index) or ""
                )
                if habit_name and habit_name.strip():
                    # Get selected year from list view
                    selected_text = self._get_selected_habit_year()
                    year = None
                    if selected_text != "Last 365 days":
                        try:
                            year = int(selected_text)
                        except ValueError:
                            year = None
                    # Apply filter to process_habits table
                    self.load_process_habits_table(ignore_filter=False)
                    # Update heatmap with selected habit
                    self.update_habit_calendar_heatmap(habit_name, year=year)

    def on_habit_selection_changed(self, current: QModelIndex, _previous: QModelIndex) -> None:
        """Handle habit table selection change.

        Args:

        - `current` (`QModelIndex`): Current selection index.
        - `_previous` (`QModelIndex`): Previous selection index.

        """
        if current.isValid():
            self.update_habit_calendar_heatmap()

    def on_habit_year_changed(self, index: QModelIndex) -> None:
        """Handle habit year list view change.

        Args:

        - `index` (`QModelIndex`): Selected index.

        """
        if self.db_manager is None:
            return

        if not index.isValid():
            return

        selected_text = self._get_selected_habit_year()
        habit_name = self._get_selected_habit_filter()

        if not habit_name:
            return

        # Parse year from selection
        year = None
        if selected_text != "Last 365 days":
            try:
                year = int(selected_text)
            except ValueError:
                year = None

        # Apply filter to process_habits table
        self.load_process_habits_table(ignore_filter=False)
        # Update heatmap with selected year
        self.update_habit_calendar_heatmap(habit_name, year=year)

    def on_habit_year_selection_changed(self, current: QModelIndex, _previous: QModelIndex) -> None:
        """Handle habit year list view selection change.

        Args:

        - `current` (`QModelIndex`): Current selected index.
        - `_previous` (`QModelIndex`): Previous selected index.

        """
        if current.isValid():
            self.on_habit_year_changed(current)

    @requires_database()
    @requires_database()
    @requires_database()
    @requires_database()
    def on_toggle_show_all_habits_records(self) -> None:
        """Toggle between showing all habits records and limited records."""
        # This will be handled in load_process_habits_table
        self.show_tables()

    @requires_database()
    @requires_database()
    def refresh_habits_and_process_habits(self) -> None:
        """Refresh habits table and process_habits table (ignoring filter for process_habits)."""
        if self._is_closing:
            return
        if not self._validate_database_connection():
            print("Database connection not available for refresh_habits_and_process_habits")
            return

        # Refresh habits table using update_all logic
        try:
            if not self.db_manager.table_exists("habits"):
                print("⚠️ Table 'habits' does not exist in database")
                self._set_habits_table_model(self._create_colored_table_model([], self.table_config["habits"][2]))
            else:
                habits_data = self.db_manager.get_all_habits()
                habits_transformed_data = []
                light_blue = QColor(240, 248, 255)  # Light blue background

                # Minimum habit row length: habit_id (index 0) + habit_name (index 1)
                min_habit_row_length = 2
                for row in habits_data:
                    try:
                        if len(row) < min_habit_row_length:
                            continue
                        is_bool_value = row[2] if len(row) > min_habit_row_length else None
                        is_bool_str = "Yes" if is_bool_value == 1 else ("No" if is_bool_value == 0 else "")
                        archived_idx = 3
                        is_archived_value = row[archived_idx] if len(row) > archived_idx else 0
                        is_archived_str = "Yes" if is_archived_value == 1 else "No"
                        habit_name = row[1] or ""
                        habit_id = row[0] if row[0] is not None else 0
                        transformed_row = [habit_name, is_bool_str, is_archived_str, habit_id, light_blue]
                        habits_transformed_data.append(transformed_row)
                    except Exception as e:
                        print(f"Error processing habit row: {e}")
                        continue
                self._set_habits_table_model(
                    self._create_colored_table_model(habits_transformed_data, self.table_config["habits"][2])
                )
        except Exception as habits_error:
            print(f"Error refreshing habits table: {habits_error}")

        # Refresh process_habits table without filter
        self.refresh_process_habits_table()
        self.update_habits_filter_combobox()

    @requires_database()
    def refresh_process_habits_table(self) -> None:
        """Refresh process habits table ignoring any filters."""
        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        # Load table without filter
        self.load_process_habits_table(ignore_filter=True)

    def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        """Handle window resize event and adjust table column widths proportionally.

        Args:

        - `event` (`QResizeEvent`): The resize event.

        """
        # Call parent resize event first
        super().resizeEvent(event)

        self._update_layout_for_window_size()

    @requires_database()
    @requires_database()
    def show_tables(self) -> None:
        """Populate habits and process_habits QTableViews using database manager."""
        if not self._validate_database_connection():
            print("Database connection not available for showing tables")
            return

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            # Refresh habits table
            if not self.db_manager.table_exists("habits"):
                print("⚠️ Table 'habits' does not exist in database")
                self._set_habits_table_model(self._create_colored_table_model([], self.table_config["habits"][2]))
            else:
                habits_data = self.db_manager.get_all_habits()
                habits_transformed_data = []
                light_blue = QColor(240, 248, 255)  # Light blue background
                min_habit_row_length = 2
                for row in habits_data:
                    try:
                        if len(row) < min_habit_row_length:
                            continue
                        is_bool_value = row[2] if len(row) > min_habit_row_length else None
                        is_bool_str = "Yes" if is_bool_value == 1 else ("No" if is_bool_value == 0 else "")
                        archived_idx = 3
                        is_archived_value = row[archived_idx] if len(row) > archived_idx else 0
                        is_archived_str = "Yes" if is_archived_value == 1 else "No"
                        habit_name = row[1] or ""
                        habit_id = row[0] if row[0] is not None else 0
                        transformed_row = [
                            habit_name,
                            is_bool_str,
                            is_archived_str,
                            habit_id,
                            light_blue,
                        ]
                        habits_transformed_data.append(transformed_row)
                    except Exception as e:
                        print(f"Error processing habit row: {e}")
                        continue
                self._set_habits_table_model(
                    self._create_colored_table_model(habits_transformed_data, self.table_config["habits"][2])
                )

            # Load process habits table data
            if self.db_manager.table_exists("process_habits"):
                self.load_process_habits_table(ignore_filter=True)
                selected_habit = self._get_selected_habit_from_table()
                if selected_habit:
                    self.update_habit_calendar_heatmap(selected_habit)
            else:
                print("⚠️ Table 'process_habits' does not exist in database")
                self.models["process_habits"] = self._create_colored_table_model(
                    [], self.table_config["process_habits"][2]
                )
                self.tableView_process_habits.setModel(self.models["process_habits"])
                self._connect_table_auto_save_signal("process_habits")

            # Connect selection change signals for habits table
            self._connect_table_signals("habits", self.on_habit_selection_changed)
            # Connect auto-save signals after all models are created
            self._connect_table_auto_save_signals()

        except Exception as e:
            print(f"Error showing tables: {e}")
            message_box.warning(self, "Database Error", f"Failed to load tables: {e}")

    def update_all(
        self,
    ) -> None:
        """Refresh habits and process_habits tables and filter list views."""
        if not self._validate_database_connection():
            print("Database connection not available for update_all")
            return

        self.show_all_records = False
        self.pushButton_habits_show_all_records.setText("📋 Show All Records")

        self.show_tables()
        self.update_habits_filter_combobox()
        self.update_habits_year_combobox()

    @requires_database(is_show_warning=False)
    @requires_database(is_show_warning=False)
    @requires_database()
    @requires_database(is_show_warning=False)
    @requires_database(is_show_warning=False)
    @requires_database()
    def update_habit_calendar_heatmap(self, habit_name: str | None = None, year: int | None = None) -> None:
        """Update the habit calendar heatmap using database manager.

        Args:

        - `habit_name` (`str | None`): Name of the habit to display. If `None`, uses selected habit from

        `listView_filter_habit`.

        - `year` (`int | None`): Year to display. If `None`, shows last 365 days.

        """
        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        # Get habit name from parameter or from list view selection
        if habit_name is None:
            habit_name = self._get_selected_habit_filter()
            if not habit_name:
                self._show_habit_heatmap_message("Please select a habit")
                return

        # Calculate date range based on year parameter
        today = datetime.now(UTC).astimezone().date()
        if year is not None:
            # Specific year: from January 1 to December 31 of that year
            start_date = datetime(year, 1, 1, tzinfo=UTC).astimezone().date()
            end_date = datetime(year, 12, 31, tzinfo=UTC).astimezone().date()
            # If year is current year, limit to today
            if year == today.year:
                end_date = today
        else:
            # Last 365 days (default)
            start_date = today - timedelta(days=365)
            end_date = today

        # Get data for the specified date range
        rows = self.db_manager.get_habit_calendar_data(
            habit_name,
            date_from=start_date.strftime("%Y-%m-%d"),
            date_to=end_date.strftime("%Y-%m-%d"),
        )
        if not rows:
            period_text = f"year {year}" if year is not None else "last 365 days"
            self._show_habit_heatmap_message(f"No data found for habit '{habit_name}' for {period_text}")
            return

        # Convert to pandas DataFrame
        dates = [datetime.fromisoformat(row[0]).date() for row in rows]
        values = [row[1] for row in rows]
        df = pd.DataFrame({"dates": dates, "values": values})

        # start_date and end_date are already calculated above

        figure = Figure(figsize=(15, 6), dpi=100)
        ax = figure.add_subplot(111)

        # Create calendar heatmap using dayplot
        try:
            # --- Color/legend rules for habits ---
            # Requirements:
            # - 0 is ALWAYS gray
            # - if is_bool=1 and only {0,1} are present: 1 is dark green
            # - otherwise: positives are green shades, negatives are red shades
            # - legend must contain exactly the values that appear on the plot
            #
            # dayplot switches to a diverging scale when negatives exist and then ignores
            # `color_for_none`, so we map real values -> non-negative indices to keep the
            # "0 gray" behavior stable, and draw a custom legend.

            def _lerp(
                a: tuple[float, float, float],
                b: tuple[float, float, float],
                t: float,
            ) -> tuple[float, float, float]:
                return (
                    a[0] + (b[0] - a[0]) * t,
                    a[1] + (b[1] - a[1]) * t,
                    a[2] + (b[2] - a[2]) * t,
                )

            def _gradient(
                a: tuple[float, float, float],
                b: tuple[float, float, float],
                n: int,
            ) -> list[tuple[float, float, float]]:
                if n <= 0:
                    return []
                if n == 1:
                    return [a]
                return [_lerp(a, b, i / (n - 1)) for i in range(n)]

            # Aggregate per-date like dayplot does (sum), then collect actual displayed values.
            df_agg = df.groupby("dates", as_index=False)["values"].sum()
            display_values_set = {int(v) for v in df_agg["values"].tolist()}
            display_values_set.add(0)  # missing days are displayed as 0

            # Fetch is_bool flag for this habit
            is_bool_flag: bool | None = None
            try:
                rows_is_bool = self.db_manager.get_rows(
                    "SELECT is_bool FROM habits WHERE name = :name LIMIT 1",
                    {"name": habit_name},
                )
                if rows_is_bool and rows_is_bool[0]:
                    raw_is_bool = rows_is_bool[0][0]
                    if raw_is_bool in (0, 1):
                        is_bool_flag = bool(raw_is_bool)
            except Exception:
                is_bool_flag = None

            is_bool_case = is_bool_flag is True and display_values_set.issubset({0, 1})

            # Base colors
            gray = "#e9e9e9"
            dark_green = "#006400"
            light_green = "#b7e4b7"
            dark_red = "#8b0000"
            light_red = "#f3b0b0"
            # Special color for maximum value in non-binary habits
            max_value_color = "#3141DA"  # Very dark green to highlight maximum

            # Map real value -> non-negative index, ensuring real 0 maps to 0 (for gray).
            value_to_mapped: dict[int, int] = {0: 0}

            if is_bool_case:
                value_to_mapped[1] = 1
                mapped_vmax = 1
                colors = [to_rgb(gray), to_rgb(dark_green)]
                cmap = LinearSegmentedColormap.from_list("habits_bool_map", colors, N=len(colors))
                legend_order = [0, 1]
            else:
                neg_values = sorted([v for v in display_values_set if v < 0])
                pos_values = sorted([v for v in display_values_set if v > 0])

                # Find maximum value (could be positive or negative)
                max_value = max(display_values_set) if display_values_set else 0

                # Check if values are binary (only 0 and 1) - if not, highlight maximum
                is_binary_values = display_values_set.issubset({0, 1})
                should_highlight_max = not is_binary_values and max_value != 0

                idx = 1
                for v in neg_values:
                    value_to_mapped[v] = idx
                    idx += 1
                for v in pos_values:
                    value_to_mapped[v] = idx
                    idx += 1

                mapped_vmax = max(idx - 1, 0)

                # Build discrete palette: [0]=gray (unused by cmap for 0), then reds, then greens.
                colors_list: list[tuple[float, float, float]] = [to_rgb(gray)]

                # Handle negative values
                if neg_values:
                    if should_highlight_max and max_value < 0:
                        # Maximum is negative and should be highlighted
                        non_max_neg = [v for v in neg_values if v != max_value]
                        if non_max_neg:
                            # Gradient for non-maximum negative values
                            colors_list.extend(_gradient(to_rgb(dark_red), to_rgb(light_red), len(non_max_neg)))
                        # Add very dark red for maximum negative value
                        colors_list.append(to_rgb("#5b0000"))  # Very dark red
                    else:
                        # Normal gradient for all negative values
                        colors_list.extend(_gradient(to_rgb(dark_red), to_rgb(light_red), len(neg_values)))

                # Handle positive values
                if pos_values:
                    if should_highlight_max and max_value > 0:
                        # Maximum value should be highlighted - put it at the end
                        non_max_pos = [v for v in pos_values if v != max_value]
                        if non_max_pos:
                            # Gradient for non-maximum positive values
                            colors_list.extend(_gradient(to_rgb(light_green), to_rgb(dark_green), len(non_max_pos)))
                        # Add special very dark green color for maximum value at the end
                        colors_list.append(to_rgb(max_value_color))
                    else:
                        # Normal gradient for all positive values
                        colors_list.extend(_gradient(to_rgb(light_green), to_rgb(dark_green), len(pos_values)))

                # dayplot requires a LinearSegmentedColormap; ensure at least 2 colors.
                if len(colors_list) == 1:
                    colors_list.append(to_rgb(gray))

                cmap = LinearSegmentedColormap.from_list(
                    "habits_signed_map",
                    colors_list,
                    N=len(colors_list),
                )
                legend_order = [*neg_values, 0, *pos_values]

            df_mapped = df.copy()
            df_mapped["values_mapped"] = [value_to_mapped.get(int(v), 0) for v in df_mapped["values"].tolist()]

            dp.calendar(
                dates=df_mapped["dates"].tolist(),
                values=df_mapped["values_mapped"],
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d"),
                legend=False,  # custom legend below
                color_for_none=gray,
                vmin=0,
                vmax=max(mapped_vmax, 1),
                cmap=cmap,
                boxstyle="round",
                ax=ax,
            )

            # Custom legend: exactly the displayed values
            norm = Normalize(vmin=0, vmax=max(mapped_vmax, 1))
            handles: list[Patch] = []
            for v in legend_order:
                if v == 0:
                    color = gray
                else:
                    mapped = value_to_mapped.get(v, 0)
                    color = cmap(norm(mapped))
                handles.append(Patch(facecolor=color, edgecolor="none", label=str(v)))

            ax.legend(
                handles=handles,
                title="Value",
                loc="upper center",
                bbox_to_anchor=(0.5, -0.10),
                ncol=min(len(handles), 10),
                frameon=False,
                fontsize=8,
                title_fontsize=8,
            )
            # Set smaller font size for title
            period_label = str(year) if year is not None else "Last 365 days"
            ax.set_title(f"Calendar Heatmap: {habit_name} ({period_label})", fontsize=10, fontweight="bold")
            # Reduce font size for all text elements (axes labels and ticks)
            ax.tick_params(labelsize=8)
            if ax.xaxis.label:
                ax.xaxis.label.set_fontsize(8)
            if ax.yaxis.label:
                ax.yaxis.label.set_fontsize(8)
            # Reduce font size for all text elements in the plot
            for text in ax.texts:
                text.set_fontsize(8)
            figure.tight_layout(rect=(0, 0.06, 1, 1))
        except Exception as e:
            print(f"Error creating calendar heatmap: {e}")
            self._show_habit_heatmap_message(f"Error creating calendar heatmap: {e}")
            return

        self._display_habit_heatmap_figure(figure)

    def update_habits_filter_combobox(self) -> None:
        """Refresh habit filter list view in the filter group."""
        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            # Check if table exists
            if not self.db_manager.table_exists("habits"):
                print("⚠️ Table 'habits' does not exist, skipping filter list view update")
                if self.habits_filter_list_model:
                    self.habits_filter_list_model.clear()
                return

            current_habit = self._get_selected_habit_filter()

            if not self.habits_filter_list_model:
                self.habits_filter_list_model = QStandardItemModel()
                self.listView_filter_habit.setModel(self.habits_filter_list_model)
                # Reconnect signals after setting new model
                selection_model = self.listView_filter_habit.selectionModel()
                if selection_model:
                    # Disconnect first to avoid duplicates
                    with contextlib.suppress(TypeError):
                        selection_model.currentChanged.disconnect()
                        selection_model.selectionChanged.disconnect()
                    selection_model.currentChanged.connect(self.on_habit_filter_selection_changed)
                    selection_model.selectionChanged.connect(self.on_habit_filter_selection_changed_slot)
                # Disconnect signals first to avoid duplicates
                with contextlib.suppress(TypeError, RuntimeError), warnings.catch_warnings():
                    warnings.simplefilter("ignore", RuntimeWarning)
                    self.listView_filter_habit.clicked.disconnect()
                with contextlib.suppress(TypeError, RuntimeError), warnings.catch_warnings():
                    warnings.simplefilter("ignore", RuntimeWarning)
                    self.listView_filter_habit.activated.disconnect()
                self.listView_filter_habit.clicked.connect(self.on_habit_filter_clicked)
                self.listView_filter_habit.activated.connect(self.on_habit_filter_clicked)

            selection_model = self.listView_filter_habit.selectionModel()
            if selection_model:
                selection_model.blockSignals(True)  # noqa: FBT003

            self.habits_filter_list_model.clear()

            habits_data = self.db_manager.get_habits(include_archived=self.show_archived_habits)
            for row in habits_data:
                min_habit_filter_columns = 2
                archived_idx = 3
                if len(row) < min_habit_filter_columns:
                    continue
                habit_id = row[0]
                habit_name = row[1] or ""
                if not str(habit_name).strip():
                    continue
                is_archived = (
                    bool(row[archived_idx]) if len(row) > archived_idx and row[archived_idx] in (0, 1) else False
                )

                display = f"{habit_name} (archived)" if (is_archived and self.show_archived_habits) else str(habit_name)
                item = QStandardItem(display)
                # Store raw name/id/archived in user roles (display text can change).
                item.setData(str(habit_name), Qt.ItemDataRole.UserRole)
                item.setData(int(habit_id) if habit_id is not None else None, Qt.ItemDataRole.UserRole + 1)
                item.setData(is_archived, Qt.ItemDataRole.UserRole + 2)
                self.habits_filter_list_model.appendRow(item)

            # Restore previous selection if it exists, otherwise select first habit
            selected_index = None
            if current_habit:
                for row in range(self.habits_filter_list_model.rowCount()):
                    item = self.habits_filter_list_model.item(row)
                    if item and (item.data(Qt.ItemDataRole.UserRole) or item.text()) == current_habit:
                        selected_index = self.habits_filter_list_model.index(row, 0)
                        break

            # If no previous selection, select first habit (index 0)
            if selected_index is None and self.habits_filter_list_model.rowCount() > 0:
                selected_index = self.habits_filter_list_model.index(0, 0)  # First habit

            # If we need to select first habit (no previous selection), do it before unblocking signals
            if selected_index is not None:
                if selection_model:
                    selection_model.setCurrentIndex(selected_index, selection_model.SelectionFlag.ClearAndSelect)
                else:
                    self.listView_filter_habit.setCurrentIndex(selected_index)

                # Trigger the update manually while signals are blocked to avoid double call
                if selected_index.isValid():
                    selected_habit = self.habits_filter_list_model.data(selected_index) or ""
                    if selected_habit and selected_habit.strip():
                        # Get selected year from list view
                        selected_text = self._get_selected_habit_year()
                        year = None
                        if selected_text != "Last 365 days":
                            try:
                                year = int(selected_text)
                            except ValueError:
                                year = None
                        # Manually trigger the selection change handler to build the graph
                        self.update_habit_calendar_heatmap(selected_habit, year=year)

            if selection_model:
                selection_model.blockSignals(False)  # noqa: FBT003

        except Exception as e:
            print(f"Error updating habits filter list view: {e}")

    @requires_database()
    def update_habits_year_combobox(self) -> None:
        """Refresh habit year list view with available years from process_habits table."""
        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            # Check if table exists
            if not self.db_manager.table_exists("process_habits"):
                print("⚠️ Table 'process_habits' does not exist, skipping year list view update")
                if not self.habits_year_list_model:
                    self._init_habits_year_list()
                if self.habits_year_list_model:
                    self.habits_year_list_model.clear()
                    item = QStandardItem("Last 365 days")
                    self.habits_year_list_model.appendRow(item)
                return

            current_selection = self._get_selected_habit_year()

            # Initialize model if needed
            if not self.habits_year_list_model:
                self._init_habits_year_list()

            selection_model = self.listView_filter_habit_year.selectionModel()
            if selection_model:
                selection_model.blockSignals(True)  # noqa: FBT003

            if self.habits_year_list_model:
                self.habits_year_list_model.clear()

                # Add "Last 365 days" as first item
                item = QStandardItem("Last 365 days")
                self.habits_year_list_model.appendRow(item)

                # Get years from database
                years = self.db_manager.get_habits_years()
                for year in years:
                    item = QStandardItem(str(year))
                    self.habits_year_list_model.appendRow(item)

                # Restore previous selection or select "Last 365 days" by default
                if current_selection:
                    # Find index of current selection
                    found_index = None
                    for row in range(self.habits_year_list_model.rowCount()):
                        index = self.habits_year_list_model.index(row, 0)
                        if self.habits_year_list_model.data(index) == current_selection:
                            found_index = index
                            break
                    if found_index and found_index.isValid():
                        self.listView_filter_habit_year.setCurrentIndex(found_index)
                    else:
                        # Select first item ("Last 365 days")
                        first_index = self.habits_year_list_model.index(0, 0)
                        self.listView_filter_habit_year.setCurrentIndex(first_index)
                else:
                    # Select first item ("Last 365 days")
                    first_index = self.habits_year_list_model.index(0, 0)
                    self.listView_filter_habit_year.setCurrentIndex(first_index)

            if selection_model:
                selection_model.blockSignals(False)  # noqa: FBT003

        except Exception as e:
            print(f"Error updating habits year list view: {e}")

    def _after_table_data_changed(
        self,
        table_name: str,
        top_left: QModelIndex,  # noqa: ARG002
        bottom_right: QModelIndex,  # noqa: ARG002
    ) -> None:
        if table_name == "habits":
            self._schedule_habits_refresh(0)

    def _cleanup_process_habit_delegates(self) -> None:
        """Remove process_habits table delegates before window destruction."""
        table_view = self.tableView_process_habits
        default_delegate = table_view.itemDelegate()
        for col_idx in self._process_habits_bool_columns | self._process_habits_int_columns:
            table_view.setItemDelegateForColumn(col_idx, default_delegate)
        for delegate in (self._process_habit_bool_delegate, self._process_habit_int_delegate):
            if delegate is not None:
                delegate.detach_from_view(table_view)
        self._process_habits_bool_columns.clear()
        self._process_habits_int_columns.clear()
        self._process_habit_bool_delegate = None
        self._process_habit_int_delegate = None

    def _clear_habit_heatmap_message_widgets(self) -> None:
        """Remove placeholder labels from the heatmap layout, keeping the chart label."""
        layout = self.verticalLayout_charts_process_habits_content
        heatmap_label = self._habits_heatmap_label
        for index in reversed(range(layout.count())):
            item = layout.takeAt(index)
            if item is None:
                continue
            widget = item.widget()
            if widget is not None and widget is not heatmap_label:
                widget.hide()
                widget.deleteLater()

    @requires_database(is_show_warning=False)
    @requires_database()
    def _connect_signals(self) -> None:
        """Wire Qt widgets to their Python slots (habits only)."""
        tables_with_controls = {"habits", "process_habits"}
        for table_name in tables_with_controls:
            if table_name == "habits":
                delete_btn_name = "pushButton_habits_delete_selected"
            else:
                delete_btn_name = "pushButton_habits_delete"
            delete_button = getattr(self, delete_btn_name, None)
            if delete_button:
                delete_button.clicked.connect(partial(self.delete_record, table_name))

            if table_name == "habits":
                refresh_btn_name = "pushButton_habits_refresh_table"
            else:
                refresh_btn_name = "pushButton_habits_refresh"
            refresh_button = getattr(self, refresh_btn_name, None)
            if refresh_button:
                if table_name == "process_habits":
                    refresh_button.clicked.connect(self.refresh_process_habits_table)
                else:
                    refresh_button.clicked.connect(self.refresh_habits_and_process_habits)

        self.pushButton_habit_add_new.clicked.connect(self.on_add_habit)
        self.pushButton_habits_show_all_records.clicked.connect(self.on_toggle_show_all_habits_records)
        self.pushButton_habits_export_csv.clicked.connect(self.on_export_habits_csv)

        self.tableView_process_habits.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tableView_process_habits.customContextMenuRequested.connect(self._show_process_habits_context_menu)
        self.tableView_process_habits.clicked.connect(self._on_process_habits_table_clicked)

    def _display_habit_heatmap_figure(self, figure: Figure) -> None:
        """Render matplotlib figure off-screen and show it in a QLabel."""
        agg_canvas = FigureCanvasAgg(figure)
        agg_canvas.draw()
        width, height = agg_canvas.get_width_height()
        image = QImage(
            agg_canvas.buffer_rgba(),
            width,
            height,
            width * 4,
            QImage.Format.Format_RGBA8888,
        ).copy()
        pixmap = QPixmap.fromImage(image)

        self._clear_habit_heatmap_message_widgets()
        if self._habits_heatmap_label is None:
            self._habits_heatmap_label = QLabel()
            self._habits_heatmap_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.verticalLayout_charts_process_habits_content.addWidget(self._habits_heatmap_label)
        self._habits_heatmap_label.setPixmap(pixmap)
        self._habits_heatmap_label.show()

    def _dispose_models(self) -> None:
        """Detach all models from QTableView and delete them (habits only)."""
        for key, model in self.models.items():
            view = self.table_config[key][0]
            view.setModel(None)
            if model is not None:
                model.deleteLater()
            self.models[key] = None

    def _finish_window_initialization(self) -> None:
        """Finish window initialization by showing the window and adjusting habits splitter."""
        if self._is_closing:
            return
        self.show()
        QTimer.singleShot(100, self._set_habits_splitter_size)

    def _get_selected_habit_filter(self) -> str:
        """Get the currently selected habit from the filter list view."""
        if not self.habits_filter_list_model:
            return ""
        current_index = self.listView_filter_habit.currentIndex()
        if current_index.isValid():
            item = self.habits_filter_list_model.itemFromIndex(current_index)
            if item is None:
                return self.habits_filter_list_model.data(current_index) or ""
            raw_name = item.data(Qt.ItemDataRole.UserRole)
            if isinstance(raw_name, str) and raw_name.strip():
                return raw_name
            return item.text() or ""
        return ""

    def _get_selected_habit_from_table(self) -> str | None:
        """Get the selected habit name from the habits table.

        Returns:

        - `str | None`: Selected habit name or `None` if no selection.

        """
        if "habits" not in self.table_config:
            return None

        view = self.table_config["habits"][0]
        selection_model = view.selectionModel()
        if not selection_model or not selection_model.hasSelection():
            return None

        current_index = selection_model.currentIndex()
        if not current_index.isValid():
            return None

        model = view.model()
        # Habit name is in the first column (index 0)
        habit_name = model.data(model.index(current_index.row(), 0), Qt.ItemDataRole.DisplayRole)
        return str(habit_name) if habit_name else None

    def _get_selected_habit_year(self) -> str:
        """Get the currently selected year from the year list view."""
        if not self.habits_year_list_model:
            return ""
        current_index = self.listView_filter_habit_year.currentIndex()
        if current_index.isValid():
            return self.habits_year_list_model.data(current_index) or ""
        return ""

    def _handle_special_table_data_changed(
        self,
        table_name: str,
        top_left: QModelIndex,
        bottom_right: QModelIndex,
        model: QStandardItemModel,
        _roles: list | None = None,
    ) -> bool:
        if table_name != "process_habits":
            return False

        for row in range(top_left.row(), bottom_right.row() + 1):
            for col in range(top_left.column(), bottom_right.column() + 1):
                if col == 0:
                    continue

                item = model.item(row, col)
                if item is None:
                    continue

                stored_data = item.data(Qt.ItemDataRole.UserRole)
                if stored_data is None:
                    date_item = model.item(row, 0)
                    if date_item is None:
                        continue
                    date_str = date_item.text()
                    habit_name = model.horizontalHeaderItem(col).text() if model.horizontalHeaderItem(col) else None
                    if not habit_name or not self.db_manager:
                        continue

                    habits_data = self.db_manager.get_all_habits()
                    habit_id = None
                    min_habit_row_length = 2
                    for h_row in habits_data:
                        if len(h_row) >= min_habit_row_length and h_row[1] == habit_name:
                            habit_id = h_row[0]
                            break
                    if habit_id is None:
                        continue
                    record_id = None
                else:
                    record_id, habit_id, date_str = stored_data

                value_str = item.text() or ""
                self._save_process_habits_data(model, row, col, record_id, habit_id, date_str, value_str)
        return True

    def _init_database(self) -> None:
        """Open the SQLite file from app config (create from `recover.sql` if missing)."""
        app_dir = Path(__file__).parent

        def _on_db_opened(db_manager: database_manager.DatabaseManager) -> None:
            with contextlib.suppress(Exception):
                db_manager.ensure_habits_schema()

        self.db_manager = init_tracker_database(
            self,
            Path(self._app_config["sqlite_habits"]),
            "habits",
            app_dir / "recover.sql",
            database_manager.DatabaseManager,
            has_required_tables=lambda dm: dm.table_exists("habits") or dm.table_exists("process_habits"),
            missing_table_label="habits/process_habits table",
            on_opened=_on_db_opened,
        )

    def _init_habits_filter_list(self) -> None:
        """Initialize the habits filter list view with a model and connect signals."""
        self.habits_filter_list_model = QStandardItemModel()
        self.listView_filter_habit.setModel(self.habits_filter_list_model)

        # Disable editing for habits filter list
        self.listView_filter_habit.setEditTriggers(QListView.EditTrigger.NoEditTriggers)

        # Context menu
        self.listView_filter_habit.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.listView_filter_habit.customContextMenuRequested.connect(self._show_habit_filter_context_menu)

        # Connect selection change signals after model is set
        selection_model = self.listView_filter_habit.selectionModel()
        if selection_model:
            selection_model.currentChanged.connect(self.on_habit_filter_selection_changed)
            # Also connect selectionChanged for additional reliability
            selection_model.selectionChanged.connect(self.on_habit_filter_selection_changed_slot)

        # Also connect clicked and activated signals for reliability when user interacts
        self.listView_filter_habit.clicked.connect(self.on_habit_filter_clicked)
        self.listView_filter_habit.activated.connect(self.on_habit_filter_clicked)

    def _init_habits_table_delegates(self) -> None:
        """Install delegates for habits table columns."""
        # Column indexes in habits table: 0=Habit, 1=Is Boolean, 2=Is Archived
        yes_no_delegate = YesNoComboDelegate(self.tableView_habits)
        self.tableView_habits.setItemDelegateForColumn(1, yes_no_delegate)
        self.tableView_habits.setItemDelegateForColumn(2, yes_no_delegate)

    def _init_habits_year_list(self) -> None:
        """Initialize the habits year list view with a model and connect signals."""
        self.habits_year_list_model = QStandardItemModel()
        self.listView_filter_habit_year.setModel(self.habits_year_list_model)

        # Disable editing for habits year list
        self.listView_filter_habit_year.setEditTriggers(QListView.EditTrigger.NoEditTriggers)

        # Context menu
        self.listView_filter_habit_year.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.listView_filter_habit_year.customContextMenuRequested.connect(self._show_habit_year_filter_context_menu)

        # Connect selection change signals after model is set
        selection_model = self.listView_filter_habit_year.selectionModel()
        if selection_model:
            selection_model.currentChanged.connect(self.on_habit_year_selection_changed)

        # Also connect clicked and activated signals for reliability when user interacts
        self.listView_filter_habit_year.clicked.connect(self.on_habit_year_changed)
        self.listView_filter_habit_year.activated.connect(self.on_habit_year_changed)

        # Optional: Show a brief notification (you can remove this if not needed)
        # You could add a toast notification here if you have one

    def _on_process_habits_table_clicked(self, index: QModelIndex) -> None:
        """Handle click on process habits table.

        If date column (column 0) is clicked, start editing first habit cell in that row.

        Args:

        - `index` (`QModelIndex`): Index of clicked cell.

        """
        if not index.isValid():
            return

        # Get source model index (accounting for proxy model)
        proxy_model = self.models.get("process_habits")
        if proxy_model is None:
            return

        source_index = proxy_model.mapToSource(index)
        if not source_index.isValid():
            return

        # If date column (column 0) is clicked, start editing first non-boolean habit cell
        if source_index.column() == 0:
            row = source_index.row()
            source_model = proxy_model.sourceModel()
            if not isinstance(source_model, QStandardItemModel):
                return

            for col in range(1, source_model.columnCount()):
                if col in self._process_habits_bool_columns:
                    continue
                habit_proxy_index = proxy_model.index(row, col)
                if habit_proxy_index.isValid():
                    self.tableView_process_habits.setCurrentIndex(habit_proxy_index)
                    self.tableView_process_habits.edit(habit_proxy_index)
                break

    def _release_habit_heatmap_display(self) -> None:
        """Remove heatmap label widget before window destruction."""
        label = self._habits_heatmap_label
        if label is not None:
            label.setParent(None)
            label.hide()
            label.deleteLater()
        self._habits_heatmap_label = None
        self._clear_habit_heatmap_message_widgets()

    def _schedule_habits_refresh(self, delay_ms: int = 0) -> None:
        """Debounce refresh triggered by auto-save edits in habits table."""
        timer = getattr(self, "_habits_refresh_timer", None)
        if timer is None:
            timer = QTimer(self)
            timer.setSingleShot(True)
            timer.timeout.connect(self.refresh_habits_and_process_habits)
            self._habits_refresh_timer = timer
        timer.start(delay_ms)

    def _set_habits_splitter_size(self) -> None:
        """Set initial width for frame_habits to 350 pixels."""
        if self._is_closing:
            return
        min_count_of_widgets = 2
        if self.splitter_habits.count() >= min_count_of_widgets:
            # Get current total width of the splitter
            total_width = self.splitter_habits.width()
            if total_width > 0:
                # Set frame_habits to 350 pixels, rest goes to tableView_process_habits
                frame_width = 350
                table_width = max(100, total_width - frame_width)  # Ensure minimum width for table
                self.splitter_habits.setSizes([frame_width, table_width])
            else:
                # If splitter doesn't have width yet, try again after a short delay
                QTimer.singleShot(50, self._set_habits_splitter_size)

    def _set_habits_table_model(self, model: QSortFilterProxyModel) -> None:
        """Assign habits table model after closing any open inline editor."""
        close_table_editor_if_open(self.tableView_habits)
        self.models["habits"] = model
        self.tableView_habits.setModel(model)
        self._connect_table_auto_save_signal("habits")

    # Add to MainWindow class (near other small helpers)

    def _setup_ui(self) -> None:
        """Set up additional UI elements after basic initialization (habits only)."""
        self.pushButton_habits_delete.setText(f"🗑️ {self.pushButton_habits_delete.text()}")
        self.pushButton_habits_refresh.setText(f"🔄 {self.pushButton_habits_refresh.text()}")
        self.pushButton_habits_show_all_records.setText(f"📋 {self.pushButton_habits_show_all_records.text()}")
        self.pushButton_habits_export_csv.setText(f"📤 {self.pushButton_habits_export_csv.text()}")
        self.pushButton_habit_add_new.setText(f"➕ {self.pushButton_habit_add_new.text()}")  # noqa: RUF001
        self.pushButton_habits_delete_selected.setText(f"🗑️ {self.pushButton_habits_delete_selected.text()}")
        self.pushButton_habits_refresh_table.setText(f"🔄 {self.pushButton_habits_refresh_table.text()}")

        self.splitter_habits.setStretchFactor(0, 1)
        self.splitter_habits.setStretchFactor(1, 3)
        self.splitter_3.setStretchFactor(0, 0)
        self.splitter_3.setStretchFactor(1, 1)
        self.splitter_3.setSizes([150, 1000])
        self.splitter_4.setStretchFactor(0, 4)
        self.splitter_4.setStretchFactor(1, 1)

    def _show_habit_filter_context_menu(self, position: QPoint) -> None:
        """Show context menu for habit filter list view."""
        if self.db_manager is None:
            return

        context_menu = QMenu(self)

        index = self.listView_filter_habit.indexAt(position)
        item = (
            self.habits_filter_list_model.itemFromIndex(index)
            if (index.isValid() and self.habits_filter_list_model)
            else None
        )

        habit_id = item.data(Qt.ItemDataRole.UserRole + 1) if item is not None else None
        is_archived = bool(item.data(Qt.ItemDataRole.UserRole + 2)) if item is not None else False

        archive_action = context_menu.addAction("🗄 Archive habit")
        unarchive_action = context_menu.addAction("♻ Unarchive habit")
        context_menu.addSeparator()
        if self.show_archived_habits:
            toggle_action = context_menu.addAction("🙈 Hide archived habits")
        else:
            toggle_action = context_menu.addAction("👀 Show archived habits")

        # Enable/disable based on selection state.
        has_habit = habit_id is not None
        archive_action.setEnabled(bool(has_habit and not is_archived))
        unarchive_action.setEnabled(bool(has_habit and is_archived))

        action = context_menu.exec_(self.listView_filter_habit.mapToGlobal(position))
        if action is None:
            return

        if action == toggle_action:
            self._toggle_show_archived_habits()
            return

        if habit_id is None:
            return

        try:
            if action == archive_action:
                self.db_manager.set_habit_archived(int(habit_id), is_archived=True)
            elif action == unarchive_action:
                self.db_manager.set_habit_archived(int(habit_id), is_archived=False)
        finally:
            # Refresh both filter list and tables to reflect new state.
            self.update_habits_filter_combobox()
            self._update_habits_list()

    def _show_habit_heatmap_message(self, text: str) -> None:
        """Show a text placeholder instead of the heatmap chart."""
        self._clear_habit_heatmap_message_widgets()
        if self._habits_heatmap_label is not None:
            self._habits_heatmap_label.hide()
        self._show_no_data_label(self.verticalLayout_charts_process_habits_content, text)

    def _show_habit_year_filter_context_menu(self, position: QPoint) -> None:
        """Show context menu for habit year filter list view."""
        context_menu = QMenu(self)
        if self.show_archived_habits:
            toggle_action = context_menu.addAction("🙈 Hide archived habits")
        else:
            toggle_action = context_menu.addAction("👀 Show archived habits")

        action = context_menu.exec_(self.listView_filter_habit_year.mapToGlobal(position))
        if action is None:
            return
        if action == toggle_action:
            self._toggle_show_archived_habits()

    def _show_process_habits_context_menu(self, position: QPoint) -> None:
        """Show context menu for process habits table.

        Args:

        - `position` (`QPoint`): Position where context menu should appear.

        """
        context_menu = QMenu(self)
        clear_cell_action = None
        menu_proxy_index = self.tableView_process_habits.indexAt(position)

        if menu_proxy_index.isValid():
            proxy_model = self.models.get("process_habits")
            if proxy_model is not None:
                source_index = proxy_model.mapToSource(menu_proxy_index)
                col = source_index.column()
                value_columns = self._process_habits_bool_columns | self._process_habits_int_columns
                if col > 0 and col in value_columns:
                    source_model = proxy_model.sourceModel()
                    if isinstance(source_model, QStandardItemModel):
                        item = source_model.item(source_index.row(), source_index.column())
                        if item is not None:
                            stored_data = item.data(Qt.ItemDataRole.UserRole)
                            has_db_record = bool(stored_data and stored_data[0] is not None)
                            has_display_value = bool(str(item.text() or "").strip())
                            if has_db_record or has_display_value:
                                clear_cell_action = context_menu.addAction("🗑 Clear cell")
                                context_menu.addSeparator()

        refresh_action = context_menu.addAction("🔄 Refresh Table")
        export_action = context_menu.addAction("📤 Export to CSV")
        context_menu.addSeparator()

        # Toggle show all/limited records
        if self.show_all_records:
            show_all_action = context_menu.addAction(f"📋 Show Last {self.count_records_to_show}")
        else:
            show_all_action = context_menu.addAction("📋 Show All Records")

        context_menu.addSeparator()
        if self.show_archived_habits:
            toggle_archived_action = context_menu.addAction("🙈 Hide archived habits")
        else:
            toggle_archived_action = context_menu.addAction("👀 Show archived habits")

        # Execute the context menu and get the selected action
        action = context_menu.exec_(self.tableView_process_habits.mapToGlobal(position))

        # Process the action only if it was actually selected (not None)
        if action is None:
            # User clicked outside the menu or pressed Esc - do nothing
            return

        if action == clear_cell_action and menu_proxy_index.isValid():
            proxy_model = self.models.get("process_habits")
            if proxy_model is not None:
                proxy_model.setData(menu_proxy_index, "", Qt.ItemDataRole.EditRole)
        elif action == refresh_action:
            print("🔧 Context menu: Refresh action triggered")
            self.pushButton_habits_refresh.click()
        elif action == export_action:
            print("🔧 Context menu: Export to CSV action triggered")
            self.pushButton_habits_export_csv.click()
        elif action == show_all_action:
            print("🔧 Context menu: Toggle show all records action triggered")
            self.pushButton_habits_show_all_records.click()
        elif action == toggle_archived_action:
            self._toggle_show_archived_habits()
            # Refresh pivot table to rebuild columns
            self.load_process_habits_table(ignore_filter=False)

    def _shutdown_window_resources(self) -> None:
        """Release timers, models, charts, and database before window destruction."""
        self._is_closing = True

        refresh_timer = getattr(self, "_habits_refresh_timer", None)
        if refresh_timer is not None:
            refresh_timer.stop()

        self._release_habit_heatmap_display()
        self._disconnect_table_auto_save_signals()
        self._cleanup_process_habit_delegates()

        self._dispose_models()

        if self.db_manager:
            self.db_manager.close()
            self.db_manager = None

    def _toggle_show_archived_habits(self) -> None:
        self.show_archived_habits = not self.show_archived_habits
        self.update_habits_filter_combobox()

    @requires_database()
    def _update_habits_list(self) -> None:
        """Update habits table after changes."""
        if not self._validate_database_connection():
            print("Database connection not available for _update_habits_list")
            return

        # Refresh habits table using update_all logic
        try:
            if not self.db_manager.table_exists("habits"):
                print("⚠️ Table 'habits' does not exist in database")
                self._set_habits_table_model(self._create_colored_table_model([], self.table_config["habits"][2]))
            else:
                habits_data = self.db_manager.get_all_habits()
                habits_transformed_data = []
                light_blue = QColor(240, 248, 255)  # Light blue background

                # Minimum habit row length: habit_id (index 0) + habit_name (index 1)
                min_habit_row_length = 2
                for row in habits_data:
                    try:
                        if len(row) < min_habit_row_length:
                            continue
                        is_bool_value = row[2] if len(row) > min_habit_row_length else None
                        is_bool_str = "Yes" if is_bool_value == 1 else ("No" if is_bool_value == 0 else "")
                        archived_idx = 3
                        is_archived_value = row[archived_idx] if len(row) > archived_idx else 0
                        is_archived_str = "Yes" if is_archived_value == 1 else "No"
                        habit_name = row[1] or ""
                        habit_id = row[0] if row[0] is not None else 0
                        transformed_row = [habit_name, is_bool_str, is_archived_str, habit_id, light_blue]
                        habits_transformed_data.append(transformed_row)
                    except Exception as e:
                        print(f"Error processing habit row: {e}")
                        continue
                self._set_habits_table_model(
                    self._create_colored_table_model(habits_transformed_data, self.table_config["habits"][2])
                )
        except Exception as habits_error:
            print(f"Error refreshing habits table: {habits_error}")

    def _update_layout_for_window_size(self) -> None:
        """Adjust key widgets based on current window height (habits UI has no responsive extras)."""
        small_window_threshold = 911
        is_small = self.height() < small_window_threshold
        self._is_small_window_layout = is_small
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
def __init__(self, *, hide_on_close: bool = False) -> None:  # noqa: D107  (inherited from Qt widgets)
        super().__init__()
        try_apply_system_backdrop(self, backdrop=SystemBackdrop.MICA)
        self.setupUi(self)
        self._setup_ui()

        # Set window icon
        self.setWindowIcon(QIcon(":/assets/logo.svg"))

        self._hide_on_close = hide_on_close
        if not hide_on_close:
            self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        # Initialize core attributes
        self._is_closing = False
        self._habits_heatmap_label: QLabel | None = None
        self.db_manager: database_manager.DatabaseManager | None = None
        self._app_config: dict[str, Any] = h.dev.config_load(get_config_path_str())
        self._is_small_window_layout: bool | None = None  # Used by _update_layout_for_window_size

        # Habits filter list model
        self.habits_filter_list_model: QStandardItemModel | None = None
        # Habits year list model
        self.habits_year_list_model: QStandardItemModel | None = None

        # Table models dictionary
        self.models: dict[str, QSortFilterProxyModel | None] = {
            "habits": None,
            "process_habits": None,
        }

        # Process habits table display mode flag
        self.count_records_to_show = 5000
        self.show_all_records = False
        # Habits list view filter flag
        self.show_archived_habits = False
        # Boolean habit column indexes in process_habits pivot (1-based habit columns)
        self._process_habits_bool_columns: set[int] = set()
        self._process_habits_int_columns: set[int] = set()
        self._process_habit_bool_delegate: ProcessHabitBoolDelegate | None = None
        self._process_habit_int_delegate: ProcessHabitIntDelegate | None = None

        # Define colors for different dates (used in process_habits table)
        self.exercise_colors = generate_pastel_qcolors(50)

        # Chart configuration (for heatmap / ChartOperations mixin)
        self.max_count_points_in_charts = 40

        # Table configuration mapping
        self.table_config: dict[str, tuple[QTableView, str, list[str]]] = {
            "habits": (self.tableView_habits, "habits", ["Habit", "Is Boolean", "Is Archived"]),
            "process_habits": (
                self.tableView_process_habits,
                "process_habits",
                [],  # Headers are now dynamic (Date + all habits)
            ),
        }

        # Initialize application
        self._init_database()
        self._connect_signals()
        self._init_habits_table_delegates()
        self._init_habits_filter_list()
        self._init_habits_year_list()
        self.update_all()

        # Set window size and position based on screen resolution
        self._setup_window_size_and_position()

        # Adjust table column widths and show window after UI is fully initialized
        QTimer.singleShot(200, self._finish_window_initialization)
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
        if self._hide_on_close:
            self._is_closing = True
            refresh_timer = getattr(self, "_habits_refresh_timer", None)
            if refresh_timer is not None:
                refresh_timer.stop()
            event.ignore()
            self.hide()
            self._is_closing = False
            return

        self._shutdown_window_resources()
        super().closeEvent(event)
```

</details>

### ⚙️ Method `delete_record`

```python
def delete_record(self, table_name: str) -> None
```

Delete selected row from table using database manager methods.

Args:

- `table_name` (`str`): Name of the table to delete from. Must be in `_SAFE_TABLES`.

Raises:

- `ValueError`: If table_name is not in `_SAFE_TABLES`.

<details>
<summary>Code:</summary>

```python
def delete_record(self, table_name: str) -> None:
        if table_name not in self._SAFE_TABLES:
            error_message = f"Illegal table name: {table_name}"
            raise ValueError(error_message)

        record_id = self._get_selected_row_id(table_name)
        if record_id is None:
            message_box.warning(self, "Error", "Select a record to delete")
            return

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        success = False
        try:
            if table_name == "habits":
                success = self.db_manager.delete_habit(record_id)
            elif table_name == "process_habits":
                success = self.db_manager.delete_process_habit_record(record_id)
        except Exception as e:
            message_box.warning(self, "Database Error", f"Failed to delete record: {e}")
            return

        if success:
            self.update_all()
        else:
            message_box.warning(self, "Error", f"Deletion failed in {table_name}")
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
        # Handle Enter key when habit Add button is focused
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            focused_widget = QApplication.focusWidget()
            if focused_widget == self.pushButton_habit_add_new:
                self.pushButton_habit_add_new.click()
                return

        if self._handle_ctrl_c_for_tables(
            event,
            [
                self.tableView_habits,
                self.tableView_process_habits,
            ],
        ):
            return

        super().keyPressEvent(event)
```

</details>

### ⚙️ Method `load_process_habits_table`

```python
def load_process_habits_table(self) -> None
```

Load process habits table as pivot table (dates as rows, habits as columns).

Args:

- `ignore_filter` (`bool`): If `True`, ignore habit filter and load all records. Defaults to `False`.

<details>
<summary>Code:</summary>

```python
def load_process_habits_table(self, *, ignore_filter: bool = False) -> None:
        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        min_habit_row_columns = 2
        min_process_habit_row_columns = 4

        # Get habits (columns), optionally including archived ones
        habits_data = self.db_manager.get_habits(include_archived=self.show_archived_habits)
        habits = []  # List of (habit_id, habit_name, is_bool) tuples
        habit_id_to_index = {}  # Map habit_id to column index
        is_bool_column_index = 2

        for idx, row in enumerate(habits_data):
            if len(row) >= min_habit_row_columns:
                habit_id = row[0]
                habit_name = row[1] or ""
                is_bool = len(row) > is_bool_column_index and row[is_bool_column_index] == 1
                habits.append((habit_id, habit_name, is_bool))
                habit_id_to_index[habit_id] = idx

        # Apply filters if set (unless ignore_filter is True)
        if ignore_filter:
            habit_filter = ""
            use_date_filter = False
            date_from = None
            date_to = None
        else:
            try:
                habit_filter = self._get_selected_habit_filter()
                use_date_filter = False  # Date filter checkbox removed
                date_from = None
                date_to = None
            except AttributeError:
                # Filters not available yet
                habit_filter = ""
                use_date_filter = False
                date_from = None
                date_to = None

        # Always load all process habits records to show all columns
        # Filter will be applied to rows (dates) only, not to columns
        if use_date_filter:
            # Only apply date filter if explicitly set
            process_habits_rows = self.db_manager.get_filtered_process_habits_records(
                habit_name=None,  # Don't filter by habit - show all columns
                date_from=date_from,
                date_to=date_to,
            )
        elif self.show_all_records:
            process_habits_rows = self.db_manager.get_all_process_habits_records()
        else:
            process_habits_rows = self.db_manager.get_limited_process_habits_records(self.count_records_to_show)

        min_process_habits_name_columns = 2

        # When archived habits are hidden, also drop rows related to archived habits
        if not self.show_archived_habits:
            allowed_names = {name for _id, name, _is_bool in habits}
            process_habits_rows = [
                r for r in process_habits_rows if len(r) >= min_process_habits_name_columns and r[1] in allowed_names
            ]

        # Create a dictionary: date -> {habit_id: (record_id, value)}
        date_data = {}  # date -> {habit_id: (record_id, value)}
        unique_dates = set()
        filtered_dates = set()  # Dates that match the habit filter (if any)

        for row in process_habits_rows:
            if len(row) < min_process_habit_row_columns:
                continue
            record_id = row[0]
            habit_name = row[1]
            value = row[2]
            date_str = row[3]

            # Find habit_id by name
            habit_id = None
            for h_id, h_name, _is_bool in habits:
                if h_name == habit_name:
                    habit_id = h_id
                    break

            if habit_id is None:
                continue

            unique_dates.add(date_str)
            if date_str not in date_data:
                date_data[date_str] = {}
            date_data[date_str][habit_id] = (record_id, value)

            # If habit filter is set, track dates that have data for the filtered habit
            if habit_filter and habit_name == habit_filter:
                filtered_dates.add(date_str)

        # Apply habit filter to dates (rows) only - show all columns but filter rows
        if habit_filter and filtered_dates:
            # Only show dates that have data for the filtered habit
            sorted_dates = sorted(filtered_dates, reverse=True)
        else:
            # Show all dates
            sorted_dates = sorted(unique_dates, reverse=True)

        # Add empty rows for dates between last record and today (if no date filter is applied and no habit filter)
        # When habit filter is applied, we only show dates with data for that habit, so don't add empty dates
        if not use_date_filter and not habit_filter and sorted_dates:
            # Get the most recent date (first in sorted_dates as it's sorted descending)
            last_date_str = sorted_dates[0]
            try:
                last_date = QDate.fromString(last_date_str, "yyyy-MM-dd")
                today = QDate.currentDate()

                # Add dates from last_date + 1 day to today (inclusive)
                if last_date < today:
                    current_date = last_date.addDays(1)
                    missing_dates = []
                    while current_date <= today:
                        date_str = current_date.toString("yyyy-MM-dd")
                        if date_str not in unique_dates:
                            missing_dates.append(date_str)
                        current_date = current_date.addDays(1)

                    # Add missing dates to sorted_dates (maintain descending order)
                    if missing_dates:
                        # Sort missing dates descending and prepend to sorted_dates
                        missing_dates.sort(reverse=True)
                        sorted_dates = missing_dates + sorted_dates
            except Exception as e:
                print(f"Error adding missing dates: {e}")

        # Assign colors to dates
        date_to_color = {}
        for idx, date_str in enumerate(sorted_dates):
            color_index = idx % len(self.exercise_colors)
            date_to_color[date_str] = self.exercise_colors[color_index]

        # Create headers: Date + all habit names
        headers = ["Date"] + [h_name for _, h_name, _is_bool in habits]

        # Create model
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(headers)

        # Fill model with data
        for row_idx, date_str in enumerate(sorted_dates):
            row_color = date_to_color.get(date_str, QColor(255, 255, 255))

            # Date column (not editable)
            date_item = QStandardItem(date_str)
            date_item.setBackground(QBrush(row_color))
            date_item.setEditable(False)
            model.setItem(row_idx, 0, date_item)

            # Habit columns
            for col_idx, (habit_id, _habit_name, is_bool_habit) in enumerate(habits, start=1):
                record_id, value = date_data.get(date_str, {}).get(habit_id, (None, None))

                # Create item with value or empty
                item = QStandardItem(str(value)) if value is not None else QStandardItem("")

                item.setBackground(QBrush(row_color))
                item.setEditable(not is_bool_habit)

                # Store record_id and habit_id in UserRole for auto-save
                # Format: (record_id, habit_id, date_str) or None if no record exists
                if record_id is not None:
                    item.setData((record_id, habit_id, date_str), Qt.ItemDataRole.UserRole)
                else:
                    item.setData((None, habit_id, date_str), Qt.ItemDataRole.UserRole)

                model.setItem(row_idx, col_idx, item)

        # Create proxy model for sorting/filtering
        proxy = QSortFilterProxyModel()
        proxy.setSourceModel(model)

        self.models["process_habits"] = proxy
        self.tableView_process_habits.setModel(proxy)
        # Reconnect auto-save signal after model is created
        self._connect_table_auto_save_signal("process_habits")

        # Recreate per-column delegates each load (detach old viewport hooks first)
        self._cleanup_process_habit_delegates()
        self._process_habit_bool_delegate = ProcessHabitBoolDelegate(self.tableView_process_habits)
        self._process_habit_int_delegate = ProcessHabitIntDelegate(self.tableView_process_habits)
        self._process_habits_bool_columns = set()
        self._process_habits_int_columns = set()
        for col_idx, (_habit_id, _habit_name, is_bool_habit) in enumerate(habits, start=1):
            if is_bool_habit:
                self._process_habits_bool_columns.add(col_idx)
                self.tableView_process_habits.setItemDelegateForColumn(col_idx, self._process_habit_bool_delegate)
            else:
                self._process_habits_int_columns.add(col_idx)
                self.tableView_process_habits.setItemDelegateForColumn(col_idx, self._process_habit_int_delegate)

        # Make table editable
        self.tableView_process_habits.setEditTriggers(
            QAbstractItemView.EditTrigger.DoubleClicked | QAbstractItemView.EditTrigger.SelectedClicked
        )

        # Configure header (habit value columns need room for hover picker UI)
        _min_habit_value_column_width = 86
        process_habits_header = self.tableView_process_habits.horizontalHeader()
        process_habits_header.setMinimumSectionSize(_min_habit_value_column_width)
        for i in range(process_habits_header.count()):
            process_habits_header.setSectionResizeMode(i, process_habits_header.ResizeMode.Interactive)
        self.tableView_process_habits.resizeColumnsToContents()
        for col_idx in self._process_habits_bool_columns | self._process_habits_int_columns:
            if process_habits_header.sectionSize(col_idx) < _min_habit_value_column_width:
                process_habits_header.resizeSection(col_idx, _min_habit_value_column_width)
```

</details>

### ⚙️ Method `on_add_habit`

```python
def on_add_habit(self) -> None
```

Insert a new habit using database manager.

<details>
<summary>Code:</summary>

```python
def on_add_habit(self) -> None:
        habit_name = self.lineEdit_habit_name.text().strip()
        is_bool = self.checkBox_habit_is_bool.isChecked() or None

        if not habit_name:
            message_box.warning(self, "Error", "Enter habit name")
            return

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            if self.db_manager.add_habit(habit_name, is_bool=is_bool):
                self.update_all()
                self.lineEdit_habit_name.clear()
                self.checkBox_habit_is_bool.setChecked(False)
            else:
                message_box.warning(self, "Error", "Failed to add habit")
        except Exception as e:
            message_box.warning(self, "Database Error", f"Failed to add habit: {e}")
```

</details>

### ⚙️ Method `on_export_habits_csv`

```python
def on_export_habits_csv(self) -> None
```

Export process habits table to CSV file.

<details>
<summary>Code:</summary>

```python
def on_export_habits_csv(self) -> None:
        if self.models.get("process_habits") is None:
            message_box.warning(self, "Error", "No data to export")
            return

        filename, _ = QFileDialog.getSaveFileName(self, "Export Habits to CSV", "", "CSV Files (*.csv);;All Files (*)")
        if not filename:
            return

        try:
            model = cast("QSortFilterProxyModel", self.models["process_habits"])
            with Path(filename).open("w", encoding="utf-8") as f:
                # Write headers
                headers = self.table_config["process_habits"][2]
                f.write(",".join(headers) + "\n")

                # Write data
                for row in range(model.rowCount()):
                    row_data = []
                    for col in range(model.columnCount()):
                        index = model.index(row, col)
                        value = model.data(index)
                        row_data.append(str(value) if value is not None else "")
                    f.write(",".join(row_data) + "\n")

            message_box.information(self, "Success", f"Exported to {filename}")
        except Exception as e:
            message_box.warning(self, "Error", f"Failed to export: {e}")
```

</details>

### ⚙️ Method `on_habit_filter_clicked`

```python
def on_habit_filter_clicked(self, index: QModelIndex) -> None
```

Handle habit filter list view click or activation.

Args:

- `index` (`QModelIndex`): Clicked/activated index.

<details>
<summary>Code:</summary>

```python
def on_habit_filter_clicked(self, index: QModelIndex) -> None:
        if index.isValid() and self.habits_filter_list_model:
            item = self.habits_filter_list_model.itemFromIndex(index)
            habit_name = (item.data(Qt.ItemDataRole.UserRole) if item is not None else None) or (
                self.habits_filter_list_model.data(index) or ""
            )
            if habit_name and habit_name.strip():
                # Get selected year from list view
                selected_text = self._get_selected_habit_year()
                year = None
                if selected_text != "Last 365 days":
                    try:
                        year = int(selected_text)
                    except ValueError:
                        year = None
                # Apply filter to process_habits table
                self.load_process_habits_table(ignore_filter=False)
                # Directly update heatmap - this is the most reliable way
                self.update_habit_calendar_heatmap(habit_name, year=year)
```

</details>

### ⚙️ Method `on_habit_filter_selection_changed`

```python
def on_habit_filter_selection_changed(self, current: QModelIndex, _previous: QModelIndex) -> None
```

Handle habit filter list view selection change.

Args:

- `current` (`QModelIndex`): Current selected index.
- `_previous` (`QModelIndex`): Previous selected index.

<details>
<summary>Code:</summary>

```python
def on_habit_filter_selection_changed(self, current: QModelIndex, _previous: QModelIndex) -> None:
        if current.isValid() and self.habits_filter_list_model:
            item = self.habits_filter_list_model.itemFromIndex(current)
            habit_name = (item.data(Qt.ItemDataRole.UserRole) if item is not None else None) or (
                self.habits_filter_list_model.data(current) or ""
            )
            if habit_name and habit_name.strip():
                # Get selected year from list view
                selected_text = self._get_selected_habit_year()
                year = None
                if selected_text != "Last 365 days":
                    try:
                        year = int(selected_text)
                    except ValueError:
                        year = None
                # Apply filter to process_habits table
                self.load_process_habits_table(ignore_filter=False)
                # Update heatmap with selected habit
                self.update_habit_calendar_heatmap(habit_name, year=year)
```

</details>

### ⚙️ Method `on_habit_filter_selection_changed_slot`

```python
def on_habit_filter_selection_changed_slot(self, selected: QItemSelection, _deselected: QItemSelection) -> None
```

Handle habit filter list view selection changed signal.

Args:

- `selected` (`QItemSelection`): Selected items.
- `_deselected` (`QItemSelection`): Deselected items.

<details>
<summary>Code:</summary>

```python
def on_habit_filter_selection_changed_slot(self, selected: QItemSelection, _deselected: QItemSelection) -> None:
        indexes = selected.indexes()
        if indexes and self.habits_filter_list_model:
            index = indexes[0]
            if index.isValid():
                item = self.habits_filter_list_model.itemFromIndex(index)
                habit_name = (item.data(Qt.ItemDataRole.UserRole) if item is not None else None) or (
                    self.habits_filter_list_model.data(index) or ""
                )
                if habit_name and habit_name.strip():
                    # Get selected year from list view
                    selected_text = self._get_selected_habit_year()
                    year = None
                    if selected_text != "Last 365 days":
                        try:
                            year = int(selected_text)
                        except ValueError:
                            year = None
                    # Apply filter to process_habits table
                    self.load_process_habits_table(ignore_filter=False)
                    # Update heatmap with selected habit
                    self.update_habit_calendar_heatmap(habit_name, year=year)
```

</details>

### ⚙️ Method `on_habit_selection_changed`

```python
def on_habit_selection_changed(self, current: QModelIndex, _previous: QModelIndex) -> None
```

Handle habit table selection change.

Args:

- `current` (`QModelIndex`): Current selection index.
- `_previous` (`QModelIndex`): Previous selection index.

<details>
<summary>Code:</summary>

```python
def on_habit_selection_changed(self, current: QModelIndex, _previous: QModelIndex) -> None:
        if current.isValid():
            self.update_habit_calendar_heatmap()
```

</details>

### ⚙️ Method `on_habit_year_changed`

```python
def on_habit_year_changed(self, index: QModelIndex) -> None
```

Handle habit year list view change.

Args:

- `index` (`QModelIndex`): Selected index.

<details>
<summary>Code:</summary>

```python
def on_habit_year_changed(self, index: QModelIndex) -> None:
        if self.db_manager is None:
            return

        if not index.isValid():
            return

        selected_text = self._get_selected_habit_year()
        habit_name = self._get_selected_habit_filter()

        if not habit_name:
            return

        # Parse year from selection
        year = None
        if selected_text != "Last 365 days":
            try:
                year = int(selected_text)
            except ValueError:
                year = None

        # Apply filter to process_habits table
        self.load_process_habits_table(ignore_filter=False)
        # Update heatmap with selected year
        self.update_habit_calendar_heatmap(habit_name, year=year)
```

</details>

### ⚙️ Method `on_habit_year_selection_changed`

```python
def on_habit_year_selection_changed(self, current: QModelIndex, _previous: QModelIndex) -> None
```

Handle habit year list view selection change.

Args:

- `current` (`QModelIndex`): Current selected index.
- `_previous` (`QModelIndex`): Previous selected index.

<details>
<summary>Code:</summary>

```python
def on_habit_year_selection_changed(self, current: QModelIndex, _previous: QModelIndex) -> None:
        if current.isValid():
            self.on_habit_year_changed(current)
```

</details>

### ⚙️ Method `on_toggle_show_all_habits_records`

```python
def on_toggle_show_all_habits_records(self) -> None
```

Toggle between showing all habits records and limited records.

<details>
<summary>Code:</summary>

```python
def on_toggle_show_all_habits_records(self) -> None:
        # This will be handled in load_process_habits_table
        self.show_tables()
```

</details>

### ⚙️ Method `refresh_habits_and_process_habits`

```python
def refresh_habits_and_process_habits(self) -> None
```

Refresh habits table and process_habits table (ignoring filter for process_habits).

<details>
<summary>Code:</summary>

```python
def refresh_habits_and_process_habits(self) -> None:
        if self._is_closing:
            return
        if not self._validate_database_connection():
            print("Database connection not available for refresh_habits_and_process_habits")
            return

        # Refresh habits table using update_all logic
        try:
            if not self.db_manager.table_exists("habits"):
                print("⚠️ Table 'habits' does not exist in database")
                self._set_habits_table_model(self._create_colored_table_model([], self.table_config["habits"][2]))
            else:
                habits_data = self.db_manager.get_all_habits()
                habits_transformed_data = []
                light_blue = QColor(240, 248, 255)  # Light blue background

                # Minimum habit row length: habit_id (index 0) + habit_name (index 1)
                min_habit_row_length = 2
                for row in habits_data:
                    try:
                        if len(row) < min_habit_row_length:
                            continue
                        is_bool_value = row[2] if len(row) > min_habit_row_length else None
                        is_bool_str = "Yes" if is_bool_value == 1 else ("No" if is_bool_value == 0 else "")
                        archived_idx = 3
                        is_archived_value = row[archived_idx] if len(row) > archived_idx else 0
                        is_archived_str = "Yes" if is_archived_value == 1 else "No"
                        habit_name = row[1] or ""
                        habit_id = row[0] if row[0] is not None else 0
                        transformed_row = [habit_name, is_bool_str, is_archived_str, habit_id, light_blue]
                        habits_transformed_data.append(transformed_row)
                    except Exception as e:
                        print(f"Error processing habit row: {e}")
                        continue
                self._set_habits_table_model(
                    self._create_colored_table_model(habits_transformed_data, self.table_config["habits"][2])
                )
        except Exception as habits_error:
            print(f"Error refreshing habits table: {habits_error}")

        # Refresh process_habits table without filter
        self.refresh_process_habits_table()
        self.update_habits_filter_combobox()
```

</details>

### ⚙️ Method `refresh_process_habits_table`

```python
def refresh_process_habits_table(self) -> None
```

Refresh process habits table ignoring any filters.

<details>
<summary>Code:</summary>

```python
def refresh_process_habits_table(self) -> None:
        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        # Load table without filter
        self.load_process_habits_table(ignore_filter=True)
```

</details>

### ⚙️ Method `resizeEvent`

```python
def resizeEvent(self, event: QResizeEvent) -> None
```

Handle window resize event and adjust table column widths proportionally.

Args:

- `event` (`QResizeEvent`): The resize event.

<details>
<summary>Code:</summary>

```python
def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        # Call parent resize event first
        super().resizeEvent(event)

        self._update_layout_for_window_size()
```

</details>

### ⚙️ Method `show_tables`

```python
def show_tables(self) -> None
```

Populate habits and process_habits QTableViews using database manager.

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
            # Refresh habits table
            if not self.db_manager.table_exists("habits"):
                print("⚠️ Table 'habits' does not exist in database")
                self._set_habits_table_model(self._create_colored_table_model([], self.table_config["habits"][2]))
            else:
                habits_data = self.db_manager.get_all_habits()
                habits_transformed_data = []
                light_blue = QColor(240, 248, 255)  # Light blue background
                min_habit_row_length = 2
                for row in habits_data:
                    try:
                        if len(row) < min_habit_row_length:
                            continue
                        is_bool_value = row[2] if len(row) > min_habit_row_length else None
                        is_bool_str = "Yes" if is_bool_value == 1 else ("No" if is_bool_value == 0 else "")
                        archived_idx = 3
                        is_archived_value = row[archived_idx] if len(row) > archived_idx else 0
                        is_archived_str = "Yes" if is_archived_value == 1 else "No"
                        habit_name = row[1] or ""
                        habit_id = row[0] if row[0] is not None else 0
                        transformed_row = [
                            habit_name,
                            is_bool_str,
                            is_archived_str,
                            habit_id,
                            light_blue,
                        ]
                        habits_transformed_data.append(transformed_row)
                    except Exception as e:
                        print(f"Error processing habit row: {e}")
                        continue
                self._set_habits_table_model(
                    self._create_colored_table_model(habits_transformed_data, self.table_config["habits"][2])
                )

            # Load process habits table data
            if self.db_manager.table_exists("process_habits"):
                self.load_process_habits_table(ignore_filter=True)
                selected_habit = self._get_selected_habit_from_table()
                if selected_habit:
                    self.update_habit_calendar_heatmap(selected_habit)
            else:
                print("⚠️ Table 'process_habits' does not exist in database")
                self.models["process_habits"] = self._create_colored_table_model(
                    [], self.table_config["process_habits"][2]
                )
                self.tableView_process_habits.setModel(self.models["process_habits"])
                self._connect_table_auto_save_signal("process_habits")

            # Connect selection change signals for habits table
            self._connect_table_signals("habits", self.on_habit_selection_changed)
            # Connect auto-save signals after all models are created
            self._connect_table_auto_save_signals()

        except Exception as e:
            print(f"Error showing tables: {e}")
            message_box.warning(self, "Database Error", f"Failed to load tables: {e}")
```

</details>

### ⚙️ Method `update_all`

```python
def update_all(self) -> None
```

Refresh habits and process_habits tables and filter list views.

<details>
<summary>Code:</summary>

```python
def update_all(
        self,
    ) -> None:
        if not self._validate_database_connection():
            print("Database connection not available for update_all")
            return

        self.show_all_records = False
        self.pushButton_habits_show_all_records.setText("📋 Show All Records")

        self.show_tables()
        self.update_habits_filter_combobox()
        self.update_habits_year_combobox()
```

</details>

### ⚙️ Method `update_habit_calendar_heatmap`

```python
def update_habit_calendar_heatmap(self, habit_name: str | None = None, year: int | None = None) -> None
```

Update the habit calendar heatmap using database manager.

Args:

- `habit_name` (`str | None`): Name of the habit to display. If `None`, uses selected habit from

`listView_filter_habit`.

- `year` (`int | None`): Year to display. If `None`, shows last 365 days.

<details>
<summary>Code:</summary>

```python
def update_habit_calendar_heatmap(self, habit_name: str | None = None, year: int | None = None) -> None:
        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        # Get habit name from parameter or from list view selection
        if habit_name is None:
            habit_name = self._get_selected_habit_filter()
            if not habit_name:
                self._show_habit_heatmap_message("Please select a habit")
                return

        # Calculate date range based on year parameter
        today = datetime.now(UTC).astimezone().date()
        if year is not None:
            # Specific year: from January 1 to December 31 of that year
            start_date = datetime(year, 1, 1, tzinfo=UTC).astimezone().date()
            end_date = datetime(year, 12, 31, tzinfo=UTC).astimezone().date()
            # If year is current year, limit to today
            if year == today.year:
                end_date = today
        else:
            # Last 365 days (default)
            start_date = today - timedelta(days=365)
            end_date = today

        # Get data for the specified date range
        rows = self.db_manager.get_habit_calendar_data(
            habit_name,
            date_from=start_date.strftime("%Y-%m-%d"),
            date_to=end_date.strftime("%Y-%m-%d"),
        )
        if not rows:
            period_text = f"year {year}" if year is not None else "last 365 days"
            self._show_habit_heatmap_message(f"No data found for habit '{habit_name}' for {period_text}")
            return

        # Convert to pandas DataFrame
        dates = [datetime.fromisoformat(row[0]).date() for row in rows]
        values = [row[1] for row in rows]
        df = pd.DataFrame({"dates": dates, "values": values})

        # start_date and end_date are already calculated above

        figure = Figure(figsize=(15, 6), dpi=100)
        ax = figure.add_subplot(111)

        # Create calendar heatmap using dayplot
        try:
            # --- Color/legend rules for habits ---
            # Requirements:
            # - 0 is ALWAYS gray
            # - if is_bool=1 and only {0,1} are present: 1 is dark green
            # - otherwise: positives are green shades, negatives are red shades
            # - legend must contain exactly the values that appear on the plot
            #
            # dayplot switches to a diverging scale when negatives exist and then ignores
            # `color_for_none`, so we map real values -> non-negative indices to keep the
            # "0 gray" behavior stable, and draw a custom legend.

            def _lerp(
                a: tuple[float, float, float],
                b: tuple[float, float, float],
                t: float,
            ) -> tuple[float, float, float]:
                return (
                    a[0] + (b[0] - a[0]) * t,
                    a[1] + (b[1] - a[1]) * t,
                    a[2] + (b[2] - a[2]) * t,
                )

            def _gradient(
                a: tuple[float, float, float],
                b: tuple[float, float, float],
                n: int,
            ) -> list[tuple[float, float, float]]:
                if n <= 0:
                    return []
                if n == 1:
                    return [a]
                return [_lerp(a, b, i / (n - 1)) for i in range(n)]

            # Aggregate per-date like dayplot does (sum), then collect actual displayed values.
            df_agg = df.groupby("dates", as_index=False)["values"].sum()
            display_values_set = {int(v) for v in df_agg["values"].tolist()}
            display_values_set.add(0)  # missing days are displayed as 0

            # Fetch is_bool flag for this habit
            is_bool_flag: bool | None = None
            try:
                rows_is_bool = self.db_manager.get_rows(
                    "SELECT is_bool FROM habits WHERE name = :name LIMIT 1",
                    {"name": habit_name},
                )
                if rows_is_bool and rows_is_bool[0]:
                    raw_is_bool = rows_is_bool[0][0]
                    if raw_is_bool in (0, 1):
                        is_bool_flag = bool(raw_is_bool)
            except Exception:
                is_bool_flag = None

            is_bool_case = is_bool_flag is True and display_values_set.issubset({0, 1})

            # Base colors
            gray = "#e9e9e9"
            dark_green = "#006400"
            light_green = "#b7e4b7"
            dark_red = "#8b0000"
            light_red = "#f3b0b0"
            # Special color for maximum value in non-binary habits
            max_value_color = "#3141DA"  # Very dark green to highlight maximum

            # Map real value -> non-negative index, ensuring real 0 maps to 0 (for gray).
            value_to_mapped: dict[int, int] = {0: 0}

            if is_bool_case:
                value_to_mapped[1] = 1
                mapped_vmax = 1
                colors = [to_rgb(gray), to_rgb(dark_green)]
                cmap = LinearSegmentedColormap.from_list("habits_bool_map", colors, N=len(colors))
                legend_order = [0, 1]
            else:
                neg_values = sorted([v for v in display_values_set if v < 0])
                pos_values = sorted([v for v in display_values_set if v > 0])

                # Find maximum value (could be positive or negative)
                max_value = max(display_values_set) if display_values_set else 0

                # Check if values are binary (only 0 and 1) - if not, highlight maximum
                is_binary_values = display_values_set.issubset({0, 1})
                should_highlight_max = not is_binary_values and max_value != 0

                idx = 1
                for v in neg_values:
                    value_to_mapped[v] = idx
                    idx += 1
                for v in pos_values:
                    value_to_mapped[v] = idx
                    idx += 1

                mapped_vmax = max(idx - 1, 0)

                # Build discrete palette: [0]=gray (unused by cmap for 0), then reds, then greens.
                colors_list: list[tuple[float, float, float]] = [to_rgb(gray)]

                # Handle negative values
                if neg_values:
                    if should_highlight_max and max_value < 0:
                        # Maximum is negative and should be highlighted
                        non_max_neg = [v for v in neg_values if v != max_value]
                        if non_max_neg:
                            # Gradient for non-maximum negative values
                            colors_list.extend(_gradient(to_rgb(dark_red), to_rgb(light_red), len(non_max_neg)))
                        # Add very dark red for maximum negative value
                        colors_list.append(to_rgb("#5b0000"))  # Very dark red
                    else:
                        # Normal gradient for all negative values
                        colors_list.extend(_gradient(to_rgb(dark_red), to_rgb(light_red), len(neg_values)))

                # Handle positive values
                if pos_values:
                    if should_highlight_max and max_value > 0:
                        # Maximum value should be highlighted - put it at the end
                        non_max_pos = [v for v in pos_values if v != max_value]
                        if non_max_pos:
                            # Gradient for non-maximum positive values
                            colors_list.extend(_gradient(to_rgb(light_green), to_rgb(dark_green), len(non_max_pos)))
                        # Add special very dark green color for maximum value at the end
                        colors_list.append(to_rgb(max_value_color))
                    else:
                        # Normal gradient for all positive values
                        colors_list.extend(_gradient(to_rgb(light_green), to_rgb(dark_green), len(pos_values)))

                # dayplot requires a LinearSegmentedColormap; ensure at least 2 colors.
                if len(colors_list) == 1:
                    colors_list.append(to_rgb(gray))

                cmap = LinearSegmentedColormap.from_list(
                    "habits_signed_map",
                    colors_list,
                    N=len(colors_list),
                )
                legend_order = [*neg_values, 0, *pos_values]

            df_mapped = df.copy()
            df_mapped["values_mapped"] = [value_to_mapped.get(int(v), 0) for v in df_mapped["values"].tolist()]

            dp.calendar(
                dates=df_mapped["dates"].tolist(),
                values=df_mapped["values_mapped"],
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d"),
                legend=False,  # custom legend below
                color_for_none=gray,
                vmin=0,
                vmax=max(mapped_vmax, 1),
                cmap=cmap,
                boxstyle="round",
                ax=ax,
            )

            # Custom legend: exactly the displayed values
            norm = Normalize(vmin=0, vmax=max(mapped_vmax, 1))
            handles: list[Patch] = []
            for v in legend_order:
                if v == 0:
                    color = gray
                else:
                    mapped = value_to_mapped.get(v, 0)
                    color = cmap(norm(mapped))
                handles.append(Patch(facecolor=color, edgecolor="none", label=str(v)))

            ax.legend(
                handles=handles,
                title="Value",
                loc="upper center",
                bbox_to_anchor=(0.5, -0.10),
                ncol=min(len(handles), 10),
                frameon=False,
                fontsize=8,
                title_fontsize=8,
            )
            # Set smaller font size for title
            period_label = str(year) if year is not None else "Last 365 days"
            ax.set_title(f"Calendar Heatmap: {habit_name} ({period_label})", fontsize=10, fontweight="bold")
            # Reduce font size for all text elements (axes labels and ticks)
            ax.tick_params(labelsize=8)
            if ax.xaxis.label:
                ax.xaxis.label.set_fontsize(8)
            if ax.yaxis.label:
                ax.yaxis.label.set_fontsize(8)
            # Reduce font size for all text elements in the plot
            for text in ax.texts:
                text.set_fontsize(8)
            figure.tight_layout(rect=(0, 0.06, 1, 1))
        except Exception as e:
            print(f"Error creating calendar heatmap: {e}")
            self._show_habit_heatmap_message(f"Error creating calendar heatmap: {e}")
            return

        self._display_habit_heatmap_figure(figure)
```

</details>

### ⚙️ Method `update_habits_filter_combobox`

```python
def update_habits_filter_combobox(self) -> None
```

Refresh habit filter list view in the filter group.

<details>
<summary>Code:</summary>

```python
def update_habits_filter_combobox(self) -> None:
        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            # Check if table exists
            if not self.db_manager.table_exists("habits"):
                print("⚠️ Table 'habits' does not exist, skipping filter list view update")
                if self.habits_filter_list_model:
                    self.habits_filter_list_model.clear()
                return

            current_habit = self._get_selected_habit_filter()

            if not self.habits_filter_list_model:
                self.habits_filter_list_model = QStandardItemModel()
                self.listView_filter_habit.setModel(self.habits_filter_list_model)
                # Reconnect signals after setting new model
                selection_model = self.listView_filter_habit.selectionModel()
                if selection_model:
                    # Disconnect first to avoid duplicates
                    with contextlib.suppress(TypeError):
                        selection_model.currentChanged.disconnect()
                        selection_model.selectionChanged.disconnect()
                    selection_model.currentChanged.connect(self.on_habit_filter_selection_changed)
                    selection_model.selectionChanged.connect(self.on_habit_filter_selection_changed_slot)
                # Disconnect signals first to avoid duplicates
                with contextlib.suppress(TypeError, RuntimeError), warnings.catch_warnings():
                    warnings.simplefilter("ignore", RuntimeWarning)
                    self.listView_filter_habit.clicked.disconnect()
                with contextlib.suppress(TypeError, RuntimeError), warnings.catch_warnings():
                    warnings.simplefilter("ignore", RuntimeWarning)
                    self.listView_filter_habit.activated.disconnect()
                self.listView_filter_habit.clicked.connect(self.on_habit_filter_clicked)
                self.listView_filter_habit.activated.connect(self.on_habit_filter_clicked)

            selection_model = self.listView_filter_habit.selectionModel()
            if selection_model:
                selection_model.blockSignals(True)  # noqa: FBT003

            self.habits_filter_list_model.clear()

            habits_data = self.db_manager.get_habits(include_archived=self.show_archived_habits)
            for row in habits_data:
                min_habit_filter_columns = 2
                archived_idx = 3
                if len(row) < min_habit_filter_columns:
                    continue
                habit_id = row[0]
                habit_name = row[1] or ""
                if not str(habit_name).strip():
                    continue
                is_archived = (
                    bool(row[archived_idx]) if len(row) > archived_idx and row[archived_idx] in (0, 1) else False
                )

                display = f"{habit_name} (archived)" if (is_archived and self.show_archived_habits) else str(habit_name)
                item = QStandardItem(display)
                # Store raw name/id/archived in user roles (display text can change).
                item.setData(str(habit_name), Qt.ItemDataRole.UserRole)
                item.setData(int(habit_id) if habit_id is not None else None, Qt.ItemDataRole.UserRole + 1)
                item.setData(is_archived, Qt.ItemDataRole.UserRole + 2)
                self.habits_filter_list_model.appendRow(item)

            # Restore previous selection if it exists, otherwise select first habit
            selected_index = None
            if current_habit:
                for row in range(self.habits_filter_list_model.rowCount()):
                    item = self.habits_filter_list_model.item(row)
                    if item and (item.data(Qt.ItemDataRole.UserRole) or item.text()) == current_habit:
                        selected_index = self.habits_filter_list_model.index(row, 0)
                        break

            # If no previous selection, select first habit (index 0)
            if selected_index is None and self.habits_filter_list_model.rowCount() > 0:
                selected_index = self.habits_filter_list_model.index(0, 0)  # First habit

            # If we need to select first habit (no previous selection), do it before unblocking signals
            if selected_index is not None:
                if selection_model:
                    selection_model.setCurrentIndex(selected_index, selection_model.SelectionFlag.ClearAndSelect)
                else:
                    self.listView_filter_habit.setCurrentIndex(selected_index)

                # Trigger the update manually while signals are blocked to avoid double call
                if selected_index.isValid():
                    selected_habit = self.habits_filter_list_model.data(selected_index) or ""
                    if selected_habit and selected_habit.strip():
                        # Get selected year from list view
                        selected_text = self._get_selected_habit_year()
                        year = None
                        if selected_text != "Last 365 days":
                            try:
                                year = int(selected_text)
                            except ValueError:
                                year = None
                        # Manually trigger the selection change handler to build the graph
                        self.update_habit_calendar_heatmap(selected_habit, year=year)

            if selection_model:
                selection_model.blockSignals(False)  # noqa: FBT003

        except Exception as e:
            print(f"Error updating habits filter list view: {e}")
```

</details>

### ⚙️ Method `update_habits_year_combobox`

```python
def update_habits_year_combobox(self) -> None
```

Refresh habit year list view with available years from process_habits table.

<details>
<summary>Code:</summary>

```python
def update_habits_year_combobox(self) -> None:
        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            # Check if table exists
            if not self.db_manager.table_exists("process_habits"):
                print("⚠️ Table 'process_habits' does not exist, skipping year list view update")
                if not self.habits_year_list_model:
                    self._init_habits_year_list()
                if self.habits_year_list_model:
                    self.habits_year_list_model.clear()
                    item = QStandardItem("Last 365 days")
                    self.habits_year_list_model.appendRow(item)
                return

            current_selection = self._get_selected_habit_year()

            # Initialize model if needed
            if not self.habits_year_list_model:
                self._init_habits_year_list()

            selection_model = self.listView_filter_habit_year.selectionModel()
            if selection_model:
                selection_model.blockSignals(True)  # noqa: FBT003

            if self.habits_year_list_model:
                self.habits_year_list_model.clear()

                # Add "Last 365 days" as first item
                item = QStandardItem("Last 365 days")
                self.habits_year_list_model.appendRow(item)

                # Get years from database
                years = self.db_manager.get_habits_years()
                for year in years:
                    item = QStandardItem(str(year))
                    self.habits_year_list_model.appendRow(item)

                # Restore previous selection or select "Last 365 days" by default
                if current_selection:
                    # Find index of current selection
                    found_index = None
                    for row in range(self.habits_year_list_model.rowCount()):
                        index = self.habits_year_list_model.index(row, 0)
                        if self.habits_year_list_model.data(index) == current_selection:
                            found_index = index
                            break
                    if found_index and found_index.isValid():
                        self.listView_filter_habit_year.setCurrentIndex(found_index)
                    else:
                        # Select first item ("Last 365 days")
                        first_index = self.habits_year_list_model.index(0, 0)
                        self.listView_filter_habit_year.setCurrentIndex(first_index)
                else:
                    # Select first item ("Last 365 days")
                    first_index = self.habits_year_list_model.index(0, 0)
                    self.listView_filter_habit_year.setCurrentIndex(first_index)

            if selection_model:
                selection_model.blockSignals(False)  # noqa: FBT003

        except Exception as e:
            print(f"Error updating habits year list view: {e}")
```

</details>
