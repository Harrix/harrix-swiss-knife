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
- [🏛️ Class `ChildRef`](#%EF%B8%8F-class-childref)
- [🔧 Function `add_entries`](#-function-add_entries)
- [🔧 Function `chromium_now`](#-function-chromium_now)
- [🔧 Function `collect_folder_orders`](#-function-collect_folder_orders)
- [🔧 Function `find_folder`](#-function-find_folder)
- [🔧 Function `flatten_bookmarks`](#-function-flatten_bookmarks)
- [🔧 Function `folder_date_modified`](#-function-folder_date_modified)
- [🔧 Function `load_bookmarks`](#-function-load_bookmarks)
- [🔧 Function `normalize_url`](#-function-normalize_url)
- [🔧 Function `relocate_entries`](#-function-relocate_entries)
- [🔧 Function `remove_urls`](#-function-remove_urls)
- [🔧 Function `reorder_folder_children`](#-function-reorder_folder_children)
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
    date_modified: str = ""
```

</details>

## 🏛️ Class `ChildRef`

```python
class ChildRef
```

One child of a bookmark folder: a URL or a named subfolder.

<details>
<summary>Code:</summary>

```python
class ChildRef:

    kind: Literal["url", "folder"]
    value: str
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

## 🔧 Function `collect_folder_orders`

```python
def collect_folder_orders(data: dict[str, Any]) -> dict[tuple[str, tuple[str, ...]], list[ChildRef]]
```

Map each folder to its child URL/folder refs in display order.

<details>
<summary>Code:</summary>

```python
def collect_folder_orders(data: dict[str, Any]) -> dict[tuple[str, tuple[str, ...]], list[ChildRef]]:
    roots = data.get("roots")
    if not isinstance(roots, dict):
        return {}
    result: dict[tuple[str, tuple[str, ...]], list[ChildRef]] = {}
    for root_key in ROOT_KEYS:
        node = roots.get(root_key)
        if isinstance(node, dict):
            _collect_folder_orders(node, root_key, (), result)
    return result
```

</details>

## 🔧 Function `find_folder`

```python
def find_folder(data: dict[str, Any], root: str, folder_path: tuple[str, ...]) -> dict[str, Any] | None
```

Return the folder node at [`root`](../apps/habits/habit_comments.g.md#%EF%B8%8F-method-root) / `folder_path`, or `None`.

<details>
<summary>Code:</summary>

```python
def find_folder(data: dict[str, Any], root: str, folder_path: tuple[str, ...]) -> dict[str, Any] | None:
    roots = data.get("roots")
    if not isinstance(roots, dict):
        return None
    current = roots.get(root if root in ROOT_KEYS else "bookmark_bar")
    if not isinstance(current, dict):
        return None
    for part in folder_path:
        children = current.get("children")
        if not isinstance(children, list):
            return None
        found: dict[str, Any] | None = None
        for child in children:
            if isinstance(child, dict) and child.get("type") == "folder" and child.get("name") == part:
                found = child
                break
        if found is None:
            return None
        current = found
    return current
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
        _walk(node, root_key, (), result, _node_date_modified(node))
    return result
```

</details>

## 🔧 Function `folder_date_modified`

```python
def folder_date_modified(data: dict[str, Any], root: str, folder_path: tuple[str, ...]) -> str
```

Return Chromium `date_modified` for a folder, or `''` if missing.

<details>
<summary>Code:</summary>

```python
def folder_date_modified(data: dict[str, Any], root: str, folder_path: tuple[str, ...]) -> str:
    folder = find_folder(data, root, folder_path)
    if folder is None:
        return ""
    return _node_date_modified(folder)
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

## 🔧 Function `relocate_entries`

```python
def relocate_entries(data: dict[str, Any], entries: list[BookmarkEntry]) -> int
```

Move existing URL bookmarks and/or update their titles. Return count changed.

<details>
<summary>Code:</summary>

```python
def relocate_entries(data: dict[str, Any], entries: list[BookmarkEntry]) -> int:
    if not entries:
        return 0
    existing = flatten_bookmarks(data)
    next_id_holder = [_max_id(data) + 1]
    moved = 0
    for entry in entries:
        key = normalize_url(entry.url)
        if not key:
            continue
        current = existing.get(key)
        if current is None:
            continue
        if current.root == entry.root and current.folder_path == entry.folder_path:
            if _apply_url_title(data, key, entry.name):
                moved += 1
            continue
        node = _extract_url_node(data, key)
        if node is None:
            continue
        if entry.name:
            node["name"] = entry.name
        node["date_modified"] = chromium_now()
        folder = _ensure_folder(data, entry.root, entry.folder_path, next_id_holder)
        children = folder.setdefault("children", [])
        if not isinstance(children, list):
            folder["children"] = []
            children = folder["children"]
        children.append(node)
        existing[key] = entry
        moved += 1
    return moved
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

## 🔧 Function `reorder_folder_children`

```python
def reorder_folder_children(data: dict[str, Any], root: str, folder_path: tuple[str, ...], desired: Sequence[ChildRef]) -> bool
```

Reorder a folder's children to match `desired`. Return whether the list changed.

Children not mentioned in `desired` stay after the matched ones, in the same
relative order. Unknown node types are kept with those leftovers.

<details>
<summary>Code:</summary>

```python
def reorder_folder_children(
    data: dict[str, Any],
    root: str,
    folder_path: tuple[str, ...],
    desired: Sequence[ChildRef],
) -> bool:
    folder = find_folder(data, root, folder_path)
    if folder is None:
        return False
    children = folder.get("children")
    if not isinstance(children, list):
        return False
    unused = list(children)
    new_children: list[Any] = []
    for ref in desired:
        match = _take_child_ref(unused, ref)
        if match is not None:
            new_children.append(match)
    new_children.extend(unused)
    if new_children == children:
        return False
    folder["children"] = new_children
    folder["date_modified"] = chromium_now()
    return True
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
