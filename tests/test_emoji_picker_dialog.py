"""Tests for the shared emoji picker and finance category icon rows."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.apps.common.emoji_picker_dialog import EmojiPickerDialog
from harrix_swiss_knife.apps.common.emoji_presets import FINANCE_EMOJI_PRESETS, unique_emojis
from harrix_swiss_knife.apps.finance.category_add_dialog import CategoryAddDialog
from harrix_swiss_knife.apps.finance.category_edit_dialog import CategoryEditDialog
from harrix_swiss_knife.apps.habits.habit_emoji_picker_dialog import HabitEmojiPickerDialog
from harrix_swiss_knife.apps.habits.habit_emojis import HABIT_EMOJI_PRESETS, normalize_habit_emoji


@pytest.fixture
def qapp() -> QApplication:
    """Ensure a QApplication exists for Qt widgets."""
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_unique_emojis_keeps_first_seen_order() -> None:
    assert unique_emojis(("💰", "🍔"), ("🍔", "☕", "💰")) == ("💰", "🍔", "☕")


def test_finance_emoji_presets_include_category_and_habit_icons() -> None:
    assert "🔌" in FINANCE_EMOJI_PRESETS
    assert "💰" in FINANCE_EMOJI_PRESETS
    assert HABIT_EMOJI_PRESETS[0] in FINANCE_EMOJI_PRESETS
    assert FINANCE_EMOJI_PRESETS[0] == "💰"


def test_emoji_picker_selects_preset(qapp: QApplication) -> None:
    assert qapp is not None
    dialog = EmojiPickerDialog(presets=("🏃", "☕"), current_emoji="🏃")
    dialog._select_emoji("☕")
    assert dialog.selected_emoji() == "☕"


def test_emoji_picker_allows_empty(qapp: QApplication) -> None:
    assert qapp is not None
    dialog = EmojiPickerDialog(current_emoji="💰", presets=("💰",), allow_empty=True)
    dialog._select_emoji("")
    assert dialog.selected_emoji() == ""


def test_habit_emoji_picker_never_returns_empty(qapp: QApplication) -> None:
    assert qapp is not None
    dialog = HabitEmojiPickerDialog(current_emoji="")
    assert dialog.selected_emoji() == normalize_habit_emoji("")
    dialog._select_emoji("")
    assert dialog.selected_emoji() == normalize_habit_emoji("")


def test_category_add_dialog_returns_icon(qapp: QApplication) -> None:
    assert qapp is not None
    dialog = CategoryAddDialog()
    dialog._name_edit.setText("Cafe")
    dialog._name_local_edit.setText("Кафе")
    dialog._icon_row.set_emoji("☕")
    dialog._on_accept()
    assert dialog.get_result() == ("Cafe", 0, "☕", "Кафе")


def test_category_edit_dialog_keeps_icon(qapp: QApplication) -> None:
    assert qapp is not None
    dialog = CategoryEditDialog(
        category_data={
            "id": 7,
            "name": "Food",
            "type": 0,
            "icon": "🍔",
            "name_local": "Еда",
        }
    )
    assert dialog._icon_row.emoji() == "🍔"
    dialog._icon_row.set_emoji("🥗")
    dialog._on_save()
    result = dialog.get_result()
    assert result["action"] == "save"
    assert result["icon"] == "🥗"
    assert result["name"] == "Food"
