---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `input_base.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `FluentLineEdit`](#%EF%B8%8F-class-fluentlineedit)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `refresh_theme`](#%EF%B8%8F-method-refresh_theme)

</details>

## 🏛️ Class `FluentLineEdit`

```python
class FluentLineEdit(QLineEdit)
```

Single-line Fluent text box with an optional clear button.

<details>
<summary>Code:</summary>

```python
class FluentLineEdit(QLineEdit):

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        placeholder: str = "",
        clearable: bool = True,
        compact: bool = False,
    ) -> None:
        """Create a text box.

        Args:

        - `parent` (`QWidget | None`): Optional parent.
        - `placeholder` (`str`): Placeholder text.
        - `clearable` (`bool`): Show a clear button while non-empty. Defaults to `True`.
        - `compact` (`bool`): Use the compact control height (title bars, toolbars). Defaults to `False`.

        """
        super().__init__(parent)
        self._height = CONTROL_HEIGHT_COMPACT if compact else CONTROL_HEIGHT
        self.setPlaceholderText(placeholder)
        self.setClearButtonEnabled(clearable)
        if compact:
            self.setFixedHeight(self._height)
        else:
            self.setMinimumHeight(self._height)
        bind_theme(self, self.refresh_theme)

    def refresh_theme(self) -> None:
        """Re-apply chrome for the current palette."""
        self.setStyleSheet(line_edit_qss(palette_for(self), height=self._height))
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None, *, placeholder: str = '', clearable: bool = True, compact: bool = False) -> None
```

Create a text box.

Args:

- `parent` (`QWidget | None`): Optional parent.
- `placeholder` (`str`): Placeholder text.
- `clearable` (`bool`): Show a clear button while non-empty. Defaults to `True`.
- `compact` (`bool`): Use the compact control height (title bars, toolbars). Defaults to `False`.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        parent: QWidget | None = None,
        *,
        placeholder: str = "",
        clearable: bool = True,
        compact: bool = False,
    ) -> None:
        super().__init__(parent)
        self._height = CONTROL_HEIGHT_COMPACT if compact else CONTROL_HEIGHT
        self.setPlaceholderText(placeholder)
        self.setClearButtonEnabled(clearable)
        if compact:
            self.setFixedHeight(self._height)
        else:
            self.setMinimumHeight(self._height)
        bind_theme(self, self.refresh_theme)
```

</details>

### ⚙️ Method `refresh_theme`

```python
def refresh_theme(self) -> None
```

Re-apply chrome for the current palette.

<details>
<summary>Code:</summary>

```python
def refresh_theme(self) -> None:
        self.setStyleSheet(line_edit_qss(palette_for(self), height=self._height))
```

</details>
