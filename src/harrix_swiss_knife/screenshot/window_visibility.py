"""Hide and restore application Windows during screenshot capture."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QApplication, QDialog
from shiboken6 import isValid

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget

if sys.platform == "win32":
    import ctypes

HSK_SCREENSHOT_UI_PROP = "hsk_screenshot_ui"

ConcealMode = Literal["hide", "opacity"]

_HWND_TOPMOST = -1
_HWND_NOTOPMOST = -2
_SWP_NOSIZE = 0x0001
_SWP_NOMOVE = 0x0002
_SWP_SHOWWINDOW = 0x0040
_ASFW_ANY = -1
_REPIN_MODAL_DELAYS_MS = (0, 50)


@dataclass(frozen=True)
class ConcealedWindow:
    """State needed to restore a window after screenshot capture."""

    widget: QWidget
    mode: ConcealMode
    opacity: float = 1.0
    modality: Qt.WindowModality = Qt.WindowModality.NonModal
    transparent_for_mouse: bool = False


def hide_app_windows() -> list[ConcealedWindow]:
    """Conceal visible top-level application Windows except screenshot UI.

    Modal dialogs are faded with opacity `0` instead of `hide()`, because
    hiding a modal `QDialog` ends its `exec()` loop as Rejected (e.g. Fill
    with AI source dialog while capturing a screenshot).

    When any modal dialog is visible, every other visible top-level window is
    also faded (not `hide()` / `show()`). `hide()` of a sibling such as
    Fitness, then `show()` after capture, often puts that window above a
    still-living `WindowModal` `QMessageBox`, which then blocks clicks while
    staying invisible.

    Modality is also set to NonModal and mouse events are ignored on faded
    dialogs. Note: Qt does not fully drop ApplicationModal blocking for a
    window that stays visible, so screenshot UI must still present itself as
    ApplicationModal on top (see `capture._capture_loop`).

    Returns:

    - `list[ConcealedWindow]`: Windows that were concealed and should be restored.

    """
    app = QApplication.instance()
    if app is None:
        return []

    candidates = [widget for widget in app.topLevelWidgets() if widget.isVisible() and not is_screenshot_ui(widget)]
    opacity_targets = _opacity_conceal_targets(candidates)

    concealed: list[ConcealedWindow] = []
    for widget in candidates:
        if widget in opacity_targets:
            concealed.append(_conceal_with_opacity(widget))
        else:
            widget.hide()
            concealed.append(ConcealedWindow(widget, "hide"))

    QApplication.processEvents()
    return concealed


def is_screenshot_ui(widget: QWidget) -> bool:
    """Return whether the widget belongs to the screenshot capture UI."""
    return bool(widget.property(HSK_SCREENSHOT_UI_PROP))


def mark_screenshot_ui(widget: QWidget) -> None:
    """Mark a widget so it is not hidden with the rest of the application."""
    widget.setProperty(HSK_SCREENSHOT_UI_PROP, True)  # noqa: FBT003


def restore_app_windows(widgets: list[ConcealedWindow]) -> None:
    """Restore Windows previously concealed by `hide_app_windows` and bring them forward.

    After a fullscreen capture overlay, other apps may sit on top of the Z-order.
    Restored widgets are raised and the topmost modal dialog is activated so the
    user returns to Fill with AI / New Markdown / an error `QMessageBox`.

    Non-modal (`hide`) Windows are restored first; opacity-concealed owners
    next; modal dialogs last so they stay above the owner chain.

    """
    hide_items = [item for item in widgets if item.mode == "hide"]
    opacity_owners, opacity_modals = _split_opacity_items(widgets)

    for item in hide_items:
        item.widget.show()
        item.widget.raise_()

    for item in [*opacity_owners, *opacity_modals]:
        _restore_opacity_item(item)

    for item in opacity_owners:
        item.widget.raise_()
    for item in opacity_modals:
        item.widget.raise_()

    QApplication.processEvents()

    focus_target = _pick_focus_target(widgets)
    if focus_target is not None:
        _bring_to_foreground(focus_target)
        QApplication.processEvents()
        # Show/raise of owners can land after the first raise; pin the modal again.
        _bring_to_foreground(focus_target)
        _schedule_foreground(focus_target)

    QApplication.processEvents()


def _bring_to_foreground(widget: QWidget) -> None:
    """Raise `widget` in Qt and ask the OS to activate its native window."""
    if not isValid(widget):
        return
    if not widget.isVisible():
        widget.show()
    widget.raise_()
    widget.activateWindow()
    _force_foreground(widget)


def _conceal_with_opacity(widget: QWidget) -> ConcealedWindow:
    """Fade a top-level window without ending a nested `exec()` loop."""
    opacity = widget.windowOpacity()
    modality = widget.windowModality()
    was_transparent = bool(widget.testAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents))
    widget.setWindowOpacity(0.0)
    # Keep exec() alive, but do not leave an ApplicationModal blocker.
    widget.setWindowModality(Qt.WindowModality.NonModal)
    widget.setAttribute(
        Qt.WidgetAttribute.WA_TransparentForMouseEvents,
        True,  # noqa: FBT003
    )
    # setWindowModality() can unmap QMessageBox; show() again so exec() stays
    # alive and restore can put the box back on top of Fitness.
    if not widget.isVisible():
        widget.show()
    return ConcealedWindow(
        widget,
        "opacity",
        opacity,
        modality=modality,
        transparent_for_mouse=was_transparent,
    )


def _force_foreground(widget: QWidget) -> None:
    """Ask the OS to put the widget's native window in the foreground."""
    if sys.platform != "win32":
        return
    try:
        hwnd = int(widget.winId())
        if not hwnd:
            return
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        flags = _SWP_NOMOVE | _SWP_NOSIZE | _SWP_SHOWWINDOW
        user32.AllowSetForegroundWindow(_ASFW_ANY)
        # TOPMOST flash: SetForegroundWindow is often denied after a fullscreen overlay.
        user32.SetWindowPos(hwnd, _HWND_TOPMOST, 0, 0, 0, 0, flags)
        user32.SetWindowPos(hwnd, _HWND_NOTOPMOST, 0, 0, 0, 0, flags)

        foreground = user32.GetForegroundWindow()
        current_thread = kernel32.GetCurrentThreadId()
        process_id = ctypes.c_ulong(0)
        other_thread = user32.GetWindowThreadProcessId(foreground, ctypes.byref(process_id))
        attached = False
        if foreground and other_thread and other_thread != current_thread:
            attached = bool(user32.AttachThreadInput(current_thread, other_thread, True))  # noqa: FBT003
        user32.BringWindowToTop(hwnd)
        user32.SetForegroundWindow(hwnd)
        if attached:
            user32.AttachThreadInput(current_thread, other_thread, False)  # noqa: FBT003
    except (AttributeError, OSError, TypeError, ValueError):
        return


