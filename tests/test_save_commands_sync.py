"""Tests for union-sync of Save Commands extension global state."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

import pytest

from harrix_swiss_knife.actions.common.quick_launcher_registry import iter_menu_structure
from harrix_swiss_knife.actions.vscode.sync_save_commands import OnSyncSaveCommands
from harrix_swiss_knife.menu_structure import get_menu_structure
from harrix_swiss_knife.save_commands_sync.merge import merge_editor_states
from harrix_swiss_knife.save_commands_sync.storage import (
    SaveCommandsStorageError,
    dump_state_payload,
    read_save_commands_state,
    write_save_commands_state,
)
from harrix_swiss_knife.save_commands_sync.sync import apply_sync_plan, build_sync_plan, format_sync_report

_CURSOR = "Cursor"
_INSIDERS = "VS Code Insiders"


def _cmd(
    cmd_id: str,
    name: str,
    command: str,
    *,
    sort_order: int = 0,
    parent_folder_id: str | None = None,
) -> dict[str, Any]:
    return {
        "id": cmd_id,
        "name": name,
        "command": command,
        "placeholderTypeId": "doubleCurlyBraces",
        "sortOrder": sort_order,
        "parentFolderId": parent_folder_id,
    }


def _folder(
    folder_id: str,
    name: str,
    *,
    parent_folder_id: str | None = None,
    sort_order: int = 0,
) -> dict[str, Any]:
    return {
        "id": folder_id,
        "name": name,
        "parentFolderId": parent_folder_id,
        "sortOrder": sort_order,
        "joinWith": None,
    }


def _init_state_db(path: Path, commands: list[dict[str, Any]], folders: list[dict[str, Any]] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.execute("CREATE TABLE ItemTable (key TEXT UNIQUE ON CONFLICT REPLACE, value BLOB)")
    conn.commit()
    conn.close()
    write_save_commands_state(path, commands, folders or [])


def test_merge_unions_distinct_commands() -> None:
    left = {"commands": [_cmd("a", "One", "echo 1", sort_order=0)], "command_folders": []}
    right = {"commands": [_cmd("b", "Two", "echo 2", sort_order=0)], "command_folders": []}
    merged = merge_editor_states([left, right])
    names = [item["name"] for item in merged.commands]
    assert names == ["One", "Two"]
    assert [item["sortOrder"] for item in merged.commands] == [0, 1]


def test_merge_collapses_same_name_and_body_with_different_ids() -> None:
    left = {"commands": [_cmd("id-cursor", "💎 hsk md beautify-md", "hsk md beautify-md")], "command_folders": []}
    right = {"commands": [_cmd("id-insiders", "💎 hsk md beautify-md", "hsk md beautify-md")], "command_folders": []}
    merged = merge_editor_states([left, right])
    assert len(merged.commands) == 1
    assert merged.commands[0]["id"] == "id-cursor"
    assert merged.collapsed_commands == [("id-insiders", "id-cursor")]


def test_merge_same_id_keeps_first_editor_on_conflict() -> None:
    left = {"commands": [_cmd("same", "Keep", "echo keep")], "command_folders": []}
    right = {"commands": [_cmd("same", "Other", "echo other")], "command_folders": []}
    merged = merge_editor_states([left, right])
    assert merged.commands[0]["name"] == "Keep"
    assert merged.command_id_conflicts == ["same"]


def test_merge_remaps_folder_ids_on_commands() -> None:
    left = {
        "commands": [_cmd("c1", "Run", "echo", parent_folder_id="folder-a")],
        "command_folders": [_folder("folder-a", "Build")],
    }
    right = {
        "commands": [_cmd("c2", "Test", "pytest", parent_folder_id="folder-b")],
        "command_folders": [_folder("folder-b", "Build")],
    }
    merged = merge_editor_states([left, right])
    assert len(merged.folders) == 1
    assert merged.folders[0]["id"] == "folder-a"
    parents = {item["name"]: item["parentFolderId"] for item in merged.commands}
    assert parents == {"Run": "folder-a", "Test": "folder-a"}
    assert merged.collapsed_folders == [("folder-b", "folder-a")]


def test_sqlite_roundtrip_read_write(tmp_path: Path) -> None:
    db_path = tmp_path / "state.vscdb"
    commands = [_cmd("x", "Hello", "echo hi", sort_order=3)]
    _init_state_db(db_path, commands, [])
    loaded = read_save_commands_state(db_path)
    assert loaded["commands"][0]["name"] == "Hello"
    write_save_commands_state(db_path, [_cmd("y", "Bye", "echo bye")], [])
    again = read_save_commands_state(db_path)
    assert again["commands"][0]["id"] == "y"
    assert "command_folders" in again


def test_build_and_apply_sync_plan(tmp_path: Path) -> None:
    cursor_db = tmp_path / "cursor" / "state.vscdb"
    insiders_db = tmp_path / "insiders" / "state.vscdb"
    _init_state_db(
        cursor_db,
        [
            _cmd("c-start", "🚀 Start", "hsk", sort_order=0),
            _cmd("c-md", "💎 hsk md beautify-md", "hsk md beautify-md", sort_order=1),
        ],
    )
    _init_state_db(
        insiders_db,
        [
            _cmd("i-md", "💎 hsk md beautify-md", "hsk md beautify-md", sort_order=0),
            _cmd("i-clear", "clear", "clear", sort_order=1),
        ],
    )
    dbs = {_CURSOR: cursor_db, _INSIDERS: insiders_db}

    plan = build_sync_plan(
        [_CURSOR, _INSIDERS],
        resolve_db=dbs.get,
        extension_installed=lambda _label: True,
        running_names=lambda _labels: [],
    )
    assert plan.has_writes
    names = {item["name"] for item in plan.merged.commands}
    assert names == {"🚀 Start", "💎 hsk md beautify-md", "clear"}
    cursor_delta = next(delta for delta in plan.deltas if delta.label == _CURSOR)
    insiders_delta = next(delta for delta in plan.deltas if delta.label == _INSIDERS)
    assert cursor_delta.added_names == ["clear"]
    assert insiders_delta.added_names == ["🚀 Start"]
    assert insiders_delta.id_realigned == 1

    report = format_sync_report(plan)
    assert "preview" in report
    assert "Will add to Cursor" in report
    assert "Will add to VS Code Insiders" in report

    apply_sync_plan(plan, create_backup=False, force=True)
    cursor_state = read_save_commands_state(cursor_db)
    insiders_state = read_save_commands_state(insiders_db)
    assert dump_state_payload(cursor_state["commands"], cursor_state["command_folders"]) == dump_state_payload(
        insiders_state["commands"],
        insiders_state["command_folders"],
    )
    assert {item["id"] for item in cursor_state["commands"]} == {item["id"] for item in insiders_state["commands"]}
    md_ids = [item["id"] for item in insiders_state["commands"] if item["name"] == "💎 hsk md beautify-md"]
    assert md_ids == ["c-md"]

    synced = build_sync_plan(
        [_CURSOR, _INSIDERS],
        resolve_db=dbs.get,
        extension_installed=lambda _label: True,
        running_names=lambda _labels: [],
    )
    assert not synced.has_writes
    applied = format_sync_report(plan, applied=True)
    assert "Status: applied" in applied
    assert "Reload Window" in applied


def test_build_sync_plan_skips_write_when_already_equal(tmp_path: Path) -> None:
    shared = [_cmd("one", "A", "echo a"), _cmd("two", "B", "echo b", sort_order=1)]
    left = tmp_path / "left.vscdb"
    right = tmp_path / "right.vscdb"
    _init_state_db(left, shared)
    _init_state_db(right, list(shared))
    dbs = {_CURSOR: left, _INSIDERS: right}
    plan = build_sync_plan(
        [_CURSOR, _INSIDERS],
        resolve_db=dbs.get,
        extension_installed=lambda _label: False,
        running_names=lambda _labels: [_CURSOR],
    )
    assert not plan.has_writes
    assert plan.running == [_CURSOR]
    report = format_sync_report(plan)
    assert "already match" in report
    assert "Close before Apply: Cursor" in report


def test_apply_sync_plan_requires_editors_closed(tmp_path: Path) -> None:
    left = tmp_path / "left.vscdb"
    right = tmp_path / "right.vscdb"
    _init_state_db(left, [_cmd("a", "One", "echo 1")])
    _init_state_db(right, [_cmd("b", "Two", "echo 2")])
    dbs = {_CURSOR: left, _INSIDERS: right}
    plan = build_sync_plan(
        [_CURSOR, _INSIDERS],
        resolve_db=dbs.get,
        extension_installed=lambda _label: True,
        running_names=lambda _labels: [],
    )
    with pytest.raises(SaveCommandsStorageError, match="Close Cursor"):
        apply_sync_plan(
            plan,
            create_backup=False,
            running_names=lambda _labels: [_CURSOR],
        )


def test_action_in_vscode_menu() -> None:
    assert OnSyncSaveCommands in list(iter_menu_structure(get_menu_structure()))
    assert OnSyncSaveCommands.cli_available
    assert "sync-save-commands" in OnSyncSaveCommands.cli_hint
