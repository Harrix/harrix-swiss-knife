"""SQLite helpers for Media Sorter reviewed state and bin assignment history."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from pathlib import Path

from harrix_swiss_knife.apps.common.qt_database_manager_base import QtSqliteDatabaseManagerBase

logger = logging.getLogger(__name__)


class DatabaseManager(QtSqliteDatabaseManagerBase):
    """Manage Media Sorter history (reviewed files, bin assignments, deletes)."""

    def __init__(self, db_filename: str) -> None:
        """Open a connection to an SQLite database stored in `db_filename`."""
        super().__init__(prefix="media_sorter_db", db_filename=db_filename)

    def add_bin_assignment(
        self,
        path: str | Path,
        bin_id: str,
        dest_path: str | Path,
        mode: str,
    ) -> bool:
        """Record that `path` was copied/moved into a config bin."""
        normalized = normalize_media_path(path)
        dest = normalize_media_path(dest_path)
        mode_norm = mode.strip().lower()
        if mode_norm not in {"copy", "move"}:
            logger.error("Invalid bin assignment mode: %s", mode)
            return False
        query = """
            INSERT INTO bin_assignments (path, bin_id, dest_path, mode, assigned_at)
            VALUES (:path, :bin_id, :dest_path, :mode, :assigned_at)
            ON CONFLICT(path, bin_id) DO UPDATE SET
                dest_path = excluded.dest_path,
                mode = excluded.mode,
                assigned_at = excluded.assigned_at
        """
        return self.execute_simple_query(
            query,
            {
                "path": normalized,
                "bin_id": bin_id,
                "dest_path": dest,
                "mode": mode_norm,
                "assigned_at": _utc_now_iso(),
            },
        )

    def get_bin_ids_for_path(self, path: str | Path) -> set[str]:
        """Return bin IDs already assigned for `path`."""
        rows = self.get_rows(
            "SELECT bin_id FROM bin_assignments WHERE path = :path",
            {"path": normalize_media_path(path)},
        )
        return {str(row[0]) for row in rows if row}

    def get_current_path_after_moves(self, original_path: str | Path) -> str:
        """Follow move assignment chain until an existing file is found."""
        current = normalize_media_path(original_path)
        seen: set[str] = set()
        while current not in seen:
            seen.add(current)
            if Path(current).is_file():
                return current
            rows = self.get_rows(
                """
                SELECT dest_path FROM bin_assignments
                WHERE path = :path AND mode = 'move'
                ORDER BY assigned_at DESC
                LIMIT 1
                """,
                {"path": current},
            )
            if not rows or not rows[0] or not rows[0][0]:
                break
            current = normalize_media_path(str(rows[0][0]))
        return current

    def is_reviewed(self, path: str | Path) -> bool:
        """Return whether `path` is marked reviewed."""
        rows = self.get_rows(
            "SELECT 1 FROM reviewed_files WHERE path = :path LIMIT 1",
            {"path": normalize_media_path(path)},
        )
        return bool(rows)

    def list_reviewed_paths(self) -> set[str]:
        """Return all reviewed absolute paths."""
        rows = self.get_rows("SELECT path FROM reviewed_files")
        return {str(row[0]) for row in rows if row and row[0]}

    def mark_deleted(self, path: str | Path, size: int | None = None) -> bool:
        """Record a file moved to the OS trash and mark it reviewed."""
        normalized = normalize_media_path(path)
        size_value = size
        if size_value is None:
            try:
                size_value = Path(normalized).stat().st_size
            except OSError:
                size_value = None
        ok_delete = self.execute_simple_query(
            """
            INSERT INTO deleted_files (path, deleted_at, size)
            VALUES (:path, :deleted_at, :size)
            """,
            {"path": normalized, "deleted_at": _utc_now_iso(), "size": size_value},
        )
        ok_reviewed = self.mark_reviewed(normalized)
        return ok_delete and ok_reviewed

    def mark_reviewed(self, path: str | Path) -> bool:
        """Mark `path` as reviewed (upsert)."""
        normalized = normalize_media_path(path)
        size: int | None = None
        mtime: float | None = None
        try:
            stat = Path(normalized).stat()
            size = int(stat.st_size)
            mtime = float(stat.st_mtime)
        except OSError:
            pass
        query = """
            INSERT INTO reviewed_files (path, reviewed_at, size, mtime)
            VALUES (:path, :reviewed_at, :size, :mtime)
            ON CONFLICT(path) DO UPDATE SET
                reviewed_at = excluded.reviewed_at,
                size = COALESCE(excluded.size, reviewed_files.size),
                mtime = COALESCE(excluded.mtime, reviewed_files.mtime)
        """
        return self.execute_simple_query(
            query,
            {
                "path": normalized,
                "reviewed_at": _utc_now_iso(),
                "size": size,
                "mtime": mtime,
            },
        )

    def path_was_moved(self, path: str | Path) -> bool:
        """Return whether `path` was a source or destination of a prior move."""
        normalized = normalize_media_path(path)
        rows = self.get_rows(
            """
            SELECT 1 FROM bin_assignments
            WHERE mode = 'move' AND (path = :path OR dest_path = :path)
            LIMIT 1
            """,
            {"path": normalized},
        )
        return bool(rows)

    def reviewed_count(self) -> int:
        """Return number of reviewed files."""
        rows = self.get_rows("SELECT COUNT(*) FROM reviewed_files")
        if not rows or not rows[0]:
            return 0
        return int(rows[0][0] or 0)

    def unmark_reviewed(self, path: str | Path) -> bool:
        """Remove reviewed mark for `path`."""
        return self.execute_simple_query(
            "DELETE FROM reviewed_files WHERE path = :path",
            {"path": normalize_media_path(path)},
        )


def normalize_media_path(path: str | Path) -> str:
    """Return a stable absolute path string for DB keys."""
    return str(Path(path).expanduser().resolve())


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()
