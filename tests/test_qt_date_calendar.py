"""Tests for Ant-like QDateEdit calendar popups."""

from __future__ import annotations

import pytest
from PySide6.QtCore import QDate
from PySide6.QtWidgets import QApplication, QDateEdit, QPushButton, QTableView, QWidget

from harrix_swiss_knife.qt_date_calendar import (
    SoftCalendarWidget,
    apply_date_calendar_popup,
    install_date_calendar_popups,
)
from harrix_swiss_knife.qt_ui_effects import install_ui_effects


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_apply_date_calendar_popup_replaces_widget(qapp: QApplication) -> None:  # noqa: ARG001
    date_edit = QDateEdit()
    date_edit.setCalendarPopup(True)
    apply_date_calendar_popup(date_edit)
    calendar = date_edit.calendarWidget()
    assert isinstance(calendar, SoftCalendarWidget)
    assert calendar.findChild(QPushButton) is not None
    assert "Today" in {button.text() for button in calendar.findChildren(QPushButton)}
    # Idempotent.
    apply_date_calendar_popup(date_edit)
    assert date_edit.calendarWidget() is calendar


def test_soft_calendar_today_and_month_title(qapp: QApplication) -> None:  # noqa: ARG001
    calendar = SoftCalendarWidget()
    calendar.setSelectedDate(QDate(2026, 1, 15))
    calendar.setCurrentPage(2026, 1)
    today = QDate.currentDate()
    calendar._go_today()
    assert calendar.selectedDate() == today
    assert calendar.yearShown() == today.year()
    assert calendar.monthShown() == today.month()
    assert calendar._title.text()


def test_soft_calendar_keeps_seven_equal_day_columns(qapp: QApplication) -> None:
    calendar = SoftCalendarWidget()
    calendar.setSelectedDate(QDate(2026, 10, 4))
    calendar.setCurrentPage(2026, 10)
    calendar.show()
    qapp.processEvents()
    calendar._tune_grid()
    qapp.processEvents()

    view = calendar.findChild(QTableView, "qt_calendar_calendarview")
    assert view is not None
    assert calendar.findChild(QWidget, "hskCalendarWeekdays") is not None
    widths = [view.columnWidth(index) for index in range(7)]
    assert len(widths) == 7
    assert min(widths) >= 30
    assert max(widths) - min(widths) <= 2
    assert calendar.sizeHint().width() >= 7 * 36
    # Selection must not remove the weekday row.
    calendar.setSelectedDate(QDate(2026, 6, 10))
    qapp.processEvents()
    weekdays = calendar.findChild(QWidget, "hskCalendarWeekdays")
    assert weekdays is not None
    assert weekdays.isVisible()
    assert weekdays.height() >= 20
    calendar.close()


def test_soft_calendar_tracks_hover_date(qapp: QApplication) -> None:
    calendar = SoftCalendarWidget()
    calendar.setCurrentPage(2026, 6)
    calendar.show()
    qapp.processEvents()
    calendar._install_hover_tracking()
    target = QDate(2026, 6, 10)
    calendar._set_hover_date(target)
    assert calendar._hover_date == target
    calendar._set_hover_date(None)
    assert calendar._hover_date is None
    calendar.close()


def test_install_ui_effects_wires_calendar_popups(qapp: QApplication) -> None:
    date_edit = QDateEdit()
    date_edit.setCalendarPopup(True)
    install_ui_effects(qapp)
    install_date_calendar_popups(qapp)  # second call is a no-op
    apply_date_calendar_popup(date_edit)
    assert isinstance(date_edit.calendarWidget(), SoftCalendarWidget)
