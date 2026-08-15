---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `speech_to_text_pending.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `PendingSpeechRecording`](#%EF%B8%8F-class-pendingspeechrecording)
  - [⚙️ Method `size_bytes (property)`](#%EF%B8%8F-method-size_bytes-property)
- [🏛️ Class `SpeechToTextPendingStore`](#%EF%B8%8F-class-speechtotextpendingstore)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `clear`](#%EF%B8%8F-method-clear)
  - [⚙️ Method `load`](#%EF%B8%8F-method-load)
  - [⚙️ Method `save`](#%EF%B8%8F-method-save)
- [🔧 Function `default_speech_to_text_pending_dir`](#-function-default_speech_to_text_pending_dir)

</details>

## 🏛️ Class `PendingSpeechRecording`

```python
class PendingSpeechRecording
```

An audio file waiting to be sent for recognition.

<details>
<summary>Code:</summary>

```python
class PendingSpeechRecording:

    path: Path
    mime_type: str

    @property
    def size_bytes(self) -> int:
        """Return file size in bytes, or `0` when missing."""
        try:
            return self.path.stat().st_size if self.path.is_file() else 0
        except OSError:
            return 0
```

</details>

### ⚙️ Method `size_bytes (property)`

```python
def size_bytes(self) -> int
```

Return file size in bytes, or `0` when missing.

<details>
<summary>Code:</summary>

```python
def size_bytes(self) -> int:
        try:
            return self.path.stat().st_size if self.path.is_file() else 0
        except OSError:
            return 0
```

</details>

## 🏛️ Class `SpeechToTextPendingStore`

```python
class SpeechToTextPendingStore
```

Keep the latest not-yet-successfully-processed speech recording on disk.

Files live under a per-user data directory (not project `temp/`), so they survive
process restarts and `clear temp folder`.

<details>
<summary>Code:</summary>

```python
class SpeechToTextPendingStore:

    def __init__(self, root: Path | None = None) -> None:
        """Initialize the store.

        Args:

        - `root` (`Path | None`): Optional override directory (tests). Defaults to the
          per-user speech-to-text data folder.

        """
        self._root = Path(root) if root is not None else default_speech_to_text_pending_dir()
        self._meta_path = self._root / _META_FILENAME

    def clear(self) -> None:
        """Delete the pending audio file and metadata."""
        if not self._root.exists():
            return
        for child in list(self._root.iterdir()):
            if child.is_file():
                child.unlink(missing_ok=True)
        with contextlib.suppress(OSError):
            self._root.rmdir()

    def load(self) -> PendingSpeechRecording | None:
        """Return the pending recording when the file and metadata are valid."""
        meta = self._read_meta()
        if meta is None:
            self.clear()
            return None

        path = Path(str(meta.get("path", "")).strip())
        if not path.is_absolute():
            path = self._root / path.name
        mime_type = str(meta.get("mime_type", "")).strip()
        if not mime_type:
            mime_type = audio_format_from_suffix(path.suffix) or ""

        if not path.is_file() or path.stat().st_size < MIN_AUDIO_BYTES or not mime_type:
            self.clear()
            return None

        return PendingSpeechRecording(path=path, mime_type=mime_type)

    def save(self, source: Path | str) -> PendingSpeechRecording:
        """Copy `source` into the pending folder and return the stored recording.

        Raises:

        - `OSError`: If the file cannot be preserved.
        - `ValueError`: If the source is missing or too small / unsupported.

        """
        source_path = Path(source)
        if not source_path.is_file():
            msg = "Recording file missing"
            raise ValueError(msg)

        size = source_path.stat().st_size
        if size < MIN_AUDIO_BYTES:
            msg = f"Recording is empty or too short ({size} bytes)"
            raise ValueError(msg)

        suffix = source_path.suffix.lower()
        mime_type = audio_format_from_suffix(suffix)
        if mime_type is None or suffix not in _SUPPORTED_SUFFIXES:
            msg = f"Unsupported audio format: {suffix or '(none)'}"
            raise ValueError(msg)

        self._root.mkdir(parents=True, exist_ok=True)
        destination = self._root / f"{_PENDING_STEM}{suffix}"
        temporary = self._root / f"{_PENDING_STEM}{suffix}.tmp"

        if source_path.resolve() != destination.resolve():
            temporary.unlink(missing_ok=True)
            shutil.copy2(source_path, temporary)
            if temporary.stat().st_size < MIN_AUDIO_BYTES:
                temporary.unlink(missing_ok=True)
                msg = "Could not preserve pending recording"
                raise OSError(msg)
            destination.unlink(missing_ok=True)
            temporary.replace(destination)
        elif not destination.is_file() or destination.stat().st_size < MIN_AUDIO_BYTES:
            msg = "Could not preserve pending recording"
            raise OSError(msg)

        for child in list(self._root.iterdir()):
            if child in (destination, self._meta_path):
                continue
            if child.is_file() and child.name.startswith(_PENDING_STEM):
                child.unlink(missing_ok=True)

        meta = {
            "path": str(destination),
            "mime_type": mime_type,
        }
        self._meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return PendingSpeechRecording(path=destination, mime_type=mime_type)

    def _read_meta(self) -> dict[str, object] | None:
        if not self._meta_path.is_file():
            for suffix in _SUPPORTED_SUFFIXES:
                candidate = self._root / f"{_PENDING_STEM}{suffix}"
                if candidate.is_file() and candidate.stat().st_size >= MIN_AUDIO_BYTES:
                    mime = audio_format_from_suffix(suffix)
                    if mime:
                        return {"path": str(candidate), "mime_type": mime}
            return None
        try:
            raw = json.loads(self._meta_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, UnicodeError):
            return None
        return raw if isinstance(raw, dict) else None
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, root: Path | None = None) -> None
```

Initialize the store.

Args:

- `root` (`Path | None`): Optional override directory (tests). Defaults to the
  per-user speech-to-text data folder.

<details>
<summary>Code:</summary>

```python
def __init__(self, root: Path | None = None) -> None:
        self._root = Path(root) if root is not None else default_speech_to_text_pending_dir()
        self._meta_path = self._root / _META_FILENAME
