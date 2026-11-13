"""Delegate that paints a main label and an optional gray local-name second line."""

from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, QRect, QSize, Qt
from PySide6.QtGui import QColor, QFont, QFontMetrics, QIcon, QPainter, QPen
from PySide6.QtWidgets import QApplication, QStyle, QStyledItemDelegate, QStyleOptionViewItem, QWidget

from harrix_swiss_knife.apps.common.ui_chrome import MUTED_TEXT
from harrix_swiss_knife.fluent.style import list_item_hover
from harrix_swiss_knife.fluent.theme import mix, palette_for
from harrix_swiss_knife.fluent.tokens import RADIUS_CONTROL

if TYPE_CHECKING:
    from PySide6.QtCore import QModelIndex, QPersistentModelIndex

NAME_LOCAL_ROLE = Qt.ItemDataRole.UserRole + 1
_NAME_LOCAL_COLOR = QColor(MUTED_TEXT)
_NAME_LOCAL_FONT_SCALE = 0.85
_NAME_LOCAL_MIN_PIXEL_SIZE = 12
_NAME_LOCAL_MIN_POINT_SIZE = 7.0
_NAME_LOCAL_FALLBACK_POINT_SIZE = 9.0
_LINE_GAP = 1
_LIST_EDGE_PAD = 4
_LIST_ICON_TEXT_GAP = 8
MARKER_WIDTH = 3
MARKER_INSET = 1
MARKER_GAP = 4


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
        local_font_scale: float = _NAME_LOCAL_FONT_SCALE,
    ) -> None:
        """Initialize the delegate.

        Args:

        - `layout` (`NameLocalLayout`): `LIST` left-aligns text beside the icon; `ICON`
          centers text under the icon.
        - `local_font_scale` (`float`): Local-name size relative to the main label font.
          Defaults to `_NAME_LOCAL_FONT_SCALE`.

        """
        super().__init__(parent)
        self._layout = layout
        self._local_font_scale = local_font_scale

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
        selected = bool(opt.state & QStyle.StateFlag.State_Selected)
        hovered = bool(opt.state & QStyle.StateFlag.State_MouseOver)
        focused = bool(opt.state & QStyle.StateFlag.State_HasFocus)

        if self._layout == NameLocalLayout.LIST:
            self._paint_list_chrome(painter, option, selected=selected, hovered=hovered, focused=focused)
            content_rect = self._list_content_rect(option.rect, selected=selected)
            decoration_rect, text_rect = self._list_layout_rects_for(content_rect, opt)
            # Keep thumbnails crisp — Selected icon mode looks like a disabled plate.
            if not opt.icon.isNull() and decoration_rect.isValid():
                opt.icon.paint(
                    painter,
                    decoration_rect,
                    Qt.AlignmentFlag.AlignCenter,
                    QIcon.Mode.Normal,
                    QIcon.State.Off,
                )
            host = self._host_widget(option)
            fluent = palette_for(host)
            text_color = mix(fluent.window_bg, fluent.text_primary)
            self._paint_labels(
                painter,
                opt.font,
                main_text,
                name_local,
                text_rect,
                text_color,
                local_color=self._local_ink(host),
            )
            return

        widget = option.widget
        style = widget.style() if widget is not None else QApplication.style()
        style.drawPrimitive(QStyle.PrimitiveElement.PE_PanelItemViewItem, opt, painter, widget)
        decoration_rect = style.subElementRect(QStyle.SubElement.SE_ItemViewItemDecoration, opt, widget)
        text_rect = style.subElementRect(QStyle.SubElement.SE_ItemViewItemText, opt, widget)
        if not text_rect.isValid():
            text_rect = option.rect.adjusted(4, 2, -4, -2)

        if not opt.icon.isNull() and decoration_rect.isValid():
            opt.icon.paint(
                painter,
                decoration_rect,
                Qt.AlignmentFlag.AlignCenter,
                QIcon.Mode.Normal,
                QIcon.State.Off,
            )

        text_color = opt.palette.text().color()
        self._paint_labels(
            painter,
            opt.font,
            main_text,
            name_local,
            text_rect,
            text_color,
            local_color=self._local_ink(self._host_widget(option)),
        )

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

    def _host_widget(self, option: QStyleOptionViewItem) -> QWidget | None:
        widget = option.widget
        return widget if isinstance(widget, QWidget) else None

    def _list_content_rect(self, item_rect: QRect, *, selected: bool) -> QRect:
        if not selected:
            return item_rect
        shift = MARKER_INSET + MARKER_WIDTH + MARKER_GAP
        return item_rect.adjusted(shift, 0, 0, 0)

    def _list_layout_rects_for(
        self,
        item_rect: QRect,
        option: QStyleOptionViewItem,
    ) -> tuple[QRect, QRect]:
        """Compact icon + text rects for list rows (tighter than default style gaps)."""
        decoration_rect = self.list_decoration_rect(
            item_rect,
            option.decorationSize,
            has_icon=not option.icon.isNull(),
        )
        if not decoration_rect.isValid():
            content = item_rect.adjusted(_LIST_EDGE_PAD, _LIST_EDGE_PAD, -_LIST_EDGE_PAD, -_LIST_EDGE_PAD)
            return QRect(), content

        content = item_rect.adjusted(_LIST_EDGE_PAD, _LIST_EDGE_PAD, -_LIST_EDGE_PAD, -_LIST_EDGE_PAD)
        text_x = decoration_rect.right() + _LIST_ICON_TEXT_GAP
        text_rect = QRect(text_x, content.y(), max(0, content.right() - text_x), content.height())
        return decoration_rect, text_rect

    def _local_font(self, base_font: QFont) -> QFont:
        local_font = QFont(base_font)
        local_font.setWeight(QFont.Weight.Normal)
        pixel = base_font.pixelSize()
        if pixel > 0:
            local_font.setPixelSize(max(_NAME_LOCAL_MIN_PIXEL_SIZE, round(pixel * self._local_font_scale)))
            return local_font
        point = base_font.pointSizeF()
        if point <= 0:
            point = float(base_font.pointSize())
        if point <= 0:
            point = _NAME_LOCAL_FALLBACK_POINT_SIZE
        local_font.setPointSizeF(max(_NAME_LOCAL_MIN_POINT_SIZE, point * self._local_font_scale))
        return local_font

    def _local_ink(self, host: QWidget | None) -> QColor:
        """Secondary line ink: design muted on light, theme secondary on dark."""
        fluent = palette_for(host)
        if fluent.dark:
            return mix(fluent.window_bg, fluent.text_secondary)
        return QColor(MUTED_TEXT)

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
        *,
        local_color: QColor | None = None,
    ) -> None:
        secondary = local_color if local_color is not None else _NAME_LOCAL_COLOR
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
            painter.setPen(secondary)
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
        painter.setPen(secondary)
        painter.setFont(local_font)
        painter.drawText(
            local_rect,
            left_flags,
            local_metrics.elidedText(name_local, Qt.TextElideMode.ElideRight, local_rect.width()),
        )
        painter.restore()

    def _paint_list_chrome(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        *,
        selected: bool,
        hovered: bool,
        focused: bool,
    ) -> None:
        """Soft-blue selection + left accent marker (Finance category list language)."""
        host = self._host_widget(option)
        fluent = palette_for(host)
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
            marker = QRect(
                option.rect.left() + MARKER_INSET,
                option.rect.top() + 4,
                MARKER_WIDTH,
                max(8, option.rect.height() - 8),
            )
            painter.fillRect(marker, fluent.accent)

        if focused and not selected:
            painter.setPen(QPen(fluent.focus_stroke_outer, 1))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(option.rect.adjusted(1, 1, -2, -2), RADIUS_CONTROL, RADIUS_CONTROL)
        painter.restore()
