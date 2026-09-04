"""Tests for MusicBee `.mbp` parse and write."""

from __future__ import annotations

from pathlib import Path

from harrix_swiss_knife.musicbee.mbp import build_mbp, parse_mbp, tracks_to_m3u8, write_mbp
from harrix_swiss_knife.musicbee.varint import encode_varint, read_varint


def test_varint_roundtrip() -> None:
    for value in (0, 1, 127, 128, 300, 16_384):
        encoded = encode_varint(value)
        decoded, offset = read_varint(encoded, 0)
        assert decoded == value
        assert offset == len(encoded)


def test_mbp_roundtrip(tmp_path: Path) -> None:
    tracks = [
        r"C:\Users\sergi\OneDrive\Music\Stream\a.mp3",
        r"C:\Users\sergi\OneDrive\Music\Stream\b.mp3",
    ]
    raw = build_mbp(tracks)
    path = tmp_path / "Stream - Ambient.mbp"
    path.write_bytes(raw)
    parsed = parse_mbp(path)
    assert parsed.path.stem == "Stream - Ambient"
    assert parsed.tracks == tracks
    rewritten = write_mbp(parsed, [*tracks, r"C:\Users\sergi\OneDrive\Music\Stream\c.mp3"])
    path.write_bytes(rewritten)
    again = parse_mbp(path)
    assert len(again.tracks) == 3
    assert again.tracks[-1].endswith("c.mp3")


def test_mbp_empty_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "Stream - Empty.mbp"
    path.write_bytes(build_mbp([]))
    parsed = parse_mbp(path)
    assert parsed.tracks == []
    path.write_bytes(write_mbp(parsed, []))
    assert parse_mbp(path).tracks == []


def test_tracks_to_m3u8() -> None:
    text = tracks_to_m3u8([r"C:\music\a.mp3"])
    assert text.startswith("#EXTM3U")
    assert r"C:\music\a.mp3" in text
