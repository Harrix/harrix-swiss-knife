"""Read / write Food calorie threshold setup state in config files.

Bands and the full person profile stay in `config.json`. Age, height, and the
date when age was recorded are also kept in `config-temp.json` so the next setup
can estimate age from elapsed time since that date.

"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, replace
from datetime import UTC, date, datetime
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
FOOD_PERSON_AGE_HEIGHT_KEY = "food_person_age_height"

_WEIGHT_KG_MIN = 30.0
_WEIGHT_KG_MAX = 300.0
_AGE_MIN = 10
_AGE_MAX = 120
_HEIGHT_CM_MIN = 100.0
_HEIGHT_CM_MAX = 250.0


@dataclass(frozen=True, slots=True)
class StoredAgeHeight:
    """Age and height snapshot from `config-temp.json`."""

    age: int
    height_cm: float
    age_recorded_on: date


def estimate_age_from_recorded(
    stored_age: int,
    recorded_on: date,
    *,
    today: date | None = None,
) -> int:
    """Return age advanced by whole years since `recorded_on` (anniversary-style)."""
    current = today or datetime.now(UTC).astimezone().date()
    if current < recorded_on:
        return _clamp_age(stored_age)
    years = current.year - recorded_on.year
    if (current.month, current.day) < (recorded_on.month, recorded_on.day):
        years -= 1
    return _clamp_age(stored_age + max(0, years))


def food_calorie_thresholds_are_configured(config: dict[str, Any] | None) -> bool:
    """Return whether the user has confirmed calorie bands at least once."""
    if not isinstance(config, dict):
        return False
    return bool(config.get(FOOD_CALORIE_THRESHOLDS_CONFIGURED_KEY))


def load_food_person_age_height(
    *,
    config_path: str | None = None,
) -> StoredAgeHeight | None:
    """Return age / height / age-recorded date from `config-temp.json`, if any."""
    path_str = config_path or get_config_path_str()
    try:
        loaded: dict[str, Any] = h.dev.config_load(path_str, is_temp=True, resolve_snippets=False)
    except (FileNotFoundError, OSError, TypeError, ValueError, json.JSONDecodeError):
        return None
    if not isinstance(loaded, dict):
        return None
    return _stored_age_height_from_mapping(loaded.get(FOOD_PERSON_AGE_HEIGHT_KEY))


def load_food_person_profile(config: dict[str, Any] | None) -> PersonProfile | None:
    """Return the stored body-metrics profile, if any."""
    if not isinstance(config, dict):
        return None
    return person_profile_from_mapping(config.get(FOOD_PERSON_PROFILE_KEY))


def load_food_person_profile_for_setup(
    config: dict[str, Any] | None,
    *,
    config_path: str | None = None,
    today: date | None = None,
) -> PersonProfile | None:
    """Return the setup profile with temp age/height and Fitness weight when available.

    Age from `config-temp.json` is advanced by whole years since `age_recorded_on`.
    Height from temp overrides the profile in `config.json`. Weight prefers the
    newest Fitness row when present.

    """
    profile = load_food_person_profile(config)
    body = load_food_person_age_height(config_path=config_path)
    fitness_weight = load_latest_fitness_weight_kg(config)

    if body is not None:
        estimated_age = estimate_age_from_recorded(body.age, body.age_recorded_on, today=today)
        if profile is None:
            profile = PersonProfile(
                sex="male",
                age=estimated_age,
                height_cm=body.height_cm,
                weight_kg=fitness_weight if fitness_weight is not None else 70.0,
            )
        else:
            profile = replace(profile, age=estimated_age, height_cm=body.height_cm)

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


def resolve_age_for_save(
    entered_age: int,
    previous: StoredAgeHeight | None,
    *,
    today: date | None = None,
) -> tuple[int, date]:
    """Return age and recorded date to store for `entered_age`.

    When the entered value matches the age estimated from the previous snapshot,
    keep the original base age and recorded date so later calls keep advancing
    correctly. Otherwise store `entered_age` with `today` as the new recorded date.

    """
    current = today or datetime.now(UTC).astimezone().date()
    clamped = _clamp_age(entered_age)
    if previous is not None:
        estimated = estimate_age_from_recorded(previous.age, previous.age_recorded_on, today=current)
        if clamped == estimated:
            return previous.age, previous.age_recorded_on
    return clamped, current


def save_food_calorie_threshold_setup(
    *,
    thresholds: CalorieThresholds,
    profile: PersonProfile,
    config_path: str | None = None,
    today: date | None = None,
) -> dict[str, Any]:
    """Persist bands, profile, and age/height temp snapshot; return updated config."""
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
    _save_food_person_age_height(profile, config_path=str(path), today=today)
    return data


def _clamp_age(age: int) -> int:
    return min(_AGE_MAX, max(_AGE_MIN, int(age)))


def _ensure_temp_config_file(config_path: str) -> None:
    temp_path = _sibling_temp_config_path(config_path)
    temp_path.parent.mkdir(parents=True, exist_ok=True)
    if not temp_path.exists() or temp_path.stat().st_size == 0:
        temp_path.write_text("{}", encoding="utf-8")


def _save_food_person_age_height(
    profile: PersonProfile,
    *,
    config_path: str,
    today: date | None = None,
) -> None:
    previous = load_food_person_age_height(config_path=config_path)
    age_to_store, recorded_on = resolve_age_for_save(profile.age, previous, today=today)
    payload = {
        "age": age_to_store,
        "height_cm": round(float(profile.height_cm), 1),
        "age_recorded_on": recorded_on.isoformat(),
    }
    _ensure_temp_config_file(config_path)
    h.dev.config_update_value(FOOD_PERSON_AGE_HEIGHT_KEY, payload, config_path, is_temp=True)


def _sibling_temp_config_path(config_path: str) -> Path:
    path = Path(config_path)
    if not path.is_absolute():
        path = Path(h.dev.get_project_root()) / path
    return path.with_name(f"{path.stem}-temp{path.suffix}")


def _stored_age_height_from_mapping(raw: object) -> StoredAgeHeight | None:
    if not isinstance(raw, dict):
        return None
    age_raw = raw.get("age")
    height_raw = raw.get("height_cm")
    recorded_raw = raw.get("age_recorded_on")
    if age_raw is None or height_raw is None or recorded_raw is None:
        return None
    try:
        age = int(age_raw)
        height_cm = float(height_raw)
        recorded_on = date.fromisoformat(str(recorded_raw).strip())
    except (TypeError, ValueError):
        return None
    if age < _AGE_MIN or age > _AGE_MAX or height_cm < _HEIGHT_CM_MIN or height_cm > _HEIGHT_CM_MAX:
        return None
    return StoredAgeHeight(age=age, height_cm=height_cm, age_recorded_on=recorded_on)
