"""Tests for Food day macros hash, parser, status, and schema migration."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from harrix_swiss_knife.apps.food.day_macros import (
    DayMacrosStatus,
    FoodDayLogLine,
    FoodDayMacrosAnalysis,
    food_day_input_hash,
    format_day_menu_for_prompt,
    parse_day_macros_response,
    percent_of_norm,
    resolve_day_macros_status,
)
from harrix_swiss_knife.apps.food.schema import ensure_food_schema


def test_food_day_input_hash_stable_and_sensitive_to_weight() -> None:
    line = FoodDayLogLine(
        name="Oatmeal",
        name_en="Oatmeal",
        weight=200.0,
        portion_calories=None,
        calories_per_100g=68.0,
        is_drink=False,
    )
    first = food_day_input_hash([line])
    second = food_day_input_hash([line])
    assert first == second
    changed = FoodDayLogLine(
        name="Oatmeal",
        name_en="Oatmeal",
        weight=250.0,
        portion_calories=None,
        calories_per_100g=68.0,
        is_drink=False,
    )
    assert food_day_input_hash([changed]) != first


def test_food_day_input_hash_order_independent() -> None:
    a = FoodDayLogLine("A", "", 10.0, None, 100.0, is_drink=False)
    b = FoodDayLogLine("B", "", 20.0, 50.0, None, is_drink=True)
    assert food_day_input_hash([a, b]) == food_day_input_hash([b, a])


def test_parse_day_macros_response_happy_path() -> None:
    text = (
        "95.5\t60\t200.25\t1800\n100\t70\t250\t2100\nVERDICT: Low protein relative to the day norm\nAdd eggs or fish."
    )
    result = parse_day_macros_response(text)
    assert result is not None
    assert result.protein_g == 95.5
    assert result.fat_g == 60.0
    assert result.carb_g == 200.25
    assert result.kcal == 1800.0
    assert result.norm_protein_g == 100.0
    assert result.norm_fat_g == 70.0
    assert result.norm_carb_g == 250.0
    assert result.norm_kcal == 2100.0
    assert "Low protein" in result.verdict
    assert "eggs" in result.notes


def test_parse_day_macros_response_rejects_bad_output() -> None:
    assert parse_day_macros_response("") is None
    assert parse_day_macros_response("a\tb\tc\td") is None
    assert parse_day_macros_response("10\t20\t30\t40") is None  # missing norms line
    assert parse_day_macros_response("-1\t0\t0\t0\n1\t1\t1\t1") is None
    assert parse_day_macros_response("10\t20\t30\n10\t20\t30\t40") is None


def test_resolve_day_macros_status() -> None:
    assert resolve_day_macros_status(None, "abc") is DayMacrosStatus.MISSING
    analysis = FoodDayMacrosAnalysis(
        date="2026-01-01",
        protein_g=1,
        fat_g=2,
        carb_g=3,
        kcal=40,
        norm_protein_g=10,
        norm_fat_g=20,
        norm_carb_g=30,
        norm_kcal=400,
        verdict="",
        notes="",
        input_hash="abc",
        analyzed_at="2026-01-01T00:00:00+00:00",
    )
    assert resolve_day_macros_status(analysis, "abc") is DayMacrosStatus.OK
    assert resolve_day_macros_status(analysis, "xyz") is DayMacrosStatus.STALE


def test_percent_of_norm() -> None:
    assert percent_of_norm(50, 100) == 50.0
    assert percent_of_norm(10, 0) is None


def test_format_day_menu_for_prompt_includes_total() -> None:
    lines = [
        FoodDayLogLine("Рис", "Rice", 100.0, None, 130.0, is_drink=False),
    ]
    menu = format_day_menu_for_prompt(lines, total_kcal=130.0)
    assert "Рис" in menu
    assert "130.0 kcal" in menu
    assert "Total kcal" in menu


def test_ensure_food_schema_creates_day_nutrition_analysis(tmp_path: Path) -> None:
    db_path = tmp_path / "food_macros.db"
    with sqlite3.connect(str(db_path)) as conn:
        conn.executescript(
            """
            CREATE TABLE food_items (
                _id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                name_en TEXT,
                is_drink INTEGER NOT NULL DEFAULT 0,
                calories_per_100g REAL,
                default_portion_weight REAL,
                default_portion_calories REAL
            );
            CREATE TABLE food_log (
                _id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                weight REAL,
                portion_calories REAL,
                calories_per_100g REAL,
                name TEXT,
                name_en TEXT,
                is_drink INTEGER NOT NULL DEFAULT 0
            );
            """
        )
        conn.commit()

    assert ensure_food_schema(db_path) is True
    assert ensure_food_schema(db_path) is False

    with sqlite3.connect(str(db_path)) as conn:
        assert _table_exists(conn, "food_day_nutrition_analysis")
        cols = {row[1] for row in conn.execute("PRAGMA table_info(food_day_nutrition_analysis)")}
        assert {
            "protein_g",
            "norm_protein_g",
            "verdict",
            "input_hash",
        }.issubset(cols)


def test_ensure_food_schema_upgrades_legacy_day_analysis_table(tmp_path: Path) -> None:
    db_path = tmp_path / "food_legacy_macros.db"
    with sqlite3.connect(str(db_path)) as conn:
        conn.executescript(
            """
            CREATE TABLE food_items (
                _id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                name_en TEXT,
                is_drink INTEGER NOT NULL DEFAULT 0,
                calories_per_100g REAL,
                default_portion_weight REAL,
                default_portion_calories REAL
            );
            CREATE TABLE food_log (
                _id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                weight REAL,
                portion_calories REAL,
                calories_per_100g REAL,
                name TEXT,
                name_en TEXT,
                is_drink INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE food_day_nutrition_analysis (
                date TEXT PRIMARY KEY NOT NULL,
                protein_g REAL NOT NULL,
                fat_g REAL NOT NULL,
                carb_g REAL NOT NULL,
                kcal REAL NOT NULL,
                notes TEXT NOT NULL DEFAULT '',
                input_hash TEXT NOT NULL,
                analyzed_at TEXT NOT NULL,
                prompt_key TEXT NOT NULL DEFAULT 'food_day_macros'
            );
            """
        )
        conn.commit()

    assert ensure_food_schema(db_path) is True
    with sqlite3.connect(str(db_path)) as conn:
        cols = {row[1] for row in conn.execute("PRAGMA table_info(food_day_nutrition_analysis)")}
        assert "norm_protein_g" in cols
        assert "verdict" in cols


def _table_exists(conn: sqlite3.Connection, table: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ? LIMIT 1",
        (table,),
    ).fetchone()
    return row is not None
