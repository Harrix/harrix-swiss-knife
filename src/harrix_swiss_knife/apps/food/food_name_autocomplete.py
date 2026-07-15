"""Autocomplete proxy model and helpers for food name input."""

from PySide6.QtCore import (
    QEvent,
    QModelIndex,
    QObject,
    QPersistentModelIndex,
    QPoint,
    QSortFilterProxyModel,
    Qt,
    QTimer,
)
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QCompleter, QLabel, QStyleOptionViewItem, QWidget
from shiboken6 import isValid


class CompleterPopupTooltipHelper(QObject):
    """Show full text near the cursor when a completer popup item is elided."""

    _TEXT_MARGIN_PX = 16
    _SHOW_DELAY_MS = 400
    _CURSOR_OFFSET = QPoint(12, 18)

    def __init__(self, completer: QCompleter) -> None:
        """Attach tooltip handling to the completer popup list."""
        popup = completer.popup()
        if popup is None:
            super().__init__(completer)
            self._popup = None
            self._viewport = None
            self._hover_index = QPersistentModelIndex()
            self._tooltip: QLabel | None = None
            self._show_timer: QTimer | None = None
            return

        super().__init__(popup)
        self._popup = popup
        self._viewport = popup.viewport()
        self._hover_index = QPersistentModelIndex()
        self._show_timer = QTimer(self)
        self._show_timer.setSingleShot(True)
        self._show_timer.setInterval(self._SHOW_DELAY_MS)
        self._show_timer.timeout.connect(self._show_tooltip_if_still_hovering)

        self._tooltip = QLabel()
        self._tooltip.setWindowFlags(Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint)
        self._tooltip.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self._tooltip.setWordWrap(True)
        self._tooltip.setMaximumWidth(480)
        self._tooltip.setStyleSheet(
            "QLabel { background-color: #ffffe1; color: #000000; border: 1px solid #767676; padding: 4px 6px; }",
        )
        self._tooltip.hide()

        popup.setMouseTracking(True)
        popup.entered.connect(self._on_item_entered)
        popup.installEventFilter(self)
        self._viewport.installEventFilter(self)
        popup.destroyed.connect(self._detach_from_popup)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Hide tooltip when popup closes or mouse leaves the hovered item."""
        if not self._is_popup_alive():
            return False

        if event.type() == QEvent.Type.Hide:
            self._hide_tooltip()
            return False

        if self._viewport is not None and watched is self._viewport and event.type() == QEvent.Type.MouseMove:
            self._on_viewport_mouse_move(event.position().toPoint())

        return False

    def _detach_from_popup(self) -> None:
        self._hide_tooltip()
        if self._popup is not None and isValid(self._popup):
            self._popup.removeEventFilter(self)
        if self._viewport is not None and isValid(self._viewport):
            self._viewport.removeEventFilter(self)
        self._popup = None
        self._viewport = None

    def _hide_tooltip(self) -> None:
        if self._show_timer is not None:
            self._show_timer.stop()
        if self._tooltip is not None:
            self._tooltip.hide()
        self._hover_index = QPersistentModelIndex()

    def _is_popup_alive(self) -> bool:
        return self._popup is not None and isValid(self._popup)

    def _is_text_elided(self, index: QModelIndex) -> tuple[bool, str]:
        if not self._is_popup_alive() or not index.isValid():
            return False, ""

        text = index.data(Qt.ItemDataRole.DisplayRole)
        if not text:
            return False, ""

        text_str = str(text)
        rect = self._popup.visualRect(index)
        if rect.width() <= 0:
            return False, text_str

        option = QStyleOptionViewItem()
        option.rect = rect
        option.fontMetrics = self._popup.fontMetrics()
        available_width = max(1, rect.width() - self._TEXT_MARGIN_PX)
        elided = option.fontMetrics.elidedText(text_str, Qt.TextElideMode.ElideRight, available_width)
        return elided != text_str, text_str

    def _on_item_entered(self, index: QModelIndex) -> None:
        self._hide_tooltip()
        if not self._is_popup_alive() or not index.isValid():
            return

        is_elided, _ = self._is_text_elided(index)
        if not is_elided:
            return

        self._hover_index = QPersistentModelIndex(index)
        if self._show_timer is not None:
            self._show_timer.start()

    def _on_viewport_mouse_move(self, pos: QPoint) -> None:
        if not self._is_popup_alive() or not self._hover_index.isValid():
            return

        index = self._popup.indexAt(pos)
        if (
            self._tooltip is not None
            and self._tooltip.isVisible()
            and index.isValid()
            and index.row() == self._hover_index.row()
        ):
            self._tooltip.move(QCursor.pos() + self._CURSOR_OFFSET)
            return

        if not index.isValid() or index.row() != self._hover_index.row():
            self._hide_tooltip()

    def _show_tooltip_if_still_hovering(self) -> None:
        if not self._is_popup_alive() or self._tooltip is None or not self._hover_index.isValid():
            return

        if self._viewport is None:
            return

        index_at_cursor = self._popup.indexAt(self._viewport.mapFromGlobal(QCursor.pos()))
        if not index_at_cursor.isValid() or index_at_cursor.row() != self._hover_index.row():
            self._hide_tooltip()
            return

        is_elided, text_str = self._is_text_elided(self._hover_index)
        if not is_elided:
            self._hide_tooltip()
            return

        self._tooltip.setText(text_str)
        self._tooltip.adjustSize()
        self._tooltip.move(QCursor.pos() + self._CURSOR_OFFSET)
        self._tooltip.show()


class FoodNameAutocompleteProxyModel(QSortFilterProxyModel):
    """Proxy model for food name autocomplete with exact/starts-with/contains ordering."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the proxy model."""
        super().__init__(parent)
        self.filter_text = ""
        self.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex | QPersistentModelIndex) -> bool:  # noqa: N802
        """Determine if a row should be accepted by the filter."""
        if not self.filter_text:
            return True

        source_model = self.sourceModel()
        index = source_model.index(source_row, 0, source_parent)
        data = source_model.data(index, Qt.ItemDataRole.DisplayRole)

        if data is None:
            return False

        text = str(data).lower()
        filter_lower = self.filter_text.lower()

        if text.startswith(filter_lower):
            return True

        return filter_lower in text

    def lessThan(  # noqa: N802
        self,
        source_left: QModelIndex | QPersistentModelIndex,
        source_right: QModelIndex | QPersistentModelIndex,
    ) -> bool:
        """Sort by match tier, then alphabetically (case-insensitive) within tier."""
        if not self.filter_text:
            left_data = self.sourceModel().data(source_left, Qt.ItemDataRole.DisplayRole)
            right_data = self.sourceModel().data(source_right, Qt.ItemDataRole.DisplayRole)
            if left_data is None or right_data is None:
                return False
            left_lower = str(left_data).lower()
            right_lower = str(right_data).lower()
            if left_lower != right_lower:
                return left_lower < right_lower
            return source_left.row() < source_right.row()

        filter_lower = self.filter_text.lower()
        left_data = self.sourceModel().data(source_left, Qt.ItemDataRole.DisplayRole)
        right_data = self.sourceModel().data(source_right, Qt.ItemDataRole.DisplayRole)

        if left_data is None or right_data is None:
            return False

        left_tier = _match_tier(str(left_data), filter_lower)
        right_tier = _match_tier(str(right_data), filter_lower)

        if left_tier != right_tier:
            return left_tier < right_tier

        left_lower = str(left_data).lower()
        right_lower = str(right_data).lower()
        if left_lower != right_lower:
            return left_lower < right_lower

        return source_left.row() < source_right.row()

    def set_filter_text(self, text: str) -> None:
        """Set the filter text and trigger re-filtering and sorting."""
        self.filter_text = text
        self.invalidateFilter()
        self.sort(0)


def setup_completer_item_tooltips(completer: QCompleter) -> CompleterPopupTooltipHelper:
    """Enable tooltips for elided items in a QCompleter popup list."""
    helper = CompleterPopupTooltipHelper(completer)
    completer._tooltip_helper = helper  # keep reference alive  # noqa: SLF001
    return helper


def _match_tier(text: str, filter_text: str) -> int:
    """Return sort tier: 0 exact, 1 starts-with, 2 contains."""
    filter_lower = filter_text.lower()
    text_lower = text.lower()
    if text_lower == filter_lower:
        return 0
    if text_lower.startswith(filter_lower):
        return 1
    return 2
