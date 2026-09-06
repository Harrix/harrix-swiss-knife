---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `annotation_snap.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `AnnotationSnapResult`](#%EF%B8%8F-class-annotationsnapresult)
- [🔧 Function `collect_annotation_guides`](#-function-collect_annotation_guides)
- [🔧 Function `snap_annotation_edit`](#-function-snap_annotation_edit)
- [🔧 Function `snap_point`](#-function-snap_point)
- [🔧 Function `snap_shape_end`](#-function-snap_shape_end)

</details>

## 🏛️ Class `AnnotationSnapResult`

```python
class AnnotationSnapResult
```

Snapped points plus active guide coordinates in image space.

<details>
<summary>Code:</summary>

```python
class AnnotationSnapResult:

    points: list[QPointF]
    x_guide: float | None = None
    y_guide: float | None = None
```

</details>

## 🔧 Function `collect_annotation_guides`

```python
def collect_annotation_guides(annotations: Sequence[Annotation], *, exclude_index: int | None = None, bounds: QRectF | None = None) -> tuple[list[float], list[float]]
```

Collect unique X/Y guides from [`annotations`](annotations.g.md#%EF%B8%8F-method-annotations-property) (and optional image `bounds`).

<details>
<summary>Code:</summary>

```python
def collect_annotation_guides(
    annotations: Sequence[Annotation],
    *,
    exclude_index: int | None = None,
    bounds: QRectF | None = None,
) -> tuple[list[float], list[float]]:
    xs: set[float] = set()
    ys: set[float] = set()
    if bounds is not None and bounds.isValid():
        xs.add(bounds.left())
        xs.add(bounds.right())
        ys.add(bounds.top())
        ys.add(bounds.bottom())
    for index, item in enumerate(annotations):
        if index == exclude_index:
            continue
        for point in item.points:
            xs.add(point.x())
            ys.add(point.y())
        if item.tool in _LINE_TOOLS:
            if len(item.points) >= _MIN_SHAPE_POINTS:
                start, end = item.points[0], item.points[-1]
                xs.add((start.x() + end.x()) / 2)
                ys.add((start.y() + end.y()) / 2)
            continue
        frame = annotation_bounds(item)
        if frame.isNull() or not frame.isValid():
            continue
        xs.update((frame.left(), frame.right(), frame.center().x()))
        ys.update((frame.top(), frame.bottom(), frame.center().y()))
    return sorted(xs), sorted(ys)
```

</details>

## 🔧 Function `snap_annotation_edit`

```python
def snap_annotation_edit(annotation: Annotation, handle: AnnotationHandle, points: list[QPointF], x_guides: Sequence[float], y_guides: Sequence[float], *, threshold: float = ANNOTATION_SNAP_THRESHOLD, shift: bool = False) -> AnnotationSnapResult
```

Snap `points` of an in-progress edit to nearby annotation guides.

<details>
<summary>Code:</summary>

```python
def snap_annotation_edit(
    annotation: Annotation,
    handle: AnnotationHandle,
    points: list[QPointF],
    x_guides: Sequence[float],
    y_guides: Sequence[float],
    *,
    threshold: float = ANNOTATION_SNAP_THRESHOLD,
    shift: bool = False,
) -> AnnotationSnapResult:
    if not points or (not x_guides and not y_guides):
        return AnnotationSnapResult([QPointF(p) for p in points])
    if handle in {"start", "end"} and annotation.tool in _LINE_TOOLS:
        return _snap_line_endpoint(handle, points, x_guides, y_guides, threshold=threshold, shift=shift)
    if handle == "move" or annotation.tool == AnnotationTool.TEXT:
        return _snap_translate(annotation, points, x_guides, y_guides, threshold=threshold)
    if shift and annotation.tool in _BOX_SHIFT_TOOLS:
        return AnnotationSnapResult([QPointF(p) for p in points])
    return _snap_box_handles(annotation, handle, points, x_guides, y_guides, threshold=threshold)
```

</details>

## 🔧 Function `snap_point`

```python
def snap_point(point: QPointF, x_guides: Sequence[float], y_guides: Sequence[float], *, threshold: float = ANNOTATION_SNAP_THRESHOLD, snap_x: bool = True, snap_y: bool = True) -> tuple[QPointF, float | None, float | None]
```

Snap `point` independently on each axis; return the point and active guides.

<details>
<summary>Code:</summary>

```python
def snap_point(
    point: QPointF,
    x_guides: Sequence[float],
    y_guides: Sequence[float],
    *,
    threshold: float = ANNOTATION_SNAP_THRESHOLD,
    snap_x: bool = True,
    snap_y: bool = True,
) -> tuple[QPointF, float | None, float | None]:
    x, x_guide = (point.x(), None)
    y, y_guide = (point.y(), None)
    if snap_x:
        x, x_guide = _snap_value(point.x(), x_guides, threshold)
    if snap_y:
        y, y_guide = _snap_value(point.y(), y_guides, threshold)
    return QPointF(x, y), x_guide, y_guide
```

</details>

## 🔧 Function `snap_shape_end`

```python
def snap_shape_end(tool: AnnotationTool, start: QPointF, end: QPointF, x_guides: Sequence[float], y_guides: Sequence[float], *, threshold: float = ANNOTATION_SNAP_THRESHOLD, shift: bool = False) -> tuple[QPointF, float | None, float | None]
```

Snap a draft shape's free end after Shift constraints have been applied.

<details>
<summary>Code:</summary>

```python
def snap_shape_end(
    tool: AnnotationTool,
    start: QPointF,
    end: QPointF,
    x_guides: Sequence[float],
    y_guides: Sequence[float],
    *,
    threshold: float = ANNOTATION_SNAP_THRESHOLD,
    shift: bool = False,
) -> tuple[QPointF, float | None, float | None]:
    if shift and tool in _BOX_SHIFT_TOOLS:
        return QPointF(end), None, None
    snap_x = True
    snap_y = True
    if shift:
        snap_x, snap_y = _axis_snap_flags(start, end)
        if not snap_x and not snap_y:
            return QPointF(end), None, None
    return snap_point(end, x_guides, y_guides, threshold=threshold, snap_x=snap_x, snap_y=snap_y)
```

</details>
