---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `text_case.py`

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
