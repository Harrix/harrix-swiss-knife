"""Tests for packing and installing selected private-data parts."""

from __future__ import annotations

import sqlite3
import zipfile
from pathlib import Path

import pytest

from harrix_swiss_knife.actions.common.private_data import (
    ZIP_API_KEYS_DIR,
    ZIP_CATALOG_NAME,
    ZIP_FINANCE_CATALOG_NAME,
    ZIP_FITNESS_IMG_DIR,
    ZIP_FOOD_CATALOG_NAME,
    PrivateDataSelection,
    collect_fitness_image_files,
    default_private_data_zip_path,
    find_importable_fitness_private_data_zip,
    inspect_private_data_zip,
    install_private_data,
    list_api_key_files_in_zip,
    pack_private_data,
    resolve_api_key_files_for_pack,
    selection_from_part_flags,
)
from harrix_swiss_knife.apps.common.avif_manager import AvifManager

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
    """Omitting every flag selects every part."""
    both = selection_from_part_flags(api_keys=False, fitness=False)
    assert both.api_keys
    assert both.fitness
    assert both.finance
    assert both.food
    keys_only = selection_from_part_flags(api_keys=True, fitness=False)
    assert keys_only.api_keys
    assert not keys_only.fitness
    assert not keys_only.finance
    assert not keys_only.food


def test_avif_manager_has_any_exercise_avif(tmp_path: Path) -> None:
    """Detect at least one `.avif` under fitness_img."""
    manager = AvifManager(tmp_path / "missing")
    assert not manager.has_any_exercise_avif()
    img_dir = tmp_path / "fitness_img"
    img_dir.mkdir()
    manager = AvifManager(img_dir)
    assert not manager.has_any_exercise_avif()
    (img_dir / "Walk.avif").write_bytes(b"x")
    assert manager.has_any_exercise_avif()


def test_find_importable_fitness_private_data_zip(tmp_path: Path) -> None:
    """Offer Transfer private data only when the default ZIP contains fitness parts."""
    project_root = tmp_path / "project"
    project_root.mkdir()
    assert find_importable_fitness_private_data_zip(project_root) is None

    source_root = tmp_path / "source"
    source_root.mkdir()
    source_db = tmp_path / "source-data" / "fitness.db"
    _create_schema_only_db(source_db)
    _insert_exercise(source_db, name="Walk", name_local="Ходьба")
    _write_avif(source_db.parent / "fitness_img" / "Walk.avif", "walk")
    packed = tmp_path / "packed.zip"
    pack_private_data(
        project_root=source_root,
        sqlite_fitness=str(source_db),
        output_zip=packed,
        selection=PrivateDataSelection(api_keys=False, fitness=True),
    )

    default_zip = default_private_data_zip_path(project_root)
    default_zip.parent.mkdir(parents=True)
    default_zip.write_bytes(packed.read_bytes())
    assert find_importable_fitness_private_data_zip(project_root) == default_zip

    keys_only = tmp_path / "keys.zip"
    api_dir = source_root / "api-keys"
    api_dir.mkdir(parents=True)
    (api_dir / "openai-api-key.txt").write_text("secret\n", encoding="utf-8")
    pack_private_data(
        project_root=source_root,
        sqlite_fitness=str(source_db),
        output_zip=keys_only,
        selection=PrivateDataSelection(api_keys=True, fitness=False),
    )
    default_zip.write_bytes(keys_only.read_bytes())
    assert find_importable_fitness_private_data_zip(project_root) is None


def test_collect_fitness_image_files_reports_missing_names(tmp_path: Path) -> None:
    """Pack every file in fitness_img and list catalog names without `{name}.avif`."""
    img_dir = tmp_path / "fitness_img"
    _write_avif(img_dir / "Pull-ups.avif", "pull")
    (img_dir / "notes.txt").write_text("extra", encoding="utf-8")
    files, missing = collect_fitness_image_files(img_dir, ["Pull-ups", "Squats"])
    names = {path.name for path in files}
    assert names == {"Pull-ups.avif", "notes.txt"}
    assert missing == ["Squats"]


def test_collect_fitness_image_files_packs_high_and_requires_root_avif(tmp_path: Path) -> None:
    """High-resolution copies are packed; missing UI files still count as missing."""
    img_dir = tmp_path / "fitness_img"
    _write_avif(img_dir / "Pull-ups.avif", "pull")
    _write_avif(img_dir / "high" / "Pull-ups.avif", "pull-hi")
    _write_avif(img_dir / "high" / "Plank.avif", "plank-only")
    files, missing = collect_fitness_image_files(img_dir, ["Pull-ups", "Plank", "Squats"])
    rels = {path.relative_to(img_dir).as_posix() for path in files}
    assert rels == {"Pull-ups.avif", "high/Pull-ups.avif", "high/Plank.avif"}
    assert missing == ["Plank", "Squats"]


