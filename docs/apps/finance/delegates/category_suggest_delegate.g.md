---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `category_suggest_delegate.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `CategorySuggestDelegate`](#%EF%B8%8F-class-categorysuggestdelegate)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `clear_suggestions`](#%EF%B8%8F-method-clear_suggestions)
  - [⚙️ Method `editorEvent`](#%EF%B8%8F-method-editorevent)
  - [⚙️ Method `paint`](#%EF%B8%8F-method-paint)
  - [⚙️ Method `set_suggested_categories`](#%EF%B8%8F-method-set_suggested_categories)
  - [⚙️ Method `sizeHint`](#%EF%B8%8F-method-sizehint)

</details>

## 🏛️ Class `CategorySuggestDelegate`

```python
class CategorySuggestDelegate(QStyledItemDelegate)
```

Paint category rows with an opaque Use button on the right for suggestions.

<details>
<summary>Code:</summary>

```python
class CategorySuggestDelegate(QStyledItemDelegate):

    use_clicked = Signal(str)

    def __init__(self, parent: QObject | None = None) -> None:
        """Initialize the delegate."""
        super().__init__(parent)
        self._suggested: set[str] = set()

    def clear_suggestions(self) -> None:
        """Clear all suggested categories."""
        self.set_suggested_categories([])

    def editorEvent(  # noqa: N802
        self,
        event: QEvent,
        model: QAbstractItemModel,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> bool:
        """Handle clicks on the Use button."""
        category_name = self._category_name(index)
        if not category_name or category_name not in self._suggested:
            return super().editorEvent(event, model, option, index)

        if (
            isinstance(event, QMouseEvent)
            and event.type() == QEvent.Type.MouseButtonRelease
            and event.button() == Qt.MouseButton.LeftButton
        ):
            button_rect = self._button_rect(option.rect, option)
            if button_rect.contains(event.position().toPoint()):
                self.use_clicked.emit(category_name)
                return True

        return super().editorEvent(event, model, option, index)

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        """Paint category text on the left and Use button on the right when suggested."""
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)

        category_name = self._category_name(index)
        show_button = bool(category_name and category_name in self._suggested)
        reserved = (self._button_width(opt) + _BUTTON_MARGIN) if show_button else 0

        if opt.state & QStyle.StateFlag.State_Selected:
            background = _ROW_SELECTED_BG
            text_color = QColor("#000000")
        elif opt.state & QStyle.StateFlag.State_MouseOver:
            background = _ROW_HOVER_BG
            text_color = opt.palette.text().color()
        else:
            background = opt.palette.base().color()
            text_color = opt.palette.text().color()

        painter.save()
        painter.fillRect(option.rect, background)

        text_rect = option.rect.adjusted(6, 0, -(reserved + 4), 0)
        painter.setPen(text_color)
        painter.setFont(opt.font)
        painter.drawText(
            text_rect,
            int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft | Qt.TextFlag.TextSingleLine),
            opt.text,
        )

        if show_button:
            self._paint_use_button(painter, opt)
        painter.restore()

    def set_suggested_categories(self, category_names: Collection[str]) -> None:
        """Replace the set of categories that show a Use button."""
        self._suggested = {str(name) for name in category_names if name}

    def sizeHint(  # noqa: N802
        self,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> QSize:
        """Keep enough vertical space for the Use button."""
        hint = super().sizeHint(option, index)
        category_name = self._category_name(index)
        if category_name and category_name in self._suggested:
            hint.setHeight(max(hint.height(), _BUTTON_HEIGHT + 2 * _BUTTON_MARGIN))
        return hint

    def _button_rect(self, item_rect: QRect, option: QStyleOptionViewItem) -> QRect:
        width = self._button_width(option)
        height = min(_BUTTON_HEIGHT, max(16, item_rect.height() - 2 * _BUTTON_MARGIN))
        x = item_rect.right() - width - _BUTTON_MARGIN + 1
        y = item_rect.top() + (item_rect.height() - height) // 2
        return QRect(x, y, width, height)

    def _button_width(self, option: QStyleOptionViewItem) -> int:
        metrics = QFontMetrics(option.font)
        return metrics.horizontalAdvance(_BUTTON_TEXT) + 2 * _BUTTON_PADDING_X

    def _category_name(self, index: QModelIndex | QPersistentModelIndex) -> str | None:
        value = index.data(Qt.ItemDataRole.UserRole)
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    def _paint_use_button(self, painter: QPainter, option: QStyleOptionViewItem) -> None:
        button_rect = self._button_rect(option.rect, option)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, on=True)
        painter.setPen(QPen(_BUTTON_BORDER, 1))
        painter.setBrush(_BUTTON_BG)
        painter.drawRoundedRect(button_rect.adjusted(0, 0, -1, -1), 4, 4)
        painter.setPen(_BUTTON_TEXT_COLOR)
        painter.setFont(option.font)
        painter.drawText(button_rect, int(Qt.AlignmentFlag.AlignCenter), _BUTTON_TEXT)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QObject | None = None) -> None
