"""Food tracker GUI.

This module contains a single `MainWindow` class that provides a Qt-based GUI for a
SQLite database with food items and food log records.
"""

from __future__ import annotations

import sys
from functools import partial
from pathlib import Path

import harrix_pylib as h
from PySide6.QtCore import QDate, QDateTime, QModelIndex, QSortFilterProxyModel, Qt
from PySide6.QtGui import QBrush, QCloseEvent, QColor, QKeyEvent, QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QApplication, QFileDialog, QMainWindow, QMessageBox, QTableView

from harrix_swiss_knife.food import database_manager, window
from harrix_swiss_knife.food.mixins import (
    AutoSaveOperations,
    ChartOperations,
    DateOperations,
    TableOperations,
    ValidationOperations,
    requires_database,
)

config = h.dev.load_config("config/config.json")


class MainWindow(
    QMainWindow,
    window.Ui_MainWindow,
    TableOperations,
    ChartOperations,
    DateOperations,
    AutoSaveOperations,
    ValidationOperations,
):
    """Main application window for the food tracking application.

    This class implements the main GUI window for the food tracker, providing
    functionality to record food items and track food consumption.
    It manages database operations for storing and retrieving food data.

    Attributes:

    - `_SAFE_TABLES` (`frozenset[str]`): Set of table names that can be safely modified,
      containing "food_log" and "food_items".

    - `db_manager` (`database_manager.DatabaseManager | None`): Database
      connection manager. Defaults to `None` until initialized.

    - `models` (`dict[str, QSortFilterProxyModel | None]`): Dictionary of table models keyed
      by table name. All values default to `None` until tables are loaded.

    - `table_config` (`dict[str, tuple[QTableView, str, list[str]]]`): Configuration for each
      table, mapping table names to tuples of (table view widget, model key, column headers).

    - `food_items_list_model` (`QStandardItemModel | None`): Model for the food items list view.
      Defaults to `None` until initialized.

    - `favorite_food_items_list_model` (`QStandardItemModel | None`): Model for the favorite food items list view.
      Defaults to `None` until initialized.

    """

    _SAFE_TABLES: frozenset[str] = frozenset(
        {"food_log"},
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

        # Food items list model
        self.food_items_list_model: QStandardItemModel | None = None

        # Favorite food items list model
        self.favorite_food_items_list_model: QStandardItemModel | None = None

        # Table models dictionary
        self.models: dict[str, QSortFilterProxyModel | None] = {
            "food_log": None,
        }

        # Table configuration mapping
        self.table_config: dict[str, tuple[QTableView, str, list[str]]] = {
            "food_log": (
                self.tableView_food_log,
                "food_log",
                ["Name", "Is Drink", "Weight", "Calories per 100g", "Portion Calories", "Date", "English Name"],
            ),
        }

        # Define colors for different dates (expanded palette)
        self.date_colors = self.generate_pastel_colors_mathematical(50)

        # Initialize application
        self._init_database()
        self._connect_signals()
        self._init_food_items_list()
        self._init_favorite_food_items_list()
        self.set_today_date()  # Set current date in dateEdit_food
        self.update_food_data()

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        """Handle application close event.

        Args:

        - `event` (`QCloseEvent`): The close event.

        """
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
            if table_name == "food_log":
                success = self.db_manager.delete_food_log_record(record_id)
        except Exception as e:
            QMessageBox.warning(self, "Database Error", f"Failed to delete record: {e}")
            return

        if success:
            self.update_food_data()
        else:
            QMessageBox.warning(self, "Error", f"Deletion failed in {table_name}")

    def generate_pastel_colors_mathematical(self, count: int = 100) -> list[QColor]:
        """Generate pastel colors using mathematical distribution.

        Args:

        - `count` (`int`): Number of colors to generate. Defaults to `100`.

        Returns:

        - `list[QColor]`: List of pastel QColor objects.

        """
        import colorsys
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
                self.tableView_food_log,
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
    def on_add_food_log(self) -> None:
        """Insert a new food log record using database manager."""
        # Get values from UI
        food_name = self.lineEdit_food_manual_name.text().strip()
        weight = self.doubleSpinBox_food_weight.value()
        calories = self.doubleSpinBox_food_calories.value()
        food_date = self.dateEdit_food.date().toString("yyyy-MM-dd")
        use_weight = self.radioButton_use_weight.isChecked()
        is_drink = self.checkBox_food_is_drink.isChecked()

        # Validate required fields
        if not food_name:
            QMessageBox.warning(self, "Error", "Enter food name")
            return

        if calories <= 0:
            QMessageBox.warning(self, "Error", "Calories must be greater than 0")
            return

        # Validate weight based on radio button selection
        if use_weight and weight <= 0:
            QMessageBox.warning(self, "Error", "Weight is required when using weight mode")
            return

        # Validate the date
        if not self._is_valid_date(food_date):
            QMessageBox.warning(self, "Error", "Invalid date format")
            return

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            # Determine calories_per_100g and portion_calories based on radio button
            calories_per_100g = calories if use_weight else None
            portion_calories = calories if not use_weight else None

            # Use database manager method
            if self.db_manager.add_food_log_record(
                date=food_date,
                calories_per_100g=calories_per_100g,
                name=food_name,
                weight=weight if weight > 0 else None,
                portion_calories=portion_calories,
                is_drink=is_drink
            ):
                # Apply date increment logic
                self._increment_date_widget(self.dateEdit_food)

                # Update UI - only food-related data
                self.update_food_data()
            else:
                QMessageBox.warning(self, "Error", "Failed to add food log record")

        except Exception as e:
            QMessageBox.warning(self, "Database Error", f"Failed to add food log record: {e}")

    @requires_database()
    def on_add_food_item(self) -> None:
        """Insert a new food item using database manager."""
        name = self.lineEdit_food_name.text().strip()
        name_en = self.lineEdit_food_name_en.text().strip()
        is_drink = self.checkBox_food_is_drink.isChecked()
        calories_per_100g = self.doubleSpinBox_food_cal100.value()
        default_portion_weight = self.doubleSpinBox_food_default_weight.value()
        default_portion_calories = self.doubleSpinBox_food_default_cal.value()

        if not name:
            QMessageBox.warning(self, "Error", "Enter food name")
            return

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            # Use database manager method
            if self.db_manager.add_food_item(
                name=name,
                name_en=name_en if name_en else None,
                is_drink=is_drink,
                calories_per_100g=calories_per_100g if calories_per_100g > 0 else None,
                default_portion_weight=default_portion_weight if default_portion_weight > 0 else None,
                default_portion_calories=default_portion_calories if default_portion_calories > 0 else None
            ):
                self.update_food_data()
                # Clear form
                self.lineEdit_food_name.clear()
                self.lineEdit_food_name_en.clear()
                self.checkBox_food_is_drink.setChecked(False)
                self.doubleSpinBox_food_cal100.setValue(0)
                self.doubleSpinBox_food_default_weight.setValue(0)
                self.doubleSpinBox_food_default_cal.setValue(0)
            else:
                QMessageBox.warning(self, "Error", "Failed to add food item")

        except Exception as e:
            QMessageBox.warning(self, "Database Error", f"Failed to add food item: {e}")

    def on_food_item_selection_changed(self, _current: QModelIndex, _previous: QModelIndex) -> None:
        """Handle food item selection change in the list view."""
        food_item = self._get_current_selected_food_item()
        if not food_item:
            return

        # Check if database manager is available and connection is open
        if not self._validate_database_connection():
            print("Database manager not available or connection not open")
            return

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            # Get food item data from database
            food_item_data = self.db_manager.get_food_item_by_name(food_item)
            if not food_item_data:
                return

            # food_item_data format: [_id, name, name_en, is_drink, calories_per_100g, default_portion_weight, default_portion_calories]
            food_id, name, name_en, is_drink, calories_per_100g, default_portion_weight, default_portion_calories = food_item_data

            # Update form fields with selected food item data
            # Fields for adding new food item
            self.lineEdit_food_name.setText(name)
            if name_en:
                self.lineEdit_food_name_en.setText(name_en)
            else:
                self.lineEdit_food_name_en.clear()

            if calories_per_100g:
                self.doubleSpinBox_food_cal100.setValue(calories_per_100g)
            else:
                self.doubleSpinBox_food_cal100.setValue(0)

            if default_portion_weight:
                self.doubleSpinBox_food_default_weight.setValue(default_portion_weight)
            else:
                self.doubleSpinBox_food_default_weight.setValue(0)

            if default_portion_calories:
                self.doubleSpinBox_food_default_cal.setValue(default_portion_calories)
            else:
                self.doubleSpinBox_food_default_cal.setValue(0)

            # Set drink checkboxes
            self.checkBox_food_is_drink.setChecked(is_drink == 1)
            self.checkBox_is_drink.setChecked(is_drink == 1)

            # Fields for adding food log record
            self.lineEdit_food_manual_name.setText(name)
            if default_portion_weight:
                self.doubleSpinBox_food_weight.setValue(default_portion_weight)
            else:
                self.doubleSpinBox_food_weight.setValue(0)

            if calories_per_100g:
                self.doubleSpinBox_food_calories.setValue(calories_per_100g)
            else:
                self.doubleSpinBox_food_calories.setValue(0)

            # Set drink checkbox for food log record
            self.checkBox_food_is_drink.setChecked(is_drink == 1)

            # Update calories calculation
            self.update_calories_calculation()

        except Exception as e:
            print(f"Error in food item selection changed: {e}")



    def set_today_date(self) -> None:
        """Set today's date in the food date edit field."""
        today_qdate = QDate.currentDate()
        self.dateEdit_food.setDate(today_qdate)

    def set_food_yesterday_date(self) -> None:
        """Set yesterday's date in the food date edit field.

        Sets the dateEdit_food widget to yesterday's date for convenient entry
        of food records from the previous day.
        """
        yesterday = QDate.currentDate().addDays(-1)
        self.dateEdit_food.setDate(yesterday)

    def show_tables(self) -> None:
        """Populate all QTableViews using database manager methods."""
        if not self._validate_database_connection():
            print("Database connection not available for showing tables")
            return

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            def transform_food_log_data(rows: list[list]) -> list[list]:
                """Refresh food_log table with data transformation and coloring.

                Args:

                - `rows` (`list[list]`): Raw food_log data from database.

                Returns:

                - `list[list]`: Transformed food_log data.

                """
                # Get all unique dates and assign colors
                unique_dates = list({row[1] for row in rows if row[1]})  # row[1] is date
                date_to_color = {}

                for idx, date_str in enumerate(sorted(unique_dates, reverse=True)):
                    color_index = idx % len(self.date_colors)
                    date_to_color[date_str] = self.date_colors[color_index]

                # Transform data and add color information
                transformed_rows = []
                for row in rows:
                    # Original transformation:
                    # [id, date, weight, portion_calories, calories_per_100g, name, name_en, is_drink] ->
                    # [name, is_drink, weight, calories_per_100g, portion_calories, date, name_en]

                    # Check if portion_calories is non-zero, then hide calories_per_100g if it's 0
                    portion_calories = row[3]
                    calories_per_100g = row[4]

                    # If portion_calories is non-zero and calories_per_100g is 0, show empty string for calories_per_100g
                    # But if portion_calories is 0 (like water), show the 0 for calories_per_100g
                    if portion_calories and portion_calories > 0 and (not calories_per_100g or calories_per_100g == 0):
                        calories_per_100g_display = ""
                    else:
                        calories_per_100g_display = calories_per_100g if calories_per_100g is not None else ""

                    transformed_row = [row[5], "1" if row[7] == 1 else "", row[2], calories_per_100g_display, portion_calories, row[1], row[6]]

                    # Add color information based on date
                    date_str = row[1]
                    date_color = date_to_color.get(date_str, QColor(255, 255, 255))  # White as fallback

                    # Add original ID and color to the row for later use
                    transformed_row.extend([row[0], date_color])  # [name, is_drink, weight, calories_per_100g, portion_calories, date, name_en, id, color]
                    transformed_rows.append(transformed_row)

                return transformed_rows

            # Get food_log data and transform it
            food_log_rows = self.db_manager.get_all_food_log_records()
            transformed_food_log_data = transform_food_log_data(food_log_rows)

            # Create food_log table model with coloring
            self.models["food_log"] = self._create_colored_food_log_table_model(
                transformed_food_log_data, self.table_config["food_log"][2]
            )
            self.tableView_food_log.setModel(self.models["food_log"])

            # Enable editing for the table
            self.tableView_food_log.setEditTriggers(QTableView.EditTrigger.DoubleClicked | QTableView.EditTrigger.EditKeyPressed)

            # Configure food_log table header - mixed approach: interactive + stretch last
            food_log_header = self.tableView_food_log.horizontalHeader()
            # Set first columns to interactive (resizable)
            for i in range(food_log_header.count() - 1):
                food_log_header.setSectionResizeMode(i, food_log_header.ResizeMode.Interactive)
            # Set last column to stretch to fill remaining space
            food_log_header.setSectionResizeMode(food_log_header.count() - 1, food_log_header.ResizeMode.Stretch)
            # Set default column widths for resizable columns
            self.tableView_food_log.setColumnWidth(0, 150)  # Name
            self.tableView_food_log.setColumnWidth(1, 80)   # Is Drink
            self.tableView_food_log.setColumnWidth(2, 80)   # Weight
            self.tableView_food_log.setColumnWidth(3, 140)  # Calories per 100g
            self.tableView_food_log.setColumnWidth(4, 120)  # Portion Calories
            self.tableView_food_log.setColumnWidth(5, 120)  # Date
            self.tableView_food_log.setColumnWidth(6, 100)  # English Name

            # Connect selection change signals after models are set
            self._connect_table_selection_signals()

            # Connect auto-save signals after all models are created
            self._connect_table_auto_save_signals()

            # Update food calories for today
            self.update_food_calories_today()

        except Exception as e:
            print(f"Error showing tables: {e}")
            QMessageBox.warning(self, "Database Error", f"Failed to load tables: {e}")

    def update_food_data(self) -> None:
        """Refresh food-related data only.

        Updates food items lists and calories count.
        """
        if not self._validate_database_connection():
            print("Database connection not available for update_food_data")
            return

        # Update food items list
        self._update_food_items_list()
        self._update_favorite_food_items_list()
        self.update_food_calories_today()
        self.show_tables()

    def update_calories_calculation(self) -> None:
        """Update the calories calculation label based on radio button selection and values."""
        weight = self.doubleSpinBox_food_weight.value()
        calories = self.doubleSpinBox_food_calories.value()
        use_weight = self.radioButton_use_weight.isChecked()

        if use_weight:
            # Weight mode: calories per 100g
            if weight > 0 and calories > 0:
                calculated_calories = (weight * calories) / 100
                self.label_food_calories_calc.setText(f"Total: {calculated_calories:.1f} kcal")
            else:
                self.label_food_calories_calc.setText("Total: 0.0 kcal")
        # Portion mode: direct calories
        elif calories > 0:
            self.label_food_calories_calc.setText(f"Total: {calories:.1f} kcal")
        else:
            self.label_food_calories_calc.setText("Total: 0.0 kcal")

    def update_food_calories_today(self) -> None:
        """Update the label showing calories consumed today."""
        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        if not self._validate_database_connection():
            self.label_food_today.setText("0 kcal")
            return

        try:
            calories = self.db_manager.get_food_calories_today()
            count = self.db_manager.get_food_calories_count_today()
            self.label_food_today.setText(f"{calories:.1f} kcal ({count} items)")
        except Exception as e:
            print(f"Error getting food calories for today: {e}")
            self.label_food_today.setText("0 kcal")

    def _connect_signals(self) -> None:
        """Wire Qt widgets to their Python slots.

        Connects all UI elements to their respective handler methods, including:

        - Button click events for adding and deleting records
        - Auto-save signals for table data changes
        """
        # Connect delete and refresh buttons for food tables
        self.pushButton_food_delete.clicked.connect(partial(self.delete_record, "food_log"))
        self.pushButton_food_refresh.clicked.connect(self.update_food_data)

        # Add buttons
        self.pushButton_food_add.clicked.connect(self.on_add_food_log)
        self.pushButton_food_item_add.clicked.connect(self.on_add_food_item)
        self.pushButton_food_yesterday.clicked.connect(self.set_food_yesterday_date)

        # Connect radio buttons and spin boxes for calories calculation
        self.radioButton_use_weight.clicked.connect(self.update_calories_calculation)
        self.radioButton_use_calories.clicked.connect(self.update_calories_calculation)
        self.doubleSpinBox_food_weight.valueChanged.connect(self.update_calories_calculation)
        self.doubleSpinBox_food_calories.valueChanged.connect(self.update_calories_calculation)

        # Export functionality removed - no export button in UI

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
        # Connect food items list selection
        selection_model = self.listView_food_items.selectionModel()
        if selection_model:
            selection_model.currentChanged.connect(self.on_food_item_selection_changed)

        # Connect favorite food items list selection
        selection_model = self.listView_favorite_food_items.selectionModel()
        if selection_model:
            selection_model.currentChanged.connect(self.on_food_item_selection_changed)

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

    def _create_colored_food_log_table_model(
        self,
        data: list[list],
        headers: list[str],
        _id_column: int = 7,  # ID is now at index 7 in transformed data
    ) -> QSortFilterProxyModel:
        """Return a proxy model filled with colored food_log data.

        Args:

        - `data` (`list[list]`): The table data with color information.
        - `headers` (`list[str]`): Column header names.
        - `_id_column` (`int`): Index of the ID column. Defaults to `7`.

        Returns:

        - `QSortFilterProxyModel`: A filterable and sortable model with colored data.

        """
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(headers)

        for row_idx, row in enumerate(data):
            # Extract color information (last element) and ID
            row_color = row[8]  # Color is at index 8
            row_id = row[7]  # ID is at index 7

            # Create items for display columns only (first 7 elements)
            items = []
            for col_idx, value in enumerate(row[:7]):  # Only first 7 elements for display
                item = QStandardItem(str(value) if value is not None else "")

                # Set background color for the item
                item.setBackground(QBrush(row_color))

                # Check if this is today's record and make it bold
                today = QDateTime.currentDateTime().toString("yyyy-MM-dd")
                id_col_date = 5  # Date column is now at index 5
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

        # food items list-view
        self.listView_food_items.setModel(None)
        if self.food_items_list_model is not None:
            self.food_items_list_model.deleteLater()
        self.food_items_list_model = None

        # favorite food items list-view
        self.listView_favorite_food_items.setModel(None)
        if self.favorite_food_items_list_model is not None:
            self.favorite_food_items_list_model.deleteLater()
        self.favorite_food_items_list_model = None

    def _get_current_selected_food_item(self) -> str | None:
        """Get the currently selected food item from the list view.

        Returns:

        - `str | None`: The name of the selected food item, or None if nothing is selected.

        """
        selection_model = self.listView_food_items.selectionModel()
        if not selection_model or not self.food_items_list_model:
            return None

        current_index = selection_model.currentIndex()
        if not current_index.isValid():
            return None

        item = self.food_items_list_model.itemFromIndex(current_index)
        return item.text() if item else None

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

    def _init_food_items_list(self) -> None:
        """Initialize the food items list view with a model and connect signals."""
        self.food_items_list_model = QStandardItemModel()
        self.listView_food_items.setModel(self.food_items_list_model)

        # Connect selection change signal after model is set
        selection_model = self.listView_food_items.selectionModel()
        if selection_model:
            selection_model.currentChanged.connect(self.on_food_item_selection_changed)

    def _init_favorite_food_items_list(self) -> None:
        """Initialize the favorite food items list view with a model and connect signals."""
        self.favorite_food_items_list_model = QStandardItemModel()
        self.listView_favorite_food_items.setModel(self.favorite_food_items_list_model)

        # Connect selection change signal after model is set
        selection_model = self.listView_favorite_food_items.selectionModel()
        if selection_model:
            selection_model.currentChanged.connect(self.on_food_item_selection_changed)

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

    def _setup_ui(self) -> None:
        """Set up additional UI elements after basic initialization."""
        # Set emoji for buttons
        self.pushButton_food_add.setText(f"🍽️ {self.pushButton_food_add.text()}")
        self.pushButton_food_item_add.setText(f"➕ {self.pushButton_food_item_add.text()}")
        self.pushButton_food_yesterday.setText(f"📅 {self.pushButton_food_yesterday.text()}")
        self.pushButton_food_delete.setText(f"🗑️ {self.pushButton_food_delete.text()}")
        self.pushButton_food_refresh.setText(f"🔄 {self.pushButton_food_refresh.text()}")
        # Export button removed from UI

        # Configure food splitter proportions
        self.splitter_food.setStretchFactor(0, 3)  # tableView_food_log gets more space
        self.splitter_food.setStretchFactor(1, 1)  # widget_food_middle gets less space
        self.splitter_food.setStretchFactor(2, 0)  # frame_food_controls with fixed size

        # Set initial radio button state and update calories calculation
        self.radioButton_use_weight.setChecked(True)
        self.update_calories_calculation()

    def _update_food_items_list(self) -> None:
        """Refresh food items list view with data from database."""
        if not self._validate_database_connection():
            print("Database manager not available or connection not open")
            return

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            # Get food items sorted by name
            food_items_data = self.db_manager.get_all_food_items()

            # Block signals during model update
            selection_model = self.listView_food_items.selectionModel()
            if selection_model:
                selection_model.blockSignals(True)  # noqa: FBT003

            # Update food items list model
            if self.food_items_list_model is not None:
                self.food_items_list_model.clear()
                for food_item_row in food_items_data:
                    # food_item_row format: [_id, name, name_en, is_drink, calories_per_100g, default_portion_weight, default_portion_calories]
                    food_name = food_item_row[1]  # name is at index 1
                    item = QStandardItem(food_name)
                    self.food_items_list_model.appendRow(item)

            # Unblock signals
            if selection_model:
                selection_model.blockSignals(False)  # noqa: FBT003

        except Exception as e:
            print(f"Error updating food items list: {e}")

    def _update_favorite_food_items_list(self) -> None:
        """Refresh favorite food items list view with popular items from database."""
        if not self._validate_database_connection():
            print("Database manager not available or connection not open")
            return

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            # Get popular food items from recent records (top 20)
            popular_food_items = self.db_manager.get_popular_food_items(500)[:20]

            # Block signals during model update
            selection_model = self.listView_favorite_food_items.selectionModel()
            if selection_model:
                selection_model.blockSignals(True)  # noqa: FBT003

            # Update favorite food items list model
            if self.favorite_food_items_list_model is not None:
                self.favorite_food_items_list_model.clear()
                for food_name in popular_food_items:
                    item = QStandardItem(food_name)
                    self.favorite_food_items_list_model.appendRow(item)

            # Unblock signals
            if selection_model:
                selection_model.blockSignals(False)  # noqa: FBT003

        except Exception as e:
            print(f"Error updating favorite food items list: {e}")

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
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