def test_resolve_api_key_files_for_pack_filters_names(tmp_path: Path) -> None:
    """Empty names pack every secret; a list packs only those files."""
    api_dir = tmp_path / "api-keys"
    api_dir.mkdir()
    (api_dir / "openai-api-key.txt").write_text("o\n", encoding="utf-8")
    (api_dir / "bothub-api-key.txt").write_text("b\n", encoding="utf-8")
    (api_dir / "openai-api-key.example.txt").write_text("x\n", encoding="utf-8")
    all_files = resolve_api_key_files_for_pack(api_dir, ())
    assert [path.name for path in all_files] == ["bothub-api-key.txt", "openai-api-key.txt"]
    subset = resolve_api_key_files_for_pack(api_dir, ["openai-api-key.txt"])
    assert [path.name for path in subset] == ["openai-api-key.txt"]
    with pytest.raises(FileNotFoundError, match=r"missing-key\.txt"):
        resolve_api_key_files_for_pack(api_dir, ["missing-key.txt"])


def test_pack_api_keys_subset_omits_other_secrets(tmp_path: Path) -> None:
    """Export can include only the checked API key files."""
    project_root = tmp_path / "src-machine"
    api_dir = project_root / "api-keys"
    api_dir.mkdir(parents=True)
    (api_dir / "openai-api-key.txt").write_text("openai\n", encoding="utf-8")
    (api_dir / "bothub-api-key.txt").write_text("bothub\n", encoding="utf-8")
    (api_dir / "github-token.txt").write_text("github\n", encoding="utf-8")
    db_path = tmp_path / "unused" / "fitness.db"
    _create_schema_only_db(db_path)
    output_zip = tmp_path / "out.zip"
    result = pack_private_data(
        project_root=project_root,
        sqlite_fitness=str(db_path),
        output_zip=output_zip,
        selection=PrivateDataSelection(
            api_keys=True,
            fitness=False,
            api_key_files=("openai-api-key.txt", "github-token.txt"),
        ),
    )
    assert result.api_keys_count == 2
    assert result.api_key_files == ("github-token.txt", "openai-api-key.txt")
    with zipfile.ZipFile(output_zip) as archive:
        names = set(archive.namelist())
    assert f"{ZIP_API_KEYS_DIR}/openai-api-key.txt" in names
    assert f"{ZIP_API_KEYS_DIR}/github-token.txt" in names
    assert f"{ZIP_API_KEYS_DIR}/bothub-api-key.txt" not in names


def test_list_api_key_files_in_zip_skips_examples(tmp_path: Path) -> None:
    """ZIP listing returns secret key names and ignores `*.example.txt`."""
    zip_path = tmp_path / "keys.zip"
    with zipfile.ZipFile(zip_path, "w") as archive:
        archive.writestr(f"{ZIP_API_KEYS_DIR}/openai-api-key.txt", "o\n")
        archive.writestr(f"{ZIP_API_KEYS_DIR}/bothub-api-key.txt", "b\n")
        archive.writestr(f"{ZIP_API_KEYS_DIR}/openai-api-key.example.txt", "x\n")
        archive.writestr(f"{ZIP_FITNESS_IMG_DIR}/Pull-ups.avif", b"avif")
    assert list_api_key_files_in_zip(zip_path) == ["bothub-api-key.txt", "openai-api-key.txt"]


def test_install_api_keys_subset_skips_other_secrets(tmp_path: Path) -> None:
    """Import can copy only the checked API key files from the ZIP."""
    source_root = tmp_path / "src-machine"
    api_dir = source_root / "api-keys"
    api_dir.mkdir(parents=True)
    (api_dir / "openai-api-key.txt").write_text("openai\n", encoding="utf-8")
    (api_dir / "bothub-api-key.txt").write_text("bothub\n", encoding="utf-8")
    db_path = tmp_path / "unused" / "fitness.db"
    _create_schema_only_db(db_path)
    zip_path = tmp_path / "out.zip"
    pack_private_data(
        project_root=source_root,
        sqlite_fitness=str(db_path),
        output_zip=zip_path,
        selection=PrivateDataSelection(api_keys=True, fitness=False),
    )
    target_root = tmp_path / "target"
    target_root.mkdir()
    result = install_private_data(
        project_root=target_root,
        sqlite_fitness=str(db_path),
        zip_path=zip_path,
        recover_sql_path=RECOVER_SQL,
        selection=PrivateDataSelection(
            api_keys=True,
            fitness=False,
            api_key_files=("openai-api-key.txt",),
        ),
    )
    assert result.api_keys_count == 1
    dest = target_root / "api-keys"
    assert (dest / "openai-api-key.txt").read_text(encoding="utf-8") == "openai\n"
    assert not (dest / "bothub-api-key.txt").exists()


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


