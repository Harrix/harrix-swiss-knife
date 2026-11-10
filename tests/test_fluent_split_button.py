"""Tests for FluentSplitButton chevron chrome."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication, QMenu

from harrix_swiss_knife.fluent.widgets.buttons import FluentSplitButton


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_fluent_split_button_shows_lucide_menu_arrow(qapp: QApplication) -> None:  # noqa: ARG001
    menu = QMenu()
    menu.addAction("One")
    button = FluentSplitButton("Recognize", menu=menu)
    button.refresh_theme()
    sheet = button.styleSheet()
    assert "QToolButton::menu-arrow" in sheet
    assert "image: none" not in sheet
    assert "image: url(" in sheet
    assert "subcontrol-origin: padding" in sheet
    assert f"padding-right: {FluentSplitButton._MENU_BUTTON_WIDTH}px" in sheet
    button.close()


def test_fluent_split_button_size_hint_reserves_chevron_gutter(qapp: QApplication) -> None:  # noqa: ARG001
    plain = FluentSplitButton("Recognize")
    menu = QMenu()
    menu.addAction("One")
    split = FluentSplitButton("Recognize", menu=menu)
    split.refresh_theme()
    assert split.sizeHint().width() >= plain.sizeHint().width() + FluentSplitButton._MENU_BUTTON_WIDTH
    plain.close()
    split.close()


def test_fluent_split_button_without_menu_hides_arrow(qapp: QApplication) -> None:  # noqa: ARG001
    button = FluentSplitButton("Plain")
    button.refresh_theme()
    sheet = button.styleSheet()
    assert "QToolButton::menu-arrow { image: none; width: 0px; }" in sheet
    button.close()
