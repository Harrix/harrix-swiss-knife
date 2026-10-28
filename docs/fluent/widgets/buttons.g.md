---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `buttons.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `FluentCheckBox`](#%EF%B8%8F-class-fluentcheckbox)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `refresh_theme`](#%EF%B8%8F-method-refresh_theme)
- [🏛️ Class `FluentCopyButton`](#%EF%B8%8F-class-fluentcopybutton)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-1)
  - [⚙️ Method `refresh_theme`](#%EF%B8%8F-method-refresh_theme-1)
  - [⚙️ Method `set_text_to_copy`](#%EF%B8%8F-method-set_text_to_copy)
- [🏛️ Class `FluentDropDownButton`](#%EF%B8%8F-class-fluentdropdownbutton)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-2)
  - [⚙️ Method `paintEvent`](#%EF%B8%8F-method-paintevent)
  - [⚙️ Method `refresh_theme`](#%EF%B8%8F-method-refresh_theme-2)
- [🏛️ Class `FluentHyperlinkButton`](#%EF%B8%8F-class-fluenthyperlinkbutton)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-3)
  - [⚙️ Method `refresh_theme`](#%EF%B8%8F-method-refresh_theme-3)
  - [⚙️ Method `set_url`](#%EF%B8%8F-method-set_url)
- [🏛️ Class `FluentIconButton`](#%EF%B8%8F-class-fluenticonbutton)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-4)
  - [⚙️ Method `refresh_theme`](#%EF%B8%8F-method-refresh_theme-4)
  - [⚙️ Method `set_icon_name`](#%EF%B8%8F-method-set_icon_name)
- [🏛️ Class `FluentPillButton`](#%EF%B8%8F-class-fluentpillbutton)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-5)
  - [⚙️ Method `refresh_theme`](#%EF%B8%8F-method-refresh_theme-5)
- [🏛️ Class `FluentPrimaryButton`](#%EF%B8%8F-class-fluentprimarybutton)
  - [⚙️ Method `refresh_theme`](#%EF%B8%8F-method-refresh_theme-6)
- [🏛️ Class `FluentRadioButton`](#%EF%B8%8F-class-fluentradiobutton)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-6)
  - [⚙️ Method `refresh_theme`](#%EF%B8%8F-method-refresh_theme-7)
- [🏛️ Class `FluentToggleButton`](#%EF%B8%8F-class-fluenttogglebutton)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-7)
  - [⚙️ Method `refresh_theme`](#%EF%B8%8F-method-refresh_theme-8)
- [🏛️ Class `FluentToggleSwitch`](#%EF%B8%8F-class-fluenttoggleswitch)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-8)
  - [⚙️ Method `get_knob`](#%EF%B8%8F-method-get_knob)
  - [⚙️ Method `paintEvent`](#%EF%B8%8F-method-paintevent-1)
  - [⚙️ Method `set_knob`](#%EF%B8%8F-method-set_knob)
  - [⚙️ Method `sizeHint`](#%EF%B8%8F-method-sizehint)
- [🏛️ Class `FluentToolButton`](#%EF%B8%8F-class-fluenttoolbutton)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-9)
  - [⚙️ Method `refresh_theme`](#%EF%B8%8F-method-refresh_theme-9)
- [🏛️ Class `FluentTransparentButton`](#%EF%B8%8F-class-fluenttransparentbutton)
  - [⚙️ Method `refresh_theme`](#%EF%B8%8F-method-refresh_theme-10)

</details>

## 🏛️ Class `FluentCheckBox`

```python
class FluentCheckBox(QCheckBox)
```

Checkbox using the shared Fluent indicator and Fluent text color.

<details>
<summary>Code:</summary>

```python
class FluentCheckBox(QCheckBox):

    def __init__(self, text: str = "", parent: QWidget | None = None) -> None:
        """Create a checkbox."""
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        apply_lucide_checkbox_style(self)
        bind_theme(self, self.refresh_theme)

    def refresh_theme(self) -> None:
        """Re-apply the label color."""
        palette = palette_for(self)
        self.setStyleSheet(
            f"QCheckBox {{ color: {css(palette.text_primary)}; spacing: {SPACE_S}px; background: transparent; }}"
            f"QCheckBox:disabled {{ color: {css(palette.text_disabled)}; }}",
        )
        self.update()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, text: str = '', parent: QWidget | None = None) -> None
