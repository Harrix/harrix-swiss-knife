"""Delegate that paints compact Fluent category rows with optional Use buttons."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QEvent, QObject, QRect, QSize, Qt, Signal
from PySide6.QtGui import QColor, QFont, QFontMetrics, QHelpEvent, QMouseEvent, QPainter, QPen
from PySide6.QtWidgets import QStyle, QStyledItemDelegate, QStyleOptionViewItem, QToolTip, QWidget

from harrix_swiss_knife.apps.finance.category_icon_display import category_lucide_icon
from harrix_swiss_knife.fluent.style import list_item_hover
from harrix_swiss_knife.fluent.theme import mix, palette_for
from harrix_swiss_knife.fluent.tokens import RADIUS_CONTROL

if TYPE_CHECKING:
    from collections.abc import Collection

    from PySide6.QtCore import QAbstractItemModel, QModelIndex, QPersistentModelIndex

CATEGORY_ROW_HEIGHT = 28
_BUTTON_TEXT = "Use"
_BUTTON_PADDING_X = 10
_BUTTON_MARGIN = 4
_BUTTON_HEIGHT = 22
_CHECK_WIDTH = 16
_MARKER_WIDTH = 3
_ICON_COLUMN_WIDTH = 24
NAME_LOCAL_ROLE = Qt.ItemDataRole.UserRole + 1
ICON_ROLE = Qt.ItemDataRole.UserRole + 2
ICON_LUCIDE_ROLE = Qt.ItemDataRole.UserRole + 3
_NAME_LOCAL_FONT_SCALE = 0.85
_NAME_LOCAL_MIN_PIXEL_SIZE = 12
_NAME_LOCAL_MIN_POINT_SIZE = 7.0
_NAME_LOCAL_FALLBACK_POINT_SIZE = 9.0


class CategorySuggestDelegate(QStyledItemDelegate):
    """Paint compact category rows with selection chrome and optional Use buttons."""

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

    def helpEvent(  # noqa: N802
        self,
        event: QHelpEvent,
        view: QWidget | None,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> bool:
        """Show the full category label when the visible text is elided."""
        del option
        if view is None:
            return False
        tip = index.data(Qt.ItemDataRole.ToolTipRole)
        if tip is None:
            tip = index.data(Qt.ItemDataRole.DisplayRole)
        text = "" if tip is None else str(tip).strip()
        if not text:
            return False
        QToolTip.showText(event.globalPos(), text, view)
        return True

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        """Paint category text, selection chrome, and optional Use button."""
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)

        category_name = self._category_name(index)
        show_button = bool(category_name and category_name in self._suggested)
        selected = bool(opt.state & QStyle.StateFlag.State_Selected)
        hovered = bool(opt.state & QStyle.StateFlag.State_MouseOver)
        focused = bool(opt.state & QStyle.StateFlag.State_HasFocus)

        reserved_right = (self._button_width(opt) + _BUTTON_MARGIN) if show_button else 0
        if selected and not show_button:
            reserved_right = _CHECK_WIDTH + _BUTTON_MARGIN

        host = self._host_widget(option)
        fluent = palette_for(host)
        text_color = mix(fluent.window_bg, fluent.text_primary)
        if selected:
            accent_fill = QColor(fluent.accent)
            accent_fill.setAlpha(36 if fluent.dark else 28)
            background = mix(fluent.window_bg, accent_fill)
        elif hovered:
            background = list_item_hover(fluent)
        else:
            background = QColor(0, 0, 0, 0)

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, on=True)
        if background.alpha() > 0:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(background)
            painter.drawRoundedRect(option.rect.adjusted(1, 1, -1, -1), RADIUS_CONTROL, RADIUS_CONTROL)

        if selected:
            marker = QRect(option.rect.left() + 1, option.rect.top() + 4, _MARKER_WIDTH, option.rect.height() - 8)
            painter.fillRect(marker, fluent.accent)

        if focused and not selected:
            pen = QPen(fluent.focus_stroke_outer, 1)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(option.rect.adjusted(1, 1, -2, -2), RADIUS_CONTROL, RADIUS_CONTROL)

        content_left = 8 if not selected else 8 + _MARKER_WIDTH
        emoji = self._category_icon(index)
        icon_rect = QRect(
            option.rect.left() + content_left,
            option.rect.top(),
            _ICON_COLUMN_WIDTH,
            option.rect.height(),
        )
        if emoji or self._category_lucide(index):
            lucide = category_lucide_icon(emoji, size=16, lucide_name=self._category_lucide(index))
            if not lucide.isNull():
                pixmap = lucide.pixmap(16, 16)
                x = icon_rect.left() + (icon_rect.width() - pixmap.width()) // 2
                y = icon_rect.top() + (icon_rect.height() - pixmap.height()) // 2
                painter.drawPixmap(x, y, pixmap)
        text_rect = option.rect.adjusted(content_left + _ICON_COLUMN_WIDTH + 4, 0, -(reserved_right + 4), 0)
        secondary = mix(fluent.window_bg, fluent.text_secondary)
        self._paint_category_label(painter, opt, index, text_rect, text_color, secondary)

        if show_button:
            self._paint_use_button(painter, opt, host)
        elif selected:
            self._paint_check(painter, option.rect, fluent.accent_text)
        painter.restore()

    def set_suggested_categories(self, category_names: Collection[str]) -> None:
        """Replace the set of categories that show a Use button."""
        self._suggested = {str(name) for name in category_names if name}

    def sizeHint(  # noqa: N802
        self,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> QSize:
        """Keep a compact, stable row height for dense category picking."""
        del option, index
        return QSize(120, CATEGORY_ROW_HEIGHT)

    def _button_rect(self, item_rect: QRect, option: QStyleOptionViewItem) -> QRect:
        width = self._button_width(option)
        height = min(_BUTTON_HEIGHT, max(16, item_rect.height() - 2 * _BUTTON_MARGIN))
        x = item_rect.right() - width - _BUTTON_MARGIN + 1
        y = item_rect.top() + (item_rect.height() - height) // 2
        return QRect(x, y, width, height)

    def _button_width(self, option: QStyleOptionViewItem) -> int:
        metrics = QFontMetrics(option.font)
        return metrics.horizontalAdvance(_BUTTON_TEXT) + 2 * _BUTTON_PADDING_X

    def _category_icon(self, index: QModelIndex | QPersistentModelIndex) -> str:
        value = index.data(ICON_ROLE)
        return "" if value is None else str(value).strip()

    def _category_lucide(self, index: QModelIndex | QPersistentModelIndex) -> str:
        value = index.data(ICON_LUCIDE_ROLE)
        return "" if value is None else str(value).strip()

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

    def _host_widget(self, option: QStyleOptionViewItem) -> QWidget | None:
        widget = option.widget
        if isinstance(widget, QWidget):
            return widget
        parent = self.parent()
        return parent if isinstance(parent, QWidget) else None

    def _paint_category_label(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
        text_rect: QRect,
        text_color: QColor,
        secondary_color: QColor,
    ) -> None:
        """Draw main category text and optional gray smaller local name."""
        # DisplayRole keeps the title without the emoji; ICON_ROLE holds DB emoji → Lucide.
        main_text = option.text
        name_local = self._category_name_local(index)

        painter.setPen(text_color)
        painter.setFont(option.font)
        main_metrics = QFontMetrics(option.font)
        flags = int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft | Qt.TextFlag.TextSingleLine)

        if not name_local:
            painter.drawText(
                text_rect,
                flags,
                main_metrics.elidedText(main_text, Qt.TextElideMode.ElideRight, max(0, text_rect.width())),
            )
            return

        local_font = QFont(option.font)
        pixel = option.font.pixelSize()
        if pixel > 0:
            local_font.setPixelSize(max(_NAME_LOCAL_MIN_PIXEL_SIZE, round(pixel * _NAME_LOCAL_FONT_SCALE)))
        else:
            base_size = option.font.pointSizeF()
            if base_size <= 0:
                base_size = float(option.font.pointSize())
            if base_size <= 0:
                base_size = _NAME_LOCAL_FALLBACK_POINT_SIZE
            local_font.setPointSizeF(max(_NAME_LOCAL_MIN_POINT_SIZE, base_size * _NAME_LOCAL_FONT_SCALE))
        local_metrics = QFontMetrics(local_font)
        local_text = f" ({name_local})"

        available = max(0, text_rect.width())
        main_width = main_metrics.horizontalAdvance(main_text)
        local_width = local_metrics.horizontalAdvance(local_text)

        if main_width + local_width <= available:
            painter.drawText(text_rect, flags, main_text)
            local_rect = QRect(text_rect.left() + main_width, text_rect.top(), local_width, text_rect.height())
            painter.setPen(secondary_color)
            painter.setFont(local_font)
            painter.drawText(local_rect, flags, local_text)
            return

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
            painter.setPen(secondary_color)
            painter.setFont(local_font)
            painter.drawText(
                local_rect,
                flags,
                local_metrics.elidedText(local_text, Qt.TextElideMode.ElideRight, local_rect.width()),
            )

    def _paint_check(self, painter: QPainter, item_rect: QRect, color: QColor) -> None:
        size = 10
        x = item_rect.right() - _CHECK_WIDTH - 2
        y = item_rect.top() + (item_rect.height() - size) // 2
        painter.setPen(QPen(color, 1.8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        painter.drawLine(x + 1, y + size // 2, x + 3, y + size - 1)
        painter.drawLine(x + 3, y + size - 1, x + size - 1, y + 1)

    def _paint_use_button(self, painter: QPainter, option: QStyleOptionViewItem, host: QWidget | None) -> None:
        fluent = palette_for(host)
        button_rect = self._button_rect(option.rect, option)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, on=True)
        painter.setPen(QPen(fluent.accent, 1))
        painter.setBrush(mix(fluent.window_bg, fluent.subtle_hover))
        painter.drawRoundedRect(button_rect.adjusted(0, 0, -1, -1), 4, 4)
        painter.setPen(fluent.accent_text)
        painter.setFont(option.font)
        painter.drawText(button_rect, int(Qt.AlignmentFlag.AlignCenter), _BUTTON_TEXT)
