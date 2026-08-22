"""Tests for fitness catalog export/upsert (no Qt required)."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from harrix_swiss_knife.apps.fitness.catalog_sync import (
    create_empty_fitness_database,
    export_fitness_catalog,
    upsert_fitness_catalog,
)

RECOVER_SQL = Path(__file__).resolve().parents[1] / "src/harrix_swiss_knife/apps/fitness/recover.sql"

# Schema only — tests that need a blank DB must not load the public seed from recover.sql.
_SCHEMA_ONLY_SQL = """
CREATE TABLE "exercises" (
	"_id"	INTEGER,
	"name"	TEXT NOT NULL,
	"unit"	TEXT,
	"is_type_required"	INTEGER NOT NULL DEFAULT 0,
	calories_per_unit REAL DEFAULT 0,
	"name_local"	TEXT,
	"is_favorite"	INTEGER NOT NULL DEFAULT 0,
	PRIMARY KEY("_id" AUTOINCREMENT)
);
CREATE TABLE "process" (
	`_id`	INTEGER PRIMARY KEY AUTOINCREMENT,
	`_id_exercises`	INTEGER NOT NULL,
	`_id_types`	INTEGER NOT NULL,
	`value`	TEXT NOT NULL,
	`date`	TEXT NOT NULL
);
CREATE TABLE `types` (
	`_id`	INTEGER PRIMARY KEY AUTOINCREMENT,
	`_id_exercises`	INTEGER NOT NULL,
	`type`	TEXT NOT NULL,
	calories_modifier REAL DEFAULT 1.0,
	`name_local`	TEXT
);
CREATE TABLE `weight` (
	`_id`	INTEGER PRIMARY KEY AUTOINCREMENT,
	`value`	REAL NOT NULL,
	`date`	TEXT
);
"""


def _create_schema_only_db(db_path: Path) -> Path:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(str(db_path)) as conn:
        conn.executescript(_SCHEMA_ONLY_SQL)
        conn.commit()
    return db_path


def _seed_source_db(db_path: Path) -> None:
    with sqlite3.connect(str(db_path)) as conn:
        conn.execute(
            """
            INSERT INTO exercises (name, unit, is_type_required, calories_per_unit, name_local)
            VALUES ('Pull-ups', '', 1, 0.5, 'Подтягивания')
            """
        )
        ex_id = int(conn.execute("SELECT _id FROM exercises WHERE name = 'Pull-ups'").fetchone()[0])
        conn.execute(
            """
            INSERT INTO types (_id_exercises, type, calories_modifier, name_local)
            VALUES (?, 'Without jerking', 1.2, 'Без рывков')
            """,
            (ex_id,),
        )
        conn.execute(
            """
            INSERT INTO process (_id_exercises, _id_types, value, date)
            VALUES (?, -1, '10', '2024-01-01')
            """,
            (ex_id,),
        )
        conn.execute("INSERT INTO weight (value, date) VALUES (80.5, '2024-01-01')")
        conn.commit()


def test_recover_sql_seeds_base_catalog(tmp_path: Path) -> None:
    """Public recover.sql still includes the base exercise seed."""
    db_path = tmp_path / "fitness.db"
    create_empty_fitness_database(db_path, RECOVER_SQL)
    with sqlite3.connect(str(db_path)) as conn:
        exercise_count = int(conn.execute("SELECT COUNT(*) FROM exercises").fetchone()[0])
        type_count = int(conn.execute("SELECT COUNT(*) FROM types").fetchone()[0])
    assert exercise_count >= 40
    assert type_count >= 50
    assert conn_has_name(db_path, "Pull-ups")


def conn_has_name(db_path: Path, name: str) -> bool:
    with sqlite3.connect(str(db_path)) as conn:
        row = conn.execute("SELECT 1 FROM exercises WHERE name = ?", (name,)).fetchone()
    return row is not None


def test_export_omits_ids_and_workouts(tmp_path: Path) -> None:
    """Catalog export has exercises/types only, without database IDs."""
    db_path = _create_schema_only_db(tmp_path / "fitness.db")
    _seed_source_db(db_path)
    catalog = export_fitness_catalog(db_path)
    assert catalog["version"] == 1
    assert len(catalog["exercises"]) == 1
    exercise = catalog["exercises"][0]
    assert exercise["name"] == "Pull-ups"
    assert "_id" not in exercise
    assert exercise["types"][0]["type"] == "Without jerking"
    assert "process" not in catalog
    assert "weight" not in catalog


def test_upsert_inserts_new_exercises_and_types(tmp_path: Path) -> None:
    """Empty target gains catalog rows from upsert."""
    source = _create_schema_only_db(tmp_path / "source.db")
    target = _create_schema_only_db(tmp_path / "target.db")
    _seed_source_db(source)
    catalog = export_fitness_catalog(source)
    stats = upsert_fitness_catalog(target, catalog)
    assert stats.exercises_inserted == 1
    assert stats.types_inserted == 1
    with sqlite3.connect(str(target)) as conn:
        assert conn.execute("SELECT COUNT(*) FROM exercises").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM types").fetchone()[0] == 1


def test_upsert_updates_existing_preserves_ids_and_process(tmp_path: Path) -> None:
    """Matching names update fields; process/weight and IDs stay intact."""
    db_path = _create_schema_only_db(tmp_path / "fitness.db")
    _seed_source_db(db_path)

    with sqlite3.connect(str(db_path)) as conn:
        ex_id = int(conn.execute("SELECT _id FROM exercises WHERE name = 'Pull-ups'").fetchone()[0])
        type_id = int(conn.execute("SELECT _id FROM types WHERE type = 'Without jerking'").fetchone()[0])
        process_count = int(conn.execute("SELECT COUNT(*) FROM process").fetchone()[0])
        weight_count = int(conn.execute("SELECT COUNT(*) FROM weight").fetchone()[0])

    catalog = {
        "version": 1,
        "exercises": [
            {
                "name": "Pull-ups",
                "unit": "reps",
                "is_type_required": True,
                "calories_per_unit": 0.6,
                "name_local": "Подтягивания (updated)",
                "types": [
                    {
                        "type": "Without jerking",
                        "calories_modifier": 1.3,
                        "name_local": "Без рывков (updated)",
                    },
                    {
                        "type": "Wide grip",
                        "calories_modifier": 1.1,
                        "name_local": "",
                    },
                ],
            }
        ],
    }
    stats = upsert_fitness_catalog(db_path, catalog)
    assert stats.exercises_updated == 1
    assert stats.exercises_inserted == 0
    assert stats.types_updated == 1
    assert stats.types_inserted == 1

    with sqlite3.connect(str(db_path)) as conn:
        row = conn.execute(
            "SELECT _id, unit, calories_per_unit, name_local FROM exercises WHERE name = 'Pull-ups'"
        ).fetchone()
        assert row is not None
        assert int(row[0]) == ex_id
        assert row[1] == "reps"
        assert float(row[2]) == 0.6
        assert row[3] == "Подтягивания (updated)"

        t_row = conn.execute("SELECT _id, calories_modifier FROM types WHERE type = 'Without jerking'").fetchone()
        assert t_row is not None
        assert int(t_row[0]) == type_id
        assert float(t_row[1]) == 1.3

        assert int(conn.execute("SELECT COUNT(*) FROM process").fetchone()[0]) == process_count
        assert int(conn.execute("SELECT COUNT(*) FROM weight").fetchone()[0]) == weight_count
        assert (
            int(conn.execute("SELECT COUNT(*) FROM process WHERE _id_exercises = ?", (ex_id,)).fetchone()[0])
            == process_count
        )


def test_upsert_does_not_delete_local_only_rows(tmp_path: Path) -> None:
    """Exercises present only on the target remain after upsert."""
    db_path = _create_schema_only_db(tmp_path / "fitness.db")
    with sqlite3.connect(str(db_path)) as conn:
        conn.execute(
            """
            INSERT INTO exercises (name, unit, is_type_required, calories_per_unit, name_local)
            VALUES ('Local-only', '', 0, 0.1, '')
            """
        )
        conn.commit()

    catalog = {
        "version": 1,
        "exercises": [
            {
                "name": "Squats",
                "unit": "",
                "is_type_required": False,
                "calories_per_unit": 0.5,
                "name_local": "",
                "types": [],
            }
        ],
    }
    upsert_fitness_catalog(db_path, catalog)
    with sqlite3.connect(str(db_path)) as conn:
        names = {row[0] for row in conn.execute("SELECT name FROM exercises").fetchall()}
    assert names == {"Local-only", "Squats"}
