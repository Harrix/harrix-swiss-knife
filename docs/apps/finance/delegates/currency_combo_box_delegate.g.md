---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `currency_combo_box_delegate.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `CurrencyComboBoxDelegate`](#️-class-currencycomboboxdelegate)
  - [⚙️ Method `__init__`](#️-method-__init__)
  - [⚙️ Method `currencies`](#️-method-currencies)
  - [⚙️ Method `currencies`](#️-method-currencies-1)

</details>

## 🏛️ Class `CurrencyComboBoxDelegate`

```python
class CurrencyComboBoxDelegate(ComboBoxDelegate)
```

Delegate for currency column in transactions table with dropdown list.

<details>
<summary>Code:</summary>

```python
class CurrencyComboBoxDelegate(ComboBoxDelegate):

    def __init__(self, parent: QObject | None = None, currencies: list[str] | None = None) -> None:
        """Initialize CurrencyComboBoxDelegate.

        Args:

        - `parent` (`QObject | None`): Parent widget.
        - `currencies` (`list[str] | None`): List of currency codes.

        """
        super().__init__(parent, items=currencies)

    @property
    def currencies(self) -> list[str]:
        """Currency codes shown in the combo box."""
        return self.items

    @currencies.setter
    def currencies(self, value: list[str] | None) -> None:
        self.items = list(value or [])
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QObject | None = None, currencies: list[str] | None = None) -> None
```

Initialize CurrencyComboBoxDelegate.

Args:

- `parent` (`QObject | None`): Parent widget.
- `currencies` (`list[str] | None`): List of currency codes.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QObject | None = None, currencies: list[str] | None = None) -> None:
        super().__init__(parent, items=currencies)
```

</details>

### ⚙️ Method `currencies`

```python
def currencies(self) -> list[str]
```

Currency codes shown in the combo box.

<details>
<summary>Code:</summary>

```python
def currencies(self) -> list[str]:
        return self.items
```

</details>

### ⚙️ Method `currencies`

```python
def currencies(self, value: list[str] | None) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def currencies(self, value: list[str] | None) -> None:
        self.items = list(value or [])
```

</details>
