"""SQLite access for snippet items and per-zone sort settings."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from harrix_swiss_knife.apps.common.qt_database_manager_base import QtSqliteDatabaseManagerBase
from harrix_swiss_knife.apps.snippets.constants import DEFAULT_SORT_MODE, SORT_MODES, SortMode, ZoneName

if TYPE_CHECKING:
    from collections.abc import Sequence


class DatabaseManager(QtSqliteDatabaseManagerBase):
    """Manage the connection and operations for the snippets database."""

    def __init__(self, db_filename: str) -> None:
        """Open a connection to an SQLite database stored in `db_filename`."""
        super().__init__(prefix="snippets_db", db_filename=db_filename)

    def add_item(self, zone: str, value: str, hint: str = "") -> int | None:
        """Insert one item and return its `_id`."""
        created_at = utc_now_iso()
        sort_index = self._next_sort_index(zone)
        ok = self.execute_simple_query(
            "INSERT INTO items (zone, value, hint, created_at, last_used_at, sort_index) "
            "VALUES (:zone, :value, :hint, :created_at, NULL, :sort_index)",
            {
                "zone": zone,
                "value": value,
                "hint": hint,
                "created_at": created_at,
                "sort_index": sort_index,
            },
        )
        if not ok:
            return None
        rows = self.get_rows("SELECT last_insert_rowid()")
        if not rows or rows[0][0] is None:
            return None
        return int(rows[0][0])

    def add_items(self, zone: str, items: Sequence[tuple[str, str]]) -> bool:
        """Insert many `(value, hint)` pairs into `zone`."""
        if not items:
            return True
        try:
            with self.sql_transaction():
                self._insert_zone_items(zone, items)
        except (RuntimeError, OSError, ConnectionError):
            return False
        return True

    def delete_item(self, item_id: int) -> bool:
        """Delete one item by `_id`."""
        return self.execute_simple_query("DELETE FROM items WHERE _id = :id", {"id": item_id})

    def get_item(self, item_id: int) -> SnippetItem | None:
        """Return one item by `_id`."""
        rows = self.get_rows(
            "SELECT _id, zone, value, hint, created_at, last_used_at, sort_index FROM items WHERE _id = :id",
            {"id": item_id},
        )
        if not rows:
            return None
        return _row_to_item(rows[0])

    def get_zone_sort(self, zone: str) -> ZoneSort:
        """Return the stored sort settings for `zone`."""
        rows = self.get_rows(
            "SELECT mode, descending FROM zone_sort WHERE zone = :zone",
            {"zone": zone},
        )
        if not rows:
            return ZoneSort(mode=DEFAULT_SORT_MODE, descending=False)
        mode_raw = str(rows[0][0] or DEFAULT_SORT_MODE)
        mode: SortMode = mode_raw if mode_raw in SORT_MODES else DEFAULT_SORT_MODE
        return ZoneSort(mode=mode, descending=bool(int(rows[0][1] or 0)))

    def list_items(self, zone: str) -> list[SnippetItem]:
        """Return all items in `zone`."""
        rows = self.get_rows(
            "SELECT _id, zone, value, hint, created_at, last_used_at, sort_index "
            "FROM items WHERE zone = :zone ORDER BY sort_index ASC, _id ASC",
            {"zone": zone},
        )
        return [_row_to_item(row) for row in rows]

    def mark_used(self, item_id: int) -> bool:
        """Set `last_used_at` to now."""
        return self.execute_simple_query(
            "UPDATE items SET last_used_at = :used_at WHERE _id = :id",
            {"used_at": utc_now_iso(), "id": item_id},
        )

    def replace_zone_items(self, zone: str, items: Sequence[tuple[str, str]]) -> bool:
        """Replace every item in `zone` with `items`, keeping new created timestamps."""
        try:
            with self.sql_transaction():
                self._replace_zone_items(zone, items)
        except (RuntimeError, OSError, ConnectionError):
            return False
        return True

    def set_zone_sort(self, zone: ZoneName | str, mode: SortMode | str, *, descending: bool) -> bool:
        """Persist sort settings for `zone`."""
        return self.execute_simple_query(
            "INSERT INTO zone_sort (zone, mode, descending) VALUES (:zone, :mode, :descending) "
            "ON CONFLICT(zone) DO UPDATE SET mode = :mode, descending = :descending",
            {"zone": zone, "mode": mode, "descending": 1 if descending else 0},
        )

    def update_item(self, item_id: int, value: str, hint: str) -> bool:
        """Update value and hint for one item."""
        return self.execute_simple_query(
            "UPDATE items SET value = :value, hint = :hint WHERE _id = :id",
            {"value": value, "hint": hint, "id": item_id},
        )

    def _insert_zone_items(self, zone: str, items: Sequence[tuple[str, str]]) -> None:
        for value, hint in items:
            if self.add_item(zone, value, hint) is None:
                msg = "Failed to insert snippet item"
                raise RuntimeError(msg)

    def _next_sort_index(self, zone: str) -> int:
        rows = self.get_rows(
            "SELECT COALESCE(MAX(sort_index), -1) FROM items WHERE zone = :zone",
            {"zone": zone},
        )
        if not rows or rows[0][0] is None:
            return 0
        return _as_int(rows[0][0]) + 1

    def _replace_zone_items(self, zone: str, items: Sequence[tuple[str, str]]) -> None:
        if not self.execute_simple_query("DELETE FROM items WHERE zone = :zone", {"zone": zone}):
            msg = "Failed to clear snippet zone"
            raise RuntimeError(msg)
        self._insert_zone_items(zone, items)


@dataclass(frozen=True)
class SnippetItem:
    """One pasteable item stored in the snippets database."""

    item_id: int
    zone: str
    value: str
    hint: str
    created_at: str
    last_used_at: str | None
    sort_index: int


@dataclass(frozen=True)
class ZoneSort:
    """Persisted sort mode for one zone."""

    mode: SortMode
    descending: bool


def utc_now_iso() -> str:
    """Return the current UTC timestamp in ISO-8601 form."""
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def _as_int(value: object, default: int = 0) -> int:
    if value is None or value == "":
        return default
    if isinstance(value, int):
        return value
    return int(str(value))


def _row_to_item(row: list[object]) -> SnippetItem:
    last_used = row[5]
    last_used_at = None if last_used in (None, "") else str(last_used)
    return SnippetItem(
        item_id=_as_int(row[0]),
        zone=str(row[1]),
        value=str(row[2]),
        hint=str(row[3] or ""),
        created_at=str(row[4]),
        last_used_at=last_used_at,
        sort_index=_as_int(row[6]),
    )
