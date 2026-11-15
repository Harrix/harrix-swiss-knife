---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `habit_icon_display.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `habit_lucide_color`](#-function-habit_lucide_color)
- [🔧 Function `habit_lucide_icon`](#-function-habit_lucide_icon)
- [🔧 Function `lucide_name_for_habit_emoji`](#-function-lucide_name_for_habit_emoji)
- [🔧 Function `normalize_habit_lucide_name`](#-function-normalize_habit_lucide_name)
- [🔧 Function `resolve_habit_display_lucide`](#-function-resolve_habit_display_lucide)

</details>

## 🔧 Function `habit_lucide_color`

```python
def habit_lucide_color(lucide_name: str) -> str
```

Return a stable chromatic stroke for habit Lucide ID [`lucide_name`](../common/lucide_picker_dialog.g.md#%EF%B8%8F-method-lucide_name).

<details>
<summary>Code:</summary>

```python
def habit_lucide_color(lucide_name: str) -> str:
    name = lucide_name.strip()
    if not name:
        return _HABIT_CYAN
    mapped = HABIT_LUCIDE_COLORS.get(name)
    if mapped is not None:
        return mapped
    digest = hashlib.sha256(name.encode("utf-8")).digest()
    return _HABIT_COLOR_PALETTE[digest[0] % len(_HABIT_COLOR_PALETTE)]
```

</details>

## 🔧 Function `habit_lucide_icon`

```python
def habit_lucide_icon(lucide_name: str = '', size: int = _HABIT_ICON_SIZE) -> QIcon
```

Return a colored Lucide `QIcon` when [`lucide_name`](../common/lucide_picker_dialog.g.md#%EF%B8%8F-method-lucide_name) is a known SVG ID.

<details>
<summary>Code:</summary>

```python
def habit_lucide_icon(lucide_name: str = "", size: int = _HABIT_ICON_SIZE) -> QIcon:
    name = lucide_name.strip()
    if not name or lucide_svg_path(name) is None:
        return QIcon()
    return create_lucide_icon(name, size, color=habit_lucide_color(name))
```

</details>

## 🔧 Function `lucide_name_for_habit_emoji`

```python
def lucide_name_for_habit_emoji(emoji: str) -> str | None
```

Return Lucide ID suggested for a habit emoji, or `None` when blank/unknown.

<details>
<summary>Code:</summary>

```python
def lucide_name_for_habit_emoji(emoji: str) -> str | None:
    raw = emoji.strip()
    if not raw:
        return None
    mapped = HABIT_EMOJI_TO_LUCIDE.get(raw)
    if mapped is None:
        key = raw.replace("\ufe0f", "")
        mapped = HABIT_EMOJI_TO_LUCIDE.get(key)
    if mapped is None:
        mapped = lucide_name_for_chrome_emoji(raw)
    if mapped and lucide_svg_path(mapped) is not None:
        return mapped
    return None
```

</details>

## 🔧 Function `normalize_habit_lucide_name`

```python
def normalize_habit_lucide_name(lucide_name: str | None) -> str
```

Return a trimmed Lucide ID when the SVG exists, otherwise empty.

<details>
<summary>Code:</summary>

```python
def normalize_habit_lucide_name(lucide_name: str | None) -> str:
    name = (lucide_name or "").strip()
    if name and lucide_svg_path(name) is not None:
        return name
    return ""
```

</details>

## 🔧 Function `resolve_habit_display_lucide`

```python
def resolve_habit_display_lucide(*, lucide_name: str = '') -> str | None
```

Return Lucide ID to paint, or `None` to fall back to emoji.

<details>
<summary>Code:</summary>

```python
def resolve_habit_display_lucide(*, lucide_name: str = "") -> str | None:
    name = normalize_habit_lucide_name(lucide_name)
    return name or None
```

</details>
