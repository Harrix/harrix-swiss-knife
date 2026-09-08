"""Union-merge global Save Commands lists from several editors."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable

_COMMAND_CORE_KEYS = ("name", "command", "placeholderTypeId", "parentFolderId")
_FOLDER_CORE_KEYS = ("name", "parentFolderId", "joinWith")


@dataclass
class MergeResult:
    """Merged command/folder lists plus notes about collapsed ids."""

    commands: list[dict[str, Any]]
    folders: list[dict[str, Any]]
    collapsed_commands: list[tuple[str, str]] = field(default_factory=list)
    collapsed_folders: list[tuple[str, str]] = field(default_factory=list)
    command_id_conflicts: list[str] = field(default_factory=list)
    folder_id_conflicts: list[str] = field(default_factory=list)


def command_fingerprint(item: dict[str, Any]) -> tuple[str, str]:
    """Identity used to treat two commands as the same entry across editors."""
    return (_as_text(item.get("name")).strip(), _as_text(item.get("command")).strip())


def folder_fingerprint(item: dict[str, Any]) -> tuple[str, str]:
    """Identity used to treat two folders as the same node across editors."""
    return (_as_text(item.get("name")).strip(), _as_text(item.get("parentFolderId")).strip())


def merge_editor_states(states: list[dict[str, list[dict[str, Any]]]]) -> MergeResult:
    """Union commands and folders; first editor wins on ID conflicts.

    Duplicate `(name, command)` pairs with different ids keep the first ID.
    Duplicate folder `(name, parentFolderId)` pairs remap to the first ID.
    `sortOrder` is rewritten from 0 to n-1 after merge.

    """
    folders_by_id: dict[str, dict[str, Any]] = {}
    folder_conflicts: list[str] = []
    for state in states:
        for folder in state.get("command_folders", []):
            fid = _as_text(folder.get("id")).strip()
            if not fid:
                continue
            incoming = dict(folder)
            existing = folders_by_id.get(fid)
            if existing is None:
                folders_by_id[fid] = incoming
                continue
            if not _core_equal(existing, incoming, _FOLDER_CORE_KEYS):
                folder_conflicts.append(fid)

    folder_remap, collapsed_folders = _collapse_by_fingerprint(folders_by_id, folder_fingerprint)
    for folder in folders_by_id.values():
        parent = _as_text(folder.get("parentFolderId")).strip()
        if parent in folder_remap:
            folder["parentFolderId"] = folder_remap[parent]

    commands_by_id: dict[str, dict[str, Any]] = {}
    command_conflicts: list[str] = []
    for state in states:
        for command in state.get("commands", []):
            cid = _as_text(command.get("id")).strip()
            if not cid:
                continue
            incoming = dict(command)
            existing = commands_by_id.get(cid)
            if existing is None:
                commands_by_id[cid] = incoming
                continue
            if not _core_equal(existing, incoming, _COMMAND_CORE_KEYS):
                command_conflicts.append(cid)

    _collapsed_cmd_remap, collapsed_commands = _collapse_by_fingerprint(commands_by_id, command_fingerprint)
    for command in commands_by_id.values():
        parent = _as_text(command.get("parentFolderId")).strip()
        if parent in folder_remap:
            command["parentFolderId"] = folder_remap[parent]

    folders = _sorted_with_order(list(folders_by_id.values()))
    commands = _sorted_with_order(list(commands_by_id.values()))
    return MergeResult(
        commands=commands,
        folders=folders,
        collapsed_commands=collapsed_commands,
        collapsed_folders=collapsed_folders,
        command_id_conflicts=_unique_keep_order(command_conflicts),
        folder_id_conflicts=_unique_keep_order(folder_conflicts),
    )


def _as_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def _collapse_by_fingerprint(
    items_by_id: dict[str, dict[str, Any]],
    fingerprint: Callable[[dict[str, Any]], tuple[str, str]],
) -> tuple[dict[str, str], list[tuple[str, str]]]:
    seen: dict[Any, str] = {}
    remap: dict[str, str] = {}
    collapsed: list[tuple[str, str]] = []
    for item_id, item in list(items_by_id.items()):
        key = fingerprint(item)
        canonical = seen.get(key)
        if canonical is None:
            seen[key] = item_id
            continue
        if item_id == canonical:
            continue
        remap[item_id] = canonical
        collapsed.append((item_id, canonical))
        del items_by_id[item_id]
    return remap, collapsed


def _core_equal(left: dict[str, Any], right: dict[str, Any], keys: tuple[str, ...]) -> bool:
    return all(left.get(key) == right.get(key) for key in keys)


def _sort_key(item: dict[str, Any]) -> tuple[int, str, str]:
    raw_order = item.get("sortOrder", 0)
    try:
        order = int(raw_order)
    except (TypeError, ValueError):
        order = 0
    return (order, _as_text(item.get("name")).casefold(), _as_text(item.get("id")))


def _sorted_with_order(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ordered = sorted(items, key=_sort_key)
    for index, item in enumerate(ordered):
        item["sortOrder"] = index
    return ordered


def _unique_keep_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        out.append(value)
    return out
