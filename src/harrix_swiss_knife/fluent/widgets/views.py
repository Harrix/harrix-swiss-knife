"""Fluent scroll areas, item views, card grids, graphics views, and the promotion carousel."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import (
    QAbstractListModel,
    QEasingCurve,
    QEvent,
    QModelIndex,
    QObject,
    QPersistentModelIndex,
    QPropertyAnimation,
    QRect,
    QRectF,
    Qt,
    QTimer,
    Signal,
)
from PySide6.QtGui import QBrush, QColor, QPainter, QPen, QPixmap, QWheelEvent
from PySide6.QtWidgets import (
    QAbstractItemView,
    QAbstractScrollArea,
    QFrame,
    QGraphicsLineItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsView,
    QHeaderView,
    QListView,
    QListWidget,
    QScrollArea,
    QScrollBar,
    QSizePolicy,
    QStackedWidget,
    QTableView,
    QTableWidget,
    QTreeView,
    QTreeWidget,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife.fluent.paint import antialiased_painter, paint_surface, rounded_path, with_alpha
from harrix_swiss_knife.fluent.style import item_view_qss, lucide_qss_url, scroll_bar_qss
from harrix_swiss_knife.fluent.theme import bind_theme, css, palette_for
from harrix_swiss_knife.fluent.tokens import (
    ANIMATION_NORMAL,
    ANIMATION_SLOW,
    CARD_GRID_SPACING,
    RADIUS_CARD,
    RADIUS_CONTROL,
    SPACE_S,
)
from harrix_swiss_knife.qt_flow_layout import FlowLayout

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

    from PySide6.QtGui import QMouseEvent, QPaintEvent
    from PySide6.QtWidgets import QStyleOptionGraphicsItem

_WHEEL_STEP_PX = 120
_CAROUSEL_INTERVAL_MS = 5000


class FluentCardGrid(QWidget):
    """Wrapping grid of fixed-size cards on a `FlowLayout` (height follows width)."""

    def __init__(self, parent: QWidget | None = None, *, spacing: int = CARD_GRID_SPACING) -> None:
        """Create an empty card grid."""
        super().__init__(parent)
        self._layout = FlowLayout(self, margin=0, h_spacing=spacing, v_spacing=spacing)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

    def add_card(self, card: QWidget) -> None:
        """Append a card."""
        card.setParent(self)
        self._layout.addWidget(card)
        card.show()

    def cards(self) -> list[QWidget]:
        """Return the cards in order."""
        result: list[QWidget] = []
        for index in range(self._layout.count()):
            item = self._layout.itemAt(index)
            widget = item.widget() if item is not None else None
            if widget is not None:
                result.append(widget)
        return result

    def clear(self) -> None:
        """Remove and delete every card."""
        while self._layout.count():
            item = self._layout.takeAt(0)
            widget = item.widget() if item is not None else None
            if widget is not None:
                widget.hide()
                widget.deleteLater()

    def count(self) -> int:
        """Return the number of cards."""
        return self._layout.count()

    def flow_layout(self) -> FlowLayout:
        """Return the underlying flow layout."""
        return self._layout


class FluentGraphicsItem(QGraphicsRectItem):
    """Rounded, selectable, movable node item with a title."""

    def __init__(self, title: str, rect: QRectF | None = None, *, accent: QColor | None = None) -> None:
        """Create a node item."""
        super().__init__(rect or QRectF(0, 0, 160, 64))
        self.title = title
        self._accent = accent or QColor("#005fb8")
        flags = QGraphicsRectItem.GraphicsItemFlag
        self.setFlags(flags.ItemIsMovable | flags.ItemIsSelectable | flags.ItemSendsGeometryChanges)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, /, widget: QWidget | None = None) -> None:
        """Paint a card-like node; the selected node gets an accent border."""
        del option, widget
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, on=True)
        stroke = self._accent if self.isSelected() else QColor(0, 0, 0, 40)
        paint_surface(
            painter,
            self.rect(),
            QColor(255, 255, 255, 235),
            stroke,
            RADIUS_CARD,
            stroke_width=2 if self.isSelected() else 1,
        )
        painter.fillRect(
            QRectF(self.rect().left() + 8, self.rect().top() + 10, 3, self.rect().height() - 20), self._accent
        )
        painter.setPen(QColor(0, 0, 0, 228))
        painter.drawText(
            self.rect().adjusted(20, 0, -8, 0),
            int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft),
            self.title,
        )


class FluentGraphicsLineItem(QGraphicsLineItem):
    """Connector line between two `FluentGraphicsItem` nodes that follows them."""

    def __init__(self, source: QGraphicsRectItem, target: QGraphicsRectItem, *, color: QColor | None = None) -> None:
        """Create a connector."""
        super().__init__()
        self._source = source
        self._target = target
        pen = QPen(color or QColor(0, 0, 0, 110), 1.5)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        self.setPen(pen)
        self.setZValue(-1)
        self.update_position()

    def update_position(self) -> None:
        """Re-anchor the line to the node centers."""
        start = self._source.sceneBoundingRect().center()
        end = self._target.sceneBoundingRect().center()
        self.setLine(start.x(), start.y(), end.x(), end.y())


class FluentGraphicsScene(QGraphicsScene):
    """Graphics scene with a theme-colored dotted grid background."""

    def __init__(self, parent: QObject | None = None, *, grid: int = 20) -> None:
        """Create a scene with a `grid` px dot pitch (`0` = no grid)."""
        super().__init__(parent)
        self._grid = grid
        self._dot = QColor(0, 0, 0, 40)
        self._background = QColor(0, 0, 0, 0)

    def drawBackground(self, painter: QPainter, rect: QRectF | QRect, /) -> None:  # noqa: N802
        """Paint the fill and grid dots."""
        rect = QRectF(rect)
        painter.fillRect(rect, self._background)
        if self._grid <= 0:
            return
        painter.setPen(QPen(self._dot, 1.5))
        left = int(rect.left()) - int(rect.left()) % self._grid
        top = int(rect.top()) - int(rect.top()) % self._grid
        for x in range(left, int(rect.right()) + 1, self._grid):
            for y in range(top, int(rect.bottom()) + 1, self._grid):
                painter.drawPoint(x, y)

    def set_colors(self, background: QColor, dot: QColor) -> None:
        """Change fill and grid colors."""
        self._background, self._dot = background, dot
        self.update()


class FluentGraphicsView(QGraphicsView):
    """Graphics view with antialiasing, wheel zoom (Ctrl), and pan by middle drag."""

    def __init__(self, scene: QGraphicsScene | None = None, parent: QWidget | None = None) -> None:
        """Create a graphics view."""
        super().__init__(parent)
        self.setScene(scene or FluentGraphicsScene(self))
        self.setRenderHint(QPainter.RenderHint.Antialiasing, enabled=True)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        bind_theme(self, self.refresh_theme)

    def refresh_theme(self) -> None:
        """Re-color the background and grid."""
        palette = palette_for(self)
        scene = self.scene()
        if isinstance(scene, FluentGraphicsScene):
            scene.set_colors(
                palette.solid_tertiary_bg if palette.dark else palette.solid_quarternary_bg,
                with_alpha(palette.text_primary, 40),
            )
        self.setStyleSheet(
            f"QGraphicsView {{ border: 1px solid {css(palette.card_stroke)}; border-radius: {RADIUS_CARD}px; }}\n"
            f"{scroll_bar_qss(palette)}"
        )

    def wheelEvent(self, event: QWheelEvent) -> None:  # noqa: N802
        """Zoom with Ctrl+wheel, scroll otherwise."""
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
            self.scale(factor, factor)
            event.accept()
            return
        super().wheelEvent(event)


class FluentListView(QListView):
    """Model-based list view with Fluent item chrome."""

    def __init__(self, parent: QWidget | None = None, *, transparent: bool = True, smooth: bool = True) -> None:
        """Create a list view."""
        super().__init__(parent)
        self._transparent = transparent
        self.setObjectName(self.objectName() or "FluentListView")
        _init_fluent_view(self, smooth=smooth)
        bind_theme(self, self.refresh_theme)

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802
        """Paint items, then the accent pill next to the current item."""
        super().paintEvent(event)
        _paint_selection_indicator(self)

    def refresh_theme(self) -> None:
        """Re-apply item chrome."""
        self.setStyleSheet(
            item_view_qss(palette_for(self), f"QListView#{self.objectName()}", transparent=self._transparent)
        )


class FluentListWidget(QListWidget):
    """List widget with rounded hover/selection, accent indicator, and smooth scrolling."""

    def __init__(self, parent: QWidget | None = None, *, transparent: bool = True, smooth: bool = True) -> None:
        """Create a list widget."""
        super().__init__(parent)
        self._transparent = transparent
        self.setObjectName(self.objectName() or "FluentListWidget")
        _init_fluent_view(self, smooth=smooth)
        bind_theme(self, self.refresh_theme)

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802
        """Paint items, then the accent pill next to the current item."""
        super().paintEvent(event)
        _paint_selection_indicator(self)

    def refresh_theme(self) -> None:
        """Re-apply item chrome."""
        self.setStyleSheet(
            item_view_qss(palette_for(self), f"QListWidget#{self.objectName()}", transparent=self._transparent)
        )


class FluentPromotionView(QWidget):
    """Auto-advancing image carousel with page dots and rounded corners."""

    current_changed = Signal(int)

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        pixmaps: Sequence[QPixmap] = (),
        interval_ms: int = _CAROUSEL_INTERVAL_MS,
    ) -> None:
        """Create a carousel."""
        super().__init__(parent)
        self._pixmaps = list(pixmaps)
        self._current = 0
        self._timer = QTimer(self)
        self._timer.setInterval(interval_ms)
        self._timer.timeout.connect(self.next_page)
        if self._pixmaps:
            self._timer.start()
        self.setMinimumHeight(160)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        bind_theme(self, self.update)

    def add_pixmap(self, pixmap: QPixmap) -> None:
        """Append a slide."""
        self._pixmaps.append(pixmap)
        if not self._timer.isActive():
            self._timer.start()
        self.update()

    def current(self) -> int:
        """Return the shown slide index."""
        return self._current

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Jump to the slide whose dot was clicked."""
        position = event.position()
        for index, dot in enumerate(self._dot_rects()):
            if dot.adjusted(-4, -4, 4, 4).contains(position):
                self.set_current(index)
                return

    def next_page(self) -> None:
        """Show the next slide (wraps around)."""
        if self._pixmaps:
            self.set_current((self._current + 1) % len(self._pixmaps))

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Paint the clipped slide and the page dots."""
        palette = palette_for(self)
        painter = antialiased_painter(self)
        rect = QRectF(self.rect())
        painter.setClipPath(rounded_path(rect, RADIUS_CARD))
        if self._pixmaps:
            pixmap = self._pixmaps[self._current]
            scaled = pixmap.scaled(
                self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation
            )
            painter.drawPixmap(
                int((self.width() - scaled.width()) / 2), int((self.height() - scaled.height()) / 2), scaled
            )
        else:
            painter.fillRect(rect, palette.subtle_hover)
        painter.setClipping(False)
        for index, dot in enumerate(self._dot_rects()):
            color = QColor(255, 255, 255, 240 if index == self._current else 130)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(color))
            painter.drawRoundedRect(dot, dot.height() / 2, dot.height() / 2)
        painter.end()

    def set_current(self, index: int) -> None:
        """Show slide `index`."""
        if not self._pixmaps:
            return
        index %= len(self._pixmaps)
        if index == self._current:
            return
        self._current = index
        self.update()
        self.current_changed.emit(index)

    def _dot_rects(self) -> list[QRectF]:
        count = len(self._pixmaps)
        if count <= 1:
            return []
        widths = [16.0 if index == self._current else 6.0 for index in range(count)]
        total = sum(widths) + (count - 1) * 6
        x = (self.width() - total) / 2
        rects = []
        for width in widths:
            rects.append(QRectF(x, self.height() - 16, width, 6))
            x += width + 6
        return rects


class FluentScrollArea(QScrollArea):
    """Transparent scroll area with thin Fluent scrollbars and smooth wheel scrolling."""

    def __init__(self, parent: QWidget | None = None, *, smooth: bool = True) -> None:
        """Create a scroll area (`widgetResizable` is on)."""
        super().__init__(parent)
        self.setWidgetResizable(True)
        _prepare_scroll_area(self, smooth=smooth)
        self.setObjectName(self.objectName() or "FluentScrollArea")
        bind_theme(self, self.refresh_theme)

    def refresh_theme(self) -> None:
        """Re-apply transparent background and scrollbar chrome."""
        palette = palette_for(self)
        self.setStyleSheet(f"QScrollArea {{ background: transparent; border: none; }}\n{scroll_bar_qss(palette)}")
        self.viewport().setAutoFillBackground(False)
        content = self.widget()
        if content is not None:
            content.setAutoFillBackground(False)

    def setWidget(self, widget: QWidget) -> None:  # noqa: N802
        """Set the content widget (kept transparent)."""
        super().setWidget(widget)
        widget.setAutoFillBackground(False)
        widget.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, on=False)


class FluentScrollBar(QScrollBar):
    """Stand-alone thin rounded scrollbar."""

    def __init__(self, orientation: Qt.Orientation = Qt.Orientation.Vertical, parent: QWidget | None = None) -> None:
        """Create a scrollbar."""
        super().__init__(orientation, parent)
        bind_theme(self, lambda: self.setStyleSheet(scroll_bar_qss(palette_for(self))))


class FluentScrollPage(FluentScrollArea):
    """Scroll area whose content is a vertical stack of page sections."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Create a scroll page with an empty content widget."""
        super().__init__(parent)
        self._content = QWidget(self)
        self._content.setObjectName("FluentScrollPageContent")
        self.content_layout = QVBoxLayout(self._content)
        self.content_layout.setContentsMargins(36, 20, 36, 36)
        self.content_layout.setSpacing(SPACE_S * 2)
        self.content_layout.addStretch(1)
        self.setWidget(self._content)

    def add_section(self, widget: QWidget) -> None:
        """Append a section before the trailing stretch."""
        self.content_layout.insertWidget(self.content_layout.count() - 1, widget)

    def scroll_to(self, widget: QWidget) -> None:
        """Scroll so `widget` is at the top of the viewport."""
        top = widget.mapTo(self._content, widget.rect().topLeft()).y()
        bar = self.verticalScrollBar()
        animation = QPropertyAnimation(bar, b"value", self)
        animation.setDuration(ANIMATION_NORMAL * 2)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.setStartValue(bar.value())
        animation.setEndValue(min(bar.maximum(), top))
        animation.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)


