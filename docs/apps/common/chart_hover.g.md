---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `chart_hover.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `create_chart_canvas`](#-function-create_chart_canvas)
- [🔧 Function `format_chart_point`](#-function-format_chart_point)
- [🔧 Function `install_chart_hover`](#-function-install_chart_hover)
- [🔧 Function `nearest_artist_tooltip`](#-function-nearest_artist_tooltip)

</details>

## 🔧 Function `create_chart_canvas`

```python
def create_chart_canvas(fig: Figure) -> FigureCanvas
```

Create a Qt Matplotlib canvas with point-value hover tooltips enabled.

<details>
<summary>Code:</summary>

```python
def create_chart_canvas(fig: Figure) -> FigureCanvas:
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas  # noqa: PLC0415

    canvas = FigureCanvas(fig)
    install_chart_hover(canvas)
    return canvas
```

</details>

## 🔧 Function `format_chart_point`

```python
def format_chart_point(x: Any, y: Any, *, label: str | None = None) -> str
```

Format one ``(x, y)`` chart point for a hover tooltip.

<details>
<summary>Code:</summary>

```python
def format_chart_point(x: Any, y: Any, *, label: str | None = None) -> str:
    x_text = _format_x_value(x)
    y_text = _format_y_value(y)
    if label:
        return f"{label}: {x_text} → {y_text}"
    return f"{x_text}: {y_text}"
```

</details>

## 🔧 Function `install_chart_hover`

```python
def install_chart_hover(canvas: FigureCanvas, *, resolve_tooltip: PointResolver | None = None, max_pixel_distance: float = 14.0) -> None
```

Show a Qt tooltip for the nearest plotted value under the cursor.

Args:

- `canvas` (`FigureCanvas`): Chart canvas.
- `resolve_tooltip` (`PointResolver | None`): Optional custom resolver. When
  omitted, nearest line / scatter / bar values are used.
- `max_pixel_distance` (`float`): Max pointer distance in display pixels for
  line and scatter points.

<details>
<summary>Code:</summary>

```python
def install_chart_hover(
    canvas: FigureCanvas,
    *,
    resolve_tooltip: PointResolver | None = None,
    max_pixel_distance: float = 14.0,
) -> None:
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
```

</details>

## 🔧 Function `nearest_artist_tooltip`

```python
def nearest_artist_tooltip(ax: Axes, pixel_x: float, pixel_y: float, *, max_pixel_distance: float = 14.0) -> str | None
```

Return tooltip text for the nearest line, scatter, or bar under the pointer.

<details>
<summary>Code:</summary>

```python
def nearest_artist_tooltip(
    ax: Axes,
    pixel_x: float,
    pixel_y: float,
    *,
    max_pixel_distance: float = 14.0,
) -> str | None:
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
```

</details>
