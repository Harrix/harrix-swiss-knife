---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `dialog_base.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `FluentDialog`](#%EF%B8%8F-class-fluentdialog)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
- [🏛️ Class `FluentDialogBody`](#%EF%B8%8F-class-fluentdialogbody)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-1)
- [🏛️ Class `FluentDialogFooter`](#%EF%B8%8F-class-fluentdialogfooter)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-2)
  - [⚙️ Method `paintEvent`](#%EF%B8%8F-method-paintevent)

</details>

## 🏛️ Class `FluentDialog`

```python
class FluentDialog(QDialog)
```

Modal window dialog: subtitle, text, optional content, and a footer with buttons.

<details>
<summary>Code:</summary>

```python
class FluentDialog(QDialog):

    def __init__(
        self,
        title: str,
        content: str = "",
        parent: QWidget | None = None,
        *,
        primary_text: str = "OK",
        secondary_text: str = "Cancel",
    ) -> None:
        """Create a dialog (`exec()` returns `Accepted` for the primary button)."""
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(_DIALOG_MIN_WIDTH)
        self.setMaximumWidth(_DIALOG_MAX_WIDTH + 200)
        if parent is None or is_fluent_themed(parent):
            enable_fluent_theme(self)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self._body = FluentDialogBody(title, content, self)
        layout.addWidget(self._body)
        self.content_layout = self._body.content_layout
        self.primary_button = self._body.primary
        self.secondary_button = self._body.secondary
        self.primary_button.setText(primary_text)
        self.secondary_button.setText(secondary_text)
        self.secondary_button.setVisible(bool(secondary_text))
        self.primary_button.clicked.connect(self.accept)
        self.secondary_button.clicked.connect(self.reject)
        self.primary_button.setDefault(True)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, title: str, content: str = '', parent: QWidget | None = None, *, primary_text: str = 'OK', secondary_text: str = 'Cancel') -> None
```

Create a dialog (`exec()` returns `Accepted` for the primary button).

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        title: str,
        content: str = "",
        parent: QWidget | None = None,
        *,
        primary_text: str = "OK",
        secondary_text: str = "Cancel",
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(_DIALOG_MIN_WIDTH)
        self.setMaximumWidth(_DIALOG_MAX_WIDTH + 200)
        if parent is None or is_fluent_themed(parent):
            enable_fluent_theme(self)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self._body = FluentDialogBody(title, content, self)
        layout.addWidget(self._body)
        self.content_layout = self._body.content_layout
        self.primary_button = self._body.primary
        self.secondary_button = self._body.secondary
        self.primary_button.setText(primary_text)
        self.secondary_button.setText(secondary_text)
        self.secondary_button.setVisible(bool(secondary_text))
        self.primary_button.clicked.connect(self.accept)
        self.secondary_button.clicked.connect(self.reject)
        self.primary_button.setDefault(True)
```

</details>

## 🏛️ Class `FluentDialogBody`

```python
class FluentDialogBody(QWidget)
```

Title + content + footer used by both [`FluentDialog`](#%EF%B8%8F-class-fluentdialog) and [`FluentContentDialog`](dialogs.g.md#%EF%B8%8F-class-fluentcontentdialog).

<details>
<summary>Code:</summary>

```python
class FluentDialogBody(QWidget):

    def __init__(self, title: str, content: str, parent: QWidget) -> None:
        """Build the title, content text, and the OK / Cancel footer."""
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        top = QWidget(self)
        self.content_layout = QVBoxLayout(top)
        self.content_layout.setContentsMargins(SPACE_XL, SPACE_XL, SPACE_XL, SPACE_XL)
        self.content_layout.setSpacing(SPACE_M)
        self.title_label = FluentText(title, top, style=TextStyle.SUBTITLE)
        self.content_layout.addWidget(self.title_label)
        self.content_label = FluentText(content, top, word_wrap=True)
        self.content_label.setVisible(bool(content))
        self.content_layout.addWidget(self.content_label)
        layout.addWidget(top, 1)
        self.footer = FluentDialogFooter(self)
        layout.addWidget(self.footer)
        self.primary = FluentPrimaryButton("OK", self.footer)
        self.secondary = FluentPushButton("Cancel", self.footer)
        self.footer.row.addWidget(self.primary, 1)
        self.footer.row.addWidget(self.secondary, 1)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, title: str, content: str, parent: QWidget) -> None
```

Build the title, content text, and the OK / Cancel footer.

<details>
<summary>Code:</summary>

```python
def __init__(self, title: str, content: str, parent: QWidget) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        top = QWidget(self)
        self.content_layout = QVBoxLayout(top)
        self.content_layout.setContentsMargins(SPACE_XL, SPACE_XL, SPACE_XL, SPACE_XL)
        self.content_layout.setSpacing(SPACE_M)
        self.title_label = FluentText(title, top, style=TextStyle.SUBTITLE)
        self.content_layout.addWidget(self.title_label)
        self.content_label = FluentText(content, top, word_wrap=True)
        self.content_label.setVisible(bool(content))
        self.content_layout.addWidget(self.content_label)
        layout.addWidget(top, 1)
        self.footer = FluentDialogFooter(self)
        layout.addWidget(self.footer)
        self.primary = FluentPrimaryButton("OK", self.footer)
        self.secondary = FluentPushButton("Cancel", self.footer)
        self.footer.row.addWidget(self.primary, 1)
        self.footer.row.addWidget(self.secondary, 1)
```

</details>

## 🏛️ Class `FluentDialogFooter`

```python
class FluentDialogFooter(QWidget)
```

Bottom strip of a dialog: `layer_alt` fill with right-aligned buttons.

<details>
<summary>Code:</summary>

```python
class FluentDialogFooter(QWidget):

    def __init__(self, parent: QWidget) -> None:
        """Create the footer with an empty button row."""
        super().__init__(parent)
        self.row = QHBoxLayout(self)
        self.row.setContentsMargins(SPACE_XL, SPACE_XL, SPACE_XL, SPACE_XL)
        self.row.setSpacing(SPACE_S)
        bind_theme(self, self.update)

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Paint the footer fill and its top hairline."""
        palette = palette_for(self)
        painter = QPainter(self)
        painter.fillRect(self.rect(), palette.layer_alt_bg if not palette.dark else palette.solid_secondary_bg)
        painter.fillRect(0, 0, self.width(), 1, palette.card_stroke)
        painter.end()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget) -> None
```

Create the footer with an empty button row.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.row = QHBoxLayout(self)
        self.row.setContentsMargins(SPACE_XL, SPACE_XL, SPACE_XL, SPACE_XL)
        self.row.setSpacing(SPACE_S)
        bind_theme(self, self.update)
```

</details>

### ⚙️ Method `paintEvent`

```python
def paintEvent(self, _event: QPaintEvent) -> None
```

Paint the footer fill and its top hairline.

<details>
<summary>Code:</summary>

```python
def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        palette = palette_for(self)
        painter = QPainter(self)
        painter.fillRect(self.rect(), palette.layer_alt_bg if not palette.dark else palette.solid_secondary_bg)
        painter.fillRect(0, 0, self.width(), 1, palette.card_stroke)
        painter.end()
```

</details>
