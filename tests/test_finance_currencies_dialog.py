"""Tests for the finance currencies catalog dialog."""

from __future__ import annotations

from typing import Any, cast

import pytest
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.apps.finance.currencies_dialog import CurrenciesDialog


class _FakeFinanceDb:
    """Minimal stand-in for `DatabaseManager` currency reads."""

    def get_all_currencies(self) -> list[list[Any]]:
        return [[1, "USD", "US Dollar", "$"], [2, "EUR", "Euro", "€"]]

    def get_default_currency(self) -> str:
        return "EUR"


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


def test_currencies_dialog_title_and_default_combo(qapp: QApplication) -> None:  # noqa: ARG001
    """Currencies dialog is titled Currencies and selects the default code."""
    dialog = CurrenciesDialog(None, cast("Any", _FakeFinanceDb()))
    assert dialog.windowTitle() == "Currencies"
    assert dialog.catalog_changed is False
    assert dialog.default_currency_changed is False
    model = dialog.table.model()
    assert model is not None
    assert model.rowCount() == 2
    assert model.columnCount() == 3
    assert dialog.combo_default_currency.count() == 2
    assert dialog.combo_default_currency.currentText() == "EUR"
    dialog.close()