```

Create a checkbox.

<details>
<summary>Code:</summary>

```python
def __init__(self, text: str = "", parent: QWidget | None = None) -> None:
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        apply_lucide_checkbox_style(self)
        bind_theme(self, self.refresh_theme)
```

</details>

### ⚙️ Method `refresh_theme`

```python
def refresh_theme(self) -> None
```

Re-apply the label color.

<details>
<summary>Code:</summary>

```python
def refresh_theme(self) -> None:
        palette = palette_for(self)
        self.setStyleSheet(
            f"QCheckBox {{ color: {css(palette.text_primary)}; spacing: {SPACE_S}px; background: transparent; }}"
            f"QCheckBox:disabled {{ color: {css(palette.text_disabled)}; }}",
        )
        self.update()
```

</details>

## 🏛️ Class `FluentCopyButton`

```python
class FluentCopyButton(FluentIconMixin, QToolButton)
```

Copies text to the clipboard and briefly shows a check mark.

<details>
<summary>Code:</summary>

```python
class FluentCopyButton(FluentIconMixin, QToolButton):

    copied = Signal(str)

    def __init__(self, text_to_copy: str = "", parent: QWidget | None = None, *, label: str = "") -> None:
        """Create a copy button.

        Args:

        - `text_to_copy` (`str`): Clipboard payload (see `set_text_to_copy`).
        - `parent` (`QWidget | None`): Optional parent.
        - `label` (`str`): Optional caption beside the icon.

        """
        super().__init__(parent)
        self._payload = text_to_copy
        self._icon_name = "copy"
        self.setText(label)
        self.setToolTip("Copy")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(CONTROL_HEIGHT)
        style = Qt.ToolButtonStyle.ToolButtonTextBesideIcon if label else Qt.ToolButtonStyle.ToolButtonIconOnly
        self.setToolButtonStyle(style)
        if not label:
            self.setFixedSize(CONTROL_HEIGHT, CONTROL_HEIGHT)
        self._reset = QTimer(self)
        self._reset.setSingleShot(True)
        self._reset.setInterval(_COPY_FEEDBACK_MS)
        self._reset.timeout.connect(self._restore_icon)
        self.clicked.connect(self._copy)
        bind_theme(self, self.refresh_theme)

    def refresh_theme(self) -> None:
        """Re-apply chrome and icon."""
        self.setStyleSheet(subtle_button_qss(palette_for(self), "QToolButton"))
        self._sync_icon()

    def set_text_to_copy(self, text: str) -> None:
        """Set the clipboard payload."""
        self._payload = text

    def _copy(self) -> None:
        QGuiApplication.clipboard().setText(self._payload)
        self._icon_name = "check"
        self._sync_icon()
        self._reset.start()
        self.copied.emit(self._payload)

    def _restore_icon(self) -> None:
        self._icon_name = "copy"
        self._sync_icon()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, text_to_copy: str = '', parent: QWidget | None = None, *, label: str = '') -> None
```

Create a copy button.

Args:

- `text_to_copy` (`str`): Clipboard payload (see [`set_text_to_copy`](#%EF%B8%8F-method-set_text_to_copy)).
- `parent` (`QWidget | None`): Optional parent.
- `label` (`str`): Optional caption beside the icon.

<details>
<summary>Code:</summary>

```python
def __init__(self, text_to_copy: str = "", parent: QWidget | None = None, *, label: str = "") -> None:
        super().__init__(parent)
        self._payload = text_to_copy
        self._icon_name = "copy"
        self.setText(label)
        self.setToolTip("Copy")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(CONTROL_HEIGHT)
        style = Qt.ToolButtonStyle.ToolButtonTextBesideIcon if label else Qt.ToolButtonStyle.ToolButtonIconOnly
        self.setToolButtonStyle(style)
        if not label:
            self.setFixedSize(CONTROL_HEIGHT, CONTROL_HEIGHT)
        self._reset = QTimer(self)
        self._reset.setSingleShot(True)
        self._reset.setInterval(_COPY_FEEDBACK_MS)
        self._reset.timeout.connect(self._restore_icon)
        self.clicked.connect(self._copy)
        bind_theme(self, self.refresh_theme)
