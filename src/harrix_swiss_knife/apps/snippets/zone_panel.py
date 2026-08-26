"""One snippets zone: sort buttons, optional filter, and item list."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QModelIndex, QPersistentModelIndex, QPoint, QRect, QSize, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QPushButton,
    QStyle,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife.apps.snippets.constants import (
    SORT_ADDED,
    SORT_ALPHA,
    SORT_USED,
    ZONE_COLOR,
    ZONE_EMOJI,
    ZONE_SYMBOL,
    SortMode,
)
from harrix_swiss_knife.apps.snippets.parse import (
    display_text,
    hint_tooltip,
    item_matches_search,
    strip_wrapping_brackets,
)
from harrix_swiss_knife.qt_app_font import apply_mono_font
from harrix_swiss_knife.qt_emoji_icon import add_emoji_action, create_emoji_icon

if TYPE_CHECKING:
    from harrix_swiss_knife.apps.snippets.database_manager import SnippetItem, ZoneSort

_ITEM_ROLE = Qt.ItemDataRole.UserRole
_COLOR_ROLE = Qt.ItemDataRole.UserRole + 1
_ICON_GRID = QSize(34, 34)
_ICON_PIXEL_SIZE = 20
_ICON_SPACING = 2
_CHIP_BORDER_DARKER = 130
_CHIP_GAP = 8
_CHIP_PADDING_X = 8
_CHIP_PADDING_Y = 3
_CHIP_RADIUS = 6
_CHIP_ROW_MARGIN = 8
_LIGHT_TEXT_THRESHOLD = 160
_MIN_COLOR_ROW_HEIGHT = 28
_SORT_BUTTONS: tuple[tuple[SortMode, str, str], ...] = (
    (SORT_USED, "🕒", "Sort by last used"),
    (SORT_ADDED, "📅", "Sort by date added"),
    (SORT_ALPHA, "🔤", "Sort alphabetically"),
)


class ColorItemDelegate(QStyledItemDelegate):
    """Paint a rounded color chip, then `: description`."""

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        """Draw the selection, hex chip, and optional hint."""
        self.initStyleOption(option, index)
        painter.save()
        widget = option.widget
        style = widget.style() if widget is not None else None
        if style is not None:
            style.drawPrimitive(QStyle.PrimitiveElement.PE_PanelItemViewItem, option, painter, widget)

        hex_value = strip_wrapping_brackets(str(index.data(_COLOR_ROLE) or ""))
        color = QColor(hex_value) if hex_value else QColor("#ffffff")
        if not color.isValid():
            color = QColor("#ffffff")
            hex_value = hex_value or "#ffffff"

        snippet = index.data(_ITEM_ROLE)
        hint = snippet.hint.strip() if snippet is not None and snippet.hint else ""
        metrics = option.fontMetrics
        chip_width = metrics.horizontalAdvance(hex_value) + _CHIP_PADDING_X * 2
        chip_height = metrics.height() + _CHIP_PADDING_Y * 2
        chip_y = option.rect.y() + (option.rect.height() - chip_height) // 2
        chip_rect = QRect(option.rect.x() + _CHIP_ROW_MARGIN, chip_y, chip_width, chip_height)

        painter.setRenderHint(QPainter.RenderHint.Antialiasing, on=True)
        painter.setBrush(color)
        painter.setPen(QPen(chip_border_color(color), 1))
        painter.drawRoundedRect(chip_rect.adjusted(0, 0, -1, -1), _CHIP_RADIUS, _CHIP_RADIUS)
        text_color = QColor("#122a3a") if color.lightness() > _LIGHT_TEXT_THRESHOLD else QColor("#ffffff")
        painter.setPen(text_color)
        painter.drawText(chip_rect, Qt.AlignmentFlag.AlignCenter, hex_value)

        if hint:
            desc_x = chip_rect.right() + _CHIP_GAP
            desc_rect = QRect(
                desc_x,
                option.rect.y(),
                max(0, option.rect.right() - desc_x - _CHIP_ROW_MARGIN),
                option.rect.height(),
            )
            painter.setPen(option.palette.color(option.palette.ColorRole.Text))
            painter.drawText(desc_rect, Qt.AlignmentFlag.AlignVCenter, f": {hint}")
        painter.restore()

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> QSize:  # noqa: N802
        """Keep color rows tall enough for the rounded chip."""
        hint = super().sizeHint(option, index)
        return QSize(hint.width(), max(hint.height(), _MIN_COLOR_ROW_HEIGHT))


class ZonePanel(QWidget):
    """List or grid of snippet items for one zone."""

    item_activated = Signal(object)
    add_requested = Signal()
    add_many_requested = Signal()
    edit_requested = Signal(object)
    edit_all_requested = Signal()
    delete_requested = Signal(object)
    sort_requested = Signal(str)

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        zone: str,
        title: str,
        show_add: bool = False,
        show_filter: bool = False,
    ) -> None:
        """Build the zone header and list.

        Args:

        - `parent` (`QWidget | None`): Parent widget. Defaults to `None`.
        - `zone` (`str`): Zone identifier.
        - `title` (`str`): Header label.
        - `show_add` (`bool`): Show the add button. Defaults to `False`.
        - `show_filter` (`bool`): Show the search field. Defaults to `False`.

        """
        super().__init__(parent)
        self.zone = zone
        self._items: list[SnippetItem] = []
        self._sort_buttons: dict[SortMode, QToolButton] = {}

        self._list = QListWidget(self)
        self._list.setFrameShape(QListWidget.Shape.NoFrame)
        apply_mono_font(self._list)
        if zone in {ZONE_EMOJI, ZONE_SYMBOL}:
            self._list.setViewMode(QListWidget.ViewMode.IconMode)
            self._list.setResizeMode(QListWidget.ResizeMode.Adjust)
            self._list.setMovement(QListWidget.Movement.Static)
            self._list.setGridSize(_ICON_GRID)
            self._list.setIconSize(QSize(_ICON_PIXEL_SIZE, _ICON_PIXEL_SIZE))
            self._list.setSpacing(_ICON_SPACING)
            self._list.setWordWrap(False)
        if zone == ZONE_COLOR:
            self._list.setItemDelegate(ColorItemDelegate(self._list))
        self._list.itemClicked.connect(self._on_item_clicked)
        self._list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._list.customContextMenuRequested.connect(self._on_context_menu)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._on_context_menu)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        if show_add:
            add_button = QToolButton(self)
            add_button.setIcon(create_emoji_icon("➕", 18))  # noqa: RUF001
            add_button.setIconSize(QSize(18, 18))
            add_button.setToolTip(title)
            add_button.setAutoRaise(True)
            add_button.clicked.connect(self.add_requested.emit)
            header.addWidget(add_button)
        else:
            title_button = QPushButton(title)
            title_button.setFlat(True)
            title_button.setEnabled(False)
            header.addWidget(title_button)
        header.addStretch()
        for mode, emoji, tooltip in _SORT_BUTTONS:
            button = QToolButton(self)
            button.setIcon(create_emoji_icon(emoji, 18))
            button.setIconSize(QSize(18, 18))
            button.setToolTip(tooltip)
            button.setAutoRaise(True)
            button.setCheckable(True)
            button.clicked.connect(lambda _checked=False, sort_mode=mode: self.sort_requested.emit(sort_mode))
            self._sort_buttons[mode] = button
            header.addWidget(button)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.addLayout(header)

        self._filter = None
        if show_filter:
            self._filter = QLineEdit(self)
            apply_mono_font(self._filter)
            self._filter.setPlaceholderText("Filter and search…")
            self._filter.setClearButtonEnabled(True)
            self._filter.textChanged.connect(self._apply_filter)
            layout.addWidget(self._filter)

        layout.addWidget(self._list, stretch=1)

    def clear_filter(self) -> None:
        """Clear the search field when the zone has one."""
        if self._filter is not None:
            self._filter.clear()

    def focus_filter(self) -> None:
        """Focus the search field when the zone has one."""
        if self._filter is not None:
            self._filter.setFocus()

    def item_at(self, pos: QPoint) -> SnippetItem | None:
        """Return the item under `pos` in list coordinates, if any."""
        item = self._list.itemAt(pos)
        if item is None:
            return None
        data = item.data(_ITEM_ROLE)
        return data if data is not None else None

    def set_items(self, items: list[SnippetItem]) -> None:
        """Replace the visible items."""
        self._items = items
        self._list.clear()
        for snippet in items:
            list_item = QListWidgetItem()
            list_item.setData(_ITEM_ROLE, snippet)
            label = display_text(snippet.value, snippet.hint, snippet.zone)
            if self.zone == ZONE_EMOJI:
                list_item.setIcon(create_emoji_icon(snippet.value, _ICON_PIXEL_SIZE))
                list_item.setToolTip(snippet.value)
            elif self.zone == ZONE_SYMBOL:
                list_item.setIcon(create_emoji_icon(snippet.value, _ICON_PIXEL_SIZE))
                list_item.setToolTip(hint_tooltip(snippet.hint, snippet.value))
            elif self.zone == ZONE_COLOR:
                list_item.setData(_COLOR_ROLE, snippet.value)
                list_item.setToolTip(snippet.hint or snippet.value)
            else:
                list_item.setText(label)
                if snippet.hint:
                    list_item.setToolTip(snippet.hint)
            self._list.addItem(list_item)
        self._apply_filter()

    def set_sort_state(self, zone_sort: ZoneSort) -> None:
        """Mark the active sort button."""
        for mode, button in self._sort_buttons.items():
            button.setChecked(mode == zone_sort.mode)
            tooltip = next(tip for sort_mode, _emoji, tip in _SORT_BUTTONS if sort_mode == mode)
            if mode == zone_sort.mode and zone_sort.descending:
                button.setToolTip(f"{tooltip} (reversed)")
            else:
                button.setToolTip(tooltip)

    def _apply_filter(self) -> None:
        if self._filter is None:
            return
        query = self._filter.text()
        for row in range(self._list.count()):
            item = self._list.item(row)
            if item is None:
                continue
            snippet = item.data(_ITEM_ROLE)
            if snippet is None:
                item.setHidden(False)
                continue
            item.setHidden(not item_matches_search(snippet.value, snippet.hint, query))

    def _on_context_menu(self, pos: QPoint) -> None:
        widget = self.sender()
        if widget is self._list:
            global_pos = self._list.mapToGlobal(pos)
            snippet = self.item_at(pos)
        else:
            global_pos = self.mapToGlobal(pos)
            snippet = self.item_at(self._list.mapFrom(self, pos))

        menu = QMenu(self)
        add_emoji_action(menu, "Add item", "➕").triggered.connect(self.add_requested.emit)  # noqa: RUF001
        add_emoji_action(menu, "Add many items", "📥").triggered.connect(self.add_many_requested.emit)
        edit_action = add_emoji_action(menu, "Edit item", "✏️")
        edit_action.setEnabled(snippet is not None)
        if snippet is not None:
            edit_action.triggered.connect(lambda _checked=False, item=snippet: self.edit_requested.emit(item))
        add_emoji_action(menu, "Edit entire list", "📝").triggered.connect(self.edit_all_requested.emit)
        delete_action = add_emoji_action(menu, "Delete item", "🗑️")
        delete_action.setEnabled(snippet is not None)
        if snippet is not None:
            delete_action.triggered.connect(lambda _checked=False, item=snippet: self.delete_requested.emit(item))
        menu.popup(global_pos)

    def _on_item_clicked(self, item: QListWidgetItem) -> None:
        snippet = item.data(_ITEM_ROLE)
        if snippet is not None:
            self.item_activated.emit(snippet)


def chip_border_color(color: QColor) -> QColor:
    """Return a 1 px border color darker than the chip fill."""
    return color.darker(_CHIP_BORDER_DARKER)


def color_hex_label(value: str) -> str:
    """Return the hex text for a color chip, without surrounding brackets."""
    return strip_wrapping_brackets(value)
