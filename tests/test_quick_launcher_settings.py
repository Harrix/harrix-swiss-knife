"""Tests for quick launcher settings in config.json."""

from __future__ import annotations

import json
from pathlib import Path

import harrix_pylib as h
import pytest

from harrix_swiss_knife.actions.quick_launcher.settings import (
    QUICK_LAUNCHER_MARKDOWN_IN_PANEL_KEY,
    load_quick_launcher_markdown_in_panel,
)


@pytest.fixture
def isolated_main_config(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
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
    return main_config


@pytest.mark.usefixtures("isolated_main_config")
def test_load_quick_launcher_markdown_in_panel_defaults_to_true() -> None:
    assert load_quick_launcher_markdown_in_panel() is True


@pytest.mark.usefixtures("isolated_main_config")
def test_load_quick_launcher_markdown_in_panel_reads_false(isolated_main_config: Path) -> None:
    config = json.loads(isolated_main_config.read_text(encoding="utf-8"))
    config[QUICK_LAUNCHER_MARKDOWN_IN_PANEL_KEY] = False
    isolated_main_config.write_text(json.dumps(config), encoding="utf-8")
    assert load_quick_launcher_markdown_in_panel() is False


@pytest.mark.usefixtures("isolated_main_config")
def test_load_quick_launcher_markdown_in_panel_reads_true(isolated_main_config: Path) -> None:
    config = json.loads(isolated_main_config.read_text(encoding="utf-8"))
    config[QUICK_LAUNCHER_MARKDOWN_IN_PANEL_KEY] = True
    isolated_main_config.write_text(json.dumps(config), encoding="utf-8")
    assert load_quick_launcher_markdown_in_panel() is True
