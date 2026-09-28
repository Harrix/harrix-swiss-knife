---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `day_total_delegate.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `FoodLogDayTotalDelegate`](#%EF%B8%8F-class-foodlogdaytotaldelegate)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `editorEvent`](#%EF%B8%8F-method-editorevent)
  - [⚙️ Method `eventFilter`](#%EF%B8%8F-method-eventfilter)
  - [⚙️ Method `paint`](#%EF%B8%8F-method-paint)
  - [⚙️ Method `set_statuses`](#%EF%B8%8F-method-set_statuses)
- [🏛️ Class `MacrosButtonAppearance`](#%EF%B8%8F-class-macrosbuttonappearance)
- [🔧 Function `apply_food_log_macros_row_heights`](#-function-apply_food_log_macros_row_heights)
- [🔧 Function `food_log_macros_row_height`](#-function-food_log_macros_row_height)
- [🔧 Function `macros_button_appearance`](#-function-macros_button_appearance)
- [🔧 Function `macros_button_rect`](#-function-macros_button_rect)

</details>

## 🏛️ Class `FoodLogDayTotalDelegate`

```python
class FoodLogDayTotalDelegate(QStyledItemDelegate)
```

Paint day calories and a second-line button that opens the macros summary.

<details>
<summary>Code:</summary>

```python
class FoodLogDayTotalDelegate(QStyledItemDelegate):

    macros_requested = Signal(str)

    def __init__(self, parent: QObject | None = None) -> None:
        """Initialize the delegate and track button hover on the food log view.

        Args:

        - `parent` (`QObject | None`): Parent object. A `QTableView` installs the hover filter.

        """
        super().__init__(parent)
        self._statuses: dict[str, DayMacrosStatus] = {}
        self._hover_index = QPersistentModelIndex()
        if isinstance(parent, QTableView):
            parent.viewport().setMouseTracking(True)
            parent.viewport().installEventFilter(self)

    def editorEvent(  # noqa: N802
        self,
        event: QEvent,
        model: QAbstractItemModel,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> bool:
        """Open the day macros dialog when the button is clicked."""
        if (
            isinstance(event, QMouseEvent)
            and event.type() == QEvent.Type.MouseButtonRelease
            and event.button() == Qt.MouseButton.LeftButton
        ):
            day = _day_key(model.index(index.row(), FOOD_LOG_COL_DATE).data())
            button = macros_button_rect(option.rect, option.font)
            if day and button.contains(event.position().toPoint()):
                self.macros_requested.emit(day)
                return True
        return super().editorEvent(event, model, option, index)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Track whether the pointer is over the macros button."""
        view = self.parent()
        if isinstance(view, QTableView) and watched is view.viewport():
            self._update_hover(view, event)
        return super().eventFilter(watched, event)

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        """Paint the calorie total and the macros button under it."""
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)
        day = _day_key(index.sibling(index.row(), FOOD_LOG_COL_DATE).data())
        if not day:
            super().paint(painter, option, index)
            return

        calorie_text = opt.text
        opt.text = ""
        widget = opt.widget
        style = widget.style() if widget is not None else QApplication.style()
        style.drawControl(QStyle.ControlElement.CE_ItemViewItem, opt, painter, widget)

        text_height = QFontMetrics(opt.font).height()
        text_rect = QRect(
            option.rect.left() + _CELL_SIDE_PAD,
            option.rect.top() + _CELL_TOP_PAD,
            max(0, option.rect.width() - (2 * _CELL_SIDE_PAD)),
            text_height,
        )
        painter.save()
        painter.setFont(opt.font)
        text_role = (
            QPalette.ColorRole.HighlightedText
            if opt.state & QStyle.StateFlag.State_Selected
            else QPalette.ColorRole.Text
        )
        painter.setPen(opt.palette.color(text_role))
        painter.drawText(
            text_rect,
            int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter),
            QFontMetrics(opt.font).elidedText(calorie_text, Qt.TextElideMode.ElideRight, text_rect.width()),
        )
        painter.restore()

        appearance = macros_button_appearance(self._statuses.get(day, DayMacrosStatus.MISSING))
        button_font = QFont(opt.font)
        button_font.setBold(False)
        self._paint_button(
            painter,
            macros_button_rect(option.rect, opt.font),
            appearance,
            button_font,
            hovered=self._hover_index.isValid() and self._hover_index == index,
        )

    def set_statuses(self, statuses: dict[str, DayMacrosStatus]) -> None:
        """Replace the cached analysis status for each visible day.

        Args:

        - `statuses` (`dict[str, DayMacrosStatus]`): Date `YYYY-MM-DD` to button state.

        """
        self._statuses = dict(statuses)

    def _paint_button(
        self,
        painter: QPainter,
        rect: QRect,
        appearance: MacrosButtonAppearance,
        font: QFont,
        *,
        hovered: bool,
    ) -> None:
        if rect.width() < _MIN_BUTTON_SIZE or rect.height() < _MIN_BUTTON_SIZE:
            return
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, on=True)
        painter.setPen(QPen(appearance.border, 1))
        painter.setBrush(appearance.hover_background if hovered else appearance.background)
        painter.drawRoundedRect(rect.adjusted(0, 0, -1, -1), _BUTTON_RADIUS, _BUTTON_RADIUS)
        painter.setFont(font)
        painter.setPen(appearance.text)
        label_width = max(0, rect.width() - 12)
        label = QFontMetrics(font).elidedText(appearance.label, Qt.TextElideMode.ElideRight, label_width)
        painter.drawText(rect.adjusted(6, 0, -6, 0), int(Qt.AlignmentFlag.AlignCenter), label)
        painter.restore()

    def _set_button_hover(self, view: QTableView, index: QModelIndex) -> None:
        if (self._hover_index.isValid() and self._hover_index == index) or (
            not self._hover_index.isValid() and not index.isValid()
        ):
            return
        previous_row = self._hover_index.row()
        previous_column = self._hover_index.column()
        had_hover = self._hover_index.isValid()
        self._hover_index = QPersistentModelIndex(index) if index.isValid() else QPersistentModelIndex()
        viewport = view.viewport()
        model = view.model()
        if had_hover and model is not None:
            viewport.update(view.visualRect(model.index(previous_row, previous_column)))
        if index.isValid():
            viewport.update(view.visualRect(index))
        viewport.setCursor(
            Qt.CursorShape.PointingHandCursor if index.isValid() else Qt.CursorShape.ArrowCursor,
        )

    def _update_hover(self, view: QTableView, event: QEvent) -> None:
        if event.type() == QEvent.Type.Leave:
            self._set_button_hover(view, QModelIndex())
            return
        if event.type() != QEvent.Type.MouseMove or not isinstance(event, QMouseEvent):
            return
        pos = event.position().toPoint()
        index = view.indexAt(pos)
        if not index.isValid() or index.column() != FOOD_LOG_COL_TOTAL_PER_DAY:
            self._set_button_hover(view, QModelIndex())
            return
        day = _day_key(index.sibling(index.row(), FOOD_LOG_COL_DATE).data())
        button = macros_button_rect(view.visualRect(index), view.font())
        if day and button.contains(pos):
            self._set_button_hover(view, index)
        else:
            self._set_button_hover(view, QModelIndex())
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QObject | None = None) -> None
```

Initialize the delegate and track button hover on the food log view.

Args:

- `parent` (`QObject | None`): Parent object. A `QTableView` installs the hover filter.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._statuses: dict[str, DayMacrosStatus] = {}
        self._hover_index = QPersistentModelIndex()
        if isinstance(parent, QTableView):
            parent.viewport().setMouseTracking(True)
            parent.viewport().installEventFilter(self)
```

</details>

### ⚙️ Method `editorEvent`

```python
def editorEvent(self, event: QEvent, model: QAbstractItemModel, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> bool
```

Open the day macros dialog when the button is clicked.

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
        if (
            isinstance(event, QMouseEvent)
            and event.type() == QEvent.Type.MouseButtonRelease
            and event.button() == Qt.MouseButton.LeftButton
        ):
            day = _day_key(model.index(index.row(), FOOD_LOG_COL_DATE).data())
            button = macros_button_rect(option.rect, option.font)
            if day and button.contains(event.position().toPoint()):
                self.macros_requested.emit(day)
                return True
        return super().editorEvent(event, model, option, index)
```

</details>

### ⚙️ Method `eventFilter`

```python
def eventFilter(self, watched: QObject, event: QEvent) -> bool
```

Track whether the pointer is over the macros button.

<details>
<summary>Code:</summary>

```python
def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        view = self.parent()
        if isinstance(view, QTableView) and watched is view.viewport():
            self._update_hover(view, event)
        return super().eventFilter(watched, event)
```

</details>

### ⚙️ Method `paint`

```python
def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> None
```

Paint the calorie total and the macros button under it.

<details>
<summary>Code:</summary>

```python
def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)
        day = _day_key(index.sibling(index.row(), FOOD_LOG_COL_DATE).data())
        if not day:
            super().paint(painter, option, index)
            return

        calorie_text = opt.text
        opt.text = ""
        widget = opt.widget
        style = widget.style() if widget is not None else QApplication.style()
        style.drawControl(QStyle.ControlElement.CE_ItemViewItem, opt, painter, widget)

        text_height = QFontMetrics(opt.font).height()
        text_rect = QRect(
            option.rect.left() + _CELL_SIDE_PAD,
            option.rect.top() + _CELL_TOP_PAD,
            max(0, option.rect.width() - (2 * _CELL_SIDE_PAD)),
            text_height,
        )
        painter.save()
        painter.setFont(opt.font)
        text_role = (
            QPalette.ColorRole.HighlightedText
            if opt.state & QStyle.StateFlag.State_Selected
            else QPalette.ColorRole.Text
        )
        painter.setPen(opt.palette.color(text_role))
        painter.drawText(
            text_rect,
            int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter),
            QFontMetrics(opt.font).elidedText(calorie_text, Qt.TextElideMode.ElideRight, text_rect.width()),
        )
        painter.restore()

        appearance = macros_button_appearance(self._statuses.get(day, DayMacrosStatus.MISSING))
        button_font = QFont(opt.font)
        button_font.setBold(False)
        self._paint_button(
            painter,
            macros_button_rect(option.rect, opt.font),
            appearance,
            button_font,
            hovered=self._hover_index.isValid() and self._hover_index == index,
        )
```

</details>

### ⚙️ Method `set_statuses`

```python
def set_statuses(self, statuses: dict[str, DayMacrosStatus]) -> None
```

Replace the cached analysis status for each visible day.

Args:

- `statuses` (`dict[str, DayMacrosStatus]`): Date `YYYY-MM-DD` to button state.

<details>
<summary>Code:</summary>

```python
def set_statuses(self, statuses: dict[str, DayMacrosStatus]) -> None:
        self._statuses = dict(statuses)
```

</details>

## 🏛️ Class `MacrosButtonAppearance`

```python
class MacrosButtonAppearance
```

Label and colors for one macros-button state.

<details>
<summary>Code:</summary>

```python
class MacrosButtonAppearance:

    label: str
    background: QColor
    border: QColor
    text: QColor
    hover_background: QColor
```

</details>

## 🔧 Function `apply_food_log_macros_row_heights`

```python
def apply_food_log_macros_row_heights(view: QTableView) -> None
```

Grow the first row of each day so the macros button fits under the calories.

Args:

- `view` (`QTableView`): Food log table.

<details>
<summary>Code:</summary>

```python
def apply_food_log_macros_row_heights(view: QTableView) -> None:
    model = view.model()
    if model is None:
        return
    dates = [str(model.index(row, FOOD_LOG_COL_DATE).data() or "") for row in range(model.rowCount())]
    starts = {start for start, _count in food_log_day_groups(dates)}
    header = view.verticalHeader()
    default = header.defaultSectionSize()
    if default <= 0:
        default = view.fontMetrics().height() + 8
    tall = max(default, food_log_macros_row_height(view.font()))
    for row in range(model.rowCount()):
        target = tall if row in starts else default
        if view.rowHeight(row) != target:
            view.setRowHeight(row, target)
```

</details>

## 🔧 Function `food_log_macros_row_height`

```python
def food_log_macros_row_height(font: QFont) -> int
```

Return the row height that fits the calorie line and the macros button.

Args:

- `font` (`QFont`): Table font.

Returns:

- `int`: Height in pixels.

<details>
<summary>Code:</summary>

```python
def food_log_macros_row_height(font: QFont) -> int:
    return _CELL_TOP_PAD + QFontMetrics(font).height() + _BUTTON_GAP + _BUTTON_HEIGHT + _CELL_TOP_PAD
```

</details>

## 🔧 Function `macros_button_appearance`

```python
def macros_button_appearance(status: DayMacrosStatus) -> MacrosButtonAppearance
```

Return the label and colors for a day-macros button.

Args:

- `status` ([`DayMacrosStatus`](../day_macros.g.md#%EF%B8%8F-class-daymacrosstatus)): Whether the saved analysis is current, stale, or missing.

Returns:

- [`MacrosButtonAppearance`](#%EF%B8%8F-class-macrosbuttonappearance): Text and colors for that state.

<details>
<summary>Code:</summary>

```python
def macros_button_appearance(status: DayMacrosStatus) -> MacrosButtonAppearance:
    if status is DayMacrosStatus.OK:
        return MacrosButtonAppearance(
            "View macros",
            QColor("#e8f5e9"),
            QColor("#43a047"),
            QColor("#1b5e20"),
            QColor("#c8e6c9"),
        )
    if status is DayMacrosStatus.STALE:
        return MacrosButtonAppearance(
            "Recalculate macros",
            QColor("#fff8e1"),
            QColor("#f9a825"),
            QColor("#e65100"),
            QColor("#ffecb3"),
        )
    return MacrosButtonAppearance(
        "Analyze macros",
        QColor("#1e88e5"),
        QColor("#1565c0"),
        QColor("#ffffff"),
        QColor("#1976d2"),
    )
```

</details>

## 🔧 Function `macros_button_rect`

```python
def macros_button_rect(cell: QRect, font: QFont) -> QRect
```

Return the button rectangle under the calorie line inside `cell`.

Args:

- `cell` (`QRect`): Total-per-day cell, including a merged span.
- `font` (`QFont`): Font used for the calorie line.

Returns:

- `QRect`: Button bounds in the same coordinates as `cell`.

<details>
<summary>Code:</summary>

```python
def macros_button_rect(cell: QRect, font: QFont) -> QRect:
    text_height = QFontMetrics(font).height()
    top = cell.top() + _CELL_TOP_PAD + text_height + _BUTTON_GAP
    return QRect(
        cell.left() + _CELL_SIDE_PAD,
        top,
        max(0, cell.width() - (2 * _CELL_SIDE_PAD)),
        _BUTTON_HEIGHT,
    )
```

</details>
