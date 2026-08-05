"""Delegate that paints a right-edge Use button on suggested category rows."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QEvent, QObject, QRect, QSize, Qt, Signal
from PySide6.QtGui import QColor, QFont, QFontMetrics, QMouseEvent, QPainter, QPen
from PySide6.QtWidgets import QStyle, QStyledItemDelegate, QStyleOptionViewItem

if TYPE_CHECKING:
    from collections.abc import Collection

    from PySide6.QtCore import QAbstractItemModel, QModelIndex, QPersistentModelIndex

_BUTTON_TEXT = "✅ Use"
_BUTTON_PADDING_X = 10
_BUTTON_MARGIN = 4
_BUTTON_HEIGHT = 22
_BUTTON_BG = QColor("#E8F5E8")
_BUTTON_BORDER = QColor("#7DB68A")
_BUTTON_TEXT_COLOR = QColor("#1B5E20")
_ROW_HOVER_BG = QColor("#F0FAF0")
_ROW_SELECTED_BG = QColor("#E8F5E8")
NAME_RU_ROLE = Qt.ItemDataRole.UserRole + 1
_NAME_RU_COLOR = QColor("#888888")
_NAME_RU_FONT_SCALE = 0.85
_NAME_RU_MIN_POINT_SIZE = 7.0


class CategorySuggestDelegate(QStyledItemDelegate):
    """Paint category rows with an opaque Use button on the right for suggestions."""

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

    def _category_name_ru(self, index: QModelIndex | QPersistentModelIndex) -> str | None:
        value = index.data(NAME_RU_ROLE)
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
        """Draw main category text and optional gray smaller Russian name."""
        main_text = option.text
        name_ru = self._category_name_ru(index)

        painter.setPen(text_color)
        painter.setFont(option.font)
        main_metrics = QFontMetrics(option.font)
        flags = int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft | Qt.TextFlag.TextSingleLine)

        if not name_ru:
            painter.drawText(text_rect, flags, main_text)
            return

        ru_font = QFont(option.font)
        base_size = option.font.pointSizeF()
        if base_size <= 0:
            base_size = float(option.font.pointSize() or 9)
        ru_font.setPointSizeF(max(_NAME_RU_MIN_POINT_SIZE, base_size * _NAME_RU_FONT_SCALE))
        ru_metrics = QFontMetrics(ru_font)
        ru_text = f" ({name_ru})"

        available = max(0, text_rect.width())
        main_width = main_metrics.horizontalAdvance(main_text)
        ru_width = ru_metrics.horizontalAdvance(ru_text)

        if main_width + ru_width <= available:
            painter.drawText(text_rect, flags, main_text)
            ru_rect = QRect(text_rect.left() + main_width, text_rect.top(), ru_width, text_rect.height())
            painter.setPen(_NAME_RU_COLOR)
            painter.setFont(ru_font)
            painter.drawText(ru_rect, flags, ru_text)
            return

        # Prefer keeping Russian visible when space is tight: elide main text.
        remaining_for_main = max(0, available - ru_width)
        elided_main = main_metrics.elidedText(main_text, Qt.TextElideMode.ElideRight, remaining_for_main)
        elided_main_width = main_metrics.horizontalAdvance(elided_main)
        painter.drawText(text_rect, flags, elided_main)
        if elided_main_width < available:
            ru_rect = QRect(
                text_rect.left() + elided_main_width,
                text_rect.top(),
                available - elided_main_width,
                text_rect.height(),
            )
            painter.setPen(_NAME_RU_COLOR)
            painter.setFont(ru_font)
            painter.drawText(
                ru_rect,
                flags,
                ru_metrics.elidedText(ru_text, Qt.TextElideMode.ElideRight, ru_rect.width()),
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
