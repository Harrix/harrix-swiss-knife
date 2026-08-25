---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `sort.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `dash_length_rank`](#-function-dash_length_rank)
- [🔧 Function `pin_dash_symbols_first`](#-function-pin_dash_symbols_first)
- [🔧 Function `sort_items`](#-function-sort_items)

</details>

## 🔧 Function `dash_length_rank`

```python
def dash_length_rank(value: str) -> int | None
```

Return an increasing length rank for a hyphen or dash, or `None`.

<details>
<summary>Code:</summary>

```python
def dash_length_rank(value: str) -> int | None:
    return _DASH_LENGTH_RANK.get(value.strip())
```

</details>

## 🔧 Function `pin_dash_symbols_first`

```python
def pin_dash_symbols_first(items: Sequence[SnippetItem]) -> list[SnippetItem]
```

Keep hyphens and dashes first, together, from shortest to longest.

<details>
<summary>Code:</summary>

```python
def pin_dash_symbols_first(items: Sequence[SnippetItem]) -> list[SnippetItem]:
    dashes: list[tuple[int, SnippetItem]] = []
    rest: list[SnippetItem] = []
    for item in items:
        rank = dash_length_rank(item.value)
        if rank is None:
            rest.append(item)
        else:
            dashes.append((rank, item))
    dashes.sort(key=lambda pair: pair[0])
    return [item for _rank, item in dashes] + rest
```

</details>

## 🔧 Function `sort_items`

```python
def sort_items(items: Sequence[SnippetItem], mode: str, *, descending: bool) -> list[SnippetItem]
```

Return items ordered by last use, date added, or alphabet.

Last-use order puts unused items at the end alphabetically. `descending`
reverses the default direction of the active mode. Symbol hyphens and
dashes stay first, grouped by increasing length.

<details>
<summary>Code:</summary>

```python
def sort_items(items: Sequence[SnippetItem], mode: str, *, descending: bool) -> list[SnippetItem]:
    if mode == SORT_USED:
        used = [item for item in items if item.last_used_at]
        unused = [item for item in items if not item.last_used_at]
        used_sorted = sorted(used, key=lambda item: item.last_used_at or "", reverse=not descending)
        unused_sorted = sorted(unused, key=lambda item: item.value.casefold())
        ordered = used_sorted + unused_sorted
    elif mode == SORT_ADDED:
        ordered = sorted(items, key=lambda item: (item.created_at, item.item_id), reverse=not descending)
    else:
        ordered = sorted(items, key=lambda item: item.value.casefold(), reverse=descending)
    if any(item.zone == ZONE_SYMBOL for item in ordered):
        return pin_dash_symbols_first(ordered)
    return ordered
```

</details>
