"""Play short CC0 UI sounds for habit Done / Not done."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QFile, QUrl
from PySide6.QtMultimedia import QSoundEffect

_DONE_NAME = "habit_done.wav"
_NOT_DONE_NAME = "habit_not_done.wav"
_VOLUME = 0.5

_active_effects: list[QSoundEffect] = []


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
    """Play the Done or Not done sound after a successful user check-in."""
    name = habit_checkin_sound_name(value)
    if name is None:
        return
    url = _sound_url(name)
    if not url.isValid():
        return
    effect = QSoundEffect()
    effect.setSource(url)
    effect.setVolume(_VOLUME)
    _active_effects.clear()
    _active_effects.append(effect)
    effect.play()


def _sound_url(name: str) -> QUrl:
    qrc_path = f":/assets/sounds/{name}"
    if QFile.exists(qrc_path):
        return QUrl(f"qrc:/assets/sounds/{name}")
    disk = Path(__file__).resolve().parents[2] / "assets" / "sounds" / name
    if disk.is_file():
        return QUrl.fromLocalFile(str(disk))
    return QUrl()
