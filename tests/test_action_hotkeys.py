"""Tests for global action hotkeys in config.json."""

from __future__ import annotations

import json
from pathlib import Path

import harrix_pylib as h
import pytest

from harrix_swiss_knife.action_hotkeys import (
    ActionHotkeyBinding,
    load_action_hotkeys,
    load_hotkeys_for_action,
)


@pytest.fixture
def isolated_main_config(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    """Point harrix_pylib project root at a temp directory with a main config."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    main_config = config_dir / "config.json"
    main_config.write_text(
        json.dumps(
            {
                "hotkeys": [
                    {"action": "OnQuickLauncher", "hotkeys": ["Ctrl+Shift+F1"]},
                    {"action": "OnScreenshotRegion", "hotkey": "Ctrl+Shift+F2"},
                ],
            },
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(h.dev, "get_project_root", lambda: tmp_path)
    return main_config


@pytest.mark.usefixtures("isolated_main_config")
def test_load_action_hotkeys_reads_main_config() -> None:
    assert load_action_hotkeys() == [
        ActionHotkeyBinding(action="OnQuickLauncher", hotkey="Ctrl+Shift+F1"),
        ActionHotkeyBinding(action="OnScreenshotRegion", hotkey="Ctrl+Shift+F2"),
    ]


@pytest.mark.usefixtures("isolated_main_config")
def test_load_hotkeys_for_action() -> None:
    assert load_hotkeys_for_action("OnQuickLauncher") == ["Ctrl+Shift+F1"]
    assert load_hotkeys_for_action("OnScreenshotRegion") == ["Ctrl+Shift+F2"]
    assert load_hotkeys_for_action("Missing") == []


def test_load_action_hotkeys_from_dict_supports_multiple_keys() -> None:
    config = {
        "hotkeys": [
            {"action": "OnQuickLauncher", "hotkeys": ["Ctrl+Shift+F1", "Ctrl+Alt+Q"]},
        ],
    }
    assert load_action_hotkeys(config) == [
        ActionHotkeyBinding(action="OnQuickLauncher", hotkey="Ctrl+Shift+F1"),
        ActionHotkeyBinding(action="OnQuickLauncher", hotkey="Ctrl+Alt+Q"),
    ]


def test_load_action_hotkeys_returns_empty_when_missing() -> None:
    assert load_action_hotkeys({}) == []


def test_load_action_hotkeys_renames_removed_keep_windows_actions() -> None:
    config = {
        "hotkeys": [
            {"action": "OnScreenshotRegionKeepWindows", "hotkeys": ["Ctrl+Shift+4"]},
            {"action": "OnScreenshotRegionClipboardKeepWindows", "hotkey": "Ctrl+Alt+4"},
        ],
    }
    assert load_action_hotkeys(config) == [
        ActionHotkeyBinding(action="OnScreenshotRegionClipboard", hotkey="Ctrl+Shift+4"),
        ActionHotkeyBinding(action="OnScreenshotRegionClipboard", hotkey="Ctrl+Alt+4"),
    ]
