"""Tests for declarative MusicBee Stream playlist rules."""

from __future__ import annotations

from pathlib import Path

from harrix_swiss_knife.musicbee.index import index_audio_files
from harrix_swiss_knife.musicbee.rules import apply_rules, expand_rule_placeholders
from harrix_swiss_knife.musicbee.settings import DEFAULT_MUSICBEE_RULES


def test_expand_rule_placeholders() -> None:
    rule = expand_rule_placeholders(
        {"type": "restrict_folder", "folder": "{stream_root}"},
        {"stream_root": r"C:\Music\Stream", "music_root": r"C:\Music"},
    )
    assert rule["folder"] == r"C:\Music\Stream"


def test_restrict_ensure_union_remainder(tmp_path: Path) -> None:
    stream = tmp_path / "Stream"
    other = tmp_path / "Other"
    stream.mkdir()
    other.mkdir()
    keep = stream / "keep.mp3"
    extra = stream / "extra.mp3"
    orphan = stream / "orphan.mp3"
    outsider = other / "out.mp3"
    keep.write_bytes(b"k")
    extra.write_bytes(b"e")
    orphan.write_bytes(b"o")
    outsider.write_bytes(b"x")
    index = index_audio_files(tmp_path, frozenset({".mp3"}))
    playlists = {
        "Stream - Epic": [str(keep)],
        "Stream - Epic (real)": [str(keep), str(extra)],
        "Stream - OST": [],
        "Stream - OST (real)": [],
        "Stream - Heavy": [],
        "Stream - Power metal": [],
        "Stream - Mad": [str(keep)],
        "Stream - Mad (electro)": [str(extra)],
        "Stream - Mad (both)": [],
        "Stream - Temp": [str(outsider)],
        "Stream - Ambient": [str(outsider), str(keep)],
    }
    warnings = apply_rules(
        playlists,
        DEFAULT_MUSICBEE_RULES,
        placeholders={"stream_root": str(stream), "music_root": str(tmp_path)},
        file_index=index,
    )
    assert warnings == []
    assert playlists["Stream - Ambient"] == [str(keep)]
    assert str(extra) in playlists["Stream - Epic"]
    assert str(keep) in playlists["Stream - Mad (both)"]
    assert str(extra) in playlists["Stream - Mad (both)"]
    assert playlists["Stream - Temp"] == [str(orphan)]
