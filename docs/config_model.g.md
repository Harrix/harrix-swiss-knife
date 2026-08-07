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
  - [📎 Attribute `editor`](#-attribute-editor)
  - [📎 Attribute `editor_notes`](#-attribute-editor_notes)
  - [📎 Attribute `hotkeys`](#-attribute-hotkeys)
  - [📎 Attribute `path_github`](#-attribute-path_github)
  - [📎 Attribute `path_notes`](#-attribute-path_notes)
  - [📎 Attribute `path_diary`](#-attribute-path_diary)
  - [📎 Attribute `path_dream`](#-attribute-path_dream)
  - [📎 Attribute `path_cases`](#-attribute-path_cases)
  - [📎 Attribute `path_memories`](#-attribute-path_memories)
  - [📎 Attribute `path_quotes`](#-attribute-path_quotes)
  - [📎 Attribute `path_articles`](#-attribute-path_articles)
  - [📎 Attribute `path_totalcmd_ini`](#-attribute-path_totalcmd_ini)
  - [📎 Attribute `path_harrix_notes_explorer`](#-attribute-path_harrix_notes_explorer)
  - [📎 Attribute `paths_python_projects`](#-attribute-paths_python_projects)
  - [📎 Attribute `paths_python_libraries`](#-attribute-paths_python_libraries)
  - [📎 Attribute `paths_notes`](#-attribute-paths_notes)
  - [📎 Attribute `paths_git`](#-attribute-paths_git)
  - [📎 Attribute `vscode_workspace_notes`](#-attribute-vscode_workspace_notes)
  - [📎 Attribute `vscode_workspace_articles`](#-attribute-vscode_workspace_articles)
  - [📎 Attribute `bothub`](#-attribute-bothub)
  - [📎 Attribute `bothub_api_key`](#-attribute-bothub_api_key)
  - [📎 Attribute `pypi_token`](#-attribute-pypi_token)
  - [📎 Attribute `sqlite_finance`](#-attribute-sqlite_finance)
  - [📎 Attribute `sqlite_fitness`](#-attribute-sqlite_fitness)
  - [📎 Attribute `sqlite_food`](#-attribute-sqlite_food)
  - [📎 Attribute `sqlite_habits`](#-attribute-sqlite_habits)
  - [📎 Attribute `food_calorie_thresholds`](#-attribute-food_calorie_thresholds)
  - [📎 Attribute `block_drives`](#-attribute-block_drives)
  - [📎 Attribute `markdown_templates`](#-attribute-markdown_templates)
  - [📎 Attribute `prompts`](#-attribute-prompts)
  - [📎 Attribute `show_main_window_on_startup`](#-attribute-show_main_window_on_startup)
  - [📎 Attribute `compact_mode`](#-attribute-compact_mode)
  - [📎 Attribute `android_build_variant`](#-attribute-android_build_variant)
- [🏛️ Class `BothubSettings`](#%EF%B8%8F-class-bothubsettings)
  - [📎 Attribute `base_url`](#-attribute-base_url)
  - [📎 Attribute `model`](#-attribute-model)
  - [📎 Attribute `speech_model`](#-attribute-speech_model)
  - [📎 Attribute `max_image_side`](#-attribute-max_image_side)
  - [📎 Attribute `proxy`](#-attribute-proxy)
- [🏛️ Class `FoodCalorieThresholds`](#%EF%B8%8F-class-foodcaloriethresholds)
  - [📎 Attribute `low`](#-attribute-low)
  - [📎 Attribute `medium_low`](#-attribute-medium_low)
  - [📎 Attribute `medium_high`](#-attribute-medium_high)
- [🏛️ Class `HotkeyEntry`](#%EF%B8%8F-class-hotkeyentry)
  - [📎 Attribute `action`](#-attribute-action)
  - [📎 Attribute `hotkeys`](#-attribute-hotkeys-1)
  - [📎 Attribute `hotkey`](#-attribute-hotkey)
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
    prompts: dict[str, str]
    show_main_window_on_startup: bool
    compact_mode: bool
    android_build_variant: str
```

</details>

### 📎 Attribute `editor`

```python
editor: str
```

_No docstring provided._

### 📎 Attribute `editor_notes`

```python
editor_notes: NotRequired[str]
```

_No docstring provided._

### 📎 Attribute `hotkeys`

```python
hotkeys: list[HotkeyEntry]
```

_No docstring provided._

### 📎 Attribute `path_github`

```python
path_github: str
```

_No docstring provided._

### 📎 Attribute `path_notes`

```python
path_notes: str
```

_No docstring provided._

### 📎 Attribute `path_diary`

```python
path_diary: str
```

_No docstring provided._

### 📎 Attribute `path_dream`

```python
path_dream: str
```

_No docstring provided._

### 📎 Attribute `path_cases`

```python
path_cases: str
```

_No docstring provided._

### 📎 Attribute `path_memories`

```python
path_memories: str
```

_No docstring provided._

### 📎 Attribute `path_quotes`

```python
path_quotes: str
```

_No docstring provided._

### 📎 Attribute `path_articles`

```python
path_articles: str
```

_No docstring provided._

### 📎 Attribute `path_totalcmd_ini`

```python
path_totalcmd_ini: str
```

_No docstring provided._

### 📎 Attribute `path_harrix_notes_explorer`

```python
path_harrix_notes_explorer: str
```

_No docstring provided._

### 📎 Attribute `paths_python_projects`

```python
paths_python_projects: list[str]
```

_No docstring provided._

### 📎 Attribute `paths_python_libraries`

```python
paths_python_libraries: list[str]
```

_No docstring provided._

### 📎 Attribute `paths_notes`

```python
paths_notes: list[str]
```

_No docstring provided._

### 📎 Attribute `paths_git`

```python
paths_git: list[str]
```

_No docstring provided._

### 📎 Attribute `vscode_workspace_notes`

```python
vscode_workspace_notes: str
```

_No docstring provided._

### 📎 Attribute `vscode_workspace_articles`

```python
vscode_workspace_articles: str
```

_No docstring provided._

### 📎 Attribute `bothub`

```python
bothub: BothubSettings
```

_No docstring provided._

### 📎 Attribute `bothub_api_key`

```python
bothub_api_key: str
```

_No docstring provided._

### 📎 Attribute `pypi_token`

```python
pypi_token: str
```

_No docstring provided._

### 📎 Attribute `sqlite_finance`

```python
sqlite_finance: str
```

_No docstring provided._

### 📎 Attribute `sqlite_fitness`

```python
sqlite_fitness: str
```

_No docstring provided._

### 📎 Attribute `sqlite_food`

```python
sqlite_food: str
```

_No docstring provided._

### 📎 Attribute `sqlite_habits`

```python
sqlite_habits: str
```

_No docstring provided._

### 📎 Attribute `food_calorie_thresholds`

```python
food_calorie_thresholds: FoodCalorieThresholds
```

_No docstring provided._

### 📎 Attribute `block_drives`

```python
block_drives: list[str]
```

_No docstring provided._

### 📎 Attribute `markdown_templates`

```python
markdown_templates: dict[str, Any]
```

_No docstring provided._

### 📎 Attribute `prompts`

```python
prompts: dict[str, str]
```

_No docstring provided._

### 📎 Attribute `show_main_window_on_startup`

```python
show_main_window_on_startup: bool
```

_No docstring provided._

### 📎 Attribute `compact_mode`

```python
compact_mode: bool
```

_No docstring provided._

### 📎 Attribute `android_build_variant`

```python
android_build_variant: str
```

_No docstring provided._

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

### 📎 Attribute `base_url`

```python
base_url: str
```

_No docstring provided._

### 📎 Attribute `model`

```python
model: str
```

_No docstring provided._

### 📎 Attribute `speech_model`

```python
speech_model: str
```

_No docstring provided._

### 📎 Attribute `max_image_side`

```python
max_image_side: int
```

_No docstring provided._

### 📎 Attribute `proxy`

```python
proxy: str
```

_No docstring provided._

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

### 📎 Attribute `low`

```python
low: int
```

_No docstring provided._

### 📎 Attribute `medium_low`

```python
medium_low: int
```

_No docstring provided._

### 📎 Attribute `medium_high`

```python
medium_high: int
```

_No docstring provided._

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

### 📎 Attribute `action`

```python
action: str
```

_No docstring provided._

### 📎 Attribute `hotkeys`

```python
hotkeys: NotRequired[list[str]]
```

_No docstring provided._

### 📎 Attribute `hotkey`

```python
hotkey: NotRequired[str]
```

_No docstring provided._

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

    for key in _RECOMMENDED_KEYS:
        value = config.get(key)
        if value is None or (isinstance(value, str) and not value.strip()):
            warnings.append(f"Missing recommended config key: {key}")
        elif isinstance(value, str) and value.startswith("<YOUR_"):
            warnings.append(f"Config key '{key}' still has a placeholder value.")

    return warnings
```

</details>
