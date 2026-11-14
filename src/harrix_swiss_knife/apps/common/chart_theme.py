"""Matplotlib defaults that follow the Fluent light/dark theme.

Figures read `rcParams` when they are created, so charts drawn after a theme
switch pick up the new colors. Build figures with `themed_figure`; style axes
with `style_axes` (also applied via rcParams for new axes). Annotation boxes
use `chart_label_face` instead of a fixed white.

Typography targets (logical px at default UI scale): title ~18-20, labels /
ticks / legend ~12-14. Matplotlib uses points; sizes below match that ramp
for the suite body font (~14px).

"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

import matplotlib as mpl
from matplotlib.figure import Figure

from harrix_swiss_knife.fluent.theme import FluentTheme, css, mix

if TYPE_CHECKING:
    from collections.abc import Sequence

    from matplotlib.axes import Axes

_CURRENCY_SCALE_MILLIONS = 1_000_000
_CURRENCY_SCALE_THOUSANDS = 10_000

_state = {"connected": False}

# Type ramp in Matplotlib points (≈ logical px for on-screen charts).
CHART_TITLE_FONTSIZE = 12
CHART_LABEL_FONTSIZE = 9
CHART_TICK_FONTSIZE = 9
CHART_LEGEND_FONTSIZE = 9
CHART_ANNOTATION_FONTSIZE = 9

CHART_LINEWIDTH = 1.75
CHART_LINEWIDTH_EMPHASIS = 2.5
CHART_MARKERSIZE = 5
CHART_GRID_ALPHA = 0.28
CHART_GRID_LINEWIDTH = 0.7

# Stable comparative series (not neon cyan/magenta). Accent is injected first.
_SERIES_FALLBACK = (
    "#3a78bc",
    "#4caf50",
    "#cc584c",
    "#8e6bbf",
    "#db8b0a",
    "#2a9d8f",
    "#6d6875",
    "#e76f51",
)

LabelMode = Literal["auto", "all", "off"]


def apply_chart_theme() -> None:
    """Write the current Fluent palette into `matplotlib.rcParams`."""
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
            "axes.titlesize": CHART_TITLE_FONTSIZE,
            "axes.labelsize": CHART_LABEL_FONTSIZE,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "axes.axisbelow": True,
            "text.color": text,
            "xtick.color": secondary,
            "ytick.color": secondary,
            "xtick.labelcolor": text,
            "ytick.labelcolor": text,
            "xtick.labelsize": CHART_TICK_FONTSIZE,
            "ytick.labelsize": CHART_TICK_FONTSIZE,
            "grid.color": divider,
            "grid.alpha": CHART_GRID_ALPHA,
            "grid.linewidth": CHART_GRID_LINEWIDTH,
            "lines.linewidth": CHART_LINEWIDTH,
            "lines.markersize": CHART_MARKERSIZE,
            "legend.facecolor": surface,
            "legend.edgecolor": divider,
            "legend.labelcolor": text,
            "legend.fontsize": CHART_LEGEND_FONTSIZE,
            "legend.frameon": False,
            "font.size": CHART_LABEL_FONTSIZE,
        },
    )


def chart_annotation_style(*, fontsize: int | None = None) -> dict[str, Any]:
    """Return kwargs for opaque value labels on a themed chart."""
    return {
        "color": chart_ink(),
        "fontsize": CHART_ANNOTATION_FONTSIZE if fontsize is None else fontsize,
        "alpha": 1.0,
        "bbox": chart_label_bbox(),
    }


def chart_danger_color() -> str:
    """Return the theme danger / expense red."""
    return FluentTheme.instance().palette().critical.name()


def chart_info_panel_qss() -> str:
    """Return QSS for the HTML recommendations strip under Fitness charts."""
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


def chart_ink() -> str:
    """Return opaque primary chart text color for the current theme."""
    palette = FluentTheme.instance().palette()
    return mix(palette.window_bg, palette.text_primary).name()


def chart_label_bbox() -> dict[str, Any]:
    """Return a matplotlib annotation plate that contrasts with the plot face."""
    return {
        "boxstyle": "round,pad=0.25",
        "facecolor": chart_label_face(),
        "edgecolor": chart_label_edge(),
        "alpha": 0.95,
    }


def chart_label_edge() -> str:
    """Return the hairline around value-label boxes."""
    palette = FluentTheme.instance().palette()
    return mix(palette.window_bg, palette.divider).name()


def chart_label_face() -> str:
    """Return the fill for small value-label boxes drawn over a chart.

    Must differ from the axes face; otherwise labels look like pale floating text.

    """
    palette = FluentTheme.instance().palette()
    # Dark axes already use solid_tertiary/popup; lift the label fill so it reads as a chip.
    return mix(palette.window_bg, palette.card_bg).name()


def chart_muted_ink() -> str:
    """Return opaque secondary chart text color for the current theme."""
    palette = FluentTheme.instance().palette()
    return mix(palette.window_bg, palette.text_secondary).name()


def chart_series_color(index: int = 0) -> str:
    """Return a stable comparative series color; index 0 is the app accent."""
    palette = FluentTheme.instance().palette()
    colors = (
        palette.accent.name(),
        *(_c for _c in _SERIES_FALLBACK if _c.casefold() != palette.accent.name().casefold()),
    )
    if not colors:
        return _SERIES_FALLBACK[0]
    return colors[index % len(colors)]


def chart_series_palette(count: int) -> list[str]:
    """Return `count` distinct series colors starting with the accent."""
    return [chart_series_color(index) for index in range(max(0, count))]


def chart_success_color() -> str:
    """Return the theme success green (habits done / positive intensity)."""
    return FluentTheme.instance().palette().success.name()


def choose_currency_axis_scale(max_abs_value: float) -> tuple[float, str]:
    """Pick a readable currency axis divisor and short unit label.

    Returns `(1.0, "")` when values stay below one million. Callers show the
    full amount in tooltips; the axis uses `values / divisor`.

    """
    if max_abs_value >= _CURRENCY_SCALE_MILLIONS:
        return float(_CURRENCY_SCALE_MILLIONS), "mln"
    if max_abs_value >= _CURRENCY_SCALE_THOUSANDS:
        return 1_000.0, "k"
    return 1.0, ""


def ensure_chart_theme() -> None:
    """Apply the chart theme now and keep it in sync with `FluentTheme.changed`."""
    if not _state["connected"]:
        FluentTheme.instance().changed.connect(lambda _mode: apply_chart_theme())
        _state["connected"] = True
    apply_chart_theme()


def intensity_bin_label(lo: int, hi: int) -> str:
    """Return a short legend label for an inclusive intensity range."""
    if lo == hi:
        return str(lo)
    return f"{lo}-{hi}"


def intensity_bin_ranges(max_positive: int, *, max_bins: int = 5) -> list[tuple[int, int]]:
    """Split 1 through `max_positive` into 4-6 inclusive ranges for heatmap legends.

    Args:

    - `max_positive` (`int`): Highest observed positive count/value.
    - `max_bins` (`int`): Preferred number of intensity steps (clamped 4-6).

    Returns:

    - `list[tuple[int, int]]`: Inclusive `(lo, hi)` ranges covering 1 to max.

    """
    if max_positive <= 0:
        return []
    bins = max(4, min(6, max_bins))
    if max_positive <= bins:
        return [(value, value) for value in range(1, max_positive + 1)]
    edges: list[int] = [1]
    for index in range(1, bins):
        edge = 1 + round(index * max_positive / bins)
        if edge <= edges[-1]:
            edge = edges[-1] + 1
        edge = min(edge, max_positive)
        edges.append(edge)
    ranges: list[tuple[int, int]] = []
    for index, start in enumerate(edges):
        end = edges[index + 1] - 1 if index + 1 < len(edges) else max_positive
        end = max(end, start)
        ranges.append((start, end))
    # Merge accidental duplicates from rounding
    merged: list[tuple[int, int]] = []
    for lo, hi in ranges:
        if merged and lo <= merged[-1][1]:
            prev_lo, prev_hi = merged[-1]
            merged[-1] = (prev_lo, max(prev_hi, hi))
        else:
            merged.append((lo, hi))
    return merged


def map_value_to_intensity_bin(value: int, ranges: Sequence[tuple[int, int]]) -> int:
    """Map a positive value to a 1-based bin index; 0 stays 0."""
    if value <= 0 or not ranges:
        return 0
    for index, (lo, hi) in enumerate(ranges, start=1):
        if lo <= value <= hi:
            return index
    return len(ranges)


def style_axes(
    ax: Axes,
    *,
    horizontal_grid_only: bool = True,
    hide_top_right: bool = True,
) -> None:
    """Apply Fluent chart chrome to one axes (spines, grid, tick sizes)."""
    if hide_top_right:
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_linewidth(0.8)
    ax.set_axisbelow(True)
    ax.grid(visible=False)
    ax.grid(visible=True, axis="y", alpha=CHART_GRID_ALPHA, linewidth=CHART_GRID_LINEWIDTH)
    if not horizontal_grid_only:
        ax.grid(visible=True, axis="x", alpha=CHART_GRID_ALPHA * 0.6, linewidth=CHART_GRID_LINEWIDTH)
    ax.tick_params(labelsize=CHART_TICK_FONTSIZE)
    title = ax.get_title()
    if title:
        ax.set_title(title, fontsize=CHART_TITLE_FONTSIZE, fontweight="bold")
    ax.xaxis.label.set_fontsize(CHART_LABEL_FONTSIZE)
    ax.yaxis.label.set_fontsize(CHART_LABEL_FONTSIZE)


def themed_axes(figure: Figure, *args: Any, **kwargs: Any) -> Axes:
    """Return a new subplot from `figure.add_subplot` with `style_axes` applied."""
    ax = figure.add_subplot(*args, **kwargs)
    style_axes(ax)
    return ax


def themed_figure(**kwargs: Any) -> Figure:
    """Return a `Figure` that uses the current Fluent chart colors.

    Args:

    - `**kwargs` (`Any`): Passed to `matplotlib.figure.Figure`.

    Returns:

    - `Figure`: New figure with themed face, axes, text, and grid colors.

    """
    ensure_chart_theme()
    return Figure(**kwargs)
