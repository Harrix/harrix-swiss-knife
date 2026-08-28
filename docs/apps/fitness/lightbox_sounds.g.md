---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `lightbox_sounds.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `fitness_timer_cue_sound_name`](#-function-fitness_timer_cue_sound_name)
- [🔧 Function `play_fitness_timer_alert`](#-function-play_fitness_timer_alert)
- [🔧 Function `play_fitness_timer_cue`](#-function-play_fitness_timer_cue)
- [🔧 Function `stop_fitness_timer_alert`](#-function-stop_fitness_timer_alert)

</details>

## 🔧 Function `fitness_timer_cue_sound_name`

```python
def fitness_timer_cue_sound_name(cue: FitnessTimerCue) -> str
```

Return the bundled WAV name for a one-shot timer cue.

<details>
<summary>Code:</summary>

```python
def fitness_timer_cue_sound_name(cue: FitnessTimerCue) -> str:
    return _CUE_NAMES[cue]
```

</details>

## 🔧 Function `play_fitness_timer_alert`

```python
def play_fitness_timer_alert() -> None
```

Start a looping alert if one is not already playing.

<details>
<summary>Code:</summary>

```python
def play_fitness_timer_alert() -> None:
    if _alert_effects and _alert_effects[0].isPlaying():
        return
    url = _sound_url(_ALERT_NAME)
    if not url.isValid():
        return
    effect = QSoundEffect()
    effect.setSource(url)
    effect.setVolume(_VOLUME)
    effect.setLoopCount(QSoundEffect.Infinite)
    _alert_effects.clear()
    _alert_effects.append(effect)
    effect.play()
```

</details>

## 🔧 Function `play_fitness_timer_cue`

```python
def play_fitness_timer_cue(cue: FitnessTimerCue) -> None
```

Play a one-shot Start or Finish cue.

<details>
<summary>Code:</summary>

```python
def play_fitness_timer_cue(cue: FitnessTimerCue) -> None:
    url = _sound_url(fitness_timer_cue_sound_name(cue))
    if not url.isValid():
        return
    effect = QSoundEffect()
    effect.setSource(url)
    effect.setVolume(_VOLUME)
    _cue_effects.clear()
    _cue_effects.append(effect)
    effect.play()
```

</details>

## 🔧 Function `stop_fitness_timer_alert`

```python
def stop_fitness_timer_alert() -> None
```

Stop the workout-slot alert if it is playing.

<details>
<summary>Code:</summary>

```python
def stop_fitness_timer_alert() -> None:
    for effect in _alert_effects:
        effect.stop()
    _alert_effects.clear()
```

</details>
