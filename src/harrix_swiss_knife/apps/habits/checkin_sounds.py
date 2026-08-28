"""Play short CC0 UI sounds for habit Done / Not done."""

from __future__ import annotations

import contextlib
from pathlib import Path

from PySide6.QtCore import QFile, QTimer, QUrl
from PySide6.QtMultimedia import QSoundEffect

_DONE_NAME = "habit_done.wav"
_NOT_DONE_NAME = "habit_not_done.wav"
_VOLUME = 0.5

_effects: dict[str, QSoundEffect] = {}


def habit_checkin_sound_name(value: int | None) -> str | None:
    """Return the bundled WAV name for a stored check-in value."""
    if value is None:
        return None
    if value == 0:
        return _NOT_DONE_NAME
    if value > 0:
        return _DONE_NAME
    return None


def play_habit_checkin_sound(value: int | None) -> None:
    """Play the Done or Not done sound without blocking the UI.

    Loading and playback are deferred to the next event-loop turn so the
    checkmark can paint before audio work runs.

    """
    name = habit_checkin_sound_name(value)
    if name is None:
        return
    QTimer.singleShot(0, lambda sound_name=name: _play_named(sound_name))


def _effect_for(name: str) -> QSoundEffect | None:
    cached = _effects.get(name)
    if cached is not None:
        return cached
    url = _sound_url(name)
    if not url.isValid():
        return None
    effect = QSoundEffect()
    effect.setSource(url)
    effect.setVolume(_VOLUME)
    _effects[name] = effect
    return effect


def _play_named(name: str) -> None:
    effect = _effect_for(name)
    if effect is None:
        return
    status = effect.status()
    if status == QSoundEffect.Status.Ready:
        effect.play()
        return
    if status == QSoundEffect.Status.Error:
        return

    def _on_status(new_status: QSoundEffect.Status) -> None:
        if new_status == QSoundEffect.Status.Error:
            with contextlib.suppress(RuntimeError):
                effect.statusChanged.disconnect(_on_status)
            return
        if new_status != QSoundEffect.Status.Ready:
            return
        with contextlib.suppress(RuntimeError):
            effect.statusChanged.disconnect(_on_status)
        effect.play()

    effect.statusChanged.connect(_on_status)


def _sound_url(name: str) -> QUrl:
    qrc_path = f":/assets/sounds/{name}"
    if QFile.exists(qrc_path):
        return QUrl(f"qrc:/assets/sounds/{name}")
    disk = Path(__file__).resolve().parents[2] / "assets" / "sounds" / name
    if disk.is_file():
        return QUrl.fromLocalFile(str(disk))
    return QUrl()
