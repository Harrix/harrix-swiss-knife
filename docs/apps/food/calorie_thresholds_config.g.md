---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `calorie_thresholds_config.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `StoredAgeHeight`](#%EF%B8%8F-class-storedageheight)
- [🔧 Function `estimate_age_from_recorded`](#-function-estimate_age_from_recorded)
- [🔧 Function `food_calorie_thresholds_are_configured`](#-function-food_calorie_thresholds_are_configured)
- [🔧 Function `load_food_person_age_height`](#-function-load_food_person_age_height)
- [🔧 Function `load_food_person_profile`](#-function-load_food_person_profile)
- [🔧 Function `load_food_person_profile_for_setup`](#-function-load_food_person_profile_for_setup)
- [🔧 Function `load_latest_fitness_weight_kg`](#-function-load_latest_fitness_weight_kg)
- [🔧 Function `resolve_age_for_save`](#-function-resolve_age_for_save)
- [🔧 Function `save_food_calorie_threshold_setup`](#-function-save_food_calorie_threshold_setup)

</details>

## 🏛️ Class `StoredAgeHeight`

```python
class StoredAgeHeight
```

Age and height snapshot from `config-temp.json`.

<details>
<summary>Code:</summary>

```python
class StoredAgeHeight:

    age: int
    height_cm: float
    age_recorded_on: date
```

</details>

## 🔧 Function `estimate_age_from_recorded`

```python
def estimate_age_from_recorded(stored_age: int, recorded_on: date, *, today: date | None = None) -> int
```

Return age advanced by whole years since `recorded_on` (anniversary-style).

<details>
<summary>Code:</summary>

```python
def estimate_age_from_recorded(
    stored_age: int,
    recorded_on: date,
    *,
    today: date | None = None,
) -> int:
    current = today or datetime.now(UTC).astimezone().date()
    if current < recorded_on:
        return _clamp_age(stored_age)
    years = current.year - recorded_on.year
    if (current.month, current.day) < (recorded_on.month, recorded_on.day):
        years -= 1
    return _clamp_age(stored_age + max(0, years))
```

</details>

## 🔧 Function `food_calorie_thresholds_are_configured`

```python
def food_calorie_thresholds_are_configured(config: dict[str, Any] | None) -> bool
```

Return whether the user has confirmed calorie bands at least once.

<details>
<summary>Code:</summary>

```python
def food_calorie_thresholds_are_configured(config: dict[str, Any] | None) -> bool:
    if not isinstance(config, dict):
        return False
    return bool(config.get(FOOD_CALORIE_THRESHOLDS_CONFIGURED_KEY))
```

</details>

## 🔧 Function `load_food_person_age_height`

```python
def load_food_person_age_height(*, config_path: str | None = None) -> StoredAgeHeight | None
```

Return age / height / age-recorded date from `config-temp.json`, if any.

<details>
<summary>Code:</summary>

```python
def load_food_person_age_height(
    *,
    config_path: str | None = None,
) -> StoredAgeHeight | None:
    path_str = config_path or get_config_path_str()
    try:
        loaded: dict[str, Any] = h.dev.config_load(path_str, is_temp=True, resolve_snippets=False)
    except (FileNotFoundError, OSError, TypeError, ValueError, json.JSONDecodeError):
        return None
    if not isinstance(loaded, dict):
        return None
    return _stored_age_height_from_mapping(loaded.get(FOOD_PERSON_AGE_HEIGHT_KEY))
```

</details>

## 🔧 Function `load_food_person_profile`

```python
def load_food_person_profile(config: dict[str, Any] | None) -> PersonProfile | None
```

Return the stored body-metrics profile, if any.

<details>
<summary>Code:</summary>

```python
def load_food_person_profile(config: dict[str, Any] | None) -> PersonProfile | None:
    if not isinstance(config, dict):
        return None
    return person_profile_from_mapping(config.get(FOOD_PERSON_PROFILE_KEY))
```

</details>

## 🔧 Function `load_food_person_profile_for_setup`

```python
def load_food_person_profile_for_setup(config: dict[str, Any] | None, *, config_path: str | None = None, today: date | None = None) -> PersonProfile | None
```

Return the setup profile with temp age/height and Fitness weight when available.

Age from `config-temp.json` is advanced by whole years since `age_recorded_on`.
Height from temp overrides the profile in `config.json`. Weight prefers the
newest Fitness row when present.

<details>
<summary>Code:</summary>

```python
def load_food_person_profile_for_setup(
    config: dict[str, Any] | None,
    *,
    config_path: str | None = None,
    today: date | None = None,
) -> PersonProfile | None:
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
```

</details>

## 🔧 Function `load_latest_fitness_weight_kg`

```python
def load_latest_fitness_weight_kg(config: dict[str, Any] | None) -> float | None
```

Return the newest body weight from Fitness `weight`, or `None` when unavailable.

<details>
<summary>Code:</summary>

```python
def load_latest_fitness_weight_kg(config: dict[str, Any] | None) -> float | None:
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
```

</details>

## 🔧 Function `resolve_age_for_save`

```python
def resolve_age_for_save(entered_age: int, previous: StoredAgeHeight | None, *, today: date | None = None) -> tuple[int, date]
```

Return age and recorded date to store for `entered_age`.

When the entered value matches the age estimated from the previous snapshot,
keep the original base age and recorded date so later calls keep advancing
correctly. Otherwise store `entered_age` with `today` as the new recorded date.

<details>
<summary>Code:</summary>

```python
def resolve_age_for_save(
    entered_age: int,
    previous: StoredAgeHeight | None,
    *,
    today: date | None = None,
) -> tuple[int, date]:
    current = today or datetime.now(UTC).astimezone().date()
    clamped = _clamp_age(entered_age)
    if previous is not None:
        estimated = estimate_age_from_recorded(previous.age, previous.age_recorded_on, today=current)
        if clamped == estimated:
            return previous.age, previous.age_recorded_on
    return clamped, current
```

</details>

## 🔧 Function `save_food_calorie_threshold_setup`

```python
def save_food_calorie_threshold_setup(*, thresholds: CalorieThresholds, profile: PersonProfile, config_path: str | None = None, today: date | None = None) -> dict[str, Any]
```

Persist bands, profile, and age/height temp snapshot; return updated config.

<details>
<summary>Code:</summary>

```python
def save_food_calorie_threshold_setup(
    *,
    thresholds: CalorieThresholds,
    profile: PersonProfile,
    config_path: str | None = None,
    today: date | None = None,
) -> dict[str, Any]:
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
```

</details>