class FluentScrollPageArea(QStackedWidget):
    """Stack of `FluentScrollPage` pages switched by key."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Create an empty page stack."""
        super().__init__(parent)
        self._pages: dict[str, FluentScrollPage] = {}

    def add_page(self, key: str) -> FluentScrollPage:
        """Create and register a page under `key`."""
        page = FluentScrollPage(self)
        self._pages[key] = page
        self.addWidget(page)
        return page

    def page(self, key: str) -> FluentScrollPage | None:
        """Return the page registered under `key`."""
        return self._pages.get(key)

    def show_page(self, key: str) -> None:
        """Switch to the page registered under `key`."""
        page = self._pages.get(key)
        if page is not None:
            self.setCurrentWidget(page)


class FluentTableView(QTableView):
    """Model-based table view with Fluent chrome."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Create a table view."""
        super().__init__(parent)
        self.setObjectName(self.objectName() or "FluentTableView")
        _setup_table(self)
        _init_fluent_view(self)
        bind_theme(self, self.refresh_theme)

    def refresh_theme(self) -> None:
        """Re-apply table chrome."""
        self.setStyleSheet(_table_qss(self, f"QTableView#{self.objectName()}"))


class FluentTableWidget(QTableWidget):
    """Table widget with hairline rows, no grid, and Fluent headers."""

    def __init__(self, rows: int = 0, columns: int = 0, parent: QWidget | None = None) -> None:
        """Create a table widget."""
        super().__init__(rows, columns, parent)
        self.setObjectName(self.objectName() or "FluentTableWidget")
        _setup_table(self)
        _init_fluent_view(self)
        bind_theme(self, self.refresh_theme)

    def refresh_theme(self) -> None:
        """Re-apply table chrome."""
        selector = f"QTableWidget#{self.objectName()}"
        self.setStyleSheet(_table_qss(self, selector))