```

Initialize the delegate.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._suggested: set[str] = set()
```

</details>

### ⚙️ Method `clear_suggestions`

```python
def clear_suggestions(self) -> None
```

Clear all suggested categories.

<details>
<summary>Code:</summary>

```python
def clear_suggestions(self) -> None:
        self.set_suggested_categories([])
```

</details>

### ⚙️ Method `editorEvent`

```python
def editorEvent(self, event: QEvent, model: QAbstractItemModel, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> bool
```

Handle clicks on the Use button.

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
        category_name = self._category_name(index)
        if not category_name or category_name not in self._suggested:
            return super().editorEvent(event, model, option, index)

        if (
            isinstance(event, QMouseEvent)
            and event.type() == QEvent.Type.MouseButtonRelease
            and event.button() == Qt.MouseButton.LeftButton
        ):
            button_rect = self._button_rect(option.rect, option)
            if button_rect.contains(event.position().toPoint()):
                self.use_clicked.emit(category_name)
                return True

        return super().editorEvent(event, model, option, index)
```

</details>

### ⚙️ Method `paint`

```python
def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> None
```

Paint category text on the left and Use button on the right when suggested.

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

        category_name = self._category_name(index)
        show_button = bool(category_name and category_name in self._suggested)
        reserved = (self._button_width(opt) + _BUTTON_MARGIN) if show_button else 0

        if opt.state & QStyle.StateFlag.State_Selected:
            background = _ROW_SELECTED_BG
            text_color = QColor("#000000")
        elif opt.state & QStyle.StateFlag.State_MouseOver:
            background = _ROW_HOVER_BG
            text_color = opt.palette.text().color()
        else:
            background = opt.palette.base().color()
            text_color = opt.palette.text().color()

        painter.save()
        painter.fillRect(option.rect, background)

        text_rect = option.rect.adjusted(6, 0, -(reserved + 4), 0)
        painter.setPen(text_color)
        painter.setFont(opt.font)
        painter.drawText(
            text_rect,
            int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft | Qt.TextFlag.TextSingleLine),
            opt.text,
        )

        if show_button:
            self._paint_use_button(painter, opt)
        painter.restore()
```

</details>

### ⚙️ Method `set_suggested_categories`

```python
def set_suggested_categories(self, category_names: Collection[str]) -> None
```

Replace the set of categories that show a Use button.

<details>
<summary>Code:</summary>

```python
def set_suggested_categories(self, category_names: Collection[str]) -> None:
        self._suggested = {str(name) for name in category_names if name}
```

</details>

### ⚙️ Method `sizeHint`

```python
def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> QSize
```

Keep enough vertical space for the Use button.

<details>
<summary>Code:</summary>

```python
def sizeHint(  # noqa: N802
        self,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> QSize:
        hint = super().sizeHint(option, index)
        category_name = self._category_name(index)
        if category_name and category_name in self._suggested:
            hint.setHeight(max(hint.height(), _BUTTON_HEIGHT + 2 * _BUTTON_MARGIN))
        return hint
```

</details>
