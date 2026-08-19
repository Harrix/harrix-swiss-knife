"""Tests for packing and installing selected private-data parts."""

from __future__ import annotations

import sqlite3
import zipfile
from pathlib import Path

from harrix_swiss_knife.actions.common.private_data import (
    ZIP_API_KEYS_DIR,
    ZIP_CATALOG_NAME,
    ZIP_FITNESS_IMG_DIR,
    PrivateDataSelection,
    collect_fitness_image_files,
    inspect_private_data_zip,
    install_private_data,
    pack_private_data,
    selection_from_part_flags,
)

RECOVER_SQL = Path(__file__).resolve().parents[1] / "src/harrix_swiss_knife/apps/fitness/recover.sql"

_SCHEMA_ONLY_SQL = """
CREATE TABLE "exercises" (
	"_id"	INTEGER,
	"name"	TEXT NOT NULL,
	"unit"	TEXT,
	"is_type_required"	INTEGER NOT NULL DEFAULT 0,
	calories_per_unit REAL DEFAULT 0,
	"name_local"	TEXT,
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


def _insert_exercise(db_path: Path, *, name: str, name_local: str) -> int:
    with sqlite3.connect(str(db_path)) as conn:
        conn.execute(
            """
            INSERT INTO exercises (name, unit, is_type_required, calories_per_unit, name_local)
            VALUES (?, '', 0, 0.5, ?)
            """,
            (name, name_local),
        )
        ex_id = int(conn.execute("SELECT _id FROM exercises WHERE name = ?", (name,)).fetchone()[0])
        conn.commit()
    return ex_id


def _write_avif(path: Path, marker: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"avif-test:" + marker.encode("utf-8"))


def test_selection_from_part_flags_defaults_to_all() -> None:
    """Omitting both flags selects every part."""
    both = selection_from_part_flags(api_keys=False, fitness=False)
    assert both.api_keys
    assert both.fitness
    keys_only = selection_from_part_flags(api_keys=True, fitness=False)
    assert keys_only.api_keys
    assert not keys_only.fitness


def test_collect_fitness_image_files_reports_missing_names(tmp_path: Path) -> None:
    """Pack every file in fitness_img and list catalog names without `{name}.avif`."""
    img_dir = tmp_path / "fitness_img"
    _write_avif(img_dir / "Pull-ups.avif", "pull")
    (img_dir / "notes.txt").write_text("extra", encoding="utf-8")
    files, missing = collect_fitness_image_files(img_dir, ["Pull-ups", "Squats"])
    names = {path.name for path in files}
    assert names == {"Pull-ups.avif", "notes.txt"}
    assert missing == ["Squats"]


def test_pack_api_keys_only_omits_fitness(tmp_path: Path) -> None:
    """Export with only API keys does not include catalog or images."""
    project_root = tmp_path / "src-machine"
    api_dir = project_root / "api-keys"
    api_dir.mkdir(parents=True)
    (api_dir / "openai-api-key.txt").write_text("secret\n", encoding="utf-8")
    (api_dir / "openai-api-key.example.txt").write_text("<YOUR_KEY>\n", encoding="utf-8")
    db_path = tmp_path / "unused" / "fitness.db"
    _create_schema_only_db(db_path)
    _insert_exercise(db_path, name="Pull-ups", name_local="Подтягивания")
    output_zip = tmp_path / "out.zip"
    result = pack_private_data(
        project_root=project_root,
        sqlite_fitness=str(db_path),
        output_zip=output_zip,
        selection=PrivateDataSelection(api_keys=True, fitness=False),
    )
    assert result.api_keys_count == 1
    assert result.fitness_img_count == 0
    assert result.exercises_count == 0
    with zipfile.ZipFile(output_zip) as archive:
        names = archive.namelist()
    assert f"{ZIP_API_KEYS_DIR}/openai-api-key.txt" in names
    assert ZIP_CATALOG_NAME not in names
    assert not any(name.startswith(f"{ZIP_FITNESS_IMG_DIR}/") for name in names)
    present = inspect_private_data_zip(output_zip)
    assert present.api_keys
    assert not present.fitness


def test_pack_fitness_includes_all_folder_images_and_missing_names(tmp_path: Path) -> None:
    """Fitness export copies every fitness_img file and reports catalog names without AVIF."""
    project_root = tmp_path / "src-machine"
    project_root.mkdir()
    db_path = tmp_path / "data" / "fitness.db"
    img_dir = db_path.parent / "fitness_img"
    _create_schema_only_db(db_path)
    _insert_exercise(db_path, name="Pull-ups", name_local="Подтягивания")
    _insert_exercise(db_path, name="Squats", name_local="Приседания")
    _write_avif(img_dir / "Pull-ups.avif", "pull")
    _write_avif(img_dir / "orphan.avif", "orphan")
    output_zip = tmp_path / "fitness.zip"
    result = pack_private_data(
        project_root=project_root,
        sqlite_fitness=str(db_path),
        output_zip=output_zip,
        selection=PrivateDataSelection(api_keys=False, fitness=True),
    )
    assert result.exercises_count == 2
    assert result.fitness_img_count == 2
    assert result.missing_exercise_images == ("Squats",)
    with zipfile.ZipFile(output_zip) as archive:
        names = set(archive.namelist())
    assert ZIP_CATALOG_NAME in names
    assert f"{ZIP_FITNESS_IMG_DIR}/Pull-ups.avif" in names
    assert f"{ZIP_FITNESS_IMG_DIR}/orphan.avif" in names
    assert f"{ZIP_FITNESS_IMG_DIR}/Squats.avif" not in names
    present = inspect_private_data_zip(output_zip)
    assert not present.api_keys
    assert present.fitness


def test_install_overlays_missing_images_next_to_existing(tmp_path: Path) -> None:
    """If the target already has catalog rows but no images, AVIFs are copied in; extras stay."""
    source_root = tmp_path / "source"
    source_root.mkdir()
    source_db = tmp_path / "source-data" / "fitness.db"
    source_img = source_db.parent / "fitness_img"
    _create_schema_only_db(source_db)
    _insert_exercise(source_db, name="Pull-ups", name_local="Подтягивания")
    _insert_exercise(source_db, name="Squats", name_local="Приседания")
    _write_avif(source_img / "Pull-ups.avif", "pull-src")
    _write_avif(source_img / "Squats.avif", "squat-src")
    zip_path = tmp_path / "transfer.zip"
    pack_private_data(
        project_root=source_root,
        sqlite_fitness=str(source_db),
        output_zip=zip_path,
        selection=PrivateDataSelection(api_keys=False, fitness=True),
    )

    target_root = tmp_path / "target"
    target_root.mkdir()
    target_db = tmp_path / "target-data" / "fitness.db"
    target_img = target_db.parent / "fitness_img"
    _create_schema_only_db(target_db)
    pull_id = _insert_exercise(target_db, name="Pull-ups", name_local="old")
    squat_id = _insert_exercise(target_db, name="Squats", name_local="old")
    with sqlite3.connect(str(target_db)) as conn:
        conn.execute(
            "INSERT INTO process (_id_exercises, _id_types, value, date) VALUES (?, -1, '10', '2024-01-01')",
            (pull_id,),
        )
        conn.execute("INSERT INTO weight (value, date) VALUES (80.5, '2024-01-01')")
        conn.commit()
    _write_avif(target_img / "local-only.avif", "keep-me")

    result = install_private_data(
        project_root=target_root,
        sqlite_fitness=str(target_db),
        zip_path=zip_path,
        recover_sql_path=RECOVER_SQL,
        selection=PrivateDataSelection(api_keys=False, fitness=True),
    )
    assert result.fitness_img_count == 2
    assert result.missing_exercise_images == ()
    assert result.catalog_stats.exercises_updated == 2
    assert result.catalog_stats.exercises_inserted == 0
    assert (target_img / "Pull-ups.avif").read_bytes() == b"avif-test:pull-src"
    assert (target_img / "Squats.avif").read_bytes() == b"avif-test:squat-src"
    assert (target_img / "local-only.avif").read_bytes() == b"avif-test:keep-me"
    with sqlite3.connect(str(target_db)) as conn:
        names = {row[0] for row in conn.execute("SELECT name FROM exercises")}
        assert names == {"Pull-ups", "Squats"}
        assert int(conn.execute("SELECT COUNT(*) FROM process").fetchone()[0]) == 1
        assert int(conn.execute("SELECT COUNT(*) FROM weight").fetchone()[0]) == 1
        assert int(conn.execute("SELECT _id FROM exercises WHERE name = 'Pull-ups'").fetchone()[0]) == pull_id
        assert int(conn.execute("SELECT _id FROM exercises WHERE name = 'Squats'").fetchone()[0]) == squat_id
        local_name = conn.execute("SELECT name_local FROM exercises WHERE name = 'Pull-ups'").fetchone()[0]
    assert local_name == "Подтягивания"


def test_install_api_keys_only_does_not_touch_fitness(tmp_path: Path) -> None:
    """API-key import overwrites matching secrets and leaves the fitness DB unused."""
    source_root = tmp_path / "source"
    api_dir = source_root / "api-keys"
    api_dir.mkdir(parents=True)
    (api_dir / "openai-api-key.txt").write_text("from-zip\n", encoding="utf-8")
    zip_path = tmp_path / "keys.zip"
    pack_private_data(
        project_root=source_root,
        sqlite_fitness="",
        output_zip=zip_path,
        selection=PrivateDataSelection(api_keys=True, fitness=False),
    )
    target_root = tmp_path / "target"
    dest_api = target_root / "api-keys"
    dest_api.mkdir(parents=True)
    (dest_api / "openai-api-key.txt").write_text("old\n", encoding="utf-8")
    (dest_api / "keep-me.txt").write_text("stay\n", encoding="utf-8")
    result = install_private_data(
        project_root=target_root,
        sqlite_fitness="",
        zip_path=zip_path,
        recover_sql_path=RECOVER_SQL,
        selection=PrivateDataSelection(api_keys=True, fitness=False),
    )
    assert result.api_keys_count == 1
    assert result.fitness_db_path is None
    assert (dest_api / "openai-api-key.txt").read_text(encoding="utf-8") == "from-zip\n"
    assert (dest_api / "keep-me.txt").read_text(encoding="utf-8") == "stay\n"
