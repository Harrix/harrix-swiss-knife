"""Tests for main window view mode settings."""

from __future__ import annotations

import json
from pathlib import Path

import harrix_pylib as h
import pytest

from harrix_swiss_knife.main_window_settings import (
    MAIN_WINDOW_ICON_GRID_KEY,
    load_main_window_icon_grid,
    save_main_window_icon_grid,
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
def test_load_main_window_icon_grid_defaults_to_true() -> None:
    assert load_main_window_icon_grid() is True


@pytest.mark.usefixtures("isolated_temp_config")
def test_load_main_window_icon_grid_reads_false() -> None:
    save_main_window_icon_grid(icon_grid=False)
    assert load_main_window_icon_grid() is False


@pytest.mark.usefixtures("isolated_temp_config")
def test_load_main_window_icon_grid_reads_true() -> None:
    save_main_window_icon_grid(icon_grid=True)
    assert load_main_window_icon_grid() is True


def test_main_window_icon_grid_key() -> None:
    assert MAIN_WINDOW_ICON_GRID_KEY == "main_window_icon_grid"


@pytest.mark.usefixtures("isolated_temp_config")
def test_save_main_window_icon_grid_writes_temp_config_only() -> None:
    save_main_window_icon_grid(icon_grid=False)

    main_text = (h.dev.get_project_root() / "config" / "config.json").read_text(encoding="utf-8")
    assert "snippet:config/beginning-of-article.md" in main_text
    assert "SHOULD_NOT_INLINE" not in main_text

    temp_config = json.loads(get_temp_config_path().read_text(encoding="utf-8"))
    assert temp_config[MAIN_WINDOW_ICON_GRID_KEY] is False
