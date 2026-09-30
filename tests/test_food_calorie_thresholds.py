"""Tests for Food calorie-threshold estimation and config persistence."""

from __future__ import annotations

import json
import sqlite3
from datetime import date
from pathlib import Path

import pytest

from harrix_swiss_knife.apps.food.calorie_thresholds_calc import (
    PersonProfile,
    estimate_calorie_bands,
    mifflin_st_jeor_bmr,
    person_profile_from_mapping,
    person_profile_to_mapping,
    round_kcal,
)
from harrix_swiss_knife.apps.food.calorie_thresholds_config import (
    StoredAgeHeight,
    estimate_age_from_recorded,
    food_calorie_thresholds_are_configured,
    load_food_person_age_height,
    load_food_person_profile,
    load_food_person_profile_for_setup,
    load_latest_fitness_weight_kg,
    resolve_age_for_save,
    save_food_calorie_threshold_setup,
)
from harrix_swiss_knife.apps.food.day_macros import CalorieThresholds


def test_mifflin_st_jeor_bmr_male_and_female() -> None:
    male = PersonProfile(sex="male", age=30, height_cm=175.0, weight_kg=70.0)
    female = PersonProfile(sex="female", age=30, height_cm=175.0, weight_kg=70.0)
    assert mifflin_st_jeor_bmr(male) == pytest.approx(1648.75)
    assert mifflin_st_jeor_bmr(female) == pytest.approx(1482.75)


def test_estimate_calorie_bands_uses_tdee_ratios() -> None:
    profile = PersonProfile(sex="male", age=30, height_cm=175.0, weight_kg=70.0, activity="moderate")
    estimate = estimate_calorie_bands(profile)
    assert estimate.tdee == pytest.approx(estimate.bmr * 1.55)
    assert estimate.thresholds.low == float(round_kcal(estimate.tdee * 0.85))
    assert estimate.thresholds.medium_low == float(round_kcal(estimate.tdee))
    assert estimate.thresholds.medium_high == float(round_kcal(estimate.tdee * 1.2))
    assert estimate.thresholds.low < estimate.thresholds.medium_low < estimate.thresholds.medium_high


def test_round_kcal_steps_and_minimum() -> None:
    assert round_kcal(2124) == 2100
    assert round_kcal(2175) == 2200
    assert round_kcal(10) == 50


def test_person_profile_round_trip() -> None:
    profile = PersonProfile(
        sex="female",
        age=42,
        height_cm=168.5,
        weight_kg=61.2,
        activity="light",
        want_to_lose_weight=True,
    )
    restored = person_profile_from_mapping(person_profile_to_mapping(profile))
    assert restored == profile


def test_estimate_calorie_bands_lose_weight_scales_down() -> None:
    base = PersonProfile(sex="male", age=30, height_cm=175.0, weight_kg=70.0, activity="moderate")
    lose = PersonProfile(
        sex="male",
        age=30,
        height_cm=175.0,
        weight_kg=70.0,
        activity="moderate",
        want_to_lose_weight=True,
    )
    maintenance = estimate_calorie_bands(base)
    deficit = estimate_calorie_bands(lose)
    assert deficit.tdee == pytest.approx(maintenance.tdee)
    assert deficit.thresholds.low == float(round_kcal(maintenance.tdee * 0.85 * 0.85))
    assert deficit.thresholds.medium_low == float(round_kcal(maintenance.tdee * 0.85))
    assert deficit.thresholds.medium_high == float(round_kcal(maintenance.tdee * 1.2 * 0.85))
    assert deficit.thresholds.low < maintenance.thresholds.low
    assert deficit.thresholds.medium_low < maintenance.thresholds.medium_low
    assert deficit.thresholds.medium_high < maintenance.thresholds.medium_high


def test_person_profile_from_mapping_rejects_invalid() -> None:
    assert person_profile_from_mapping(None) is None
    assert person_profile_from_mapping({"sex": "male"}) is None
    assert person_profile_from_mapping({"sex": "other", "age": 30, "height_cm": 170, "weight_kg": 70}) is None


def test_food_calorie_thresholds_are_configured_flag() -> None:
    assert not food_calorie_thresholds_are_configured(None)
    assert not food_calorie_thresholds_are_configured({})
    assert not food_calorie_thresholds_are_configured({"food_calorie_thresholds_configured": False})
    assert food_calorie_thresholds_are_configured({"food_calorie_thresholds_configured": True})


def test_save_food_calorie_threshold_setup_writes_flag_profile_and_bands(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "food_calorie_thresholds": {"low": 1800, "medium_low": 2100, "medium_high": 2500},
                "food_calorie_thresholds_configured": False,
            },
        ),
        encoding="utf-8",
    )
    profile = PersonProfile(sex="male", age=35, height_cm=180.0, weight_kg=80.0, activity="active")
    thresholds = CalorieThresholds(low=2000.0, medium_low=2400.0, medium_high=2900.0)

    updated = save_food_calorie_threshold_setup(
        thresholds=thresholds,
        profile=profile,
        config_path=str(config_path),
        today=date(2026, 3, 15),
    )

    assert updated["food_calorie_thresholds_configured"] is True
    assert updated["food_calorie_thresholds"] == {"low": 2000, "medium_low": 2400, "medium_high": 2900}
    assert load_food_person_profile(updated) == profile
    written = json.loads(config_path.read_text(encoding="utf-8"))
    assert written["food_calorie_thresholds_configured"] is True
    assert written["food_person_profile"]["age"] == 35
    stored = load_food_person_age_height(config_path=str(config_path))
    assert stored == StoredAgeHeight(age=35, height_cm=180.0, age_recorded_on=date(2026, 3, 15))


