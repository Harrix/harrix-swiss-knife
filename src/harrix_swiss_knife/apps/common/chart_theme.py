"""Matplotlib defaults that follow the Fluent light/dark theme.

Figures read `rcParams` when they are created, so charts drawn after a theme
switch pick up the new colors. Build figures with `themed_figure`; annotation
boxes use `chart_label_face` instead of a fixed white.

"""

from __future__ import annotations

from typing import Any

import matplotlib as mpl
from matplotlib.figure import Figure

from harrix_swiss_knife.fluent.theme import FluentTheme, css, mix

_state = {"connected": False}


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


def chart_annotation_style(*, fontsize: int = 9) -> dict[str, Any]:
    """Return kwargs for opaque value labels on a themed chart."""
    return {
        "color": chart_ink(),
        "fontsize": fontsize,
        "alpha": 1.0,
        "bbox": chart_label_bbox(),
    }


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
    if palette.dark:
        return palette.popup_bg.name()
    return mix(palette.window_bg, palette.card_bg).name()


def chart_muted_ink() -> str:
    """Return opaque secondary chart text color for the current theme."""
    palette = FluentTheme.instance().palette()
    return mix(palette.window_bg, palette.text_secondary).name()


def ensure_chart_theme() -> None:
    """Apply the chart theme now and keep it in sync with `FluentTheme.changed`."""
    if not _state["connected"]:
        FluentTheme.instance().changed.connect(lambda _mode: apply_chart_theme())
        _state["connected"] = True
    apply_chart_theme()


def themed_figure(**kwargs: Any) -> Figure:
    """Return a `Figure` that uses the current Fluent chart colors.

    Args:

    - `**kwargs` (`Any`): Passed to `matplotlib.figure.Figure`.

    Returns:

    - `Figure`: New figure with themed face, axes, text, and grid colors.

    """
    ensure_chart_theme()
    return Figure(**kwargs)
