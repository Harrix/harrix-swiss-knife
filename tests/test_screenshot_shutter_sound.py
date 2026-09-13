"""Tests for screenshot shutter sound helpers."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from PySide6.QtCore import QFile
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife import resources_rc  # noqa: F401
from harrix_swiss_knife.screenshot import shutter_sound
from harrix_swiss_knife.screenshot.shutter_sound import (
    SCREENSHOT_SHUTTER_SOUND_KEY,
    load_screenshot_shutter_sound_enabled,
    screenshot_shutter_sound_name,
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


def test_screenshot_shutter_sound_name() -> None:
    assert screenshot_shutter_sound_name() == "screenshot_shutter.wav"


def test_screenshot_shutter_sound_is_embedded(qapp: QApplication) -> None:  # noqa: ARG001
    assert QFile.exists(":/assets/sounds/screenshot_shutter.wav")


def test_load_screenshot_shutter_sound_enabled_defaults_true(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "harrix_swiss_knife.screenshot.shutter_sound.h.dev.config_load",
        lambda _path: {},
    )
    assert load_screenshot_shutter_sound_enabled() is True


def test_load_screenshot_shutter_sound_enabled_reads_false(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "harrix_swiss_knife.screenshot.shutter_sound.h.dev.config_load",
        lambda _path: {SCREENSHOT_SHUTTER_SOUND_KEY: False},
    )
    assert load_screenshot_shutter_sound_enabled() is False


def test_play_respects_disabled_setting(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(shutter_sound, "qt_sounds_muted", lambda: False)
    monkeypatch.setattr(shutter_sound, "load_screenshot_shutter_sound_enabled", lambda: False)
    ensure = MagicMock()
    monkeypatch.setattr(shutter_sound, "_ensure_primed", ensure)
    shutter_sound.play_screenshot_shutter_sound()
    ensure.assert_not_called()


def test_play_creates_audible_effect(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(shutter_sound, "qt_sounds_muted", lambda: False)
    monkeypatch.setattr(shutter_sound, "load_screenshot_shutter_sound_enabled", lambda: True)
    monkeypatch.setattr(shutter_sound, "_ensure_primed", lambda _url: None)
    monkeypatch.setattr(
        shutter_sound,
        "_sound_url",
        lambda _name: MagicMock(isValid=lambda: True),
    )
    effect = MagicMock()
    effect.isPlaying.return_value = False
    monkeypatch.setattr(shutter_sound, "QSoundEffect", lambda: effect)
    shutter_sound._live_effects.clear()
    shutter_sound.play_screenshot_shutter_sound()
    effect.setVolume.assert_called_with(1.0)
    effect.play.assert_called_once()
