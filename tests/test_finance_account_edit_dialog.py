"""Tests for the finance account add/edit dialog."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.apps.finance.account_edit_dialog import AccountEditDialog


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


def test_account_edit_dialog_add_mode_hides_delete(qapp: QApplication) -> None:  # noqa: ARG001
    """New-account dialog is titled Add Account and has no Delete button."""
    dialog = AccountEditDialog(currencies=["RUB", "USD"], default_currency_code="USD")
    assert dialog.windowTitle() == "Add Account"
    assert dialog.delete_button.isHidden()
    assert dialog.currency_combo.currentText() == "USD"
    dialog.close()


def test_account_edit_dialog_edit_mode_shows_delete(qapp: QApplication) -> None:  # noqa: ARG001
    """Existing-account dialog keeps Delete and the Edit Account title."""
    dialog = AccountEditDialog(
        account_data={
            "id": 1,
            "name": "Cash",
            "balance": 10.0,
            "currency_code": "RUB",
            "is_liquid": True,
            "is_cash": True,
        },
        currencies=["RUB", "USD"],
    )
    assert dialog.windowTitle() == "Edit Account"
    assert not dialog.delete_button.isHidden()
    dialog.close()
