"""Path templates for the external `data-for-hsk` folder (no Qt or database imports)."""

from __future__ import annotations

import re
from pathlib import Path  # noqa: TC003
from typing import Any

_NOTES_DIR_NAME = "Notes"
_PLACEHOLDER_RE = re.compile(r"<YOUR_[^>]*>", re.IGNORECASE)

DEFAULT_DATA_FOR_HSK_NOTES_FOLDERS: tuple[str, ...] = (
    "Notes",
    "Notes-Diaries",
    "Notes-External",
    "Notes-Health",
    "Notes-Lists",
    "Notes-Places",
    "Notes-Temp",
)

# Map note folder names under `Notes/` to single-value config keys.
_NOTE_FOLDER_SINGLE_KEYS: dict[str, tuple[str, ...]] = {
    "Notes": ("path_notes", "path_last_note_folder", "path_articles"),
    "Notes-Diaries": ("path_diary", "path_dream", "path_memories"),
    "Notes-External": ("path_cases",),
    "Notes-Lists": ("path_quotes",),
}

TRACKER_DATABASE_NAMES: tuple[str, ...] = (
    "finance.db",
    "fitness.db",
    "habits.db",
    "food.db",
)

SQLITE_CONFIG_KEYS: tuple[str, ...] = (
    "sqlite_finance",
    "sqlite_fitness",
    "sqlite_habits",
    "sqlite_food",
)


def build_config_updates(data_root: Path, notes_folders: tuple[str, ...] | list[str]) -> dict[str, Any]:
    """Return `config.json` fields for `data_root` and its Notes subfolders."""
    data_root = data_root.expanduser().resolve()
    databases_dir = data_root / "databases"
    notes_parent = data_root / _NOTES_DIR_NAME
    folder_paths = {name: notes_parent / name for name in notes_folders}

    updates: dict[str, Any] = {
        "data_for_hsk_root": data_root.as_posix(),
        "data_for_hsk_notes_folders": list(notes_folders),
        "data_for_hsk_setup_done": True,
        "sqlite_finance": (databases_dir / "finance.db").as_posix(),
        "sqlite_fitness": (databases_dir / "fitness.db").as_posix(),
        "sqlite_habits": (databases_dir / "habits.db").as_posix(),
        "sqlite_food": (databases_dir / "food.db").as_posix(),
    }

    for folder_name, keys in _NOTE_FOLDER_SINGLE_KEYS.items():
        if folder_name not in folder_paths:
            continue
        path_posix = folder_paths[folder_name].as_posix()
        for key in keys:
            updates[key] = path_posix

    all_note_paths = [folder_paths[name].as_posix() for name in notes_folders if name in folder_paths]
    updates["paths_notes"] = all_note_paths
    updates["paths_git"] = [*all_note_paths, databases_dir.as_posix()]
    summary_names = [name for name in ("Notes", "Notes-Diaries") if name in folder_paths]
    updates["paths_notes_for_summaries"] = [folder_paths[name].as_posix() for name in summary_names]

    return updates


def is_config_placeholder_path(value: object) -> bool:
    """Return whether `value` is empty or contains a `<YOUR_…>` placeholder."""
    if not isinstance(value, str) or not value.strip():
        return True
    return bool(_PLACEHOLDER_RE.search(value))
