"""Tests for Food calorie-threshold estimation and config persistence."""

from __future__ import annotations

import json
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
    food_calorie_thresholds_are_configured,
    load_food_person_profile,
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
    profile = PersonProfile(sex="female", age=42, height_cm=168.5, weight_kg=61.2, activity="light")
    restored = person_profile_from_mapping(person_profile_to_mapping(profile))
    assert restored == profile


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
    )

    assert updated["food_calorie_thresholds_configured"] is True
    assert updated["food_calorie_thresholds"] == {"low": 2000, "medium_low": 2400, "medium_high": 2900}
    assert load_food_person_profile(updated) == profile
    written = json.loads(config_path.read_text(encoding="utf-8"))
    assert written["food_calorie_thresholds_configured"] is True
    assert written["food_person_profile"]["age"] == 35
