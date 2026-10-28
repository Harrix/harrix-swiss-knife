---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `qt_split_menu_button.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `SplitColors`](#%EF%B8%8F-class-splitcolors)
- [🏛️ Class `SplitMenuButton`](#%EF%B8%8F-class-splitmenubutton)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `arrow_button (property)`](#%EF%B8%8F-method-arrow_button-property)
  - [⚙️ Method `icon`](#%EF%B8%8F-method-icon)
  - [⚙️ Method `main_button (property)`](#%EF%B8%8F-method-main_button-property)
  - [⚙️ Method `menu`](#%EF%B8%8F-method-menu)
  - [⚙️ Method `minimumSizeHint`](#%EF%B8%8F-method-minimumsizehint)
  - [⚙️ Method `refresh_theme`](#%EF%B8%8F-method-refresh_theme)
  - [⚙️ Method `setIcon`](#%EF%B8%8F-method-seticon)
  - [⚙️ Method `setIconSize`](#%EF%B8%8F-method-seticonsize)
  - [⚙️ Method `setMenu`](#%EF%B8%8F-method-setmenu)
  - [⚙️ Method `setText`](#%EF%B8%8F-method-settext)
  - [⚙️ Method `sizeHint`](#%EF%B8%8F-method-sizehint)
  - [⚙️ Method `text`](#%EF%B8%8F-method-text)
- [🔧 Function `make_lucide_split_menu_button`](#-function-make_lucide_split_menu_button)
- [🔧 Function `split_colors`](#-function-split_colors)
- [🔧 Function `split_style`](#-function-split_style)

</details>

## 🏛️ Class `SplitColors`

```python
class SplitColors
```

CSS colors for the split button chrome.

<details>
<summary>Code:</summary>

```python
class SplitColors:

    border: str
    background: str
    hover: str
    zone_hover: str
    pressed: str
    text: str
    separator: str
