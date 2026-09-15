"""Tests for tray main-window list section headers scrolling the cards pane."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication, QListWidgetItem, QMenu, QWidget

from harrix_swiss_knife.config_model import MAIN_WINDOW_SORT_MODE_MENU
from harrix_swiss_knife.main_window import MainWindow


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def _menu_with_sections(parent: QWidget | None = None) -> QMenu:
    menu = QMenu(parent)
    menu.addAction("Top command")

    files = menu.addMenu("Files")
    for index in range(4):
        files.addAction(f"File action {index}")

    images = menu.addMenu("Images")
    for index in range(4):
        images.addAction(f"Image action {index}")

    return menu


def _build_window(qapp: QApplication) -> MainWindow:  # noqa: ARG001
    with (
        patch("harrix_swiss_knife.main_window.get_main_window_sort_mode", return_value=MAIN_WINDOW_SORT_MODE_MENU),
        patch("harrix_swiss_knife.main_window.get_show_main_window_on_startup", return_value=False),
        patch("harrix_swiss_knife.main_window.apply_app_window_size_and_position"),
        patch("harrix_swiss_knife.main_window.try_apply_system_backdrop"),
        patch("harrix_swiss_knife.main_window.list_recent_gui_action_names", return_value=[]),
    ):
        menu = _menu_with_sections()
        window = MainWindow(menu)
    # Parent the source menu so its QActions outlive the test locals.
    menu.setParent(window)
    return window


def _section_header(window: MainWindow, title: str) -> QListWidgetItem | None:
    for index in range(window.list_widget.count()):
        item = window.list_widget.item(index)
        if item is not None and item.data(Qt.ItemDataRole.UserRole) == title:
            return item
    return None


def test_sort_combo_matches_search_field_height(qapp: QApplication) -> None:
    window = _build_window(qapp)
    try:
        assert window._sort_combo.minimumHeight() == window._search_edit.minimumHeight()
        assert window._sort_combo.minimumHeight() > 0
    finally:
        window.close()
        window.deleteLater()
        qapp.processEvents()


def test_section_header_stores_title_and_is_not_selectable(qapp: QApplication) -> None:
    window = _build_window(qapp)
    try:
        headers = [
            window.list_widget.item(index)
            for index in range(window.list_widget.count())
            if not (window.list_widget.item(index).flags() & Qt.ItemFlag.ItemIsSelectable)
        ]
        titles = [item.data(Qt.ItemDataRole.UserRole) for item in headers if item is not None]
        assert "Files" in titles
        assert "Images" in titles
        assert "Main" in titles
    finally:
        window.close()
        window.deleteLater()
        qapp.processEvents()


def test_clicking_section_header_scrolls_to_grouped_section(qapp: QApplication) -> None:
    window = _build_window(qapp)
    try:
        images_item = _section_header(window, "Images")
        assert images_item is not None
        images_section = next(section for section in window._sections if section.title == "Images")
        assert images_section.widget is not None

        with patch.object(window, "_scroll_cards_to_widget") as scroll_to:
            window.on_item_clicked(images_item)
            scroll_to.assert_called_once_with(images_section.widget)
    finally:
        window.close()
        window.deleteLater()
        qapp.processEvents()


def test_clicking_section_header_in_search_scrolls_to_first_card(qapp: QApplication) -> None:
    window = _build_window(qapp)
    try:
        window._search_edit.setText("action")
        qapp.processEvents()
        assert not window._search_grid.isHidden()
        assert window._grouped_widget.isHidden()

        images_item = _section_header(window, "Images")
        assert images_item is not None

        first_images_widget: QWidget | None = None
        for index in range(window._search_grid.count()):
            item = window._search_grid.item(index)
            assert item is not None
            action = item.data(Qt.ItemDataRole.UserRole)
            assert isinstance(action, QAction)
            if window._action_sections.get(action) == "Images":
                first_images_widget = window._search_grid.itemWidget(item)
                break
        assert first_images_widget is not None

        with patch.object(window, "_scroll_cards_to_widget") as scroll_to:
            window.on_item_clicked(images_item)
            scroll_to.assert_called_once_with(first_images_widget)
    finally:
        window.close()
        window.deleteLater()
        qapp.processEvents()


def test_scroll_cards_to_widget_sets_scrollbar_value(qapp: QApplication) -> None:
    window = _build_window(qapp)
    try:
        content = MagicMock()
        bar = MagicMock()
        bar.maximum.return_value = 400
        widget = MagicMock()
        widget.mapTo.return_value.y.return_value = 250

        with (
            patch.object(window._scroll, "widget", return_value=content),
            patch.object(window._scroll, "verticalScrollBar", return_value=bar),
        ):
            window._scroll_cards_to_widget(widget)

        widget.mapTo.assert_called_once()
        bar.setValue.assert_called_once_with(250)
    finally:
        window.close()
        window.deleteLater()
        qapp.processEvents()
