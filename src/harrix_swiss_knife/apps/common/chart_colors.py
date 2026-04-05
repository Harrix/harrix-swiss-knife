"""Shared Qt chart color helpers for app main windows."""

from __future__ import annotations

import colorsys

from PySide6.QtGui import QColor


def generate_pastel_qcolors(count: int = 100) -> list[QColor]:
    """Build pastel QColors using golden-ratio hue spacing.

    Args:

    - `count` (`int`): Number of colors. Defaults to `100`.

    Returns:

    - `list[QColor]`: Pastel colors for series or date stripes.

    """
    colors: list[QColor] = []

    for i in range(count):
        hue = (i * 0.618033988749895) % 1.0
        saturation = 0.6
        lightness = 0.95
        r, g, b = colorsys.hls_to_rgb(hue, lightness, saturation)
        colors.append(QColor(int(r * 255), int(g * 255), int(b * 255)))

    return colors
