---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `selection_guides.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `GuideLabel`](#%EF%B8%8F-class-guidelabel)
- [🔧 Function `diagonal_angle_degrees`](#-function-diagonal_angle_degrees)
- [🔧 Function `diagonal_length_px`](#-function-diagonal_length_px)
- [🔧 Function `format_angle_label`](#-function-format_angle_label)
- [🔧 Function `guide_label_font`](#-function-guide_label_font)
- [🔧 Function `guide_offsets`](#-function-guide_offsets)
- [🔧 Function `hit_test_size_label`](#-function-hit_test_size_label)
- [🔧 Function `paint_selection_guides`](#-function-paint_selection_guides)
- [🔧 Function `parse_size_label`](#-function-parse_size_label)
- [🔧 Function `place_angle_label`](#-function-place_angle_label)
- [🔧 Function `place_diagonal_label`](#-function-place_diagonal_label)
- [🔧 Function `place_height_label`](#-function-place_height_label)
- [🔧 Function `place_width_label`](#-function-place_width_label)
- [🔧 Function `selection_guide_labels`](#-function-selection_guide_labels)

</details>

## 🏛️ Class `GuideLabel`

```python
class GuideLabel
```

One measurement label placed relative to the selection rectangle.

<details>
<summary>Code:</summary>

```python
class GuideLabel:

    text: str
    box: QRect
    color: QColor
    inside: bool
    kind: GuideLabelKind
```

</details>

## 🔧 Function `diagonal_angle_degrees`

```python
def diagonal_angle_degrees(width: int, height: int) -> float
```

Return the angle (degrees) between the bottom edge and the falling diagonal.

<details>
<summary>Code:</summary>

```python
def diagonal_angle_degrees(width: int, height: int) -> float:
    if width <= 0:
        return 90.0
    if height <= 0:
        return 0.0
    return math.degrees(math.atan2(height, width))
```

</details>

## 🔧 Function `diagonal_length_px`

```python
def diagonal_length_px(width: int, height: int) -> int
```

Return the diagonal length in whole pixels.

<details>
<summary>Code:</summary>

```python
def diagonal_length_px(width: int, height: int) -> int:
    return round(math.hypot(width, height))
```

</details>

## 🔧 Function `format_angle_label`

```python
def format_angle_label(angle_degrees: float) -> str
```

Return the angle text shown under the bottom-right corner.

<details>
<summary>Code:</summary>

```python
def format_angle_label(angle_degrees: float) -> str:
    return f"{angle_degrees:.4f} °"
```

</details>

## 🔧 Function `guide_label_font`

```python
def guide_label_font(base: QFont | None = None) -> QFont
```

Return the bold measurement font used on the selection frame.

<details>
<summary>Code:</summary>

```python
def guide_label_font(base: QFont | None = None) -> QFont:
    font = QFont() if base is None else QFont(base)
    font.setPointSize(_LABEL_POINT_SIZE)
    font.setBold(True)
    return font
```

</details>

## 🔧 Function `guide_offsets`

```python
def guide_offsets(length: int) -> tuple[int, int, int]
```

Return 1/3, 1/2, and 2/3 offsets along `length`.

<details>
<summary>Code:</summary>

```python
def guide_offsets(length: int) -> tuple[int, int, int]:
    return length // 3, length // 2, (2 * length) // 3
```

</details>

## 🔧 Function `hit_test_size_label`

```python
def hit_test_size_label(rect: QRect, bounds: QRect, pos: QPoint, metrics: QFontMetrics, *, padding: int = _SIZE_HIT_PADDING) -> SizeLabelKind | None
```

Return `width` or `height` when `pos` is on that measurement label.

<details>
<summary>Code:</summary>

```python
def hit_test_size_label(
    rect: QRect,
    bounds: QRect,
    pos: QPoint,
    metrics: QFontMetrics,
    *,
    padding: int = _SIZE_HIT_PADDING,
) -> SizeLabelKind | None:
    width_label, height_label, _, _ = selection_guide_labels(rect, bounds, metrics)
    if width_label.box.adjusted(-padding, -padding, padding, padding).contains(pos):
        return "width"
    if height_label.box.adjusted(-padding, -padding, padding, padding).contains(pos):
        return "height"
    return None
```

</details>

## 🔧 Function `paint_selection_guides`

```python
def paint_selection_guides(painter: QPainter, rect: QRect, bounds: QRect, *, skip_size: SizeLabelKind | None = None) -> None
```

Draw thirds/halves, diagonal, size labels, and the bottom-right angle.

<details>
<summary>Code:</summary>

```python
def paint_selection_guides(
    painter: QPainter,
    rect: QRect,
    bounds: QRect,
    *,
    skip_size: SizeLabelKind | None = None,
) -> None:
    if rect.width() < _MIN_GUIDE_SIZE or rect.height() < _MIN_GUIDE_SIZE:
        return
    frame = rect.adjusted(0, 0, -1, -1)
    painter.save()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, on=False)
    _paint_grid(painter, frame)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, on=True)
    _paint_diagonal(painter, frame)
    _paint_angle_arc(painter, frame)
    painter.setFont(guide_label_font(painter.font()))
    for label in selection_guide_labels(rect, bounds, painter.fontMetrics()):
        if skip_size is not None and label.kind == skip_size:
            continue
        painter.setPen(label.color)
        painter.drawText(label.box, Qt.AlignmentFlag.AlignCenter, label.text)
    painter.restore()
```

</details>

## 🔧 Function `parse_size_label`

```python
def parse_size_label(text: str) -> int | None
```

Parse a typed width or height in whole pixels, or `None` if invalid.

<details>
<summary>Code:</summary>

```python
def parse_size_label(text: str) -> int | None:
    stripped = text.strip()
    if not stripped.isdigit():
        return None
    value = int(stripped)
    return value if value > 0 else None
