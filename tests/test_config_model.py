"""Tests for typed config validation helpers."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import harrix_pylib as h
import pytest

from harrix_swiss_knife.config_model import (
    SHOW_MAIN_WINDOW_ON_STARTUP_KEY,
    UI_FONT_SCALE_DEFAULT,
    UI_FONT_SCALE_KEY,
    clamp_ui_font_scale,
    get_show_main_window_on_startup,
    get_ui_font_scale,
    load_app_config,
    restart_required_config_keys,
    set_show_main_window_on_startup,
    validate_app_config,
)
from harrix_swiss_knife.paths import ensure_local_config

if TYPE_CHECKING:
    from pathlib import Path


def test_validate_app_config_accepts_hotkeys() -> None:
    warnings = validate_app_config(
        {
            "hotkeys": [{"action": "OnQuickLauncher", "hotkeys": ["Ctrl+Shift+F1"]}],
            "editor-notes": "code",
            "path_github": "D:/GitHub",
            "path_notes": "D:/Notes",
            "vscode_workspace_notes": "D:/Notes.code-workspace",
        },
    )
    assert warnings == []


def test_validate_app_config_rejects_bad_hotkeys() -> None:
    with pytest.raises(TypeError, match="hotkeys"):
        validate_app_config({"hotkeys": "nope"})


def test_validate_app_config_warns_on_placeholders() -> None:
    warnings = validate_app_config(
        {
            "editor-notes": "<YOUR_EDITOR>",
            "path_github": "<YOUR_GITHUB_FOLDER>",
            "path_notes": "<YOUR_NOTES_FOLDER>",
            "vscode_workspace_notes": "<YOUR_NOTES_CODE_WORKSPACE>",
        },
    )
    assert any("placeholder" in item for item in warnings)


def test_load_app_config_and_ensure_local(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    example = config_dir / "config.example.json"
    example.write_text(json.dumps({"editor-notes": "code", "hotkeys": []}), encoding="utf-8")
    monkeypatch.setattr(h.dev, "get_project_root", lambda: tmp_path)

    path = ensure_local_config()
    assert path.is_file()
    assert path.name == "config.json"
    loaded = load_app_config(str(path))
    assert loaded["editor-notes"] == "code"


def test_restart_required_config_keys_detects_font_scale_and_hotkeys() -> None:
    before = {UI_FONT_SCALE_KEY: 1.0, "hotkeys": [], "editor": "cursor"}
    assert restart_required_config_keys(before, before) == []
    assert restart_required_config_keys(before, {**before, "editor": "code"}) == []
    assert restart_required_config_keys(before, {**before, UI_FONT_SCALE_KEY: 1.2}) == [UI_FONT_SCALE_KEY]
    after_hotkeys = {
        **before,
        "hotkeys": [{"action": "OnQuickLauncher", "hotkeys": ["Ctrl+F1"]}],
    }
    assert restart_required_config_keys(before, after_hotkeys) == ["hotkeys"]


def test_ui_font_scale_defaults_and_clamps() -> None:
    assert get_ui_font_scale({}) == UI_FONT_SCALE_DEFAULT
    assert get_ui_font_scale({UI_FONT_SCALE_KEY: 0.9}) == 0.9
    assert get_ui_font_scale({UI_FONT_SCALE_KEY: "0.85"}) == 0.85
    assert get_ui_font_scale({UI_FONT_SCALE_KEY: "nope"}) == UI_FONT_SCALE_DEFAULT
    assert get_ui_font_scale({UI_FONT_SCALE_KEY: 0.1}) == UI_FONT_SCALE_DEFAULT
    assert clamp_ui_font_scale(0.5) == 0.7
    assert clamp_ui_font_scale(2.0) == 1.5


def test_show_main_window_on_startup_defaults_and_writes(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    path.write_text(json.dumps({"editor-notes": "code"}), encoding="utf-8")
    assert get_show_main_window_on_startup({}) is True
    assert get_show_main_window_on_startup({SHOW_MAIN_WINDOW_ON_STARTUP_KEY: False}) is False
    set_show_main_window_on_startup(enabled=False, config_path=str(path))
    written = json.loads(path.read_text(encoding="utf-8"))
    assert written[SHOW_MAIN_WINDOW_ON_STARTUP_KEY] is False
    set_show_main_window_on_startup(enabled=True, config_path=str(path))
    written = json.loads(path.read_text(encoding="utf-8"))
    assert written[SHOW_MAIN_WINDOW_ON_STARTUP_KEY] is True
    assert written["editor-notes"] == "code"
