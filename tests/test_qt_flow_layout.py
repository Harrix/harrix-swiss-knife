"""Tests for FlowLayout wrapping."""

from __future__ import annotations

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QPushButton, QWidget

from harrix_swiss_knife.qt_flow_layout import FlowLayout


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_flow_layout_wraps_to_second_row(qapp: QApplication) -> None:
    host = QWidget()
    layout = FlowLayout(host, h_spacing=4, v_spacing=4)
    buttons = [QPushButton(f"Button {index}") for index in range(4)]
    for button in buttons:
        layout.addWidget(button)
    host.resize(220, 200)
    host.show()
    qapp.processEvents()
    layout.setGeometry(host.rect())
    qapp.processEvents()
    tops = {button.geometry().top() for button in buttons}
    assert len(tops) >= 2
    for button in buttons:
        assert button.width() >= button.sizeHint().width() - 2
    host.close()


def test_flow_layout_aligns_rows_to_the_right(qapp: QApplication) -> None:
    host = QWidget()
    layout = FlowLayout(host, h_spacing=4, v_spacing=4, alignment=Qt.AlignmentFlag.AlignRight)
    buttons = [QPushButton(f"Button {index}") for index in range(3)]
    for button in buttons:
        layout.addWidget(button)
    host.resize(500, 120)
    host.show()
    qapp.processEvents()
    layout.setGeometry(host.rect())
    qapp.processEvents()
    left_gap = min(button.geometry().left() for button in buttons)
    right_gap = host.width() - 1 - max(button.geometry().right() for button in buttons)
    assert left_gap > right_gap
    assert left_gap > 40
    host.close()
