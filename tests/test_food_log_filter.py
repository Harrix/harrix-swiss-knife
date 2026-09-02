"""Tests for food log toolbar filters (name, type, date)."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.apps.food.database_manager import (
    DatabaseManager,
    _filter_rows_by_name,
    _name_matches_filter,
)

RECOVER_SQL = Path(__file__).resolve().parents[1] / "src" / "harrix_swiss_knife" / "apps" / "food" / "recover.sql"


@pytest.fixture(scope="module")
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


@pytest.fixture
def food_db(tmp_path: Path, qapp: QApplication) -> Iterator[DatabaseManager]:  # noqa: ARG001
    db_path = tmp_path / "food.db"
    assert DatabaseManager.create_database_from_sql(str(db_path), str(RECOVER_SQL))
    db = DatabaseManager(str(db_path))
    db.execute_simple_query("DELETE FROM food_log")
    yield db
    db.close()


def test_name_matches_filter_cyrillic_case_insensitive() -> None:
    assert _name_matches_filter("Ветчина Для тостов", None, "Ветчина")
    assert _name_matches_filter("Ветчина Для тостов", None, "ветчина")
    assert _name_matches_filter("Молоко", "Ham toast", "ham")
    assert not _name_matches_filter("Молоко 2.5%", None, "Ветчина")


def test_filter_rows_by_name_searches_name_and_english() -> None:
    rows = [
        [1, "2026-01-01", 50, None, 200, "Ветчина Для тостов", "Ham toast", 0],
        [2, "2026-01-02", 200, None, 50, "Молоко 2.5%", "Milk", 1],
        [3, "2026-01-03", 85, None, 80, "Корм для кошек", "Tuna", 0],
    ]
    filtered = _filter_rows_by_name(rows, "Ветчина")
    assert [row[0] for row in filtered] == [1]
    filtered_en = _filter_rows_by_name(rows, "ham")
    assert [row[0] for row in filtered_en] == [1]


def test_get_filtered_food_log_records_by_type_and_date(food_db: DatabaseManager) -> None:
    assert food_db.add_food_log_record("2026-01-01", name="Bread", weight=50, calories_per_100g=250)
    assert food_db.add_food_log_record("2026-01-02", name="Milk", weight=200, calories_per_100g=50, is_drink=True)
    assert food_db.add_food_log_record("2026-01-03", name="Tea", weight=250, calories_per_100g=1, is_drink=True)

    drinks = food_db.get_filtered_food_log_records(is_drink=1)
    assert [row[5] for row in drinks] == ["Tea", "Milk"]

    january_food = food_db.get_filtered_food_log_records(
        is_drink=0,
        date_from="2026-01-01",
        date_to="2026-01-02",
    )
    assert [row[5] for row in january_food] == ["Bread"]


def test_get_filtered_food_log_records_by_name(food_db: DatabaseManager) -> None:
    assert food_db.add_food_log_record("2026-02-01", name="Ветчина", name_en="Ham", weight=40, calories_per_100g=200)
    assert food_db.add_food_log_record("2026-02-02", name="Молоко", name_en="Milk", weight=200, calories_per_100g=50)

    rows = food_db.get_filtered_food_log_records(name_filter="ветчина")
    assert [row[5] for row in rows] == ["Ветчина"]

    rows_en = food_db.get_filtered_food_log_records(name_filter="milk")
    assert [row[5] for row in rows_en] == ["Молоко"]
