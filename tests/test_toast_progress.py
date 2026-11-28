"""Tests for progress toast notification."""

from __future__ import annotations

import pytest
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.fluent.theme import FluentTheme, ThemeMode, css
from harrix_swiss_knife.fluent.tokens import RADIUS_OVERLAY
from harrix_swiss_knife.qt_lucide_icon import create_lucide_icon
from harrix_swiss_knife.toast_notification_base import TOAST_RADIUS_COMPACT, TOAST_RADIUS_DEFAULT
from harrix_swiss_knife.toast_progress_notification import ToastProgressNotification


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_progress_chunk_follows_theme_accent(qapp: QApplication) -> None:  # noqa: ARG001
    theme = FluentTheme.instance()
    previous = theme.mode()
    theme.set_mode(ThemeMode.LIGHT, persist=False)
    toast = ToastProgressNotification("Working…", total=4)
    try:
        light = css(theme.palette().accent)
        assert light in toast.progress_bar.styleSheet()
        assert "90, 170, 255" not in toast.progress_bar.styleSheet()
        assert f"border-bottom-left-radius: {RADIUS_OVERLAY}px" in toast._progress_container.styleSheet()
        theme.set_mode(ThemeMode.DARK, persist=False)
        dark = css(theme.palette().accent)
        assert dark in toast.progress_bar.styleSheet()
        assert light not in toast.progress_bar.styleSheet()
    finally:
        toast.close()
        theme.set_mode(previous, persist=False)


def test_progress_toast_cancel_emits_once(qapp: QApplication) -> None:  # noqa: ARG001
    toast = ToastProgressNotification("Opening folder…", cancellable=True)
    cancelled: list[int] = []
    toast.cancel_requested.connect(lambda: cancelled.append(1))
    toast.close()
    toast.close()
    assert cancelled == [1]


def test_progress_toast_cancel_hint_uses_smaller_font(qapp: QApplication) -> None:  # noqa: ARG001
    toast = ToastProgressNotification("Opening folder…", cancellable=True)
    toast._refresh_label_text()
    html = toast.label.text()
    assert "Press Esc to cancel" in html
    assert "font-size: 10pt" in html
    assert "font-weight: normal" in html
    toast.close()


def test_progress_toast_detail_line(qapp: QApplication) -> None:  # noqa: ARG001
    toast = ToastProgressNotification("Syncing…", total=4)
    assert toast.detail_label.isHidden()
    toast.set_detail("English: TickTick Done 2026-08-01")
    assert not toast.detail_label.isHidden()
    assert toast.detail_label.text() == "English: TickTick Done 2026-08-01"
    toast.set_detail("")
    assert toast.detail_label.isHidden()
    toast.close()


def test_progress_toast_updates_bar(qapp: QApplication) -> None:  # noqa: ARG001
    toast = ToastProgressNotification("Rendering…", total=10)
    assert toast.total == 10
    assert toast.completed_count == 0
    assert toast.progress_bar.maximum() == 10
    assert toast.progress_bar.value() == 0

    toast.set_progress(4)
    assert toast.completed_count == 4
    assert toast.progress_bar.value() == 4

    toast.set_progress(12)
    assert toast.completed_count == 10
    assert toast.progress_bar.value() == 10

    toast.set_progress(3, total=20)
    assert toast.total == 20
    assert toast.completed_count == 3
    assert toast.progress_bar.maximum() == 20
    toast.close()


def test_progress_toast_zero_total_is_indeterminate(qapp: QApplication) -> None:  # noqa: ARG001
    toast = ToastProgressNotification("Working…", total=0)
    assert toast.progress_bar.minimum() == 0
    assert toast.progress_bar.maximum() == 0
    toast.set_progress(5)
    assert toast.completed_count == 5
    toast.close()


def test_toast_action_icons_are_lucide(qapp: QApplication) -> None:  # noqa: ARG001
    from harrix_swiss_knife.toast_notification_base import (  # noqa: PLC0415
        COMPACT_ACTION_BUTTON_SIDE,
        DEFAULT_ACTION_BUTTON_SIDE,
        action_button_icon_side,
    )

    white = QColor(255, 255, 255)
    default_side = action_button_icon_side(DEFAULT_ACTION_BUTTON_SIDE)
    compact_side = action_button_icon_side(COMPACT_ACTION_BUTTON_SIDE)
    toast = ToastProgressNotification("Working…", cancellable=True)
    assert toast._collapse_button.icon().cacheKey() == create_lucide_icon("minus", default_side, color=white).cacheKey()
    assert toast._close_button.icon().cacheKey() == create_lucide_icon("x", default_side, color=white).cacheKey()
    toast.set_pinned(pinned=True)
    assert (
        toast._collapse_button.icon().cacheKey() == create_lucide_icon("maximize", compact_side, color=white).cacheKey()
    )
    assert toast._close_button.icon().cacheKey() == create_lucide_icon("x", compact_side, color=white).cacheKey()
    toast.close()


def test_toast_plate_radius_matches_overlay() -> None:
    assert TOAST_RADIUS_DEFAULT == RADIUS_OVERLAY == 8
    assert TOAST_RADIUS_COMPACT == RADIUS_OVERLAY