```

</details>

## 🏛️ Class `SplitMenuButton`

```python
class SplitMenuButton(QWidget)
```

Push-button left zone plus a menu arrow separated by a vertical line.

Clicking the main zone emits `clicked`. Clicking the arrow opens `menu()`.
Use this wherever a default action and a related dropdown are needed.

<details>
<summary>Code:</summary>

```python
class SplitMenuButton(QWidget):

    clicked = Signal()

    def __init__(self, parent: QWidget | None = None, text: str = "") -> None:
        """Build the split chrome with an empty optional menu."""
        super().__init__(parent)
        self.setObjectName("splitMenuButton")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, on=True)
        self.setStyleSheet(split_style(_HARRIX_COLORS))
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(_idle_push_button_height())

        self._menu: QMenu | None = None

        self._main = QPushButton(text, self)
        self._main.setObjectName("splitMenuMain")
        self._main.setCursor(Qt.CursorShape.PointingHandCursor)
        self._main.setAutoDefault(False)
        self._main.setDefault(False)
        self._main.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self._main.clicked.connect(self.clicked.emit)

        self._separator = QFrame(self)
        self._separator.setObjectName("splitMenuSeparator")
        self._separator.setFrameShape(QFrame.Shape.NoFrame)
        self._separator.setFixedWidth(1)
        self._separator.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

        self._arrow = QToolButton(self)
        self._arrow.setObjectName("splitMenuArrow")
        self._arrow.setCursor(Qt.CursorShape.PointingHandCursor)
        self._arrow.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._arrow.setAutoRaise(False)
        self._arrow.setFixedWidth(_ARROW_WIDTH)
        self._arrow.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self._arrow.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        apply_lucide_button_icon(self._arrow, "chevron-down", icon_size=_ARROW_ICON_SIZE)
        self._arrow.clicked.connect(self._show_menu)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(_FRAME_PX, _FRAME_PX, _FRAME_PX, _FRAME_PX)
        layout.setSpacing(0)
        layout.addWidget(self._main, stretch=1)
        layout.addWidget(self._separator)
        layout.addWidget(self._arrow)

        self.setFocusProxy(self._main)
        bind_theme(self, self.refresh_theme)

    @property
    def arrow_button(self) -> QToolButton:
        """Return the menu-arrow button."""
        return self._arrow

    def icon(self) -> QIcon:
        """Return the main-zone icon."""
        return self._main.icon()

    @property
    def main_button(self) -> QPushButton:
        """Return the primary-action button (text / icon target)."""
        return self._main

    def menu(self) -> QMenu | None:
        """Return the dropdown menu, or `None` when unset."""
        return self._menu

    def minimumSizeHint(self) -> QSize:  # noqa: N802
        """Prefer the combined main + separator + arrow width."""
        return self.sizeHint()

    def refresh_theme(self) -> None:
        """Re-apply chrome colors for the current window theme."""
        colors = split_colors(self)
        sheet = split_style(colors)
        if sheet != self.styleSheet():
            self.setStyleSheet(sheet)
            apply_lucide_button_icon(self._arrow, "chevron-down", icon_size=_ARROW_ICON_SIZE, color=colors.text)

    def setIcon(self, icon: QIcon) -> None:  # noqa: N802
        """Set the Lucide / chrome icon on the main zone."""
        self._main.setIcon(icon)

    def setIconSize(self, size: QSize) -> None:  # noqa: N802
        """Set the main-zone icon size."""
        self._main.setIconSize(size)

    def setMenu(self, menu: QMenu | None) -> None:  # noqa: N802
        """Attach the dropdown shown when the arrow is clicked."""
        self._menu = menu
        if menu is not None:
            menu.setParent(self)

    def setText(self, text: str) -> None:  # noqa: N802
        """Set the main-zone caption."""
        self._main.setText(text)

    def sizeHint(self) -> QSize:  # noqa: N802
        """Return the size of main zone plus separator and arrow."""
        main = self._main.sizeHint()
        arrow = self._arrow.sizeHint()
        height = max(main.height() + _FRAME_PX * 2, arrow.height() + _FRAME_PX * 2, _idle_push_button_height())
        width = main.width() + self._separator.width() + max(arrow.width(), _ARROW_WIDTH) + _FRAME_PX * 2
        return QSize(width, height)

    def text(self) -> str:
        """Return the main-zone caption."""
        return self._main.text()

    def _show_menu(self) -> None:
        if self._menu is None:
            return
        self._menu.exec(self._arrow.mapToGlobal(QPoint(0, self._arrow.height())))
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None, text: str = '') -> None
```

Build the split chrome with an empty optional menu.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None, text: str = "") -> None:
        super().__init__(parent)
        self.setObjectName("splitMenuButton")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, on=True)
        self.setStyleSheet(split_style(_HARRIX_COLORS))
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(_idle_push_button_height())

        self._menu: QMenu | None = None

        self._main = QPushButton(text, self)
        self._main.setObjectName("splitMenuMain")
        self._main.setCursor(Qt.CursorShape.PointingHandCursor)
        self._main.setAutoDefault(False)
        self._main.setDefault(False)
        self._main.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self._main.clicked.connect(self.clicked.emit)

        self._separator = QFrame(self)
        self._separator.setObjectName("splitMenuSeparator")
        self._separator.setFrameShape(QFrame.Shape.NoFrame)
        self._separator.setFixedWidth(1)
        self._separator.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

        self._arrow = QToolButton(self)
        self._arrow.setObjectName("splitMenuArrow")
        self._arrow.setCursor(Qt.CursorShape.PointingHandCursor)
        self._arrow.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._arrow.setAutoRaise(False)
        self._arrow.setFixedWidth(_ARROW_WIDTH)
        self._arrow.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self._arrow.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        apply_lucide_button_icon(self._arrow, "chevron-down", icon_size=_ARROW_ICON_SIZE)
        self._arrow.clicked.connect(self._show_menu)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(_FRAME_PX, _FRAME_PX, _FRAME_PX, _FRAME_PX)
        layout.setSpacing(0)
        layout.addWidget(self._main, stretch=1)
        layout.addWidget(self._separator)
        layout.addWidget(self._arrow)

        self.setFocusProxy(self._main)
        bind_theme(self, self.refresh_theme)
```

