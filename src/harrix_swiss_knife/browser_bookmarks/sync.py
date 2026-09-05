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
    backup_path: Path | None = None
    browsers_running: list[str] = field(default_factory=list)

    @property
    def has_writes(self) -> bool:
        """Whether Apply would change either Bookmarks file."""
        return bool(self.add_to_chrome or self.add_to_yandex or self.delete_from_chrome or self.delete_from_yandex)


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
    add_entries(chrome_data, plan.add_to_chrome)
    add_entries(yandex_data, plan.add_to_yandex)

    write_bookmarks(plan.chrome_path, chrome_data)
    write_bookmarks(plan.yandex_path, yandex_data)

    final_urls = set(flatten_bookmarks(load_bookmarks(plan.chrome_path))) | set(
        flatten_bookmarks(load_bookmarks(plan.yandex_path))
    )
    # After sync both sides should share the same URL set; snapshot that union.
    save_snapshot(final_urls, plan.snapshot_file)

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
    """Read both Bookmarks files and the snapshot; compute adds/deletes."""
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
    previous = load_snapshot(snap)
    first_run = not previous

    add_to_chrome: list[BookmarkEntry] = []
    add_to_yandex: list[BookmarkEntry] = []
    delete_from_chrome: list[str] = []
    delete_from_yandex: list[str] = []

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
        browsers_running=running_browser_names(),
    )


def format_sync_report(plan: SyncPlan) -> str:
    """Build the preview text shown before Apply."""
    lines = [
        f"Chrome: {plan.chrome_path}",
        f"Yandex: {plan.yandex_path}",
        f"Snapshot: {plan.snapshot_file}",
        "",
    ]
    if plan.browsers_running:
        lines.append("Close these browsers before clicking Apply:")
        lines.extend(f"  - {name}" for name in plan.browsers_running)
        lines.append("")
    else:
        lines.append("Browsers appear closed.")
        lines.append("")

    if plan.first_run:
        lines.append("No previous sync snapshot — merge only, no deletions.")
        lines.append("")

    lines.append(f"Add to Chrome (from Yandex): {len(plan.add_to_chrome)}")
    lines.extend(_format_entry_lines(plan.add_to_chrome))
    lines.append("")
    lines.append(f"Add to Yandex (from Chrome): {len(plan.add_to_yandex)}")
    lines.extend(_format_entry_lines(plan.add_to_yandex))
    lines.append("")
    lines.append(f"Delete from Chrome: {len(plan.delete_from_chrome)}")
    lines.extend(_format_url_lines(plan.delete_from_chrome))
    lines.append("")
    lines.append(f"Delete from Yandex: {len(plan.delete_from_yandex)}")
    lines.extend(_format_url_lines(plan.delete_from_yandex))

    if not plan.has_writes:
        lines.append("")
        lines.append("Nothing to apply — bookmarks already match the sync rules.")
    else:
        lines.append("")
        lines.append("Click Apply to write both Bookmarks files and update the snapshot.")
        lines.append("Cancel closes without writing.")
    return "\n".join(lines)


def load_snapshot(path: Path | None = None) -> set[str]:
    """Load normalized URLs from the last successful sync snapshot."""
    snap = path if path is not None else snapshot_path()
    if not snap.is_file():
        return set()
    raw = json.loads(snap.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        return set()
    urls = raw.get("urls")
    if not isinstance(urls, list):
        return set()
    return {normalize_url(item) for item in urls if isinstance(item, str) and item.strip()}


def save_snapshot(urls: set[str], path: Path | None = None) -> Path:
    """Write the sync snapshot outside the Git repo."""
    snap = path if path is not None else snapshot_path()
    snap.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": 1,
        "updated_at": datetime.now(UTC).isoformat(),
        "urls": sorted(urls),
    }
    snap.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return snap


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
