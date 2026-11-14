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
def annotate_chart_extrema_labels(ax: Axes, fig: Figure, x_nums: Sequence[float], y_values: Sequence[float], label_for_index: Callable[[int], str], *, enabled: bool = True, config: ChartExtremaLabelsConfig | None = None, point_color: str = 'steelblue') -> None
```

Draw extrema labels, leader lines, and highlight rings on a line chart.

Args:

- `ax` (`Axes`): Target axes (line already plotted).
- `fig` (`Figure`): Figure used to obtain a renderer for bbox measurement.
- `x_nums` (`Sequence[float]`): X coordinates (same length as `y_values`).
- `y_values` (`Sequence[float]`): Y values.
- `label_for_index` (`Callable[[int], str]`): Text for each candidate index.
- `enabled` (`bool`): When `False`, nothing is drawn.
- [`config`](../../actions/common/base.g.md#%EF%B8%8F-method-config-property) (`ChartExtremaLabelsConfig | None`): Placement parameters.
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

    global_min_index = min(range(len(y_list)), key=lambda index: y_list[index])
    global_max_index = max(range(len(y_list)), key=lambda index: y_list[index])
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
            {"arrowstyle": "-", "color": chart_muted_ink(), "linewidth": 0.6, "shrinkA": 0, "shrinkB": 2}
            if moved
            else None
        )
        style: dict[str, Any] = chart_annotation_style(fontsize=cfg.label_fontsize)
        bbox = dict(style.get("bbox", {}))
        bbox["edgecolor"] = point_color
        style["bbox"] = bbox
        ax.annotate(
            label_text,
            (x_list[index], y_list[index]),
            textcoords="offset points",
            xytext=label_offset,
            ha="center",
            arrowprops=arrowprops,
            **style,
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
