"""Load MusicBee action settings from `config.json` / `config-temp.json`."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from harrix_swiss_knife.paths import get_config_path_str, get_temp_config_path

DEFAULT_AUDIO_EXTENSIONS = (".mp3", ".flac", ".m4a", ".ogg", ".opus", ".wav", ".wma")
DEFAULT_STREAM_PREFIX = "Stream - "
DEFAULT_MUSICBEE_RULES: list[dict[str, Any]] = [
    {"type": "restrict_folder", "playlists": "Stream - *", "folder": "{stream_root}"},
    {"type": "ensure_subset", "source": "Stream - Epic (real)", "target": "Stream - Epic"},
    {"type": "ensure_subset", "source": "Stream - OST (real)", "target": "Stream - OST"},
    {"type": "ensure_subset", "source": "Stream - Power metal", "target": "Stream - Heavy"},
    {
        "type": "union",
        "target": "Stream - Mad (both)",
        "sources": ["Stream - Mad", "Stream - Mad (electro)"],
    },
    {
        "type": "rebuild_remainder",
        "playlist": "Stream - Temp",
        "from_folder": "{stream_root}",
        "exclude_playlists": "Stream - *",
    },
]


@dataclass(frozen=True, slots=True)
class MusicBeeSettings:
    """Resolved MusicBee paths and Stream rules."""

    library_dir: Path
    music_root: Path
    stream_root: Path
    backup_dir: Path
    audio_extensions: frozenset[str]
    stream_playlist_prefix: str
    rules: list[dict[str, Any]]

    @property
    def library_file(self) -> Path:
        """`MusicBeeLibrary.mbl` path."""
        return self.library_dir / "MusicBeeLibrary.mbl"

    @property
    def placeholders(self) -> dict[str, str]:
        """Values for `{music_root}` / `{stream_root}` in rules."""
        return {
            "music_root": str(self.music_root),
            "stream_root": str(self.stream_root),
        }

    @property
    def playlists_dir(self) -> Path:
        """Directory that holds `.mbp` / `.xautopf` files."""
        return self.library_dir / "Playlists"


def default_musicbee_config() -> dict[str, Any]:
    """Return the example `musicbee` object for `config.example.json`."""
    return {
        "library_dir": "D:/Dropbox/Programs/MusicBee/Library",
        "music_root": "C:/Users/sergi/OneDrive/Music",
        "stream_root": "C:/Users/sergi/OneDrive/Music/Stream",
        "backup_dir": "D:/Dropbox/Backups",
        "audio_extensions": list(DEFAULT_AUDIO_EXTENSIONS),
        "stream_playlist_prefix": DEFAULT_STREAM_PREFIX,
        "rules": list(DEFAULT_MUSICBEE_RULES),
    }


def load_musicbee_settings(
    config: dict[str, Any],
    *,
    config_path: str | None = None,
) -> MusicBeeSettings:
    """Read the `musicbee` block, allowing `backup_dir` from `config-temp.json`."""
    block = config.get("musicbee")
    if block is None:
        msg = "config.json is missing the musicbee object"
        raise ValueError(msg)
    if not isinstance(block, dict):
        msg = "config.json musicbee must be an object"
        raise TypeError(msg)
    library_dir = _required_path(block, "library_dir")
    music_root = _required_path(block, "music_root")
    stream_root = _required_path(block, "stream_root")
    backup_dir = _backup_dir(block, config_path)
    raw_ext = block.get("audio_extensions") or list(DEFAULT_AUDIO_EXTENSIONS)
    extensions = frozenset(str(item).casefold() for item in raw_ext if str(item).strip())
    prefix = str(block.get("stream_playlist_prefix") or DEFAULT_STREAM_PREFIX)
    rules = block.get("rules")
    if not isinstance(rules, list) or not rules:
        rules = list(DEFAULT_MUSICBEE_RULES)
    return MusicBeeSettings(
        library_dir=library_dir,
        music_root=music_root,
        stream_root=stream_root,
        backup_dir=backup_dir,
        audio_extensions=extensions,
        stream_playlist_prefix=prefix,
        rules=[item for item in rules if isinstance(item, dict)],
    )


def _backup_dir(block: dict[str, Any], config_path: str | None) -> Path:
    temp_override = _temp_backup_dir(config_path)
    if temp_override is not None:
        return temp_override
    return _required_path(block, "backup_dir")


def _required_path(block: dict[str, Any], key: str) -> Path:
    raw = str(block.get(key) or "").strip()
    if not raw:
        msg = f"musicbee.{key} is missing"
        raise ValueError(msg)
    return Path(raw)


def _sibling_temp_config(config_path: Path) -> Path:
    return config_path.with_name(f"{config_path.stem}-temp{config_path.suffix}")


def _temp_backup_dir(config_path: str | None) -> Path | None:
    if config_path:
        temp_path = _sibling_temp_config(Path(config_path))
    else:
        temp_path = get_temp_config_path()
        if not temp_path.is_file():
            sibling = _sibling_temp_config(Path(get_config_path_str()))
            temp_path = sibling if sibling.is_file() else temp_path
    if not temp_path.is_file():
        return None
    try:
        data = json.loads(temp_path.read_text(encoding="utf-8"))
    except (OSError, TypeError, ValueError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict):
        return None
    block = data.get("musicbee")
    if not isinstance(block, dict):
        return None
    raw = str(block.get("backup_dir") or "").strip()
    return Path(raw) if raw else None
