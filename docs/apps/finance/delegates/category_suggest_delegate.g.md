---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `category_suggest_delegate.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [📎 Constant `NAME_LOCAL_ROLE`](#-constant-name_local_role)
- [🏛️ Class `CategorySuggestDelegate`](#%EF%B8%8F-class-categorysuggestdelegate)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `clear_suggestions`](#%EF%B8%8F-method-clear_suggestions)
  - [⚙️ Method `editorEvent`](#%EF%B8%8F-method-editorevent)
  - [⚙️ Method `paint`](#%EF%B8%8F-method-paint)
  - [⚙️ Method `set_suggested_categories`](#%EF%B8%8F-method-set_suggested_categories)
  - [⚙️ Method `sizeHint`](#%EF%B8%8F-method-sizehint)

</details>

## 📎 Constant `NAME_LOCAL_ROLE`

```python
NAME_LOCAL_ROLE = Qt.ItemDataRole.UserRole + 1
```

_No docstring provided._

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
        self._paint_category_label(painter, opt, index, text_rect, text_color)

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

    def _category_name_local(self, index: QModelIndex | QPersistentModelIndex) -> str | None:
        value = index.data(NAME_LOCAL_ROLE)
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    def _paint_category_label(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
        text_rect: QRect,
        text_color: QColor,
    ) -> None:
        """Draw main category text and optional gray smaller local name."""
        main_text = option.text
        name_local = self._category_name_local(index)

        painter.setPen(text_color)
        painter.setFont(option.font)
        main_metrics = QFontMetrics(option.font)
        flags = int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft | Qt.TextFlag.TextSingleLine)

        if not name_local:
            painter.drawText(text_rect, flags, main_text)
            return

        local_font = QFont(option.font)
        base_size = option.font.pointSizeF()
        if base_size <= 0:
            base_size = float(option.font.pointSize() or 9)
        local_font.setPointSizeF(max(_NAME_LOCAL_MIN_POINT_SIZE, base_size * _NAME_LOCAL_FONT_SCALE))
        local_metrics = QFontMetrics(local_font)
        local_text = f" ({name_local})"

        available = max(0, text_rect.width())
        main_width = main_metrics.horizontalAdvance(main_text)
        local_width = local_metrics.horizontalAdvance(local_text)

        if main_width + local_width <= available:
            painter.drawText(text_rect, flags, main_text)
            local_rect = QRect(text_rect.left() + main_width, text_rect.top(), local_width, text_rect.height())
            painter.setPen(_NAME_LOCAL_COLOR)
            painter.setFont(local_font)
            painter.drawText(local_rect, flags, local_text)
            return

        # Prefer keeping local name visible when space is tight: elide main text.
        remaining_for_main = max(0, available - local_width)
        elided_main = main_metrics.elidedText(main_text, Qt.TextElideMode.ElideRight, remaining_for_main)
        elided_main_width = main_metrics.horizontalAdvance(elided_main)
        painter.drawText(text_rect, flags, elided_main)
        if elided_main_width < available:
            local_rect = QRect(
                text_rect.left() + elided_main_width,
                text_rect.top(),
                available - elided_main_width,
                text_rect.height(),
            )
            painter.setPen(_NAME_LOCAL_COLOR)
            painter.setFont(local_font)
            painter.drawText(
                local_rect,
                flags,
                local_metrics.elidedText(local_text, Qt.TextElideMode.ElideRight, local_rect.width()),
            )

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
        self._paint_category_label(painter, opt, index, text_rect, text_color)

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
