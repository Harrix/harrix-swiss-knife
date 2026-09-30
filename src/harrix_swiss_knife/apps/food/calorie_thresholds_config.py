"""Read / write Food calorie threshold setup state in `config.json`."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import replace
from pathlib import Path
from typing import TYPE_CHECKING, Any

import harrix_pylib as h

from harrix_swiss_knife.apps.food.calorie_thresholds_calc import (
    PersonProfile,
    person_profile_from_mapping,
    person_profile_to_mapping,
    thresholds_to_mapping,
)
from harrix_swiss_knife.paths import get_config_path_str

if TYPE_CHECKING:
    from harrix_swiss_knife.apps.food.day_macros import CalorieThresholds

FOOD_CALORIE_THRESHOLDS_KEY = "food_calorie_thresholds"
FOOD_CALORIE_THRESHOLDS_CONFIGURED_KEY = "food_calorie_thresholds_configured"
FOOD_PERSON_PROFILE_KEY = "food_person_profile"

_WEIGHT_KG_MIN = 30.0
_WEIGHT_KG_MAX = 300.0


def food_calorie_thresholds_are_configured(config: dict[str, Any] | None) -> bool:
    """Return whether the user has confirmed calorie bands at least once."""
    if not isinstance(config, dict):
        return False
    return bool(config.get(FOOD_CALORIE_THRESHOLDS_CONFIGURED_KEY))


def load_food_person_profile(config: dict[str, Any] | None) -> PersonProfile | None:
    """Return the stored body-metrics profile, if any."""
    if not isinstance(config, dict):
        return None
    return person_profile_from_mapping(config.get(FOOD_PERSON_PROFILE_KEY))


def load_food_person_profile_for_setup(config: dict[str, Any] | None) -> PersonProfile | None:
    """Return the setup profile, preferring the latest Fitness weight when available."""
    profile = load_food_person_profile(config)
    fitness_weight = load_latest_fitness_weight_kg(config)
    if fitness_weight is None:
        return profile
    if profile is None:
        return PersonProfile(sex="male", age=30, height_cm=175.0, weight_kg=fitness_weight)
    return replace(profile, weight_kg=fitness_weight)


def load_latest_fitness_weight_kg(config: dict[str, Any] | None) -> float | None:
    """Return the newest body weight from Fitness `weight`, or `None` when unavailable."""
    if not isinstance(config, dict):
        return None
    raw = str(config.get("sqlite_fitness") or "").strip()
    if not raw:
        return None
    path = Path(raw)
    if not path.is_file():
        return None
    try:
        connection = sqlite3.connect(str(path))
        try:
            connection.execute("PRAGMA query_only = ON")
            row = connection.execute(
                "SELECT value FROM weight ORDER BY date DESC, _id DESC LIMIT 1",
            ).fetchone()
        finally:
            connection.close()
    except sqlite3.Error:
        return None
    if not row or row[0] is None:
        return None
    try:
        value = float(row[0])
    except (TypeError, ValueError):
        return None
    if value < _WEIGHT_KG_MIN or value > _WEIGHT_KG_MAX:
        return None
    return value


def save_food_calorie_threshold_setup(
    *,
    thresholds: CalorieThresholds,
    profile: PersonProfile,
    config_path: str | None = None,
) -> dict[str, Any]:
    """Persist bands, profile, and the configured flag; return the updated config."""
    path = Path(config_path or get_config_path_str())
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        msg = f"Config root must be a JSON object: {path}"
        raise TypeError(msg)
    data[FOOD_CALORIE_THRESHOLDS_KEY] = thresholds_to_mapping(thresholds)
    data[FOOD_CALORIE_THRESHOLDS_CONFIGURED_KEY] = True
    data[FOOD_PERSON_PROFILE_KEY] = person_profile_to_mapping(profile)
    path.write_text(h.dev.dumps_pretty_json(data), encoding="utf-8")
    return data
