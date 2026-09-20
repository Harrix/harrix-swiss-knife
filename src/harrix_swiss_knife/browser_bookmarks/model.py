"""Read and mutate Chromium `Bookmarks` JSON trees."""

from __future__ import annotations

import copy
import hashlib
import json
import time
import uuid
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path

ROOT_KEYS = ("bookmark_bar", "other", "synced")


@dataclass(frozen=True, slots=True)
class BookmarkEntry:
    """One URL bookmark with its folder path under a root."""

    url: str
    name: str
    root: str
    folder_path: tuple[str, ...]
    date_modified: str = ""


@dataclass(frozen=True, slots=True)
class ChildRef:
    """One child of a bookmark folder: a URL or a named subfolder."""

    kind: Literal["url", "folder"]
    value: str


def add_entries(data: dict[str, Any], entries: list[BookmarkEntry]) -> int:
    """Insert missing URL bookmarks (create folders as needed). Return count added."""
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


def chromium_now() -> str:
    """Return Chromium `date_added` timestamp (microseconds since Windows epoch)."""
    # Windows epoch is 1601-01-01; Unix epoch offset is 11644473600 seconds.
    return str(int(time.time() * 1_000_000) + 11_644_473_600_000_000)


def collect_folder_orders(data: dict[str, Any]) -> dict[tuple[str, tuple[str, ...]], list[ChildRef]]:
    """Map each folder to its child URL/folder refs in display order."""
    roots = data.get("roots")
    if not isinstance(roots, dict):
        return {}
    result: dict[tuple[str, tuple[str, ...]], list[ChildRef]] = {}
    for root_key in ROOT_KEYS:
        node = roots.get(root_key)
        if isinstance(node, dict):
            _collect_folder_orders(node, root_key, (), result)
    return result


def find_folder(data: dict[str, Any], root: str, folder_path: tuple[str, ...]) -> dict[str, Any] | None:
    """Return the folder node at `root` / `folder_path`, or `None`."""
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


def flatten_bookmarks(data: dict[str, Any]) -> dict[str, BookmarkEntry]:
    """Map normalized URL → first occurrence in the tree."""
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


def folder_date_modified(data: dict[str, Any], root: str, folder_path: tuple[str, ...]) -> str:
    """Return Chromium `date_modified` for a folder, or `''` if missing."""
    folder = find_folder(data, root, folder_path)
    if folder is None:
        return ""
    return _node_date_modified(folder)


def load_bookmarks(path: Path) -> dict[str, Any]:
    """Load a Chromium Bookmarks JSON file."""
    text = path.read_text(encoding="utf-8")
    data = json.loads(text)
    if not isinstance(data, dict) or "roots" not in data:
        msg = f"Invalid Bookmarks file: {path}"
        raise ValueError(msg)
    return data


def normalize_url(url: str) -> str:
    """Return a comparison key for a bookmark URL."""
    return url.strip()


def relocate_entries(data: dict[str, Any], entries: list[BookmarkEntry]) -> int:
    """Move existing URL bookmarks and/or update their titles. Return count changed."""
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


def remove_urls(data: dict[str, Any], urls: set[str]) -> int:
    """Remove bookmark URL nodes whose normalized URL is in `urls`. Return count."""
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


def reorder_folder_children(
    data: dict[str, Any],
    root: str,
    folder_path: tuple[str, ...],
    desired: Sequence[ChildRef],
) -> bool:
    """Reorder a folder's children to match `desired`. Return whether the list changed.

    Children not mentioned in `desired` stay after the matched ones, in the same
    relative order. Unknown node types are kept with those leftovers.

    """
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


def write_bookmarks(path: Path, data: dict[str, Any]) -> None:
    """Write Bookmarks JSON with a refreshed checksum (atomic replace)."""
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


def _apply_url_title(data: dict[str, Any], url_key: str, name: str) -> bool:
    if not name:
        return False
    node = _find_url_node(data, url_key)
    if node is None:
        return False
    current = node.get("name")
    if isinstance(current, str) and current == name:
        return False
    node["name"] = name
    node["date_modified"] = chromium_now()
    return True


