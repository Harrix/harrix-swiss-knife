"""Hide and restore application Windows during screenshot capture."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QDialog

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget

if sys.platform == "win32":
    import ctypes

HSK_SCREENSHOT_UI_PROP = "hsk_screenshot_ui"

ConcealMode = Literal["hide", "opacity"]


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

    Modality is also set to NonModal and mouse events are ignored on those
    dialogs. Note: Qt does not fully drop ApplicationModal blocking for a
    window that stays visible, so screenshot UI must still present itself as
    ApplicationModal on top (see `capture._capture_loop`).

    Returns:

    - `list[ConcealedWindow]`: Windows that were concealed and should be restored.

    """
    app = QApplication.instance()
    if app is None:
        return []

    concealed: list[ConcealedWindow] = []
    for widget in app.topLevelWidgets():
        if not widget.isVisible():
            continue
        if is_screenshot_ui(widget):
            continue
        if isinstance(widget, QDialog) and widget.isModal():
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
            concealed.append(
                ConcealedWindow(
                    widget,
                    "opacity",
                    opacity,
                    modality=modality,
                    transparent_for_mouse=was_transparent,
                )
            )
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
    user returns to Fill with AI / New Markdown without hunting the taskbar.

    """
    for item in widgets:
        if item.mode == "opacity":
            item.widget.setAttribute(
                Qt.WidgetAttribute.WA_TransparentForMouseEvents,
                item.transparent_for_mouse,
            )
            item.widget.setWindowModality(item.modality)
            item.widget.setWindowOpacity(item.opacity)
        else:
            item.widget.show()
        item.widget.raise_()

    focus_target = _pick_focus_target(widgets)
    if focus_target is not None:
        focus_target.show()
        focus_target.raise_()
        focus_target.activateWindow()
        _force_foreground(focus_target)

    QApplication.processEvents()


def _force_foreground(widget: QWidget) -> None:
    """Ask the OS to put the widget's native window in the foreground."""
    if sys.platform != "win32":
        return
    try:
        hwnd = int(widget.winId())
        if not hwnd:
            return
        user32 = ctypes.windll.user32
        # Allow this process to set the foreground window after capture UI closes.
        user32.AllowSetForegroundWindow(-1)  # ASFW_ANY
        user32.BringWindowToTop(hwnd)
        user32.SetForegroundWindow(hwnd)
    except (AttributeError, OSError, TypeError, ValueError):
        return


def _pick_focus_target(widgets: list[ConcealedWindow]) -> QWidget | None:
    """Prefer the last visible modal dialog; otherwise the last restored widget."""
    focus_target: QWidget | None = None
    for item in widgets:
        if item.widget.isVisible():
            focus_target = item.widget
    for item in reversed(widgets):
        widget = item.widget
        if widget.isVisible() and isinstance(widget, QDialog) and widget.isModal():
            return widget
    return focus_target
