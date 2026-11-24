---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `heatmap_charts.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `daily_metric_recorded`](#-function-daily_metric_recorded)
- [🔧 Function `heatmap_period_choices`](#-function-heatmap_period_choices)
- [🔧 Function `metric_years`](#-function-metric_years)
- [🔧 Function `present_food_heatmap`](#-function-present_food_heatmap)
- [🔧 Function `range_period_choices`](#-function-range_period_choices)

</details>

## 🔧 Function `daily_metric_recorded`

```python
def daily_metric_recorded(points: list[tuple[str, float]], metric: str) -> dict[date, int]
```

Convert daily float points into integer recorded values for heatmap binning.

<details>
<summary>Code:</summary>

```python
def daily_metric_recorded(points: list[tuple[str, float]], metric: str) -> dict[date, int]:
    scale = _METRIC_SCALE.get(metric, 1)
    recorded: dict[date, int] = {}
    for text, amount in points:
        try:
            day = date.fromisoformat(str(text)[:10])
        except ValueError:
            continue
        units = round(float(amount) * scale)
        if units > 0:
            recorded[day] = recorded.get(day, 0) + units
    return recorded
```

</details>

## 🔧 Function `heatmap_period_choices`

```python
def heatmap_period_choices(years: list[int]) -> list[tuple[str, object]]
```

Build ChartToolbar period choices for the food heatmap.

<details>
<summary>Code:</summary>

```python
def heatmap_period_choices(years: list[int]) -> list[tuple[str, object]]:
    choices: list[tuple[str, object]] = [(LAST_365_LABEL, LAST_365_LABEL), (ALL_YEARS_LABEL, ALL_YEARS_LABEL)]
    choices.extend((str(year), year) for year in years)
    return choices
```

</details>

## 🔧 Function `metric_years`

```python
def metric_years(recorded: dict[date, int], *, today: date | None = None) -> list[int]
```

Return descending calendar years that have recorded activity.

<details>
<summary>Code:</summary>

```python
def metric_years(recorded: dict[date, int], *, today: date | None = None) -> list[int]:
    limit = today or datetime.now(UTC).astimezone().date()
    return sorted({day.year for day in recorded if day.year <= limit.year}, reverse=True)
```

</details>

## 🔧 Function `present_food_heatmap`

```python
def present_food_heatmap(layout: QVBoxLayout, recorded: dict[date, int], *, selection: object, metric: str, metric_title: str, unit: str, today: date | None = None) -> None
```

Fill `layout` with metrics, calendar heatmap, and optional timeline.

<details>
<summary>Code:</summary>

```python
def present_food_heatmap(
    layout: QVBoxLayout,
    recorded: dict[date, int],
    *,
    selection: object,
    metric: str,
    metric_title: str,
    unit: str,
    today: date | None = None,
) -> None:
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget() if item is not None else None
        if widget is not None:
            widget.deleteLater()

    day = today or datetime.now(UTC).astimezone().date()
    scale = _METRIC_SCALE.get(metric, 1)
    if not recorded:
        empty = FluentText(f"No {metric_title.lower()} to show.", word_wrap=True, role=TextRole.SECONDARY)
        layout.addWidget(empty)
        layout.addStretch(1)
        return

    bounds = _period_bounds(selection, day)
    metrics = MetricStrip()
    layout.addWidget(metrics)

    if bounds is None:
        _present_all_years(
            layout,
            metrics,
            recorded,
            metric_title=metric_title,
            unit=unit,
            scale=scale,
            today=day,
        )
        return

    start, end = bounds
    period_recorded = {key: value for key, value in recorded.items() if start <= key <= end}
    first_day = min(period_recorded) if period_recorded else None
    tokens, marks, legend, bin_count = habit_calendar_model(
        period_recorded,
        start,
        end,
        is_bool=False,
        activity_start=first_day,
        today=day,
    )
    colors = {cell: habit_token_color(state, bin_count=bin_count) for cell, state in tokens.items()}
    tips = {
        cell: _cell_tip(cell, period_recorded.get(cell, 0), metric_title=metric_title, unit=unit, scale=scale)
        for cell in tokens
    }
    heatmap = YearHeatmap()
    heatmap.set_calendar(
        start,
        end,
        colors,
        legend=habit_legend_colors(legend, bin_count=bin_count),
        marks=marks,
        tooltips=tips,
    )
    layout.addWidget(heatmap)

    stats = habit_period_stats(period_recorded, start, end, is_bool=False, today=day)
    metrics.set_metrics(_metric_pairs(stats, unit=unit, scale=scale))

    raw_bars, _percent = habit_timeline_bars(period_recorded, start, end, is_bool=False, today=day)
    bars = [
        TimelineBar(
            bar.start,
            bar.end,
            bar.value / scale,
            None if bar.line is None else bar.line / scale,
            _week_tip(bar.start, bar.end, period_recorded, metric_title=metric_title, unit=unit, scale=scale),
        )
        for bar in raw_bars
    ]

    time_host = QWidget()
    time_layout = QVBoxLayout(time_host)
    time_layout.setContentsMargins(0, SPACE_S, 0, 0)
    time_layout.setSpacing(0)
    layout.addWidget(time_host, 1)
    if not bars:
        return

    width = max(time_host.width(), 480)
    height = max(220, 240)
    figure = build_timeline_figure(
        bars,
        title=f"{metric_title} over time",
        ylabel="Weekly total",
        bar_label="Weekly total",
        line_label="7-day average",
        figsize=(width / 100, height / 100),
        line_on_twin=True,
        line_ylabel="7-day average",
    )
    canvas = create_chart_canvas(figure)

    def resolve_tooltip(event: Any) -> str | None:
        if event.xdata is None:
            return None
        bar = bar_at_x(bars, float(event.xdata))
        return None if bar is None else bar.tooltip

    install_chart_hover(canvas, resolve_tooltip=resolve_tooltip)
    canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    time_layout.addWidget(canvas, stretch=1)
    canvas.show()
    canvas.draw()
```

</details>

## 🔧 Function `range_period_choices`

```python
def range_period_choices() -> list[tuple[str, object]]
```

Restore the default Days / Months / Years period combo.

<details>
<summary>Code:</summary>

```python
def range_period_choices() -> list[tuple[str, object]]:
    return [(item, item) for item in _RANGE_PERIOD_ITEMS]
```

</details>
