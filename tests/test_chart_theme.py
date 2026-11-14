"""Chart theme ink and label plates follow Fluent dark/light."""

from __future__ import annotations

import matplotlib as mpl
import pytest
from matplotlib.colors import to_hex
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.apps.common.chart_theme import (
    HEATMAP_LEVELS_DARK,
    HEATMAP_LEVELS_LIGHT,
    apply_chart_theme,
    apply_theme,
    chart_annotation_style,
    chart_info_panel_qss,
    chart_ink,
    chart_label_face,
    current_chart_theme,
    themed_figure,
)
from harrix_swiss_knife.fluent.theme import FluentTheme, ThemeMode
from harrix_swiss_knife.fluent.tokens import DARK_PALETTE


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_dark_chart_label_face_differs_from_axes_surface(qapp: QApplication) -> None:
    assert qapp is not None
    theme = FluentTheme.instance()
    previous = theme.mode()
    theme.set_mode(ThemeMode.DARK, persist=False)
    try:
        apply_chart_theme()
        face = QColor(chart_label_face())
        surface = DARK_PALETTE.solid_tertiary_bg
        assert face.name() != surface.name()
        assert face.lightness() < 80
        ink = QColor(chart_ink())
        assert ink.lightness() > 180
        style = chart_annotation_style()
        assert style["alpha"] == 1.0
        assert style["color"] == chart_ink()
        panel = chart_info_panel_qss().casefold()
        assert "#f0f0f0" not in panel
        assert "rgba(" in panel
        dark_theme = current_chart_theme()
        assert dark_theme.dark is True
        assert dark_theme.heatmap == HEATMAP_LEVELS_DARK
        assert dark_theme.accent == theme.palette().accent.name()
        assert "DejaVu Sans" in mpl.rcParams["font.sans-serif"]
    finally:
        theme.set_mode(previous, persist=False)
        apply_chart_theme()


def test_light_heatmap_scale(qapp: QApplication) -> None:
    """The light contribution scale matches the shared heatmap tokens."""
    assert qapp is not None
    theme = FluentTheme.instance()
    previous = theme.mode()
    theme.set_mode(ThemeMode.LIGHT, persist=False)
    try:
        chart = current_chart_theme()
        assert chart.dark is False
        assert chart.heatmap == HEATMAP_LEVELS_LIGHT
        assert chart.habit_done == "#30A14E"
    finally:
        theme.set_mode(previous, persist=False)
        apply_chart_theme()


def test_dark_heatmap_cells_are_not_white(qapp: QApplication) -> None:
    """Translucent card tokens must not collapse to #ffffff empty cells."""
    assert qapp is not None
    from harrix_swiss_knife.apps.common.chart_theme import (
        accent_heatmap_colors,
        chart_surface,
        heatmap_absent_color,
        heatmap_zero_color,
    )

    theme = FluentTheme.instance()
    previous = theme.mode()
    theme.set_mode(ThemeMode.DARK, persist=False)
    try:
        apply_chart_theme()
        absent = QColor(heatmap_absent_color())
        zero = QColor(heatmap_zero_color())
        surface = chart_surface()
        assert absent.isValid() and absent.lightness() < 80
        assert zero.isValid() and zero.lightness() < 140
        assert surface.lightness() < 80
        for fill in accent_heatmap_colors(4):
            assert QColor(fill).lightness() < 200
    finally:
        theme.set_mode(previous, persist=False)
        apply_chart_theme()


def test_apply_theme_updates_legend_and_annotation_after_switch(qapp: QApplication) -> None:
    """Open charts keep readable legend / value labels when light/dark flips."""
    assert qapp is not None
    theme = FluentTheme.instance()
    previous = theme.mode()
    theme.set_mode(ThemeMode.DARK, persist=False)
    apply_chart_theme()
    fig = themed_figure(figsize=(4, 3), dpi=100)
    ax = fig.add_subplot(111)
    ax.plot([1, 2, 3], [1, 2, 1], label="Series A")
    ax.legend(loc="upper left")
    ax.annotate("12", xy=(2, 2), **chart_annotation_style())
    dark_legend = ax.get_legend().get_texts()[0].get_color()
    dark_ink = QColor(to_hex(dark_legend, keep_alpha=False))
    assert dark_ink.lightness() > 180
    try:
        theme.set_mode(ThemeMode.LIGHT, persist=False)
        apply_theme(fig)
        light_legend = ax.get_legend().get_texts()[0].get_color()
        light_ink = QColor(to_hex(light_legend, keep_alpha=False))
        assert light_ink.lightness() < 80
        annotation = ax.texts[0]
        assert QColor(to_hex(annotation.get_color(), keep_alpha=False)).lightness() < 80
        face = annotation.get_bbox_patch()
        assert face is not None
        assert QColor(to_hex(face.get_facecolor(), keep_alpha=False)).lightness() > 180
    finally:
        theme.set_mode(previous, persist=False)
        apply_chart_theme()
