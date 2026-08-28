---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `apps_config.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `get_apps_fitness_image_high_max_size`](#-function-get_apps_fitness_image_high_max_size)
- [🔧 Function `get_apps_fitness_image_max_size`](#-function-get_apps_fitness_image_max_size)
- [🔧 Function `get_apps_fitness_image_min_max_size`](#-function-get_apps_fitness_image_min_max_size)
- [🔧 Function `get_apps_fitness_image_static_max_size`](#-function-get_apps_fitness_image_static_max_size)
- [🔧 Function `get_apps_fitness_lightbox_countdown_seconds`](#-function-get_apps_fitness_lightbox_countdown_seconds)
- [🔧 Function `get_apps_fitness_workout_duration_min`](#-function-get_apps_fitness_workout_duration_min)
- [🔧 Function `get_apps_fitness_workout_gender`](#-function-get_apps_fitness_workout_gender)
- [🔧 Function `get_apps_fitness_workout_history_count`](#-function-get_apps_fitness_workout_history_count)
- [🔧 Function `get_apps_list_limits`](#-function-get_apps_list_limits)
- [🔧 Function `get_apps_local_language`](#-function-get_apps_local_language)
- [🔧 Function `get_apps_local_language_display_name`](#-function-get_apps_local_language_display_name)
- [🔧 Function `set_apps_fitness_workout_duration_min`](#-function-set_apps_fitness_workout_duration_min)
- [🔧 Function `set_apps_fitness_workout_gender`](#-function-set_apps_fitness_workout_gender)

</details>

## 🔧 Function `get_apps_fitness_image_high_max_size`

```python
def get_apps_fitness_image_high_max_size(config: dict[str, Any]) -> int
```

Return max lightbox image size from `apps.fitness_image_high_max_size`.

Always at least the small UI size. Default `1920`.

<details>
<summary>Code:</summary>

```python
def get_apps_fitness_image_high_max_size(config: dict[str, Any]) -> int:
    small = get_apps_fitness_image_max_size(config)
    apps = config.get("apps") or {}
    raw = apps.get("fitness_image_high_max_size", DEFAULT_FITNESS_IMAGE_HIGH_MAX_SIZE)
    try:
        return max(int(raw), small)
    except (TypeError, ValueError):
        return max(DEFAULT_FITNESS_IMAGE_HIGH_MAX_SIZE, small)
```

</details>

## 🔧 Function `get_apps_fitness_image_max_size`

```python
def get_apps_fitness_image_max_size(config: dict[str, Any]) -> int
```

Return max exercise image width/height in pixels from `apps.fitness_image_max_size`.

Larger media is scaled down so neither side exceeds this value (default `330`).
Used for the small AVIF shown in lists, tables, and previews.

<details>
<summary>Code:</summary>

```python
def get_apps_fitness_image_max_size(config: dict[str, Any]) -> int:
    apps = config.get("apps") or {}
    raw = apps.get("fitness_image_max_size", DEFAULT_FITNESS_IMAGE_MAX_SIZE)
    try:
        return max(int(raw), 1)
    except (TypeError, ValueError):
        return DEFAULT_FITNESS_IMAGE_MAX_SIZE
```

</details>

## 🔧 Function `get_apps_fitness_image_min_max_size`

```python
def get_apps_fitness_image_min_max_size(config: dict[str, Any]) -> int
```

Return max table-icon width/height from `apps.fitness_image_min_max_size`.

Default `96`. Used for static WebP files under `fitness_img/min/`.

<details>
<summary>Code:</summary>

```python
def get_apps_fitness_image_min_max_size(config: dict[str, Any]) -> int:
    apps = config.get("apps") or {}
    raw = apps.get("fitness_image_min_max_size", DEFAULT_FITNESS_IMAGE_MIN_MAX_SIZE)
    try:
        return max(int(raw), 1)
    except (TypeError, ValueError):
        return DEFAULT_FITNESS_IMAGE_MIN_MAX_SIZE
```

</details>

## 🔧 Function `get_apps_fitness_image_static_max_size`

```python
def get_apps_fitness_image_static_max_size(config: dict[str, Any]) -> int
```

Return max Select Exercise preview size from `apps.fitness_image_static_max_size`.

Default `512`. Used for static WebP files under `fitness_img/static/`.

<details>
<summary>Code:</summary>

```python
def get_apps_fitness_image_static_max_size(config: dict[str, Any]) -> int:
    apps = config.get("apps") or {}
    raw = apps.get("fitness_image_static_max_size", DEFAULT_FITNESS_IMAGE_STATIC_MAX_SIZE)
    try:
        return max(int(raw), 1)
    except (TypeError, ValueError):
        return DEFAULT_FITNESS_IMAGE_STATIC_MAX_SIZE
