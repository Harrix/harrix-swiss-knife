---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `mixins.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `AutoSaveOperations`](#%EF%B8%8F-class-autosaveoperations)
  - [⚙️ Method `_get_save_handlers`](#%EF%B8%8F-method-_get_save_handlers)
  - [⚙️ Method `_save_habit_data`](#%EF%B8%8F-method-_save_habit_data)
  - [⚙️ Method `_save_process_habits_data`](#%EF%B8%8F-method-_save_process_habits_data)
- [🏛️ Class `ChartOperations`](#%EF%B8%8F-class-chartoperations)
- [🏛️ Class `DateOperations`](#%EF%B8%8F-class-dateoperations)
- [🏛️ Class `ValidationOperations`](#%EF%B8%8F-class-validationoperations)

</details>

## 🏛️ Class `AutoSaveOperations`

```python
class AutoSaveOperations(AutoSaveMixin)
```

Mixin class for auto-save operations.

<details>
<summary>Code:</summary>

```python
class AutoSaveOperations(AutoSaveMixin):

    db_manager: Any
    _validate_database_connection: Callable[[], bool]
    update_habits_filter_combobox: Callable[[], None]
    _is_valid_date: Callable[[str], bool]

    def _get_save_handlers(self) -> dict[str, Callable[..., None]]:
        return {"habits": self._save_habit_data}

    def _save_habit_data(self, model: QStandardItemModel, row: int, row_id: str) -> None:
        """Save habit data.

        Args:

        - `model` (`QStandardItemModel`): The model containing the data.
        - `row` (`int`): Row index.
        - `row_id` (`str`): Database ID of the row.

        """
        name = model.data(model.index(row, 0)) or ""
        is_bool_str = model.data(model.index(row, 1)) or ""
        is_archived_str = model.data(model.index(row, 2)) or ""

        # Validate habit name
        if not name.strip():
            message_box.warning(None, "Validation Error", "Habit name cannot be empty")
            return

        # Convert is_bool_str to boolean or None
        # "Yes" -> True, "No" -> False, "" -> None
        is_bool = None
        if is_bool_str == "Yes":
            is_bool = True
        elif is_bool_str == "No":
            is_bool = False
        # else: is_bool remains None

        # Convert is_archived_str to boolean (default False)
        is_archived = is_archived_str == "Yes"

        # Update database
        if not self.db_manager.update_habit(int(row_id), name.strip(), is_bool=is_bool, is_archived=is_archived):
            message_box.warning(None, "Database Error", "Failed to save habit record")

    def _save_process_habits_data(
        self,
        model: QStandardItemModel,
        row: int,
        col: int,
        record_id: int | None,
        habit_id: int,
        date_str: str,
        value_str: str,
    ) -> None:
        """Save process habits cell data.

        Args:

        - `model` (`QStandardItemModel`): The model containing the data.
        - `row` (`int`): Row index (date row).
        - `col` (`int`): Column index (habit column).
        - `record_id` (`int | None`): Existing record ID or None if new record.
        - `habit_id` (`int`): Habit ID.
        - `date_str` (`str`): Date string.
        - `value_str` (`str`): Value as string.

        """
        if not self._validate_database_connection():
            return

        # Get the item to update its UserRole after save
        item = model.item(row, col)
        if item is None:
            return

        # Parse value
        try:
            if not value_str or value_str.strip() == "":
                # Empty value - delete record if exists
                if record_id is not None:
                    self.db_manager.delete_process_habit_record(record_id)
                    # Clear stored data
                    item.setData((None, habit_id, date_str), Qt.ItemDataRole.UserRole)
                return

            value = int(value_str.strip())
        except (ValueError, TypeError):
            message_box.warning(
                None,
                "Validation Error",
                f"Invalid value: {value_str}. Must be an integer.",
            )
            return

        # Validate date format
        if not self._is_valid_date(date_str):
            message_box.warning(None, "Validation Error", "Use YYYY-MM-DD date format")
            return

        # Update or insert record
        if record_id is not None:
            # Update existing record
            if not self.db_manager.update_process_habit_record(record_id, habit_id, value, date_str):
                message_box.warning(
                    None,
                    "Database Error",
                    "Failed to update process habit record",
                )
        else:
            # Create new record - need to get the new record_id
            # First, check if record already exists for this habit and date
            existing_records = self.db_manager.get_rows(
                "SELECT _id FROM process_habits WHERE _id_habit = :habit_id AND date = :date",
                {"habit_id": habit_id, "date": date_str},
            )
            if existing_records and len(existing_records) > 0:
                # Update existing record instead
                existing_record_id = existing_records[0][0]
                if not self.db_manager.update_process_habit_record(existing_record_id, habit_id, value, date_str):
                    message_box.warning(
                        None,
                        "Database Error",
                        "Failed to update process habit record",
                    )
                else:
                    # Update stored record_id in the item
                    item.setData(
                        (existing_record_id, habit_id, date_str),
                        Qt.ItemDataRole.UserRole,
                    )
            # Create new record
            elif self.db_manager.add_process_habit_record(habit_id, value, date_str):
                # Get the new record_id
                new_records = self.db_manager.get_rows(
                    "SELECT _id FROM process_habits "
                    "WHERE _id_habit = :habit_id AND date = :date "
                    "ORDER BY _id DESC LIMIT 1",
                    {"habit_id": habit_id, "date": date_str},
                )
                if new_records and len(new_records) > 0:
                    new_record_id = new_records[0][0]
                    # Update stored record_id in the item
                    item.setData(
                        (new_record_id, habit_id, date_str),
                        Qt.ItemDataRole.UserRole,
                    )
            else:
                message_box.warning(
                    None,
                    "Database Error",
                    "Failed to add process habit record",
                )
