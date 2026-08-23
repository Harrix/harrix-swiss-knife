"""Tests for shared app window helpers."""

from __future__ import annotations

import pytest
from PySide6.QtCore import QRect, Qt
from PySide6.QtWidgets import QApplication, QMenuBar, QWidget

from harrix_swiss_knife.apps.common.qt_main_window import (
    compute_app_window_geometry,
    resolve_window_menu_bar,
    window_frame_margins,
)
from harrix_swiss_knife.qt_emoji_icon import apply_leading_emoji_icons


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_compute_app_window_geometry_centers_on_ultrawide() -> None:
    """A 1920-wide window sits in the middle of a wider work area."""
    rect = compute_app_window_geometry(QRect(0, 0, 3440, 1440))
    assert rect == QRect(760, 0, 1920, 1440)


def test_compute_app_window_geometry_fits_scaled_1080p() -> None:
    """A 125% 1080p work area must not request a 1920 window at a negative X."""
    rect = compute_app_window_geometry(QRect(0, 48, 1536, 816))
    assert rect == QRect(0, 48, 1536, 816)


def test_compute_app_window_geometry_uses_available_origin() -> None:
    """Centering keeps the work-area origin of a secondary screen."""
    rect = compute_app_window_geometry(QRect(1920, 80, 3440, 1360))
    assert rect == QRect(1920 + 760, 80, 1920, 1360)


def test_compute_app_window_geometry_maximizes_on_standard_1080p() -> None:
    """A standard 1920-wide work area should maximize instead of floating."""
    assert compute_app_window_geometry(QRect(0, 0, 1920, 1032)) is None


def test_compute_app_window_geometry_reserves_title_bar() -> None:
    """Client rect leaves room so Close / Maximize stay inside the work area."""
    rect = compute_app_window_geometry(QRect(0, 0, 3440, 1440), frame_top=32)
    assert rect == QRect(760, 32, 1920, 1408)


def test_compute_app_window_geometry_reserves_title_bar_on_scaled_work_area() -> None:
    """A work area that already starts below a top taskbar still reserves the caption."""
    rect = compute_app_window_geometry(QRect(0, 48, 1536, 816), frame_top=32)
    assert rect == QRect(0, 80, 1536, 784)


def test_window_frame_margins_are_zero_when_frameless(qapp: QApplication) -> None:  # noqa: ARG001
    widget = QWidget()
    widget.setWindowFlags(Qt.WindowType.FramelessWindowHint)
    assert window_frame_margins(widget) == (0, 0, 0, 0)


def test_window_frame_margins_reserve_title_bar_for_window(qapp: QApplication) -> None:  # noqa: ARG001
    widget = QWidget()
    widget.setWindowFlags(Qt.WindowType.Window)
    _left, top, _right, _bottom = window_frame_margins(widget)
    assert top >= 24


def test_resolve_window_menu_bar_when_attribute_shadows_method(qapp: QApplication) -> None:
    """UI files assign `menuBar` to a widget, so `window.menuBar()` must not be called."""
    assert qapp is not None
    window = QWidget()
    bar = QMenuBar(window)
    window.menuBar = bar
    action = bar.addAction("🚪 Exit")
    resolved = resolve_window_menu_bar(window)
    assert resolved is bar
    apply_leading_emoji_icons(resolved)
    assert action.text() == "Exit"
    assert not action.icon().isNull()
