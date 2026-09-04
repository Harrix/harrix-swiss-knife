---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `mbl.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `MblLibrary`](#%EF%B8%8F-class-mbllibrary)
- [🏛️ Class `MblTrack`](#%EF%B8%8F-class-mbltrack)
  - [⚙️ Method `file_size (property)`](#%EF%B8%8F-method-file_size-property)
- [🔧 Function `build_minimal_mbl`](#-function-build_minimal_mbl)
- [🔧 Function `parse_mbl`](#-function-parse_mbl)
- [🔧 Function `write_mbl`](#-function-write_mbl)
- [🔧 Function `write_mbl_file`](#-function-write_mbl_file)

</details>

## 🏛️ Class `MblLibrary`

```python
class MblLibrary
```

Parsed MusicBee library.

<details>
<summary>Code:</summary>

```python
class MblLibrary:

    path: Path
    header: bytes
    tracks: list[MblTrack] = field(default_factory=list)
    trailing_data: bytes = b""
```

</details>

## 🏛️ Class `MblTrack`

```python
class MblTrack
```

One library record: opaque blobs around a file path.

<details>
<summary>Code:</summary>

```python
class MblTrack:

    pre_path_data: bytes
    path: str
    post_path_data: bytes

    @property
    def file_size(self) -> int | None:
        """File size in bytes from the 32-byte metadata after the path, if present."""
        if len(self.post_path_data) < _UINT32_SIZE:
            return None
        return struct.unpack_from("<I", self.post_path_data, 0)[0]
```

</details>

### ⚙️ Method `file_size (property)`

```python
def file_size(self) -> int | None
```

File size in bytes from the 32-byte metadata after the path, if present.

<details>
<summary>Code:</summary>

```python
def file_size(self) -> int | None:
        if len(self.post_path_data) < _UINT32_SIZE:
            return None
        return struct.unpack_from("<I", self.post_path_data, 0)[0]
```

</details>

## 🔧 Function `build_minimal_mbl`

```python
def build_minimal_mbl(tracks: list[tuple[str, int]]) -> bytes
```

Build a tiny valid `.mbl` used by tests: `(path, file_size)` rows.

<details>
<summary>Code:</summary>

```python
def build_minimal_mbl(tracks: list[tuple[str, int]]) -> bytes:
    library = MblLibrary(path=Path("MusicBeeLibrary.mbl"), header=struct.pack("<I", 0))
    for path, size in tracks:
        post = struct.pack("<I", size) + b"\x00" * (_META_SIZE - _UINT32_SIZE) + b"\xfe\x00\x00"
        library.tracks.append(MblTrack(pre_path_data=b"\x00" * _PRE_PATH_SIZE, path=path, post_path_data=post))
    return write_mbl(library)
```

</details>

## 🔧 Function `parse_mbl`

```python
def parse_mbl(path: Path, content: bytes | None = None) -> MblLibrary
```

Parse `MusicBeeLibrary.mbl` into track records.

<details>
<summary>Code:</summary>

```python
def parse_mbl(path: Path, content: bytes | None = None) -> MblLibrary:
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
```

</details>

## 🔧 Function `write_mbl`

```python
def write_mbl(library: MblLibrary) -> bytes
```

Serialize `library` including updated paths.

<details>
<summary>Code:</summary>

```python
def write_mbl(library: MblLibrary) -> bytes:
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
```

</details>

## 🔧 Function `write_mbl_file`

```python
def write_mbl_file(library: MblLibrary) -> None
```

Write `library` back to disk.

<details>
<summary>Code:</summary>

```python
def write_mbl_file(library: MblLibrary) -> None:
    library.path.write_bytes(write_mbl(library))
```

</details>
