"""Orchestration for ShareX-like region screenshot capture."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from PySide6.QtCore import QEventLoop, QRect, QTimer
from PySide6.QtWidgets import QApplication, QDialog

from harrix_swiss_knife.screenshot.dpi import ScreenGrab
from harrix_swiss_knife.screenshot.preview_dialog import show_screenshot_preview
from harrix_swiss_knife.screenshot.region_overlay import (
    RESULT_TOGGLE_ARRANGE,
    RESULT_TOGGLE_KEEP_WINDOWS,
    RegionOverlay,
)
from harrix_swiss_knife.screenshot.shutter_button import ArrangeModeDialog
from harrix_swiss_knife.screenshot.window_rects import list_snappable_window_rects
from harrix_swiss_knife.screenshot.window_visibility import (
    PREVIEW_FOREGROUND_DELAYS_MS,
    ConcealedWindow,
    bring_window_to_foreground,
    has_visible_modal_dialog,
    hide_app_windows,
    restore_app_windows,
)

if TYPE_CHECKING:
    from collections.abc import Iterable

    from PySide6.QtGui import QImage
    from PySide6.QtWidgets import QWidget

_HIDE_SETTLE_MS = 200


@dataclass
class _HideSession:
    """Mutable hide/restore state so the shutter can toggle keep-Windows mid-capture."""

    hide_app: bool
    show_preview: bool = True
    hidden: list[ConcealedWindow] = field(default_factory=list)

    def apply_keep_windows(self, *, keep: bool) -> None:
        should_hide = not keep
        if should_hide == self.hide_app:
            return
        if keep:
            if self.hidden:
                restore_app_windows(self.hidden, activate=False)
            self.hidden = []
            self.hide_app = False
        else:
            self.hidden = hide_app_windows()
            self.hide_app = True
        _wait_ms(_HIDE_SETTLE_MS)

    def exclude_hwnds(self) -> list[int]:
        return _hwnds_from_widgets(item.widget for item in self.hidden)


def capture_region(
    *,
    show_preview: bool = True,
    show_shutter_button: bool = True,
    hide_app: bool | None = None,
) -> QImage | None:
    """Capture a screen region with a ShareX-like workflow.

    Optionally hides application Windows for the whole session, freezes the desktop
    for region selection, copies the cropped region to the clipboard, restores
    Windows, and optionally shows a preview in the foreground.

    When `hide_app` is `None` (the default), application Windows are hidden unless
    a modal dialog is visible (for example Finance Balance check). Hiding that
    dialog would drop it from the snap list so hover highlights the owner instead.

    When `hide_app` is `False`, application Windows stay visible so they can be
    included in the capture (for example a tracker window). The keep-Windows
    shutter button can flip this during selection: the overlay closes, Windows
    are hidden or restored, and a fresh grab opens a new overlay.

    When `show_shutter_button` is `True`, arrange, adjust, guides, keep-Windows,
    clipboard-only, and close buttons are embedded in the selection overlay.
    Arrange removes the overlay so the desktop can be rearranged; clipboard-only
    skips the preview after capture; adjust keeps the next selection editable
    (move/resize) until Enter or double-click; close cancels. A floating camera
    button returns to region selection with a fresh grab.

    Every capture overlay runs modally via `exec()`. The optional preview window is
    non-modal so later captures can add tabs to an already open preview.

    Args:

    - `show_preview` (`bool`): If `True`, displays the preview window after capture.
    - `show_shutter_button` (`bool`): If `True`, shows the mode-toggle shutter controls.
    - `hide_app` (`bool | None`): If `True`, conceals application Windows before
      the grab. If `False`, they stay visible. If `None`, conceal unless a modal
      dialog is visible.

    Returns:

    - `QImage | None`: Cropped image if captured, or `None` if the user cancelled.

    """
    app = QApplication.instance()
    if app is None:
        return None

    if hide_app is None:
        hide_app = not has_visible_modal_dialog()

    session = _HideSession(
        hide_app=hide_app,
        show_preview=show_preview,
        hidden=hide_app_windows() if hide_app else [],
    )
    image: QImage | None = None
    try:
        if session.hide_app:
            _wait_ms(_HIDE_SETTLE_MS)
        image = _capture_loop(with_controls=show_shutter_button, session=session)
    finally:
        show_preview_now = session.show_preview and image is not None and not image.isNull()
        if session.hide_app:
            restore_app_windows(session.hidden, activate=not show_preview_now)

    if session.show_preview and image is not None and not image.isNull():
        window = show_screenshot_preview(image)
        bring_window_to_foreground(window, delays_ms=PREVIEW_FOREGROUND_DELAYS_MS)

    return image


def _capture_loop(*, with_controls: bool, session: _HideSession) -> QImage | None:
    """Alternate between region selection and desktop-arrangement until done."""
    adjust_mode = False
    guides_mode = False
    clipboard_only = not session.show_preview
    while True:
        window_rects = list_snappable_window_rects(exclude_hwnds=session.exclude_hwnds())
        grabs, geometry = _grab_all_screens()
        if not grabs:
            return None

        overlay = RegionOverlay(
            grabs[0].pixmap,
            geometry,
            screen_grabs=grabs,
            with_shutter_controls=with_controls,
            window_rects=window_rects,
            keep_windows=not session.hide_app,
            clipboard_only=clipboard_only,
            adjust_mode=adjust_mode,
            guides_mode=guides_mode,
        )
        result = overlay.exec()
        adjust_mode = overlay.adjust_mode
        guides_mode = overlay.guides_mode
        clipboard_only = overlay.clipboard_only
        session.show_preview = not clipboard_only

        if result == int(QDialog.DialogCode.Accepted):
            image = overlay.cropped_image
            if image is None or image.isNull():
                return None
            _copy_image_to_clipboard(image)
            return image

        if result == RESULT_TOGGLE_KEEP_WINDOWS:
            session.apply_keep_windows(keep=overlay.keep_windows)
            continue

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


def _grab_all_screens() -> tuple[list[ScreenGrab], QRect]:
    """Grab each monitor at native resolution.

    A single overlay HWND uses the primary screen's DPI, so a 200% 4K monitor
    next to a 100% ultrawide would only cover part of the 4K display. Each grab
    is shown on its own fullscreen pane instead.

    """
    app = QApplication.instance()
    if app is None:
        return [], QRect()

    screens = app.screens()
    primary = app.primaryScreen()
    if not screens or primary is None:
        return [], QRect()

    grabs: list[ScreenGrab] = []
    for screen in screens:
        grab = screen.grabWindow(0)
        if grab.isNull():
            continue
        dpr = screen.devicePixelRatio()
        grabs.append(
            ScreenGrab(
                geometry=screen.geometry(),
                dpr=dpr if dpr > 0 else 1.0,
                pixmap=grab,
            ),
        )
    return grabs, primary.virtualGeometry()


def _hwnds_from_widgets(widgets: Iterable[QWidget]) -> list[int]:
    """Collect native window handles from Qt widgets (best-effort)."""
    handles: list[int] = []
    for widget in widgets:
        try:
            handle = int(widget.winId())
        except (AttributeError, RuntimeError, TypeError, ValueError):
            continue
        if handle:
            handles.append(handle)
    return handles


def _wait_ms(milliseconds: int) -> None:
    """Block the current call stack while keeping the Qt event loop running."""
    loop = QEventLoop()
    QTimer.singleShot(milliseconds, loop.quit)
    loop.exec()
