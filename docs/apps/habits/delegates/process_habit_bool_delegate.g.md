---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `process_habit_bool_delegate.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ProcessHabitBoolDelegate`](#️-class-processhabitbooldelegate)
  - [⚙️ Method `__init__`](#️-method-__init__)
  - [⚙️ Method `detach_from_view`](#️-method-detach_from_view)
  - [⚙️ Method `displayText`](#️-method-displaytext)
  - [⚙️ Method `editorEvent`](#️-method-editorevent)
  - [⚙️ Method `eventFilter`](#️-method-eventfilter)
  - [⚙️ Method `paint`](#️-method-paint)
- [🔧 Function `cell_state_from_index`](#-function-cell_state_from_index)
- [🔧 Function `next_value_for_toggle`](#-function-next_value_for_toggle)
- [🔧 Function `parse_process_habit_bool`](#-function-parse_process_habit_bool)

</details>

## 🏛️ Class `ProcessHabitBoolDelegate`

```python
class ProcessHabitBoolDelegate(QStyledItemDelegate)
```

Paint checkboxes; hover picker for empty cells, toggle for existing values.

<details>
<summary>Code:</summary>

```python
class ProcessHabitBoolDelegate(QStyledItemDelegate):

    def __init__(self, parent: QAbstractItemView | None = None) -> None:
        """Enable mouse tracking on the table view for hover picker UI."""
        super().__init__(parent)
        self._hover_index: QPersistentModelIndex | None = None
        if parent is not None:
            parent.setMouseTracking(True)
            parent.viewport().installEventFilter(self)

    def detach_from_view(self, table_view: QAbstractItemView) -> None:
        """Release viewport hooks before the table view or delegate is destroyed."""
        self._hover_index = None
        table_view.viewport().removeEventFilter(self)
        self.setParent(None)

    def displayText(self, _value: object, _locale: QLocale | QLocale.Language) -> str:  # noqa: N802
        """Hide stored 0/1 text; checkbox is drawn in paint()."""
        return ""

    def editorEvent(  # noqa: N802
        self,
        event: QEvent,
        model: QAbstractItemModel,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> bool:
        """Set value on click: dual-picker for absent cells, toggle otherwise."""
        if event.type() != QEvent.Type.MouseButtonRelease:
            return False
        mouse_event = event
        if not isinstance(mouse_event, QMouseEvent):
            return False
        if mouse_event.button() != Qt.MouseButton.LeftButton:
            return False

        state = cell_state_from_index(index)
        if state == "absent":
            if not _is_same_cell(index, self._hover_index):
                return False
            pick = _pick_dual_checkbox(option, index, mouse_event)
            if pick is None:
                return False
            new_value = "1" if pick == "checked" else "0"
            return model.setData(index, new_value, Qt.ItemDataRole.EditRole)

        new_value = next_value_for_toggle(state)
        return model.setData(index, new_value, Qt.ItemDataRole.EditRole)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Track hovered absent cell to show dual-checkbox picker."""
        view = self.parent()
        if not isinstance(view, QAbstractItemView) or watched is not view.viewport():
            return super().eventFilter(watched, event)

        if event.type() == QEvent.Type.MouseMove:
            mouse_event = event
            if isinstance(mouse_event, QMouseEvent):
                idx = view.indexAt(mouse_event.position().toPoint())
                new_hover: QPersistentModelIndex | None = None
                if idx.isValid() and view.itemDelegateForIndex(idx) is self and cell_state_from_index(idx) == "absent":
                    new_hover = QPersistentModelIndex(idx)
                if not _persistent_index_equals(self._hover_index, new_hover):
                    self._hover_index = new_hover
                    view.viewport().update()
        elif event.type() in {QEvent.Type.Leave, QEvent.Type.HoverLeave}:
            if self._hover_index is not None:
                self._hover_index = None
                view.viewport().update()

        return super().eventFilter(watched, event)

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        """Draw row background; draw checkbox(es) for stored or pending values."""
        self.initStyleOption(option, index)
        style = option.widget.style() if option.widget is not None else QApplication.style()

        # Fill cell background (row color from model)
        style.drawPrimitive(QStyle.PrimitiveElement.PE_PanelItemViewItem, option, painter, option.widget)

        state = cell_state_from_index(index)
        if state == "absent":
            if _is_same_cell(index, self._hover_index):
                _paint_dual_checkboxes(painter, option, style)
            return

        check_option = QStyleOptionButton()
        check_option.state = QStyle.StateFlag.State_Enabled | QStyle.StateFlag.State_Active
        if state == "checked":
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

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QAbstractItemView | None = None) -> None
```

Enable mouse tracking on the table view for hover picker UI.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QAbstractItemView | None = None) -> None:
        super().__init__(parent)
        self._hover_index: QPersistentModelIndex | None = None
        if parent is not None:
            parent.setMouseTracking(True)
            parent.viewport().installEventFilter(self)
```

</details>

### ⚙️ Method `detach_from_view`

```python
def detach_from_view(self, table_view: QAbstractItemView) -> None
```

Release viewport hooks before the table view or delegate is destroyed.

<details>
<summary>Code:</summary>

```python
def detach_from_view(self, table_view: QAbstractItemView) -> None:
        self._hover_index = None
        table_view.viewport().removeEventFilter(self)
        self.setParent(None)
```

</details>

### ⚙️ Method `displayText`

```python
def displayText(self, _value: object, _locale: QLocale | QLocale.Language) -> str
```

Hide stored 0/1 text; checkbox is drawn in paint().

<details>
<summary>Code:</summary>

```python
def displayText(self, _value: object, _locale: QLocale | QLocale.Language) -> str:  # noqa: N802
        return ""
```

</details>

### ⚙️ Method `editorEvent`

```python
def editorEvent(self, event: QEvent, model: QAbstractItemModel, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> bool
```

Set value on click: dual-picker for absent cells, toggle otherwise.

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

        state = cell_state_from_index(index)
        if state == "absent":
            if not _is_same_cell(index, self._hover_index):
                return False
            pick = _pick_dual_checkbox(option, index, mouse_event)
            if pick is None:
                return False
            new_value = "1" if pick == "checked" else "0"
            return model.setData(index, new_value, Qt.ItemDataRole.EditRole)

        new_value = next_value_for_toggle(state)
        return model.setData(index, new_value, Qt.ItemDataRole.EditRole)
```

</details>

### ⚙️ Method `eventFilter`

```python
def eventFilter(self, watched: QObject, event: QEvent) -> bool
```

Track hovered absent cell to show dual-checkbox picker.

<details>
<summary>Code:</summary>

```python
def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        view = self.parent()
        if not isinstance(view, QAbstractItemView) or watched is not view.viewport():
            return super().eventFilter(watched, event)

        if event.type() == QEvent.Type.MouseMove:
            mouse_event = event
            if isinstance(mouse_event, QMouseEvent):
                idx = view.indexAt(mouse_event.position().toPoint())
                new_hover: QPersistentModelIndex | None = None
                if idx.isValid() and view.itemDelegateForIndex(idx) is self and cell_state_from_index(idx) == "absent":
                    new_hover = QPersistentModelIndex(idx)
                if not _persistent_index_equals(self._hover_index, new_hover):
                    self._hover_index = new_hover
                    view.viewport().update()
        elif event.type() in {QEvent.Type.Leave, QEvent.Type.HoverLeave}:
            if self._hover_index is not None:
                self._hover_index = None
                view.viewport().update()

        return super().eventFilter(watched, event)
```

</details>

### ⚙️ Method `paint`

```python
def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> None
```

Draw row background; draw checkbox(es) for stored or pending values.

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
        style = option.widget.style() if option.widget is not None else QApplication.style()

        # Fill cell background (row color from model)
        style.drawPrimitive(QStyle.PrimitiveElement.PE_PanelItemViewItem, option, painter, option.widget)

        state = cell_state_from_index(index)
        if state == "absent":
            if _is_same_cell(index, self._hover_index):
                _paint_dual_checkboxes(painter, option, style)
            return

        check_option = QStyleOptionButton()
        check_option.state = QStyle.StateFlag.State_Enabled | QStyle.StateFlag.State_Active
        if state == "checked":
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
    text = str(value).strip().lower() if value is not None else ""
    if record_id is None:
        if not text:
            return "absent"
        if text in _TRUTHY_VALUES:
            return "checked"
        if text in _FALSY_VALUES:
            return "unchecked"
        return "absent"
    if text in _TRUTHY_VALUES:
        return "checked"
    return "unchecked"
```

</details>