def test_pack_and_install_fitness_copies_high_resolution_images(tmp_path: Path) -> None:
    """OnTransferPrivateData packs and overlays `fitness_img/high/{name}.avif`."""
    source_root = tmp_path / "source"
    source_root.mkdir()
    source_db = tmp_path / "source-data" / "fitness.db"
    source_img = source_db.parent / "fitness_img"
    _create_schema_only_db(source_db)
    _insert_exercise(source_db, name="Walk", name_local="Ходьба")
    _write_avif(source_img / "Walk.avif", "walk-small")
    _write_avif(source_img / "high" / "Walk.avif", "walk-high")
    zip_path = tmp_path / "transfer.zip"
    packed = pack_private_data(
        project_root=source_root,
        sqlite_fitness=str(source_db),
        output_zip=zip_path,
        selection=PrivateDataSelection(api_keys=False, fitness=True),
    )
    assert packed.fitness_img_count == 2
    with zipfile.ZipFile(zip_path) as archive:
        names = set(archive.namelist())
    assert f"{ZIP_FITNESS_IMG_DIR}/Walk.avif" in names
    assert f"{ZIP_FITNESS_IMG_DIR}/high/Walk.avif" in names

    target_root = tmp_path / "target"
    target_root.mkdir()
    target_db = tmp_path / "target-data" / "fitness.db"
    target_img = target_db.parent / "fitness_img"
    _create_schema_only_db(target_db)
    result = install_private_data(
        project_root=target_root,
        sqlite_fitness=str(target_db),
        zip_path=zip_path,
        recover_sql_path=RECOVER_SQL,
        selection=PrivateDataSelection(api_keys=False, fitness=True),
    )
    assert result.fitness_img_count == 2
    assert (target_img / "Walk.avif").read_bytes() == b"avif-test:walk-small"
    assert (target_img / "high" / "Walk.avif").read_bytes() == b"avif-test:walk-high"


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
    leftover_dirs = [
        path for path in output_zip.parent.iterdir() if path.is_dir() and path.name.startswith(".hsk-private-data-")
    ]
    assert leftover_dirs == []


def test_pack_removes_leftover_adjacent_stage_folder(tmp_path: Path) -> None:
    """A previous empty `.hsk-private-data-pack-*` folder next to the ZIP must go."""
    leftover = tmp_path / ".hsk-private-data-pack-private-data-harrix-swiss-knife"
    leftover.mkdir()
    project_root = tmp_path / "src-machine"
    api_dir = project_root / "api-keys"
    api_dir.mkdir(parents=True)
    (api_dir / "openai-api-key.txt").write_text("secret\n", encoding="utf-8")
    db_path = tmp_path / "unused" / "fitness.db"
    _create_schema_only_db(db_path)
    output_zip = tmp_path / "private-data-harrix-swiss-knife.zip"
    pack_private_data(
        project_root=project_root,
        sqlite_fitness=str(db_path),
        output_zip=output_zip,
        selection=PrivateDataSelection(api_keys=True, fitness=False),
    )
    assert not leftover.exists()
    leftover_dirs = [
        path for path in tmp_path.iterdir() if path.is_dir() and path.name.startswith(".hsk-private-data-")
    ]
    assert leftover_dirs == []


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


_FINANCE_SCHEMA_SQL = """
CREATE TABLE currencies (
    _id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    symbol TEXT NOT NULL,
    subdivision INTEGER NOT NULL DEFAULT 100,
    ticker TEXT
);
CREATE TABLE categories (
    _id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type INTEGER NOT NULL,
    icon TEXT,
    name_local TEXT
);
CREATE TABLE standard_items (
    _id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    name_en TEXT,
    _id_categories INTEGER NOT NULL
);
CREATE TABLE transactions (
    _id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount INTEGER NOT NULL,
    description TEXT NOT NULL,
    _id_categories INTEGER NOT NULL,
    _id_currencies INTEGER NOT NULL,
    date TEXT NOT NULL
);
"""

