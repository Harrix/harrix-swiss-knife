"""Tests for the app-loading countdown toast."""

from __future__ import annotations

from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.apps.common.app_startup_toast import (
    DEFAULT_APP_LOADING_TITLE,
    app_loading_title,
    start_app_loading_toast,
    stop_app_loading_toast,
)
from harrix_swiss_knife.toast_countdown_notification import ToastCountdownNotification


def test_app_loading_title_uses_about_app_name_then_title() -> None:
    """Window classes expose `about_app_name`; launchers expose `title`."""

    class Window:
        about_app_name = "Fitness tracker"

    class Launcher:
        title = "Habit tracker"

    assert app_loading_title(Window) == "Fitness tracker"
    assert app_loading_title(Launcher()) == "Habit tracker"
    assert app_loading_title(object()) == DEFAULT_APP_LOADING_TITLE


def test_start_and_stop_app_loading_toast() -> None:
    """The toast shows a loading message and can be closed."""
    app = QApplication.instance()
    if app is None:
        QApplication([])

    toast = start_app_loading_toast("Fitness tracker")
    assert isinstance(toast, ToastCountdownNotification)
    assert toast.message == "Loading Fitness tracker…"
    assert toast.isVisible()
    stop_app_loading_toast(toast)
    assert not toast.isVisible()
    stop_app_loading_toast(None)
