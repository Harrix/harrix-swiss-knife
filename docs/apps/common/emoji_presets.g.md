---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `emoji_presets.py`

## 🔧 Function `unique_emojis`

```python
def unique_emojis(*groups: Iterable[str]) -> tuple[str, ...]
```

Return emojis in first-seen order across `groups`.

<details>
<summary>Code:</summary>

```python
def unique_emojis(*groups: Iterable[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    result: list[str] = []
    for group in groups:
        for emoji in group:
            value = str(emoji).strip()
            if not value or value in seen:
                continue
            seen.add(value)
            result.append(value)
    return tuple(result)
```

</details>
