"""Tests for the app-loading countdown toast."""

from __future__ import annotations

import time

from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.app_startup import TRAY_LOADING_TITLE
from harrix_swiss_knife.apps.common.app_startup_toast import (
    DEFAULT_APP_LOADING_TITLE,
    AppLoadingToastPumper,
    app_loading_title,
    start_app_loading_toast,
    stop_app_loading_toast,
)
from harrix_swiss_knife.toast_countdown_notification import ToastCountdownNotification, format_elapsed_clock


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


def test_tray_startup_toast_uses_app_title() -> None:
    app = QApplication.instance()
    if app is None:
        QApplication([])

    toast = start_app_loading_toast(TRAY_LOADING_TITLE)
    assert toast.message == "Loading Harrix Swiss Knife…"
    assert toast.isVisible()
    stop_app_loading_toast(toast)


def test_loading_toast_pumper_updates_clock_without_qt_timers() -> None:
    """The clock advances during busy Python work even if QTimer cannot fire."""
    app = QApplication.instance()
    if app is None:
        QApplication([])

    toast = start_app_loading_toast("Fitness tracker")
    toast.timer.stop()
    pumper = AppLoadingToastPumper(toast, interval_s=0.05)
    pumper.start()
    try:
        deadline = time.monotonic() + 1.15

        def work() -> None:
            return None

        while time.monotonic() < deadline:
            work()
    finally:
        pumper.stop()
    assert toast.elapsed_seconds >= 1
    assert format_elapsed_clock(toast.elapsed_seconds) in toast.label.text()
    stop_app_loading_toast(toast)
