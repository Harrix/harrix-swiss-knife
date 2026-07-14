---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `keyboard_layout_search.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `command_matches_search`](#-function-command_matches_search)
- [🔧 Function `normalize_command_title`](#-function-normalize_command_title)
- [🔧 Function `swap_keyboard_layout`](#-function-swap_keyboard_layout)

</details>

## 🔧 Function `command_matches_search`

```python
def command_matches_search(title: str, query: str) -> bool
```

Return True if query matches title, including EN/RU layout mistakes.

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
    text = title.strip()
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
