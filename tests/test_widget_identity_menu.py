"""Tests for Copy object name / Copy class name widget identity menus."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from PySide6.QtCore import QEvent, QPoint, QPointF, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QApplication, QLabel, QLineEdit, QListWidget, QPushButton, QWidget

import harrix_swiss_knife.qt_widget_identity_menu as identity_menu
from harrix_swiss_knife.fluent.widgets.card_base import FluentInteractiveCard
from harrix_swiss_knife.qt_widget_identity_menu import (
    WidgetIdentityEventFilter,
    ensure_widget_object_name,
    format_copy_class_name_menu_label,
    format_copy_object_name_menu_label,
    install_widget_identity_context_menus,
    resolve_identity_widget,
    widget_class_name_for_copy,
    widget_object_name_for_copy,
)


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


@pytest.fixture(autouse=True)
def _reset_auto_object_name_counts() -> None:
    identity_menu._AUTO_NAME_COUNTS.clear()


def _middle_press(widget: QWidget) -> QMouseEvent:
    local = QPointF(1, 1)
    return QMouseEvent(
        QEvent.Type.MouseButtonPress,
        local,
        widget.mapToGlobal(local.toPoint()),
        Qt.MouseButton.MiddleButton,
        Qt.MouseButton.MiddleButton,
        Qt.KeyboardModifier.NoModifier,
    )


def test_widget_object_name_auto_assigns_from_text(qapp: QApplication) -> None:  # noqa: ARG001
    widget = QPushButton("Select exercise")
    assert widget_object_name_for_copy(widget) == "QPushButton_Select_exercise"
    assert widget.objectName() == "QPushButton_Select_exercise"
    assert widget_class_name_for_copy(widget) == "QPushButton"


def test_widget_object_name_preserves_explicit_name(qapp: QApplication) -> None:  # noqa: ARG001
    widget = QPushButton("Select exercise")
    widget.setObjectName("pushButton_select_exercise")
    assert widget_object_name_for_copy(widget) == "pushButton_select_exercise"
    assert ensure_widget_object_name(widget) == "pushButton_select_exercise"


def test_widget_object_name_suffixes_duplicates(qapp: QApplication) -> None:  # noqa: ARG001
    first = QPushButton("OK")
    second = QPushButton("OK")
    assert widget_object_name_for_copy(first) == "QPushButton_OK"
    assert widget_object_name_for_copy(second) == "QPushButton_OK_2"


def test_ensure_skips_when_name_already_set(qapp: QApplication) -> None:  # noqa: ARG001
    view = QListWidget()
    view.setObjectName("FluentListWidget")
    assert ensure_widget_object_name(view) == "FluentListWidget"
    assert view.objectName() == "FluentListWidget"


def test_format_copy_labels() -> None:
    assert format_copy_object_name_menu_label("foo") == "📋 Copy object name (foo)"
    assert format_copy_class_name_menu_label("Bar") == "📋 Copy class name (Bar)"


def test_resolve_identity_widget_prefers_named_view(qapp: QApplication) -> None:  # noqa: ARG001
    view = QListWidget()
    view.setObjectName("listView_exercises")
    viewport = view.viewport()
    assert viewport is not None
    assert resolve_identity_widget(viewport) is view
    assert resolve_identity_widget(view) is view


def test_install_widget_identity_context_menus_is_idempotent(qapp: QApplication) -> None:
    install_widget_identity_context_menus(qapp)
    first = qapp.property("_hskWidgetIdentityFilter")
    install_widget_identity_context_menus(qapp)
    second = qapp.property("_hskWidgetIdentityFilter")
    assert isinstance(first, WidgetIdentityEventFilter)
    assert first is second


def test_filter_auto_names_on_polish(qapp: QApplication) -> None:
    install_widget_identity_context_menus(qapp)
    event_filter = qapp.property("_hskWidgetIdentityFilter")
    assert isinstance(event_filter, WidgetIdentityEventFilter)
    button = QPushButton("Print")
    assert button.objectName() == ""
    event_filter.eventFilter(button, QEvent(QEvent.Type.Polish))
    assert button.objectName() == "QPushButton_Print"


def test_filter_handles_middle_click_on_label(qapp: QApplication) -> None:
    install_widget_identity_context_menus(qapp)
    event_filter = qapp.property("_hskWidgetIdentityFilter")
    assert isinstance(event_filter, WidgetIdentityEventFilter)
    label = QLabel("hi")
    label.setObjectName("label_exercise")
    with patch(
        "harrix_swiss_knife.qt_widget_identity_menu.show_widget_identity_context_menu",
    ) as show_menu:
        handled = event_filter.eventFilter(label, _middle_press(label))
    assert handled is True
    show_menu.assert_called_once()


def test_filter_handles_middle_click_on_line_edit(qapp: QApplication) -> None:
    install_widget_identity_context_menus(qapp)
    event_filter = qapp.property("_hskWidgetIdentityFilter")
    assert isinstance(event_filter, WidgetIdentityEventFilter)
    edit = QLineEdit()
    edit.setObjectName("lineEdit_tag")
    with patch(
        "harrix_swiss_knife.qt_widget_identity_menu.show_widget_identity_context_menu",
    ) as show_menu:
        handled = event_filter.eventFilter(edit, _middle_press(edit))
    assert handled is True
    show_menu.assert_called_once()


def test_filter_skips_fluent_interactive_card(qapp: QApplication) -> None:
    """Command cards own middle-click for the richer action copy menu."""
    install_widget_identity_context_menus(qapp)
    event_filter = qapp.property("_hskWidgetIdentityFilter")
    assert isinstance(event_filter, WidgetIdentityEventFilter)
    card = FluentInteractiveCard()
    with patch(
        "harrix_swiss_knife.qt_widget_identity_menu.show_widget_identity_context_menu",
    ) as show_menu:
        handled = event_filter.eventFilter(card, _middle_press(card))
    assert handled is False
    show_menu.assert_not_called()


def test_filter_ignores_right_click_context_menu(qapp: QApplication) -> None:
    install_widget_identity_context_menus(qapp)
    event_filter = qapp.property("_hskWidgetIdentityFilter")
    assert isinstance(event_filter, WidgetIdentityEventFilter)
    label = QLabel("hi")
    right = QMouseEvent(
        QEvent.Type.MouseButtonPress,
        QPointF(1, 1),
        label.mapToGlobal(QPoint(1, 1)),
        Qt.MouseButton.RightButton,
        Qt.MouseButton.RightButton,
        Qt.KeyboardModifier.NoModifier,
    )
    with patch(
        "harrix_swiss_knife.qt_widget_identity_menu.show_widget_identity_context_menu",
    ) as show_menu:
        handled = event_filter.eventFilter(label, right)
    assert handled is False
    show_menu.assert_not_called()


def test_filter_ignores_non_mouse_events(qapp: QApplication) -> None:
    event_filter = WidgetIdentityEventFilter(qapp)
    widget = QWidget()
    assert event_filter.eventFilter(widget, QEvent(QEvent.Type.Hide)) is False
