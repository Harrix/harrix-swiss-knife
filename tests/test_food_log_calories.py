"""Tests for local food-log calorie recalculation."""

from __future__ import annotations

import pytest
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.apps.food.food_log_calories import (
    FOOD_LOG_COL_CALCULATED,
    FOOD_LOG_COL_TOTAL_PER_DAY,
    FOOD_LOG_COL_WEIGHT,
    calculate_food_log_calories,
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


def test_portion_calories_win_over_weight_mode() -> None:
    assert calculate_food_log_calories(weight=200, calories_per_100g=50, portion_calories=300) == 300


def test_weight_mode_uses_calories_per_100g() -> None:
    assert calculate_food_log_calories(weight=200, calories_per_100g=50, portion_calories=None) == 100


def test_zero_portion_falls_back_to_weight_mode() -> None:
    assert calculate_food_log_calories(weight=100, calories_per_100g=80, portion_calories=0) == 80


def test_parse_food_log_number_rejects_empty() -> None:
    assert parse_food_log_number("") is None
    assert parse_food_log_number(None) is None
    assert parse_food_log_number("12.5") == 12.5


def test_refresh_food_log_calorie_columns_updates_day_total(qapp: QApplication) -> None:  # noqa: ARG001
    model = QStandardItemModel()
    model.setColumnCount(9)
    first = [_item(value) for value in ["Soup", "", "200", "50", "", "0.0", "2026-08-25", "", ""]]
    second = [_item(value) for value in ["Bread", "", "100", "80", "", "0.0", "2026-08-25", "", ""]]
    other = [_item(value) for value in ["Tea", "1", "250", "", "10", "10.0", "2026-08-24", "", "10.0"]]
    model.appendRow(first)
    model.appendRow(second)
    model.appendRow(other)

    first[FOOD_LOG_COL_WEIGHT].setText("100")
    totals = refresh_food_log_calorie_columns(model)

    assert totals["2026-08-25"] == 130.0
    assert model.item(0, FOOD_LOG_COL_CALCULATED).text() == "50.0"
    assert model.item(1, FOOD_LOG_COL_CALCULATED).text() == "80.0"
    assert model.item(0, FOOD_LOG_COL_TOTAL_PER_DAY).text() == "130.0"
    assert model.item(1, FOOD_LOG_COL_TOTAL_PER_DAY).text() == ""
    assert model.item(2, FOOD_LOG_COL_TOTAL_PER_DAY).text() == "10.0"


def _item(value: str) -> QStandardItem:
    return QStandardItem(value)
