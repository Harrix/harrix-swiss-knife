"""Fluent navigation: side navigation bar, breadcrumb, pivot, pagination, tabs, expander, group box, splitter."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from PySide6.QtCore import QEasingCurve, QPoint, QRectF, QSize, Qt, QVariantAnimation, Signal
from PySide6.QtGui import QFont, QFontMetrics
from PySide6.QtWidgets import (
    QHBoxLayout,
    QSizePolicy,
    QSplitter,
    QStackedWidget,
    QTabBar,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife.fluent.paint import antialiased_painter, paint_surface
from harrix_swiss_knife.fluent.style import lucide_qss_url, themed_icon
from harrix_swiss_knife.fluent.theme import bind_theme, css, fluent_font, palette_for
from harrix_swiss_knife.fluent.tokens import (
    ANIMATION_NORMAL,
    CONTROL_HEIGHT,
    ICON_SIZE,
    NAV_INDICATOR_HEIGHT,
    NAV_INDICATOR_WIDTH,
    NAV_ITEM_HEIGHT,
    RADIUS_CARD,
    RADIUS_CONTROL,
    SPACE_L,
    SPACE_M,
    SPACE_S,
    SPACE_XS,
    TYPE_BODY,
    TYPE_BODY_LARGE,
    TYPE_CAPTION,
    TYPE_SUBTITLE,
)
from harrix_swiss_knife.fluent.widgets.buttons import FluentIconButton, FluentTransparentButton
from harrix_swiss_knife.fluent.widgets.enums import TextRole, TextStyle
from harrix_swiss_knife.fluent.widgets.text_base import FluentText
from harrix_swiss_knife.fluent.widgets.views import FluentScrollArea

if TYPE_CHECKING:
    from collections.abc import Sequence

    from PySide6.QtCore import QEvent
    from PySide6.QtGui import QEnterEvent, QMouseEvent, QPaintEvent, QResizeEvent

_NAV_COMPACT_WIDTH = 48
_NAV_EXPANDED_WIDTH = 280
_PAGINATION_WINDOW = 2
_QWIDGETSIZE_MAX = 16777215


class FluentBreadcrumb(QWidget):
    """Path of clickable items separated by chevrons; the last item is the current page."""

    item_clicked = Signal(int)

    def __init__(self, parent: QWidget | None = None, *, items: Sequence[str] = ()) -> None:
        """Create a breadcrumb."""
        super().__init__(parent)
        self._items = list(items)
        self._hover = -1
        self.setMouseTracking(True)
        self.setFixedHeight(CONTROL_HEIGHT + SPACE_S)
        bind_theme(self, self.update)

    def items(self) -> list[str]:
        """Return the path items."""
        return list(self._items)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Track the hovered item."""
        index = self._index_at(event.position().x())
        if index != self._hover:
            self._hover = index
            self.setCursor(
                Qt.CursorShape.PointingHandCursor if 0 <= index < len(self._items) - 1 else Qt.CursorShape.ArrowCursor
            )
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Navigate back to the clicked item (drops the items after it)."""
        index = self._index_at(event.position().x())
        if 0 <= index < len(self._items) - 1:
            self._items = self._items[: index + 1]
            self.update()
            self.item_clicked.emit(index)

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Paint items and separators."""
        palette = palette_for(self)
        painter = antialiased_painter(self)
        font = fluent_font(self.font(), TYPE_SUBTITLE, weight=QFont.Weight.DemiBold)
        painter.setFont(font)
        for index, (text, rect, chevron) in enumerate(self._layout_items(QFontMetrics(font))):
            last = index == len(self._items) - 1
            color = palette.text_primary if last else palette.text_secondary
            if index == self._hover and not last:
                color = palette.text_primary
            painter.setPen(color)
            painter.drawText(rect, int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft), text)
            if chevron is not None:
                themed_icon("chevron-right", palette, palette.text_secondary, ICON_SIZE).paint(
                    painter, chevron.toRect()
                )
        painter.end()

    def push(self, text: str) -> None:
        """Append an item (a new current page)."""
        self._items.append(text)
        self.update()

    def set_items(self, items: Sequence[str]) -> None:
        """Replace the path."""
        self._items = list(items)
        self.update()

    def _index_at(self, x: float) -> int:
        font = fluent_font(self.font(), TYPE_SUBTITLE, weight=QFont.Weight.DemiBold)
        for index, (_text, rect, _chevron) in enumerate(self._layout_items(QFontMetrics(font))):
            if rect.left() <= x <= rect.right():
                return index
        return -1

    def _layout_items(self, metrics: QFontMetrics) -> list[tuple[str, QRectF, QRectF | None]]:
        result: list[tuple[str, QRectF, QRectF | None]] = []
        x = 0.0
        for index, text in enumerate(self._items):
            width = metrics.horizontalAdvance(text)
            rect = QRectF(x, 0, width, self.height())
            x += width
            chevron = None
            if index < len(self._items) - 1:
                chevron = QRectF(x + SPACE_S, (self.height() - ICON_SIZE) / 2, ICON_SIZE, ICON_SIZE)
                x += ICON_SIZE + 2 * SPACE_S
            result.append((text, rect, chevron))
        return result


