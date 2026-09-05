"""Tests for Chrome ↔ Yandex bookmark sync."""

from __future__ import annotations

from pathlib import Path

import pytest

from harrix_swiss_knife.actions.common.quick_launcher_registry import iter_menu_structure
from harrix_swiss_knife.actions.files.sync_chrome_yandex_bookmarks import OnSyncChromeYandexBookmarks
from harrix_swiss_knife.browser_bookmarks.model import flatten_bookmarks, load_bookmarks, write_bookmarks
from harrix_swiss_knife.browser_bookmarks.sync import (
    apply_sync_plan,
    build_sync_plan,
    format_sync_report,
    load_snapshot,
    save_snapshot,
)
from harrix_swiss_knife.menu_structure import get_menu_structure


def _minimal_bookmarks(*urls: tuple[str, str]) -> dict:
    """Build a tiny Bookmarks tree: (name, url) on the bookmark bar."""
    children = [
        {
            "date_added": "1",
            "guid": f"00000000-0000-0000-0000-{index:012d}",
            "id": str(index + 1),
            "name": name,
            "type": "url",
            "url": url,
        }
        for index, (name, url) in enumerate(urls)
    ]
    return {
        "checksum": "",
        "roots": {
            "bookmark_bar": {
                "children": children,
                "id": "1",
                "name": "Bookmarks bar",
                "type": "folder",
            },
            "other": {"children": [], "id": "2", "name": "Other bookmarks", "type": "folder"},
            "synced": {"children": [], "id": "3", "name": "Mobile bookmarks", "type": "folder"},
        },
        "version": 1,
    }


def _write_pair(
    tmp_path: Path, chrome_urls: list[tuple[str, str]], yandex_urls: list[tuple[str, str]]
) -> tuple[Path, Path]:
    chrome = tmp_path / "chrome" / "Bookmarks"
    yandex = tmp_path / "yandex" / "Bookmarks"
    chrome.parent.mkdir(parents=True)
    yandex.parent.mkdir(parents=True)
    write_bookmarks(chrome, _minimal_bookmarks(*chrome_urls))
    write_bookmarks(yandex, _minimal_bookmarks(*yandex_urls))
    return chrome, yandex


def test_first_run_merge_only(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("harrix_swiss_knife.browser_bookmarks.sync.running_browser_names", list)
    chrome, yandex = _write_pair(
        tmp_path,
        [("A", "https://a.example/")],
        [("B", "https://b.example/")],
    )
    snap = tmp_path / "snap.json"
    plan = build_sync_plan(chrome_path=chrome, yandex_path=yandex, snapshot_file=snap)
    assert plan.first_run
    assert plan.delete_from_chrome == []
    assert plan.delete_from_yandex == []
    assert [item.url for item in plan.add_to_chrome] == ["https://b.example/"]
    assert [item.url for item in plan.add_to_yandex] == ["https://a.example/"]
    report = format_sync_report(plan)
    assert "merge only" in report.casefold()
    apply_sync_plan(plan, create_backup=False)
    chrome_urls = set(flatten_bookmarks(load_bookmarks(chrome)))
    yandex_urls = set(flatten_bookmarks(load_bookmarks(yandex)))
    assert chrome_urls == yandex_urls == {"https://a.example/", "https://b.example/"}
    assert load_snapshot(snap) == chrome_urls


def test_delete_propagates_from_snapshot(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("harrix_swiss_knife.browser_bookmarks.sync.running_browser_names", list)
    chrome, yandex = _write_pair(
        tmp_path,
        [("A", "https://a.example/"), ("Keep", "https://keep.example/")],
        [("A", "https://a.example/"), ("Keep", "https://keep.example/")],
    )
    snap = tmp_path / "snap.json"
    save_snapshot({"https://a.example/", "https://keep.example/", "https://gone.example/"}, snap)
    # Simulate delete of A in Chrome only.
    write_bookmarks(chrome, _minimal_bookmarks(("Keep", "https://keep.example/")))
    plan = build_sync_plan(chrome_path=chrome, yandex_path=yandex, snapshot_file=snap)
    assert not plan.first_run
    assert plan.delete_from_yandex == ["https://a.example/"]
    apply_sync_plan(plan, create_backup=False)
    assert "https://a.example/" not in flatten_bookmarks(load_bookmarks(yandex))
    assert "https://keep.example/" in flatten_bookmarks(load_bookmarks(chrome))
    assert "https://a.example/" not in load_snapshot(snap)


def test_delete_wins_over_other_side(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("harrix_swiss_knife.browser_bookmarks.sync.running_browser_names", list)
    chrome, yandex = _write_pair(
        tmp_path,
        [],
        [("Renamed", "https://x.example/")],
    )
    snap = tmp_path / "snap.json"
    save_snapshot({"https://x.example/"}, snap)
    plan = build_sync_plan(chrome_path=chrome, yandex_path=yandex, snapshot_file=snap)
    assert plan.delete_from_yandex == ["https://x.example/"]
    assert plan.add_to_chrome == []
    apply_sync_plan(plan, create_backup=False)
    assert flatten_bookmarks(load_bookmarks(yandex)) == {}
    assert flatten_bookmarks(load_bookmarks(chrome)) == {}


def test_cancel_does_not_update_snapshot(tmp_path: Path) -> None:
    chrome, yandex = _write_pair(
        tmp_path,
        [("A", "https://a.example/")],
        [],
    )
    snap = tmp_path / "snap.json"
    plan = build_sync_plan(chrome_path=chrome, yandex_path=yandex, snapshot_file=snap)
    assert plan.has_writes
    assert not snap.exists()
    # Cancel path: do not call apply_sync_plan.
    assert load_snapshot(snap) == set()


def test_apply_refuses_when_browsers_running(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "harrix_swiss_knife.browser_bookmarks.sync.running_browser_names",
        lambda: ["Google Chrome"],
    )
    chrome, yandex = _write_pair(tmp_path, [("A", "https://a.example/")], [])
    snap = tmp_path / "snap.json"
    plan = build_sync_plan(chrome_path=chrome, yandex_path=yandex, snapshot_file=snap)
    with pytest.raises(OSError, match="Close Google Chrome"):
        apply_sync_plan(plan, create_backup=False)


def test_action_in_file_operations_menu() -> None:
    assert OnSyncChromeYandexBookmarks.title == "Sync Chrome and Yandex bookmarks"
    assert OnSyncChromeYandexBookmarks in list(iter_menu_structure(get_menu_structure()))
