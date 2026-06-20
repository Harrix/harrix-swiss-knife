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

</details>

## 🏛️ Class `TextInputDialog`

```python
class TextInputDialog(_BaseTextInputDialog)
```

Dialog for entering food information as text.

<details>
<summary>Code:</summary>

```python
class TextInputDialog(_BaseTextInputDialog):

    def __init__(
        self,
        parent: QWidget | None = None,
        default_date: QDate | None = None,
        *,
        initial_text: str | None = None,
        focus_text_on_show: bool = True,
    ) -> None:
        """Initialize the food text input dialog.

        Args:

        - `parent` (`QWidget | None`): Parent widget. Defaults to `None`.
        - `default_date` (`QDate | None`): Default date for food log entries.
        - `initial_text` (`str | None`): Pre-filled text. Defaults to `None`.
        - `focus_text_on_show` (`bool`): Focus text area on show. Defaults to `True`.

        """
        super().__init__(
            parent,
            title="Add Food as Text",
            description=_DESCRIPTION,
            placeholder=FOOD_TEXT_PLACEHOLDER,
            show_date=True,
            default_date=default_date,
            initial_text=initial_text,
            focus_text_on_show=focus_text_on_show,
        )
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None, default_date: QDate | None = None) -> None
```

Initialize the food text input dialog.

Args:

- `parent` (`QWidget | None`): Parent widget. Defaults to `None`.
- `default_date` (`QDate | None`): Default date for food log entries.
- `initial_text` (`str | None`): Pre-filled text. Defaults to `None`.
- `focus_text_on_show` (`bool`): Focus text area on show. Defaults to `True`.

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
    ) -> None:
        super().__init__(
            parent,
            title="Add Food as Text",
            description=_DESCRIPTION,
            placeholder=FOOD_TEXT_PLACEHOLDER,
            show_date=True,
            default_date=default_date,
            initial_text=initial_text,
            focus_text_on_show=focus_text_on_show,
        )
```

</details>
