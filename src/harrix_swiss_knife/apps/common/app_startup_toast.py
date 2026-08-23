"""Countdown toast shown while a tracker app window is created."""

from __future__ import annotations

import sys
import time
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any

from harrix_swiss_knife.toast_countdown_notification import ToastCountdownNotification

if TYPE_CHECKING:
    from collections.abc import Iterator

DEFAULT_APP_LOADING_TITLE = "Application"
_PUMP_INTERVAL_S = 0.2


class AppLoadingToastPumper:
    """Refresh the loading toast clock while the UI thread is busy.

    `QTimer` does not fire during `MainWindow` construction. A per-thread
    `sys.setprofile` hook calls `update_time()` and `repaint()` without
    `processEvents`, so other Qt timers cannot run re-entrantly.

    """

    def __init__(self, toast: ToastCountdownNotification, *, interval_s: float = _PUMP_INTERVAL_S) -> None:
        """Store the toast and how often to refresh the clock."""
        self._toast = toast
        self._interval_s = interval_s
        self._last = 0.0
        self._previous: Any = None
        self._active = False

    def refresh_display(self) -> None:
        """Read `QElapsedTimer` and paint the toast without processing Qt events."""
        toast = self._toast
        toast.update_time()
        toast.label.repaint()
        toast.repaint()

    def start(self) -> None:
        """Install the profile hook and paint the first clock value."""
        if self._active:
            return
        self._active = True
        self._last = 0.0
        self._previous = sys.getprofile()
        sys.setprofile(self._on_profile)
        self.refresh_display()

    def stop(self) -> None:
        """Restore the previous profile hook and paint the final clock value."""
        if not self._active:
            return
        self._active = False
        sys.setprofile(self._previous)
        self._previous = None
        self.refresh_display()

    def _on_profile(self, _frame: object, event: str, _arg: object) -> object:
        if event == "call":
            now = time.monotonic()
            if now - self._last >= self._interval_s:
                self._last = now
                self.refresh_display()
        return self._on_profile


def app_loading_title(source: object) -> str:
    """Return a short app name for the loading toast.

    Prefers `about_app_name` (window class), then `title` (launcher action).

    """
    about = getattr(source, "about_app_name", None)
    if isinstance(about, str):
        text = about.strip()
        if text:
            return text
    title = getattr(source, "title", None)
    if isinstance(title, str):
        text = title.strip()
        if text:
            return text
    return DEFAULT_APP_LOADING_TITLE


@contextmanager
def app_loading_toast_scope(app_title: str) -> Iterator[ToastCountdownNotification]:
    """Show a loading toast and keep its elapsed clock updating until exit."""
    toast = start_app_loading_toast(app_title)
    pumper = AppLoadingToastPumper(toast)
    pumper.start()
    try:
        yield toast
    finally:
        pumper.stop()
        stop_app_loading_toast(toast)


def start_app_loading_toast(app_title: str) -> ToastCountdownNotification:
    """Show a countdown toast for `Loading {app_title}…`."""
    text = app_title.strip() or DEFAULT_APP_LOADING_TITLE
    toast = ToastCountdownNotification(f"Loading {text}…")
    toast.start_countdown()
    toast.pump_events()
    return toast


def stop_app_loading_toast(toast: ToastCountdownNotification | None) -> None:
    """Refresh elapsed time once, then close the loading toast."""
    if toast is None:
        return
    toast.update_time()
    toast.pump_events()
    toast.close()
