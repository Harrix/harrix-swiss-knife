"""Orchestration for ShareX-like region screenshot capture."""

from __future__ import annotations

from PySide6.QtCore import QEventLoop, QRect, Qt, QTimer
from PySide6.QtGui import QImage, QPainter, QPixmap
from PySide6.QtWidgets import QApplication, QDialog

from harrix_swiss_knife.screenshot.preview_dialog import ScreenshotPreviewDialog
from harrix_swiss_knife.screenshot.region_overlay import RESULT_TOGGLE_ARRANGE, RegionOverlay
from harrix_swiss_knife.screenshot.shutter_button import ArrangeModeDialog
from harrix_swiss_knife.screenshot.window_visibility import hide_app_windows, restore_app_windows

_HIDE_SETTLE_MS = 200


def capture_region(
    *,
    show_preview: bool = True,
    show_shutter_button: bool = True,
) -> QImage | None:
    """Capture a screen region with a ShareX-like workflow.

    Hides application Windows for the whole session, freezes the desktop for region
    selection, copies the cropped region to the clipboard, restores Windows, and
    optionally shows a preview.

    When `show_shutter_button` is `True`, arrange and close buttons are embedded in
    the selection overlay. Clicking the arrange button removes the overlay so the
    desktop can be arranged while the app stays hidden; a floating camera button
    returns to region selection with a fresh grab. Close / Escape cancels.

    Every window shown here runs modally via `exec()`, so capture works even when
    it is started from nested modal dialogs (e.g. New Markdown → Fill with AI).

    Args:

    - `show_preview` (`bool`): If `True`, displays the preview dialog after capture.
    - `show_shutter_button` (`bool`): If `True`, shows the mode-toggle shutter controls.

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
        image = _capture_loop(with_controls=show_shutter_button)
    finally:
        restore_app_windows(hidden)

    if show_preview and image is not None and not image.isNull():
        dialog = ScreenshotPreviewDialog(image)
        dialog.exec()

    return image


def _capture_loop(*, with_controls: bool) -> QImage | None:
    """Alternate between region selection and desktop-arrangement until done."""
    while True:
        frozen, geometry = _grab_virtual_desktop()
        if frozen.isNull():
            return None

        overlay = RegionOverlay(frozen, geometry, with_shutter_controls=with_controls)
        result = overlay.exec()

        if result == int(QDialog.DialogCode.Accepted):
            image = overlay.cropped_image
            if image is None or image.isNull():
                return None
            _copy_image_to_clipboard(image)
            return image

        if result != RESULT_TOGGLE_ARRANGE:
            return None

        # Arrange mode: overlay is gone, app stays hidden, camera button floats on top.
        arrange = ArrangeModeDialog()
        if arrange.exec() != int(QDialog.DialogCode.Accepted):
            return None
        _wait_ms(_HIDE_SETTLE_MS)


def _copy_image_to_clipboard(image: QImage) -> None:
    clipboard = QApplication.clipboard()
    if clipboard is not None:
        clipboard.setImage(image)


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
