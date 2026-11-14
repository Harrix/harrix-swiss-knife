"""Qt year heatmap shared by Habits charts and TickTick.

Cells stay square. Width comes from the real week columns of the visible
months, including weeks split across a month boundary. The widget does not
stretch seven rows to fill the page.

"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import TYPE_CHECKING

from PySide6.QtCore import QPoint, QRect, QSize, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QFont, QMouseEvent, QPainter, QPen, QResizeEvent
from PySide6.QtWidgets import (
    QAbstractScrollArea,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QToolTip,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife.apps.common.calendar_heatmap import (
    HEATMAP_WEEK_STARTS_ON,
    habit_heatmap_month_column_count,
    habit_heatmap_month_ranges,
    habit_heatmap_week_start,
    habit_heatmap_weekday_index,
)
from harrix_swiss_knife.apps.common.chart_theme import chart_ink, chart_series_color, chart_tint
from harrix_swiss_knife.fluent.theme import FluentTheme, bind_theme, css, mix
from harrix_swiss_knife.qt_flow_layout import FlowLayout

if TYPE_CHECKING:
    from collections.abc import Sequence

_CELL_MIN = 10
_CELL_MAX = 22
_CELL_GAP = 3
_MONTH_GAP = 10
_GUTTER = 32
_PAD = 2
_MONTH_LABEL_H = 16
_RADIUS = 2
_LABEL_SHORT_ROW = 16
_MARK_MIN_CELL = 14
_LIGHT_MARK_CUTOFF = 150
_VIEWPORT_FALLBACK = 80
_FALLBACK_WIDTH = 320
_PY_WEEKDAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")


@dataclass(frozen=True)
class HeatmapCell:
    """One painted day."""

    day: date
    rect: QRect
    color: str | None
    mark: str
    tip: str


class YearHeatmap(QWidget):
    """Square-cell calendar for one date range, with a legend that does not stretch."""

    day_clicked = Signal(object)

    def __init__(self, parent: QWidget | None = None) -> None:
        """Build an empty calendar. `set_calendar` supplies the days."""
        super().__init__(parent)
        self.week_starts_on = HEATMAP_WEEK_STARTS_ON
        self.selected_days: set[date] = set()
        self._start: date | None = None
        self._end: date | None = None
        self._colors: dict[date, str | None] = {}
        self._marks: dict[date, str] = {}
        self._tips: dict[date, str] = {}
        self._layout_guard = False
        self._relayout_pending = False

        self._scroll = QScrollArea(self)
        self._scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self._scroll.setWidgetResizable(False)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._grid = _Grid(self)
        self._scroll.setWidget(self._grid)
        self._scroll.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustIgnored)
        self._scroll.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed)
        self._legend = _Legend(self)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        layout.addWidget(self._scroll)
        layout.addWidget(self._legend)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        bind_theme(self, self._relayout)

    def minimumSizeHint(self) -> QSize:  # noqa: N802
        """Stay as wide as the column allows. The grid scrolls inside itself."""
        return QSize(0, self._content_height())

    def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        """Refit square cells to the new width."""
        super().resizeEvent(event)
        self._relayout()
        if self._relayout_pending:
            return
        self._relayout_pending = True
        QTimer.singleShot(0, self._relayout_after_resize)

    def set_calendar(
        self,
        start: date,
        end: date,
        colors: dict[date, str | None],
        *,
        legend: Sequence[tuple[str, str]],
        marks: dict[date, str] | None = None,
        tooltips: dict[date, str] | None = None,
        selected: set[date] | None = None,
        week_starts_on: int | None = None,
    ) -> None:
        """Replace the visible range. `None` colors are no-record outlines."""
        self._start = start
        self._end = end
        self._colors = colors
        self._marks = dict(marks or {})
        self._tips = dict(tooltips or {})
        self.selected_days = set(selected or ())
        if week_starts_on is not None:
            self.week_starts_on = week_starts_on
        self._legend.set_items(legend)
        self._relayout()

    def set_selected(self, days: set[date]) -> None:
        """Move the contrast outline without rebuilding the calendar."""
        self.selected_days = set(days)
        self._grid.update()

    def sizeHint(self) -> QSize:  # noqa: N802
        """Report the calendar height without adopting the scrolled grid width."""
        return QSize(_FALLBACK_WIDTH, self._content_height())

    def _content_height(self) -> int:
        layout = self.layout()
        spacing = layout.spacing() if layout is not None else 0
        legend_h = self._legend.sizeHint().height()
        scroll_h = self._scroll.height()
        if scroll_h < _MONTH_LABEL_H + _CELL_MIN:
            scroll_h = _MONTH_LABEL_H + 7 * (_CELL_MIN + _CELL_GAP) + _PAD * 2
        return scroll_h + legend_h + spacing

    def _relayout(self) -> None:
        if self._layout_guard or self._start is None or self._end is None:
            return
        self._layout_guard = True
        try:
            months = habit_heatmap_month_ranges(self._start, self._end)
            columns = [
                habit_heatmap_month_column_count(month_start, month_end, week_starts_on=self.week_starts_on)
                for month_start, month_end in months
            ]
            viewport = max(self.width(), self._scroll.viewport().width())
            if viewport < _VIEWPORT_FALLBACK:
                viewport = _FALLBACK_WIDTH
            cell, _scrolling = _cell_size(viewport, sum(columns), len(months))
            cells, month_labels, width, height = _place_cells(
                self._start,
                self._end,
                cell=cell,
                colors=self._colors,
                marks=self._marks,
                tips=self._tips,
                week_starts_on=self.week_starts_on,
            )
            self._grid.set_scene(cells, month_labels, width, height)
            bar = self._scroll.horizontalScrollBar().sizeHint().height() if width > viewport + 1 else 0
            self._scroll.setFixedHeight(height + bar)
            self.updateGeometry()
        finally:
            self._layout_guard = False

    def _relayout_after_resize(self) -> None:
        self._relayout_pending = False
        self._relayout()


class _Grid(QWidget):
    """Painted month blocks. Mouse hits stay in pixel space."""

    def __init__(self, owner: YearHeatmap) -> None:
        super().__init__(owner)
        self._owner = owner
        self._cells: list[HeatmapCell] = []
        self._month_labels: list[tuple[str, int]] = []
        self.setMouseTracking(True)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        cell = self._cell_at(event.position().toPoint())
        if cell is None or not cell.tip:
            QToolTip.hideText()
            return
        QToolTip.showText(event.globalPosition().toPoint(), cell.tip, self)

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() != Qt.MouseButton.LeftButton:
            return
        cell = self._cell_at(event.position().toPoint())
        if cell is not None:
            self._owner.day_clicked.emit(cell.day)

    def paintEvent(self, _event: object) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, on=True)
        palette = FluentTheme.instance().palette()
        ink = QColor(chart_ink())
        font = QFont(self.font())
        font.setPixelSize(11)
        painter.setFont(font)
        painter.setPen(ink)
        week_starts_on = self._owner.week_starts_on
        if self._cells:
            row_h = self._cells[0].rect.height() + _CELL_GAP
            top = self._cells[0].rect.top()
            for row in range(7):
                label = _row_label(row, week_starts_on=week_starts_on)
                text = label[:2] if row_h < _LABEL_SHORT_ROW else label[:3]
                painter.drawText(QRect(0, top + row * row_h, _GUTTER - 4, row_h), Qt.AlignmentFlag.AlignVCenter, text)
        for label, x in self._month_labels:
            painter.drawText(
                QRect(x, 0, 48, _MONTH_LABEL_H),
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom,
                label,
            )
        selected = self._owner.selected_days
        accent = QColor(chart_series_color(0))
        page = palette.card_bg
        for cell in self._cells:
            rect = cell.rect
            painter.setPen(Qt.PenStyle.NoPen)
            if cell.color is None:
                painter.setBrush(QColor(page))
                painter.drawRoundedRect(rect, _RADIUS, _RADIUS)
                painter.setPen(QPen(QColor(heatmap_hairline()), 1))
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawRoundedRect(rect, _RADIUS, _RADIUS)
            else:
                painter.setBrush(QColor(cell.color))
                painter.drawRoundedRect(rect, _RADIUS, _RADIUS)
            if cell.mark and rect.width() >= _MARK_MIN_CELL:
                painter.setPen(_mark_color(cell.color))
                painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, cell.mark)
            if cell.day in selected:
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.setPen(QPen(page, 3))
                painter.drawRoundedRect(rect.adjusted(1, 1, -1, -1), _RADIUS, _RADIUS)
                painter.setPen(QPen(accent, 2))
                painter.drawRoundedRect(rect.adjusted(2, 2, -2, -2), _RADIUS, _RADIUS)
        painter.end()

    def set_scene(
        self,
        cells: list[HeatmapCell],
        month_labels: list[tuple[str, int]],
        width: int,
        height: int,
    ) -> None:
        self._cells = cells
        self._month_labels = month_labels
        self.setFixedSize(max(width, 1), max(height, 1))
        self.update()

    def _cell_at(self, point: QPoint) -> HeatmapCell | None:
        for cell in self._cells:
            if cell.rect.contains(point):
                return cell
        return None


class _Legend(QWidget):
    """Wrapping color key under the grid. It stays outside the horizontal scroller."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._items: list[tuple[str, str]] = []
        self._flow = FlowLayout(self, margin=0, h_spacing=12, v_spacing=4)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)

    def hasHeightForWidth(self) -> bool:  # noqa: N802
        return True

    def heightForWidth(self, width: int) -> int:  # noqa: N802
        return self._flow.heightForWidth(width)

    def set_items(self, items: Sequence[tuple[str, str]]) -> None:
        self._items = list(items)
        self._rebuild()

    def sizeHint(self) -> QSize:  # noqa: N802
        return self._flow.sizeHint()

    def _rebuild(self) -> None:
        while self._flow.count():
            item = self._flow.takeAt(0)
            widget = item.widget() if item is not None else None
            if widget is not None:
                widget.deleteLater()
        palette = FluentTheme.instance().palette()
        ink = css(mix(palette.window_bg, palette.text_primary))
        for color, label in self._items:
            row = QWidget(self)
            box = QHBoxLayout(row)
            box.setContentsMargins(0, 0, 0, 0)
            box.setSpacing(6)
            swatch = QLabel(row)
            swatch.setFixedSize(12, 12)
            swatch.setStyleSheet(f"background: {color}; border-radius: 2px;")
            text = QLabel(label, row)
            text.setStyleSheet(f"color: {ink};")
            box.addWidget(swatch)
            box.addWidget(text)
            self._flow.addWidget(row)
        self.updateGeometry()


