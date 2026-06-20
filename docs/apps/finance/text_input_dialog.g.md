---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `text_input_dialog.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `TextInputDialog`](#️-class-textinputdialog)
  - [⚙️ Method `__init__`](#️-method-__init__)
  - [⚙️ Method `get_items`](#️-method-get_items)

</details>

## 🏛️ Class `TextInputDialog`

```python
class TextInputDialog(PurchaseTableDialog)
```

Dialog for entering purchase information in an editable table.

<details>
<summary>Code:</summary>

```python
class TextInputDialog(PurchaseTableDialog):

    def __init__(
        self,
        parent: QWidget | None = None,
        default_date: QDate | None = None,
        *,
        initial_text: str | None = None,
        focus_text_on_show: bool = True,
        currency_symbol: str = "",
    ) -> None:
        """Initialize the finance purchase input dialog.

        Args:

        - `parent` (`QWidget | None`): Parent widget. Defaults to `None`.
        - `default_date` (`QDate | None`): Default date for purchases. Defaults to `None` (current date).
        - `initial_text` (`str | None`): Pre-filled purchase lines from AI. Defaults to `None`.
        - `focus_text_on_show` (`bool`): Ignored; kept for API compatibility.
        - `currency_symbol` (`str`): Default currency symbol for the total label.

        """
        super().__init__(
            parent,
            title="Add Purchases as Text",
            description=_DESCRIPTION,
            default_date=default_date,
            initial_text=initial_text,
            currency_symbol=currency_symbol,
            text_placeholder=PURCHASE_TEXT_PLACEHOLDER,
        )
        _ = focus_text_on_show

    def get_items(self) -> list[ParsedPurchaseItem]:
        """Return validated purchase items accepted by the user."""
        return super().get_items()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None, default_date: QDate | None = None) -> None
```

Initialize the finance purchase input dialog.

Args:

- `parent` (`QWidget | None`): Parent widget. Defaults to `None`.
- `default_date` (`QDate | None`): Default date for purchases. Defaults to `None` (current date).
- `initial_text` (`str | None`): Pre-filled purchase lines from AI. Defaults to `None`.
- `focus_text_on_show` (`bool`): Ignored; kept for API compatibility.
- `currency_symbol` (`str`): Default currency symbol for the total label.

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
        currency_symbol: str = "",
    ) -> None:
        super().__init__(
            parent,
            title="Add Purchases as Text",
            description=_DESCRIPTION,
            default_date=default_date,
            initial_text=initial_text,
            currency_symbol=currency_symbol,
            text_placeholder=PURCHASE_TEXT_PLACEHOLDER,
        )
        _ = focus_text_on_show
```

</details>

### ⚙️ Method `get_items`

```python
def get_items(self) -> list[ParsedPurchaseItem]
```

Return validated purchase items accepted by the user.

<details>
<summary>Code:</summary>

```python
def get_items(self) -> list[ParsedPurchaseItem]:
        return super().get_items()
```

</details>
