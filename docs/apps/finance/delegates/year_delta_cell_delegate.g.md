---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `year_delta_cell_delegate.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `YearDeltaCellDelegate`](#%EF%B8%8F-class-yeardeltacelldelegate)
  - [⚙️ Method `paint`](#%EF%B8%8F-method-paint)
  - [⚙️ Method `sizeHint`](#%EF%B8%8F-method-sizehint)

</details>

## 🏛️ Class `YearDeltaCellDelegate`

```python
class YearDeltaCellDelegate(QStyledItemDelegate)
```

Paint a delta on the first line and its baseline amount smaller underneath.

<details>
<summary>Code:</summary>

```python
class YearDeltaCellDelegate(QStyledItemDelegate):

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        """Paint one line, or a delta plus a smaller baseline when the text has two lines."""
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)
        text = opt.text
        first, separator, second = text.partition("\n")
        if not separator or not second.strip():
            super().paint(painter, option, index)
            return

        opt.text = ""
        widget = opt.widget
        style = widget.style() if widget is not None else QApplication.style()
        style.drawControl(QStyle.ControlElement.CE_ItemViewItem, opt, painter, widget)

        text_rect = style.subElementRect(QStyle.SubElement.SE_ItemViewItemText, opt, widget)
        small_font = _smaller_font(opt.font)
        first_height = QFontMetrics(opt.font).height()
        second_height = QFontMetrics(small_font).height()
        block_height = first_height + _LINE_GAP + second_height
        top = text_rect.top() + max(0, (text_rect.height() - block_height) // 2)

        selected = bool(opt.state & QStyle.StateFlag.State_Selected)
        painter.save()
        if selected:
            painter.setPen(opt.palette.highlightedText().color())
        else:
            painter.setPen(opt.palette.text().color())
        painter.setFont(opt.font)
        painter.drawText(
            QRect(text_rect.left(), top, text_rect.width(), first_height),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            first,
        )
        painter.setFont(small_font)
        painter.drawText(
            QRect(text_rect.left(), top + first_height + _LINE_GAP, text_rect.width(), second_height),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            second,
        )
        painter.restore()

    def sizeHint(  # noqa: N802
        self,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> QSize:
        """Grow the row when the cell carries a baseline under the delta."""
        hint = super().sizeHint(option, index)
        text = str(index.data(Qt.ItemDataRole.DisplayRole) or "")
        first, separator, second = text.partition("\n")
        if not separator or not second.strip():
            return hint
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)
        small_font = _smaller_font(opt.font)
        width = max(
            QFontMetrics(opt.font).horizontalAdvance(first),
            QFontMetrics(small_font).horizontalAdvance(second),
        )
        height = QFontMetrics(opt.font).height() + _LINE_GAP + QFontMetrics(small_font).height() + _TEXT_PADDING
        return QSize(max(hint.width(), width + _TEXT_PADDING), max(hint.height(), height))
```

</details>

### ⚙️ Method `paint`

```python
def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> None
```

Paint one line, or a delta plus a smaller baseline when the text has two lines.

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
        text = opt.text
        first, separator, second = text.partition("\n")
        if not separator or not second.strip():
            super().paint(painter, option, index)
            return

        opt.text = ""
        widget = opt.widget
        style = widget.style() if widget is not None else QApplication.style()
        style.drawControl(QStyle.ControlElement.CE_ItemViewItem, opt, painter, widget)

        text_rect = style.subElementRect(QStyle.SubElement.SE_ItemViewItemText, opt, widget)
        small_font = _smaller_font(opt.font)
        first_height = QFontMetrics(opt.font).height()
        second_height = QFontMetrics(small_font).height()
        block_height = first_height + _LINE_GAP + second_height
        top = text_rect.top() + max(0, (text_rect.height() - block_height) // 2)

        selected = bool(opt.state & QStyle.StateFlag.State_Selected)
        painter.save()
        if selected:
            painter.setPen(opt.palette.highlightedText().color())
        else:
            painter.setPen(opt.palette.text().color())
        painter.setFont(opt.font)
        painter.drawText(
            QRect(text_rect.left(), top, text_rect.width(), first_height),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            first,
        )
        painter.setFont(small_font)
        painter.drawText(
            QRect(text_rect.left(), top + first_height + _LINE_GAP, text_rect.width(), second_height),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            second,
        )
        painter.restore()
```

</details>

### ⚙️ Method `sizeHint`

```python
def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> QSize
```

Grow the row when the cell carries a baseline under the delta.

<details>
<summary>Code:</summary>

```python
def sizeHint(  # noqa: N802
        self,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> QSize:
        hint = super().sizeHint(option, index)
        text = str(index.data(Qt.ItemDataRole.DisplayRole) or "")
        first, separator, second = text.partition("\n")
        if not separator or not second.strip():
            return hint
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)
        small_font = _smaller_font(opt.font)
        width = max(
            QFontMetrics(opt.font).horizontalAdvance(first),
            QFontMetrics(small_font).horizontalAdvance(second),
        )
        height = QFontMetrics(opt.font).height() + _LINE_GAP + QFontMetrics(small_font).height() + _TEXT_PADDING
        return QSize(max(hint.width(), width + _TEXT_PADDING), max(hint.height(), height))
```

</details>
