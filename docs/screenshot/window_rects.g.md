---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `window_rects.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `filter_nested_control_candidates`](#-function-filter_nested_control_candidates)
- [🔧 Function `list_snappable_window_rects`](#-function-list_snappable_window_rects)
- [🔧 Function `snap_rect_at_point`](#-function-snap_rect_at_point)

</details>

## 🔧 Function `filter_nested_control_candidates`

```python
def filter_nested_control_candidates(candidates: Sequence[_SnapCandidate]) -> list[QRect]
```

Keep top-level frames always; drop controls fully covered by an earlier region.

ShareX builds the list depth-first (controls before parents). Hit-testing then picks
the first rectangle that contains the cursor, so smaller regions stay preferred.

Args:

- `candidates` (`Sequence[_SnapCandidate]`): Raw snap candidates in discovery order.

Returns:

- `list[QRect]`: Filtered rectangles for hover snapping.

<details>
<summary>Code:</summary>

```python
def filter_nested_control_candidates(candidates: Sequence[_SnapCandidate]) -> list[QRect]:
    result: list[QRect] = []
    for candidate in candidates:
        if not candidate.is_window and any(existing.contains(candidate.rect) for existing in result):
            continue
        result.append(QRect(candidate.rect))
    return result
```

</details>

## 🔧 Function `list_snappable_window_rects`

```python
def list_snappable_window_rects(*, exclude_hwnds: Sequence[int] = ()) -> list[QRect]
```

Return snappable regions in Qt logical global coordinates.

Includes window frames, client areas, child controls, and the taskbar. Ordered so
the first rectangle containing a point is the most specific match (ShareX-style).

Args:

- `exclude_hwnds` (`Sequence[int]`): Native window handles to skip (e.g. overlay).

Returns:

- `list[QRect]`: Snappable rectangles in global logical pixels.

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

Return the first rectangle that contains `point`, or `None`.

Args:

- `point` (`QPoint`): Cursor position in the same coordinate space as `window_rects`.
- `window_rects` (`Sequence[QRect]`): Candidates ordered most-specific first.

Returns:

- `QRect | None`: Matching rectangle, or `None` when the point is outside all regions.

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
