---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `chart_theme.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `apply_chart_theme`](#-function-apply_chart_theme)
- [🔧 Function `chart_annotation_style`](#-function-chart_annotation_style)
- [🔧 Function `chart_info_panel_qss`](#-function-chart_info_panel_qss)
- [🔧 Function `chart_ink`](#-function-chart_ink)
- [🔧 Function `chart_label_bbox`](#-function-chart_label_bbox)
- [🔧 Function `chart_label_edge`](#-function-chart_label_edge)
- [🔧 Function `chart_label_face`](#-function-chart_label_face)
- [🔧 Function `chart_muted_ink`](#-function-chart_muted_ink)
- [🔧 Function `ensure_chart_theme`](#-function-ensure_chart_theme)
- [🔧 Function `themed_figure`](#-function-themed_figure)

</details>

## 🔧 Function `apply_chart_theme`

```python
def apply_chart_theme() -> None
```

Write the current Fluent palette into `matplotlib.rcParams`.

<details>
<summary>Code:</summary>

```python
def apply_chart_theme() -> None:
    palette = FluentTheme.instance().palette()
    surface = (palette.solid_tertiary_bg if palette.dark else palette.solid_quarternary_bg).name()
    text = chart_ink()
    secondary = chart_muted_ink()
    divider = mix(palette.window_bg, palette.divider).name()
    stroke = mix(palette.window_bg, palette.control_strong_stroke).name()
    mpl.rcParams.update(
        {
            "figure.facecolor": surface,
            "figure.edgecolor": surface,
            "savefig.facecolor": surface,
            "savefig.edgecolor": surface,
            "axes.facecolor": surface,
            "axes.edgecolor": stroke,
            "axes.labelcolor": text,
            "axes.titlecolor": text,
            "text.color": text,
            "xtick.color": secondary,
            "ytick.color": secondary,
            "xtick.labelcolor": text,
            "ytick.labelcolor": text,
            "grid.color": divider,
            "legend.facecolor": surface,
            "legend.edgecolor": divider,
            "legend.labelcolor": text,
        },
    )
```

</details>

## 🔧 Function `chart_annotation_style`

```python
def chart_annotation_style(*, fontsize: int = 9) -> dict[str, Any]
```

Return kwargs for opaque value labels on a themed chart.

<details>
<summary>Code:</summary>

```python
def chart_annotation_style(*, fontsize: int = 9) -> dict[str, Any]:
    return {
        "color": chart_ink(),
        "fontsize": fontsize,
        "alpha": 1.0,
        "bbox": chart_label_bbox(),
    }
```

</details>

## 🔧 Function `chart_info_panel_qss`

```python
def chart_info_panel_qss() -> str
```

Return QSS for the HTML recommendations strip under Fitness charts.

<details>
<summary>Code:</summary>

```python
def chart_info_panel_qss() -> str:
    palette = FluentTheme.instance().palette()
    background = css(mix(palette.window_bg, palette.card_bg) if palette.dark else palette.solid_tertiary_bg)
    border = css(mix(palette.window_bg, palette.divider))
    text = css(mix(palette.window_bg, palette.text_primary))
    return f"""
            margin: 5px 0px;
            padding: 10px;
            background-color: {background};
            border: 1px solid {border};
            border-radius: 5px;
            color: {text};
            line-height: 1.2;
        """
```

</details>

## 🔧 Function `chart_ink`

```python
def chart_ink() -> str
```

Return opaque primary chart text color for the current theme.

<details>
<summary>Code:</summary>

```python
def chart_ink() -> str:
    palette = FluentTheme.instance().palette()
    return mix(palette.window_bg, palette.text_primary).name()
```

</details>

## 🔧 Function `chart_label_bbox`

```python
def chart_label_bbox() -> dict[str, Any]
```

Return a matplotlib annotation plate that contrasts with the plot face.

<details>
<summary>Code:</summary>

```python
def chart_label_bbox() -> dict[str, Any]:
    return {
        "boxstyle": "round,pad=0.25",
        "facecolor": chart_label_face(),
        "edgecolor": chart_label_edge(),
        "alpha": 0.95,
    }
```

</details>

## 🔧 Function `chart_label_edge`

```python
def chart_label_edge() -> str
```

Return the hairline around value-label boxes.

<details>
<summary>Code:</summary>

```python
def chart_label_edge() -> str:
    palette = FluentTheme.instance().palette()
    return mix(palette.window_bg, palette.divider).name()
```

</details>

## 🔧 Function `chart_label_face`

```python
def chart_label_face() -> str
```

Return the fill for small value-label boxes drawn over a chart.

Must differ from the axes face; otherwise labels look like pale floating text.

<details>
<summary>Code:</summary>

```python
def chart_label_face() -> str:
    palette = FluentTheme.instance().palette()
    if palette.dark:
        return palette.popup_bg.name()
    return mix(palette.window_bg, palette.card_bg).name()
```

</details>

## 🔧 Function `chart_muted_ink`

```python
def chart_muted_ink() -> str
```

Return opaque secondary chart text color for the current theme.

<details>
<summary>Code:</summary>

```python
def chart_muted_ink() -> str:
    palette = FluentTheme.instance().palette()
    return mix(palette.window_bg, palette.text_secondary).name()
```

</details>

## 🔧 Function `ensure_chart_theme`

```python
def ensure_chart_theme() -> None
```

Apply the chart theme now and keep it in sync with `FluentTheme.changed`.

<details>
<summary>Code:</summary>

```python
def ensure_chart_theme() -> None:
    if not _state["connected"]:
        FluentTheme.instance().changed.connect(lambda _mode: apply_chart_theme())
        _state["connected"] = True
    apply_chart_theme()
```

</details>

## 🔧 Function `themed_figure`

```python
def themed_figure(**kwargs: Any) -> Figure
```

Return a `Figure` that uses the current Fluent chart colors.

Args:

- `**kwargs` (`Any`): Passed to `matplotlib.figure.Figure`.

Returns:

- `Figure`: New figure with themed face, axes, text, and grid colors.

<details>
<summary>Code:</summary>

```python
def themed_figure(**kwargs: Any) -> Figure:
    ensure_chart_theme()
    return Figure(**kwargs)
```

</details>
