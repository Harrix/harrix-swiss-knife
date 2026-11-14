---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `chart_timeline.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `TimelineBar`](#%EF%B8%8F-class-timelinebar)
- [🔧 Function `bar_at_x`](#-function-bar_at_x)
- [🔧 Function `build_timeline_figure`](#-function-build_timeline_figure)
- [🔧 Function `calendar_days`](#-function-calendar_days)
- [🔧 Function `needs_weekly_bars`](#-function-needs_weekly_bars)
- [🔧 Function `rolling_mean`](#-function-rolling_mean)
- [🔧 Function `week_spans`](#-function-week_spans)

</details>

## 🏛️ Class `TimelineBar`

```python
class TimelineBar
```

One bar, optionally with a matching average point.

<details>
<summary>Code:</summary>

```python
class TimelineBar:

    start: date
    end: date
    value: float
    line: float | None
    tooltip: str
```

</details>

## 🔧 Function `bar_at_x`

```python
def bar_at_x(bars: list[TimelineBar], x_value: float) -> TimelineBar | None
```

Return the bar whose date span contains a Matplotlib date coordinate.

<details>
<summary>Code:</summary>

```python
def bar_at_x(bars: list[TimelineBar], x_value: float) -> TimelineBar | None:
    if not bars:
        return None
    best: TimelineBar | None = None
    best_dist = 10_000.0
    for bar in bars:
        start_num = float(mdates.date2num(bar.start))
        end_num = float(mdates.date2num(bar.end)) + 1.0
        center = (start_num + end_num) / 2
        if start_num <= x_value <= end_num:
            return bar
        dist = abs(x_value - center)
        if dist < best_dist:
            best = bar
            best_dist = dist
    if best is None or best_dist > _HIT_SLOP_DAYS:
        return None
    return best
```

</details>

## 🔧 Function `build_timeline_figure`

```python
def build_timeline_figure(bars: list[TimelineBar], *, title: str, ylabel: str, bar_label: str, line_label: str, figsize: tuple[float, float], selected_start: date | None = None, selected_end: date | None = None, y_max: float | None = None, line_on_twin: bool = False, line_ylabel: str = '') -> Figure
```

Draw value bars and an average line. Limits stay on the supplied dates.

<details>
<summary>Code:</summary>

```python
def build_timeline_figure(
    bars: list[TimelineBar],
    *,
    title: str,
    ylabel: str,
    bar_label: str,
    line_label: str,
    figsize: tuple[float, float],
    selected_start: date | None = None,
    selected_end: date | None = None,
    y_max: float | None = None,
    line_on_twin: bool = False,
    line_ylabel: str = "",
) -> Figure:
    figure = themed_figure(figsize=figsize, dpi=100)
    axis = figure.add_subplot(111)
    if not bars:
        axis.set_title(title)
        axis.text(0.5, 0.5, "No data for the selected period", ha="center", va="center", transform=axis.transAxes)
        style_axes(axis)
        figure.tight_layout()
        return figure

    palette = FluentTheme.instance().palette()
    card = palette.card_bg.name()
    bar_color = chart_tint(palette.card_bg, palette.accent, 0.55).name()
    line_color = chart_series_color(0)
    centers = [mdates.date2num(bar.start) + (bar.end - bar.start).days / 2 for bar in bars]
    widths = [_bar_width_days(bar) for bar in bars]
    values = [bar.value for bar in bars]
    # Card-colored edges keep a 100% run from becoming one solid wall.
    axis.bar(
        centers,
        values,
        width=widths,
        color=bar_color,
        edgecolor=card,
        linewidth=0.8,
        label=bar_label,
        zorder=2,
        align="center",
    )

    line_axis = axis.twinx() if line_on_twin else axis
    line_x = [center for center, bar in zip(centers, bars, strict=True) if bar.line is not None]
    line_y = [bar.line for bar in bars if bar.line is not None]
    if line_x:
        (line,) = line_axis.plot(line_x, line_y, color=line_color, linewidth=2.0, label=line_label, zorder=4)
        # Halo so a flat 100% average stays readable on filled bars.
        line.set_path_effects(
            [patheffects.Stroke(linewidth=3.6, foreground=card), patheffects.Normal()],
        )
    if line_on_twin:
        line_axis.set_ylabel(line_ylabel or line_label)
        line_axis.tick_params(labelsize=9)
        line_axis.spines["top"].set_visible(False)

    if selected_start is not None and selected_end is not None:
        axis.axvspan(
            mdates.date2num(selected_start),
            mdates.date2num(selected_end) + 1,
            color=line_color,
            alpha=0.12,
            zorder=1,
        )

    start_num = float(mdates.date2num(bars[0].start)) - 0.5
    end_num = float(mdates.date2num(bars[-1].end)) + 1.5
    axis.set_xlim(start_num, end_num)
    axis.set_title(title)
    axis.set_ylabel(ylabel)
    if y_max is not None:
        # Leave room above 100% so full bars do not weld into the top spine.
        axis.set_ylim(0, y_max * _PERCENT_HEADROOM)
        if abs(y_max - _PERCENT_AXIS) < _PERCENT_AXIS_EPS:
            axis.set_yticks([0, 20, 40, 60, 80, 100])
    setup_date_axis(axis)
    style_axes(axis)
    handles, labels = axis.get_legend_handles_labels()
    if line_on_twin:
        extra_handles, extra_labels = line_axis.get_legend_handles_labels()
        handles += extra_handles
        labels += extra_labels
    if handles:
        legend = axis.legend(handles, labels, loc="upper left", frameon=True, fontsize=9)
        frame = legend.get_frame()
        frame.set_facecolor(palette.card_bg.name())
        frame.set_edgecolor(palette.card_bg.name())
        frame.set_alpha(0.92)
    figure.tight_layout()
    return figure
