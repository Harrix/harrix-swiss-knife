"""Camera shutter click for successful region screenshots."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import harrix_pylib as h
from PySide6.QtCore import QFile, QTimer, QUrl
from PySide6.QtMultimedia import QSoundEffect

from harrix_swiss_knife.paths import get_config_path_str
from harrix_swiss_knife.qt_sounds import qt_sounds_muted

SCREENSHOT_SHUTTER_SOUND_KEY = "screenshot_shutter_sound"
_SOUND_NAME = "screenshot_shutter.wav"
_VOLUME = 0.85

_state: dict[str, Any] = {
    "effect": None,
    "pending_play": False,
    "primed": False,
}


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
    preload_screenshot_shutter_sound()
    QTimer.singleShot(0, _play)


def preload_screenshot_shutter_sound() -> None:
    """Decode the shutter effect so the first capture can play immediately."""
    _effect_for()


def screenshot_shutter_sound_name() -> str:
    """Return the bundled WAV filename for the shutter click."""
    return _SOUND_NAME


def _effect_for() -> QSoundEffect | None:
    cached = _state["effect"]
    if cached is not None:
        return cached
    url = _sound_url(_SOUND_NAME)
    if not url.isValid():
        return None
    effect = QSoundEffect()
    effect.setVolume(0.0)
    effect.statusChanged.connect(lambda e=effect: _on_effect_status(e))
    effect.setSource(url)
    _state["effect"] = effect
    if effect.status() == QSoundEffect.Status.Ready:
        _on_effect_status(effect)
    return effect


def _on_effect_status(effect: QSoundEffect) -> None:
    status = effect.status()
    if status == QSoundEffect.Status.Error:
        _state["pending_play"] = False
        return
    if status != QSoundEffect.Status.Ready:
        return
    if not _state["primed"]:
        _prime_effect(effect)
        if _state["pending_play"]:
            QTimer.singleShot(0, lambda e=effect: _play_pending(e))
        return
    if _state["pending_play"]:
        _play_pending(effect)


def _play() -> None:
    if qt_sounds_muted() or not load_screenshot_shutter_sound_enabled():
        return
    effect = _effect_for()
    if effect is None:
        return
    if effect.status() == QSoundEffect.Status.Error:
        return
    if effect.status() == QSoundEffect.Status.Ready and _state["primed"]:
        effect.setVolume(_VOLUME)
        effect.play()
        return
    _state["pending_play"] = True
    if effect.status() == QSoundEffect.Status.Ready:
        _on_effect_status(effect)


def _play_pending(effect: QSoundEffect) -> None:
    _state["pending_play"] = False
    if qt_sounds_muted() or not load_screenshot_shutter_sound_enabled():
        return
    if effect.status() != QSoundEffect.Status.Ready:
        return
    effect.setVolume(_VOLUME)
    effect.play()


def _prime_effect(effect: QSoundEffect) -> None:
    """Warm the Windows audio device; the first play() of a new effect is often silent."""
    _state["primed"] = True
    if qt_sounds_muted():
        return
    effect.setVolume(0.0)
    effect.play()


def _sound_url(name: str) -> QUrl:
    qrc_path = f":/assets/sounds/{name}"
    if QFile.exists(qrc_path):
        return QUrl(f"qrc:/assets/sounds/{name}")
    disk = Path(__file__).resolve().parents[1] / "assets" / "sounds" / name
    if disk.is_file():
        return QUrl.fromLocalFile(str(disk))
    return QUrl()
