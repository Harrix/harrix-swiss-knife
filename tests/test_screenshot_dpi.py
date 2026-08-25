"""Tests for HiDPI logical-to-physical screenshot mapping."""

from __future__ import annotations

import pytest
from PySide6.QtCore import QRect, QSize
from PySide6.QtGui import QColor, QImage, QPixmap
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.screenshot.dpi import (
    crop_pixmap_from_logical_rect,
    logical_rect_to_pixel_rect,
    logical_size_to_pixel_size,
    pixmap_as_physical_pixels,
    screen_destination_in_physical_pixels,
)


@pytest.fixture
def qapp() -> QApplication:
    """Ensure a QApplication exists for pixmap helpers."""
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_logical_rect_to_pixel_rect_scales_fractional_dpr() -> None:
    """125% maps a logical 80x40 box at (8, 16) to 100x50 device pixels."""
    logical = QRect(8, 16, 80, 40)
    assert logical_rect_to_pixel_rect(logical, 1.25) == QRect(10, 20, 100, 50)


def test_logical_size_to_pixel_size_at_150_percent() -> None:
    """150% maps a 1280x720 logical desktop to 1920x1080 pixels."""
    assert logical_size_to_pixel_size(QSize(1280, 720), 1.5) == QSize(1920, 1080)


def test_screen_destination_places_second_monitor_in_physical_space() -> None:
    """A second logical 1280-wide screen starts at x=1920 when DPR is 1.5."""
    virtual = QRect(0, 0, 2560, 720)
    second = QRect(1280, 0, 1280, 720)
    assert screen_destination_in_physical_pixels(second, virtual, 1.5) == QRect(1920, 0, 1920, 1080)


def test_crop_pixmap_from_logical_rect_uses_device_pixels(qapp: QApplication) -> None:  # noqa: ARG001
    """A 10x10 logical crop on a 1.5x pixmap copies 15x15 native pixels."""
    source = QImage(30, 20, QImage.Format.Format_RGB32)
    source.fill(QColor(10, 20, 30))
    for x in range(15):
        for y in range(15):
            source.setPixelColor(x, y, QColor(200, 40, 40))
    pixmap = QPixmap.fromImage(source)
    pixmap.setDevicePixelRatio(1.5)

    cropped = crop_pixmap_from_logical_rect(pixmap, QRect(0, 0, 10, 10))
    assert cropped is not None
    assert cropped.size() == QSize(15, 15)
    assert cropped.devicePixelRatio() == 1.0
    assert cropped.pixelColor(0, 0) == QColor(200, 40, 40)
    assert cropped.pixelColor(14, 14) == QColor(200, 40, 40)


def test_pixmap_as_physical_pixels_clears_dpr(qapp: QApplication) -> None:  # noqa: ARG001
    """Painters must see the raw pixel size after stripping DPR."""
    source = QImage(1920, 1080, QImage.Format.Format_RGB32)
    source.fill(QColor("white"))
    pixmap = QPixmap.fromImage(source)
    pixmap.setDevicePixelRatio(1.5)
    physical = pixmap_as_physical_pixels(pixmap)
    assert physical.devicePixelRatio() == 1.0
    assert physical.size() == QSize(1920, 1080)
