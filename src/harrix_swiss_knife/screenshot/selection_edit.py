"""Hit-testing and geometry helpers for an adjustable screenshot selection frame."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from PySide6.QtCore import QPoint, QRect

if TYPE_CHECKING:
    from collections.abc import Sequence

HandleKind = Literal["move", "n", "s", "e", "w", "ne", "nw", "se", "sw"]
ArrowDir = Literal["left", "right", "up", "down"]

_DEFAULT_HANDLE = 8
_DEFAULT_EDGE_SNAP = 8


def collect_edge_guides(rects: Sequence[QRect], bounds: QRect) -> tuple[list[int], list[int]]:
    """Collect unique X/Y edge positions from `rects` and `bounds` for magnetic snapping."""
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


def cursor_for_handle(handle: HandleKind | None) -> str:
    """Return a Qt cursor shape name for `handle` (or cross for none)."""
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


def hit_test_selection_handle(
    rect: QRect,
    pos: QPoint,
    *,
    handle_size: int = _DEFAULT_HANDLE,
) -> HandleKind | None:
    """Return which resize handle (or move) is under `pos`, or `None` outside the frame.

    Corners are preferred over edges; the interior returns `move`.

    Args:

    - `rect` (`QRect`): Current selection rectangle.
    - `pos` (`QPoint`): Pointer position in the same coordinates as `rect`.
    - `handle_size` (`int`): Half-extent of the hot zone around edges/corners.

    Returns:

    - `HandleKind | None`: Handle under the pointer, or `None` if outside `rect`.

    """
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


def nudge_selection_rect(
    rect: QRect,
    direction: ArrowDir,
    *,
    step: int,
    resize: bool,
    bounds: QRect,
    min_size: int = 2,
) -> QRect:
    """Move or resize `rect` by `step` pixels in `direction`.

    Without `resize`, arrows translate the frame. With `resize`, left/right change
    width and up/down change height (top-left stays fixed when possible).

    """
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


def resize_selection_to_size(
    rect: QRect,
    *,
    width: int | None = None,
    height: int | None = None,
    bounds: QRect,
    min_size: int = 2,
) -> QRect:
    """Set width and/or height of `rect`, keeping the top-left corner when possible.

    If the new size would overflow `bounds`, the frame is shifted so the
    requested size still fits when `bounds` is large enough. Otherwise the
    size is clamped to `bounds`.

    Args:

    - `rect` (`QRect`): Current selection rectangle.
    - `width` (`int | None`): New width in pixels, or `None` to keep the current width.
    - `height` (`int | None`): New height in pixels, or `None` to keep the current height.
    - `bounds` (`QRect`): Clamp the result to this rectangle (usually the overlay).
    - `min_size` (`int`): Minimum width and height.

    Returns:

    - `QRect`: Updated selection, normalized and clamped.

    """
    new_width = rect.width() if width is None else width
    new_height = rect.height() if height is None else height
    new_width = min(max(min_size, new_width), max(min_size, bounds.width()))
    new_height = min(max(min_size, new_height), max(min_size, bounds.height()))
    left = rect.left()
    top = rect.top()
    if left + new_width - 1 > bounds.right():
        left = bounds.right() - new_width + 1
    if top + new_height - 1 > bounds.bottom():
        top = bounds.bottom() - new_height + 1
    left = max(left, bounds.left())
    top = max(top, bounds.top())
    return QRect(left, top, new_width, new_height).intersected(bounds)


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
    """Magnetically snap edges of `rect` involved in `handle` to nearby guides."""
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


def transform_selection_rect(
    start_rect: QRect,
    handle: HandleKind,
    press_pos: QPoint,
    current_pos: QPoint,
    *,
    bounds: QRect,
    min_size: int = 2,
) -> QRect:
    """Move or resize `start_rect` according to drag from `press_pos` to `current_pos`.

    Args:

    - `start_rect` (`QRect`): Rectangle at mouse-press time.
    - `handle` (`HandleKind`): Active handle / move mode.
    - `press_pos` (`QPoint`): Pointer position when the drag started.
    - `current_pos` (`QPoint`): Current pointer position.
    - `bounds` (`QRect`): Clamp result to this rectangle (usually the overlay).
    - `min_size` (`int`): Minimum width and height.

    Returns:

    - `QRect`: Updated selection, normalized and clamped.

    """
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


def _best_snap_delta(values: Sequence[int], targets: Sequence[int], threshold: int) -> int:
    """Return the translation that snaps the closest of `values` to a target."""
    best_delta = 0
    best_dist = threshold + 1
    for value in values:
        for target in targets:
            delta = target - value
            dist = abs(delta)
            if dist < best_dist:
                best_dist = dist
                best_delta = delta
    return best_delta if best_dist <= threshold else 0


def _clamp_move(rect: QRect, bounds: QRect) -> QRect:
    dx = 0
    dy = 0
    if rect.left() < bounds.left():
        dx = bounds.left() - rect.left()
    elif rect.right() > bounds.right():
        dx = bounds.right() - rect.right()
    if rect.top() < bounds.top():
        dy = bounds.top() - rect.top()
    elif rect.bottom() > bounds.bottom():
        dy = bounds.bottom() - rect.bottom()
    return rect.translated(dx, dy)


def _snap_value(value: int, targets: Sequence[int], threshold: int) -> int:
    best = value
    best_dist = threshold + 1
    for target in targets:
        dist = abs(value - target)
        if dist < best_dist:
            best_dist = dist
            best = target
    return best if best_dist <= threshold else value
