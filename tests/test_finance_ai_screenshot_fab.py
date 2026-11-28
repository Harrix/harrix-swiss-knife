"""Tests for Finance floating Add-with-AI screenshot control."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from PySide6.QtCore import QPoint, QRect
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.apps.finance.ai_screenshot_fab import FinanceAiScreenshotFab
from harrix_swiss_knife.apps.finance.ai_screenshot_fab_settings import (
    clamp_fab_top_left,
    default_fab_top_left,
    resolve_fab_top_left,
)


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_finance_ai_screenshot_fab_clamps_off_screen_position() -> None:
    """Saved 4K coordinates stay inside a small available geometry."""
    available = QRect(0, 0, 1024, 768)
    size = 48
    point = clamp_fab_top_left(3500, 2000, size=size, available=available)
    assert available.left() <= point.x() <= available.right() - size + 1
    assert available.top() <= point.y() <= available.bottom() - size + 1


def test_finance_ai_screenshot_fab_hides_when_disabled(qapp: QApplication) -> None:
    """show_for_finance does nothing visible when the pref is off."""
    assert qapp is not None
    fab = FinanceAiScreenshotFab(MagicMock())
    try:
        with patch(
            "harrix_swiss_knife.apps.finance.ai_screenshot_fab.load_fab_enabled",
            return_value=False,
        ):
            fab.show_for_finance()
        assert not fab.isVisible()
    finally:
        fab.close()
        fab.deleteLater()


def test_finance_ai_screenshot_fab_places_on_right_edge(qapp: QApplication) -> None:
    """FAB sits near the right edge and can be shown/hidden for Finance."""
    assert qapp is not None
    clicked = MagicMock()
    fab = FinanceAiScreenshotFab(clicked)
    try:
        fab.place_on_screen(use_default=True)
        screen = qapp.primaryScreen()
        assert screen is not None
        geo = screen.availableGeometry()
        assert fab.x() >= geo.right() - fab.width() - 40
        with patch(
            "harrix_swiss_knife.apps.finance.ai_screenshot_fab.load_fab_enabled",
            return_value=True,
        ):
            fab.show_for_finance()
        assert fab.isVisible()
        fab.hide_for_finance()
        assert not fab.isVisible()
    finally:
        fab.close()
        fab.deleteLater()


def test_finance_ai_screenshot_fab_resolve_uses_default_when_unset() -> None:
    """Unset position resolves to the right-edge default."""
    available = QRect(0, 0, 1920, 1080)
    with patch(
        "harrix_swiss_knife.apps.finance.ai_screenshot_fab_settings.load_fab_position",
        return_value=None,
    ):
        point = resolve_fab_top_left(size=48, available=available)
    expected = default_fab_top_left(size=48, available=available)
    assert point == expected


def test_finance_ai_screenshot_fab_restore_default_position(qapp: QApplication) -> None:
    """Restore default clears the custom spot and re-pins to the right edge."""
    assert qapp is not None
    fab = FinanceAiScreenshotFab(MagicMock())
    try:
        screen = qapp.primaryScreen()
        assert screen is not None
        geo = screen.availableGeometry()
        fab.move(geo.left() + 40, geo.top() + 40)
        with patch(
            "harrix_swiss_knife.apps.finance.ai_screenshot_fab.clear_fab_position",
        ) as clear_mock:
            fab.restore_default_position()
        clear_mock.assert_called_once()
        assert fab.x() >= geo.right() - fab.width() - 40
        assert isinstance(fab.pos(), QPoint)
    finally:
        fab.close()
        fab.deleteLater()
