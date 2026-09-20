"""Compute and apply Chrome ↔ Yandex bookmark sync plans."""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from harrix_swiss_knife.browser_bookmarks.backup import create_bookmarks_backup
from harrix_swiss_knife.browser_bookmarks.model import (
    BookmarkEntry,
    ChildRef,
    add_entries,
    collect_folder_orders,
    flatten_bookmarks,
    folder_date_modified,
    load_bookmarks,
    normalize_url,
    relocate_entries,
    remove_urls,
    reorder_folder_children,
    write_bookmarks,
)
from harrix_swiss_knife.browser_bookmarks.paths import (
    default_chrome_bookmarks_path,
    default_yandex_bookmarks_path,
    running_browser_names,
    snapshot_path,
)

if TYPE_CHECKING:
    from pathlib import Path

_BULK_REVERT_MIN_SOURCES = 2
_BULK_REVERT_MIN_URLS = 5
_REPORT_LIST_LIMIT = 40
_SNAPSHOT_VERSION = 3


@dataclass(frozen=True, slots=True)
class FolderOrder:
    """Desired child order for one folder under a bookmark root."""

    root: str
    folder_path: tuple[str, ...]
    children: tuple[ChildRef, ...]


@dataclass(frozen=True, slots=True)
class SnapshotLocation:
    """Folder location of a URL bookmark under one browser root."""

    root: str
    folder_path: tuple[str, ...]
    name: str = ""


@dataclass
class SnapshotState:
    """Last successful sync: URL set plus per-browser folder locations."""

    urls: set[str] = field(default_factory=set)
    chrome_locations: dict[str, SnapshotLocation] = field(default_factory=dict)
    yandex_locations: dict[str, SnapshotLocation] = field(default_factory=dict)
    chrome_orders: dict[tuple[str, tuple[str, ...]], tuple[ChildRef, ...]] = field(default_factory=dict)
    yandex_orders: dict[tuple[str, tuple[str, ...]], tuple[ChildRef, ...]] = field(default_factory=dict)


@dataclass
class SyncPlan:
    """In-memory sync result ready to report or apply."""

    chrome_path: Path
    yandex_path: Path
    snapshot_file: Path
    first_run: bool
    chrome_data: dict[str, Any]
    yandex_data: dict[str, Any]
    add_to_chrome: list[BookmarkEntry] = field(default_factory=list)
    add_to_yandex: list[BookmarkEntry] = field(default_factory=list)
    delete_from_chrome: list[str] = field(default_factory=list)
    delete_from_yandex: list[str] = field(default_factory=list)
    move_in_chrome: list[BookmarkEntry] = field(default_factory=list)
    move_in_yandex: list[BookmarkEntry] = field(default_factory=list)
    reorder_in_chrome: list[FolderOrder] = field(default_factory=list)
    reorder_in_yandex: list[FolderOrder] = field(default_factory=list)
    backup_path: Path | None = None
    browsers_running: list[str] = field(default_factory=list)

    @property
    def has_writes(self) -> bool:
        """Whether Apply would change either Bookmarks file."""
        return bool(
            self.add_to_chrome
            or self.add_to_yandex
            or self.delete_from_chrome
            or self.delete_from_yandex
            or self.move_in_chrome
            or self.move_in_yandex
            or self.reorder_in_chrome
            or self.reorder_in_yandex
        )


def apply_sync_plan(plan: SyncPlan, *, create_backup: bool = True) -> list[Path]:
    """Backup, write both Bookmarks files, and refresh the snapshot."""
    running = running_browser_names()
    if running:
        msg = "Close Google Chrome and Yandex Browser before applying bookmark changes"
        raise OSError(msg)

    backup = create_bookmarks_backup(plan.chrome_path, plan.yandex_path) if create_backup else None
    plan.backup_path = backup

    chrome_data = plan.chrome_data
    yandex_data = plan.yandex_data
    remove_urls(chrome_data, set(plan.delete_from_chrome))
    remove_urls(yandex_data, set(plan.delete_from_yandex))
    relocate_entries(chrome_data, plan.move_in_chrome)
    relocate_entries(yandex_data, plan.move_in_yandex)
    add_entries(chrome_data, plan.add_to_chrome)
    add_entries(yandex_data, plan.add_to_yandex)
    for order in plan.reorder_in_chrome:
        reorder_folder_children(chrome_data, order.root, order.folder_path, order.children)
    for order in plan.reorder_in_yandex:
        reorder_folder_children(yandex_data, order.root, order.folder_path, order.children)

    write_bookmarks(plan.chrome_path, chrome_data)
    write_bookmarks(plan.yandex_path, yandex_data)

    persist_snapshot(plan)

    written = [plan.chrome_path, plan.yandex_path, plan.snapshot_file]
    if backup is not None:
        written.insert(0, backup)
    return written


