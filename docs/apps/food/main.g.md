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
  - [⚙️ Method `closeEvent`](#%EF%B8%8F-method-closeevent)
  - [⚙️ Method `delete_record`](#%EF%B8%8F-method-delete_record)
  - [⚙️ Method `keyPressEvent`](#%EF%B8%8F-method-keypressevent)
  - [⚙️ Method `on_add_as_text`](#%EF%B8%8F-method-on_add_as_text)
  - [⚙️ Method `on_add_food_item`](#%EF%B8%8F-method-on_add_food_item)
  - [⚙️ Method `on_add_food_log`](#%EF%B8%8F-method-on_add_food_log)
  - [⚙️ Method `on_check_problematic_records`](#%EF%B8%8F-method-on_check_problematic_records)
  - [⚙️ Method `on_clear_food_manual_name`](#%EF%B8%8F-method-on_clear_food_manual_name)
  - [⚙️ Method `on_export_csv`](#%EF%B8%8F-method-on_export_csv)
  - [⚙️ Method `on_export_excel`](#%EF%B8%8F-method-on_export_excel)
  - [⚙️ Method `on_food_add_by_voice`](#%EF%B8%8F-method-on_food_add_by_voice)
  - [⚙️ Method `on_food_add_with_ai`](#%EF%B8%8F-method-on_food_add_with_ai)
  - [⚙️ Method `on_food_dashboard_add_photo`](#%EF%B8%8F-method-on_food_dashboard_add_photo)
  - [⚙️ Method `on_food_dashboard_add_text`](#%EF%B8%8F-method-on_food_dashboard_add_text)
  - [⚙️ Method `on_food_dashboard_add_voice`](#%EF%B8%8F-method-on_food_dashboard_add_voice)
  - [⚙️ Method `on_food_item_double_clicked`](#%EF%B8%8F-method-on_food_item_double_clicked)
  - [⚙️ Method `on_food_log_table_cell_clicked`](#%EF%B8%8F-method-on_food_log_table_cell_clicked)
  - [⚙️ Method `on_food_stats_all_time`](#%EF%B8%8F-method-on_food_stats_all_time)
  - [⚙️ Method `on_food_stats_drink`](#%EF%B8%8F-method-on_food_stats_drink)
  - [⚙️ Method `on_food_stats_food_weight`](#%EF%B8%8F-method-on_food_stats_food_weight)
  - [⚙️ Method `on_food_stats_last_month`](#%EF%B8%8F-method-on_food_stats_last_month)
  - [⚙️ Method `on_food_stats_last_week`](#%EF%B8%8F-method-on_food_stats_last_week)
  - [⚙️ Method `on_food_stats_last_year`](#%EF%B8%8F-method-on_food_stats_last_year)
  - [⚙️ Method `on_food_stats_period_changed`](#%EF%B8%8F-method-on_food_stats_period_changed)
  - [⚙️ Method `on_food_stats_update`](#%EF%B8%8F-method-on_food_stats_update)
  - [⚙️ Method `on_kcal_with_ai`](#%EF%B8%8F-method-on_kcal_with_ai)
  - [⚙️ Method `on_main_food_item_selection_changed`](#%EF%B8%8F-method-on_main_food_item_selection_changed)
  - [⚙️ Method `on_portion_weight_with_ai_from_calories`](#%EF%B8%8F-method-on_portion_weight_with_ai_from_calories)
  - [⚙️ Method `on_show_all_records_clicked`](#%EF%B8%8F-method-on_show_all_records_clicked)
  - [⚙️ Method `on_translate_with_ai`](#%EF%B8%8F-method-on_translate_with_ai)
  - [⚙️ Method `resizeEvent`](#%EF%B8%8F-method-resizeevent)
  - [⚙️ Method `set_today_date`](#%EF%B8%8F-method-set_today_date)
  - [⚙️ Method `show_tables`](#%EF%B8%8F-method-show_tables)
  - [⚙️ Method `update_calories_calculation`](#%EF%B8%8F-method-update_calories_calculation)
  - [⚙️ Method `update_food_calories_today`](#%EF%B8%8F-method-update_food_calories_today)
  - [⚙️ Method `update_food_data`](#%EF%B8%8F-method-update_food_data)

</details>

## 🏛️ Class `MainWindow`

```python
class MainWindow(QMainWindow, window.Ui_MainWindow, AppWindowMixin, TableOperations, ChartOperations, DateOperations, AutoSaveOperations, ValidationOperations)
```

Main application window for the food tracking application.

This class implements the main GUI window for the food tracker, providing
functionality to record food items and track food consumption.
It manages database operations for storing and retrieving food data.

Attributes:

- `_SAFE_TABLES` (`frozenset[str]`): Set of table names that can be safely modified,
  containing `food_log`.
- `db_manager` (`database_manager.DatabaseManager | None`): Database
  connection manager. Defaults to `None` until initialized.
- `models` (`dict[str, QSortFilterProxyModel | None]`): Dictionary of table models keyed
  by table name. All values default to `None` until tables are loaded.
- `table_config` (`dict[str, tuple[QTableView, str, list[str]]]`): Configuration for each
  table, mapping table names to tuples of (table view widget, model key, column headers).
- `food_items_list_model` (`QStandardItemModel | None`): Model for the food items list view.
  Defaults to `None` until initialized.

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
        {"food_log"},
    )
    about_app_name = "Food tracker"
    about_description = "Track food intake, calories, and drinks."

    def __init__(self, *, hide_on_close: bool = False) -> None:  # noqa: D107
        super().__init__()
        try_apply_system_backdrop(self, backdrop=SystemBackdrop.MICA)
        self.setupUi(self)
        self._food_dashboard: FoodDashboardWidget | None = None
        self._setup_ui()

        # Set window icon
        self.setWindowIcon(QIcon(":/assets/logo.svg"))

        self._init_hide_on_close(hide_on_close=hide_on_close)

        # Initialize core attributes
        self._is_closing = False
        self.db_manager: database_manager.DatabaseManager | None = None
        self._app_config: dict[str, Any] = h.dev.config_load(get_config_path_str())

        # Food items list model
        self.food_items_list_model: QStandardItemModel | None = None

        # Table models dictionary
        self.models: dict[str, QSortFilterProxyModel | None] = {
            "food_log": None,
            "kcal_per_day": None,
        }

        # Food log display state
        initial_count, load_more_count = get_apps_list_limits(self._app_config)
        self.count_food_records_to_show: int = initial_count
        self.food_log_load_more_count: int = load_more_count
        self.name_autocomplete_log_limit: int = initial_count
        self.show_all_food_records: bool = False

        # Food log table pagination state
        self._food_log_pagination = ScrollPagination()
        self._food_log_dates_with_totals: set[str] = set()
        self._food_log_date_color_map: dict[str, QColor] = {}

        # Dialog state to prevent multiple dialogs
        self._food_item_dialog_open: bool = False
        self._bothub_state = BothubRequestState()

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
                    "Total per day",
                ],
            ),
            "kcal_per_day": (
                self.tableView_kcal_per_day,
                "kcal_per_day",
                ["Date", "Calories"],
            ),
        }

        # Define colors for different dates (expanded palette)
        self.date_colors = generate_pastel_qcolors(50)

        # Chart configuration
        self.max_count_points_in_charts = 50

        # Initialize application
        self._init_database()
        self._setup_autocomplete()
        self._connect_signals()
        self._init_food_log_table_delegates()
        self._init_food_items_list()
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
        if self._hide_instead_of_close(event):
            return

        self._is_closing = True

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
            logger.error("❌ Database manager is not initialized")
            return

        # Use appropriate database manager method
        success = False
        try:
            if table_name == "food_log":
                success = self.db_manager.delete_food_log_record(record_id)
        except Exception as e:
            message_box.warning(self, "Database Error", f"Failed to delete record: {e}")
            return

        if success:
            self.update_food_data()
        else:
            message_box.warning(self, "Error", f"Deletion failed in {table_name}")

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        """Handle key press events for the main window.

        Args:

        - `event` (`QKeyEvent`): The key press event.

        """
        if self._handle_ctrl_c_for_tables(event, [self.tableView_food_log]):
            return

        # Handle Enter key on various widgets to trigger add button
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            focused_widget = QApplication.focusWidget()
            if focused_widget in (
                self.doubleSpinBox_food_calories,
                self.spinBox_food_weight,
                self.checkBox_food_is_drink,
                self.pushButton_food_add,
            ):
                self.pushButton_food_add.click()
                return

        # Handle Delete key on tableView_food_log to trigger delete button

        # Call parent implementation for other key events
        super().keyPressEvent(event)

    def on_add_as_text(self) -> None:
        """Open text input dialog and process entered food items."""
        if not self._validate_database_connection():
            message_box.warning(self, "Error", "Database connection not available")
            return
        self._open_text_input_dialog(self.dateEdit_food.date())

    @requires_database()
    def on_add_food_item(self) -> None:
        """Create a new food item via the edit dialog (prefilled from manual food entry form)."""
        name = self.lineEdit_food_manual_name.text().strip()
        if not name:
            message_box.warning(self, "Error", "Enter food name")
            return

        if self.db_manager is None:
            logger.error("❌ Database manager is not initialized")
            return

        try:
            is_drink = self.checkBox_food_is_drink.isChecked()
            weight = float(self.spinBox_food_weight.value())
            calories_value = float(self.doubleSpinBox_food_calories.value())
            use_weight = self.radioButton_use_weight.isChecked()

            if use_weight:
                calories_per_100g = calories_value if calories_value > 0 else None
                portion_calories = None
            else:
                calories_per_100g = None
                portion_calories = calories_value if calories_value > 0 else None

            prefill = database_manager.FoodLogItemByNameRow(
                name=name,
                name_en=None,
                is_drink=is_drink,
                calories_per_100g=calories_per_100g,
                weight=weight if weight > 0 else None,
                portion_calories=portion_calories,
            )

            dialog = FoodItemDialog(self, prefill, is_create=True)
            if dialog.exec() != QDialog.DialogCode.Accepted:
                return

            data = dialog.get_edited_data()
            if not self.db_manager.add_food_item(
                name=str(data["name"]),
                name_en=data["name_en"],
                is_drink=bool(data["is_drink"]),
                calories_per_100g=data["calories_per_100g"],
                default_portion_weight=data["default_portion_weight"],
                default_portion_calories=data["default_portion_calories"],
            ):
                message_box.warning(self, "Error", "Failed to add food item")
                return

            self.update_food_data()

        except Exception as e:
            message_box.warning(self, "Database Error", f"Failed to add food item: {e}")

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
            message_box.warning(self, "Error", "Enter food name")
            return

        if weight <= 0:
            message_box.warning(self, "Error", "Weight is required")
            self.spinBox_food_weight.setFocus()
            self.spinBox_food_weight.selectAll()
            return

        # Validate calories based on radio button selection
        if not use_weight and calories <= 0:
            message_box.warning(self, "Error", "Calories are required when using portion mode")
            return

        # Validate the date
        if not self._is_valid_date(food_date):
            message_box.warning(self, "Error", "Invalid date format")
            return

        if self.db_manager is None:
            logger.error("❌ Database manager is not initialized")
            return

        try:
            # Double-check radio button state before processing
            use_weight_final = self.radioButton_use_weight.isChecked()

            # Determine calories_per_100g and portion_calories based on radio button
            if use_weight_final:
                # Weight mode: calories is calories_per_100g
                calories_per_100g = max(0, calories)
                portion_calories = None
            else:
                # Portion mode: calories is portion_calories, set calories_per_100g to 0
                calories_per_100g = 0  # Required by database schema (NOT NULL)
                portion_calories = calories if calories > 0 else None

            # Reuse an existing English translation for the same food name, if any.
            known_translations = self.db_manager.lookup_existing_name_en_for_names([food_name])
            name_en = known_translations.get(food_name)

            # Use database manager method
            if self.db_manager.add_food_log_record(
                date=food_date,
                calories_per_100g=calories_per_100g,
                name=food_name,
                name_en=name_en,
                weight=weight,
                portion_calories=portion_calories,
                is_drink=is_drink,
            ):
                # Update UI - only food-related data
                self.update_food_data()

                # Clear form fields after successful addition
                self.lineEdit_food_manual_name.clear()
                self.spinBox_food_weight.setValue(0)
                self.doubleSpinBox_food_calories.setValue(0.0)
                self.checkBox_food_is_drink.setChecked(False)

                # Reset radio buttons to default state
                self.radioButton_use_weight.setChecked(True)
                self.radioButton_use_calories.setChecked(False)

                # Update button appearance and calories calculation
                self._update_add_button_appearance()
                self.update_calories_calculation()

                # Keep focus on food name field for next entry
                self.lineEdit_food_manual_name.setFocus()

            else:
                message_box.warning(self, "Error", "Failed to add food log record")

        except Exception as e:
            message_box.warning(self, "Database Error", f"Failed to add food log record: {e}")

    def on_check_problematic_records(self) -> None:
        """Filter food log table to show only problematic records."""
        if not self._validate_database_connection():
            message_box.warning(self, "Error", "Database connection not available")
            return

        if self.db_manager is None:
            logger.error("❌ Database manager is not initialized")
            return

        try:
            # Get problematic records from database
            problematic_records = self.db_manager.get_problematic_food_records()

            if not problematic_records:
                message_box.information(self, "No Issues", "No problematic records found!")
                return

            # Update the food log table with only problematic records
            self._update_food_log_table_with_data(problematic_records)

            missing_weight = sum(1 for row in problematic_records if self._food_log_row_missing_weight(row))
            missing_calories = sum(1 for row in problematic_records if self._food_log_row_missing_calories(row))
            details = [
                f"Found {len(problematic_records)} problematic record(s).",
                f"• Missing or zero weight: {missing_weight}",
                f"• Missing calories (non-drink): {missing_calories}",
            ]
            message_box.information(self, "Problematic Records", "\n".join(details))

        except Exception as e:
            message_box.warning(self, "Error", f"Failed to check problematic records: {e}")

    def on_clear_food_manual_name(self) -> None:
        """Clear the food manual name input field."""
        self.lineEdit_food_manual_name.clear()
        # Reset drink checkbox and button appearance
        self.checkBox_food_is_drink.setChecked(False)
        self._update_add_button_appearance()
        # Move focus back to the cleared field
        self.lineEdit_food_manual_name.setFocus()

    def on_export_csv(self) -> None:
        """Save current food log view as CSV (Excel is also offered)."""
        self._export_food_log_table(prefer="csv")

    def on_export_excel(self) -> None:
        """Save current food log view as Excel (CSV is also offered)."""
        self._export_food_log_table(prefer="xlsx")

    def on_food_add_by_voice(self) -> None:
        """Record speech, transcribe via BotHub, convert to food log TSV, then open preview dialog."""
        self._run_food_add_by_voice()

    @requires_database()
    def on_food_add_with_ai(
        self,
        *,
        initial_image_path: str | None = None,
        initial_image_paths: list[str] | None = None,
    ) -> None:
        """Collect text/images, call BotHub, then open food text dialog with AI result."""
        max_image_side = get_max_image_side(self._app_config)
        source_dialog = AiSourceDialog(
            self,
            max_image_side=max_image_side,
            initial_image_path=initial_image_path,
            initial_image_paths=initial_image_paths,
        )
        source_result = source_dialog.exec()
        if source_result == QDialog.DialogCode.Rejected:
            return
        if source_result == AiSourceDialog.SKIP_MANUAL:
            self._open_text_input_dialog(self.dateEdit_food.date())
            return

        self._send_food_log_to_ai(
            source_dialog.get_raw_text(),
            source_dialog.get_images_bytes_and_mime(),
        )

    def on_food_dashboard_add_photo(self) -> None:
        """Open a large photo-only form and send the image to AI."""
        if not self._validate_database_connection():
            message_box.warning(self, "Error", "Database connection not available")
            return
        source_dialog = create_food_dashboard_photo_dialog(
            self,
            max_image_side=get_max_image_side(self._app_config),
        )
        if source_dialog.exec() != QDialog.DialogCode.Accepted:
            return
        self._send_food_log_to_ai(
            source_dialog.get_raw_text(),
            source_dialog.get_images_bytes_and_mime(),
        )

    def on_food_dashboard_add_text(self) -> None:
        """Open a large text-only form and send the description to AI."""
        if not self._validate_database_connection():
            message_box.warning(self, "Error", "Database connection not available")
            return
        source_dialog = create_food_dashboard_text_dialog(self)
        if source_dialog.exec() != QDialog.DialogCode.Accepted:
            return
        self._send_food_log_to_ai(source_dialog.get_raw_text())

    def on_food_dashboard_add_voice(self) -> None:
        """Open a large recording form and send speech to AI."""
        self._run_food_add_by_voice(large_ui=True)

    def on_food_item_double_clicked(self, _index: QModelIndex) -> None:
        """Handle double click on food item in the list view.

        Args:

        - `_index` (`QModelIndex`): Index of the double-clicked item.

        """
        # Prevent multiple dialogs from opening
        if self._food_item_dialog_open:
            return

        food_item = self._get_current_selected_food_item()
        if not food_item:
            return

        # Check if database manager is available and connection is open
        if not self._validate_database_connection():
            logger.warning("Database manager not available or connection not open")
            return

        if self.db_manager is None:
            logger.error("❌ Database manager is not initialized")
            return

        try:
            # Set dialog open flag
            self._food_item_dialog_open = True

            # Get food item data from food_items table
            food_item_data = self.db_manager.get_food_item_by_name(food_item)

            if food_item_data:
                dialog = FoodItemDialog(self, food_item_data, is_create=False)
            else:
                food_log_data = self.db_manager.get_food_log_item_by_name(food_item)
                if not food_log_data:
                    message_box.warning(
                        self,
                        "Error",
                        f"Food item '{food_item}' not found in database or food log!",
                    )
                    return
                dialog = FoodItemDialog(self, food_log_data, is_create=True)

            result = dialog.exec_()

            # Only process if dialog was accepted (not cancelled)
            if result == QDialog.DialogCode.Accepted:
                if hasattr(dialog, "delete_confirmed") and dialog.delete_confirmed:
                    if not isinstance(food_item_data, database_manager.FoodItemByNameRow):
                        return
                    food_id = food_item_data.id
                    if self.db_manager.delete_food_item(food_id):
                        message_box.information(self, "Success", f"Food item '{food_item}' deleted successfully!")
                        self.update_food_data()
                    else:
                        message_box.warning(self, "Error", f"Failed to delete food item '{food_item}'!")
                else:
                    edited_data = dialog.get_edited_data()
                    if food_item_data:
                        food_id = food_item_data.id
                        if self.db_manager.update_food_item(
                            food_item_id=food_id,
                            name=edited_data["name"],
                            name_en=edited_data["name_en"],
                            is_drink=edited_data["is_drink"],
                            calories_per_100g=edited_data["calories_per_100g"],
                            default_portion_weight=edited_data["default_portion_weight"],
                            default_portion_calories=edited_data["default_portion_calories"],
                        ):
                            message_box.information(
                                self, "Success", f"Food item '{edited_data['name']}' updated successfully!"
                            )
                            self.update_food_data()
                        else:
                            message_box.warning(self, "Error", f"Failed to update food item '{edited_data['name']}'!")
                    elif self.db_manager.add_food_item(
                        name=edited_data["name"],
                        name_en=edited_data["name_en"],
                        is_drink=edited_data["is_drink"],
                        calories_per_100g=edited_data["calories_per_100g"],
                        default_portion_weight=edited_data["default_portion_weight"],
                        default_portion_calories=edited_data["default_portion_calories"],
                    ):
                        message_box.information(
                            self, "Success", f"Food item '{edited_data['name']}' created successfully!"
                        )
                        self.update_food_data()
                    else:
                        message_box.warning(self, "Error", f"Failed to create food item '{edited_data['name']}'!")

            # If result is Rejected (Cancel), do nothing - just close the dialog
            # No need for additional logic here

        except Exception as e:
            logger.exception("Error in food item double clicked")
            message_box.warning(self, "Error", f"Error editing food item: {e}")
        finally:
            # Always reset the dialog open flag
            self._food_item_dialog_open = False

    def on_food_log_table_cell_clicked(self, index: QModelIndex) -> None:
        """Handle food log table cell click and populate form fields with row data.

        Args:

        - `index` (`QModelIndex`): Index of the clicked cell.

        """
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
            name = source_model.item(index.row(), 0).text() if source_model.item(index.row(), 0) else ""
            is_drink_item = source_model.item(index.row(), 1)
            is_drink = parse_is_drink_cell(is_drink_item.data(Qt.ItemDataRole.EditRole)) if is_drink_item else False
            weight_str = source_model.item(index.row(), 2).text() if source_model.item(index.row(), 2) else "0"
            calories_per_100g_str = (
                source_model.item(index.row(), 3).text() if source_model.item(index.row(), 3) else "0"
            )
            portion_calories_str = (
                source_model.item(index.row(), 4).text() if source_model.item(index.row(), 4) else "0"
            )

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
            self._update_add_button_appearance()

            # Determine radio button state based on portion_calories
            if portion_calories > 0:
                # Use portion calories mode
                self.radioButton_use_calories.setChecked(True)
                self.doubleSpinBox_food_calories.setValue(portion_calories)
            else:
                # Use weight mode
                self.radioButton_use_weight.setChecked(True)
                self.doubleSpinBox_food_calories.setValue(calories_per_100g)

            # Update calories calculation
            self.update_calories_calculation()

            # Move focus to weight spinbox and select all text
            self.spinBox_food_weight.setFocus()
            self.spinBox_food_weight.selectAll()

        except Exception:
            logger.exception("Error in food log table cell clicked")

    def on_food_stats_all_time(self) -> None:
        """Set date range to all available data and update chart."""
        if not self.db_manager or not self._validate_database_connection():
            return

        try:
            # Get earliest date from database
            earliest_date_str = self.db_manager.get_earliest_food_log_date()
            if earliest_date_str:
                earliest_date = QDate.fromString(earliest_date_str, "yyyy-MM-dd")
                if QDate.isValid(earliest_date.year(), earliest_date.month(), earliest_date.day()):
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

        except Exception:
            logger.exception("Error setting all time date range")
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

    def on_kcal_with_ai(self) -> None:
        """Look up calories, drink flag, mode, and weight via BotHub from the food name."""
        food_name = self.lineEdit_food_manual_name.text().strip()
        if not food_name:
            message_box.warning(self, "Food Name", "Enter a food name first.")
            return

        try:
            prompt_text = build_prompt(self._app_config, "food_kcal_lookup", {"FOOD_NAME": food_name})
        except ValueError as exc:
            show_bothub_prompt_build_error(self, exc)
            return

        def on_success(response_text: str) -> None:
            result = parse_kcal_lookup_response(response_text)
            if result is None:
                preview = response_text.strip()[:200]
                message_box.warning(
                    self,
                    "AI Response",
                    "Could not parse BotHub response.\n\nExpected TSV: Calories, Mode, Drink, Weight\n\n"
                    f"Response:\n{preview}",
                )
                return
            self._apply_kcal_lookup_result(result)

        self._start_bothub_worker(prompt_text, on_success)

    def on_main_food_item_selection_changed(self, current: QModelIndex, _previous: QModelIndex) -> None:
        """Handle food item selection change in the list view.

        Args:

        - `current` (`QModelIndex`): Current selected index.
        - `_previous` (`QModelIndex`): Previously selected index.

        """
        if not current.isValid():
            return

        if self.food_items_list_model:
            item = self.food_items_list_model.itemFromIndex(current)
            if item:
                food_name = extract_food_name_from_display(item.text())
                self._process_food_item_selection(food_name)

    def on_portion_weight_with_ai_from_calories(self) -> None:
        """Determine portion weight and drink flag via BotHub for calories-mode entry."""
        if self.radioButton_use_weight.isChecked():
            message_box.warning(
                self,
                "Mode",
                "Switch to 'Enter calories directly' mode first.",
            )
            return

        food_name = self.lineEdit_food_manual_name.text().strip()
        if not food_name:
            message_box.warning(self, "Food Name", "Enter a food name first.")
            return

        calories_total = float(self.doubleSpinBox_food_calories.value())
        if calories_total <= 0:
            message_box.warning(self, "Calories", "Enter calories first.")
            return

        drink = "yes" if self.checkBox_food_is_drink.isChecked() else "no"
        try:
            prompt_text = build_prompt(
                self._app_config,
                "food_portion_weight_from_calories",
                {
                    "FOOD_NAME": food_name,
                    "CALORIES_TOTAL": f"{calories_total:.1f}",
                    "DRINK": drink,
                },
            )
        except ValueError as exc:
            show_bothub_prompt_build_error(self, exc)
            return

        def on_success(response_text: str) -> None:
            result = parse_portion_weight_response(response_text)
            if result is None:
                preview = response_text.strip()[:200]
                message_box.warning(
                    self,
                    "AI Response",
                    f"Could not parse BotHub response.\n\nExpected TSV: Drink, Weight\n\nResponse:\n{preview}",
                )
                return

            self.checkBox_food_is_drink.setChecked(result.is_drink)
            if result.weight_g > 0:
                self.spinBox_food_weight.setValue(result.weight_g)
            self.update_calories_calculation()
            self._update_add_button_appearance()

        self._start_bothub_worker(prompt_text, on_success)

    def on_show_all_records_clicked(self) -> None:
        """Toggle between showing all records and last self.count_food_records_to_show records."""
        self.show_all_food_records = not self.show_all_food_records

        # Update menu action text
        if self.show_all_food_records:
            set_action_text_with_emoji_icon(
                self.action_show_all_records,
                f"📊 Show Last {self.count_food_records_to_show}",
            )
        else:
            set_action_text_with_emoji_icon(self.action_show_all_records, "📊 Show All Records")

        # Refresh the food log table
        self._update_food_log_table()

    @requires_database()
    def on_translate_with_ai(self) -> None:
        """Translate missing food_log name_en values via BotHub from unique Russian names."""
        if self.db_manager is None:
            logger.error("❌ Database manager is not initialized")
            return

        unique_names_limit = self._food_log_translate_names_limit()
        names = self.db_manager.get_unique_food_log_names_missing_name_en(limit=unique_names_limit)
        if not names:
            self._report_food_translate_completion()
            return

        known_translations = self.db_manager.lookup_existing_name_en_for_names(names)
        filled_from_existing = 0
        if known_translations:
            filled_from_existing = self._commit_food_translate_translations(
                known_translations,
                show_completion=False,
            )

        names_for_ai = [name for name in names if name not in known_translations]
        if not names_for_ai:
            prefix = ""
            if filled_from_existing > 0:
                prefix = (
                    f"Filled English names for {filled_from_existing} unique food name(s) "
                    "from existing translations in the database."
                )
            self._report_food_translate_completion(prefix=prefix)
            return

        food_names_text = "\n".join(names_for_ai)
        try:
            prompt_text = build_prompt(
                self._app_config,
                "food_log_translate_names",
                {"FOOD_NAMES": food_names_text},
            )
        except ValueError as exc:
            show_bothub_prompt_build_error(self, exc)
            return

        def on_success(response_text: str) -> None:
            self._show_food_translate_preview(
                names_for_ai,
                response_text,
                unique_names_limit=unique_names_limit,
                filled_from_existing=filled_from_existing,
            )

        self._start_bothub_worker(prompt_text, on_success)

    def resizeEvent(self, _event: QResizeEvent) -> None:  # noqa: N802
        """Handle window resize event and adjust table column widths proportionally.

        Args:

        - `_event` (`QResizeEvent`): The resize event.

        """
        # Call parent resize event first
        super().resizeEvent(_event)

        # Adjust food log table column widths based on window size
        self._adjust_food_log_table_columns()

    def set_today_date(self) -> None:
        """Set today's date in the food date edit field."""
        today_qdate = QDate.currentDate()
        self.dateEdit_food.setDate(today_qdate)

    def show_tables(self) -> None:
        """Populate all QTableViews using database manager methods."""
        if not self._validate_database_connection():
            logger.warning("Database connection not available for showing tables")
            return

        if self.db_manager is None:
            logger.error("❌ Database manager is not initialized")
            return

        try:
            self._load_food_log_page(reset=True)
            self._connect_table_selection_signals()
            self._connect_table_auto_save_signals()
            self.update_food_calories_today()
        except Exception as e:
            logger.exception("Error showing tables")
            message_box.warning(self, "Database Error", f"Failed to load tables: {e}")

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
            logger.error("❌ Database manager is not initialized")
            return

        if not self._validate_database_connection():
            self.label_food_today.setText("0 kcal\n0,0 liters")
            if self._food_dashboard is not None:
                self._food_dashboard.set_today_calories(0)
            return

        try:
            calories = self.db_manager.get_food_calories_today()
            drinks_weight = self.db_manager.get_drinks_weight_today()
            drinks_liters = drinks_weight / 1000 if drinks_weight else 0.0
            drinks_liters_str = f"{drinks_liters:.1f}"
            self.label_food_today.setText(f"{calories:.1f} kcal \n{drinks_liters_str} liters")
            if self._food_dashboard is not None:
                self._food_dashboard.set_today_calories(calories)
        except Exception:
            logger.exception("Error getting food calories for today")
            self.label_food_today.setText("0 kcal\n0,0 liters")
            if self._food_dashboard is not None:
                self._food_dashboard.set_today_calories(0)

    def update_food_data(self) -> None:
        """Refresh food-related data only.

        Updates food items lists and calories count.

        """
        if not self._validate_database_connection():
            logger.warning("Database connection not available for update_food_data")
            return

        # Update food items list
        self._update_food_items_list()
        self._update_autocomplete_data()
        self.update_food_calories_today()
        self.show_tables()

    @requires_database()
    def _add_food_item_from_log_record(self, *, include_weight: bool = True) -> None:
        """Add a new food item to food_items table based on selected food log record.

        Args:

        - `include_weight` (`bool`): If `True`, includes the weight from the log record.
          If `False`, sets weight to zero. Defaults to `True`.

        """
        if self.db_manager is None:
            logger.error("❌ Database manager is not initialized")
            return

        try:
            # Get the selected row data from the table model
            proxy_model = self.models["food_log"]
            if proxy_model is None:
                return
            source_model = proxy_model.sourceModel()
            if not isinstance(source_model, QStandardItemModel):
                return

            current_index = self.tableView_food_log.currentIndex()
            if not current_index.isValid():
                message_box.warning(self, "Error", "No row selected")
                return

            row = current_index.row()

            # Get data from the table model directly
            name = source_model.item(row, 0).text() if source_model.item(row, 0) else ""
            is_drink_item = source_model.item(row, 1)
            is_drink_str = is_drink_item.data(Qt.ItemDataRole.EditRole) if is_drink_item else ""
            weight_str = source_model.item(row, 2).text() if source_model.item(row, 2) else "0"
            calories_per_100g_str = source_model.item(row, 3).text() if source_model.item(row, 3) else "0"
            portion_calories_str = source_model.item(row, 4).text() if source_model.item(row, 4) else "0"
            name_en = source_model.item(row, 7).text() if source_model.item(row, 7) else ""

            # Validate food name
            if not name.strip():
                message_box.warning(self, "Error", "Food name cannot be empty")
                return

            # Check if food item already exists
            existing_item = self.db_manager.get_food_item_by_name(name.strip())
            if existing_item:
                message_box.warning(self, "Error", f"Food item '{name.strip()}' already exists in food items table")
                return

            # Parse values
            is_drink = parse_is_drink_cell(is_drink_str)

            # Parse weight
            weight = None
            if include_weight and weight_str.strip():
                try:
                    weight = float(weight_str)
                    if weight <= 0:
                        weight = None
                except (ValueError, TypeError):
                    weight = None

            # Parse calories per 100g
            calories_per_100g = None
            if calories_per_100g_str.strip():
                try:
                    calories_per_100g = float(calories_per_100g_str)
                    if calories_per_100g <= 0:
                        calories_per_100g = None
                except (ValueError, TypeError):
                    calories_per_100g = None

            # Parse portion calories
            portion_calories = None
            if portion_calories_str.strip():
                try:
                    portion_calories = float(portion_calories_str)
                    if portion_calories <= 0:
                        portion_calories = None
                except (ValueError, TypeError):
                    portion_calories = None

            # Determine which values to use based on what's available
            # If portion_calories exists, use it as default_portion_calories
            # If calories_per_100g exists, use it
            # Use weight as default_portion_weight if include_weight is True

            default_portion_weight = weight if include_weight else None
            default_portion_calories = portion_calories
            final_calories_per_100g = calories_per_100g

            # Add the food item to database
            success = self.db_manager.add_food_item(
                name=name.strip(),
                name_en=name_en.strip() or None,
                is_drink=is_drink,
                calories_per_100g=final_calories_per_100g,
                default_portion_weight=default_portion_weight,
                default_portion_calories=default_portion_calories,
            )

            if success:
                # Update UI
                self.update_food_data()

                # Show success message with details
                weight_info = f" with weight {weight}g" if include_weight and weight else " without weight"
                calories_info = ""
                if final_calories_per_100g:
                    calories_info += f", {final_calories_per_100g} kcal/100g"
                if default_portion_calories:
                    calories_info += f", {default_portion_calories} kcal/portion"

                message_box.information(
                    self, "Success", f"Food item '{name.strip()}' added successfully{weight_info}{calories_info}!"
                )
            else:
                message_box.warning(self, "Error", "Failed to add food item to database")

        except Exception as e:
            message_box.warning(self, "Database Error", f"Failed to add food item: {e}")
            logger.exception("Error adding food item from log record")

    def _adjust_food_log_table_columns(self) -> None:
        """Adjust food log table column widths proportionally to window size."""
        if not hasattr(self, "tableView_food_log") or not self.tableView_food_log.model():
            return
        # Hidden tabs report a dummy width; wait until Food is actually shown.
        if not self.tableView_food_log.isVisible():
            return

        # Get current table width (approximate available width for table)
        table_width = self.tableView_food_log.width()
        if table_width <= 0:
            return

        # Ensure minimum table width for better appearance
        table_width = max(table_width, 800)

        # Reserve space for vertical headers, scrollbar, and borders
        vertical_header_width = self.tableView_food_log.verticalHeader().width()
        scrollbar_width = 20  # Approximate scrollbar width
        borders_and_margins = 10  # Space for borders and margins

        available_width = table_width - vertical_header_width - scrollbar_width - borders_and_margins

        # Define proportional distribution of available width
        # Total: 100% = 18% + 5% + 5% + 11% + 9% + 9% + 11% + 20% + 12%
        proportions = [
            0.18,  # Name
            0.05,  # Is Drink
            0.05,  # Weight
            0.11,  # Calories per 100g
            0.09,  # Portion Calories
            0.09,  # Calculated Calories
            0.11,  # Date
            0.20,  # English Name
            0.12,  # Total per day
        ]

        # Calculate widths based on proportions of available width
        column_widths = [int(available_width * prop) for prop in proportions]

        # Apply widths to all columns
        for i, width in enumerate(column_widths):
            self.tableView_food_log.setColumnWidth(i, width)
        food_log_header = self.tableView_food_log.horizontalHeader()
        if isinstance(food_log_header, WordWrapHeaderView):
            food_log_header.refresh_wrapped_height()

    def _adjust_kcal_per_day_table_columns(self) -> None:
        """Set column widths for kcal per day table."""
        if not hasattr(self, "tableView_kcal_per_day") or not self.tableView_kcal_per_day.model():
            return

        # Set first column (Date) to fixed width of 80px
        self.tableView_kcal_per_day.setColumnWidth(0, 80)

        # Set second column (Calories) to stretch to remaining space
        self.tableView_kcal_per_day.horizontalHeader().setStretchLastSection(True)

    def _after_table_data_changed(
        self,
        table_name: str,
        top_left: QModelIndex,
        bottom_right: QModelIndex,
    ) -> None:
        """Recalculate food-log day totals in the current model only."""
        if table_name != "food_log":
            return
        self._refresh_food_log_calories_after_edit(top_left, bottom_right)

    def _append_food_log_rows_to_model(self, model: QStandardItemModel, transformed_data: list[list]) -> None:
        """Append transformed food log rows to an existing source model."""
        start_row_idx: int = model.rowCount()
        today = QDateTime.currentDateTime().toString("yyyy-MM-dd")

        for row_offset, row in enumerate(transformed_data):
            row_idx: int = start_row_idx + row_offset
            row_color: QColor = row[10]
            row_id = row[9]
            items: list[QStandardItem] = []

            col_calculated_calories = 5
            col_date = 6
            col_total_per_day = 8
            for col_idx, value in enumerate(row[:9]):
                item = QStandardItem(str(value) if value is not None else "")
                item.setBackground(QBrush(row_color))

                if col_idx == col_calculated_calories:
                    item.setEditable(False)
                if col_idx == col_total_per_day:
                    item.setEditable(False)
                if col_idx == col_date and str(value) == today:
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)

                items.append(item)

            model.appendRow(items)
            model.setVerticalHeaderItem(row_idx, QStandardItem(str(row_id)))

    @requires_database()
    def _apply_eaten_fraction_to_selected_food_log(self, fraction: float) -> None:
        """Scale weight and, in portion mode, serving calories on selected rows."""
        if self.db_manager is None:
            return
        record_ids = self._get_selected_row_ids("food_log")
        if not record_ids:
            message_box.warning(self, "Error", "Select one or more food log rows")
            return
        if fraction <= 0 or fraction > 1:
            message_box.warning(self, "Error", "Percent eaten must be between 0 and 100")
            return

        updated = 0
        for record_id in record_ids:
            amounts = self.db_manager.get_food_log_amounts(record_id)
            if amounts is None:
                continue
            weight, _calories_per_100g, portion_calories = amounts
            new_weight, new_portion = scale_food_log_eaten_amounts(
                weight=weight,
                portion_calories=portion_calories,
                fraction=fraction,
            )
            if self.db_manager.update_food_log_weight_and_portion_calories(
                record_id,
                new_weight,
                new_portion,
            ):
                updated += 1

        if updated:
            self.update_food_data()
            return
        message_box.warning(self, "Error", "Failed to update selected food log rows")

    def _apply_kcal_lookup_result(self, result: KcalLookupResult) -> None:
        """Fill manual food entry fields from a parsed kcal lookup result."""
        self.radioButton_use_weight.setChecked(result.is_weight_mode)
        self.radioButton_use_calories.setChecked(not result.is_weight_mode)
        self.doubleSpinBox_food_calories.setValue(result.calories)
        self.checkBox_food_is_drink.setChecked(result.is_drink)
        if result.weight_g > 0:
            self.spinBox_food_weight.setValue(result.weight_g)
        self.update_calories_calculation()
        self._update_add_button_appearance()

    def _clear_food_log_table_filter(self) -> None:
        """Clear client-side filter on the food log table proxy."""
        proxy = self.models.get("food_log")
        if proxy is None:
            return
        proxy.setFilterRegularExpression(QRegularExpression())
        proxy.setFilterKeyColumn(-1)

    def _commit_food_translate_translations(
        self,
        translations: dict[str, str],
        *,
        show_completion: bool = True,
        prefix: str = "",
    ) -> int:
        """Write confirmed name → English mappings to food_log.

        Returns:

        - `int`: Number of unique names successfully updated.

        """
        if self.db_manager is None or not translations:
            if show_completion:
                self._report_food_translate_completion(prefix=prefix)
            return 0

        updated_names = 0
        failed_names: list[str] = []

        for name, name_en in translations.items():
            if self.db_manager.update_food_log_name_en_by_name(name, name_en):
                updated_names += 1
            else:
                failed_names.append(name)

        self.update_food_data()

        if show_completion:
            result_parts = []
            if prefix:
                result_parts.append(prefix)
            if updated_names > 0:
                result_parts.append(f"Updated English names for {updated_names} unique food name(s).")
            max_names_in_message = 8
            if failed_names:
                preview = ", ".join(failed_names[:max_names_in_message])
                suffix = "…" if len(failed_names) > max_names_in_message else ""
                result_parts.append(f"Database update failed ({len(failed_names)}): {preview}{suffix}")
            if updated_names == 0 and not failed_names and not prefix:
                result_parts.append("No records were updated.")
            self._report_food_translate_completion(prefix="\n\n".join(result_parts) if result_parts else "")

        return updated_names

    def _connect_signals(self) -> None:
        """Wire Qt widgets to their Python slots.

        Connects all UI elements to their respective handler methods, including:

        - Button click events for adding and deleting records
        - Auto-save signals for table data changes

        """
        self.action_refresh.triggered.connect(self.update_food_data)
        self._connect_exit_about_actions()

        # Window resize event is handled by overriding resizeEvent method

        # Connect tab widget signal for updating stats when switching to food stats tab
        self.tabWidget.currentChanged.connect(self._on_tab_changed)

        # Add buttons
        self.pushButton_food_add.clicked.connect(self.on_add_food_log)
        self.pushButton_food_add_with_ai.clicked.connect(self.on_food_add_with_ai)
        self.pushButton_food_add_by_voice.clicked.connect(self.on_food_add_by_voice)
        max_image_side = get_max_image_side(self._app_config)
        self._ai_image_drop_zone = ImagePicker(
            mode=ImagePickerMode.COMPACT,
            on_paths=self._on_food_add_with_ai_image_dropped,
            on_double_click=self.pushButton_food_add_with_ai.click,
            extra_drop_targets=[self.pushButton_food_add_with_ai],
            max_image_side=max_image_side,
        )
        self.verticalLayout_2.insertWidget(1, self._ai_image_drop_zone)
        self.pushButton_kcal_with_ai.clicked.connect(self.on_kcal_with_ai)
        self.action_add_food_item.triggered.connect(self.on_add_food_item)
        self.action_translate_with_ai.triggered.connect(self.on_translate_with_ai)
        self.action_add_as_text.triggered.connect(self.on_add_as_text)
        self.action_show_all_records.triggered.connect(self.on_show_all_records_clicked)
        self.action_check.triggered.connect(self.on_check_problematic_records)

        # Add context menu for kcal AI button (additional commands)
        self.pushButton_kcal_with_ai.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.pushButton_kcal_with_ai.customContextMenuRequested.connect(self._show_kcal_with_ai_context_menu)

        self.pushButton_food_manual_name_clear.clicked.connect(self.on_clear_food_manual_name)

        # Connect radio buttons and spin boxes for calories calculation
        self.radioButton_use_weight.clicked.connect(self.update_calories_calculation)
        self.radioButton_use_calories.clicked.connect(self.update_calories_calculation)
        self.spinBox_food_weight.valueChanged.connect(self.update_calories_calculation)
        self.doubleSpinBox_food_calories.valueChanged.connect(self.update_calories_calculation)

        # Add context menu for calories mode radio button
        self.radioButton_use_calories.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.radioButton_use_calories.customContextMenuRequested.connect(self._show_use_calories_context_menu)

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

        # Connect drink checkbox for button appearance update
        self.checkBox_food_is_drink.toggled.connect(self._update_add_button_appearance)

    def _connect_table_selection_signals(self) -> None:
        """Connect selection change signals for all tables."""
        selection_model = self.listView_food_items.selectionModel()
        if selection_model:
            selection_model.currentChanged.connect(self.on_main_food_item_selection_changed)

        self.listView_food_items.doubleClicked.connect(self.on_food_item_double_clicked)

        # Connect food log table cell click
        self.tableView_food_log.clicked.connect(self.on_food_log_table_cell_clicked)

        # Add context menu for food log table
        self.tableView_food_log.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tableView_food_log.customContextMenuRequested.connect(self._show_food_log_context_menu)

        # Load more food log rows when scrolling near the bottom
        self.tableView_food_log.verticalScrollBar().valueChanged.connect(self._on_food_log_scroll)

    def _correct_food_input_line(self, line: str) -> str | None:
        """Ask user to correct one unparseable input line (UI responsibility)."""
        corrected_line, ok = QInputDialog.getText(
            self,
            "Correct Line",
            f"Unable to parse line: '{line}'\nPlease correct it or leave empty to skip:",
            text=line,
        )
        if ok and corrected_line.strip():
            return corrected_line
        return None

    def _create_colored_food_log_table_model(
        self,
        data: list[list],
        headers: list[str],
        _id_column: int = 9,  # ID is now at index 9 in transformed data
    ) -> QSortFilterProxyModel:
        """Return a proxy model filled with colored food_log data.

        Args:

        - `data` (`list[list]`): The table data with color information.
        - `headers` (`list[str]`): Column header names.
        - `_id_column` (`int`): Index of the ID column. Defaults to `9`.

        Returns:

        - `QSortFilterProxyModel`: A filterable and sortable model with colored data.

        """
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(headers)

        for row_idx, row in enumerate(data):
            # Extract color information (last element) and ID
            row_color = row[10]  # Color is at index 10
            row_id = row[9]  # ID is at index 9

            # Create items for display columns only (first 9 elements)
            items = []
            for col_idx, value in enumerate(row[:9]):  # Only first 9 elements for display
                item = QStandardItem(str(value) if value is not None else "")

                # Set background color for the item
                item.setBackground(QBrush(row_color))

                # Make calculated calories column non-editable (column 5)
                id_column_calories = 5
                if col_idx == id_column_calories:
                    item.setEditable(False)

                # Make total per day column non-editable (column 8)
                id_column_total_per_day = 8
                if col_idx == id_column_total_per_day:
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

        for _row_idx, row in enumerate(data):
            items = []
            row_color = None

            # Determine row color based on calories (second column)
            if len(row) > 1:
                try:
                    calories = float(row[1]) if row[1] else 0.0
                    thresholds = self._app_config.get("food_calorie_thresholds", {})
                    low_threshold = thresholds.get("low", 1800)
                    medium_low_threshold = thresholds.get("medium_low", 2100)
                    medium_high_threshold = thresholds.get("medium_high", 2500)

                    if calories <= low_threshold:
                        # Green for low calories
                        row_color = QColor(144, 238, 144)
                    elif calories <= medium_low_threshold:
                        # Green-yellow for medium-low calories
                        row_color = QColor(255, 255, 224)
                    elif calories <= medium_high_threshold:
                        # Yellow for medium-high calories
                        row_color = QColor(255, 228, 196)
                    else:
                        # Red for high calories
                        row_color = QColor(255, 192, 203)
                except (ValueError, TypeError):
                    # If calories can't be parsed, use default background
                    pass

            # Create items for all columns
            for _col_idx, value in enumerate(row):
                item = QStandardItem(str(value) if value is not None else "")

                # Apply row color to all items in the row
                if row_color:
                    item.setBackground(QBrush(row_color))

                items.append(item)

            model.appendRow(items)

        proxy = QSortFilterProxyModel()
        proxy.setSourceModel(model)
        return proxy

    @requires_database()
    def _create_dish_from_selected_ingredients(self) -> None:
        """Create a dish from selected ingredients in food log table.

        Gets data from selected rows, calculates total weight and calories,
        adds new dish to Food Items, and optionally replaces selected records.

        """
        if self.db_manager is None:
            logger.error("❌ Database manager is not initialized")
            return

        # Get selected rows data
        selection_model = self.tableView_food_log.selectionModel()
        if not selection_model:
            message_box.warning(self, "Error", "No selection found")
            return

        selected_indexes = selection_model.selectedIndexes()
        if not selected_indexes:
            message_box.warning(self, "Error", "No rows selected")
            return

        # Get unique rows
        unique_rows = {}
        proxy_model = self.models["food_log"]
        if proxy_model is None:
            return
        source_model = proxy_model.sourceModel()
        if not isinstance(source_model, QStandardItemModel):
            return

        for index in selected_indexes:
            row = index.row()
            if row not in unique_rows:
                # Get row ID from vertical header
                row_id_item = source_model.verticalHeaderItem(row)
                if row_id_item:
                    row_id = int(row_id_item.text())
                    unique_rows[row] = row_id

        min_ingredients_required = 2
        if len(unique_rows) < min_ingredients_required:
            message_box.warning(self, "Error", "Please select at least 2 ingredients")
            return

        # Collect ingredients data
        ingredients_data = []
        total_weight = 0.0
        total_calories = 0.0
        ingredient_names = []

        for row, row_id in unique_rows.items():
            # Get data from table model
            name = source_model.item(row, 0).text() if source_model.item(row, 0) else ""
            weight_str = source_model.item(row, 2).text() if source_model.item(row, 2) else "0"
            calculated_calories_str = source_model.item(row, 5).text() if source_model.item(row, 5) else "0"

            try:
                weight = float(weight_str) if weight_str else 0.0
                calories = float(calculated_calories_str) if calculated_calories_str else 0.0
            except (ValueError, TypeError):
                weight = 0.0
                calories = 0.0

            ingredients_data.append(
                {
                    "row_id": row_id,
                    "name": name,
                    "weight": weight,
                    "calories": calories,
                }
            )
            total_weight += weight
            total_calories += calories
            ingredient_names.append(name)

        if total_weight == 0:
            message_box.warning(
                self, "Error", "Selected ingredients have no weight. Cannot calculate calories per 100g."
            )
            return

        # Show dialog for dish name and drink selection
        dialog = QDialog(self)
        dialog.setWindowTitle("Create Dish from Ingredients")
        qt_modality.set_owner_window_modal(dialog)
        dialog.setMinimumWidth(400)

        layout = QVBoxLayout(dialog)

        # Dish name input
        name_label = QLabel("Dish name:")
        layout.addWidget(name_label)
        name_input = QLineEdit()
        name_input.setPlaceholderText("Enter dish name (e.g., Cappuccino)")
        layout.addWidget(name_input)

        # Is drink checkbox
        is_drink_checkbox = QCheckBox("This is a drink")
        layout.addWidget(is_drink_checkbox)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        cancel_button = make_emoji_push_button("Cancel", CANCEL_BUTTON_EMOJI)
        cancel_button.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_button)
        ok_button = make_emoji_push_button("OK", OK_BUTTON_EMOJI)
        ok_button.setDefault(True)
        ok_button.clicked.connect(dialog.accept)
        button_layout.addWidget(ok_button)
        layout.addLayout(button_layout)

        if dialog.exec_() != QDialog.DialogCode.Accepted:
            return

        dish_name = name_input.text().strip()
        if not dish_name:
            message_box.warning(self, "Error", "Dish name cannot be empty")
            return

        is_drink = is_drink_checkbox.isChecked()

        # Calculate calories per 100g
        # Require weight to calculate calories per 100g
        if total_weight == 0:
            message_box.warning(self, "Error", "Cannot calculate calories per 100g: total weight is zero")
            return

        calories_per_100g = round((total_calories / total_weight) * 100, 2)

        # Prepare ingredients info message
        ingredients_list = "\n".join([f"  • {name}" for name in ingredient_names])
        info_message = (
            f"Ingredients:\n{ingredients_list}\n\n"
            f"Total weight: {total_weight:.1f} g\n"
            f"Calories per 100g: {calories_per_100g:.2f} kcal"
        )

        # Ask if user wants to add dish to Food Items
        add_to_food_items_reply = message_box.question(
            self,
            "Add to Food Items?",
            f"Dish '{dish_name}'\n\n{info_message}\n\nDo you want to add this dish to Food Items?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        # Add dish to Food Items if user confirmed
        if add_to_food_items_reply == QMessageBox.StandardButton.Yes:
            # Check if dish already exists
            existing_item = self.db_manager.get_food_item_by_name(dish_name)
            if existing_item:
                update_reply = message_box.question(
                    self,
                    "Dish Already Exists",
                    f"Dish '{dish_name}' already exists in Food Items. Do you want to update it?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No,
                )
                if update_reply == QMessageBox.StandardButton.No:
                    return

                # Update existing item - use calories_per_100g instead of portion_calories
                food_id = existing_item[0]
                success = self.db_manager.update_food_item(
                    food_item_id=food_id,
                    name=dish_name,
                    name_en="",
                    is_drink=is_drink,
                    calories_per_100g=calories_per_100g,
                    default_portion_weight=int(total_weight) if total_weight > 0 else None,
                    default_portion_calories=None,  # Don't use portion calories
                )
            else:
                # Add new item - use calories_per_100g instead of portion_calories
                success = self.db_manager.add_food_item(
                    name=dish_name,
                    name_en="",
                    is_drink=is_drink,
                    calories_per_100g=calories_per_100g,
                    default_portion_weight=int(total_weight) if total_weight > 0 else None,
                    default_portion_calories=None,  # Don't use portion calories
                )

            if not success:
                message_box.warning(self, "Error", f"Failed to add dish '{dish_name}' to Food Items")
                return

        # Ask if user wants to replace selected records with the new dish
        reply = message_box.question(
            self,
            "Replace Records?",
            f"Dish '{dish_name}'\n\n{info_message}\n\nDo you want to replace the selected records with this dish?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Replace selected records with the new dish
            # Get the date from the first selected row
            first_row = min(unique_rows.keys())
            date_str = (
                source_model.item(first_row, 6).text()
                if source_model.item(first_row, 6)
                else QDate.currentDate().toString("yyyy-MM-dd")
            )

            # Delete selected records only when replacement can be written with a valid weight
            if total_weight <= 0:
                message_box.warning(self, "Error", "Cannot replace records: total weight must be greater than zero")
            else:
                for row_id in unique_rows.values():
                    self.db_manager.delete_food_log_record(row_id)

                # Add new dish record (weight mode with calories_per_100g)
                self.db_manager.add_food_log_record(
                    date=date_str,
                    calories_per_100g=calories_per_100g,
                    name=dish_name,
                    weight=int(total_weight),
                    portion_calories=None,
                    is_drink=is_drink,
                )

                message_box.information(self, "Success", f"Selected records have been replaced with '{dish_name}'")
        elif add_to_food_items_reply == QMessageBox.StandardButton.Yes:
            message_box.information(
                self, "Success", f"Dish '{dish_name}' has been added to Food Items.\n\n{info_message}"
            )
        else:
            message_box.information(self, "Success", f"Dish '{dish_name}' created.\n\n{info_message}")

        # Update UI
        self.update_food_data()

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
        return create_table_proxy_model(data, headers, id_column=id_column)

    @requires_database()
    def _delete_selected_food_log_rows(self, record_ids: list[int]) -> None:
        """Delete multiple selected rows from food log table.

        Args:

        - `record_ids` (`list[int]`): Database IDs of food log rows to delete.

        """
        if self.db_manager is None:
            logger.error("❌ Database manager is not initialized")
            return

        if not record_ids:
            message_box.warning(self, "Error", "No valid rows to delete")
            return

        # Confirm deletion
        reply = message_box.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete {len(record_ids)} selected row(s)?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # Delete all selected rows
        success_count = 0
        failed_count = 0

        for row_id in record_ids:
            try:
                if self.db_manager.delete_food_log_record(row_id):
                    success_count += 1
                else:
                    failed_count += 1
            except Exception:
                logger.exception("Error deleting row %s", row_id)
                failed_count += 1

        # Show result message
        if failed_count == 0:
            message_box.information(self, "Success", f"Successfully deleted {success_count} row(s)")
        else:
            message_box.warning(
                self,
                "Partial Success",
                f"Deleted {success_count} row(s), failed to delete {failed_count} row(s)",
            )

        # Update UI
        self.update_food_data()

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

        # Dispose autocomplete completer
        if hasattr(self, "food_completer") and self.food_completer is not None:
            self.food_completer.deleteLater()
            self.food_completer = None

        if hasattr(self, "food_completer_proxy") and self.food_completer_proxy is not None:
            self.food_completer_proxy.deleteLater()
            self.food_completer_proxy = None

        if hasattr(self, "food_completer_source_model") and self.food_completer_source_model is not None:
            self.food_completer_source_model.deleteLater()
            self.food_completer_source_model = None

    def _export_food_log_table(self, *, prefer: Literal["csv", "xlsx"]) -> None:
        """Export the food log source model as CSV or Excel."""
        proxy = self.models.get("food_log")
        model = proxy.sourceModel() if isinstance(proxy, QSortFilterProxyModel) else proxy
        export_table_via_dialog(self, model, prefer=prefer, sheet_name="Food log")

    def _filter_food_items(self, text: str) -> None:
        """Filter food items list based on input text.

        Args:

        - `text` (`str`): Filter text from lineEdit_food_manual_name.

        """
        if not text:
            self._show_all_food_items()
            return

        if self.food_items_list_model:
            for i in range(self.food_items_list_model.rowCount()):
                item = self.food_items_list_model.item(i)
                if item:
                    self.listView_food_items.setRowHidden(
                        i,
                        not text_matches_autocomplete(item.text(), text),
                    )

    def _filter_food_log_by_column(self, column: int, value: str) -> None:
        """Apply exact-match filter on one food log table column (loaded rows only)."""
        proxy = self.models.get("food_log")
        if proxy is None:
            return
        text = value.strip()
        if not text:
            return
        proxy.setFilterKeyColumn(column)
        proxy.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        proxy.setFilterRegularExpression(
            QRegularExpression(f"^{QRegularExpression.escape(text)}$"),
        )

    def _finish_window_initialization(self) -> None:
        """Finish window initialization by showing the window and adjusting columns."""
        if self._is_closing:
            return
        self._show_placed_window()
        # Adjust columns after window is shown and has proper dimensions
        QTimer.singleShot(50, self._adjust_food_log_table_columns)
        # Update food stats chart after initialization
        QTimer.singleShot(100, self._update_food_calories_chart)

    @staticmethod
    def _food_log_row_missing_calories(row: list[Any]) -> bool:
        """Return whether a problematic-query row lacks calories (non-drink)."""
        if len(row) < _FOOD_LOG_QUERY_MIN_COLS_FOR_CALORIES:
            return True
        if int(row[_FOOD_LOG_QUERY_COL_IS_DRINK] or 0) == 1:
            return False

        def _empty_or_zero(value: Any) -> bool:
            if value is None or value == "":
                return True
            try:
                return float(value) <= 0
            except (TypeError, ValueError):
                return True

        return _empty_or_zero(row[_FOOD_LOG_QUERY_COL_CALORIES_PER_100G]) and _empty_or_zero(
            row[_FOOD_LOG_QUERY_COL_PORTION_CALORIES]
        )

    @staticmethod
    def _food_log_row_missing_weight(row: list[Any]) -> bool:
        """Return whether a food_log row has NULL/empty/non-positive weight."""
        if len(row) < _FOOD_LOG_QUERY_MIN_COLS_FOR_WEIGHT:
            return True
        weight = row[_FOOD_LOG_QUERY_COL_WEIGHT]
        if weight is None or weight == "":
            return True
        try:
            return float(weight) <= 0
        except (TypeError, ValueError):
            return True

    def _food_log_translate_names_limit(self) -> int:
        """Return max unique untranslated names per AI batch from config."""
        raw = self._app_config.get("food_log_translate_names_limit", 1000)
        try:
            limit = int(raw)
        except (TypeError, ValueError):
            limit = 1000
        return max(1, limit)

    def _get_current_selected_food_item(self) -> str | None:
        """Get the currently selected food item name from the list view.

        Returns:

        - `str | None`: Selected food name, or `None` if nothing is selected.

        """
        selection_model = self.listView_food_items.selectionModel()
        if selection_model and self.food_items_list_model:
            current_index = selection_model.currentIndex()
            if current_index.isValid():
                item = self.food_items_list_model.itemFromIndex(current_index)
                if item:
                    return extract_food_name_from_display(item.text())

        return None

    def _get_selected_food_log_recalc_targets(self) -> list[tuple[int, str]]:
        """Return `(record_id, name)` for each selected food log row."""
        targets: list[tuple[int, str]] = []
        try:
            table_view, model_key, _ = self.table_config["food_log"]
            proxy_model = self.models[model_key]
            if proxy_model is None:
                return targets

            selection_model = table_view.selectionModel()
            if selection_model is None:
                return targets

            source_model = proxy_model.sourceModel()
            if not isinstance(source_model, QStandardItemModel):
                return targets

            seen_source_rows: set[int] = set()
            proxy_indexes = list(selection_model.selectedIndexes())
            current_index = table_view.currentIndex()
            if not proxy_indexes and current_index.isValid():
                proxy_indexes = [current_index]
            for proxy_index in proxy_indexes:
                source_index = proxy_model.mapToSource(proxy_index)
                if not source_index.isValid():
                    continue
                row = source_index.row()
                if row in seen_source_rows:
                    continue
                seen_source_rows.add(row)
                vertical_header_item = source_model.verticalHeaderItem(row)
                if vertical_header_item is None:
                    continue
                name_item = source_model.item(row, 0)
                name = name_item.text().strip() if name_item is not None else ""
                targets.append((int(vertical_header_item.text()), name))
        except (KeyError, ValueError, TypeError, AttributeError):
            return []
        return targets

    def _init_database(self) -> None:
        """Open the SQLite file from app config (create from `recover.sql` if missing)."""
        app_dir = Path(__file__).parent
        configured = Path(self._app_config["sqlite_food"])
        db_path = QtSqliteDatabaseManagerBase.resolve_db_path_with_fallback(configured, "food")
        if db_path.exists():
            # Installer/old recover.sql created id/datetime/calories; migrate before open.
            ensure_food_schema(db_path)

        self.db_manager = init_tracker_database(
            self,
            configured,
            "food",
            app_dir / "recover.sql",
            database_manager.DatabaseManager,
            has_required_tables=lambda dm: dm.table_exists("food_log"),
            missing_table_label="food_log table",
        )

    def _init_food_items_list(self) -> None:
        """Initialize the food items list view with a model and connect signals."""
        self.food_items_list_model = QStandardItemModel()
        self.listView_food_items.setModel(self.food_items_list_model)

        # Connect selection change signal after model is set
        selection_model = self.listView_food_items.selectionModel()
        if selection_model:
            selection_model.currentChanged.connect(self.on_main_food_item_selection_changed)

    def _init_food_log_table_delegates(self) -> None:
        """Install column delegates for the food log table."""
        self._is_drink_delegate = IsDrinkDelegate(self.tableView_food_log)
        self.tableView_food_log.setItemDelegateForColumn(1, self._is_drink_delegate)

        self._date_delegate = DateDelegate(self.tableView_food_log)
        self.tableView_food_log.setItemDelegateForColumn(6, self._date_delegate)

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
                if not earliest_date.isNull():
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

        except Exception:
            logger.exception("Error getting earliest food log date")
            # Fallback to last month if any error occurs
            today = QDate.currentDate()
            month_ago = today.addMonths(-1)
            self.dateEdit_food_stats_from.setDate(month_ago)
            self.dateEdit_food_stats_to.setDate(today)

            # Update the chart with fallback date range
            QTimer.singleShot(50, self._update_food_calories_chart)

    def _load_food_log_page(self, *, reset: bool = True) -> None:
        """Load the first page of food log records."""
        if self.db_manager is None:
            return

        if reset:
            self._reset_food_log_pagination_state()

        if self.show_all_food_records:
            rows: list[list] = self.db_manager.get_all_food_log_records()
            self._food_log_pagination.record_first_page(len(rows), None, pagination_enabled=False)
        else:
            limit: int = self.count_food_records_to_show
            rows = self.db_manager.get_recent_food_log_records(limit, 0)
            self._food_log_pagination.record_first_page(len(rows), limit)

        transformed_data: list[list] = self._transform_food_log_data(rows, append_state=False)
        self.models["food_log"] = self._create_colored_food_log_table_model(
            transformed_data, self.table_config["food_log"][2]
        )
        self.tableView_food_log.setModel(self.models["food_log"])
        self.tableView_food_log.setEditTriggers(
            QTableView.EditTrigger.DoubleClicked | QTableView.EditTrigger.EditKeyPressed
        )

        food_log_header = self.tableView_food_log.horizontalHeader()
        for i in range(food_log_header.count()):
            food_log_header.setSectionResizeMode(i, food_log_header.ResizeMode.Interactive)
        self._adjust_food_log_table_columns()

    def _load_more_food_log(self) -> None:
        """Append the next page of food log records when scrolling to the bottom."""
        if self.show_all_food_records or self.db_manager is None or self.models["food_log"] is None:
            return

        def append_rows(rows: list[list]) -> None:
            transformed_data: list[list] = self._transform_food_log_data(rows, append_state=True)
            proxy = cast("QSortFilterProxyModel", self.models["food_log"])
            source_model = cast("QStandardItemModel", proxy.sourceModel())
            self._append_food_log_rows_to_model(source_model, transformed_data)

        self._food_log_pagination.load_more(
            load_more_count=self.food_log_load_more_count,
            fetch_rows=self.db_manager.get_recent_food_log_records,
            append_rows=append_rows,
        )

    def _on_autocomplete_selected(self, text: str) -> None:
        """Handle autocomplete selection and populate form fields.

        Args:

        - `text` (`str`): Selected autocomplete text.

        """
        if not text:
            return

        # Set the selected text
        self.lineEdit_food_manual_name.setText(text)

        # Trigger the food item selection logic
        self._populate_form_from_food_name(text)

        # Move focus to weight spinbox and select all text
        self.spinBox_food_weight.setFocus()
        self.spinBox_food_weight.selectAll()

    def _on_food_add_with_ai_image_dropped(self, paths: list[str]) -> None:
        """Open Add Food with AI dialog with dropped images already loaded."""
        if paths:
            self.on_food_add_with_ai(initial_image_paths=paths)

    def _on_food_log_scroll(self, value: int) -> None:
        """Trigger loading more food log rows when scrolled near the bottom."""
        scrollbar = self.tableView_food_log.verticalScrollBar()
        on_scroll_load_more(value, scrollbar.maximum(), self._load_more_food_log)

    def _on_food_name_text_edited(self, text: str) -> None:
        """Update autocomplete filter and sorting when food name text changes."""
        self.food_completer_proxy.set_filter_text(text)

        if text:
            self.food_completer.setCompletionPrefix(text)
            self.food_completer.complete()
        else:
            self.food_completer_proxy.set_filter_text("")
            popup = self.food_completer.popup()
            if popup is not None and popup.isVisible():
                popup.hide()

    def _on_tab_changed(self, index: int) -> None:
        """Handle tab widget index change.

        Args:

        - `index` (`int`): Index of the newly selected tab.

        """
        # Get the widget at the current index
        current_widget = self.tabWidget.widget(index)
        if current_widget is None:
            return

        tab_name = current_widget.objectName()
        if tab_name == "tab_food_dashboard":
            self.update_food_calories_today()
            return
        if tab_name == "tab_food":
            # Splitter/table get a real width only after the hidden tab is shown.
            QTimer.singleShot(0, self._adjust_food_log_table_columns)
            QTimer.singleShot(50, self._adjust_food_log_table_columns)
            return
        if tab_name == "tab_food_stats":
            self._update_kcal_per_day_table()
            self._update_food_calories_chart()

    def _open_text_input_dialog(
        self,
        default_date: QDate,
        *,
        initial_text: str | None = None,
        focus_text_on_show: bool = True,
    ) -> None:
        """Show food table dialog and process accepted input."""
        dialog = TextInputDialog(
            self,
            default_date=default_date,
            initial_text=initial_text,
            focus_text_on_show=focus_text_on_show,
            db_manager=self.db_manager,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        items = dialog.get_items()
        date = dialog.get_date()
        if items and date:
            self._process_food_items(items, date)

    def _populate_form_from_food_name(self, food_name: str) -> None:
        """Populate form fields based on food name from database.

        Args:

        - `food_name` (`str`): Name of the food item to populate form with.

        """
        if not self._validate_database_connection():
            return

        if self.db_manager is None:
            return

        try:
            # First try to get food item data from food_items table
            food_item_data = self.db_manager.get_food_item_by_name(food_name)

            if food_item_data:
                is_drink = food_item_data.is_drink
                calories_per_100g = food_item_data.calories_per_100g
                default_portion_weight = food_item_data.default_portion_weight
                default_portion_calories = food_item_data.default_portion_calories

                # Populate form fields
                self.spinBox_food_weight.setValue(int(default_portion_weight) if default_portion_weight else 100)
                self.checkBox_food_is_drink.setChecked(is_drink)
                self._update_add_button_appearance()

                # Determine radio button state based on default_portion_calories
                if default_portion_calories and default_portion_calories > 0:
                    self.radioButton_use_calories.setChecked(True)
                    self.doubleSpinBox_food_calories.setValue(default_portion_calories)
                else:
                    self.radioButton_use_weight.setChecked(True)
                    self.doubleSpinBox_food_calories.setValue(calories_per_100g or 0)

            else:
                # If not found in food_items, try to get from food_log
                food_log_data = self.db_manager.get_food_log_item_by_name(food_name)

                if food_log_data:
                    is_drink = food_log_data.is_drink
                    calories_per_100g = food_log_data.calories_per_100g
                    weight = food_log_data.weight
                    portion_calories = food_log_data.portion_calories

                    # Populate form fields
                    self.spinBox_food_weight.setValue(int(weight) if weight else 100)
                    self.checkBox_food_is_drink.setChecked(is_drink)
                    self._update_add_button_appearance()

                    # Determine radio button state based on portion_calories
                    if portion_calories and portion_calories > 0:
                        self.radioButton_use_calories.setChecked(True)
                        self.doubleSpinBox_food_calories.setValue(portion_calories)
                    else:
                        self.radioButton_use_weight.setChecked(True)
                        self.doubleSpinBox_food_calories.setValue(calories_per_100g or 0)
                else:
                    # If not found in either table, set defaults
                    self.spinBox_food_weight.setValue(100)
                    self.checkBox_food_is_drink.setChecked(False)
                    self.radioButton_use_weight.setChecked(True)
                    self.doubleSpinBox_food_calories.setValue(0)
                    self._update_add_button_appearance()

            # Update calories calculation
            self.update_calories_calculation()

        except Exception:
            logger.exception("Error populating form from food name")

    def _process_food_item_selection(self, food_name: str) -> None:
        """Process food item selection and populate form fields.

        Args:

        - `food_name` (`str`): Name of the selected food item.

        """
        if not food_name:
            return

        # Check if database manager is available and connection is open
        if not self._validate_database_connection():
            logger.warning("Database manager not available or connection not open")
            return

        if self.db_manager is None:
            logger.error("❌ Database manager is not initialized")
            return

        try:
            # First try to get food item data from food_items table
            food_item_data = self.db_manager.get_food_item_by_name(food_name)

            if food_item_data:
                name = food_item_data.name
                is_drink = food_item_data.is_drink
                calories_per_100g = food_item_data.calories_per_100g
                default_portion_weight = food_item_data.default_portion_weight
                default_portion_calories = food_item_data.default_portion_calories

                # Populate groupBox_food_add fields (food log record form)
                self.lineEdit_food_manual_name.setText(name)
                self.spinBox_food_weight.setValue(int(default_portion_weight) if default_portion_weight else 100)
                self.checkBox_food_is_drink.setChecked(is_drink)
                self._update_add_button_appearance()

                # Determine radio button state based on default_portion_calories
                if default_portion_calories and default_portion_calories > 0:
                    # Use portion calories mode
                    self.radioButton_use_calories.setChecked(True)
                    self.doubleSpinBox_food_calories.setValue(default_portion_calories)
                else:
                    # Use weight mode
                    self.radioButton_use_weight.setChecked(True)
                    self.doubleSpinBox_food_calories.setValue(calories_per_100g or 0)

            else:
                # If not found in food_items, try to get from food_log (for popular items)
                food_log_data = self.db_manager.get_food_log_item_by_name(food_name)

                if food_log_data:
                    name = food_log_data.name or food_name
                    is_drink = food_log_data.is_drink
                    calories_per_100g = food_log_data.calories_per_100g
                    weight = food_log_data.weight
                    portion_calories = food_log_data.portion_calories

                    # Populate groupBox_food_add fields (food log record form)
                    self.lineEdit_food_manual_name.setText(name)
                    self.spinBox_food_weight.setValue(int(weight) if weight else 100)
                    self.checkBox_food_is_drink.setChecked(is_drink)
                    self._update_add_button_appearance()

                    # Determine radio button state based on portion_calories
                    if portion_calories and portion_calories > 0:
                        # Use portion calories mode
                        self.radioButton_use_calories.setChecked(True)
                        self.doubleSpinBox_food_calories.setValue(portion_calories)
                    else:
                        # Use weight mode
                        self.radioButton_use_weight.setChecked(True)
                        self.doubleSpinBox_food_calories.setValue(calories_per_100g or 0)

                else:
                    # If not found in either table, just set the name
                    self.lineEdit_food_manual_name.setText(food_name)
                    # Reset other fields to defaults
                    self.spinBox_food_weight.setValue(100)
                    self.checkBox_food_is_drink.setChecked(False)
                    self.radioButton_use_weight.setChecked(True)
                    self.doubleSpinBox_food_calories.setValue(0)
                    self._update_add_button_appearance()

            # Update calories calculation
            self.update_calories_calculation()

            # Move focus to weight spinbox and select all text after selection
            self.spinBox_food_weight.setFocus()
            self.spinBox_food_weight.selectAll()

        except Exception:
            logger.exception("Error in food item selection")
            # In case of error, at least set the name and move focus
            self.lineEdit_food_manual_name.setText(food_name)
            self.spinBox_food_weight.setFocus()
            self.spinBox_food_weight.selectAll()

    def _process_food_items(self, parsed_items: list[ParsedFoodItem], default_date: str) -> None:
        """Add parsed food items to the database.

        Args:

        - `parsed_items` (`list[ParsedFoodItem]`): Food items to save.
        - `default_date` (`str`): Default date for entries in yyyy-MM-dd format.

        """
        if self.db_manager is None:
            logger.error("❌ Database manager is not initialized")
            return

        if not parsed_items:
            message_box.information(self, "No Items", "No valid food items found.")
            return

        success_count = 0
        error_count = 0
        error_messages = []

        for item in parsed_items:
            try:
                if item.weight is None or item.weight <= 0:
                    error_count += 1
                    error_messages.append(f"Weight is required: {item.name}")
                    continue
                success = self.db_manager.add_food_log_record(
                    date=item.food_date or default_date,
                    calories_per_100g=item.calories_per_100g,
                    name=item.name,
                    weight=item.weight,
                    portion_calories=item.portion_calories,
                    is_drink=item.is_drink,
                )
                if success:
                    success_count += 1
                else:
                    error_count += 1
                    error_messages.append(f"Failed to add: {item.name}")
            except Exception as e:
                error_count += 1
                error_messages.append(f"Error adding {item.name}: {e}")

        if success_count > 0:
            self.update_food_data()

        if error_count > 0:
            max_errors = 10
            error_text = f"Added {success_count} items successfully.\n\nErrors:\n" + "\n".join(
                error_messages[:max_errors]
            )
            if len(error_messages) > max_errors:
                error_text += f"\n... and {len(error_messages) - max_errors} more errors"
            message_box.warning(self, "Results", error_text)
        else:
            toast = toast_notification.ToastNotification(
                f"Successfully added {success_count} food items.",
                duration=2000,
                parent=self,
            )
            toast.present()

    def _process_text_input(self, text: str, default_date: str) -> None:
        """Process text input and add food items to database.

        Args:

        - `text` (`str`): Text input to process.
        - `default_date` (`str`): Default date for entries in yyyy-MM-dd format.

        """
        if self.db_manager is None:
            logger.error("❌ Database manager is not initialized")
            return

        parser = TextParser()
        parsed_items = parser.parse_text(
            text,
            self.db_manager,
            default_date,
            correct_unparseable_line=self._correct_food_input_line,
        )
        self._process_food_items(parsed_items, default_date)

    def _prompt_eaten_percent_and_apply(self) -> None:
        """Ask for a percent eaten (default 50) and scale selected food log rows."""
        percent, ok = QInputDialog.getDouble(
            self,
            "I ate %",
            "Percent eaten:",
            50.0,
            0.1,
            100.0,
            1,
        )
        if not ok:
            return
        self._apply_eaten_fraction_to_selected_food_log(percent / 100.0)

    def _recalculate_food_log_calories_queue(
        self,
        remaining: list[tuple[int, str]],
        *,
        updated: int,
        failed: list[str],
    ) -> None:
        """Send the next food log name to BotHub, then apply calories without changing mass."""
        if not remaining:
            if updated:
                self.update_food_data()
            if failed:
                max_names_in_message = 8
                preview = ", ".join(failed[:max_names_in_message])
                suffix = "…" if len(failed) > max_names_in_message else ""
                message_box.warning(
                    self,
                    "AI Response",
                    f"Could not recalculate calories for {len(failed)} item(s): {preview}{suffix}",
                )
            elif updated == 0:
                message_box.warning(self, "Error", "Failed to update selected food log rows")
            return

        record_id, food_name = remaining[0]
        rest = remaining[1:]
        try:
            prompt_text = build_prompt(self._app_config, "food_kcal_lookup", {"FOOD_NAME": food_name})
        except ValueError as exc:
            show_bothub_prompt_build_error(self, exc)
            return

        def on_success(response_text: str) -> None:
            result = parse_kcal_lookup_response(response_text)
            if result is None:
                self._recalculate_food_log_calories_queue(rest, updated=updated, failed=[*failed, food_name])
                return
            calories_per_100g, portion_calories = calories_from_kcal_lookup(result)
            ok = self.db_manager is not None and self.db_manager.update_food_log_calories(
                record_id,
                calories_per_100g,
                portion_calories,
            )
            if ok:
                self._recalculate_food_log_calories_queue(rest, updated=updated + 1, failed=failed)
                return
            self._recalculate_food_log_calories_queue(rest, updated=updated, failed=[*failed, food_name])

        total = updated + len(remaining)
        current = updated + 1
        toast_message = (
            f"Recalculating calories with AI ({current}/{total}): {food_name}…"
            if total > 1
            else f"Recalculating calories with AI ({food_name})…"
        )
        started = self._start_bothub_worker(prompt_text, on_success, toast_message=toast_message)
        if not started and updated:
            self.update_food_data()

    @requires_database()
    def _recalculate_selected_food_log_calories_with_ai(self) -> None:
        """Resend selected food names to AI and update calories, leaving weight unchanged."""
        if self.db_manager is None:
            return
        targets = [(record_id, name) for record_id, name in self._get_selected_food_log_recalc_targets() if name]
        if not targets:
            message_box.warning(self, "Food Name", "Select one or more food log rows with a name.")
            return
        self._recalculate_food_log_calories_queue(targets, updated=0, failed=[])

    def _reconnect_context_menu(self) -> None:
        """Reconnect the context menu signal after deletion."""
        self.tableView_food_log.customContextMenuRequested.connect(self._show_food_log_context_menu)

    def _refresh_food_log_calories_after_edit(
        self,
        top_left: QModelIndex,
        bottom_right: QModelIndex,
    ) -> None:
        """Update calculated and daily totals in the open food-log model.

        Reloads neither tables nor charts. `label_food_today` is refreshed only
        when the edit touches today's date.

        """
        proxy_model = self.models.get("food_log")
        if proxy_model is None:
            return
        source_model = proxy_model.sourceModel()
        if not isinstance(source_model, QStandardItemModel):
            return

        today = QDate.currentDate().toString("yyyy-MM-dd")
        date_column_changed = top_left.column() <= FOOD_LOG_COL_DATE <= bottom_right.column()
        edited_today = False
        for row in range(top_left.row(), bottom_right.row() + 1):
            date_item = source_model.item(row, FOOD_LOG_COL_DATE)
            if date_item is not None and date_item.text() == today:
                edited_today = True
                break

        refresh_food_log_calorie_columns(source_model)
        self.tableView_food_log.viewport().update()

        if date_column_changed or edited_today:
            self.update_food_calories_today()

    def _report_food_translate_completion(self, *, prefix: str = "") -> None:
        """Tell the user how many rows still lack name_en and offer another AI batch."""
        if self.db_manager is None:
            return

        remaining_rows = self.db_manager.count_food_log_rows_missing_name_en()
        if remaining_rows == 0:
            message = "All food log records have an English name. Everything is translated."
            if prefix:
                message = f"{prefix}\n\n{message}"
            message_box.information(self, "Translate with AI", message)
            return

        unique_names_limit = self._food_log_translate_names_limit()
        message = (
            f"{remaining_rows} food_log record(s) still have an empty or NULL English name.\n\n"
            f"Run Translate with AI again? The next batch processes up to "
            f"{unique_names_limit} unique untranslated names."
        )
        if prefix:
            message = f"{prefix}\n\n{message}"

        answer = message_box.question(
            self,
            "Translate with AI",
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer == QMessageBox.StandardButton.Yes:
            self.on_translate_with_ai()

    def _reset_food_log_pagination_state(self) -> None:
        """Reset pagination counters and display state for food log table."""
        self._food_log_pagination.reset()
        self._food_log_dates_with_totals = set()
        self._food_log_date_color_map = {}

    def _run_food_add_by_voice(self, *, large_ui: bool = False) -> None:
        """Record speech, transcribe via BotHub, convert to food log TSV, then open preview dialog."""
        recording_dialog = SimpleRecordingDialog(self, large_ui=large_ui)
        if recording_dialog.exec() != QDialog.DialogCode.Accepted:
            recording_dialog.release_multimedia()
            return

        audio_path = recording_dialog.get_audio_path()
        recording_dialog.release_multimedia()
        if not audio_path:
            return

        try:
            audio_data = audio_bytes_and_mime(audio_path)
        except ValueError as exc:
            message_box.critical(self, "Audio Error", str(exc))
            return

        def on_transcription_success(transcribed_text: str) -> None:
            if not transcribed_text.strip():
                message_box.critical(self, "BotHub Error", "Empty transcription from BotHub.")
                return

            try:
                prompt_text = build_prompt(
                    self._app_config,
                    "food_voice_log_to_tsv",
                    {"RAW_DATA": transcribed_text},
                )
            except ValueError as exc:
                show_bothub_prompt_build_error(self, exc)
                return

            def on_tsv_success(response_text: str) -> None:
                self._open_text_input_dialog(
                    self.dateEdit_food.date(),
                    initial_text=response_text,
                    focus_text_on_show=False,
                )

            self._start_bothub_worker(
                prompt_text,
                on_tsv_success,
                toast_message="Parsing food log…",
            )

        run_bothub_request(
            self,
            self._app_config,
            build_transcription_prompt(),
            on_transcription_success,
            audio=audio_data,
            model=get_speech_model(self._app_config),
            toast_message="Recognizing speech…",
            is_busy=lambda: self._bothub_state.worker is not None,
            state=self._bothub_state,
        )

    def _send_food_log_to_ai(
        self,
        raw_text: str,
        images_data: list[tuple[bytes, str]] | None = None,
    ) -> None:
        """Send food source text and optional images to BotHub, then open the preview dialog."""
        try:
            prompt_text = build_prompt(self._app_config, "food_log_to_tsv", {"RAW_DATA": raw_text})
        except ValueError as exc:
            show_bothub_prompt_build_error(self, exc)
            return

        def on_success(response_text: str) -> None:
            self._open_text_input_dialog(
                self.dateEdit_food.date(),
                initial_text=response_text,
                focus_text_on_show=False,
            )

        self._start_bothub_worker(prompt_text, on_success, images=images_data or None)

    @requires_database()
    def _set_date_for_selected_food_log_records(self, record_ids: list[int]) -> None:
        """Set the same date on several food log rows after user picks a date in a dialog."""
        min_rows_for_bulk_date = 2
        if len(record_ids) < min_rows_for_bulk_date or self.db_manager is None:
            return
        if not self._validate_database_connection():
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Set date for selected food log records")
        dialog_layout = QVBoxLayout(dialog)
        dialog_layout.addWidget(
            QLabel(f"New date for {len(record_ids)} food log records:", dialog),
        )
        date_edit = QDateEdit(dialog)
        date_edit.setCalendarPopup(True)
        date_edit.setDisplayFormat("yyyy-MM-dd")
        date_edit.setDate(self.dateEdit_food.date())
        dialog_layout.addWidget(date_edit)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            parent=dialog,
        )
        apply_emoji_dialog_buttons(buttons)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        dialog_layout.addWidget(buttons)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        new_date: str = date_edit.date().toString("yyyy-MM-dd")
        if self.db_manager.update_food_log_records_date(record_ids, new_date):
            QTimer.singleShot(0, self.update_food_data)
        else:
            message_box.warning(self, "Date", "Could not update date for one or more food log records.")

    def _set_date_from_table(self, date_value: str) -> None:
        """Set the date from a food log row into `dateEdit_food`."""
        try:
            date_obj = QDate.fromString(date_value.strip()[:10], "yyyy-MM-dd")
            if not date_obj.isNull():
                self.dateEdit_food.setDate(date_obj)
            else:
                logger.error("%s", f"❌ Invalid date format: {date_value}")
        except Exception:
            logger.exception("❌ Error setting date from table")

    def _set_date_from_table_minus_one_day(self, date_value: str) -> None:
        """Set `dateEdit_food` to the food log row date minus one day."""
        try:
            date_obj = QDate.fromString(date_value.strip()[:10], "yyyy-MM-dd")
            if not date_obj.isNull():
                self.dateEdit_food.setDate(date_obj.addDays(-1))
            else:
                logger.error("%s", f"❌ Invalid date format: {date_value}")
        except Exception:
            logger.exception("❌ Error setting date from table - 1 day")

    def _set_date_from_table_plus_one_day(self, date_value: str) -> None:
        """Set `dateEdit_food` to the food log row date plus one day."""
        try:
            date_obj = QDate.fromString(date_value.strip()[:10], "yyyy-MM-dd")
            if not date_obj.isNull():
                self.dateEdit_food.setDate(date_obj.addDays(1))
            else:
                logger.error("%s", f"❌ Invalid date format: {date_value}")
        except Exception:
            logger.exception("❌ Error setting date from table + 1 day")

    def _setup_autocomplete(self) -> None:
        """Set up autocomplete functionality for food name input."""
        self.food_completer_source_model = QStandardItemModel(self)
        self.food_completer_proxy = FoodNameAutocompleteProxyModel(self)
        self.food_completer_proxy.setSourceModel(self.food_completer_source_model)

        self.food_completer = QCompleter(self.food_completer_proxy, self)
        self.food_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.food_completer.setFilterMode(Qt.MatchFlag.MatchContains)
        # Proxy already filters (incl. EN/RU layout); do not re-filter by literal prefix.
        self.food_completer.setCompletionMode(QCompleter.CompletionMode.UnfilteredPopupCompletion)

        self.lineEdit_food_manual_name.setCompleter(self.food_completer)
        setup_completer_item_tooltips(self.food_completer)

        self._update_autocomplete_data()

        self.lineEdit_food_manual_name.textEdited.connect(self._on_food_name_text_edited)
        self.food_completer.activated.connect(self._on_autocomplete_selected)

    def _setup_food_dashboard_tab(self) -> None:
        """Fill the first Food tab with the quick-add dashboard."""
        self._food_dashboard = FoodDashboardWidget(self)
        self._food_dashboard.add_photo_requested.connect(self.on_food_dashboard_add_photo)
        self._food_dashboard.add_voice_requested.connect(self.on_food_dashboard_add_voice)
        self._food_dashboard.add_text_requested.connect(self.on_food_dashboard_add_text)
        self.verticalLayout_food_dashboard.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_food_dashboard.addWidget(self._food_dashboard, 1)
        install_open_quick_tab_checkbox(
            self,
            app="food",
            tab_layout=self.verticalLayout_food_dashboard,
            tab_widget=self.tabWidget,
        )

    def _setup_ui(self) -> None:
        """Set up additional UI elements after basic initialization."""
        self._place_menu_bar_on_tab_row()
        self._install_word_wrap_table_headers()

        # Date field: attach quick preset/offset menu button (removed from .ui)
        self.pushButton_food_date_quick = attach_date_edit_quick_controls(
            self.dateEdit_food,
            button_object_name="pushButton_food_date_quick",
        )

        # Set emoji for buttons
        self.pushButton_food_add.setText(f"➕ {self.pushButton_food_add.text()}")  # noqa: RUF001
        self.pushButton_food_add_with_ai.setText(f"🤖 {self.pushButton_food_add_with_ai.text()}")
        self.pushButton_food_add_by_voice.setText(f"🎙️ {self.pushButton_food_add_by_voice.text()}")
        self.action_refresh.setText(f"🔄 {self.action_refresh.text()}")
        self.action_add_food_item.setText(f"➕ {self.action_add_food_item.text()}")  # noqa: RUF001
        self.action_translate_with_ai.setText(f"🤖 {self.action_translate_with_ai.text()}")
        self.action_add_as_text.setText(f"📝 {self.action_add_as_text.text()}")
        self.action_show_all_records.setText(f"📊 {self.action_show_all_records.text()}")
        self.action_check.setText(f"🔍 {self.action_check.text()}")
        self._apply_exit_about_menu_emojis()
        self.pushButton_food_manual_name_clear.setText("🧹")
        self.pushButton_food_manual_name_clear.setToolTip("Clear food name input")
        self.pushButton_kcal_with_ai.setText("🤖")
        self.pushButton_kcal_with_ai.setToolTip(
            "Look up calories, drink flag, weight, and entry mode via AI from the food name",
        )

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

        self._setup_food_dashboard_tab()

        # Keep keyboard focus on the Food tab form only while that tab is current
        if self.tabWidget.currentWidget() is self.tab_food:
            self.lineEdit_food_manual_name.setFocus()

        # Initialize add button appearance
        self._update_add_button_appearance()

        # Set tab order for groupBox_food_add so that pushButton_food_manual_name_clear is last
        # Current order: lineEdit_food_manual_name -> pushButton_food_manual_name_clear -> spinBox_food_weight -> ...
        # Desired order: lineEdit_food_manual_name -> spinBox_food_weight -> ... -> pushButton_food_manual_name_clear

        # Set tab order to make pushButton_food_manual_name_clear the last element
        QWidget.setTabOrder(self.lineEdit_food_manual_name, self.spinBox_food_weight)
        QWidget.setTabOrder(self.spinBox_food_weight, self.doubleSpinBox_food_calories)
        QWidget.setTabOrder(self.doubleSpinBox_food_calories, self.checkBox_food_is_drink)
        QWidget.setTabOrder(self.checkBox_food_is_drink, self.radioButton_use_weight)
        QWidget.setTabOrder(self.radioButton_use_weight, self.radioButton_use_calories)
        QWidget.setTabOrder(self.radioButton_use_calories, self.dateEdit_food)
        QWidget.setTabOrder(self.dateEdit_food, self.pushButton_food_date_quick)
        QWidget.setTabOrder(self.pushButton_food_date_quick, self.pushButton_food_add)
        QWidget.setTabOrder(self.pushButton_food_add, self.pushButton_food_manual_name_clear)

    def _show_all_food_items(self) -> None:
        """Show all food items in the list (remove filtering)."""
        if self.food_items_list_model:
            for i in range(self.food_items_list_model.rowCount()):
                self.listView_food_items.setRowHidden(i, False)  # noqa: FBT003

    def _show_food_log_context_menu(self, position: QPoint) -> None:
        """Show context menu for food log table.

        Args:

        - `position` (`QPoint`): Position where context menu should appear.

        """
        # Check that a row is selected before showing the menu
        if not self.tableView_food_log.currentIndex().isValid():
            return

        # Check if multiple rows are selected
        selection_model = self.tableView_food_log.selectionModel()
        selected_indexes = selection_model.selectedIndexes() if selection_model else []
        unique_rows = {index.row() for index in selected_indexes}
        multiple_rows_selected = len(unique_rows) > 1
        selected_food_log_ids = self._get_selected_row_ids("food_log")

        # Calculate total calories from selected rows
        total_calories = 0.0
        if multiple_rows_selected:
            proxy_model = self.models["food_log"]
            if proxy_model:
                source_model = proxy_model.sourceModel()
                if isinstance(source_model, QStandardItemModel):
                    calculated_calories_column = 5  # Calculated Calories column index
                    for row in unique_rows:
                        item = source_model.item(row, calculated_calories_column)
                        if item:
                            try:
                                calories = float(item.text())
                                total_calories += calories
                            except (ValueError, TypeError):
                                pass

        context_menu = QMenu(self)
        index = self.tableView_food_log.currentIndex()
        model = self.tableView_food_log.model()

        filter_by_name_action = None
        filter_by_date_action = None
        set_date_action = None
        set_date_plus_one_action = None
        set_date_minus_one_action = None
        name_value = ""
        date_value = ""

        if not multiple_rows_selected and index.isValid() and model is not None:
            name_raw = model.data(model.index(index.row(), 0))
            date_raw = model.data(model.index(index.row(), 6))
            name_value = str(name_raw).strip() if name_raw is not None else ""
            date_value = str(date_raw).strip() if date_raw is not None else ""

            if date_value:
                set_date_action, set_date_plus_one_action, set_date_minus_one_action = add_date_in_main_field_actions(
                    context_menu
                )

        add_food_item_action = None
        add_food_item_no_weight_action = None
        if not multiple_rows_selected:
            add_separator(context_menu)
            add_food_item_action = context_menu.addAction("➕ Add to Food Items (with weight)")  # noqa: RUF001
            add_food_item_no_weight_action = context_menu.addAction("➕ Add to Food Items (without weight)")  # noqa: RUF001

        create_dish_action = None
        if multiple_rows_selected:
            add_separator(context_menu)
            create_dish_action = context_menu.addAction("🍽 Create dish from selected ingredients")

        add_separator(context_menu)
        ate_half_action = context_menu.addAction("🍽️ I ate half")
        ate_third_action = context_menu.addAction("🍽️ I ate a third")
        ate_two_thirds_action = context_menu.addAction("🍽️ I ate two thirds")
        ate_percent_action = context_menu.addAction("🍽️ I ate %…")

        add_separator(context_menu)
        swap_weight_calories_action = context_menu.addAction("🔄 Swap Weight and Calories per 100g")
        recalc_calories_ai_action = context_menu.addAction("🤖 Recalculate calories with AI")

        bulk_date_action = None
        ids_for_date_change: list[int] = []
        if multiple_rows_selected:
            ids_for_date_change = list(selected_food_log_ids)
            if len(ids_for_date_change) > 1:
                add_separator(context_menu)
                bulk_date_action = context_menu.addAction(LABEL_SET_DATE_SELECTED)

        add_separator(context_menu)
        export_action, export_excel_action = add_export_actions(context_menu)

        if multiple_rows_selected:
            add_info_action(context_menu, f"📊 Total calories: {total_calories:.1f} kcal")

        begin_filters_block(context_menu)
        if name_value:
            filter_by_name_action = context_menu.addAction(LABEL_FILTER_BY_NAME)
        if date_value:
            filter_by_date_action = context_menu.addAction(LABEL_FILTER_BY_DATE)
        clear_filters_action = add_clear_filters_action(context_menu)

        delete_action = add_delete_action(context_menu)
        apply_leading_emoji_icons(context_menu)
        action = context_menu.exec_(self.tableView_food_log.mapToGlobal(position))

        # Process the action only if it was actually selected (not None)
        if action is None:
            # User clicked outside the menu or pressed Esc - do nothing
            return

        # Temporarily disconnect the context menu signal to prevent recursive calls
        self.tableView_food_log.customContextMenuRequested.disconnect()

        try:
            if action == filter_by_name_action and name_value:
                self._filter_food_log_by_column(0, name_value)
            elif action == filter_by_date_action and date_value:
                self._filter_food_log_by_column(6, date_value.strip()[:10])
            elif action == clear_filters_action:
                self._clear_food_log_table_filter()
            elif action == set_date_action and date_value:
                self._set_date_from_table(date_value)
            elif action == set_date_plus_one_action and date_value:
                self._set_date_from_table_plus_one_day(date_value)
            elif action == set_date_minus_one_action and date_value:
                self._set_date_from_table_minus_one_day(date_value)
            elif action == add_food_item_action:
                self._add_food_item_from_log_record(include_weight=True)
            elif action == add_food_item_no_weight_action:
                self._add_food_item_from_log_record(include_weight=False)
            elif action == create_dish_action:
                self._create_dish_from_selected_ingredients()
            elif action == ate_half_action:
                self._apply_eaten_fraction_to_selected_food_log(ATE_HALF)
            elif action == ate_third_action:
                self._apply_eaten_fraction_to_selected_food_log(ATE_THIRD)
            elif action == ate_two_thirds_action:
                self._apply_eaten_fraction_to_selected_food_log(ATE_TWO_THIRDS)
            elif action == ate_percent_action:
                self._prompt_eaten_percent_and_apply()
            elif action == swap_weight_calories_action:
                self._swap_weight_and_calories_per_100g()
            elif action == recalc_calories_ai_action:
                self._recalculate_selected_food_log_calories_with_ai()
            elif action == delete_action:
                # Perform the deletion
                if multiple_rows_selected:
                    self._delete_selected_food_log_rows(selected_food_log_ids)
                else:
                    self.delete_record("food_log")
            elif bulk_date_action is not None and action == bulk_date_action:
                self._set_date_for_selected_food_log_records(ids_for_date_change)
            elif action == export_action:
                self.on_export_csv()
            elif action == export_excel_action:
                self.on_export_excel()
        finally:
            # Reconnect the context menu signal after a short delay
            QTimer.singleShot(100, self._reconnect_context_menu)

    def _show_food_translate_preview(
        self,
        names: list[str],
        response_text: str,
        *,
        unique_names_limit: int,
        filled_from_existing: int = 0,
    ) -> None:
        """Parse BotHub TSV, show preview table, and apply on user confirmation."""
        translations = parse_food_translate_response(response_text)
        if not translations:
            preview = response_text.strip()[:300]
            message_box.warning(
                self,
                "AI Response",
                f"Could not parse BotHub response.\n\nExpected TSV: Name<TAB>EnglishName\n\nResponse:\n{preview}",
            )
            return

        dialog = FoodTranslatePreviewDialog(
            self,
            names,
            translations,
            unique_names_limit,
            filled_from_existing=filled_from_existing,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            if filled_from_existing > 0:
                self._report_food_translate_completion(
                    prefix=(
                        f"Filled English names for {filled_from_existing} unique food name(s) "
                        "from existing translations in the database."
                    ),
                )
            return

        to_apply = dialog.get_translations_to_apply()
        if not to_apply:
            prefix = ""
            if filled_from_existing > 0:
                prefix = (
                    f"Filled English names for {filled_from_existing} unique food name(s) "
                    "from existing translations in the database."
                )
            message_box.information(self, "Translate with AI", "No translations selected to apply.")
            self._report_food_translate_completion(prefix=prefix)
            return

        prefix_parts: list[str] = []
        if filled_from_existing > 0:
            prefix_parts.append(
                f"Filled English names for {filled_from_existing} unique food name(s) "
                "from existing translations in the database."
            )
        self._commit_food_translate_translations(
            to_apply,
            prefix="\n\n".join(prefix_parts) if prefix_parts else "",
        )

    def _show_kcal_with_ai_context_menu(self, position: QPoint) -> None:
        """Show context menu for the kcal AI button (manual entry helpers)."""
        context_menu = QMenu(self)
        portion_weight_action = context_menu.addAction("🤖 Determine portion weight from calories")
        global_pos: QPoint = self.pushButton_kcal_with_ai.mapToGlobal(position)
        action = context_menu.exec_(global_pos)
        if action == portion_weight_action:
            self.on_portion_weight_with_ai_from_calories()

    def _show_use_calories_context_menu(self, position: QPoint) -> None:
        """Show context menu for calories mode radio button."""
        context_menu = QMenu(self)
        portion_weight_action = context_menu.addAction("🤖 Determine portion weight from calories")
        global_pos: QPoint = self.radioButton_use_calories.mapToGlobal(position)
        action = context_menu.exec_(global_pos)
        if action == portion_weight_action:
            self.on_portion_weight_with_ai_from_calories()

    def _start_bothub_worker(
        self,
        prompt_text: str,
        on_success: Callable[[str], None],
        *,
        images: list[tuple[bytes, str]] | None = None,
        image: tuple[bytes, str] | None = None,
        toast_message: str = "Requesting BotHub…",
    ) -> bool:
        """Run BotHub chat completion in a background worker."""
        return run_bothub_request(
            self,
            self._app_config,
            prompt_text,
            on_success,
            images=images,
            image=image,
            toast_message=toast_message,
            is_busy=lambda: self._bothub_state.worker is not None,
            state=self._bothub_state,
        )

    def _swap_weight_and_calories_per_100g(self) -> None:
        """Swap weight and calories per 100g values in the selected row."""
        if not self._validate_database_connection():
            message_box.warning(self, "Error", "Database connection not available")
            return

        if self.db_manager is None:
            logger.error("❌ Database manager is not initialized")
            return

        try:
            # Get the selected row data from the table model
            proxy_model = self.models["food_log"]
            if proxy_model is None:
                return
            source_model = proxy_model.sourceModel()
            if not isinstance(source_model, QStandardItemModel):
                return

            current_index = self.tableView_food_log.currentIndex()
            if not current_index.isValid():
                message_box.warning(self, "Error", "No row selected")
                return

            row = current_index.row()

            # Get data from the table model directly
            weight_str = source_model.item(row, 2).text() if source_model.item(row, 2) else "0"
            calories_per_100g_str = source_model.item(row, 3).text() if source_model.item(row, 3) else "0"

            # Parse values, handle empty strings and convert to float
            try:
                weight = float(weight_str) if weight_str and weight_str.strip() != "" else 0.0
            except (ValueError, TypeError):
                weight = 0.0

            try:
                calories_per_100g = (
                    float(calories_per_100g_str)
                    if calories_per_100g_str and calories_per_100g_str.strip() != ""
                    else 0.0
                )
            except (ValueError, TypeError):
                calories_per_100g = 0.0

            # Check if both values are 0 (no point in swapping)
            if weight == 0.0 and calories_per_100g == 0.0:
                message_box.information(
                    self, "Information", "Both weight and calories per 100g are 0. No swapping needed."
                )
                return

            # Check if portion_calories exists and might affect display
            portion_calories_str = source_model.item(row, 4).text() if source_model.item(row, 4) else "0"
            try:
                portion_calories = (
                    float(portion_calories_str) if portion_calories_str and portion_calories_str.strip() != "" else 0.0
                )
            except (ValueError, TypeError):
                portion_calories = 0.0

            # Warn user if portion_calories might affect display
            if portion_calories > 0:
                result = message_box.question(
                    self,
                    "Portion Calories Warning",
                    (
                        f"This record has portion calories ({portion_calories}), "
                        f"which might affect how calories per 100g are displayed. "
                        f"Continue with swap?"
                    ),
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No,
                )
                if result == QMessageBox.StandardButton.No:
                    return

            # Swap the values
            new_weight = calories_per_100g
            new_calories_per_100g = weight

            # Show information about the swap
            s_weight = f"weight={weight} -> {new_weight}"
            s_calories_per_100g = f"calories_per_100g={calories_per_100g} -> {new_calories_per_100g}"
            logger.info("%s", f"🔄 Swapping values: {s_weight}, {s_calories_per_100g}")

            # Update the table model
            source_model.item(row, 2).setText(str(new_weight))
            source_model.item(row, 3).setText(str(new_calories_per_100g))

            # Update calculated calories column if both values are available
            if new_weight > 0 and new_calories_per_100g > 0:
                calculated_calories = (new_weight * new_calories_per_100g) / 100
                source_model.item(row, 5).setText(f"{calculated_calories:.1f}")
                logger.info("%s", f"🔄 Updated calculated calories: {calculated_calories:.1f}")

            # Get the row ID for database update
            row_id = source_model.verticalHeaderItem(row).text()
            if row_id:
                # Update the database
                success = self.db_manager.update_food_log_weight_and_calories(
                    int(row_id), new_weight, new_calories_per_100g
                )
                if success:
                    # Refresh the table to show updated calculated calories
                    self.update_food_data()
                else:
                    logger.error("%s", f"❌ Failed to update database for row {row_id}")
                    message_box.warning(self, "Error", "Failed to update database")

        except Exception as e:
            logger.exception("Error swapping weight and calories")
            message_box.warning(self, "Error", f"Failed to swap weight and calories: {e}")

    def _transform_food_log_data(self, rows: list[list], *, append_state: bool = False) -> list[list]:
        """Transform food_log rows for table display with colors and daily totals."""
        date_to_color: dict[str, QColor] = dict(self._food_log_date_color_map) if append_state else {}
        dates_with_totals: set[str] = set(self._food_log_dates_with_totals) if append_state else set()
        color_index: int = len(date_to_color)

        date_to_total_calories: dict[str, float] = {}
        for row in rows:
            date_str = row[1]
            calculated_calories = calculate_food_log_calories(
                parse_food_log_number(row[2]),
                parse_food_log_number(row[4]),
                parse_food_log_number(row[3]),
            )
            if date_str:
                date_to_total_calories[date_str] = date_to_total_calories.get(date_str, 0.0) + calculated_calories

        transformed_rows: list[list] = []
        for row in rows:
            portion_calories = row[3]
            calories_per_100g = row[4]
            weight = row[2]
            date_str = row[1]

            if date_str not in date_to_color:
                date_to_color[date_str] = self.date_colors[color_index % len(self.date_colors)]
                color_index += 1

            if portion_calories and portion_calories > 0 and (not calories_per_100g or calories_per_100g == 0):
                calories_per_100g_display = ""
            else:
                calories_per_100g_display = calories_per_100g if calories_per_100g is not None else ""

            calculated_calories = calculate_food_log_calories(
                parse_food_log_number(weight),
                parse_food_log_number(calories_per_100g),
                parse_food_log_number(portion_calories),
            )

            is_first_of_day = date_str not in dates_with_totals
            if is_first_of_day:
                dates_with_totals.add(date_str)

            total_per_day = date_to_total_calories.get(date_str, 0.0)
            total_per_day_display = f"{total_per_day:.1f}" if is_first_of_day else ""

            transformed_row = [
                row[5],
                "1" if row[7] == 1 else "",
                row[2],
                calories_per_100g_display,
                portion_calories,
                f"{calculated_calories:.1f}",
                row[1],
                row[6],
                total_per_day_display,
            ]
            date_color = date_to_color.get(date_str, QColor(255, 255, 255))
            transformed_row.extend([row[0], date_color])
            transformed_rows.append(transformed_row)

        self._food_log_date_color_map = date_to_color
        self._food_log_dates_with_totals = dates_with_totals
        return transformed_rows

    def _update_add_button_appearance(self) -> None:
        """Update the appearance of the add button based on whether it's a drink or food."""
        is_drink = self.checkBox_food_is_drink.isChecked()

        if is_drink:
            # Drink mode: blue color and drink icon
            self.pushButton_food_add.setText("🥤 Add Drink")
            self.pushButton_food_add.setStyleSheet(
                "QPushButton {\n"
                "    background-color: #e8f5e8;\n"
                "    border: 1px solid #4CAF50;\n"
                "    border-radius: 4px;\n"
                "    color: #2E7D32;\n"
                "    }\n"
                "    QPushButton:hover {\n"
                "    background-color: #c8e6c9;\n"
                "    }\n"
                "    QPushButton:pressed {\n"
                "    background-color: #a5d6a7;\n"
                "    }"
            )
        else:
            # Food mode: default blue color and food icon
            self.pushButton_food_add.setText("➕ Add Food")  # noqa: RUF001
            self.pushButton_food_add.setStyleSheet(
                "QPushButton {\n"
                "    background-color: #e3f2fd;\n"
                "    border: 1px solid #2196F3;\n"
                "    border-radius: 4px;\n"
                "    color: #000000;\n"
                "    }\n"
                "    QPushButton:hover {\n"
                "    background-color: #bbdefb;\n"
                "    }\n"
                "    QPushButton:pressed {\n"
                "    background-color: #90caf9;\n"
                "    }"
            )

    def _update_autocomplete_data(self) -> None:
        """Update autocomplete data from database."""
        if not self._validate_database_connection():
            return

        if self.db_manager is None:
            return

        try:
            log_names = self.db_manager.get_recent_food_names_for_autocomplete(self.name_autocomplete_log_limit)
            item_names = self.db_manager.get_food_item_names_for_autocomplete()
            merged_entries = database_manager.merge_food_autocomplete_entries(log_names, item_names)

            if self.food_completer_source_model is not None:
                self.food_completer_source_model.clear()
                for entry in merged_entries:
                    item = QStandardItem(entry.name)
                    item.setData(entry.name_en or "", Qt.ItemDataRole.UserRole)
                    self.food_completer_source_model.appendRow(item)
                self.food_completer_proxy.invalidateFilter()

        except Exception:
            logger.exception("Error updating autocomplete data")

    def _update_drinks_chart(self) -> None:
        """Update the drinks chart with data from database."""
        if not self._validate_database_connection():
            logger.warning("Database connection not available for updating drinks chart")
            return

        if self.db_manager is None:
            logger.error("❌ Database manager is not initialized")
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
                "fill_zero_periods": False,
                "date_from": date_from,
                "date_to": date_to,
                "is_calories_chart": False,  # Not calories chart
            }

            # Create chart
            layout = self.scrollAreaWidgetContents_food_stats.layout()
            if layout is not None:
                self._create_chart(layout, chart_data, chart_config)

        except Exception as e:
            logger.exception("Error updating drinks chart")
            message_box.warning(self, "Chart Error", f"Failed to create drinks chart: {e}")

    def _update_food_calories_chart(self) -> None:
        """Update the food calories chart with data from database."""
        if not self._validate_database_connection():
            logger.warning("Database connection not available for updating food calories chart")
            return

        if self.db_manager is None:
            logger.error("❌ Database manager is not initialized")
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
                "fill_zero_periods": False,
                "date_from": date_from,
                "date_to": date_to,
                "is_calories_chart": True,  # Add this parameter
            }

            # Create chart
            layout = self.scrollAreaWidgetContents_food_stats.layout()
            if layout is not None:
                self._create_chart(layout, chart_data, chart_config)

        except Exception as e:
            logger.exception("Error updating food calories chart")
            message_box.warning(self, "Chart Error", f"Failed to create calories chart: {e}")

    def _update_food_items_list(self) -> None:
        """Refresh food items list view with data from database."""
        if not self._validate_database_connection():
            logger.warning("Database manager not available or connection not open")
            return

        if self.db_manager is None:
            logger.error("❌ Database manager is not initialized")
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
                    food_name = food_item_row[1]  # name is at index 1
                    is_drink = (
                        parse_is_drink_cell(food_item_row[_FOOD_ITEM_COL_IS_DRINK])
                        if len(food_item_row) > _FOOD_ITEM_COL_IS_DRINK
                        else False
                    )
                    calories_per_100g = food_item_row[4]
                    default_portion_calories = food_item_row[6]

                    # Format display name with calories info
                    display_name = format_food_name_with_calories(
                        food_name,
                        calories_per_100g,
                        default_portion_calories,
                        is_drink=is_drink,
                    )
                    item = QStandardItem(display_name)
                    self.food_items_list_model.appendRow(item)

            # Unblock signals
            if selection_model:
                selection_model.blockSignals(False)  # noqa: FBT003

        except Exception:
            logger.exception("Error updating food items list")

    def _update_food_log_table(self) -> None:
        """Update the food log table based on current display state."""
        if not self._validate_database_connection():
            logger.warning("Database connection not available for updating food log table")
            return

        if self.db_manager is None:
            logger.error("❌ Database manager is not initialized")
            return

        try:
            self._load_food_log_page(reset=True)
            self._connect_table_selection_signals()
            self._connect_table_auto_save_signals()
        except Exception as e:
            logger.exception("Error updating food log table")
            message_box.warning(self, "Database Error", f"Failed to update food log table: {e}")

    def _update_food_log_table_with_data(self, food_log_rows: list[list]) -> None:
        """Update the food log table with specific data (no pagination)."""
        if not self._validate_database_connection():
            logger.warning("Database connection not available for updating food log table")
            return

        try:
            self._reset_food_log_pagination_state()
            transformed_food_log_data = self._transform_food_log_data(food_log_rows, append_state=False)
            self.models["food_log"] = self._create_colored_food_log_table_model(
                transformed_food_log_data, self.table_config["food_log"][2]
            )
            self.tableView_food_log.setModel(self.models["food_log"])
            self.tableView_food_log.setEditTriggers(
                QTableView.EditTrigger.DoubleClicked | QTableView.EditTrigger.EditKeyPressed
            )
            food_log_header = self.tableView_food_log.horizontalHeader()
            for i in range(food_log_header.count()):
                food_log_header.setSectionResizeMode(i, food_log_header.ResizeMode.Interactive)
            self._adjust_food_log_table_columns()
            self._food_log_pagination.record_first_page(len(food_log_rows), None, pagination_enabled=False)
            self._connect_table_selection_signals()
            self._connect_table_auto_save_signals()
        except Exception as e:
            logger.exception("Error updating food log table")
            message_box.warning(self, "Database Error", f"Failed to update food log table: {e}")

    def _update_food_weight_chart(self) -> None:
        """Update the food weight chart with data from database."""
        if not self._validate_database_connection():
            logger.warning("Database connection not available for updating food weight chart")
            return

        if self.db_manager is None:
            logger.error("❌ Database manager is not initialized")
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
                "title": f"Food Weight Consumed (excluding drinks) ({period})",
                "xlabel": "Date",
                "ylabel": "Weight (kg)",
                "color": "green",
                "show_stats": True,
                "stats_unit": "kg",
                "period": period,
                "fill_zero_periods": False,
                "date_from": date_from,
                "date_to": date_to,
                "is_calories_chart": False,  # Not calories chart
            }

            # Create chart
            layout = self.scrollAreaWidgetContents_food_stats.layout()
            if layout is not None:
                self._create_chart(layout, chart_data, chart_config)

        except Exception as e:
            logger.exception("Error updating food weight chart")
            message_box.warning(self, "Chart Error", f"Failed to create food weight chart: {e}")

    def _update_kcal_per_day_table(self) -> None:
        """Update the calories per day table with data from database."""
        if not self._validate_database_connection():
            logger.warning("Database connection not available for updating kcal per day table")
            return

        if self.db_manager is None:
            logger.error("❌ Database manager is not initialized")
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
            logger.exception("Error updating kcal per day table")
            message_box.warning(self, "Database Error", f"Failed to load calories per day data: {e}")
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, *, hide_on_close: bool = False) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def __init__(self, *, hide_on_close: bool = False) -> None:  # noqa: D107
        super().__init__()
        try_apply_system_backdrop(self, backdrop=SystemBackdrop.MICA)
        self.setupUi(self)
        self._food_dashboard: FoodDashboardWidget | None = None
        self._setup_ui()

        # Set window icon
        self.setWindowIcon(QIcon(":/assets/logo.svg"))

        self._init_hide_on_close(hide_on_close=hide_on_close)

        # Initialize core attributes
        self._is_closing = False
        self.db_manager: database_manager.DatabaseManager | None = None
        self._app_config: dict[str, Any] = h.dev.config_load(get_config_path_str())

        # Food items list model
        self.food_items_list_model: QStandardItemModel | None = None

        # Table models dictionary
        self.models: dict[str, QSortFilterProxyModel | None] = {
            "food_log": None,
            "kcal_per_day": None,
        }

        # Food log display state
        initial_count, load_more_count = get_apps_list_limits(self._app_config)
        self.count_food_records_to_show: int = initial_count
        self.food_log_load_more_count: int = load_more_count
        self.name_autocomplete_log_limit: int = initial_count
        self.show_all_food_records: bool = False

        # Food log table pagination state
        self._food_log_pagination = ScrollPagination()
        self._food_log_dates_with_totals: set[str] = set()
        self._food_log_date_color_map: dict[str, QColor] = {}

        # Dialog state to prevent multiple dialogs
        self._food_item_dialog_open: bool = False
        self._bothub_state = BothubRequestState()

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
                    "Total per day",
                ],
            ),
            "kcal_per_day": (
                self.tableView_kcal_per_day,
                "kcal_per_day",
                ["Date", "Calories"],
            ),
        }

        # Define colors for different dates (expanded palette)
        self.date_colors = generate_pastel_qcolors(50)

        # Chart configuration
        self.max_count_points_in_charts = 50

        # Initialize application
        self._init_database()
        self._setup_autocomplete()
        self._connect_signals()
        self._init_food_log_table_delegates()
        self._init_food_items_list()
        self.set_today_date()  # Set current date in dateEdit_food
        self.update_food_data()
        self._setup_window_size_and_position()

        # Initialize food stats date range with earliest date from database
        self._init_food_stats_dates()

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
        if self._hide_instead_of_close(event):
            return

        self._is_closing = True

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
            logger.error("❌ Database manager is not initialized")
            return

        # Use appropriate database manager method
        success = False
        try:
            if table_name == "food_log":
                success = self.db_manager.delete_food_log_record(record_id)
        except Exception as e:
            message_box.warning(self, "Database Error", f"Failed to delete record: {e}")
            return

        if success:
            self.update_food_data()
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
        if self._handle_ctrl_c_for_tables(event, [self.tableView_food_log]):
            return

        # Handle Enter key on various widgets to trigger add button
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            focused_widget = QApplication.focusWidget()
            if focused_widget in (
                self.doubleSpinBox_food_calories,
                self.spinBox_food_weight,
                self.checkBox_food_is_drink,
                self.pushButton_food_add,
            ):
                self.pushButton_food_add.click()
                return

        # Handle Delete key on tableView_food_log to trigger delete button

        # Call parent implementation for other key events
        super().keyPressEvent(event)
```

</details>

### ⚙️ Method `on_add_as_text`

```python
def on_add_as_text(self) -> None
```

Open text input dialog and process entered food items.

<details>
<summary>Code:</summary>

```python
def on_add_as_text(self) -> None:
        if not self._validate_database_connection():
            message_box.warning(self, "Error", "Database connection not available")
            return
        self._open_text_input_dialog(self.dateEdit_food.date())
```

</details>

### ⚙️ Method `on_add_food_item`

```python
def on_add_food_item(self) -> None
```

Create a new food item via the edit dialog (prefilled from manual food entry form).

<details>
<summary>Code:</summary>

```python
def on_add_food_item(self) -> None:
        name = self.lineEdit_food_manual_name.text().strip()
        if not name:
            message_box.warning(self, "Error", "Enter food name")
            return

        if self.db_manager is None:
            logger.error("❌ Database manager is not initialized")
            return

        try:
            is_drink = self.checkBox_food_is_drink.isChecked()
            weight = float(self.spinBox_food_weight.value())
            calories_value = float(self.doubleSpinBox_food_calories.value())
            use_weight = self.radioButton_use_weight.isChecked()

            if use_weight:
                calories_per_100g = calories_value if calories_value > 0 else None
                portion_calories = None
            else:
                calories_per_100g = None
                portion_calories = calories_value if calories_value > 0 else None

            prefill = database_manager.FoodLogItemByNameRow(
                name=name,
                name_en=None,
                is_drink=is_drink,
                calories_per_100g=calories_per_100g,
                weight=weight if weight > 0 else None,
                portion_calories=portion_calories,
            )

            dialog = FoodItemDialog(self, prefill, is_create=True)
            if dialog.exec() != QDialog.DialogCode.Accepted:
                return

            data = dialog.get_edited_data()
            if not self.db_manager.add_food_item(
                name=str(data["name"]),
                name_en=data["name_en"],
                is_drink=bool(data["is_drink"]),
                calories_per_100g=data["calories_per_100g"],
                default_portion_weight=data["default_portion_weight"],
                default_portion_calories=data["default_portion_calories"],
            ):
                message_box.warning(self, "Error", "Failed to add food item")
                return

            self.update_food_data()

        except Exception as e:
            message_box.warning(self, "Database Error", f"Failed to add food item: {e}")
```

</details>

### ⚙️ Method `on_add_food_log`

```python
def on_add_food_log(self) -> None
```

Insert a new food log record using database manager.

<details>
<summary>Code:</summary>

```python
def on_add_food_log(self) -> None:
        # Get values from UI
        food_name = self.lineEdit_food_manual_name.text().strip()
        weight = self.spinBox_food_weight.value()
        calories = self.doubleSpinBox_food_calories.value()
        food_date = self.dateEdit_food.date().toString("yyyy-MM-dd")
        use_weight = self.radioButton_use_weight.isChecked()
        is_drink = self.checkBox_food_is_drink.isChecked()

        # Validate required fields
        if not food_name:
            message_box.warning(self, "Error", "Enter food name")
            return

        if weight <= 0:
            message_box.warning(self, "Error", "Weight is required")
            self.spinBox_food_weight.setFocus()
            self.spinBox_food_weight.selectAll()
            return

        # Validate calories based on radio button selection
        if not use_weight and calories <= 0:
            message_box.warning(self, "Error", "Calories are required when using portion mode")
            return

        # Validate the date
        if not self._is_valid_date(food_date):
            message_box.warning(self, "Error", "Invalid date format")
            return

        if self.db_manager is None:
            logger.error("❌ Database manager is not initialized")
            return

        try:
            # Double-check radio button state before processing
            use_weight_final = self.radioButton_use_weight.isChecked()

            # Determine calories_per_100g and portion_calories based on radio button
            if use_weight_final:
                # Weight mode: calories is calories_per_100g
                calories_per_100g = max(0, calories)
                portion_calories = None
            else:
                # Portion mode: calories is portion_calories, set calories_per_100g to 0
                calories_per_100g = 0  # Required by database schema (NOT NULL)
                portion_calories = calories if calories > 0 else None

            # Reuse an existing English translation for the same food name, if any.
            known_translations = self.db_manager.lookup_existing_name_en_for_names([food_name])
            name_en = known_translations.get(food_name)

            # Use database manager method
            if self.db_manager.add_food_log_record(
                date=food_date,
                calories_per_100g=calories_per_100g,
                name=food_name,
                name_en=name_en,
                weight=weight,
                portion_calories=portion_calories,
                is_drink=is_drink,
            ):
                # Update UI - only food-related data
                self.update_food_data()

                # Clear form fields after successful addition
                self.lineEdit_food_manual_name.clear()
                self.spinBox_food_weight.setValue(0)
                self.doubleSpinBox_food_calories.setValue(0.0)
                self.checkBox_food_is_drink.setChecked(False)

                # Reset radio buttons to default state
                self.radioButton_use_weight.setChecked(True)
                self.radioButton_use_calories.setChecked(False)

                # Update button appearance and calories calculation
                self._update_add_button_appearance()
                self.update_calories_calculation()

                # Keep focus on food name field for next entry
                self.lineEdit_food_manual_name.setFocus()

            else:
                message_box.warning(self, "Error", "Failed to add food log record")

        except Exception as e:
            message_box.warning(self, "Database Error", f"Failed to add food log record: {e}")
```

</details>

### ⚙️ Method `on_check_problematic_records`

```python
def on_check_problematic_records(self) -> None
```

Filter food log table to show only problematic records.

<details>
<summary>Code:</summary>

```python
def on_check_problematic_records(self) -> None:
        if not self._validate_database_connection():
            message_box.warning(self, "Error", "Database connection not available")
            return

        if self.db_manager is None:
            logger.error("❌ Database manager is not initialized")
            return

        try:
            # Get problematic records from database
            problematic_records = self.db_manager.get_problematic_food_records()

            if not problematic_records:
                message_box.information(self, "No Issues", "No problematic records found!")
                return

            # Update the food log table with only problematic records
            self._update_food_log_table_with_data(problematic_records)

            missing_weight = sum(1 for row in problematic_records if self._food_log_row_missing_weight(row))
            missing_calories = sum(1 for row in problematic_records if self._food_log_row_missing_calories(row))
            details = [
                f"Found {len(problematic_records)} problematic record(s).",
                f"• Missing or zero weight: {missing_weight}",
                f"• Missing calories (non-drink): {missing_calories}",
            ]
            message_box.information(self, "Problematic Records", "\n".join(details))

        except Exception as e:
            message_box.warning(self, "Error", f"Failed to check problematic records: {e}")
```

</details>

### ⚙️ Method `on_clear_food_manual_name`

```python
def on_clear_food_manual_name(self) -> None
```

Clear the food manual name input field.

<details>
<summary>Code:</summary>

```python
def on_clear_food_manual_name(self) -> None:
        self.lineEdit_food_manual_name.clear()
        # Reset drink checkbox and button appearance
        self.checkBox_food_is_drink.setChecked(False)
        self._update_add_button_appearance()
        # Move focus back to the cleared field
        self.lineEdit_food_manual_name.setFocus()
```

</details>

### ⚙️ Method `on_export_csv`

```python
def on_export_csv(self) -> None
```

Save current food log view as CSV (Excel is also offered).

<details>
<summary>Code:</summary>

```python
def on_export_csv(self) -> None:
        self._export_food_log_table(prefer="csv")
```

</details>

### ⚙️ Method `on_export_excel`

```python
def on_export_excel(self) -> None
```

Save current food log view as Excel (CSV is also offered).

<details>
<summary>Code:</summary>

```python
def on_export_excel(self) -> None:
        self._export_food_log_table(prefer="xlsx")
```

</details>

### ⚙️ Method `on_food_add_by_voice`

```python
def on_food_add_by_voice(self) -> None
```

Record speech, transcribe via BotHub, convert to food log TSV, then open preview dialog.

<details>
<summary>Code:</summary>

```python
def on_food_add_by_voice(self) -> None:
        self._run_food_add_by_voice()
```

</details>

### ⚙️ Method `on_food_add_with_ai`

```python
def on_food_add_with_ai(self, *, initial_image_path: str | None = None, initial_image_paths: list[str] | None = None) -> None
```

Collect text/images, call BotHub, then open food text dialog with AI result.

<details>
<summary>Code:</summary>

```python
def on_food_add_with_ai(
        self,
        *,
        initial_image_path: str | None = None,
        initial_image_paths: list[str] | None = None,
    ) -> None:
        max_image_side = get_max_image_side(self._app_config)
        source_dialog = AiSourceDialog(
            self,
            max_image_side=max_image_side,
            initial_image_path=initial_image_path,
            initial_image_paths=initial_image_paths,
        )
        source_result = source_dialog.exec()
        if source_result == QDialog.DialogCode.Rejected:
            return
        if source_result == AiSourceDialog.SKIP_MANUAL:
            self._open_text_input_dialog(self.dateEdit_food.date())
            return

        self._send_food_log_to_ai(
            source_dialog.get_raw_text(),
            source_dialog.get_images_bytes_and_mime(),
        )
```

</details>

### ⚙️ Method `on_food_dashboard_add_photo`

```python
def on_food_dashboard_add_photo(self) -> None
```

Open a large photo-only form and send the image to AI.

<details>
<summary>Code:</summary>

```python
def on_food_dashboard_add_photo(self) -> None:
        if not self._validate_database_connection():
            message_box.warning(self, "Error", "Database connection not available")
            return
        source_dialog = create_food_dashboard_photo_dialog(
            self,
            max_image_side=get_max_image_side(self._app_config),
        )
        if source_dialog.exec() != QDialog.DialogCode.Accepted:
            return
        self._send_food_log_to_ai(
            source_dialog.get_raw_text(),
            source_dialog.get_images_bytes_and_mime(),
        )
```

</details>

### ⚙️ Method `on_food_dashboard_add_text`

```python
def on_food_dashboard_add_text(self) -> None
```

Open a large text-only form and send the description to AI.

<details>
<summary>Code:</summary>

```python
def on_food_dashboard_add_text(self) -> None:
        if not self._validate_database_connection():
            message_box.warning(self, "Error", "Database connection not available")
            return
        source_dialog = create_food_dashboard_text_dialog(self)
        if source_dialog.exec() != QDialog.DialogCode.Accepted:
            return
        self._send_food_log_to_ai(source_dialog.get_raw_text())
```

</details>

### ⚙️ Method `on_food_dashboard_add_voice`

```python
def on_food_dashboard_add_voice(self) -> None
```

Open a large recording form and send speech to AI.

<details>
<summary>Code:</summary>

```python
def on_food_dashboard_add_voice(self) -> None:
        self._run_food_add_by_voice(large_ui=True)
```

</details>

### ⚙️ Method `on_food_item_double_clicked`

```python
def on_food_item_double_clicked(self, _index: QModelIndex) -> None
```

Handle double click on food item in the list view.

Args:

- `_index` (`QModelIndex`): Index of the double-clicked item.

<details>
<summary>Code:</summary>

```python
def on_food_item_double_clicked(self, _index: QModelIndex) -> None:
        # Prevent multiple dialogs from opening
        if self._food_item_dialog_open:
            return

        food_item = self._get_current_selected_food_item()
        if not food_item:
            return

        # Check if database manager is available and connection is open
        if not self._validate_database_connection():
            logger.warning("Database manager not available or connection not open")
            return

        if self.db_manager is None:
            logger.error("❌ Database manager is not initialized")
            return

        try:
            # Set dialog open flag
            self._food_item_dialog_open = True

            # Get food item data from food_items table
            food_item_data = self.db_manager.get_food_item_by_name(food_item)

            if food_item_data:
                dialog = FoodItemDialog(self, food_item_data, is_create=False)
            else:
                food_log_data = self.db_manager.get_food_log_item_by_name(food_item)
                if not food_log_data:
                    message_box.warning(
                        self,
                        "Error",
                        f"Food item '{food_item}' not found in database or food log!",
                    )
                    return
                dialog = FoodItemDialog(self, food_log_data, is_create=True)

            result = dialog.exec_()

            # Only process if dialog was accepted (not cancelled)
            if result == QDialog.DialogCode.Accepted:
                if hasattr(dialog, "delete_confirmed") and dialog.delete_confirmed:
                    if not isinstance(food_item_data, database_manager.FoodItemByNameRow):
                        return
                    food_id = food_item_data.id
                    if self.db_manager.delete_food_item(food_id):
                        message_box.information(self, "Success", f"Food item '{food_item}' deleted successfully!")
                        self.update_food_data()
                    else:
                        message_box.warning(self, "Error", f"Failed to delete food item '{food_item}'!")
                else:
                    edited_data = dialog.get_edited_data()
                    if food_item_data:
                        food_id = food_item_data.id
                        if self.db_manager.update_food_item(
                            food_item_id=food_id,
                            name=edited_data["name"],
                            name_en=edited_data["name_en"],
                            is_drink=edited_data["is_drink"],
                            calories_per_100g=edited_data["calories_per_100g"],
                            default_portion_weight=edited_data["default_portion_weight"],
                            default_portion_calories=edited_data["default_portion_calories"],
                        ):
                            message_box.information(
                                self, "Success", f"Food item '{edited_data['name']}' updated successfully!"
                            )
                            self.update_food_data()
                        else:
                            message_box.warning(self, "Error", f"Failed to update food item '{edited_data['name']}'!")
                    elif self.db_manager.add_food_item(
                        name=edited_data["name"],
                        name_en=edited_data["name_en"],
                        is_drink=edited_data["is_drink"],
                        calories_per_100g=edited_data["calories_per_100g"],
                        default_portion_weight=edited_data["default_portion_weight"],
                        default_portion_calories=edited_data["default_portion_calories"],
                    ):
                        message_box.information(
                            self, "Success", f"Food item '{edited_data['name']}' created successfully!"
                        )
                        self.update_food_data()
                    else:
                        message_box.warning(self, "Error", f"Failed to create food item '{edited_data['name']}'!")

            # If result is Rejected (Cancel), do nothing - just close the dialog
            # No need for additional logic here

        except Exception as e:
            logger.exception("Error in food item double clicked")
            message_box.warning(self, "Error", f"Error editing food item: {e}")
        finally:
            # Always reset the dialog open flag
            self._food_item_dialog_open = False
```

</details>

### ⚙️ Method `on_food_log_table_cell_clicked`

```python
def on_food_log_table_cell_clicked(self, index: QModelIndex) -> None
```

Handle food log table cell click and populate form fields with row data.

Args:

- `index` (`QModelIndex`): Index of the clicked cell.

<details>
<summary>Code:</summary>

```python
def on_food_log_table_cell_clicked(self, index: QModelIndex) -> None:
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
            name = source_model.item(index.row(), 0).text() if source_model.item(index.row(), 0) else ""
            is_drink_item = source_model.item(index.row(), 1)
            is_drink = parse_is_drink_cell(is_drink_item.data(Qt.ItemDataRole.EditRole)) if is_drink_item else False
            weight_str = source_model.item(index.row(), 2).text() if source_model.item(index.row(), 2) else "0"
            calories_per_100g_str = (
                source_model.item(index.row(), 3).text() if source_model.item(index.row(), 3) else "0"
            )
            portion_calories_str = (
                source_model.item(index.row(), 4).text() if source_model.item(index.row(), 4) else "0"
            )

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
            self._update_add_button_appearance()

            # Determine radio button state based on portion_calories
            if portion_calories > 0:
                # Use portion calories mode
                self.radioButton_use_calories.setChecked(True)
                self.doubleSpinBox_food_calories.setValue(portion_calories)
            else:
                # Use weight mode
                self.radioButton_use_weight.setChecked(True)
                self.doubleSpinBox_food_calories.setValue(calories_per_100g)

            # Update calories calculation
            self.update_calories_calculation()

            # Move focus to weight spinbox and select all text
            self.spinBox_food_weight.setFocus()
            self.spinBox_food_weight.selectAll()

        except Exception:
            logger.exception("Error in food log table cell clicked")
```

</details>

### ⚙️ Method `on_food_stats_all_time`

```python
def on_food_stats_all_time(self) -> None
```

Set date range to all available data and update chart.

<details>
<summary>Code:</summary>

```python
def on_food_stats_all_time(self) -> None:
        if not self.db_manager or not self._validate_database_connection():
            return

        try:
            # Get earliest date from database
            earliest_date_str = self.db_manager.get_earliest_food_log_date()
            if earliest_date_str:
                earliest_date = QDate.fromString(earliest_date_str, "yyyy-MM-dd")
                if QDate.isValid(earliest_date.year(), earliest_date.month(), earliest_date.day()):
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

        except Exception:
            logger.exception("Error setting all time date range")
            # Fallback to last year if any error occurs
            today = QDate.currentDate()
            year_ago = today.addYears(-1)
            self.dateEdit_food_stats_from.setDate(year_ago)
            self.dateEdit_food_stats_to.setDate(today)
            self._update_food_calories_chart()
```

</details>

### ⚙️ Method `on_food_stats_drink`

```python
def on_food_stats_drink(self) -> None
```

Show drinks chart.

<details>
<summary>Code:</summary>

```python
def on_food_stats_drink(self) -> None:
        self._update_drinks_chart()
```

</details>

### ⚙️ Method `on_food_stats_food_weight`

```python
def on_food_stats_food_weight(self) -> None
```

Show food weight chart.

<details>
<summary>Code:</summary>

```python
def on_food_stats_food_weight(self) -> None:
        self._update_food_weight_chart()
```

</details>

### ⚙️ Method `on_food_stats_last_month`

```python
def on_food_stats_last_month(self) -> None
```

Set date range to last month and update chart.

<details>
<summary>Code:</summary>

```python
def on_food_stats_last_month(self) -> None:
        today = QDate.currentDate()
        month_ago = today.addMonths(-1)

        self.dateEdit_food_stats_from.setDate(month_ago)
        self.dateEdit_food_stats_to.setDate(today)

        self._update_food_calories_chart()
```

</details>

### ⚙️ Method `on_food_stats_last_week`

```python
def on_food_stats_last_week(self) -> None
```

Set date range to last week and update chart.

<details>
<summary>Code:</summary>

```python
def on_food_stats_last_week(self) -> None:
        today = QDate.currentDate()
        week_ago = today.addDays(-7)

        self.dateEdit_food_stats_from.setDate(week_ago)
        self.dateEdit_food_stats_to.setDate(today)

        self._update_food_calories_chart()
```

</details>

### ⚙️ Method `on_food_stats_last_year`

```python
def on_food_stats_last_year(self) -> None
```

Set date range to last year and update chart.

<details>
<summary>Code:</summary>

```python
def on_food_stats_last_year(self) -> None:
        today = QDate.currentDate()
        year_ago = today.addYears(-1)

        self.dateEdit_food_stats_from.setDate(year_ago)
        self.dateEdit_food_stats_to.setDate(today)

        self._update_food_calories_chart()
```

</details>

### ⚙️ Method `on_food_stats_period_changed`

```python
def on_food_stats_period_changed(self) -> None
```

Handle period selection change and update chart.

<details>
<summary>Code:</summary>

```python
def on_food_stats_period_changed(self) -> None:
        self._update_food_calories_chart()
```

</details>

### ⚙️ Method `on_food_stats_update`

```python
def on_food_stats_update(self) -> None
```

Update the food calories chart.

<details>
<summary>Code:</summary>

```python
def on_food_stats_update(self) -> None:
        self._update_food_calories_chart()
```

</details>

### ⚙️ Method `on_kcal_with_ai`

```python
def on_kcal_with_ai(self) -> None
```

Look up calories, drink flag, mode, and weight via BotHub from the food name.

<details>
<summary>Code:</summary>

```python
def on_kcal_with_ai(self) -> None:
        food_name = self.lineEdit_food_manual_name.text().strip()
        if not food_name:
            message_box.warning(self, "Food Name", "Enter a food name first.")
            return

        try:
            prompt_text = build_prompt(self._app_config, "food_kcal_lookup", {"FOOD_NAME": food_name})
        except ValueError as exc:
            show_bothub_prompt_build_error(self, exc)
            return

        def on_success(response_text: str) -> None:
            result = parse_kcal_lookup_response(response_text)
            if result is None:
                preview = response_text.strip()[:200]
                message_box.warning(
                    self,
                    "AI Response",
                    "Could not parse BotHub response.\n\nExpected TSV: Calories, Mode, Drink, Weight\n\n"
                    f"Response:\n{preview}",
                )
                return
            self._apply_kcal_lookup_result(result)

        self._start_bothub_worker(prompt_text, on_success)
```

</details>

### ⚙️ Method `on_main_food_item_selection_changed`

```python
def on_main_food_item_selection_changed(self, current: QModelIndex, _previous: QModelIndex) -> None
```

Handle food item selection change in the list view.

Args:

- `current` (`QModelIndex`): Current selected index.
- `_previous` (`QModelIndex`): Previously selected index.

<details>
<summary>Code:</summary>

```python
def on_main_food_item_selection_changed(self, current: QModelIndex, _previous: QModelIndex) -> None:
        if not current.isValid():
            return

        if self.food_items_list_model:
            item = self.food_items_list_model.itemFromIndex(current)
            if item:
                food_name = extract_food_name_from_display(item.text())
                self._process_food_item_selection(food_name)
```

</details>

### ⚙️ Method `on_portion_weight_with_ai_from_calories`

```python
def on_portion_weight_with_ai_from_calories(self) -> None
```

Determine portion weight and drink flag via BotHub for calories-mode entry.

<details>
<summary>Code:</summary>

```python
def on_portion_weight_with_ai_from_calories(self) -> None:
        if self.radioButton_use_weight.isChecked():
            message_box.warning(
                self,
                "Mode",
                "Switch to 'Enter calories directly' mode first.",
            )
            return

        food_name = self.lineEdit_food_manual_name.text().strip()
        if not food_name:
            message_box.warning(self, "Food Name", "Enter a food name first.")
            return

        calories_total = float(self.doubleSpinBox_food_calories.value())
        if calories_total <= 0:
            message_box.warning(self, "Calories", "Enter calories first.")
            return

        drink = "yes" if self.checkBox_food_is_drink.isChecked() else "no"
        try:
            prompt_text = build_prompt(
                self._app_config,
                "food_portion_weight_from_calories",
                {
                    "FOOD_NAME": food_name,
                    "CALORIES_TOTAL": f"{calories_total:.1f}",
                    "DRINK": drink,
                },
            )
        except ValueError as exc:
            show_bothub_prompt_build_error(self, exc)
            return

        def on_success(response_text: str) -> None:
            result = parse_portion_weight_response(response_text)
            if result is None:
                preview = response_text.strip()[:200]
                message_box.warning(
                    self,
                    "AI Response",
                    f"Could not parse BotHub response.\n\nExpected TSV: Drink, Weight\n\nResponse:\n{preview}",
                )
                return

            self.checkBox_food_is_drink.setChecked(result.is_drink)
            if result.weight_g > 0:
                self.spinBox_food_weight.setValue(result.weight_g)
            self.update_calories_calculation()
            self._update_add_button_appearance()

        self._start_bothub_worker(prompt_text, on_success)
```

</details>

### ⚙️ Method `on_show_all_records_clicked`

```python
def on_show_all_records_clicked(self) -> None
```

Toggle between showing all records and last self.count_food_records_to_show records.

<details>
<summary>Code:</summary>

```python
def on_show_all_records_clicked(self) -> None:
        self.show_all_food_records = not self.show_all_food_records

        # Update menu action text
        if self.show_all_food_records:
            set_action_text_with_emoji_icon(
                self.action_show_all_records,
                f"📊 Show Last {self.count_food_records_to_show}",
            )
        else:
            set_action_text_with_emoji_icon(self.action_show_all_records, "📊 Show All Records")

        # Refresh the food log table
        self._update_food_log_table()
```

</details>

### ⚙️ Method `on_translate_with_ai`

```python
def on_translate_with_ai(self) -> None
```

Translate missing food_log name_en values via BotHub from unique Russian names.

<details>
<summary>Code:</summary>

```python
def on_translate_with_ai(self) -> None:
        if self.db_manager is None:
            logger.error("❌ Database manager is not initialized")
            return

        unique_names_limit = self._food_log_translate_names_limit()
        names = self.db_manager.get_unique_food_log_names_missing_name_en(limit=unique_names_limit)
        if not names:
            self._report_food_translate_completion()
            return

        known_translations = self.db_manager.lookup_existing_name_en_for_names(names)
        filled_from_existing = 0
        if known_translations:
            filled_from_existing = self._commit_food_translate_translations(
                known_translations,
                show_completion=False,
            )

        names_for_ai = [name for name in names if name not in known_translations]
        if not names_for_ai:
            prefix = ""
            if filled_from_existing > 0:
                prefix = (
                    f"Filled English names for {filled_from_existing} unique food name(s) "
                    "from existing translations in the database."
                )
            self._report_food_translate_completion(prefix=prefix)
            return

        food_names_text = "\n".join(names_for_ai)
        try:
            prompt_text = build_prompt(
                self._app_config,
                "food_log_translate_names",
                {"FOOD_NAMES": food_names_text},
            )
        except ValueError as exc:
            show_bothub_prompt_build_error(self, exc)
            return

        def on_success(response_text: str) -> None:
            self._show_food_translate_preview(
                names_for_ai,
                response_text,
                unique_names_limit=unique_names_limit,
                filled_from_existing=filled_from_existing,
            )

        self._start_bothub_worker(prompt_text, on_success)
```

</details>

### ⚙️ Method `resizeEvent`

```python
def resizeEvent(self, _event: QResizeEvent) -> None
```

Handle window resize event and adjust table column widths proportionally.

Args:

- `_event` (`QResizeEvent`): The resize event.

<details>
<summary>Code:</summary>

```python
def resizeEvent(self, _event: QResizeEvent) -> None:  # noqa: N802
        # Call parent resize event first
        super().resizeEvent(_event)

        # Adjust food log table column widths based on window size
        self._adjust_food_log_table_columns()
```

</details>

### ⚙️ Method `set_today_date`

```python
def set_today_date(self) -> None
```

Set today's date in the food date edit field.

<details>
<summary>Code:</summary>

```python
def set_today_date(self) -> None:
        today_qdate = QDate.currentDate()
        self.dateEdit_food.setDate(today_qdate)
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
            logger.warning("Database connection not available for showing tables")
            return

        if self.db_manager is None:
            logger.error("❌ Database manager is not initialized")
            return

        try:
            self._load_food_log_page(reset=True)
            self._connect_table_selection_signals()
            self._connect_table_auto_save_signals()
            self.update_food_calories_today()
        except Exception as e:
            logger.exception("Error showing tables")
            message_box.warning(self, "Database Error", f"Failed to load tables: {e}")
```

</details>

### ⚙️ Method `update_calories_calculation`

```python
def update_calories_calculation(self) -> None
```

Update the calories calculation label based on radio button selection and values.

<details>
<summary>Code:</summary>

```python
def update_calories_calculation(self) -> None:
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
```

</details>

### ⚙️ Method `update_food_calories_today`

```python
def update_food_calories_today(self) -> None
```

Update the label showing calories consumed today and drinks weight in liters (comma as decimal separator).

<details>
<summary>Code:</summary>

```python
def update_food_calories_today(self) -> None:
        if self.db_manager is None:
            logger.error("❌ Database manager is not initialized")
            return

        if not self._validate_database_connection():
            self.label_food_today.setText("0 kcal\n0,0 liters")
            if self._food_dashboard is not None:
                self._food_dashboard.set_today_calories(0)
            return

        try:
            calories = self.db_manager.get_food_calories_today()
            drinks_weight = self.db_manager.get_drinks_weight_today()
            drinks_liters = drinks_weight / 1000 if drinks_weight else 0.0
            drinks_liters_str = f"{drinks_liters:.1f}"
            self.label_food_today.setText(f"{calories:.1f} kcal \n{drinks_liters_str} liters")
            if self._food_dashboard is not None:
                self._food_dashboard.set_today_calories(calories)
        except Exception:
            logger.exception("Error getting food calories for today")
            self.label_food_today.setText("0 kcal\n0,0 liters")
            if self._food_dashboard is not None:
                self._food_dashboard.set_today_calories(0)
```

</details>

### ⚙️ Method `update_food_data`

```python
def update_food_data(self) -> None
```

Refresh food-related data only.

Updates food items lists and calories count.

<details>
<summary>Code:</summary>

```python
def update_food_data(self) -> None:
        if not self._validate_database_connection():
            logger.warning("Database connection not available for update_food_data")
            return

        # Update food items list
        self._update_food_items_list()
        self._update_autocomplete_data()
        self.update_food_calories_today()
        self.show_tables()
```

</details>
