"""Tests for muting Qt UI sounds during pytest."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harrix_swiss_knife.apps.fitness.lightbox_sounds import play_fitness_timer_cue
from harrix_swiss_knife.qt_sounds import qt_sounds_muted

if TYPE_CHECKING:
    import pytest


def test_qt_sounds_muted_during_pytest() -> None:
    assert qt_sounds_muted()


def test_qt_sounds_muted_off_when_env_cleared(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("HSK_MUTE_SOUNDS", raising=False)
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "")
    assert not qt_sounds_muted()


def test_play_fitness_timer_cue_is_silent_when_muted() -> None:
    play_fitness_timer_cue("ready")
    play_fitness_timer_cue("go")