```

</details>

### ⚙️ Method `_get_save_handlers`

```python
def _get_save_handlers(self) -> dict[str, Callable[..., None]]
```

*No docstring provided.*

<details>
<summary>Code:</summary>

```python
def _get_save_handlers(self) -> dict[str, Callable[..., None]]:
        return {"habits": self._save_habit_data}
```

</details>

### ⚙️ Method `_save_habit_data`

```python
def _save_habit_data(self, model: QStandardItemModel, row: int, row_id: str) -> None
```

Save habit data.

Args:

- `model` (`QStandardItemModel`): The model containing the data.
- `row` (`int`): Row index.
- `row_id` (`str`): Database ID of the row.

<details>
<summary>Code:</summary>

```python
def _save_habit_data(self, model: QStandardItemModel, row: int, row_id: str) -> None:
        name = model.data(model.index(row, 0)) or ""
        is_bool_str = model.data(model.index(row, 1)) or ""
        is_archived_str = model.data(model.index(row, 2)) or ""

        # Validate habit name
        if not name.strip():
            message_box.warning(None, "Validation Error", "Habit name cannot be empty")
            return

        # Convert is_bool_str to boolean or None
        # "Yes" -> True, "No" -> False, "" -> None
        is_bool = None
        if is_bool_str == "Yes":
            is_bool = True
        elif is_bool_str == "No":
            is_bool = False
        # else: is_bool remains None

        # Convert is_archived_str to boolean (default False)
        is_archived = is_archived_str == "Yes"

        # Update database
        if not self.db_manager.update_habit(int(row_id), name.strip(), is_bool=is_bool, is_archived=is_archived):
            message_box.warning(None, "Database Error", "Failed to save habit record")
