---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `checkin_sounds.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `habit_checkin_sound_name`](#-function-habit_checkin_sound_name)
- [🔧 Function `play_habit_checkin_sound`](#-function-play_habit_checkin_sound)

</details>

## 🔧 Function `habit_checkin_sound_name`

```python
def habit_checkin_sound_name(value: int | None) -> str | None
```

Return the bundled WAV name for a stored check-in value.

<details>
<summary>Code:</summary>

```python
def habit_checkin_sound_name(value: int | None) -> str | None:
    if value is None:
        return None
    if value == 0:
        return _NOT_DONE_NAME
    if value > 0:
        return _DONE_NAME
    return None
```

</details>

## 🔧 Function `play_habit_checkin_sound`

```python
def play_habit_checkin_sound(value: int | None) -> None
```

Play the Done or Not done sound without blocking the UI.

Loading and playback are deferred to the next event-loop turn so the
checkmark can paint before audio work runs.

<details>
<summary>Code:</summary>

```python
def play_habit_checkin_sound(value: int | None) -> None:
    name = habit_checkin_sound_name(value)
    if name is None:
        return
    QTimer.singleShot(0, lambda sound_name=name: _play_named(sound_name))
```

</details>
