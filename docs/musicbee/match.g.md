---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `match.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `PathMatch`](#%EF%B8%8F-class-pathmatch)
- [🔧 Function `match_missing_path`](#-function-match_missing_path)

</details>

## 🏛️ Class `PathMatch`

```python
class PathMatch
```

Outcome of looking up a missing library or playlist path.

<details>
<summary>Code:</summary>

```python
class PathMatch:

    original: str
    status: str
    resolved: str | None = None
    candidates: tuple[str, ...] = ()
```

</details>

## 🔧 Function `match_missing_path`

```python
def match_missing_path(original: str, index: FileIndex, *, file_size: int | None = None) -> PathMatch
```

Map `original` to a unique file under the music index.

Status is `ok` (still present), `remap`, `ambiguous`, or `missing`.

<details>
<summary>Code:</summary>

```python
def match_missing_path(original: str, index: FileIndex, *, file_size: int | None = None) -> PathMatch:
    existing = index.existing_path(original)
    if existing is not None:
        resolved = str(existing)
        if normalize_path_key(resolved) == normalize_path_key(original):
            return PathMatch(original=original, status="ok", resolved=resolved)
        return PathMatch(original=original, status="remap", resolved=resolved)

    basename = Path(original).name.casefold()
    hits = list(index.by_basename.get(basename, ()))
    if file_size is not None and len(hits) != 1:
        sized = [item for item in hits if item.size == file_size]
        if sized:
            hits = sized
    return _from_hits(original, hits)
```

</details>
