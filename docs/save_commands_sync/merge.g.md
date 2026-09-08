---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `merge.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `MergeResult`](#%EF%B8%8F-class-mergeresult)
- [🔧 Function `command_fingerprint`](#-function-command_fingerprint)
- [🔧 Function `folder_fingerprint`](#-function-folder_fingerprint)
- [🔧 Function `merge_editor_states`](#-function-merge_editor_states)

</details>

## 🏛️ Class `MergeResult`

```python
class MergeResult
```

Merged command/folder lists plus notes about collapsed ids.

<details>
<summary>Code:</summary>

```python
class MergeResult:

    commands: list[dict[str, Any]]
    folders: list[dict[str, Any]]
    collapsed_commands: list[tuple[str, str]] = field(default_factory=list)
    collapsed_folders: list[tuple[str, str]] = field(default_factory=list)
    command_id_conflicts: list[str] = field(default_factory=list)
    folder_id_conflicts: list[str] = field(default_factory=list)
```

</details>

## 🔧 Function `command_fingerprint`

```python
def command_fingerprint(item: dict[str, Any]) -> tuple[str, str]
```

Identity used to treat two commands as the same entry across editors.

<details>
<summary>Code:</summary>

```python
def command_fingerprint(item: dict[str, Any]) -> tuple[str, str]:
    return (_as_text(item.get("name")).strip(), _as_text(item.get("command")).strip())
```

</details>

## 🔧 Function `folder_fingerprint`

```python
def folder_fingerprint(item: dict[str, Any]) -> tuple[str, str]
```

Identity used to treat two folders as the same node across editors.

<details>
<summary>Code:</summary>

```python
def folder_fingerprint(item: dict[str, Any]) -> tuple[str, str]:
    return (_as_text(item.get("name")).strip(), _as_text(item.get("parentFolderId")).strip())
```

</details>

## 🔧 Function `merge_editor_states`

```python
def merge_editor_states(states: list[dict[str, list[dict[str, Any]]]]) -> MergeResult
```

Union commands and folders; first editor wins on ID conflicts.

Duplicate `(name, command)` pairs with different ids keep the first ID.
Duplicate folder `(name, parentFolderId)` pairs remap to the first ID.
`sortOrder` is rewritten from 0 to n-1 after merge.

<details>
<summary>Code:</summary>

```python
def merge_editor_states(states: list[dict[str, list[dict[str, Any]]]]) -> MergeResult:
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
```

</details>
