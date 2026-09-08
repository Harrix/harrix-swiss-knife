"""Build and apply a union-sync of global Save Commands across editors."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from harrix_swiss_knife.browser_bookmarks.paths import harrix_swiss_knife_data_dir
from harrix_swiss_knife.save_commands_sync.editors import (
    discover_editors,
    running_editor_names,
    save_commands_extension_installed,
    state_vscdb_path,
)
from harrix_swiss_knife.save_commands_sync.merge import (
    MergeResult,
    command_fingerprint,
    merge_editor_states,
)
from harrix_swiss_knife.save_commands_sync.storage import (
    SaveCommandsStorageError,
    copy_state_db,
    dump_state_payload,
    read_save_commands_state,
    write_save_commands_state,
)

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

_REPORT_LIST_LIMIT = 40
MIN_SYNC_EDITORS = 2


@dataclass
class EditorSnapshot:
    """Save Commands global state read from one editor profile."""

    label: str
    state_db: Path
    commands: list[dict[str, Any]]
    folders: list[dict[str, Any]]
    extension_installed: bool


@dataclass
class EditorWriteDelta:
    """How the merged set differs from one editor's current global commands."""

    label: str
    added_names: list[str]
    id_realigned: int
    unchanged: bool


@dataclass
class SyncPlan:
    """In-memory union-sync ready to report or apply."""

    editors: list[EditorSnapshot]
    merged: MergeResult
    deltas: list[EditorWriteDelta]
    running: list[str] = field(default_factory=list)
    backup_path: Path | None = None

    @property
    def has_writes(self) -> bool:
        """Whether Apply would change at least one `state.vscdb`."""
        return any(not delta.unchanged for delta in self.deltas)


def apply_sync_plan(
    plan: SyncPlan,
    *,
    create_backup: bool = True,
    force: bool = False,
    running_names: Callable[[list[str]], list[str]] | None = None,
) -> Path | None:
    """Backup (optional) and write the merged global commands to every selected editor.

    Args:

    - `plan` (`SyncPlan`): Plan from `build_sync_plan`.
    - `create_backup` (`bool`): Copy each `state.vscdb` before writing. Defaults to `True`.
    - `force` (`bool`): Write even if selected editors are running. Defaults to `False`.
    - `running_names` (`Callable[[list[str]], list[str]] | None`): Override process detection (tests).

    Returns:

    - `Path | None`: Backup folder when `create_backup` is true and at least one file was copied.

    """
    labels = [editor.label for editor in plan.editors]
    running_for = running_names or running_editor_names
    running = running_for(labels)
    if running and not force:
        names = ", ".join(running)
        msg = f"Close {names} before writing Saved Commands (the editors overwrite state.vscdb on exit)"
        raise SaveCommandsStorageError(msg)

    backup: Path | None = None
    if create_backup:
        backup = _backup_root() / datetime.now(UTC).astimezone().strftime("%Y-%m-%d_%H-%M-%S")
        backup.mkdir(parents=True, exist_ok=True)
        for editor in plan.editors:
            copy_state_db(editor.state_db, backup / _backup_filename(editor.label))
        plan.backup_path = backup

    for editor, delta in zip(plan.editors, plan.deltas, strict=True):
        if delta.unchanged:
            continue
        write_save_commands_state(editor.state_db, plan.merged.commands, plan.merged.folders)
    return backup


def build_sync_plan(
    labels: list[str],
    *,
    resolve_db: Callable[[str], Path | None] | None = None,
    extension_installed: Callable[[str], bool] | None = None,
    running_names: Callable[[list[str]], list[str]] | None = None,
) -> SyncPlan:
    """Read selected editors and compute the union of global Save Commands.

    Args:

    - `labels` (`list[str]`): Canonical editor labels (at least two).
    - `resolve_db` (`Callable[[str], Path | None] | None`): Override `state.vscdb` lookup (tests).
    - `extension_installed` (`Callable[[str], bool] | None`): Override extension-folder check (tests).
    - `running_names` (`Callable[[list[str]], list[str]] | None`): Override process detection (tests).

    Returns:

    - `SyncPlan`: Snapshots, merged lists, and per-editor deltas.

    """
    if len(labels) < MIN_SYNC_EDITORS:
        msg = "Select at least two editors"
        raise SaveCommandsStorageError(msg)

    db_for = resolve_db or state_vscdb_path
    ext_for = extension_installed or save_commands_extension_installed
    running_for = running_names or running_editor_names

    snapshots: list[EditorSnapshot] = []
    for label in labels:
        db_path = db_for(label)
        if db_path is None:
            msg = f"Unknown editor: {label}"
            raise SaveCommandsStorageError(msg)
        if not db_path.is_file():
            msg = f"{label}: state.vscdb not found ({db_path})"
            raise SaveCommandsStorageError(msg)
        state = read_save_commands_state(db_path)
        snapshots.append(
            EditorSnapshot(
                label=label,
                state_db=db_path,
                commands=state["commands"],
                folders=state["command_folders"],
                extension_installed=ext_for(label),
            )
        )

    merged = merge_editor_states([{"commands": snap.commands, "command_folders": snap.folders} for snap in snapshots])
    merged_payload = dump_state_payload(merged.commands, merged.folders)
    deltas = [_delta_for(snap, merged, merged_payload) for snap in snapshots]
    return SyncPlan(
        editors=snapshots,
        merged=merged,
        deltas=deltas,
        running=running_for(labels),
    )


