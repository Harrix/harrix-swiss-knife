"""Tests for whole-day calorie totals used by the food log table."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.apps.food.database_manager import DatabaseManager
from harrix_swiss_knife.apps.food.food_log_calories import calculate_food_log_calories

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


def _add_log(
    db: DatabaseManager,
    date: str,
    *,
    weight: float | None = None,
    per_100g: float | None = None,
    portion: float | None = None,
) -> None:
    assert db.execute_simple_query(
        """
        INSERT INTO food_log (date, weight, portion_calories, calories_per_100g, name, is_drink)
        VALUES (:date, :weight, :portion, :per_100g, 'item', 0)
        """,
        {"date": date, "weight": weight, "portion": portion, "per_100g": per_100g},
    )


def test_totals_between_matches_row_calculation(food_db: DatabaseManager) -> None:
    """SQL day totals must equal summing `calculate_food_log_calories` over the rows."""
    _add_log(food_db, "2024-05-01", weight=200.0, per_100g=50.0)
    _add_log(food_db, "2024-05-01", portion=120.0)
    _add_log(food_db, "2024-05-02", weight=150.0, per_100g=80.0)

    totals = food_db.get_calories_totals_between("2024-05-01", "2024-05-02")

    expected_first = calculate_food_log_calories(200.0, 50.0, None) + calculate_food_log_calories(None, None, 120.0)
    assert totals["2024-05-01"] == pytest.approx(expected_first)
    assert totals["2024-05-02"] == pytest.approx(calculate_food_log_calories(150.0, 80.0, None))


def test_totals_between_prefers_portion_calories(food_db: DatabaseManager) -> None:
    """Portion calories win over weight times calories per 100 g, as in Python."""
    _add_log(food_db, "2024-05-03", weight=1000.0, per_100g=900.0, portion=42.0)

    totals = food_db.get_calories_totals_between("2024-05-03", "2024-05-03")

    assert totals["2024-05-03"] == pytest.approx(42.0)


def test_totals_between_is_not_truncated_by_a_row_limit(food_db: DatabaseManager) -> None:
    """A day total must cover the whole day, not just the rows a page would load.

    This is the bug the SQL aggregate fixes: the table previously summed only the loaded
    page, so the day at a page boundary showed a fraction of its real total.
    """
    for _ in range(10):
        _add_log(food_db, "2024-05-04", portion=100.0)

    page = food_db.get_rows("SELECT portion_calories FROM food_log WHERE date = '2024-05-04' LIMIT 3")
    page_sum = sum(float(row[0]) for row in page)
    totals = food_db.get_calories_totals_between("2024-05-04", "2024-05-04")

    assert page_sum == pytest.approx(300.0)
    assert totals["2024-05-04"] == pytest.approx(1000.0)


def test_totals_between_excludes_dates_outside_range(food_db: DatabaseManager) -> None:
    """Only dates inside the inclusive range are returned."""
    _add_log(food_db, "2024-05-05", portion=10.0)
    _add_log(food_db, "2024-06-05", portion=20.0)

    totals = food_db.get_calories_totals_between("2024-05-01", "2024-05-31")

    assert "2024-05-05" in totals
    assert "2024-06-05" not in totals


def test_calories_and_drinks_on_date(food_db: DatabaseManager) -> None:
    """Day summaries for the Today/Yesterday boxes use the same calorie SQL as totals."""
    assert food_db.add_food_log_record(
        "2024-08-01",
        name="Bread",
        weight=200.0,
        calories_per_100g=50.0,
    )
    assert food_db.add_food_log_record(
        "2024-08-01",
        name="Tea",
        weight=500.0,
        calories_per_100g=1.0,
        is_drink=True,
    )
    assert food_db.add_food_log_record(
        "2024-08-02",
        name="Soup",
        portion_calories=300.0,
    )

    assert food_db.get_food_calories_on_date("2024-08-01") == pytest.approx(105.0)
    assert food_db.get_drinks_weight_on_date("2024-08-01") == 500
    assert food_db.get_food_calories_on_date("2024-08-02") == pytest.approx(300.0)
    assert food_db.get_drinks_weight_on_date("2024-08-02") == 0
    assert food_db.get_food_calories_on_date("2024-08-03") == pytest.approx(0.0)


def test_totals_between_agrees_with_calories_per_day(food_db: DatabaseManager) -> None:
    """The bounded aggregate must agree with the all-days aggregate it shares SQL with."""
    _add_log(food_db, "2024-07-01", weight=300.0, per_100g=33.0)
    _add_log(food_db, "2024-07-02", portion=250.0)

    per_day = {str(row[0]): float(row[1]) for row in food_db.get_calories_per_day()}
    totals = food_db.get_calories_totals_between("2024-07-01", "2024-07-02")

    assert totals["2024-07-01"] == pytest.approx(per_day["2024-07-01"])
    assert totals["2024-07-02"] == pytest.approx(per_day["2024-07-02"])
