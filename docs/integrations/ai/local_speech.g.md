---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `local_speech.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `is_ai_unreachable_error`](#-function-is_ai_unreachable_error)
- [🔧 Function `is_local_speech_enabled`](#-function-is_local_speech_enabled)
- [🔧 Function `local_speech_model_size`](#-function-local_speech_model_size)
- [🔧 Function `transcribe_audio_local`](#-function-transcribe_audio_local)

</details>

## 🔧 Function `is_ai_unreachable_error`

```python
def is_ai_unreachable_error(message: str) -> bool
```

Return whether `message` means the AI host could not be reached.

<details>
<summary>Code:</summary>

```python
def is_ai_unreachable_error(message: str) -> bool:
    text = (message or "").strip()
    if not text:
        return False
    if BOTHUB_UNREACHABLE_MSG in text:
        return True
    if is_connect_timeout_message(text):
        return True
    lower = text.lower()
    return any(marker in lower for marker in _UNREACHABLE_MARKERS)
```

</details>

## 🔧 Function `is_local_speech_enabled`

```python
def is_local_speech_enabled(config: dict[str, Any]) -> bool
```

Return whether optional local speech fallback is enabled in config.

<details>
<summary>Code:</summary>

```python
def is_local_speech_enabled(config: dict[str, Any]) -> bool:
    section = _local_speech_section(config)
    return bool(section.get("enabled"))
```

</details>

## 🔧 Function `local_speech_model_size`

```python
def local_speech_model_size(config: dict[str, Any]) -> str
```

Return Whisper model size for local speech (`small` by default).

<details>
<summary>Code:</summary>

```python
def local_speech_model_size(config: dict[str, Any]) -> str:
    section = _local_speech_section(config)
    model = str(section.get("model") or "small").strip()
    return model or "small"
```

</details>

## 🔧 Function `transcribe_audio_local`

```python
def transcribe_audio_local(audio: tuple[bytes, str], *, model_size: str = 'small') -> str
```

Transcribe `audio` with faster-whisper.

Raises:

- `RuntimeError`: When faster-whisper is missing or transcription fails.
- `ValueError`: When the transcript is empty.

<details>
<summary>Code:</summary>

```python
def transcribe_audio_local(
    audio: tuple[bytes, str],
    *,
    model_size: str = "small",
) -> str:
    data, mime = audio
    if not data:
        msg = "Empty audio for local speech recognition"
        raise ValueError(msg)

    try:
        whisper = importlib.import_module("faster_whisper")
    except ImportError as exc:
        msg = "Local speech requires the optional package faster-whisper. Install with: uv sync --extra local-speech"
        raise RuntimeError(msg) from exc

    suffix = _suffix_for_mime(mime)
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as handle:
        handle.write(data)
        temp_path = Path(handle.name)

    try:
        model = whisper.WhisperModel(model_size, device="cpu", compute_type="int8")
        segments, _info = model.transcribe(str(temp_path), beam_size=1)
        text = " ".join(segment.text.strip() for segment in segments if segment.text.strip()).strip()
    except Exception as exc:
        msg = f"Local speech recognition failed: {exc}"
        raise RuntimeError(msg) from exc
    finally:
        temp_path.unlink(missing_ok=True)

    if not text:
        msg = "Empty transcription from local speech model"
        raise ValueError(msg)
    return text
```

</details>