</details>

### ⚙️ Method `arrow_button (property)`

```python
def arrow_button(self) -> QToolButton
```

Return the menu-arrow button.

<details>
<summary>Code:</summary>

```python
def arrow_button(self) -> QToolButton:
        return self._arrow
```

</details>

### ⚙️ Method `icon`

```python
def icon(self) -> QIcon
```

Return the main-zone icon.

<details>
<summary>Code:</summary>

```python
def icon(self) -> QIcon:
        return self._main.icon()
```

</details>

### ⚙️ Method `main_button (property)`

```python
def main_button(self) -> QPushButton
```

Return the primary-action button (text / icon target).

<details>
<summary>Code:</summary>

```python
def main_button(self) -> QPushButton:
        return self._main
```

</details>

### ⚙️ Method `menu`

```python
def menu(self) -> QMenu | None
```

Return the dropdown menu, or `None` when unset.

<details>
<summary>Code:</summary>

```python
def menu(self) -> QMenu | None:
        return self._menu
```

</details>

### ⚙️ Method `minimumSizeHint`

```python
def minimumSizeHint(self) -> QSize
```

Prefer the combined main + separator + arrow width.

<details>
<summary>Code:</summary>

```python
def minimumSizeHint(self) -> QSize:  # noqa: N802
        return self.sizeHint()
```

</details>

### ⚙️ Method `refresh_theme`

```python
def refresh_theme(self) -> None
```

Re-apply chrome colors for the current window theme.

<details>
<summary>Code:</summary>

```python
def refresh_theme(self) -> None:
        colors = split_colors(self)
        sheet = split_style(colors)
        if sheet != self.styleSheet():
            self.setStyleSheet(sheet)
            apply_lucide_button_icon(self._arrow, "chevron-down", icon_size=_ARROW_ICON_SIZE, color=colors.text)
```

</details>

### ⚙️ Method `setIcon`

```python
def setIcon(self, icon: QIcon) -> None
```

Set the Lucide / chrome icon on the main zone.

<details>
<summary>Code:</summary>

```python
def setIcon(self, icon: QIcon) -> None:  # noqa: N802
        self._main.setIcon(icon)
```

</details>

### ⚙️ Method `setIconSize`

```python
def setIconSize(self, size: QSize) -> None
```

Set the main-zone icon size.

<details>
<summary>Code:</summary>

```python
def setIconSize(self, size: QSize) -> None:  # noqa: N802
        self._main.setIconSize(size)
```

</details>

### ⚙️ Method `setMenu`

```python
def setMenu(self, menu: QMenu | None) -> None
```

Attach the dropdown shown when the arrow is clicked.

<details>
<summary>Code:</summary>

```python
def setMenu(self, menu: QMenu | None) -> None:  # noqa: N802
        self._menu = menu
        if menu is not None:
            menu.setParent(self)
```

</details>

### ⚙️ Method `setText`

```python
def setText(self, text: str) -> None
```

Set the main-zone caption.

<details>
<summary>Code:</summary>

```python
def setText(self, text: str) -> None:  # noqa: N802
        self._main.setText(text)
```

</details>

### ⚙️ Method `sizeHint`

```python
def sizeHint(self) -> QSize
```

Return the size of main zone plus separator and arrow.

<details>
<summary>Code:</summary>

```python
def sizeHint(self) -> QSize:  # noqa: N802
        main = self._main.sizeHint()
        arrow = self._arrow.sizeHint()
        height = max(main.height() + _FRAME_PX * 2, arrow.height() + _FRAME_PX * 2, _idle_push_button_height())
        width = main.width() + self._separator.width() + max(arrow.width(), _ARROW_WIDTH) + _FRAME_PX * 2
        return QSize(width, height)
```

</details>

### ⚙️ Method `text`

```python
def text(self) -> str
```

Return the main-zone caption.

<details>
<summary>Code:</summary>

