"""Tests for Food day macros hash, parser, status, and schema migration."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from harrix_swiss_knife.apps.food.day_macros import (
    CalorieThresholds,
    DayMacrosStatus,
    FoodDayLogLine,
    FoodDayMacrosAnalysis,
    calorie_band_rgb,
    food_day_input_hash,
    format_day_menu_for_prompt,
    kcal_tone,
    macro_tone,
    parse_day_macros_response,
    parse_range_macros_response,
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


def test_parse_day_macros_response_bilingual() -> None:
    text = (
        "95.5\t60\t200.25\t1800\n"
        "100\t70\t250\t2100\n"
        "VERDICT_EN: Low protein\n"
        "VERDICT: Мало белка\n"
        "EN:\n"
        "Add **eggs**.\n"
        "\n"
        "Calories are in the medium band.\n"
        "LOCAL:\n"
        "Добавьте **яйца**.\n"
        "\n"
        "Калории в среднем диапазоне."
    )
    result = parse_day_macros_response(text)
    assert result is not None
    assert result.protein_g == 95.5
    assert result.norm_kcal == 2100.0
    assert "Low protein" in result.verdict_en
    assert "Мало белка" in result.verdict
    assert "**eggs**" in result.notes_en
    assert "**яйца**" in result.notes
    assert "\n\n" in result.notes_en
    assert "Calories" in result.notes_en


def test_parse_day_macros_response_rejects_bad_output() -> None:
    assert parse_day_macros_response("") is None
    assert parse_day_macros_response("a\tb\tc\td") is None
    assert parse_day_macros_response("10\t20\t30\t40") is None
    assert parse_day_macros_response("-1\t0\t0\t0\n1\t1\t1\t1") is None


def test_parse_range_macros_response() -> None:
    text = (
        "VERDICT_EN: Period balanced\n"
        "VERDICT: Период в балансе\n"
        "EN:\n"
        "Heavy day offset by light days.\n"
        "LOCAL:\n"
        "Тяжёлый день компенсирован лёгкими."
    )
    result = parse_range_macros_response(text)
    assert result is not None
    assert "balanced" in result.verdict_en
    assert "балансе" in result.verdict
    assert "offset" in result.notes_en


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
        verdict_en="",
        notes_en="",
    )
    assert resolve_day_macros_status(analysis, "abc") is DayMacrosStatus.OK
    assert resolve_day_macros_status(analysis, "xyz") is DayMacrosStatus.STALE


def test_percent_and_tones() -> None:
    assert percent_of_norm(50, 100) == 50.0
    assert percent_of_norm(10, 0) is None
    assert macro_tone(100, 100) == "good"
    assert macro_tone(50, 100) == "bad"
    assert kcal_tone(1700, CalorieThresholds()) == "good"
    assert kcal_tone(3000, CalorieThresholds()) == "bad"


def test_calorie_band_rgb_matches_thresholds() -> None:
    thresholds = CalorieThresholds(low=1800, medium_low=2100, medium_high=2500)
    assert calorie_band_rgb(1700, thresholds) == (144, 238, 144)
    assert calorie_band_rgb(1800, thresholds) == (144, 238, 144)
    assert calorie_band_rgb(2000, thresholds) == (255, 255, 224)
    assert calorie_band_rgb(2300, thresholds) == (255, 228, 196)
    assert calorie_band_rgb(2600, thresholds) == (255, 192, 203)


def test_format_day_menu_for_prompt_includes_total() -> None:
    lines = [
        FoodDayLogLine("Рис", "Rice", 100.0, None, 130.0, is_drink=False),
    ]
    menu = format_day_menu_for_prompt(lines, total_kcal=130.0)
    assert "Рис" in menu
    assert "130.0 kcal" in menu
    assert "Total kcal" in menu


def test_ensure_food_schema_creates_day_and_range_analysis(tmp_path: Path) -> None:
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
        assert _table_exists(conn, "food_range_nutrition_analysis")
        cols = {row[1] for row in conn.execute("PRAGMA table_info(food_day_nutrition_analysis)")}
        assert {"verdict_en", "notes_en", "norm_protein_g"}.issubset(cols)


def test_ensure_food_schema_adds_bilingual_columns(tmp_path: Path) -> None:
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
                norm_protein_g REAL NOT NULL,
                norm_fat_g REAL NOT NULL,
                norm_carb_g REAL NOT NULL,
                norm_kcal REAL NOT NULL,
                verdict TEXT NOT NULL DEFAULT '',
                notes TEXT NOT NULL DEFAULT '',
                input_hash TEXT NOT NULL,
                analyzed_at TEXT NOT NULL,
                prompt_key TEXT NOT NULL DEFAULT 'food_day_macros'
            );
            """
        )
        conn.execute(
            """
            INSERT INTO food_day_nutrition_analysis (
                date, protein_g, fat_g, carb_g, kcal,
                norm_protein_g, norm_fat_g, norm_carb_g, norm_kcal,
                verdict, notes, input_hash, analyzed_at
            ) VALUES ('2026-01-01', 1, 2, 3, 4, 10, 20, 30, 40, 'v', 'n', 'h', 't')
            """
        )
        conn.commit()

    assert ensure_food_schema(db_path) is True
    with sqlite3.connect(str(db_path)) as conn:
        cols = {row[1] for row in conn.execute("PRAGMA table_info(food_day_nutrition_analysis)")}
        assert "verdict_en" in cols
        assert "notes_en" in cols
        row = conn.execute("SELECT verdict, notes FROM food_day_nutrition_analysis").fetchone()
        assert row == ("v", "n")


def _table_exists(conn: sqlite3.Connection, table: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ? LIMIT 1",
        (table,),
    ).fetchone()
    return row is not None
