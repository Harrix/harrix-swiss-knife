"""Tests for comma/period decimal input in QDoubleSpinBox."""

from __future__ import annotations

import pytest
from PySide6.QtCore import QLocale, Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QDoubleSpinBox

from harrix_swiss_knife.qt_flexible_decimal import (
    install_flexible_decimal_separators,
    normalize_decimal_text,
    spinbox_decimal_point,
)


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    install_flexible_decimal_separators(app)
    return app


def test_normalize_decimal_text_swaps_lone_separator() -> None:
    assert normalize_decimal_text("1,5", ".") == "1.5"
    assert normalize_decimal_text("1.5", ",") == "1,5"
    assert normalize_decimal_text("1.5", ".") == "1.5"
    assert normalize_decimal_text("1,234.56", ".") == "1,234.56"


def _type_into_spin(spin: QDoubleSpinBox, text: str) -> None:
    line = spin.lineEdit()
    assert line is not None
    spin.show()
    line.setFocus()
    line.selectAll()
    QTest.keyClicks(line, text)
    QTest.keyClick(line, Qt.Key.Key_Enter)


def test_comma_is_accepted_when_locale_uses_dot(qapp: QApplication) -> None:  # noqa: ARG001
    spin = QDoubleSpinBox()
    spin.setLocale(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates))
    spin.setDecimals(2)
    spin.setRange(0, 100)
    spin.setValue(0)
    _type_into_spin(spin, "1,5")
    assert spin.value() == pytest.approx(1.5)
    assert spinbox_decimal_point(spin) == "."


def test_period_is_accepted_when_locale_uses_comma(qapp: QApplication) -> None:  # noqa: ARG001
    spin = QDoubleSpinBox()
    spin.setLocale(QLocale(QLocale.Language.Russian, QLocale.Country.Russia))
    spin.setDecimals(2)
    spin.setRange(0, 100)
    spin.setValue(0)
    _type_into_spin(spin, "1.5")
    assert spin.value() == pytest.approx(1.5)
    assert spinbox_decimal_point(spin) == ","