```

</details>

## 🔧 Function `place_angle_label`

```python
def place_angle_label(rect: QRect, bounds: QRect, *, text_width: int, text_height: int, gap: int = _LABEL_GAP) -> tuple[QRect, bool]
```

Place the angle label below the bottom-right corner, or inside if it does not fit.

<details>
<summary>Code:</summary>

```python
def place_angle_label(
    rect: QRect,
    bounds: QRect,
    *,
    text_width: int,
    text_height: int,
    gap: int = _LABEL_GAP,
) -> tuple[QRect, bool]:
    x = rect.right() - text_width
    y = rect.bottom() + gap
    box = QRect(x, y, text_width, text_height)
    if bounds.contains(box):
        return box, False
    inner = QRect(rect.right() - gap - text_width, rect.bottom() - gap - text_height, text_width, text_height)
    return _clamp_inside(inner, rect, text_width, text_height, gap), True
```

</details>

## 🔧 Function `place_diagonal_label`

```python
def place_diagonal_label(rect: QRect, *, text_width: int, text_height: int, gap: int = _LABEL_GAP) -> QRect
```

Place the diagonal length next to the line, not on it.

Prefers the top-right side of the falling diagonal; falls back to the
opposite side if that box does not fit inside `rect`.

<details>
<summary>Code:</summary>

```python
def place_diagonal_label(
    rect: QRect,
    *,
    text_width: int,
    text_height: int,
    gap: int = _LABEL_GAP,
) -> QRect:
    preferred = _offset_from_diagonal(rect, text_width, text_height, gap=gap, toward_top_right=True)
    if _label_clears_diagonal(rect, preferred):
        return preferred
    return _offset_from_diagonal(rect, text_width, text_height, gap=gap, toward_top_right=False)
```

</details>

## 🔧 Function `place_height_label`

```python
def place_height_label(rect: QRect, bounds: QRect, *, text_width: int, text_height: int, gap: int = _LABEL_GAP) -> tuple[QRect, bool]
```

Place the height label to the left of the frame, or inside if it does not fit.

<details>
<summary>Code:</summary>

```python
def place_height_label(
    rect: QRect,
    bounds: QRect,
    *,
    text_width: int,
    text_height: int,
    gap: int = _LABEL_GAP,
) -> tuple[QRect, bool]:
    x = rect.left() - gap - text_width
    y = rect.center().y() - text_height // 2
    box = QRect(x, y, text_width, text_height)
    if bounds.contains(box):
        return box, False
    inner = QRect(rect.left() + gap, rect.center().y() - text_height // 2, text_width, text_height)
    return _clamp_inside(inner, rect, text_width, text_height, gap), True
```

</details>

## 🔧 Function `place_width_label`

```python
def place_width_label(rect: QRect, bounds: QRect, *, text_width: int, text_height: int, gap: int = _LABEL_GAP) -> tuple[QRect, bool]
```

Place the width label above the frame, or inside if it does not fit.

<details>
<summary>Code:</summary>

```python
def place_width_label(
    rect: QRect,
    bounds: QRect,
    *,
    text_width: int,
    text_height: int,
    gap: int = _LABEL_GAP,
) -> tuple[QRect, bool]:
    x = rect.center().x() - text_width // 2
    y = rect.top() - gap - text_height
    box = QRect(x, y, text_width, text_height)
    if bounds.contains(box):
        return box, False
    inner = QRect(rect.center().x() - text_width // 2, rect.top() + gap, text_width, text_height)
    return _clamp_inside(inner, rect, text_width, text_height, gap), True
```

</details>

## 🔧 Function `selection_guide_labels`

```python
def selection_guide_labels(rect: QRect, bounds: QRect, metrics: QFontMetrics, *, gap: int = _LABEL_GAP) -> tuple[GuideLabel, GuideLabel, GuideLabel, GuideLabel]
```

Return width, height, diagonal, and angle labels for `rect`.

<details>
<summary>Code:</summary>

```python
def selection_guide_labels(
    rect: QRect,
    bounds: QRect,
    metrics: QFontMetrics,
    *,
    gap: int = _LABEL_GAP,
) -> tuple[GuideLabel, GuideLabel, GuideLabel, GuideLabel]:
    width = rect.width()
    height = rect.height()
    width_text = str(width)
    height_text = str(height)
    diagonal_text = str(diagonal_length_px(width, height))
    angle_text = format_angle_label(diagonal_angle_degrees(width, height))

    width_box, width_inside = place_width_label(
        rect,
        bounds,
        text_width=metrics.horizontalAdvance(width_text),
        text_height=metrics.height(),
        gap=gap,
    )
    height_box, height_inside = place_height_label(
        rect,
        bounds,
        text_width=metrics.horizontalAdvance(height_text),
        text_height=metrics.height(),
        gap=gap,
    )
    angle_box, angle_inside = place_angle_label(
        rect,
        bounds,
        text_width=metrics.horizontalAdvance(angle_text),
        text_height=metrics.height(),
        gap=gap,
    )
    diagonal_box = place_diagonal_label(
        rect,
        text_width=metrics.horizontalAdvance(diagonal_text),
        text_height=metrics.height(),
        gap=gap,
    )
    return (
        GuideLabel(width_text, width_box, _LABEL_COLOR, width_inside, "width"),
        GuideLabel(height_text, height_box, _LABEL_COLOR, height_inside, "height"),
        GuideLabel(diagonal_text, diagonal_box, _DIAGONAL_COLOR, inside=True, kind="diagonal"),
        GuideLabel(angle_text, angle_box, _ANGLE_COLOR, angle_inside, "angle"),
    )
```

</details>
