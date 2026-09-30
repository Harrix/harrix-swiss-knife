---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `calorie_thresholds_config.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `food_calorie_thresholds_are_configured`](#-function-food_calorie_thresholds_are_configured)
- [🔧 Function `load_food_person_profile`](#-function-load_food_person_profile)
- [🔧 Function `load_food_person_profile_for_setup`](#-function-load_food_person_profile_for_setup)
- [🔧 Function `load_latest_fitness_weight_kg`](#-function-load_latest_fitness_weight_kg)
- [🔧 Function `save_food_calorie_threshold_setup`](#-function-save_food_calorie_threshold_setup)

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
def load_food_person_profile_for_setup(config: dict[str, Any] | None) -> PersonProfile | None
```

Return the setup profile, preferring the latest Fitness weight when available.

<details>
<summary>Code:</summary>

```python
def load_food_person_profile_for_setup(config: dict[str, Any] | None) -> PersonProfile | None:
    profile = load_food_person_profile(config)
    fitness_weight = load_latest_fitness_weight_kg(config)
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

## 🔧 Function `save_food_calorie_threshold_setup`

```python
def save_food_calorie_threshold_setup(*, thresholds: CalorieThresholds, profile: PersonProfile, config_path: str | None = None) -> dict[str, Any]
```

Persist bands, profile, and the configured flag; return the updated config.

<details>
<summary>Code:</summary>

```python
def save_food_calorie_threshold_setup(
    *,
    thresholds: CalorieThresholds,
    profile: PersonProfile,
    config_path: str | None = None,
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
    return data
```

</details>
