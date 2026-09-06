---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `config.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `ensure_screen_record_config_defaults`](#-function-ensure_screen_record_config_defaults)
- [🔧 Function `get_screen_record_audio`](#-function-get_screen_record_audio)
- [🔧 Function `get_screen_record_countdown_seconds`](#-function-get_screen_record_countdown_seconds)
- [🔧 Function `get_screen_record_microphone_id`](#-function-get_screen_record_microphone_id)
- [🔧 Function `save_screen_record_settings`](#-function-save_screen_record_settings)

</details>

## 🔧 Function `ensure_screen_record_config_defaults`

```python
def ensure_screen_record_config_defaults() -> None
```

Write missing `apps.screen_record_countdown_seconds` into `config.json` once.

<details>
<summary>Code:</summary>

```python
def ensure_screen_record_config_defaults() -> None:
    path = Path(get_config_path_str())
    if not path.is_file():
        return
    try:
        with path.open(encoding="utf-8") as handle:
            config = json.load(handle)
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        return
    if not isinstance(config, dict):
        return
    apps = dict(config.get("apps") or {})
    changed = False
    if _SCREEN_RECORD_COUNTDOWN_KEY not in apps:
        apps[_SCREEN_RECORD_COUNTDOWN_KEY] = DEFAULT_SCREEN_RECORD_COUNTDOWN_SECONDS
        changed = True
    # Audio lives in config-temp.json; drop a leftover key from config.json if present.
    if _SCREEN_RECORD_AUDIO_KEY in apps:
        del apps[_SCREEN_RECORD_AUDIO_KEY]
        changed = True
    if not changed:
        return
    config["apps"] = apps
    path.write_text(h.dev.dumps_pretty_json(config), encoding="utf-8")
```

</details>

## 🔧 Function `get_screen_record_audio`

```python
def get_screen_record_audio(temp_config: dict[str, Any] | None = None) -> ScreenRecordAudio
```

Return `screen_record_audio` from `config-temp.json`.

<details>
<summary>Code:</summary>

```python
def get_screen_record_audio(temp_config: dict[str, Any] | None = None) -> ScreenRecordAudio:
    data = temp_config
    if data is None:
        try:
            loaded = h.dev.config_load(get_config_path_str(), is_temp=True)
            data = loaded if isinstance(loaded, dict) else {}
        except (FileNotFoundError, OSError, TypeError, ValueError):
            data = {}
    raw = str(data.get(_SCREEN_RECORD_AUDIO_KEY, DEFAULT_SCREEN_RECORD_AUDIO)).strip().lower()
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

## 🔧 Function `get_screen_record_microphone_id`

```python
def get_screen_record_microphone_id(config: dict[str, Any] | None = None) -> str
```

Return `apps.screen_record_microphone_id` (empty when unset).

<details>
<summary>Code:</summary>

```python
def get_screen_record_microphone_id(config: dict[str, Any] | None = None) -> str:
    apps = _apps(config)
    return str(apps.get(_SCREEN_RECORD_MIC_KEY, "") or "").strip()
```

</details>

## 🔧 Function `save_screen_record_settings`

```python
def save_screen_record_settings(*, audio: ScreenRecordAudio | None = None, countdown_seconds: int | None = None, microphone_id: str | None = None) -> None
```

Persist screen-record settings (`audio` → config-temp; rest → `config.json`).

<details>
<summary>Code:</summary>

```python
def save_screen_record_settings(
    *,
    audio: ScreenRecordAudio | None = None,
    countdown_seconds: int | None = None,
    microphone_id: str | None = None,
) -> None:
    if audio is not None and audio in SCREEN_RECORD_AUDIO_MODES:
        _save_temp_audio(audio)

    if countdown_seconds is None and microphone_id is None:
        return

    path = Path(get_config_path_str())
    with path.open(encoding="utf-8") as handle:
        config = json.load(handle)
    apps = dict(config.get("apps") or {})
    if countdown_seconds is not None:
        apps[_SCREEN_RECORD_COUNTDOWN_KEY] = max(0, min(int(countdown_seconds), _MAX_COUNTDOWN_SECONDS))
    if microphone_id is not None:
        apps[_SCREEN_RECORD_MIC_KEY] = microphone_id.strip()
    if _SCREEN_RECORD_COUNTDOWN_KEY not in apps:
        apps[_SCREEN_RECORD_COUNTDOWN_KEY] = DEFAULT_SCREEN_RECORD_COUNTDOWN_SECONDS
    apps.pop(_SCREEN_RECORD_AUDIO_KEY, None)
    config["apps"] = apps
    path.write_text(h.dev.dumps_pretty_json(config), encoding="utf-8")
```

</details>
