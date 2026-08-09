---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `config_model.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `AppConfig`](#%EF%B8%8F-class-appconfig)
- [🏛️ Class `BothubSettings`](#%EF%B8%8F-class-bothubsettings)
- [🏛️ Class `FoodCalorieThresholds`](#%EF%B8%8F-class-foodcaloriethresholds)
- [🏛️ Class `HotkeyEntry`](#%EF%B8%8F-class-hotkeyentry)
- [🏛️ Class `PersonalDataSettings`](#%EF%B8%8F-class-personaldatasettings)
- [🔧 Function `load_app_config`](#-function-load_app_config)
- [🔧 Function `validate_app_config`](#-function-validate_app_config)

</details>

## 🏛️ Class `AppConfig`

```python
class AppConfig(TypedDict, total=False)
```

Known top-level keys of the application config.

Extra keys are allowed at runtime; this model documents the stable surface.

<details>
<summary>Code:</summary>

```python
class AppConfig(TypedDict, total=False):

    editor: str
    editor_notes: NotRequired[str]
    hotkeys: list[HotkeyEntry]
    path_github: str
    path_notes: str
    path_diary: str
    path_dream: str
    path_cases: str
    path_memories: str
    path_quotes: str
    path_articles: str
    path_totalcmd_ini: str
    path_harrix_notes_explorer: str
    paths_python_projects: list[str]
    paths_python_libraries: list[str]
    paths_notes: list[str]
    paths_git: list[str]
    vscode_workspace_notes: str
    vscode_workspace_articles: str
    bothub: BothubSettings
    bothub_api_key: str
    pypi_token: str
    sqlite_finance: str
    sqlite_fitness: str
    sqlite_food: str
    sqlite_habits: str
    food_calorie_thresholds: FoodCalorieThresholds
    block_drives: list[str]
    markdown_templates: dict[str, Any]
    personal_data: PersonalDataSettings
    prompts: dict[str, str]
    show_main_window_on_startup: bool
    compact_mode: bool
    android_build_variant: str
    path_photos: str
```

</details>

## 🏛️ Class `BothubSettings`

```python
class BothubSettings(TypedDict, total=False)
```

BotHub API settings.

<details>
<summary>Code:</summary>

```python
class BothubSettings(TypedDict, total=False):

    base_url: str
    model: str
    speech_model: str
    max_image_side: int
    proxy: str
```

</details>

## 🏛️ Class `FoodCalorieThresholds`

```python
class FoodCalorieThresholds(TypedDict, total=False)
```

Calorie threshold bands for the food tracker UI.

<details>
<summary>Code:</summary>

```python
class FoodCalorieThresholds(TypedDict, total=False):

    low: int
    medium_low: int
    medium_high: int
```

</details>

## 🏛️ Class `HotkeyEntry`

```python
class HotkeyEntry(TypedDict)
```

One hotkey binding entry from config.

<details>
<summary>Code:</summary>

```python
class HotkeyEntry(TypedDict):

    action: str
    hotkeys: NotRequired[list[str]]
    hotkey: NotRequired[str]
```

</details>

## 🏛️ Class `PersonalDataSettings`

```python
class PersonalDataSettings(TypedDict, total=False)
```

Author/contact fields for note frontmatter (@hsk-sync:new-note).

<details>
<summary>Code:</summary>

```python
class PersonalDataSettings(TypedDict, total=False):

    enabled: bool
    author: str
    author_email: str
```

</details>

## 🔧 Function `load_app_config`

```python
def load_app_config(config_path: str | None = None) -> dict[str, Any]
```

Load config JSON and return a plain dict after soft validation.

<details>
<summary>Code:</summary>

```python
def load_app_config(config_path: str | None = None) -> dict[str, Any]:
    path = config_path or get_config_path_str()
    loaded = h.dev.config_load(path)
    if not isinstance(loaded, dict):
        msg = f"Config root must be a JSON object: {path}"
        raise TypeError(msg)
    validate_app_config(loaded)
    return loaded
```

</details>

## 🔧 Function `validate_app_config`

```python
def validate_app_config(config: dict[str, Any]) -> list[str]
```

Validate config shape; return human-readable warnings (never raises for soft issues).

Raises:

- `TypeError`: When required container types are wrong (e.g. `hotkeys` is not a list).

<details>
<summary>Code:</summary>

```python
def validate_app_config(config: dict[str, Any]) -> list[str]:
    warnings: list[str] = []

    hotkeys = config.get("hotkeys")
    if hotkeys is not None:
        if not isinstance(hotkeys, list):
            msg = "Config key 'hotkeys' must be a list."
            raise TypeError(msg)
        for index, item in enumerate(hotkeys):
            if not isinstance(item, dict):
                msg = f"Config hotkeys[{index}] must be an object."
                raise TypeError(msg)
            action = str(item.get("action") or "").strip()
            if not action:
                msg = f"Config hotkeys[{index}] is missing non-empty 'action'."
                raise TypeError(msg)

    for key in ("paths_python_projects", "paths_python_libraries", "paths_notes", "paths_git", "block_drives"):
        value = config.get(key)
        if value is not None and not isinstance(value, list):
            msg = f"Config key '{key}' must be a list."
            raise TypeError(msg)

    templates = config.get("markdown_templates")
    if templates is not None and not isinstance(templates, dict):
        msg = "Config key 'markdown_templates' must be an object."
        raise TypeError(msg)

    personal_data = config.get("personal_data")
    if personal_data is not None and not isinstance(personal_data, dict):
        msg = "Config key 'personal_data' must be an object."
        raise TypeError(msg)

    for key in _RECOMMENDED_KEYS:
        value = config.get(key)
        if value is None or (isinstance(value, str) and not value.strip()):
            warnings.append(f"Missing recommended config key: {key}")
        elif isinstance(value, str) and value.startswith("<YOUR_"):
            warnings.append(f"Config key '{key}' still has a placeholder value.")

    return warnings
```

</details>
