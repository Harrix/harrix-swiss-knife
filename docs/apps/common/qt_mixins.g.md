---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `qt_mixins.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `DateMixin`](#%EF%B8%8F-class-datemixin)
  - [⚙️ Method `_increment_date_widget`](#%EF%B8%8F-method-_increment_date_widget)
- [🏛️ Class `TableOperations`](#%EF%B8%8F-class-tableoperations)
  - [⚙️ Method `_connect_table_signals`](#%EF%B8%8F-method-_connect_table_signals)
  - [⚙️ Method `_get_selected_row_id`](#%EF%B8%8F-method-_get_selected_row_id)
  - [⚙️ Method `_refresh_table`](#%EF%B8%8F-method-_refresh_table)
- [🏛️ Class `ValidationMixin`](#%EF%B8%8F-class-validationmixin)
  - [⚙️ Method `_is_valid_date`](#%EF%B8%8F-method-_is_valid_date)

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
```

</details>

### ⚙️ Method `_increment_date_widget`

```python
def _increment_date_widget(self, date_widget: QDateEdit) -> None
```

Increment date widget by one day if not already today.

Args:

- `date_widget` (`QDateEdit`): QDateEdit widget to increment.

<details>
<summary>Code:</summary>

```python
def _increment_date_widget(self, date_widget: QDateEdit) -> None:
        current_date = date_widget.date()
        today = QDate.currentDate()

        if current_date >= today:
            return

        next_date = current_date.addDays(1)
        date_widget.setDate(next_date)
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

### ⚙️ Method `_connect_table_signals`

```python
def _connect_table_signals(self, table_name: str, selection_handler: Callable) -> None
```

Connect selection change signal for a table.

Args:

- `table_name` (`str`): Name of the table.
- `selection_handler` (`Callable`): Handler function for selection changes.

<details>
<summary>Code:</summary>

```python
def _connect_table_signals(self, table_name: str, selection_handler: Callable) -> None:
        view = self.table_config[table_name][0]
        selection_model = view.selectionModel()
        if selection_model:
            selection_model.currentRowChanged.connect(selection_handler)
```

</details>

### ⚙️ Method `_get_selected_row_id`

```python
def _get_selected_row_id(self, table_name: str) -> int | None
```

Get the database ID of the currently selected row.

Args:

- `table_name` (`str`): Name of the table.

Returns:

- `int | None`: Database ID of selected row or None if no selection.

<details>
<summary>Code:</summary>

```python
def _get_selected_row_id(self, table_name: str) -> int | None:
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
```

</details>

### ⚙️ Method `_refresh_table`

```python
def _refresh_table(self, table_name: str, data_getter: Callable, data_transformer: Callable[[list], list] | None = None) -> None
```

Refresh a table with data.

Args:

- `table_name` (`str`): Name of the table to refresh.
- `data_getter` (`Callable`): Function to get data from database.
- `data_transformer` (`Callable[[list], list] | None`): Optional function to transform raw data.
  Defaults to `None`.

Raises:

- `ValueError`: If the table name is unknown.

<details>
<summary>Code:</summary>

```python
def _refresh_table(
        self, table_name: str, data_getter: Callable, data_transformer: Callable[[list], list] | None = None
    ) -> None:
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

### ⚙️ Method `_is_valid_date`

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
            datetime.fromisoformat(date_str).replace(tzinfo=UTC)
        except (ValueError, TypeError):
            return False
        else:
            return True
```

</details>
