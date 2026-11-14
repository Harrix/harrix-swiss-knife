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

import contextlib
import weakref
from typing import TYPE_CHECKING, Any, Literal

import matplotlib as mpl
from matplotlib.figure import Figure
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.fluent.paint import with_alpha
from harrix_swiss_knife.fluent.theme import FluentTheme, css, mix

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence

    from matplotlib.axes import Axes
    from PySide6.QtGui import QColor

_CURRENCY_SCALE_MILLIONS = 1_000_000
_CURRENCY_SCALE_THOUSANDS = 10_000

_state = {"connected": False}
_LIVE_CANVASES: weakref.WeakSet[Any] = weakref.WeakSet()

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

# GitHub-style contribution levels. Chart code outside this module reads them from `ChartTheme`.
HEATMAP_LEVELS_LIGHT: tuple[str, ...] = ("#EBEDF0", "#9BE9A8", "#40C463", "#30A14E", "#216E39")
HEATMAP_LEVELS_DARK: tuple[str, ...] = ("#2D333B", "#0E4429", "#006D32", "#26A641", "#39D353")
HABIT_DONE_LIGHT = "#30A14E"
HABIT_DONE_DARK = "#26A641"

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
_SERIES_COUNT = 8


class ChartTheme:
    """Colors and font for one light or dark chart pass.

    Heatmap greens and habit-done greens are fixed scales. Everything else
    follows the Fluent palette so a theme switch repaints open charts.

    """

    __slots__ = (
        "accent",
        "bg",
        "border",
        "dark",
        "font_family",
        "grid",
        "habit_done",
        "habit_empty",
        "habit_outline",
        "habit_skipped",
        "heatmap",
        "negative",
        "neutral",
        "positive",
        "series",
        "text",
        "text_muted",
    )

    def __init__(
        self,
        *,
        dark: bool,
        font_family: str,
        bg: str,
        text: str,
        text_muted: str,
        grid: str,
        border: str,
        accent: str,
        positive: str,
        negative: str,
        neutral: str,
        series: tuple[str, ...],
        heatmap: tuple[str, ...],
        habit_done: str,
        habit_skipped: str,
        habit_empty: str,
        habit_outline: str,
    ) -> None:
        """Store one resolved theme snapshot."""
        self.dark = dark
        self.font_family = font_family
        self.bg = bg
        self.text = text
        self.text_muted = text_muted
        self.grid = grid
        self.border = border
        self.accent = accent
        self.positive = positive
        self.negative = negative
        self.neutral = neutral
        self.series = series
        self.heatmap = heatmap
        self.habit_done = habit_done
        self.habit_skipped = habit_skipped
        self.habit_empty = habit_empty
        self.habit_outline = habit_outline


def accent_heatmap_colors(steps: int) -> list[str]:
    """Return `steps` fills from a pale accent to the theme accent."""
    palette = FluentTheme.instance().palette()
    count = max(0, int(steps))
    if count == 0:
        return []
    if count == 1:
        return [palette.accent.name()]
    pale = 0.32
    span = 0.68
    surface = chart_surface()
    return [
        chart_tint(surface, palette.accent, pale + span * index / (count - 1)).name() for index in range(count)
    ]


