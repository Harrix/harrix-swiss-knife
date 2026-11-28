"""Tests for Finance floating Add-with-AI screenshot control."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.apps.finance.ai_screenshot_fab import FinanceAiScreenshotFab


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_finance_ai_screenshot_fab_places_on_right_edge(qapp: QApplication) -> None:
    """FAB sits near the right edge and can be shown/hidden for Finance."""
    assert qapp is not None
    clicked = MagicMock()
    fab = FinanceAiScreenshotFab(clicked)
    try:
        fab.place_on_screen()
        screen = qapp.primaryScreen()
        assert screen is not None
        geo = screen.availableGeometry()
        assert fab.x() >= geo.right() - fab.width() - 40
        fab.show_for_finance()
        assert fab.isVisible()
        fab.hide_for_finance()
        assert not fab.isVisible()
    finally:
        fab.close()
        fab.deleteLater()
