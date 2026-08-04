---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `keyboard_layout_search.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `autocomplete_match_tier`](#-function-autocomplete_match_tier)
- [🔧 Function `command_matches_search`](#-function-command_matches_search)
- [🔧 Function `normalize_command_title`](#-function-normalize_command_title)
- [🔧 Function `swap_keyboard_layout`](#-function-swap_keyboard_layout)
- [🔧 Function `text_matches_autocomplete`](#-function-text_matches_autocomplete)

</details>

## 🔧 Function `autocomplete_match_tier`

```python
def autocomplete_match_tier(text: str, query: str) -> int | None
```

Return best match tier for autocomplete, including EN/RU layout mistakes.

Tiers: `0` exact, `1` starts-with, `2` contains. Returns `None` if neither the
plain query nor its layout-swapped form matches `text`.

<details>
<summary>Code:</summary>

```python
def autocomplete_match_tier(text: str, query: str) -> int | None:
    text_fold = text.casefold()
    query_fold = query.casefold()
    swapped_fold = swap_keyboard_layout(query).casefold()

    best: int | None = None
    for needle in (query_fold, swapped_fold):
        if not needle:
            continue
        tier = _plain_autocomplete_tier(text_fold, needle)
        if tier is not None and (best is None or tier < best):
            best = tier
    return best
```

</details>

## 🔧 Function `command_matches_search`

```python
def command_matches_search(title: str, query: str) -> bool
```

Return `True` if query matches title, including EN/RU layout mistakes.

Empty query matches everything.

<details>
<summary>Code:</summary>

```python
def command_matches_search(title: str, query: str) -> bool:
    needle = query.strip()
    if not needle:
        return True

    haystack = normalize_command_title(title)
    needle_fold = needle.casefold()
    swapped_fold = swap_keyboard_layout(needle).casefold()
    return needle_fold in haystack or swapped_fold in haystack
```

</details>

## 🔧 Function `normalize_command_title`

```python
def normalize_command_title(title: str) -> str
```

Normalize a menu title for search comparison.

<details>
<summary>Code:</summary>

```python
def normalize_command_title(title: str) -> str:
    text = strip_md_inline_code_markers(title.strip())
    text = text.removeprefix(_BOLD_TITLE_PREFIX)
    if CLI_MENU_SUFFIX and text.endswith(CLI_MENU_SUFFIX):
        text = text[: -len(CLI_MENU_SUFFIX)]
    return text.strip().casefold()
```

</details>

## 🔧 Function `swap_keyboard_layout`

```python
def swap_keyboard_layout(text: str) -> str
```

Swap characters as if typed on the other EN/RU keyboard layout.

<details>
<summary>Code:</summary>

```python
def swap_keyboard_layout(text: str) -> str:
    return "".join(_LAYOUT_SWAP.get(char, char) for char in text)
```

</details>

## 🔧 Function `text_matches_autocomplete`

```python
def text_matches_autocomplete(text: str, query: str) -> bool
```

Return `True` if query matches text for autocomplete, including layout mistakes.

<details>
<summary>Code:</summary>

```python
def text_matches_autocomplete(text: str, query: str) -> bool:
    return autocomplete_match_tier(text, query) is not None
```

</details>
