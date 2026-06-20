---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `process_habit_int_delegate.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ProcessHabitIntDelegate`](#️-class-processhabitintdelegate)
  - [⚙️ Method `__init__`](#️-method-__init__)
  - [⚙️ Method `createEditor`](#️-method-createeditor)
  - [⚙️ Method `detach_from_view`](#️-method-detach_from_view)
  - [⚙️ Method `displayText`](#️-method-displaytext)
  - [⚙️ Method `editorEvent`](#️-method-editorevent)
  - [⚙️ Method `eventFilter`](#️-method-eventfilter)
  - [⚙️ Method `paint`](#️-method-paint)
- [🔧 Function `cell_state_from_index`](#-function-cell_state_from_index)
- [🔧 Function `parse_process_habit_int`](#-function-parse_process_habit_int)
- [🔧 Function `_int_picker_rects`](#-function-_int_picker_rects)
- [🔧 Function `_paint_int_picker`](#-function-_paint_int_picker)
- [🔧 Function `_pick_int_picker`](#-function-_pick_int_picker)

</details>

## 🏛️ Class `ProcessHabitIntDelegate`

```python
class ProcessHabitIntDelegate(QStyledItemDelegate)
```

Paint 0/1 as checkboxes or other values as text; hover picker for empty cells.

<details>
<summary>Code:</summary>

```python
class ProcessHabitIntDelegate(QStyledItemDelegate):

    def __init__(self, parent: QAbstractItemView | None = None) -> None:
        """Enable mouse tracking on the table view for hover picker UI."""
        super().__init__(parent)
        self._hover_index: QPersistentModelIndex | None = None
        if parent is not None:
            parent.setMouseTracking(True)
            parent.viewport().installEventFilter(self)

    def createEditor(  # noqa: N802
        self,
        parent: QWidget,
        _option: QStyleOptionViewItem,
        _index: QModelIndex | QPersistentModelIndex,
    ) -> QLineEdit:
        """Line editor with integer validator (double-click / input zone)."""
        editor = QLineEdit(parent)
        editor.setValidator(QIntValidator(editor))
        editor.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return editor

    def detach_from_view(self, table_view: QAbstractItemView) -> None:
        """Release viewport hooks before the table view or delegate is destroyed."""
        self._hover_index = None
        table_view.viewport().removeEventFilter(self)
        self.setParent(None)

    def displayText(self, value: object, _locale: QLocale | QLocale.Language) -> str:  # noqa: N802
        """Hide 0/1 text; checkbox is drawn in paint()."""
        text = str(value).strip() if value is not None else ""
        if text in {"0", "1"}:
            return ""
        return text

    def editorEvent(  # noqa: N802
        self,
        event: QEvent,
        model: QAbstractItemModel,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> bool:
        """Handle picker clicks and 0/1 toggle; leave double-click to the view."""
        if event.type() == QEvent.Type.MouseButtonDblClick:
            return False

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
            pick = _pick_int_picker(option, index, mouse_event)
            if pick is None:
                return False
            if pick == "input":
                view = option.widget
                if isinstance(view, QAbstractItemView):
                    edit_index = model.index(index.row(), index.column(), index.parent())

                    def open_editor() -> None:
                        view.setCurrentIndex(edit_index)
                        view.edit(edit_index)

                    QTimer.singleShot(0, open_editor)
                return True
            new_value = "1" if pick == "one" else "0"
            return model.setData(index, new_value, Qt.ItemDataRole.EditRole)

        if state in {"zero", "one"}:
            new_value = "0" if state == "one" else "1"
            return model.setData(index, new_value, Qt.ItemDataRole.EditRole)

        return False

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Track hovered empty int cell to show picker UI."""
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
        """Draw row background; checkbox, number, or hover picker."""
        self.initStyleOption(option, index)
        style = option.widget.style() if option.widget is not None else QApplication.style()

        style.drawPrimitive(QStyle.PrimitiveElement.PE_PanelItemViewItem, option, painter, option.widget)

        state = cell_state_from_index(index)
        if state == "absent":
            if _is_same_cell(index, self._hover_index):
                _paint_int_picker(painter, option, style)
            return

        if state in {"zero", "one"}:
            check_option = QStyleOptionButton()
            check_option.state = QStyle.StateFlag.State_Enabled | QStyle.StateFlag.State_Active
            if state == "one":
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
            return

        text = str(index.data(Qt.ItemDataRole.DisplayRole) or "")
        if text:
            painter.save()
            painter.setPen(option.palette.color(option.palette.ColorRole.Text))
            painter.drawText(option.rect, int(Qt.AlignmentFlag.AlignCenter), text)
            painter.restore()
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

### ⚙️ Method `createEditor`

```python
def createEditor(self, parent: QWidget, _option: QStyleOptionViewItem, _index: QModelIndex | QPersistentModelIndex) -> QLineEdit
```

Line editor with integer validator (double-click / input zone).

<details>
<summary>Code:</summary>

```python
def createEditor(  # noqa: N802
        self,
        parent: QWidget,
        _option: QStyleOptionViewItem,
        _index: QModelIndex | QPersistentModelIndex,
    ) -> QLineEdit:
        editor = QLineEdit(parent)
        editor.setValidator(QIntValidator(editor))
        editor.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return editor
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
def displayText(self, value: object, _locale: QLocale | QLocale.Language) -> str
```

Hide 0/1 text; checkbox is drawn in paint().

<details>
<summary>Code:</summary>

```python
def displayText(self, value: object, _locale: QLocale | QLocale.Language) -> str:  # noqa: N802
        text = str(value).strip() if value is not None else ""
        if text in {"0", "1"}:
            return ""
        return text
```

</details>

### ⚙️ Method `editorEvent`

```python
def editorEvent(self, event: QEvent, model: QAbstractItemModel, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> bool
```

Handle picker clicks and 0/1 toggle; leave double-click to the view.

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
        if event.type() == QEvent.Type.MouseButtonDblClick:
            return False

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
            pick = _pick_int_picker(option, index, mouse_event)
            if pick is None:
                return False
            if pick == "input":
                view = option.widget
                if isinstance(view, QAbstractItemView):
                    edit_index = model.index(index.row(), index.column(), index.parent())

                    def open_editor() -> None:
                        view.setCurrentIndex(edit_index)
                        view.edit(edit_index)

                    QTimer.singleShot(0, open_editor)
                return True
            new_value = "1" if pick == "one" else "0"
            return model.setData(index, new_value, Qt.ItemDataRole.EditRole)

        if state in {"zero", "one"}:
            new_value = "0" if state == "one" else "1"
            return model.setData(index, new_value, Qt.ItemDataRole.EditRole)

        return False
```

</details>

### ⚙️ Method `eventFilter`

```python
def eventFilter(self, watched: QObject, event: QEvent) -> bool
```

Track hovered empty int cell to show picker UI.

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

Draw row background; checkbox, number, or hover picker.

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

        style.drawPrimitive(QStyle.PrimitiveElement.PE_PanelItemViewItem, option, painter, option.widget)

        state = cell_state_from_index(index)
        if state == "absent":
            if _is_same_cell(index, self._hover_index):
                _paint_int_picker(painter, option, style)
            return

        if state in {"zero", "one"}:
            check_option = QStyleOptionButton()
            check_option.state = QStyle.StateFlag.State_Enabled | QStyle.StateFlag.State_Active
            if state == "one":
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
            return

        text = str(index.data(Qt.ItemDataRole.DisplayRole) or "")
        if text:
            painter.save()
            painter.setPen(option.palette.color(option.palette.ColorRole.Text))
            painter.drawText(option.rect, int(Qt.AlignmentFlag.AlignCenter), text)
            painter.restore()
```

</details>

## 🔧 Function `cell_state_from_index`

```python
def cell_state_from_index(index: QModelIndex | QPersistentModelIndex) -> ProcessHabitIntState
```

Return visual state for an integer process-habit cell.

<details>
<summary>Code:</summary>

```python
def cell_state_from_index(index: QModelIndex | QPersistentModelIndex) -> ProcessHabitIntState:
    stored = index.data(Qt.ItemDataRole.UserRole)
    record_id = stored[0] if stored else None
    display = index.data(Qt.ItemDataRole.DisplayRole)
    return parse_process_habit_int(display, record_id)
```

</details>

## 🔧 Function `parse_process_habit_int`

```python
def parse_process_habit_int(value: object, record_id: object) -> ProcessHabitIntState
```

Map model storage to absent / zero / one / number.

<details>
<summary>Code:</summary>

```python
def parse_process_habit_int(value: object, record_id: object) -> ProcessHabitIntState:
    text = str(value).strip() if value is not None else ""
    if record_id is None and not text:
        return "absent"
    if not text:
        return "absent"
    try:
        number = int(text)
    except ValueError:
        return "absent"
    if number == 0:
        return "zero"
    if number == 1:
        return "one"
    return "number"
```

</details>

## 🔧 Function `_int_picker_rects`

```python
def _int_picker_rects(outer: QRect, indicator_size: QSize) -> tuple[QRect, QRect, QRect]
```

Return (unchecked_rect, checked_rect, input_rect) for hover picker.

<details>
<summary>Code:</summary>

```python
def _int_picker_rects(outer: QRect, indicator_size: QSize) -> tuple[QRect, QRect, QRect]:
    input_w = max(_INPUT_MIN_WIDTH, min(56, outer.width() // 3))
    total_w = indicator_size.width() * 2 + _PICKER_GAP * 2 + input_w
    start_x = outer.x() + max(0, (outer.width() - total_w) // 2)
    y = outer.y() + (outer.height() - indicator_size.height()) // 2
    unchecked = QRect(start_x, y, indicator_size.width(), indicator_size.height())
    checked = QRect(
        start_x + indicator_size.width() + _PICKER_GAP,
        y,
        indicator_size.width(),
        indicator_size.height(),
    )
    input_rect = QRect(
        start_x + (indicator_size.width() + _PICKER_GAP) * 2,
        outer.y() + (outer.height() - indicator_size.height()) // 2,
        input_w,
        indicator_size.height(),
    )
    return unchecked, checked, input_rect
```

</details>

## 🔧 Function `_paint_int_picker`

```python
def _paint_int_picker(painter: QPainter, option: QStyleOptionViewItem, style: QStyle) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _paint_int_picker(painter: QPainter, option: QStyleOptionViewItem, style: QStyle) -> None:
    indicator_size = _checkbox_indicator_size(style, option.widget)
    unchecked_rect, checked_rect, input_rect = _int_picker_rects(option.rect, indicator_size)
    _paint_checkbox(painter, unchecked_rect, checked=False, style=style, widget=option.widget)
    _paint_checkbox(painter, checked_rect, checked=True, style=style, widget=option.widget)

    painter.save()
    border = option.palette.color(option.palette.ColorRole.Mid)
    painter.setPen(QPen(border, 1))
    painter.setBrush(QColor(255, 255, 255, 40))
    painter.drawRect(input_rect.adjusted(0, 0, -1, -1))
    painter.setPen(option.palette.color(option.palette.ColorRole.Text))
    painter.drawText(input_rect, int(Qt.AlignmentFlag.AlignCenter), "123")
    painter.restore()
```

</details>

## 🔧 Function `_pick_int_picker`

```python
def _pick_int_picker(option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex, mouse_event: QMouseEvent) -> _IntPick | None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _pick_int_picker(
    option: QStyleOptionViewItem,
    index: QModelIndex | QPersistentModelIndex,
    mouse_event: QMouseEvent,
) -> _IntPick | None:
    view = option.widget
    if view is None:
        return None
    pos = mouse_event.position().toPoint()
    cell_rect = view.visualRect(index)
    if not cell_rect.contains(pos):
        return None

    local = pos - cell_rect.topLeft()
    local_rect = QRect(0, 0, cell_rect.width(), cell_rect.height())
    style = view.style() if view is not None else QApplication.style()
    indicator_size = _checkbox_indicator_size(style, view)
    unchecked_rect, checked_rect, input_rect = _int_picker_rects(local_rect, indicator_size)

    if input_rect.contains(local):
        return "input"
    if checked_rect.contains(local):
        return "one"
    if unchecked_rect.contains(local):
        return "zero"
    return None
```

</details>
