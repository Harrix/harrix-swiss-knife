---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `mixins.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `AutoSaveOperations`](#️-class-autosaveoperations)
  - [⚙️ Method `_get_save_handlers`](#️-method-_get_save_handlers)
  - [⚙️ Method `_save_exercise_data`](#️-method-_save_exercise_data)
  - [⚙️ Method `_save_process_data`](#️-method-_save_process_data)
  - [⚙️ Method `_save_type_data`](#️-method-_save_type_data)
  - [⚙️ Method `_save_weight_data`](#️-method-_save_weight_data)
- [🏛️ Class `ChartOperations`](#️-class-chartoperations)
- [🏛️ Class `DateOperations`](#️-class-dateoperations)
- [🏛️ Class `ValidationOperations`](#️-class-validationoperations)

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
    _update_comboboxes: Callable[..., None]
    update_filter_comboboxes: Callable[[], None]
    _is_valid_date: Callable[[str], bool]

    def _get_save_handlers(self) -> dict[str, Callable[..., None]]:
        return {
            "process": self._save_process_data,
            "exercises": self._save_exercise_data,
            "types": self._save_type_data,
            "weight": self._save_weight_data,
        }

    def _save_exercise_data(self, model: QStandardItemModel, row: int, row_id: str) -> None:
        """Save exercise data.

        Args:

        - `model` (`QStandardItemModel`): The model containing the data.
        - `row` (`int`): Row index.
        - `row_id` (`str`): Database ID of the row.

        """
        name = model.data(model.index(row, 0)) or ""
        unit = model.data(model.index(row, 1)) or ""
        is_type_required_str = model.data(model.index(row, 2)) or "0"
        calories_per_unit_str = model.data(model.index(row, 3)) or "0"

        # Validate exercise name
        if not name.strip():
            message_box.warning(None, "Validation Error", "Exercise name cannot be empty")
            return

        # Convert is_type_required to boolean
        is_type_required = is_type_required_str == "1"

        # Convert calories_per_unit to float
        try:
            calories_per_unit = float(calories_per_unit_str)
        except (ValueError, TypeError):
            message_box.warning(None, "Validation Error", f"Invalid calories per unit value: {calories_per_unit_str}")
            return

        # Update database
        if not self.db_manager.update_exercise(
            int(row_id),
            name.strip(),
            unit.strip(),
            is_type_required=is_type_required,
            calories_per_unit=calories_per_unit,
        ):
            message_box.warning(None, "Database Error", "Failed to save exercise record")
        else:
            # Update related UI elements
            self._update_comboboxes()
            self.update_filter_comboboxes()

    def _save_process_data(self, model: QStandardItemModel, row: int, row_id: str) -> None:
        """Save process record data.

        Args:

        - `model` (`QStandardItemModel`): The model containing the data.
        - `row` (`int`): Row index.
        - `row_id` (`str`): Database ID of the row.

        """
        exercise = model.data(model.index(row, 0))
        type_name = model.data(model.index(row, 1))
        value_raw = model.data(model.index(row, 2))
        date = model.data(model.index(row, 3))

        # Extract value from "value unit" format
        value = value_raw.split(" ")[0] if value_raw else ""

        # Validate date format
        if not self._is_valid_date(date):
            message_box.warning(None, "Validation Error", "Use YYYY-MM-DD date format")
            return

        # Get exercise ID
        ex_id = self.db_manager.get_id("exercises", "name", exercise)
        if ex_id is None:
            message_box.warning(None, "Validation Error", f"Exercise '{exercise}' not found")
            return

        # Get type ID (can be -1 for no type)
        tp_id = (
            self.db_manager.get_id("types", "type", type_name, condition=f"_id_exercises = {ex_id}")
            if type_name
            else -1
        )

        # Validate numeric value
        try:
            float(value)
        except (ValueError, TypeError):
            message_box.warning(None, "Validation Error", f"Invalid numeric value: {value}")
            return

        # Update database
        if not self.db_manager.update_process_record(int(row_id), ex_id, tp_id or -1, value, date):
            message_box.warning(None, "Database Error", "Failed to save process record")

    def _save_type_data(self, model: QStandardItemModel, row: int, row_id: str) -> None:
        """Save exercise type data.

        Args:

        - `model` (`QStandardItemModel`): The model containing the data.
        - `row` (`int`): Row index.
        - `row_id` (`str`): Database ID of the row.

        """
        exercise_name = model.data(model.index(row, 0)) or ""
        type_name = model.data(model.index(row, 1)) or ""
        calories_modifier_str = model.data(model.index(row, 2)) or "1.0"

        # Validate inputs
        if not exercise_name.strip():
            message_box.warning(None, "Validation Error", "Exercise name cannot be empty")
            return

        if not type_name.strip():
            message_box.warning(None, "Validation Error", "Type name cannot be empty")
            return

        # Convert calories_modifier to float
        try:
            calories_modifier = float(calories_modifier_str)
        except (ValueError, TypeError):
            message_box.warning(None, "Validation Error", f"Invalid calories modifier value: {calories_modifier_str}")
            return

        # Get exercise ID
        ex_id = self.db_manager.get_id("exercises", "name", exercise_name)
        if ex_id is None:
            message_box.warning(None, "Validation Error", f"Exercise '{exercise_name}' not found")
            return

        # Update database
        if not self.db_manager.update_exercise_type(int(row_id), ex_id, type_name.strip(), calories_modifier):
            message_box.warning(None, "Database Error", "Failed to save type record")
        else:
            # Update related UI elements
            self._update_comboboxes()
            self.update_filter_comboboxes()

    def _save_weight_data(self, model: QStandardItemModel, row: int, row_id: str) -> None:
        """Save weight data.

        Args:

        - `model` (`QStandardItemModel`): The model containing the data.
        - `row` (`int`): Row index.
        - `row_id` (`str`): Database ID of the row.

        """
        weight_str = model.data(model.index(row, 0)) or ""
        date = model.data(model.index(row, 1)) or ""

        # Validate weight value
        try:
            weight_value = float(weight_str)
            if weight_value <= 0:
                message_box.warning(None, "Validation Error", "Weight must be a positive number")
                return
        except (ValueError, TypeError):
            message_box.warning(None, "Validation Error", f"Invalid weight value: {weight_str}")
            return

        # Validate date format
        if not self._is_valid_date(date):
            message_box.warning(None, "Validation Error", "Use YYYY-MM-DD date format")
            return

        # Update database
        if not self.db_manager.update_weight_record(int(row_id), weight_value, date):
            message_box.warning(None, "Database Error", "Failed to save weight record")
```

