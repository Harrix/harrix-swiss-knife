---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `tags.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `format_tag_text`](#-function-format_tag_text)
- [🔧 Function `parse_tag_text`](#-function-parse_tag_text)

</details>

## 🔧 Function `format_tag_text`

```python
def format_tag_text(names: list[str]) -> str
```

Join tag names for the transaction tag cell.

Args:

- `names` (`list[str]`): Tag names, possibly with duplicates or extra spaces.

Returns:

- `str`: Unique names sorted without case, separated by `", "`. Empty when
  there are no names.

<details>
<summary>Code:</summary>

```python
def format_tag_text(names: list[str]) -> str:
    return ", ".join(sorted(parse_tag_text(", ".join(names)), key=str.casefold))
```

</details>

## 🔧 Function `parse_tag_text`

```python
def parse_tag_text(text: str) -> list[str]
```

Split a tag field into unique names.

Names are separated by commas. Surrounding whitespace is removed and runs of
spaces inside a name are collapsed. Duplicate detection ignores case and keeps
the first spelling.

Args:

- `text` (`str`): Raw tag field, possibly empty.

Returns:

- `list[str]`: Tag names in first-seen order.

<details>
<summary>Code:</summary>

```python
def parse_tag_text(text: str) -> list[str]:
    seen: set[str] = set()
    names: list[str] = []
    for part in text.split(","):
        name = " ".join(part.split())
        if not name:
            continue
        key = name.casefold()
        if key in seen:
            continue
        seen.add(key)
        names.append(name)
    return names
```

</details>