def _is_modal_dialog(widget: QWidget) -> bool:
    """Return whether `widget` is a modal dialog that must not be `hide()`'d."""
    if not isinstance(widget, QDialog):
        return False
    return widget.isModal() or widget.windowModality() != Qt.WindowModality.NonModal


def _item_is_modal(item: ConcealedWindow) -> bool:
    """Return whether the concealed item was modal before fade-out.

    Args:

    - `item` (`ConcealedWindow`): Window state captured before concealment.

    Returns:

    - `bool`: `True` when the window should be treated as a modal dialog.

    """
    return item.modality != Qt.WindowModality.NonModal or _is_modal_dialog(item.widget)


def _opacity_conceal_targets(candidates: list[QWidget]) -> set[QWidget]:
    """Return Windows that must be faded instead of `hide()`'d.

    Any visible modal dialog plus every other visible top-level window: a later
    `hide()` / `show()` of a sibling (Fitness, the main window, …) can land
    above a still-living `WindowModal` box and leave it unreachable.

    """
    if any(_is_modal_dialog(widget) for widget in candidates):
        return set(candidates)
    return set()


def _pick_focus_target(widgets: list[ConcealedWindow]) -> QWidget | None:
    """Prefer the last modal dialog; otherwise the last restored visible widget.

    A `QMessageBox` can be unmapped by `setWindowModality` during conceal. It
    must still win focus so restore can `show()` it above Fitness.

    Args:

    - `widgets` (`list[ConcealedWindow]`): Concealed Windows from `hide_app_windows`.

    Returns:

    - `QWidget | None`: Window that should be activated after restore.

    """
    focus_target: QWidget | None = None
    for item in widgets:
        if item.widget.isVisible():
            focus_target = item.widget
    for item in reversed(widgets):
        if _item_is_modal(item):
            return item.widget
    return focus_target


def _restore_opacity_item(item: ConcealedWindow) -> None:
    """Restore modality, mouse handling, and opacity for one faded window.

    Args:

    - `item` (`ConcealedWindow`): Window state captured before concealment.

    """
    item.widget.setAttribute(
        Qt.WidgetAttribute.WA_TransparentForMouseEvents,
        item.transparent_for_mouse,
    )
    item.widget.setWindowModality(item.modality)
    item.widget.setWindowOpacity(item.opacity)
    if not item.widget.isVisible():
        item.widget.show()


def _schedule_foreground(widget: QWidget) -> None:
    """Pin `widget` again after Windows finishes activating the capture overlay's owner.

    Args:

    - `widget` (`QWidget`): Modal dialog that must stay above its owner.

    """

    def _pin() -> None:
        if isValid(widget) and widget.isVisible():
            _bring_to_foreground(widget)

    for delay_ms in _REPIN_MODAL_DELAYS_MS:
        QTimer.singleShot(delay_ms, _pin)


def _split_opacity_items(widgets: list[ConcealedWindow]) -> tuple[list[ConcealedWindow], list[ConcealedWindow]]:
    """Split faded Windows into owners first and modal dialogs last.

    Args:

    - `widgets` (`list[ConcealedWindow]`): Concealed Windows from `hide_app_windows`.

    Returns:

    - `tuple[list[ConcealedWindow], list[ConcealedWindow]]`: Non-modal faded
      Windows, then modal dialogs.

    """
    owners: list[ConcealedWindow] = []
    modals: list[ConcealedWindow] = []
    for item in widgets:
        if item.mode != "opacity":
            continue
        if _item_is_modal(item):
            modals.append(item)
        else:
            owners.append(item)
    return owners, modals