```

</details>

### ⚙️ Method `refresh_theme`

```python
def refresh_theme(self) -> None
```

Re-apply chrome and icon.

<details>
<summary>Code:</summary>

```python
def refresh_theme(self) -> None:
        self.setStyleSheet(subtle_button_qss(palette_for(self), "QToolButton"))
        self._sync_icon()
```

</details>

### ⚙️ Method `set_text_to_copy`

```python
def set_text_to_copy(self, text: str) -> None
```

Set the clipboard payload.

<details>
<summary>Code:</summary>

```python
def set_text_to_copy(self, text: str) -> None:
        self._payload = text
```

</details>

## 🏛️ Class `FluentDropDownButton`

```python
class FluentDropDownButton(FluentPushButton)
```

Button that opens a menu from anywhere on its face.

<details>
<summary>Code:</summary>

```python
class FluentDropDownButton(FluentPushButton):

    def __init__(
        self, text: str = "", parent: QWidget | None = None, *, icon: str = "", menu: QMenu | None = None
    ) -> None:
        """Create a drop-down button.

        Args:

        - `text` (`str`): Caption.
        - `parent` (`QWidget | None`): Optional parent.
        - `icon` (`str`): Optional Lucide icon ID.
        - `menu` (`QMenu | None`): Menu shown on click.

        """
        super().__init__(text, parent, icon=icon)
        if menu is not None:
            self.setMenu(menu)

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802
        """Paint the button, then a chevron on the right."""
        super().paintEvent(event)
        palette = palette_for(self)
        icon = themed_icon("chevron-down", palette, palette.text_secondary, 12)
        side = 12
        x = self.width() - side - SPACE_S - 2
        y = (self.height() - side) // 2
        painter = antialiased_painter(self)
        icon.paint(painter, x, y, side, side)
        painter.end()

    def refresh_theme(self) -> None:
        """Re-apply chrome and hide Qt's native menu indicator."""
        self.setStyleSheet(
            push_button_qss(palette_for(self))
            + "QPushButton { padding-right: 28px; } QPushButton::menu-indicator { image: none; width: 0px; }",
        )
        self._sync_icon()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, text: str = '', parent: QWidget | None = None, *, icon: str = '', menu: QMenu | None = None) -> None
```

Create a drop-down button.

Args:

- `text` (`str`): Caption.
- `parent` (`QWidget | None`): Optional parent.
- [`icon`](../../qt_split_menu_button.g.md#%EF%B8%8F-method-icon) (`str`): Optional Lucide icon ID.
- [`menu`](../../qt_split_menu_button.g.md#%EF%B8%8F-method-menu) (`QMenu | None`): Menu shown on click.

<details>
<summary>Code:</summary>

```python
def __init__(
        self, text: str = "", parent: QWidget | None = None, *, icon: str = "", menu: QMenu | None = None
    ) -> None:
        super().__init__(text, parent, icon=icon)
        if menu is not None:
            self.setMenu(menu)
```

</details>

### ⚙️ Method `paintEvent`

```python
def paintEvent(self, event: QPaintEvent) -> None
```

Paint the button, then a chevron on the right.

<details>
<summary>Code:</summary>

```python
def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802
        super().paintEvent(event)
        palette = palette_for(self)
        icon = themed_icon("chevron-down", palette, palette.text_secondary, 12)
        side = 12
        x = self.width() - side - SPACE_S - 2
        y = (self.height() - side) // 2
        painter = antialiased_painter(self)
        icon.paint(painter, x, y, side, side)
        painter.end()
```

</details>

### ⚙️ Method `refresh_theme`

```python
def refresh_theme(self) -> None
```

Re-apply chrome and hide Qt's native menu indicator.

<details>
<summary>Code:</summary>

```python
def refresh_theme(self) -> None:
        self.setStyleSheet(
            push_button_qss(palette_for(self))
            + "QPushButton { padding-right: 28px; } QPushButton::menu-indicator { image: none; width: 0px; }",
        )
        self._sync_icon()
