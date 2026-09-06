"""Compute and apply Chrome ↔ Yandex bookmark sync plans."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from harrix_swiss_knife.browser_bookmarks.backup import create_bookmarks_backup
from harrix_swiss_knife.browser_bookmarks.model import (
    BookmarkEntry,
    add_entries,
    flatten_bookmarks,
    load_bookmarks,
    normalize_url,
    relocate_entries,
    remove_urls,
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

_REPORT_LIST_LIMIT = 40
_SNAPSHOT_VERSION = 2


@dataclass(frozen=True, slots=True)
class SnapshotLocation:
    """Folder location of a URL bookmark under one browser root."""

    root: str
    folder_path: tuple[str, ...]


@dataclass
class SnapshotState:
    """Last successful sync: URL set plus per-browser folder locations."""

    urls: set[str] = field(default_factory=set)
    chrome_locations: dict[str, SnapshotLocation] = field(default_factory=dict)
    yandex_locations: dict[str, SnapshotLocation] = field(default_factory=dict)


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
    total = add_chrome + add_yandex + del_chrome + del_yandex + move_chrome + move_yandex

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
        f"  Total bookmark changes: {total}",
        "",
    ]
    if plan.first_run:
        lines.append("Mode: first sync — merge only, no deletions.")
    else:
        lines.append("Mode: sync with additions, deletions, and folder moves (from snapshot).")
    lines.append("")

    if plan.browsers_running:
        lines.append("Close before Apply: " + ", ".join(plan.browsers_running))
    else:
        lines.append("Browsers: appear closed.")
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
    """Load snapshot URLs and per-browser folder locations (v1 or v2)."""
    snap = path if path is not None else snapshot_path()
    if not snap.is_file():
        return SnapshotState()
    raw = json.loads(snap.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        return SnapshotState()
    bookmarks = raw.get("bookmarks")
    if isinstance(bookmarks, dict):
        return _snapshot_state_from_v2(bookmarks)
    urls_raw = raw.get("urls")
    if not isinstance(urls_raw, list):
        return SnapshotState()
    urls = {normalize_url(item) for item in urls_raw if isinstance(item, str) and item.strip()}
    return SnapshotState(urls=urls)


def persist_snapshot(plan: SyncPlan) -> Path:
    """Write a v2 snapshot from the current in-memory bookmark trees."""
    return save_snapshot(
        flatten_bookmarks(plan.chrome_data),
        flatten_bookmarks(plan.yandex_data),
        plan.snapshot_file,
    )


def save_snapshot(
    chrome_map: dict[str, BookmarkEntry],
    yandex_map: dict[str, BookmarkEntry],
    path: Path | None = None,
) -> Path:
    """Write the v2 sync snapshot with per-browser folder locations."""
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


def _format_url_lines(urls: list[str]) -> list[str]:
    lines = [f"  {url}" for url in urls[:_REPORT_LIST_LIMIT]]
    extra = len(urls) - _REPORT_LIST_LIMIT
    if extra > 0:
        lines.append(f"  … and {extra} more")
    return lines


def _location_key(entry: BookmarkEntry) -> tuple[str, tuple[str, ...]]:
    return (entry.root, entry.folder_path)


def _location_payload(entry: BookmarkEntry) -> dict[str, Any]:
    return {"root": entry.root, "folder_path": list(entry.folder_path)}


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
    return SnapshotLocation(root=root, folder_path=tuple(parts))


def _plan_folder_moves(
    chrome_map: dict[str, BookmarkEntry],
    yandex_map: dict[str, BookmarkEntry],
    state: SnapshotState,
    deleted_urls: set[str],
) -> tuple[list[BookmarkEntry], list[BookmarkEntry]]:
    move_in_chrome: list[BookmarkEntry] = []
    move_in_yandex: list[BookmarkEntry] = []
    for url in sorted(set(chrome_map) & set(yandex_map)):
        if url in deleted_urls:
            continue
        chrome_entry = chrome_map[url]
        yandex_entry = yandex_map[url]
        chrome_loc = _location_key(chrome_entry)
        yandex_loc = _location_key(yandex_entry)
        if chrome_loc == yandex_loc:
            continue
        snap_chrome = state.chrome_locations.get(url)
        snap_yandex = state.yandex_locations.get(url)
        chrome_changed = snap_chrome is not None and chrome_loc != _snapshot_location_key(snap_chrome)
        yandex_changed = snap_yandex is not None and yandex_loc != _snapshot_location_key(snap_yandex)
        if chrome_changed and not yandex_changed:
            move_in_yandex.append(chrome_entry)
        elif yandex_changed and not chrome_changed:
            move_in_chrome.append(yandex_entry)
        elif chrome_changed and yandex_changed:
            if _chromium_timestamp(yandex_entry.date_modified) > _chromium_timestamp(chrome_entry.date_modified):
                move_in_chrome.append(yandex_entry)
            else:
                move_in_yandex.append(chrome_entry)
    return move_in_chrome, move_in_yandex


def _snapshot_location_key(location: SnapshotLocation) -> tuple[str, tuple[str, ...]]:
    return (location.root, location.folder_path)


def _snapshot_state_from_v2(bookmarks: dict[str, Any]) -> SnapshotState:
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
    return SnapshotState(urls=urls, chrome_locations=chrome_locations, yandex_locations=yandex_locations)
