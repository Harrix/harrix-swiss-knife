---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `category_combo_box_delegate.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `CategoryComboBoxDelegate`](#%EF%B8%8F-class-categorycomboboxdelegate)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `categories`](#%EF%B8%8F-method-categories)
  - [⚙️ Method `categories`](#%EF%B8%8F-method-categories-1)

</details>

## 🏛️ Class `CategoryComboBoxDelegate`

```python
class CategoryComboBoxDelegate(ComboBoxDelegate)
```

Delegate for category column in transactions table with dropdown list.

<details>
<summary>Code:</summary>

```python
class CategoryComboBoxDelegate(ComboBoxDelegate):

    def __init__(self, parent: QObject | None = None, categories: list[str] | None = None) -> None:
        """Initialize CategoryComboBoxDelegate.

        Args:

        - `parent` (`QObject | None`): Parent object.
        - `categories` (`list[str] | None`): List of category names for the combo box.

        """
        super().__init__(parent, items=categories)

    @property
    def categories(self) -> list[str]:
        """Category names shown in the combo box."""
        return self.items

    @categories.setter
    def categories(self, value: list[str] | None) -> None:
        self.items = list(value or [])
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QObject | None = None, categories: list[str] | None = None) -> None
```

Initialize CategoryComboBoxDelegate.

Args:

- `parent` (`QObject | None`): Parent object.
- `categories` (`list[str] | None`): List of category names for the combo box.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QObject | None = None, categories: list[str] | None = None) -> None:
        super().__init__(parent, items=categories)
```

</details>

### ⚙️ Method `categories`

```python
def categories(self) -> list[str]
```

Category names shown in the combo box.

<details>
<summary>Code:</summary>

```python
def categories(self) -> list[str]:
        return self.items
```

</details>

### ⚙️ Method `categories`

```python
def categories(self, value: list[str] | None) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def categories(self, value: list[str] | None) -> None:
        self.items = list(value or [])
```

</details>
