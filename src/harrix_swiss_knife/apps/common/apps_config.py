"""Shared config helpers for desktop apps."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

import harrix_pylib as h

from harrix_swiss_knife.paths import get_config_path_str

DEFAULT_INITIAL_COUNT = 1000
DEFAULT_LOAD_MORE_COUNT = 500
DEFAULT_LOCAL_LANGUAGE = "ru"
DEFAULT_FITNESS_IMAGE_MAX_SIZE = 330
DEFAULT_FITNESS_IMAGE_HIGH_MAX_SIZE = 1920
DEFAULT_FITNESS_IMAGE_MIN_MAX_SIZE = 96
DEFAULT_FITNESS_WORKOUT_HISTORY_COUNT = 100
DEFAULT_FITNESS_LIGHTBOX_COUNTDOWN_SECONDS = 5
FITNESS_WORKOUT_GENDER_KEY = "fitness_workout_gender"
_VALID_FITNESS_WORKOUT_GENDERS = frozenset({"male", "female"})
OPEN_QUICK_TAB_ON_STARTUP_DEFAULT = True
OPEN_QUICK_TAB_ON_STARTUP_KEY_PREFIX = "open_quick_tab_on_startup_"

QuickTabAppName = Literal["finance", "food", "fitness"]
_QUICK_TAB_APPS: frozenset[str] = frozenset({"finance", "food", "fitness"})

_LANGUAGE_DISPLAY_NAMES: dict[str, str] = {
    "ru": "Russian",
    "en": "English",
    "de": "German",
    "fr": "French",
    "es": "Spanish",
    "it": "Italian",
    "pt": "Portuguese",
    "pl": "Polish",
    "uk": "Ukrainian",
    "zh": "Chinese",
    "ja": "Japanese",
    "ko": "Korean",
}


def get_apps_fitness_image_high_max_size(config: dict[str, Any]) -> int:
    """Return max lightbox image size from `apps.fitness_image_high_max_size`.

    Always at least the small UI size. Default `1920`.

    """
    small = get_apps_fitness_image_max_size(config)
    apps = config.get("apps") or {}
    raw = apps.get("fitness_image_high_max_size", DEFAULT_FITNESS_IMAGE_HIGH_MAX_SIZE)
    try:
        return max(int(raw), small)
    except (TypeError, ValueError):
        return max(DEFAULT_FITNESS_IMAGE_HIGH_MAX_SIZE, small)


def get_apps_fitness_image_max_size(config: dict[str, Any]) -> int:
    """Return max exercise image width/height in pixels from `apps.fitness_image_max_size`.

    Larger media is scaled down so neither side exceeds this value (default `330`).
    Used for the small AVIF shown in lists, tables, and previews.

    """
    apps = config.get("apps") or {}
    raw = apps.get("fitness_image_max_size", DEFAULT_FITNESS_IMAGE_MAX_SIZE)
    try:
        return max(int(raw), 1)
    except (TypeError, ValueError):
        return DEFAULT_FITNESS_IMAGE_MAX_SIZE


def get_apps_fitness_image_min_max_size(config: dict[str, Any]) -> int:
    """Return max table-icon width/height from `apps.fitness_image_min_max_size`.

    Default `96`. Used for static WebP files under `fitness_img/min/`.

    """
    apps = config.get("apps") or {}
    raw = apps.get("fitness_image_min_max_size", DEFAULT_FITNESS_IMAGE_MIN_MAX_SIZE)
    try:
        return max(int(raw), 1)
    except (TypeError, ValueError):
        return DEFAULT_FITNESS_IMAGE_MIN_MAX_SIZE


def get_apps_fitness_lightbox_countdown_seconds(config: dict[str, Any]) -> int:
    """Return the ready-countdown before the exercise stopwatch starts.

    Reads `apps.fitness_lightbox_countdown_seconds`. Default `5`. Always at
    least `0` (skip the countdown and start the stopwatch immediately).

    """
    apps = config.get("apps") or {}
    raw = apps.get("fitness_lightbox_countdown_seconds", DEFAULT_FITNESS_LIGHTBOX_COUNTDOWN_SECONDS)
    try:
        return max(int(raw), 0)
    except (TypeError, ValueError):
        return DEFAULT_FITNESS_LIGHTBOX_COUNTDOWN_SECONDS


def get_apps_fitness_workout_gender(config: dict[str, Any]) -> str | None:
    """Return stored workout gender from `apps.fitness_workout_gender`.

    Returns `male`, `female`, or `None` when the user has not chosen yet.

    """
    apps = config.get("apps") or {}
    raw = apps.get(FITNESS_WORKOUT_GENDER_KEY)
    gender = str(raw or "").strip().lower()
    if gender in _VALID_FITNESS_WORKOUT_GENDERS:
        return gender
    return None


def get_apps_fitness_workout_history_count(config: dict[str, Any]) -> int:
    """Return how many recent sets to send when generating a workout.

    Reads `apps.fitness_workout_history_count`. Default `100`. Always at least `1`.

    """
    apps = config.get("apps") or {}
    raw = apps.get("fitness_workout_history_count", DEFAULT_FITNESS_WORKOUT_HISTORY_COUNT)
    try:
        return max(int(raw), 1)
    except (TypeError, ValueError):
        return DEFAULT_FITNESS_WORKOUT_HISTORY_COUNT


def get_apps_list_limits(config: dict[str, Any]) -> tuple[int, int]:
    """Return `(initial_count, load_more_count)` from the shared `apps` config block.

    Used for table first-page size, scroll load-more size, and similar limits
    (autocomplete sample size, frequency window) that share the same defaults.

    """
    apps = config.get("apps") or {}
    return (
        int(apps.get("initial_count", DEFAULT_INITIAL_COUNT)),
        int(apps.get("load_more_count", DEFAULT_LOAD_MORE_COUNT)),
    )


def get_apps_local_language(config: dict[str, Any]) -> str:
    """Return local language code from `apps.local_language` (default `ru`)."""
    apps = config.get("apps") or {}
    raw = apps.get("local_language", DEFAULT_LOCAL_LANGUAGE)
    code = str(raw or DEFAULT_LOCAL_LANGUAGE).strip().lower()
    return code or DEFAULT_LOCAL_LANGUAGE


def get_apps_local_language_display_name(config: dict[str, Any]) -> str:
    """Return English display name for `apps.local_language` (e.g. `Russian`)."""
    code = get_apps_local_language(config)
    if code in _LANGUAGE_DISPLAY_NAMES:
        return _LANGUAGE_DISPLAY_NAMES[code]
    return code.upper()


def get_open_quick_tab_on_startup(config: dict[str, Any], app: QuickTabAppName) -> bool:
    """Return whether the Quick tab should open first for `app`.

    Args:

    - `config` (`dict[str, Any]`): Loaded application config.
    - `app` (`QuickTabAppName`): `finance`, `food`, or `fitness`.

    Returns:

    - `bool`: `True` to open Quick first; `False` to open the second tab.

    """
    apps = config.get("apps") or {}
    raw = apps.get(open_quick_tab_on_startup_key(app), OPEN_QUICK_TAB_ON_STARTUP_DEFAULT)
    return raw if isinstance(raw, bool) else OPEN_QUICK_TAB_ON_STARTUP_DEFAULT


def open_quick_tab_on_startup_key(app: QuickTabAppName) -> str:
    """Return the `apps` config key for the Quick-tab startup preference."""
    if app not in _QUICK_TAB_APPS:
        msg = f"Unknown Quick-tab app: {app}"
        raise ValueError(msg)
    return f"{OPEN_QUICK_TAB_ON_STARTUP_KEY_PREFIX}{app}"


def set_apps_fitness_workout_gender(
    gender: str,
    *,
    config: dict[str, Any] | None = None,
    config_path: str | None = None,
) -> None:
    """Write workout gender (`male` or `female`) into `config.json`.

    Args:

    - `gender` (`str`): Athlete gender for AI workout generation.
    - `config` (`dict[str, Any] | None`): Optional in-memory config to keep in sync.
    - `config_path` (`str | None`): Config file path. Defaults to the project config.

    """
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


def set_open_quick_tab_on_startup(
    app: QuickTabAppName,
    *,
    enabled: bool,
    config: dict[str, Any] | None = None,
    config_path: str | None = None,
) -> None:
    """Write the Quick-tab startup preference for `app` into `config.json`.

    Args:

    - `app` (`QuickTabAppName`): `finance`, `food`, or `fitness`.
    - `enabled` (`bool`): `True` to open Quick first on startup.
    - `config` (`dict[str, Any] | None`): Optional in-memory config to keep in sync.
    - `config_path` (`str | None`): Config file path. Defaults to the project config.

    """
    key = open_quick_tab_on_startup_key(app)
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
    apps[key] = bool(enabled)
    path.write_text(h.dev.dumps_pretty_json(data), encoding="utf-8")
    if config is not None:
        live_apps = config.setdefault("apps", {})
        if isinstance(live_apps, dict):
            live_apps[key] = bool(enabled)


def startup_tab_index(*, open_quick: bool) -> int:
    """Return the tab index to select when an app starts."""
    return 0 if open_quick else 1