def default_sync_editor_labels() -> list[str]:
    """Editors to sync when the CLI omits tokens: extension present, else any with `state.vscdb`."""
    discovered = discover_editors()
    with_extension = [label for label in discovered if save_commands_extension_installed(label)]
    if len(with_extension) >= MIN_SYNC_EDITORS:
        return with_extension
    with_db: list[str] = []
    for label in discovered:
        db_path = state_vscdb_path(label)
        if db_path is not None and db_path.is_file():
            with_db.append(label)
    return with_db


def format_sync_report(plan: SyncPlan, *, applied: bool = False) -> str:
    """Build preview or post-apply report with counts first."""
    merged_commands = len(plan.merged.commands)
    merged_folders = len(plan.merged.folders)
    collapsed = len(plan.merged.collapsed_commands)
    status = "applied" if applied else "preview (not written yet)"
    lines = [
        f"Status: {status}",
        "",
        "Summary:",
        f"  Editors: {len(plan.editors)}",
        f"  Merged commands: {merged_commands}",
        f"  Merged folders: {merged_folders}",
        f"  Collapsed duplicate commands (same name and body, different ids): {collapsed}",
        f"  Collapsed duplicate folders: {len(plan.merged.collapsed_folders)}",
        "",
    ]
    for snap in plan.editors:
        ext = "Save Commands installed" if snap.extension_installed else "Save Commands folder not found"
        lines.append(f"  {snap.label}: {len(snap.commands)} commands, {len(snap.folders)} folders ({ext})")
    lines.append("")
    lines.append("Workspace-scoped Saved Commands are not synced.")
    lines.append("")

    if plan.merged.command_id_conflicts:
        lines.append(
            "Same id, different command body (kept the first editor's copy): "
            + ", ".join(plan.merged.command_id_conflicts[:_REPORT_LIST_LIMIT])
        )
        lines.append("")
    if plan.merged.folder_id_conflicts:
        lines.append(
            "Same id, different folder body (kept the first editor's copy): "
            + ", ".join(plan.merged.folder_id_conflicts[:_REPORT_LIST_LIMIT])
        )
        lines.append("")

    if plan.running:
        lines.append("Close before Apply: " + ", ".join(plan.running))
    else:
        lines.append("Editors: appear closed.")
    lines.append("")

    for delta in plan.deltas:
        if delta.unchanged:
            lines.append(f"{delta.label}: already matches the merged set.")
            lines.append("")
            continue
        verb = "Added" if applied else "Will add"
        if delta.added_names:
            lines.append(f"{verb} to {delta.label} ({len(delta.added_names)}):")
            lines.extend(_format_name_lines(delta.added_names))
            lines.append("")
        if delta.id_realigned:
            lines.append(
                f"{delta.label}: {delta.id_realigned} command(s) keep the same name "
                "but will use the id from the merged set."
            )
            lines.append("")
        if not delta.added_names and not delta.id_realigned:
            lines.append(f"{delta.label}: command list will be rewritten (order or folders).")
            lines.append("")

    if applied and plan.backup_path is not None:
        lines.append(f"Backup: {plan.backup_path}")
        lines.append("")
    if applied:
        lines.append("Reload Window in each editor (or restart) to see updated Saved Commands.")
    elif not plan.has_writes:
        lines.append("Nothing to apply — Saved Commands already match.")
    return "\n".join(lines).rstrip() + "\n"


def _as_id(item: dict[str, Any]) -> str:
    value = item.get("id")
    return "" if value is None else str(value)


def _backup_filename(label: str) -> str:
    safe = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in label)
    return f"{safe}.state.vscdb"


def _backup_root() -> Path:
    return harrix_swiss_knife_data_dir() / "save_commands_backups"


def _delta_for(snap: EditorSnapshot, merged: MergeResult, merged_payload: str) -> EditorWriteDelta:
    current_payload = dump_state_payload(snap.commands, snap.folders)
    if current_payload == merged_payload:
        return EditorWriteDelta(label=snap.label, added_names=[], id_realigned=0, unchanged=True)

    current_fps = {command_fingerprint(item) for item in snap.commands}
    added_names = [
        command_fingerprint(item)[0] or "(unnamed)"
        for item in merged.commands
        if command_fingerprint(item) not in current_fps
    ]
    current_by_fp = {command_fingerprint(item): _as_id(item) for item in snap.commands}
    merged_by_fp = {command_fingerprint(item): _as_id(item) for item in merged.commands}
    realigned = 0
    for fingerprint, merged_id in merged_by_fp.items():
        current_id = current_by_fp.get(fingerprint)
        if current_id is not None and current_id != merged_id:
            realigned += 1
    return EditorWriteDelta(
        label=snap.label,
        added_names=added_names,
        id_realigned=realigned,
        unchanged=False,
    )


def _format_name_lines(names: list[str]) -> list[str]:
    shown = names[:_REPORT_LIST_LIMIT]
    lines = [f"  - {name}" for name in shown]
    extra = len(names) - len(shown)
    if extra > 0:
        lines.append(f"  … {extra} more")
    return lines
