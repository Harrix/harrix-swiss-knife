"""Orchestration for ShareX-like region screenshot capture."""

from __future__ import annotations

from PySide6.QtCore import QEventLoop, QRect, Qt, QTimer
from PySide6.QtGui import QImage, QPainter, QPixmap
from PySide6.QtWidgets import QApplication, QDialog

from harrix_swiss_knife.screenshot.preview_dialog import ScreenshotPreviewDialog
from harrix_swiss_knife.screenshot.region_overlay import RegionOverlay
from harrix_swiss_knife.screenshot.shutter_button import ShutterButton
from harrix_swiss_knife.screenshot.window_visibility import hide_app_windows, restore_app_windows

_HIDE_SETTLE_MS = 200


def capture_region(
    *,
    show_preview: bool = True,
    show_shutter_button: bool = True,
) -> QImage | None:
    """Capture a screen region with a ShareX-like workflow.

    Hides application Windows, optionally displays a floating camera (shutter) button,
    freezes the desktop for region selection, copies the cropped region to the clipboard,
    restores Windows, and optionally shows a preview dialog.

    Args:

    - `show_preview` (`bool`): If `True`, displays the preview dialog after capture. Defaults to `True`.
    - `show_shutter_button` (`bool`): If `True`, waits for a floating camera button click before
      starting region selection. Defaults to `True`.

    Returns:

    - `QImage | None`: Cropped image if captured, or `None` if the user cancelled.

    """
    app = QApplication.instance()
    if app is None:
        return None

    hidden = hide_app_windows()
    image: QImage | None = None
    try:
        _wait_ms(_HIDE_SETTLE_MS)

        if show_shutter_button:
            shutter = ShutterButton()
            if shutter.exec() != QDialog.DialogCode.Accepted:
                return None
            shutter.close()
            QApplication.processEvents()
            _wait_ms(50)

        frozen, geometry = _grab_virtual_desktop()
        if frozen.isNull():
            return None

        overlay = RegionOverlay(frozen, geometry)
        if overlay.exec() != QDialog.DialogCode.Accepted:
            return None

        image = overlay.cropped_image
        if image is None or image.isNull():
            return None

        clipboard = QApplication.clipboard()
        if clipboard is not None:
            clipboard.setImage(image)
    finally:
        restore_app_windows(hidden)

    if show_preview and image is not None and not image.isNull():
        dialog = ScreenshotPreviewDialog(image)
        dialog.exec()

    return image


def _grab_virtual_desktop() -> tuple[QPixmap, QRect]:
    """Grab all screens and stitch them into one pixmap covering the virtual desktop."""
    app = QApplication.instance()
    if app is None:
        return QPixmap(), QRect()

    screens = app.screens()
    primary = app.primaryScreen()
    if not screens or primary is None:
        return QPixmap(), QRect()

    virtual_geometry = primary.virtualGeometry()
    composed = QPixmap(virtual_geometry.size())
    composed.fill(Qt.GlobalColor.black)

    painter = QPainter(composed)
    try:
        for screen in screens:
            grab = screen.grabWindow(0)
            if grab.isNull():
                continue
            geo = screen.geometry()
            target = QRect(
                geo.x() - virtual_geometry.x(),
                geo.y() - virtual_geometry.y(),
                geo.width(),
                geo.height(),
            )
            painter.drawPixmap(target, grab)
    finally:
        painter.end()

    return composed, virtual_geometry


def _wait_ms(milliseconds: int) -> None:
    """Block the current call stack while keeping the Qt event loop running."""
    loop = QEventLoop()
    QTimer.singleShot(milliseconds, loop.quit)
    loop.exec()