def _child_ref_of(node: dict[str, Any]) -> ChildRef | None:
    node_type = node.get("type")
    if node_type == "url":
        url = node.get("url")
        if isinstance(url, str) and url.strip():
            return ChildRef("url", normalize_url(url))
        return None
    if node_type == "folder":
        name = node.get("name")
        return ChildRef("folder", name if isinstance(name, str) else "")
    return None


def _collect_folder_orders(
    node: dict[str, Any],
    root: str,
    folder_path: tuple[str, ...],
    out: dict[tuple[str, tuple[str, ...]], list[ChildRef]],
) -> None:
    children = node.get("children")
    if not isinstance(children, list):
        return
    refs: list[ChildRef] = []
    for child in children:
        if not isinstance(child, dict):
            continue
        ref = _child_ref_of(child)
        if ref is not None:
            refs.append(ref)
    out[(root, folder_path)] = refs
    for child in children:
        if not isinstance(child, dict) or child.get("type") != "folder":
            continue
        name = child.get("name")
        label = name if isinstance(name, str) else ""
        _collect_folder_orders(child, root, (*folder_path, label), out)


def _ensure_folder(
    data: dict[str, Any],
    root: str,
    folder_path: tuple[str, ...],
    next_id_holder: list[int],
) -> dict[str, Any]:
    roots = data.setdefault("roots", {})
    if not isinstance(roots, dict):
        msg = "Bookmarks roots must be an object"
        raise TypeError(msg)
    root_key = root if root in ROOT_KEYS else "bookmark_bar"
    folder = roots.get(root_key)
    if not isinstance(folder, dict):
        folder = {
            "children": [],
            "id": str(next_id_holder[0]),
            "name": root_key,
            "type": "folder",
        }
        next_id_holder[0] += 1
        roots[root_key] = folder
    current = folder
    for part in folder_path:
        children = current.setdefault("children", [])
        if not isinstance(children, list):
            current["children"] = []
            children = current["children"]
        found: dict[str, Any] | None = None
        for child in children:
            if isinstance(child, dict) and child.get("type") == "folder" and child.get("name") == part:
                found = child
                break
        if found is None:
            found = {
                "children": [],
                "date_added": chromium_now(),
                "date_modified": chromium_now(),
                "guid": str(uuid.uuid4()),
                "id": str(next_id_holder[0]),
                "name": part,
                "type": "folder",
            }
            next_id_holder[0] += 1
            children.append(found)
        current = found
    return current


def _extract_url_from_children(folder: dict[str, Any], url_key: str) -> dict[str, Any] | None:
    children = folder.get("children")
    if not isinstance(children, list):
        return None
    kept: list[Any] = []
    extracted: dict[str, Any] | None = None
    for child in children:
        if extracted is not None:
            kept.append(child)
            continue
        if not isinstance(child, dict):
            kept.append(child)
            continue
        if child.get("type") == "url":
            url = child.get("url")
            if isinstance(url, str) and normalize_url(url) == url_key:
                extracted = child
                continue
            kept.append(child)
            continue
        if child.get("type") == "folder":
            found = _extract_url_from_children(child, url_key)
            if found is not None:
                extracted = found
            kept.append(child)
            continue
        kept.append(child)
    folder["children"] = kept
    return extracted


def _extract_url_node(data: dict[str, Any], url_key: str) -> dict[str, Any] | None:
    roots = data.get("roots")
    if not isinstance(roots, dict):
        return None
    for root_key in ROOT_KEYS:
        node = roots.get(root_key)
        if isinstance(node, dict):
            found = _extract_url_from_children(node, url_key)
            if found is not None:
                return found
    return None


def _find_url_in_node(node: dict[str, Any], url_key: str) -> dict[str, Any] | None:
    if node.get("type") == "url":
        url = node.get("url")
        if isinstance(url, str) and normalize_url(url) == url_key:
            return node
        return None
    children = node.get("children")
    if not isinstance(children, list):
        return None
    for child in children:
        if isinstance(child, dict):
            found = _find_url_in_node(child, url_key)
            if found is not None:
                return found
    return None


