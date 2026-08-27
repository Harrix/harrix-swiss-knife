"""Tests for persisted workout gender in config.json."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

import pytest

from harrix_swiss_knife.apps.common.apps_config import (
    FITNESS_WORKOUT_GENDER_KEY,
    get_apps_fitness_workout_gender,
    set_apps_fitness_workout_gender,
)

if TYPE_CHECKING:
    from pathlib import Path


def test_get_apps_fitness_workout_gender_missing_or_invalid() -> None:
    """Missing or invalid values mean the user has not chosen yet."""
    assert get_apps_fitness_workout_gender({}) is None
    assert get_apps_fitness_workout_gender({"apps": {}}) is None
    assert get_apps_fitness_workout_gender({"apps": {FITNESS_WORKOUT_GENDER_KEY: "other"}}) is None


def test_set_apps_fitness_workout_gender_writes_and_syncs_live_config(tmp_path: Path) -> None:
    """Gender is stored under `apps` and the in-memory config stays in sync."""
    path = tmp_path / "config.json"
    path.write_text(json.dumps({"editor-notes": "code", "apps": {"initial_count": 10}}), encoding="utf-8")
    live: dict[str, Any] = {"apps": {"initial_count": 10}}
    set_apps_fitness_workout_gender("female", config=live, config_path=str(path))
    written = json.loads(path.read_text(encoding="utf-8"))
    assert written["apps"][FITNESS_WORKOUT_GENDER_KEY] == "female"
    assert written["apps"]["initial_count"] == 10
    assert live["apps"][FITNESS_WORKOUT_GENDER_KEY] == "female"
    assert get_apps_fitness_workout_gender(live) == "female"


def test_set_apps_fitness_workout_gender_rejects_unknown_value(tmp_path: Path) -> None:
    """Only male/female are accepted."""
    with pytest.raises(ValueError, match="male"):
        set_apps_fitness_workout_gender("unknown", config_path=str(tmp_path / "config.json"))
