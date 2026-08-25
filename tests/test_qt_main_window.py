"""Tests for shared app window helpers."""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from PySide6.QtCore import QRect, Qt
from PySide6.QtWidgets import QApplication, QMenuBar, QWidget

from harrix_swiss_knife.apps.common.qt_main_window import (
    apply_app_window_size_and_position,
    compute_app_window_geometry,
    compute_maximize_pin_geometry,
    compute_restore_window_geometry,
    inset_restore_frame_rect,
    resolve_window_menu_bar,
    window_frame_escapes_work_area,
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


def test_apply_pins_hidden_window_to_secondary_screen_before_maximize(
    qapp: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Maximize is deferred until show; geometry is pinned to the target screen."""
    fake_screen = SimpleNamespace(availableGeometry=lambda: QRect(1920, 0, 1920, 1080))
    monkeypatch.setattr(
        "harrix_swiss_knife.apps.common.qt_main_window.QGuiApplication.screenAt",
        lambda _pos: fake_screen,
    )
    widget = QWidget()
    widget.setWindowFlags(Qt.WindowType.Window)
    apply_app_window_size_and_position(widget)
    assert not widget.isVisible()
    assert widget.geometry() == QRect(1920, 0, 1920, 1080)
    assert not widget.windowState() & Qt.WindowState.WindowMaximized
    widget.show()
    qapp.processEvents()
    qapp.processEvents()
    assert widget.windowState() & Qt.WindowState.WindowMaximized
    widget.close()


def test_apply_centers_frameless_window_on_secondary_ultrawide(
    qapp: QApplication,  # noqa: ARG001
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ultrawide secondary screens keep a centered 1920-wide window."""
    fake_screen = SimpleNamespace(availableGeometry=lambda: QRect(1920, 80, 3440, 1360))
    monkeypatch.setattr(
        "harrix_swiss_knife.apps.common.qt_main_window.QGuiApplication.screenAt",
        lambda _pos: fake_screen,
    )
    widget = QWidget()
    widget.setWindowFlags(Qt.WindowType.FramelessWindowHint)
    apply_app_window_size_and_position(widget)
    assert widget.geometry() == QRect(1920 + 760, 80, 1920, 1360)
    assert not widget.windowState() & Qt.WindowState.WindowMaximized
    widget.close()


def test_compute_maximize_pin_geometry_uses_work_area() -> None:
    """Maximize pin keeps the full work area so the window has no side gaps."""
    available = QRect(0, 0, 3840, 2064)
    assert (
        compute_maximize_pin_geometry(
            available,
            frame_left=13,
            frame_top=58,
            frame_right=13,
            frame_bottom=13,
        )
        == available
    )


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


def test_compute_restore_window_geometry_insets_standard_1080p() -> None:
    """Restore from maximize keeps the title bar inside a standard work area."""
    rect = compute_restore_window_geometry(
        QRect(0, 0, 1920, 1032),
        frame_left=8,
        frame_top=32,
        frame_right=8,
        frame_bottom=8,
    )
    assert rect == QRect(8, 32, 1904, 992)


def test_compute_restore_window_geometry_matches_centered_ultrawide() -> None:
    """Ultrawide restore uses the same centered 1920-wide client as placement."""
    available = QRect(1920, 80, 3440, 1360)
    assert compute_restore_window_geometry(
        available,
        frame_top=32,
    ) == compute_app_window_geometry(available, frame_top=32)


def test_window_frame_escapes_work_area_when_title_bar_is_above() -> None:
    """A restore pin that uses the work area as the client sits above the screen."""
    available = QRect(0, 0, 1920, 1032)
    frame = QRect(-8, -32, 1936, 1072)
    assert window_frame_escapes_work_area(frame, available)
    assert not window_frame_escapes_work_area(QRect(0, 0, 1920, 1032), available)
    assert not window_frame_escapes_work_area(QRect(-8, -8, 1936, 1048), available)


def test_inset_restore_frame_rect_shifts_caption_into_work_area() -> None:
    """Win32 restore frame is inset by the title bar and borders."""
    assert inset_restore_frame_rect(0, -32, 1920, 1040, frame_x=8, title=32, frame_y=8) == (8, 0, 1912, 1032)
    assert inset_restore_frame_rect(0, 0, 20, 20, frame_x=8, title=32, frame_y=8) is None


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
