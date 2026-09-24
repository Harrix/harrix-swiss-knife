"""Two-line cells for year-delta report columns."""

from __future__ import annotations

from PySide6.QtCore import QLocale, QModelIndex, QPersistentModelIndex, QRect, QSize, Qt
from PySide6.QtGui import QFont, QFontMetrics, QPainter
from PySide6.QtWidgets import QApplication, QStyle, QStyledItemDelegate, QStyleOptionViewItem

from harrix_swiss_knife.apps.finance.number_utils import format_amount

_SMALLER_FONT_DELTA_PT = 2.0
_MIN_POINT_SIZE = 7.0
_MIN_PIXEL_SIZE = 8
_LINE_GAP = 1
_TEXT_PADDING = 8


class YearDeltaCellDelegate(QStyledItemDelegate):
    """Paint a bold delta on the first line and its baseline amount smaller underneath.

    Amounts use the same thousands separators and subscript decimals as report cells.
    Column width follows the text, so a stretched table does not keep the cells wide.

    """

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


def _bold_font(font: QFont) -> QFont:
    bold = QFont(font)
    bold.setBold(True)
    return bold


def _format_amount_line(text: str) -> str:
    if not text or text == "—":
        return text
    sign = ""
    body = text
    if body[0] in "+-":
        sign = body[0]
        body = body[1:]
    number_text, separator, suffix = body.partition(" ")
    formatted = format_amount(f"-{number_text}" if sign == "-" else number_text)
    if sign == "+":
        formatted = f"+{formatted}"
    if separator:
        return f"{formatted} {suffix}"
    return formatted


def _smaller_font(font: QFont) -> QFont:
    small = QFont(font)
    point_size = font.pointSizeF()
    if point_size > 0:
        small.setPointSizeF(max(point_size - _SMALLER_FONT_DELTA_PT, _MIN_POINT_SIZE))
        return small
    pixel_size = font.pixelSize()
    if pixel_size > 0:
        small.setPixelSize(max(pixel_size - int(_SMALLER_FONT_DELTA_PT), _MIN_PIXEL_SIZE))
    return small
