---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `scripts.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ScriptsPanel`](#%EF%B8%8F-class-scriptspanel)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `append_glyph`](#%EF%B8%8F-method-append_glyph)
  - [⚙️ Method `clear`](#%EF%B8%8F-method-clear)
  - [⚙️ Method `composed_text`](#%EF%B8%8F-method-composed_text)
  - [⚙️ Method `focus_composer`](#%EF%B8%8F-method-focus_composer)

</details>

## 🏛️ Class `ScriptsPanel`

```python
class ScriptsPanel(QWidget)
```

Compose a superscript or subscript string, then paste it with Add.

<details>
<summary>Code:</summary>

```python
class ScriptsPanel(QWidget):

    add_requested = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        """Build the composer and the glyph buttons."""
        super().__init__(parent)
        self._edit = QLineEdit(self)
        self._edit.setPlaceholderText("Click characters, then Add")
        self._edit.setClearButtonEnabled(True)
        self._edit.returnPressed.connect(self._emit_add)

        self._add_button = QPushButton("Add", self)
        self._add_button.setObjectName("scriptsAddButton")
        self._add_button.setAutoDefault(False)
        self._add_button.setDefault(False)
        self._add_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._add_button.clicked.connect(self._emit_add)

        composer = QHBoxLayout()
        composer.setContentsMargins(0, 0, 0, 0)
        composer.addWidget(self._edit, stretch=1)
        composer.addWidget(self._add_button)

        sections = QWidget(self)
        sections_layout = QVBoxLayout(sections)
        sections_layout.setContentsMargins(0, 0, 0, 0)
        sections_layout.setSpacing(SPACE_S)
        self._section_labels: list[QLabel] = []
        self._glyph_buttons: list[QPushButton] = []
        for title, glyphs in SCRIPT_SECTIONS:
            label = _section_label(title, sections)
            self._section_labels.append(label)
            sections_layout.addWidget(label)
            flow = _glyph_flow(glyphs, title, self._append_glyph, sections)
            self._glyph_buttons.extend(flow.findChildren(QPushButton))
            sections_layout.addWidget(flow)
        sections_layout.addStretch(1)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidget(sections)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, SPACE_S, 0, 0)
        layout.addLayout(composer)
        layout.addWidget(scroll, stretch=1)
        bind_theme(self, self._refresh_theme)

    def append_glyph(self, char: str) -> None:
        """Insert `char` at the composer caret."""
        self._append_glyph(char)

    def clear(self) -> None:
        """Empty the composer."""
        self._edit.clear()

    def composed_text(self) -> str:
        """Return the characters collected in the composer."""
        return self._edit.text()

    def focus_composer(self) -> None:
        """Move keyboard focus to the composer."""
        self._edit.setFocus()

    def _append_glyph(self, char: str) -> None:
        """Insert `char` at the composer caret and keep the caret there."""
        edit = self._edit
        pos = edit.cursorPosition()
        text = edit.text()
        edit.setText(text[:pos] + char + text[pos:])
        edit.setCursorPosition(pos + len(char))
        edit.setFocus()

    def _emit_add(self) -> None:
        """Ask the overlay to paste the composer text."""
        text = self._edit.text()
        if not text:
            return
        self.add_requested.emit(text)

    def _refresh_theme(self) -> None:
        palette = palette_for(self)
        self._edit.setStyleSheet(line_edit_qss(palette))
        self._add_button.setStyleSheet(accent_button_qss(palette, "QPushButton#scriptsAddButton"))
        secondary = css(mix(palette.window_bg, palette.text_secondary))
        for label in self._section_labels:
            label.setStyleSheet(f"color: {secondary};")
        glyph_qss = push_button_qss(palette) + f"QPushButton {{ padding: 0 {SPACE_XS}px; }}"
        for button in self._glyph_buttons:
            button.setStyleSheet(glyph_qss)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Build the composer and the glyph buttons.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._edit = QLineEdit(self)
        self._edit.setPlaceholderText("Click characters, then Add")
        self._edit.setClearButtonEnabled(True)
        self._edit.returnPressed.connect(self._emit_add)

        self._add_button = QPushButton("Add", self)
        self._add_button.setObjectName("scriptsAddButton")
        self._add_button.setAutoDefault(False)
        self._add_button.setDefault(False)
        self._add_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._add_button.clicked.connect(self._emit_add)

        composer = QHBoxLayout()
        composer.setContentsMargins(0, 0, 0, 0)
        composer.addWidget(self._edit, stretch=1)
        composer.addWidget(self._add_button)

        sections = QWidget(self)
        sections_layout = QVBoxLayout(sections)
        sections_layout.setContentsMargins(0, 0, 0, 0)
        sections_layout.setSpacing(SPACE_S)
        self._section_labels: list[QLabel] = []
        self._glyph_buttons: list[QPushButton] = []
        for title, glyphs in SCRIPT_SECTIONS:
            label = _section_label(title, sections)
            self._section_labels.append(label)
            sections_layout.addWidget(label)
            flow = _glyph_flow(glyphs, title, self._append_glyph, sections)
            self._glyph_buttons.extend(flow.findChildren(QPushButton))
            sections_layout.addWidget(flow)
        sections_layout.addStretch(1)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidget(sections)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, SPACE_S, 0, 0)
        layout.addLayout(composer)
        layout.addWidget(scroll, stretch=1)
        bind_theme(self, self._refresh_theme)
```

</details>

### ⚙️ Method `append_glyph`

```python
def append_glyph(self, char: str) -> None
```

Insert `char` at the composer caret.

<details>
<summary>Code:</summary>

```python
def append_glyph(self, char: str) -> None:
        self._append_glyph(char)
```

</details>

### ⚙️ Method `clear`

```python
def clear(self) -> None
```

Empty the composer.

<details>
<summary>Code:</summary>

```python
def clear(self) -> None:
        self._edit.clear()
```

</details>

### ⚙️ Method `composed_text`

```python
def composed_text(self) -> str
```

Return the characters collected in the composer.

<details>
<summary>Code:</summary>

```python
def composed_text(self) -> str:
        return self._edit.text()
```

</details>

### ⚙️ Method `focus_composer`

```python
def focus_composer(self) -> None
```

Move keyboard focus to the composer.

<details>
<summary>Code:</summary>

```python
def focus_composer(self) -> None:
        self._edit.setFocus()
```

</details>
