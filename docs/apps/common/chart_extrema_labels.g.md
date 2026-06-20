---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `chart_extrema_labels.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ChartExtremaLabelCandidate`](#%EF%B8%8F-class-chartextremalabelcandidate)
- [🏛️ Class `ChartExtremaLabelsConfig`](#%EF%B8%8F-class-chartextremalabelsconfig)
- [🔧 Function `annotate_chart_extrema_labels`](#-function-annotate_chart_extrema_labels)
- [🔧 Function `_annotation_candidates`](#-function-_annotation_candidates)
- [🔧 Function `_bbox_inside`](#-function-_bbox_inside)
- [🔧 Function `_bbox_overlap`](#-function-_bbox_overlap)
- [🔧 Function `_default_label_offset`](#-function-_default_label_offset)
- [🔧 Function `_draw_highlight_rings`](#-function-_draw_highlight_rings)
- [🔧 Function `_extremum_rank`](#-function-_extremum_rank)
- [🔧 Function `_find_label_offset`](#-function-_find_label_offset)
- [🔧 Function `_find_label_offset_no_clip`](#-function-_find_label_offset_no_clip)
- [🔧 Function `_get_renderer`](#-function-_get_renderer)
- [🔧 Function `_is_window_local_maximum`](#-function-_is_window_local_maximum)
- [🔧 Function `_is_window_local_minimum`](#-function-_is_window_local_minimum)
- [🔧 Function `_label_offset_candidates`](#-function-_label_offset_candidates)
- [🔧 Function `_local_max_prominence`](#-function-_local_max_prominence)
- [🔧 Function `_local_min_prominence`](#-function-_local_min_prominence)
- [🔧 Function `_measure_label_bbox`](#-function-_measure_label_bbox)
- [🔧 Function `_prioritize_stagger_candidates`](#-function-_prioritize_stagger_candidates)

</details>

## 🏛️ Class `ChartExtremaLabelCandidate`

```python
class ChartExtremaLabelCandidate
```

Series point eligible for an extrema label.

<details>
<summary>Code:</summary>

```python
class ChartExtremaLabelCandidate:

    index: int
    priority: int  # priority_high = global extrema / last point; priority_low = local
```

</details>

## 🏛️ Class `ChartExtremaLabelsConfig`

```python
class ChartExtremaLabelsConfig
```

Tunable parameters for extrema label placement.

<details>
<summary>Code:</summary>

```python
class ChartExtremaLabelsConfig:

    max_annotations: int = 18
    max_local_extrema_each: int = 8
    extrema_window: int = 2
    label_fontsize: int = 8
    overlap_pad: float = 8.0
    priority_high: int = 0
    priority_low: int = 1
```

</details>

## 🔧 Function `annotate_chart_extrema_labels`

```python
def annotate_chart_extrema_labels(ax: Axes, fig: Figure, x_nums: Sequence[float], y_values: Sequence[float], label_for_index: Callable[[int], str]) -> None
```

Draw extrema labels, leader lines, and highlight rings on a line chart.

Args:

- `ax` (`Axes`): Target axes (line already plotted).
- `fig` (`Figure`): Figure used to obtain a renderer for bbox measurement.
- `x_nums` (`Sequence[float]`): X coordinates (same length as `y_values`).
- `y_values` (`Sequence[float]`): Y values.
- `label_for_index` (`Callable[[int], str]`): Text for each candidate index.
- `enabled` (`bool`): When False, nothing is drawn.
- `config` (`ChartExtremaLabelsConfig | None`): Placement parameters.
- `point_color` (`str`): Color of the dashed highlight ring.

<details>
<summary>Code:</summary>

```python
def annotate_chart_extrema_labels(
    ax: Axes,
    fig: Figure,
    x_nums: Sequence[float],
    y_values: Sequence[float],
    label_for_index: Callable[[int], str],
    *,
    enabled: bool = True,
    config: ChartExtremaLabelsConfig | None = None,
    point_color: str = "steelblue",
) -> None:
    if not enabled or not y_values:
        return

    cfg = config or ChartExtremaLabelsConfig()
    y_list = list(y_values)
    x_list = list(x_nums)
    candidates = _annotation_candidates(y_list, cfg)
    if not candidates:
        return

    global_min_index = min(range(len(y_list)), key=y_list.__getitem__)
    global_max_index = max(range(len(y_list)), key=y_list.__getitem__)
    renderer = _get_renderer(fig)
    axes_bbox = ax.get_window_extent(renderer).expanded(0.98, 0.94)
    placed_boxes: list[Bbox] = []
    placed_indices: list[int] = []

    sorted_candidates = sorted(
        candidates,
        key=lambda candidate: (
            candidate.priority,
            candidate.index,
            -_extremum_rank(y_list, candidate.index, cfg),
        ),
    )

    for candidate in sorted_candidates:
        index = candidate.index
        label_text = label_for_index(index)
        default_offset = _default_label_offset(
            index,
            y_list,
            global_min_index=global_min_index,
            global_max_index=global_max_index,
        )
        label_offset = _find_label_offset(
            ax,
            renderer,
            axes_bbox,
            placed_boxes,
            cfg=cfg,
            x_num=x_list[index],
            y_value=y_list[index],
            label_text=label_text,
            default_offset=default_offset,
            placed_count=len(placed_indices),
        )
        if label_offset is None and candidate.priority == cfg.priority_high:
            label_offset = _find_label_offset(
                ax,
                renderer,
                axes_bbox,
                placed_boxes,
                cfg=cfg,
                x_num=x_list[index],
                y_value=y_list[index],
                label_text=label_text,
                default_offset=default_offset,
                placed_count=len(placed_indices),
                extended=True,
            )
        if label_offset is None and candidate.priority == cfg.priority_high:
            label_offset = _find_label_offset_no_clip(
                ax,
                renderer,
                placed_boxes,
                cfg=cfg,
                x_num=x_list[index],
                y_value=y_list[index],
                label_text=label_text,
                default_offset=default_offset,
                placed_count=len(placed_indices),
            )
        if label_offset is None:
            continue

        moved = label_offset != default_offset
        arrowprops = (
            {"arrowstyle": "-", "color": "gray", "linewidth": 0.6, "shrinkA": 0, "shrinkB": 2} if moved else None
        )
        ax.annotate(
            label_text,
            (x_list[index], y_list[index]),
            textcoords="offset points",
            xytext=label_offset,
            ha="center",
            fontsize=cfg.label_fontsize,
            alpha=0.8,
            bbox={"boxstyle": "round,pad=0.2", "facecolor": "white", "edgecolor": "none", "alpha": 0.7},
            arrowprops=arrowprops,
        )
        placed_boxes.append(
            _measure_label_bbox(
                ax,
                renderer,
                cfg,
                x_list[index],
                y_list[index],
                label_text,
                label_offset,
            )
        )
        placed_indices.append(index)

    _draw_highlight_rings(ax, x_list, y_list, placed_indices, color=point_color)
```

</details>

## 🔧 Function `_annotation_candidates`

```python
def _annotation_candidates(y_values: list[float], cfg: ChartExtremaLabelsConfig) -> list[ChartExtremaLabelCandidate]
```

Return label candidates: global extrema, last point (high), then local extrema (low).

<details>
<summary>Code:</summary>

```python
def _annotation_candidates(
    y_values: list[float],
    cfg: ChartExtremaLabelsConfig,
) -> list[ChartExtremaLabelCandidate]:
    count = len(y_values)
    if count == 0:
        return []
    window = cfg.extrema_window
    global_min_index = min(range(count), key=y_values.__getitem__)
    global_max_index = max(range(count), key=y_values.__getitem__)
    last_index = count - 1
    high_indices = {global_min_index, global_max_index, last_index}

    if count == 1:
        return [ChartExtremaLabelCandidate(0, cfg.priority_high)]

    local_maxima: list[int] = []
    local_minima: list[int] = []
    for index in range(count):
        if _is_window_local_maximum(y_values, index, window):
            local_maxima.append(index)
        elif _is_window_local_minimum(y_values, index, window):
            local_minima.append(index)

    candidates: list[ChartExtremaLabelCandidate] = [
        ChartExtremaLabelCandidate(index, cfg.priority_high) for index in high_indices
    ]
    selected_indices = set(high_indices)

    max_local_each = min(cfg.max_local_extrema_each, max(3, count // 8))
    ranked_local: list[tuple[int, float]] = [
        (index, _local_max_prominence(y_values, index, window))
        for index in local_maxima
        if index not in selected_indices
    ]
    ranked_local.extend(
        (index, _local_min_prominence(y_values, index, window))
        for index in local_minima
        if index not in selected_indices
    )
    ranked_local.sort(key=lambda item: item[1], reverse=True)

    for index, prominence in ranked_local:
        if prominence <= 0:
            continue
        if len(selected_indices) >= cfg.max_annotations:
            break
        if index in local_maxima:
            same_kind = [i for i in local_maxima if i in selected_indices]
        else:
            same_kind = [i for i in local_minima if i in selected_indices]
        if len(same_kind) >= max_local_each and index not in selected_indices:
            continue
        candidates.append(ChartExtremaLabelCandidate(index, cfg.priority_low))
        selected_indices.add(index)

    remaining = [
        (index, prominence) for index, prominence in ranked_local if index not in selected_indices and prominence > 0
    ]
    for index, _prominence in remaining:
        if len(selected_indices) >= cfg.max_annotations:
            break
        candidates.append(ChartExtremaLabelCandidate(index, cfg.priority_low))
        selected_indices.add(index)

    return candidates
```

</details>

## 🔧 Function `_bbox_inside`

```python
def _bbox_inside(inner: Bbox, outer: Bbox) -> bool
```

*No docstring provided.*

<details>
<summary>Code:</summary>

```python
def _bbox_inside(inner: Bbox, outer: Bbox) -> bool:
    center_x = (inner.x0 + inner.x1) / 2
    center_y = (inner.y0 + inner.y1) / 2
    return outer.x0 <= center_x <= outer.x1 and outer.y0 <= center_y <= outer.y1
```

</details>

## 🔧 Function `_bbox_overlap`

```python
def _bbox_overlap(first: Bbox, second: Bbox) -> bool
```

*No docstring provided.*

<details>
<summary>Code:</summary>

```python
def _bbox_overlap(first: Bbox, second: Bbox, *, pad: float) -> bool:
    return not (
        first.x1 + pad < second.x0
        or first.x0 - pad > second.x1
        or first.y1 + pad < second.y0
        or first.y0 - pad > second.y1
    )
```

</details>

## 🔧 Function `_default_label_offset`

```python
def _default_label_offset(index: int, y_values: list[float]) -> tuple[int, int]
```

*No docstring provided.*

<details>
<summary>Code:</summary>

```python
def _default_label_offset(
    index: int,
    y_values: list[float],
    *,
    global_min_index: int,
    global_max_index: int,
) -> tuple[int, int]:
    if index == global_max_index:
        return (0, 12)
    if index == global_min_index:
        return (0, -14)
    if index > 0 and y_values[index] >= y_values[index - 1]:
        return (0, 10)
    return (0, -12)
```

</details>

## 🔧 Function `_draw_highlight_rings`

```python
def _draw_highlight_rings(ax: Axes, x_nums: list[float], y_values: list[float], indices: list[int]) -> None
```

*No docstring provided.*

<details>
<summary>Code:</summary>

```python
def _draw_highlight_rings(
    ax: Axes,
    x_nums: list[float],
    y_values: list[float],
    indices: list[int],
    *,
    color: str,
) -> None:
    if not indices:
        return
    xs = [x_nums[index] for index in indices]
    ys = [y_values[index] for index in indices]
    ax.scatter(
        xs,
        ys,
        s=80,
        facecolors="none",
        edgecolors="white",
        linewidths=1.2,
        zorder=5,
    )
    ax.scatter(
        xs,
        ys,
        s=110,
        facecolors="none",
        edgecolors=color,
        linewidths=1.0,
        linestyles="--",
        zorder=4,
    )
```

</details>

## 🔧 Function `_extremum_rank`

```python
def _extremum_rank(y_values: list[float], index: int, cfg: ChartExtremaLabelsConfig) -> float
```

*No docstring provided.*

<details>
<summary>Code:</summary>

```python
def _extremum_rank(y_values: list[float], index: int, cfg: ChartExtremaLabelsConfig) -> float:
    window = cfg.extrema_window
    return max(
        _local_max_prominence(y_values, index, window),
        _local_min_prominence(y_values, index, window),
    )
```

</details>

## 🔧 Function `_find_label_offset`

```python
def _find_label_offset(ax: Axes, renderer: Any, axes_bbox: Bbox, placed_boxes: list[Bbox]) -> tuple[int, int] | None
```

*No docstring provided.*

<details>
<summary>Code:</summary>

```python
def _find_label_offset(
    ax: Axes,
    renderer: Any,
    axes_bbox: Bbox,
    placed_boxes: list[Bbox],
    *,
    cfg: ChartExtremaLabelsConfig,
    x_num: float,
    y_value: float,
    label_text: str,
    default_offset: tuple[int, int],
    placed_count: int = 0,
    extended: bool = False,
) -> tuple[int, int] | None:
    offset_candidates = _label_offset_candidates(
        default_offset,
        placed_count=placed_count,
        extended=extended,
    )
    if placed_boxes:
        default_bbox = _measure_label_bbox(
            ax,
            renderer,
            cfg,
            x_num,
            y_value,
            label_text,
            default_offset,
        )
        if any(_bbox_overlap(default_bbox, placed_bbox, pad=cfg.overlap_pad) for placed_bbox in placed_boxes):
            offset_candidates = _prioritize_stagger_candidates(
                offset_candidates,
                default_offset,
                placed_count,
            )

    for xytext in offset_candidates:
        label_bbox = _measure_label_bbox(ax, renderer, cfg, x_num, y_value, label_text, xytext)
        if not _bbox_inside(label_bbox, axes_bbox):
            continue
        if any(_bbox_overlap(label_bbox, placed_bbox, pad=cfg.overlap_pad) for placed_bbox in placed_boxes):
            continue
        return xytext
    return None
```

</details>

## 🔧 Function `_find_label_offset_no_clip`

```python
def _find_label_offset_no_clip(ax: Axes, renderer: Any, placed_boxes: list[Bbox]) -> tuple[int, int] | None
```

*No docstring provided.*

<details>
<summary>Code:</summary>

```python
def _find_label_offset_no_clip(
    ax: Axes,
    renderer: Any,
    placed_boxes: list[Bbox],
    *,
    cfg: ChartExtremaLabelsConfig,
    x_num: float,
    y_value: float,
    label_text: str,
    default_offset: tuple[int, int],
    placed_count: int,
) -> tuple[int, int] | None:
    offset_candidates = _prioritize_stagger_candidates(
        _label_offset_candidates(default_offset, placed_count=placed_count, extended=True),
        default_offset,
        placed_count,
    )
    for xytext in offset_candidates:
        label_bbox = _measure_label_bbox(ax, renderer, cfg, x_num, y_value, label_text, xytext)
        if not any(_bbox_overlap(label_bbox, placed_bbox, pad=cfg.overlap_pad) for placed_bbox in placed_boxes):
            return xytext
    return None
```

</details>

## 🔧 Function `_get_renderer`

```python
def _get_renderer(fig: Figure) -> Any
```

*No docstring provided.*

<details>
<summary>Code:</summary>

```python
def _get_renderer(fig: Figure) -> Any:
    canvas = FigureCanvasAgg(fig)
    canvas.draw()
    return canvas.get_renderer()
```

</details>

## 🔧 Function `_is_window_local_maximum`

```python
def _is_window_local_maximum(y_values: list[float], index: int, window: int) -> bool
```

*No docstring provided.*

<details>
<summary>Code:</summary>

```python
def _is_window_local_maximum(y_values: list[float], index: int, window: int) -> bool:
    count = len(y_values)
    lo = max(0, index - window)
    hi = min(count - 1, index + window)
    current = y_values[index]
    segment = y_values[lo : hi + 1]
    if current < max(segment):
        return False
    return any(j != index and current > y_values[j] for j in range(lo, hi + 1))
```

</details>

## 🔧 Function `_is_window_local_minimum`

```python
def _is_window_local_minimum(y_values: list[float], index: int, window: int) -> bool
```

*No docstring provided.*

<details>
<summary>Code:</summary>

```python
def _is_window_local_minimum(y_values: list[float], index: int, window: int) -> bool:
    count = len(y_values)
    lo = max(0, index - window)
    hi = min(count - 1, index + window)
    current = y_values[index]
    segment = y_values[lo : hi + 1]
    if current > min(segment):
        return False
    return any(j != index and current < y_values[j] for j in range(lo, hi + 1))
```

</details>

## 🔧 Function `_label_offset_candidates`

```python
def _label_offset_candidates(default_offset: tuple[int, int]) -> list[tuple[int, int]]
```

*No docstring provided.*

<details>
<summary>Code:</summary>

```python
def _label_offset_candidates(
    default_offset: tuple[int, int],
    *,
    placed_count: int = 0,
    extended: bool = False,
) -> list[tuple[int, int]]:
    default_x, default_y = default_offset
    stagger_sign = 1 if placed_count % 2 == 0 else -1
    opposite_y = -default_y if default_y != 0 else (-16 if default_y >= 0 else 16)

    offsets: list[tuple[int, int]] = [
        default_offset,
        (default_x, opposite_y),
        (default_x, stagger_sign * 22),
        (default_x, -stagger_sign * 22),
        (default_x, stagger_sign * 34),
        (default_x, -stagger_sign * 34),
        (0, 10),
        (0, -12),
        (0, 12),
        (0, -14),
    ]
    seen = set(offsets)
    steps = (14, 20, 26, 32, 40, 48, 56, 64, 72, 80) if extended else (14, 20, 26, 32, 40, 48, 56)
    for step in steps:
        for dx, dy in (
            (0, step),
            (0, -step),
            (10, step),
            (-10, step),
            (10, -step),
            (-10, -step),
            (14, step // 2),
            (-14, step // 2),
            (14, -step // 2),
            (-14, -step // 2),
        ):
            if (dx, dy) not in seen:
                offsets.append((dx, dy))
                seen.add((dx, dy))
    return offsets
```

</details>

## 🔧 Function `_local_max_prominence`

```python
def _local_max_prominence(y_values: list[float], index: int, window: int) -> float
```

*No docstring provided.*

<details>
<summary>Code:</summary>

```python
def _local_max_prominence(y_values: list[float], index: int, window: int) -> float:
    lo = max(0, index - window)
    hi = min(len(y_values) - 1, index + window)
    current = y_values[index]
    left_ref = max((y_values[j] for j in range(lo, index)), default=float("-inf"))
    right_ref = max((y_values[j] for j in range(index + 1, hi + 1)), default=float("-inf"))
    return max(0.0, current - max(left_ref, right_ref))
```

</details>

## 🔧 Function `_local_min_prominence`

```python
def _local_min_prominence(y_values: list[float], index: int, window: int) -> float
```

*No docstring provided.*

<details>
<summary>Code:</summary>

```python
def _local_min_prominence(y_values: list[float], index: int, window: int) -> float:
    lo = max(0, index - window)
    hi = min(len(y_values) - 1, index + window)
    current = y_values[index]
    left_ref = min((y_values[j] for j in range(lo, index)), default=float("inf"))
    right_ref = min((y_values[j] for j in range(index + 1, hi + 1)), default=float("inf"))
    return max(0.0, min(left_ref, right_ref) - current)
```

</details>

## 🔧 Function `_measure_label_bbox`

```python
def _measure_label_bbox(ax: Axes, renderer: Any, cfg: ChartExtremaLabelsConfig, x_num: float, y_value: float, label_text: str, xytext: tuple[int, int]) -> Bbox
```

*No docstring provided.*

<details>
<summary>Code:</summary>

```python
def _measure_label_bbox(
    ax: Axes,
    renderer: Any,
    cfg: ChartExtremaLabelsConfig,
    x_num: float,
    y_value: float,
    label_text: str,
    xytext: tuple[int, int],
) -> Bbox:
    annotation = ax.annotate(
        label_text,
        (x_num, y_value),
        textcoords="offset points",
        xytext=xytext,
        ha="center",
        fontsize=cfg.label_fontsize,
        alpha=0.8,
        bbox={"boxstyle": "round,pad=0.2", "facecolor": "white", "edgecolor": "none", "alpha": 0.7},
    )
    try:
        return annotation.get_window_extent(renderer).expanded(1.06, 1.14)
    finally:
        annotation.remove()
```

</details>

## 🔧 Function `_prioritize_stagger_candidates`

```python
def _prioritize_stagger_candidates(candidates: list[tuple[int, int]], default_offset: tuple[int, int], placed_count: int) -> list[tuple[int, int]]
```

*No docstring provided.*

<details>
<summary>Code:</summary>

```python
def _prioritize_stagger_candidates(
    candidates: list[tuple[int, int]],
    default_offset: tuple[int, int],
    placed_count: int,
) -> list[tuple[int, int]]:
    default_x, default_y = default_offset
    opposite_y = -default_y if default_y != 0 else (-14 if default_y >= 0 else 14)
    stagger_sign = 1 if placed_count % 2 == 0 else -1
    priority_offsets: list[tuple[int, int]] = []
    seen: set[tuple[int, int]] = set()

    def add_offset(offset: tuple[int, int]) -> None:
        if offset not in seen:
            priority_offsets.append(offset)
            seen.add(offset)

    for dy in (opposite_y, stagger_sign * 24, stagger_sign * 36, -stagger_sign * 24, -stagger_sign * 36):
        add_offset((default_x, dy))
    for dx in (12, -12, 16, -16):
        add_offset((dx, opposite_y))
        add_offset((dx, stagger_sign * 28))
    for offset in candidates:
        add_offset(offset)
    return priority_offsets
```

</details>
