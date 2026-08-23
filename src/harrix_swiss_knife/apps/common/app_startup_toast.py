"""Countdown toast shown while a tracker app window is created."""

from __future__ import annotations

from harrix_swiss_knife.toast_countdown_notification import ToastCountdownNotification

DEFAULT_APP_LOADING_TITLE = "Application"


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