```

</details>

## 🏛️ Class `FluentHyperlinkButton`

```python
class FluentHyperlinkButton(FluentPushButton)
```

Text button in the accent color that opens a URL.

<details>
<summary>Code:</summary>

```python
class FluentHyperlinkButton(FluentPushButton):

    def __init__(self, text: str, url: str = "", parent: QWidget | None = None) -> None:
        """Create a hyperlink button.

        Args:

        - `text` (`str`): Caption.
        - `url` (`str`): URL opened on click (empty: only `clicked` is emitted).
        - `parent` (`QWidget | None`): Optional parent.

        """
        super().__init__(text, parent)
        self._url = url
        self.clicked.connect(self._open_url)

    def refresh_theme(self) -> None:
        """Re-apply hyperlink chrome."""
        palette = palette_for(self)
        self.setStyleSheet(
            subtle_button_qss(palette, "QPushButton") + f"QPushButton {{ color: {css(palette.accent_text)}; }}",
        )

    def set_url(self, url: str) -> None:
        """Set the URL opened on click."""
        self._url = url

    def _open_url(self) -> None:
        if self._url:
            QDesktopServices.openUrl(QUrl(self._url))
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, text: str, url: str = '', parent: QWidget | None = None) -> None
```

Create a hyperlink button.

Args:

- `text` (`str`): Caption.
- `url` (`str`): URL opened on click (empty: only `clicked` is emitted).
- `parent` (`QWidget | None`): Optional parent.

<details>
<summary>Code:</summary>

```python
def __init__(self, text: str, url: str = "", parent: QWidget | None = None) -> None:
        super().__init__(text, parent)
        self._url = url
        self.clicked.connect(self._open_url)
```

</details>

### ⚙️ Method `refresh_theme`

```python
def refresh_theme(self) -> None
```

Re-apply hyperlink chrome.

<details>
<summary>Code:</summary>

```python
def refresh_theme(self) -> None:
        palette = palette_for(self)
        self.setStyleSheet(
            subtle_button_qss(palette, "QPushButton") + f"QPushButton {{ color: {css(palette.accent_text)}; }}",
        )
```

</details>

### ⚙️ Method `set_url`

```python
def set_url(self, url: str) -> None
```

Set the URL opened on click.

<details>
<summary>Code:</summary>

```python
def set_url(self, url: str) -> None:
        self._url = url
```

</details>

## 🏛️ Class `FluentIconButton`

```python
class FluentIconButton(FluentIconMixin, QToolButton)
```

Square subtle button that shows only a Lucide icon.

<details>
<summary>Code:</summary>

```python
class FluentIconButton(FluentIconMixin, QToolButton):

    def __init__(self, icon: str, parent: QWidget | None = None, *, tooltip: str = "") -> None:
        """Create an icon button.

        Args:

        - `icon` (`str`): Lucide icon ID.
        - `parent` (`QWidget | None`): Optional parent.
        - `tooltip` (`str`): Tooltip and accessible name.

        """
        super().__init__(parent)
        self._icon_name = icon
        self.setToolTip(tooltip)
        self.setAccessibleName(tooltip or icon)
        self.setFixedSize(CONTROL_HEIGHT, CONTROL_HEIGHT)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAutoRaise(True)
        bind_theme(self, self.refresh_theme)

    def refresh_theme(self) -> None:
        """Re-apply subtle chrome and icon color."""
        self.setStyleSheet(subtle_button_qss(palette_for(self), "QToolButton") + "QToolButton { padding: 0px; }")
        self._sync_icon()

    def set_icon_name(self, name: str) -> None:
        """Switch the Lucide icon."""
        self._icon_name = name
        self._sync_icon()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, icon: str, parent: QWidget | None = None, *, tooltip: str = '') -> None
```

Create an icon button.

Args:

- [`icon`](../../qt_split_menu_button.g.md#%EF%B8%8F-method-icon) (`str`): Lucide icon ID.
- `parent` (`QWidget | None`): Optional parent.
- `tooltip` (`str`): Tooltip and accessible name.

<details>
<summary>Code:</summary>

```python
def __init__(self, icon: str, parent: QWidget | None = None, *, tooltip: str = "") -> None:
        super().__init__(parent)
        self._icon_name = icon
        self.setToolTip(tooltip)
        self.setAccessibleName(tooltip or icon)
        self.setFixedSize(CONTROL_HEIGHT, CONTROL_HEIGHT)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAutoRaise(True)
        bind_theme(self, self.refresh_theme)
```

</details>

### ⚙️ Method `refresh_theme`

```python
def refresh_theme(self) -> None
```

Re-apply subtle chrome and icon color.

<details>
<summary>Code:</summary>

```python
def refresh_theme(self) -> None:
        self.setStyleSheet(subtle_button_qss(palette_for(self), "QToolButton") + "QToolButton { padding: 0px; }")
        self._sync_icon()
