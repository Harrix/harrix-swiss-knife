"""Delegate that paints a main label and an optional gray local-name second line."""

from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, QRect, QSize, Qt
from PySide6.QtGui import QColor, QFont, QFontMetrics, QIcon
from PySide6.QtWidgets import QApplication, QStyle, QStyledItemDelegate, QStyleOptionViewItem

if TYPE_CHECKING:
    from PySide6.QtCore import QModelIndex, QPersistentModelIndex
    from PySide6.QtGui import QPainter

NAME_LOCAL_ROLE = Qt.ItemDataRole.UserRole + 1
_NAME_LOCAL_COLOR = QColor("#888888")
_NAME_LOCAL_FONT_SCALE = 0.85
_NAME_LOCAL_MIN_POINT_SIZE = 7.0
_LINE_GAP = 1
_LIST_EDGE_PAD = 4
_LIST_ICON_TEXT_GAP = 8


class NameLocalLayout(StrEnum):
    """How main and local labels are arranged in the item text area."""

    LIST = "list"
    ICON = "icon"


class NameLocalListDelegate(QStyledItemDelegate):
    """Keep style chrome (selection, borders, icon) and paint two-line text."""

    def __init__(
        self,
        parent: QObject | None = None,
        *,
        layout: NameLocalLayout = NameLocalLayout.LIST,
    ) -> None:
        """Initialize the delegate.

        Args:

        - `layout` (`NameLocalLayout`): `LIST` left-aligns text beside the icon; `ICON`
          centers text under the icon.

        """
        super().__init__(parent)
        self._layout = layout

    @staticmethod
    def list_decoration_rect(item_rect: QRect, icon_size: QSize, *, has_icon: bool = True) -> QRect:
        """Return the icon rectangle for a LIST-layout row (viewport/item coordinates)."""
        if not has_icon or icon_size.width() <= 0 or icon_size.height() <= 0:
            return QRect()
        content = item_rect.adjusted(_LIST_EDGE_PAD, _LIST_EDGE_PAD, -_LIST_EDGE_PAD, -_LIST_EDGE_PAD)
        icon_y = content.y() + max(0, (content.height() - icon_size.height()) // 2)
        return QRect(content.x(), icon_y, icon_size.width(), icon_size.height())

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        """Draw style panel and icon, then overlay one or two text lines."""
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)

        main_text = opt.text
        name_local = self._name_local(index)

        widget = option.widget
        style = widget.style() if widget is not None else QApplication.style()

        # Panel draws stylesheet selection/hover backgrounds and item separators.
        style.drawPrimitive(QStyle.PrimitiveElement.PE_PanelItemViewItem, opt, painter, widget)

        if self._layout == NameLocalLayout.LIST:
            decoration_rect, text_rect = self._list_layout_rects(opt)
        else:
            decoration_rect = style.subElementRect(QStyle.SubElement.SE_ItemViewItemDecoration, opt, widget)
            text_rect = style.subElementRect(QStyle.SubElement.SE_ItemViewItemText, opt, widget)
            if not text_rect.isValid():
                text_rect = option.rect.adjusted(4, 2, -4, -2)

        if not opt.icon.isNull() and decoration_rect.isValid():
            mode = QIcon.Mode.Selected if opt.state & QStyle.StateFlag.State_Selected else QIcon.Mode.Normal
            opt.icon.paint(painter, decoration_rect, Qt.AlignmentFlag.AlignCenter, mode, QIcon.State.Off)

        if self._layout == NameLocalLayout.LIST and opt.state & QStyle.StateFlag.State_Selected:
            text_color = QColor("#000000")
        else:
            text_color = opt.palette.text().color()

        self._paint_labels(painter, opt.font, main_text, name_local, text_rect, text_color)

    def sizeHint(  # noqa: N802
        self,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> QSize:
        """Reserve vertical space for an optional local-name line."""
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)
        name_local = self._name_local(index)
        main_height = QFontMetrics(opt.font).height()
        local_height = QFontMetrics(self._local_font(opt.font)).height() if name_local else 0
        text_height = main_height + ((_LINE_GAP + local_height) if name_local else 0)

        if self._layout == NameLocalLayout.LIST:
            icon_h = opt.decorationSize.height() if not opt.icon.isNull() else 0
            return QSize(option.rect.width(), max(icon_h, text_height) + 2 * _LIST_EDGE_PAD)

        hint = super().sizeHint(option, index)
        if name_local:
            hint.setHeight(hint.height() + local_height + _LINE_GAP)
        return hint

    def _list_layout_rects(self, option: QStyleOptionViewItem) -> tuple[QRect, QRect]:
        """Compact icon + text rects for list rows (tighter than default style gaps)."""
        decoration_rect = self.list_decoration_rect(
            option.rect,
            option.decorationSize,
            has_icon=not option.icon.isNull(),
        )
        if not decoration_rect.isValid():
            content = option.rect.adjusted(_LIST_EDGE_PAD, _LIST_EDGE_PAD, -_LIST_EDGE_PAD, -_LIST_EDGE_PAD)
            return QRect(), content

        content = option.rect.adjusted(_LIST_EDGE_PAD, _LIST_EDGE_PAD, -_LIST_EDGE_PAD, -_LIST_EDGE_PAD)
        text_x = decoration_rect.right() + _LIST_ICON_TEXT_GAP
        text_rect = QRect(text_x, content.y(), max(0, content.right() - text_x), content.height())
        return decoration_rect, text_rect

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
        font: QFont,
        main_text: str,
        name_local: str | None,
        text_rect: QRect,
        text_color: QColor,
    ) -> None:
        main_metrics = QFontMetrics(font)
        painter.save()

        if not name_local:
            painter.setPen(text_color)
            painter.setFont(font)
            flags = (
                Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop | Qt.TextFlag.TextSingleLine
                if self._layout == NameLocalLayout.ICON
                else Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft | Qt.TextFlag.TextSingleLine
            )
            painter.drawText(text_rect, int(flags), main_text)
            painter.restore()
            return

        local_font = self._local_font(font)
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
            painter.setFont(font)
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
            painter.restore()
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
        painter.setFont(font)
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
        painter.restore()
