"""Tests for date-edit calendar wiring and split menu button."""

from __future__ import annotations

import pytest
from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication, QDateEdit, QHBoxLayout, QLabel, QMenu, QPushButton, QWidget

from harrix_swiss_knife.apps.common.date_edit_quick import (
    attach_date_edit_quick_controls,
    match_control_heights,
    match_date_edit_form_height,
    match_layout_control_heights,
)
from harrix_swiss_knife.qt_date_calendar import SoftCalendarWidget
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


def test_attach_date_edit_quick_controls_applies_calendar(qapp: QApplication) -> None:
    assert qapp is not None
    host = QWidget()
    layout = QHBoxLayout(host)
    date_edit = QDateEdit()
    date_edit.setObjectName("dateEdit_food")
    date_edit.setCalendarPopup(True)
    date_edit.setDate(QDate.currentDate())
    layout.addWidget(date_edit)

    attach_date_edit_quick_controls(date_edit)
    QApplication.processEvents()

    calendar = date_edit.calendarWidget()
    assert isinstance(calendar, SoftCalendarWidget)
    labels = {button.text() for button in calendar.findChildren(QPushButton)}
    assert {"Yesterday", "Today", "+1 day", "-1 day"} <= labels
    assert host.findChild(SplitMenuButton) is None
    line_edit = date_edit.lineEdit()
    assert line_edit is not None
    leading = [action for action in line_edit.actions() if action.objectName() == "hskDateEditCalendarIcon"]
    assert len(leading) == 1
    assert not leading[0].icon().isNull()

    host.close()


def test_match_control_heights_aligns_label_and_date_with_button(qapp: QApplication) -> None:
    assert qapp is not None
    host = QWidget()
    layout = QHBoxLayout(host)
    label = QLabel("From:")
    date_edit = QDateEdit()
    date_edit.setCalendarPopup(True)
    button = QPushButton("📅 Last Month")
    layout.addWidget(label)
    layout.addWidget(date_edit)
    layout.addWidget(button)
    host.show()
    QApplication.processEvents()

    height = match_layout_control_heights(layout)
    QApplication.processEvents()

    assert height >= 24
    assert label.minimumHeight() == height
    assert date_edit.minimumHeight() == height
    assert button.minimumHeight() == height
    assert label.maximumHeight() == height
    assert date_edit.maximumHeight() == height
    assert button.maximumHeight() == height
    assert match_control_heights() == 0

    host.close()


def test_match_date_edit_form_height_copies_peer_font(qapp: QApplication) -> None:
    assert qapp is not None
    host = QWidget()
    layout = QHBoxLayout(host)
    peer = QPushButton("Amount")
    peer_font = QFont(peer.font())
    peer_font.setPointSize(12)
    peer.setFont(peer_font)
    date_edit = QDateEdit()
    date_edit.setCalendarPopup(True)
    layout.addWidget(peer)
    layout.addWidget(date_edit)
    host.show()
    QApplication.processEvents()

    height = match_date_edit_form_height(date_edit, peer)
    QApplication.processEvents()

    assert height >= 24
    assert date_edit.font().pointSize() == 12
    assert date_edit.minimumHeight() == height
    assert peer.minimumHeight() == height
    assert match_date_edit_form_height(date_edit) == 0

    host.close()
