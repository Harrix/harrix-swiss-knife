"""Camera shutter click for successful region screenshots."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import harrix_pylib as h
from PySide6.QtCore import QFile, QUrl
from PySide6.QtMultimedia import QSoundEffect

from harrix_swiss_knife.paths import get_config_path_str
from harrix_swiss_knife.qt_sounds import qt_sounds_muted

SCREENSHOT_SHUTTER_SOUND_KEY = "screenshot_shutter_sound"
_SOUND_NAME = "screenshot_shutter.wav"
_VOLUME = 1.0
_MAX_LIVE_EFFECTS = 4

_live_effects: list[QSoundEffect] = []
_prime_state: dict[str, Any] = {"effect": None, "ready": False}


def load_screenshot_shutter_sound_enabled() -> bool:
    """Return whether the screenshot shutter sound is enabled in `config.json`."""
    try:
        config = h.dev.config_load(get_config_path_str())
    except (FileNotFoundError, OSError, ValueError):
        return True
    value = config.get(SCREENSHOT_SHUTTER_SOUND_KEY, True)
    if isinstance(value, bool):
        return value
    return bool(value)


def play_screenshot_shutter_sound() -> None:
    """Play the camera shutter sound after a successful region capture.

    Respects `screenshot_shutter_sound` in config and `HSK_MUTE_SOUNDS` / pytest.

    """
    if qt_sounds_muted() or not load_screenshot_shutter_sound_enabled():
        return
    url = _sound_url(_SOUND_NAME)
    if not url.isValid():
        return
    _ensure_primed(url)
    effect = QSoundEffect()
    effect.setSource(url)
    effect.setVolume(_VOLUME)
    _prune_live_effects()
    _live_effects.append(effect)
    effect.play()


def preload_screenshot_shutter_sound() -> None:
    """Warm the audio device so the first capture click is audible on Windows."""
    if qt_sounds_muted():
        return
    url = _sound_url(_SOUND_NAME)
    if url.isValid():
        _ensure_primed(url)


def screenshot_shutter_sound_name() -> str:
    """Return the bundled WAV filename for the shutter click."""
    return _SOUND_NAME


def _ensure_primed(url: QUrl) -> None:
    if _prime_state["ready"] and _prime_state["effect"] is not None:
        return
    effect = QSoundEffect()
    effect.setVolume(0.0)
    effect.setSource(url)
    _prime_state["effect"] = effect

    def on_ready() -> None:
        if effect.status() != QSoundEffect.Status.Ready or _prime_state["ready"]:
            return
        _prime_state["ready"] = True
        if qt_sounds_muted():
            return
        effect.setVolume(0.0)
        effect.play()

    effect.statusChanged.connect(on_ready)
    if effect.status() == QSoundEffect.Status.Ready:
        on_ready()


def _prune_live_effects() -> None:
    live = [effect for effect in _live_effects if effect.isPlaying()]
    if len(live) >= _MAX_LIVE_EFFECTS:
        live = live[-(_MAX_LIVE_EFFECTS - 1) :]
    _live_effects.clear()
    _live_effects.extend(live)


def _sound_url(name: str) -> QUrl:
    qrc_path = f":/assets/sounds/{name}"
    if QFile.exists(qrc_path):
        return QUrl(f"qrc:/assets/sounds/{name}")
    disk = Path(__file__).resolve().parents[1] / "assets" / "sounds" / name
    if disk.is_file():
        return QUrl.fromLocalFile(str(disk))
    return QUrl()