def apply_chart_theme() -> None:
    """Write the current Fluent palette and UI font into `matplotlib.rcParams`."""
    theme = current_chart_theme()
    mpl.rcParams.update(
        {
            "figure.facecolor": theme.bg,
            "figure.edgecolor": theme.bg,
            "savefig.facecolor": theme.bg,
            "savefig.edgecolor": theme.bg,
            "axes.facecolor": theme.bg,
            "axes.edgecolor": theme.border,
            "axes.labelcolor": theme.text_muted,
            "axes.titlecolor": theme.text,
            "axes.titlesize": CHART_TITLE_FONTSIZE,
            "axes.labelsize": CHART_LABEL_FONTSIZE,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "axes.axisbelow": True,
            "text.color": theme.text,
            "xtick.color": theme.text_muted,
            "ytick.color": theme.text_muted,
            "xtick.labelcolor": theme.text,
            "ytick.labelcolor": theme.text,
            "xtick.labelsize": CHART_TICK_FONTSIZE,
            "ytick.labelsize": CHART_TICK_FONTSIZE,
            "grid.color": theme.grid,
            "grid.alpha": CHART_GRID_ALPHA,
            "grid.linewidth": CHART_GRID_LINEWIDTH,
            "lines.linewidth": CHART_LINEWIDTH,
            "lines.markersize": CHART_MARKERSIZE,
            "legend.facecolor": theme.bg,
            "legend.edgecolor": theme.grid,
            "legend.labelcolor": theme.text,
            "legend.fontsize": CHART_LEGEND_FONTSIZE,
            "legend.frameon": False,
            "font.family": "sans-serif",
            "font.sans-serif": [theme.font_family, "Segoe UI", "DejaVu Sans"],
            "font.size": CHART_LABEL_FONTSIZE,
        },
    )


def apply_theme(fig: Figure, ax: Axes | None = None) -> None:
    """Paint `fig` (and `ax`, or every axes) with the current chart theme.

    New figures use constrained layout. Axes lose the top and right spines and
    keep a thin horizontal grid. Call again after a light/dark switch — including
    legend labels and value-label plates that were drawn under the previous theme.

    """
    ensure_chart_theme()
    theme = current_chart_theme()
    fig.set_facecolor(theme.bg)
    fig.set_edgecolor(theme.bg)
    targets = list(fig.axes) if ax is None else [ax]
    for axis in targets:
        axis.set_facecolor(theme.bg)
        style_axes(axis)
        axis.xaxis.label.set_color(theme.text_muted)
        axis.yaxis.label.set_color(theme.text_muted)
        axis.title.set_color(theme.text)
        axis.tick_params(axis="both", colors=theme.text_muted, labelcolor=theme.text)
        for side in ("left", "bottom"):
            axis.spines[side].set_color(theme.border)
    _restyle_figure_overlays(fig, theme)
    if fig.get_layout_engine() is None:
        with contextlib.suppress(Exception):
            fig.set_layout_engine("constrained")


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


def chart_font_family() -> str:
    """Return the application font family, or Segoe UI when Qt has no app yet."""
    app = QApplication.instance()
    if isinstance(app, QApplication):
        family = app.font().family().strip()
        if family:
            return family
    return "Segoe UI"


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


def chart_neutral_color() -> str:
    """Return the theme neutral gray for past comparison series."""
    return FluentTheme.instance().palette().neutral.name()


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


def chart_surface() -> QColor:
    """Return an opaque card/plot surface for the active theme.

    Fluent `card_bg` is a translucent wash. Calling `.name()` on it yields pure
    white/black RGB and washes out dark heatmaps and legend plates — always mix
    it onto `window_bg` before painting or tinting.

    """
    palette = FluentTheme.instance().palette()
    return mix(palette.window_bg, palette.card_bg)


def chart_tint(base: QColor, overlay: QColor, amount: float) -> QColor:
    """Blend `overlay` over `base`. `amount` is 0 for `base` and 1 for `overlay`."""
    return mix(base, with_alpha(overlay, round(amount * 255)))


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


def current_chart_theme() -> ChartTheme:
    """Return chart colors and the UI font for the active light or dark palette."""
    palette = FluentTheme.instance().palette()
    dark = bool(palette.dark)
    surface = palette.solid_tertiary_bg if dark else palette.solid_quarternary_bg
    heatmap = HEATMAP_LEVELS_DARK if dark else HEATMAP_LEVELS_LIGHT
    return ChartTheme(
        dark=dark,
        font_family=chart_font_family(),
        bg=surface.name(),
        text=chart_ink(),
        text_muted=chart_muted_ink(),
        grid=mix(palette.window_bg, palette.divider).name(),
        border=mix(palette.window_bg, palette.control_strong_stroke).name(),
        accent=palette.accent.name(),
        positive=palette.success.name(),
        negative=palette.critical.name(),
        neutral=palette.neutral.name(),
        series=tuple(chart_series_palette(_SERIES_COUNT)),
        heatmap=heatmap,
        habit_done=HABIT_DONE_DARK if dark else HABIT_DONE_LIGHT,
        habit_skipped=palette.caution.name(),
        habit_empty=heatmap[0],
        habit_outline=mix(palette.window_bg, palette.control_strong_stroke).name(),
    )


