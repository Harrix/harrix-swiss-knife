---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `text_input_dialog.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `TextInputDialog`](#%EF%B8%8F-class-textinputdialog)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)

</details>

## 🏛️ Class `TextInputDialog`

```python
class TextInputDialog(_BaseTextInputDialog)
```

Dialog for entering purchase information as text.

<details>
<summary>Code:</summary>

```python
class TextInputDialog(_BaseTextInputDialog):

    def __init__(self, parent: QWidget | None = None, default_date: QDate | None = None) -> None:
        """Initialize the finance text input dialog.

        Args:

        - `parent` (`QWidget | None`): Parent widget. Defaults to `None`.
        - `default_date` (`QDate | None`): Default date for purchases. Defaults to `None` (current date).

        """
        super().__init__(
            parent,
            title="Add Purchases as Text",
            description=_DESCRIPTION,
            placeholder=_PLACEHOLDER,
            show_date=True,
            default_date=default_date,
            focus_text_on_show=True,
        )
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None, default_date: QDate | None = None) -> None
```

Initialize the finance text input dialog.

Args:

- `parent` (`QWidget | None`): Parent widget. Defaults to `None`.
- `default_date` (`QDate | None`): Default date for purchases. Defaults to `None` (current date).

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None, default_date: QDate | None = None) -> None:
        super().__init__(
            parent,
            title="Add Purchases as Text",
            description=_DESCRIPTION,
            placeholder=_PLACEHOLDER,
            show_date=True,
            default_date=default_date,
            focus_text_on_show=True,
        )
```

</details>
