"""Logical ↔ physical pixel helpers for HiDPI screenshot capture."""

from __future__ import annotations

from PySide6.QtCore import QRect, QSize
from PySide6.QtGui import QImage, QPixmap


def crop_pixmap_from_logical_rect(pixmap: QPixmap, logical_rect: QRect) -> QImage | None:
    """Copy `logical_rect` from `pixmap`, mapping through its device pixel ratio.

    `QPixmap.copy()` uses device pixels. Mouse selection is in logical widget
    coordinates, so the rectangle must be scaled by `devicePixelRatio` first.

    The returned image has `devicePixelRatio` 1.0 so clipboard and preview treat
    the pixels as native resolution.

    """
    dpr = pixmap_device_pixel_ratio(pixmap)
    pixel_rect = logical_rect_to_pixel_rect(logical_rect, dpr)
    clipped = pixel_rect.intersected(QRect(0, 0, pixmap.width(), pixmap.height()))
    if clipped.isEmpty():
        return None
    image = pixmap.copy(clipped).toImage()
    image.setDevicePixelRatio(1.0)
    return image


def logical_rect_to_pixel_rect(rect: QRect, dpr: float) -> QRect:
    """Scale a logical rectangle to device pixels."""
    scale = dpr if dpr > 0 else 1.0
    return QRect(
        round(rect.x() * scale),
        round(rect.y() * scale),
        max(0, round(rect.width() * scale)),
        max(0, round(rect.height() * scale)),
    )


def logical_size_to_pixel_size(size: QSize, dpr: float) -> QSize:
    """Scale a logical size to device pixels."""
    scale = dpr if dpr > 0 else 1.0
    return QSize(
        max(1, round(size.width() * scale)),
        max(1, round(size.height() * scale)),
    )


def pixmap_as_physical_pixels(pixmap: QPixmap) -> QPixmap:
    """Return a copy whose `devicePixelRatio` is 1.0 so painters use raw pixels."""
    if pixmap_device_pixel_ratio(pixmap) == 1.0:
        return pixmap
    physical = QPixmap(pixmap)
    physical.setDevicePixelRatio(1.0)
    return physical


def pixmap_device_pixel_ratio(pixmap: QPixmap) -> float:
    """Return a positive device pixel ratio for `pixmap`."""
    dpr = pixmap.devicePixelRatio()
    return dpr if dpr > 0 else 1.0


def screen_destination_in_physical_pixels(
    screen_geometry: QRect,
    virtual_geometry: QRect,
    composed_dpr: float,
) -> QRect:
    """Map a screen's logical geometry onto the stitched physical canvas."""
    scale = composed_dpr if composed_dpr > 0 else 1.0
    return QRect(
        round((screen_geometry.x() - virtual_geometry.x()) * scale),
        round((screen_geometry.y() - virtual_geometry.y()) * scale),
        max(1, round(screen_geometry.width() * scale)),
        max(1, round(screen_geometry.height() * scale)),
    )
