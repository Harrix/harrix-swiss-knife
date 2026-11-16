"""Tests for the shared `path_backups` resolver."""

from __future__ import annotations

from pathlib import Path

from harrix_swiss_knife.backup_paths import (
    cursor_backup_root,
    resolve_backup_dir,
)
from harrix_swiss_knife.musicbee.settings import load_musicbee_settings


def test_resolve_backup_dir_prefers_path_backups(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        '{"path_backups": "D:/Dropbox/Backups", "musicbee": {"backup_dir": "D:/Other"}}',
        encoding="utf-8",
    )
    assert resolve_backup_dir(config_path=str(config_path)) == Path("D:/Dropbox/Backups")


def test_resolve_backup_dir_falls_back_to_musicbee(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text('{"musicbee": {"backup_dir": "D:/Dropbox/Backups"}}', encoding="utf-8")
    assert resolve_backup_dir(config_path=str(config_path)) == Path("D:/Dropbox/Backups")


def test_resolve_backup_dir_temp_override(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text('{"path_backups": "D:/Dropbox/Backups"}', encoding="utf-8")
    (tmp_path / "config-temp.json").write_text('{"path_backups": "D:/TempBackups"}', encoding="utf-8")
    assert resolve_backup_dir(config_path=str(config_path)) == Path("D:/TempBackups")


def test_cursor_backup_root_creates_subdir(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text("{}", encoding="utf-8")
    root = cursor_backup_root(
        {"path_backups": str(tmp_path / "Backups")},
        config_path=str(config_path),
    )
    assert root == tmp_path / "Backups" / "Cursor"
    assert root.is_dir()


def test_musicbee_uses_shared_path_backups(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        '{"path_backups": "D:/SharedBackups"}',
        encoding="utf-8",
    )
    settings = load_musicbee_settings(
        {
            "musicbee": {
                "library_dir": "D:/lib",
                "music_root": "D:/music",
                "stream_root": "D:/music/Stream",
                "backup_dir": "D:/Legacy",
            },
        },
        config_path=str(config_path),
    )
    assert settings.backup_dir == Path("D:/SharedBackups")
