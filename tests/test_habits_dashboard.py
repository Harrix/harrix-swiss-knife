"""Tests for habits dashboard database helpers (streak / toggle)."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import pytest
from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QImage, QPainter, QStandardItem, QStandardItemModel
from PySide6.QtTest import QTest
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QStyleOptionViewItem,
    QTableView,
    QWidget,
)

from harrix_swiss_knife.apps.habits.dashboard import HabitDashboardWidget
from harrix_swiss_knife.apps.habits.dashboard_widgets import (
    CheckCircle,
    HabitRow,
    MonthCalendarGrid,
    habit_day_state,
    paint_habit_day_circle,
)
from harrix_swiss_knife.apps.habits.database_manager import DatabaseManager
from harrix_swiss_knife.apps.habits.delegates.process_habit_bool_delegate import ProcessHabitBoolDelegate
from harrix_swiss_knife.apps.habits.delegates.process_habit_int_delegate import ProcessHabitIntDelegate
from harrix_swiss_knife.apps.habits.habit_day_picker import (
    DayChoiceCircle,
    HabitDayPickerPopup,
    alternative_habit_day_choices,
    habit_day_choice_caption,
)

RECOVER_SQL = Path(__file__).resolve().parents[1] / "src/harrix_swiss_knife/apps/habits/recover.sql"


@pytest.fixture
def qapp() -> QApplication:
    """Ensure a QApplication exists for Qt SQL drivers."""
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


@pytest.fixture
def habits_db(tmp_path: Path, qapp: QApplication) -> Iterator[DatabaseManager]:  # noqa: ARG001
    """Create an empty habits SQLite database for tests."""
    db_path = tmp_path / "habits.sqlite"
    assert DatabaseManager.create_database_from_sql(str(db_path), str(RECOVER_SQL))
    db = DatabaseManager(str(db_path))
    yield db
    db.close()


def _local_today() -> date:
    return datetime.now(UTC).astimezone().date()


def test_toggle_habit_checkin_and_total(habits_db: DatabaseManager) -> None:
    """Toggle inserts then removes a check-in and updates totals."""
    assert habits_db.add_habit("Walk", is_bool=True)
    habit_id = int(habits_db.get_habits()[0][0])
    today = _local_today().isoformat()

    assert habits_db.toggle_habit_checkin(habit_id, today)
    assert habits_db.is_habit_done_on_date(habit_id, today)
    assert habits_db.get_habit_total_checkins(habit_id) == 1

    assert habits_db.toggle_habit_checkin(habit_id, today)
    assert not habits_db.is_habit_done_on_date(habit_id, today)
    assert habits_db.get_habit_total_checkins(habit_id) == 0


def test_habit_streak_counts_consecutive_days(habits_db: DatabaseManager) -> None:
    """Streak counts consecutive completed days ending today or yesterday."""
    assert habits_db.add_habit("Read", is_bool=True)
    habit_id = int(habits_db.get_habits()[0][0])
    today = _local_today()

    for offset in range(3):
        day = (today - timedelta(days=offset)).isoformat()
        assert habits_db.add_process_habit_record(habit_id, 1, day)

    assert habits_db.get_habit_streak(habit_id) == 3

    # Gap yesterday breaks streak when today is also missing after we clear today
    assert habits_db.toggle_habit_checkin(habit_id, today.isoformat())  # uncheck today
    # Still 2 if yesterday and day-2 are done (grace: start from yesterday)
    assert habits_db.get_habit_streak(habit_id) == 2


def test_habit_day_state_mapping() -> None:
    """Map missing, zero, one, and other integers to dashboard states."""
    assert habit_day_state(None) == "absent"
    assert habit_day_state(0) == "zero"
    assert habit_day_state(1) == "one"
    assert habit_day_state(2) == "number"
    assert habit_day_state(15) == "number"
    assert habit_day_state(-3) == "number"


def test_get_habit_value_on_date_and_values_between(habits_db: DatabaseManager) -> None:
    """Distinguish no row, stored 0, stored 1, and other numeric values."""
    assert habits_db.add_habit("Push-ups", is_bool=False)
    habit_id = int(habits_db.get_habits()[0][0])
    today = _local_today()
    day_one = today.isoformat()
    day_zero = (today - timedelta(days=1)).isoformat()
    day_number = (today - timedelta(days=2)).isoformat()
    day_absent = (today - timedelta(days=3)).isoformat()

    assert habits_db.add_process_habit_record(habit_id, 1, day_one)
    assert habits_db.add_process_habit_record(habit_id, 0, day_zero)
    assert habits_db.add_process_habit_record(habit_id, 12, day_number)

    assert habits_db.get_habit_value_on_date(habit_id, day_one) == 1
    assert habits_db.get_habit_value_on_date(habit_id, day_zero) == 0
    assert habits_db.get_habit_value_on_date(habit_id, day_number) == 12
    assert habits_db.get_habit_value_on_date(habit_id, day_absent) is None

    values = habits_db.get_habit_values_between(habit_id, day_absent, day_one)
    assert values[day_one] == 1
    assert values[day_zero] == 0
    assert values[day_number] == 12
    assert day_absent not in values

    assert habits_db.is_habit_done_on_date(habit_id, day_one)
    assert not habits_db.is_habit_done_on_date(habit_id, day_zero)
    assert habits_db.is_habit_done_on_date(habit_id, day_number)
    assert not habits_db.is_habit_done_on_date(habit_id, day_absent)


def test_check_circle_four_states(qapp: QApplication) -> None:
    """CheckCircle shows absent, zero, completed, and numeric states."""
    assert qapp is not None
    circle = CheckCircle()
    assert circle.day_state() == "absent"
    assert circle.toolTip() == ""
    assert not circle.is_done()
    assert circle.value() is None

    circle.set_value(0)
    assert circle.day_state() == "zero"
    assert not circle.is_done()

    circle.set_value(1)
    assert circle.day_state() == "one"
    assert circle.is_done()

    circle.set_value(8)
    assert circle.day_state() == "number"
    assert circle.is_done()
    assert circle.value() == 8


def test_paint_habit_day_circle_states(qapp: QApplication) -> None:
    """Shared circle painter accepts absent, zero, one, and numeric values."""
    assert qapp is not None
    image = QImage(24, 24, QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(0)
    painter = QPainter(image)
    assert painter.isActive()
    for value in (None, 0, 1, 8, -3):
        paint_habit_day_circle(painter, QRectF(1, 1, 22, 22), value)
    painter.end()


def test_process_habit_delegates_paint_circles(qapp: QApplication) -> None:
    """Table delegates paint dashboard-style circles for 0, 1, number, and empty."""
    assert qapp is not None
    model = QStandardItemModel(1, 4)
    empty = QStandardItem("")
    empty.setData((None, 1, "2026-08-15"), Qt.ItemDataRole.UserRole)
    zero = QStandardItem("0")
    zero.setData((10, 1, "2026-08-15"), Qt.ItemDataRole.UserRole)
    one = QStandardItem("1")
    one.setData((11, 1, "2026-08-15"), Qt.ItemDataRole.UserRole)
    number = QStandardItem("12")
    number.setData((12, 2, "2026-08-15"), Qt.ItemDataRole.UserRole)
    model.setItem(0, 0, empty)
    model.setItem(0, 1, zero)
    model.setItem(0, 2, one)
    model.setItem(0, 3, number)

    view = QTableView()
    view.setModel(model)
    bool_delegate = ProcessHabitBoolDelegate(view)
    int_delegate = ProcessHabitIntDelegate(view)
    view.setItemDelegateForColumn(0, bool_delegate)
    view.setItemDelegateForColumn(1, bool_delegate)
    view.setItemDelegateForColumn(2, bool_delegate)
    view.setItemDelegateForColumn(3, int_delegate)

    image = QImage(80, 32, QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(0)
    painter = QPainter(image)
    option = QStyleOptionViewItem()
    option.rect = image.rect()
    option.widget = view
    for column, delegate in ((0, bool_delegate), (1, bool_delegate), (2, bool_delegate), (3, int_delegate)):
        delegate.paint(painter, option, model.index(0, column))
    painter.end()
    view.deleteLater()


def test_set_habit_checkin_four_kinds(habits_db: DatabaseManager) -> None:
    """Set no record, 0, 1, and a numeric value for a habit day."""
    assert habits_db.add_habit("Push-ups", is_bool=False)
    habit_id = int(habits_db.get_habits()[0][0])
    day = _local_today().isoformat()

    assert habits_db.set_habit_checkin(habit_id, day, None)
    assert habits_db.get_habit_value_on_date(habit_id, day) is None

    assert habits_db.set_habit_checkin(habit_id, day, 0)
    assert habits_db.get_habit_value_on_date(habit_id, day) == 0
    assert not habits_db.is_habit_done_on_date(habit_id, day)

    assert habits_db.set_habit_checkin(habit_id, day, 1)
    assert habits_db.get_habit_value_on_date(habit_id, day) == 1
    assert habits_db.is_habit_done_on_date(habit_id, day)

    assert habits_db.set_habit_checkin(habit_id, day, 15)
    assert habits_db.get_habit_value_on_date(habit_id, day) == 15
    assert habits_db.is_habit_done_on_date(habit_id, day)

    assert habits_db.set_habit_checkin(habit_id, day, None)
    assert habits_db.get_habit_value_on_date(habit_id, day) is None
    assert not habits_db.is_habit_done_on_date(habit_id, day)


def test_habit_row_day_value_set_signal(qapp: QApplication) -> None:
    """Week circles forward picker values, including None."""
    assert qapp is not None
    row = HabitRow()
    row.set_habit_data(7, "Walk", 0, 0, [None] * 7, selected=False, allows_number=True)
    received: list[tuple[int, int, object]] = []
    row.day_value_set.connect(lambda hid, idx, val: received.append((hid, idx, val)))

    circles = row.findChildren(CheckCircle)
    assert len(circles) == 7
    assert all(circle.allows_number() for circle in circles)
    circles[3].value_set.emit(12)
    circles[0].value_set.emit(None)
    assert received == [(7, 3, 12), (7, 0, None)]

    row.set_habit_data(7, "Walk", 0, 0, [None] * 7, selected=False, allows_number=False)
    assert all(not circle.allows_number() for circle in row.findChildren(CheckCircle))
    assert "border-bottom" in row.styleSheet()
    assert "#FFFFFF" in row.styleSheet()
    row.set_habit_data(7, "Walk", 0, 0, [None] * 7, selected=True, allows_number=False)
    assert "#EFF6FF" in row.styleSheet()
    assert "QFrame#habitRow QLabel" in row.styleSheet()


def test_habit_dashboard_list_scrolls(qapp: QApplication) -> None:
    """Habit list sits in a resizable scroll area so long lists can move down."""
    assert qapp is not None
    dashboard = HabitDashboardWidget()
    scroll = dashboard.findChild(QScrollArea, "habitDashListScroll")
    assert scroll is not None
    assert scroll.widgetResizable()
    assert scroll.verticalScrollBarPolicy() == Qt.ScrollBarPolicy.ScrollBarAsNeeded


def test_habit_dashboard_empty_shows_add_button(habits_db: DatabaseManager, qapp: QApplication) -> None:
    """Empty dashboard shows a large Add habit button instead of the list."""
    assert qapp is not None
    dashboard = HabitDashboardWidget()
    dashboard.set_database(habits_db)

    empty = dashboard.findChild(QWidget, "habitDashEmptyState")
    button = dashboard.findChild(QPushButton, "habitDashAddHabitButton")
    assert empty is not None
    assert button is not None
    assert not empty.isHidden()
    assert button.text().endswith("Add habit")
    assert button.minimumHeight() >= 64
    assert button.minimumWidth() >= 280

    assert habits_db.add_habit("Walk", is_bool=True)
    dashboard.refresh()
    assert empty.isHidden()


def test_month_calendar_day_value_set_signal(qapp: QApplication) -> None:
    """Month circles forward picker values for the selected date."""
    assert qapp is not None
    grid = MonthCalendarGrid()
    grid.set_month(2026, 8, {"2026-08-14": 1}, allows_number=True, today=date(2026, 8, 15))
    received: list[tuple[str, object]] = []
    grid.day_value_set.connect(lambda date_str, val: received.append((date_str, val)))

    matches = [circle for circle in grid.findChildren(CheckCircle) if circle.value() == 1]
    assert len(matches) == 1
    assert matches[0].allows_number()
    assert matches[0].is_editable()
    matches[0].value_set.emit(4)

    assert received == [("2026-08-14", 4)]


def test_check_circle_future_date_not_editable(qapp: QApplication) -> None:
    """Future circles ignore left-clicks and show a future-date tooltip."""
    assert qapp is not None
    circle = CheckCircle()
    received: list[bool] = []
    circle.clicked.connect(lambda: received.append(True))

    circle.set_editable(editable=False)
    assert not circle.is_editable()
    assert circle.toolTip() == "Future date"
    QTest.mouseClick(circle, Qt.MouseButton.LeftButton)
    assert received == []

    circle.set_editable(editable=True)
    assert circle.is_editable()
    QTest.mouseClick(circle, Qt.MouseButton.LeftButton)
    assert received == [True]


def test_month_calendar_blocks_future_dates(qapp: QApplication) -> None:
    """Future month days are not editable and the next-month button stops at today."""
    assert qapp is not None
    today = date(2026, 8, 15)
    grid = MonthCalendarGrid()
    grid.set_month(2026, 8, {"2026-08-16": 0}, today=today)
    future = [circle for circle in grid.findChildren(CheckCircle) if circle.value() == 0]
    assert len(future) == 1
    assert not future[0].is_editable()
    assert future[0].toolTip() == "Future date"

    next_btn = next(button for button in grid.findChildren(QPushButton) if button.toolTip() == "Next month")
    assert not next_btn.isEnabled()
    assert next_btn.cursor().shape() == Qt.CursorShape.ArrowCursor
    assert "QPushButton:disabled" in next_btn.styleSheet()

    changed: list[tuple[int, int]] = []
    grid.month_changed.connect(lambda year, month: changed.append((year, month)))
    next_btn.click()
    assert changed == []

    grid.set_month(2026, 7, {}, today=today)
    next_btn = next(button for button in grid.findChildren(QPushButton) if button.toolTip() == "Next month")
    assert next_btn.isEnabled()
    assert next_btn.cursor().shape() == Qt.CursorShape.PointingHandCursor


def test_month_calendar_title_double_click_returns_to_today(qapp: QApplication) -> None:
    """Double-clicking the month title jumps back to the current month."""
    assert qapp is not None
    today = date(2026, 8, 15)
    grid = MonthCalendarGrid()
    grid.set_month(2026, 6, {}, today=today)
    changed: list[tuple[int, int]] = []
    grid.month_changed.connect(lambda year, month: changed.append((year, month)))
    title = grid.findChild(QLabel, "habitDashCalendarTitle")
    assert title is not None
    QTest.mouseDClick(title, Qt.MouseButton.LeftButton)
    assert changed == [(2026, 8)]

    grid.set_month(2026, 8, {}, today=today)
    changed.clear()
    QTest.mouseDClick(title, Qt.MouseButton.LeftButton)
    assert changed == []


def test_alternative_habit_day_choices() -> None:
    """Picker offers every state except the one already on the circle."""
    assert alternative_habit_day_choices(None, allows_number=True) == [0, 1, "number"]
    assert alternative_habit_day_choices(0, allows_number=True) == [None, 1, "number"]
    assert alternative_habit_day_choices(1, allows_number=True) == [None, 0, "number"]
    assert alternative_habit_day_choices(8, allows_number=True) == [None, 0, 1]
    assert alternative_habit_day_choices(None, allows_number=False) == [0, 1]
    assert alternative_habit_day_choices(1, allows_number=False) == [None, 0]
    assert habit_day_choice_caption(None) == "No record"
    assert habit_day_choice_caption("number") == "Number"


def test_habit_day_picker_selects_alternative(qapp: QApplication) -> None:
    """Clicking a picker circle sets that remaining value and closes the panel."""
    assert qapp is not None
    circle = CheckCircle()
    circle.set_allows_number(allows_number=True)
    received: list[object] = []
    circle.value_set.connect(received.append)

    popup = HabitDayPickerPopup.show_for(circle)
    assert popup.choices() == [0, 1, "number"]
    zero = next(option for option in popup.findChildren(DayChoiceCircle) if option.choice() == 0)
    QTest.mouseClick(zero, Qt.MouseButton.LeftButton)
    assert received == [0]
    assert not popup.isVisible()
    HabitDayPickerPopup.hide_active()


def test_habit_day_picker_number_stepper(qapp: QApplication) -> None:
    """Number choice opens a stepper that emits the typed value."""
    assert qapp is not None
    circle = CheckCircle()
    circle.set_allows_number(allows_number=True)
    received: list[object] = []
    circle.value_set.connect(received.append)

    popup = HabitDayPickerPopup.show_for(circle)
    number = next(option for option in popup.findChildren(DayChoiceCircle) if option.choice() == "number")
    QTest.mouseClick(number, Qt.MouseButton.LeftButton)
    edit = popup.findChild(QLineEdit)
    assert edit is not None
    edit.setText("12")
    set_btn = next(button for button in popup.findChildren(QPushButton) if button.text() == "Set")
    QTest.mouseClick(set_btn, Qt.MouseButton.LeftButton)
    assert received == [12]
    assert not popup.isVisible()
    HabitDayPickerPopup.hide_active()


def test_habit_day_picker_two_choices_are_compact(qapp: QApplication) -> None:
    """Two remaining states stay close together instead of stretching to the stepper page."""
    assert qapp is not None
    HabitDayPickerPopup.hide_active()

    two_circle = CheckCircle()
    two_circle.set_allows_number(allows_number=False)
    two_circle.show()
    popup = HabitDayPickerPopup.show_for(two_circle)
    qapp.processEvents()
    assert popup.choices() == [0, 1]
    two_width = popup.width()
    two_height = popup.height()

    three_circle = CheckCircle()
    three_circle.set_allows_number(allows_number=True)
    three_circle.show()
    popup = HabitDayPickerPopup.show_for(three_circle)
    qapp.processEvents()
    assert popup.choices() == [0, 1, "number"]
    three_width = popup.width()
    HabitDayPickerPopup.hide_active()

    assert two_width < three_width
    assert two_height < 90


def _assert_picker_above_circle(popup: HabitDayPickerPopup, circle: CheckCircle) -> None:
    circle_top = circle.mapToGlobal(circle.rect().topLeft()).y()
    popup_bottom = popup.y() + popup.height()
    assert popup.y() < circle_top
    assert popup_bottom <= circle_top


def test_habit_day_picker_sits_above_circle(qapp: QApplication) -> None:
    """Bubble stays above the hovered circle even after a taller stepper page."""
    assert qapp is not None
    HabitDayPickerPopup.hide_active()

    host = QWidget()
    host.resize(400, 400)
    host.move(240, 240)
    circle = CheckCircle(host)
    circle.set_allows_number(allows_number=True)
    circle.move(180, 220)
    host.show()
    qapp.processEvents()

    popup = HabitDayPickerPopup.show_for(circle)
    qapp.processEvents()
    _assert_picker_above_circle(popup, circle)

    number = next(option for option in popup.findChildren(DayChoiceCircle) if option.choice() == "number")
    QTest.mouseClick(number, Qt.MouseButton.LeftButton)
    qapp.processEvents()
    popup = HabitDayPickerPopup.show_for(circle)
    qapp.processEvents()
    _assert_picker_above_circle(popup, circle)

    HabitDayPickerPopup.hide_active()
    host.close()
