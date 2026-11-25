"""SQLite helpers for the Beat Saber tracker."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path

from harrix_swiss_knife.apps.common.qt_database_manager_base import QtSqliteDatabaseManagerBase
from harrix_swiss_knife.beat_saber_saves.ingest import STANDARD_DIFFICULTIES
from harrix_swiss_knife.beat_saber_saves.report import DIFFICULTY_NAMES


class DatabaseManager(QtSqliteDatabaseManagerBase):
    """Beat Saber tracker database (Qt connection + sqlite3 query helpers)."""

    def __init__(self, db_filename: str) -> None:
        """Open the tracker database at `db_filename`."""
        super().__init__(prefix="beat_saber_db", db_filename=db_filename)

    @property
    def db_path(self) -> Path:
        """Return the SQLite file path."""
        return Path(self._db_filename)

    def is_empty_tracker(self) -> bool:
        """Return `True` when catalog and clears are empty (first-run seed needed)."""
        with sqlite3.connect(self.db_path) as conn:
            songs = conn.execute("SELECT COUNT(*) FROM songs").fetchone()
            clears = conn.execute("SELECT COUNT(*) FROM clears_current").fetchone()
        return int(songs[0] if songs else 0) == 0 and int(clears[0] if clears else 0) == 0

    def list_clears(self, *, source: str, search: str) -> list[tuple[str, ...]]:
        """Return current clears rows for the Clears tab."""
        needle = search.strip().casefold()
        sql = """
            SELECT COALESCE(s.title, c.level_id) AS title,
                   COALESCE(s.pack, ''),
                   c.source,
                   c.characteristic,
                   c.difficulty,
                   c.rank_name,
                   c.full_combo,
                   c.high_score,
                   c.play_count,
                   c.observed_at
            FROM clears_current c
            LEFT JOIN songs s ON s.level_id = c.level_id
            WHERE c.level_id NOT LIKE 'custom_level_%'
        """
        params: list[object] = []
        if source in {"pc", "quest"}:
            sql += " AND c.source = ?"
            params.append(source)
        sql += " ORDER BY title COLLATE NOCASE, c.difficulty, c.source"
        with sqlite3.connect(self.db_path) as conn:
            raw = conn.execute(sql, params).fetchall()
        rows: list[tuple[str, ...]] = []
        for (
            title,
            pack,
            src,
            characteristic,
            difficulty,
            rank_name,
            full_combo,
            high_score,
            play_count,
            observed,
        ) in raw:
            if needle and needle not in str(title).casefold() and needle not in str(pack).casefold():
                continue
            diff_name = (
                DIFFICULTY_NAMES[int(difficulty)] if 0 <= int(difficulty) < len(DIFFICULTY_NAMES) else str(difficulty)
            )
            rows.append(
                (
                    str(title),
                    str(pack),
                    str(src),
                    str(characteristic),
                    diff_name,
                    str(rank_name),
                    "yes" if int(full_combo) else "—",
                    str(high_score),
                    str(play_count),
                    str(observed),
                )
            )
        return rows

    def list_compare(self, *, difficulty: int | None, search: str) -> list[tuple[str, ...]]:
        """Return compare rows: title, pack, diff, pc_rank, pc_fc, quest_rank, quest_fc, verdict."""
        diffs = STANDARD_DIFFICULTIES if difficulty is None else (difficulty,)
        needle = search.strip().casefold()
        rows: list[tuple[str, ...]] = []
        with sqlite3.connect(self.db_path) as conn:
            songs = conn.execute(
                "SELECT level_id, title, pack FROM songs WHERE is_official = 1 ORDER BY title COLLATE NOCASE"
            ).fetchall()
            clears = conn.execute(
                """
                SELECT level_id, difficulty, source, full_combo, rank_name, max_rank
                FROM clears_current
                WHERE characteristic = 'Standard' AND level_id NOT LIKE 'custom_level_%'
                """
            ).fetchall()

        lookup: dict[tuple[str, int, str], tuple[str, int, int]] = {}
        for level_id, diff, src, full_combo, rank_name, max_rank in clears:
            lookup[(str(level_id), int(diff), str(src))] = (str(rank_name), int(full_combo), int(max_rank))

        for level_id, title, pack in songs:
            if needle and needle not in str(title).casefold() and needle not in str(pack).casefold():
                continue
            for diff in diffs:
                pc = lookup.get((str(level_id), int(diff), "pc"))
                quest = lookup.get((str(level_id), int(diff), "quest"))
                if pc is None and quest is None:
                    continue
                pc_rank = pc[0] if pc else "—"
                pc_fc = "yes" if pc and pc[1] else "—"
                quest_rank = quest[0] if quest else "—"
                quest_fc = "yes" if quest and quest[1] else "—"
                verdict = _compare_verdict(pc, quest)
                rows.append(
                    (
                        str(title),
                        str(pack),
                        DIFFICULTY_NAMES[diff],
                        pc_rank,
                        pc_fc,
                        quest_rank,
                        quest_fc,
                        verdict,
                    )
                )
        return rows

    def list_history(self, *, search: str, limit: int = 500) -> list[tuple[str, ...]]:
        """Return recent history rows."""
        needle = search.strip().casefold()
        with sqlite3.connect(self.db_path) as conn:
            raw = conn.execute(
                """
                SELECT COALESCE(s.title, h.level_id) AS title,
                       COALESCE(s.pack, ''),
                       h.source,
                       h.characteristic,
                       h.difficulty,
                       h.rank_name,
                       h.full_combo,
                       h.high_score,
                       h.observed_at
                FROM clears_history h
                LEFT JOIN songs s ON s.level_id = h.level_id
                WHERE h.level_id NOT LIKE 'custom_level_%'
                ORDER BY h.observed_at DESC, h._id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        rows: list[tuple[str, ...]] = []
        for title, pack, src, characteristic, difficulty, rank_name, full_combo, high_score, observed in raw:
            if needle and needle not in str(title).casefold() and needle not in str(pack).casefold():
                continue
            diff_name = (
                DIFFICULTY_NAMES[int(difficulty)] if 0 <= int(difficulty) < len(DIFFICULTY_NAMES) else str(difficulty)
            )
            rows.append(
                (
                    str(observed),
                    str(title),
                    str(pack),
                    str(src),
                    str(characteristic),
                    diff_name,
                    str(rank_name),
                    "yes" if int(full_combo) else "—",
                    str(high_score),
                )
            )
        return rows

    def list_missing(
        self,
        *,
        source: str,
        difficulty: int | None,
        require_fc: bool,
        search: str,
    ) -> list[tuple[str, str, str, str, str]]:
        """Return missing official Standard rows: title, pack, diff, status, level_id."""
        diffs = STANDARD_DIFFICULTIES if difficulty is None else (difficulty,)
        needle = search.strip().casefold()
        rows: list[tuple[str, str, str, str, str]] = []
        with sqlite3.connect(self.db_path) as conn:
            songs = conn.execute(
                "SELECT level_id, title, pack FROM songs WHERE is_official = 1 ORDER BY title COLLATE NOCASE"
            ).fetchall()
            clears = conn.execute(
                """
                SELECT level_id, difficulty, source, full_combo, rank_name
                FROM clears_current
                WHERE characteristic = 'Standard' AND level_id NOT LIKE 'custom_level_%'
                """
            ).fetchall()

        by_key: dict[tuple[str, int], list[tuple[str, int, str]]] = {}
        for level_id, diff, src, full_combo, rank_name in clears:
            by_key.setdefault((str(level_id), int(diff)), []).append((str(src), int(full_combo), str(rank_name)))

        for level_id, title, pack in songs:
            if needle and needle not in str(title).casefold() and needle not in str(pack).casefold():
                continue
            for diff in diffs:
                entries = by_key.get((str(level_id), int(diff)), [])
                status = _missing_status(entries, source=source, require_fc=require_fc)
                if status is None:
                    continue
                rows.append((str(title), str(pack), DIFFICULTY_NAMES[diff], status, str(level_id)))
        return rows

    def needs_first_run_seed(self) -> bool:
        """Return `True` when no sync has completed yet (retry seed after a failed first open)."""
        with sqlite3.connect(self.db_path) as conn:
            sync_runs = conn.execute("SELECT COUNT(*) FROM sync_runs").fetchone()
        return int(sync_runs[0] if sync_runs else 0) == 0

    def summary_stats(self) -> SummaryStats:
        """Return aggregate counts for the summary label."""
        with sqlite3.connect(self.db_path) as conn:
            official = conn.execute("SELECT COUNT(*) FROM songs WHERE is_official = 1").fetchone()
            clears_pc = conn.execute(
                "SELECT COUNT(*) FROM clears_current WHERE source = 'pc' AND level_id NOT LIKE 'custom_level_%'"
            ).fetchone()
            clears_quest = conn.execute(
                "SELECT COUNT(*) FROM clears_current WHERE source = 'quest' AND level_id NOT LIKE 'custom_level_%'"
            ).fetchone()
            fc_pc = conn.execute(
                "SELECT COUNT(*) FROM clears_current WHERE source = 'pc' AND full_combo = 1 "
                "AND level_id NOT LIKE 'custom_level_%'"
            ).fetchone()
            fc_quest = conn.execute(
                "SELECT COUNT(*) FROM clears_current WHERE source = 'quest' AND full_combo = 1 "
                "AND level_id NOT LIKE 'custom_level_%'"
            ).fetchone()
            sync_runs = conn.execute("SELECT COUNT(*) FROM sync_runs").fetchone()
            missing = len(self.list_missing(source="best", difficulty=None, require_fc=False, search=""))
        return SummaryStats(
            official_songs=int(official[0] if official else 0),
            clears_pc=int(clears_pc[0] if clears_pc else 0),
            clears_quest=int(clears_quest[0] if clears_quest else 0),
            fc_pc=int(fc_pc[0] if fc_pc else 0),
            fc_quest=int(fc_quest[0] if fc_quest else 0),
            missing_standard=missing,
            sync_runs=int(sync_runs[0] if sync_runs else 0),
        )


