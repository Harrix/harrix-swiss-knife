---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `model.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `BookmarkEntry`](#%EF%B8%8F-class-bookmarkentry)
- [🔧 Function `add_entries`](#-function-add_entries)
- [🔧 Function `chromium_now`](#-function-chromium_now)
- [🔧 Function `flatten_bookmarks`](#-function-flatten_bookmarks)
- [🔧 Function `load_bookmarks`](#-function-load_bookmarks)
- [🔧 Function `normalize_url`](#-function-normalize_url)
- [🔧 Function `remove_urls`](#-function-remove_urls)
- [🔧 Function `write_bookmarks`](#-function-write_bookmarks)

</details>

## 🏛️ Class `BookmarkEntry`

```python
class BookmarkEntry
```

One URL bookmark with its folder path under a root.

<details>
<summary>Code:</summary>

```python
class BookmarkEntry:

    url: str
    name: str
    root: str
    folder_path: tuple[str, ...]
```

</details>

## 🔧 Function `add_entries`

```python
def add_entries(data: dict[str, Any], entries: list[BookmarkEntry]) -> int
```

Insert missing URL bookmarks (create folders as needed). Return count added.

<details>
<summary>Code:</summary>

```python
def add_entries(data: dict[str, Any], entries: list[BookmarkEntry]) -> int:
    if not entries:
        return 0
    existing = flatten_bookmarks(data)
    next_id_holder = [_max_id(data) + 1]
    added = 0
    for entry in entries:
        key = normalize_url(entry.url)
        if not key or key in existing:
            continue
        folder = _ensure_folder(data, entry.root, entry.folder_path, next_id_holder)
        children = folder.setdefault("children", [])
        if not isinstance(children, list):
            folder["children"] = []
            children = folder["children"]
        children.append(_new_url_node(entry, next_id_holder[0]))
        next_id_holder[0] += 1
        existing[key] = entry
        added += 1
    return added
```

</details>

## 🔧 Function `chromium_now`

```python
def chromium_now() -> str
```

Return Chromium `date_added` timestamp (microseconds since Windows epoch).

<details>
<summary>Code:</summary>

```python
def chromium_now() -> str:
    # Windows epoch is 1601-01-01; Unix epoch offset is 11644473600 seconds.
    return str(int(time.time() * 1_000_000) + 11_644_473_600_000_000)
```

</details>

## 🔧 Function `flatten_bookmarks`

```python
def flatten_bookmarks(data: dict[str, Any]) -> dict[str, BookmarkEntry]
```

Map normalized URL → first occurrence in the tree.

<details>
<summary>Code:</summary>

```python
def flatten_bookmarks(data: dict[str, Any]) -> dict[str, BookmarkEntry]:
    roots = data.get("roots")
    if not isinstance(roots, dict):
        return {}
    result: dict[str, BookmarkEntry] = {}
    for root_key in ROOT_KEYS:
        node = roots.get(root_key)
        if not isinstance(node, dict):
            continue
        _walk(node, root_key, (), result)
    return result
```

</details>

## 🔧 Function `load_bookmarks`

```python
def load_bookmarks(path: Path) -> dict[str, Any]
```

Load a Chromium Bookmarks JSON file.

<details>
<summary>Code:</summary>

```python
def load_bookmarks(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    data = json.loads(text)
    if not isinstance(data, dict) or "roots" not in data:
        msg = f"Invalid Bookmarks file: {path}"
        raise ValueError(msg)
    return data
```

</details>

## 🔧 Function `normalize_url`

```python
def normalize_url(url: str) -> str
```

Return a comparison key for a bookmark URL.

<details>
<summary>Code:</summary>

```python
def normalize_url(url: str) -> str:
    return url.strip()
```

</details>

## 🔧 Function `remove_urls`

```python
def remove_urls(data: dict[str, Any], urls: set[str]) -> int
```

Remove bookmark URL nodes whose normalized URL is in `urls`. Return count.

<details>
<summary>Code:</summary>

```python
def remove_urls(data: dict[str, Any], urls: set[str]) -> int:
    if not urls:
        return 0
    roots = data.get("roots")
    if not isinstance(roots, dict):
        return 0
    removed = 0
    for root_key in ROOT_KEYS:
        node = roots.get(root_key)
        if isinstance(node, dict):
            removed += _remove_from_children(node, urls)
    return removed
```

</details>

## 🔧 Function `write_bookmarks`

```python
def write_bookmarks(path: Path, data: dict[str, Any]) -> None
```

Write Bookmarks JSON with a refreshed checksum (atomic replace).

<details>
<summary>Code:</summary>

```python
def write_bookmarks(path: Path, data: dict[str, Any]) -> None:
    payload = copy.deepcopy(data)
    payload["checksum"] = ""
    body = json.dumps(payload, ensure_ascii=False, indent=3)
    # Chromium historically used MD5 over the file with an empty checksum field.
    checksum = hashlib.md5(body.encode("utf-8"), usedforsecurity=False).hexdigest()
    payload["checksum"] = checksum
    text = json.dumps(payload, ensure_ascii=False, indent=3) + "\n"
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)
```

</details>