```

</details>

### ⚙️ Method `set_icon_name`

```python
def set_icon_name(self, name: str) -> None
```

Switch the Lucide icon.

<details>
<summary>Code:</summary>

```python
def set_icon_name(self, name: str) -> None:
        self._icon_name = name
        self._sync_icon()
```

</details>

## 🏛️ Class `FluentPillButton`

```python
class FluentPillButton(FluentPushButton)
```

Checkable rounded pill (filter chip).

<details>
<summary>Code:</summary>

```python
class FluentPillButton(FluentPushButton):

    def __init__(self, text: str = "", parent: QWidget | None = None, *, icon: str = "") -> None:
        """Create a checkable pill button."""
        super().__init__(text, parent, icon=icon)
        self.setCheckable(True)

    def refresh_theme(self) -> None:
        """Re-apply pill chrome."""
        radius = CONTROL_HEIGHT // 2
        self.setStyleSheet(push_button_qss(palette_for(self)) + f"QPushButton {{ border-radius: {radius}px; }}")
        self._sync_icon()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, text: str = '', parent: QWidget | None = None, *, icon: str = '') -> None
```

Create a checkable pill button.

<details>
<summary>Code:</summary>

```python
def __init__(self, text: str = "", parent: QWidget | None = None, *, icon: str = "") -> None:
        super().__init__(text, parent, icon=icon)
        self.setCheckable(True)
```

</details>

### ⚙️ Method `refresh_theme`

```python
def refresh_theme(self) -> None
```

Re-apply pill chrome.

<details>
<summary>Code:</summary>

```python
def refresh_theme(self) -> None:
        radius = CONTROL_HEIGHT // 2
        self.setStyleSheet(push_button_qss(palette_for(self)) + f"QPushButton {{ border-radius: {radius}px; }}")
        self._sync_icon()
```

</details>

## 🏛️ Class `FluentPrimaryButton`

```python
class FluentPrimaryButton(FluentPushButton)
```

Accent-filled button for the main action of a view.

<details>
<summary>Code:</summary>

```python
class FluentPrimaryButton(FluentPushButton):

    _icon_on_accent = True

    def refresh_theme(self) -> None:
        """Re-apply accent chrome."""
        self.setStyleSheet(accent_button_qss(palette_for(self)))
        self._sync_icon()
```

</details>

### ⚙️ Method `refresh_theme`

```python
def refresh_theme(self) -> None
```

Re-apply accent chrome.

<details>
<summary>Code:</summary>

```python
def refresh_theme(self) -> None:
        self.setStyleSheet(accent_button_qss(palette_for(self)))
        self._sync_icon()
```

</details>

## 🏛️ Class `FluentRadioButton`

```python
class FluentRadioButton(QRadioButton)
```

Radio button using the shared Fluent indicator and Fluent text color.

<details>
<summary>Code:</summary>

```python
class FluentRadioButton(QRadioButton):

    def __init__(self, text: str = "", parent: QWidget | None = None) -> None:
        """Create a radio button."""
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        apply_lucide_radio_style(self)
        bind_theme(self, self.refresh_theme)

    def refresh_theme(self) -> None:
        """Re-apply the label color."""
        palette = palette_for(self)
        self.setStyleSheet(
            f"QRadioButton {{ color: {css(palette.text_primary)}; spacing: {SPACE_S}px; background: transparent; }}"
            f"QRadioButton:disabled {{ color: {css(palette.text_disabled)}; }}",
        )
        self.update()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, text: str = '', parent: QWidget | None = None) -> None
```

Create a radio button.

<details>
<summary>Code:</summary>

```python
def __init__(self, text: str = "", parent: QWidget | None = None) -> None:
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        apply_lucide_radio_style(self)
        bind_theme(self, self.refresh_theme)
```

</details>

### ⚙️ Method `refresh_theme`

```python
def refresh_theme(self) -> None
```

Re-apply the label color.

<details>
<summary>Code:</summary>

```python
def refresh_theme(self) -> None:
        palette = palette_for(self)
        self.setStyleSheet(
            f"QRadioButton {{ color: {css(palette.text_primary)}; spacing: {SPACE_S}px; background: transparent; }}"
            f"QRadioButton:disabled {{ color: {css(palette.text_disabled)}; }}",
        )
        self.update()
