"""Tests for Chrome ↔ Yandex bookmark sync."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from harrix_swiss_knife.actions.common.quick_launcher_registry import iter_menu_structure
from harrix_swiss_knife.actions.files.sync_chrome_yandex_bookmarks import OnSyncChromeYandexBookmarks
from harrix_swiss_knife.browser_bookmarks.model import (
    BookmarkEntry,
    flatten_bookmarks,
    load_bookmarks,
    write_bookmarks,
)
from harrix_swiss_knife.browser_bookmarks.sync import (
    apply_sync_plan,
    build_sync_plan,
    format_sync_report,
    load_snapshot,
    load_snapshot_state,
    save_snapshot,
    save_url_snapshot,
)
from harrix_swiss_knife.menu_structure import get_menu_structure

_URL_A = "https://a.example/"
_URL_KEEP = "https://keep.example/"
_URL_X = "https://x.example/"


def _empty_bookmarks() -> dict[str, Any]:
    return {
        "checksum": "",
        "roots": {
            "bookmark_bar": {
                "children": [],
                "id": "1",
                "name": "Bookmarks bar",
                "type": "folder",
            },
            "other": {"children": [], "id": "2", "name": "Other bookmarks", "type": "folder"},
            "synced": {"children": [], "id": "3", "name": "Mobile bookmarks", "type": "folder"},
        },
        "version": 1,
    }


def _find_url_node(data: dict[str, Any], url: str) -> dict[str, Any] | None:
    roots = data.get("roots")
    if not isinstance(roots, dict):
        return None

    def walk(node: Any) -> dict[str, Any] | None:
        if not isinstance(node, dict):
            return None
        if node.get("type") == "url" and node.get("url") == url:
            return node
        children = node.get("children")
        if not isinstance(children, list):
            return None
        for child in children:
            found = walk(child)
            if found is not None:
                return found
        return None

    for root in roots.values():
        found = walk(root)
        if found is not None:
            return found
    return None


def _folder_node(name: str, children: list[dict[str, Any]], *, node_id: str) -> dict[str, Any]:
    return {
        "children": children,
        "date_added": "1",
        "date_modified": "1",
        "guid": f"00000000-0000-0000-0000-{int(node_id):012d}",
        "id": node_id,
        "name": name,
        "type": "folder",
    }


def _minimal_bookmarks(*urls: tuple[str, str]) -> dict[str, Any]:
    """Build a tiny Bookmarks tree: (name, url) on the bookmark bar."""
    data = _empty_bookmarks()
    data["roots"]["bookmark_bar"]["children"] = [
        _url_node(name, url, node_id=str(index + 10)) for index, (name, url) in enumerate(urls)
    ]
    return data


def _tree_with_url(
    name: str,
    url: str,
    folder_path: tuple[str, ...],
    *,
    date_modified: str = "1",
    root: str = "bookmark_bar",
) -> dict[str, Any]:
    data = _empty_bookmarks()
    node = _url_node(name, url, node_id="20", date_modified=date_modified)
    current_children = data["roots"][root]["children"]
    for index, part in enumerate(folder_path):
        folder = _folder_node(part, [], node_id=str(30 + index))
        current_children.append(folder)
        current_children = folder["children"]
    current_children.append(node)
    return data


def _url_node(name: str, url: str, *, node_id: str, date_modified: str = "1") -> dict[str, Any]:
    return {
        "date_added": "1",
        "date_modified": date_modified,
        "guid": f"00000000-0000-0000-0000-{int(node_id):012d}",
        "id": node_id,
        "name": name,
        "type": "url",
        "url": url,
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


def _write_trees(tmp_path: Path, chrome_data: dict[str, Any], yandex_data: dict[str, Any]) -> tuple[Path, Path]:
    chrome = tmp_path / "chrome" / "Bookmarks"
    yandex = tmp_path / "yandex" / "Bookmarks"
    chrome.parent.mkdir(parents=True, exist_ok=True)
    yandex.parent.mkdir(parents=True, exist_ok=True)
    write_bookmarks(chrome, chrome_data)
    write_bookmarks(yandex, yandex_data)
    return chrome, yandex


def _write_v1_snapshot(path: Path, urls: set[str]) -> None:
    payload = {
        "version": 1,
        "updated_at": "2026-01-01T00:00:00+00:00",
        "urls": sorted(urls),
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def test_first_run_merge_only(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("harrix_swiss_knife.browser_bookmarks.sync.running_browser_names", list)
    chrome, yandex = _write_pair(
        tmp_path,
        [("A", _URL_A)],
        [("B", "https://b.example/")],
    )
    snap = tmp_path / "snap.json"
    plan = build_sync_plan(chrome_path=chrome, yandex_path=yandex, snapshot_file=snap)
    assert plan.first_run
    assert plan.delete_from_chrome == []
    assert plan.delete_from_yandex == []
    assert [item.url for item in plan.add_to_chrome] == ["https://b.example/"]
    assert [item.url for item in plan.add_to_yandex] == [_URL_A]
    report = format_sync_report(plan)
    assert "merge only" in report.casefold()
    assert "Status: preview" in report
    assert "Total bookmark changes:" in report
    apply_sync_plan(plan, create_backup=False)
    done = format_sync_report(plan, applied=True)
    assert "Status: applied" in done
    assert "Copied to Chrome" in done
    assert "Moved in Chrome" in done
    assert "Total bookmark changes: 2" in done
    chrome_urls = set(flatten_bookmarks(load_bookmarks(chrome)))
    yandex_urls = set(flatten_bookmarks(load_bookmarks(yandex)))
    assert chrome_urls == yandex_urls == {_URL_A, "https://b.example/"}
    assert load_snapshot(snap) == chrome_urls
    state = load_snapshot_state(snap)
    assert state.chrome_locations[_URL_A].folder_path == ()
    assert state.yandex_locations[_URL_A].folder_path == ()


def test_delete_propagates_from_snapshot(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("harrix_swiss_knife.browser_bookmarks.sync.running_browser_names", list)
    chrome, yandex = _write_pair(
        tmp_path,
        [("A", _URL_A), ("Keep", _URL_KEEP)],
        [("A", _URL_A), ("Keep", _URL_KEEP)],
    )
    snap = tmp_path / "snap.json"
    save_url_snapshot({_URL_A, _URL_KEEP, "https://gone.example/"}, snap)
    # Simulate delete of A in Chrome only.
    write_bookmarks(chrome, _minimal_bookmarks(("Keep", _URL_KEEP)))
    plan = build_sync_plan(chrome_path=chrome, yandex_path=yandex, snapshot_file=snap)
    assert not plan.first_run
    assert plan.delete_from_yandex == [_URL_A]
    apply_sync_plan(plan, create_backup=False)
    assert _URL_A not in flatten_bookmarks(load_bookmarks(yandex))
    assert _URL_KEEP in flatten_bookmarks(load_bookmarks(chrome))
    assert _URL_A not in load_snapshot(snap)


def test_delete_wins_over_other_side(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("harrix_swiss_knife.browser_bookmarks.sync.running_browser_names", list)
    chrome, yandex = _write_pair(
        tmp_path,
        [],
        [("Renamed", _URL_X)],
    )
    snap = tmp_path / "snap.json"
    save_url_snapshot({_URL_X}, snap)
    plan = build_sync_plan(chrome_path=chrome, yandex_path=yandex, snapshot_file=snap)
    assert plan.delete_from_yandex == [_URL_X]
    assert plan.add_to_chrome == []
    apply_sync_plan(plan, create_backup=False)
    assert flatten_bookmarks(load_bookmarks(yandex)) == {}
    assert flatten_bookmarks(load_bookmarks(chrome)) == {}


def test_cancel_does_not_update_snapshot(tmp_path: Path) -> None:
    chrome, yandex = _write_pair(
        tmp_path,
        [("A", _URL_A)],
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
    chrome, yandex = _write_pair(tmp_path, [("A", _URL_A)], [])
    snap = tmp_path / "snap.json"
    plan = build_sync_plan(chrome_path=chrome, yandex_path=yandex, snapshot_file=snap)
    with pytest.raises(OSError, match="Close Google Chrome"):
        apply_sync_plan(plan, create_backup=False)


def test_action_in_file_operations_menu() -> None:
    assert OnSyncChromeYandexBookmarks.title == "Sync Chrome and Yandex bookmarks"
    assert OnSyncChromeYandexBookmarks in list(iter_menu_structure(get_menu_structure()))


def test_first_run_does_not_relocate_existing_url(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("harrix_swiss_knife.browser_bookmarks.sync.running_browser_names", list)
    chrome, yandex = _write_trees(
        tmp_path,
        _tree_with_url("A", _URL_A, ("Work",)),
        _tree_with_url("A", _URL_A, ("Archive",)),
    )
    snap = tmp_path / "snap.json"
    plan = build_sync_plan(chrome_path=chrome, yandex_path=yandex, snapshot_file=snap)
    assert plan.first_run
    assert plan.move_in_chrome == []
    assert plan.move_in_yandex == []
    assert not plan.has_writes


def test_folder_move_propagates_from_chrome(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("harrix_swiss_knife.browser_bookmarks.sync.running_browser_names", list)
    chrome, yandex = _write_trees(
        tmp_path,
        _tree_with_url("A", _URL_A, ("Work",)),
        _tree_with_url("A", _URL_A, ("Work",)),
    )
    snap = tmp_path / "snap.json"
    apply_sync_plan(
        build_sync_plan(chrome_path=chrome, yandex_path=yandex, snapshot_file=snap),
        create_backup=False,
    )
    yandex_guid = _find_url_node(load_bookmarks(yandex), _URL_A)
    assert yandex_guid is not None
    original_guid = yandex_guid["guid"]
    write_bookmarks(chrome, _tree_with_url("A", _URL_A, ("Archive", "Nested")))
    plan = build_sync_plan(chrome_path=chrome, yandex_path=yandex, snapshot_file=snap)
    assert not plan.first_run
    assert plan.move_in_chrome == []
    assert [item.url for item in plan.move_in_yandex] == [_URL_A]
    assert plan.move_in_yandex[0].folder_path == ("Archive", "Nested")
    report = format_sync_report(plan)
    assert "Will move in Yandex: 1" in report
    apply_sync_plan(plan, create_backup=False)
    yandex_map = flatten_bookmarks(load_bookmarks(yandex))
    assert yandex_map[_URL_A].folder_path == ("Archive", "Nested")
    assert yandex_map[_URL_A].root == "bookmark_bar"
    moved = _find_url_node(load_bookmarks(yandex), _URL_A)
    assert moved is not None
    assert moved["guid"] == original_guid


def test_folder_move_propagates_from_yandex(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("harrix_swiss_knife.browser_bookmarks.sync.running_browser_names", list)
    chrome, yandex = _write_trees(
        tmp_path,
        _tree_with_url("A", _URL_A, ("Work",)),
        _tree_with_url("A", _URL_A, ("Work",)),
    )
    snap = tmp_path / "snap.json"
    apply_sync_plan(
        build_sync_plan(chrome_path=chrome, yandex_path=yandex, snapshot_file=snap),
        create_backup=False,
    )
    write_bookmarks(yandex, _tree_with_url("A", _URL_A, ("Other",), root="other"))
    plan = build_sync_plan(chrome_path=chrome, yandex_path=yandex, snapshot_file=snap)
    assert [item.url for item in plan.move_in_chrome] == [_URL_A]
    assert plan.move_in_chrome[0].root == "other"
    assert plan.move_in_chrome[0].folder_path == ("Other",)
    apply_sync_plan(plan, create_backup=False)
    chrome_map = flatten_bookmarks(load_bookmarks(chrome))
    assert chrome_map[_URL_A].root == "other"
    assert chrome_map[_URL_A].folder_path == ("Other",)


def test_matching_folders_do_not_plan_move(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("harrix_swiss_knife.browser_bookmarks.sync.running_browser_names", list)
    chrome, yandex = _write_trees(
        tmp_path,
        _tree_with_url("A", _URL_A, ("Work",)),
        _tree_with_url("A", _URL_A, ("Work",)),
    )
    snap = tmp_path / "snap.json"
    apply_sync_plan(
        build_sync_plan(chrome_path=chrome, yandex_path=yandex, snapshot_file=snap),
        create_backup=False,
    )
    plan = build_sync_plan(chrome_path=chrome, yandex_path=yandex, snapshot_file=snap)
    assert plan.move_in_chrome == []
    assert plan.move_in_yandex == []
    assert not plan.has_writes


def test_move_conflict_newer_date_modified_wins(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("harrix_swiss_knife.browser_bookmarks.sync.running_browser_names", list)
    chrome, yandex = _write_trees(
        tmp_path,
        _tree_with_url("A", _URL_A, ("Work",)),
        _tree_with_url("A", _URL_A, ("Work",)),
    )
    snap = tmp_path / "snap.json"
    apply_sync_plan(
        build_sync_plan(chrome_path=chrome, yandex_path=yandex, snapshot_file=snap),
        create_backup=False,
    )
    write_bookmarks(chrome, _tree_with_url("A", _URL_A, ("FromChrome",), date_modified="100"))
    write_bookmarks(yandex, _tree_with_url("A", _URL_A, ("FromYandex",), date_modified="200"))
    plan = build_sync_plan(chrome_path=chrome, yandex_path=yandex, snapshot_file=snap)
    assert [item.url for item in plan.move_in_chrome] == [_URL_A]
    assert plan.move_in_chrome[0].folder_path == ("FromYandex",)
    assert plan.move_in_yandex == []
    apply_sync_plan(plan, create_backup=False)
    assert flatten_bookmarks(load_bookmarks(chrome))[_URL_A].folder_path == ("FromYandex",)


def test_delete_wins_over_folder_move(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("harrix_swiss_knife.browser_bookmarks.sync.running_browser_names", list)
    chrome, yandex = _write_trees(
        tmp_path,
        _tree_with_url("A", _URL_A, ("Work",)),
        _tree_with_url("A", _URL_A, ("Work",)),
    )
    snap = tmp_path / "snap.json"
    apply_sync_plan(
        build_sync_plan(chrome_path=chrome, yandex_path=yandex, snapshot_file=snap),
        create_backup=False,
    )
    write_bookmarks(chrome, _empty_bookmarks())
    write_bookmarks(yandex, _tree_with_url("A", _URL_A, ("Archive",)))
    plan = build_sync_plan(chrome_path=chrome, yandex_path=yandex, snapshot_file=snap)
    assert plan.delete_from_yandex == [_URL_A]
    assert plan.move_in_chrome == []
    assert plan.move_in_yandex == []
    apply_sync_plan(plan, create_backup=False)
    assert flatten_bookmarks(load_bookmarks(yandex)) == {}


def test_v1_snapshot_does_not_guess_folder_moves(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("harrix_swiss_knife.browser_bookmarks.sync.running_browser_names", list)
    chrome, yandex = _write_trees(
        tmp_path,
        _tree_with_url("A", _URL_A, ("Work",)),
        _tree_with_url("A", _URL_A, ("Archive",)),
    )
    snap = tmp_path / "snap.json"
    _write_v1_snapshot(snap, {_URL_A})
    plan = build_sync_plan(chrome_path=chrome, yandex_path=yandex, snapshot_file=snap)
    assert not plan.first_run
    assert plan.move_in_chrome == []
    assert plan.move_in_yandex == []
    apply_sync_plan(plan, create_backup=False)
    raw = json.loads(snap.read_text(encoding="utf-8"))
    assert raw["version"] == 2
    assert raw["bookmarks"][_URL_A]["chrome"]["folder_path"] == ["Work"]
    assert raw["bookmarks"][_URL_A]["yandex"]["folder_path"] == ["Archive"]
    later = build_sync_plan(chrome_path=chrome, yandex_path=yandex, snapshot_file=snap)
    assert later.move_in_chrome == []
    assert later.move_in_yandex == []
    write_bookmarks(chrome, _tree_with_url("A", _URL_A, ("Inbox",)))
    after_move = build_sync_plan(chrome_path=chrome, yandex_path=yandex, snapshot_file=snap)
    assert [item.url for item in after_move.move_in_yandex] == [_URL_A]
    assert after_move.move_in_yandex[0].folder_path == ("Inbox",)


def test_save_snapshot_writes_v2_locations(tmp_path: Path) -> None:
    entry = BookmarkEntry(url=_URL_A, name="A", root="bookmark_bar", folder_path=("Work",))
    snap = tmp_path / "snap.json"
    save_snapshot({_URL_A: entry}, {_URL_A: entry}, snap)
    state = load_snapshot_state(snap)
    assert state.urls == {_URL_A}
    assert state.chrome_locations[_URL_A].folder_path == ("Work",)
    assert state.yandex_locations[_URL_A].folder_path == ("Work",)
