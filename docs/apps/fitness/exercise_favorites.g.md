---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `exercise_favorites.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `format_favorite_exercise_label`](#-function-format_favorite_exercise_label)
- [🔧 Function `prefer_favorite_names`](#-function-prefer_favorite_names)

</details>

## 🔧 Function `format_favorite_exercise_label`

```python
def format_favorite_exercise_label(name: str, *, favorite: bool, extra: str = '') -> str
```

Build a list label, prefixing a star when the exercise is a favorite.

Args:

- `name` (`str`): English exercise name.
- `favorite` (`bool`): Whether the exercise is pinned as a favorite.
- `extra` (`str`): Optional suffix such as a daily goal. Defaults to `""`.

Returns:

- `str`: Display text. The real name must still be stored in `UserRole`.

<details>
<summary>Code:</summary>

```python
def format_favorite_exercise_label(name: str, *, favorite: bool, extra: str = "") -> str:
    prefix = FAVORITE_PREFIX if favorite else ""
    extra_part = f" {extra}" if extra else ""
    return f"{prefix}{name}{extra_part}"
```

</details>

## 🔧 Function `prefer_favorite_names`

```python
def prefer_favorite_names(names: list[str], favorite_names: set[str]) -> list[str]
```

Return `names` with favorites first, keeping relative order in each group.

Args:

- `names` (`list[str]`): Exercise names in the current list order.
- `favorite_names` (`set[str]`): Names marked as favorites.

Returns:

- `list[str]`: Favorites, then the remaining names.

<details>
<summary>Code:</summary>

```python
def prefer_favorite_names(names: list[str], favorite_names: set[str]) -> list[str]:
    if not favorite_names:
        return list(names)
    favorites = [name for name in names if name in favorite_names]
    others = [name for name in names if name not in favorite_names]
    return favorites + others
```

</details>
