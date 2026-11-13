---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `habit_emoji_picker_dialog.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `HabitEmojiPickerDialog`](#%EF%B8%8F-class-habitemojipickerdialog)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `selected_emoji`](#%EF%B8%8F-method-selected_emoji)

</details>

## 🏛️ Class `HabitEmojiPickerDialog`

```python
class HabitEmojiPickerDialog(EmojiPickerDialog)
```

Pick a habit emoji from a preset grid or paste a custom emoji.

<details>
<summary>Code:</summary>

```python
class HabitEmojiPickerDialog(EmojiPickerDialog):

    def __init__(self, parent: QWidget | None = None, *, current_emoji: str = "") -> None:
        """Initialize the emoji picker dialog.

        Args:

        - `parent` (`QWidget | None`): Parent widget. Defaults to `None`.
        - `current_emoji` (`str`): Preselected emoji. Defaults to `""`.

        """
        super().__init__(
            parent,
            current_emoji=normalize_habit_emoji(current_emoji),
            presets=HABIT_EMOJI_PRESETS,
            allow_empty=False,
        )

    def selected_emoji(self) -> str:
        """Return the chosen emoji, never empty."""
        return normalize_habit_emoji(super().selected_emoji())
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None, *, current_emoji: str = '') -> None
```

Initialize the emoji picker dialog.

Args:

- `parent` (`QWidget | None`): Parent widget. Defaults to `None`.
- `current_emoji` (`str`): Preselected emoji. Defaults to `""`.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None, *, current_emoji: str = "") -> None:
        super().__init__(
            parent,
            current_emoji=normalize_habit_emoji(current_emoji),
            presets=HABIT_EMOJI_PRESETS,
            allow_empty=False,
        )
```

</details>

### ⚙️ Method `selected_emoji`

```python
def selected_emoji(self) -> str
```

Return the chosen emoji, never empty.

<details>
<summary>Code:</summary>

```python
def selected_emoji(self) -> str:
        return normalize_habit_emoji(super().selected_emoji())
```

</details>
