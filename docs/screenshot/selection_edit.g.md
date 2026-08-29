---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `selection_edit.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `collect_edge_guides`](#-function-collect_edge_guides)
- [🔧 Function `cursor_for_handle`](#-function-cursor_for_handle)
- [🔧 Function `hit_test_selection_handle`](#-function-hit_test_selection_handle)
- [🔧 Function `nudge_selection_rect`](#-function-nudge_selection_rect)
- [🔧 Function `snap_rect_to_edges`](#-function-snap_rect_to_edges)
- [🔧 Function `transform_selection_rect`](#-function-transform_selection_rect)

</details>

## 🔧 Function `collect_edge_guides`

```python
def collect_edge_guides(rects: Sequence[QRect], bounds: QRect) -> tuple[list[int], list[int]]
```

Collect unique X/Y edge positions from `rects` and `bounds` for magnetic snapping.

<details>
<summary>Code:</summary>

```python
def collect_edge_guides(rects: Sequence[QRect], bounds: QRect) -> tuple[list[int], list[int]]:
    x_edges = {bounds.left(), bounds.right()}
    y_edges = {bounds.top(), bounds.bottom()}
    for rect in rects:
        if not rect.isValid() or rect.isEmpty():
            continue
        x_edges.add(rect.left())
        x_edges.add(rect.right())
        y_edges.add(rect.top())
        y_edges.add(rect.bottom())
    return sorted(x_edges), sorted(y_edges)
```

</details>

## 🔧 Function `cursor_for_handle`

```python
def cursor_for_handle(handle: HandleKind | None) -> str
```

Return a Qt cursor shape name for `handle` (or cross for none).

<details>
<summary>Code:</summary>

```python
def cursor_for_handle(handle: HandleKind | None) -> str:
    mapping = {
        "move": "SizeAllCursor",
        "n": "SizeVerCursor",
        "s": "SizeVerCursor",
        "e": "SizeHorCursor",
        "w": "SizeHorCursor",
        "ne": "SizeBDiagCursor",
        "sw": "SizeBDiagCursor",
        "nw": "SizeFDiagCursor",
        "se": "SizeFDiagCursor",
    }
    return mapping.get(handle or "", "CrossCursor")
```

</details>

## 🔧 Function `hit_test_selection_handle`

```python
def hit_test_selection_handle(rect: QRect, pos: QPoint, *, handle_size: int = _DEFAULT_HANDLE) -> HandleKind | None
```

Return which resize handle (or move) is under `pos`, or `None` outside the frame.

Corners are preferred over edges; the interior returns `move`.

Args:

- `rect` (`QRect`): Current selection rectangle.
- `pos` (`QPoint`): Pointer position in the same coordinates as `rect`.
- `handle_size` (`int`): Half-extent of the hot zone around edges/corners.

Returns:

- `HandleKind | None`: Handle under the pointer, or `None` if outside `rect`.

<details>
<summary>Code:</summary>

```python
def hit_test_selection_handle(
    rect: QRect,
    pos: QPoint,
    *,
    handle_size: int = _DEFAULT_HANDLE,
) -> HandleKind | None:
    if not rect.isValid() or rect.isEmpty():
        return None
    outer = rect.adjusted(-handle_size, -handle_size, handle_size, handle_size)
    if not outer.contains(pos):
        return None

    left = abs(pos.x() - rect.left()) <= handle_size
    right = abs(pos.x() - rect.right()) <= handle_size
    top = abs(pos.y() - rect.top()) <= handle_size
    bottom = abs(pos.y() - rect.bottom()) <= handle_size

    if top and left:
        return "nw"
    if top and right:
        return "ne"
    if bottom and left:
        return "sw"
    if bottom and right:
        return "se"
    if top:
        return "n"
    if bottom:
        return "s"
    if left:
        return "w"
    if right:
        return "e"
    if rect.contains(pos):
        return "move"
    return None
```

</details>

## 🔧 Function `nudge_selection_rect`

```python
def nudge_selection_rect(rect: QRect, direction: ArrowDir, *, step: int, resize: bool, bounds: QRect, min_size: int = 2) -> QRect
```

Move or resize `rect` by [`step`](../installer/log.g.md#%EF%B8%8F-method-step) pixels in `direction`.

Without `resize`, arrows translate the frame. With `resize`, left/right change
width and up/down change height (top-left stays fixed when possible).

<details>
<summary>Code:</summary>

```python
def nudge_selection_rect(
    rect: QRect,
    direction: ArrowDir,
    *,
    step: int,
    resize: bool,
    bounds: QRect,
    min_size: int = 2,
) -> QRect:
    if step <= 0 or not rect.isValid():
        return QRect(rect)

    if not resize:
        dx = {"left": -step, "right": step, "up": 0, "down": 0}[direction]
        dy = {"left": 0, "right": 0, "up": -step, "down": step}[direction]
        moved = rect.translated(dx, dy)
        shift_x = 0
        shift_y = 0
        if moved.left() < bounds.left():
            shift_x = bounds.left() - moved.left()
        elif moved.right() > bounds.right():
            shift_x = bounds.right() - moved.right()
        if moved.top() < bounds.top():
            shift_y = bounds.top() - moved.top()
        elif moved.bottom() > bounds.bottom():
            shift_y = bounds.bottom() - moved.bottom()
        return moved.translated(shift_x, shift_y)

    left = rect.left()
    top = rect.top()
    width = rect.width()
    height = rect.height()
    if direction == "left":
        width = max(min_size, width - step)
    elif direction == "right":
        width = width + step
    elif direction == "up":
        height = max(min_size, height - step)
    else:
        height = height + step

    resized = QRect(left, top, width, height)
    if resized.right() > bounds.right():
        resized.setRight(bounds.right())
    if resized.bottom() > bounds.bottom():
        resized.setBottom(bounds.bottom())
    if resized.width() < min_size:
        resized.setWidth(min_size)
    if resized.height() < min_size:
        resized.setHeight(min_size)
    return resized.intersected(bounds)
