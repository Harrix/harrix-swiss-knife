---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `paint.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `antialiased_painter`](#-function-antialiased_painter)
- [🔧 Function `inset`](#-function-inset)
- [🔧 Function `paint_fluent_splitter_handle`](#-function-paint_fluent_splitter_handle)
- [🔧 Function `paint_surface`](#-function-paint_surface)
- [🔧 Function `rounded_path`](#-function-rounded_path)
- [🔧 Function `with_alpha`](#-function-with_alpha)

</details>

## 🔧 Function `antialiased_painter`

```python
def antialiased_painter(device: QPaintDevice) -> QPainter
```

Return a `QPainter` on `device` with antialiasing and smooth pixmaps.

<details>
<summary>Code:</summary>

```python
def antialiased_painter(device: QPaintDevice) -> QPainter:
    painter = QPainter(device)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, on=True)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, on=True)
    painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, on=True)
    return painter
```

</details>

## 🔧 Function `inset`

```python
def inset(rect: QRect | QRectF, amount: float = 0.5) -> QRectF
```

Return `rect` shrunk by `amount` on every side (crisp 1 px strokes).

<details>
<summary>Code:</summary>

```python
def inset(rect: QRect | QRectF, amount: float = 0.5) -> QRectF:
    result = QRectF(rect)
    return result.adjusted(amount, amount, -amount, -amount)
```

</details>

## 🔧 Function `paint_fluent_splitter_handle`

```python
def paint_fluent_splitter_handle(device: QWidget, palette: FluentPalette, orientation: Qt.Orientation, *, hovered: bool, pressed: bool) -> None
```

Paint a Fluent splitter handle: 1px divider idle, 2px accent + dots on hover.

Args:

- `device` (`QWidget`): Handle widget to paint onto.
- [`palette`](theme.g.md#%EF%B8%8F-method-palette) ([`FluentPalette`](tokens.g.md#%EF%B8%8F-class-fluentpalette)): Theme colors.
- `orientation` (`Qt.Orientation`): Parent splitter orientation.
- `hovered` (`bool`): Pointer is over the handle.
- `pressed` (`bool`): Handle is being dragged.

<details>
<summary>Code:</summary>

```python
def paint_fluent_splitter_handle(
    device: QWidget,
    palette: FluentPalette,
    orientation: Qt.Orientation,
    *,
    hovered: bool,
    pressed: bool,
) -> None:
    painter = antialiased_painter(device)
    rect = device.rect()
    active = hovered or pressed
    if active:
        line = palette.accent_pressed if pressed else palette.accent
        line_width = 2
    else:
        line = mix(palette.window_bg, palette.divider)
        line_width = 1
    pen = QPen(line)
    pen.setWidth(line_width)
    pen.setCapStyle(Qt.PenCapStyle.FlatCap)
    painter.setPen(pen)
    if orientation == Qt.Orientation.Horizontal:
        x = rect.center().x()
        painter.drawLine(x, rect.top(), x, rect.bottom())
    else:
        y = rect.center().y()
        painter.drawLine(rect.left(), y, rect.right(), y)

    if active:
        fill = palette.accent_pressed if pressed else palette.accent
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(fill)
        cx = float(rect.center().x())
        cy = float(rect.center().y())
        span = (_SPLITTER_DOT_COUNT - 1) * _SPLITTER_DOT_GAP
        start = -span / 2
        for index in range(_SPLITTER_DOT_COUNT):
            offset = start + index * _SPLITTER_DOT_GAP
            center = QPointF(cx, cy + offset) if orientation == Qt.Orientation.Horizontal else QPointF(cx + offset, cy)
            painter.drawEllipse(center, _SPLITTER_DOT_RADIUS, _SPLITTER_DOT_RADIUS)
    painter.end()
```

</details>

## 🔧 Function `paint_surface`

```python
def paint_surface(painter: QPainter, rect: QRect | QRectF, fill: QColor | None, stroke: QColor | None = None, radius: float = 0.0, *, stroke_width: float = 1.0) -> None
```

Fill and optionally stroke a rounded rectangle.

Args:

- `painter` (`QPainter`): Active painter.
- `rect` (`QRect | QRectF`): Outer bounds.
- `fill` (`QColor | None`): Fill color; `None` leaves the inside empty.
- `stroke` (`QColor | None`): Border color; `None` draws no border.
- `radius` (`float`): Corner radius.
- `stroke_width` (`float`): Border width. Defaults to `1.0`.

<details>
<summary>Code:</summary>

```python
def paint_surface(
    painter: QPainter,
    rect: QRect | QRectF,
    fill: QColor | None,
    stroke: QColor | None = None,
    radius: float = 0.0,
    *,
    stroke_width: float = 1.0,
) -> None:
    painter.save()
    if stroke is not None and stroke.alpha() > 0:
        pen = QPen(stroke)
        pen.setWidthF(stroke_width)
        painter.setPen(pen)
        target = inset(rect, stroke_width / 2)
    else:
        painter.setPen(Qt.PenStyle.NoPen)
        target = QRectF(rect)
    painter.setBrush(fill if fill is not None else Qt.BrushStyle.NoBrush)
    painter.drawRoundedRect(target, radius, radius)
    painter.restore()
```

</details>

## 🔧 Function `rounded_path`

```python
def rounded_path(rect: QRect | QRectF, radius: float) -> QPainterPath
```

Return a rounded-rectangle path (handy for clipping images).

<details>
<summary>Code:</summary>

```python
def rounded_path(rect: QRect | QRectF, radius: float) -> QPainterPath:
    path = QPainterPath()
    path.addRoundedRect(QRectF(rect), radius, radius)
    return path
```

</details>

## 🔧 Function `with_alpha`

```python
def with_alpha(color: QColor, alpha: int) -> QColor
```

Return a copy of [`color`](widgets/dialogs.g.md#%EF%B8%8F-method-color) with a new alpha channel (0-255).

<details>
<summary>Code:</summary>

```python
def with_alpha(color: QColor, alpha: int) -> QColor:
    result = QColor(color)
    result.setAlpha(max(0, min(255, alpha)))
    return result
```

</details>
