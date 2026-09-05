"""Screen recording config helpers (audio mode + countdown)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal, cast

import harrix_pylib as h

from harrix_swiss_knife.paths import get_config_path_str

ScreenRecordAudio = Literal["none", "mic", "system", "mic_and_system"]

SCREEN_RECORD_AUDIO_MODES: frozenset[str] = frozenset({"none", "mic", "system", "mic_and_system"})
DEFAULT_SCREEN_RECORD_AUDIO: ScreenRecordAudio = "system"
DEFAULT_SCREEN_RECORD_COUNTDOWN_SECONDS = 3
_SCREEN_RECORD_AUDIO_KEY = "screen_record_audio"
_SCREEN_RECORD_COUNTDOWN_KEY = "screen_record_countdown_seconds"
_MAX_COUNTDOWN_SECONDS = 30


def get_screen_record_audio(config: dict[str, Any] | None = None) -> ScreenRecordAudio:
    """Return `apps.screen_record_audio` (`none` / `mic` / `system` / `mic_and_system`)."""
    apps = _apps(config)
    raw = str(apps.get(_SCREEN_RECORD_AUDIO_KEY, DEFAULT_SCREEN_RECORD_AUDIO)).strip().lower()
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


def save_screen_record_settings(
    *,
    audio: ScreenRecordAudio | None = None,
    countdown_seconds: int | None = None,
) -> None:
    """Persist screen-record settings under `apps` in `config.json`."""
    path = Path(get_config_path_str())
    with path.open(encoding="utf-8") as handle:
        config = json.load(handle)
    apps = dict(config.get("apps") or {})
    if audio is not None and audio in SCREEN_RECORD_AUDIO_MODES:
        apps[_SCREEN_RECORD_AUDIO_KEY] = audio
    if countdown_seconds is not None:
        apps[_SCREEN_RECORD_COUNTDOWN_KEY] = max(0, min(int(countdown_seconds), _MAX_COUNTDOWN_SECONDS))
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