class FluentTreeView(QTreeView):
    """Model-based tree view with Fluent chrome."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Create a tree view."""
        super().__init__(parent)
        self.setObjectName(self.objectName() or "FluentTreeView")
        self.setAnimated(True)
        self.setIndentation(20)
        _init_fluent_view(self)
        bind_theme(self, self.refresh_theme)

    def refresh_theme(self) -> None:
        """Re-apply tree chrome."""
        self.setStyleSheet(_tree_qss(self, f"QTreeView#{self.objectName()}"))


class FluentTreeWidget(QTreeWidget):
    """Tree widget with rounded rows and Lucide branch chevrons."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Create a tree widget."""
        super().__init__(parent)
        self.setObjectName(self.objectName() or "FluentTreeWidget")
        self.setAnimated(True)
        self.setIndentation(20)
        _init_fluent_view(self)
        bind_theme(self, self.refresh_theme)

    def refresh_theme(self) -> None:
        """Re-apply tree chrome."""
        self.setStyleSheet(_tree_qss(self, f"QTreeWidget#{self.objectName()}"))


class FluentVirtualList(FluentListView):
    """List of up to millions of rows: text is produced lazily by a callback."""

    def __init__(
        self, parent: QWidget | None = None, *, count: int = 0, provider: Callable[[int], str] | None = None
    ) -> None:
        """Create a virtual list.

        Args:

        - `parent` (`QWidget | None`): Optional parent.
        - `count` (`int`): Number of rows.
        - `provider` (`Callable[[int], str] | None`): Returns the text of a row.

        """
        super().__init__(parent)
        self._model = _StringListModel(provider or str, count, self)
        self.setModel(self._model)
        self.setUniformItemSizes(True)
        self.setLayoutMode(QListView.LayoutMode.Batched)
        self.setBatchSize(200)

    def set_rows(self, count: int, provider: Callable[[int], str]) -> None:
        """Replace the row count and text provider."""
        self._model.reset(provider, count)


