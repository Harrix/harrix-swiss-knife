"""Tests for the read-only checkbox table delegate."""

from __future__ import annotations

from PySide6.QtCore import QLocale
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.apps.common.delegates.checkbox_display_delegate import (
    CheckboxDisplayDelegate,
    is_checkbox_cell_checked,
)


def _qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_is_checkbox_cell_checked() -> None:
    assert is_checkbox_cell_checked(1)
    assert is_checkbox_cell_checked("1")
    assert is_checkbox_cell_checked("Yes")
    assert is_checkbox_cell_checked("true")
    assert not is_checkbox_cell_checked(0)
    assert not is_checkbox_cell_checked("0")
    assert not is_checkbox_cell_checked("")
    assert not is_checkbox_cell_checked(None)
    assert not is_checkbox_cell_checked("no")


def test_checkbox_display_delegate_hides_raw_values() -> None:
    assert _qapp() is not None
    delegate = CheckboxDisplayDelegate()
    locale = QLocale()
    assert delegate.displayText("1", locale) == ""
    assert delegate.displayText("0", locale) == ""
