"""Tests for date-edit quick button labels and split menu button."""

from __future__ import annotations

import pytest
from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import QApplication, QDateEdit, QHBoxLayout, QMenu, QWidget

from harrix_swiss_knife.apps.common.date_edit_quick import (
    attach_date_edit_quick_controls,
    date_quick_button_label,
    date_quick_primary_action,
)
from harrix_swiss_knife.qt_split_menu_button import SplitMenuButton, make_lucide_split_menu_button


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_date_quick_button_label_today_yesterday_and_other() -> None:
    today = QDate(2026, 8, 16)
    assert date_quick_button_label(today, today=today) == "📅 Today"
    assert date_quick_button_label(today.addDays(-1), today=today) == "📅 Yesterday"
    assert date_quick_button_label(today.addDays(-2), today=today) == "➕ Add + 1"  # noqa: RUF001
    assert date_quick_button_label(today.addDays(1), today=today) == "➕ Add + 1"  # noqa: RUF001


def test_date_quick_primary_action_matches_label() -> None:
    today = QDate(2026, 8, 16)
    calls: list[str] = []

    def set_today() -> None:
        calls.append("today")

    def set_yesterday() -> None:
        calls.append("yesterday")

    def add_one_day() -> None:
        calls.append("add")

    date_quick_primary_action(
        today,
        set_today=set_today,
        set_yesterday=set_yesterday,
        add_one_day=add_one_day,
        today=today,
    )()
    date_quick_primary_action(
        today.addDays(-1),
        set_today=set_today,
        set_yesterday=set_yesterday,
        add_one_day=add_one_day,
        today=today,
    )()
    date_quick_primary_action(
        today.addDays(2),
        set_today=set_today,
        set_yesterday=set_yesterday,
        add_one_day=add_one_day,
        today=today,
    )()
    assert calls == ["today", "yesterday", "add"]


def test_split_menu_button_main_click_does_not_require_menu(qapp: QApplication) -> None:
    assert qapp is not None
    button = SplitMenuButton(text="Run")
    clicked: list[bool] = []
    button.clicked.connect(lambda: clicked.append(True))
    button.main_button.click()
    assert clicked == [True]
    assert button.menu() is None
    button.close()


def test_split_menu_button_set_menu_and_text(qapp: QApplication) -> None:
    assert qapp is not None
    button = SplitMenuButton()
    menu = QMenu(button)
    menu.addAction("Item")
    button.setMenu(menu)
    button.setText("Primary")
    assert button.menu() is menu
    assert button.text() == "Primary"
    assert button.arrow_button.focusPolicy() == Qt.FocusPolicy.NoFocus
    button.close()


def test_make_lucide_split_menu_button_sets_icon(qapp: QApplication) -> None:
    assert qapp is not None
    button = make_lucide_split_menu_button("Check", "map")
    assert button.text() == "Check"
    assert not button.main_button.icon().isNull()
    button.close()


def test_attach_date_edit_quick_controls_uses_split_and_matches_height(
    qapp: QApplication,
) -> None:
    assert qapp is not None
    host = QWidget()
    layout = QHBoxLayout(host)
    date_edit = QDateEdit()
    date_edit.setObjectName("dateEdit_food")
    date_edit.setCalendarPopup(True)
    date_edit.setDate(QDate.currentDate())
    layout.addWidget(date_edit)

    button = attach_date_edit_quick_controls(date_edit, button_object_name="pushButton_food_date_quick")
    QApplication.processEvents()

    assert isinstance(button, SplitMenuButton)
    assert button.objectName() == "pushButton_food_date_quick"
    assert button.menu() is not None
    assert date_edit.minimumHeight() == button.minimumHeight()
    assert date_edit.maximumHeight() == button.maximumHeight()
    assert date_edit.height() == button.height() or date_edit.minimumHeight() == button.minimumHeight()

    before = date_edit.date()
    button.main_button.click()
    QApplication.processEvents()
    assert date_edit.date() == before  # today → primary is set_today

    date_edit.setDate(before.addDays(-3))
    QApplication.processEvents()
    button.main_button.click()
    QApplication.processEvents()
    assert date_edit.date() == before.addDays(-2)

    host.close()
