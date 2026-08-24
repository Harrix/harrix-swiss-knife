"""Tests for shared table context-menu labels and helpers."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication, QMenu

from harrix_swiss_knife.apps.common.table_context_menu import (
    LABEL_DELETE,
    LABEL_SET_DATE,
    LABEL_SHOW_ALL_RECORDS,
    add_date_in_main_field_actions,
    add_delete_action,
    add_info_action,
    add_separator,
    show_records_label,
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


def test_add_delete_action_is_last_and_named_delete(qapp: QApplication) -> None:  # noqa: ARG001
    menu = QMenu()
    menu.addAction("✏️ Edit")
    add_delete_action(menu)
    texts = [action.text() for action in menu.actions() if not action.isSeparator()]
    assert texts[-1] == LABEL_DELETE
    assert LABEL_DELETE == "🗑️ Delete"


def test_add_separator_skips_empty_and_duplicate(qapp: QApplication) -> None:  # noqa: ARG001
    menu = QMenu()
    add_separator(menu)
    assert menu.isEmpty()
    menu.addAction("✏️ Edit")
    add_separator(menu)
    add_separator(menu)
    assert [action.isSeparator() for action in menu.actions()] == [False, True]


def test_add_date_in_main_field_actions_use_shared_labels(qapp: QApplication) -> None:  # noqa: ARG001
    menu = QMenu()
    set_date, plus_one, minus_one = add_date_in_main_field_actions(menu)
    assert set_date.text() == LABEL_SET_DATE
    assert "1 day" in plus_one.text()
    assert "1 day" in minus_one.text()


def test_add_info_action_is_disabled(qapp: QApplication) -> None:  # noqa: ARG001
    menu = QMenu()
    menu.addAction("📤 Export to CSV")
    info = add_info_action(menu, "💰 Sum of selected: 10")
    assert not info.isEnabled()
    add_delete_action(menu)
    texts = [action.text() for action in menu.actions() if not action.isSeparator()]
    assert texts[-1] == LABEL_DELETE


def test_show_records_label() -> None:
    assert show_records_label(show_all=False, last_count=20) == LABEL_SHOW_ALL_RECORDS
    assert show_records_label(show_all=True, last_count=20) == "📋 Show last 20"
