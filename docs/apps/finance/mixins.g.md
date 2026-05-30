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
  - [⚙️ Method `_auto_save_row`](#%EF%B8%8F-method-_auto_save_row)
  - [⚙️ Method `_get_save_handlers`](#%EF%B8%8F-method-_get_save_handlers)
  - [⚙️ Method `_save_account_data`](#%EF%B8%8F-method-_save_account_data)
  - [⚙️ Method `_save_category_data`](#%EF%B8%8F-method-_save_category_data)
  - [⚙️ Method `_save_currency_data`](#%EF%B8%8F-method-_save_currency_data)
  - [⚙️ Method `_save_exchange_data`](#%EF%B8%8F-method-_save_exchange_data)
  - [⚙️ Method `_save_rate_data`](#%EF%B8%8F-method-_save_rate_data)
  - [⚙️ Method `_save_transaction_data`](#%EF%B8%8F-method-_save_transaction_data)
- [🏛️ Class `DateOperations`](#%EF%B8%8F-class-dateoperations)
- [🏛️ Class `ValidationOperations`](#%EF%B8%8F-class-validationoperations)
  - [⚙️ Method `_show_db_error`](#%EF%B8%8F-method-_show_db_error)
  - [⚙️ Method `_show_error`](#%EF%B8%8F-method-_show_error)
  - [⚙️ Method `_show_validation_error`](#%EF%B8%8F-method-_show_validation_error)

</details>

## 🏛️ Class `AutoSaveOperations`

```python
class AutoSaveOperations
```

Mixin class for auto-save operations.

Expected attributes from main class:

- `db_manager`: Database manager instance.
- `_validate_database_connection`: Method to validate database connection.
- `_update_comboboxes`: Method to update comboboxes.
- `update_filter_comboboxes`: Method to update filter comboboxes.
- `_is_valid_date`: Method to validate date format.

Table save handlers are provided by \_get_save_handlers(); \_auto_save_row
dispatches to the handler for the given table name.

<details>
<summary>Code:</summary>

```python
class AutoSaveOperations:

    # Expected attributes from main class
    db_manager: Any
    _validate_database_connection: Callable[[], bool]
    _update_comboboxes: Callable[[], None]
    update_filter_comboboxes: Callable[[], None]
    _is_valid_date: Callable[[str], bool]

    def _auto_save_row(self, table_name: str, model: QStandardItemModel, row: int, row_id: str) -> None:
        """Auto-save table row data.

        Args:

        - `table_name` (`str`): Name of the table.
        - `model` (`QStandardItemModel`): The model containing the data.
        - `row` (`int`): Row index.
        - `row_id` (`str`): Database ID of the row.

        """
        if not self._validate_database_connection():
            return

        handlers = self._get_save_handlers()
        handler = handlers.get(table_name)
        if handler:
            try:
                handler(model, row, row_id)
            except Exception as e:
                self._show_error("Auto-save Error", f"Failed to save {table_name} row: {e!s}")

    def _get_save_handlers(self) -> dict[str, Callable[..., None]]:
        """Return map of table name to save handler (model, row, row_id) -> None."""
        return {
            "transactions": self._save_transaction_data,
            "categories": self._save_category_data,
            "accounts": self._save_account_data,
            "currencies": self._save_currency_data,
            "currency_exchanges": self._save_exchange_data,
            "exchange_rates": self._save_rate_data,
        }

    def _save_account_data(self, model: QStandardItemModel, row: int, row_id: str) -> None:
        """Save account data.

        Args:

        - `model` (`QStandardItemModel`): The model containing the data.
        - `row` (`int`): Row index.
        - `row_id` (`str`): Database ID of the row.

        """
        name = model.data(model.index(row, 0)) or ""
        balance_str = model.data(model.index(row, 1)) or "0"
        currency_code = model.data(model.index(row, 2)) or ""
        is_liquid_str = model.data(model.index(row, 3)) or "1"
        is_cash_str = model.data(model.index(row, 4)) or "0"

        # Validate account name
        if not name.strip():
            self._show_validation_error("Account name cannot be empty")
            return

        # Convert balance to float
        try:
            balance = float(balance_str)
        except (ValueError, TypeError):
            self._show_validation_error(f"Invalid balance value: {balance_str}")
            return

        # Get currency ID
        currency_info = self.db_manager.get_currency_by_code(currency_code)
        if not currency_info:
            self._show_validation_error(f"Currency '{currency_code}' not found")
            return
        currency_id = currency_info[0]

        # Convert boolean flags
        is_liquid = is_liquid_str == "1"
        is_cash = is_cash_str == "1"

        # Update database
        if not self.db_manager.update_account(
            int(row_id), name.strip(), balance, currency_id, is_liquid=is_liquid, is_cash=is_cash
        ):
            self._show_db_error("Failed to save account record")
        else:
            # Update related UI elements
            self._update_comboboxes()

    def _save_category_data(self, model: QStandardItemModel, row: int, row_id: str) -> None:
        """Save category data.

        Args:

        - `model` (`QStandardItemModel`): The model containing the data.
        - `row` (`int`): Row index.
        - `row_id` (`str`): Database ID of the row.

        """
        name = model.data(model.index(row, 0)) or ""
        type_str = model.data(model.index(row, 1)) or "0"
        icon = model.data(model.index(row, 2)) or ""

        # Validate category name
        if not name.strip():
            self._show_validation_error("Category name cannot be empty")
            return

        # Convert type to int and validate
        try:
            category_type = int(type_str)
        except (ValueError, TypeError):
            self._show_validation_error(f"Invalid category type: {type_str}")
            return
        if category_type not in (0, 1):
            self._show_validation_error("Type must be 0 or 1")
            return

        # Update database
        if not self.db_manager.update_category(int(row_id), name.strip(), category_type, icon.strip()):
            self._show_db_error("Failed to save category record")
        else:
            # Update related UI elements
            self._update_comboboxes()
            self.update_filter_comboboxes()

    def _save_currency_data(self, model: QStandardItemModel, row: int, row_id: str) -> None:
        """Save currency data.

        Args:

        - `model` (`QStandardItemModel`): The model containing the data.
        - `row` (`int`): Row index.
        - `row_id` (`str`): Database ID of the row.

        """
        code = model.data(model.index(row, 0)) or ""
        name = model.data(model.index(row, 1)) or ""
        symbol = model.data(model.index(row, 2)) or ""

        # Validate inputs
        if not code.strip():
            self._show_validation_error("Currency code cannot be empty")
            return

        if not name.strip():
            self._show_validation_error("Currency name cannot be empty")
            return

        if not symbol.strip():
            self._show_validation_error("Currency symbol cannot be empty")
            return

        # Update database
        if not self.db_manager.update_currency(int(row_id), code.strip(), name.strip(), symbol.strip()):
            self._show_db_error("Failed to save currency record")
        else:
            # Update related UI elements
            self._update_comboboxes()

    def _save_exchange_data(self, model: QStandardItemModel, row: int, row_id: str) -> None:
        """Save currency exchange data.

        Args:

        - `model` (`QStandardItemModel`): The model containing the data.
        - `row` (`int`): Row index.
        - `row_id` (`str`): Database ID of the row.

        """
        try:
            # Get all field values from the model
            # Column layout: From, To, Amount From, Amount To, Rate, Fee, Date, Description, Loss, Today's Loss
            from_currency_code = model.data(model.index(row, 0)) or ""
            to_currency_code = model.data(model.index(row, 1)) or ""
            amount_from_text = model.data(model.index(row, 2)) or "0"
            amount_to_text = model.data(model.index(row, 3)) or "0"
            rate_text = model.data(model.index(row, 4)) or "0"
            fee_text = model.data(model.index(row, 5)) or "0"
            date = model.data(model.index(row, 6)) or ""
            description = model.data(model.index(row, 7)) or ""

            # Convert amounts to float, handling any formatting
            try:
                amount_from = float(clean_number_text(amount_from_text))
                amount_to = float(clean_number_text(amount_to_text))
                rate = float(clean_number_text(rate_text))
                fee = float(clean_number_text(fee_text))
            except (ValueError, TypeError) as e:
                self._show_validation_error(f"Invalid numeric values: {e}")
                print(
                    f"❌ Error converting values: amount_from={amount_from_text}, amount_to={amount_to_text}, "
                    f"rate={rate_text}, fee={fee_text}"
                )
                return

            errors = validate_exchange_data(
                from_currency_code,
                to_currency_code,
                amount_from,
                amount_to,
                rate,
                fee,
                date_str=date,
                is_valid_date=self._is_valid_date,
            )
            if errors:
                self._show_validation_error(errors[0])
                return

            # Update database using the full update method
            print(f"🔄 Attempting to save exchange data for row {row_id}:")
            print(f"   From: {from_currency_code}, To: {to_currency_code}")
            print(f"   Amount From: {amount_from}, Amount To: {amount_to}")
            print(f"   Rate: {rate}, Fee: {fee}, Date: {date}")
            print(f"   Description: {description}")

            if not self.db_manager.update_currency_exchange_full(
                int(row_id),
                from_currency_code,
                to_currency_code,
                amount_from,
                amount_to,
                rate,
                fee,
                date,
                description,
            ):
                self._show_db_error("Failed to save currency exchange record")
                print(f"❌ Failed to save currency exchange {row_id}")
            else:
                print(f"✅ Successfully updated currency exchange {row_id}")
                # Refresh the table to show updated Loss and Today's Loss values
                # This is done through the update_all mechanism

        except Exception as e:
            self._show_error("Error", f"Failed to save exchange data: {e}")
            print(f"❌ Error saving exchange data for row {row_id}: {e}")

    def _save_rate_data(self, _model: QStandardItemModel, _row: int, _row_id: str) -> None:
        """Save exchange rate data.

        Args:

        - `_model` (`QStandardItemModel`): The model containing the data.
        - `_row` (`int`): Row index.
        - `_row_id` (`str`): Database ID of the row.

        """
        # Exchange rates are complex to update, so we'll skip auto-save for now
        message_box.information(cast("QWidget", self), "Info", "Exchange rate auto-save not implemented yet")

    def _save_transaction_data(self, model: QStandardItemModel, row: int, row_id: str) -> None:
        """Save transaction data.

        Args:

        - `model` (`QStandardItemModel`): The model containing the data.
        - `row` (`int`): Row index.
        - `row_id` (`str`): Database ID of the row.

        """
        # Correct column order in tableView_transactions
        description = model.data(model.index(row, 0)) or ""  # Description
        amount_str = model.data(model.index(row, 1)) or "0"  # Amount
        category_name = model.data(model.index(row, 2)) or ""  # Category
        currency_code = model.data(model.index(row, 3)) or ""  # Currency
        date = model.data(model.index(row, 4)) or ""  # Date
        tag = model.data(model.index(row, 5)) or ""  # Tag

        # Validate date format
        if not self._is_valid_date(date):
            self._show_validation_error("Use YYYY-MM-DD date format")
            return

        # Validate numeric amount (always store positive values in database)
        try:
            # Remove minus sign for validation - always store positive values
            clean_amount_str = amount_str.replace("-", "")
            amount = float(clean_amount_str)
            # Ensure amount is positive (absolute value)
            amount = abs(amount)
        except (ValueError, TypeError):
            self._show_validation_error(f"Invalid amount value: {amount_str}")
            return

        # Validate description
        if not description.strip():
            self._show_validation_error("Description cannot be empty")
            return

        # Remove emoji prefix and "(Income)" suffix if present for database lookup
        clean_category_name = category_name
        # Remove emoji prefix (emoji is typically at the start, followed by a space)
        if (
            clean_category_name
            and clean_category_name[0] not in "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        ):
            # Find first letter/number character (skip emoji)
            for i, char in enumerate(clean_category_name):
                if char in "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz":
                    clean_category_name = clean_category_name[i:].lstrip()
                    break
        # Remove "(Income)" suffix
        clean_category_name = clean_category_name.replace(" (Income)", "")

        # Get category ID
        cat_id = self.db_manager.get_id("categories", "name", clean_category_name)
        if cat_id is None:
            self._show_validation_error(f"Category '{clean_category_name}' not found")
            return

        # Get currency ID
        currency_info = self.db_manager.get_currency_by_code(currency_code)
        if not currency_info:
            self._show_validation_error(f"Currency '{currency_code}' not found")
            return
        currency_id = currency_info[0]

        # Update database
        if not self.db_manager.update_transaction(int(row_id), amount, description, cat_id, currency_id, date, tag):
            self._show_db_error("Failed to save transaction record")
```

</details>

### ⚙️ Method `_auto_save_row`

```python
def _auto_save_row(self, table_name: str, model: QStandardItemModel, row: int, row_id: str) -> None
```

Auto-save table row data.

Args:

- `table_name` (`str`): Name of the table.
- `model` (`QStandardItemModel`): The model containing the data.
- `row` (`int`): Row index.
- `row_id` (`str`): Database ID of the row.

<details>
<summary>Code:</summary>

```python
def _auto_save_row(self, table_name: str, model: QStandardItemModel, row: int, row_id: str) -> None:
        if not self._validate_database_connection():
            return

        handlers = self._get_save_handlers()
        handler = handlers.get(table_name)
        if handler:
            try:
                handler(model, row, row_id)
            except Exception as e:
                self._show_error("Auto-save Error", f"Failed to save {table_name} row: {e!s}")
```

</details>

### ⚙️ Method `_get_save_handlers`

```python
def _get_save_handlers(self) -> dict[str, Callable[..., None]]
```

Return map of table name to save handler (model, row, row_id) -> None.

<details>
<summary>Code:</summary>

```python
def _get_save_handlers(self) -> dict[str, Callable[..., None]]:
        return {
            "transactions": self._save_transaction_data,
            "categories": self._save_category_data,
            "accounts": self._save_account_data,
            "currencies": self._save_currency_data,
            "currency_exchanges": self._save_exchange_data,
            "exchange_rates": self._save_rate_data,
        }
```

</details>

### ⚙️ Method `_save_account_data`

```python
def _save_account_data(self, model: QStandardItemModel, row: int, row_id: str) -> None
```

Save account data.

Args:

- `model` (`QStandardItemModel`): The model containing the data.
- `row` (`int`): Row index.
- `row_id` (`str`): Database ID of the row.

<details>
<summary>Code:</summary>

```python
def _save_account_data(self, model: QStandardItemModel, row: int, row_id: str) -> None:
        name = model.data(model.index(row, 0)) or ""
        balance_str = model.data(model.index(row, 1)) or "0"
        currency_code = model.data(model.index(row, 2)) or ""
        is_liquid_str = model.data(model.index(row, 3)) or "1"
        is_cash_str = model.data(model.index(row, 4)) or "0"

        # Validate account name
        if not name.strip():
            self._show_validation_error("Account name cannot be empty")
            return

        # Convert balance to float
        try:
            balance = float(balance_str)
        except (ValueError, TypeError):
            self._show_validation_error(f"Invalid balance value: {balance_str}")
            return

        # Get currency ID
        currency_info = self.db_manager.get_currency_by_code(currency_code)
        if not currency_info:
            self._show_validation_error(f"Currency '{currency_code}' not found")
            return
        currency_id = currency_info[0]

        # Convert boolean flags
        is_liquid = is_liquid_str == "1"
        is_cash = is_cash_str == "1"

        # Update database
        if not self.db_manager.update_account(
            int(row_id), name.strip(), balance, currency_id, is_liquid=is_liquid, is_cash=is_cash
        ):
            self._show_db_error("Failed to save account record")
        else:
            # Update related UI elements
            self._update_comboboxes()
```

</details>

### ⚙️ Method `_save_category_data`

```python
def _save_category_data(self, model: QStandardItemModel, row: int, row_id: str) -> None
```

Save category data.

Args:

- `model` (`QStandardItemModel`): The model containing the data.
- `row` (`int`): Row index.
- `row_id` (`str`): Database ID of the row.

<details>
<summary>Code:</summary>

```python
def _save_category_data(self, model: QStandardItemModel, row: int, row_id: str) -> None:
        name = model.data(model.index(row, 0)) or ""
        type_str = model.data(model.index(row, 1)) or "0"
        icon = model.data(model.index(row, 2)) or ""

        # Validate category name
        if not name.strip():
            self._show_validation_error("Category name cannot be empty")
            return

        # Convert type to int and validate
        try:
            category_type = int(type_str)
        except (ValueError, TypeError):
            self._show_validation_error(f"Invalid category type: {type_str}")
            return
        if category_type not in (0, 1):
            self._show_validation_error("Type must be 0 or 1")
            return

        # Update database
        if not self.db_manager.update_category(int(row_id), name.strip(), category_type, icon.strip()):
            self._show_db_error("Failed to save category record")
        else:
            # Update related UI elements
            self._update_comboboxes()
            self.update_filter_comboboxes()
```

</details>

### ⚙️ Method `_save_currency_data`

```python
def _save_currency_data(self, model: QStandardItemModel, row: int, row_id: str) -> None
```

Save currency data.

Args:

- `model` (`QStandardItemModel`): The model containing the data.
- `row` (`int`): Row index.
- `row_id` (`str`): Database ID of the row.

<details>
<summary>Code:</summary>

```python
def _save_currency_data(self, model: QStandardItemModel, row: int, row_id: str) -> None:
        code = model.data(model.index(row, 0)) or ""
        name = model.data(model.index(row, 1)) or ""
        symbol = model.data(model.index(row, 2)) or ""

        # Validate inputs
        if not code.strip():
            self._show_validation_error("Currency code cannot be empty")
            return

        if not name.strip():
            self._show_validation_error("Currency name cannot be empty")
            return

        if not symbol.strip():
            self._show_validation_error("Currency symbol cannot be empty")
            return

        # Update database
        if not self.db_manager.update_currency(int(row_id), code.strip(), name.strip(), symbol.strip()):
            self._show_db_error("Failed to save currency record")
        else:
            # Update related UI elements
            self._update_comboboxes()
```

</details>

### ⚙️ Method `_save_exchange_data`

```python
def _save_exchange_data(self, model: QStandardItemModel, row: int, row_id: str) -> None
```

Save currency exchange data.

Args:

- `model` (`QStandardItemModel`): The model containing the data.
- `row` (`int`): Row index.
- `row_id` (`str`): Database ID of the row.

<details>
<summary>Code:</summary>

```python
def _save_exchange_data(self, model: QStandardItemModel, row: int, row_id: str) -> None:
        try:
            # Get all field values from the model
            # Column layout: From, To, Amount From, Amount To, Rate, Fee, Date, Description, Loss, Today's Loss
            from_currency_code = model.data(model.index(row, 0)) or ""
            to_currency_code = model.data(model.index(row, 1)) or ""
            amount_from_text = model.data(model.index(row, 2)) or "0"
            amount_to_text = model.data(model.index(row, 3)) or "0"
            rate_text = model.data(model.index(row, 4)) or "0"
            fee_text = model.data(model.index(row, 5)) or "0"
            date = model.data(model.index(row, 6)) or ""
            description = model.data(model.index(row, 7)) or ""

            # Convert amounts to float, handling any formatting
            try:
                amount_from = float(clean_number_text(amount_from_text))
                amount_to = float(clean_number_text(amount_to_text))
                rate = float(clean_number_text(rate_text))
                fee = float(clean_number_text(fee_text))
            except (ValueError, TypeError) as e:
                self._show_validation_error(f"Invalid numeric values: {e}")
                print(
                    f"❌ Error converting values: amount_from={amount_from_text}, amount_to={amount_to_text}, "
                    f"rate={rate_text}, fee={fee_text}"
                )
                return

            errors = validate_exchange_data(
                from_currency_code,
                to_currency_code,
                amount_from,
                amount_to,
                rate,
                fee,
                date_str=date,
                is_valid_date=self._is_valid_date,
            )
            if errors:
                self._show_validation_error(errors[0])
                return

            # Update database using the full update method
            print(f"🔄 Attempting to save exchange data for row {row_id}:")
            print(f"   From: {from_currency_code}, To: {to_currency_code}")
            print(f"   Amount From: {amount_from}, Amount To: {amount_to}")
            print(f"   Rate: {rate}, Fee: {fee}, Date: {date}")
            print(f"   Description: {description}")

            if not self.db_manager.update_currency_exchange_full(
                int(row_id),
                from_currency_code,
                to_currency_code,
                amount_from,
                amount_to,
                rate,
                fee,
                date,
                description,
            ):
                self._show_db_error("Failed to save currency exchange record")
                print(f"❌ Failed to save currency exchange {row_id}")
            else:
                print(f"✅ Successfully updated currency exchange {row_id}")
                # Refresh the table to show updated Loss and Today's Loss values
                # This is done through the update_all mechanism

        except Exception as e:
            self._show_error("Error", f"Failed to save exchange data: {e}")
            print(f"❌ Error saving exchange data for row {row_id}: {e}")
```

</details>

### ⚙️ Method `_save_rate_data`

```python
def _save_rate_data(self, _model: QStandardItemModel, _row: int, _row_id: str) -> None
```

Save exchange rate data.

Args:

- `_model` (`QStandardItemModel`): The model containing the data.
- `_row` (`int`): Row index.
- `_row_id` (`str`): Database ID of the row.

<details>
<summary>Code:</summary>

```python
def _save_rate_data(self, _model: QStandardItemModel, _row: int, _row_id: str) -> None:
        # Exchange rates are complex to update, so we'll skip auto-save for now
        message_box.information(cast("QWidget", self), "Info", "Exchange rate auto-save not implemented yet")
```

</details>

### ⚙️ Method `_save_transaction_data`

```python
def _save_transaction_data(self, model: QStandardItemModel, row: int, row_id: str) -> None
```

Save transaction data.

Args:

- `model` (`QStandardItemModel`): The model containing the data.
- `row` (`int`): Row index.
- `row_id` (`str`): Database ID of the row.

<details>
<summary>Code:</summary>

```python
def _save_transaction_data(self, model: QStandardItemModel, row: int, row_id: str) -> None:
        # Correct column order in tableView_transactions
        description = model.data(model.index(row, 0)) or ""  # Description
        amount_str = model.data(model.index(row, 1)) or "0"  # Amount
        category_name = model.data(model.index(row, 2)) or ""  # Category
        currency_code = model.data(model.index(row, 3)) or ""  # Currency
        date = model.data(model.index(row, 4)) or ""  # Date
        tag = model.data(model.index(row, 5)) or ""  # Tag

        # Validate date format
        if not self._is_valid_date(date):
            self._show_validation_error("Use YYYY-MM-DD date format")
            return

        # Validate numeric amount (always store positive values in database)
        try:
            # Remove minus sign for validation - always store positive values
            clean_amount_str = amount_str.replace("-", "")
            amount = float(clean_amount_str)
            # Ensure amount is positive (absolute value)
            amount = abs(amount)
        except (ValueError, TypeError):
            self._show_validation_error(f"Invalid amount value: {amount_str}")
            return

        # Validate description
        if not description.strip():
            self._show_validation_error("Description cannot be empty")
            return

        # Remove emoji prefix and "(Income)" suffix if present for database lookup
        clean_category_name = category_name
        # Remove emoji prefix (emoji is typically at the start, followed by a space)
        if (
            clean_category_name
            and clean_category_name[0] not in "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        ):
            # Find first letter/number character (skip emoji)
            for i, char in enumerate(clean_category_name):
                if char in "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz":
                    clean_category_name = clean_category_name[i:].lstrip()
                    break
        # Remove "(Income)" suffix
        clean_category_name = clean_category_name.replace(" (Income)", "")

        # Get category ID
        cat_id = self.db_manager.get_id("categories", "name", clean_category_name)
        if cat_id is None:
            self._show_validation_error(f"Category '{clean_category_name}' not found")
            return

        # Get currency ID
        currency_info = self.db_manager.get_currency_by_code(currency_code)
        if not currency_info:
            self._show_validation_error(f"Currency '{currency_code}' not found")
            return
        currency_id = currency_info[0]

        # Update database
        if not self.db_manager.update_transaction(int(row_id), amount, description, cat_id, currency_id, date, tag):
            self._show_db_error("Failed to save transaction record")
```

</details>

## 🏛️ Class `DateOperations`

```python
class DateOperations(DateMixin)
```

Mixin class for date operations.

Expected attributes from main class:

- `db_manager`: Database manager instance.
- `_validate_database_connection`: Method to validate database connection.

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

    def _show_db_error(self, message: str) -> None:
        """Show database error message."""
        message_box.warning(cast("QWidget", self), "Database Error", message)

    def _show_error(self, title: str, message: str) -> None:
        """Show error message with given title."""
        message_box.warning(cast("QWidget", self), title, message)

    def _show_validation_error(self, message: str) -> None:
        """Show validation error message."""
        message_box.warning(cast("QWidget", self), "Validation Error", message)
```

</details>

### ⚙️ Method `_show_db_error`

```python
def _show_db_error(self, message: str) -> None
```

Show database error message.

<details>
<summary>Code:</summary>

```python
def _show_db_error(self, message: str) -> None:
        message_box.warning(cast("QWidget", self), "Database Error", message)
```

</details>

### ⚙️ Method `_show_error`

```python
def _show_error(self, title: str, message: str) -> None
```

Show error message with given title.

<details>
<summary>Code:</summary>

```python
def _show_error(self, title: str, message: str) -> None:
        message_box.warning(cast("QWidget", self), title, message)
```

</details>

### ⚙️ Method `_show_validation_error`

```python
def _show_validation_error(self, message: str) -> None
```

Show validation error message.

<details>
<summary>Code:</summary>

```python
def _show_validation_error(self, message: str) -> None:
        message_box.warning(cast("QWidget", self), "Validation Error", message)
```

</details>
