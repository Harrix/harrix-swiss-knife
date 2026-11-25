"""Ingest Beat Saber clears into the tracker SQLite database."""

from __future__ import annotations

import json
import sqlite3
import zipfile
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from harrix_swiss_knife.beat_saber_saves.catalog import load_official_songs
from harrix_swiss_knife.beat_saber_saves.report import LevelClear, load_level_clears

STANDARD_DIFFICULTIES: tuple[int, ...] = (0, 1, 2, 3, 4)
CUSTOM_LEVEL_PREFIX = "custom_level_"


@dataclass
class IngestResult:
    """Outcome of one ingest / seed operation."""

    ok: bool
    source: str = ""
    observed_at: str = ""
    sync_run_id: int | None = None
    clears_seen: int = 0
    clears_inserted: int = 0
    clears_updated: int = 0
    history_rows: int = 0
    songs_upserted: int = 0
    message: str = ""
    lines: list[str] = field(default_factory=list)


def ingest_backup_folder(db_path: Path | str, folder: Path | str, *, seed_catalog: bool = True) -> IngestResult:
    """Ingest all `beat-saber-*.zip` files under a folder (oldest first)."""
    root = Path(folder)
    if not root.is_dir():
        return IngestResult(ok=False, message=f"Backup folder not found: `{root}`")
    zips = sorted(root.glob("beat-saber-*.zip"), key=lambda p: p.stat().st_mtime)
    if not zips:
        return IngestResult(ok=False, message=f"No beat-saber-*.zip in `{root}`")

    if seed_catalog:
        seed_official_catalog(db_path)

    total = IngestResult(ok=True, message="")
    lines: list[str] = []
    for zip_path in zips:
        one = ingest_backup_zip(db_path, zip_path, seed_catalog=False)
        lines.append(f"{zip_path.name}: {one.message}")
        if not one.ok:
            total.ok = False
            continue
        total.clears_seen += one.clears_seen
        total.clears_inserted += one.clears_inserted
        total.clears_updated += one.clears_updated
        total.history_rows += one.history_rows
    total.lines = lines
    total.message = f"Imported {len(zips)} backup ZIP(s)."
    return total


def ingest_backup_zip(
    db_path: Path | str,
    zip_path: Path | str,
    *,
    source_override: str | None = None,
    seed_catalog: bool = True,
) -> IngestResult:
    """Ingest `PlayerData.dat` from an HSK Beat Saber backup ZIP."""
    zpath = Path(zip_path)
    if not zpath.is_file():
        return IngestResult(ok=False, message=f"ZIP not found: `{zpath}`")

    observed = iso_from_mtime(zpath)
    source = source_override or "zip"
    try:
        with zipfile.ZipFile(zpath, "r") as zf:
            names = set(zf.namelist())
            manifest_name = "manifest.json" if "manifest.json" in names else None
            if manifest_name:
                try:
                    manifest = json.loads(zf.read(manifest_name).decode("utf-8"))
                    if isinstance(manifest, dict) and not source_override:
                        raw_source = str(manifest.get("source") or "").strip().lower()
                        if raw_source in {"pc", "quest", "zip"}:
                            source = raw_source
                except (UnicodeDecodeError, json.JSONDecodeError, OSError):
                    pass
            member = _player_data_member(names)
            if member is None:
                return IngestResult(ok=False, message=f"No PlayerData.dat in `{zpath.name}`")
            payload = zf.read(member)
    except (OSError, zipfile.BadZipFile) as exc:
        return IngestResult(ok=False, message=f"Could not read ZIP: {exc}")

    tmp = Path(db_path).parent / f".hsk-bs-ingest-{zpath.stem}.dat"
    try:
        tmp.write_bytes(payload)
        return ingest_player_data(
            db_path,
            tmp,
            source=source,
            observed_at=observed,
            backup_path=str(zpath),
            note=f"from {zpath.name}",
            seed_catalog=seed_catalog,
        )
    finally:
        tmp.unlink(missing_ok=True)


