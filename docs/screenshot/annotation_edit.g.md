---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `annotation_edit.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `annotation_bounds`](#-function-annotation_bounds)
- [🔧 Function `apply_annotation_edit`](#-function-apply_annotation_edit)
- [🔧 Function `cursor_for_annotation_handle`](#-function-cursor_for_annotation_handle)
- [🔧 Function `hit_test_annotation`](#-function-hit_test_annotation)
- [🔧 Function `hit_test_topmost`](#-function-hit_test_topmost)
- [🔧 Function `paint_annotation_selection`](#-function-paint_annotation_selection)

</details>

## 🔧 Function `annotation_bounds`

```python
def annotation_bounds(annotation: Annotation) -> QRectF
```

Axis-aligned bounds of `annotation` in image coordinates.

<details>
<summary>Code:</summary>

```python
def annotation_bounds(annotation: Annotation) -> QRectF:
    points = annotation.points
    if not points:
        return QRectF()
    if annotation.tool == AnnotationTool.TEXT:
        return _text_bounds(annotation)
    if annotation.tool in {AnnotationTool.RECTANGLE, AnnotationTool.ELLIPSE, AnnotationTool.CROP}:
        if len(points) < _MIN_SHAPE_POINTS:
            return QRectF(points[0], points[0])
        return QRectF(points[0], points[-1]).normalized()
    return _points_bounds(points)
```

</details>

## 🔧 Function `apply_annotation_edit`

```python
def apply_annotation_edit(annotation: Annotation, handle: AnnotationHandle, origin_points: list[QPointF], press: QPointF, current: QPointF, *, shift: bool) -> list[QPointF]
```

Return updated points for `handle` dragged from `press` to `current`.

<details>
<summary>Code:</summary>

```python
def apply_annotation_edit(
    annotation: Annotation,
    handle: AnnotationHandle,
    origin_points: list[QPointF],
    press: QPointF,
    current: QPointF,
    *,
    shift: bool,
) -> list[QPointF]:
    if handle == "move" or annotation.tool == AnnotationTool.TEXT:
        delta = current - press
        return [QPointF(p.x() + delta.x(), p.y() + delta.y()) for p in origin_points]
    if annotation.tool in _LINE_TOOLS:
        return _edit_line_points(annotation.tool, handle, origin_points, current, shift=shift)
    origin_rect = annotation_bounds(
        Annotation(tool=annotation.tool, points=origin_points, style=annotation.style, text=annotation.text)
    )
    if origin_rect.isEmpty():
        delta = current - press
        return [QPointF(p.x() + delta.x(), p.y() + delta.y()) for p in origin_points]
    new_rect = _transform_rect(origin_rect, handle, press, current)
    if shift and annotation.tool in {AnnotationTool.ELLIPSE, AnnotationTool.RECTANGLE}:
        new_rect = _square_rect_from_handle(origin_rect, new_rect, handle)
    if annotation.tool in {AnnotationTool.RECTANGLE, AnnotationTool.ELLIPSE}:
        return [new_rect.topLeft(), new_rect.bottomRight()]
    return _map_points_from_rect(origin_points, origin_rect, new_rect)
```

</details>

## 🔧 Function `cursor_for_annotation_handle`

```python
def cursor_for_annotation_handle(handle: AnnotationHandle | None) -> str
```

Return a Qt cursor shape name for an annotation handle.

<details>
<summary>Code:</summary>

```python
def cursor_for_annotation_handle(handle: AnnotationHandle | None) -> str:
    if handle in {None, "start", "end", "move"}:
        return "SizeAllCursor" if handle else "CrossCursor"
    return cursor_for_handle(handle)
