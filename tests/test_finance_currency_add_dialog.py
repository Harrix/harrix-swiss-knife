"""Tests for the finance currency add dialog."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.apps.finance.currency_add_dialog import CurrencyAddDialog


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


def test_currency_add_dialog_title_and_empty_result(qapp: QApplication) -> None:  # noqa: ARG001
    """New-currency dialog is titled Add Currency and has no result until saved."""
    dialog = CurrencyAddDialog()
    assert dialog.windowTitle() == "Add Currency"
    assert dialog.get_result() is None
    dialog.close()
