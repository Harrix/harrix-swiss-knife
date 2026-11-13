---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `button_base.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `FluentIconMixin`](#%EF%B8%8F-class-fluenticonmixin)
- [🏛️ Class `FluentPushButton`](#%EF%B8%8F-class-fluentpushbutton)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `refresh_theme`](#%EF%B8%8F-method-refresh_theme)
  - [⚙️ Method `set_icon_name`](#%EF%B8%8F-method-set_icon_name)

</details>

## 🏛️ Class `FluentIconMixin`

```python
class FluentIconMixin
```

Keep a Lucide icon on a button in the current text color.

<details>
<summary>Code:</summary>

```python
class FluentIconMixin:

    _icon_name: str = ""
    _icon_on_accent: bool = False

    def _sync_icon(self) -> None:
        button = self
        if not isinstance(button, QAbstractButton) or not self._icon_name:
            return
        palette = palette_for(button)
        if self._icon_on_accent:
            button.setIcon(create_lucide_icon(self._icon_name, ICON_SIZE, color=palette.text_on_accent))
        else:
            button.setIcon(themed_icon(self._icon_name, palette))
        button.setIconSize(QSize(ICON_SIZE, ICON_SIZE))
```

</details>

## 🏛️ Class `FluentPushButton`

```python
class FluentPushButton(FluentIconMixin, QPushButton)
```

Standard neutral Fluent button with an optional Lucide icon.

<details>
<summary>Code:</summary>

```python
class FluentPushButton(FluentIconMixin, QPushButton):

    def __init__(self, text: str = "", parent: QWidget | None = None, *, icon: str = "") -> None:
        """Create a standard button.

        Args:

        - `text` (`str`): Caption.
        - `parent` (`QWidget | None`): Optional parent.
        - `icon` (`str`): Optional Lucide icon ID.

        """
        super().__init__(text, parent)
        self._icon_name = icon
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAutoDefault(False)
        bind_theme(self, self.refresh_theme)

    def refresh_theme(self) -> None:
        """Re-apply chrome and icon colors."""
        self.setStyleSheet(push_button_qss(palette_for(self)))
        self._sync_icon()

    def set_icon_name(self, name: str) -> None:
        """Set the Lucide icon ID."""
        self._icon_name = name
        self._sync_icon()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, text: str = '', parent: QWidget | None = None, *, icon: str = '') -> None
```

Create a standard button.

Args:

- `text` (`str`): Caption.
- `parent` (`QWidget | None`): Optional parent.
- [`icon`](../../qt_split_menu_button.g.md#%EF%B8%8F-method-icon) (`str`): Optional Lucide icon ID.

<details>
<summary>Code:</summary>

```python
def __init__(self, text: str = "", parent: QWidget | None = None, *, icon: str = "") -> None:
        super().__init__(text, parent)
        self._icon_name = icon
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAutoDefault(False)
        bind_theme(self, self.refresh_theme)
```

</details>

### ⚙️ Method `refresh_theme`

```python
def refresh_theme(self) -> None
```

Re-apply chrome and icon colors.

<details>
<summary>Code:</summary>

```python
def refresh_theme(self) -> None:
        self.setStyleSheet(push_button_qss(palette_for(self)))
        self._sync_icon()
```

</details>

### ⚙️ Method `set_icon_name`

```python
def set_icon_name(self, name: str) -> None
```

Set the Lucide icon ID.

<details>
<summary>Code:</summary>

```python
def set_icon_name(self, name: str) -> None:
        self._icon_name = name
        self._sync_icon()
```

</details>