class SmoothScroller(QObject):
    """Animate wheel scrolling of a `QAbstractScrollArea` instead of jumping."""

    def __init__(self, area: QAbstractScrollArea, *, orientation: Qt.Orientation = Qt.Orientation.Vertical) -> None:
        """Install smooth wheel scrolling on `area`."""
        super().__init__(area)
        self._area = area
        self._orientation = orientation
        bar = self._bar()
        self._animation = QPropertyAnimation(bar, b"value", self)
        self._animation.setDuration(ANIMATION_SLOW)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._target = bar.value()
        self._viewport = area.viewport()
        self._viewport.installEventFilter(self)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Turn wheel events into an animated scroll."""
        if watched is self._viewport and event.type() == QEvent.Type.Wheel and isinstance(event, QWheelEvent):
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                return False
            return self.scroll_by_wheel(event)
        return False

    def scroll_by_wheel(self, event: QWheelEvent) -> bool:
        """Scroll for one wheel event; return whether it was consumed."""
        bar = self._bar()
        if bar.maximum() <= bar.minimum():
            return False
        delta = event.angleDelta().y() or event.angleDelta().x()
        if not event.pixelDelta().isNull():
            bar.setValue(bar.value() - (event.pixelDelta().y() or event.pixelDelta().x()))
            self._target = bar.value()
            return True
        if self._animation.state() != QPropertyAnimation.State.Running:
            self._target = bar.value()
        step = bar.singleStep() * 3 if bar.singleStep() > 1 else _WHEEL_STEP_PX
        self._target = max(bar.minimum(), min(bar.maximum(), self._target - round(delta / _WHEEL_STEP_PX * step)))
        self._animation.stop()
        self._animation.setStartValue(bar.value())
        self._animation.setEndValue(self._target)
        self._animation.start()
        return True

    def _bar(self) -> QScrollBar:
        if self._orientation == Qt.Orientation.Horizontal:
            return self._area.horizontalScrollBar()
        return self._area.verticalScrollBar()


class _StringListModel(QAbstractListModel):
    def __init__(self, provider: Callable[[int], str], count: int, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._provider = provider
        self._count = count

    def data(self, index: QModelIndex | QPersistentModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> object:
        if role == Qt.ItemDataRole.DisplayRole and index.isValid():
            return self._provider(index.row())
        return None

    def reset(self, provider: Callable[[int], str], count: int) -> None:
        self.beginResetModel()
        self._provider = provider
        self._count = count
        self.endResetModel()

    def rowCount(self, parent: QModelIndex | QPersistentModelIndex | None = None) -> int:  # noqa: N802
        if parent is not None and parent.isValid():
            return 0
        return self._count


def _header_qss(selector: str, *, palette_widget: QWidget) -> str:
    palette = palette_for(palette_widget)
    return f"""
{selector} QHeaderView {{ background: transparent; border: none; }}
{selector} QHeaderView::section {{
    background: transparent;
    color: {css(palette.text_secondary)};
    border: none;
    border-bottom: 1px solid {css(palette.divider)};
    padding: 6px 8px;
}}
{selector} QHeaderView::section:hover {{ background: {css(palette.subtle_hover)}; }}
{selector} QTableCornerButton::section {{ background: transparent; border: none; }}
"""


def _init_fluent_view(view: QAbstractItemView, *, smooth: bool = True) -> None:
    _prepare_scroll_area(view, smooth=smooth)
    view.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
    view.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
    view.setMouseTracking(True)
    view.viewport().setAutoFillBackground(False)


def _paint_selection_indicator(view: QAbstractItemView) -> None:
    index = view.currentIndex()
    if not index.isValid() or not view.selectionModel().isSelected(index):
        return
    rect = view.visualRect(index)
    if rect.isNull():
        return
    palette = palette_for(view)
    painter = antialiased_painter(view.viewport())
    height = min(16, max(8, rect.height() - 16))
    pill = QRectF(rect.left() + 4, rect.center().y() - height / 2 + 1, 3, height)
    paint_surface(painter, pill, palette.accent, None, 1.5)
    painter.end()


def _prepare_scroll_area(area: QAbstractScrollArea, *, smooth: bool) -> None:
    area.setFrameShape(QFrame.Shape.NoFrame)
    if smooth:
        SmoothScroller(area)


def _setup_table(table: QTableView) -> None:
    table.setShowGrid(False)
    table.setAlternatingRowColors(False)
    table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    table.verticalHeader().setVisible(False)
    table.verticalHeader().setDefaultSectionSize(36)
    table.horizontalHeader().setHighlightSections(False)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
    table.horizontalHeader().setStretchLastSection(True)
    table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)


def _table_qss(table: QWidget, selector: str) -> str:
    palette = palette_for(table)
    return f"""
{selector} {{
    background: {css(palette.card_bg)};
    color: {css(palette.text_primary)};
    border: 1px solid {css(palette.card_stroke)};
    border-radius: {RADIUS_CARD}px;
    outline: none;
    gridline-color: transparent;
}}
{selector}::item {{ border: none; border-bottom: 1px solid {css(palette.divider)}; padding: 0px 8px; }}
{selector}::item:hover {{ background: {css(palette.subtle_hover)}; }}
{selector}::item:selected {{ background: {css(palette.subtle_pressed)}; color: {css(palette.text_primary)}; }}
{_header_qss(selector, palette_widget=table)}
{scroll_bar_qss(palette)}
"""


def _tree_qss(tree: QWidget, selector: str) -> str:
    palette = palette_for(tree)
    closed = lucide_qss_url("chevron-right", palette.text_secondary, 12)
    opened = lucide_qss_url("chevron-down", palette.text_secondary, 12)
    return f"""
{item_view_qss(palette, selector)}
{selector}::item {{ margin: 1px 0px; border-radius: {RADIUS_CONTROL}px; }}
{selector}::branch {{ background: transparent; }}
{selector}::branch:has-children:closed {{ image: url("{closed}"); }}
{selector}::branch:has-children:open {{ image: url("{opened}"); }}
{_header_qss(selector, palette_widget=tree)}
"""
