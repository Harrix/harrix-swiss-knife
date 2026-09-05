"""Read and mutate Chromium `Bookmarks` JSON trees."""

from __future__ import annotations

import copy
import hashlib
import json
import time
import uuid
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pathlib import Path

ROOT_KEYS = ("bookmark_bar", "other", "synced")


@dataclass(frozen=True, slots=True)
class BookmarkEntry:
    """One URL bookmark with its folder path under a root."""

    url: str
    name: str
    root: str
    folder_path: tuple[str, ...]


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
        _walk(node, root_key, (), result)
    return result


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


def _walk(
    node: dict[str, Any],
    root: str,
    folder_path: tuple[str, ...],
    out: dict[str, BookmarkEntry],
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
            _walk(child, root, (*folder_path, label), out)
        else:
            _walk(child, root, folder_path, out)
