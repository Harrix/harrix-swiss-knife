"""Tests for shared chart color generation."""

from __future__ import annotations

from PySide6.QtGui import QColor

from harrix_swiss_knife.apps.common.chart_colors import generate_pastel_qcolors


def test_generate_pastel_qcolors_length() -> None:
    colors = generate_pastel_qcolors(7)
    assert len(colors) == 7
    assert all(isinstance(c, QColor) for c in colors)


def test_generate_pastel_qcolors_default_count() -> None:
    colors = generate_pastel_qcolors()
    assert len(colors) == 100


def test_generate_pastel_qcolors_distinct_hues() -> None:
    colors = generate_pastel_qcolors(5)
    rgb = {(c.red(), c.green(), c.blue()) for c in colors}
    assert len(rgb) == 5