def ingest_player_data(
    db_path: Path | str,
    player_data_path: Path | str,
    *,
    source: str,
    observed_at: str | None = None,
    backup_path: str | None = None,
    note: str = "",
    seed_catalog: bool = True,
) -> IngestResult:
    """Parse `PlayerData.dat` and upsert clears for `source` (`pc` / `quest` / `zip`)."""
    path = Path(db_path)
    player_path = Path(player_data_path)
    observed = observed_at or iso_now()
    if seed_catalog:
        seed_official_catalog(path)

    clears, error = load_level_clears(player_path)
    if error:
        return IngestResult(ok=False, source=source, observed_at=observed, message=error)

    with sqlite3.connect(path) as conn:
        sync_run_id = _insert_sync_run(conn, source=source, observed_at=observed, backup_path=backup_path, note=note)
        result = _apply_clears(conn, clears, source=source, observed_at=observed, sync_run_id=sync_run_id)
        conn.commit()

    result.ok = True
    result.source = source
    result.observed_at = observed
    result.sync_run_id = sync_run_id
    result.message = (
        f"Ingested {result.clears_seen} clears from `{source}` "
        f"(+{result.clears_inserted} / ~{result.clears_updated}, history {result.history_rows})."
    )
    return result


def iso_from_mtime(path: Path) -> str:
    """Return ISO timestamp from a file's mtime."""
    stamp = datetime.fromtimestamp(path.stat().st_mtime).astimezone()
    return stamp.isoformat(timespec="seconds")


def iso_now() -> str:
    """Return current local ISO timestamp with offset."""
    return datetime.now(UTC).astimezone().isoformat(timespec="seconds")


def seed_official_catalog(db_path: Path | str) -> IngestResult:
    """Upsert official songs and Standard Easy — Expert+ modes."""
    songs = load_official_songs()
    if not songs:
        return IngestResult(ok=False, message="Official catalog is empty.")
    path = Path(db_path)
    with sqlite3.connect(path) as conn:
        songs_upserted = _upsert_songs(conn, songs)
        modes = 0
        for song in songs:
            modes += _ensure_standard_modes(conn, song["level_id"])
        conn.commit()
    return IngestResult(
        ok=True,
        songs_upserted=songs_upserted,
        message=f"Catalog: {songs_upserted} songs, {modes} Standard modes ensured.",
        lines=[f"Upserted {songs_upserted} official songs."],
    )