class FluentExpander(QWidget):
    """Card with a header row (icon, title, caption, chevron) that expands to show content."""

    expanded_changed = Signal(bool)

    def __init__(self, title: str, parent: QWidget | None = None, *, caption: str = "", icon: str = "") -> None:
        """Create an expander; put content into `content_layout`."""
        super().__init__(parent)
        self._expanded = False
        self._icon = icon
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self._header = _ExpanderHeader(title, caption, icon, self)
        self._header.clicked.connect(self.toggle)
        self.content = QWidget(self)
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(SPACE_L * 3, SPACE_M, SPACE_L, SPACE_M)
        self.content.setVisible(False)
        layout.addWidget(self._header)
        layout.addWidget(self.content)
        bind_theme(self, self.update)

    def is_expanded(self) -> bool:
        """Return whether the content is shown."""
        return self._expanded

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Paint the card behind header and content."""
        palette = palette_for(self)
        painter = antialiased_painter(self)
        paint_surface(painter, self.rect(), palette.card_bg, palette.card_stroke, RADIUS_CARD)
        if self._expanded:
            y = self._header.geometry().bottom() + 1
            painter.fillRect(QRectF(1, y, self.width() - 2, 1), palette.divider)
        painter.end()

    def set_expanded(self, *, expanded: bool) -> None:
        """Show or hide the content."""
        if expanded == self._expanded:
            return
        self._expanded = expanded
        self.content.setVisible(expanded)
        self._header.set_expanded(expanded=expanded)
        self.update()
        self.expanded_changed.emit(expanded)

    def toggle(self) -> None:
        """Flip the expanded state."""
        self.set_expanded(expanded=not self._expanded)


class FluentGroupBox(QWidget):
    """Titled group of setting cards (subtitle header + stacked content)."""

    def __init__(self, title: str, parent: QWidget | None = None) -> None:
        """Create a group; add cards with `add_widget`."""
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACE_S)
        self.title_label = FluentText(title, self, style=TextStyle.BODY_STRONG)
        layout.addWidget(self.title_label)
        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(SPACE_XS)
        layout.addLayout(self.content_layout)

    def add_widget(self, widget: QWidget) -> None:
        """Append a widget (usually a card) to the group."""
        self.content_layout.addWidget(widget)


class FluentNavigationBar(QWidget):
    """Side navigation: icons + text rows, section headers, accent pill, and a compact mode.

    Rows are painted (no `QListWidget`), so hover, the selected fill, and the
    sliding accent indicator match WinUI `NavigationView` exactly.

    """

    current_changed = Signal(str)
    item_context_menu_requested = Signal(str, QPoint)

    def __init__(self, parent: QWidget | None = None, *, collapsible: bool = True) -> None:
        """Create an empty navigation bar."""
        super().__init__(parent)
        self._items: list[NavigationItem] = []
        self._footer: list[NavigationItem] = []
        self._current = ""
        self._hover = ""
        self._compact = False
        self._indicator_y = -1.0
        self._indicator = QVariantAnimation(self)
        self._indicator.setDuration(ANIMATION_NORMAL)
        self._indicator.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._indicator.valueChanged.connect(self._on_indicator)
        self._scroll_offset = 0
        self.setMouseTracking(True)
        self.setMinimumWidth(_NAV_COMPACT_WIDTH)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACE_XS, SPACE_XS, SPACE_XS, SPACE_XS)
        layout.setSpacing(0)
        self._toggle: FluentIconButton | None = None
        if collapsible:
            self._toggle = FluentIconButton("menu", self, tooltip="Toggle navigation")
            self._toggle.clicked.connect(self.toggle_compact)
            layout.addWidget(self._toggle, 0, Qt.AlignmentFlag.AlignLeft)
        layout.addStretch(1)
        bind_theme(self, self.update)

    def add_footer_item(self, key: str, text: str, *, icon: str = "", data: object = None) -> None:
        """Append a row pinned to the bottom (for example Settings)."""
        self._footer.append(NavigationItem(key, text, icon, data=data))
        self.update()

    def add_header(self, text: str) -> None:
        """Append a section header row."""
        self._items.append(NavigationItem(f"__header__{len(self._items)}", text, header=True))
        self.updateGeometry()
        self.update()

    def add_item(self, key: str, text: str, *, icon: str = "", data: object = None) -> None:
        """Append a navigation row."""
        self._items.append(NavigationItem(key, text, icon, data=data))
        if not self._current:
            self._current = key
        self.updateGeometry()
        self.update()

    def clear(self) -> None:
        """Remove every row."""
        self._items.clear()
        self._current = ""
        self._indicator_y = -1
        self.update()

    def current(self) -> str:
        """Return the selected key."""
        return self._current

    def is_compact(self) -> bool:
        """Return whether only icons are shown."""
        return self._compact

    def item(self, key: str) -> NavigationItem | None:
        """Return the row with `key`."""
        for entry in [*self._items, *self._footer]:
            if entry.key == key:
                return entry
        return None

    def items(self) -> list[NavigationItem]:
        """Return the main (non-footer) rows, including headers."""
        return list(self._items)

    def leaveEvent(self, event: QEvent) -> None:  # noqa: N802
        """Clear the hover row."""
        self._hover = ""
        self.update()
        super().leaveEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Track the hovered row."""
        key = self._key_at(event.position().y())
        if key != self._hover:
            self._hover = key
            self.update()
        entry = self.item(key) if key else None
        self.setToolTip(entry.text if entry is not None and self._compact else "")

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Select the clicked row; right click requests a context menu."""
        key = self._key_at(event.position().y())
        if not key:
            return
        if event.button() == Qt.MouseButton.RightButton:
            self.item_context_menu_requested.emit(key, event.globalPosition().toPoint())
            return
        if event.button() == Qt.MouseButton.LeftButton:
            self.set_current(key)

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Paint rows, headers, selection fill, and the accent indicator."""
        palette = palette_for(self)
        painter = antialiased_painter(self)
        body = fluent_font(self.font(), TYPE_BODY)
        header_font = fluent_font(self.font(), TYPE_CAPTION, weight=QFont.Weight.DemiBold)
        for entry, rect in self._row_rects():
            if entry.header:
                if self._compact:
                    painter.fillRect(
                        QRectF(rect.left() + SPACE_S, rect.center().y(), rect.width() - 2 * SPACE_S, 1), palette.divider
                    )
                    continue
                painter.setFont(header_font)
                painter.setPen(palette.text_secondary)
                painter.drawText(
                    rect.adjusted(SPACE_M, 0, -SPACE_S, 0),
                    int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft),
                    entry.text,
                )
                continue
            selected = entry.key == self._current
            if selected or entry.key == self._hover:
                fill = palette.subtle_pressed if selected and entry.key == self._hover else palette.subtle_hover
                paint_surface(painter, rect.adjusted(0, 2, 0, -2), fill, None, RADIUS_CONTROL)
            x = rect.left() + SPACE_M
            if entry.icon:
                icon = themed_icon(entry.icon, palette, palette.text_primary, ICON_SIZE)
                icon.paint(painter, int(x), int(rect.center().y() - ICON_SIZE / 2), ICON_SIZE, ICON_SIZE)
                x += ICON_SIZE + SPACE_M
            if not self._compact:
                painter.setFont(body)
                painter.setPen(palette.text_primary)
                metrics = QFontMetrics(body)
                width = int(rect.right() - x - SPACE_S)
                text = metrics.elidedText(entry.text, Qt.TextElideMode.ElideRight, width)
                painter.drawText(
                    QRectF(x, rect.top(), width, rect.height()),
                    int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft),
                    text,
                )
        if self._indicator_y >= 0:
            pill = QRectF(
                SPACE_XS + 1,
                self._indicator_y + (NAV_ITEM_HEIGHT - NAV_INDICATOR_HEIGHT) / 2,
                NAV_INDICATOR_WIDTH,
                NAV_INDICATOR_HEIGHT,
            )
            paint_surface(painter, pill, palette.accent, None, NAV_INDICATOR_WIDTH / 2)
        painter.end()

    def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        """Keep the indicator on the current row."""
        super().resizeEvent(event)
        self._snap_indicator()

    def set_compact(self, *, compact: bool) -> None:
        """Show icons only (`True`) or icons and text."""
        self._compact = compact
        if compact:
            self.setFixedWidth(_NAV_COMPACT_WIDTH)
        else:
            self.setMinimumWidth(_NAV_COMPACT_WIDTH)
            self.setMaximumWidth(_QWIDGETSIZE_MAX)
        self.updateGeometry()
        self.update()

    def set_current(self, key: str) -> None:
        """Select the row with `key` and animate the indicator."""
        entry = self.item(key)
        if entry is None or entry.header:
            return
        changed = key != self._current
        self._current = key
        target = self._row_top(key)
        if target is not None:
            start = self._indicator_y if self._indicator_y >= 0 else target
            self._indicator.stop()
            self._indicator.setStartValue(float(start))
            self._indicator.setEndValue(float(target))
            self._indicator.start()
        self.update()
        if changed:
            self.current_changed.emit(key)

    def sizeHint(self) -> QSize:  # noqa: N802
        """Return the expanded width and the height of all rows."""
        rows = len(self._items) + len(self._footer) + 1
        return QSize(_NAV_COMPACT_WIDTH if self._compact else _NAV_EXPANDED_WIDTH, rows * NAV_ITEM_HEIGHT)

    def toggle_compact(self) -> None:
        """Flip compact mode."""
        self.set_compact(compact=not self._compact)

    def _content_top(self) -> int:
        return SPACE_XS + (CONTROL_HEIGHT + SPACE_XS if self._toggle is not None else 0)

    def _key_at(self, y: float) -> str:
        for entry, rect in self._row_rects():
            if not entry.header and rect.top() <= y < rect.bottom():
                return entry.key
        return ""

    def _on_indicator(self, value: object) -> None:
        self._indicator_y = float(value)  # ty: ignore[invalid-argument-type]
        self.update()

    def _row_rects(self) -> list[tuple[NavigationItem, QRectF]]:
        rects: list[tuple[NavigationItem, QRectF]] = []
        y = float(self._content_top())
        width = self.width() - 2 * SPACE_XS
        for entry in self._items:
            height = NAV_ITEM_HEIGHT if not entry.header else (SPACE_L if self._compact else NAV_ITEM_HEIGHT)
            rects.append((entry, QRectF(SPACE_XS, y, width, height)))
            y += height
        bottom = float(self.height() - SPACE_XS)
        for entry in reversed(self._footer):
            bottom -= NAV_ITEM_HEIGHT
            rects.append((entry, QRectF(SPACE_XS, bottom, width, NAV_ITEM_HEIGHT)))
        return rects

    def _row_top(self, key: str) -> float | None:
        for entry, rect in self._row_rects():
            if entry.key == key:
                return rect.top()
        return None

    def _snap_indicator(self) -> None:
        target = self._row_top(self._current) if self._current else None
        self._indicator_y = target if target is not None else -1
        self.update()


