---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `category_icon_display.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `category_display_label`](#-function-category_display_label)
- [🔧 Function `category_lucide_icon`](#-function-category_lucide_icon)
- [🔧 Function `lucide_name_for_category_icon`](#-function-lucide_name_for_category_icon)
- [🔧 Function `strip_category_display_value`](#-function-strip_category_display_value)

</details>

## 🔧 Function `category_display_label`

```python
def category_display_label(name: str, *, income: bool = False, name_local: str = '') -> str
```

Return category label text without the DB emoji glyph.

<details>
<summary>Code:</summary>

```python
def category_display_label(name: str, *, income: bool = False, name_local: str = "") -> str:
    display = name.strip()
    if income:
        display = f"{display} (Income)"
    local = name_local.strip()
    if local:
        display = f"{display} ({local})"
    return display
```

</details>

## 🔧 Function `category_lucide_icon`

```python
def category_lucide_icon(emoji: str, size: int = _CATEGORY_ICON_SIZE) -> QIcon
```

Return a Lucide `QIcon` for a category emoji, or empty when [`emoji`](../common/emoji_picker_dialog.g.md#%EF%B8%8F-method-emoji) is blank.

<details>
<summary>Code:</summary>

```python
def category_lucide_icon(emoji: str, size: int = _CATEGORY_ICON_SIZE) -> QIcon:
    name = lucide_name_for_category_icon(emoji)
    if name is None:
        return QIcon()
    return create_lucide_icon(name, size)
```

</details>

## 🔧 Function `lucide_name_for_category_icon`

```python
def lucide_name_for_category_icon(emoji: str) -> str | None
```

Return Lucide ID for a category emoji, or `None` when blank.

<details>
<summary>Code:</summary>

```python
def lucide_name_for_category_icon(emoji: str) -> str | None:
    raw = emoji.strip()
    if not raw:
        return None
    # Variation selectors / ZWJ sequences: try exact, then stripped token.
    mapped = FINANCE_CATEGORY_EMOJI_TO_LUCIDE.get(raw)
    if mapped is None:
        key = raw.replace("\ufe0f", "")
        mapped = FINANCE_CATEGORY_EMOJI_TO_LUCIDE.get(key)
    if mapped is None:
        mapped = lucide_name_for_chrome_emoji(raw)
    return mapped or _FALLBACK_LUCIDE
```

</details>

## 🔧 Function `strip_category_display_value`

```python
def strip_category_display_value(category_value: str) -> str
```

Strip a leading emoji and `(Income)` marker from a category display value.

<details>
<summary>Code:</summary>

```python
def strip_category_display_value(category_value: str) -> str:
    _emoji, rest = split_leading_emoji(category_value)
    text = rest if _emoji else category_value
    return text.replace(" (Income)", "").strip()
```

</details>
