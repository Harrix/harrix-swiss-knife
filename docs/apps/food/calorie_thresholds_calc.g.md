---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `calorie_thresholds_calc.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `CalorieEstimate`](#%EF%B8%8F-class-calorieestimate)
- [🏛️ Class `PersonProfile`](#%EF%B8%8F-class-personprofile)
- [🔧 Function `estimate_calorie_bands`](#-function-estimate_calorie_bands)
- [🔧 Function `mifflin_st_jeor_bmr`](#-function-mifflin_st_jeor_bmr)
- [🔧 Function `person_profile_from_mapping`](#-function-person_profile_from_mapping)
- [🔧 Function `person_profile_to_mapping`](#-function-person_profile_to_mapping)
- [🔧 Function `round_kcal`](#-function-round_kcal)
- [🔧 Function `thresholds_to_mapping`](#-function-thresholds_to_mapping)

</details>

## 🏛️ Class `CalorieEstimate`

```python
class CalorieEstimate
```

BMR, TDEE, and suggested threshold bands.

<details>
<summary>Code:</summary>

```python
class CalorieEstimate:

    bmr: float
    tdee: float
    thresholds: CalorieThresholds
```

</details>

## 🏛️ Class `PersonProfile`

```python
class PersonProfile
```

Inputs for calorie-need estimation.

<details>
<summary>Code:</summary>

```python
class PersonProfile:

    sex: Sex
    age: int
    height_cm: float
    weight_kg: float
    activity: ActivityLevel = "moderate"
    want_to_lose_weight: bool = False
```

</details>

## 🔧 Function `estimate_calorie_bands`

```python
def estimate_calorie_bands(profile: PersonProfile) -> CalorieEstimate
```

Return BMR, TDEE, and rounded low / medium_low / medium_high bands.

Uses Mifflin St Jeor BMR and a standard activity multiplier. Suggested
bands: low ~ 85% of TDEE, medium_low ~ TDEE, medium_high ~ 120% of TDEE,
each rounded to the nearest 50 kcal. When `want_to_lose_weight` is set,
all three bands are scaled by 85% (~15% deficit).

<details>
<summary>Code:</summary>

```python
def estimate_calorie_bands(profile: PersonProfile) -> CalorieEstimate:
    bmr = mifflin_st_jeor_bmr(profile)
    factor = ACTIVITY_FACTORS[profile.activity]
    tdee = bmr * factor
    band_scale = _LOSE_WEIGHT_RATIO if profile.want_to_lose_weight else 1.0
    thresholds = CalorieThresholds(
        low=float(round_kcal(tdee * _LOW_RATIO * band_scale)),
        medium_low=float(round_kcal(tdee * band_scale)),
        medium_high=float(round_kcal(tdee * _HIGH_RATIO * band_scale)),
    )
    return CalorieEstimate(bmr=bmr, tdee=tdee, thresholds=thresholds)
```

</details>

## 🔧 Function `mifflin_st_jeor_bmr`

```python
def mifflin_st_jeor_bmr(profile: PersonProfile) -> float
```

Return basal metabolic rate in kcal/day (Mifflin St Jeor).

<details>
<summary>Code:</summary>

```python
def mifflin_st_jeor_bmr(profile: PersonProfile) -> float:
    base = 10.0 * profile.weight_kg + 6.25 * profile.height_cm - 5.0 * profile.age
    if profile.sex == "male":
        return base + 5.0
    return base - 161.0
```

</details>

## 🔧 Function `person_profile_from_mapping`

```python
def person_profile_from_mapping(raw: object) -> PersonProfile | None
```

Parse a stored profile dict, or `None` when incomplete.

<details>
<summary>Code:</summary>

```python
def person_profile_from_mapping(raw: object) -> PersonProfile | None:
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
        want_to_lose_weight=bool(raw.get("want_to_lose_weight")),
    )
```

</details>

## 🔧 Function `person_profile_to_mapping`

```python
def person_profile_to_mapping(profile: PersonProfile) -> dict[str, object]
```

Serialize `profile` for `config.json`.

<details>
<summary>Code:</summary>

```python
def person_profile_to_mapping(profile: PersonProfile) -> dict[str, object]:
    return {
        "sex": profile.sex,
        "age": profile.age,
        "height_cm": round(profile.height_cm, 1),
        "weight_kg": round(profile.weight_kg, 1),
        "activity": profile.activity,
        "want_to_lose_weight": profile.want_to_lose_weight,
    }
```

</details>

## 🔧 Function `round_kcal`

```python
def round_kcal(value: float) -> int
```

Round kcal to the nearest `_ROUND_STEP` (at least `_ROUND_STEP`).

<details>
<summary>Code:</summary>

```python
def round_kcal(value: float) -> int:
    rounded = int(round(value / _ROUND_STEP) * _ROUND_STEP)
    return max(_ROUND_STEP, rounded)
```

</details>

## 🔧 Function `thresholds_to_mapping`

```python
def thresholds_to_mapping(thresholds: CalorieThresholds) -> dict[str, int]
```

Serialize thresholds as ints for config.

<details>
<summary>Code:</summary>

```python
def thresholds_to_mapping(thresholds: CalorieThresholds) -> dict[str, int]:
    return {
        "low": round(thresholds.low),
        "medium_low": round(thresholds.medium_low),
        "medium_high": round(thresholds.medium_high),
    }
```

</details>
