"""Map a logical selection rectangle to ffmpeg gdigrab crop parameters."""

from __future__ import annotations

import sys
from dataclasses import dataclass

from PySide6.QtCore import QPoint, QRect
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.screenshot.dpi import logical_rect_to_pixel_rect

_MIN_EVEN_SIZE = 2
_MONITOR_DEFAULT_TO_NEAREST = 2

if sys.platform == "win32":
    import ctypes
    from ctypes import wintypes
else:
    ctypes = None  # type: ignore[assignment]
    wintypes = None  # type: ignore[assignment]


@dataclass(frozen=True, slots=True)
class GdigrabRegion:
    """Physical desktop crop for `-f gdigrab`."""

    offset_x: int
    offset_y: int
    width: int
    height: int


def even_size(width: int, height: int) -> tuple[int, int]:
    """Return even width/height (required by many video codecs)."""
    return max(_MIN_EVEN_SIZE, width - (width % 2)), max(_MIN_EVEN_SIZE, height - (height % 2))


def logical_rect_to_gdigrab(region: QRect) -> GdigrabRegion | None:
    """Convert a global logical Qt rectangle to gdigrab offsets and size.

    Prefers a single monitor that contains the selection center. Mixed-DPI
    selections that span monitors are clamped to the primary intersecting screen.

    """
    if region.isEmpty() or region.width() < _MIN_EVEN_SIZE or region.height() < _MIN_EVEN_SIZE:
        return None
    app = QApplication.instance()
    if app is None:
        return None
    screen = app.screenAt(region.center()) or app.primaryScreen()
    if screen is None:
        return None
    geo = screen.geometry()
    clipped = region.intersected(geo)
    if clipped.isEmpty():
        return None
    dpr = screen.devicePixelRatio()
    local = clipped.translated(-geo.x(), -geo.y())
    physical_local = logical_rect_to_pixel_rect(local, dpr)
    monitor_origin = _physical_monitor_origin(geo.topLeft())
    width, height = even_size(physical_local.width(), physical_local.height())
    if width < _MIN_EVEN_SIZE or height < _MIN_EVEN_SIZE:
        return None
    return GdigrabRegion(
        offset_x=monitor_origin.x() + physical_local.x(),
        offset_y=monitor_origin.y() + physical_local.y(),
        width=width,
        height=height,
    )


def _physical_monitor_origin(logical_top_left: QPoint) -> QPoint:
    """Return the physical virtual-desktop origin of the monitor at `logical_top_left`."""
    if sys.platform != "win32" or ctypes is None or wintypes is None:
        return QPoint(logical_top_left)

    class MONITORINFO(ctypes.Structure):
        _fields_ = (
            ("cbSize", wintypes.DWORD),
            ("rcMonitor", wintypes.RECT),
            ("rcWork", wintypes.RECT),
            ("dwFlags", wintypes.DWORD),
        )

    user32 = ctypes.windll.user32
    point = wintypes.POINT(int(logical_top_left.x()), int(logical_top_left.y()))
    try:
        desktop = user32.GetDesktopWindow()
        user32.LogicalToPhysicalPointForPerMonitorDPI(desktop, ctypes.byref(point))
    except AttributeError:
        pass
    monitor = user32.MonitorFromPoint(point, _MONITOR_DEFAULT_TO_NEAREST)
    info = MONITORINFO()
    info.cbSize = ctypes.sizeof(MONITORINFO)
    if not user32.GetMonitorInfoW(monitor, ctypes.byref(info)):
        return QPoint(logical_top_left)
    return QPoint(int(info.rcMonitor.left), int(info.rcMonitor.top))
