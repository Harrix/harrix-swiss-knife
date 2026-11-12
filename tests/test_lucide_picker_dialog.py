"""Tests for the shared Lucide picker dialog."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.apps.common.lucide_icon_ai import parse_lucide_icon_response
from harrix_swiss_knife.apps.common.lucide_picker_dialog import LucideChoiceRow, LucidePickerDialog
from harrix_swiss_knife.qt_lucide_icon import list_lucide_icon_names


@pytest.fixture
def qapp() -> QApplication:
    """Ensure a QApplication exists for the dialog."""
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_list_lucide_icon_names_includes_utensils() -> None:
    names = list_lucide_icon_names()
    assert "utensils" in names
    assert names == tuple(sorted(names))


def test_lucide_picker_selects_name(qapp: QApplication) -> None:  # noqa: ARG001
    dialog = LucidePickerDialog(None, current_name="car", presets=("car", "utensils"), allow_empty=True)
    assert dialog.selected_name() == "car"
    dialog._select_name("utensils")
    assert dialog.selected_name() == "utensils"
    dialog._select_name("")
    assert dialog.selected_name() == ""
    dialog.close()


def test_lucide_choice_row_auto_label(qapp: QApplication) -> None:  # noqa: ARG001
    row = LucideChoiceRow(None, current_name="", presets=("utensils",), allow_empty=True)
    assert row.lucide_name() == ""
    assert "Auto" in row._label.text()
    row.set_lucide_name("utensils")
    assert row.lucide_name() == "utensils"
    assert row._label.text() == "utensils"


def test_parse_lucide_icon_response_keeps_valid_unique() -> None:
    known = ("car", "shopping-cart", "sparkles", "utensils")
    assert parse_lucide_icon_response("utensils\ncar\nutensils", known_names=known) == ["utensils", "car"]
    assert parse_lucide_icon_response("```\n- shopping-cart\n`sparkles`\n", known_names=known) == [
        "shopping-cart",
        "sparkles",
    ]
    assert parse_lucide_icon_response("not-a-real-icon\ncar", known_names=known) == ["car"]
    assert parse_lucide_icon_response("no icons here", known_names=known) == []


def test_lucide_picker_ai_button_uses_suggest_query(qapp: QApplication) -> None:  # noqa: ARG001
    dialog = LucidePickerDialog(
        None,
        current_name="",
        presets=("car",),
        allow_empty=True,
        suggest_query="Coffee shops",
    )
    assert dialog._ai_query_text() == "Coffee shops"
    assert dialog._ai_button.isEnabled()
    dialog._search.setText("cart")
    assert dialog._ai_query_text() == "cart"
    dialog.close()
