"""Hit-testing and geometry helpers for an adjustable screenshot selection frame."""

from __future__ import annotations

from typing import Literal

from PySide6.QtCore import QPoint, QRect

HandleKind = Literal["move", "n", "s", "e", "w", "ne", "nw", "se", "sw"]

_DEFAULT_HANDLE = 8


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
        moved = start_rect.translated(delta)
        dx = 0
        dy = 0
        if moved.left() < bounds.left():
            dx = bounds.left() - moved.left()
        elif moved.right() > bounds.right():
            dx = bounds.right() - moved.right()
        if moved.top() < bounds.top():
            dy = bounds.top() - moved.top()
        elif moved.bottom() > bounds.bottom():
            dy = bounds.bottom() - moved.bottom()
        return moved.translated(dx, dy)

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