def _apply_clears(
    conn: sqlite3.Connection,
    clears: list[LevelClear],
    *,
    source: str,
    observed_at: str,
    sync_run_id: int,
) -> IngestResult:
    result = IngestResult(ok=True, clears_seen=len(clears))
    for clear in clears:
        if clear.level_id.startswith(CUSTOM_LEVEL_PREFIX):
            _upsert_song(
                conn,
                level_id=clear.level_id,
                title=clear.display_name,
                pack="Custom",
                is_official=0,
            )
        else:
            _upsert_song(
                conn,
                level_id=clear.level_id,
                title=clear.display_name,
                pack="Official (from saves)",
                is_official=1,
            )
            _ensure_standard_modes(conn, clear.level_id)

        previous = conn.execute(
            """
            SELECT max_rank, full_combo, high_score, play_count, rank_name
            FROM clears_current
            WHERE level_id = ? AND characteristic = ? AND difficulty = ? AND source = ?
            """,
            (clear.level_id, clear.characteristic, clear.difficulty, source),
        ).fetchone()

        changed = previous is None or (
            int(previous[0]) != clear.max_rank
            or bool(previous[1]) != clear.full_combo
            or int(previous[2]) != clear.high_score
            or int(previous[3]) != clear.play_count
        )
        if changed:
            conn.execute(
                """
                INSERT INTO clears_history (
                    level_id, characteristic, difficulty, source,
                    max_rank, rank_name, full_combo, high_score, play_count,
                    observed_at, sync_run_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    clear.level_id,
                    clear.characteristic,
                    clear.difficulty,
                    source,
                    clear.max_rank,
                    clear.rank_name,
                    int(clear.full_combo),
                    clear.high_score,
                    clear.play_count,
                    observed_at,
                    sync_run_id,
                ),
            )
            result.history_rows += 1

        conn.execute(
            """
            INSERT INTO clears_current (
                level_id, characteristic, difficulty, source,
                max_rank, rank_name, full_combo, high_score, play_count,
                observed_at, sync_run_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(level_id, characteristic, difficulty, source) DO UPDATE SET
                max_rank = excluded.max_rank,
                rank_name = excluded.rank_name,
                full_combo = excluded.full_combo,
                high_score = excluded.high_score,
                play_count = excluded.play_count,
                observed_at = excluded.observed_at,
                sync_run_id = excluded.sync_run_id
            """,
            (
                clear.level_id,
                clear.characteristic,
                clear.difficulty,
                source,
                clear.max_rank,
                clear.rank_name,
                int(clear.full_combo),
                clear.high_score,
                clear.play_count,
                observed_at,
                sync_run_id,
            ),
        )
        if previous is None:
            result.clears_inserted += 1
        elif changed:
            result.clears_updated += 1
    return result


def _ensure_standard_modes(conn: sqlite3.Connection, level_id: str) -> int:
    count = 0
    for difficulty in STANDARD_DIFFICULTIES:
        cur = conn.execute(
            """
            INSERT OR IGNORE INTO song_modes (level_id, characteristic, difficulty)
            VALUES (?, 'Standard', ?)
            """,
            (level_id, difficulty),
        )
        count += cur.rowcount
    return count


def _insert_sync_run(
    conn: sqlite3.Connection,
    *,
    source: str,
    observed_at: str,
    backup_path: str | None,
    note: str,
) -> int:
    cur = conn.execute(
        """
        INSERT INTO sync_runs (source, observed_at, backup_path, note)
        VALUES (?, ?, ?, ?)
        """,
        (source, observed_at, backup_path, note),
    )
    return int(cur.lastrowid or 0)


def _player_data_member(names: set[str]) -> str | None:
    candidates = ("saves/PlayerData.dat", "PlayerData.dat", "./PlayerData.dat")
    for name in candidates:
        if name in names:
            return name
    for name in names:
        if Path(name).name == "PlayerData.dat":
            return name
    return None


def _upsert_song(
    conn: sqlite3.Connection,
    *,
    level_id: str,
    title: str,
    pack: str,
    is_official: int,
) -> None:
    existing = conn.execute("SELECT title, pack, is_official FROM songs WHERE level_id = ?", (level_id,)).fetchone()
    if existing is None:
        conn.execute(
            "INSERT INTO songs (level_id, title, pack, is_official) VALUES (?, ?, ?, ?)",
            (level_id, title, pack, is_official),
        )
        return
    # Keep richer catalog title/pack when already official from seed.
    old_title, old_pack, old_official = existing
    new_title = old_title if old_official and old_pack not in {"", "Official (from saves)"} else title
    new_pack = old_pack if old_official and old_pack not in {"", "Official (from saves)"} else pack
    new_official = max(int(old_official), is_official)
    if old_title == new_title and old_pack == new_pack and int(old_official) == new_official:
        return
    conn.execute(
        "UPDATE songs SET title = ?, pack = ?, is_official = ? WHERE level_id = ?",
        (new_title, new_pack, new_official, level_id),
    )


def _upsert_songs(conn: sqlite3.Connection, songs: list[dict[str, str]]) -> int:
    count = 0
    for song in songs:
        before = conn.execute("SELECT 1 FROM songs WHERE level_id = ?", (song["level_id"],)).fetchone()
        conn.execute(
            """
            INSERT INTO songs (level_id, title, pack, is_official)
            VALUES (?, ?, ?, 1)
            ON CONFLICT(level_id) DO UPDATE SET
                title = excluded.title,
                pack = excluded.pack,
                is_official = 1
            """,
            (song["level_id"], song["title"], song["pack"]),
        )
        count += 1 if before is None else 0
    # ON CONFLICT still updates — report total processed as upserted for message clarity
    return len(songs)
