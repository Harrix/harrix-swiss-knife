---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `text_toolbar.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ScreenshotTextToolbar`](#%EF%B8%8F-class-screenshottexttoolbar)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `set_color`](#%EF%B8%8F-method-set_color)
  - [⚙️ Method `set_settings`](#%EF%B8%8F-method-set_settings)
  - [⚙️ Method `settings`](#%EF%B8%8F-method-settings)

</details>

## 🏛️ Class `ScreenshotTextToolbar`

```python
class ScreenshotTextToolbar(QWidget)
```

Compact font / style strip shown while the text tool is active.

<details>
<summary>Code:</summary>

```python
class ScreenshotTextToolbar(QWidget):

    settings_changed = Signal(object)

    def __init__(self, parent: QWidget | None = None) -> None:
        """Build combos and toggles; call `set_settings` before showing."""
        super().__init__(parent)
        self._updating = False
        self._settings = ScreenshotTextSettings()
        self.setObjectName("hskScreenshotTextToolbar")
        self.setStyleSheet(
            "#hskScreenshotTextToolbar {  background: #f7f7f8;  border: 1px solid #d0d0d4;  border-radius: 10px;}"
        )

        row = QHBoxLayout(self)
        row.setContentsMargins(10, 6, 10, 6)
        row.setSpacing(8)

        self._family = QComboBox(self)
        self._family.setMinimumWidth(100)
        self._family.setMaximumWidth(140)
        self._family.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        for name in available_text_font_families():
            self._family.addItem(name)
        self._family.currentTextChanged.connect(self._on_family_changed)
        row.addWidget(self._family)

        self._size = QComboBox(self)
        self._size.setEditable(True)
        self._size.setMinimumWidth(64)
        for size in font_size_choices():
            self._size.addItem(str(int(size) if size == int(size) else size))
        self._size.currentTextChanged.connect(self._on_size_changed)
        row.addWidget(self._size)

        row.addWidget(_vsep(self))

        self._style_buttons: dict[str, QToolButton] = {}
        for key, label, tip in _STYLE_BUTTONS:
            button = QToolButton(self)
            button.setText(label)
            button.setCheckable(True)
            button.setToolTip(tip)
            button.setFixedSize(TOOLBAR_BUTTON_SIZE, TOOLBAR_BUTTON_SIZE)
            button.setStyleSheet(TOOLBAR_BUTTON_STYLE)
            button.toggled.connect(lambda checked, k=key: self._on_style_toggled(k, checked=checked))
            self._style_buttons[key] = button
            row.addWidget(button)

        row.addWidget(_vsep(self))

        self._align_buttons: dict[str, QToolButton] = {}
        for key, icon_name, tip in _ALIGN_BUTTONS:
            button = QToolButton(self)
            button.setCheckable(True)
            button.setAutoExclusive(True)
            button.setToolTip(tip)
            button.setFixedSize(TOOLBAR_BUTTON_SIZE, TOOLBAR_BUTTON_SIZE)
            button.setStyleSheet(TOOLBAR_BUTTON_STYLE)
            button.setIcon(create_lucide_icon(icon_name, size=TOOLBAR_ICON_SIZE))
            button.toggled.connect(lambda checked, k=key: self._on_align_toggled(k, checked=checked))
            self._align_buttons[key] = button
            row.addWidget(button)

        row.addWidget(_vsep(self))

        self._bg_fill = QCheckBox("Background fill", self)
        self._bg_fill.toggled.connect(self._on_bg_toggled)
        row.addWidget(self._bg_fill)
        row.addStretch(1)

    def set_color(self, color: QColor) -> None:
        """Update the text color stored in settings (from the main color picker)."""
        if not color.isValid():
            return
        self._settings.color = color.name()
        self._emit()

    def set_settings(self, settings: ScreenshotTextSettings) -> None:
        """Load `settings` into the controls without emitting."""
        self._updating = True
        self._settings = ScreenshotTextSettings(
            font_family=settings.font_family,
            font_size=settings.font_size,
            bold=settings.bold,
            italic=settings.italic,
            underline=settings.underline,
            strikeout=settings.strikeout,
            align=settings.align,
            background_fill=settings.background_fill,
            color=settings.color,
        )
        family = settings.font_family
        index = self._family.findText(family)
        if index < 0 and family:
            self._family.addItem(family)
            index = self._family.findText(family)
        if index >= 0:
            self._family.setCurrentIndex(index)
        size_value = settings.font_size
        size_text = str(int(size_value) if size_value == int(size_value) else size_value)
        size_index = self._size.findText(size_text)
        if size_index >= 0:
            self._size.setCurrentIndex(size_index)
        else:
            self._size.setEditText(size_text)
        self._style_buttons["bold"].setChecked(settings.bold)
        self._style_buttons["italic"].setChecked(settings.italic)
        self._style_buttons["underline"].setChecked(settings.underline)
        self._style_buttons["strikeout"].setChecked(settings.strikeout)
        for key, button in self._align_buttons.items():
            button.setChecked(key == settings.align)
        self._bg_fill.setChecked(settings.background_fill)
        self._updating = False

    def settings(self) -> ScreenshotTextSettings:
        """Return the current toolbar settings."""
        return self._settings

    def _emit(self) -> None:
        if self._updating:
            return
        self.settings_changed.emit(self._settings)

    def _on_align_toggled(self, key: str, *, checked: bool) -> None:
        if self._updating or not checked:
            return
        align: TextAlign = key if key in {"left", "center", "right"} else "left"
        self._settings.align = align
        self._emit()

    def _on_bg_toggled(self, checked: bool) -> None:  # noqa: FBT001
        if self._updating:
            return
        self._settings.background_fill = checked
        self._emit()

    def _on_family_changed(self, family: str) -> None:
        if self._updating:
            return
        self._settings.font_family = family.strip()
        self._emit()

    def _on_size_changed(self, text: str) -> None:
        if self._updating:
            return
        try:
            size = float(text.replace(",", ".").strip())
        except ValueError:
            return
        if size < _MIN_FONT_SIZE or size > _MAX_FONT_SIZE:
            return
        self._settings.font_size = size
        self._emit()

    def _on_style_toggled(self, key: str, *, checked: bool) -> None:
        if self._updating:
            return
        if key == "bold":
            self._settings.bold = checked
        elif key == "italic":
            self._settings.italic = checked
        elif key == "underline":
            self._settings.underline = checked
        elif key == "strikeout":
            self._settings.strikeout = checked
        self._emit()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Build combos and toggles; call [`set_settings`](#%EF%B8%8F-method-set_settings) before showing.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._updating = False
        self._settings = ScreenshotTextSettings()
        self.setObjectName("hskScreenshotTextToolbar")
        self.setStyleSheet(
            "#hskScreenshotTextToolbar {  background: #f7f7f8;  border: 1px solid #d0d0d4;  border-radius: 10px;}"
        )

        row = QHBoxLayout(self)
        row.setContentsMargins(10, 6, 10, 6)
        row.setSpacing(8)

        self._family = QComboBox(self)
        self._family.setMinimumWidth(100)
        self._family.setMaximumWidth(140)
        self._family.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        for name in available_text_font_families():
            self._family.addItem(name)
        self._family.currentTextChanged.connect(self._on_family_changed)
        row.addWidget(self._family)

        self._size = QComboBox(self)
        self._size.setEditable(True)
        self._size.setMinimumWidth(64)
        for size in font_size_choices():
            self._size.addItem(str(int(size) if size == int(size) else size))
        self._size.currentTextChanged.connect(self._on_size_changed)
        row.addWidget(self._size)

        row.addWidget(_vsep(self))

        self._style_buttons: dict[str, QToolButton] = {}
        for key, label, tip in _STYLE_BUTTONS:
            button = QToolButton(self)
            button.setText(label)
            button.setCheckable(True)
            button.setToolTip(tip)
            button.setFixedSize(TOOLBAR_BUTTON_SIZE, TOOLBAR_BUTTON_SIZE)
            button.setStyleSheet(TOOLBAR_BUTTON_STYLE)
            button.toggled.connect(lambda checked, k=key: self._on_style_toggled(k, checked=checked))
            self._style_buttons[key] = button
            row.addWidget(button)

        row.addWidget(_vsep(self))

        self._align_buttons: dict[str, QToolButton] = {}
        for key, icon_name, tip in _ALIGN_BUTTONS:
            button = QToolButton(self)
            button.setCheckable(True)
            button.setAutoExclusive(True)
            button.setToolTip(tip)
            button.setFixedSize(TOOLBAR_BUTTON_SIZE, TOOLBAR_BUTTON_SIZE)
            button.setStyleSheet(TOOLBAR_BUTTON_STYLE)
            button.setIcon(create_lucide_icon(icon_name, size=TOOLBAR_ICON_SIZE))
            button.toggled.connect(lambda checked, k=key: self._on_align_toggled(k, checked=checked))
            self._align_buttons[key] = button
            row.addWidget(button)

        row.addWidget(_vsep(self))

        self._bg_fill = QCheckBox("Background fill", self)
        self._bg_fill.toggled.connect(self._on_bg_toggled)
        row.addWidget(self._bg_fill)
        row.addStretch(1)
```

</details>

### ⚙️ Method `set_color`

```python
def set_color(self, color: QColor) -> None
```

Update the text color stored in settings (from the main color picker).

<details>
<summary>Code:</summary>

```python
def set_color(self, color: QColor) -> None:
        if not color.isValid():
            return
        self._settings.color = color.name()
        self._emit()
```

</details>

### ⚙️ Method `set_settings`

```python
def set_settings(self, settings: ScreenshotTextSettings) -> None
```

Load [`settings`](#%EF%B8%8F-method-settings) into the controls without emitting.

<details>
<summary>Code:</summary>

```python
def set_settings(self, settings: ScreenshotTextSettings) -> None:
        self._updating = True
        self._settings = ScreenshotTextSettings(
            font_family=settings.font_family,
            font_size=settings.font_size,
            bold=settings.bold,
            italic=settings.italic,
            underline=settings.underline,
            strikeout=settings.strikeout,
            align=settings.align,
            background_fill=settings.background_fill,
            color=settings.color,
        )
        family = settings.font_family
        index = self._family.findText(family)
        if index < 0 and family:
            self._family.addItem(family)
            index = self._family.findText(family)
        if index >= 0:
            self._family.setCurrentIndex(index)
        size_value = settings.font_size
        size_text = str(int(size_value) if size_value == int(size_value) else size_value)
        size_index = self._size.findText(size_text)
        if size_index >= 0:
            self._size.setCurrentIndex(size_index)
        else:
            self._size.setEditText(size_text)
        self._style_buttons["bold"].setChecked(settings.bold)
        self._style_buttons["italic"].setChecked(settings.italic)
        self._style_buttons["underline"].setChecked(settings.underline)
        self._style_buttons["strikeout"].setChecked(settings.strikeout)
        for key, button in self._align_buttons.items():
            button.setChecked(key == settings.align)
        self._bg_fill.setChecked(settings.background_fill)
        self._updating = False
```

</details>

### ⚙️ Method `settings`

```python
def settings(self) -> ScreenshotTextSettings
```

Return the current toolbar settings.

<details>
<summary>Code:</summary>

```python
def settings(self) -> ScreenshotTextSettings:
        return self._settings
```

</details>
