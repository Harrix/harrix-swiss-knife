"""Play short CC0 UI sounds for habit Done / Not done."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QFile, QTimer, QUrl
from PySide6.QtMultimedia import QSoundEffect

from harrix_swiss_knife.qt_sounds import qt_sounds_muted

_DONE_NAME = "habit_done.wav"
_NOT_DONE_NAME = "habit_not_done.wav"
_SOUND_NAMES = (_DONE_NAME, _NOT_DONE_NAME)
_VOLUME_DONE = 0.5
_VOLUME_NOT_DONE = 1.0

_effects: dict[str, QSoundEffect] = {}
_pending_play: set[str] = set()
_primed: set[str] = set()


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
    if name is None or qt_sounds_muted():
        return
    preload_habit_checkin_sounds()
    QTimer.singleShot(0, lambda sound_name=name: _play_named(sound_name))


def preload_habit_checkin_sounds() -> None:
    """Decode both check-in effects so the first click of each type can play."""
    for name in _SOUND_NAMES:
        _effect_for(name)


def _effect_for(name: str) -> QSoundEffect | None:
    cached = _effects.get(name)
    if cached is not None:
        cached.setVolume(_volume_for(name))
        return cached
    url = _sound_url(name)
    if not url.isValid():
        return None
    effect = QSoundEffect()
    # Connect before setSource: Ready can fire before the caller inspects status.
    effect.statusChanged.connect(lambda n=name, e=effect: _on_effect_status(n, e))
    effect.setSource(url)
    effect.setVolume(_volume_for(name))
    _effects[name] = effect
    if effect.status() == QSoundEffect.Status.Ready:
        _on_effect_status(name, effect)
    return effect


def _on_effect_status(name: str, effect: QSoundEffect) -> None:
    status = effect.status()
    if status == QSoundEffect.Status.Error:
        _pending_play.discard(name)
        return
    if status != QSoundEffect.Status.Ready:
        return
    if name not in _primed:
        _prime_effect(name, effect)
        if name in _pending_play:
            QTimer.singleShot(0, lambda n=name, e=effect: _play_pending(n, e))
        return
    if name in _pending_play:
        _play_pending(name, effect)


def _play_named(name: str) -> None:
    if qt_sounds_muted():
        return
    effect = _effect_for(name)
    if effect is None:
        return
    if effect.status() == QSoundEffect.Status.Error:
        return
    if effect.status() == QSoundEffect.Status.Ready and name in _primed:
        effect.play()
        return
    _pending_play.add(name)
    if effect.status() == QSoundEffect.Status.Ready:
        _on_effect_status(name, effect)


def _play_pending(name: str, effect: QSoundEffect) -> None:
    _pending_play.discard(name)
    if qt_sounds_muted():
        return
    if effect.status() != QSoundEffect.Status.Ready:
        return
    effect.setVolume(_volume_for(name))
    effect.play()


def _prime_effect(name: str, effect: QSoundEffect) -> None:
    """Warm the Windows audio device; the first play() of a new effect is often silent."""
    _primed.add(name)
    if qt_sounds_muted():
        return
    saved = effect.volume()
    effect.setVolume(0.0)
    effect.play()
    effect.setVolume(saved)


def _sound_url(name: str) -> QUrl:
    qrc_path = f":/assets/sounds/{name}"
    if QFile.exists(qrc_path):
        return QUrl(f"qrc:/assets/sounds/{name}")
    disk = Path(__file__).resolve().parents[2] / "assets" / "sounds" / name
    if disk.is_file():
        return QUrl.fromLocalFile(str(disk))
    return QUrl()


def _volume_for(name: str) -> float:
    if name == _NOT_DONE_NAME:
        return _VOLUME_NOT_DONE
    return _VOLUME_DONE
