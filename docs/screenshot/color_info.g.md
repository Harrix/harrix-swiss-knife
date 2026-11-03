---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `color_info.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `EyedropperColorDialog`](#%EF%B8%8F-class-eyedroppercolordialog)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `set_color`](#%EF%B8%8F-method-set_color)
  - [⚙️ Method `show_color`](#%EF%B8%8F-method-show_color)
- [🔧 Function `color_clipboard_formats`](#-function-color_clipboard_formats)

</details>

## 🏛️ Class `EyedropperColorDialog`

```python
class EyedropperColorDialog(QDialog)
```

Window of copyable color formats after an eyedropper pick.

<details>
<summary>Code:</summary>

```python
class EyedropperColorDialog(QDialog):

    def __init__(self, parent: QWidget | None = None) -> None:
        """Build an empty formats window. Call `show_color` to fill and display it."""
        super().__init__(parent)
        self.setWindowTitle("Color")
        self.setObjectName("eyedropper_color_dialog")
        self.setWindowModality(Qt.WindowModality.NonModal)
        self._anchored = False
        self._edits: dict[str, QLineEdit] = {}
        self._copy_buttons: dict[str, FluentCopyButton] = {}

        root = QVBoxLayout(self)
        root.setContentsMargins(SPACE_M, SPACE_M, SPACE_M, SPACE_M)
        root.setSpacing(SPACE_S)

        header = QHBoxLayout()
        header.setSpacing(SPACE_S)
        self._swatch = QLabel(self)
        self._swatch.setFixedSize(_SWATCH_SIZE, _SWATCH_SIZE)
        header.addWidget(self._swatch, 0, Qt.AlignmentFlag.AlignTop)
        titles = QVBoxLayout()
        titles.setSpacing(SPACE_XS // 2)
        self._headline = QLabel("Picked color", self)
        headline_font = self._headline.font()
        headline_font.setBold(True)
        self._headline.setFont(headline_font)
        self._status = QLabel(self)
        self._status.setObjectName("color_copy_status")
        self._status.setWordWrap(True)
        titles.addWidget(self._headline)
        titles.addWidget(self._status)
        titles.addStretch(1)
        header.addLayout(titles, 1)
        root.addLayout(header)

        grid = QGridLayout()
        grid.setHorizontalSpacing(SPACE_XS)
        grid.setVerticalSpacing(SPACE_XS)
        grid.setColumnStretch(1, 1)
        for row, label in enumerate(COLOR_FORMAT_LABELS):
            name = QLabel(label, self)
            name.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            edit = QLineEdit(self)
            edit.setReadOnly(True)
            edit.setFont(mono_qfont())
            edit.setObjectName(f"value_{label}")
            edit.setMinimumWidth(220)
            button = FluentCopyButton(parent=self)
            button.setObjectName(f"copy_{label}")
            button.setToolTip(f"Copy {label} to clipboard")
            button.copied.connect(lambda text, name=label, field=edit: self._on_copied(name, field, text))
            self._edits[label] = edit
            self._copy_buttons[label] = button
            grid.addWidget(name, row, 0)
            grid.addWidget(edit, row, 1)
            grid.addWidget(button, row, 2)
        root.addLayout(grid)

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        close = FluentPushButton("Close", self, icon=CLOSE_BUTTON_ICON)
        close.setAutoDefault(False)
        close.setDefault(False)
        close.clicked.connect(self.hide)
        buttons.addWidget(close)
        root.addLayout(buttons)
        bind_theme(self._status, self._refresh_status_theme)
        self._refresh_status_theme()
        install_fluent_dialog_chrome(self)

    def set_color(self, color: QColor) -> None:
        """Fill the format fields and swatch from `color`."""
        if not color.isValid():
            return
        values = dict(color_clipboard_formats(color))
        for label, edit in self._edits.items():
            text = values.get(label, "")
            edit.setText(text)
            edit.deselect()
            edit.setCursorPosition(0)
            self._copy_buttons[label].set_text_to_copy(text)
        self._swatch.setPixmap(_swatch_pixmap(color, _SWATCH_SIZE))
        self._headline.setText(values.get("HEX", "Picked color"))

    def show_color(self, color: QColor) -> None:
        """Show `color`. HEX is already on the clipboard."""
        if not color.isValid():
            return
        self.set_color(color)
        self._status.setText("HEX copied to clipboard")
        place = not self._anchored
        self.show()
        self.adjustSize()
        if place:
            self._center_on_parent()
            self._anchored = True
        self.raise_()
        self.activateWindow()

    def _center_on_parent(self) -> None:
        parent = self.parentWidget()
        if parent is None:
            return
        frame = self.frameGeometry()
        frame.moveCenter(parent.frameGeometry().center())
        self.move(frame.topLeft())

    def _on_copied(self, label: str, edit: QLineEdit, text: str) -> None:
        edit.selectAll()
        self._status.setText(f"Copied {text}" if text else f"Copied {label}")

    def _refresh_status_theme(self) -> None:
        palette = palette_for(self)
        self._status.setStyleSheet(f"color: {css(palette.text_secondary)};")
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Build an empty formats window. Call [`show_color`](#%EF%B8%8F-method-show_color) to fill and display it.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Color")
        self.setObjectName("eyedropper_color_dialog")
        self.setWindowModality(Qt.WindowModality.NonModal)
        self._anchored = False
        self._edits: dict[str, QLineEdit] = {}
        self._copy_buttons: dict[str, FluentCopyButton] = {}

        root = QVBoxLayout(self)
        root.setContentsMargins(SPACE_M, SPACE_M, SPACE_M, SPACE_M)
        root.setSpacing(SPACE_S)

        header = QHBoxLayout()
        header.setSpacing(SPACE_S)
        self._swatch = QLabel(self)
        self._swatch.setFixedSize(_SWATCH_SIZE, _SWATCH_SIZE)
        header.addWidget(self._swatch, 0, Qt.AlignmentFlag.AlignTop)
        titles = QVBoxLayout()
        titles.setSpacing(SPACE_XS // 2)
        self._headline = QLabel("Picked color", self)
        headline_font = self._headline.font()
        headline_font.setBold(True)
        self._headline.setFont(headline_font)
        self._status = QLabel(self)
        self._status.setObjectName("color_copy_status")
        self._status.setWordWrap(True)
        titles.addWidget(self._headline)
        titles.addWidget(self._status)
        titles.addStretch(1)
        header.addLayout(titles, 1)
        root.addLayout(header)

        grid = QGridLayout()
        grid.setHorizontalSpacing(SPACE_XS)
        grid.setVerticalSpacing(SPACE_XS)
        grid.setColumnStretch(1, 1)
        for row, label in enumerate(COLOR_FORMAT_LABELS):
            name = QLabel(label, self)
            name.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            edit = QLineEdit(self)
            edit.setReadOnly(True)
            edit.setFont(mono_qfont())
            edit.setObjectName(f"value_{label}")
            edit.setMinimumWidth(220)
            button = FluentCopyButton(parent=self)
            button.setObjectName(f"copy_{label}")
            button.setToolTip(f"Copy {label} to clipboard")
            button.copied.connect(lambda text, name=label, field=edit: self._on_copied(name, field, text))
            self._edits[label] = edit
            self._copy_buttons[label] = button
            grid.addWidget(name, row, 0)
            grid.addWidget(edit, row, 1)
            grid.addWidget(button, row, 2)
        root.addLayout(grid)

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        close = FluentPushButton("Close", self, icon=CLOSE_BUTTON_ICON)
        close.setAutoDefault(False)
        close.setDefault(False)
        close.clicked.connect(self.hide)
        buttons.addWidget(close)
        root.addLayout(buttons)
        bind_theme(self._status, self._refresh_status_theme)
        self._refresh_status_theme()
        install_fluent_dialog_chrome(self)
```

</details>

### ⚙️ Method `set_color`

```python
def set_color(self, color: QColor) -> None
```

Fill the format fields and swatch from [`color`](../fluent/widgets/dialogs.g.md#%EF%B8%8F-method-color).

<details>
<summary>Code:</summary>

```python
def set_color(self, color: QColor) -> None:
        if not color.isValid():
            return
        values = dict(color_clipboard_formats(color))
        for label, edit in self._edits.items():
            text = values.get(label, "")
            edit.setText(text)
            edit.deselect()
            edit.setCursorPosition(0)
            self._copy_buttons[label].set_text_to_copy(text)
        self._swatch.setPixmap(_swatch_pixmap(color, _SWATCH_SIZE))
        self._headline.setText(values.get("HEX", "Picked color"))
```

</details>

### ⚙️ Method `show_color`

```python
def show_color(self, color: QColor) -> None
```

Show [`color`](../fluent/widgets/dialogs.g.md#%EF%B8%8F-method-color). HEX is already on the clipboard.

<details>
<summary>Code:</summary>

```python
def show_color(self, color: QColor) -> None:
        if not color.isValid():
            return
        self.set_color(color)
        self._status.setText("HEX copied to clipboard")
        place = not self._anchored
        self.show()
        self.adjustSize()
        if place:
            self._center_on_parent()
            self._anchored = True
        self.raise_()
        self.activateWindow()
```

</details>

## 🔧 Function `color_clipboard_formats`

```python
def color_clipboard_formats(color: QColor) -> tuple[tuple[str, str], ...]
```

Return `(label, clipboard text)` pairs for [`color`](../fluent/widgets/dialogs.g.md#%EF%B8%8F-method-color).

HEX matches `QColor.name()` (`#rrggbb`). RGB, HSL, HSV, CMYK, and RGBA follow.

<details>
<summary>Code:</summary>

```python
def color_clipboard_formats(color: QColor) -> tuple[tuple[str, str], ...]:
    red = color.red()
    green = color.green()
    blue = color.blue()
    values = {
        "HEX": color.name(QColor.NameFormat.HexRgb),
        "RGB": f"rgb({red}, {green}, {blue})",
        "HSL": (
            f"hsl({_hue_degrees(color.hslHue())}, {_channel_percent(color.hslSaturation())}%, "
            f"{_channel_percent(color.lightness())}%)"
        ),
        "HSV": (
            f"hsv({_hue_degrees(color.hsvHue())}, {_channel_percent(color.hsvSaturation())}%, "
            f"{_channel_percent(color.value())}%)"
        ),
        "CMYK": (
            f"cmyk({_channel_percent(color.cyan())}%, {_channel_percent(color.magenta())}%, "
            f"{_channel_percent(color.yellow())}%, {_channel_percent(color.black())}%)"
        ),
        "RGBA": f"rgba({red}, {green}, {blue}, {_css_alpha(color.alpha())})",
    }
    return tuple((label, values[label]) for label in COLOR_FORMAT_LABELS)
```

</details>
