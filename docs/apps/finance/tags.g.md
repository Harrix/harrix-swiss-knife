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
- [🔧 Function `matching_known_tags`](#-function-matching_known_tags)
- [🔧 Function `parse_tag_text`](#-function-parse_tag_text)
- [🔧 Function `tag_fragment_parts`](#-function-tag_fragment_parts)

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

## 🔧 Function `matching_known_tags`

```python
def matching_known_tags(known_tags: Sequence[str], query: str, *, exclude: Sequence[str] = ()) -> list[str]
```

Return known tags that contain `query` (case-insensitive), keeping DB order.

Args:

- `known_tags` (`Sequence[str]`): Candidate tag names, newest-first from the DB.
- `query` (`str`): Fragment typed after the last comma.
- `exclude` (`Sequence[str]`): Tags already chosen in the field; skipped.

Returns:

- `list[str]`: Matching names. Empty when `query` is blank.

<details>
<summary>Code:</summary>

```python
def matching_known_tags(
    known_tags: Sequence[str],
    query: str,
    *,
    exclude: Sequence[str] = (),
) -> list[str]:
    needle = " ".join(query.split()).casefold()
    if not needle:
        return []
    excluded = {name.casefold() for name in exclude if name.strip()}
    matches: list[str] = []
    seen: set[str] = set()
    for name in known_tags:
        key = name.casefold()
        if key in excluded or key in seen:
            continue
        if needle not in key:
            continue
        seen.add(key)
        matches.append(name)
    return matches
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

## 🔧 Function `tag_fragment_parts`

```python
def tag_fragment_parts(text: str) -> tuple[str, str]
```

Split a tags field into completed prefix and the fragment currently typed.

Args:

- `text` (`str`): Raw contents of the Tags line edit.

Returns:

- `tuple[str, str]`: `(prefix, fragment)` where `prefix` includes the trailing
  comma when present, and `fragment` is the text after that comma (or the whole
  field when there is no comma).

<details>
<summary>Code:</summary>

```python
def tag_fragment_parts(text: str) -> tuple[str, str]:
    if "," not in text:
        return "", text
    head, sep, tail = text.rpartition(",")
    return f"{head}{sep}", tail
```

</details>
