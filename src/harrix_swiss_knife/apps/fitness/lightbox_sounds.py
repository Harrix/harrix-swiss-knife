"""Loop a short alert when a workout exercise slot runs out."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QFile, QUrl
from PySide6.QtMultimedia import QSoundEffect

_ALERT_NAME = "habit_done.wav"
_VOLUME = 0.5

_alert_effects: list[QSoundEffect] = []


def play_fitness_timer_alert() -> None:
    """Start a looping alert if one is not already playing."""
    if _alert_effects and _alert_effects[0].isPlaying():
        return
    url = _sound_url(_ALERT_NAME)
    if not url.isValid():
        return
    effect = QSoundEffect()
    effect.setSource(url)
    effect.setVolume(_VOLUME)
    effect.setLoopCount(QSoundEffect.Infinite)
    _alert_effects.clear()
    _alert_effects.append(effect)
    effect.play()


def stop_fitness_timer_alert() -> None:
    """Stop the workout-slot alert if it is playing."""
    for effect in _alert_effects:
        effect.stop()
    _alert_effects.clear()


def _sound_url(name: str) -> QUrl:
    qrc_path = f":/assets/sounds/{name}"
    if QFile.exists(qrc_path):
        return QUrl(f"qrc:/assets/sounds/{name}")
    disk = Path(__file__).resolve().parents[2] / "assets" / "sounds" / name
    if disk.is_file():
        return QUrl.fromLocalFile(str(disk))
    return QUrl()
