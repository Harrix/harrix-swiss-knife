"""Tests for MusicBee `.mbl` parse and write."""

from __future__ import annotations

from pathlib import Path

from harrix_swiss_knife.musicbee.mbl import build_minimal_mbl, parse_mbl, write_mbl


def test_mbl_roundtrip_keeps_path_and_size(tmp_path: Path) -> None:
    original = r"C:\Users\sergi\OneDrive\Music\old\track.mp3"
    moved = r"C:\Users\sergi\OneDrive\Music\new\track.mp3"
    raw = build_minimal_mbl([(original, 1234)])
    path = tmp_path / "MusicBeeLibrary.mbl"
    path.write_bytes(raw)
    library = parse_mbl(path)
    assert len(library.tracks) == 1
    assert library.tracks[0].path == original
    assert library.tracks[0].file_size == 1234
    library.tracks[0].path = moved
    path.write_bytes(write_mbl(library))
    again = parse_mbl(path)
    assert again.tracks[0].path == moved
    assert again.tracks[0].file_size == 1234