```python
def text(self) -> str:
        return self._main.text()
```

</details>

## 🔧 Function `make_lucide_split_menu_button`

```python
def make_lucide_split_menu_button(label: str, name: str, *, icon_size: int = DEFAULT_LUCIDE_BUTTON_ICON_SIZE, color: QColor | str | None = None, parent: QWidget | None = None) -> SplitMenuButton
```

Create a split menu button with a Lucide icon on the main zone.

<details>
<summary>Code:</summary>

```python
def make_lucide_split_menu_button(
    label: str,
    name: str,
    *,
    icon_size: int = DEFAULT_LUCIDE_BUTTON_ICON_SIZE,
    color: QColor | str | None = None,
    parent: QWidget | None = None,
) -> SplitMenuButton:
    button = SplitMenuButton(parent, text=label)
    apply_lucide_button_icon(button.main_button, name, icon_size=icon_size, color=color)
    return button
```

</details>

## 🔧 Function `split_colors`

```python
def split_colors(widget: QWidget | None) -> SplitColors
```

Return Fluent control colors in themed Windows and the Harrix idle chrome elsewhere.

<details>
<summary>Code:</summary>

```python
def split_colors(widget: QWidget | None) -> SplitColors:
    if not is_fluent_themed(widget):
        return _HARRIX_COLORS
    palette = palette_for(widget)
    return SplitColors(
        border=css(palette.control_stroke),
        background=css(palette.control_fill),
        hover=css(palette.control_fill),
        zone_hover=css(palette.control_fill_hover),
        pressed=css(palette.control_fill_pressed),
        text=css(palette.text_primary),
        separator=css(palette.divider),
    )
```

</details>

## 🔧 Function `split_style`

```python
def split_style(colors: SplitColors) -> str
```

Return the split button stylesheet.

The outer frame owns the border; the inner zones keep the shared padding and
min-height without a second border, so the control matches a plain button's height.

<details>
<summary>Code:</summary>

```python
def split_style(colors: SplitColors) -> str:
    return f"""
SplitMenuButton {{
    border: 1px solid {colors.border};
    border-radius: {PANEL_RADIUS}px;
    background-color: {colors.background};
}}
SplitMenuButton:hover {{
    background-color: {colors.hover};
    border-color: {colors.border};
}}
SplitMenuButton QPushButton#splitMenuMain {{
    border: none;
    background: transparent;
    color: {colors.text};
    padding: {BUTTON_PADDING};
    min-height: {BUTTON_MIN_HEIGHT_PX}px;
}}
SplitMenuButton QToolButton#splitMenuArrow {{
    border: none;
    background-color: transparent;
    color: {colors.text};
    padding: 0;
    margin: 0;
    min-height: 0;
    min-width: {_ARROW_WIDTH}px;
    max-width: {_ARROW_WIDTH}px;
}}
SplitMenuButton QPushButton#splitMenuMain:hover {{
    background-color: {colors.zone_hover};
    border-top-left-radius: {_INNER_RADIUS}px;
    border-bottom-left-radius: {_INNER_RADIUS}px;
}}
SplitMenuButton QToolButton#splitMenuArrow:hover {{
    background-color: {colors.zone_hover};
    border-top-right-radius: {_INNER_RADIUS}px;
    border-bottom-right-radius: {_INNER_RADIUS}px;
}}
SplitMenuButton QPushButton#splitMenuMain:pressed {{
    background-color: {colors.pressed};
    border-top-left-radius: {_INNER_RADIUS}px;
    border-bottom-left-radius: {_INNER_RADIUS}px;
}}
SplitMenuButton QToolButton#splitMenuArrow:pressed {{
    background-color: {colors.pressed};
    border-top-right-radius: {_INNER_RADIUS}px;
    border-bottom-right-radius: {_INNER_RADIUS}px;
}}
SplitMenuButton QFrame#splitMenuSeparator {{
    background-color: {colors.separator};
    border: none;
    max-width: 1px;
    min-width: 1px;
}}
"""
```

</details>
