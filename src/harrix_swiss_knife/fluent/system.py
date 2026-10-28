"""System helpers from the Fluent catalog: exponential blur and screen capture.

DXGI desktop duplication is not implemented; `ScreenCaptureManager` uses
`QScreen.grabWindow`, which is enough for screenshots and acrylic previews.

"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np
from PySide6.QtGui import QGuiApplication, QImage, QPixmap

if TYPE_CHECKING:
    from PySide6.QtCore import QRect

_ALPHA_PRECISION = 16
_PARAM_PRECISION = 7


class ScreenCaptureManager:
    """List monitors and grab a monitor or a desktop region as a `QPixmap`."""

    def capture_region(self, region: QRect) -> QPixmap:
        """Grab a rectangle in virtual-desktop coordinates (from the screen that holds its center)."""
        screen = QGuiApplication.screenAt(region.center()) or QGuiApplication.primaryScreen()
        if screen is None:
            return QPixmap()
        local = region.translated(-screen.geometry().topLeft())
        return screen.grabWindow(0, local.x(), local.y(), local.width(), local.height())

    def capture_screen(self, index: int = 0) -> QPixmap:
        """Grab the whole monitor at `index`."""
        screens = QGuiApplication.screens()
        if not 0 <= index < len(screens):
            return QPixmap()
        return screens[index].grabWindow(0)

    def screens(self) -> list[ScreenInfo]:
        """Return the connected monitors."""
        return [
            ScreenInfo(index, screen.name(), screen.geometry(), screen.devicePixelRatio())
            for index, screen in enumerate(QGuiApplication.screens())
        ]


@dataclass(frozen=True, slots=True)
class ScreenInfo:
    """One monitor known to `ScreenCaptureManager`."""

    index: int
    name: str
    geometry: QRect
    device_pixel_ratio: float


def exponential_blur(image: QImage, radius: int) -> QImage:
    """Return a blurred copy of `image` using a two-pass exponential (IIR) filter.

    Args:

    - `image` (`QImage`): Source image (any format; converted to ARGB32).
    - `radius` (`int`): Blur radius in pixels (`<= 0` returns a copy).

    """
    source = image.convertToFormat(QImage.Format.Format_ARGB32_Premultiplied)
    if radius <= 0 or source.isNull():
        return source.copy()
    width, height = source.width(), source.height()
    pointer = source.constBits()
    data = np.frombuffer(pointer, dtype=np.uint8, count=source.sizeInBytes()).reshape(height, source.bytesPerLine())
    pixels = data[:, : width * 4].reshape(height, width, 4).astype(np.int64) << _PARAM_PRECISION
    alpha = int((1 << _ALPHA_PRECISION) * (1.0 - np.exp(-2.3 / (radius + 1.0))))
    for _ in range(2):
        for axis in (1, 0):
            pixels = _blur_axis(pixels, alpha, axis)
    result = np.clip(pixels >> _PARAM_PRECISION, 0, 255).astype(np.uint8)
    output = QImage(width, height, QImage.Format.Format_ARGB32_Premultiplied)
    buffer = np.frombuffer(output.bits(), dtype=np.uint8, count=output.sizeInBytes()).reshape(
        height, output.bytesPerLine()
    )
    buffer[:, : width * 4] = result.reshape(height, width * 4)
    return output


def _blur_axis(pixels: np.ndarray, alpha: int, axis: int) -> np.ndarray:
    moved = np.moveaxis(pixels, axis, 0).copy()
    accumulator = moved[0].copy()
    for index in range(1, moved.shape[0]):
        accumulator += (alpha * (moved[index] - accumulator)) >> _ALPHA_PRECISION
        moved[index] = accumulator
    accumulator = moved[-1].copy()
    for index in range(moved.shape[0] - 2, -1, -1):
        accumulator += (alpha * (moved[index] - accumulator)) >> _ALPHA_PRECISION
        moved[index] = accumulator
    return np.moveaxis(moved, 0, axis)
