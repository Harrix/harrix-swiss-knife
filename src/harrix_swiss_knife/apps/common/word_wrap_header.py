"""Horizontal header that wraps long section titles onto several lines."""

from __future__ import annotations

from PySide6.QtCore import QAbstractItemModel, QEvent, QRect, QSize, Qt
from PySide6.QtGui import QColor, QFontMetrics, QMouseEvent, QPainter, QPaintEvent, QPalette, QPen
from PySide6.QtWidgets import QHeaderView, QStyle, QStyleOptionHeader, QTableView, QWidget

from harrix_swiss_knife.apps.common.ui_chrome import MUTED_TEXT
from harrix_swiss_knife.fluent.theme import is_fluent_themed

HEADER_TEXT_FLAGS = Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap
_BOUNDARY_GRIP_PX = 5
_BOUNDARY_INSET_PX = 8
_TEXT_PADDING = 8
_TEXT_INSET = 4


class WordWrapHeaderView(QHeaderView):
    """`QHeaderView` that paints and sizes section titles with word wrap."""

    def __init__(
        self,
        orientation: Qt.Orientation,
        parent: QWidget | None = None,
        *,
        wrap_width: int | None = None,
        wrap_first_section: bool = False,
    ) -> None:
        """Create a wrapping header.

        Args:

        - `orientation` (`Qt.Orientation`): Header orientation.
        - `parent` (`QWidget | None`): Parent widget. Defaults to `None`.
        - `wrap_width` (`int | None`): Preferred wrap width for compact columns. Defaults to `None`.
        - `wrap_first_section` (`bool`): Also wrap the first section. Defaults to `False`.

        """
        super().__init__(orientation, parent)
        self._wrap_width = wrap_width
        self._wrap_first_section = wrap_first_section
        self._updating_height = False
        self._hover_boundary_x: int | None = None
        self.setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setTextElideMode(Qt.TextElideMode.ElideNone)
        self.setMouseTracking(True)
        self.viewport().setMouseTracking(True)
        self.sectionResized.connect(self._on_section_resized)

    def leaveEvent(self, event: QEvent) -> None:  # noqa: N802
        """Hide the column-boundary mark when the pointer leaves the header."""
        self._set_hover_boundary(None)
        super().leaveEvent(event)

    def minimumSizeHint(self) -> QSize:  # noqa: N802
        """Use the wrapped height as the minimum header size."""
        return self.sizeHint()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Show a vertical mark and resize cursor on the boundary between columns."""
        super().mouseMoveEvent(event)
        boundary = self._boundary_x_at(int(event.position().x()))
        self._set_hover_boundary(boundary)
        if boundary is not None:
            self.setCursor(Qt.CursorShape.SplitHCursor)
        elif self.cursor().shape() == Qt.CursorShape.SplitHCursor:
            self.unsetCursor()

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802
        """Paint wrapped titles, then the hovered column boundary."""
        super().paintEvent(event)
        if self._hover_boundary_x is None:
            return
        painter = QPainter(self.viewport())
        painter.setPen(QPen(QColor(MUTED_TEXT), 1))
        x = self._hover_boundary_x
        height = self.viewport().height()
        inset = min(_BOUNDARY_INSET_PX, max((height - 8) // 2, 0))
        painter.drawLine(x, inset, x, max(inset, height - inset - 1))
        painter.end()

    def paintSection(self, painter: QPainter, rect: QRect, logical_index: int) -> None:  # noqa: N802
        """Paint the section chrome, then draw the title with wrapping."""
        if not rect.isValid():
            return

        option = QStyleOptionHeader()
        self.initStyleOption(option)
        self.initStyleOptionForIndex(option, logical_index)
        option.rect = rect
        option.text = ""
        style = self.style()
        if style is not None:
            style.drawControl(QStyle.ControlElement.CE_Header, option, painter, self)

        text = self._section_text(logical_index)
        if not text:
            return

        painter.save()
        painter.setPen(option.palette.color(QPalette.ColorRole.ButtonText))
        painter.drawText(rect.adjusted(_TEXT_INSET, 2, -_TEXT_INSET, -2), int(HEADER_TEXT_FLAGS), text)
        painter.restore()

    def refresh_wrapped_height(self) -> None:
        """Recalculate header height from the current section widths."""
        if self._updating_height:
            return
        self._updating_height = True
        try:
            self.updateGeometries()
        finally:
            self._updating_height = False

    def sectionSizeFromContents(self, logical_index: int) -> QSize:  # noqa: N802
        """Prefer a compact wrapped width when `wrap_width` is set."""
        if not self._should_wrap_section(logical_index) or self._wrap_width is None:
            return super().sectionSizeFromContents(logical_index)
        return wrapped_header_text_size(self._section_text(logical_index), self._wrap_width, self.fontMetrics())

    def setModel(self, model: QAbstractItemModel | None) -> None:  # noqa: N802
        """Refresh wrapped height after the header model is assigned."""
        super().setModel(model)
        self.refresh_wrapped_height()

    def sizeHint(self) -> QSize:  # noqa: N802
        """Grow vertically so wrapped titles stay visible."""
        hint = super().sizeHint()
        return QSize(hint.width(), max(hint.height(), self._max_wrapped_height()))

    def viewportEvent(self, event: QEvent) -> bool:  # noqa: N802
        """Clear the boundary mark when the pointer leaves the header viewport."""
        handled = super().viewportEvent(event)
        if event.type() in {QEvent.Type.Leave, QEvent.Type.HoverLeave}:
            self._set_hover_boundary(None)
            if self.cursor().shape() == Qt.CursorShape.SplitHCursor:
                self.unsetCursor()
        return handled

    def _boundary_x_at(self, viewport_x: int) -> int | None:
        """Return the position of an interactive section edge near the pointer."""
        last = self.count() - 1
        for logical in range(self.count()):
            if self.isSectionHidden(logical) or logical == last:
                continue
            if self.sectionResizeMode(logical) != QHeaderView.ResizeMode.Interactive:
                continue
            right = self.sectionViewportPosition(logical) + self.sectionSize(logical)
            if abs(viewport_x - right) <= _BOUNDARY_GRIP_PX:
                return right
        return None

    def _max_wrapped_height(self) -> int:
        if self.count() == 0:
            return 0
        max_height = 0
        for logical_index in range(self.count()):
            width = self.sectionSize(logical_index)
            if width <= 0 and self._wrap_width is not None and self._should_wrap_section(logical_index):
                width = self._wrap_width
            if width <= 0:
                continue
            max_height = max(
                max_height,
                wrapped_header_text_size(self._section_text(logical_index), width, self.fontMetrics()).height(),
            )
        return max_height

    def _on_section_resized(self, _logical_index: int, _old_size: int, _new_size: int) -> None:
        self.refresh_wrapped_height()

    def _section_text(self, logical_index: int) -> str:
        model = self.model()
        if model is None:
            return ""
        value = model.headerData(logical_index, self.orientation(), Qt.ItemDataRole.DisplayRole)
        return "" if value is None else str(value)

    def _set_hover_boundary(self, boundary_x: int | None) -> None:
        if boundary_x == self._hover_boundary_x:
            return
        self._hover_boundary_x = boundary_x
        self.viewport().update()

    def _should_wrap_section(self, logical_index: int) -> bool:
        return self._wrap_first_section or logical_index > 0


def install_word_wrap_header(
    table: QTableView,
    *,
    wrap_width: int | None = None,
    wrap_first_section: bool = True,
) -> WordWrapHeaderView:
    """Replace a table's horizontal header with a wrapping header.

    Existing clickable, stretch, and size settings are copied from the current header.

    Args:

    - `table` (`QTableView`): Table whose header should wrap.
    - `wrap_width` (`int | None`): Preferred wrap width for compact columns. Defaults to `None`.
    - `wrap_first_section` (`bool`): Also wrap the first section. Defaults to `True`.

    Returns:

    - `WordWrapHeaderView`: The header now used by `table`.

    """
    current = table.horizontalHeader()
    if isinstance(current, WordWrapHeaderView):
        return current

    header = WordWrapHeaderView(
        Qt.Orientation.Horizontal,
        table,
        wrap_width=wrap_width,
        wrap_first_section=wrap_first_section,
    )
    if current is not None:
        header.setSectionsClickable(current.sectionsClickable())
        header.setHighlightSections(current.highlightSections())
        header.setStretchLastSection(current.stretchLastSection())
        header.setSortIndicatorShown(current.isSortIndicatorShown())
        header.setDefaultAlignment(current.defaultAlignment())
        header.setMinimumSectionSize(current.minimumSectionSize())
        header.setDefaultSectionSize(current.defaultSectionSize())
        header.setSectionsMovable(current.sectionsMovable())
    header.setTextElideMode(Qt.TextElideMode.ElideNone)
    table.setHorizontalHeader(header)
    # New headers start on the system light palette; restore Fluent dark chrome.
    if is_fluent_themed(table):
        from harrix_swiss_knife.fluent.app_chrome import style_fluent_table  # noqa: PLC0415

        style_fluent_table(table)
    return header


def install_word_wrap_headers(
    parent: QWidget,
    *,
    skip: set[QTableView] | frozenset[QTableView] | None = None,
    wrap_first_section: bool = True,
) -> None:
    """Install wrapping headers on every `QTableView` under `parent`."""
    skipped = skip or set()
    for table in parent.findChildren(QTableView):
        if table in skipped:
            continue
        install_word_wrap_header(table, wrap_first_section=wrap_first_section)


def wrapped_header_text_size(
    text: str,
    width: int,
    font_metrics: QFontMetrics,
    *,
    padding: int = _TEXT_PADDING,
) -> QSize:
    """Return the size of `text` wrapped into `width` pixels."""
    inner_width = max(width - padding, 1)
    bounds = font_metrics.boundingRect(0, 0, inner_width, 10_000, int(HEADER_TEXT_FLAGS), text)
    return QSize(max(width, bounds.width() + padding), bounds.height() + padding)