```

</details>

## 🏛️ Class `FluentToggleButton`

```python
class FluentToggleButton(FluentPushButton)
```

Button that toggles between rest and accent (checked) states.

<details>
<summary>Code:</summary>

```python
class FluentToggleButton(FluentPushButton):

    def __init__(self, text: str = "", parent: QWidget | None = None, *, icon: str = "") -> None:
        """Create a toggle button."""
        super().__init__(text, parent, icon=icon)
        self.setCheckable(True)
        self.toggled.connect(lambda _checked: self._sync_toggle_icon())

    def refresh_theme(self) -> None:
        """Re-apply chrome; the icon follows the checked fill."""
        self.setStyleSheet(push_button_qss(palette_for(self)))
        self._sync_toggle_icon()

    def _sync_toggle_icon(self) -> None:
        self._icon_on_accent = self.isChecked()
        self._sync_icon()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, text: str = '', parent: QWidget | None = None, *, icon: str = '') -> None
```

Create a toggle button.

<details>
<summary>Code:</summary>

```python
def __init__(self, text: str = "", parent: QWidget | None = None, *, icon: str = "") -> None:
        super().__init__(text, parent, icon=icon)
        self.setCheckable(True)
        self.toggled.connect(lambda _checked: self._sync_toggle_icon())
```

</details>

### ⚙️ Method `refresh_theme`

```python
def refresh_theme(self) -> None
```

Re-apply chrome; the icon follows the checked fill.

<details>
<summary>Code:</summary>

```python
def refresh_theme(self) -> None:
        self.setStyleSheet(push_button_qss(palette_for(self)))
        self._sync_toggle_icon()