def ensure_chart_theme() -> None:
    """Apply the chart theme now and restyle open canvases when the theme changes."""
    if not _state["connected"]:
        FluentTheme.instance().changed.connect(lambda _mode: restyle_live_charts())
        _state["connected"] = True
    apply_chart_theme()


def heatmap_absent_color() -> str:
    """Return the no-record cell fill. It stays lighter than an explicit zero."""
    return current_chart_theme().habit_empty


def heatmap_zero_color() -> str:
    """Return the fill for a recorded zero (not done / no completions)."""
    palette = FluentTheme.instance().palette()
    return chart_tint(chart_surface(), palette.text_secondary, 0.32).name()


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


def quantile_intensity_ranges(values: Iterable[int], *, max_bins: int = 4) -> list[tuple[int, int]]:
    """Split positive counts into non-overlapping quantile ranges.

    Zero is omitted so callers can show it as its own legend entry. Equal values
    collapse to one range. A short set of unique values becomes one range each
    instead of empty bins.

    Args:

    - `values` (`Iterable[int]`): Observed counts, including zeros.
    - `max_bins` (`int`): Upper bound on nonzero ranges.

    Returns:

    - `list[tuple[int, int]]`: Inclusive `(lo, hi)` ranges covering every positive value.

    """
    positive = sorted({int(value) for value in values if int(value) > 0})
    if not positive:
        return []
    bins = max(1, min(int(max_bins), len(positive)))
    if len(positive) <= bins:
        return [(value, value) for value in positive]
    ranges: list[tuple[int, int]] = []
    count = len(positive)
    for index in range(bins):
        start_index = round(index * count / bins)
        end_index = round((index + 1) * count / bins) - 1
        if end_index < start_index:
            continue
        lo = positive[start_index]
        hi = positive[end_index]
        if ranges and lo <= ranges[-1][1]:
            ranges[-1] = (ranges[-1][0], max(ranges[-1][1], hi))
        else:
            ranges.append((lo, hi))
    return ranges


def register_chart_canvas(canvas: object) -> None:
    """Remember a Qt canvas so a theme switch can restyle it without a restart."""
    with contextlib.suppress(TypeError):
        _LIVE_CANVASES.add(canvas)


def restyle_live_charts() -> None:
    """Push the current theme into rcParams and every registered canvas."""
    apply_chart_theme()
    for canvas in list(_LIVE_CANVASES):
        figure = getattr(canvas, "figure", None)
        if not isinstance(figure, Figure):
            continue
        apply_theme(figure)
        draw = getattr(canvas, "draw_idle", None)
        if callable(draw):
            draw()


def _restyle_figure_overlays(fig: Figure, theme: ChartTheme) -> None:
    """Repaint legend text and boxed annotations after a light/dark switch."""
    ink = chart_ink()
    face = chart_label_face()
    edge = chart_label_edge()
    legends: list[Any] = []
    for axis in fig.axes:
        legend = axis.get_legend()
        if legend is not None:
            legends.append(legend)
        for text in axis.texts:
            bbox = text.get_bbox_patch()
            if bbox is None:
                continue
            text.set_color(ink)
            bbox.set_facecolor(face)
            bbox.set_edgecolor(edge)
    figure_legends = getattr(fig, "legends", None)
    if figure_legends:
        legends.extend(figure_legends)
    for legend in legends:
        for text in legend.get_texts():
            text.set_color(theme.text)
        frame = legend.get_frame()
        frame.set_facecolor(theme.bg)
        frame.set_edgecolor(theme.grid)


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
    figure = Figure(**kwargs)
    apply_theme(figure)
    return figure