```

</details>

## 🔧 Function `get_apps_fitness_lightbox_countdown_seconds`

```python
def get_apps_fitness_lightbox_countdown_seconds(config: dict[str, Any]) -> int
```

Return the ready-countdown before the exercise stopwatch starts.

Reads `apps.fitness_lightbox_countdown_seconds`. Default `5`. Always at
least `0` (skip the countdown and start the stopwatch immediately).

<details>
<summary>Code:</summary>

```python
def get_apps_fitness_lightbox_countdown_seconds(config: dict[str, Any]) -> int:
    apps = config.get("apps") or {}
    raw = apps.get("fitness_lightbox_countdown_seconds", DEFAULT_FITNESS_LIGHTBOX_COUNTDOWN_SECONDS)
    try:
        return max(int(raw), 0)
    except (TypeError, ValueError):
        return DEFAULT_FITNESS_LIGHTBOX_COUNTDOWN_SECONDS
```

</details>

## 🔧 Function `get_apps_fitness_workout_duration_min`

```python
def get_apps_fitness_workout_duration_min(config: dict[str, Any]) -> int | None
```

Return stored planned workout duration from `apps.fitness_workout_duration_min`.

Returns minutes in `10..240`, or `None` when the user has not set a value yet.

<details>
<summary>Code:</summary>

```python
def get_apps_fitness_workout_duration_min(config: dict[str, Any]) -> int | None:
    apps = config.get("apps") or {}
    raw = apps.get(FITNESS_WORKOUT_DURATION_MIN_KEY)
    if raw is None:
        return None
    try:
        value = int(raw)
    except (TypeError, ValueError):
        return None
    if value < _MIN_FITNESS_WORKOUT_DURATION_MIN or value > _MAX_FITNESS_WORKOUT_DURATION_MIN:
        return None
    return value
```

</details>

## 🔧 Function `get_apps_fitness_workout_gender`

```python
def get_apps_fitness_workout_gender(config: dict[str, Any]) -> str | None
```

Return stored workout gender from `apps.fitness_workout_gender`.

Returns `male`, `female`, or `None` when the user has not chosen yet.

<details>
<summary>Code:</summary>

```python
def get_apps_fitness_workout_gender(config: dict[str, Any]) -> str | None:
    apps = config.get("apps") or {}
    raw = apps.get(FITNESS_WORKOUT_GENDER_KEY)
    gender = str(raw or "").strip().lower()
    if gender in _VALID_FITNESS_WORKOUT_GENDERS:
        return gender
    return None
```

</details>

## 🔧 Function `get_apps_fitness_workout_history_count`

```python
def get_apps_fitness_workout_history_count(config: dict[str, Any]) -> int
```

Return how many recent sets to send when generating a workout.

Reads `apps.fitness_workout_history_count`. Default `100`. Always at least `1`.

<details>
<summary>Code:</summary>

```python
def get_apps_fitness_workout_history_count(config: dict[str, Any]) -> int:
    apps = config.get("apps") or {}
    raw = apps.get("fitness_workout_history_count", DEFAULT_FITNESS_WORKOUT_HISTORY_COUNT)
    try:
        return max(int(raw), 1)
    except (TypeError, ValueError):
        return DEFAULT_FITNESS_WORKOUT_HISTORY_COUNT
```

</details>

## 🔧 Function `get_apps_list_limits`

```python
def get_apps_list_limits(config: dict[str, Any]) -> tuple[int, int]
```

Return `(initial_count, load_more_count)` from the shared `apps` config block.

Used for table first-page size, scroll load-more size, and similar limits
(autocomplete sample size, frequency window) that share the same defaults.

<details>
<summary>Code:</summary>

```python
def get_apps_list_limits(config: dict[str, Any]) -> tuple[int, int]:
    apps = config.get("apps") or {}
    return (
        int(apps.get("initial_count", DEFAULT_INITIAL_COUNT)),
        int(apps.get("load_more_count", DEFAULT_LOAD_MORE_COUNT)),
    )
```

</details>

## 🔧 Function `get_apps_local_language`

```python
def get_apps_local_language(config: dict[str, Any]) -> str
```

Return local language code from `apps.local_language` (default `ru`).

<details>
<summary>Code:</summary>

```python
def get_apps_local_language(config: dict[str, Any]) -> str:
    apps = config.get("apps") or {}
    raw = apps.get("local_language", DEFAULT_LOCAL_LANGUAGE)
    code = str(raw or DEFAULT_LOCAL_LANGUAGE).strip().lower()
    return code or DEFAULT_LOCAL_LANGUAGE
