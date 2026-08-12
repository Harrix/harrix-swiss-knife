"""Persist Vector Icons UI settings in config files."""

from __future__ import annotations

import contextlib
from pathlib import Path

import harrix_pylib as h

from harrix_swiss_knife.paths import get_config_path_str, get_temp_config_path

ICON_SIZE_KEY = "vector_icons_icon_size"
CATEGORY_ICONS_KEY = "vector_icons_category_icons"
RECENT_FOLDERS_KEY = "vector_icons_recent_folders"
PINNED_FOLDERS_KEY = "path_vector_icons_pinned"
RECENT_FOLDERS_MAX_KEY = "vector_icons_recent_folders_max"
ICON_SIZE_MIN = 64
ICON_SIZE_MAX = 256
ICON_SIZE_DEFAULT = 160
RECENT_FOLDERS_MAX_DEFAULT = 12
RECENT_FOLDERS_MAX_LIMIT = 50


def clamp_icon_size(value: object) -> int:
    """Return icon size clamped to the supported slider range."""
    if isinstance(value, bool):
        return ICON_SIZE_DEFAULT
    if isinstance(value, int):
        size = value
    elif isinstance(value, float):
        size = int(value)
    elif isinstance(value, str):
        try:
            size = int(value.strip())
        except ValueError:
            return ICON_SIZE_DEFAULT
    else:
        return ICON_SIZE_DEFAULT
    return max(ICON_SIZE_MIN, min(ICON_SIZE_MAX, size))


def clamp_recent_folders_max(value: object) -> int:
    """Return recent-folders capacity clamped to a safe range."""
    if isinstance(value, bool):
        return RECENT_FOLDERS_MAX_DEFAULT
    if isinstance(value, int):
        size = value
    elif isinstance(value, float):
        size = int(value)
    elif isinstance(value, str):
        try:
            size = int(value.strip())
        except ValueError:
            return RECENT_FOLDERS_MAX_DEFAULT
    else:
        return RECENT_FOLDERS_MAX_DEFAULT
    return max(1, min(RECENT_FOLDERS_MAX_LIMIT, size))


def load_category_icons() -> dict[str, str]:
    """Load category → family-id map from `config-temp.json`."""
    try:
        config = h.dev.config_load(get_config_path_str(), is_temp=True)
    except (FileNotFoundError, OSError, ValueError):
        return {}
    raw = config.get(CATEGORY_ICONS_KEY)
    if not isinstance(raw, dict):
        return {}
    result: dict[str, str] = {}
    for key, value in raw.items():
        category = str(key).strip()
        family_id = str(value).strip()
        if category and family_id:
            result[category] = family_id
    return result


def load_icon_size() -> int:
    """Load icon display size from `config-temp.json`."""
    try:
        config = h.dev.config_load(get_config_path_str(), is_temp=True)
    except (FileNotFoundError, OSError, ValueError):
        return ICON_SIZE_DEFAULT
    return clamp_icon_size(config.get(ICON_SIZE_KEY, ICON_SIZE_DEFAULT))


def load_pinned_folders() -> list[Path]:
    """Load pinned folders from `config.json` (`path_vector_icons_pinned`).

    When the pinned list is empty, fall back to `path_vector_icons` and
    `path_vector_icons_ai` when those paths exist.

    """
    try:
        config = h.dev.config_load(get_config_path_str())
    except (FileNotFoundError, OSError, ValueError):
        return []
    pinned = _parse_path_list(config.get(PINNED_FOLDERS_KEY))
    if pinned:
        return pinned
    fallback: list[Path] = []
    for key in ("path_vector_icons", "path_vector_icons_ai"):
        raw = str(config.get(key) or "").strip()
        if not raw or raw.startswith("<"):
            continue
        path = Path(raw)
        if path.is_dir() and path not in fallback:
            fallback.append(path)
    return fallback