</details>

### ⚙️ Method `_get_save_handlers`

```python
def _get_save_handlers(self) -> dict[str, Callable[..., None]]
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _get_save_handlers(self) -> dict[str, Callable[..., None]]:
        return {
            "process": self._save_process_data,
            "exercises": self._save_exercise_data,
            "types": self._save_type_data,
            "weight": self._save_weight_data,
        }
```

</details>

### ⚙️ Method `_save_exercise_data`

```python
def _save_exercise_data(self, model: QStandardItemModel, row: int, row_id: str) -> None
```

Save exercise data.

Args:

- `model` (`QStandardItemModel`): The model containing the data.
- `row` (`int`): Row index.
- `row_id` (`str`): Database ID of the row.

<details>
<summary>Code:</summary>

```python
def _save_exercise_data(self, model: QStandardItemModel, row: int, row_id: str) -> None:
        name = model.data(model.index(row, 0)) or ""
        unit = model.data(model.index(row, 1)) or ""
        is_type_required_str = model.data(model.index(row, 2)) or "0"
        calories_per_unit_str = model.data(model.index(row, 3)) or "0"

        # Validate exercise name
        if not name.strip():
            message_box.warning(None, "Validation Error", "Exercise name cannot be empty")
            return

        # Convert is_type_required to boolean
        is_type_required = is_type_required_str == "1"

        # Convert calories_per_unit to float
        try:
            calories_per_unit = float(calories_per_unit_str)
        except (ValueError, TypeError):
            message_box.warning(None, "Validation Error", f"Invalid calories per unit value: {calories_per_unit_str}")
            return

        # Update database
        if not self.db_manager.update_exercise(
            int(row_id),
            name.strip(),
            unit.strip(),
            is_type_required=is_type_required,
            calories_per_unit=calories_per_unit,
        ):
            message_box.warning(None, "Database Error", "Failed to save exercise record")
        else:
            # Update related UI elements
            self._update_comboboxes()
            self.update_filter_comboboxes()
```

</details>

### ⚙️ Method `_save_process_data`

```python
def _save_process_data(self, model: QStandardItemModel, row: int, row_id: str) -> None
```

Save process record data.

Args:

