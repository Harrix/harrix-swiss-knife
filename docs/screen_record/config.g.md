---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `config.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `get_screen_record_audio`](#-function-get_screen_record_audio)
- [🔧 Function `get_screen_record_countdown_seconds`](#-function-get_screen_record_countdown_seconds)
- [🔧 Function `save_screen_record_settings`](#-function-save_screen_record_settings)

</details>

## 🔧 Function `get_screen_record_audio`

```python
def get_screen_record_audio(config: dict[str, Any] | None = None) -> ScreenRecordAudio
```

Return `apps.screen_record_audio` (`none` / `mic` / `system` / `mic_and_system`).

<details>
<summary>Code:</summary>

```python
def get_screen_record_audio(config: dict[str, Any] | None = None) -> ScreenRecordAudio:
    apps = _apps(config)
    raw = str(apps.get(_SCREEN_RECORD_AUDIO_KEY, DEFAULT_SCREEN_RECORD_AUDIO)).strip().lower()
    if raw in SCREEN_RECORD_AUDIO_MODES:
        return cast("ScreenRecordAudio", raw)
    return DEFAULT_SCREEN_RECORD_AUDIO
```

</details>

## 🔧 Function `get_screen_record_countdown_seconds`

```python
def get_screen_record_countdown_seconds(config: dict[str, Any] | None = None) -> int
```

Return `apps.screen_record_countdown_seconds` (default `3`, clamped to `0..30`).

<details>
<summary>Code:</summary>

```python
def get_screen_record_countdown_seconds(config: dict[str, Any] | None = None) -> int:
    apps = _apps(config)
    raw = apps.get(_SCREEN_RECORD_COUNTDOWN_KEY, DEFAULT_SCREEN_RECORD_COUNTDOWN_SECONDS)
    try:
        return max(0, min(int(raw), _MAX_COUNTDOWN_SECONDS))
    except (TypeError, ValueError):
        return DEFAULT_SCREEN_RECORD_COUNTDOWN_SECONDS
```

</details>

## 🔧 Function `save_screen_record_settings`

```python
def save_screen_record_settings(*, audio: ScreenRecordAudio | None = None, countdown_seconds: int | None = None) -> None
```

Persist screen-record settings under `apps` in `config.json`.

<details>
<summary>Code:</summary>

```python
def save_screen_record_settings(
    *,
    audio: ScreenRecordAudio | None = None,
    countdown_seconds: int | None = None,
) -> None:
    path = Path(get_config_path_str())
    with path.open(encoding="utf-8") as handle:
        config = json.load(handle)
    apps = dict(config.get("apps") or {})
    if audio is not None and audio in SCREEN_RECORD_AUDIO_MODES:
        apps[_SCREEN_RECORD_AUDIO_KEY] = audio
    if countdown_seconds is not None:
        apps[_SCREEN_RECORD_COUNTDOWN_KEY] = max(0, min(int(countdown_seconds), _MAX_COUNTDOWN_SECONDS))
    config["apps"] = apps
    path.write_text(h.dev.dumps_pretty_json(config), encoding="utf-8")
```

</details>
