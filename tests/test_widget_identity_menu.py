"""Tests for Copy object name / Copy class name widget identity menus."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from PySide6.QtCore import QEvent, QPoint, Qt
from PySide6.QtGui import QContextMenuEvent
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QWidget,
)

from harrix_swiss_knife.qt_widget_identity_menu import (
    WidgetIdentityEventFilter,
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


def test_widget_object_name_falls_back_to_class(qapp: QApplication) -> None:  # noqa: ARG001
    widget = QPushButton()
    assert widget_object_name_for_copy(widget) == "QPushButton"
    widget.setObjectName("pushButton_select_exercise")
    assert widget_object_name_for_copy(widget) == "pushButton_select_exercise"
    assert widget_class_name_for_copy(widget) == "QPushButton"


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


def test_filter_handles_plain_label_context_menu(qapp: QApplication) -> None:
    install_widget_identity_context_menus(qapp)
    event_filter = qapp.property("_hskWidgetIdentityFilter")
    assert isinstance(event_filter, WidgetIdentityEventFilter)
    label = QLabel("hi")
    label.setObjectName("label_exercise")
    event = QContextMenuEvent(
        QContextMenuEvent.Reason.Mouse,
        QPoint(1, 1),
        label.mapToGlobal(QPoint(1, 1)),
    )
    with patch(
        "harrix_swiss_knife.qt_widget_identity_menu.show_widget_identity_context_menu",
    ) as show_menu:
        handled = event_filter.eventFilter(label, event)
    assert handled is True
    show_menu.assert_called_once()


def test_filter_keeps_line_edit_default_menu(qapp: QApplication) -> None:
    install_widget_identity_context_menus(qapp)
    event_filter = qapp.property("_hskWidgetIdentityFilter")
    assert isinstance(event_filter, WidgetIdentityEventFilter)
    edit = QLineEdit()
    event = QContextMenuEvent(
        QContextMenuEvent.Reason.Mouse,
        QPoint(1, 1),
        edit.mapToGlobal(QPoint(1, 1)),
    )
    with patch(
        "harrix_swiss_knife.qt_widget_identity_menu.show_widget_identity_context_menu",
    ) as show_menu:
        handled = event_filter.eventFilter(edit, event)
    assert handled is False
    show_menu.assert_not_called()


def test_filter_ctrl_overrides_custom_context_menu(qapp: QApplication) -> None:
    install_widget_identity_context_menus(qapp)
    event_filter = qapp.property("_hskWidgetIdentityFilter")
    assert isinstance(event_filter, WidgetIdentityEventFilter)
    button = QPushButton("x")
    button.setObjectName("pushButton_select_exercise")
    button.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
    event = QContextMenuEvent(
        QContextMenuEvent.Reason.Mouse,
        QPoint(1, 1),
        button.mapToGlobal(QPoint(1, 1)),
        Qt.KeyboardModifier.ControlModifier,
    )
    with patch(
        "harrix_swiss_knife.qt_widget_identity_menu.show_widget_identity_context_menu",
    ) as show_menu:
        handled = event_filter.eventFilter(button, event)
    assert handled is True
    show_menu.assert_called_once()
    assert event.type() == QEvent.Type.ContextMenu


def test_filter_ignores_non_context_events(qapp: QApplication) -> None:
    event_filter = WidgetIdentityEventFilter(qapp)
    widget = QWidget()
    assert event_filter.eventFilter(widget, QEvent(QEvent.Type.Show)) is False
