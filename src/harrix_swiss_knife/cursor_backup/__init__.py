"""Pack Cursor IDE settings, chats, and `.cursor` folders into a ZIP backup."""

from harrix_swiss_knife.cursor_backup.pack import (
    DEFAULT_PARTS,
    PART_DOT_CURSOR,
    PART_EXTENSIONS,
    PART_PROJECT_CURSOR,
    PART_USER,
    BackupPart,
    BackupResult,
    estimate_part_sizes,
    format_backup_report,
    pack_cursor_backup,
    parts_from_labels,
)
from harrix_swiss_knife.cursor_backup.paths import (
    cursor_dot_dir,
    cursor_running,
    cursor_user_dir,
    discover_project_cursor_dirs,
)

__all__ = [
    "DEFAULT_PARTS",
    "PART_DOT_CURSOR",
    "PART_EXTENSIONS",
    "PART_PROJECT_CURSOR",
    "PART_USER",
    "BackupPart",
    "BackupResult",
    "cursor_dot_dir",
    "cursor_running",
    "cursor_user_dir",
    "discover_project_cursor_dirs",
    "estimate_part_sizes",
    "format_backup_report",
    "pack_cursor_backup",
    "parts_from_labels",
]
