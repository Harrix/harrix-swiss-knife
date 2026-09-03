"""Tests for the finance standard-item add/edit dialog."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.apps.finance.standard_items_dialog import _StandardItemEditDialog


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


def test_standard_item_edit_dialog_capitalizes_names(qapp: QApplication) -> None:  # noqa: ARG001
    """Add Standard Item capitalizes Name and English."""
    dialog = _StandardItemEditDialog(None, [[1, "Food", 0, "🍔"]])
    dialog.name_edit.setText("кофе")
    dialog.name_en_edit.setText("coffee")
    dialog._on_save()
    result = dialog.get_result()
    assert result["name"] == "Кофе"
    assert result["name_en"] == "Coffee"
    dialog.close()
