---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `text_base.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `FluentText`](#%EF%B8%8F-class-fluenttext)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `refresh_theme`](#%EF%B8%8F-method-refresh_theme)
  - [⚙️ Method `set_role`](#%EF%B8%8F-method-set_role)
  - [⚙️ Method `set_text_style`](#%EF%B8%8F-method-set_text_style)
  - [⚙️ Method `text_style`](#%EF%B8%8F-method-text_style)

</details>

## 🏛️ Class `FluentText`

```python
class FluentText(QLabel)
```

Label that uses one step of the Fluent type ramp and a theme text color.

<details>
<summary>Code:</summary>

```python
class FluentText(QLabel):

    def __init__(
        self,
        text: str = "",
        parent: QWidget | None = None,
        *,
        style: TextStyle = TextStyle.BODY,
        role: TextRole = TextRole.PRIMARY,
        word_wrap: bool = False,
    ) -> None:
        """Create a themed label.

        Args:

        - `text` (`str`): Label text.
        - `parent` (`QWidget | None`): Optional parent.
        - `style` (`TextStyle`): Type ramp entry. Defaults to `BODY`.
        - `role` (`TextRole`): Color role. Defaults to `PRIMARY`.
        - `word_wrap` (`bool`): Wrap long text. Defaults to `False`.

        """
        super().__init__(text, parent)
        self._style = style
        self._role = role
        self.setWordWrap(word_wrap)
        self._apply_font()
        bind_theme(self, self.refresh_theme)

    def refresh_theme(self) -> None:
        """Re-apply the text color for the current palette."""
        palette = palette_for(self)
        colors = {
            TextRole.PRIMARY: palette.text_primary,
            TextRole.SECONDARY: palette.text_secondary,
            TextRole.TERTIARY: palette.text_tertiary,
            TextRole.ACCENT: palette.accent_text,
            TextRole.DISABLED: palette.text_disabled,
        }
        self.setStyleSheet(f"QLabel {{ color: {css(colors[self._role])}; background: transparent; }}")

    def set_role(self, role: TextRole) -> None:
        """Switch the color role."""
        self._role = role
        self.refresh_theme()

    def set_text_style(self, style: TextStyle) -> None:
        """Switch the type ramp entry."""
        self._style = style
        self._apply_font()

    def text_style(self) -> TextStyle:
        """Return the type ramp entry."""
        return self._style

    def _apply_font(self) -> None:
        scale, weight = self._style.value
        app = QApplication.instance()
        base = app.font() if isinstance(app, QApplication) else QFont()
        self.setFont(fluent_font(base, scale, weight=weight))
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, text: str = '', parent: QWidget | None = None, *, style: TextStyle = TextStyle.BODY, role: TextRole = TextRole.PRIMARY, word_wrap: bool = False) -> None
```

Create a themed label.

Args:

- `text` (`str`): Label text.
- `parent` (`QWidget | None`): Optional parent.
- `style` ([`TextStyle`](enums.g.md#%EF%B8%8F-class-textstyle)): Type ramp entry. Defaults to `BODY`.
- `role` ([`TextRole`](enums.g.md#%EF%B8%8F-class-textrole)): Color role. Defaults to `PRIMARY`.
- `word_wrap` (`bool`): Wrap long text. Defaults to `False`.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        text: str = "",
        parent: QWidget | None = None,
        *,
        style: TextStyle = TextStyle.BODY,
        role: TextRole = TextRole.PRIMARY,
        word_wrap: bool = False,
    ) -> None:
        super().__init__(text, parent)
        self._style = style
        self._role = role
        self.setWordWrap(word_wrap)
        self._apply_font()
        bind_theme(self, self.refresh_theme)
```

</details>

### ⚙️ Method `refresh_theme`

```python
def refresh_theme(self) -> None
```

Re-apply the text color for the current palette.

<details>
<summary>Code:</summary>

```python
def refresh_theme(self) -> None:
        palette = palette_for(self)
        colors = {
            TextRole.PRIMARY: palette.text_primary,
            TextRole.SECONDARY: palette.text_secondary,
            TextRole.TERTIARY: palette.text_tertiary,
            TextRole.ACCENT: palette.accent_text,
            TextRole.DISABLED: palette.text_disabled,
        }
        self.setStyleSheet(f"QLabel {{ color: {css(colors[self._role])}; background: transparent; }}")
```

</details>

### ⚙️ Method `set_role`

```python
def set_role(self, role: TextRole) -> None
```

Switch the color role.

<details>
<summary>Code:</summary>

```python
def set_role(self, role: TextRole) -> None:
        self._role = role
        self.refresh_theme()
```

</details>

### ⚙️ Method `set_text_style`

```python
def set_text_style(self, style: TextStyle) -> None
```

Switch the type ramp entry.

<details>
<summary>Code:</summary>

```python
def set_text_style(self, style: TextStyle) -> None:
        self._style = style
        self._apply_font()
```

</details>

### ⚙️ Method `text_style`

```python
def text_style(self) -> TextStyle
```

Return the type ramp entry.

<details>
<summary>Code:</summary>

```python
def text_style(self) -> TextStyle:
        return self._style
```

</details>
