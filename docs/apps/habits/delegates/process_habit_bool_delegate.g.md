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
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `detach_from_view`](#%EF%B8%8F-method-detach_from_view)
  - [⚙️ Method `displayText`](#%EF%B8%8F-method-displaytext)
  - [⚙️ Method `editorEvent`](#%EF%B8%8F-method-editorevent)
  - [⚙️ Method `eventFilter`](#%EF%B8%8F-method-eventfilter)
  - [⚙️ Method `paint`](#%EF%B8%8F-method-paint)
  - [⚙️ Method `sizeHint`](#%EF%B8%8F-method-sizehint)
- [🔧 Function `cell_state_from_index`](#-function-cell_state_from_index)
- [🔧 Function `next_value_for_toggle`](#-function-next_value_for_toggle)
- [🔧 Function `parse_process_habit_bool`](#-function-parse_process_habit_bool)

</details>

## 🏛️ Class `ProcessHabitBoolDelegate`

```python
class ProcessHabitBoolDelegate(QStyledItemDelegate)
```

Paint dashboard-style circles; hover picker for empty cells, toggle otherwise.

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
        """Hide stored 0/1 text; circle is drawn in paint()."""
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
        """Track hovered absent cell to show dual-circle picker."""
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
        """Draw row background and dashboard-style day circles."""
        self.initStyleOption(option, index)
        style = option.widget.style() if option.widget is not None else QApplication.style()

        # Fill cell background (row color from model)
        style.drawPrimitive(QStyle.PrimitiveElement.PE_PanelItemViewItem, option, painter, option.widget)

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        state = cell_state_from_index(index)
        if state == "absent":
            if _is_same_cell(index, self._hover_index):
                _paint_dual_circles(painter, option)
            else:
                _paint_day_circle(painter, _centered_circle_rect(option.rect), None, font=option.font)
        elif state == "checked":
            _paint_day_circle(painter, _centered_circle_rect(option.rect), 1, font=option.font)
        else:
            _paint_day_circle(painter, _centered_circle_rect(option.rect), 0, font=option.font)
        painter.restore()

    def sizeHint(  # noqa: N802
        self,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> QSize:
        """Keep rows tall enough for dashboard-style circles."""
        hint = super().sizeHint(option, index)
        return QSize(max(hint.width(), 48), max(hint.height(), _MIN_CELL_HEIGHT))
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

Hide stored 0/1 text; circle is drawn in paint().

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

Track hovered absent cell to show dual-circle picker.

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

Draw row background and dashboard-style day circles.

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

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        state = cell_state_from_index(index)
        if state == "absent":
            if _is_same_cell(index, self._hover_index):
                _paint_dual_circles(painter, option)
            else:
                _paint_day_circle(painter, _centered_circle_rect(option.rect), None, font=option.font)
        elif state == "checked":
            _paint_day_circle(painter, _centered_circle_rect(option.rect), 1, font=option.font)
        else:
            _paint_day_circle(painter, _centered_circle_rect(option.rect), 0, font=option.font)
        painter.restore()
```

</details>

### ⚙️ Method `sizeHint`

```python
def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> QSize
```

Keep rows tall enough for dashboard-style circles.

<details>
<summary>Code:</summary>

```python
def sizeHint(  # noqa: N802
        self,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> QSize:
        hint = super().sizeHint(option, index)
        return QSize(max(hint.width(), 48), max(hint.height(), _MIN_CELL_HEIGHT))
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

- [`value`](../dashboard_widgets.g.md#%EF%B8%8F-method-value) (`object`): Display/edit value from the model.
- `record_id` (`object`): First element of UserRole tuple, or `None` if no DB row.

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