```

</details>

## 🔧 Function `snap_rect_to_edges`

```python
def snap_rect_to_edges(rect: QRect, handle: HandleKind, x_edges: Sequence[int], y_edges: Sequence[int], *, threshold: int = _DEFAULT_EDGE_SNAP, bounds: QRect, min_size: int = 2) -> QRect
```

Magnetically snap edges of `rect` involved in `handle` to nearby guides.

<details>
<summary>Code:</summary>

```python
def snap_rect_to_edges(
    rect: QRect,
    handle: HandleKind,
    x_edges: Sequence[int],
    y_edges: Sequence[int],
    *,
    threshold: int = _DEFAULT_EDGE_SNAP,
    bounds: QRect,
    min_size: int = 2,
) -> QRect:
    left = rect.left()
    top = rect.top()
    right = rect.right()
    bottom = rect.bottom()

    if handle == "move":
        dx = _best_snap_delta([left, right], x_edges, threshold)
        dy = _best_snap_delta([top, bottom], y_edges, threshold)
        snapped = rect.translated(dx, dy)
        return _clamp_move(snapped, bounds)

    if "w" in handle:
        left = _snap_value(left, x_edges, threshold)
    if "e" in handle:
        right = _snap_value(right, x_edges, threshold)
    if "n" in handle:
        top = _snap_value(top, y_edges, threshold)
    if "s" in handle:
        bottom = _snap_value(bottom, y_edges, threshold)

    snapped = QRect(QPoint(left, top), QPoint(right, bottom)).normalized()
    if snapped.width() < min_size:
        if "w" in handle:
            snapped.setLeft(snapped.right() - min_size + 1)
        else:
            snapped.setRight(snapped.left() + min_size - 1)
    if snapped.height() < min_size:
        if "n" in handle:
            snapped.setTop(snapped.bottom() - min_size + 1)
        else:
            snapped.setBottom(snapped.top() + min_size - 1)
    return snapped.intersected(bounds)
```

</details>

## 🔧 Function `transform_selection_rect`

```python
def transform_selection_rect(start_rect: QRect, handle: HandleKind, press_pos: QPoint, current_pos: QPoint, *, bounds: QRect, min_size: int = 2) -> QRect
```

Move or resize `start_rect` according to drag from `press_pos` to `current_pos`.

Args:

- `start_rect` (`QRect`): Rectangle at mouse-press time.
- `handle` (`HandleKind`): Active handle / move mode.
- `press_pos` (`QPoint`): Pointer position when the drag started.
- `current_pos` (`QPoint`): Current pointer position.
- `bounds` (`QRect`): Clamp result to this rectangle (usually the overlay).
- `min_size` (`int`): Minimum width and height.

Returns:

- `QRect`: Updated selection, normalized and clamped.

<details>
<summary>Code:</summary>

```python
def transform_selection_rect(
    start_rect: QRect,
    handle: HandleKind,
    press_pos: QPoint,
    current_pos: QPoint,
    *,
    bounds: QRect,
    min_size: int = 2,
) -> QRect:
    delta = current_pos - press_pos
    left = start_rect.left()
    top = start_rect.top()
    right = start_rect.right()
    bottom = start_rect.bottom()

    if handle == "move":
        return _clamp_move(start_rect.translated(delta), bounds)

    if "w" in handle:
        left = start_rect.left() + delta.x()
    if "e" in handle:
        right = start_rect.right() + delta.x()
    if "n" in handle:
        top = start_rect.top() + delta.y()
    if "s" in handle:
        bottom = start_rect.bottom() + delta.y()

    rect = QRect(QPoint(left, top), QPoint(right, bottom)).normalized()
    if rect.width() < min_size:
        if "w" in handle:
            rect.setLeft(rect.right() - min_size + 1)
        else:
            rect.setRight(rect.left() + min_size - 1)
    if rect.height() < min_size:
        if "n" in handle:
            rect.setTop(rect.bottom() - min_size + 1)
        else:
            rect.setBottom(rect.top() + min_size - 1)
    return rect.intersected(bounds)
```

</details>