```

</details>

### ⚙️ Method `_save_process_habits_data`

```python
def _save_process_habits_data(self, model: QStandardItemModel, row: int, col: int, record_id: int | None, habit_id: int, date_str: str, value_str: str) -> None
```

Save process habits cell data.

Args:

- `model` (`QStandardItemModel`): The model containing the data.
- `row` (`int`): Row index (date row).
- `col` (`int`): Column index (habit column).
- `record_id` (`int | None`): Existing record ID or None if new record.
- `habit_id` (`int`): Habit ID.
- `date_str` (`str`): Date string.
- `value_str` (`str`): Value as string.

<details>
<summary>Code:</summary>

```python
def _save_process_habits_data(
        self,
        model: QStandardItemModel,
        row: int,
        col: int,
        record_id: int | None,
        habit_id: int,
        date_str: str,
        value_str: str,
    ) -> None:
        if not self._validate_database_connection():
            return

        # Get the item to update its UserRole after save
        item = model.item(row, col)
        if item is None:
            return

        # Parse value
        try:
            if not value_str or value_str.strip() == "":
                # Empty value - delete record if exists
                if record_id is not None:
                    self.db_manager.delete_process_habit_record(record_id)
                    # Clear stored data
                    item.setData((None, habit_id, date_str), Qt.ItemDataRole.UserRole)
                return

            value = int(value_str.strip())
        except (ValueError, TypeError):
            message_box.warning(
                None,
                "Validation Error",
                f"Invalid value: {value_str}. Must be an integer.",
            )
            return

        # Validate date format
        if not self._is_valid_date(date_str):
            message_box.warning(None, "Validation Error", "Use YYYY-MM-DD date format")
            return

        # Update or insert record
        if record_id is not None:
            # Update existing record
            if not self.db_manager.update_process_habit_record(record_id, habit_id, value, date_str):
                message_box.warning(
                    None,
                    "Database Error",
                    "Failed to update process habit record",
                )
        else:
            # Create new record - need to get the new record_id
            # First, check if record already exists for this habit and date
            existing_records = self.db_manager.get_rows(
                "SELECT _id FROM process_habits WHERE _id_habit = :habit_id AND date = :date",
                {"habit_id": habit_id, "date": date_str},
            )
            if existing_records and len(existing_records) > 0:
                # Update existing record instead
                existing_record_id = existing_records[0][0]
                if not self.db_manager.update_process_habit_record(existing_record_id, habit_id, value, date_str):
                    message_box.warning(
                        None,
                        "Database Error",
                        "Failed to update process habit record",
                    )
                else:
                    # Update stored record_id in the item
                    item.setData(
                        (existing_record_id, habit_id, date_str),
                        Qt.ItemDataRole.UserRole,
                    )
            # Create new record
            elif self.db_manager.add_process_habit_record(habit_id, value, date_str):
                # Get the new record_id
                new_records = self.db_manager.get_rows(
                    "SELECT _id FROM process_habits "
                    "WHERE _id_habit = :habit_id AND date = :date "
                    "ORDER BY _id DESC LIMIT 1",
                    {"habit_id": habit_id, "date": date_str},
                )
                if new_records and len(new_records) > 0:
                    new_record_id = new_records[0][0]
                    # Update stored record_id in the item
                    item.setData(
                        (new_record_id, habit_id, date_str),
                        Qt.ItemDataRole.UserRole,
                    )
            else:
                message_box.warning(
                    None,
                    "Database Error",
                    "Failed to add process habit record",
                )
```

</details>

## 🏛️ Class `ChartOperations`

```python
class ChartOperations(ChartOperationsBase)
```

Mixin class for chart operations.

<details>
<summary>Code:</summary>

```python
class ChartOperations(ChartOperationsBase):
```

</details>

## 🏛️ Class `DateOperations`

```python
class DateOperations(DateMixin)
```

Mixin class for date operations.

<details>
<summary>Code:</summary>

```python
class DateOperations(DateMixin):

    db_manager: Any
    _validate_database_connection: Callable[[], bool]
```

</details>

## 🏛️ Class `ValidationOperations`

```python
class ValidationOperations(ValidationMixin)
```

Mixin class for validation operations.

<details>
<summary>Code:</summary>

```python
class ValidationOperations(ValidationMixin):
```

</details>
