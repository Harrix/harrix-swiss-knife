---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `settings.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `MusicBeeSettings`](#%EF%B8%8F-class-musicbeesettings)
  - [⚙️ Method `library_file (property)`](#%EF%B8%8F-method-library_file-property)
  - [⚙️ Method `placeholders (property)`](#%EF%B8%8F-method-placeholders-property)
  - [⚙️ Method `playlists_dir (property)`](#%EF%B8%8F-method-playlists_dir-property)
- [🔧 Function `default_musicbee_config`](#-function-default_musicbee_config)
- [🔧 Function `load_musicbee_settings`](#-function-load_musicbee_settings)

</details>

## 🏛️ Class `MusicBeeSettings`

```python
class MusicBeeSettings
```

Resolved MusicBee paths and Stream rules.

<details>
<summary>Code:</summary>

```python
class MusicBeeSettings:

    library_dir: Path
    music_root: Path
    stream_root: Path
    backup_dir: Path
    audio_extensions: frozenset[str]
    stream_playlist_prefix: str
    rules: list[dict[str, Any]]

    @property
    def library_file(self) -> Path:
        """`MusicBeeLibrary.mbl` path."""
        return self.library_dir / "MusicBeeLibrary.mbl"

    @property
    def placeholders(self) -> dict[str, str]:
        """Values for `{music_root}` / `{stream_root}` in rules."""
        return {
            "music_root": str(self.music_root),
            "stream_root": str(self.stream_root),
        }

    @property
    def playlists_dir(self) -> Path:
        """Directory that holds `.mbp` / `.xautopf` files."""
        return self.library_dir / "Playlists"
```

</details>

### ⚙️ Method `library_file (property)`

```python
def library_file(self) -> Path
```

`MusicBeeLibrary.mbl` path.

<details>
<summary>Code:</summary>

```python
def library_file(self) -> Path:
        return self.library_dir / "MusicBeeLibrary.mbl"
```

</details>

### ⚙️ Method `placeholders (property)`

```python
def placeholders(self) -> dict[str, str]
```

Values for `{music_root}` / `{stream_root}` in rules.

<details>
<summary>Code:</summary>

```python
def placeholders(self) -> dict[str, str]:
        return {
            "music_root": str(self.music_root),
            "stream_root": str(self.stream_root),
        }
```

</details>

### ⚙️ Method `playlists_dir (property)`

```python
def playlists_dir(self) -> Path
```

Directory that holds `.mbp` / `.xautopf` files.

<details>
<summary>Code:</summary>

```python
def playlists_dir(self) -> Path:
        return self.library_dir / "Playlists"
```

</details>

## 🔧 Function `default_musicbee_config`

```python
def default_musicbee_config() -> dict[str, Any]
```

Return the example `musicbee` object for `config.example.json`.

<details>
<summary>Code:</summary>

```python
def default_musicbee_config() -> dict[str, Any]:
    return {
        "library_dir": "D:/Dropbox/Programs/MusicBee/Library",
        "music_root": "C:/Users/sergi/OneDrive/Music",
        "stream_root": "C:/Users/sergi/OneDrive/Music/Stream",
        "backup_dir": "D:/Dropbox/Backups",
        "audio_extensions": list(DEFAULT_AUDIO_EXTENSIONS),
        "stream_playlist_prefix": DEFAULT_STREAM_PREFIX,
        "rules": list(DEFAULT_MUSICBEE_RULES),
    }
```

</details>

## 🔧 Function `load_musicbee_settings`

```python
def load_musicbee_settings(config: dict[str, Any], *, config_path: str | None = None) -> MusicBeeSettings
```

Read the `musicbee` block, allowing `backup_dir` from `config-temp.json`.

<details>
<summary>Code:</summary>

```python
def load_musicbee_settings(
    config: dict[str, Any],
    *,
    config_path: str | None = None,
) -> MusicBeeSettings:
    block = config.get("musicbee")
    if block is None:
        msg = "config.json is missing the musicbee object"
        raise ValueError(msg)
    if not isinstance(block, dict):
        msg = "config.json musicbee must be an object"
        raise TypeError(msg)
    library_dir = _required_path(block, "library_dir")
    music_root = _required_path(block, "music_root")
    stream_root = _required_path(block, "stream_root")
    backup_dir = _backup_dir(block, config_path)
    raw_ext = block.get("audio_extensions") or list(DEFAULT_AUDIO_EXTENSIONS)
    extensions = frozenset(str(item).casefold() for item in raw_ext if str(item).strip())
    prefix = str(block.get("stream_playlist_prefix") or DEFAULT_STREAM_PREFIX)
    rules = block.get("rules")
    if not isinstance(rules, list) or not rules:
        rules = list(DEFAULT_MUSICBEE_RULES)
    return MusicBeeSettings(
        library_dir=library_dir,
        music_root=music_root,
        stream_root=stream_root,
        backup_dir=backup_dir,
        audio_extensions=extensions,
        stream_playlist_prefix=prefix,
        rules=[item for item in rules if isinstance(item, dict)],
    )
```

</details>
