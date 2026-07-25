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
_RESULT_TOGGLE = 2


def capture_region(
    *,
    show_preview: bool = True,
    show_shutter_button: bool = True,
) -> QImage | None:
    """Capture a screen region with a ShareX-like workflow.

    Hides application Windows for the whole session, freezes the desktop for region
    selection, copies the cropped region to the clipboard, restores Windows, and
    optionally shows a preview.

    When `show_shutter_button` is `True`, floating camera and close buttons stay on
    the left. Capture starts in region-selection mode. Clicking the camera removes
    the overlay so the desktop can be arranged while the app stays hidden; clicking
    again returns to region selection with a fresh grab. Close / Escape cancels.

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
    shutter: ShutterButton | None = None
    try:
        _wait_ms(_HIDE_SETTLE_MS)

        if show_shutter_button:
            shutter = ShutterButton()
            shutter.show()
            image = _capture_with_shutter_toggle(shutter)
        else:
            image = _capture_once()
            if image is None:
                return None
    finally:
        if shutter is not None:
            shutter.close()
        restore_app_windows(hidden)

    if show_preview and image is not None and not image.isNull():
        dialog = ScreenshotPreviewDialog(image)
        dialog.exec()

    return image


def _capture_once() -> QImage | None:
    """Grab desktop, run region overlay, return crop or `None`."""
    frozen, geometry = _grab_virtual_desktop()
    if frozen.isNull():
        return None

    overlay = RegionOverlay(frozen, geometry)
    if overlay.exec() != QDialog.DialogCode.Accepted:
        return None

    image = overlay.cropped_image
    if image is None or image.isNull():
        return None

    _copy_image_to_clipboard(image)
    return image


def _capture_with_shutter_toggle(shutter: ShutterButton) -> QImage | None:
    """Run selection and desktop-arrangement loop while app Windows stay hidden."""
    while True:
        shutter.set_mode("selection")
        frozen, geometry = _grab_desktop_without_shutter(shutter)
        if frozen.isNull():
            return None

        overlay = RegionOverlay(frozen, geometry)
        result = _run_region_selection(overlay, shutter)

        if result == int(QDialog.DialogCode.Accepted):
            image = overlay.cropped_image
            if image is None or image.isNull():
                return None
            _copy_image_to_clipboard(image)
            return image

        if result == int(QDialog.DialogCode.Rejected):
            return None

        # Mode button clicked: drop overlay so the desktop can be arranged; app stays hidden.
        if not shutter.wait_for_trigger_or_cancel():
            return None

        _wait_ms(_HIDE_SETTLE_MS)
        shutter.raise_above()


def _copy_image_to_clipboard(image: QImage) -> None:
    clipboard = QApplication.clipboard()
    if clipboard is not None:
        clipboard.setImage(image)


def _grab_desktop_without_shutter(shutter: ShutterButton) -> tuple[QPixmap, QRect]:
    """Hide the shutter briefly so it is not baked into the frozen desktop."""
    shutter.hide()
    QApplication.processEvents()
    _wait_ms(50)
    frozen, geometry = _grab_virtual_desktop()
    shutter.raise_above()
    return frozen, geometry


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


def _run_region_selection(overlay: RegionOverlay, shutter: ShutterButton) -> int:
    """Show non-modal overlay with shutter on top; return Accepted, Rejected, or toggle."""
    loop = QEventLoop()
    state = {"result": int(QDialog.DialogCode.Rejected), "done": False}

    def finish(result: int) -> None:
        if state["done"]:
            return
        state["done"] = True
        state["result"] = result
        loop.quit()

    def on_overlay_finished(result: int) -> None:
        finish(result)

    def on_shutter_triggered() -> None:
        finish(_RESULT_TOGGLE)

    def on_shutter_cancelled() -> None:
        finish(int(QDialog.DialogCode.Rejected))

    overlay.setWindowModality(Qt.WindowModality.NonModal)
    overlay.finished.connect(on_overlay_finished)
    shutter.triggered.connect(on_shutter_triggered)
    shutter.cancelled.connect(on_shutter_cancelled)
    try:
        overlay.show()
        overlay.raise_()
        overlay.activateWindow()
        shutter.raise_above()
        loop.exec()
    finally:
        shutter.triggered.disconnect(on_shutter_triggered)
        shutter.cancelled.disconnect(on_shutter_cancelled)
        overlay.finished.disconnect(on_overlay_finished)
        if overlay.isVisible():
            overlay.hide()
        overlay.close()

    return int(state["result"])


def _wait_ms(milliseconds: int) -> None:
    """Block the current call stack while keeping the Qt event loop running."""
    loop = QEventLoop()
    QTimer.singleShot(milliseconds, loop.quit)
    loop.exec()
