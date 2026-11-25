"""Tests for Beat Saber tracker ingest and missing queries."""

from __future__ import annotations

import json
import sqlite3
import zipfile
from pathlib import Path

from harrix_swiss_knife.beat_saber_saves.ingest import ingest_backup_zip, ingest_player_data, seed_official_catalog


def test_ingest_backup_zip_uses_manifest_source(tmp_path: Path) -> None:
    db_path = _create_db(tmp_path)
    seed_official_catalog(db_path)
    player = tmp_path / "PlayerData.dat"
    _write_player_data(player)
    zip_path = tmp_path / "beat-saber-test.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("manifest.json", json.dumps({"app": "beat-saber", "source": "quest"}))
        zf.write(player, arcname="saves/PlayerData.dat")

    result = ingest_backup_zip(db_path, zip_path, seed_catalog=False)
    assert result.ok
    assert result.source == "quest"

    with sqlite3.connect(db_path) as conn:
        row = conn.execute("SELECT source FROM clears_current WHERE level_id = 'EnterSandman'").fetchone()
    assert row == ("quest",)


def test_ingest_creates_history_and_missing(tmp_path: Path) -> None:
    db_path = _create_db(tmp_path)
    seed = seed_official_catalog(db_path)
    assert seed.ok

    player = tmp_path / "PlayerData.dat"
    _write_player_data(player, rank=6, full_combo=True, score=200)
    first = ingest_player_data(
        db_path,
        player,
        source="pc",
        observed_at="2026-11-25T10:00:00+03:00",
        seed_catalog=False,
    )
    assert first.ok
    assert first.clears_inserted == 1
    assert first.history_rows == 1

    _write_player_data(player, rank=5, full_combo=False, score=150)
    second = ingest_player_data(
        db_path,
        player,
        source="pc",
        observed_at="2026-11-26T10:00:00+03:00",
        seed_catalog=False,
    )
    assert second.ok
    assert second.clears_updated == 1
    assert second.history_rows == 1

    with sqlite3.connect(db_path) as conn:
        history = conn.execute("SELECT COUNT(*) FROM clears_history").fetchone()
        current = conn.execute(
            "SELECT rank_name, full_combo FROM clears_current WHERE level_id = ? AND difficulty = 2 AND source = 'pc'",
            ("EnterSandman",),
        ).fetchone()
        missing_expert_plus = conn.execute(
            "SELECT 1 FROM song_modes m "
            "WHERE m.level_id = 'EnterSandman' AND m.characteristic = 'Standard' AND m.difficulty = 4 "
            "AND NOT EXISTS ("
            " SELECT 1 FROM clears_current c "
            " WHERE c.level_id = m.level_id AND c.characteristic = m.characteristic "
            " AND c.difficulty = m.difficulty AND c.source = 'pc'"
            ")"
        ).fetchone()
    assert history is not None
    assert int(history[0]) == 2
    assert current == ("S", 0)
    assert missing_expert_plus is not None


def _create_db(tmp_path: Path) -> Path:
    recover = Path("src/harrix_swiss_knife/apps/beat_saber/recover.sql")
    db_path = tmp_path / "beat_saber.db"
    sql = recover.read_text(encoding="utf-8")
    with sqlite3.connect(db_path) as conn:
        conn.executescript(sql)
        conn.commit()
    return db_path


def _write_player_data(path: Path, *, rank: int = 6, full_combo: bool = True, score: int = 100) -> None:
    path.write_text(
        json.dumps(
            {
                "localPlayers": [
                    {
                        "levelsStatsData": [
                            {
                                "levelId": "EnterSandman",
                                "difficulty": 2,
                                "beatmapCharacteristicName": "Standard",
                                "highScore": score,
                                "maxCombo": 10,
                                "fullCombo": full_combo,
                                "maxRank": rank,
                                "validScore": True,
                                "playCount": 1,
                            }
                        ]
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