```

</details>

### ⚙️ Method `clear`

```python
def clear(self) -> None
```

Delete the pending audio file and metadata.

<details>
<summary>Code:</summary>

```python
def clear(self) -> None:
        if not self._root.exists():
            return
        for child in list(self._root.iterdir()):
            if child.is_file():
                child.unlink(missing_ok=True)
        with contextlib.suppress(OSError):
            self._root.rmdir()
```

</details>

### ⚙️ Method `load`

```python
def load(self) -> PendingSpeechRecording | None
```

Return the pending recording when the file and metadata are valid.

<details>
<summary>Code:</summary>

```python
def load(self) -> PendingSpeechRecording | None:
        meta = self._read_meta()
        if meta is None:
            self.clear()
            return None

        path = Path(str(meta.get("path", "")).strip())
        if not path.is_absolute():
            path = self._root / path.name
        mime_type = str(meta.get("mime_type", "")).strip()
        if not mime_type:
            mime_type = audio_format_from_suffix(path.suffix) or ""

        if not path.is_file() or path.stat().st_size < MIN_AUDIO_BYTES or not mime_type:
            self.clear()
            return None

        return PendingSpeechRecording(path=path, mime_type=mime_type)
```

</details>

### ⚙️ Method `save`

```python
def save(self, source: Path | str) -> PendingSpeechRecording
```

Copy `source` into the pending folder and return the stored recording.

Raises:

- `OSError`: If the file cannot be preserved.
- `ValueError`: If the source is missing or too small / unsupported.

<details>
<summary>Code:</summary>

```python
def save(self, source: Path | str) -> PendingSpeechRecording:
        source_path = Path(source)
        if not source_path.is_file():
            msg = "Recording file missing"
            raise ValueError(msg)

        size = source_path.stat().st_size
        if size < MIN_AUDIO_BYTES:
            msg = f"Recording is empty or too short ({size} bytes)"
            raise ValueError(msg)

        suffix = source_path.suffix.lower()
        mime_type = audio_format_from_suffix(suffix)
        if mime_type is None or suffix not in _SUPPORTED_SUFFIXES:
            msg = f"Unsupported audio format: {suffix or '(none)'}"
            raise ValueError(msg)

        self._root.mkdir(parents=True, exist_ok=True)
        destination = self._root / f"{_PENDING_STEM}{suffix}"
        temporary = self._root / f"{_PENDING_STEM}{suffix}.tmp"

        if source_path.resolve() != destination.resolve():
            temporary.unlink(missing_ok=True)
            shutil.copy2(source_path, temporary)
            if temporary.stat().st_size < MIN_AUDIO_BYTES:
                temporary.unlink(missing_ok=True)
                msg = "Could not preserve pending recording"
                raise OSError(msg)
            destination.unlink(missing_ok=True)
            temporary.replace(destination)
        elif not destination.is_file() or destination.stat().st_size < MIN_AUDIO_BYTES:
            msg = "Could not preserve pending recording"
            raise OSError(msg)

        for child in list(self._root.iterdir()):
            if child in (destination, self._meta_path):
                continue
            if child.is_file() and child.name.startswith(_PENDING_STEM):
                child.unlink(missing_ok=True)

        meta = {
            "path": str(destination),
            "mime_type": mime_type,
        }
        self._meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return PendingSpeechRecording(path=destination, mime_type=mime_type)
```

</details>

## 🔧 Function `default_speech_to_text_pending_dir`

```python
def default_speech_to_text_pending_dir() -> Path
```

Return the default per-user directory for pending speech recordings.

<details>
<summary>Code:</summary>

```python
def default_speech_to_text_pending_dir() -> Path:
    if sys.platform == "win32":
        local = os.environ.get("LOCALAPPDATA")
        if not local:
            local = str(Path.home() / "AppData" / "Local")
        return Path(local) / "HarrixSwissKnife" / "speech_to_text"
    xdg = os.environ.get("XDG_DATA_HOME")
    base = Path(xdg) if xdg else Path.home() / ".local" / "share"
    return base / "harrix-swiss-knife" / "speech_to_text"
```

</details>
