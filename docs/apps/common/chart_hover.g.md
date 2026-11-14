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
  - [⚙️ Method `paintEvent`](#%EF%B8%8F-method-paintevent)
  - [⚙️ Method `resizeEvent`](#%EF%B8%8F-method-resizeevent)
  - [⚙️ Method `set_hover_cursor`](#%EF%B8%8F-method-set_hover_cursor)
  - [⚙️ Method `show_centered_message`](#%EF%B8%8F-method-show_centered_message)
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
        register_chart_canvas(self)
        self._cursor_x: int | None = None
        self._resize_timer = QTimer(self)
        self._resize_timer.setSingleShot(True)
        self._resize_timer.setInterval(_RESIZE_DEBOUNCE_MS)
        self._resize_timer.timeout.connect(self._flush_resize)
```

</details>

### ⚙️ Method `paintEvent`

```python
def paintEvent(self, event: QPaintEvent) -> None
```

Draw the figure, then a hover guide that is not part of the data.

<details>
<summary>Code:</summary>

```python
def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802
        super().paintEvent(event)
        if self._cursor_x is None:
            return
        painter = QPainter(self)
        painter.setPen(QPen(QColor(chart_muted_ink()), 1, Qt.PenStyle.SolidLine))
        painter.drawLine(self._cursor_x, 0, self._cursor_x, self.height())
        painter.end()
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
        self._resize_timer.start(_RESIZE_DEBOUNCE_MS)
```

</details>

### ⚙️ Method `set_hover_cursor`

```python
def set_hover_cursor(self, x_px: float | None) -> None
```

Move the vertical hover guide. `None` hides it.

The guide is painted by Qt. It is not a Matplotlib line, so it cannot
change the axis limits.

<details>
<summary>Code:</summary>

```python
def set_hover_cursor(self, x_px: float | None) -> None:
        cursor_x = None if x_px is None else round(x_px)
        if cursor_x == self._cursor_x:
            return
        self._cursor_x = cursor_x
        self.update()
```

</details>

### ⚙️ Method `show_centered_message`

```python
def show_centered_message(self, text: str = NO_CHART_DATA) -> None
```

Replace the figure with one centered line of text.

<details>
<summary>Code:</summary>

```python
def show_centered_message(self, text: str = NO_CHART_DATA) -> None:
        self.figure.clear()
        axis = self.figure.add_subplot(111)
        apply_theme(self.figure, axis)
        axis.set_axis_off()
        axis.text(0.5, 0.5, text, ha="center", va="center", color=chart_muted_ink(), transform=axis.transAxes)
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
    text = f"{x_text} — {y_text}"
    if label:
        return f"{text} ({label})"
    return text
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
