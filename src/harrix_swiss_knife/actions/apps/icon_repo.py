"""Resolve a Vector Icons note repository for maintenance actions."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from harrix_swiss_knife.apps.icons.catalog import is_note_icons_repo, resolve_icons_root

if TYPE_CHECKING:
    from harrix_swiss_knife.actions.common.base import ActionBase


def pick_vector_icons_repo(action: ActionBase) -> Path | None:
    """Ask for a Vector Icons note repo, starting from configured folders."""
    choices = vector_icons_repo_choices(action.config)
    default = str(action.config.get("path_github") or (choices[0] if choices else ""))
    chosen = action.dialogs.get_folder_with_choice_option(choices, default)
    if chosen is None:
        return None
    try:
        root = resolve_icons_root(Path(chosen))
    except (OSError, FileNotFoundError) as exc:
        action.add_line(f"❌ {exc}")
        action.show_result()
        return None
    if not is_note_icons_repo(root):
        action.add_line(f"❌ `{root}` is not a Vector Icons note repository (need `icons/` notes).")
        action.show_result()
        return None
    return root


def vector_icons_repo_choices(config: dict[str, Any]) -> list[str]:
    """Return existing Vector Icons folders from `config.json`."""
    seen: set[Path] = set()
    result: list[str] = []

    def add(raw: object) -> None:
        text = str(raw or "").strip()
        if not text or text.startswith("<"):
            return
        path = Path(text).expanduser()
        try:
            resolved = path.resolve()
        except OSError:
            return
        if not resolved.is_dir() or resolved in seen:
            return
        seen.add(resolved)
        result.append(str(resolved))

    add(config.get("path_vector_icons"))
    pinned = config.get("path_vector_icons_pinned")
    if isinstance(pinned, list):
        for item in pinned:
            add(item)
    return result
