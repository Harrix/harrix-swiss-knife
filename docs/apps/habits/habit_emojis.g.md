---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `habit_emojis.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `default_habit_emoji`](#-function-default_habit_emoji)
- [🔧 Function `normalize_habit_emoji`](#-function-normalize_habit_emoji)

</details>

## 🔧 Function `default_habit_emoji`

```python
def default_habit_emoji(habit_id: int) -> str
```

Return a stable preset emoji for a habit ID.

<details>
<summary>Code:</summary>

```python
def default_habit_emoji(habit_id: int) -> str:
    if not HABIT_EMOJI_PRESETS:
        return "✅"
    return HABIT_EMOJI_PRESETS[habit_id % len(HABIT_EMOJI_PRESETS)]
```

</details>

## 🔧 Function `normalize_habit_emoji`

```python
def normalize_habit_emoji(emoji: str | None, *, habit_id: int | None = None) -> str
```

Return a cleaned emoji or a fallback when empty.

<details>
<summary>Code:</summary>

```python
def normalize_habit_emoji(emoji: str | None, *, habit_id: int | None = None) -> str:
    value = (emoji or "").strip()
    if value:
        return value
    if habit_id is not None:
        return default_habit_emoji(habit_id)
    return HABIT_EMOJI_PRESETS[0] if HABIT_EMOJI_PRESETS else "✅"
```

</details>