def test_estimate_age_from_recorded_advances_on_anniversary() -> None:
    recorded = date(2024, 6, 10)
    assert estimate_age_from_recorded(30, recorded, today=date(2024, 6, 9)) == 30
    assert estimate_age_from_recorded(30, recorded, today=date(2024, 6, 10)) == 30
    assert estimate_age_from_recorded(30, recorded, today=date(2025, 6, 9)) == 30
    assert estimate_age_from_recorded(30, recorded, today=date(2025, 6, 10)) == 31
    assert estimate_age_from_recorded(30, recorded, today=date(2027, 6, 11)) == 33


def test_resolve_age_for_save_keeps_base_when_estimate_matches() -> None:
    previous = StoredAgeHeight(age=30, height_cm=175.0, age_recorded_on=date(2024, 1, 1))
    age, recorded = resolve_age_for_save(31, previous, today=date(2025, 1, 1))
    assert age == 30
    assert recorded == date(2024, 1, 1)
    age, recorded = resolve_age_for_save(40, previous, today=date(2025, 1, 1))
    assert age == 40
    assert recorded == date(2025, 1, 1)


def test_load_food_person_profile_for_setup_estimates_age_from_temp(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "food_person_profile": {
                    "sex": "female",
                    "age": 40,
                    "height_cm": 160,
                    "weight_kg": 70,
                    "activity": "light",
                },
            },
        ),
        encoding="utf-8",
    )
    (tmp_path / "config-temp.json").write_text(
        json.dumps(
            {
                "food_person_age_height": {
                    "age": 40,
                    "height_cm": 165.5,
                    "age_recorded_on": "2024-09-30",
                },
            },
        ),
        encoding="utf-8",
    )
    profile = load_food_person_profile_for_setup(
        json.loads(config_path.read_text(encoding="utf-8")),
        config_path=str(config_path),
        today=date(2026, 9, 30),
    )
    assert profile is not None
    assert profile.sex == "female"
    assert profile.age == 42
    assert profile.height_cm == pytest.approx(165.5)


def test_save_keeps_age_recorded_on_when_estimated_age_unchanged(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text("{}", encoding="utf-8")
    profile = PersonProfile(sex="male", age=35, height_cm=180.0, weight_kg=80.0)
    thresholds = CalorieThresholds(low=2000.0, medium_low=2400.0, medium_high=2900.0)
    save_food_calorie_threshold_setup(
        thresholds=thresholds,
        profile=profile,
        config_path=str(config_path),
        today=date(2024, 3, 1),
    )
    save_food_calorie_threshold_setup(
        thresholds=thresholds,
        profile=PersonProfile(sex="male", age=36, height_cm=181.0, weight_kg=80.0),
        config_path=str(config_path),
        today=date(2025, 3, 1),
    )
    stored = load_food_person_age_height(config_path=str(config_path))
    assert stored == StoredAgeHeight(age=35, height_cm=181.0, age_recorded_on=date(2024, 3, 1))


def test_load_latest_fitness_weight_kg_uses_newest_row(tmp_path: Path) -> None:
    db_path = tmp_path / "fitness.db"
    connection = sqlite3.connect(str(db_path))
    try:
        connection.execute("CREATE TABLE weight (_id INTEGER PRIMARY KEY, value REAL, date TEXT)")
        connection.execute("INSERT INTO weight (value, date) VALUES (81.2, '2026-01-01')")
        connection.execute("INSERT INTO weight (value, date) VALUES (79.4, '2026-03-15')")
        connection.execute("INSERT INTO weight (value, date) VALUES (80.1, '2026-02-01')")
        connection.commit()
    finally:
        connection.close()

    assert load_latest_fitness_weight_kg({"sqlite_fitness": str(db_path)}) == pytest.approx(79.4)
    assert load_latest_fitness_weight_kg({"sqlite_fitness": str(tmp_path / "missing.db")}) is None
    assert load_latest_fitness_weight_kg({}) is None


def test_load_food_person_profile_for_setup_prefers_fitness_weight(tmp_path: Path) -> None:
    db_path = tmp_path / "fitness.db"
    connection = sqlite3.connect(str(db_path))
    try:
        connection.execute("CREATE TABLE weight (_id INTEGER PRIMARY KEY, value REAL, date TEXT)")
        connection.execute("INSERT INTO weight (value, date) VALUES (88.5, '2026-09-01')")
        connection.commit()
    finally:
        connection.close()

    config = {
        "sqlite_fitness": str(db_path),
        "food_person_profile": {
            "sex": "female",
            "age": 40,
            "height_cm": 165,
            "weight_kg": 70,
            "activity": "light",
        },
    }
    profile = load_food_person_profile_for_setup(config, config_path=str(tmp_path / "config.json"))
    assert profile is not None
    assert profile.sex == "female"
    assert profile.age == 40
    assert profile.weight_kg == pytest.approx(88.5)
