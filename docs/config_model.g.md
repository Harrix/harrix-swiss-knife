---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `config_model.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `AiSettings`](#%EF%B8%8F-class-aisettings)
- [🏛️ Class `AnthropicSettings`](#%EF%B8%8F-class-anthropicsettings)
- [🏛️ Class `AppConfig`](#%EF%B8%8F-class-appconfig)
- [🏛️ Class `BothubSettings`](#%EF%B8%8F-class-bothubsettings)
- [🏛️ Class `FoodCalorieThresholds`](#%EF%B8%8F-class-foodcaloriethresholds)
- [🏛️ Class `GeminiSettings`](#%EF%B8%8F-class-geminisettings)
- [🏛️ Class `HotkeyEntry`](#%EF%B8%8F-class-hotkeyentry)
- [🏛️ Class `OpenAISettings`](#%EF%B8%8F-class-openaisettings)
- [🏛️ Class `PersonalDataSettings`](#%EF%B8%8F-class-personaldatasettings)
- [🔧 Function `clamp_ui_font_scale`](#-function-clamp_ui_font_scale)
- [🔧 Function `get_show_main_window_on_startup`](#-function-get_show_main_window_on_startup)
- [🔧 Function `get_ui_font_scale`](#-function-get_ui_font_scale)
- [🔧 Function `load_app_config`](#-function-load_app_config)
- [🔧 Function `restart_required_config_keys`](#-function-restart_required_config_keys)
- [🔧 Function `set_show_main_window_on_startup`](#-function-set_show_main_window_on_startup)
- [🔧 Function `validate_app_config`](#-function-validate_app_config)

</details>

## 🏛️ Class `AiSettings`

```python
class AiSettings(TypedDict, total=False)
```

Active AI provider selection and shared transport settings.

<details>
<summary>Code:</summary>

```python
class AiSettings(TypedDict, total=False):

    provider: str
    speech_provider: str
    max_image_side: int
    proxy: str
```

</details>

## 🏛️ Class `AnthropicSettings`

```python
class AnthropicSettings(TypedDict, total=False)
```

Anthropic Messages API settings.

<details>
<summary>Code:</summary>

```python
class AnthropicSettings(TypedDict, total=False):

    base_url: str
    model: str
    max_tokens: int
```

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
    path_habit_comments: NotRequired[str]
    path_articles: str
    path_totalcmd_ini: str
    path_harrix_notes_explorer: str
    paths_python_projects: list[str]
    paths_python_libraries: list[str]
    paths_notes: list[str]
    paths_git: list[str]
    vscode_workspace_notes: str
    vscode_workspace_articles: str
    ai: AiSettings
    bothub: BothubSettings
    bothub_api_key: str
    bothub_ru: BothubSettings
    bothub_ru_api_key: str
    openai: OpenAISettings
    openai_api_key: str
    anthropic: AnthropicSettings
    anthropic_api_key: str
    gemini: GeminiSettings
    gemini_api_key: str
    github_token: str
    pypi_token: str
    sqlite_finance: str
    sqlite_fitness: str
    sqlite_food: str
    sqlite_habits: str
    sqlite_snippets: str
    transfer_private_data_default_api_keys: NotRequired[list[str]]
    food_calorie_thresholds: FoodCalorieThresholds
    block_drives: list[str]
    markdown_templates: dict[str, Any]
    personal_data: PersonalDataSettings
    prompts: dict[str, str]
    show_main_window_on_startup: bool
    ui_font_scale: NotRequired[float]
    data_for_hsk_root: NotRequired[str]
    data_for_hsk_notes_folders: NotRequired[list[str]]
    data_for_hsk_setup_done: NotRequired[bool]
    android_build_variant: str
    path_photos: str
    path_vector_icons: NotRequired[str]
    path_vector_icons_ai: NotRequired[str]
    path_vector_icons_source_app: NotRequired[str]
    path_vector_icons_pinned: NotRequired[list[str]]
    vector_icons_recent_folders_max: NotRequired[int]
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

## 🏛️ Class `GeminiSettings`

```python
class GeminiSettings(TypedDict, total=False)
```

Google Gemini generateContent settings.

<details>
<summary>Code:</summary>

```python
class GeminiSettings(TypedDict, total=False):

    base_url: str
    model: str
    speech_model: str
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

