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
- [🔧 Function `play_fitness_timer_cue`](#-function-play_fitness_timer_cue)
- [🔧 Function `stop_fitness_timer_alert`](#-function-stop_fitness_timer_alert)

</details>

## 🔧 Function `fitness_timer_cue_sound_name`

```python
def fitness_timer_cue_sound_name(cue: FitnessTimerCue) -> str
```

Return the bundled WAV name for a fitness cue.

<details>
<summary>Code:</summary>

```python
def fitness_timer_cue_sound_name(cue: FitnessTimerCue) -> str:
    return _CUE_NAMES[cue]
```

</details>

## 🔧 Function `play_fitness_timer_cue`

```python
def play_fitness_timer_cue(cue: FitnessTimerCue) -> None
```

Play a one-shot fitness cue without cutting off earlier voices.

<details>
<summary>Code:</summary>

```python
def play_fitness_timer_cue(cue: FitnessTimerCue) -> None:
    if qt_sounds_muted():
        return
    url = _sound_url(fitness_timer_cue_sound_name(cue))
    if not url.isValid():
        return
    effect = QSoundEffect()
    effect.setSource(url)
    effect.setVolume(_VOLUME)
    _prune_cue_effects()
    _cue_effects.append(effect)
    effect.play()
```

</details>

## 🔧 Function `stop_fitness_timer_alert`

```python
def stop_fitness_timer_alert() -> None
```

No-op kept for call sites that used the old looping overtime alert.

<details>
<summary>Code:</summary>

```python
def stop_fitness_timer_alert() -> None:
```

</details>
