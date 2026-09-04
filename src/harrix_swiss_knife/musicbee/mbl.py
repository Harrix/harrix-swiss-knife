"""Read and write MusicBee library (`.mbl`) files."""

from __future__ import annotations

import struct
from dataclasses import dataclass, field
from pathlib import Path

from harrix_swiss_knife.musicbee.paths import decode_musicbee_text
from harrix_swiss_knife.musicbee.varint import encode_varint, read_varint

_UINT32_SIZE = 4
_PRE_PATH_SIZE = 15
_META_SIZE = 32
_ARTWORK_END = 0xFE
_CUE_TAG = 255
_CUE_SIZE_BYTES = 2
_CUE_ENTRY_SIZE = 13


@dataclass
class MblLibrary:
    """Parsed MusicBee library."""

    path: Path
    header: bytes
    tracks: list[MblTrack] = field(default_factory=list)
    trailing_data: bytes = b""


@dataclass
class MblTrack:
    """One library record: opaque blobs around a file path."""

    pre_path_data: bytes
    path: str
    post_path_data: bytes

    @property
    def file_size(self) -> int | None:
        """File size in bytes from the 32-byte metadata after the path, if present."""
        if len(self.post_path_data) < _UINT32_SIZE:
            return None
        return struct.unpack_from("<I", self.post_path_data, 0)[0]


def build_minimal_mbl(tracks: list[tuple[str, int]]) -> bytes:
    """Build a tiny valid `.mbl` used by tests: `(path, file_size)` rows."""
    library = MblLibrary(path=Path("MusicBeeLibrary.mbl"), header=struct.pack("<I", 0))
    for path, size in tracks:
        post = struct.pack("<I", size) + b"\x00" * (_META_SIZE - _UINT32_SIZE) + b"\xfe\x00\x00"
        library.tracks.append(MblTrack(pre_path_data=b"\x00" * _PRE_PATH_SIZE, path=path, post_path_data=post))
    return write_mbl(library)


def parse_mbl(path: Path, content: bytes | None = None) -> MblLibrary:
    """Parse `MusicBeeLibrary.mbl` into track records."""
    raw = path.read_bytes() if content is None else content
    if len(raw) < _UINT32_SIZE:
        msg = f"MusicBee library is too small: {path}"
        raise ValueError(msg)
    header = raw[:_UINT32_SIZE]
    count = struct.unpack_from("<I", header, 0)[0] >> 8
    position = _UINT32_SIZE
    tracks: list[MblTrack] = []
    for _ in range(count):
        if position + _PRE_PATH_SIZE > len(raw):
            msg = "Unexpected end of MusicBee library while reading a track"
            raise ValueError(msg)
        pre = raw[position : position + _PRE_PATH_SIZE]
        position += _PRE_PATH_SIZE
        path_text, position = _read_pascal(raw, position)
        post_start = position
        position = _skip_to_next_track(raw, position)
        tracks.append(MblTrack(pre_path_data=pre, path=path_text, post_path_data=raw[post_start:position]))
    return MblLibrary(path=path, header=header, tracks=tracks, trailing_data=raw[position:])


def write_mbl(library: MblLibrary) -> bytes:
    """Serialize `library` including updated paths."""
    flag = library.header[0] if library.header else 0
    body = bytearray(struct.pack("<I", (len(library.tracks) << 8) | flag))
    for track in library.tracks:
        body += track.pre_path_data
        encoded = track.path.encode("utf-8")
        body += encode_varint(len(encoded))
        body += encoded
        body += track.post_path_data
    body += library.trailing_data
    return bytes(body)


def write_mbl_file(library: MblLibrary) -> None:
    """Write `library` back to disk."""
    library.path.write_bytes(write_mbl(library))


def _read_pascal(data: bytes, offset: int) -> tuple[str, int]:
    length, position = read_varint(data, offset)
    if length is None:
        msg = "Invalid MusicBee library path length"
        raise ValueError(msg)
    raw = data[position : position + length]
    if len(raw) < length:
        msg = "Unexpected end of MusicBee library path"
        raise ValueError(msg)
    return decode_musicbee_text(raw), position + length


def _skip_to_next_track(data: bytes, offset: int) -> int:
    position = offset + _META_SIZE
    if position > len(data):
        msg = "Unexpected end of MusicBee library metadata"
        raise ValueError(msg)
    art = data[position : position + 1]
    position += 1
    while art and art[0] < _ARTWORK_END:
        _text, position = _read_pascal(data, position)
        position += 1
        _text, position = _read_pascal(data, position)
        art = data[position : position + 1]
        position += 1
    position += 1
    if position > len(data):
        msg = "Unexpected end of MusicBee library artwork block"
        raise ValueError(msg)
    tag = data[position : position + 1]
    position += 1
    while tag and tag[0] != 0:
        if tag[0] == _CUE_TAG:
            cue = data[position : position + _CUE_SIZE_BYTES]
            position += _CUE_SIZE_BYTES
            if len(cue) < _CUE_SIZE_BYTES:
                break
            position += struct.unpack("<H", cue)[0] * _CUE_ENTRY_SIZE
            break
        _text, position = _read_pascal(data, position)
        tag = data[position : position + 1]
        position += 1
    return position
