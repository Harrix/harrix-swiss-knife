---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `qt_mixins.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `AutoSaveMixin`](#️-class-autosavemixin)
- [🏛️ Class `DateMixin`](#️-class-datemixin)
- [🏛️ Class `TableOperations`](#️-class-tableoperations)
- [🏛️ Class `ValidationMixin`](#️-class-validationmixin)

</details>

## 🏛️ Class `AutoSaveMixin`

```python
class AutoSaveMixin
```

Mixin with shared auto-save infrastructure for tracker table views.

<details>
<summary>Code:</summary>

```python
class AutoSaveMixin:

    models: dict[str, Any]
    _SAFE_TABLES: set[str]
    _validate_database_connection: Callable[[], bool]
    _auto_save_handlers: dict[str, Callable[..., None]]
    _auto_save_source_models: dict[str, QStandardItemModel]

    def _after_table_data_changed(
        self,
        table_name: str,
        top_left: QModelIndex,
        bottom_right: QModelIndex,
    ) -> None:
        """Run after standard row auto-save completes."""

    def _auto_save_row(self, table_name: str, model: QStandardItemModel, row: int, row_id: str) -> None:
        """Dispatch auto-save for one table row via app-specific handlers."""
        if not self._validate_database_connection():
            return

        handler = self._get_save_handlers().get(table_name)
        if handler is None:
            return

        try:
            handler(model, row, row_id)
        except Exception as e:
            self._show_auto_save_error(f"Failed to save {table_name} row: {e!s}")

    def _connect_table_auto_save_signal(self, table_name: str) -> None:
        """Connect `dataChanged` for one table, avoiding duplicate handlers."""
        if table_name not in self._SAFE_TABLES:
            return

        proxy_model = self.models.get(table_name)
        if proxy_model is None or not hasattr(proxy_model, "sourceModel"):
            return

        source_model = proxy_model.sourceModel()
        if source_model is None:
            return

        if not hasattr(self, "_auto_save_handlers"):
            self._auto_save_handlers = {}
        if not hasattr(self, "_auto_save_source_models"):
            self._auto_save_source_models = {}

        old_handler = self._auto_save_handlers.get(table_name)
        old_source_model = self._auto_save_source_models.get(table_name)
        if old_handler is not None and old_source_model is not None:
            with contextlib.suppress(TypeError, RuntimeError):
                old_source_model.dataChanged.disconnect(old_handler)

        handler = partial(self._on_table_data_changed, table_name)
        self._auto_save_handlers[table_name] = handler
        self._auto_save_source_models[table_name] = source_model
        source_model.dataChanged.connect(handler)

    def _connect_table_auto_save_signals(self) -> None:
        """Connect auto-save handlers for every table in `_SAFE_TABLES`."""
        for table_name in self._SAFE_TABLES:
            self._connect_table_auto_save_signal(table_name)

    def _disconnect_table_auto_save_signals(self) -> None:
        """Disconnect all auto-save `dataChanged` handlers."""
        handlers = getattr(self, "_auto_save_handlers", None)
        source_models = getattr(self, "_auto_save_source_models", None)
        if not handlers or not source_models:
            return

        for table_name, handler in list(handlers.items()):
            source_model = source_models.get(table_name)
            if source_model is not None and handler is not None:
                with contextlib.suppress(TypeError, RuntimeError):
                    source_model.dataChanged.disconnect(handler)

        handlers.clear()
        source_models.clear()

    def _get_save_handlers(self) -> dict[str, Callable[..., None]]:
        """Return map of table name to save handler. Override in app mixins."""
        return {}

    def _handle_special_table_data_changed(
        self,
        table_name: str,
        top_left: QModelIndex,
        bottom_right: QModelIndex,
        model: QStandardItemModel,
        _roles: list | None = None,
    ) -> bool:
        """Return True when a non-row auto-save handler processed the change."""
        del table_name, top_left, bottom_right, model
        return False

    def _on_table_data_changed(
        self, table_name: str, top_left: QModelIndex, bottom_right: QModelIndex, _roles: list | None = None
    ) -> None:
        """Handle table model changes and auto-save affected rows."""
        if table_name not in self._SAFE_TABLES:
            return

        if not self._validate_database_connection():
            return

        try:
            proxy_model: QSortFilterProxyModel | None = self.models.get(table_name)
            if proxy_model is None:
                return
            source_model = proxy_model.sourceModel()
            if not isinstance(source_model, QStandardItemModel):
                return

            if self._handle_special_table_data_changed(table_name, top_left, bottom_right, source_model, _roles):
                return

            for row in range(top_left.row(), bottom_right.row() + 1):
                if row >= source_model.rowCount():
                    continue
                vertical_header_item = source_model.verticalHeaderItem(row)
                if vertical_header_item is None:
                    continue
                row_id = vertical_header_item.text()
                self._auto_save_row(table_name, source_model, row, row_id)

            self._after_table_data_changed(table_name, top_left, bottom_right)
        except Exception as e:
            self._show_auto_save_error(f"Failed to auto-save changes: {e!s}")

    def _show_auto_save_error(self, message: str) -> None:
        """Show auto-save error dialog. Override for app-specific error UI."""
        parent = self if isinstance(self, QWidget) else None
        message_box.warning(parent, "Auto-save Error", message)