def build_sync_plan(
    *,
    chrome_path: Path | None = None,
    yandex_path: Path | None = None,
    snapshot_file: Path | None = None,
) -> SyncPlan:
    """Read both Bookmarks files and the snapshot; compute adds/deletes/moves."""
    chrome = chrome_path if chrome_path is not None else default_chrome_bookmarks_path()
    yandex = yandex_path if yandex_path is not None else default_yandex_bookmarks_path()
    snap = snapshot_file if snapshot_file is not None else snapshot_path()
    if not chrome.is_file():
        msg = f"Chrome Bookmarks not found: {chrome}"
        raise FileNotFoundError(msg)
    if not yandex.is_file():
        msg = f"Yandex Bookmarks not found: {yandex}"
        raise FileNotFoundError(msg)

    chrome_data = load_bookmarks(chrome)
    yandex_data = load_bookmarks(yandex)
    chrome_map = flatten_bookmarks(chrome_data)
    yandex_map = flatten_bookmarks(yandex_data)
    chrome_urls = set(chrome_map)
    yandex_urls = set(yandex_map)
    state = load_snapshot_state(snap)
    previous = state.urls
    first_run = not previous

    add_to_chrome: list[BookmarkEntry] = []
    add_to_yandex: list[BookmarkEntry] = []
    delete_from_chrome: list[str] = []
    delete_from_yandex: list[str] = []
    move_in_chrome: list[BookmarkEntry] = []
    move_in_yandex: list[BookmarkEntry] = []
    deleted_either: set[str] = set()

    if first_run:
        add_to_yandex.extend(chrome_map[url] for url in sorted(chrome_urls - yandex_urls))
        add_to_chrome.extend(yandex_map[url] for url in sorted(yandex_urls - chrome_urls))
    else:
        chrome_deleted = previous - chrome_urls
        yandex_deleted = previous - yandex_urls
        chrome_added = chrome_urls - previous
        yandex_added = yandex_urls - previous

        # Delete wins: propagate deletions even if the other side still has the URL.
        delete_from_yandex.extend(url for url in sorted(chrome_deleted) if url in yandex_urls)
        delete_from_chrome.extend(url for url in sorted(yandex_deleted) if url in chrome_urls)

        deleted_either = chrome_deleted | yandex_deleted
        for url in sorted(chrome_added):
            if url in deleted_either:
                continue
            if url not in yandex_urls:
                add_to_yandex.append(chrome_map[url])
        for url in sorted(yandex_added):
            if url in deleted_either:
                continue
            if url not in chrome_urls:
                add_to_chrome.append(yandex_map[url])

    move_in_chrome, move_in_yandex = _plan_folder_moves(
        chrome_map,
        yandex_map,
        state,
        deleted_either,
    )
    reorder_in_chrome, reorder_in_yandex = _plan_folder_orders(chrome_data, yandex_data, state)

    return SyncPlan(
        chrome_path=chrome,
        yandex_path=yandex,
        snapshot_file=snap,
        first_run=first_run,
        chrome_data=chrome_data,
        yandex_data=yandex_data,
        add_to_chrome=add_to_chrome,
        add_to_yandex=add_to_yandex,
        delete_from_chrome=delete_from_chrome,
        delete_from_yandex=delete_from_yandex,
        move_in_chrome=move_in_chrome,
        move_in_yandex=move_in_yandex,
        reorder_in_chrome=reorder_in_chrome,
        reorder_in_yandex=reorder_in_yandex,
        browsers_running=running_browser_names(),
    )


