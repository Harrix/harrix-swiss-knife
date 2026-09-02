"""Tests for HiDPI logical-to-physical screenshot mapping."""

from __future__ import annotations

import pytest
from PySide6.QtCore import QRect, QSize
from PySide6.QtGui import QColor, QImage, QPixmap
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.screenshot.dpi import (
    ScreenGrab,
    crop_from_mixed_dpi_grabs,
    crop_pixmap_from_logical_rect,
    logical_rect_to_pixel_rect,
    logical_size_to_pixel_size,
    pixmap_as_physical_pixels,
    screen_destination_in_physical_pixels,
    screen_native_destination,
)
from harrix_swiss_knife.screenshot.region_overlay import RegionOverlay

_K4_COLOR = QColor(20, 80, 200)
_UW_COLOR = QColor(200, 80, 20)
_K4_LOGICAL = QRect(0, 0, 1920, 1080)
_UW_LOGICAL = QRect(1920, 0, 3440, 1440)
_VIRTUAL = QRect(0, 0, 5360, 1440)


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


def test_screen_native_destination_keeps_100_percent_ultrawide_unscaled() -> None:
    """4K @ 200% stays 3840x2160; adjacent 100% ultrawide is not stretched to 200%."""
    assert screen_native_destination(_K4_LOGICAL, _VIRTUAL, 2.0, QSize(3840, 2160)) == QRect(0, 0, 3840, 2160)
    assert screen_native_destination(_UW_LOGICAL, _VIRTUAL, 2.0, QSize(3440, 1440)) == QRect(3840, 0, 3440, 1440)


def test_crop_from_mixed_dpi_grabs_4k_only(qapp: QApplication) -> None:  # noqa: ARG001
    """A selection on the 200% screen keeps native 3840x2160 pixels."""
    grabs = _mixed_dpi_grabs()
    cropped = crop_from_mixed_dpi_grabs(_K4_LOGICAL, grabs)
    assert cropped is not None
    assert cropped.size() == QSize(3840, 2160)
    assert cropped.devicePixelRatio() == 1.0
    assert cropped.pixelColor(0, 0) == _K4_COLOR
    assert cropped.pixelColor(3839, 2159) == _K4_COLOR


def test_crop_from_mixed_dpi_grabs_ultrawide_only(qapp: QApplication) -> None:  # noqa: ARG001
    """A selection on the 100% screen is not upscaled to the 4K DPR."""
    grabs = _mixed_dpi_grabs()
    cropped = crop_from_mixed_dpi_grabs(_UW_LOGICAL, grabs)
    assert cropped is not None
    assert cropped.size() == QSize(3440, 1440)
    assert cropped.pixelColor(0, 0) == _UW_COLOR
    assert cropped.pixelColor(3439, 1439) == _UW_COLOR


def test_crop_from_mixed_dpi_grabs_spanning_uses_max_dpr(qapp: QApplication) -> None:  # noqa: ARG001
    """A box that crosses both screens uses the higher DPR so the 4K side stays sharp."""
    grabs = _mixed_dpi_grabs()
    cropped = crop_from_mixed_dpi_grabs(QRect(1820, 0, 200, 1080), grabs)
    assert cropped is not None
    assert cropped.size() == QSize(400, 2160)
    assert cropped.pixelColor(0, 0) == _K4_COLOR
    assert cropped.pixelColor(399, 0) == _UW_COLOR


def test_overlay_builds_one_pane_per_screen_grab(qapp: QApplication) -> None:  # noqa: ARG001
    """Mixed DPI capture uses a fullscreen pane per monitor instead of one HWND."""
    grabs = _mixed_dpi_grabs()
    overlay = RegionOverlay(grabs[0].pixmap, _VIRTUAL, screen_grabs=grabs)
    try:
        assert overlay.geometry() == QRect(-16, -16, 1, 1)
        assert [pane.grab.geometry for pane in overlay._panes] == [_K4_LOGICAL, _UW_LOGICAL]
    finally:
        overlay.close()


def test_overlay_crops_4k_selection_at_native_pixels(qapp: QApplication) -> None:  # noqa: ARG001
    """Confirming a 4K-only frame copies native pixels, not the 1440-tall virtual canvas."""
    grabs = _mixed_dpi_grabs()
    overlay = RegionOverlay(grabs[0].pixmap, _VIRTUAL, screen_grabs=grabs)
    try:
        overlay._finish_with_rect(QRect(0, 0, 1920, 1080))
        image = overlay.cropped_image
        assert image is not None
        assert image.size() == QSize(3840, 2160)
        assert image.pixelColor(0, 0) == _K4_COLOR
    finally:
        overlay.close()


def _mixed_dpi_grabs() -> list[ScreenGrab]:
    """4K @ 200% on the left, 3440x1440 @ 100% on the right."""
    return [
        ScreenGrab(_K4_LOGICAL, 2.0, _solid_pixmap(3840, 2160, _K4_COLOR, dpr=2.0)),
        ScreenGrab(_UW_LOGICAL, 1.0, _solid_pixmap(3440, 1440, _UW_COLOR, dpr=1.0)),
    ]


def _solid_pixmap(width: int, height: int, color: QColor, *, dpr: float) -> QPixmap:
    image = QImage(width, height, QImage.Format.Format_RGB32)
    image.fill(color)
    pixmap = QPixmap.fromImage(image)
    pixmap.setDevicePixelRatio(dpr)
    return pixmap