```

</details>

## 🏛️ Class `DateMixin`

```python
class DateMixin
```

Mixin class for date widget helpers.

<details>
<summary>Code:</summary>

```python
class DateMixin:

    db_manager: Any
    _validate_database_connection: Callable[[], bool]

    def _get_earliest_date_for_chart_range(self, from_widget: QDateEdit) -> str | None:
        """Resolve earliest available date for an all-time chart range."""
        db = self.db_manager
        if hasattr(from_widget, "objectName") and "weight" in from_widget.objectName():
            getter = getattr(db, "get_earliest_weight_date", None)
            return getter() if callable(getter) else None

        for method_name in (
            "get_earliest_transaction_date",
            "get_earliest_process_habit_date",
            "get_earliest_process_date",
        ):
            getter = getattr(db, method_name, None)
            if callable(getter):
                earliest = getter()
                if earliest:
                    return earliest
        return None

    def _increment_date_widget(self, date_widget: QDateEdit) -> None:
        """Increment date widget by one day if not already today.

        Args:

        - `date_widget` (`QDateEdit`): QDateEdit widget to increment.

        """
        current_date = date_widget.date()
        today = QDate.currentDate()

        if current_date >= today:
            return

        next_date = current_date.addDays(1)
        date_widget.setDate(next_date)

    def _set_date_range(
        self,
        from_widget: QDateEdit,
        to_widget: QDateEdit,
        months: int = 0,
        years: int = 0,
        *,
        is_all_time: bool = False,
    ) -> None:
        """Set date range for date widgets."""
        current_date = QDate.currentDate()
        to_widget.setDate(current_date)

        if is_all_time and self._validate_database_connection():
            earliest = self._get_earliest_date_for_chart_range(from_widget)
            if earliest:
                from_widget.setDate(QDate.fromString(earliest, "yyyy-MM-dd"))
            else:
                fallback_years = 2 if hasattr(self.db_manager, "get_earliest_transaction_date") else 1
                from_widget.setDate(current_date.addYears(-fallback_years))
        elif years:
            from_widget.setDate(current_date.addYears(-years))
        elif months:
            from_widget.setDate(current_date.addMonths(-months))
```

</details>

## 🏛️ Class `TableOperations`

```python
class TableOperations
```

Mixin class for common table operations.

Expected attributes from main class:

- `table_config` (`dict`): Dictionary with table configuration.
- `models` (`dict`): Dictionary with table models.
- `_create_table_model`: Method to create table model.

<details>
<summary>Code:</summary>

```python
class TableOperations:

    table_config: dict[str, tuple[Any, str, list[str]]]
    models: dict[str, Any]
    _create_table_model: Callable[[list, list[str]], Any]

    def _connect_table_signals(self, table_name: str, selection_handler: Callable) -> None:
        """Connect selection change signal for a table.

        Args:

        - `table_name` (`str`): Name of the table.
        - `selection_handler` (`Callable`): Handler function for selection changes.

        """
        view = self.table_config[table_name][0]
        selection_model = view.selectionModel()
        if selection_model:
            selection_model.currentRowChanged.connect(selection_handler)

    def _create_colored_table_model(
        self,
        data: list[list],
        headers: list[str],
        id_column: int = -2,
        *,
        color_column: int = -1,
    ) -> QSortFilterProxyModel:
        """Return a proxy model filled with colored table data."""
        return create_colored_table_proxy_model(
            data,
            headers,
            id_column=id_column,
            color_column=color_column,
        )

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

            source_index = model.mapToSource(index)
            if not source_index.isValid():
                return None

            vertical_header_item = source_model.verticalHeaderItem(source_index.row())
            return int(vertical_header_item.text()) if vertical_header_item else None

        except (KeyError, ValueError, TypeError, AttributeError):
            return None

    def _get_selected_row_ids(self, table_name: str) -> list[int]:
        """Get database IDs for every distinct selected row (proxy-aware).

        Args:

        - `table_name` (`str`): Name of the table.

        Returns:

        - `list[int]`: IDs from vertical headers in selection order (first occurrence per row).

        """
        ids: list[int] = []
        try:
            table_view, model_key, _ = self.table_config[table_name]
            proxy_model = self.models[model_key]

            if proxy_model is None:
                return ids

            selection_model = table_view.selectionModel()
            if selection_model is None:
                return ids

            source_model = proxy_model.sourceModel()
            if not isinstance(source_model, QStandardItemModel):
                return ids

            seen_source_rows: set[int] = set()
            for proxy_index in selection_model.selectedIndexes():
                source_index = proxy_model.mapToSource(proxy_index)
                if not source_index.isValid():
                    continue
                row = source_index.row()
                if row in seen_source_rows:
                    continue
                seen_source_rows.add(row)
                vertical_header_item = source_model.verticalHeaderItem(row)
                if vertical_header_item:
                    ids.append(int(vertical_header_item.text()))
        except (KeyError, ValueError, TypeError, AttributeError):
            return []
        return ids

    def _refresh_table(
        self, table_name: str, data_getter: Callable, data_transformer: Callable[[list], list] | None = None
    ) -> None:
        """Refresh a table with data.

        Args:

        - `table_name` (`str`): Name of the table to refresh.
        - `data_getter` (`Callable`): Function to get data from database.
        - `data_transformer` (`Callable[[list], list] | None`): Optional function to transform raw data.
        Defaults to `None`.

        Raises:

        - `ValueError`: If the table name is unknown.

        """
        if table_name not in self.table_config:
            error_msg = f"❌ Unknown table: {table_name}"
            raise ValueError(error_msg)

        rows = data_getter()
        if data_transformer:
            rows = data_transformer(rows)

        view, model_key, headers = self.table_config[table_name]
        self.models[model_key] = self._create_table_model(rows, headers)
        view.setModel(self.models[model_key])
        view.resizeColumnsToContents()
```

</details>

## 🏛️ Class `ValidationMixin`

```python
class ValidationMixin
```

Mixin class for validation helpers.

<details>
<summary>Code:</summary>

```python
class ValidationMixin:

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
            datetime.fromisoformat(date_str).replace(tzinfo=UTC)
        except (ValueError, TypeError):
            return False
        else:
            return True
```

</details>
