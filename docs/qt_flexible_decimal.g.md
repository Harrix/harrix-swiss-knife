---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `qt_flexible_decimal.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `FlexibleDecimalSpinFilter`](#%EF%B8%8F-class-flexibledecimalspinfilter)
  - [⚙️ Method `eventFilter`](#%EF%B8%8F-method-eventfilter)
- [🔧 Function `double_spinbox_from_widget`](#-function-double_spinbox_from_widget)
- [🔧 Function `install_flexible_decimal_separators`](#-function-install_flexible_decimal_separators)
- [🔧 Function `normalize_decimal_text`](#-function-normalize_decimal_text)
- [🔧 Function `spinbox_decimal_point`](#-function-spinbox_decimal_point)

</details>

## 🏛️ Class `FlexibleDecimalSpinFilter`

```python
class FlexibleDecimalSpinFilter(QObject)
```

Map `,`/`.` keys and pasted text to the spin box locale decimal point.

<details>
<summary>Code:</summary>

```python
class FlexibleDecimalSpinFilter(QObject):

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Rewrite decimal keys and normalize pasted numbers in double spin boxes."""
        spin = double_spinbox_from_widget(watched)
        if spin is None:
            return False

        self._ensure_line_edit_hook(spin)
        decimal = spinbox_decimal_point(spin)
        other = _ALT_SEPARATORS.get(decimal)
        if event.type() != QEvent.Type.KeyPress or not isinstance(event, QKeyEvent):
            return False

        if event.matches(QKeySequence.StandardKey.Paste):
            clipboard = QApplication.clipboard()
            line = spin.lineEdit()
            if clipboard is not None and line is not None:
                line.insert(normalize_decimal_text(clipboard.text(), decimal))
                return True

        if other is not None and event.text() == other:
            key = Qt.Key.Key_Period if decimal == "." else Qt.Key.Key_Comma
            replacement = QKeyEvent(QEvent.Type.KeyPress, key, event.modifiers(), decimal)
            QApplication.sendEvent(watched, replacement)
            return True

        return False

    def _ensure_line_edit_hook(self, spin: QDoubleSpinBox) -> None:
        line = spin.lineEdit()
        if line is None or line.property("_hskFlexibleDecimal") == "1":
            return
        line.setProperty("_hskFlexibleDecimal", "1")
        line.textChanged.connect(lambda text, editor=line, box=spin: _normalize_spin_line(editor, box, text))
```

</details>

### ⚙️ Method `eventFilter`

```python
def eventFilter(self, watched: QObject, event: QEvent) -> bool
```

Rewrite decimal keys and normalize pasted numbers in double spin boxes.

<details>
<summary>Code:</summary>

```python
def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        spin = double_spinbox_from_widget(watched)
        if spin is None:
            return False

        self._ensure_line_edit_hook(spin)
        decimal = spinbox_decimal_point(spin)
        other = _ALT_SEPARATORS.get(decimal)
        if event.type() != QEvent.Type.KeyPress or not isinstance(event, QKeyEvent):
            return False

        if event.matches(QKeySequence.StandardKey.Paste):
            clipboard = QApplication.clipboard()
            line = spin.lineEdit()
            if clipboard is not None and line is not None:
                line.insert(normalize_decimal_text(clipboard.text(), decimal))
                return True

        if other is not None and event.text() == other:
            key = Qt.Key.Key_Period if decimal == "." else Qt.Key.Key_Comma
            replacement = QKeyEvent(QEvent.Type.KeyPress, key, event.modifiers(), decimal)
            QApplication.sendEvent(watched, replacement)
            return True

        return False
```

</details>

## 🔧 Function `double_spinbox_from_widget`

```python
def double_spinbox_from_widget(widget: QObject | None) -> QDoubleSpinBox | None
```

Return the `QDoubleSpinBox` that owns `widget`, if any.

<details>
<summary>Code:</summary>

```python
def double_spinbox_from_widget(widget: QObject | None) -> QDoubleSpinBox | None:
    current: QObject | None = widget
    while current is not None:
        if isinstance(current, QDoubleSpinBox):
            return current
        current = current.parent()
    return None
```

</details>

## 🔧 Function `install_flexible_decimal_separators`

```python
def install_flexible_decimal_separators(app: QApplication) -> None
```

Install an application-wide filter so every `QDoubleSpinBox` accepts `,` and `.`.

<details>
<summary>Code:</summary>

```python
def install_flexible_decimal_separators(app: QApplication) -> None:
    if not isinstance(app, QApplication):
        return
    existing = app.property("_hskFlexibleDecimalFilter")
    if isinstance(existing, FlexibleDecimalSpinFilter):
        return
    event_filter = FlexibleDecimalSpinFilter(app)
    app.installEventFilter(event_filter)
    app.setProperty("_hskFlexibleDecimalFilter", event_filter)
```

</details>

## 🔧 Function `normalize_decimal_text`

```python
def normalize_decimal_text(text: str, decimal_point: str) -> str
```

Replace the other separator with `decimal_point` when it is the only one used.

<details>
<summary>Code:</summary>

```python
def normalize_decimal_text(text: str, decimal_point: str) -> str:
    other = _ALT_SEPARATORS.get(decimal_point)
    if other is None or other not in text or decimal_point in text:
        return text
    return text.replace(other, decimal_point)
```

</details>

## 🔧 Function `spinbox_decimal_point`

```python
def spinbox_decimal_point(spin: QDoubleSpinBox) -> str
```

Return the locale decimal-point character for `spin`.

<details>
<summary>Code:</summary>

```python
def spinbox_decimal_point(spin: QDoubleSpinBox) -> str:
    point = spin.locale().decimalPoint()
    return point if isinstance(point, str) and point else "."
```

</details>
