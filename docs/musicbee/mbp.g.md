---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `mbp.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `MbpPlaylist`](#%EF%B8%8F-class-mbpplaylist)
- [🔧 Function `build_mbp`](#-function-build_mbp)
- [🔧 Function `find_song_list_start`](#-function-find_song_list_start)
- [🔧 Function `parse_mbp`](#-function-parse_mbp)
- [🔧 Function `tracks_to_m3u8`](#-function-tracks_to_m3u8)
- [🔧 Function `write_mbp`](#-function-write_mbp)
- [🔧 Function `write_mbp_file`](#-function-write_mbp_file)

</details>

## 🏛️ Class `MbpPlaylist`

```python
class MbpPlaylist
```

Parsed static MusicBee playlist.

<details>
<summary>Code:</summary>

```python
class MbpPlaylist:

    path: Path
    header: bytes
    tracks: list[str] = field(default_factory=list)
    trailer: bytes = b""
```

</details>

## 🔧 Function `build_mbp`

```python
def build_mbp(tracks: list[str], *, header: bytes | None = None) -> bytes
```

Build a minimal `.mbp` payload used by tests and rewrites.

<details>
<summary>Code:</summary>

```python
def build_mbp(tracks: list[str], *, header: bytes | None = None) -> bytes:
    prefix = header if header is not None else b"\x00" * _DEFAULT_HEADER_SIZE
    return _serialize(prefix, tracks, b"")
```

</details>

## 🔧 Function `find_song_list_start`

```python
def find_song_list_start(content: bytes) -> tuple[int | None, int | None, int]
```

Return `(count_offset, entries_offset, count)` for a valid song list.

<details>
<summary>Code:</summary>

```python
def find_song_list_start(content: bytes) -> tuple[int | None, int | None, int]:
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
```

</details>

## 🔧 Function `parse_mbp`

```python
def parse_mbp(path: Path, content: bytes | None = None) -> MbpPlaylist
```

Parse a `.mbp` file into header, tracks, and trailer.

<details>
<summary>Code:</summary>

```python
def parse_mbp(path: Path, content: bytes | None = None) -> MbpPlaylist:
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
```

</details>

## 🔧 Function `tracks_to_m3u8`

```python
def tracks_to_m3u8(tracks: list[str]) -> str
```

Return an `#EXTM3U` dump of playlist paths.

<details>
<summary>Code:</summary>

```python
def tracks_to_m3u8(tracks: list[str]) -> str:
    lines = ["#EXTM3U"]
    lines.extend(tracks)
    return "\n".join(lines) + "\n"
```

</details>

## 🔧 Function `write_mbp`

```python
def write_mbp(playlist: MbpPlaylist, tracks: list[str] | None = None) -> bytes
```

Serialize `playlist` with optional replacement `tracks`.

<details>
<summary>Code:</summary>

```python
def write_mbp(playlist: MbpPlaylist, tracks: list[str] | None = None) -> bytes:
    return _serialize(playlist.header, playlist.tracks if tracks is None else tracks, playlist.trailer)
```

</details>

## 🔧 Function `write_mbp_file`

```python
def write_mbp_file(playlist: MbpPlaylist, tracks: list[str] | None = None) -> None
```

Write `playlist` back to disk.

<details>
<summary>Code:</summary>

```python
def write_mbp_file(playlist: MbpPlaylist, tracks: list[str] | None = None) -> None:
    playlist.path.write_bytes(write_mbp(playlist, tracks))
```

</details>
