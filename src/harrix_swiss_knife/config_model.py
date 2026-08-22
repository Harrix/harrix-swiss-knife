"""Typed config helpers and light validation for `config.json`."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, NotRequired, TypedDict

import harrix_pylib as h

from harrix_swiss_knife.paths import get_config_path_str

SHOW_MAIN_WINDOW_ON_STARTUP_DEFAULT = True
SHOW_MAIN_WINDOW_ON_STARTUP_KEY = "show_main_window_on_startup"


class AiSettings(TypedDict, total=False):
    """Active AI provider selection and shared transport settings."""

    provider: str
    speech_provider: str
    max_image_side: int
    proxy: str


class AnthropicSettings(TypedDict, total=False):
    """Anthropic Messages API settings."""

    base_url: str
    model: str
    max_tokens: int


class AppConfig(TypedDict, total=False):
    """Known top-level keys of the application config.

    Extra keys are allowed at runtime; this model documents the stable surface.

    """

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
    food_calorie_thresholds: FoodCalorieThresholds
    block_drives: list[str]
    markdown_templates: dict[str, Any]
    personal_data: PersonalDataSettings
    prompts: dict[str, str]
    show_main_window_on_startup: bool
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


class BothubSettings(TypedDict, total=False):
    """BotHub API settings."""

    base_url: str
    model: str
    speech_model: str
    max_image_side: int
    proxy: str


class FoodCalorieThresholds(TypedDict, total=False):
    """Calorie threshold bands for the food tracker UI."""

    low: int
    medium_low: int
    medium_high: int


class GeminiSettings(TypedDict, total=False):
    """Google Gemini generateContent settings."""

    base_url: str
    model: str
    speech_model: str


class HotkeyEntry(TypedDict):
    """One hotkey binding entry from config."""

    action: str
    hotkeys: NotRequired[list[str]]
    hotkey: NotRequired[str]


class OpenAISettings(TypedDict, total=False):
    """OpenAI chat completions and Whisper settings."""

    base_url: str
    model: str
    speech_model: str


class PersonalDataSettings(TypedDict, total=False):
    """Author/contact fields for note frontmatter (@hsk-sync:new-note)."""

    enabled: bool
    author: str
    author_email: str


def get_show_main_window_on_startup(config: dict[str, Any] | None = None) -> bool:
    """Return whether the commands window should open when the app starts."""
    data = config
    if data is None:
        try:
            data = load_app_config()
        except (OSError, TypeError, ValueError):
            return SHOW_MAIN_WINDOW_ON_STARTUP_DEFAULT
    value = data.get(SHOW_MAIN_WINDOW_ON_STARTUP_KEY, SHOW_MAIN_WINDOW_ON_STARTUP_DEFAULT)
    return value if isinstance(value, bool) else SHOW_MAIN_WINDOW_ON_STARTUP_DEFAULT


def load_app_config(config_path: str | None = None) -> dict[str, Any]:
    """Load config JSON and return a plain dict after soft validation."""
    path = config_path or get_config_path_str()
    loaded = h.dev.config_load(path)
    if not isinstance(loaded, dict):
        msg = f"Config root must be a JSON object: {path}"
        raise TypeError(msg)
    validate_app_config(loaded)
    return loaded


def set_show_main_window_on_startup(*, enabled: bool, config_path: str | None = None) -> None:
    """Write `show_main_window_on_startup` to `config.json`."""
    path = Path(config_path or get_config_path_str())
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        msg = f"Config root must be a JSON object: {path}"
        raise TypeError(msg)
    data[SHOW_MAIN_WINDOW_ON_STARTUP_KEY] = bool(enabled)
    path.write_text(h.dev.dumps_pretty_json(data), encoding="utf-8")


def validate_app_config(config: dict[str, Any]) -> list[str]:
    """Validate config shape; return human-readable warnings (never raises for soft issues).

    Raises:

    - `TypeError`: When required container types are wrong (e.g. `hotkeys` is not a list).

    """
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


# Keys that should exist for a usable personal setup (soft warnings, not hard fail).
_RECOMMENDED_KEYS: tuple[str, ...] = (
    "editor-notes",
    "path_github",
    "path_notes",
    "vscode_workspace_notes",
)
