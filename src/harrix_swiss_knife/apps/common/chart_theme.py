"""Matplotlib defaults that follow the Fluent light/dark theme.

Figures read `rcParams` when they are created, so charts drawn after a theme
switch pick up the new colors. Build figures with `themed_figure`; annotation
boxes use `chart_label_face` instead of a fixed white.

"""

from __future__ import annotations

from typing import Any

import matplotlib as mpl
from matplotlib.figure import Figure

from harrix_swiss_knife.fluent.theme import FluentTheme, mix

_state = {"connected": False}


def apply_chart_theme() -> None:
    """Write the current Fluent palette into `matplotlib.rcParams`."""
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


def chart_label_face() -> str:
    """Return the fill for small value-label boxes drawn over a chart."""
    palette = FluentTheme.instance().palette()
    return (palette.solid_tertiary_bg if palette.dark else palette.solid_quarternary_bg).name()


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
