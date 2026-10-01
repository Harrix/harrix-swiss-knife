"""Tests for local food-log calorie recalculation."""

from __future__ import annotations

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QApplication, QTableView

from harrix_swiss_knife.apps.food.food_log_calories import (
    FOOD_LOG_COL_DATE,
    FOOD_LOG_COL_TOTAL_PER_DAY,
    FOOD_LOG_COL_WEIGHT,
    apply_food_log_day_spans,
    calculate_food_log_calories,
    calories_per_100g_for_storage,
    convert_calories_per_100g_to_portion,
    convert_portion_to_calories_per_100g,
    food_log_day_row_spans,
    parse_food_log_number,
    refresh_food_log_calorie_columns,
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


def test_weight_mode_uses_calories_per_100g() -> None:
    assert calculate_food_log_calories(weight=200, calories_per_100g=50) == 100


def test_zero_calories_per_100g() -> None:
    assert calculate_food_log_calories(weight=100, calories_per_100g=0) == 0


def test_calories_per_100g_for_storage_keeps_zero_when_requested() -> None:
    assert calories_per_100g_for_storage(0, keep_zero=True) == 0.0
    assert calories_per_100g_for_storage(0, keep_zero=False) is None
    assert calories_per_100g_for_storage(12.5) == 12.5
    assert calories_per_100g_for_storage(-1) is None
    assert calories_per_100g_for_storage(None) is None


def test_convert_portion_to_calories_per_100g() -> None:
    assert convert_portion_to_calories_per_100g(weight=200, portion_calories=300) == 150.0
    assert convert_portion_to_calories_per_100g(weight=150, portion_calories=100) == 66.7


def test_convert_calories_per_100g_to_portion() -> None:
    assert convert_calories_per_100g_to_portion(weight=200, calories_per_100g=150) == 300.0
    assert convert_calories_per_100g_to_portion(weight=70, calories_per_100g=33.3) == 23.3
    assert convert_calories_per_100g_to_portion(weight=150, calories_per_100g=66.7) == 100.0


def test_parse_food_log_number_rejects_empty() -> None:
    assert parse_food_log_number("") is None
    assert parse_food_log_number(None) is None
    assert parse_food_log_number("12.5") == 12.5


def test_refresh_food_log_calorie_columns_updates_day_total(qapp: QApplication) -> None:  # noqa: ARG001
    model = QStandardItemModel()
    model.setColumnCount(7)
    first = [_item(value) for value in ["Soup", "", "200", "50", "2026-08-25", "", ""]]
    second = [_item(value) for value in ["Bread", "", "100", "80", "2026-08-25", "", ""]]
    other = [_item(value) for value in ["Tea", "1", "250", "4", "2026-08-24", "", ""]]
    model.appendRow(first)
    model.appendRow(second)
    model.appendRow(other)

    first[FOOD_LOG_COL_WEIGHT].setText("100")
    totals = refresh_food_log_calorie_columns(model)

    assert totals["2026-08-25"] == 130.0
    assert model.item(0, FOOD_LOG_COL_TOTAL_PER_DAY).text() == "130.0"
    assert model.item(1, FOOD_LOG_COL_TOTAL_PER_DAY).text() == ""
    assert totals["2026-08-24"] == 10.0


def test_food_log_day_row_spans_groups_consecutive_days() -> None:
    dates = ["2026-08-25", "2026-08-25", "2026-08-24", "2026-08-24", "2026-08-24", "2026-08-23"]
    assert food_log_day_row_spans(dates) == [(0, 2), (2, 3)]
    assert food_log_day_row_spans(["2026-08-25"]) == []
    assert food_log_day_row_spans(["", ""]) == []


def test_apply_food_log_day_spans_merges_total_column(qapp: QApplication) -> None:  # noqa: ARG001
    model = QStandardItemModel()
    model.setColumnCount(7)
    for date, total in (
        ("2026-08-25", "130.0"),
        ("2026-08-25", ""),
        ("2026-08-24", "10.0"),
        ("2026-08-24", ""),
        ("2026-08-24", ""),
    ):
        row = [_item("") for _ in range(7)]
        row[FOOD_LOG_COL_DATE].setText(date)
        row[FOOD_LOG_COL_TOTAL_PER_DAY].setText(total)
        model.appendRow(row)

    view = QTableView()
    view.setModel(model)
    apply_food_log_day_spans(view)

    assert view.rowSpan(0, FOOD_LOG_COL_TOTAL_PER_DAY) == 2
    assert view.rowSpan(2, FOOD_LOG_COL_TOTAL_PER_DAY) == 3
    assert _vertical_alignment(model, 0) == Qt.AlignmentFlag.AlignTop
    assert _vertical_alignment(model, 2) == Qt.AlignmentFlag.AlignTop

    model.item(2, FOOD_LOG_COL_DATE).setText("2026-08-23")
    apply_food_log_day_spans(view)
    assert view.rowSpan(0, FOOD_LOG_COL_TOTAL_PER_DAY) == 2
    assert view.rowSpan(2, FOOD_LOG_COL_TOTAL_PER_DAY) == 1
    assert view.rowSpan(3, FOOD_LOG_COL_TOTAL_PER_DAY) == 2
    assert _vertical_alignment(model, 0) == Qt.AlignmentFlag.AlignTop
    assert _vertical_alignment(model, 2) == Qt.AlignmentFlag.AlignVCenter
    assert _vertical_alignment(model, 3) == Qt.AlignmentFlag.AlignTop


def _item(value: str) -> QStandardItem:
    return QStandardItem(value)


def _vertical_alignment(model: QStandardItemModel, row: int) -> Qt.AlignmentFlag:
    item = model.item(row, FOOD_LOG_COL_TOTAL_PER_DAY)
    assert item is not None
    return item.textAlignment() & Qt.AlignmentFlag.AlignVertical_Mask
