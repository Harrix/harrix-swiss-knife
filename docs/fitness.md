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
  - [Method `_format_chart_x_axis`](#method-_format_chart_x_axis)
  - [Method `_get_exercise_avif_path`](#method-_get_exercise_avif_path)
  - [Method `_group_exercise_data_by_period`](#method-_group_exercise_data_by_period)
  - [Method `_increment_date_after_add`](#method-_increment_date_after_add)
  - [Method `_init_database`](#method-_init_database)
  - [Method `_init_exercise_chart_controls`](#method-_init_exercise_chart_controls)
  - [Method `_init_filter_controls`](#method-_init_filter_controls)
  - [Method `_init_weight_chart_controls`](#method-_init_weight_chart_controls)
  - [Method `_is_valid_date`](#method-_is_valid_date)
  - [Method `_load_default_exercise_chart`](#method-_load_default_exercise_chart)
  - [Method `_load_exercise_avif`](#method-_load_exercise_avif)
  - [Method `_next_avif_frame`](#method-_next_avif_frame)
  - [Method `_update_comboboxes`](#method-_update_comboboxes)
  - [Method `_update_record_generic`](#method-_update_record_generic)
  - [Method `add_record_generic`](#method-add_record_generic)
  - [Method `apply_filter`](#method-apply_filter)
  - [Method `clear_filter`](#method-clear_filter)
  - [Method `closeEvent`](#method-closeevent)
  - [Method `delete_record`](#method-delete_record)
  - [Method `on_add_exercise`](#method-on_add_exercise)
  - [Method `on_add_record`](#method-on_add_record)
  - [Method `on_add_type`](#method-on_add_type)
  - [Method `on_add_weight`](#method-on_add_weight)
  - [Method `on_exercise_changed`](#method-on_exercise_changed)
  - [Method `on_exercise_selection_changed`](#method-on_exercise_selection_changed)
  - [Method `on_export_csv`](#method-on_export_csv)
  - [Method `on_refresh_statistics`](#method-on_refresh_statistics)
  - [Method `on_tab_changed`](#method-on_tab_changed)
  - [Method `on_update_exercises`](#method-on_update_exercises)
  - [Method `on_update_process`](#method-on_update_process)
  - [Method `on_update_types`](#method-on_update_types)
  - [Method `on_update_weight`](#method-on_update_weight)
  - [Method `set_chart_all_time`](#method-set_chart_all_time)
  - [Method `set_chart_last_month`](#method-set_chart_last_month)
  - [Method `set_chart_last_year`](#method-set_chart_last_year)
  - [Method `set_current_date`](#method-set_current_date)
  - [Method `set_weight_all_time`](#method-set_weight_all_time)
  - [Method `set_weight_last_month`](#method-set_weight_last_month)
  - [Method `set_weight_last_year`](#method-set_weight_last_year)
  - [Method `show_tables`](#method-show_tables)
  - [Method `update_all`](#method-update_all)
  - [Method `update_chart_comboboxes`](#method-update_chart_comboboxes)
  - [Method `update_chart_type_combobox`](#method-update_chart_type_combobox)
  - [Method `update_exercise_chart`](#method-update_exercise_chart)
  - [Method `update_filter_comboboxes`](#method-update_filter_comboboxes)
  - [Method `update_filter_type_combobox`](#method-update_filter_type_combobox)
  - [Method `update_weight_chart`](#method-update_weight_chart)

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

        self.current_movie: QMovie | None = None

        # Add attributes for AVI animation
        self.avif_frames: list = []
        self.current_frame_index: int = 0
        self.avif_timer: QTimer | None = None

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
                ["Exercise", "Unit of Measurement", "Type Required"],
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
        self._init_weight_chart_controls()
        self._init_exercise_chart_controls()
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

        # Weight chart signals
        self.pushButton_update_weight_chart.clicked.connect(self.update_weight_chart)
        self.pushButton_weight_last_month.clicked.connect(self.set_weight_last_month)
        self.pushButton_weight_last_year.clicked.connect(self.set_weight_last_year)
        self.pushButton_weight_all_time.clicked.connect(self.set_weight_all_time)

        # Exercise chart signals
        self.pushButton_update_chart.clicked.connect(self.update_exercise_chart)
        self.pushButton_chart_last_month.clicked.connect(self.set_chart_last_month)
        self.pushButton_chart_last_year.clicked.connect(self.set_chart_last_year)
        self.pushButton_chart_all_time.clicked.connect(self.set_chart_all_time)
        self.comboBox_chart_exercise.currentIndexChanged.connect(self.update_chart_type_combobox)

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

    def _format_chart_x_axis(self, ax: plt.Axes, dates: list, period: str) -> None:
        """Format x-axis for exercise charts based on period and data range."""
        if not dates:
            return

        from matplotlib.ticker import MaxNLocator

        days_in_month = 31
        days_in_year = 365

        if period == "Days":
            # Limit to max 10-15 ticks
            ax.xaxis.set_major_locator(MaxNLocator(nbins=10, prune="both"))

            date_range = (max(dates) - min(dates)).days
            if date_range <= days_in_month or date_range <= days_in_year:
                ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
            else:
                ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))

        elif period == "Months":
            ax.xaxis.set_major_locator(MaxNLocator(nbins=12, prune="both"))
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))

        elif period == "Years":
            ax.xaxis.set_major_locator(MaxNLocator(nbins=10, prune="both"))
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

        # Rotate date labels for better readability
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha="right")

    def _get_exercise_avif_path(self, exercise_name: str) -> Path | None:
        """Get the path to the AVIF file for the given exercise.

        Args:

        - `exercise_name` (`str`): Name of the exercise.

        Returns:

        - `Path | None`: Path to the AVIF file if it exists, None otherwise.

        """
        if not exercise_name or not self.db_manager:
            return None

        # Form path to AVIF file using exercise name directly
        db_path = Path(config["sqlite_fitness"])
        avif_dir = db_path.parent / "fitness_img"
        avif_path = avif_dir / f"{exercise_name}.avif"

        return avif_path if avif_path.exists() else None

    def _group_exercise_data_by_period(self, rows: list, period: str) -> dict:
        """Group exercise data by the specified period (Days, Months, Years)."""
        grouped = defaultdict(float)

        # Regex pattern for YYYY-MM-DD format
        date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")

        for date_str, value_str in rows:
            # Quick validation without exceptions
            if not date_pattern.match(date_str):
                continue

            try:
                value = float(value_str)
            except (ValueError, TypeError):
                continue

            # Safe date parsing with proper error handling
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            except ValueError:
                # Skip invalid dates (e.g., Feb 30, Apr 31, etc.)
                continue

            if period == "Days":
                key = date_obj
            elif period == "Months":
                key = date_obj.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            elif period == "Years":
                key = date_obj.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            else:
                key = date_obj

            grouped[key] += value

        return dict(sorted(grouped.items()))

    def _increment_date_after_add(self) -> None:
        """Move `date` edit one day forward unless it already shows today.

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
        """Open the SQLite file from `config` (ask the user if missing).

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

    def _init_exercise_chart_controls(self) -> None:
        """Initialize exercise chart controls."""
        current_date = QDate.currentDate()
        self.dateEdit_chart_from.setDate(current_date.addMonths(-1))
        self.dateEdit_chart_to.setDate(current_date)

        # Initialize exercise combobox
        self.update_chart_comboboxes()

    def _init_filter_controls(self) -> None:
        """Prepare widgets on the `Filters` group box.

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

    def _init_weight_chart_controls(self) -> None:
        """Initialize weight chart date controls."""
        current_date = QDate.currentDate()
        self.dateEdit_weight_from.setDate(current_date.addMonths(-1))
        self.dateEdit_weight_to.setDate(current_date)

    @staticmethod
    def _is_valid_date(date_str: str) -> bool:
        """Return `True` if `YYYY-MM-DD` formatted `date_str` is correct.

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

    def _load_default_exercise_chart(self) -> None:
        """Load default exercise chart on first visit to charts tab."""
        if not hasattr(self, "_charts_initialized"):
            self._charts_initialized = True

            # Set period to Months
            self.comboBox_chart_period.setCurrentText("Months")

            # Try to set exercise with _id = 39
            if self.db_manager:
                rows = self.db_manager.get_rows("SELECT name FROM exercises WHERE _id = 39")
                if rows:
                    exercise_name = rows[0][0]
                    index = self.comboBox_chart_exercise.findText(exercise_name)
                    if index >= 0:
                        self.comboBox_chart_exercise.setCurrentIndex(index)

            # Load chart with all time data
            self.set_chart_all_time()

    def _load_exercise_avif(self, exercise_name: str) -> None:
        """Load and display AVIF animation for the given exercise using Pillow with AVIF support."""
        # Stop current animation if exists
        if self.current_movie:
            self.current_movie.stop()
            self.current_movie = None

        # Stop AVIF animation if exists
        if self.avif_timer:
            self.avif_timer.stop()
            self.avif_timer = None

        self.avif_frames = []
        self.current_frame_index = 0

        # Clear label and reset alignment
        self.label_exercise_avif.clear()
        self.label_exercise_avif.setAlignment(Qt.AlignCenter)

        if not exercise_name:
            self.label_exercise_avif.setText("No exercise selected")
            return

        # Get path to AVIF
        avif_path = self._get_exercise_avif_path(exercise_name)

        if avif_path is None:
            self.label_exercise_avif.setText(f"No AVIF found for:\n{exercise_name}")
            return

        try:
            # Try Qt native first
            from PySide6.QtGui import QPixmap

            pixmap = QPixmap(str(avif_path))

            if not pixmap.isNull():
                label_size = self.label_exercise_avif.size()
                scaled_pixmap = pixmap.scaled(label_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.label_exercise_avif.setPixmap(scaled_pixmap)
                return

            # Fallback to Pillow with AVIF plugin for animation
            try:
                import pillow_avif  # noqa: F401

                # Open with Pillow
                pil_image = Image.open(avif_path)

                # Handle animated AVIF
                if hasattr(pil_image, "is_animated") and pil_image.is_animated:
                    # Extract all frames
                    self.avif_frames = []
                    label_size = self.label_exercise_avif.size()

                    for frame_index in range(pil_image.n_frames):
                        pil_image.seek(frame_index)

                        # Create a copy of the frame
                        frame = pil_image.copy()

                        # Convert to RGB if needed
                        if frame.mode in ("RGBA", "LA", "P"):
                            background = Image.new("RGB", frame.size, (255, 255, 255))
                            if frame.mode == "P":
                                frame = frame.convert("RGBA")
                            if frame.mode in ("RGBA", "LA"):
                                background.paste(frame, mask=frame.split()[-1])
                            else:
                                background.paste(frame)
                            frame = background
                        elif frame.mode != "RGB":
                            frame = frame.convert("RGB")

                        # Convert PIL image to QPixmap
                        buffer = io.BytesIO()
                        frame.save(buffer, format="PNG")
                        buffer.seek(0)

                        pixmap = QPixmap()
                        pixmap.loadFromData(buffer.getvalue())

                        if not pixmap.isNull():
                            scaled_pixmap = pixmap.scaled(label_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                            self.avif_frames.append(scaled_pixmap)

                    if self.avif_frames:
                        # Show first frame
                        self.label_exercise_avif.setPixmap(self.avif_frames[0])

                        # Start animation timer
                        self.avif_timer = QTimer()
                        self.avif_timer.timeout.connect(self._next_avif_frame)

                        # Get frame duration (default 100ms if not available)
                        try:
                            duration = pil_image.info.get("duration", 100)
                        except Exception:
                            duration = 100

                        self.avif_timer.start(duration)
                        return
                else:
                    # Static image
                    frame = pil_image

                    # Convert to RGB if needed
                    if frame.mode in ("RGBA", "LA", "P"):
                        background = Image.new("RGB", frame.size, (255, 255, 255))
                        if frame.mode == "P":
                            frame = frame.convert("RGBA")
                        if frame.mode in ("RGBA", "LA"):
                            background.paste(frame, mask=frame.split()[-1])
                        else:
                            background.paste(frame)
                        frame = background
                    elif frame.mode != "RGB":
                        frame = frame.convert("RGB")

                    # Convert PIL image to QPixmap
                    buffer = io.BytesIO()
                    frame.save(buffer, format="PNG")
                    buffer.seek(0)

                    pixmap = QPixmap()
                    pixmap.loadFromData(buffer.getvalue())

                    if not pixmap.isNull():
                        label_size = self.label_exercise_avif.size()
                        scaled_pixmap = pixmap.scaled(label_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        self.label_exercise_avif.setPixmap(scaled_pixmap)
                        return

            except ImportError as import_error:
                print(f"Import error: {import_error}")
                self.label_exercise_avif.setText(f"AVIF plugin not available:\n{exercise_name}")
                return
            except Exception as pil_error:
                print(f"Pillow error: {pil_error}")

            self.label_exercise_avif.setText(f"Cannot load AVIF:\n{exercise_name}")

        except Exception as e:
            print(f"General error: {e}")
            self.label_exercise_avif.setText(f"Error loading AVIF:\n{exercise_name}\n{e}")

    def _next_avif_frame(self) -> None:
        """Show next frame in AVIF animation."""
        if not self.avif_frames:
            return

        self.current_frame_index = (self.current_frame_index + 1) % len(self.avif_frames)
        self.label_exercise_avif.setPixmap(self.avif_frames[self.current_frame_index])

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
        """Add a single row to `any` table.

        Args:

        - `table_name` (`str`): Target table (must be one of `self._SAFE_TABLES`).
        - `query_text` (`str`): SQL `INSERT` statement with named placeholders.
        - `params` (`dict`): Mapping for the placeholders.

        Returns:

        - `bool`: `True` if the row was written successfully.

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
        """Apply combo-box/date filters to the `process` table.

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

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        """Handle application close event."""
        # Stop animations
        if self.current_movie:
            self.current_movie.stop()
        if self.avif_timer:
            self.avif_timer.stop()

        event.accept()

    def delete_record(self, table_name: str) -> None:
        """Delete selected row from `table_name` (must be safe).

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

        # Получаем значение чекбокса
        is_type_required = 1 if self.check_box_is_type_required.isChecked() else 0

        self.add_record_generic(
            "exercises",
            "INSERT INTO exercises (name, unit, is_type_required) VALUES (:name, :unit, :is_type_required)",
            {"name": exercise, "unit": unit, "is_type_required": is_type_required},
        )

    def on_add_record(self) -> None:
        """Insert a new `process` row.

        Adds a new exercise record to the process table using the currently selected
        exercise, type, count, and date values. Validates that exercise type is provided
        when required. Automatically advances the date after successful addition.
        """
        exercise = self.comboBox_exercise.currentText()
        ex_id = self.db_manager.get_id("exercises", "name", exercise)
        if ex_id is None:
            return

        type_name = self.comboBox_type.currentText()

        # Check if exercise type is required
        is_type_required_query = "SELECT is_type_required FROM exercises WHERE _id = :ex_id"
        rows = self.db_manager.get_rows(is_type_required_query, {"ex_id": ex_id})

        if rows and rows[0][0] == 1 and not type_name.strip():
            QMessageBox.warning(self, "Error", f"Exercise type is required for '{exercise}'. Please select a type.")
            return

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
        """Insert a new exercise `type` for the selected exercise.

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
        """Load exercise types for the newly selected exercise in `comboBox_type`.

        Updates the exercise type combo box with the types associated with the
        currently selected exercise. Automatically selects the most recently used
        type for this exercise from the process table. Also loads the exercise AVIF.
        """
        exercise = self.comboBox_exercise.currentText()

        self._load_exercise_avif(exercise)

        ex_id = self.db_manager.get_id("exercises", "name", exercise)
        if ex_id is None:
            return

        # Get all types for this exercise
        types = self.db_manager.get_items(
            "types",
            "type",
            condition=f"_id_exercises = {ex_id}",
        )

        # Clear and populate the combobox
        self.comboBox_type.clear()
        self.comboBox_type.addItem("")
        self.comboBox_type.addItems(types)

        # Find the most recently used type for this exercise
        last_type_query = """
            SELECT t.type
            FROM process p
            LEFT JOIN types t ON p._id_types = t._id AND t._id_exercises = p._id_exercises
            WHERE p._id_exercises = :ex_id
            ORDER BY p._id DESC
            LIMIT 1
        """

        rows = self.db_manager.get_rows(last_type_query, {"ex_id": ex_id})

        if rows:
            last_type = rows[0][0] if rows[0][0] is not None else ""
            # Find and select this type in the combobox
            type_index = self.comboBox_type.findText(last_type)
            if type_index >= 0:
                self.comboBox_type.setCurrentIndex(type_index)

    def on_exercise_selection_changed(self) -> None:
        """Update form fields when exercise selection changes in the table.

        Synchronizes the form fields (name, unit, is_type_required checkbox)
        with the currently selected exercise in the table.
        """
        index = self.tableView_exercises.currentIndex()
        if not index.isValid():
            # Clear the fields if nothing is selected
            self.lineEdit_exercise_name.clear()
            self.lineEdit_exercise_unit.clear()
            self.check_box_is_type_required.setChecked(False)
            return

        model = self.models["exercises"]
        row = index.row()

        # Fill in the fields with data from the selected row
        name = model.data(model.index(row, 0)) or ""
        unit = model.data(model.index(row, 1)) or ""
        is_required = model.data(model.index(row, 2)) or "0"

        self.lineEdit_exercise_name.setText(name)
        self.lineEdit_exercise_unit.setText(unit)
        self.check_box_is_type_required.setChecked(is_required == "1")

    def on_export_csv(self) -> None:
        """Save current `process` view to a CSV file (semicolon-separated).

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
        index_tab_weight = 5
        index_tab_charts = 4

        if index == 0:  # Main tab
            self.update_filter_comboboxes()
        elif index == index_tab_charts:  # Exercise Chart tab
            self.update_chart_comboboxes()
            self._load_default_exercise_chart()
        elif index == index_tab_weight:
            self.set_weight_all_time()

    def on_update_exercises(self) -> None:
        """Update the selected exercise row.

        Updates the name, unit, and is_type_required of the currently selected exercise in the
        exercises table.
        """
        self._update_record_generic(
            "exercises",
            "exercises",
            "UPDATE exercises SET name = :n, unit = :u, is_type_required = :itr WHERE _id = :id",
            lambda r, m, _id: {
                "n": m.data(m.index(r, 0)),
                "u": m.data(m.index(r, 1)),
                "itr": 1 if m.data(m.index(r, 2)) == "1" else 0,
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
        """Update the selected `types` row.

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

    def set_chart_all_time(self) -> None:
        """Set chart date range to all available data."""
        # Get the earliest process record
        rows = self.db_manager.get_rows("SELECT MIN(date) FROM process WHERE date IS NOT NULL")

        if rows and rows[0][0]:
            earliest_date = QDate.fromString(rows[0][0], "yyyy-MM-dd")
            self.dateEdit_chart_from.setDate(earliest_date)
        else:
            # Fallback to one year ago if no data
            current_date = QDate.currentDate()
            self.dateEdit_chart_from.setDate(current_date.addYears(-1))

        self.dateEdit_chart_to.setDate(QDate.currentDate())
        self.update_exercise_chart()

    def set_chart_last_month(self) -> None:
        """Set chart date range to last month."""
        current_date = QDate.currentDate()
        self.dateEdit_chart_from.setDate(current_date.addMonths(-1))
        self.dateEdit_chart_to.setDate(current_date)
        self.update_exercise_chart()

    def set_chart_last_year(self) -> None:
        """Set chart date range to last year."""
        current_date = QDate.currentDate()
        self.dateEdit_chart_from.setDate(current_date.addYears(-1))
        self.dateEdit_chart_to.setDate(current_date)
        self.update_exercise_chart()

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

    def set_weight_all_time(self) -> None:
        """Set weight chart date range to all available data."""
        # Get the earliest weight record
        rows = self.db_manager.get_rows("SELECT MIN(date) FROM weight WHERE date IS NOT NULL")

        if rows and rows[0][0]:
            earliest_date = QDate.fromString(rows[0][0], "yyyy-MM-dd")
            self.dateEdit_weight_from.setDate(earliest_date)
        else:
            # Fallback to one year ago if no data
            current_date = QDate.currentDate()
            self.dateEdit_weight_from.setDate(current_date.addYears(-1))

        self.dateEdit_weight_to.setDate(QDate.currentDate())
        self.update_weight_chart()

    def set_weight_last_month(self) -> None:
        """Set weight chart date range to last month."""
        current_date = QDate.currentDate()
        self.dateEdit_weight_from.setDate(current_date.addMonths(-1))
        self.dateEdit_weight_to.setDate(current_date)
        self.update_weight_chart()

    def set_weight_last_year(self) -> None:
        """Set weight chart date range to last year."""
        current_date = QDate.currentDate()
        self.dateEdit_weight_from.setDate(current_date.addYears(-1))
        self.dateEdit_weight_to.setDate(current_date)
        self.update_weight_chart()

    def show_tables(self) -> None:
        """Populate all four `QTableView`s from the database.

        Loads data from the database into all table views:

        - Process table (exercise records)
        - Exercises table
        - Exercise types table
        - Weight table
        """
        # exercises - adding new field
        rows = self.db_manager.get_rows("SELECT _id, name, unit, is_type_required FROM exercises")
        # Update column headers
        exercises_headers = ["Exercise", "Unit of Measurement", "Type Required"]
        self.models["exercises"] = self._create_table_model(
            rows,
            exercises_headers,
        )
        self.tableView_exercises.setModel(self.models["exercises"])
        self.tableView_exercises.resizeColumnsToContents()

        # Connect selection change signal AFTER setting the model
        selection_model = self.tableView_exercises.selectionModel()
        if selection_model:
            # Qt automatically avoids duplicate connections
            selection_model.currentRowChanged.connect(self.on_exercise_selection_changed)

        # Other tables remain unchanged...
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

        # Clear the exercise addition form after updating
        self.lineEdit_exercise_name.clear()
        self.lineEdit_exercise_unit.clear()
        self.check_box_is_type_required.setChecked(False)

        # Upload a AVIF for the currently selected exercise
        current_exercise_name = self.comboBox_exercise.currentText()
        self._load_exercise_avif(current_exercise_name)

    def update_chart_comboboxes(self) -> None:
        """Update exercise and type comboboxes for charts."""
        # Update exercise combobox
        exercises = self.db_manager.get_items("exercises", "name")

        self.comboBox_chart_exercise.blockSignals(True)  # noqa: FBT003
        self.comboBox_chart_exercise.clear()
        if exercises:
            self.comboBox_chart_exercise.addItems(exercises)
        self.comboBox_chart_exercise.blockSignals(False)  # noqa: FBT003

        # Update type combobox
        self.update_chart_type_combobox()

    def update_chart_type_combobox(self) -> None:
        """Update chart type combobox based on selected exercise."""
        self.comboBox_chart_type.clear()
        self.comboBox_chart_type.addItem("All types")

        exercise = self.comboBox_chart_exercise.currentText()
        if exercise:
            ex_id = self.db_manager.get_id("exercises", "name", exercise)
            if ex_id is not None:
                types = self.db_manager.get_items(
                    "types",
                    "type",
                    condition=f"_id_exercises = {ex_id}",
                )
                self.comboBox_chart_type.addItems(types)

    def update_exercise_chart(self) -> None:
        """Update the exercise chart with current filters."""
        exercise = self.comboBox_chart_exercise.currentText()
        exercise_type = self.comboBox_chart_type.currentText()
        period = self.comboBox_chart_period.currentText()
        date_from = self.dateEdit_chart_from.date().toString("yyyy-MM-dd")
        date_to = self.dateEdit_chart_to.date().toString("yyyy-MM-dd")

        # Clear existing chart
        layout = self.verticalLayout_charts_content
        for i in reversed(range(layout.count())):
            child = layout.takeAt(i).widget()
            if child:
                child.setParent(None)

        if not exercise:
            from PySide6.QtWidgets import QLabel

            no_data_label = QLabel("Please select an exercise")
            no_data_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(no_data_label)
            return

        # Build query based on filters
        conditions = ["e.name = :exercise", "p.date BETWEEN :date_from AND :date_to"]
        params = {"exercise": exercise, "date_from": date_from, "date_to": date_to}

        if exercise_type and exercise_type != "All types":
            conditions.append("t.type = :type")
            params["type"] = exercise_type

        query = f"""
            SELECT p.date, p.value
            FROM process p
            JOIN exercises e ON p._id_exercises = e._id
            LEFT JOIN types t ON p._id_types = t._id AND t._id_exercises = e._id
            WHERE {" AND ".join(conditions)}
            ORDER BY p.date ASC
        """

        rows = self.db_manager.get_rows(query, params)

        if not rows:
            from PySide6.QtWidgets import QLabel

            no_data_label = QLabel("No data found for the selected filters")
            no_data_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(no_data_label)
            return

        # Group data by period
        grouped_data = self._group_exercise_data_by_period(rows, period)

        if not grouped_data:
            from PySide6.QtWidgets import QLabel

            no_data_label = QLabel("No data to display")
            no_data_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(no_data_label)
            return

        # Create matplotlib figure
        fig = Figure(figsize=(12, 6), dpi=100)
        canvas = FigureCanvas(fig)

        # Create plot
        ax = fig.add_subplot(111)

        # Extract dates and values
        dates = list(grouped_data.keys())
        values = list(grouped_data.values())

        # Plot line without markers
        ax.plot(dates, values, "b-", linewidth=2, alpha=0.8)

        # Customize the plot
        ax.set_xlabel("Date", fontsize=12)
        ax.set_ylabel("Total Value", fontsize=12)

        chart_title = f"{exercise}"
        if exercise_type and exercise_type != "All types":
            chart_title += f" - {exercise_type}"
        chart_title += f" ({period})"

        ax.set_title(chart_title, fontsize=14, fontweight="bold")
        ax.grid(visible=True, alpha=0.3)

        # Format x-axis dates
        self._format_chart_x_axis(ax, dates, period)

        # Add statistics
        if len(values) > 1:
            min_value = min(values)
            max_value = max(values)
            avg_value = sum(values) / len(values)
            total_value = sum(values)

            stats_text = (
                f"Min: {min_value:.1f} | Max: {max_value:.1f} | Avg: {avg_value:.1f} | Total: {total_value:.1f}"
            )
            ax.text(
                0.5,
                0.02,
                stats_text,
                transform=ax.transAxes,
                ha="center",
                va="bottom",
                fontsize=10,
                bbox={"boxstyle": "round,pad=0.3", "facecolor": "lightgray", "alpha": 0.8},
            )

        # Adjust layout to prevent label cutoff
        fig.tight_layout()

        # Add canvas to layout
        layout.addWidget(canvas)

        # Force update
        canvas.draw()

    def update_filter_comboboxes(self) -> None:
        """Refresh `exercise` and `type` combo-boxes in the filter group.

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
        """Populate `type` filter based on the `exercise` filter selection.

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

    def update_weight_chart(self) -> None:
        """Update the weight chart with current date range."""
        date_from = self.dateEdit_weight_from.date().toString("yyyy-MM-dd")
        date_to = self.dateEdit_weight_to.date().toString("yyyy-MM-dd")

        # Clear existing chart
        layout = self.verticalLayout_weight_chart_content
        for i in reversed(range(layout.count())):
            child = layout.takeAt(i).widget()
            if child:
                child.setParent(None)

        # Get weight data
        query = """
            SELECT value, date
            FROM weight
            WHERE date BETWEEN :date_from AND :date_to
            AND date IS NOT NULL
            ORDER BY date ASC
        """

        rows = self.db_manager.get_rows(query, {"date_from": date_from, "date_to": date_to})

        if not rows:
            from PySide6.QtWidgets import QLabel

            no_data_label = QLabel("No weight data found for the selected period")
            no_data_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(no_data_label)
            return

        # Create matplotlib figure
        fig = Figure(figsize=(12, 6), dpi=100)
        canvas = FigureCanvas(fig)

        # Parse data
        weights = [float(row[0]) for row in rows]
        dates = [datetime.strptime(row[1], "%Y-%m-%d").replace(tzinfo=timezone.utc) for row in rows]

        # Create plot
        ax = fig.add_subplot(111)

        # Plot line
        ax.plot(
            dates,
            weights,
            "b-",
            linewidth=2,
            alpha=0.8,
        )

        # Customize the plot
        ax.set_xlabel("Date", fontsize=12)
        ax.set_ylabel("Weight (kg)", fontsize=12)
        ax.set_title("Weight Progress", fontsize=14, fontweight="bold")
        ax.grid(visible=True, alpha=0.3)

        # Define constants at the top of your file or function
        days_in_month = 31
        days_in_year = 365

        # Format x-axis dates
        if len(dates) > 0:
            date_range = (max(dates) - min(dates)).days

            if date_range <= days_in_month:  # Less than a month
                ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(dates) // 10)))
                ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
            elif date_range <= days_in_year:  # Less than a year
                ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=max(1, len(dates) // 10)))
                ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
            else:  # More than a year
                ax.xaxis.set_major_locator(mdates.MonthLocator(interval=max(1, date_range // days_in_year)))
                ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))

        # Rotate date labels
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha="right")

        # Add statistics
        if len(weights) > 1:
            min_weight = min(weights)
            max_weight = max(weights)
            avg_weight = sum(weights) / len(weights)
            weight_change = weights[-1] - weights[0]

            stats_text = (
                f"Min: {min_weight:.1f} kg | Max: {max_weight:.1f} kg | "
                f"Avg: {avg_weight:.1f} kg | Change: {weight_change:+.1f} kg"
            )
            ax.text(
                0.5,
                0.02,
                stats_text,
                transform=ax.transAxes,
                ha="center",
                va="bottom",
                fontsize=10,
                bbox={"boxstyle": "round,pad=0.3", "facecolor": "lightgray", "alpha": 0.8},
            )

        # Adjust layout to prevent label cutoff
        fig.tight_layout()

        # Add canvas to layout
        layout.addWidget(canvas)

        # Force update
        canvas.draw()
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

        self.current_movie: QMovie | None = None

        # Add attributes for AVI animation
        self.avif_frames: list = []
        self.current_frame_index: int = 0
        self.avif_timer: QTimer | None = None

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
                ["Exercise", "Unit of Measurement", "Type Required"],
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
        self._init_weight_chart_controls()
        self._init_exercise_chart_controls()
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

        # Weight chart signals
        self.pushButton_update_weight_chart.clicked.connect(self.update_weight_chart)
        self.pushButton_weight_last_month.clicked.connect(self.set_weight_last_month)
        self.pushButton_weight_last_year.clicked.connect(self.set_weight_last_year)
        self.pushButton_weight_all_time.clicked.connect(self.set_weight_all_time)

        # Exercise chart signals
        self.pushButton_update_chart.clicked.connect(self.update_exercise_chart)
        self.pushButton_chart_last_month.clicked.connect(self.set_chart_last_month)
        self.pushButton_chart_last_year.clicked.connect(self.set_chart_last_year)
        self.pushButton_chart_all_time.clicked.connect(self.set_chart_all_time)
        self.comboBox_chart_exercise.currentIndexChanged.connect(self.update_chart_type_combobox)
```

</details>

### Method `_create_table_model`

```python
def _create_table_model(self, data: list[list[str]], headers: list[str], id_column: int = 0) -> QSortFilterProxyModel
```

Return a proxy model filled with `data`.

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

### Method `_format_chart_x_axis`

```python
def _format_chart_x_axis(self, ax: plt.Axes, dates: list, period: str) -> None
```

Format x-axis for exercise charts based on period and data range.

<details>
<summary>Code:</summary>

```python
def _format_chart_x_axis(self, ax: plt.Axes, dates: list, period: str) -> None:
        if not dates:
            return

        from matplotlib.ticker import MaxNLocator

        days_in_month = 31
        days_in_year = 365

        if period == "Days":
            # Limit to max 10-15 ticks
            ax.xaxis.set_major_locator(MaxNLocator(nbins=10, prune="both"))

            date_range = (max(dates) - min(dates)).days
            if date_range <= days_in_month or date_range <= days_in_year:
                ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
            else:
                ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))

        elif period == "Months":
            ax.xaxis.set_major_locator(MaxNLocator(nbins=12, prune="both"))
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))

        elif period == "Years":
            ax.xaxis.set_major_locator(MaxNLocator(nbins=10, prune="both"))
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

        # Rotate date labels for better readability
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha="right")
```

</details>

### Method `_get_exercise_avif_path`

```python
def _get_exercise_avif_path(self, exercise_name: str) -> Path | None
```

Get the path to the AVIF file for the given exercise.

Args:

- `exercise_name` (`str`): Name of the exercise.

Returns:

- `Path | None`: Path to the AVIF file if it exists, None otherwise.

<details>
<summary>Code:</summary>

```python
def _get_exercise_avif_path(self, exercise_name: str) -> Path | None:
        if not exercise_name or not self.db_manager:
            return None

        # Form path to AVIF file using exercise name directly
        db_path = Path(config["sqlite_fitness"])
        avif_dir = db_path.parent / "fitness_img"
        avif_path = avif_dir / f"{exercise_name}.avif"

        return avif_path if avif_path.exists() else None
```

</details>

### Method `_group_exercise_data_by_period`

```python
def _group_exercise_data_by_period(self, rows: list, period: str) -> dict
```

Group exercise data by the specified period (Days, Months, Years).

<details>
<summary>Code:</summary>

```python
def _group_exercise_data_by_period(self, rows: list, period: str) -> dict:
        grouped = defaultdict(float)

        # Regex pattern for YYYY-MM-DD format
        date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")

        for date_str, value_str in rows:
            # Quick validation without exceptions
            if not date_pattern.match(date_str):
                continue

            try:
                value = float(value_str)
            except (ValueError, TypeError):
                continue

            # Safe date parsing with proper error handling
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            except ValueError:
                # Skip invalid dates (e.g., Feb 30, Apr 31, etc.)
                continue

            if period == "Days":
                key = date_obj
            elif period == "Months":
                key = date_obj.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            elif period == "Years":
                key = date_obj.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            else:
                key = date_obj

            grouped[key] += value

        return dict(sorted(grouped.items()))
```

</details>

### Method `_increment_date_after_add`

```python
def _increment_date_after_add(self) -> None
```

Move `date` edit one day forward unless it already shows today.

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

Open the SQLite file from `config` (ask the user if missing).

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

### Method `_init_exercise_chart_controls`

```python
def _init_exercise_chart_controls(self) -> None
```

Initialize exercise chart controls.

<details>
<summary>Code:</summary>

```python
def _init_exercise_chart_controls(self) -> None:
        current_date = QDate.currentDate()
        self.dateEdit_chart_from.setDate(current_date.addMonths(-1))
        self.dateEdit_chart_to.setDate(current_date)

        # Initialize exercise combobox
        self.update_chart_comboboxes()
```

</details>

### Method `_init_filter_controls`

```python
def _init_filter_controls(self) -> None
```

Prepare widgets on the `Filters` group box.

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

### Method `_init_weight_chart_controls`

```python
def _init_weight_chart_controls(self) -> None
```

Initialize weight chart date controls.

<details>
<summary>Code:</summary>

```python
def _init_weight_chart_controls(self) -> None:
        current_date = QDate.currentDate()
        self.dateEdit_weight_from.setDate(current_date.addMonths(-1))
        self.dateEdit_weight_to.setDate(current_date)
```

</details>

### Method `_is_valid_date`

```python
def _is_valid_date(date_str: str) -> bool
```

Return `True` if `YYYY-MM-DD` formatted `date_str` is correct.

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

### Method `_load_default_exercise_chart`

```python
def _load_default_exercise_chart(self) -> None
```

Load default exercise chart on first visit to charts tab.

<details>
<summary>Code:</summary>

```python
def _load_default_exercise_chart(self) -> None:
        if not hasattr(self, "_charts_initialized"):
            self._charts_initialized = True

            # Set period to Months
            self.comboBox_chart_period.setCurrentText("Months")

            # Try to set exercise with _id = 39
            if self.db_manager:
                rows = self.db_manager.get_rows("SELECT name FROM exercises WHERE _id = 39")
                if rows:
                    exercise_name = rows[0][0]
                    index = self.comboBox_chart_exercise.findText(exercise_name)
                    if index >= 0:
                        self.comboBox_chart_exercise.setCurrentIndex(index)

            # Load chart with all time data
            self.set_chart_all_time()
```

</details>

### Method `_load_exercise_avif`

```python
def _load_exercise_avif(self, exercise_name: str) -> None
```

Load and display AVIF animation for the given exercise using Pillow with AVIF support.

<details>
<summary>Code:</summary>

```python
def _load_exercise_avif(self, exercise_name: str) -> None:
        # Stop current animation if exists
        if self.current_movie:
            self.current_movie.stop()
            self.current_movie = None

        # Stop AVIF animation if exists
        if self.avif_timer:
            self.avif_timer.stop()
            self.avif_timer = None

        self.avif_frames = []
        self.current_frame_index = 0

        # Clear label and reset alignment
        self.label_exercise_avif.clear()
        self.label_exercise_avif.setAlignment(Qt.AlignCenter)

        if not exercise_name:
            self.label_exercise_avif.setText("No exercise selected")
            return

        # Get path to AVIF
        avif_path = self._get_exercise_avif_path(exercise_name)

        if avif_path is None:
            self.label_exercise_avif.setText(f"No AVIF found for:\n{exercise_name}")
            return

        try:
            # Try Qt native first
            from PySide6.QtGui import QPixmap

            pixmap = QPixmap(str(avif_path))

            if not pixmap.isNull():
                label_size = self.label_exercise_avif.size()
                scaled_pixmap = pixmap.scaled(label_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.label_exercise_avif.setPixmap(scaled_pixmap)
                return

            # Fallback to Pillow with AVIF plugin for animation
            try:
                import pillow_avif  # noqa: F401

                # Open with Pillow
                pil_image = Image.open(avif_path)

                # Handle animated AVIF
                if hasattr(pil_image, "is_animated") and pil_image.is_animated:
                    # Extract all frames
                    self.avif_frames = []
                    label_size = self.label_exercise_avif.size()

                    for frame_index in range(pil_image.n_frames):
                        pil_image.seek(frame_index)

                        # Create a copy of the frame
                        frame = pil_image.copy()

                        # Convert to RGB if needed
                        if frame.mode in ("RGBA", "LA", "P"):
                            background = Image.new("RGB", frame.size, (255, 255, 255))
                            if frame.mode == "P":
                                frame = frame.convert("RGBA")
                            if frame.mode in ("RGBA", "LA"):
                                background.paste(frame, mask=frame.split()[-1])
                            else:
                                background.paste(frame)
                            frame = background
                        elif frame.mode != "RGB":
                            frame = frame.convert("RGB")

                        # Convert PIL image to QPixmap
                        buffer = io.BytesIO()
                        frame.save(buffer, format="PNG")
                        buffer.seek(0)

                        pixmap = QPixmap()
                        pixmap.loadFromData(buffer.getvalue())

                        if not pixmap.isNull():
                            scaled_pixmap = pixmap.scaled(label_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                            self.avif_frames.append(scaled_pixmap)

                    if self.avif_frames:
                        # Show first frame
                        self.label_exercise_avif.setPixmap(self.avif_frames[0])

                        # Start animation timer
                        self.avif_timer = QTimer()
                        self.avif_timer.timeout.connect(self._next_avif_frame)

                        # Get frame duration (default 100ms if not available)
                        try:
                            duration = pil_image.info.get("duration", 100)
                        except Exception:
                            duration = 100

                        self.avif_timer.start(duration)
                        return
                else:
                    # Static image
                    frame = pil_image

                    # Convert to RGB if needed
                    if frame.mode in ("RGBA", "LA", "P"):
                        background = Image.new("RGB", frame.size, (255, 255, 255))
                        if frame.mode == "P":
                            frame = frame.convert("RGBA")
                        if frame.mode in ("RGBA", "LA"):
                            background.paste(frame, mask=frame.split()[-1])
                        else:
                            background.paste(frame)
                        frame = background
                    elif frame.mode != "RGB":
                        frame = frame.convert("RGB")

                    # Convert PIL image to QPixmap
                    buffer = io.BytesIO()
                    frame.save(buffer, format="PNG")
                    buffer.seek(0)

                    pixmap = QPixmap()
                    pixmap.loadFromData(buffer.getvalue())

                    if not pixmap.isNull():
                        label_size = self.label_exercise_avif.size()
                        scaled_pixmap = pixmap.scaled(label_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        self.label_exercise_avif.setPixmap(scaled_pixmap)
                        return

            except ImportError as import_error:
                print(f"Import error: {import_error}")
                self.label_exercise_avif.setText(f"AVIF plugin not available:\n{exercise_name}")
                return
            except Exception as pil_error:
                print(f"Pillow error: {pil_error}")

            self.label_exercise_avif.setText(f"Cannot load AVIF:\n{exercise_name}")

        except Exception as e:
            print(f"General error: {e}")
            self.label_exercise_avif.setText(f"Error loading AVIF:\n{exercise_name}\n{e}")
```

</details>

### Method `_next_avif_frame`

```python
def _next_avif_frame(self) -> None
```

Show next frame in AVIF animation.

<details>
<summary>Code:</summary>

```python
def _next_avif_frame(self) -> None:
        if not self.avif_frames:
            return

        self.current_frame_index = (self.current_frame_index + 1) % len(self.avif_frames)
        self.label_exercise_avif.setPixmap(self.avif_frames[self.current_frame_index])
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

Add a single row to `any` table.

Args:

- `table_name` (`str`): Target table (must be one of `self._SAFE_TABLES`).
- `query_text` (`str`): SQL `INSERT` statement with named placeholders.
- `params` (`dict`): Mapping for the placeholders.

Returns:

- `bool`: `True` if the row was written successfully.

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

Apply combo-box/date filters to the `process` table.

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

### Method `closeEvent`

```python
def closeEvent(self, event: QCloseEvent) -> None
```

Handle application close event.

<details>
<summary>Code:</summary>

```python
def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        # Stop animations
        if self.current_movie:
            self.current_movie.stop()
        if self.avif_timer:
            self.avif_timer.stop()

        event.accept()
```

</details>

### Method `delete_record`

```python
def delete_record(self, table_name: str) -> None
```

Delete selected row from `table_name` (must be safe).

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

        # Получаем значение чекбокса
        is_type_required = 1 if self.check_box_is_type_required.isChecked() else 0

        self.add_record_generic(
            "exercises",
            "INSERT INTO exercises (name, unit, is_type_required) VALUES (:name, :unit, :is_type_required)",
            {"name": exercise, "unit": unit, "is_type_required": is_type_required},
        )
```

</details>

### Method `on_add_record`

```python
def on_add_record(self) -> None
```

Insert a new `process` row.

Adds a new exercise record to the process table using the currently selected
exercise, type, count, and date values. Validates that exercise type is provided
when required. Automatically advances the date after successful addition.

<details>
<summary>Code:</summary>

```python
def on_add_record(self) -> None:
        exercise = self.comboBox_exercise.currentText()
        ex_id = self.db_manager.get_id("exercises", "name", exercise)
        if ex_id is None:
            return

        type_name = self.comboBox_type.currentText()

        # Check if exercise type is required
        is_type_required_query = "SELECT is_type_required FROM exercises WHERE _id = :ex_id"
        rows = self.db_manager.get_rows(is_type_required_query, {"ex_id": ex_id})

        if rows and rows[0][0] == 1 and not type_name.strip():
            QMessageBox.warning(self, "Error", f"Exercise type is required for '{exercise}'. Please select a type.")
            return

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

Insert a new exercise `type` for the selected exercise.

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

Load exercise types for the newly selected exercise in `comboBox_type`.

Updates the exercise type combo box with the types associated with the
currently selected exercise. Automatically selects the most recently used
type for this exercise from the process table. Also loads the exercise AVIF.

<details>
<summary>Code:</summary>

```python
def on_exercise_changed(self) -> None:
        exercise = self.comboBox_exercise.currentText()

        self._load_exercise_avif(exercise)

        ex_id = self.db_manager.get_id("exercises", "name", exercise)
        if ex_id is None:
            return

        # Get all types for this exercise
        types = self.db_manager.get_items(
            "types",
            "type",
            condition=f"_id_exercises = {ex_id}",
        )

        # Clear and populate the combobox
        self.comboBox_type.clear()
        self.comboBox_type.addItem("")
        self.comboBox_type.addItems(types)

        # Find the most recently used type for this exercise
        last_type_query = """
            SELECT t.type
            FROM process p
            LEFT JOIN types t ON p._id_types = t._id AND t._id_exercises = p._id_exercises
            WHERE p._id_exercises = :ex_id
            ORDER BY p._id DESC
            LIMIT 1
        """

        rows = self.db_manager.get_rows(last_type_query, {"ex_id": ex_id})

        if rows:
            last_type = rows[0][0] if rows[0][0] is not None else ""
            # Find and select this type in the combobox
            type_index = self.comboBox_type.findText(last_type)
            if type_index >= 0:
                self.comboBox_type.setCurrentIndex(type_index)
```

</details>

### Method `on_exercise_selection_changed`

```python
def on_exercise_selection_changed(self) -> None
```

Update form fields when exercise selection changes in the table.

Synchronizes the form fields (name, unit, is_type_required checkbox)
with the currently selected exercise in the table.

<details>
<summary>Code:</summary>

```python
def on_exercise_selection_changed(self) -> None:
        index = self.tableView_exercises.currentIndex()
        if not index.isValid():
            # Clear the fields if nothing is selected
            self.lineEdit_exercise_name.clear()
            self.lineEdit_exercise_unit.clear()
            self.check_box_is_type_required.setChecked(False)
            return

        model = self.models["exercises"]
        row = index.row()

        # Fill in the fields with data from the selected row
        name = model.data(model.index(row, 0)) or ""
        unit = model.data(model.index(row, 1)) or ""
        is_required = model.data(model.index(row, 2)) or "0"

        self.lineEdit_exercise_name.setText(name)
        self.lineEdit_exercise_unit.setText(unit)
        self.check_box_is_type_required.setChecked(is_required == "1")
```

</details>

### Method `on_export_csv`

```python
def on_export_csv(self) -> None
```

Save current `process` view to a CSV file (semicolon-separated).

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
        index_tab_weight = 5
        index_tab_charts = 4

        if index == 0:  # Main tab
            self.update_filter_comboboxes()
        elif index == index_tab_charts:  # Exercise Chart tab
            self.update_chart_comboboxes()
            self._load_default_exercise_chart()
        elif index == index_tab_weight:
            self.set_weight_all_time()
```

</details>

### Method `on_update_exercises`

```python
def on_update_exercises(self) -> None
```

Update the selected exercise row.

Updates the name, unit, and is_type_required of the currently selected exercise in the
exercises table.

<details>
<summary>Code:</summary>

```python
def on_update_exercises(self) -> None:
        self._update_record_generic(
            "exercises",
            "exercises",
            "UPDATE exercises SET name = :n, unit = :u, is_type_required = :itr WHERE _id = :id",
            lambda r, m, _id: {
                "n": m.data(m.index(r, 0)),
                "u": m.data(m.index(r, 1)),
                "itr": 1 if m.data(m.index(r, 2)) == "1" else 0,
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

Update the selected `types` row.

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

### Method `set_chart_all_time`

```python
def set_chart_all_time(self) -> None
```

Set chart date range to all available data.

<details>
<summary>Code:</summary>

```python
def set_chart_all_time(self) -> None:
        # Get the earliest process record
        rows = self.db_manager.get_rows("SELECT MIN(date) FROM process WHERE date IS NOT NULL")

        if rows and rows[0][0]:
            earliest_date = QDate.fromString(rows[0][0], "yyyy-MM-dd")
            self.dateEdit_chart_from.setDate(earliest_date)
        else:
            # Fallback to one year ago if no data
            current_date = QDate.currentDate()
            self.dateEdit_chart_from.setDate(current_date.addYears(-1))

        self.dateEdit_chart_to.setDate(QDate.currentDate())
        self.update_exercise_chart()
```

</details>

### Method `set_chart_last_month`

```python
def set_chart_last_month(self) -> None
```

Set chart date range to last month.

<details>
<summary>Code:</summary>

```python
def set_chart_last_month(self) -> None:
        current_date = QDate.currentDate()
        self.dateEdit_chart_from.setDate(current_date.addMonths(-1))
        self.dateEdit_chart_to.setDate(current_date)
        self.update_exercise_chart()
```

</details>

### Method `set_chart_last_year`

```python
def set_chart_last_year(self) -> None
```

Set chart date range to last year.

<details>
<summary>Code:</summary>

```python
def set_chart_last_year(self) -> None:
        current_date = QDate.currentDate()
        self.dateEdit_chart_from.setDate(current_date.addYears(-1))
        self.dateEdit_chart_to.setDate(current_date)
        self.update_exercise_chart()
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

### Method `set_weight_all_time`

```python
def set_weight_all_time(self) -> None
```

Set weight chart date range to all available data.

<details>
<summary>Code:</summary>

```python
def set_weight_all_time(self) -> None:
        # Get the earliest weight record
        rows = self.db_manager.get_rows("SELECT MIN(date) FROM weight WHERE date IS NOT NULL")

        if rows and rows[0][0]:
            earliest_date = QDate.fromString(rows[0][0], "yyyy-MM-dd")
            self.dateEdit_weight_from.setDate(earliest_date)
        else:
            # Fallback to one year ago if no data
            current_date = QDate.currentDate()
            self.dateEdit_weight_from.setDate(current_date.addYears(-1))

        self.dateEdit_weight_to.setDate(QDate.currentDate())
        self.update_weight_chart()
```

</details>

### Method `set_weight_last_month`

```python
def set_weight_last_month(self) -> None
```

Set weight chart date range to last month.

<details>
<summary>Code:</summary>

```python
def set_weight_last_month(self) -> None:
        current_date = QDate.currentDate()
        self.dateEdit_weight_from.setDate(current_date.addMonths(-1))
        self.dateEdit_weight_to.setDate(current_date)
        self.update_weight_chart()
```

</details>

### Method `set_weight_last_year`

```python
def set_weight_last_year(self) -> None
```

Set weight chart date range to last year.

<details>
<summary>Code:</summary>

```python
def set_weight_last_year(self) -> None:
        current_date = QDate.currentDate()
        self.dateEdit_weight_from.setDate(current_date.addYears(-1))
        self.dateEdit_weight_to.setDate(current_date)
        self.update_weight_chart()
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
        # exercises - adding new field
        rows = self.db_manager.get_rows("SELECT _id, name, unit, is_type_required FROM exercises")
        # Update column headers
        exercises_headers = ["Exercise", "Unit of Measurement", "Type Required"]
        self.models["exercises"] = self._create_table_model(
            rows,
            exercises_headers,
        )
        self.tableView_exercises.setModel(self.models["exercises"])
        self.tableView_exercises.resizeColumnsToContents()

        # Connect selection change signal AFTER setting the model
        selection_model = self.tableView_exercises.selectionModel()
        if selection_model:
            # Qt automatically avoids duplicate connections
            selection_model.currentRowChanged.connect(self.on_exercise_selection_changed)

        # Other tables remain unchanged...
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

        # Clear the exercise addition form after updating
        self.lineEdit_exercise_name.clear()
        self.lineEdit_exercise_unit.clear()
        self.check_box_is_type_required.setChecked(False)

        # Upload a AVIF for the currently selected exercise
        current_exercise_name = self.comboBox_exercise.currentText()
        self._load_exercise_avif(current_exercise_name)
```

</details>

### Method `update_chart_comboboxes`

```python
def update_chart_comboboxes(self) -> None
```

Update exercise and type comboboxes for charts.

<details>
<summary>Code:</summary>

```python
def update_chart_comboboxes(self) -> None:
        # Update exercise combobox
        exercises = self.db_manager.get_items("exercises", "name")

        self.comboBox_chart_exercise.blockSignals(True)  # noqa: FBT003
        self.comboBox_chart_exercise.clear()
        if exercises:
            self.comboBox_chart_exercise.addItems(exercises)
        self.comboBox_chart_exercise.blockSignals(False)  # noqa: FBT003

        # Update type combobox
        self.update_chart_type_combobox()
```

</details>

### Method `update_chart_type_combobox`

```python
def update_chart_type_combobox(self) -> None
```

Update chart type combobox based on selected exercise.

<details>
<summary>Code:</summary>

```python
def update_chart_type_combobox(self) -> None:
        self.comboBox_chart_type.clear()
        self.comboBox_chart_type.addItem("All types")

        exercise = self.comboBox_chart_exercise.currentText()
        if exercise:
            ex_id = self.db_manager.get_id("exercises", "name", exercise)
            if ex_id is not None:
                types = self.db_manager.get_items(
                    "types",
                    "type",
                    condition=f"_id_exercises = {ex_id}",
                )
                self.comboBox_chart_type.addItems(types)
```

</details>

### Method `update_exercise_chart`

```python
def update_exercise_chart(self) -> None
```

Update the exercise chart with current filters.

<details>
<summary>Code:</summary>

```python
def update_exercise_chart(self) -> None:
        exercise = self.comboBox_chart_exercise.currentText()
        exercise_type = self.comboBox_chart_type.currentText()
        period = self.comboBox_chart_period.currentText()
        date_from = self.dateEdit_chart_from.date().toString("yyyy-MM-dd")
        date_to = self.dateEdit_chart_to.date().toString("yyyy-MM-dd")

        # Clear existing chart
        layout = self.verticalLayout_charts_content
        for i in reversed(range(layout.count())):
            child = layout.takeAt(i).widget()
            if child:
                child.setParent(None)

        if not exercise:
            from PySide6.QtWidgets import QLabel

            no_data_label = QLabel("Please select an exercise")
            no_data_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(no_data_label)
            return

        # Build query based on filters
        conditions = ["e.name = :exercise", "p.date BETWEEN :date_from AND :date_to"]
        params = {"exercise": exercise, "date_from": date_from, "date_to": date_to}

        if exercise_type and exercise_type != "All types":
            conditions.append("t.type = :type")
            params["type"] = exercise_type

        query = f"""
            SELECT p.date, p.value
            FROM process p
            JOIN exercises e ON p._id_exercises = e._id
            LEFT JOIN types t ON p._id_types = t._id AND t._id_exercises = e._id
            WHERE {" AND ".join(conditions)}
            ORDER BY p.date ASC
        """

        rows = self.db_manager.get_rows(query, params)

        if not rows:
            from PySide6.QtWidgets import QLabel

            no_data_label = QLabel("No data found for the selected filters")
            no_data_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(no_data_label)
            return

        # Group data by period
        grouped_data = self._group_exercise_data_by_period(rows, period)

        if not grouped_data:
            from PySide6.QtWidgets import QLabel

            no_data_label = QLabel("No data to display")
            no_data_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(no_data_label)
            return

        # Create matplotlib figure
        fig = Figure(figsize=(12, 6), dpi=100)
        canvas = FigureCanvas(fig)

        # Create plot
        ax = fig.add_subplot(111)

        # Extract dates and values
        dates = list(grouped_data.keys())
        values = list(grouped_data.values())

        # Plot line without markers
        ax.plot(dates, values, "b-", linewidth=2, alpha=0.8)

        # Customize the plot
        ax.set_xlabel("Date", fontsize=12)
        ax.set_ylabel("Total Value", fontsize=12)

        chart_title = f"{exercise}"
        if exercise_type and exercise_type != "All types":
            chart_title += f" - {exercise_type}"
        chart_title += f" ({period})"

        ax.set_title(chart_title, fontsize=14, fontweight="bold")
        ax.grid(visible=True, alpha=0.3)

        # Format x-axis dates
        self._format_chart_x_axis(ax, dates, period)

        # Add statistics
        if len(values) > 1:
            min_value = min(values)
            max_value = max(values)
            avg_value = sum(values) / len(values)
            total_value = sum(values)

            stats_text = (
                f"Min: {min_value:.1f} | Max: {max_value:.1f} | Avg: {avg_value:.1f} | Total: {total_value:.1f}"
            )
            ax.text(
                0.5,
                0.02,
                stats_text,
                transform=ax.transAxes,
                ha="center",
                va="bottom",
                fontsize=10,
                bbox={"boxstyle": "round,pad=0.3", "facecolor": "lightgray", "alpha": 0.8},
            )

        # Adjust layout to prevent label cutoff
        fig.tight_layout()

        # Add canvas to layout
        layout.addWidget(canvas)

        # Force update
        canvas.draw()
```

</details>

### Method `update_filter_comboboxes`

```python
def update_filter_comboboxes(self) -> None
```

Refresh `exercise` and `type` combo-boxes in the filter group.

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

Populate `type` filter based on the `exercise` filter selection.

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

### Method `update_weight_chart`

```python
def update_weight_chart(self) -> None
```

Update the weight chart with current date range.

<details>
<summary>Code:</summary>

```python
def update_weight_chart(self) -> None:
        date_from = self.dateEdit_weight_from.date().toString("yyyy-MM-dd")
        date_to = self.dateEdit_weight_to.date().toString("yyyy-MM-dd")

        # Clear existing chart
        layout = self.verticalLayout_weight_chart_content
        for i in reversed(range(layout.count())):
            child = layout.takeAt(i).widget()
            if child:
                child.setParent(None)

        # Get weight data
        query = """
            SELECT value, date
            FROM weight
            WHERE date BETWEEN :date_from AND :date_to
            AND date IS NOT NULL
            ORDER BY date ASC
        """

        rows = self.db_manager.get_rows(query, {"date_from": date_from, "date_to": date_to})

        if not rows:
            from PySide6.QtWidgets import QLabel

            no_data_label = QLabel("No weight data found for the selected period")
            no_data_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(no_data_label)
            return

        # Create matplotlib figure
        fig = Figure(figsize=(12, 6), dpi=100)
        canvas = FigureCanvas(fig)

        # Parse data
        weights = [float(row[0]) for row in rows]
        dates = [datetime.strptime(row[1], "%Y-%m-%d").replace(tzinfo=timezone.utc) for row in rows]

        # Create plot
        ax = fig.add_subplot(111)

        # Plot line
        ax.plot(
            dates,
            weights,
            "b-",
            linewidth=2,
            alpha=0.8,
        )

        # Customize the plot
        ax.set_xlabel("Date", fontsize=12)
        ax.set_ylabel("Weight (kg)", fontsize=12)
        ax.set_title("Weight Progress", fontsize=14, fontweight="bold")
        ax.grid(visible=True, alpha=0.3)

        # Define constants at the top of your file or function
        days_in_month = 31
        days_in_year = 365

        # Format x-axis dates
        if len(dates) > 0:
            date_range = (max(dates) - min(dates)).days

            if date_range <= days_in_month:  # Less than a month
                ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(dates) // 10)))
                ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
            elif date_range <= days_in_year:  # Less than a year
                ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=max(1, len(dates) // 10)))
                ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
            else:  # More than a year
                ax.xaxis.set_major_locator(mdates.MonthLocator(interval=max(1, date_range // days_in_year)))
                ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))

        # Rotate date labels
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha="right")

        # Add statistics
        if len(weights) > 1:
            min_weight = min(weights)
            max_weight = max(weights)
            avg_weight = sum(weights) / len(weights)
            weight_change = weights[-1] - weights[0]

            stats_text = (
                f"Min: {min_weight:.1f} kg | Max: {max_weight:.1f} kg | "
                f"Avg: {avg_weight:.1f} kg | Change: {weight_change:+.1f} kg"
            )
            ax.text(
                0.5,
                0.02,
                stats_text,
                transform=ax.transAxes,
                ha="center",
                va="bottom",
                fontsize=10,
                bbox={"boxstyle": "round,pad=0.3", "facecolor": "lightgray", "alpha": 0.8},
            )

        # Adjust layout to prevent label cutoff
        fig.tight_layout()

        # Add canvas to layout
        layout.addWidget(canvas)

        # Force update
        canvas.draw()
```

</details>
