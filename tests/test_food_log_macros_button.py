"""Tests for the food-log day total macros button."""

from __future__ import annotations

import pytest
from PySide6.QtCore import QEvent, QPointF, QRect, Qt
from PySide6.QtGui import QFont, QFontMetrics, QMouseEvent, QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QApplication, QStyleOptionViewItem, QTableView

from harrix_swiss_knife.apps.food.day_macros import DayMacrosStatus
from harrix_swiss_knife.apps.food.delegates.day_total_delegate import (
    FoodLogDayTotalDelegate,
    apply_food_log_macros_row_heights,
    food_log_macros_row_height,
    food_log_total_column_width,
    macros_button_appearance,
    macros_button_rect,
)
from harrix_swiss_knife.apps.food.food_log_calories import (
    FOOD_LOG_COL_DATE,
    FOOD_LOG_COL_TOTAL_PER_DAY,
    food_log_day_groups,
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


def test_total_column_width_fits_the_widest_macros_button(qapp: QApplication) -> None:  # noqa: ARG001
    font = QFont()
    width = food_log_total_column_width(font)
    metrics = QFontMetrics(font)
    assert width >= metrics.horizontalAdvance("Recalculate macros")
    assert width >= metrics.horizontalAdvance("Analyze macros")
    assert width > metrics.horizontalAdvance("View macros")


def test_macros_button_states_use_distinct_labels_and_colors(qapp: QApplication) -> None:  # noqa: ARG001
    view = macros_button_appearance(DayMacrosStatus.OK)
    stale = macros_button_appearance(DayMacrosStatus.STALE)
    missing = macros_button_appearance(DayMacrosStatus.MISSING)

    assert view.label == "View macros"
    assert stale.label == "Recalculate macros"
    assert missing.label == "Analyze macros"
    assert len({view.label, stale.label, missing.label}) == 3
    assert len({view.background.name(), stale.background.name(), missing.background.name()}) == 3
    assert view.text.name() != stale.text.name()
    assert stale.text.name() != missing.text.name()


def test_macros_button_sits_under_the_calorie_line(qapp: QApplication) -> None:  # noqa: ARG001
    font = QFont()
    cell = QRect(0, 20, 160, 80)
    button = macros_button_rect(cell, font)

    assert button.top() >= cell.top() + QFontMetrics(font).height()
    assert button.height() == 22
    assert button.left() > cell.left()
    assert button.right() < cell.right()


def test_food_log_day_groups_include_single_row_days() -> None:
    dates = ["2026-08-25", "2026-08-25", "2026-08-24", ""]
    assert food_log_day_groups(dates) == [(0, 2), (2, 1)]


def test_day_start_rows_grow_to_fit_the_macros_button(qapp: QApplication) -> None:  # noqa: ARG001
    model = QStandardItemModel()
    model.setColumnCount(7)
    for date in ("2026-08-25", "2026-08-25", "2026-08-24"):
        row = [QStandardItem("") for _ in range(7)]
        row[FOOD_LOG_COL_DATE].setText(date)
        model.appendRow(row)

    view = QTableView()
    view.setModel(model)
    view.verticalHeader().setDefaultSectionSize(24)
    apply_food_log_macros_row_heights(view)

    tall = food_log_macros_row_height(view.font())
    assert view.rowHeight(0) == max(24, tall)
    assert view.rowHeight(1) == 24
    assert view.rowHeight(2) == max(24, tall)


def test_click_on_button_requests_the_day(qapp: QApplication) -> None:  # noqa: ARG001
    model = QStandardItemModel(1, 7)
    model.setData(model.index(0, FOOD_LOG_COL_DATE), "2026-08-25")
    model.setData(model.index(0, FOOD_LOG_COL_TOTAL_PER_DAY), "100")
    delegate = FoodLogDayTotalDelegate()
    option = QStyleOptionViewItem()
    option.rect = QRect(0, 0, 160, 80)
    option.font = QFont()
    button = macros_button_rect(option.rect, option.font)
    received: list[str] = []
    delegate.macros_requested.connect(received.append)
    center = button.center()

    assert delegate.editorEvent(
        _release(QPointF(center)),
        model,
        option,
        model.index(0, FOOD_LOG_COL_TOTAL_PER_DAY),
    )
    assert received == ["2026-08-25"]

    assert not delegate.editorEvent(
        _release(QPointF(8, 4)),
        model,
        option,
        model.index(0, FOOD_LOG_COL_TOTAL_PER_DAY),
    )
    assert received == ["2026-08-25"]


def _release(pos: QPointF) -> QMouseEvent:
    return QMouseEvent(
        QEvent.Type.MouseButtonRelease,
        pos,
        pos.toPoint(),
        Qt.MouseButton.LeftButton,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
    )