def _find_url_node(data: dict[str, Any], url_key: str) -> dict[str, Any] | None:
    roots = data.get("roots")
    if not isinstance(roots, dict):
        return None
    for root_key in ROOT_KEYS:
        node = roots.get(root_key)
        if isinstance(node, dict):
            found = _find_url_in_node(node, url_key)
            if found is not None:
                return found
    return None


def _max_id(data: dict[str, Any]) -> int:
    best = 0

    def visit(node: Any) -> None:
        nonlocal best
        if isinstance(node, dict):
            raw = node.get("id")
            if isinstance(raw, str) and raw.isdigit():
                best = max(best, int(raw))
            elif isinstance(raw, int):
                best = max(best, raw)
            for value in node.values():
                visit(value)
        elif isinstance(node, list):
            for item in node:
                visit(item)

    visit(data.get("roots"))
    return best


def _new_url_node(entry: BookmarkEntry, node_id: int) -> dict[str, Any]:
    return {
        "date_added": chromium_now(),
        "date_last_used": "0",
        "guid": str(uuid.uuid4()),
        "id": str(node_id),
        "name": entry.name or entry.url,
        "type": "url",
        "url": entry.url,
    }


def _newer_chromium_timestamp(first: str, second: str) -> str:
    first_n = int(first) if first.isdigit() else 0
    second_n = int(second) if second.isdigit() else 0
    if first_n >= second_n:
        return first or second
    return second or first


def _node_date_modified(node: dict[str, Any]) -> str:
    raw = node.get("date_modified")
    if isinstance(raw, int):
        return str(raw)
    if isinstance(raw, str) and raw.strip():
        return raw.strip()
    added = node.get("date_added")
    if isinstance(added, int):
        return str(added)
    if isinstance(added, str) and added.strip():
        return added.strip()
    return ""


def _remove_from_children(folder: dict[str, Any], urls: set[str]) -> int:
    children = folder.get("children")
    if not isinstance(children, list):
        return 0
    kept: list[Any] = []
    removed = 0
    for child in children:
        if not isinstance(child, dict):
            kept.append(child)
            continue
        if child.get("type") == "url":
            url = child.get("url")
            if isinstance(url, str) and normalize_url(url) in urls:
                removed += 1
                continue
            kept.append(child)
            continue
        if child.get("type") == "folder":
            removed += _remove_from_children(child, urls)
            kept.append(child)
            continue
        kept.append(child)
    folder["children"] = kept
    return removed


def _take_child_ref(unused: list[Any], ref: ChildRef) -> dict[str, Any] | None:
    for index, child in enumerate(unused):
        if not isinstance(child, dict):
            continue
        current = _child_ref_of(child)
        if current == ref:
            return unused.pop(index)
    return None


def _walk(
    node: dict[str, Any],
    root: str,
    folder_path: tuple[str, ...],
    out: dict[str, BookmarkEntry],
    parent_modified: str,
) -> None:
    node_type = node.get("type")
    if node_type == "url":
        url = node.get("url")
        if isinstance(url, str) and url.strip():
            key = normalize_url(url)
            if key not in out:
                name = node.get("name")
                out[key] = BookmarkEntry(
                    url=url.strip(),
                    name=name if isinstance(name, str) else "",
                    root=root,
                    folder_path=folder_path,
                    date_modified=_newer_chromium_timestamp(_node_date_modified(node), parent_modified),
                )
        return
    children = node.get("children")
    if not isinstance(children, list):
        return
    for child in children:
        if not isinstance(child, dict):
            continue
        if child.get("type") == "folder":
            child_name = child.get("name")
            label = child_name if isinstance(child_name, str) else ""
            _walk(child, root, (*folder_path, label), out, _node_date_modified(child))
        else:
            _walk(child, root, folder_path, out, parent_modified)
