"""Fluent list views keep readable item text in dark theme."""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QApplication, QLabel, QListView, QWidget

from harrix_swiss_knife.apps.fitness.fitness_entry_chrome import _polish_exercise_list
from harrix_swiss_knife.apps.food.food_entry_chrome import _polish_items_list
from harrix_swiss_knife.fluent.app_chrome import install_fluent_app_window, style_fluent_item_view
from harrix_swiss_knife.fluent.theme import FluentTheme, ThemeMode, enable_fluent_theme, mix


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_style_fluent_item_view_keeps_light_text_in_dark_theme(qapp: QApplication) -> None:
    assert qapp is not None
    theme = FluentTheme.instance()
    previous = theme.mode()
    theme.set_mode(ThemeMode.DARK, persist=False)
    try:
        host = QWidget()
        view = QListView(host)
        view.setObjectName("list_chart_categories")
        install_fluent_app_window(host)
        # Layout chrome used to clear the sheet and leave system black ink.
        view.setStyleSheet("")
        style_fluent_item_view(view)
        text = view.palette().color(QPalette.ColorRole.Text)
        expected = mix(theme.palette().window_bg, theme.palette().text_primary)
        assert text.lightness() > 180
        assert text.name() == expected.name()
        assert "color:" in view.styleSheet().lower()
        host.close()
    finally:
        theme.set_mode(previous, persist=False)


def test_fitness_exercise_list_polish_replaces_white_sheet(qapp: QApplication) -> None:
    assert qapp is not None
    theme = FluentTheme.instance()
    previous = theme.mode()
    theme.set_mode(ThemeMode.DARK, persist=False)
    host = QWidget()
    enable_fluent_theme(host)
    try:
        view = QListView(host)
        view.setObjectName("listView_exercises")
        view.setStyleSheet("QListView { background-color: white; }")
        _polish_exercise_list(SimpleNamespace(listView_exercises=view, label_exercises_list=None))
        sheet = view.styleSheet().casefold()
        assert "background-color: white" not in sheet
        assert "color:" in sheet
        assert view.palette().color(QPalette.ColorRole.Text).lightness() > 180
    finally:
        theme.set_mode(previous, persist=False)
        host.close()


def test_food_items_list_polish_replaces_white_sheet(qapp: QApplication) -> None:
    assert qapp is not None
    theme = FluentTheme.instance()
    previous = theme.mode()
    theme.set_mode(ThemeMode.DARK, persist=False)
    host = QWidget()
    enable_fluent_theme(host)
    try:
        view = QListView(host)
        view.setObjectName("listView_food_items")
        view.setStyleSheet("QListView { background-color: white; }")
        _polish_items_list(SimpleNamespace(listView_food_items=view, label_food_items=QLabel(host)))
        sheet = view.styleSheet().casefold()
        assert "background-color: white" not in sheet
        assert "color:" in sheet
        assert view.palette().color(QPalette.ColorRole.Text).lightness() > 180
    finally:
        theme.set_mode(previous, persist=False)
        host.close()
