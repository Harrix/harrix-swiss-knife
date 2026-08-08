"""Shared config helpers for desktop apps."""

from __future__ import annotations

from typing import Any

DEFAULT_INITIAL_COUNT = 1000
DEFAULT_LOAD_MORE_COUNT = 500
DEFAULT_LOCAL_LANGUAGE = "ru"

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
