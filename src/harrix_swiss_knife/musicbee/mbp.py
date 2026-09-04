"""Read and write MusicBee static playlist (`.mbp`) files."""

from __future__ import annotations

import struct
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from harrix_swiss_knife.musicbee.paths import decode_musicbee_text
from harrix_swiss_knife.musicbee.varint import encode_varint, read_varint

if TYPE_CHECKING:
    from pathlib import Path

SONG_SEPARATOR = b"\xff\xff\xff\xff"
_UINT32_SIZE = 4
_DEFAULT_HEADER_SIZE = 32
_MAX_SONGS = 50_000
_MAX_PATH_LENGTH = 4096
_COUNT_SEARCH_START = 0


@dataclass
class MbpPlaylist:
    """Parsed static MusicBee playlist."""

    path: Path
    header: bytes
    tracks: list[str] = field(default_factory=list)
    trailer: bytes = b""


def build_mbp(tracks: list[str], *, header: bytes | None = None) -> bytes:
    """Build a minimal `.mbp` payload used by tests and rewrites."""
    prefix = header if header is not None else b"\x00" * _DEFAULT_HEADER_SIZE
    return _serialize(prefix, tracks, b"")


def find_song_list_start(content: bytes) -> tuple[int | None, int | None, int]:
    """Return `(count_offset, entries_offset, count)` for a valid song list."""
    offset = _COUNT_SEARCH_START
    limit = max(0, len(content) - _UINT32_SIZE)
    while offset <= limit:
        count = struct.unpack_from("<I", content, offset)[0]
        if 0 < count < _MAX_SONGS:
            entries_offset = offset + _UINT32_SIZE
            if _is_valid_list_at_offset(content, entries_offset, count):
                return offset, entries_offset, count
        offset += 1
    return None, None, 0


def parse_mbp(path: Path, content: bytes | None = None) -> MbpPlaylist:
    """Parse a `.mbp` file into header, tracks, and trailer."""
    raw = path.read_bytes() if content is None else content
    count_offset, entries_offset, count = find_song_list_start(raw)
    if count_offset is None or entries_offset is None:
        empty = _empty_song_list_start(raw)
        if empty is None:
            msg = f"Could not parse MusicBee playlist: {path.name}"
            raise ValueError(msg)
        count_offset, entries_offset, count = empty
    tracks, end = _read_tracks(raw, entries_offset, count)
    return MbpPlaylist(
        path=path,
        header=raw[:count_offset],
        tracks=tracks,
        trailer=raw[end:],
    )


def tracks_to_m3u8(tracks: list[str]) -> str:
    """Return an `#EXTM3U` dump of playlist paths."""
    lines = ["#EXTM3U"]
    lines.extend(tracks)
    return "\n".join(lines) + "\n"


def write_mbp(playlist: MbpPlaylist, tracks: list[str] | None = None) -> bytes:
    """Serialize `playlist` with optional replacement `tracks`."""
    return _serialize(playlist.header, playlist.tracks if tracks is None else tracks, playlist.trailer)


def write_mbp_file(playlist: MbpPlaylist, tracks: list[str] | None = None) -> None:
    """Write `playlist` back to disk."""
    playlist.path.write_bytes(write_mbp(playlist, tracks))


def _empty_song_list_start(content: bytes) -> tuple[int, int, int] | None:
    """Treat a trailing or 32-byte-header `uint32(0)` as an empty track list.

    `find_song_list_start` ignores count 0 so it does not match header zeros.

    """
    if len(content) < _UINT32_SIZE:
        return None
    candidates = [_DEFAULT_HEADER_SIZE, len(content) - _UINT32_SIZE]
    seen: set[int] = set()
    for offset in candidates:
        if offset in seen or offset < 0 or offset + _UINT32_SIZE > len(content):
            continue
        seen.add(offset)
        if struct.unpack_from("<I", content, offset)[0] == 0:
            return offset, offset + _UINT32_SIZE, 0
    return None


def _is_valid_list_at_offset(content: bytes, offset: int, count: int) -> bool:
    if count == 0:
        return True
    position = offset
    for _ in range(count):
        length, position = read_varint(content, position)
        if length is None or not (0 < length < _MAX_PATH_LENGTH):
            return False
        if position + length + _UINT32_SIZE > len(content):
            return False
        position += length
        if content[position : position + _UINT32_SIZE] != SONG_SEPARATOR:
            return False
        position += _UINT32_SIZE
    return True


def _read_tracks(content: bytes, offset: int, count: int) -> tuple[list[str], int]:
    tracks: list[str] = []
    position = offset
    for _ in range(count):
        length, position = read_varint(content, position)
        if length is None:
            msg = "Invalid playlist path length"
            raise ValueError(msg)
        raw = content[position : position + length]
        position += length
        separator = content[position : position + _UINT32_SIZE]
        position += _UINT32_SIZE
        if separator != SONG_SEPARATOR:
            msg = "Invalid playlist entry separator"
            raise ValueError(msg)
        tracks.append(decode_musicbee_text(raw))
    return tracks, position


def _serialize(header: bytes, tracks: list[str], trailer: bytes) -> bytes:
    body = bytearray(header)
    body += struct.pack("<I", len(tracks))
    for track in tracks:
        encoded = track.encode("utf-8")
        body += encode_varint(len(encoded))
        body += encoded
        body += SONG_SEPARATOR
    body += trailer
    return bytes(body)
