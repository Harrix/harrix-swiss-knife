---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `process_habit_int_delegate.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ProcessHabitIntDelegate`](#%EF%B8%8F-class-processhabitintdelegate)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `createEditor`](#%EF%B8%8F-method-createeditor)
  - [⚙️ Method `detach_from_view`](#%EF%B8%8F-method-detach_from_view)
  - [⚙️ Method `displayText`](#%EF%B8%8F-method-displaytext)
  - [⚙️ Method `editorEvent`](#%EF%B8%8F-method-editorevent)
  - [⚙️ Method `eventFilter`](#%EF%B8%8F-method-eventfilter)
  - [⚙️ Method `paint`](#%EF%B8%8F-method-paint)
  - [⚙️ Method `sizeHint`](#%EF%B8%8F-method-sizehint)
- [🔧 Function `cell_state_from_index`](#-function-cell_state_from_index)
- [🔧 Function `parse_process_habit_int`](#-function-parse_process_habit_int)

</details>

## 🏛️ Class `ProcessHabitIntDelegate`

```python
class ProcessHabitIntDelegate(QStyledItemDelegate)
```

Paint 0/1/number as dashboard circles; hover picker for empty cells.

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

    def displayText(self, _value: object, _locale: QLocale | QLocale.Language) -> str:  # noqa: N802
        """Hide stored values; circle is drawn in paint()."""
        return ""

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
        """Draw row background and dashboard-style day circles."""
        self.initStyleOption(option, index)
        style = option.widget.style() if option.widget is not None else QApplication.style()

        style.drawPrimitive(QStyle.PrimitiveElement.PE_PanelItemViewItem, option, painter, option.widget)

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        state = cell_state_from_index(index)
        if state == "absent":
            if _is_same_cell(index, self._hover_index):
                _paint_int_picker(painter, option)
            else:
                _paint_day_circle(painter, _centered_circle_rect(option.rect), None, font=option.font)
        elif state == "zero":
            _paint_day_circle(painter, _centered_circle_rect(option.rect), 0, font=option.font)
        elif state == "one":
            _paint_day_circle(painter, _centered_circle_rect(option.rect), 1, font=option.font)
        else:
            display = index.data(Qt.ItemDataRole.DisplayRole)
            try:
                value = int(str(display).strip())
            except (TypeError, ValueError):
                value = None
            if value is not None:
                _paint_day_circle(painter, _centered_circle_rect(option.rect), value, font=option.font)
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
def displayText(self, _value: object, _locale: QLocale | QLocale.Language) -> str
```

Hide stored values; circle is drawn in paint().

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

        style.drawPrimitive(QStyle.PrimitiveElement.PE_PanelItemViewItem, option, painter, option.widget)

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        state = cell_state_from_index(index)
        if state == "absent":
            if _is_same_cell(index, self._hover_index):
                _paint_int_picker(painter, option)
            else:
                _paint_day_circle(painter, _centered_circle_rect(option.rect), None, font=option.font)
        elif state == "zero":
            _paint_day_circle(painter, _centered_circle_rect(option.rect), 0, font=option.font)
        elif state == "one":
            _paint_day_circle(painter, _centered_circle_rect(option.rect), 1, font=option.font)
        else:
            display = index.data(Qt.ItemDataRole.DisplayRole)
            try:
                value = int(str(display).strip())
            except (TypeError, ValueError):
                value = None
            if value is not None:
                _paint_day_circle(painter, _centered_circle_rect(option.rect), value, font=option.font)
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
