"""Tests for habit Done / Not done check-in sounds."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from PySide6.QtCore import QFile
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife import resources_rc  # noqa: F401
from harrix_swiss_knife.apps.habits import checkin_sounds
from harrix_swiss_knife.apps.habits.checkin_sounds import habit_checkin_sound_name


@pytest.fixture
def qapp() -> QApplication:
    """Ensure a QApplication exists so Qt resources can be queried."""
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_habit_checkin_sound_name_maps_values() -> None:
    """Done uses check, Not done uses delete, absent is silent."""
    assert habit_checkin_sound_name(1) == "habit_done.wav"
    assert habit_checkin_sound_name(3) == "habit_done.wav"
    assert habit_checkin_sound_name(0) == "habit_not_done.wav"
    assert habit_checkin_sound_name(None) is None
    assert habit_checkin_sound_name(-1) is None


def test_habit_checkin_sounds_are_embedded(qapp: QApplication) -> None:  # noqa: ARG001
    """WAV files from UI SFX cinematic are compiled into Qt resources."""
    assert QFile.exists(":/assets/sounds/habit_done.wav")
    assert QFile.exists(":/assets/sounds/habit_not_done.wav")


def test_prime_effect_stays_silent(monkeypatch: pytest.MonkeyPatch) -> None:
    """Startup preload must not restore volume before the muted prime play starts."""
    monkeypatch.setattr(checkin_sounds, "qt_sounds_muted", lambda: False)
    effect = MagicMock()
    effect.volume.return_value = 1.0
    primed_before = set(checkin_sounds._primed)
    try:
        checkin_sounds._primed.discard("habit_not_done.wav")
        checkin_sounds._prime_effect("habit_not_done.wav", effect)
        effect.play.assert_called_once()
        volumes = [call.args[0] for call in effect.setVolume.call_args_list]
        assert volumes
        assert volumes[-1] == 0.0
    finally:
        checkin_sounds._primed.clear()
        checkin_sounds._primed.update(primed_before)