def format_sync_report(plan: SyncPlan, *, applied: bool = False) -> str:
    """Build preview or post-apply report with a clear count summary first."""
    add_chrome = len(plan.add_to_chrome)
    add_yandex = len(plan.add_to_yandex)
    del_chrome = len(plan.delete_from_chrome)
    del_yandex = len(plan.delete_from_yandex)
    move_chrome = len(plan.move_in_chrome)
    move_yandex = len(plan.move_in_yandex)
    order_chrome = len(plan.reorder_in_chrome)
    order_yandex = len(plan.reorder_in_yandex)
    total = add_chrome + add_yandex + del_chrome + del_yandex + move_chrome + move_yandex + order_chrome + order_yandex

    if applied:
        lines = [
            "Status: applied",
            "",
            "Summary:",
            f"  Copied to Chrome (from Yandex): {add_chrome}",
            f"  Copied to Yandex (from Chrome): {add_yandex}",
            f"  Deleted from Chrome: {del_chrome}",
            f"  Deleted from Yandex: {del_yandex}",
            f"  Moved in Chrome: {move_chrome}",
            f"  Moved in Yandex: {move_yandex}",
            f"  Reordered in Chrome: {order_chrome}",
            f"  Reordered in Yandex: {order_yandex}",
            f"  Total bookmark changes: {total}",
            "",
        ]
        if plan.backup_path is not None:
            lines.append(f"Backup: {plan.backup_path}")
        lines.append(f"Snapshot updated: {plan.snapshot_file}")
        return "\n".join(lines)

    lines = [
        "Status: preview (not written yet)",
        "",
        "Summary:",
        f"  Will copy to Chrome (from Yandex): {add_chrome}",
        f"  Will copy to Yandex (from Chrome): {add_yandex}",
        f"  Will delete from Chrome: {del_chrome}",
        f"  Will delete from Yandex: {del_yandex}",
        f"  Will move in Chrome: {move_chrome}",
        f"  Will move in Yandex: {move_yandex}",
        f"  Will reorder in Chrome: {order_chrome}",
        f"  Will reorder in Yandex: {order_yandex}",
        f"  Total bookmark changes: {total}",
        "",
    ]
    if plan.first_run:
        lines.append("Mode: first sync — merge missing URLs, then align folders and order.")
    else:
        lines.append("Mode: sync additions, deletions, folder moves, and child order.")
    lines.append("")

    if plan.browsers_running:
        lines.append("Close before Apply: " + ", ".join(plan.browsers_running))
    else:
        lines.append("Browsers: appear closed.")
    lines.append("Leave both browsers closed until you confirm the new folders loaded.")
    lines.append("Browser account sync can put bookmarks back after Apply.")
    lines.append("")

    if add_chrome:
        lines.append(f"Copy to Chrome ({add_chrome}):")
        lines.extend(_format_entry_lines(plan.add_to_chrome))
        lines.append("")
    if add_yandex:
        lines.append(f"Copy to Yandex ({add_yandex}):")
        lines.extend(_format_entry_lines(plan.add_to_yandex))
        lines.append("")
    if del_chrome:
        lines.append(f"Delete from Chrome ({del_chrome}):")
        lines.extend(_format_url_lines(plan.delete_from_chrome))
        lines.append("")
    if del_yandex:
        lines.append(f"Delete from Yandex ({del_yandex}):")
        lines.extend(_format_url_lines(plan.delete_from_yandex))
        lines.append("")
    if move_chrome:
        lines.append(f"Move in Chrome ({move_chrome}):")
        lines.extend(_format_entry_lines(plan.move_in_chrome))
        lines.append("")
    if move_yandex:
        lines.append(f"Move in Yandex ({move_yandex}):")
        lines.extend(_format_entry_lines(plan.move_in_yandex))
        lines.append("")
    if order_chrome:
        lines.append(f"Reorder in Chrome ({order_chrome}):")
        lines.extend(_format_order_lines(plan.reorder_in_chrome))
        lines.append("")
    if order_yandex:
        lines.append(f"Reorder in Yandex ({order_yandex}):")
        lines.extend(_format_order_lines(plan.reorder_in_yandex))
        lines.append("")

    if not plan.has_writes:
        lines.append("Nothing to apply — bookmarks already match.")
    else:
        lines.append("Click Apply to write both Bookmarks files and update the snapshot.")
        lines.append("Cancel closes without writing.")
    return "\n".join(lines)


