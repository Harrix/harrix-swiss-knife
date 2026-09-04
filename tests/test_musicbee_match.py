"""Tests for MusicBee missing-path remapping."""

from __future__ import annotations

from pathlib import Path

from harrix_swiss_knife.musicbee.index import index_audio_files
from harrix_swiss_knife.musicbee.match import match_missing_path
from harrix_swiss_knife.musicbee.paths import path_is_under


def test_path_is_under_missing_files() -> None:
    folder = r"C:\Users\sergi\OneDrive\Music\Stream"
    assert path_is_under(rf"{folder}\a.mp3", folder)
    assert not path_is_under(r"C:\Users\sergi\OneDrive\Music\Other\a.mp3", folder)


def test_match_unique_basename(tmp_path: Path) -> None:
    root = tmp_path / "Music"
    dest = root / "Album"
    dest.mkdir(parents=True)
    file = dest / "song.mp3"
    file.write_bytes(b"abc")
    index = index_audio_files(root, frozenset({".mp3"}))
    missing = str(tmp_path / "Music" / "Old" / "song.mp3")
    result = match_missing_path(missing, index)
    assert result.status == "remap"
    assert result.resolved == str(file)


def test_match_size_disambiguates(tmp_path: Path) -> None:
    root = tmp_path / "Music"
    first = root / "A"
    second = root / "B"
    first.mkdir(parents=True)
    second.mkdir(parents=True)
    (first / "song.mp3").write_bytes(b"aa")
    (second / "song.mp3").write_bytes(b"bbbb")
    index = index_audio_files(root, frozenset({".mp3"}))
    missing = str(tmp_path / "old" / "song.mp3")
    result = match_missing_path(missing, index, file_size=4)
    assert result.status == "remap"
    assert result.resolved is not None
    assert result.resolved.endswith(str(Path("B") / "song.mp3"))


def test_match_ambiguous_without_size(tmp_path: Path) -> None:
    root = tmp_path / "Music"
    first = root / "A"
    second = root / "B"
    first.mkdir(parents=True)
    second.mkdir(parents=True)
    (first / "song.mp3").write_bytes(b"aa")
    (second / "song.mp3").write_bytes(b"bb")
    index = index_audio_files(root, frozenset({".mp3"}))
    result = match_missing_path(str(tmp_path / "old" / "song.mp3"), index)
    assert result.status == "ambiguous"
    assert len(result.candidates) == 2
