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
- [🔧 Function `category_lucide_color`](#-function-category_lucide_color)
- [🔧 Function `category_lucide_icon`](#-function-category_lucide_icon)
- [🔧 Function `lucide_name_for_category_icon`](#-function-lucide_name_for_category_icon)
- [🔧 Function `resolve_category_lucide_name`](#-function-resolve_category_lucide_name)
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

## 🔧 Function `category_lucide_color`

```python
def category_lucide_color(lucide_name: str) -> str
```

Return a stable chromatic stroke for category Lucide ID [`lucide_name`](../common/lucide_picker_dialog.g.md#%EF%B8%8F-method-lucide_name).

<details>
<summary>Code:</summary>

```python
def category_lucide_color(lucide_name: str) -> str:
    name = lucide_name.strip()
    if not name:
        return _CATEGORY_CYAN
    mapped = CATEGORY_LUCIDE_COLORS.get(name)
    if mapped is not None:
        return mapped
    digest = hashlib.sha256(name.encode("utf-8")).digest()
    return _CATEGORY_COLOR_PALETTE[digest[0] % len(_CATEGORY_COLOR_PALETTE)]
```

</details>

## 🔧 Function `category_lucide_icon`

```python
def category_lucide_icon(emoji: str = '', size: int = _CATEGORY_ICON_SIZE, *, lucide_name: str = '') -> QIcon
```

Return a colored Lucide `QIcon` for a category.

Prefers an explicit [`lucide_name`](../common/lucide_picker_dialog.g.md#%EF%B8%8F-method-lucide_name) override from `categories.icon_lucide`.
Otherwise resolves from the DB emoji via [`lucide_name_for_category_icon`](#-function-lucide_name_for_category_icon).

<details>
<summary>Code:</summary>

```python
def category_lucide_icon(
    emoji: str = "",
    size: int = _CATEGORY_ICON_SIZE,
    *,
    lucide_name: str = "",
) -> QIcon:
    name = resolve_category_lucide_name(emoji=emoji, lucide_name=lucide_name)
    if name is None:
        return QIcon()
    return create_lucide_icon(name, size, color=category_lucide_color(name))
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

## 🔧 Function `resolve_category_lucide_name`

```python
def resolve_category_lucide_name(*, emoji: str = '', lucide_name: str = '') -> str | None
```

Return the Lucide ID to paint for a category row.

<details>
<summary>Code:</summary>

```python
def resolve_category_lucide_name(*, emoji: str = "", lucide_name: str = "") -> str | None:
    override = lucide_name.strip()
    if override and lucide_svg_path(override) is not None:
        return override
    return lucide_name_for_category_icon(emoji)
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
