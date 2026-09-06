"""Screen recording config helpers (audio mode, mic, countdown)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal, cast

import harrix_pylib as h

from harrix_swiss_knife.paths import get_config_path_str, get_temp_config_path

ScreenRecordAudio = Literal["none", "mic", "system", "mic_and_system"]

SCREEN_RECORD_AUDIO_MODES: frozenset[str] = frozenset({"none", "mic", "system", "mic_and_system"})
DEFAULT_SCREEN_RECORD_AUDIO: ScreenRecordAudio = "system"
DEFAULT_SCREEN_RECORD_COUNTDOWN_SECONDS = 3
_SCREEN_RECORD_AUDIO_KEY = "screen_record_audio"
_SCREEN_RECORD_COUNTDOWN_KEY = "screen_record_countdown_seconds"
_SCREEN_RECORD_MIC_KEY = "screen_record_microphone_id"
_MAX_COUNTDOWN_SECONDS = 30


def ensure_screen_record_config_defaults() -> None:
    """Write missing `apps.screen_record_countdown_seconds` into `config.json` once."""
    path = Path(get_config_path_str())
    if not path.is_file():
        return
    try:
        with path.open(encoding="utf-8") as handle:
            config = json.load(handle)
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        return
    if not isinstance(config, dict):
        return
    apps = dict(config.get("apps") or {})
    changed = False
    if _SCREEN_RECORD_COUNTDOWN_KEY not in apps:
        apps[_SCREEN_RECORD_COUNTDOWN_KEY] = DEFAULT_SCREEN_RECORD_COUNTDOWN_SECONDS
        changed = True
    # Audio lives in config-temp.json; drop a leftover key from config.json if present.
    if _SCREEN_RECORD_AUDIO_KEY in apps:
        del apps[_SCREEN_RECORD_AUDIO_KEY]
        changed = True
    if not changed:
        return
    config["apps"] = apps
    path.write_text(h.dev.dumps_pretty_json(config), encoding="utf-8")


def get_screen_record_audio(temp_config: dict[str, Any] | None = None) -> ScreenRecordAudio:
    """Return `screen_record_audio` from `config-temp.json`."""
    data = temp_config
    if data is None:
        try:
            loaded = h.dev.config_load(get_config_path_str(), is_temp=True)
            data = loaded if isinstance(loaded, dict) else {}
        except (FileNotFoundError, OSError, TypeError, ValueError):
            data = {}
    raw = str(data.get(_SCREEN_RECORD_AUDIO_KEY, DEFAULT_SCREEN_RECORD_AUDIO)).strip().lower()
    if raw in SCREEN_RECORD_AUDIO_MODES:
        return cast("ScreenRecordAudio", raw)
    return DEFAULT_SCREEN_RECORD_AUDIO


def get_screen_record_countdown_seconds(config: dict[str, Any] | None = None) -> int:
    """Return `apps.screen_record_countdown_seconds` (default `3`, clamped to `0..30`)."""
    apps = _apps(config)
    raw = apps.get(_SCREEN_RECORD_COUNTDOWN_KEY, DEFAULT_SCREEN_RECORD_COUNTDOWN_SECONDS)
    try:
        return max(0, min(int(raw), _MAX_COUNTDOWN_SECONDS))
    except (TypeError, ValueError):
        return DEFAULT_SCREEN_RECORD_COUNTDOWN_SECONDS


def get_screen_record_microphone_id(config: dict[str, Any] | None = None) -> str:
    """Return `apps.screen_record_microphone_id` (empty when unset)."""
    apps = _apps(config)
    return str(apps.get(_SCREEN_RECORD_MIC_KEY, "") or "").strip()


def save_screen_record_settings(
    *,
    audio: ScreenRecordAudio | None = None,
    countdown_seconds: int | None = None,
    microphone_id: str | None = None,
) -> None:
    """Persist screen-record settings (`audio` → config-temp; rest → `config.json`)."""
    if audio is not None and audio in SCREEN_RECORD_AUDIO_MODES:
        _save_temp_audio(audio)

    if countdown_seconds is None and microphone_id is None:
        return

    path = Path(get_config_path_str())
    with path.open(encoding="utf-8") as handle:
        config = json.load(handle)
    apps = dict(config.get("apps") or {})
    if countdown_seconds is not None:
        apps[_SCREEN_RECORD_COUNTDOWN_KEY] = max(0, min(int(countdown_seconds), _MAX_COUNTDOWN_SECONDS))
    if microphone_id is not None:
        apps[_SCREEN_RECORD_MIC_KEY] = microphone_id.strip()
    if _SCREEN_RECORD_COUNTDOWN_KEY not in apps:
        apps[_SCREEN_RECORD_COUNTDOWN_KEY] = DEFAULT_SCREEN_RECORD_COUNTDOWN_SECONDS
    apps.pop(_SCREEN_RECORD_AUDIO_KEY, None)
    config["apps"] = apps
    path.write_text(h.dev.dumps_pretty_json(config), encoding="utf-8")


def _apps(config: dict[str, Any] | None) -> dict[str, Any]:
    if config is None:
        try:
            config = h.dev.config_load(get_config_path_str())
        except (OSError, TypeError, ValueError):
            return {}
    apps = config.get("apps") or {}
    return apps if isinstance(apps, dict) else {}


def _save_temp_audio(audio: ScreenRecordAudio) -> None:
    temp_path = get_temp_config_path()
    try:
        temp_path.parent.mkdir(parents=True, exist_ok=True)
        if not temp_path.exists() or temp_path.stat().st_size == 0:
            temp_path.write_text("{}", encoding="utf-8")
        h.dev.config_update_value(
            _SCREEN_RECORD_AUDIO_KEY,
            audio,
            get_config_path_str(),
            is_temp=True,
        )
    except (FileNotFoundError, OSError, TypeError, ValueError):
        return
