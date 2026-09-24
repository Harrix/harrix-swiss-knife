---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `text_case.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `capitalize_first_letter`](#-function-capitalize_first_letter)
- [🔧 Function `edited_source_text_differs`](#-function-edited_source_text_differs)

</details>

## 🔧 Function `capitalize_first_letter`

```python
def capitalize_first_letter(text: str) -> str
```

Uppercase the first letter, skipping leading quotes and emoji.

Args:

- `text` (`str`): Value from a food name or finance description field.

Returns:

- `str`: Stripped text with the first alphabetic character uppercased.

<details>
<summary>Code:</summary>

```python
def capitalize_first_letter(text: str) -> str:
    cleaned = text.strip()
    for index, char in enumerate(cleaned):
        if not char.isalpha():
            continue
        upper = char.upper()
        if upper == char:
            return cleaned
        return f"{cleaned[:index]}{upper}{cleaned[index + 1 :]}"
    return cleaned
```

</details>

## 🔧 Function `edited_source_text_differs`

```python
def edited_source_text_differs(stored: str, edited: str) -> bool
```

Return whether a manual edit changed source text enough to drop its translation.

Comparison ignores surrounding whitespace and letter case, so saving the same
words again does not clear an existing English field.

Args:

- `stored` (`str`): Value currently saved in the database.
- `edited` (`str`): Value about to be saved from the table cell.

Returns:

- `bool`: `True` when the English translation for this row should be cleared.

<details>
<summary>Code:</summary>

```python
def edited_source_text_differs(stored: str, edited: str) -> bool:
    return stored.strip().casefold() != edited.strip().casefold()
```

</details>