def heatmap_column_count(start: date, end: date, *, week_starts_on: int = HEATMAP_WEEK_STARTS_ON) -> int:
    """Return week columns for `[start, end]`, without assuming 52 columns."""
    return sum(
        habit_heatmap_month_column_count(month_start, month_end, week_starts_on=week_starts_on)
        for month_start, month_end in habit_heatmap_month_ranges(start, end)
    )


def heatmap_hairline() -> str:
    """Return the outline used for days with no record."""
    palette = FluentTheme.instance().palette()
    return chart_tint(palette.card_bg, palette.text_secondary, 0.28).name()


def _cell_size(viewport_width: int, columns: int, months: int) -> tuple[int, bool]:
    gaps = max(0, columns - months) * _CELL_GAP + max(0, months - 1) * _MONTH_GAP
    available = max(viewport_width, 1) - _GUTTER - _PAD * 2 - gaps
    raw = available / max(columns, 1)
    if raw < _CELL_MIN:
        return _CELL_MIN, True
    return min(_CELL_MAX, int(raw)), False


def _mark_color(fill: str | None) -> QColor:
    color = QColor(fill or "#ffffff")
    if color.lightness() < _LIGHT_MARK_CUTOFF:
        return QColor("#ffffff")
    return QColor(chart_ink())