```

</details>

## 🔧 Function `calendar_days`

```python
def calendar_days(start: date, end: date) -> list[date]
```

Return each date from `start` through `end`.

<details>
<summary>Code:</summary>

```python
def calendar_days(start: date, end: date) -> list[date]:
    days: list[date] = []
    day = start
    while day <= end:
        days.append(day)
        day += timedelta(days=1)
    return days
```

</details>

## 🔧 Function `needs_weekly_bars`

```python
def needs_weekly_bars(day_count: int, width_px: int) -> bool
```

Use week bars when a day would be thinner than a readable column.

<details>
<summary>Code:</summary>

```python
def needs_weekly_bars(day_count: int, width_px: int) -> bool:
    if day_count <= 0:
        return False
    return width_px / day_count < _DAILY_BAR_PX
```

</details>

## 🔧 Function `rolling_mean`

```python
def rolling_mean(values: list[float], window: int) -> list[float | None]
```

Trailing mean. Leading points use the shorter available window.

<details>
<summary>Code:</summary>

```python
def rolling_mean(values: list[float], window: int) -> list[float | None]:
    if window <= 0:
        return [None for _value in values]
    means: list[float | None] = []
    for index in range(len(values)):
        chunk = values[max(0, index - window + 1) : index + 1]
        means.append(sum(chunk) / len(chunk) if chunk else None)
    return means
```

</details>

## 🔧 Function `week_spans`

```python
def week_spans(start: date, end: date, *, week_starts_on: int = HEATMAP_WEEK_STARTS_ON) -> list[tuple[date, date]]
```

Return inclusive week slices clipped to `[start, end]`.

<details>
<summary>Code:</summary>

```python
def week_spans(start: date, end: date, *, week_starts_on: int = HEATMAP_WEEK_STARTS_ON) -> list[tuple[date, date]]:
    if end < start:
        return []
    spans: list[tuple[date, date]] = []
    cursor = start
    while cursor <= end:
        week_end = habit_heatmap_week_start(cursor, week_starts_on=week_starts_on) + timedelta(days=6)
        span_end = min(end, week_end)
        spans.append((cursor, span_end))
        cursor = span_end + timedelta(days=1)
    return spans
```

</details>
