"""Hover tooltips for Matplotlib charts embedded in Qt canvases."""

from __future__ import annotations

from collections.abc import Callable
from datetime import date, datetime
from typing import TYPE_CHECKING, Any

import matplotlib.dates as mdates
import numpy as np
from matplotlib.collections import PathCollection
from matplotlib.container import BarContainer, ErrorbarContainer
from matplotlib.patches import Rectangle
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QToolTip

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.backend_bases import Event, MouseEvent
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    from matplotlib.lines import Line2D

PointResolver = Callable[["MouseEvent"], str | None]
_HOVER_ATTR = "_hsk_chart_hover_cid"
_LEAVE_ATTR = "_hsk_chart_leave_cid"
_HOVER_STATE_ATTR = "_hsk_chart_hover_state"
_MPL_DATE_NUMBER_MIN = 1000.0
_INT_EPSILON = 1e-9


def create_chart_canvas(fig: Figure) -> FigureCanvas:
    """Create a Qt Matplotlib canvas with point-value hover tooltips enabled."""
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas  # noqa: PLC0415

    canvas = FigureCanvas(fig)
    install_chart_hover(canvas)
    return canvas


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
        if tip:
            if tip != state["last_tip"]:
                state["last_tip"] = tip
            QToolTip.showText(QCursor.pos(), tip, canvas)
            return
        if state["last_tip"] is not None:
            state["last_tip"] = None
            QToolTip.hideText()

    def on_leave(_event: Event) -> None:
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


def format_chart_point(x: Any, y: Any, *, label: str | None = None) -> str:
    """Format one ``(x, y)`` chart point for a hover tooltip."""
    x_text = _format_x_value(x)
    y_text = _format_y_value(y)
    if label:
        return f"{label}: {x_text} → {y_text}"
    return f"{x_text}: {y_text}"


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
    label = line.get_label()
    if not label or label.startswith("_"):
        label = None
    return format_chart_point(xs[index], ys[index], label=label), dist


def _scatter_tooltip(
    ax: Axes,
    collection: PathCollection,
    pixel_x: float,
    pixel_y: float,
    *,
    max_pixel_distance: float,
) -> tuple[str | None, float]:
    offsets = collection.get_offsets()
    if offsets is None or len(offsets) == 0:
        return None, max_pixel_distance
    points = ax.transData.transform(np.asarray(offsets, dtype=float))
    deltas = points - np.array([pixel_x, pixel_y], dtype=float)
    distances = np.hypot(deltas[:, 0], deltas[:, 1])
    index = int(np.argmin(distances))
    dist = float(distances[index])
    if dist > max_pixel_distance:
        return None, max_pixel_distance
    x_val, y_val = offsets[index]
    label = collection.get_label()
    if not label or label.startswith("_"):
        label = None
    return format_chart_point(x_val, y_val, label=label), dist


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
    clean_label = label if label and not label.startswith("_") else None
    return format_chart_point(x_val, y_val, label=clean_label)


def _format_x_value(value: Any) -> str:
    if isinstance(value, datetime):
        if value.hour or value.minute or value.second:
            return value.strftime("%Y-%m-%d %H:%M")
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
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
            if converted.hour or converted.minute or converted.second:
                return converted.strftime("%Y-%m-%d %H:%M")
            return converted.date().isoformat()
        except (ValueError, OverflowError, OSError):
            pass
    return _format_y_value(number)


def _format_y_value(value: Any) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    if abs(number - round(number)) < _INT_EPSILON:
        return str(round(number))
    text = f"{number:.4f}".rstrip("0").rstrip(".")
    return text or "0"
