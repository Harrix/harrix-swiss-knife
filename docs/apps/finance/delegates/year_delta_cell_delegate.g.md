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
  - [⚙️ Method `displayText`](#%EF%B8%8F-method-displaytext)
  - [⚙️ Method `paint`](#%EF%B8%8F-method-paint)
  - [⚙️ Method `sizeHint`](#%EF%B8%8F-method-sizehint)

</details>

## 🏛️ Class `YearDeltaCellDelegate`

```python
class YearDeltaCellDelegate(QStyledItemDelegate)
```

Paint a bold delta on the first line and its baseline amount smaller underneath.

Amounts use the same thousands separators and subscript decimals as report cells.
Column width follows the text, so a stretched table does not keep the cells wide.

<details>
<summary>Code:</summary>

```python
class YearDeltaCellDelegate(QStyledItemDelegate):

    def displayText(self, value: object, _locale: QLocale | QLocale.Language) -> str:  # noqa: N802
        """Format each line with thousands separators and subscript decimals."""
        return "\n".join(_format_amount_line(line) for line in str(value).split("\n"))

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
        delta_font = _bold_font(opt.font)
        small_font = _smaller_font(opt.font)
        first_height = QFontMetrics(delta_font).height()
        second_height = QFontMetrics(small_font).height()
        block_height = first_height + _LINE_GAP + second_height
        top = text_rect.top() + max(0, (text_rect.height() - block_height) // 2)

        selected = bool(opt.state & QStyle.StateFlag.State_Selected)
        painter.save()
        if selected:
            painter.setPen(opt.palette.highlightedText().color())
        else:
            painter.setPen(opt.palette.text().color())
        painter.setFont(delta_font)
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
        """Size the cell from its text so a stretched column does not stay wide."""
        text = self.displayText(index.data(Qt.ItemDataRole.DisplayRole) or "", QLocale())
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)
        first, separator, second = text.partition("\n")
        if separator and second.strip():
            delta_font = _bold_font(opt.font)
            small_font = _smaller_font(opt.font)
            width = max(
                QFontMetrics(delta_font).horizontalAdvance(first),
                QFontMetrics(small_font).horizontalAdvance(second),
            )
            height = QFontMetrics(delta_font).height() + _LINE_GAP + QFontMetrics(small_font).height()
            return QSize(width + _TEXT_PADDING, height + _TEXT_PADDING)
        metrics = QFontMetrics(opt.font)
        return QSize(metrics.horizontalAdvance(first) + _TEXT_PADDING, metrics.height() + _TEXT_PADDING)
```

</details>

### ⚙️ Method `displayText`

```python
def displayText(self, value: object, _locale: QLocale | QLocale.Language) -> str
```

Format each line with thousands separators and subscript decimals.

<details>
<summary>Code:</summary>

```python
def displayText(self, value: object, _locale: QLocale | QLocale.Language) -> str:  # noqa: N802
        return "\n".join(_format_amount_line(line) for line in str(value).split("\n"))
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
        delta_font = _bold_font(opt.font)
        small_font = _smaller_font(opt.font)
        first_height = QFontMetrics(delta_font).height()
        second_height = QFontMetrics(small_font).height()
        block_height = first_height + _LINE_GAP + second_height
        top = text_rect.top() + max(0, (text_rect.height() - block_height) // 2)

        selected = bool(opt.state & QStyle.StateFlag.State_Selected)
        painter.save()
        if selected:
            painter.setPen(opt.palette.highlightedText().color())
        else:
            painter.setPen(opt.palette.text().color())
        painter.setFont(delta_font)
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

Size the cell from its text so a stretched column does not stay wide.

<details>
<summary>Code:</summary>

```python
def sizeHint(  # noqa: N802
        self,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> QSize:
        text = self.displayText(index.data(Qt.ItemDataRole.DisplayRole) or "", QLocale())
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)
        first, separator, second = text.partition("\n")
        if separator and second.strip():
            delta_font = _bold_font(opt.font)
            small_font = _smaller_font(opt.font)
            width = max(
                QFontMetrics(delta_font).horizontalAdvance(first),
                QFontMetrics(small_font).horizontalAdvance(second),
            )
            height = QFontMetrics(delta_font).height() + _LINE_GAP + QFontMetrics(small_font).height()
            return QSize(width + _TEXT_PADDING, height + _TEXT_PADDING)
        metrics = QFontMetrics(opt.font)
        return QSize(metrics.horizontalAdvance(first) + _TEXT_PADDING, metrics.height() + _TEXT_PADDING)
```

</details>
