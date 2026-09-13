---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `shutter_sound.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `load_screenshot_shutter_sound_enabled`](#-function-load_screenshot_shutter_sound_enabled)
- [🔧 Function `play_screenshot_shutter_sound`](#-function-play_screenshot_shutter_sound)
- [🔧 Function `preload_screenshot_shutter_sound`](#-function-preload_screenshot_shutter_sound)
- [🔧 Function `screenshot_shutter_sound_name`](#-function-screenshot_shutter_sound_name)

</details>

## 🔧 Function `load_screenshot_shutter_sound_enabled`

```python
def load_screenshot_shutter_sound_enabled() -> bool
```

Return whether the screenshot shutter sound is enabled in `config.json`.

<details>
<summary>Code:</summary>

```python
def load_screenshot_shutter_sound_enabled() -> bool:
    try:
        config = h.dev.config_load(get_config_path_str())
    except (FileNotFoundError, OSError, ValueError):
        return True
    value = config.get(SCREENSHOT_SHUTTER_SOUND_KEY, True)
    if isinstance(value, bool):
        return value
    return bool(value)
```

</details>

## 🔧 Function `play_screenshot_shutter_sound`

```python
def play_screenshot_shutter_sound() -> None
```

Play the camera shutter sound after a successful region capture.

Respects `screenshot_shutter_sound` in config and `HSK_MUTE_SOUNDS` / pytest.

<details>
<summary>Code:</summary>

```python
def play_screenshot_shutter_sound() -> None:
    if qt_sounds_muted() or not load_screenshot_shutter_sound_enabled():
        return
    url = _sound_url(_SOUND_NAME)
    if not url.isValid():
        return
    _ensure_primed(url)
    effect = QSoundEffect()
    effect.setSource(url)
    effect.setVolume(_VOLUME)
    _prune_live_effects()
    _live_effects.append(effect)
    effect.play()
```

</details>

## 🔧 Function `preload_screenshot_shutter_sound`

```python
def preload_screenshot_shutter_sound() -> None
```

Warm the audio device so the first capture click is audible on Windows.

<details>
<summary>Code:</summary>

```python
def preload_screenshot_shutter_sound() -> None:
    if qt_sounds_muted():
        return
    url = _sound_url(_SOUND_NAME)
    if url.isValid():
        _ensure_primed(url)
```

</details>

## 🔧 Function `screenshot_shutter_sound_name`

```python
def screenshot_shutter_sound_name() -> str
```

Return the bundled WAV filename for the shutter click.

<details>
<summary>Code:</summary>

```python
def screenshot_shutter_sound_name() -> str:
    return _SOUND_NAME
```

</details>
