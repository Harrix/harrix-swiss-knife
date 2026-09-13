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
    preload = MagicMock()
    monkeypatch.setattr(shutter_sound, "preload_screenshot_shutter_sound", preload)
    shutter_sound.play_screenshot_shutter_sound()
    preload.assert_not_called()


def test_prime_effect_stays_silent(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(shutter_sound, "qt_sounds_muted", lambda: False)
    effect = MagicMock()
    was_primed = shutter_sound._state["primed"]
    try:
        shutter_sound._state["primed"] = False
        shutter_sound._prime_effect(effect)
        effect.play.assert_called_once()
        volumes = [call.args[0] for call in effect.setVolume.call_args_list]
        assert volumes
        assert volumes[-1] == 0.0
        assert shutter_sound._state["primed"] is True
    finally:
        shutter_sound._state["primed"] = was_primed
