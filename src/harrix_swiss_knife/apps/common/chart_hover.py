"""Hover tooltips for Matplotlib charts embedded in Qt canvases."""

from __future__ import annotations

import contextlib
from collections.abc import Callable
from datetime import date, datetime
from typing import TYPE_CHECKING, Any

import matplotlib.dates as mdates
import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.collections import PathCollection
from matplotlib.container import BarContainer, ErrorbarContainer
from matplotlib.patches import Rectangle
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QCursor, QPainter, QPaintEvent, QPen, QResizeEvent
from PySide6.QtWidgets import QSizePolicy, QToolTip

from harrix_swiss_knife.apps.common.chart_format import NO_CHART_DATA, fmt_date, fmt_number
from harrix_swiss_knife.apps.common.chart_theme import apply_theme, chart_muted_ink, register_chart_canvas

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.backend_bases import Event, MouseEvent
    from matplotlib.figure import Figure
    from matplotlib.lines import Line2D

PointResolver = Callable[["MouseEvent"], str | None]
_HOVER_ATTR = "_hsk_chart_hover_cid"
_LEAVE_ATTR = "_hsk_chart_leave_cid"
_HOVER_STATE_ATTR = "_hsk_chart_hover_state"
_MPL_DATE_NUMBER_MIN = 1000.0
_MIN_CANVAS_PX = 80
_RESIZE_DEBOUNCE_MS = 100


class ExpandingChartCanvas(FigureCanvas):
    """Qt Matplotlib canvas that fills its layout cell on resize."""

    def __init__(self, figure: Figure) -> None:
        """Bind `figure` and expand to fill the parent layout cell."""
        super().__init__(figure)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumSize(_MIN_CANVAS_PX, _MIN_CANVAS_PX)
        register_chart_canvas(self)
        self._cursor_x: int | None = None
        self._resize_timer = QTimer(self)
        self._resize_timer.setSingleShot(True)
        self._resize_timer.setInterval(_RESIZE_DEBOUNCE_MS)
        self._resize_timer.timeout.connect(self._flush_resize)

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802
        """Draw the figure, then a hover guide that is not part of the data."""
        super().paintEvent(event)
        if self._cursor_x is None:
            return
        painter = QPainter(self)
        painter.setPen(QPen(QColor(chart_muted_ink()), 1, Qt.PenStyle.SolidLine))
        painter.drawLine(self._cursor_x, 0, self._cursor_x, self.height())
        painter.end()

    def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        """Resize the Matplotlib figure to match the Qt widget size."""
        super().resizeEvent(event)
        self._resize_timer.start(_RESIZE_DEBOUNCE_MS)

    def set_hover_cursor(self, x_px: float | None) -> None:
        """Move the vertical hover guide. `None` hides it.

        The guide is painted by Qt. It is not a Matplotlib line, so it cannot
        change the axis limits.

        """
        cursor_x = None if x_px is None else round(x_px)
        if cursor_x == self._cursor_x:
            return
        self._cursor_x = cursor_x
        self.update()

    def show_centered_message(self, text: str = NO_CHART_DATA) -> None:
        """Replace the figure with one centered line of text."""
        self.figure.clear()
        axis = self.figure.add_subplot(111)
        apply_theme(self.figure, axis)
        axis.set_axis_off()
        axis.text(0.5, 0.5, text, ha="center", va="center", color=chart_muted_ink(), transform=axis.transAxes)
        self.draw_idle()

    def _flush_resize(self) -> None:
        width = max(self.width(), _MIN_CANVAS_PX)
        height = max(self.height(), _MIN_CANVAS_PX)
        dpi = float(self.figure.dpi) if self.figure.dpi else 100.0
        self.figure.set_size_inches(width / dpi, height / dpi, forward=False)
        engine = self.figure.get_layout_engine()
        engine_name = type(engine).__name__.lower() if engine is not None else ""
        if "constrained" not in engine_name:
            with contextlib.suppress(Exception):
                self.figure.tight_layout()
        self.draw_idle()


def create_chart_canvas(fig: Figure) -> FigureCanvas:
    """Create a Qt Matplotlib canvas with point-value hover tooltips enabled."""
    canvas = ExpandingChartCanvas(fig)
    install_chart_hover(canvas)
    return canvas


