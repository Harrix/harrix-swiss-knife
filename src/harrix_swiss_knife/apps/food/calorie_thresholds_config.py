"""Read / write Food calorie threshold setup state in `config.json`."""

from __future__ import annotations

import json
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
