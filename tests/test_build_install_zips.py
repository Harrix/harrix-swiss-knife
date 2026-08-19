"""Tests for the Build install zips action helpers."""

from pathlib import Path

from harrix_swiss_knife.actions.development.build_install_zips import (
    BUILD_ALL_BAT_NAME,
    BUILD_ALL_OPEN_FLAG,
    build_all_cmd,
    install_folder,
)
from harrix_swiss_knife.paths import get_project_root


def test_build_all_cmd_calls_bat_with_open_flag() -> None:
    assert build_all_cmd() == ["cmd.exe", "/c", "call", BUILD_ALL_BAT_NAME, BUILD_ALL_OPEN_FLAG]


def test_install_folder_is_project_install_dir() -> None:
    root = Path("D:/example/harrix-swiss-knife")
    assert install_folder(root) == root / "install"


def test_build_all_bat_supports_open_and_nopause() -> None:
    bat = get_project_root() / "install" / BUILD_ALL_BAT_NAME
    text = bat.read_text(encoding="utf-8")
    assert 'if /i "%~1"=="/open"' in text
    assert 'if /i "%~1"=="/nopause"' in text
    assert 'set "OPEN_INSTALL=1"' in text
    assert 'explorer "%CD%"' in text
    assert "pause > nul" in text
