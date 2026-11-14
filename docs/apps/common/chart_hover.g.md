---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `chart_hover.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ExpandingChartCanvas`](#%EF%B8%8F-class-expandingchartcanvas)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `resizeEvent`](#%EF%B8%8F-method-resizeevent)
- [🔧 Function `create_chart_canvas`](#-function-create_chart_canvas)
- [🔧 Function `format_chart_point`](#-function-format_chart_point)
- [🔧 Function `install_chart_hover`](#-function-install_chart_hover)
- [🔧 Function `nearest_artist_tooltip`](#-function-nearest_artist_tooltip)

</details>

## 🏛️ Class `ExpandingChartCanvas`

```python
class ExpandingChartCanvas(FigureCanvas)
```

Qt Matplotlib canvas that fills its layout cell on resize.

<details>
<summary>Code:</summary>

```python
class ExpandingChartCanvas(FigureCanvas):

    def __init__(self, figure: Figure) -> None:
        """Bind `figure` and expand to fill the parent layout cell."""
        super().__init__(figure)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumSize(_MIN_CANVAS_PX, _MIN_CANVAS_PX)

    def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        """Resize the Matplotlib figure to match the Qt widget size."""
        super().resizeEvent(event)
        width = max(self.width(), _MIN_CANVAS_PX)
        height = max(self.height(), _MIN_CANVAS_PX)
        dpi = float(self.figure.dpi) if self.figure.dpi else 100.0
        self.figure.set_size_inches(width / dpi, height / dpi, forward=False)
        with contextlib.suppress(Exception):
            self.figure.tight_layout()
        self.draw_idle()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, figure: Figure) -> None
```

Bind `figure` and expand to fill the parent layout cell.

<details>
<summary>Code:</summary>

```python
def __init__(self, figure: Figure) -> None:
        super().__init__(figure)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumSize(_MIN_CANVAS_PX, _MIN_CANVAS_PX)
```

</details>

### ⚙️ Method `resizeEvent`

```python
def resizeEvent(self, event: QResizeEvent) -> None
```

Resize the Matplotlib figure to match the Qt widget size.

<details>
<summary>Code:</summary>

```python
def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        super().resizeEvent(event)
        width = max(self.width(), _MIN_CANVAS_PX)
        height = max(self.height(), _MIN_CANVAS_PX)
        dpi = float(self.figure.dpi) if self.figure.dpi else 100.0
        self.figure.set_size_inches(width / dpi, height / dpi, forward=False)
        with contextlib.suppress(Exception):
            self.figure.tight_layout()
        self.draw_idle()
```

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
    canvas = ExpandingChartCanvas(fig)
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
