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

Dialog for entering food information as text.

<details>
<summary>Code:</summary>

```python
class TextInputDialog(_BaseTextInputDialog):

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the food text input dialog.

        Args:

        - `parent` (`QWidget | None`): Parent widget. Defaults to `None`.

        """
        super().__init__(
            parent,
            title="Add Food as Text",
            description=_DESCRIPTION,
            placeholder=_PLACEHOLDER,
        )
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Initialize the food text input dialog.

Args:

- `parent` (`QWidget | None`): Parent widget. Defaults to `None`.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(
            parent,
            title="Add Food as Text",
            description=_DESCRIPTION,
            placeholder=_PLACEHOLDER,
        )
```

</details>