```

</details>

## 🔧 Function `hit_test_annotation`

```python
def hit_test_annotation(annotation: Annotation, pos: QPointF, *, handle_size: float) -> AnnotationHandle | None
```

Return the handle under `pos`, preferring resize handles over move.

<details>
<summary>Code:</summary>

```python
def hit_test_annotation(
    annotation: Annotation,
    pos: QPointF,
    *,
    handle_size: float,
) -> AnnotationHandle | None:
    bounds = annotation_bounds(annotation)
    if bounds.isNull():
        return None
    for handle, point in _handle_points(annotation, bounds):
        if _handle_rect(point, handle_size).contains(pos):
            return handle
    padding = max(handle_size, annotation.style.width, _HIT_PADDING)
    if annotation.tool == AnnotationTool.ARROW:
        padding = max(padding, max(1.0, annotation.style.width) * _ARROW_HEAD_HIT_MULT)
    if annotation.tool in _LINE_TOOLS:
        if len(annotation.points) < _MIN_SHAPE_POINTS:
            return None
        if _distance_to_segment(pos, annotation.points[0], annotation.points[-1]) <= padding:
            return "move"
        return None
    if annotation.tool == AnnotationTool.PEN:
        if _hit_polyline(annotation.points, pos, padding) or bounds.adjusted(
            -padding, -padding, padding, padding
        ).contains(pos):
            return "move"
        return None
    if annotation.tool == AnnotationTool.ELLIPSE:
        return "move" if _hit_ellipse_stroke(bounds, pos, padding) else None
    if annotation.tool == AnnotationTool.RECTANGLE:
        return "move" if _hit_rect_stroke(bounds, pos, padding) else None
    inflated = bounds.adjusted(-padding, -padding, padding, padding)
    if inflated.contains(pos):
        return "move"
    return None
```

</details>

## 🔧 Function `hit_test_topmost`

```python
def hit_test_topmost(annotations: list[Annotation], pos: QPointF, *, handle_size: float, prefer_tool: AnnotationTool | None = None, selected_index: int | None = None) -> tuple[int, AnnotationHandle] | None
```

Hit-test from front to back; selected handles are checked first.

When `prefer_tool` is a drawing tool, matching annotations are tested before
other shapes so switching back to arrows still selects old arrows.

<details>
<summary>Code:</summary>

```python
def hit_test_topmost(
    annotations: list[Annotation],
    pos: QPointF,
    *,
    handle_size: float,
    prefer_tool: AnnotationTool | None = None,
    selected_index: int | None = None,
) -> tuple[int, AnnotationHandle] | None:
    if selected_index is not None and 0 <= selected_index < len(annotations):
        handle = hit_test_annotation(annotations[selected_index], pos, handle_size=handle_size)
        if handle is not None:
            return selected_index, handle
    prefer = prefer_tool not in {None, AnnotationTool.NONE, AnnotationTool.CROP, AnnotationTool.EYEDROPPER}
    if prefer:
        for index in range(len(annotations) - 1, -1, -1):
            if index == selected_index or annotations[index].tool != prefer_tool:
                continue
            handle = hit_test_annotation(annotations[index], pos, handle_size=handle_size)
            if handle is not None:
                return index, handle
    for index in range(len(annotations) - 1, -1, -1):
        if index == selected_index:
            continue
        if prefer and annotations[index].tool == prefer_tool:
            continue
        handle = hit_test_annotation(annotations[index], pos, handle_size=handle_size)
        if handle is not None:
            return index, handle
    return None
```

</details>

## 🔧 Function `paint_annotation_selection`

```python
def paint_annotation_selection(painter: QPainter, annotation: Annotation, *, handle_size: float) -> None
```

Draw the selection frame and handles for `annotation`.

<details>
<summary>Code:</summary>

```python
def paint_annotation_selection(painter: QPainter, annotation: Annotation, *, handle_size: float) -> None:
    bounds = annotation_bounds(annotation)
    if bounds.isNull():
        return
    pad = max(handle_size * 0.5, _MIN_BOX)
    frame = bounds.adjusted(-pad, -pad, pad, pad)
    pen = QPen(SELECTION_BORDER_COLOR, 1.0)
    pen.setStyle(Qt.PenStyle.DashLine)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawRect(frame)
    half = max(SELECTION_HANDLE_DRAW / 2, handle_size / 2)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(SELECTION_HANDLE_FILL)
    for _handle, point in _handle_points(annotation, bounds):
        painter.drawRect(QRectF(point.x() - half, point.y() - half, half * 2, half * 2))
```

</details>
