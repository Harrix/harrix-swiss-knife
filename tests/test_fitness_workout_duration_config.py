"""Tests for persisted workout duration in config.json."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

import pytest
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.apps.common.apps_config import (
    FITNESS_WORKOUT_DURATION_MIN_KEY,
    get_apps_fitness_workout_duration_min,
    set_apps_fitness_workout_duration_min,
)
from harrix_swiss_knife.apps.fitness.workout_generate_dialog import WorkoutGenerateDialog

if TYPE_CHECKING:
    from pathlib import Path


def _qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_get_apps_fitness_workout_duration_min_missing_or_invalid() -> None:
    assert get_apps_fitness_workout_duration_min({}) is None
    assert get_apps_fitness_workout_duration_min({"apps": {}}) is None
    assert get_apps_fitness_workout_duration_min({"apps": {FITNESS_WORKOUT_DURATION_MIN_KEY: 5}}) is None
    assert get_apps_fitness_workout_duration_min({"apps": {FITNESS_WORKOUT_DURATION_MIN_KEY: 300}}) is None
    assert get_apps_fitness_workout_duration_min({"apps": {FITNESS_WORKOUT_DURATION_MIN_KEY: "nope"}}) is None


def test_set_apps_fitness_workout_duration_min_writes_and_syncs_live_config(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    path.write_text(json.dumps({"editor-notes": "code", "apps": {"initial_count": 10}}), encoding="utf-8")
    live: dict[str, Any] = {"apps": {"initial_count": 10}}
    set_apps_fitness_workout_duration_min(60, config=live, config_path=str(path))
    written = json.loads(path.read_text(encoding="utf-8"))
    assert written["apps"][FITNESS_WORKOUT_DURATION_MIN_KEY] == 60
    assert written["apps"]["initial_count"] == 10
    assert live["apps"][FITNESS_WORKOUT_DURATION_MIN_KEY] == 60
    assert get_apps_fitness_workout_duration_min(live) == 60


def test_set_apps_fitness_workout_duration_min_rejects_out_of_range(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="between"):
        set_apps_fitness_workout_duration_min(9, config_path=str(tmp_path / "config.json"))


def test_workout_generate_dialog_uses_initial_duration() -> None:
    assert _qapp() is not None
    dialog = WorkoutGenerateDialog(show_gender=False, initial_duration_min=75)
    assert dialog.duration_min() == 75
    dialog.close()