## 🏛️ Class `OpenAISettings`

```python
class OpenAISettings(TypedDict, total=False)
```

OpenAI chat completions and Whisper settings.

<details>
<summary>Code:</summary>

```python
class OpenAISettings(TypedDict, total=False):

    base_url: str
    model: str
    speech_model: str
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

## 🔧 Function `clamp_ui_font_scale`

```python
def clamp_ui_font_scale(value: float) -> float
```

Clamp `ui_font_scale` to the supported range.

<details>
<summary>Code:</summary>

```python
def clamp_ui_font_scale(value: float) -> float:
    return min(UI_FONT_SCALE_MAX, max(UI_FONT_SCALE_MIN, value))
```

</details>

## 🔧 Function `get_show_main_window_on_startup`

```python
def get_show_main_window_on_startup(config: dict[str, Any] | None = None) -> bool
```

Return whether the commands window should open when the app starts.

<details>
<summary>Code:</summary>

```python
def get_show_main_window_on_startup(config: dict[str, Any] | None = None) -> bool:
    data = config
    if data is None:
        try:
            data = load_app_config()
        except (OSError, TypeError, ValueError):
            return SHOW_MAIN_WINDOW_ON_STARTUP_DEFAULT
    value = data.get(SHOW_MAIN_WINDOW_ON_STARTUP_KEY, SHOW_MAIN_WINDOW_ON_STARTUP_DEFAULT)
    return value if isinstance(value, bool) else SHOW_MAIN_WINDOW_ON_STARTUP_DEFAULT
```

</details>

## 🔧 Function `get_ui_font_scale`

```python
def get_ui_font_scale(config: dict[str, Any] | None = None) -> float
```

Return the global UI font multiplier from `config.json` (`1.0` by default).

<details>
<summary>Code:</summary>

```python
def get_ui_font_scale(config: dict[str, Any] | None = None) -> float:
    data = config
    if data is None:
        try:
            data = load_app_config()
        except (OSError, TypeError, ValueError):
            return UI_FONT_SCALE_DEFAULT
    raw = data.get(UI_FONT_SCALE_KEY, UI_FONT_SCALE_DEFAULT)
    try:
        value = float(raw)
    except (TypeError, ValueError):
        return UI_FONT_SCALE_DEFAULT
    if value < UI_FONT_SCALE_MIN or value > UI_FONT_SCALE_MAX:
        return UI_FONT_SCALE_DEFAULT
    return value
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

## 🔧 Function `restart_required_config_keys`

```python
def restart_required_config_keys(before: dict[str, Any], after: dict[str, Any]) -> list[str]
```

Return restart-required keys whose values changed from `before` to `after`.

Args:

- `before` (`dict[str, Any]`): Config snapshot before save.
- `after` (`dict[str, Any]`): Config that will be written.

Returns:

- `list[str]`: Changed keys that apply only after an application restart.

<details>
<summary>Code:</summary>

```python
def restart_required_config_keys(before: dict[str, Any], after: dict[str, Any]) -> list[str]:
    return [key for key in sorted(RESTART_REQUIRED_CONFIG_KEYS) if before.get(key) != after.get(key)]
```

</details>

## 🔧 Function `set_show_main_window_on_startup`

```python
def set_show_main_window_on_startup(*, enabled: bool, config_path: str | None = None) -> None
```

Write `show_main_window_on_startup` to `config.json`.

<details>
<summary>Code:</summary>

```python
def set_show_main_window_on_startup(*, enabled: bool, config_path: str | None = None) -> None:
    path = Path(config_path or get_config_path_str())
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        msg = f"Config root must be a JSON object: {path}"
        raise TypeError(msg)
    data[SHOW_MAIN_WINDOW_ON_STARTUP_KEY] = bool(enabled)
    path.write_text(h.dev.dumps_pretty_json(data), encoding="utf-8")
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

    for key in (
        "paths_python_projects",
        "paths_python_libraries",
        "paths_notes",
        "paths_git",
        "block_drives",
        "transfer_private_data_default_api_keys",
    ):
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
