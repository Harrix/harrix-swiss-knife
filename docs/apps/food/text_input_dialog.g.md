---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `text_input_dialog.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [📎 Constant `FOOD_TEXT_PLACEHOLDER`](#-constant-food_text_placeholder)
- [🏛️ Class `TextInputDialog`](#%EF%B8%8F-class-textinputdialog)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `get_items`](#%EF%B8%8F-method-get_items)

</details>

## 📎 Constant `FOOD_TEXT_PLACEHOLDER`

```python
FOOD_TEXT_PLACEHOLDER = 'Enter your food items here...\nTSV example:\nOatmeal\t150\t350\tweight\tno\nCoffee\t250\t85\tportion\tyes\n\nLegacy example:\n100 200 Apple\n150 Coffee\nCoffee 100 portion'
```

_No docstring provided._

## 🏛️ Class `TextInputDialog`

```python
class TextInputDialog(FoodTableDialog)
```

Dialog for entering food information in an editable table.

<details>
<summary>Code:</summary>

```python
class TextInputDialog(FoodTableDialog):

    def __init__(
        self,
        parent: QWidget | None = None,
        default_date: QDate | None = None,
        *,
        initial_text: str | None = None,
        focus_text_on_show: bool = True,
        db_manager: Any | None = None,
    ) -> None:
        """Initialize the food input dialog.

        Args:

        - `parent` (`QWidget | None`): Parent widget. Defaults to `None`.
        - `default_date` (`QDate | None`): Default date for food log entries.
        - `initial_text` (`str | None`): Pre-filled lines from AI. Defaults to `None`.
        - `focus_text_on_show` (`bool`): Ignored; kept for API compatibility.
        - `db_manager` (`Any | None`): Database manager for legacy text lookup.

        """
        super().__init__(
            parent,
            title="Add Food as Text",
            description=_DESCRIPTION,
            default_date=default_date,
            initial_text=initial_text,
            text_placeholder=FOOD_TEXT_PLACEHOLDER,
            db_manager=db_manager,
        )
        _ = focus_text_on_show

    def get_items(self) -> list[ParsedFoodItem]:
        """Return validated food items accepted by the user."""
        return super().get_items()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None, default_date: QDate | None = None, *, initial_text: str | None = None, focus_text_on_show: bool = True, db_manager: Any | None = None) -> None
```

Initialize the food input dialog.

Args:

- `parent` (`QWidget | None`): Parent widget. Defaults to `None`.
- `default_date` (`QDate | None`): Default date for food log entries.
- `initial_text` (`str | None`): Pre-filled lines from AI. Defaults to `None`.
- `focus_text_on_show` (`bool`): Ignored; kept for API compatibility.
- `db_manager` (`Any | None`): Database manager for legacy text lookup.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        parent: QWidget | None = None,
        default_date: QDate | None = None,
        *,
        initial_text: str | None = None,
        focus_text_on_show: bool = True,
        db_manager: Any | None = None,
    ) -> None:
        super().__init__(
            parent,
            title="Add Food as Text",
            description=_DESCRIPTION,
            default_date=default_date,
            initial_text=initial_text,
            text_placeholder=FOOD_TEXT_PLACEHOLDER,
            db_manager=db_manager,
        )
        _ = focus_text_on_show
```

</details>

### ⚙️ Method `get_items`

```python
def get_items(self) -> list[ParsedFoodItem]
```

Return validated food items accepted by the user.

<details>
<summary>Code:</summary>

```python
def get_items(self) -> list[ParsedFoodItem]:
        return super().get_items()
```

</details>