def load_snapshot(path: Path | None = None) -> set[str]:
    """Load normalized URLs from the last successful sync snapshot."""
    return load_snapshot_state(path).urls


def load_snapshot_state(path: Path | None = None) -> SnapshotState:
    """Load snapshot URLs, folder locations, and child orders (v1 — v3)."""
    snap = path if path is not None else snapshot_path()
    if not snap.is_file():
        return SnapshotState()
    raw = json.loads(snap.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        return SnapshotState()
    bookmarks = raw.get("bookmarks")
    if isinstance(bookmarks, dict):
        return _snapshot_state_from_v2(bookmarks, raw.get("orders"))
    urls_raw = raw.get("urls")
    if not isinstance(urls_raw, list):
        return SnapshotState()
    urls = {normalize_url(item) for item in urls_raw if isinstance(item, str) and item.strip()}
    return SnapshotState(urls=urls)


def persist_snapshot(plan: SyncPlan) -> Path:
    """Write a v3 snapshot from the current in-memory bookmark trees."""
    return save_snapshot(
        flatten_bookmarks(plan.chrome_data),
        flatten_bookmarks(plan.yandex_data),
        plan.snapshot_file,
        chrome_orders=collect_folder_orders(plan.chrome_data),
        yandex_orders=collect_folder_orders(plan.yandex_data),
    )


def save_snapshot(
    chrome_map: dict[str, BookmarkEntry],
    yandex_map: dict[str, BookmarkEntry],
    path: Path | None = None,
    *,
    chrome_orders: dict[tuple[str, tuple[str, ...]], list[ChildRef]] | None = None,
    yandex_orders: dict[tuple[str, tuple[str, ...]], list[ChildRef]] | None = None,
) -> Path:
    """Write the v3 sync snapshot with per-browser folder locations and orders."""
    snap = path if path is not None else snapshot_path()
    snap.parent.mkdir(parents=True, exist_ok=True)
    urls = set(chrome_map) | set(yandex_map)
    bookmarks: dict[str, dict[str, Any]] = {}
    for url in sorted(urls):
        sides: dict[str, Any] = {}
        if url in chrome_map:
            sides["chrome"] = _location_payload(chrome_map[url])
        if url in yandex_map:
            sides["yandex"] = _location_payload(yandex_map[url])
        bookmarks[url] = sides
    payload = {
        "version": _SNAPSHOT_VERSION,
        "updated_at": datetime.now(UTC).isoformat(),
        "bookmarks": bookmarks,
        "orders": {
            "chrome": _orders_payload(chrome_orders or {}),
            "yandex": _orders_payload(yandex_orders or {}),
        },
    }
    snap.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return snap


def save_url_snapshot(urls: set[str], path: Path | None = None) -> Path:
    """Write snapshot URL keys without folder locations (unknown-path state)."""
    snap = path if path is not None else snapshot_path()
    snap.parent.mkdir(parents=True, exist_ok=True)
    bookmarks = {url: {} for url in sorted(normalize_url(item) for item in urls if item.strip())}
    payload = {
        "version": _SNAPSHOT_VERSION,
        "updated_at": datetime.now(UTC).isoformat(),
        "bookmarks": bookmarks,
        "orders": {"chrome": [], "yandex": []},
    }
    snap.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return snap


def _chromium_timestamp(value: str) -> int:
    if value.isdigit():
        return int(value)
    return 0


def _format_entry_lines(entries: list[BookmarkEntry]) -> list[str]:
    lines: list[str] = []
    for entry in entries[:_REPORT_LIST_LIMIT]:
        folder = "/".join(entry.folder_path) if entry.folder_path else "(root)"
        title = entry.name or entry.url
        lines.append(f"  [{entry.root}/{folder}] {title}")
        lines.append(f"    {entry.url}")
    extra = len(entries) - _REPORT_LIST_LIMIT
    if extra > 0:
        lines.append(f"  … and {extra} more")
    return lines


def _format_order_lines(orders: list[FolderOrder]) -> list[str]:
    lines: list[str] = []
    for order in orders[:_REPORT_LIST_LIMIT]:
        folder = "/".join(order.folder_path) if order.folder_path else "(root)"
        lines.append(f"  [{order.root}/{folder}] {len(order.children)} child(ren)")
    extra = len(orders) - _REPORT_LIST_LIMIT
    if extra > 0:
        lines.append(f"  … and {extra} more")
    return lines


def _format_url_lines(urls: list[str]) -> list[str]:
    lines = [f"  {url}" for url in urls[:_REPORT_LIST_LIMIT]]
    extra = len(urls) - _REPORT_LIST_LIMIT
    if extra > 0:
        lines.append(f"  … and {extra} more")
    return lines


def _is_path_prefix(shorter: tuple[str, ...], longer: tuple[str, ...]) -> bool:
    return len(shorter) < len(longer) and longer[: len(shorter)] == shorter


def _location_key(entry: BookmarkEntry) -> tuple[str, tuple[str, ...]]:
    return (entry.root, entry.folder_path)


def _location_payload(entry: BookmarkEntry) -> dict[str, Any]:
    return {"root": entry.root, "folder_path": list(entry.folder_path), "name": entry.name}


def _order_winner(
    key: tuple[str, tuple[str, ...]],
    chrome_order: list[ChildRef],
    yandex_order: list[ChildRef],
    chrome_modified: str,
    yandex_modified: str,
    state: SnapshotState,
) -> str:
    snap_chrome = state.chrome_orders.get(key)
    snap_yandex = state.yandex_orders.get(key)
    chrome_changed = snap_chrome is not None and tuple(chrome_order) != snap_chrome
    yandex_changed = snap_yandex is not None and tuple(yandex_order) != snap_yandex
    if chrome_changed and not yandex_changed:
        return "chrome"
    if yandex_changed and not chrome_changed:
        return "yandex"
    if _chromium_timestamp(yandex_modified) > _chromium_timestamp(chrome_modified):
        return "yandex"
    return "chrome"


def _orders_payload(
    orders: dict[tuple[str, tuple[str, ...]], list[ChildRef]],
) -> list[dict[str, Any]]:
    payload: list[dict[str, Any]] = []
    for (root, folder_path), children in sorted(orders.items()):
        payload.append(
            {
                "root": root,
                "folder_path": list(folder_path),
                "children": [{"kind": child.kind, "value": child.value} for child in children],
            },
        )
    return payload


def _parse_child_ref(raw: Any) -> ChildRef | None:
    if not isinstance(raw, dict):
        return None
    kind = raw.get("kind")
    value = raw.get("value")
    if kind not in {"url", "folder"} or not isinstance(value, str):
        return None
    return ChildRef(kind, value)


def _parse_folder_order_list(raw: Any) -> dict[tuple[str, tuple[str, ...]], tuple[ChildRef, ...]]:
    if not isinstance(raw, list):
        return {}
    result: dict[tuple[str, tuple[str, ...]], tuple[ChildRef, ...]] = {}
    for item in raw:
        if not isinstance(item, dict):
            continue
        root = item.get("root")
        folder_path = item.get("folder_path")
        children_raw = item.get("children")
        if not isinstance(root, str) or not root.strip() or not isinstance(folder_path, list):
            continue
        parts: list[str] = []
        valid_path = True
        for part in folder_path:
            if not isinstance(part, str):
                valid_path = False
                break
            parts.append(part)
        if not valid_path or not isinstance(children_raw, list):
            continue
        children: list[ChildRef] = []
        for child_raw in children_raw:
            ref = _parse_child_ref(child_raw)
            if ref is not None:
                children.append(ref)
        result[(root, tuple(parts))] = tuple(children)
    return result


def _parse_orders(
    raw: Any,
) -> tuple[
    dict[tuple[str, tuple[str, ...]], tuple[ChildRef, ...]],
    dict[tuple[str, tuple[str, ...]], tuple[ChildRef, ...]],
]:
    if not isinstance(raw, dict):
        return {}, {}
    return _parse_folder_order_list(raw.get("chrome")), _parse_folder_order_list(raw.get("yandex"))


def _parse_snapshot_location(raw: Any) -> SnapshotLocation | None:
    if not isinstance(raw, dict):
        return None
    root = raw.get("root")
    folder_path = raw.get("folder_path")
    if not isinstance(root, str) or not root.strip():
        return None
    if not isinstance(folder_path, list):
        return None
    parts: list[str] = []
    for item in folder_path:
        if not isinstance(item, str):
            return None
        parts.append(item)
    name_raw = raw.get("name")
    name = name_raw if isinstance(name_raw, str) else ""
    return SnapshotLocation(root=root, folder_path=tuple(parts), name=name)


def _plan_folder_moves(
    chrome_map: dict[str, BookmarkEntry],
    yandex_map: dict[str, BookmarkEntry],
    state: SnapshotState,
    deleted_urls: set[str],
) -> tuple[list[BookmarkEntry], list[BookmarkEntry]]:
    pending: list[tuple[str, BookmarkEntry, BookmarkEntry, bool, bool]] = []
    yandex_only_dest_sources: dict[tuple[str, tuple[str, ...]], set[tuple[str, tuple[str, ...]]]] = defaultdict(set)
    chrome_only_dest_sources: dict[tuple[str, tuple[str, ...]], set[tuple[str, tuple[str, ...]]]] = defaultdict(set)
    yandex_only_dest_count: dict[tuple[str, tuple[str, ...]], int] = defaultdict(int)
    chrome_only_dest_count: dict[tuple[str, tuple[str, ...]], int] = defaultdict(int)
    for url in sorted(set(chrome_map) & set(yandex_map)):
        if url in deleted_urls:
            continue
        chrome_entry = chrome_map[url]
        yandex_entry = yandex_map[url]
        chrome_loc = _location_key(chrome_entry)
        yandex_loc = _location_key(yandex_entry)
        snap_chrome = state.chrome_locations.get(url)
        snap_yandex = state.yandex_locations.get(url)
        chrome_loc_changed = snap_chrome is not None and chrome_loc != _snapshot_location_key(snap_chrome)
        yandex_loc_changed = snap_yandex is not None and yandex_loc != _snapshot_location_key(snap_yandex)
        chrome_name_changed = bool(
            snap_chrome is not None and snap_chrome.name and chrome_entry.name != snap_chrome.name
        )
        yandex_name_changed = bool(
            snap_yandex is not None and snap_yandex.name and yandex_entry.name != snap_yandex.name
        )
        chrome_changed = chrome_loc_changed or chrome_name_changed
        yandex_changed = yandex_loc_changed or yandex_name_changed
        if chrome_loc == yandex_loc and chrome_entry.name == yandex_entry.name:
            continue
        pending.append((url, chrome_entry, yandex_entry, chrome_changed, yandex_changed))
        if yandex_loc_changed and not chrome_changed and snap_chrome is not None:
            yandex_only_dest_sources[yandex_loc].add(_snapshot_location_key(snap_chrome))
            yandex_only_dest_count[yandex_loc] += 1
        elif chrome_loc_changed and not yandex_changed and snap_yandex is not None:
            chrome_only_dest_sources[chrome_loc].add(_snapshot_location_key(snap_yandex))
            chrome_only_dest_count[chrome_loc] += 1

    yandex_bulk_revert = {
        dest
        for dest, sources in yandex_only_dest_sources.items()
        if len(sources) >= _BULK_REVERT_MIN_SOURCES and yandex_only_dest_count[dest] >= _BULK_REVERT_MIN_URLS
    }
    chrome_bulk_revert = {
        dest
        for dest, sources in chrome_only_dest_sources.items()
        if len(sources) >= _BULK_REVERT_MIN_SOURCES and chrome_only_dest_count[dest] >= _BULK_REVERT_MIN_URLS
    }

    move_in_chrome: list[BookmarkEntry] = []
    move_in_yandex: list[BookmarkEntry] = []
    for _url, chrome_entry, yandex_entry, chrome_changed, yandex_changed in pending:
        chrome_loc = _location_key(chrome_entry)
        yandex_loc = _location_key(yandex_entry)
        if chrome_changed and not yandex_changed:
            if chrome_loc in chrome_bulk_revert:
                move_in_chrome.append(yandex_entry)
            else:
                move_in_yandex.append(chrome_entry)
        elif yandex_changed and not chrome_changed:
            if yandex_loc in yandex_bulk_revert:
                move_in_yandex.append(chrome_entry)
            else:
                move_in_chrome.append(yandex_entry)
        elif chrome_changed and yandex_changed:
            if _prefer_yandex_timestamp(chrome_entry, yandex_entry):
                move_in_chrome.append(yandex_entry)
            else:
                move_in_yandex.append(chrome_entry)
        elif chrome_loc == yandex_loc and chrome_entry.name != yandex_entry.name:
            move_in_yandex.append(chrome_entry)
        elif _stale_divergence_winner(chrome_entry, yandex_entry) == "yandex":
            move_in_chrome.append(yandex_entry)
        else:
            move_in_yandex.append(chrome_entry)
    return move_in_chrome, move_in_yandex


def _plan_folder_orders(
    chrome_data: dict[str, Any],
    yandex_data: dict[str, Any],
    state: SnapshotState,
) -> tuple[list[FolderOrder], list[FolderOrder]]:
    chrome_orders = collect_folder_orders(chrome_data)
    yandex_orders = collect_folder_orders(yandex_data)
    reorder_in_chrome: list[FolderOrder] = []
    reorder_in_yandex: list[FolderOrder] = []
    for key in sorted(set(chrome_orders) & set(yandex_orders)):
        chrome_order = chrome_orders[key]
        yandex_order = yandex_orders[key]
        if chrome_order == yandex_order:
            continue
        winner = _order_winner(
            key,
            chrome_order,
            yandex_order,
            folder_date_modified(chrome_data, key[0], key[1]),
            folder_date_modified(yandex_data, key[0], key[1]),
            state,
        )
        desired = tuple(chrome_order if winner == "chrome" else yandex_order)
        folder_order = FolderOrder(root=key[0], folder_path=key[1], children=desired)
        if winner == "chrome":
            reorder_in_yandex.append(folder_order)
        else:
            reorder_in_chrome.append(folder_order)
    return reorder_in_chrome, reorder_in_yandex


def _prefer_yandex_timestamp(chrome_entry: BookmarkEntry, yandex_entry: BookmarkEntry) -> bool:
    return _chromium_timestamp(yandex_entry.date_modified) > _chromium_timestamp(chrome_entry.date_modified)


def _snapshot_location_key(location: SnapshotLocation) -> tuple[str, tuple[str, ...]]:
    return (location.root, location.folder_path)


def _snapshot_state_from_v2(bookmarks: dict[str, Any], orders_raw: Any = None) -> SnapshotState:
    urls: set[str] = set()
    chrome_locations: dict[str, SnapshotLocation] = {}
    yandex_locations: dict[str, SnapshotLocation] = {}
    for raw_url, raw_sides in bookmarks.items():
        if not isinstance(raw_url, str) or not raw_url.strip():
            continue
        url = normalize_url(raw_url)
        urls.add(url)
        if not isinstance(raw_sides, dict):
            continue
        chrome_loc = _parse_snapshot_location(raw_sides.get("chrome"))
        if chrome_loc is not None:
            chrome_locations[url] = chrome_loc
        yandex_loc = _parse_snapshot_location(raw_sides.get("yandex"))
        if yandex_loc is not None:
            yandex_locations[url] = yandex_loc
    chrome_orders, yandex_orders = _parse_orders(orders_raw)
    return SnapshotState(
        urls=urls,
        chrome_locations=chrome_locations,
        yandex_locations=yandex_locations,
        chrome_orders=chrome_orders,
        yandex_orders=yandex_orders,
    )


def _stale_divergence_winner(chrome_entry: BookmarkEntry, yandex_entry: BookmarkEntry) -> str:
    if chrome_entry.root == yandex_entry.root:
        if _is_path_prefix(yandex_entry.folder_path, chrome_entry.folder_path):
            return "chrome"
        if _is_path_prefix(chrome_entry.folder_path, yandex_entry.folder_path):
            return "yandex"
    if _prefer_yandex_timestamp(chrome_entry, yandex_entry):
        return "yandex"
    return "chrome"