class FluentNavigationPanel(QWidget):
    """`FluentNavigationBar` on the left of a stack of pages in a scroll area."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Create a navigation panel."""
        super().__init__(parent)
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(0)
        self.navigation = FluentNavigationBar(self)
        self.navigation.setFixedWidth(_NAV_EXPANDED_WIDTH - 64)
        self.stack = QStackedWidget(self)
        row.addWidget(self.navigation)
        row.addWidget(self.stack, 1)
        self._pages: dict[str, QWidget] = {}
        self.navigation.current_changed.connect(self._show)

    def add_page(self, key: str, text: str, widget: QWidget, *, icon: str = "") -> None:
        """Register a page and its navigation row."""
        scroll = FluentScrollArea(self.stack)
        scroll.setWidget(widget)
        self._pages[key] = scroll
        self.stack.addWidget(scroll)
        self.navigation.add_item(key, text, icon=icon)
        if len(self._pages) == 1:
            self.stack.setCurrentWidget(scroll)

    def _show(self, key: str) -> None:
        page = self._pages.get(key)
        if page is not None:
            self.stack.setCurrentWidget(page)


class FluentPagination(QWidget):
    """Page selector: previous / numbered pages with ellipses / next."""

    page_changed = Signal(int)

    def __init__(self, parent: QWidget | None = None, *, pages: int = 1) -> None:
        """Create a pagination control (pages are 1-based)."""
        super().__init__(parent)
        self._pages = max(1, pages)
        self._current = 1
        self._row = QHBoxLayout(self)
        self._row.setContentsMargins(0, 0, 0, 0)
        self._row.setSpacing(SPACE_XS)
        self._rebuild()

    def current(self) -> int:
        """Return the current page (1-based)."""
        return self._current

    def page_count(self) -> int:
        """Return the number of pages."""
        return self._pages

    def set_current(self, page: int) -> None:
        """Go to `page` (clamped)."""
        page = max(1, min(self._pages, page))
        if page == self._current:
            return
        self._current = page
        self._rebuild()
        self.page_changed.emit(page)

    def set_page_count(self, pages: int) -> None:
        """Change the number of pages."""
        self._pages = max(1, pages)
        self._current = min(self._current, self._pages)
        self._rebuild()

    def visible_pages(self) -> list[int]:
        """Return page numbers to show (`0` = ellipsis)."""
        pages = {1, self._pages, *range(self._current - _PAGINATION_WINDOW, self._current + _PAGINATION_WINDOW + 1)}
        ordered = sorted(page for page in pages if 1 <= page <= self._pages)
        result: list[int] = []
        for page in ordered:
            if result and page - result[-1] > 1:
                result.append(0)
            result.append(page)
        return result

    def _rebuild(self) -> None:
        while self._row.count():
            item = self._row.takeAt(0)
            widget = item.widget() if item is not None else None
            if widget is not None:
                widget.deleteLater()
        previous = FluentIconButton("chevron-left", self, tooltip="Previous")
        previous.setEnabled(self._current > 1)
        previous.clicked.connect(lambda: self.set_current(self._current - 1))
        self._row.addWidget(previous)
        for page in self.visible_pages():
            if page == 0:
                self._row.addWidget(FluentText("…", self, role=TextRole.SECONDARY))
                continue
            button = FluentTransparentButton(str(page), self)
            button.setCheckable(True)
            button.setChecked(page == self._current)
            button.setFixedWidth(CONTROL_HEIGHT + SPACE_S)
            button.clicked.connect(lambda _checked=False, target=page: self.set_current(target))
            self._row.addWidget(button)
        following = FluentIconButton("chevron-right", self, tooltip="Next")
        following.setEnabled(self._current < self._pages)
        following.clicked.connect(lambda: self.set_current(self._current + 1))
        self._row.addWidget(following)
        self._row.addStretch(1)