```

</details>

## 🏛️ Class `FluentToggleSwitch`

```python
class FluentToggleSwitch(QAbstractButton)
```

Animated on/off switch with an optional label on the right.

<details>
<summary>Code:</summary>

```python
class FluentToggleSwitch(QAbstractButton):

    def __init__(self, parent: QWidget | None = None, *, on_text: str = "On", off_text: str = "Off") -> None:
        """Create a toggle switch.

        Args:

        - `parent` (`QWidget | None`): Optional parent.
        - `on_text` (`str`): Label while checked (empty hides it).
        - `off_text` (`str`): Label while unchecked.

        """
        super().__init__(parent)
        self._on_text = on_text
        self._off_text = off_text
        self._knob = 0.0
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self._animation = QVariantAnimation(self)
        self._animation.valueChanged.connect(lambda value: self.set_knob(float(value)))
        self._animation.setDuration(ANIMATION_NORMAL)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.toggled.connect(self._animate)
        bind_theme(self, self.update)

    def get_knob(self) -> float:
        """Return the knob position (`0.0` off, `1.0` on)."""
        return self._knob

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Paint the track, knob, and label."""
        palette = palette_for(self)
        painter = antialiased_painter(self)
        track = QRectF(
            0.5, (self.height() - TOGGLE_SWITCH_HEIGHT) / 2 + 0.5, TOGGLE_SWITCH_WIDTH - 1, TOGGLE_SWITCH_HEIGHT - 1
        )
        on = self._knob > 0.5  # noqa: PLR2004
        hovered = self.underMouse()
        if not self.isEnabled():
            fill = palette.accent_disabled if on else None
            stroke = palette.text_disabled
            knob_color = palette.text_on_accent if on else palette.text_disabled
        elif on:
            fill = palette.accent_hover if hovered else palette.accent
            stroke = None
            knob_color = palette.text_on_accent
        else:
            fill = palette.control_alt_fill if hovered else None
            stroke = palette.control_strong_stroke
            knob_color = palette.text_secondary
        paint_surface(painter, track, fill, stroke, track.height() / 2)
        knob_size = 12 if not hovered else 14
        travel = TOGGLE_SWITCH_WIDTH - 8 - knob_size
        knob_x = track.left() + 3.5 + travel * self._knob
        knob = QRectF(knob_x, track.center().y() - knob_size / 2, knob_size, knob_size)
        paint_surface(painter, knob, knob_color, None, knob_size / 2)
        text = self._on_text if self.isChecked() else self._off_text
        if text:
            painter.setPen(palette.text_primary if self.isEnabled() else palette.text_disabled)
            text_rect = QRectF(
                TOGGLE_SWITCH_WIDTH + SPACE_S, 0, self.width() - TOGGLE_SWITCH_WIDTH - SPACE_S, self.height()
            )
            painter.drawText(text_rect, int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft), text)
        painter.end()

    def set_knob(self, value: float) -> None:
        """Move the knob (animation property)."""
        self._knob = value
        self.update()

    def sizeHint(self) -> QSize:  # noqa: N802
        """Return the track width plus the widest label."""
        metrics = QFontMetrics(self.font())
        labels = [text for text in (self._on_text, self._off_text) if text]
        text_width = max((metrics.horizontalAdvance(text) for text in labels), default=0)
        extra = SPACE_S + text_width if labels else 0
        return QSize(TOGGLE_SWITCH_WIDTH + extra, CONTROL_HEIGHT)

    def _animate(self, checked: bool) -> None:  # noqa: FBT001
        self._animation.stop()
        self._animation.setStartValue(self._knob)
        self._animation.setEndValue(1.0 if checked else 0.0)
        self._animation.start()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None, *, on_text: str = 'On', off_text: str = 'Off') -> None
```

Create a toggle switch.

Args:

- `parent` (`QWidget | None`): Optional parent.
- `on_text` (`str`): Label while checked (empty hides it).
- `off_text` (`str`): Label while unchecked.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None, *, on_text: str = "On", off_text: str = "Off") -> None:
        super().__init__(parent)
        self._on_text = on_text
        self._off_text = off_text
        self._knob = 0.0
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self._animation = QVariantAnimation(self)
        self._animation.valueChanged.connect(lambda value: self.set_knob(float(value)))
        self._animation.setDuration(ANIMATION_NORMAL)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.toggled.connect(self._animate)
        bind_theme(self, self.update)
```

</details>

### ⚙️ Method `get_knob`

```python
def get_knob(self) -> float
```

Return the knob position (`0.0` off, `1.0` on).

<details>
<summary>Code:</summary>

```python
def get_knob(self) -> float:
        return self._knob
```

</details>

### ⚙️ Method `paintEvent`

```python
def paintEvent(self, _event: QPaintEvent) -> None
```

Paint the track, knob, and label.

<details>
<summary>Code:</summary>

```python
def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        palette = palette_for(self)
        painter = antialiased_painter(self)
        track = QRectF(
            0.5, (self.height() - TOGGLE_SWITCH_HEIGHT) / 2 + 0.5, TOGGLE_SWITCH_WIDTH - 1, TOGGLE_SWITCH_HEIGHT - 1
        )
        on = self._knob > 0.5  # noqa: PLR2004
        hovered = self.underMouse()
        if not self.isEnabled():
            fill = palette.accent_disabled if on else None
            stroke = palette.text_disabled
            knob_color = palette.text_on_accent if on else palette.text_disabled
        elif on:
            fill = palette.accent_hover if hovered else palette.accent
            stroke = None
            knob_color = palette.text_on_accent
        else:
            fill = palette.control_alt_fill if hovered else None
            stroke = palette.control_strong_stroke
            knob_color = palette.text_secondary
        paint_surface(painter, track, fill, stroke, track.height() / 2)
        knob_size = 12 if not hovered else 14
        travel = TOGGLE_SWITCH_WIDTH - 8 - knob_size
        knob_x = track.left() + 3.5 + travel * self._knob
        knob = QRectF(knob_x, track.center().y() - knob_size / 2, knob_size, knob_size)
        paint_surface(painter, knob, knob_color, None, knob_size / 2)
        text = self._on_text if self.isChecked() else self._off_text
        if text:
            painter.setPen(palette.text_primary if self.isEnabled() else palette.text_disabled)
            text_rect = QRectF(
                TOGGLE_SWITCH_WIDTH + SPACE_S, 0, self.width() - TOGGLE_SWITCH_WIDTH - SPACE_S, self.height()
            )
            painter.drawText(text_rect, int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft), text)
        painter.end()
```

</details>

### ⚙️ Method `set_knob`

```python
def set_knob(self, value: float) -> None
```

Move the knob (animation property).

<details>
<summary>Code:</summary>

```python
def set_knob(self, value: float) -> None:
        self._knob = value
        self.update()
```

</details>

### ⚙️ Method `sizeHint`

```python
def sizeHint(self) -> QSize
```

Return the track width plus the widest label.

<details>
<summary>Code:</summary>

```python
def sizeHint(self) -> QSize:  # noqa: N802
        metrics = QFontMetrics(self.font())
        labels = [text for text in (self._on_text, self._off_text) if text]
        text_width = max((metrics.horizontalAdvance(text) for text in labels), default=0)
        extra = SPACE_S + text_width if labels else 0
        return QSize(TOGGLE_SWITCH_WIDTH + extra, CONTROL_HEIGHT)
```

</details>

## 🏛️ Class `FluentToolButton`

```python
class FluentToolButton(FluentIconMixin, QToolButton)
```

Subtle tool button with icon, optional text, and an optional instant menu.

<details>
<summary>Code:</summary>

```python
class FluentToolButton(FluentIconMixin, QToolButton):

    def __init__(
        self,
        text: str = "",
        parent: QWidget | None = None,
        *,
        icon: str = "",
        menu: QMenu | None = None,
    ) -> None:
        """Create a tool button.

        Args:

        - `text` (`str`): Caption beside the icon.
        - `parent` (`QWidget | None`): Optional parent.
        - `icon` (`str`): Lucide icon ID.
        - `menu` (`QMenu | None`): Menu shown instantly on click.

        """
        super().__init__(parent)
        self._icon_name = icon
        self.setText(text)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAutoRaise(True)
        self.setMinimumHeight(CONTROL_HEIGHT)
        style = Qt.ToolButtonStyle.ToolButtonTextBesideIcon if text else Qt.ToolButtonStyle.ToolButtonIconOnly
        self.setToolButtonStyle(style)
        if menu is not None:
            self.setMenu(menu)
            self.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        bind_theme(self, self.refresh_theme)

    def refresh_theme(self) -> None:
        """Re-apply subtle chrome."""
        self.setStyleSheet(
            subtle_button_qss(palette_for(self), "QToolButton") + "QToolButton::menu-indicator { image: none; }",
        )
        self._sync_icon()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, text: str = '', parent: QWidget | None = None, *, icon: str = '', menu: QMenu | None = None) -> None
```

Create a tool button.

Args:

- `text` (`str`): Caption beside the icon.
- `parent` (`QWidget | None`): Optional parent.
- [`icon`](../../qt_split_menu_button.g.md#%EF%B8%8F-method-icon) (`str`): Lucide icon ID.
- [`menu`](../../qt_split_menu_button.g.md#%EF%B8%8F-method-menu) (`QMenu | None`): Menu shown instantly on click.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        text: str = "",
        parent: QWidget | None = None,
        *,
        icon: str = "",
        menu: QMenu | None = None,
    ) -> None:
        super().__init__(parent)
        self._icon_name = icon
        self.setText(text)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAutoRaise(True)
        self.setMinimumHeight(CONTROL_HEIGHT)
        style = Qt.ToolButtonStyle.ToolButtonTextBesideIcon if text else Qt.ToolButtonStyle.ToolButtonIconOnly
        self.setToolButtonStyle(style)
        if menu is not None:
            self.setMenu(menu)
            self.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        bind_theme(self, self.refresh_theme)
```

</details>

### ⚙️ Method `refresh_theme`

```python
def refresh_theme(self) -> None
```

Re-apply subtle chrome.

<details>
<summary>Code:</summary>

```python
def refresh_theme(self) -> None:
        self.setStyleSheet(
            subtle_button_qss(palette_for(self), "QToolButton") + "QToolButton::menu-indicator { image: none; }",
        )
        self._sync_icon()
```

</details>

## 🏛️ Class `FluentTransparentButton`

```python
class FluentTransparentButton(FluentPushButton)
```

Subtle button without a fill until hovered.

<details>
<summary>Code:</summary>

```python
class FluentTransparentButton(FluentPushButton):

    def refresh_theme(self) -> None:
        """Re-apply subtle chrome."""
        self.setStyleSheet(subtle_button_qss(palette_for(self), "QPushButton"))
        self._sync_icon()
```

</details>

### ⚙️ Method `refresh_theme`

```python
def refresh_theme(self) -> None
```

Re-apply subtle chrome.

<details>
<summary>Code:</summary>

```python
def refresh_theme(self) -> None:
        self.setStyleSheet(subtle_button_qss(palette_for(self), "QPushButton"))
        self._sync_icon()
```

</details>
