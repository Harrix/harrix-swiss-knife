"""Tests for GUI/CLI action usage persistence and recent GUI ranking."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harrix_swiss_knife import action_usage
from harrix_swiss_knife.action_usage import (
    RECENT_GUI_ACTIONS_LIMIT,
    RECENT_GUI_EXCLUDED_CLASS_NAMES,
    list_recent_gui_action_names,
    load_action_usage,
    record_action_usage,
)

if TYPE_CHECKING:
    from pathlib import Path

    import pytest


def test_record_action_usage_gui_sets_last_used_gui(tmp_path: Path) -> None:
    path = tmp_path / "action_usage.json"
    record_action_usage("OnFinance", via_cli=False, path=path)

    entry = load_action_usage(path)["OnFinance"]
    assert entry["count"] == 1
    assert entry["gui"] == 1
    assert entry["cli"] == 0
    assert entry["last_used"]
    assert entry["last_used_gui"] == entry["last_used"]


def test_record_action_usage_cli_does_not_set_last_used_gui(tmp_path: Path) -> None:
    path = tmp_path / "action_usage.json"
    record_action_usage("OnFinance", via_cli=True, path=path)

    entry = load_action_usage(path)["OnFinance"]
    assert entry["count"] == 1
    assert entry["gui"] == 0
    assert entry["cli"] == 1
    assert entry["last_used"]
    assert entry["last_used_gui"] == ""


def test_list_recent_gui_action_names_ignores_cli_and_keeps_newest_six(tmp_path: Path) -> None:
    path = tmp_path / "action_usage.json"
    record_action_usage("OnCliOnly", via_cli=True, path=path)
    for index in range(8):
        record_action_usage(f"OnGui{index}", via_cli=False, path=path)

    names = list_recent_gui_action_names(path=path)
    assert "OnCliOnly" not in names
    assert names == [f"OnGui{index}" for index in range(7, 1, -1)]
    assert len(names) == RECENT_GUI_ACTIONS_LIMIT


def test_list_recent_gui_action_names_uses_gui_stamp_after_later_cli(tmp_path: Path) -> None:
    path = tmp_path / "action_usage.json"
    path.write_text(
        """{
  "OnOlderGui": {
    "count": 2,
    "gui": 1,
    "cli": 1,
    "last_used": "2026-08-16T10:00:00+03:00",
    "last_used_gui": "2026-08-16T08:00:00+03:00"
  },
  "OnNewerGui": {
    "count": 1,
    "gui": 1,
    "cli": 0,
    "last_used": "2026-08-16T09:00:00+03:00",
    "last_used_gui": "2026-08-16T09:00:00+03:00"
  }
}
""",
        encoding="utf8",
    )

    assert list_recent_gui_action_names(path=path) == ["OnNewerGui", "OnOlderGui"]


def test_list_recent_gui_action_names_falls_back_to_gui_only_last_used(tmp_path: Path) -> None:
    path = tmp_path / "action_usage.json"
    path.write_text(
        """{
  "OnLegacyGui": {
    "count": 2,
    "gui": 2,
    "cli": 0,
    "last_used": "2026-08-16T09:00:00+03:00"
  },
  "OnMixed": {
    "count": 3,
    "gui": 1,
    "cli": 2,
    "last_used": "2026-08-16T10:00:00+03:00"
  }
}
""",
        encoding="utf8",
    )

    assert list_recent_gui_action_names(path=path) == ["OnLegacyGui"]


def test_list_recent_gui_action_names_skips_excluded_exit(tmp_path: Path) -> None:
    path = tmp_path / "action_usage.json"
    path.write_text(
        """{
  "OnExit": {
    "count": 4,
    "gui": 4,
    "cli": 0,
    "last_used": "2026-08-16T12:00:00+03:00",
    "last_used_gui": "2026-08-16T12:00:00+03:00"
  },
  "OnFinance": {
    "count": 1,
    "gui": 1,
    "cli": 0,
    "last_used": "2026-08-16T11:00:00+03:00",
    "last_used_gui": "2026-08-16T11:00:00+03:00"
  },
  "OnFood": {
    "count": 1,
    "gui": 1,
    "cli": 0,
    "last_used": "2026-08-16T10:00:00+03:00",
    "last_used_gui": "2026-08-16T10:00:00+03:00"
  }
}
""",
        encoding="utf8",
    )

    assert "OnExit" in RECENT_GUI_EXCLUDED_CLASS_NAMES
    assert list_recent_gui_action_names(path=path, limit=2) == ["OnFinance", "OnFood"]


def test_record_action_usage_retries_replace_on_permission_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = tmp_path / "action_usage.json"
    calls = {"n": 0}
    real_replace = action_usage.Path.replace

    def flaky_replace(self: Path, target: Path) -> Path:
        calls["n"] += 1
        if calls["n"] == 1:
            raise PermissionError(5, "Access is denied")
        return real_replace(self, target)

    monkeypatch.setattr(action_usage, "_REPLACE_RETRY_DELAYS_S", (0.0,))
    monkeypatch.setattr(action_usage.Path, "replace", flaky_replace)

    record_action_usage("OnExit", via_cli=False, path=path)

    assert calls["n"] == 2
    assert load_action_usage(path)["OnExit"]["count"] == 1


def test_record_action_usage_overwrites_when_replace_stays_denied(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = tmp_path / "action_usage.json"

    def deny_replace(_self: Path, _target: Path) -> Path:
        raise PermissionError(5, "Access is denied")

    monkeypatch.setattr(action_usage, "_REPLACE_RETRY_DELAYS_S", ())
    monkeypatch.setattr(action_usage.Path, "replace", deny_replace)

    record_action_usage("OnExit", via_cli=False, path=path)

    assert load_action_usage(path)["OnExit"]["count"] == 1
