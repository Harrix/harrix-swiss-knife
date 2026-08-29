---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `window_rects.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `list_snappable_window_rects`](#-function-list_snappable_window_rects)
- [🔧 Function `snap_rect_at_point`](#-function-snap_rect_at_point)

</details>

## 🔧 Function `list_snappable_window_rects`

```python
def list_snappable_window_rects(*, exclude_hwnds: Sequence[int] = ()) -> list[QRect]
```

Return visible top-level window bounds in Qt logical global coordinates.

Rectangles are ordered top-most first (same as Win32 `EnumWindows`). Non-Windows
platforms return an empty list.

Args:

- `exclude_hwnds` (`Sequence[int]`): Native window handles to skip (e.g. overlay).

Returns:

- `list[QRect]`: Snappable window rectangles in global logical pixels.

<details>
<summary>Code:</summary>

```python
def list_snappable_window_rects(*, exclude_hwnds: Sequence[int] = ()) -> list[QRect]:
    if sys.platform != "win32":
        return []
    excluded = {int(handle) for handle in exclude_hwnds if handle}
    return _list_snappable_window_rects_win32(exclude_hwnds=excluded)
```

</details>

## 🔧 Function `snap_rect_at_point`

```python
def snap_rect_at_point(point: QPoint, window_rects: Sequence[QRect]) -> QRect | None
```

Return the top-most rectangle that contains `point`, or `None`.

Args:

- `point` (`QPoint`): Cursor position in the same coordinate space as `window_rects`.
- `window_rects` (`Sequence[QRect]`): Candidates ordered top-most first.

Returns:

- `QRect | None`: Matching rectangle, or `None` when the point is outside all Windows.

<details>
<summary>Code:</summary>

```python
def snap_rect_at_point(point: QPoint, window_rects: Sequence[QRect]) -> QRect | None:
    for rect in window_rects:
        if rect.contains(point):
            return QRect(rect)
    return None
```

</details>
