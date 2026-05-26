---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `process_habit_bool_delegate.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ProcessHabitBoolDelegate`](#%EF%B8%8F-class-processhabitbooldelegate)
  - [⚙️ Method `displayText`](#%EF%B8%8F-method-displaytext)
  - [⚙️ Method `editorEvent`](#%EF%B8%8F-method-editorevent)
  - [⚙️ Method `paint`](#%EF%B8%8F-method-paint)
- [🔧 Function `cell_state_from_index`](#-function-cell_state_from_index)
- [🔧 Function `next_value_for_toggle`](#-function-next_value_for_toggle)
- [🔧 Function `parse_process_habit_bool`](#-function-parse_process_habit_bool)
- [🔧 Function `_center_rect`](#-function-_center_rect)

</details>

## 🏛️ Class `ProcessHabitBoolDelegate`

```python
class ProcessHabitBoolDelegate(QStyledItemDelegate)
```

Paint a checkbox in view mode; toggle value on click without entering edit mode.

<details>
<summary>Code:</summary>

```python
class ProcessHabitBoolDelegate(QStyledItemDelegate):

    def displayText(self, value: object, _locale: QLocale | QLocale.Language) -> str:  # noqa: N802
        """Hide stored 0/1 text; checkbox is drawn in paint()."""
        return ""

    def editorEvent(  # noqa: N802
        self,
        event: QEvent,
        model: QAbstractItemModel,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> bool:
        """Toggle cell value on mouse release."""
        if event.type() != QEvent.Type.MouseButtonRelease:
            return False
        mouse_event = event
        if not isinstance(mouse_event, QMouseEvent):
            return False
        if mouse_event.button() != Qt.MouseButton.LeftButton:
            return False

        new_value = next_value_for_toggle(cell_state_from_index(index))
        return model.setData(index, new_value, Qt.ItemDataRole.EditRole)

    def paint(  # noqa: N802
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        """Draw row background; draw a centered checkbox when a DB record exists."""
        self.initStyleOption(option, index)
        style = option.widget.style() if option.widget is not None else QApplication.style()

        # Fill cell background (row color from model)
        style.drawPrimitive(QStyle.PrimitiveElement.PE_PanelItemViewItem, option, painter, option.widget)

        if cell_state_from_index(index) == "absent":
            return

        check_option = QStyleOptionButton()
        check_option.state = QStyle.StateFlag.State_Enabled | QStyle.StateFlag.State_Active
        if cell_state_from_index(index) == "checked":
            check_option.state |= QStyle.StateFlag.State_On
        else:
            check_option.state |= QStyle.StateFlag.State_Off

        indicator_rect = style.subElementRect(
            QStyle.SubElement.SE_CheckBoxIndicator,
            check_option,
            option.widget,
        )
        check_option.rect = _center_rect(option.rect, indicator_rect.size())
        style.drawControl(QStyle.ControlElement.CE_CheckBox, check_option, painter, option.widget)
```

</details>

### ⚙️ Method `displayText`

```python
def displayText(self, value: object, _locale: QLocale | QLocale.Language) -> str
```

Hide stored 0/1 text; checkbox is drawn in paint().

<details>
<summary>Code:</summary>

```python
def displayText(self, value: object, _locale: QLocale | QLocale.Language) -> str:  # noqa: N802
        return ""
```

</details>

### ⚙️ Method `editorEvent`

```python
def editorEvent(self, event: QEvent, model: QAbstractItemModel, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> bool
```

Toggle cell value on mouse release.

<details>
<summary>Code:</summary>

```python
def editorEvent(  # noqa: N802
        self,
        event: QEvent,
        model: QAbstractItemModel,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> bool:
        if event.type() != QEvent.Type.MouseButtonRelease:
            return False
        mouse_event = event
        if not isinstance(mouse_event, QMouseEvent):
            return False
        if mouse_event.button() != Qt.MouseButton.LeftButton:
            return False

        new_value = next_value_for_toggle(cell_state_from_index(index))
        return model.setData(index, new_value, Qt.ItemDataRole.EditRole)
```

</details>

### ⚙️ Method `paint`

```python
def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> None
```

Draw row background; draw a centered checkbox when a DB record exists.

<details>
<summary>Code:</summary>

```python
def paint(  # noqa: N802
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        self.initStyleOption(option, index)
        style = option.widget.style() if option.widget is not None else QApplication.style()

        # Fill cell background (row color from model)
        style.drawPrimitive(QStyle.PrimitiveElement.PE_PanelItemViewItem, option, painter, option.widget)

        if cell_state_from_index(index) == "absent":
            return

        check_option = QStyleOptionButton()
        check_option.state = QStyle.StateFlag.State_Enabled | QStyle.StateFlag.State_Active
        if cell_state_from_index(index) == "checked":
            check_option.state |= QStyle.StateFlag.State_On
        else:
            check_option.state |= QStyle.StateFlag.State_Off

        indicator_rect = style.subElementRect(
            QStyle.SubElement.SE_CheckBoxIndicator,
            check_option,
            option.widget,
        )
        check_option.rect = _center_rect(option.rect, indicator_rect.size())
        style.drawControl(QStyle.ControlElement.CE_CheckBox, check_option, painter, option.widget)
```

</details>

## 🔧 Function `cell_state_from_index`

```python
def cell_state_from_index(index: QModelIndex | QPersistentModelIndex) -> ProcessHabitBoolState
```

Return visual state for a boolean process-habit cell.

<details>
<summary>Code:</summary>

```python
def cell_state_from_index(index: QModelIndex | QPersistentModelIndex) -> ProcessHabitBoolState:
    stored = index.data(Qt.ItemDataRole.UserRole)
    record_id = stored[0] if stored else None
    display = index.data(Qt.ItemDataRole.DisplayRole)
    return parse_process_habit_bool(display, record_id)
```

</details>

## 🔧 Function `next_value_for_toggle`

```python
def next_value_for_toggle(current: ProcessHabitBoolState) -> str
```

Return the model string value after a click on the cell.

<details>
<summary>Code:</summary>

```python
def next_value_for_toggle(current: ProcessHabitBoolState) -> str:
    if current == "absent":
        return "1"
    if current == "checked":
        return "0"
    return "1"
```

</details>

## 🔧 Function `parse_process_habit_bool`

```python
def parse_process_habit_bool(value: object, record_id: object) -> ProcessHabitBoolState
```

Map model storage to absent / checked / unchecked.

Args:

- `value` (`object`): Display/edit value from the model.
- `record_id` (`object`): First element of UserRole tuple, or None if no DB row.

Returns:

- `ProcessHabitBoolState`: Cell visual state.

<details>
<summary>Code:</summary>

```python
def parse_process_habit_bool(value: object, record_id: object) -> ProcessHabitBoolState:
    if record_id is None:
        return "absent"
    text = str(value).strip().lower() if value is not None else ""
    if text in _TRUTHY_VALUES:
        return "checked"
    return "unchecked"
```

</details>

## 🔧 Function `_center_rect`

```python
def _center_rect(outer: QRect, size: QSize) -> QRect
```

Center a rectangle of given size inside outer.

<details>
<summary>Code:</summary>

```python
def _center_rect(outer: QRect, size: QSize) -> QRect:
    x = outer.x() + (outer.width() - size.width()) // 2
    y = outer.y() + (outer.height() - size.height()) // 2
    return QRect(x, y, size.width(), size.height())
```

</details>
