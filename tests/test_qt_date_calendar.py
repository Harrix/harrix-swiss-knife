"""Tests for Ant-like QDateEdit calendar popups."""

from __future__ import annotations

import pytest
from PySide6.QtCore import QDate
from PySide6.QtWidgets import QApplication, QDateEdit, QPushButton, QTableView, QWidget

from harrix_swiss_knife.qt_date_calendar import (
    SoftCalendarWidget,
    apply_date_calendar_popup,
    decade_panel_years,
    decade_start,
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
    labels = {button.text() for button in calendar.findChildren(QPushButton)}
    assert {"Yesterday", "Today", "+1 day", "-1 day"} <= labels
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
    assert str(today.year()) == calendar._title_year.text()


def test_soft_calendar_footer_presets(qapp: QApplication) -> None:  # noqa: ARG001
    calendar = SoftCalendarWidget()
    calendar.setSelectedDate(QDate(2026, 6, 15))
    calendar.setCurrentPage(2026, 6)
    calendar._go_yesterday()
    yesterday = QDate.currentDate().addDays(-1)
    assert calendar.selectedDate() == yesterday
    calendar._go_plus_one_day()
    assert calendar.selectedDate() == yesterday.addDays(1)
    calendar._go_minus_one_day()
    assert calendar.selectedDate() == yesterday
    calendar.close()


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


def test_soft_calendar_hover_matches_painted_cell(qapp: QApplication) -> None:
    calendar = SoftCalendarWidget()
    calendar.setCurrentPage(2026, 6)
    calendar.setSelectedDate(QDate(2026, 6, 15))
    calendar.show()
    qapp.processEvents()
    calendar._tune_grid()
    calendar._install_hover_tracking()
    calendar.update()
    qapp.processEvents()

    painted = [(rect, date) for rect, date in calendar._painted_cells if date == QDate(2026, 6, 10)]
    assert painted
    rect, date = painted[0]
    assert calendar._date_at_viewport_pos(rect.center()) == date
    calendar.close()


def test_install_ui_effects_wires_calendar_popups(qapp: QApplication) -> None:
    date_edit = QDateEdit()
    date_edit.setCalendarPopup(True)
    install_ui_effects(qapp)
    install_date_calendar_popups(qapp)  # second call is a no-op
    apply_date_calendar_popup(date_edit)
    assert isinstance(date_edit.calendarWidget(), SoftCalendarWidget)


def test_decade_panel_years_includes_adjacent_years() -> None:
    start, years = decade_panel_years(2026)
    assert start == 2020
    assert decade_start(2026) == 2020
    assert years == [2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030]


def test_soft_calendar_year_title_opens_decade_panel(qapp: QApplication) -> None:
    calendar = SoftCalendarWidget()
    calendar.setCurrentPage(2026, 6)
    calendar.show()
    qapp.processEvents()

    calendar._title_year.click()
    qapp.processEvents()

    panel = calendar.findChild(QWidget, "hskCalendarYearPanel")
    assert panel is not None
    assert panel.isVisible()
    assert calendar._title_year.text() == "2020-2029"
    assert calendar._title_month.isHidden()
    labels = [button.text() for button in calendar._year_buttons]
    assert labels[0] == "2019"
    assert labels[-1] == "2030"
    assert "2026" in labels

    calendar._year_buttons[labels.index("2024")].click()
    qapp.processEvents()
    assert calendar.yearShown() == 2024
    assert calendar.monthShown() == 6
    assert not panel.isVisible()
    month_panel = calendar.findChild(QWidget, "hskCalendarMonthPanel")
    assert month_panel is not None
    assert month_panel.isVisible()
    assert calendar._title_year.text() == "2024"
    assert calendar._title_month.isHidden()
    calendar.close()


def test_soft_calendar_month_title_opens_month_panel(qapp: QApplication) -> None:
    calendar = SoftCalendarWidget()
    calendar.setCurrentPage(2026, 6)
    calendar.show()
    qapp.processEvents()

    calendar._title_month.click()
    qapp.processEvents()

    panel = calendar.findChild(QWidget, "hskCalendarMonthPanel")
    assert panel is not None
    assert panel.isVisible()
    assert calendar._title_month.isHidden()
    assert calendar._title_year.text() == "2026"
    labels = [button.text() for button in calendar._month_buttons]
    assert labels == ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    calendar._next_year.click()
    qapp.processEvents()
    assert calendar._title_year.text() == "2027"

    calendar._month_buttons[labels.index("Oct")].click()
    qapp.processEvents()
    assert calendar.yearShown() == 2027
    assert calendar.monthShown() == 10
    assert not panel.isVisible()
    assert calendar._title_month.text() == "Oct"
    assert calendar._title_year.text() == "2027"
    calendar.close()
