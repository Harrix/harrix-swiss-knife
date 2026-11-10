"""Tests for Fluent QDateEdit chrome fitting yyyy-MM-dd."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication, QDateEdit, QWidget

from harrix_swiss_knife.fluent.app_chrome import install_fluent_app_window
from harrix_swiss_knife.fluent.style import date_edit_qss
from harrix_swiss_knife.fluent.theme import FluentTheme, palette_for
from harrix_swiss_knife.fluent.tokens import DATE_EDIT_MIN_WIDTH


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_date_edit_qss_reserves_chevron_gutter(qapp: QApplication) -> None:  # noqa: ARG001
    FluentTheme.instance()
    sheet = date_edit_qss(palette_for(QDateEdit()))
    assert "padding-right: 24px" in sheet
    assert "QDateEdit::drop-down" in sheet
    assert "width: 24px" in sheet


def test_fluent_chrome_enforces_date_edit_min_width(qapp: QApplication) -> None:  # noqa: ARG001
    FluentTheme.instance()
    host = QWidget()
    date_edit = QDateEdit(host)
    date_edit.setCalendarPopup(True)
    date_edit.setDisplayFormat("yyyy-MM-dd")
    date_edit.setMinimumWidth(100)
    install_fluent_app_window(host)
    assert date_edit.minimumWidth() >= DATE_EDIT_MIN_WIDTH
    assert "padding-right: 24px" in date_edit.styleSheet()
    host.close()