class FluentPivot(QWidget):
    """Top text tabs with an accent underline that slides between items."""

    current_changed = Signal(int)

    def __init__(self, parent: QWidget | None = None, *, items: Sequence[str] = ()) -> None:
        """Create a pivot."""
        super().__init__(parent)
        self._items = list(items)
        self._current = 0
        self._hover = -1
        self._line_x = -1.0
        self._line_width = 0.0
        self._animation = QVariantAnimation(self)
        self._animation.setDuration(ANIMATION_NORMAL)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._animation.valueChanged.connect(self._on_animation)
        self.setMouseTracking(True)
        self.setFixedHeight(CONTROL_HEIGHT + SPACE_M)
        bind_theme(self, self.update)

    def add_item(self, text: str) -> None:
        """Append a tab."""
        self._items.append(text)
        self.update()

    def current(self) -> int:
        """Return the selected index."""
        return self._current

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Track the hovered tab."""
        index = self._index_at(event.position().x())
        if index != self._hover:
            self._hover = index
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Select the clicked tab."""
        index = self._index_at(event.position().x())
        if index >= 0:
            self.set_current(index)

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Paint tab texts and the underline."""
        palette = palette_for(self)
        painter = antialiased_painter(self)
        font = fluent_font(self.font(), TYPE_BODY_LARGE)
        painter.setFont(font)
        rects = self._rects(QFontMetrics(font))
        for index, (text, rect) in enumerate(zip(self._items, rects, strict=True)):
            if index in (self._current, self._hover):
                painter.setPen(palette.text_primary)
            else:
                painter.setPen(palette.text_secondary)
            painter.drawText(rect, int(Qt.AlignmentFlag.AlignCenter), text)
        if rects and 0 <= self._current < len(rects):
            if self._line_x < 0:
                self._line_x = rects[self._current].center().x()
            line = QRectF(self._line_x - 8, self.height() - 3, 16, 3)
            paint_surface(painter, line, palette.accent, None, 1.5)
        painter.end()

    def set_current(self, index: int) -> None:
        """Select a tab and slide the underline."""
        if not 0 <= index < len(self._items) or index == self._current:
            return
        rects = self._rects(QFontMetrics(fluent_font(self.font(), TYPE_BODY_LARGE)))
        self._animation.stop()
        self._animation.setStartValue(rects[self._current].center().x())
        self._animation.setEndValue(rects[index].center().x())
        self._animation.start()
        self._current = index
        self.update()
        self.current_changed.emit(index)

    def _index_at(self, x: float) -> int:
        for index, rect in enumerate(self._rects(QFontMetrics(fluent_font(self.font(), TYPE_BODY_LARGE)))):
            if rect.left() <= x <= rect.right():
                return index
        return -1

    def _on_animation(self, value: object) -> None:
        self._line_x = float(value)  # ty: ignore[invalid-argument-type]
        self.update()

    def _rects(self, metrics: QFontMetrics) -> list[QRectF]:
        rects: list[QRectF] = []
        x = 0.0
        for text in self._items:
            width = metrics.horizontalAdvance(text) + 2 * SPACE_M
            rects.append(QRectF(x, 0, width, self.height() - 3))
            x += width
        return rects


class FluentSplitter(QSplitter):
    """Splitter with a thin hairline handle that turns accent on hover."""

    def __init__(self, orientation: Qt.Orientation = Qt.Orientation.Horizontal, parent: QWidget | None = None) -> None:
        """Create a splitter."""
        super().__init__(orientation, parent)
        self.setHandleWidth(SPACE_XS + 1)
        self.setChildrenCollapsible(False)
        bind_theme(self, self.refresh_theme)

    def refresh_theme(self) -> None:
        """Re-color the handle."""
        palette = palette_for(self)
        self.setStyleSheet(
            f"QSplitter::handle {{ background: transparent; margin: 2px; }}"
            f" QSplitter::handle:hover {{ background: {css(palette.accent)}; border-radius: 1px; }}",
        )


class FluentTabBar(QTabBar):
    """Document tabs: rounded top corners, selected tab joins the content surface."""

    def __init__(self, parent: QWidget | None = None, *, closable: bool = True) -> None:
        """Create a tab bar."""
        super().__init__(parent)
        self.setTabsClosable(closable)
        self.setMovable(True)
        self.setDocumentMode(True)
        self.setExpanding(False)
        self.setElideMode(Qt.TextElideMode.ElideRight)
        self.setDrawBase(False)
        bind_theme(self, self.refresh_theme)

    def refresh_theme(self) -> None:
        """Re-apply tab chrome."""
        palette = palette_for(self)
        close = lucide_qss_url("x", palette.text_secondary, 12)
        self.setStyleSheet(f"""