def load_recent_folders() -> list[Path]:
    """Load recent folders from `config-temp.json`, newest first."""
    try:
        config = h.dev.config_load(get_config_path_str(), is_temp=True)
    except (FileNotFoundError, OSError, ValueError):
        return []
    paths = _parse_path_list(config.get(RECENT_FOLDERS_KEY))
    return paths[: load_recent_folders_max()]


def load_recent_folders_max() -> int:
    """Load max unique recent folders from `config.json`."""
    try:
        config = h.dev.config_load(get_config_path_str())
    except (FileNotFoundError, OSError, ValueError):
        return RECENT_FOLDERS_MAX_DEFAULT
    return clamp_recent_folders_max(config.get(RECENT_FOLDERS_MAX_KEY, RECENT_FOLDERS_MAX_DEFAULT))


def pin_folder(path: Path) -> list[Path]:
    """Add `path` to pinned folders in `config.json` and return the new list."""
    resolved = path.expanduser().resolve()
    if not resolved.is_dir():
        return load_pinned_folders()
    try:
        config = h.dev.config_load(get_config_path_str())
    except (FileNotFoundError, OSError, ValueError):
        config = {}
    existing = _parse_path_list(config.get(PINNED_FOLDERS_KEY))
    if not existing:
        # Materialize fallback defaults before appending.
        existing = load_pinned_folders()
    updated = [resolved, *[item for item in existing if item.resolve() != resolved]]
    h.dev.config_update_value(
        PINNED_FOLDERS_KEY,
        [str(item) for item in updated],
        get_config_path_str(),
    )
    return updated


def remember_recent_folder(path: Path) -> list[Path]:
    """Prepend `path` to recent folders and persist in `config-temp.json`."""
    resolved = path.expanduser().resolve()
    if not resolved.is_dir():
        return load_recent_folders()
    max_count = load_recent_folders_max()
    current = [item for item in load_recent_folders() if item.resolve() != resolved]
    updated = [resolved, *current][:max_count]
    _ensure_temp_config()
    h.dev.config_update_value(
        RECENT_FOLDERS_KEY,
        [str(item) for item in updated],
        get_config_path_str(),
        is_temp=True,
    )
    return updated


def save_category_icons(mapping: dict[str, str]) -> None:
    """Persist category → family-id map in `config-temp.json`."""
    cleaned: dict[str, str] = {}
    for key, value in mapping.items():
        category = str(key).strip()
        family_id = str(value).strip()
        if category and family_id:
            cleaned[category] = family_id
    _ensure_temp_config()
    h.dev.config_update_value(
        CATEGORY_ICONS_KEY,
        cleaned,
        get_config_path_str(),
        is_temp=True,
    )


def save_icon_size(size: int) -> None:
    """Persist icon display size in `config-temp.json`."""
    _ensure_temp_config()
    h.dev.config_update_value(
        ICON_SIZE_KEY,
        clamp_icon_size(size),
        get_config_path_str(),
        is_temp=True,
    )


def set_category_icon(category: str, family_id: str) -> dict[str, str]:
    """Assign `family_id` as the icon for `category` and persist the map."""
    mapping = load_category_icons()
    mapping[category.strip()] = family_id.strip()
    save_category_icons(mapping)
    return mapping


def _ensure_temp_config() -> None:
    temp_config_path = get_temp_config_path()
    temp_config_path.parent.mkdir(parents=True, exist_ok=True)
    if not temp_config_path.exists() or temp_config_path.stat().st_size == 0:
        temp_config_path.write_text("{}", encoding="utf-8")


def _parse_path_list(raw: object) -> list[Path]:
    if not isinstance(raw, list):
        return []
    result: list[Path] = []
    seen: set[str] = set()
    for item in raw:
        text = str(item).strip()
        if not text or text.startswith("<"):
            continue
        path = Path(text)
        key = str(path)
        with contextlib.suppress(OSError):
            key = str(path.resolve())
        if key in seen:
            continue
        seen.add(key)
        if path.is_dir():
            result.append(path)
    return result
