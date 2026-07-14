"""Tests for quick launcher dialog layout helpers."""

import pytest
from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget

from harrix_swiss_knife.actions.quick_launcher.dialog import _layout_spacing_total


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_layout_spacing_total_without_markdown_panel(qapp: QApplication) -> None:  # noqa: ARG001
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.setSpacing(12)

    assert _layout_spacing_total(layout, split=False) == 36


def test_layout_spacing_total_with_markdown_panel(qapp: QApplication) -> None:  # noqa: ARG001
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.setSpacing(12)

    assert _layout_spacing_total(layout, split=True) == 60
