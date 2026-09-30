"""Derive Food calorie bands from body metrics (Mifflin St Jeor + activity)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from harrix_swiss_knife.apps.food.day_macros import CalorieThresholds

Sex = Literal["male", "female"]
ActivityLevel = Literal["sedentary", "light", "moderate", "active", "very_active"]

ACTIVITY_FACTORS: dict[ActivityLevel, float] = {
    "sedentary": 1.2,
    "light": 1.375,
    "moderate": 1.55,
    "active": 1.725,
    "very_active": 1.9,
}

ACTIVITY_LABELS: tuple[tuple[ActivityLevel, str], ...] = (
    ("sedentary", "Sedentary (little or no exercise)"),
    ("light", "Light (1-3 days / week)"),
    ("moderate", "Moderate (3-5 days / week)"),
    ("active", "Active (6-7 days / week)"),
    ("very_active", "Very active (hard exercise / physical job)"),
)

_LOW_RATIO = 0.85
_HIGH_RATIO = 1.2
_ROUND_STEP = 50
_AGE_MIN = 10
_AGE_MAX = 120
_HEIGHT_CM_MIN = 100.0
_HEIGHT_CM_MAX = 250.0
_WEIGHT_KG_MIN = 30.0
_WEIGHT_KG_MAX = 300.0


@dataclass(frozen=True, slots=True)
class CalorieEstimate:
    """BMR, TDEE, and suggested threshold bands."""

    bmr: float
    tdee: float
    thresholds: CalorieThresholds


@dataclass(frozen=True, slots=True)
class PersonProfile:
    """Inputs for calorie-need estimation."""

    sex: Sex
    age: int
    height_cm: float
    weight_kg: float
    activity: ActivityLevel = "moderate"


def estimate_calorie_bands(profile: PersonProfile) -> CalorieEstimate:
    """Return BMR, TDEE, and rounded low / medium_low / medium_high bands.

    Uses Mifflin St Jeor BMR and a standard activity multiplier. Suggested
    bands: low ~ 85% of TDEE, medium_low ~ TDEE, medium_high ~ 120% of TDEE,
    each rounded to the nearest 50 kcal.

    """
    bmr = mifflin_st_jeor_bmr(profile)
    factor = ACTIVITY_FACTORS[profile.activity]
    tdee = bmr * factor
    thresholds = CalorieThresholds(
        low=float(round_kcal(tdee * _LOW_RATIO)),
        medium_low=float(round_kcal(tdee)),
        medium_high=float(round_kcal(tdee * _HIGH_RATIO)),
    )
    return CalorieEstimate(bmr=bmr, tdee=tdee, thresholds=thresholds)


def mifflin_st_jeor_bmr(profile: PersonProfile) -> float:
    """Return basal metabolic rate in kcal/day (Mifflin St Jeor)."""
    base = 10.0 * profile.weight_kg + 6.25 * profile.height_cm - 5.0 * profile.age
    if profile.sex == "male":
        return base + 5.0
    return base - 161.0


def person_profile_from_mapping(raw: object) -> PersonProfile | None:
    """Parse a stored profile dict, or `None` when incomplete."""
    if not isinstance(raw, dict):
        return None
    sex = str(raw.get("sex") or "").strip().casefold()
    activity = str(raw.get("activity") or "moderate").strip().casefold()
    if sex not in {"male", "female"}:
        return None
    if activity not in ACTIVITY_FACTORS:
        activity = "moderate"
    age_raw = raw.get("age")
    height_raw = raw.get("height_cm")
    weight_raw = raw.get("weight_kg")
    if age_raw is None or height_raw is None or weight_raw is None:
        return None
    try:
        age = int(age_raw)
        height_cm = float(height_raw)
        weight_kg = float(weight_raw)
    except (TypeError, ValueError):
        return None
    if (
        age < _AGE_MIN
        or age > _AGE_MAX
        or height_cm < _HEIGHT_CM_MIN
        or height_cm > _HEIGHT_CM_MAX
        or weight_kg < _WEIGHT_KG_MIN
        or weight_kg > _WEIGHT_KG_MAX
    ):
        return None
    return PersonProfile(
        sex=sex,  # type: ignore[arg-type]
        age=age,
        height_cm=height_cm,
        weight_kg=weight_kg,
        activity=activity,  # type: ignore[arg-type]
    )


def person_profile_to_mapping(profile: PersonProfile) -> dict[str, object]:
    """Serialize `profile` for `config.json`."""
    return {
        "sex": profile.sex,
        "age": profile.age,
        "height_cm": round(profile.height_cm, 1),
        "weight_kg": round(profile.weight_kg, 1),
        "activity": profile.activity,
    }


def round_kcal(value: float) -> int:
    """Round kcal to the nearest `_ROUND_STEP` (at least `_ROUND_STEP`)."""
    rounded = int(round(value / _ROUND_STEP) * _ROUND_STEP)
    return max(_ROUND_STEP, rounded)


def thresholds_to_mapping(thresholds: CalorieThresholds) -> dict[str, int]:
    """Serialize thresholds as ints for config."""
    return {
        "low": round(thresholds.low),
        "medium_low": round(thresholds.medium_low),
        "medium_high": round(thresholds.medium_high),
    }
