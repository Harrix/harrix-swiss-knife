"""Tests for MusicBee check plan: remap, rules, apply, backup."""

from __future__ import annotations

from pathlib import Path

import pytest

from harrix_swiss_knife.actions.common.quick_launcher_registry import iter_menu_structure
from harrix_swiss_knife.actions.files.check_musicbee_playlists import OnCheckMusicBeePlaylists
from harrix_swiss_knife.menu_structure import get_menu_structure
from harrix_swiss_knife.musicbee.mbl import build_minimal_mbl, parse_mbl
from harrix_swiss_knife.musicbee.mbp import build_mbp, parse_mbp
from harrix_swiss_knife.musicbee.process import CheckPlan, apply_plan, format_check_report, run_check
from harrix_swiss_knife.musicbee.settings import MusicBeeSettings, default_musicbee_config, load_musicbee_settings


def _settings(root: Path) -> MusicBeeSettings:
    music = root / "Music"
    stream = music / "Stream"
    library = root / "Library"
    playlists = library / "Playlists"
    playlists.mkdir(parents=True)
    stream.mkdir(parents=True)
    return MusicBeeSettings(
        library_dir=library,
        music_root=music,
        stream_root=stream,
        backup_dir=root / "Backups",
        audio_extensions=frozenset({".mp3"}),
        stream_playlist_prefix="Stream - ",
        rules=list(default_musicbee_config()["rules"]),
    )


def test_load_musicbee_settings_and_temp_backup_override(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text("{}", encoding="utf-8")
    (tmp_path / "config-temp.json").write_text(
        '{"musicbee": {"backup_dir": "D:/TempBackups"}}',
        encoding="utf-8",
    )
    settings = load_musicbee_settings(
        {
            "musicbee": {
                "library_dir": "D:/lib",
                "music_root": "D:/music",
                "stream_root": "D:/music/Stream",
                "backup_dir": "D:/Dropbox/Backups",
            },
        },
        config_path=str(config_path),
    )
    assert settings.backup_dir == Path("D:/TempBackups")


def test_run_check_remaps_and_apply(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("harrix_swiss_knife.musicbee.process.is_musicbee_running", lambda: False)
    settings = _settings(tmp_path)
    old = settings.music_root / "Old" / "song.mp3"
    new = settings.stream_root / "song.mp3"
    orphan = settings.stream_root / "orphan.mp3"
    new.write_bytes(b"data")
    orphan.write_bytes(b"only")
    before = new.read_bytes()
    (settings.library_dir / "MusicBeeLibrary.mbl").write_bytes(build_minimal_mbl([(str(old), 4)]))
    playlist_path = settings.playlists_dir / "Stream - Ambient.mbp"
    playlist_path.write_bytes(build_mbp([str(old), str(settings.music_root / "outside.mp3")]))
    for name in (
        "Stream - Epic",
        "Stream - Epic (real)",
        "Stream - OST",
        "Stream - OST (real)",
        "Stream - Heavy",
        "Stream - Power metal",
        "Stream - Mad",
        "Stream - Mad (electro)",
        "Stream - Mad (both)",
        "Stream - Temp",
    ):
        (settings.playlists_dir / f"{name}.mbp").write_bytes(build_mbp([]))

    plan = run_check(settings)
    assert plan.backup_path.is_dir()
    assert (plan.backup_path / "exported" / "Stream - Ambient.m3u8").is_file()
    assert any(item.status == "remap" for item in plan.remaps)
    ambient = next(item for item in plan.playlists if item.name == "Stream - Ambient")
    temp = next(item for item in plan.playlists if item.name == "Stream - Temp")
    assert str(new) in ambient.new_tracks
    assert not any(Path(path).name == "outside.mp3" for path in ambient.new_tracks)
    assert temp.new_tracks == [str(orphan)]
    report = format_check_report(plan)
    assert "Remapped paths" in report
    written = apply_plan(plan)
    assert settings.library_file in written
    library = parse_mbl(settings.library_file)
    assert library.tracks[0].path == str(new)
    assert parse_mbp(playlist_path).tracks == [str(new)]
    assert parse_mbp(settings.playlists_dir / "Stream - Temp.mbp").tracks == [str(orphan)]
    assert new.read_bytes() == before


def test_apply_plan_refuses_when_musicbee_running(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("harrix_swiss_knife.musicbee.process.is_musicbee_running", lambda: True)
    settings = _settings(tmp_path)
    plan = CheckPlan(settings=settings, backup_path=tmp_path, library_changed=True)
    with pytest.raises(OSError, match="Close MusicBee"):
        apply_plan(plan)


def test_action_is_in_file_operations_menu() -> None:
    assert OnCheckMusicBeePlaylists.title == "Check MusicBee playlists"
    assert OnCheckMusicBeePlaylists in list(iter_menu_structure(get_menu_structure()))
