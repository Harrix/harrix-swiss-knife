"""Food tracker GUI.

This module contains a single `MainWindow` class that provides a Qt-based GUI for a
SQLite database with food items and food log records.
"""

from __future__ import annotations

import sys
from functools import partial
from pathlib import Path

import harrix_pylib as h
from PySide6.QtCore import QDate, QDateTime, QModelIndex, QSortFilterProxyModel, QStringListModel, Qt, QTimer
from PySide6.QtGui import QBrush, QCloseEvent, QColor, QKeyEvent, QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QApplication, QCompleter, QDialog, QFileDialog, QMainWindow, QMessageBox, QTableView

from harrix_swiss_knife.food import database_manager, window
from harrix_swiss_knife.food.food_item_dialog import FoodItemDialog
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

        # Initialize core attributes
        self.db_manager: database_manager.DatabaseManager | None = None

        # Food items list model
        self.food_items_list_model: QStandardItemModel | None = None

        # Favorite food items list model
        self.favorite_food_items_list_model: QStandardItemModel | None = None

        # Table models dictionary
        self.models: dict[str, QSortFilterProxyModel | None] = {
            "food_log": None,
            "kcal_per_day": None,
        }

        # Food log display state
        self.show_all_food_records: bool = False

        # Dialog state to prevent multiple dialogs
        self._food_item_dialog_open: bool = False

        # Table configuration mapping
        self.table_config: dict[str, tuple[QTableView, str, list[str]]] = {
            "food_log": (
                self.tableView_food_log,
                "food_log",
                [
                    "Name",
                    "Is Drink",
                    "Weight",
                    "Calories per 100g",
                    "Portion Calories",
                    "Calculated Calories",
                    "Date",
                    "English Name",
                ],
            ),
            "kcal_per_day": (
                self.tableView_kcal_per_day,
                "kcal_per_day",
                ["Date", "Calories"],
            ),
        }

        # Define colors for different dates (expanded palette)
        self.date_colors = self.generate_pastel_colors_mathematical(50)

        # Chart configuration
        self.max_count_points_in_charts = 50

        # Initialize application
        self._init_database()
        self._setup_autocomplete()
        self._connect_signals()
        self._init_food_items_list()
        self._init_favorite_food_items_list()
        self.set_today_date()  # Set current date in dateEdit_food
        self.update_food_data()
        self._setup_window_size_and_position()

        # Initialize food stats date range with earliest date from database
        self._init_food_stats_dates()

        # Adjust table column widths and show window after UI is fully initialized
        QTimer.singleShot(200, self._finish_window_initialization)

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

        # Handle Enter key on various widgets to trigger add button
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            focused_widget = QApplication.focusWidget()
            if (
                focused_widget == self.doubleSpinBox_food_calories
                or focused_widget == self.spinBox_food_weight
                or focused_widget == self.checkBox_food_is_drink
            ):
                self.pushButton_food_add.click()
                return

        # Call parent implementation for other key events
        super().keyPressEvent(event)

    @requires_database()
    def on_add_food_item(self) -> None:
        """Insert a new food item using database manager."""
        name = self.lineEdit_food_name.text().strip()
        name_en = self.lineEdit_food_name_en.text().strip()
        is_drink = self.checkBox_food_is_drink.isChecked()
        calories_per_100g = self.doubleSpinBox_food_cal100.value()
        default_portion_weight = self.spinBox_food_default_weight.value()
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
                default_portion_calories=default_portion_calories if default_portion_calories > 0 else None,
            ):
                self.update_food_data()
                # Clear form
                self.lineEdit_food_name.clear()
                self.lineEdit_food_name_en.clear()
                self.checkBox_food_is_drink.setChecked(False)
                self.doubleSpinBox_food_cal100.setValue(0)
                self.spinBox_food_default_weight.setValue(0)
                self.doubleSpinBox_food_default_cal.setValue(0)
            else:
                QMessageBox.warning(self, "Error", "Failed to add food item")

        except Exception as e:
            QMessageBox.warning(self, "Database Error", f"Failed to add food item: {e}")

    @requires_database()
    def on_add_food_log(self) -> None:
        """Insert a new food log record using database manager."""
        # Get values from UI
        food_name = self.lineEdit_food_manual_name.text().strip()
        weight = self.spinBox_food_weight.value()
        calories = self.doubleSpinBox_food_calories.value()
        food_date = self.dateEdit_food.date().toString("yyyy-MM-dd")
        use_weight = self.radioButton_use_weight.isChecked()
        is_drink = self.checkBox_food_is_drink.isChecked()

        # Validate required fields
        if not food_name:
            QMessageBox.warning(self, "Error", "Enter food name")
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
            if use_weight:
                # Weight mode: calories is calories_per_100g
                calories_per_100g = calories if calories > 0 else 0
                portion_calories = None
            else:
                # Portion mode: calories is portion_calories, set calories_per_100g to 0
                calories_per_100g = 0  # Required by database schema (NOT NULL)
                portion_calories = calories if calories > 0 else None

            # Use database manager method
            if self.db_manager.add_food_log_record(
                date=food_date,
                calories_per_100g=calories_per_100g,
                name=food_name,
                weight=weight if weight > 0 else None,
                portion_calories=portion_calories,
                is_drink=is_drink,
            ):
                # Update UI - only food-related data
                self.update_food_data()

                # Move focus to food name field and select all text
                self.lineEdit_food_manual_name.setFocus()
                self.lineEdit_food_manual_name.selectAll()
            else:
                QMessageBox.warning(self, "Error", "Failed to add food log record")

        except Exception as e:
            QMessageBox.warning(self, "Database Error", f"Failed to add food log record: {e}")

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
            # First try to get food item data from food_items table
            food_item_data = self.db_manager.get_food_item_by_name(food_item)

            if food_item_data:
                # food_item_data format: [_id, name, name_en, is_drink, calories_per_100g, default_portion_weight, default_portion_calories]
                (
                    food_id,
                    name,
                    name_en,
                    is_drink,
                    calories_per_100g,
                    default_portion_weight,
                    default_portion_calories,
                ) = food_item_data

                # Populate groupBox_food_add fields (food log record form)
                self.lineEdit_food_manual_name.setText(name)
                self.spinBox_food_weight.setValue(int(default_portion_weight) if default_portion_weight else 100)
                self.checkBox_food_is_drink.setChecked(is_drink == 1)

                # Determine radio button state based on default_portion_calories
                if default_portion_calories and default_portion_calories > 0:
                    # Use portion calories mode
                    self.radioButton_use_calories.setChecked(True)
                    self.doubleSpinBox_food_calories.setValue(default_portion_calories)
                else:
                    # Use weight mode
                    self.radioButton_use_weight.setChecked(True)
                    self.doubleSpinBox_food_calories.setValue(calories_per_100g if calories_per_100g else 0)

                # Populate groupBox_food_items fields (food item form)
                self.lineEdit_food_name.setText(name)
                self.lineEdit_food_name_en.setText(name_en if name_en else "")
                self.checkBox_is_drink.setChecked(is_drink == 1)
                self.doubleSpinBox_food_cal100.setValue(calories_per_100g if calories_per_100g else 0)
                self.spinBox_food_default_weight.setValue(
                    int(default_portion_weight) if default_portion_weight else 100
                )
                self.doubleSpinBox_food_default_cal.setValue(
                    default_portion_calories if default_portion_calories else 0
                )

            else:
                # If not found in food_items, try to get from food_log (for popular items)
                food_log_data = self.db_manager.get_food_log_item_by_name(food_item)

                if food_log_data:
                    # food_log_data format: [name, name_en, is_drink, calories_per_100g, weight, portion_calories]
                    name, name_en, is_drink, calories_per_100g, weight, portion_calories = food_log_data

                    # Populate groupBox_food_add fields (food log record form)
                    self.lineEdit_food_manual_name.setText(name)
                    self.spinBox_food_weight.setValue(int(weight) if weight else 100)
                    self.checkBox_food_is_drink.setChecked(is_drink == 1)

                    # Determine radio button state based on portion_calories
                    if portion_calories and portion_calories > 0:
                        # Use portion calories mode
                        self.radioButton_use_calories.setChecked(True)
                        self.doubleSpinBox_food_calories.setValue(portion_calories)
                    else:
                        # Use weight mode
                        self.radioButton_use_weight.setChecked(True)
                        self.doubleSpinBox_food_calories.setValue(calories_per_100g if calories_per_100g else 0)

                    # Populate groupBox_food_items fields (food item form)
                    self.lineEdit_food_name.setText(name)
                    self.lineEdit_food_name_en.setText(name_en if name_en else "")
                    self.checkBox_is_drink.setChecked(is_drink == 1)
                    self.doubleSpinBox_food_cal100.setValue(calories_per_100g if calories_per_100g else 0)
                    self.spinBox_food_default_weight.setValue(int(weight) if weight else 100)
                    self.doubleSpinBox_food_default_cal.setValue(portion_calories if portion_calories else 0)

                else:
                    # If not found in either table, just set the name
                    self.lineEdit_food_manual_name.setText(food_item)
                    self.lineEdit_food_name.setText(food_item)
                    # Reset other fields to defaults
                    self.spinBox_food_weight.setValue(100)
                    self.checkBox_food_is_drink.setChecked(False)
                    self.radioButton_use_weight.setChecked(True)
                    self.doubleSpinBox_food_calories.setValue(0)
                    self.lineEdit_food_name_en.setText("")
                    self.checkBox_is_drink.setChecked(False)
                    self.doubleSpinBox_food_cal100.setValue(0)
                    self.spinBox_food_default_weight.setValue(100)
                    self.doubleSpinBox_food_default_cal.setValue(0)

            # Update calories calculation
            self.update_calories_calculation()

            # Move focus to weight spinbox and select all text after selection
            self.spinBox_food_weight.setFocus()
            self.spinBox_food_weight.selectAll()

        except Exception as e:
            print(f"Error in food item selection changed: {e}")
            # In case of error, at least set the name and move focus
            self.lineEdit_food_manual_name.setText(food_item)
            self.lineEdit_food_name.setText(food_item)
            self.spinBox_food_weight.setFocus()
            self.spinBox_food_weight.selectAll()

    def on_food_item_double_clicked(self, index: QModelIndex) -> None:
        """Handle double click on food item in the list view."""
        # Prevent multiple dialogs from opening
        if self._food_item_dialog_open:
            return

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
            # Set dialog open flag
            self._food_item_dialog_open = True

            # Get food item data from food_items table
            food_item_data = self.db_manager.get_food_item_by_name(food_item)

            if not food_item_data:
                QMessageBox.warning(self, "Error", f"Food item '{food_item}' not found in database!")
                self._food_item_dialog_open = False
                return

            # Create and show the edit dialog
            dialog = FoodItemDialog(self, food_item_data)
            result = dialog.exec()

            # Only process if dialog was accepted (not cancelled)
            if result == QDialog.DialogCode.Accepted:
                if hasattr(dialog, 'delete_confirmed') and dialog.delete_confirmed:
                    # Delete the food item
                    food_id = food_item_data[0]
                    if self.db_manager.delete_food_item(food_id):
                        QMessageBox.information(self, "Success", f"Food item '{food_item}' deleted successfully!")
                        self.update_food_data()
                    else:
                        QMessageBox.warning(self, "Error", f"Failed to delete food item '{food_item}'!")
                else:
                    # Update the food item
                    edited_data = dialog.get_edited_data()
                    food_id = food_item_data[0]

                    if self.db_manager.update_food_item(
                        food_item_id=food_id,
                        name=edited_data["name"],
                        name_en=edited_data["name_en"],
                        is_drink=edited_data["is_drink"],
                        calories_per_100g=edited_data["calories_per_100g"],
                        default_portion_weight=edited_data["default_portion_weight"],
                        default_portion_calories=edited_data["default_portion_calories"],
                    ):
                        QMessageBox.information(self, "Success", f"Food item '{edited_data['name']}' updated successfully!")
                        self.update_food_data()
                    else:
                        QMessageBox.warning(self, "Error", f"Failed to update food item '{edited_data['name']}'!")
            # If result is Rejected (Cancel), do nothing - just close the dialog

        except Exception as e:
            print(f"Error in food item double clicked: {e}")
            QMessageBox.warning(self, "Error", f"Error editing food item: {e}")
        finally:
            # Always reset the dialog open flag
            self._food_item_dialog_open = False

    def on_food_log_table_cell_clicked(self, index: QModelIndex) -> None:
        """Handle food log table cell click and populate form fields with row data."""
        try:
            # Get the row ID from the vertical header
            proxy_model = self.models["food_log"]
            if proxy_model is None:
                return
            source_model = proxy_model.sourceModel()
            if not isinstance(source_model, QStandardItemModel):
                return

            row_id = source_model.verticalHeaderItem(index.row())
            if not row_id:
                return

            # Get data from the table model directly
            # The table columns are: [name, is_drink, weight, calories_per_100g, portion_calories, calculated_calories, date, name_en]
            name = source_model.item(index.row(), 0).text() if source_model.item(index.row(), 0) else ""
            is_drink = source_model.item(index.row(), 1).text() == "1" if source_model.item(index.row(), 1) else False
            weight_str = source_model.item(index.row(), 2).text() if source_model.item(index.row(), 2) else "0"
            calories_per_100g_str = (
                source_model.item(index.row(), 3).text() if source_model.item(index.row(), 3) else "0"
            )
            portion_calories_str = (
                source_model.item(index.row(), 4).text() if source_model.item(index.row(), 4) else "0"
            )
            name_en = source_model.item(index.row(), 7).text() if source_model.item(index.row(), 7) else ""

            # Convert string values to appropriate types
            weight = float(weight_str) if weight_str and weight_str != "" else 0
            calories_per_100g = (
                float(calories_per_100g_str) if calories_per_100g_str and calories_per_100g_str != "" else 0
            )
            portion_calories = float(portion_calories_str) if portion_calories_str and portion_calories_str != "" else 0

            # Populate groupBox_food_add fields (food log record form)
            self.lineEdit_food_manual_name.setText(name)
            self.spinBox_food_weight.setValue(int(weight) if weight > 0 else 0)
            self.checkBox_food_is_drink.setChecked(is_drink)

            # Determine radio button state based on portion_calories
            if portion_calories > 0:
                # Use portion calories mode
                self.radioButton_use_calories.setChecked(True)
                self.doubleSpinBox_food_calories.setValue(portion_calories)
            else:
                # Use weight mode
                self.radioButton_use_weight.setChecked(True)
                self.doubleSpinBox_food_calories.setValue(calories_per_100g)

            # Populate groupBox_food_items fields (food item form)
            self.lineEdit_food_name.setText(name)
            self.lineEdit_food_name_en.setText(name_en)
            self.checkBox_is_drink.setChecked(is_drink)
            self.doubleSpinBox_food_cal100.setValue(calories_per_100g)
            self.spinBox_food_default_weight.setValue(int(weight) if weight > 0 else 0)
            self.doubleSpinBox_food_default_cal.setValue(portion_calories)

            # Update calories calculation
            self.update_calories_calculation()

            # Move focus to weight spinbox and select all text
            self.spinBox_food_weight.setFocus()
            self.spinBox_food_weight.selectAll()

        except Exception as e:
            print(f"Error in food log table cell clicked: {e}")

    def on_food_stats_all_time(self) -> None:
        """Set date range to all available data and update chart."""
        if not self.db_manager or not self._validate_database_connection():
            return

        try:
            # Get earliest date from database
            earliest_date_str = self.db_manager.get_earliest_food_log_date()
            if earliest_date_str:
                earliest_date = QDate.fromString(earliest_date_str, "yyyy-MM-dd")
                if earliest_date.isValid():
                    self.dateEdit_food_stats_from.setDate(earliest_date)
                else:
                    # Fallback to a reasonable default if date parsing fails
                    self.dateEdit_food_stats_from.setDate(QDate.currentDate().addYears(-10))
            else:
                # No data in database, use a reasonable default
                self.dateEdit_food_stats_from.setDate(QDate.currentDate().addYears(-10))

            # Set end date to today
            self.dateEdit_food_stats_to.setDate(QDate.currentDate())

            self._update_food_calories_chart()

        except Exception as e:
            print(f"Error setting all time date range: {e}")
            # Fallback to last year if any error occurs
            today = QDate.currentDate()
            year_ago = today.addYears(-1)
            self.dateEdit_food_stats_from.setDate(year_ago)
            self.dateEdit_food_stats_to.setDate(today)
            self._update_food_calories_chart()

    def on_food_stats_drink(self) -> None:
        """Show drinks chart."""
        self._update_drinks_chart()

    def on_food_stats_food_weight(self) -> None:
        """Show food weight chart."""
        self._update_food_weight_chart()

    def on_food_stats_last_month(self) -> None:
        """Set date range to last month and update chart."""
        today = QDate.currentDate()
        month_ago = today.addMonths(-1)

        self.dateEdit_food_stats_from.setDate(month_ago)
        self.dateEdit_food_stats_to.setDate(today)

        self._update_food_calories_chart()

    def on_food_stats_last_week(self) -> None:
        """Set date range to last week and update chart."""
        today = QDate.currentDate()
        week_ago = today.addDays(-7)

        self.dateEdit_food_stats_from.setDate(week_ago)
        self.dateEdit_food_stats_to.setDate(today)

        self._update_food_calories_chart()

    def on_food_stats_last_year(self) -> None:
        """Set date range to last year and update chart."""
        today = QDate.currentDate()
        year_ago = today.addYears(-1)

        self.dateEdit_food_stats_from.setDate(year_ago)
        self.dateEdit_food_stats_to.setDate(today)

        self._update_food_calories_chart()

    def on_food_stats_period_changed(self) -> None:
        """Handle period selection change and update chart."""
        self._update_food_calories_chart()

    def on_food_stats_update(self) -> None:
        """Update the food calories chart."""
        self._update_food_calories_chart()

    def on_show_all_records_clicked(self) -> None:
        """Toggle between showing all records and last 5000 records."""
        self.show_all_food_records = not self.show_all_food_records

        # Update button text and icon
        if self.show_all_food_records:
            self.pushButton_show_all_records.setText("📊 Show Last 5000")
        else:
            self.pushButton_show_all_records.setText("📊 Show All Records")

        # Refresh the food log table
        self._update_food_log_table()

    def set_food_yesterday_date(self) -> None:
        """Set yesterday's date in the food date edit field.

        Sets the dateEdit_food widget to yesterday's date for convenient entry
        of food records from the previous day.
        """
        yesterday = QDate.currentDate().addDays(-1)
        self.dateEdit_food.setDate(yesterday)

    def set_today_date(self) -> None:
        """Set today's date in the food date edit field."""
        today_qdate = QDate.currentDate()
        self.dateEdit_food.setDate(today_qdate)

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
                    # [name, is_drink, weight, calories_per_100g, portion_calories, calculated_calories, date, name_en]

                    # Check if portion_calories is non-zero, then hide calories_per_100g if it's 0
                    portion_calories = row[3]
                    calories_per_100g = row[4]
                    weight = row[2]

                    # If portion_calories is non-zero and calories_per_100g is 0, show empty string for calories_per_100g
                    # But if portion_calories is 0 (like water), show the 0 for calories_per_100g
                    if portion_calories and portion_calories > 0 and (not calories_per_100g or calories_per_100g == 0):
                        calories_per_100g_display = ""
                    else:
                        calories_per_100g_display = calories_per_100g if calories_per_100g is not None else ""

                    # Calculate total calories
                    calculated_calories = 0.0
                    if portion_calories and portion_calories > 0:
                        # Use portion calories directly
                        calculated_calories = float(portion_calories)
                    elif calories_per_100g and calories_per_100g > 0 and weight and weight > 0:
                        # Calculate from weight and calories per 100g
                        calculated_calories = (float(calories_per_100g) * float(weight)) / 100

                    transformed_row = [
                        row[5],
                        "1" if row[7] == 1 else "",
                        row[2],
                        calories_per_100g_display,
                        portion_calories,
                        f"{calculated_calories:.1f}",
                        row[1],
                        row[6],
                    ]

                    # Add color information based on date
                    date_str = row[1]
                    date_color = date_to_color.get(date_str, QColor(255, 255, 255))  # White as fallback

                    # Add original ID and color to the row for later use
                    transformed_row.extend(
                        [row[0], date_color]
                    )  # [name, is_drink, weight, calories_per_100g, portion_calories, calculated_calories, date, name_en, id, color]
                    transformed_rows.append(transformed_row)

                return transformed_rows

            # Get food_log data and transform it
            # Use limited records for table display to improve performance with large datasets
            # Statistics methods will still analyze all records from the database
            food_log_rows = self.db_manager.get_recent_food_log_records(5000)
            transformed_food_log_data = transform_food_log_data(food_log_rows)

            # Create food_log table model with coloring
            self.models["food_log"] = self._create_colored_food_log_table_model(
                transformed_food_log_data, self.table_config["food_log"][2]
            )
            self.tableView_food_log.setModel(self.models["food_log"])

            # Enable editing for the table
            self.tableView_food_log.setEditTriggers(
                QTableView.EditTrigger.DoubleClicked | QTableView.EditTrigger.EditKeyPressed
            )

            # Configure food_log table header - interactive mode for all columns
            food_log_header = self.tableView_food_log.horizontalHeader()
            # Set all columns to interactive (resizable)
            for i in range(food_log_header.count()):
                food_log_header.setSectionResizeMode(i, food_log_header.ResizeMode.Interactive)
            # Set proportional column widths for all columns
            self._adjust_food_log_table_columns()

            # Connect selection change signals after models are set
            self._connect_table_selection_signals()

            # Connect auto-save signals after all models are created
            self._connect_table_auto_save_signals()

            # Update food calories for today
            self.update_food_calories_today()

        except Exception as e:
            print(f"Error showing tables: {e}")
            QMessageBox.warning(self, "Database Error", f"Failed to load tables: {e}")

    def update_calories_calculation(self) -> None:
        """Update the calories calculation label based on radio button selection and values."""
        weight = self.spinBox_food_weight.value()
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
        """Update the label showing calories consumed today and drinks weight in liters (comma as decimal separator)."""
        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        if not self._validate_database_connection():
            self.label_food_today.setText("0 kcal\n0,0 liters")
            return

        try:
            calories = self.db_manager.get_food_calories_today()
            drinks_weight = self.db_manager.get_drinks_weight_today()
            drinks_liters = drinks_weight / 1000 if drinks_weight else 0.0
            drinks_liters_str = f"{drinks_liters:.1f}"
            self.label_food_today.setText(f"{calories:.1f} kcal \n{drinks_liters_str} liters")
        except Exception as e:
            print(f"Error getting food calories for today: {e}")
            self.label_food_today.setText("0 kcal\n0,0 liters")

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
        self._update_autocomplete_data()  # Добавьте эту строку
        self.update_food_calories_today()
        self.show_tables()

    def _adjust_food_log_table_columns(self) -> None:
        """Adjust food log table column widths proportionally to window size."""
        if not hasattr(self, "tableView_food_log") or not self.tableView_food_log.model():
            return

        # Get current table width (approximate available width for table)
        table_width = self.tableView_food_log.width()
        if table_width <= 0:
            # Fallback to window width if table width is not available
            table_width = self.width() * 0.7  # Assume table takes ~70% of window width

        # Ensure minimum table width for better appearance
        table_width = max(table_width, 800)

        # Reserve space for vertical headers, scrollbar, and borders
        vertical_header_width = self.tableView_food_log.verticalHeader().width()
        scrollbar_width = 20  # Approximate scrollbar width
        borders_and_margins = 10  # Space for borders and margins

        available_width = table_width - vertical_header_width - scrollbar_width - borders_and_margins

        # Define proportional distribution of available width
        # Total: 100% = 20% + 6% + 6% + 12% + 10% + 10% + 12% + 24%
        proportions = [
            0.20,  # Name
            0.06,  # Is Drink
            0.06,  # Weight
            0.12,  # Calories per 100g
            0.10,  # Portion Calories
            0.10,  # Calculated Calories
            0.12,  # Date
            0.24,  # English Name
        ]

        # Calculate widths based on proportions of available width
        column_widths = [int(available_width * prop) for prop in proportions]

        # Apply widths to all columns
        for i, width in enumerate(column_widths):
            self.tableView_food_log.setColumnWidth(i, width)

    def _adjust_kcal_per_day_table_columns(self) -> None:
        """Set column widths for kcal per day table."""
        if not hasattr(self, "tableView_kcal_per_day") or not self.tableView_kcal_per_day.model():
            return

        # Set first column (Date) to fixed width of 80px
        self.tableView_kcal_per_day.setColumnWidth(0, 80)

        # Set second column (Calories) to stretch to remaining space
        self.tableView_kcal_per_day.horizontalHeader().setStretchLastSection(True)

    def _connect_signals(self) -> None:
        """Wire Qt widgets to their Python slots.

        Connects all UI elements to their respective handler methods, including:

        - Button click events for adding and deleting records
        - Auto-save signals for table data changes
        """
        # Connect delete and refresh buttons for food tables
        self.pushButton_food_delete.clicked.connect(partial(self.delete_record, "food_log"))
        self.pushButton_food_refresh.clicked.connect(self.update_food_data)

        # Connect window resize event for automatic column resizing
        self.resizeEvent = self._on_window_resize

        # Connect tab widget signal for updating stats when switching to food stats tab
        self.tabWidget.currentChanged.connect(self._on_tab_changed)

        # Add buttons
        self.pushButton_food_add.clicked.connect(self.on_add_food_log)
        self.pushButton_food_item_add.clicked.connect(self.on_add_food_item)
        self.pushButton_food_yesterday.clicked.connect(self.set_food_yesterday_date)
        self.pushButton_show_all_records.clicked.connect(self.on_show_all_records_clicked)

        # Connect radio buttons and spin boxes for calories calculation
        self.radioButton_use_weight.clicked.connect(self.update_calories_calculation)
        self.radioButton_use_calories.clicked.connect(self.update_calories_calculation)
        self.spinBox_food_weight.valueChanged.connect(self.update_calories_calculation)
        self.doubleSpinBox_food_calories.valueChanged.connect(self.update_calories_calculation)

        # Connect food stats controls
        self.pushButton_food_stats_last_week.clicked.connect(self.on_food_stats_last_week)
        self.pushButton_food_stats_last_month.clicked.connect(self.on_food_stats_last_month)
        self.pushButton_food_stats_last_year.clicked.connect(self.on_food_stats_last_year)
        self.pushButton_food_stats_all_time.clicked.connect(self.on_food_stats_all_time)
        self.pushButton_food_stats_food_weight.clicked.connect(self.on_food_stats_food_weight)
        self.pushButton_food_stats_drink.clicked.connect(self.on_food_stats_drink)
        self.pushButton_food_stats_update.clicked.connect(self.on_food_stats_update)
        self.comboBox_food_stats_period.currentTextChanged.connect(self.on_food_stats_period_changed)

        # Connect food name input for real-time filtering
        self.lineEdit_food_manual_name.textChanged.connect(self._filter_food_items)

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

        # Connect food items list double click
        self.listView_food_items.doubleClicked.connect(self.on_food_item_double_clicked)

        # Connect food log table cell click
        self.tableView_food_log.clicked.connect(self.on_food_log_table_cell_clicked)

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
        _id_column: int = 8,  # ID is now at index 8 in transformed data
    ) -> QSortFilterProxyModel:
        """Return a proxy model filled with colored food_log data.

        Args:

        - `data` (`list[list]`): The table data with color information.
        - `headers` (`list[str]`): Column header names.
        - `_id_column` (`int`): Index of the ID column. Defaults to `8`.

        Returns:

        - `QSortFilterProxyModel`: A filterable and sortable model with colored data.

        """
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(headers)

        for row_idx, row in enumerate(data):
            # Extract color information (last element) and ID
            row_color = row[9]  # Color is at index 9
            row_id = row[8]  # ID is at index 8

            # Create items for display columns only (first 8 elements)
            items = []
            for col_idx, value in enumerate(row[:8]):  # Only first 8 elements for display
                item = QStandardItem(str(value) if value is not None else "")

                # Set background color for the item
                item.setBackground(QBrush(row_color))

                # Make calculated calories column non-editable (column 5)
                if col_idx == 5:
                    item.setEditable(False)

                # Check if this is today's record and make it bold
                today = QDateTime.currentDateTime().toString("yyyy-MM-dd")
                id_col_date = 6  # Date column is now at index 6
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

    def _create_colored_kcal_per_day_table_model(
        self,
        data: list[list],
        headers: list[str],
    ) -> QSortFilterProxyModel:
        """Return a proxy model filled with colored kcal per day data.

        Args:

        - `data` (`list[list]`): The table data.
        - `headers` (`list[str]`): Column header names.

        Returns:

        - `QSortFilterProxyModel`: A filterable and sortable model with colored data.

        """
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(headers)

        for row_idx, row in enumerate(data):
            items = []
            row_color = None

            # Determine row color based on calories (second column)
            if len(row) > 1:
                try:
                    calories = float(row[1]) if row[1] else 0.0
                    if calories <= 1800:
                        # Green for low calories
                        row_color = QColor(144, 238, 144)
                    elif calories <= 2100:
                        # Green-yellow for medium-low calories
                        row_color = QColor(255, 255, 224)
                    elif calories <= 2500:
                        # Yellow for medium-high calories
                        row_color = QColor(255, 228, 196)
                    else:
                        # Red for high calories
                        row_color = QColor(255, 192, 203)
                except (ValueError, TypeError):
                    # If calories can't be parsed, use default background
                    pass

            # Create items for all columns
            for col_idx, value in enumerate(row):
                item = QStandardItem(str(value) if value is not None else "")

                # Apply row color to all items in the row
                if row_color:
                    item.setBackground(QBrush(row_color))

                items.append(item)

            model.appendRow(items)

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

        # Dispose autocomplete completer
        if hasattr(self, "food_completer") and self.food_completer is not None:
            self.food_completer.deleteLater()
            self.food_completer = None

        if hasattr(self, "food_completer_model") and self.food_completer_model is not None:
            self.food_completer_model.deleteLater()
            self.food_completer_model = None

    def _filter_food_items(self, text: str) -> None:
        """Filter food items lists based on input text.

        Args:
            text (str): Filter text from lineEdit_food_manual_name

        """
        if not text:
            # If text is empty, show all items
            self._show_all_food_items()
            return

        # Convert to lowercase for case-insensitive search
        filter_text = text.lower()

        # Filter favorite food items
        if self.favorite_food_items_list_model:
            for i in range(self.favorite_food_items_list_model.rowCount()):
                item = self.favorite_food_items_list_model.item(i)
                if item:
                    item_text = item.text().lower()
                    # Hide/show row based on filter match
                    self.listView_favorite_food_items.setRowHidden(i, filter_text not in item_text)

        # Filter main food items
        if self.food_items_list_model:
            for i in range(self.food_items_list_model.rowCount()):
                item = self.food_items_list_model.item(i)
                if item:
                    item_text = item.text().lower()
                    # Hide/show row based on filter match
                    self.listView_food_items.setRowHidden(i, filter_text not in item_text)

    def _finish_window_initialization(self) -> None:
        """Finish window initialization by showing the window and adjusting columns."""
        self.show()
        # Adjust columns after window is shown and has proper dimensions
        QTimer.singleShot(50, self._adjust_food_log_table_columns)
        # Update food stats chart after initialization
        QTimer.singleShot(100, self._update_food_calories_chart)

    def _get_current_selected_food_item(self) -> str | None:
        """Get the currently selected food item from either list view.

        Returns:

        - `str | None`: The name of the selected food item, or None if nothing is selected.

        """
        # Check main food items list first
        selection_model = self.listView_food_items.selectionModel()
        if selection_model and self.food_items_list_model:
            current_index = selection_model.currentIndex()
            if current_index.isValid():
                item = self.food_items_list_model.itemFromIndex(current_index)
                if item:
                    return item.text()

        # Check favorite food items list if nothing selected in main list
        selection_model = self.listView_favorite_food_items.selectionModel()
        if selection_model and self.favorite_food_items_list_model:
            current_index = selection_model.currentIndex()
            if current_index.isValid():
                item = self.favorite_food_items_list_model.itemFromIndex(current_index)
                if item:
                    return item.text()

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

    def _init_favorite_food_items_list(self) -> None:
        """Initialize the favorite food items list view with a model and connect signals."""
        self.favorite_food_items_list_model = QStandardItemModel()
        self.listView_favorite_food_items.setModel(self.favorite_food_items_list_model)

        # Connect selection change signal after model is set
        selection_model = self.listView_favorite_food_items.selectionModel()
        if selection_model:
            selection_model.currentChanged.connect(self.on_food_item_selection_changed)

    def _init_food_items_list(self) -> None:
        """Initialize the food items list view with a model and connect signals."""
        self.food_items_list_model = QStandardItemModel()
        self.listView_food_items.setModel(self.food_items_list_model)

        # Connect selection change signal after model is set
        selection_model = self.listView_food_items.selectionModel()
        if selection_model:
            selection_model.currentChanged.connect(self.on_food_item_selection_changed)

    def _init_food_stats_dates(self) -> None:
        """Initialize food stats date range with last month as default."""
        if not self.db_manager or not self._validate_database_connection():
            return

        try:
            # Set default date range to last month
            today = QDate.currentDate()
            month_ago = today.addMonths(-1)

            # Check if we have data in the database
            earliest_date_str = self.db_manager.get_earliest_food_log_date()
            if earliest_date_str:
                earliest_date = QDate.fromString(earliest_date_str, "yyyy-MM-dd")
                if earliest_date.isValid():
                    # If earliest date is more recent than month ago, use earliest date
                    if earliest_date > month_ago:
                        self.dateEdit_food_stats_from.setDate(earliest_date)
                    else:
                        # Use month ago as default, but ensure it's not before earliest date
                        self.dateEdit_food_stats_from.setDate(max(month_ago, earliest_date))
                else:
                    # Fallback to month ago if date parsing fails
                    self.dateEdit_food_stats_from.setDate(month_ago)
            else:
                # No data in database, use month ago as default
                self.dateEdit_food_stats_from.setDate(month_ago)

                # Always set end date to today
            self.dateEdit_food_stats_to.setDate(today)

            # Update the chart with the new date range
            QTimer.singleShot(50, self._update_food_calories_chart)

        except Exception as e:
            print(f"Error getting earliest food log date: {e}")
            # Fallback to last month if any error occurs
            today = QDate.currentDate()
            month_ago = today.addMonths(-1)
            self.dateEdit_food_stats_from.setDate(month_ago)
            self.dateEdit_food_stats_to.setDate(today)

            # Update the chart with fallback date range
            QTimer.singleShot(50, self._update_food_calories_chart)

    def _on_autocomplete_selected(self, text: str) -> None:
        """Handle autocomplete selection and populate form fields."""
        if not text:
            return

        # Set the selected text
        self.lineEdit_food_manual_name.setText(text)

        # Trigger the food item selection logic
        self._populate_form_from_food_name(text)

        # Move focus to weight spinbox and select all text
        self.spinBox_food_weight.setFocus()
        self.spinBox_food_weight.selectAll()

    def _on_tab_changed(self, index: int) -> None:
        """Handle tab widget index change.

        Args:

        - `index` (`int`): Index of the newly selected tab.

        """
        # Get the widget at the current index
        current_widget = self.tabWidget.widget(index)
        if current_widget is None:
            return

        # Check if the current tab is the food stats tab
        if current_widget.objectName() == "tab_food_stats":
            self._update_kcal_per_day_table()
            self._update_food_calories_chart()

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

    def _on_window_resize(self, event) -> None:
        """Handle window resize event and adjust table column widths proportionally.

        Args:

        - `event`: The resize event.

        """
        # Call parent resize event first
        super().resizeEvent(event)

        # Adjust food log table column widths based on window size
        self._adjust_food_log_table_columns()

    def _populate_form_from_food_name(self, food_name: str) -> None:
        """Populate form fields based on food name from database."""
        if not self._validate_database_connection():
            return

        if self.db_manager is None:
            return

        try:
            # First try to get food item data from food_items table
            food_item_data = self.db_manager.get_food_item_by_name(food_name)

            if food_item_data:
                # food_item_data format: [_id, name, name_en, is_drink, calories_per_100g, default_portion_weight, default_portion_calories]
                (
                    food_id,
                    name,
                    name_en,
                    is_drink,
                    calories_per_100g,
                    default_portion_weight,
                    default_portion_calories,
                ) = food_item_data

                # Populate form fields
                self.spinBox_food_weight.setValue(int(default_portion_weight) if default_portion_weight else 100)
                self.checkBox_food_is_drink.setChecked(is_drink == 1)

                # Determine radio button state based on default_portion_calories
                if default_portion_calories and default_portion_calories > 0:
                    self.radioButton_use_calories.setChecked(True)
                    self.doubleSpinBox_food_calories.setValue(default_portion_calories)
                else:
                    self.radioButton_use_weight.setChecked(True)
                    self.doubleSpinBox_food_calories.setValue(calories_per_100g if calories_per_100g else 0)

            else:
                # If not found in food_items, try to get from food_log
                food_log_data = self.db_manager.get_food_log_item_by_name(food_name)

                if food_log_data:
                    # food_log_data format: [name, name_en, is_drink, calories_per_100g, weight, portion_calories]
                    name, name_en, is_drink, calories_per_100g, weight, portion_calories = food_log_data

                    # Populate form fields
                    self.spinBox_food_weight.setValue(int(weight) if weight else 100)
                    self.checkBox_food_is_drink.setChecked(is_drink == 1)

                    # Determine radio button state based on portion_calories
                    if portion_calories and portion_calories > 0:
                        self.radioButton_use_calories.setChecked(True)
                        self.doubleSpinBox_food_calories.setValue(portion_calories)
                    else:
                        self.radioButton_use_weight.setChecked(True)
                        self.doubleSpinBox_food_calories.setValue(calories_per_100g if calories_per_100g else 0)
                else:
                    # If not found in either table, set defaults
                    self.spinBox_food_weight.setValue(100)
                    self.checkBox_food_is_drink.setChecked(False)
                    self.radioButton_use_weight.setChecked(True)
                    self.doubleSpinBox_food_calories.setValue(0)

            # Update calories calculation
            self.update_calories_calculation()

        except Exception as e:
            print(f"Error populating form from food name: {e}")

    def _setup_autocomplete(self) -> None:
        """Setup autocomplete functionality for food name input."""
        from PySide6.QtCore import QStringListModel, Qt
        from PySide6.QtWidgets import QCompleter

        # Create completer
        self.food_completer = QCompleter(self)
        self.food_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.food_completer.setFilterMode(Qt.MatchFlag.MatchContains)  # Поиск по содержимому
        self.food_completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)

        # Create model for completer
        self.food_completer_model = QStringListModel(self)
        self.food_completer.setModel(self.food_completer_model)

        # Set completer to the line edit
        self.lineEdit_food_manual_name.setCompleter(self.food_completer)

        # Update autocomplete data
        self._update_autocomplete_data()

        # Connect selection signal
        self.food_completer.activated.connect(self._on_autocomplete_selected)

    def _setup_ui(self) -> None:
        """Set up additional UI elements after basic initialization."""
        # Set emoji for buttons
        self.pushButton_food_add.setText(f"🍽️ {self.pushButton_food_add.text()}")
        self.pushButton_food_item_add.setText(f"➕ {self.pushButton_food_item_add.text()}")
        self.pushButton_food_yesterday.setText(f"📅 {self.pushButton_food_yesterday.text()}")
        self.pushButton_food_delete.setText(f"🗑️ {self.pushButton_food_delete.text()}")
        self.pushButton_food_refresh.setText(f"🔄 {self.pushButton_food_refresh.text()}")
        self.pushButton_show_all_records.setText(f"📊 {self.pushButton_show_all_records.text()}")

        # Set emoji for food stats buttons
        self.pushButton_food_stats_last_week.setText(f"📅 {self.pushButton_food_stats_last_week.text()}")
        self.pushButton_food_stats_last_month.setText(f"📅 {self.pushButton_food_stats_last_month.text()}")
        self.pushButton_food_stats_last_year.setText(f"📅 {self.pushButton_food_stats_last_year.text()}")
        self.pushButton_food_stats_all_time.setText(f"📅 {self.pushButton_food_stats_all_time.text()}")
        self.pushButton_food_stats_food_weight.setText(f"⚖️ {self.pushButton_food_stats_food_weight.text()}")
        self.pushButton_food_stats_drink.setText(f"🥤 {self.pushButton_food_stats_drink.text()}")
        self.pushButton_food_stats_update.setText(f"🔄 {self.pushButton_food_stats_update.text()}")

        # Set decimal places for calorie spin boxes
        self.doubleSpinBox_food_calories.setDecimals(1)
        self.doubleSpinBox_food_cal100.setDecimals(1)
        self.doubleSpinBox_food_default_cal.setDecimals(1)

        # Export button removed from UI

        # Configure food splitter proportions
        self.splitter_food.setStretchFactor(0, 0)  # frame_food_controls with fixed size
        self.splitter_food.setStretchFactor(1, 1)  # widget_food_middle gets less space
        self.splitter_food.setStretchFactor(2, 3)  # tableView_food_log gets more space

        # Set initial radio button state and update calories calculation
        self.radioButton_use_weight.setChecked(True)
        self.update_calories_calculation()

        # Initialize food stats date range (will be set after database initialization)
        today = QDate.currentDate()
        month_ago = today.addMonths(-1)
        self.dateEdit_food_stats_from.setDate(month_ago)
        self.dateEdit_food_stats_to.setDate(today)

        # Keep default period as "Days" for food stats
        # (but date range will be set to last month)

        # Set focus to the food name input field for quick data entry
        self.lineEdit_food_manual_name.setFocus()

    def _setup_window_size_and_position(self) -> None:
        """Set window size and position based on screen resolution and characteristics."""
        screen_geometry = QApplication.primaryScreen().geometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        # Determine window size and position based on screen characteristics
        aspect_ratio = screen_width / screen_height
        is_standard_aspect = aspect_ratio <= 2.0  # Standard aspect ratio (16:9, 16:10, etc.)

        if is_standard_aspect and screen_width >= 1920:
            # For standard aspect ratios with width >= 1920, maximize window
            self.showMaximized()
        else:
            title_bar_height = 30  # Approximate title bar height
            windows_task_bar_height = 48  # Approximate windows task bar height
            # For other cases, use fixed width and full height minus title bar
            window_width = 1920
            window_height = screen_height - title_bar_height - windows_task_bar_height
            # Position window on screen
            screen_center = screen_geometry.center()
            # Center horizontally, position at top vertically with title bar offset
            self.setGeometry(
                screen_center.x() - window_width // 2,
                title_bar_height,  # Position below title bar
                window_width,
                window_height,
            )

    def _show_all_food_items(self) -> None:
        """Show all food items in both lists (remove filtering)."""
        # Show all favorite food items
        if self.favorite_food_items_list_model:
            for i in range(self.favorite_food_items_list_model.rowCount()):
                self.listView_favorite_food_items.setRowHidden(i, False)

        # Show all main food items
        if self.food_items_list_model:
            for i in range(self.food_items_list_model.rowCount()):
                self.listView_food_items.setRowHidden(i, False)

    def _update_autocomplete_data(self) -> None:
        """Update autocomplete data from database."""
        if not self._validate_database_connection():
            return

        if self.db_manager is None:
            return

        try:
            # Get recent food names for autocomplete
            recent_names = self.db_manager.get_recent_food_names_for_autocomplete(100)

            # Update completer model
            if self.food_completer_model is not None:
                self.food_completer_model.setStringList(recent_names)

        except Exception as e:
            print(f"Error updating autocomplete data: {e}")

    def _update_drinks_chart(self) -> None:
        """Update the drinks chart with data from database."""
        if not self._validate_database_connection():
            print("Database connection not available for updating drinks chart")
            return

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            # Get date range from UI
            date_from = self.dateEdit_food_stats_from.date().toString("yyyy-MM-dd")
            date_to = self.dateEdit_food_stats_to.date().toString("yyyy-MM-dd")
            period = self.comboBox_food_stats_period.currentText()

            # Get drinks weight data for the selected period
            weight_data = self.db_manager.get_drinks_weight_per_day()

            # Filter data by date range
            filtered_data = []
            for row in weight_data:
                date_str = str(row[0]) if row[0] is not None else ""
                weight_grams = row[1] if row[1] is not None else 0.0

                if date_from <= date_str <= date_to:
                    # Convert grams to liters (1 liter = 1000 grams)
                    weight_liters = weight_grams / 1000.0
                    filtered_data.append((date_str, weight_liters))

            # Group data by period
            grouped_data = self._group_data_by_period(filtered_data, period, "float")

            # Convert to list of tuples for chart
            chart_data = [(date, value) for date, value in grouped_data.items()]

            # Create chart configuration
            chart_config = {
                "title": f"Drinks Consumed ({period})",
                "xlabel": "Date",
                "ylabel": "Volume (liters)",
                "color": "cyan",
                "show_stats": True,
                "stats_unit": "L",
                "period": period,
                "fill_zero_periods": True,
                "date_from": date_from,
                "date_to": date_to,
                "is_calories_chart": False,  # Not calories chart
            }

            # Create chart
            layout = self.scrollAreaWidgetContents_food_stats.layout()
            if layout is not None:
                self._create_chart(layout, chart_data, chart_config)

        except Exception as e:
            print(f"Error updating drinks chart: {e}")
            QMessageBox.warning(self, "Chart Error", f"Failed to create drinks chart: {e}")

    def _update_favorite_food_items_list(self) -> None:
        """Refresh favorite food items list view with popular items from database."""
        if not self._validate_database_connection():
            print("Database manager not available or connection not open")
            return

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            # Get popular food items from recent records (top 22)
            popular_food_items = self.db_manager.get_popular_food_items(500)[:22]

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

    def _update_food_calories_chart(self) -> None:
        """Update the food calories chart with data from database."""
        if not self._validate_database_connection():
            print("Database connection not available for updating food calories chart")
            return

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            # Get date range from UI
            date_from = self.dateEdit_food_stats_from.date().toString("yyyy-MM-dd")
            date_to = self.dateEdit_food_stats_to.date().toString("yyyy-MM-dd")
            period = self.comboBox_food_stats_period.currentText()

            # Get calories data for the selected period
            kcal_data = self.db_manager.get_calories_per_day()

            # Filter data by date range
            filtered_data = []
            for row in kcal_data:
                date_str = str(row[0]) if row[0] is not None else ""
                calories = row[1] if row[1] is not None else 0.0

                if date_from <= date_str <= date_to:
                    filtered_data.append((date_str, calories))

            # Group data by period
            grouped_data = self._group_data_by_period(filtered_data, period, "float")

            # Convert to list of tuples for chart
            chart_data = [(date, value) for date, value in grouped_data.items()]

            # Create chart configuration
            chart_config = {
                "title": f"Calories Consumed ({period})",
                "xlabel": "Date",
                "ylabel": "Calories (kcal)",
                "color": "blue",
                "show_stats": True,
                "stats_unit": "kcal",
                "period": period,
                "fill_zero_periods": True,
                "date_from": date_from,
                "date_to": date_to,
                "is_calories_chart": True,  # Add this parameter
            }

            # Create chart
            layout = self.scrollAreaWidgetContents_food_stats.layout()
            if layout is not None:
                self._create_chart(layout, chart_data, chart_config)

        except Exception as e:
            print(f"Error updating food calories chart: {e}")
            QMessageBox.warning(self, "Chart Error", f"Failed to create calories chart: {e}")

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

    def _update_food_log_table(self) -> None:
        """Update the food log table based on current display state."""
        if not self._validate_database_connection():
            print("Database connection not available for updating food log table")
            return

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:

            def transform_food_log_data(rows: list[list]) -> list[list]:
                """Transform food_log data with coloring.

                Args:
                    rows (list[list]): Raw food_log data from database.

                Returns:
                    list[list]: Transformed food_log data.
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
                    # [name, is_drink, weight, calories_per_100g, portion_calories, calculated_calories, date, name_en]

                    # Check if portion_calories is non-zero, then hide calories_per_100g if it's 0
                    portion_calories = row[3]
                    calories_per_100g = row[4]
                    weight = row[2]

                    # If portion_calories is non-zero and calories_per_100g is 0, show empty string for calories_per_100g
                    # But if portion_calories is 0 (like water), show the 0 for calories_per_100g
                    if portion_calories and portion_calories > 0 and (not calories_per_100g or calories_per_100g == 0):
                        calories_per_100g_display = ""
                    else:
                        calories_per_100g_display = calories_per_100g if calories_per_100g is not None else ""

                    # Calculate total calories
                    calculated_calories = 0.0
                    if portion_calories and portion_calories > 0:
                        # Use portion calories directly
                        calculated_calories = float(portion_calories)
                    elif calories_per_100g and calories_per_100g > 0 and weight and weight > 0:
                        # Calculate from weight and calories per 100g
                        calculated_calories = (float(calories_per_100g) * float(weight)) / 100

                    transformed_row = [
                        row[5],
                        "1" if row[7] == 1 else "",
                        row[2],
                        calories_per_100g_display,
                        portion_calories,
                        f"{calculated_calories:.1f}",
                        row[1],
                        row[6],
                    ]

                    # Add color information based on date
                    date_str = row[1]
                    date_color = date_to_color.get(date_str, QColor(255, 255, 255))  # White as fallback

                    # Add original ID and color to the row for later use
                    transformed_row.extend(
                        [row[0], date_color]
                    )  # [name, is_drink, weight, calories_per_100g, portion_calories, calculated_calories, date, name_en, id, color]
                    transformed_rows.append(transformed_row)

                return transformed_rows

            # Get food_log data based on current state
            if self.show_all_food_records:
                # Get all records
                food_log_rows = self.db_manager.get_all_food_log_records()
            else:
                # Get recent records (last 5000)
                food_log_rows = self.db_manager.get_recent_food_log_records(5000)

            transformed_food_log_data = transform_food_log_data(food_log_rows)

            # Create food_log table model with coloring
            self.models["food_log"] = self._create_colored_food_log_table_model(
                transformed_food_log_data, self.table_config["food_log"][2]
            )
            self.tableView_food_log.setModel(self.models["food_log"])

            # Enable editing for the table
            self.tableView_food_log.setEditTriggers(
                QTableView.EditTrigger.DoubleClicked | QTableView.EditTrigger.EditKeyPressed
            )

            # Configure food_log table header - interactive mode for all columns
            food_log_header = self.tableView_food_log.horizontalHeader()
            # Set all columns to interactive (resizable)
            for i in range(food_log_header.count()):
                food_log_header.setSectionResizeMode(i, food_log_header.ResizeMode.Interactive)
            # Set proportional column widths for all columns
            self._adjust_food_log_table_columns()

            # Connect selection change signals after models are set
            self._connect_table_selection_signals()

            # Connect auto-save signals after all models are created
            self._connect_table_auto_save_signals()

        except Exception as e:
            print(f"Error updating food log table: {e}")
            QMessageBox.warning(self, "Database Error", f"Failed to update food log table: {e}")

    def _update_food_weight_chart(self) -> None:
        """Update the food weight chart with data from database."""
        if not self._validate_database_connection():
            print("Database connection not available for updating food weight chart")
            return

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            # Get date range from UI
            date_from = self.dateEdit_food_stats_from.date().toString("yyyy-MM-dd")
            date_to = self.dateEdit_food_stats_to.date().toString("yyyy-MM-dd")
            period = self.comboBox_food_stats_period.currentText()

            # Get food weight data for the selected period
            weight_data = self.db_manager.get_food_weight_per_day()

            # Filter data by date range
            filtered_data = []
            for row in weight_data:
                date_str = str(row[0]) if row[0] is not None else ""
                weight_grams = row[1] if row[1] is not None else 0.0

                if date_from <= date_str <= date_to:
                    # Convert grams to kilograms
                    weight_kg = weight_grams / 1000.0
                    filtered_data.append((date_str, weight_kg))

            # Group data by period
            grouped_data = self._group_data_by_period(filtered_data, period, "float")

            # Convert to list of tuples for chart
            chart_data = [(date, value) for date, value in grouped_data.items()]

            # Create chart configuration
            chart_config = {
                "title": f"Food Weight Consumed ({period})",
                "xlabel": "Date",
                "ylabel": "Weight (kg)",
                "color": "green",
                "show_stats": True,
                "stats_unit": "kg",
                "period": period,
                "fill_zero_periods": True,
                "date_from": date_from,
                "date_to": date_to,
                "is_calories_chart": False,  # Not calories chart
            }

            # Create chart
            layout = self.scrollAreaWidgetContents_food_stats.layout()
            if layout is not None:
                self._create_chart(layout, chart_data, chart_config)

        except Exception as e:
            print(f"Error updating food weight chart: {e}")
            QMessageBox.warning(self, "Chart Error", f"Failed to create food weight chart: {e}")

    def _update_kcal_per_day_table(self) -> None:
        """Update the calories per day table with data from database."""
        if not self._validate_database_connection():
            print("Database connection not available for updating kcal per day table")
            return

        if self.db_manager is None:
            print("❌ Database manager is not initialized")
            return

        try:
            # Get calories per day data for all days
            kcal_per_day_data = self.db_manager.get_calories_per_day()

            # Transform data for display
            transformed_data = []
            for row in kcal_per_day_data:
                date_str = str(row[0]) if row[0] is not None else ""
                calories = row[1] if row[1] is not None else 0.0
                # Format calories to 1 decimal place
                calories_str = f"{float(calories):.1f}" if calories else "0.0"
                transformed_data.append([date_str, calories_str])

            # Create colored table model
            self.models["kcal_per_day"] = self._create_colored_kcal_per_day_table_model(
                transformed_data, self.table_config["kcal_per_day"][2]
            )
            self.tableView_kcal_per_day.setModel(self.models["kcal_per_day"])

            # Configure table header
            kcal_per_day_header = self.tableView_kcal_per_day.horizontalHeader()
            # Set all columns to interactive (resizable)
            for i in range(kcal_per_day_header.count()):
                kcal_per_day_header.setSectionResizeMode(i, kcal_per_day_header.ResizeMode.Interactive)
            # Set proportional column widths
            self._adjust_kcal_per_day_table_columns()

        except Exception as e:
            print(f"Error updating kcal per day table: {e}")
            QMessageBox.warning(self, "Database Error", f"Failed to load calories per day data: {e}")

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
    # Window will be shown after initialization in _finish_window_initialization
    sys.exit(app.exec())
