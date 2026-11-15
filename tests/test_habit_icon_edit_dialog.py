"""Tests for habit table icon (emoji + Lucide) editing."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.apps.habits.habit_icon_edit_dialog import HabitIconEditDialog


@pytest.fixture
def qapp() -> QApplication:
    """Ensure a QApplication exists for dialog widgets."""
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_habit_icon_edit_dialog_returns_emoji_and_lucide(qapp: QApplication) -> None:  # noqa: ARG001
    dialog = HabitIconEditDialog(
        emoji="🚶",
        icon_lucide="footprints",
        habit_name="Walk",
    )
    assert dialog.selected_emoji() == "🚶"
    assert dialog.selected_icon_lucide() == "footprints"
    dialog._lucide_row.set_lucide_name("bike")
    assert dialog.selected_icon_lucide() == "bike"
