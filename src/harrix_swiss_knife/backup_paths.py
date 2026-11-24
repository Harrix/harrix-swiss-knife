"""Shared backup root from `config.json` (`path_backups`).

All backup writers (MusicBee, Cursor, bookmarks, Saved Commands, Habits,
Beat Saber) should use this folder so Dropbox / external drives stay in one place.

Resolution order:

1. `config-temp.json` → `path_backups` or `musicbee.backup_dir`
2. `config.json` → `path_backups` or `musicbee.backup_dir`
3. Optional in-memory `config` mapping (tests / MusicBee fallback)
4. `%LOCALAPPDATA%/HarrixSwissKnife/Backups`

"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

import harrix_pylib as h

from harrix_swiss_knife.paths import get_config_path_str, get_temp_config_path

PATH_BACKUPS_KEY = "path_backups"
_SUBDIR_BEAT_SABER = "BeatSaber"
_SUBDIR_BROWSER_BOOKMARKS = "browser_bookmarks"
_SUBDIR_CURSOR = "Cursor"
_SUBDIR_HABITS = "Habits"
_SUBDIR_MUSICBEE = "MusicBee"
_SUBDIR_SAVE_COMMANDS = "save_commands"
_SUBDIR_TICKTICK = "TickTick"


def backup_subdir(name: str, config: dict[str, Any] | None = None, *, config_path: str | None = None) -> Path:
    """Return `{path_backups}/{name}`, creating it when missing."""
    path = resolve_backup_dir(config, config_path=config_path) / name
    path.mkdir(parents=True, exist_ok=True)
    return path


def beat_saber_backup_root(config: dict[str, Any] | None = None, *, config_path: str | None = None) -> Path:
    """Return the folder for Beat Saber save ZIP backups."""
    return backup_subdir(_SUBDIR_BEAT_SABER, config, config_path=config_path)


def browser_bookmarks_backup_root(config: dict[str, Any] | None = None, *, config_path: str | None = None) -> Path:
    """Return the folder for Chrome/Yandex Bookmarks backups."""
    return backup_subdir(_SUBDIR_BROWSER_BOOKMARKS, config, config_path=config_path)


def cursor_backup_root(config: dict[str, Any] | None = None, *, config_path: str | None = None) -> Path:
    """Return the folder for Cursor AI ZIP backups."""
    return backup_subdir(_SUBDIR_CURSOR, config, config_path=config_path)


def habits_backup_root(config: dict[str, Any] | None = None, *, config_path: str | None = None) -> Path:
    """Return the folder for Habits tracker backups."""
    return backup_subdir(_SUBDIR_HABITS, config, config_path=config_path)


def musicbee_backup_root(config: dict[str, Any] | None = None, *, config_path: str | None = None) -> Path:
    """Return the shared backups root used by MusicBee (parent of `MusicBee/…`)."""
    return resolve_backup_dir(config, config_path=config_path)


def resolve_backup_dir(config: dict[str, Any] | None = None, *, config_path: str | None = None) -> Path:
    """Return the shared backups directory from config (see module docstring)."""
    path_str = config_path or get_config_path_str()
    temp_value = _read_path_backups_from_file(_temp_config_path(path_str))
    if temp_value is not None:
        return temp_value

    file_value = _path_backups_from_mapping(_load_config(path_str))
    if file_value is not None:
        return file_value

    if config is not None:
        provided = _path_backups_from_mapping(config)
        if provided is not None:
            return provided

    return _default_local_backups_dir()


def save_commands_backup_root(config: dict[str, Any] | None = None) -> Path:
    """Return the folder for Save Commands `state.vscdb` backups."""
    return backup_subdir(_SUBDIR_SAVE_COMMANDS, config)


def ticktick_backup_root(config: dict[str, Any] | None = None) -> Path:
    """Return the folder for TickTick-only backups."""
    return backup_subdir(_SUBDIR_TICKTICK, config)


def _default_local_backups_dir() -> Path:
    if sys.platform == "win32":
        local = os.environ.get("LOCALAPPDATA")
        if not local:
            local = str(Path.home() / "AppData" / "Local")
        return Path(local) / "HarrixSwissKnife" / "Backups"
    xdg = os.environ.get("XDG_DATA_HOME")
    base = Path(xdg) if xdg else Path.home() / ".local" / "share"
    return base / "harrix-swiss-knife" / "Backups"


def _load_config(config_path: str) -> dict[str, Any]:
    try:
        loaded = h.dev.config_load(config_path, resolve_snippets=False)
    except (OSError, TypeError, ValueError, FileNotFoundError):
        return {}
    return loaded if isinstance(loaded, dict) else {}


def _path_backups_from_mapping(data: dict[str, Any] | None) -> Path | None:
    if not isinstance(data, dict):
        return None
    raw = str(data.get(PATH_BACKUPS_KEY) or "").strip()
    if raw:
        return Path(raw)
    block = data.get("musicbee")
    if isinstance(block, dict):
        legacy = str(block.get("backup_dir") or "").strip()
        if legacy:
            return Path(legacy)
    return None


def _read_path_backups_from_file(path: Path) -> Path | None:
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, TypeError, ValueError, json.JSONDecodeError):
        return None
    return _path_backups_from_mapping(data if isinstance(data, dict) else None)


def _temp_config_path(config_path: str) -> Path:
    primary = Path(config_path)
    sibling = primary.with_name(f"{primary.stem}-temp{primary.suffix}")
    default_temp = get_temp_config_path()
    if sibling.is_file():
        return sibling
    return default_temp
