---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `checkbox_display_delegate.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `CheckboxDisplayDelegate`](#%EF%B8%8F-class-checkboxdisplaydelegate)
  - [⚙️ Method `displayText`](#%EF%B8%8F-method-displaytext)
  - [⚙️ Method `paint`](#%EF%B8%8F-method-paint)
- [🔧 Function `is_checkbox_cell_checked`](#-function-is_checkbox_cell_checked)

</details>

## 🏛️ Class `CheckboxDisplayDelegate`

```python
class CheckboxDisplayDelegate(QStyledItemDelegate)
```

Paint a centered Lucide checkbox instead of raw 1/0 text.

<details>
<summary>Code:</summary>

```python
class CheckboxDisplayDelegate(QStyledItemDelegate):

    def displayText(self, _value: object, _locale: QLocale | QLocale.Language) -> str:  # noqa: N802
        """Hide stored 1/0 text; the checkbox is drawn in `paint`."""
        return ""

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        """Draw the row background and a centered Lucide checkbox indicator."""
        self.initStyleOption(option, index)
        option.text = ""
        widget = option.widget
        style = widget.style() if widget is not None else QApplication.style()
        style.drawPrimitive(QStyle.PrimitiveElement.PE_PanelItemViewItem, option, painter, widget)

        size = CHECKBOX_INDICATOR_PX
        rect = QRect(
            option.rect.x() + (option.rect.width() - size) // 2,
            option.rect.y() + (option.rect.height() - size) // 2,
            size,
            size,
        )
        paint_lucide_checkbox(
            painter,
            rect,
            checked=is_checkbox_cell_checked(index.data(Qt.ItemDataRole.DisplayRole)),
            enabled=bool(option.state & QStyle.StateFlag.State_Enabled),
        )
```

</details>

### ⚙️ Method `displayText`

```python
def displayText(self, _value: object, _locale: QLocale | QLocale.Language) -> str
```

Hide stored 1/0 text; the checkbox is drawn in `paint`.

<details>
<summary>Code:</summary>

```python
def displayText(self, _value: object, _locale: QLocale | QLocale.Language) -> str:  # noqa: N802
        return ""
```

</details>

### ⚙️ Method `paint`

```python
def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> None
```

Draw the row background and a centered Lucide checkbox indicator.

<details>
<summary>Code:</summary>

```python
def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        self.initStyleOption(option, index)
        option.text = ""
        widget = option.widget
        style = widget.style() if widget is not None else QApplication.style()
        style.drawPrimitive(QStyle.PrimitiveElement.PE_PanelItemViewItem, option, painter, widget)

        size = CHECKBOX_INDICATOR_PX
        rect = QRect(
            option.rect.x() + (option.rect.width() - size) // 2,
            option.rect.y() + (option.rect.height() - size) // 2,
            size,
            size,
        )
        paint_lucide_checkbox(
            painter,
            rect,
            checked=is_checkbox_cell_checked(index.data(Qt.ItemDataRole.DisplayRole)),
            enabled=bool(option.state & QStyle.StateFlag.State_Enabled),
        )
```

</details>

## 🔧 Function `is_checkbox_cell_checked`

```python
def is_checkbox_cell_checked(value: object) -> bool
```

Return whether a model cell value represents a checked flag.

Args:

- `value` (`object`): Raw cell value from the model.

Returns:

- `bool`: `True` for `1`, `true`, `yes`, or a non-zero integer.

<details>
<summary>Code:</summary>

```python
def is_checkbox_cell_checked(value: object) -> bool:
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value != 0
    text = str(value).strip().lower()
    return text in _TRUTHY_VALUES
```

</details>