QTabBar {{ background: transparent; }}
QTabBar::tab {{
    background: transparent;
    color: {css(palette.text_secondary)};
    border: 1px solid transparent;
    border-top-left-radius: {RADIUS_CARD}px;
    border-top-right-radius: {RADIUS_CARD}px;
    padding: 0px 12px;
    min-height: {CONTROL_HEIGHT}px;
    min-width: 96px;
    max-width: 240px;
}}
QTabBar::tab:hover {{ background: {css(palette.subtle_hover)}; color: {css(palette.text_primary)}; }}
QTabBar::tab:selected {{
    background: {css(palette.solid_tertiary_bg if palette.dark else palette.solid_quarternary_bg)};
    color: {css(palette.text_primary)};
    border-color: {css(palette.card_stroke)};
    border-bottom-color: transparent;
}}
QTabBar::close-button {{
    image: url("{close}"); subcontrol-position: right; border-radius: {RADIUS_CONTROL}px;
    width: 16px; height: 16px; padding: 2px;
}}
QTabBar::close-button:hover {{ background: {css(palette.subtle_hover)}; }}
""")


class FluentTabWidget(QWidget):
    """`FluentTabBar` over a stacked content surface."""

    current_changed = Signal(int)

    def __init__(self, parent: QWidget | None = None, *, closable: bool = True) -> None:
        """Create a tab widget."""
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.tab_bar = FluentTabBar(self, closable=closable)
        self.stack = QStackedWidget(self)
        layout.addWidget(self.tab_bar)
        layout.addWidget(self.stack, 1)
        self.tab_bar.currentChanged.connect(self._on_current)
        self.tab_bar.tabCloseRequested.connect(self.remove_tab)
        self.tab_bar.tabMoved.connect(self._on_moved)
        bind_theme(self, self.refresh_theme)

    def add_tab(self, widget: QWidget, text: str, *, icon: str = "") -> int:
        """Append a page and return its index."""
        self.stack.addWidget(widget)
        index = self.tab_bar.addTab(text)
        if icon:
            self.tab_bar.setTabIcon(index, themed_icon(icon, palette_for(self)))
        return index

    def count(self) -> int:
        """Return the number of pages."""
        return self.stack.count()

    def current_index(self) -> int:
        """Return the selected page index."""
        return self.tab_bar.currentIndex()

    def refresh_theme(self) -> None:
        """Re-color the content surface."""
        palette = palette_for(self)
        fill = palette.solid_tertiary_bg if palette.dark else palette.solid_quarternary_bg
        self.stack.setObjectName("FluentTabStack")
        self.stack.setStyleSheet(
            f"QStackedWidget#FluentTabStack {{ background: {css(fill)}; border: 1px solid {css(palette.card_stroke)};"
            f" border-top-right-radius: {RADIUS_CARD}px; border-bottom-left-radius: {RADIUS_CARD}px;"
            f" border-bottom-right-radius: {RADIUS_CARD}px; }}",
        )

    def remove_tab(self, index: int) -> None:
        """Close the page at `index`."""
        widget = self.stack.widget(index)
        self.tab_bar.removeTab(index)
        if widget is not None:
            self.stack.removeWidget(widget)
            widget.deleteLater()

    def set_current_index(self, index: int) -> None:
        """Select a page."""
        self.tab_bar.setCurrentIndex(index)

    def _on_current(self, index: int) -> None:
        self.stack.setCurrentIndex(index)
        self.current_changed.emit(index)

    def _on_moved(self, source: int, target: int) -> None:
        widget = self.stack.widget(source)
        if widget is None:
            return
        self.stack.removeWidget(widget)
        self.stack.insertWidget(target, widget)
        self.stack.setCurrentIndex(self.tab_bar.currentIndex())


@dataclass
class NavigationItem:
    """One entry of `FluentNavigationBar` (or a header when `header` is set)."""

    key: str
    text: str
    icon: str = ""
    header: bool = False
    data: object = None
    children: list[NavigationItem] = field(default_factory=list)


class _ExpanderHeader(QWidget):
    clicked = Signal()

    def __init__(self, title: str, caption: str, icon: str, parent: QWidget) -> None:
        super().__init__(parent)
        self._title = title
        self._caption = caption
        self._icon = icon
        self._expanded = False
        self._hover = False
        self.setFixedHeight(64 if caption else 48)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        bind_theme(self, self.update)

    def enterEvent(self, event: QEnterEvent) -> None:  # noqa: N802
        self._hover = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event: QEvent) -> None:  # noqa: N802
        self._hover = False
        self.update()
        super().leaveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        palette = palette_for(self)
        painter = antialiased_painter(self)
        if self._hover:
            paint_surface(
                painter, QRectF(self.rect()).adjusted(1, 1, -1, -1), palette.subtle_hover, None, RADIUS_CARD - 1
            )
        x = SPACE_L
        if self._icon:
            themed_icon(self._icon, palette).paint(painter, x, (self.height() - ICON_SIZE) // 2, ICON_SIZE, ICON_SIZE)
        x += ICON_SIZE + SPACE_L
        body = fluent_font(self.font(), TYPE_BODY)
        caption = fluent_font(self.font(), TYPE_CAPTION)
        body_h = QFontMetrics(body).height()
        caption_h = QFontMetrics(caption).height() if self._caption else 0
        y = (self.height() - body_h - caption_h) / 2
        width = self.width() - x - 48
        painter.setFont(body)
        painter.setPen(palette.text_primary)
        painter.drawText(
            QRectF(x, y, width, body_h), int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter), self._title
        )
        if self._caption:
            painter.setFont(caption)
            painter.setPen(palette.text_secondary)
            painter.drawText(
                QRectF(x, y + body_h, width, caption_h),
                int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter),
                self._caption,
            )
        chevron = "chevron-up" if self._expanded else "chevron-down"
        themed_icon(chevron, palette, palette.text_secondary, 12).paint(
            painter, self.width() - SPACE_L - 12, (self.height() - 12) // 2, 12, 12
        )
        painter.end()

    def set_expanded(self, *, expanded: bool) -> None:
        self._expanded = expanded
        self.update()
