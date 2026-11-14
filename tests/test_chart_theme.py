"""Chart theme ink and label plates follow Fluent dark/light."""

from __future__ import annotations

import matplotlib as mpl
import pytest
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.apps.common.chart_theme import (
    HEATMAP_LEVELS_DARK,
    HEATMAP_LEVELS_LIGHT,
    apply_chart_theme,
    chart_annotation_style,
    chart_info_panel_qss,
    chart_ink,
    chart_label_face,
    current_chart_theme,
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