def format_chart_point(x: Any, y: Any, *, label: str | None = None) -> str:
    """Format one ``(x, y)`` chart point for a hover tooltip."""
    x_text = _format_x_value(x)
    y_text = _format_y_value(y)
    text = f"{x_text} — {y_text}"
    if label:
        return f"{text} ({label})"
    return text


def install_chart_hover(
    canvas: FigureCanvas,
    *,
    resolve_tooltip: PointResolver | None = None,
    max_pixel_distance: float = 14.0,
) -> None:
    """Show a Qt tooltip for the nearest plotted value under the cursor.

    Args:

    - `canvas` (`FigureCanvas`): Chart canvas.
    - `resolve_tooltip` (`PointResolver | None`): Optional custom resolver. When
      omitted, nearest line / scatter / bar values are used.
    - `max_pixel_distance` (`float`): Max pointer distance in display pixels for
      line and scatter points.

    """
    previous_motion = getattr(canvas, _HOVER_ATTR, None)
    previous_leave = getattr(canvas, _LEAVE_ATTR, None)
    if previous_motion is not None:
        canvas.mpl_disconnect(previous_motion)
    if previous_leave is not None:
        canvas.mpl_disconnect(previous_leave)

    state: dict[str, Any] = {"last_tip": None}
    setattr(canvas, _HOVER_STATE_ATTR, state)
    canvas.setMouseTracking(True)

    def on_move(event: MouseEvent) -> None:
        tip = None
        if resolve_tooltip is not None:
            tip = resolve_tooltip(event)
        elif event.inaxes is not None and event.xdata is not None and event.ydata is not None:
            tip = nearest_artist_tooltip(
                event.inaxes,
                float(event.x),
                float(event.y),
                max_pixel_distance=max_pixel_distance,
            )
        _set_hover_cursor(canvas, None if event.inaxes is None or event.x is None else float(event.x))
        if tip:
            if tip != state["last_tip"]:
                state["last_tip"] = tip
            QToolTip.showText(QCursor.pos(), tip, canvas)
            return
        if state["last_tip"] is not None:
            state["last_tip"] = None
            QToolTip.hideText()

    def on_leave(_event: Event) -> None:
        _set_hover_cursor(canvas, None)
        if state["last_tip"] is not None:
            state["last_tip"] = None
            QToolTip.hideText()

    setattr(canvas, _HOVER_ATTR, canvas.mpl_connect("motion_notify_event", on_move))
    setattr(canvas, _LEAVE_ATTR, canvas.mpl_connect("figure_leave_event", on_leave))


def nearest_artist_tooltip(
    ax: Axes,
    pixel_x: float,
    pixel_y: float,
    *,
    max_pixel_distance: float = 14.0,
) -> str | None:
    """Return tooltip text for the nearest line, scatter, or bar under the pointer."""
    best_tip: str | None = None
    best_dist = max_pixel_distance

    for line in ax.lines:
        tip, dist = _line_tooltip(ax, line, pixel_x, pixel_y, max_pixel_distance=best_dist)
        if tip is not None and dist < best_dist:
            best_tip, best_dist = tip, dist

    for collection in ax.collections:
        if not isinstance(collection, PathCollection):
            continue
        tip, dist = _scatter_tooltip(ax, collection, pixel_x, pixel_y, max_pixel_distance=best_dist)
        if tip is not None and dist < best_dist:
            best_tip, best_dist = tip, dist

    for container in ax.containers:
        if isinstance(container, ErrorbarContainer):
            continue
        if isinstance(container, BarContainer):
            tip = _bar_container_tooltip(ax, container, pixel_x, pixel_y)
            if tip is not None:
                return tip

    for patch in ax.patches:
        if not isinstance(patch, Rectangle):
            continue
        tip = _rectangle_tooltip(ax, patch, pixel_x, pixel_y)
        if tip is not None:
            return tip

    return best_tip


def _bar_container_tooltip(
    ax: Axes,
    container: BarContainer,
    pixel_x: float,
    pixel_y: float,
) -> str | None:
    label = container.get_label()
    for patch in container:
        if not isinstance(patch, Rectangle):
            continue
        tip = _rectangle_tooltip(ax, patch, pixel_x, pixel_y, label=label)
        if tip is not None:
            return tip
    return None


