"""Orchestration for ShareX-like region screenshot capture."""

from __future__ import annotations

from PySide6.QtCore import QEventLoop, QRect, Qt, QTimer
from PySide6.QtGui import QImage, QPainter, QPixmap, QScreen
from PySide6.QtWidgets import QApplication, QDialog

from harrix_swiss_knife.screenshot.dpi import (
    logical_size_to_pixel_size,
    pixmap_as_physical_pixels,
    screen_destination_in_physical_pixels,
)
from harrix_swiss_knife.screenshot.preview_dialog import ScreenshotPreviewDialog
from harrix_swiss_knife.screenshot.region_overlay import RESULT_TOGGLE_ARRANGE, RegionOverlay
from harrix_swiss_knife.screenshot.shutter_button import ArrangeModeDialog
from harrix_swiss_knife.screenshot.window_visibility import (
    PREVIEW_FOREGROUND_DELAYS_MS,
    bring_window_to_foreground,
    hide_app_windows,
    restore_app_windows,
)

_HIDE_SETTLE_MS = 200


def capture_region(
    *,
    show_preview: bool = True,
    show_shutter_button: bool = True,
) -> QImage | None:
    """Capture a screen region with a ShareX-like workflow.

    Hides application Windows for the whole session, freezes the desktop for region
    selection, copies the cropped region to the clipboard, restores Windows, and
    optionally shows a preview in the foreground.

    When `show_shutter_button` is `True`, arrange and close buttons are embedded in
    the selection overlay. Clicking the arrange button removes the overlay so the
    desktop can be arranged while the app stays hidden; a floating camera button
    returns to region selection with a fresh grab. Escape during a drag clears
    that selection; Escape with no active drag (or Close) cancels capture.

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
        show_preview_now = show_preview and image is not None and not image.isNull()
        restore_app_windows(hidden, activate=not show_preview_now)

    if show_preview and image is not None and not image.isNull():
        dialog = ScreenshotPreviewDialog(image)
        dialog.show()
        bring_window_to_foreground(dialog, delays_ms=PREVIEW_FOREGROUND_DELAYS_MS)
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


def _composed_device_pixel_ratio(screens: list[QScreen]) -> float:
    """Use the highest screen DPR so a HiDPI grab is never downscaled."""
    ratios = [screen.devicePixelRatio() for screen in screens if screen.devicePixelRatio() > 0]
    return max(ratios) if ratios else 1.0


def _copy_image_to_clipboard(image: QImage) -> None:
    clipboard = QApplication.clipboard()
    if clipboard is not None:
        clipboard.setImage(image)


def _grab_virtual_desktop() -> tuple[QPixmap, QRect]:
    """Grab all screens and stitch them into one pixmap covering the virtual desktop.

    `QScreen.geometry()` is in logical pixels, while `grabWindow(0)` returns
    physical pixels. The canvas is built in device pixels, then tagged with the
    compose DPR so the overlay can map mouse coordinates back correctly.

    """
    app = QApplication.instance()
    if app is None:
        return QPixmap(), QRect()

    screens = app.screens()
    primary = app.primaryScreen()
    if not screens or primary is None:
        return QPixmap(), QRect()

    virtual_geometry = primary.virtualGeometry()
    composed_dpr = _composed_device_pixel_ratio(screens)
    pixel_size = logical_size_to_pixel_size(virtual_geometry.size(), composed_dpr)
    canvas = QImage(pixel_size, QImage.Format.Format_ARGB32_Premultiplied)
    canvas.fill(Qt.GlobalColor.black)

    painter = QPainter(canvas)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, on=False)
    try:
        for screen in screens:
            grab = screen.grabWindow(0)
            if grab.isNull():
                continue
            dest = screen_destination_in_physical_pixels(screen.geometry(), virtual_geometry, composed_dpr)
            physical = pixmap_as_physical_pixels(grab)
            if physical.size() == dest.size():
                painter.drawPixmap(dest.topLeft(), physical)
            else:
                painter.drawPixmap(dest, physical)
    finally:
        painter.end()

    composed = QPixmap.fromImage(canvas)
    composed.setDevicePixelRatio(composed_dpr)
    return composed, virtual_geometry


def _wait_ms(milliseconds: int) -> None:
    """Block the current call stack while keeping the Qt event loop running."""
    loop = QEventLoop()
    QTimer.singleShot(milliseconds, loop.quit)
    loop.exec()