```

</details>

## 🔧 Function `get_apps_local_language_display_name`

```python
def get_apps_local_language_display_name(config: dict[str, Any]) -> str
```

Return English display name for `apps.local_language` (e.g. `Russian`).

<details>
<summary>Code:</summary>

```python
def get_apps_local_language_display_name(config: dict[str, Any]) -> str:
    code = get_apps_local_language(config)
    if code in _LANGUAGE_DISPLAY_NAMES:
        return _LANGUAGE_DISPLAY_NAMES[code]
    return code.upper()
```

</details>

## 🔧 Function `set_apps_fitness_workout_duration_min`

```python
def set_apps_fitness_workout_duration_min(duration_min: int, *, config: dict[str, Any] | None = None, config_path: str | None = None) -> None
```

Write planned workout duration into `config.json`.

Args:

- [`duration_min`](../fitness/workout_generate_dialog.g.md#%EF%B8%8F-method-duration_min) (`int`): Minutes in `10..240`.
- [`config`](../../actions/common/base.g.md#%EF%B8%8F-method-config-property) (`dict[str, Any] | None`): Optional in-memory config to keep in sync.
- `config_path` (`str | None`): Config file path. Defaults to the project config.

<details>
<summary>Code:</summary>

```python
def set_apps_fitness_workout_duration_min(
    duration_min: int,
    *,
    config: dict[str, Any] | None = None,
    config_path: str | None = None,
) -> None:
    try:
        value = int(duration_min)
    except (TypeError, ValueError) as exc:
        msg = "Workout duration must be an integer number of minutes"
        raise ValueError(msg) from exc
    if value < _MIN_FITNESS_WORKOUT_DURATION_MIN or value > _MAX_FITNESS_WORKOUT_DURATION_MIN:
        msg = (
            f"Workout duration must be between {_MIN_FITNESS_WORKOUT_DURATION_MIN} "
            f"and {_MAX_FITNESS_WORKOUT_DURATION_MIN} minutes"
        )
        raise ValueError(msg)

    path = Path(config_path or get_config_path_str())
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        msg = f"Config root must be a JSON object: {path}"
        raise TypeError(msg)
    apps = data.get("apps")
    if not isinstance(apps, dict):
        apps = {}
        data["apps"] = apps
    apps[FITNESS_WORKOUT_DURATION_MIN_KEY] = value
    path.write_text(h.dev.dumps_pretty_json(data), encoding="utf-8")
    if config is not None:
        live_apps = config.setdefault("apps", {})
        if isinstance(live_apps, dict):
            live_apps[FITNESS_WORKOUT_DURATION_MIN_KEY] = value
```

</details>

## 🔧 Function `set_apps_fitness_workout_gender`

```python
def set_apps_fitness_workout_gender(gender: str, *, config: dict[str, Any] | None = None, config_path: str | None = None) -> None
```

Write workout gender (`male` or `female`) into `config.json`.

Args:

- [`gender`](../fitness/workout_generate_dialog.g.md#%EF%B8%8F-method-gender) (`str`): Athlete gender for AI workout generation.
- [`config`](../../actions/common/base.g.md#%EF%B8%8F-method-config-property) (`dict[str, Any] | None`): Optional in-memory config to keep in sync.
- `config_path` (`str | None`): Config file path. Defaults to the project config.

<details>
<summary>Code:</summary>

```python
def set_apps_fitness_workout_gender(
    gender: str,
    *,
    config: dict[str, Any] | None = None,
    config_path: str | None = None,
) -> None:
    normalized = str(gender or "").strip().lower()
    if normalized not in _VALID_FITNESS_WORKOUT_GENDERS:
        msg = f"Workout gender must be one of: {', '.join(sorted(_VALID_FITNESS_WORKOUT_GENDERS))}"
        raise ValueError(msg)

    path = Path(config_path or get_config_path_str())
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        msg = f"Config root must be a JSON object: {path}"
        raise TypeError(msg)
    apps = data.get("apps")
    if not isinstance(apps, dict):
        apps = {}
        data["apps"] = apps
    apps[FITNESS_WORKOUT_GENDER_KEY] = normalized
    path.write_text(h.dev.dumps_pretty_json(data), encoding="utf-8")
    if config is not None:
        live_apps = config.setdefault("apps", {})
        if isinstance(live_apps, dict):
            live_apps[FITNESS_WORKOUT_GENDER_KEY] = normalized
```

</details>
