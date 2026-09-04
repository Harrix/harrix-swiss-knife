"""Tests for MusicBee `.mbl` parse and write."""

from __future__ import annotations

import struct
from pathlib import Path

from harrix_swiss_knife.musicbee.mbl import MblLibrary, MblTrack, build_minimal_mbl, parse_mbl, write_mbl


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


def test_mbl_parses_cue_block_then_next_track(tmp_path: Path) -> None:
    first = r"C:\music\album\track.mp3"
    second = r"C:\music\album\next.mp3"
    cue_count = 13
    post = (
        struct.pack("<I", 100)
        + b"\x00" * 28
        + b"\xfe\x00\xff"
        + struct.pack("<H", cue_count)
        + b"\x00" * (cue_count * 13)
    )
    library = MblLibrary(
        path=tmp_path / "MusicBeeLibrary.mbl",
        header=struct.pack("<I", 0),
        tracks=[
            MblTrack(pre_path_data=b"\x00" * 15, path=first, post_path_data=post),
            MblTrack(
                pre_path_data=b"\x00" * 15,
                path=second,
                post_path_data=struct.pack("<I", 50) + b"\x00" * 28 + b"\xfe\x00\x00",
            ),
        ],
    )
    path = tmp_path / "MusicBeeLibrary.mbl"
    path.write_bytes(write_mbl(library))
    parsed = parse_mbl(path)
    assert [track.path for track in parsed.tracks] == [first, second]