def _place_cells(
    start: date,
    end: date,
    *,
    cell: int,
    colors: dict[date, str | None],
    marks: dict[date, str],
    tips: dict[date, str],
    week_starts_on: int,
) -> tuple[list[HeatmapCell], list[tuple[str, int]], int, int]:
    step = cell + _CELL_GAP
    x = _GUTTER + _PAD
    top = _MONTH_LABEL_H + _PAD
    placed: list[HeatmapCell] = []
    month_labels: list[tuple[str, int]] = []
    for month_start, month_end in habit_heatmap_month_ranges(start, end):
        month_labels.append((month_start.strftime("%b"), x))
        week0 = habit_heatmap_week_start(month_start, week_starts_on=week_starts_on)
        day = month_start
        while day <= month_end:
            column = (habit_heatmap_week_start(day, week_starts_on=week_starts_on) - week0).days // 7
            row = habit_heatmap_weekday_index(day, week_starts_on=week_starts_on)
            rect = QRect(x + column * step, top + row * step, cell, cell)
            placed.append(
                HeatmapCell(
                    day=day,
                    rect=rect,
                    color=colors.get(day),
                    mark=marks.get(day, ""),
                    tip=tips.get(day, ""),
                ),
            )
            day += timedelta(days=1)
        columns = habit_heatmap_month_column_count(month_start, month_end, week_starts_on=week_starts_on)
        x += columns * step - _CELL_GAP + _MONTH_GAP
    width = max(x - _MONTH_GAP + _PAD, _GUTTER + cell)
    height = top + 7 * step - _CELL_GAP + _PAD
    return placed, month_labels, width, height


def _row_label(row: int, *, week_starts_on: int) -> str:
    return _PY_WEEKDAYS[(week_starts_on + row) % 7]
