"""Tests for habit Done / Not done check-in sounds."""

from __future__ import annotations

import pytest
from PySide6.QtCore import QFile
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife import resources_rc  # noqa: F401
from harrix_swiss_knife.apps.habits.checkin_sounds import (
    habit_checkin_sound_name,
    play_habit_checkin_sound,
    preload_habit_checkin_sounds,
)


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


def test_play_habit_checkin_sound_returns_immediately(qapp: QApplication) -> None:
    """Playback is scheduled asynchronously and must not block the caller."""
    play_habit_checkin_sound(1)
    play_habit_checkin_sound(0)
    play_habit_checkin_sound(None)
    qapp.processEvents()


def test_preload_habit_checkin_sounds_is_idempotent(qapp: QApplication) -> None:  # noqa: ARG001
    """Preload must be safe to call more than once before the first click."""
    preload_habit_checkin_sounds()
    preload_habit_checkin_sounds()