def _clean_artist_label(label: object) -> str | None:
    """Return a visible legend label, or `None` for Matplotlib's private `_…` names."""
    if not isinstance(label, str) or not label or label.startswith("_"):
        return None
    return label


def _format_x_value(value: Any) -> str:
    if isinstance(value, datetime | date):
        return fmt_date(value)
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    # Matplotlib date numbers are typically large for modern calendar dates.
    if number > _MPL_DATE_NUMBER_MIN:
        try:
            converted = mdates.num2date(number)
            if converted.tzinfo is not None:
                converted = converted.astimezone().replace(tzinfo=None)
            return fmt_date(converted)
        except (ValueError, OverflowError, OSError):
            pass
    return _format_y_value(number)


def _format_y_value(value: Any) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    return fmt_number(number)


def _line_tooltip(
    ax: Axes,
    line: Line2D,
    pixel_x: float,
    pixel_y: float,
    *,
    max_pixel_distance: float,
) -> tuple[str | None, float]:
    xdata = line.get_xdata(orig=False)
    ydata = line.get_ydata(orig=False)
    if xdata is None or ydata is None:
        return None, max_pixel_distance
    xs = np.asarray(xdata, dtype=float)
    ys = np.asarray(ydata, dtype=float)
    if xs.size == 0 or ys.size == 0 or xs.size != ys.size:
        return None, max_pixel_distance
    mask = np.isfinite(xs) & np.isfinite(ys)
    xs = xs[mask]
    ys = ys[mask]
    if xs.size == 0:
        return None, max_pixel_distance

    points = ax.transData.transform(np.column_stack([xs, ys]))
    deltas = points - np.array([pixel_x, pixel_y], dtype=float)
    distances = np.hypot(deltas[:, 0], deltas[:, 1])
    index = int(np.argmin(distances))
    dist = float(distances[index])
    if dist > max_pixel_distance:
        return None, max_pixel_distance
    return format_chart_point(xs[index], ys[index], label=_clean_artist_label(line.get_label())), dist


def _rectangle_tooltip(
    ax: Axes,
    patch: Rectangle,
    pixel_x: float,
    pixel_y: float,
    *,
    label: str | None = None,
) -> str | None:
    try:
        renderer = ax.figure.canvas.get_renderer()
    except Exception:
        return None
    bbox = patch.get_window_extent(renderer=renderer)
    if not bbox.contains(pixel_x, pixel_y):
        return None
    x0 = patch.get_x()
    width = patch.get_width()
    height = patch.get_height()
    y0 = patch.get_y()
    # Vertical bars: x is category center-ish, y height is the value.
    if abs(height) >= abs(width):
        x_val = x0 + width / 2.0
        y_val = height if y0 == 0 else y0 + height
    else:
        x_val = width if x0 == 0 else x0 + width
        y_val = y0 + height / 2.0
    return format_chart_point(x_val, y_val, label=_clean_artist_label(label))


def _scatter_tooltip(
    ax: Axes,
    collection: PathCollection,
    pixel_x: float,
    pixel_y: float,
    *,
    max_pixel_distance: float,
) -> tuple[str | None, float]:
    offsets_arr = np.asarray(collection.get_offsets(), dtype=float)
    if offsets_arr.size == 0:
        return None, max_pixel_distance
    if offsets_arr.ndim == 1:
        if offsets_arr.size < 2:  # noqa: PLR2004
            return None, max_pixel_distance
        offsets_arr = offsets_arr.reshape(1, 2)
    points = ax.transData.transform(offsets_arr)
    deltas = points - np.array([pixel_x, pixel_y], dtype=float)
    distances = np.hypot(deltas[:, 0], deltas[:, 1])
    index = int(np.argmin(distances))
    dist = float(distances[index])
    if dist > max_pixel_distance:
        return None, max_pixel_distance
    x_val = float(offsets_arr[index, 0])
    y_val = float(offsets_arr[index, 1])
    return format_chart_point(x_val, y_val, label=_clean_artist_label(collection.get_label())), dist


def _set_hover_cursor(canvas: FigureCanvas, x_px: float | None) -> None:
    setter = getattr(canvas, "set_hover_cursor", None)
    if callable(setter):
        setter(x_px)