@dataclass(frozen=True, slots=True)
class SummaryStats:
    """Header counts for the tracker window."""

    official_songs: int
    clears_pc: int
    clears_quest: int
    fc_pc: int
    fc_quest: int
    missing_standard: int
    sync_runs: int


def _compare_verdict(
    pc: tuple[str, int, int] | None,
    quest: tuple[str, int, int] | None,
) -> str:
    if pc is None and quest is None:
        return "missing"
    if pc is None:
        return "Quest only"
    if quest is None:
        return "PC only"
    if pc[2] == quest[2] and pc[1] == quest[1]:
        return "equal"
    if pc[2] > quest[2] or (pc[2] == quest[2] and pc[1] > quest[1]):
        return "PC better"
    if quest[2] > pc[2] or (quest[2] == pc[2] and quest[1] > pc[1]):
        return "Quest better"
    return "different"


def _missing_status(
    entries: list[tuple[str, int, str]],
    *,
    source: str,
    require_fc: bool,
) -> str | None:
    """Return status text if missing for the filter, else `None`."""
    if source == "pc":
        relevant = [e for e in entries if e[0] == "pc"]
    elif source == "quest":
        relevant = [e for e in entries if e[0] == "quest"]
    else:
        relevant = entries

    if not relevant:
        return "not played"

    if require_fc and not any(e[1] for e in relevant):
        ranks = ", ".join(sorted({f"{e[0]}:{e[2]}" for e in relevant}))
        return f"no FC ({ranks})"
    if require_fc:
        return None
    return None