_FOOD_SCHEMA_SQL = """
CREATE TABLE food_items (
    _id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    name_en TEXT,
    is_drink INTEGER NOT NULL DEFAULT 0,
    calories_per_100g REAL,
    default_portion_weight REAL,
    default_portion_calories REAL
);
CREATE TABLE food_log (
    _id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    weight REAL,
    portion_calories REAL,
    calories_per_100g REAL,
    name TEXT,
    name_en TEXT,
    is_drink INTEGER NOT NULL DEFAULT 0
);
"""


def _create_finance_db(db_path: Path) -> Path:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(str(db_path)) as conn:
        conn.executescript(_FINANCE_SCHEMA_SQL)
        conn.execute("INSERT INTO currencies (code, name, symbol, subdivision) VALUES ('USD', 'US Dollar', '$', 100)")
        conn.execute("INSERT INTO categories (name, type, icon, name_local) VALUES ('Food', 0, '🍔', 'Еда')")
        category_id = int(conn.execute("SELECT _id FROM categories WHERE name = 'Food'").fetchone()[0])
        conn.execute(
            "INSERT INTO standard_items (name, name_en, _id_categories) VALUES ('Вода', 'Water', ?)",
            (category_id,),
        )
        conn.execute(
            """
            INSERT INTO transactions (amount, description, _id_categories, _id_currencies, date)
            VALUES (50, 'Keep me', ?, 1, '2024-01-01')
            """,
            (category_id,),
        )
        conn.commit()
    return db_path


def _create_food_db(db_path: Path) -> Path:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(str(db_path)) as conn:
        conn.executescript(_FOOD_SCHEMA_SQL)
        conn.execute(
            """
            INSERT INTO food_items (name, name_en, is_drink, calories_per_100g)
            VALUES ('Банан', 'Banana', 0, 89)
            """
        )
        conn.execute(
            "INSERT INTO food_log (date, name, calories_per_100g, weight, is_drink) "
            "VALUES ('2024-01-01', 'Банан', 89, 100, 0)",
        )
        conn.commit()
    return db_path


def test_pack_and_install_finance_and_food_catalogs(tmp_path: Path) -> None:
    """Finance and food catalogs transfer by name and leave history tables alone."""
    source_root = tmp_path / "source"
    source_root.mkdir()
    source_finance = _create_finance_db(tmp_path / "source-data" / "finance.db")
    source_food = _create_food_db(tmp_path / "source-data" / "food.db")
    zip_path = tmp_path / "catalogs.zip"
    result = pack_private_data(
        project_root=source_root,
        sqlite_fitness="",
        sqlite_finance=str(source_finance),
        sqlite_food=str(source_food),
        output_zip=zip_path,
        selection=PrivateDataSelection(api_keys=False, fitness=False, finance=True, food=True),
    )
    assert result.finance_currencies_count == 1
    assert result.finance_categories_count == 1
    assert result.finance_standard_items_count == 1
    assert result.food_items_count == 1
    with zipfile.ZipFile(zip_path) as archive:
        names = set(archive.namelist())
    assert ZIP_FINANCE_CATALOG_NAME in names
    assert ZIP_FOOD_CATALOG_NAME in names
    assert ZIP_CATALOG_NAME not in names
    present = inspect_private_data_zip(zip_path)
    assert present.finance
    assert present.food
    assert not present.fitness

    target_finance = _create_finance_db(tmp_path / "target-data" / "finance.db")
    target_food = _create_food_db(tmp_path / "target-data" / "food.db")
    with sqlite3.connect(str(target_finance)) as conn:
        conn.execute("UPDATE categories SET icon = 'old' WHERE name = 'Food'")
        conn.commit()
    with sqlite3.connect(str(target_food)) as conn:
        conn.execute("UPDATE food_items SET calories_per_100g = 1 WHERE name = 'Банан'")
        conn.commit()

    installed = install_private_data(
        project_root=tmp_path / "target",
        sqlite_fitness="",
        sqlite_finance=str(target_finance),
        sqlite_food=str(target_food),
        zip_path=zip_path,
        recover_sql_path=RECOVER_SQL,
        selection=PrivateDataSelection(api_keys=False, fitness=False, finance=True, food=True),
    )
    assert installed.finance_stats.categories_updated == 1
    assert installed.food_stats.food_items_updated == 1
    with sqlite3.connect(str(target_finance)) as conn:
        icon = conn.execute("SELECT icon FROM categories WHERE name = 'Food'").fetchone()[0]
        assert icon == "🍔"
        assert int(conn.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]) == 1
    with sqlite3.connect(str(target_food)) as conn:
        calories = conn.execute("SELECT calories_per_100g FROM food_items WHERE name = 'Банан'").fetchone()[0]
        assert float(calories) == 89
        assert int(conn.execute("SELECT COUNT(*) FROM food_log").fetchone()[0]) == 1