- `model` (`QStandardItemModel`): The model containing the data.
- `row` (`int`): Row index.
- `row_id` (`str`): Database ID of the row.

<details>
<summary>Code:</summary>

```python
def _save_process_data(self, model: QStandardItemModel, row: int, row_id: str) -> None:
        exercise = model.data(model.index(row, 0))
        type_name = model.data(model.index(row, 1))
        value_raw = model.data(model.index(row, 2))
        date = model.data(model.index(row, 3))

        # Extract value from "value unit" format
        value = value_raw.split(" ")[0] if value_raw else ""

        # Validate date format
        if not self._is_valid_date(date):
            message_box.warning(None, "Validation Error", "Use YYYY-MM-DD date format")
            return

        # Get exercise ID
        ex_id = self.db_manager.get_id("exercises", "name", exercise)
        if ex_id is None:
            message_box.warning(None, "Validation Error", f"Exercise '{exercise}' not found")
            return

        # Get type ID (can be -1 for no type)
        tp_id = (
            self.db_manager.get_id("types", "type", type_name, condition=f"_id_exercises = {ex_id}")
            if type_name
            else -1
        )

        # Validate numeric value
        try:
            float(value)
        except (ValueError, TypeError):
            message_box.warning(None, "Validation Error", f"Invalid numeric value: {value}")
            return

        # Update database
        if not self.db_manager.update_process_record(int(row_id), ex_id, tp_id or -1, value, date):
            message_box.warning(None, "Database Error", "Failed to save process record")
```

</details>

### ⚙️ Method `_save_type_data`

```python
def _save_type_data(self, model: QStandardItemModel, row: int, row_id: str) -> None
```

Save exercise type data.

Args:

- `model` (`QStandardItemModel`): The model containing the data.
- `row` (`int`): Row index.
- `row_id` (`str`): Database ID of the row.

<details>
<summary>Code:</summary>

```python
def _save_type_data(self, model: QStandardItemModel, row: int, row_id: str) -> None:
        exercise_name = model.data(model.index(row, 0)) or ""
        type_name = model.data(model.index(row, 1)) or ""
        calories_modifier_str = model.data(model.index(row, 2)) or "1.0"

        # Validate inputs
        if not exercise_name.strip():
            message_box.warning(None, "Validation Error", "Exercise name cannot be empty")
            return

        if not type_name.strip():
            message_box.warning(None, "Validation Error", "Type name cannot be empty")
            return

        # Convert calories_modifier to float
        try:
            calories_modifier = float(calories_modifier_str)
        except (ValueError, TypeError):
            message_box.warning(None, "Validation Error", f"Invalid calories modifier value: {calories_modifier_str}")
            return

        # Get exercise ID
        ex_id = self.db_manager.get_id("exercises", "name", exercise_name)
        if ex_id is None:
            message_box.warning(None, "Validation Error", f"Exercise '{exercise_name}' not found")
            return

        # Update database
        if not self.db_manager.update_exercise_type(int(row_id), ex_id, type_name.strip(), calories_modifier):
            message_box.warning(None, "Database Error", "Failed to save type record")
        else:
            # Update related UI elements
            self._update_comboboxes()
            self.update_filter_comboboxes()
```

</details>

### ⚙️ Method `_save_weight_data`

```python
def _save_weight_data(self, model: QStandardItemModel, row: int, row_id: str) -> None
```

Save weight data.

Args:

- `model` (`QStandardItemModel`): The model containing the data.
- `row` (`int`): Row index.
- `row_id` (`str`): Database ID of the row.

<details>
<summary>Code:</summary>

```python
def _save_weight_data(self, model: QStandardItemModel, row: int, row_id: str) -> None:
        weight_str = model.data(model.index(row, 0)) or ""
        date = model.data(model.index(row, 1)) or ""

        # Validate weight value
        try:
            weight_value = float(weight_str)
            if weight_value <= 0:
                message_box.warning(None, "Validation Error", "Weight must be a positive number")
                return
        except (ValueError, TypeError):
            message_box.warning(None, "Validation Error", f"Invalid weight value: {weight_str}")
            return

        # Validate date format
        if not self._is_valid_date(date):
            message_box.warning(None, "Validation Error", "Use YYYY-MM-DD date format")
            return

        # Update database
        if not self.db_manager.update_weight_record(int(row_id), weight_value, date):
            message_box.warning(None, "Database Error", "Failed to save weight record")
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
