"""Background translate must not touch UI after Finance window starts closing."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any, cast

import pytest
from PySide6.QtWidgets import QApplication, QMainWindow
from shiboken6 import delete, isValid

from harrix_swiss_knife.apps.finance import main as finance_main


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def _bind_clear(window: QMainWindow) -> Any:
    return finance_main.MainWindow._clear_background_transaction_translate_status.__get__(
        cast("finance_main.MainWindow", window),
        finance_main.MainWindow,
    )


def _bind_apply(window: QMainWindow) -> Any:
    return finance_main.MainWindow._apply_background_transaction_translate_response.__get__(
        cast("finance_main.MainWindow", window),
        finance_main.MainWindow,
    )


def test_clear_background_translate_status_skips_when_closing(qapp: QApplication) -> None:
    assert qapp is not None
    window = QMainWindow()
    window._is_closing = False
    status = window.statusBar()
    assert status is not None
    status.showMessage(finance_main._BACKGROUND_TX_TRANSLATE_STATUS)
    clear = _bind_clear(window)
    clear()
    assert status.currentMessage() == ""

    window._is_closing = True
    status.showMessage(finance_main._BACKGROUND_TX_TRANSLATE_STATUS)
    clear()
    assert status.currentMessage() == finance_main._BACKGROUND_TX_TRANSLATE_STATUS
    window.close()


def test_clear_and_apply_safe_after_cpp_delete(qapp: QApplication) -> None:
    assert qapp is not None
    window = QMainWindow()
    window._is_closing = False
    window.db_manager = SimpleNamespace()
    clear = _bind_clear(window)
    apply = _bind_apply(window)
    delete(window)
    assert not isValid(window)
    clear()
    apply("[]", ["Coffee"])
