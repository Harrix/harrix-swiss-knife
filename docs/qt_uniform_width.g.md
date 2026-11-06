---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `qt_uniform_width.py`

## 🔧 Function `resolve_uniform_item_width`

```python
def resolve_uniform_item_width(available_width: int, *, spacing: int, base_width: int, min_scale: float = 0.82) -> int
```

Return item width so full rows fill `available_width` with a shared column size.

Column count comes only from `available_width` (how many `base_width` items fit,
optionally one more when the squeeze is still at least `min_scale`). Incomplete
last rows keep that width and leave a trailing gap.

<details>
<summary>Code:</summary>

```python
def resolve_uniform_item_width(
    available_width: int,
    *,
    spacing: int,
    base_width: int,
    min_scale: float = 0.82,
) -> int:
    if available_width <= 0 or base_width <= 0:
        return max(1, base_width)
    columns = max(1, (available_width + spacing) // (base_width + spacing))
    extra = columns + 1
    width_for_extra = (available_width - (extra - 1) * spacing) // extra
    if width_for_extra / base_width >= min_scale:
        columns = extra
    return max(1, (available_width - (columns - 1) * spacing) // columns)
```

</details>
