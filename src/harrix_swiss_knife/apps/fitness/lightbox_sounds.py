"""Timer and outcome cues for the Fitness exercise lightbox."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from PySide6.QtCore import QFile, QUrl
from PySide6.QtMultimedia import QSoundEffect

from harrix_swiss_knife.qt_sounds import qt_sounds_muted

_CUE_NAMES: dict[str, str] = {
    "ready": "fitness_ready.wav",
    "3": "fitness_3.wav",
    "2": "fitness_2.wav",
    "1": "fitness_1.wav",
    "go": "fitness_go.wav",
    "time_over": "fitness_time_over.wav",
    "applause": "fitness_applause.wav",
    "congratulations": "fitness_congratulations.wav",
    "success": "fitness_success.wav",
    "paste": "fitness_paste.wav",
    "pause": "fitness_pause.wav",
    "continue": "fitness_continue.wav",
}
_VOLUME = 0.9
_MAX_LIVE_EFFECTS = 8

_cue_effects: list[QSoundEffect] = []

FitnessTimerCue = Literal[
    "ready",
    "3",
    "2",
    "1",
    "go",
    "time_over",
    "applause",
    "congratulations",
    "success",
    "paste",
    "pause",
    "continue",
]


def fitness_timer_cue_sound_name(cue: FitnessTimerCue) -> str:
    """Return the bundled WAV name for a fitness cue."""
    return _CUE_NAMES[cue]


def play_fitness_timer_cue(cue: FitnessTimerCue) -> None:
    """Play a one-shot fitness cue without cutting off earlier voices."""
    if qt_sounds_muted():
        return
    url = _sound_url(fitness_timer_cue_sound_name(cue))
    if not url.isValid():
        return
    effect = QSoundEffect()
    effect.setSource(url)
    effect.setVolume(_VOLUME)
    _prune_cue_effects()
    _cue_effects.append(effect)
    effect.play()


def stop_fitness_timer_alert() -> None:
    """No-op kept for call sites that used the old looping overtime alert."""


def _prune_cue_effects() -> None:
    live = [effect for effect in _cue_effects if effect.isPlaying()]
    if len(live) >= _MAX_LIVE_EFFECTS:
        live = live[-(_MAX_LIVE_EFFECTS - 1) :]
    _cue_effects.clear()
    _cue_effects.extend(live)


def _sound_url(name: str) -> QUrl:
    qrc_path = f":/assets/sounds/{name}"
    if QFile.exists(qrc_path):
        return QUrl(f"qrc:/assets/sounds/{name}")
    disk = Path(__file__).resolve().parents[2] / "assets" / "sounds" / name
    if disk.is_file():
        return QUrl.fromLocalFile(str(disk))
    return QUrl()
