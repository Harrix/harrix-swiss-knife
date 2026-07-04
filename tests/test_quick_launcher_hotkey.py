"""Tests for quick launcher hotkey persistence in config-temp.json."""

from __future__ import annotations

import json
from pathlib import Path

import harrix_pylib as h
import pytest

from harrix_swiss_knife.actions.quick_launcher.hotkey import (
    QUICK_LAUNCHER_HOTKEY_KEY,
    load_quick_launcher_hotkey,
    save_quick_launcher_hotkey,
)
from harrix_swiss_knife.paths import get_temp_config_path


@pytest.fixture
def isolated_temp_config(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Point harrix_pylib project root at a temp directory with a minimal main config."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    main_config = config_dir / "config.json"
    main_config.write_text(
        json.dumps({"beginning_of_article": "snippet:config/beginning-of-article.md"}),
        encoding="utf-8",
    )
    config_dir.joinpath("beginning-of-article.md").write_text("SHOULD_NOT_INLINE", encoding="utf-8")
    monkeypatch.setattr(h.dev, "get_project_root", lambda: tmp_path)


@pytest.mark.usefixtures("isolated_temp_config")
def test_save_quick_launcher_hotkey_does_not_modify_main_config() -> None:
    save_quick_launcher_hotkey("Ctrl+Alt+Space")

    main_text = (h.dev.get_project_root() / "config" / "config.json").read_text(encoding="utf-8")
    assert "snippet:config/beginning-of-article.md" in main_text
    assert "SHOULD_NOT_INLINE" not in main_text

    temp_config = json.loads(get_temp_config_path().read_text(encoding="utf-8"))
    assert temp_config[QUICK_LAUNCHER_HOTKEY_KEY] == "Ctrl+Alt+Space"


@pytest.mark.usefixtures("isolated_temp_config")
def test_load_quick_launcher_hotkey_reads_temp_config() -> None:
    save_quick_launcher_hotkey("Ctrl+Shift+Q")
    assert load_quick_launcher_hotkey() == "Ctrl+Shift+Q"


@pytest.mark.usefixtures("isolated_temp_config")
def test_load_quick_launcher_hotkey_returns_empty_when_missing() -> None:
    assert load_quick_launcher_hotkey() == ""
