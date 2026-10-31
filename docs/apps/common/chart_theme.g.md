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
- [🔧 Function `chart_label_face`](#-function-chart_label_face)
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
    text = mix(palette.window_bg, palette.text_primary).name()
    secondary = mix(palette.window_bg, palette.text_secondary).name()
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
            "xtick.labelcolor": secondary,
            "ytick.labelcolor": secondary,
            "grid.color": divider,
            "legend.facecolor": surface,
            "legend.edgecolor": divider,
            "legend.labelcolor": text,
        },
    )
```

</details>

## 🔧 Function `chart_label_face`

```python
def chart_label_face() -> str
```

Return the fill for small value-label boxes drawn over a chart.

<details>
<summary>Code:</summary>

```python
def chart_label_face() -> str:
    palette = FluentTheme.instance().palette()
    return (palette.solid_tertiary_bg if palette.dark else palette.solid_quarternary_bg).name()
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
