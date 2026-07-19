---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `speech.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `audio_bytes_and_mime`](#-function-audio_bytes_and_mime)
- [🔧 Function `audio_format_from_suffix`](#-function-audio_format_from_suffix)
- [🔧 Function `build_transcription_prompt`](#-function-build_transcription_prompt)
- [🔧 Function `validate_audio_bytes`](#-function-validate_audio_bytes)

</details>

## 🔧 Function `audio_bytes_and_mime`

```python
def audio_bytes_and_mime(path: str | Path) -> tuple[bytes, str]
```

Read an audio file and return its bytes and MIME type.

Raises:

- `ValueError`: If the file extension is not supported or the file is too small.

<details>
<summary>Code:</summary>

```python
def audio_bytes_and_mime(path: str | Path) -> tuple[bytes, str]:
    file_path = Path(path)
    mime_type = audio_format_from_suffix(file_path.suffix)
    if mime_type is None:
        msg = f"Unsupported audio format: {file_path.suffix}"
        raise ValueError(msg)
    data = file_path.read_bytes()
    validate_audio_bytes(data, file_path.name)
    return data, mime_type
```

</details>

## 🔧 Function `audio_format_from_suffix`

```python
def audio_format_from_suffix(suffix: str) -> str | None
```

Map a file suffix to MIME type, or `None` if unsupported.

<details>
<summary>Code:</summary>

```python
def audio_format_from_suffix(suffix: str) -> str | None:
    return _MIME_BY_SUFFIX.get(suffix.lower())
```

</details>

## 🔧 Function `build_transcription_prompt`

```python
def build_transcription_prompt() -> str
```

Return the built-in prompt for speech-to-text requests.

<details>
<summary>Code:</summary>

```python
def build_transcription_prompt() -> str:
    return TRANSCRIPTION_PROMPT
```

</details>

## 🔧 Function `validate_audio_bytes`

```python
def validate_audio_bytes(data: bytes, label: str = "audio") -> None
```

Raise ValueError when audio payload is empty or too small to be valid.

<details>
<summary>Code:</summary>

```python
def validate_audio_bytes(data: bytes, label: str = "audio") -> None:
    if len(data) < MIN_AUDIO_BYTES:
        msg = f"{label} is empty or too short ({len(data)} bytes). Record longer or choose another file."
        raise ValueError(msg)
```

</details>
