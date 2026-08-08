---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `name_local_list_delegate.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `NameLocalLayout`](#%EF%B8%8F-class-namelocallayout)
- [🏛️ Class `NameLocalListDelegate`](#%EF%B8%8F-class-namelocallistdelegate)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `paint`](#%EF%B8%8F-method-paint)
  - [⚙️ Method `sizeHint`](#%EF%B8%8F-method-sizehint)

</details>

## 🏛️ Class `NameLocalLayout`

```python
class NameLocalLayout(StrEnum)
```

How main and local labels are arranged relative to the decoration.

<details>
<summary>Code:</summary>

```python
class NameLocalLayout(StrEnum):

    LIST = "list"
    ICON = "icon"
```

</details>

## 🏛️ Class `NameLocalListDelegate`

```python
class NameLocalListDelegate(QStyledItemDelegate)
```

Paint `DisplayRole` on the first line and `NAME_LOCAL_ROLE` below in gray.

<details>
<summary>Code:</summary>

```python
class NameLocalListDelegate(QStyledItemDelegate):

    def __init__(
        self,
        parent: QObject | None = None,
        *,
        layout: NameLocalLayout = NameLocalLayout.LIST,
    ) -> None:
        """Initialize the delegate.

        Args:

        - `layout` (`NameLocalLayout`): `LIST` places text beside the icon; `ICON` places
          text under the icon (centered).

        """
        super().__init__(parent)
        self._layout = layout

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        """Paint decoration plus one or two text lines."""
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)

        painter.save()
        if self._layout == NameLocalLayout.LIST:
            if opt.state & QStyle.StateFlag.State_Selected:
                painter.fillRect(option.rect, opt.palette.highlight())
                text_color = opt.palette.highlightedText().color()
            elif opt.state & QStyle.StateFlag.State_MouseOver:
                painter.fillRect(option.rect, opt.palette.alternateBase())
                text_color = opt.palette.text().color()
            else:
                painter.fillRect(option.rect, opt.palette.base())
                text_color = opt.palette.text().color()
        else:
            # Icon grids keep selection chrome in the view stylesheet (border only).
            text_color = opt.palette.text().color()

        decoration_rect = self._decoration_rect(opt)
        if not opt.icon.isNull() and decoration_rect.isValid():
            mode = QIcon.Mode.Selected if opt.state & QStyle.StateFlag.State_Selected else QIcon.Mode.Normal
            opt.icon.paint(painter, decoration_rect, Qt.AlignmentFlag.AlignCenter, mode, QIcon.State.Off)

        text_rect = self._text_rect(opt, decoration_rect)
        self._paint_labels(painter, opt, index, text_rect, text_color)
        painter.restore()

    def sizeHint(  # noqa: N802
        self,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> QSize:
        """Reserve vertical space for an optional local-name line."""
        hint = super().sizeHint(option, index)
        name_local = self._name_local(index)
        if not name_local:
            return hint

        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)
        local_height = QFontMetrics(self._local_font(opt.font)).height()
        if self._layout == NameLocalLayout.LIST:
            main_height = QFontMetrics(opt.font).height()
            needed = max(opt.decorationSize.height(), main_height + local_height + _LINE_GAP + 4)
            hint.setHeight(max(hint.height(), needed))
        else:
            hint.setHeight(hint.height() + local_height + _LINE_GAP)
        return hint

    def _decoration_rect(self, option: QStyleOptionViewItem) -> QRect:
        if option.icon.isNull():
            return QRect()
        size = option.decorationSize
        if self._layout == NameLocalLayout.ICON:
            x = option.rect.x() + max(0, (option.rect.width() - size.width()) // 2)
            y = option.rect.y() + 4
            return QRect(x, y, size.width(), size.height())
        x = option.rect.x() + 4
        y = option.rect.y() + max(0, (option.rect.height() - size.height()) // 2)
        return QRect(x, y, size.width(), size.height())

    def _local_font(self, base_font: QFont) -> QFont:
        local_font = QFont(base_font)
        base_size = base_font.pointSizeF()
        if base_size <= 0:
            base_size = float(base_font.pointSize() or 9)
        local_font.setPointSizeF(max(_NAME_LOCAL_MIN_POINT_SIZE, base_size * _NAME_LOCAL_FONT_SCALE))
        return local_font

    def _name_local(self, index: QModelIndex | QPersistentModelIndex) -> str | None:
        value = index.data(NAME_LOCAL_ROLE)
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    def _paint_labels(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
        text_rect: QRect,
        text_color: QColor,
    ) -> None:
        main_text = option.text
        name_local = self._name_local(index)
        main_metrics = QFontMetrics(option.font)

        if not name_local:
            painter.setPen(text_color)
            painter.setFont(option.font)
            flags = (
                Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop | Qt.TextFlag.TextSingleLine
                if self._layout == NameLocalLayout.ICON
                else Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft | Qt.TextFlag.TextSingleLine
            )
            painter.drawText(text_rect, int(flags), main_text)
            return

        local_font = self._local_font(option.font)
        local_metrics = QFontMetrics(local_font)
        main_height = main_metrics.height()
        local_height = local_metrics.height()

        if self._layout == NameLocalLayout.ICON:
            main_rect = QRect(text_rect.x(), text_rect.y(), text_rect.width(), main_height)
            local_rect = QRect(
                text_rect.x(),
                main_rect.bottom() + _LINE_GAP,
                text_rect.width(),
                local_height,
            )
            center_flags = int(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop | Qt.TextFlag.TextSingleLine)
            painter.setPen(text_color)
            painter.setFont(option.font)
            painter.drawText(
                main_rect,
                center_flags,
                main_metrics.elidedText(main_text, Qt.TextElideMode.ElideRight, main_rect.width()),
            )
            painter.setPen(_NAME_LOCAL_COLOR)
            painter.setFont(local_font)
            painter.drawText(
                local_rect,
                center_flags,
                local_metrics.elidedText(name_local, Qt.TextElideMode.ElideRight, local_rect.width()),
            )
            return

        total_height = main_height + _LINE_GAP + local_height
        top = text_rect.y() + max(0, (text_rect.height() - total_height) // 2)
        main_rect = QRect(text_rect.x(), top, text_rect.width(), main_height)
        local_rect = QRect(
            text_rect.x(),
            top + main_height + _LINE_GAP,
            text_rect.width(),
            local_height,
        )
        left_flags = int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter | Qt.TextFlag.TextSingleLine)
        painter.setPen(text_color)
        painter.setFont(option.font)
        painter.drawText(
            main_rect,
            left_flags,
            main_metrics.elidedText(main_text, Qt.TextElideMode.ElideRight, main_rect.width()),
        )
        painter.setPen(_NAME_LOCAL_COLOR)
        painter.setFont(local_font)
        painter.drawText(
            local_rect,
            left_flags,
            local_metrics.elidedText(name_local, Qt.TextElideMode.ElideRight, local_rect.width()),
        )

    def _text_rect(self, option: QStyleOptionViewItem, decoration_rect: QRect) -> QRect:
        if self._layout == NameLocalLayout.ICON:
            y = decoration_rect.bottom() + 4 if decoration_rect.isValid() else option.rect.y() + 4
            return QRect(
                option.rect.x() + _TEXT_PADDING_X,
                y,
                max(0, option.rect.width() - 2 * _TEXT_PADDING_X),
                max(0, option.rect.bottom() - y),
            )
        x = (
            decoration_rect.right() + _TEXT_PADDING_X
            if decoration_rect.isValid()
            else option.rect.x() + _TEXT_PADDING_X
        )
        return QRect(x, option.rect.y(), max(0, option.rect.right() - x - 4), option.rect.height())
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QObject | None = None, *, layout: NameLocalLayout = NameLocalLayout.LIST) -> None
```

Initialize the delegate.

Args:

- `layout` ([`NameLocalLayout`](#%EF%B8%8F-class-namelocallayout)): `LIST` places text beside the icon; `ICON` places
  text under the icon (centered).

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        parent: QObject | None = None,
        *,
        layout: NameLocalLayout = NameLocalLayout.LIST,
    ) -> None:
        super().__init__(parent)
        self._layout = layout
```

</details>

### ⚙️ Method `paint`

```python
def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> None
```

Paint decoration plus one or two text lines.

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

        painter.save()
        if self._layout == NameLocalLayout.LIST:
            if opt.state & QStyle.StateFlag.State_Selected:
                painter.fillRect(option.rect, opt.palette.highlight())
                text_color = opt.palette.highlightedText().color()
            elif opt.state & QStyle.StateFlag.State_MouseOver:
                painter.fillRect(option.rect, opt.palette.alternateBase())
                text_color = opt.palette.text().color()
            else:
                painter.fillRect(option.rect, opt.palette.base())
                text_color = opt.palette.text().color()
        else:
            # Icon grids keep selection chrome in the view stylesheet (border only).
            text_color = opt.palette.text().color()

        decoration_rect = self._decoration_rect(opt)
        if not opt.icon.isNull() and decoration_rect.isValid():
            mode = QIcon.Mode.Selected if opt.state & QStyle.StateFlag.State_Selected else QIcon.Mode.Normal
            opt.icon.paint(painter, decoration_rect, Qt.AlignmentFlag.AlignCenter, mode, QIcon.State.Off)

        text_rect = self._text_rect(opt, decoration_rect)
        self._paint_labels(painter, opt, index, text_rect, text_color)
        painter.restore()
```

</details>

### ⚙️ Method `sizeHint`

```python
def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> QSize
```

Reserve vertical space for an optional local-name line.

<details>
<summary>Code:</summary>

```python
def sizeHint(  # noqa: N802
        self,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> QSize:
        hint = super().sizeHint(option, index)
        name_local = self._name_local(index)
        if not name_local:
            return hint

        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)
        local_height = QFontMetrics(self._local_font(opt.font)).height()
        if self._layout == NameLocalLayout.LIST:
            main_height = QFontMetrics(opt.font).height()
            needed = max(opt.decorationSize.height(), main_height + local_height + _LINE_GAP + 4)
            hint.setHeight(max(hint.height(), needed))
        else:
            hint.setHeight(hint.height() + local_height + _LINE_GAP)
        return hint
```

</details>
