"""Pack and install personal private data ZIP (api-keys and tracker catalogs).

Not part of public install bundles. History tables are never included: fitness
`process`/`weight`, finance transactions/accounts, and food `food_log`. Catalog
upsert preserves existing IDs on the target machine. Fitness images are
`{exercise English name}.avif` under `fitness_img/` next to the DB, plus optional
high-resolution copies in `fitness_img/high/`.

"""

from __future__ import annotations

import contextlib
import json
import re
import shutil
import sqlite3
import stat
import tempfile
import time
import zipfile
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

from harrix_swiss_knife.apps.finance.catalog_sync import (
    FinanceCatalogUpsertStats,
    create_empty_finance_database,
    export_finance_catalog,
    load_finance_catalog_json,
    upsert_finance_catalog,
)
from harrix_swiss_knife.apps.fitness.catalog_sync import (
    CatalogUpsertStats,
    create_empty_fitness_database,
    export_fitness_catalog,
    load_fitness_catalog_json,
    upsert_fitness_catalog,
)
from harrix_swiss_knife.apps.food.catalog_sync import (
    FoodCatalogUpsertStats,
    create_empty_food_database,
    export_food_catalog,
    load_food_catalog_json,
    upsert_food_catalog,
)

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

DEFAULT_PRIVATE_DATA_ZIP_NAME = "private-data-harrix-swiss-knife.zip"
_PLACEHOLDER_RE = re.compile(r"<YOUR_")
ZIP_API_KEYS_DIR = "api-keys"
ZIP_FITNESS_IMG_DIR = "fitness_img"
ZIP_CATALOG_NAME = "fitness_catalog.json"
ZIP_FINANCE_CATALOG_NAME = "finance_catalog.json"
ZIP_FOOD_CATALOG_NAME = "food_catalog.json"
ZIP_MANIFEST_NAME = "manifest.json"
_STAGE_INSTALL_PREFIX = ".hsk-private-data-install-"
_STAGE_PACK_PREFIX = ".hsk-private-data-pack-"
_REMOVE_TREE_ATTEMPTS = 5
_REMOVE_TREE_RETRY_S = 0.05


@dataclass(frozen=True)
class InstallPrivateDataResult:
    """Result of installing a private-data ZIP."""

    api_keys_count: int
    fitness_img_count: int
    catalog_stats: CatalogUpsertStats
    fitness_db_path: Path | None
    fitness_img_dir: Path | None
    created_database: bool
    missing_exercise_images: tuple[str, ...] = ()
    finance_stats: FinanceCatalogUpsertStats = field(default_factory=FinanceCatalogUpsertStats)
    food_stats: FoodCatalogUpsertStats = field(default_factory=FoodCatalogUpsertStats)
    finance_db_path: Path | None = None
    food_db_path: Path | None = None
    created_finance_database: bool = False
    created_food_database: bool = False


@dataclass(frozen=True)
class PackPrivateDataResult:
    """Result of packing a private-data ZIP."""

    zip_path: Path
    api_keys_count: int
    fitness_img_count: int
    exercises_count: int
    types_count: int
    api_key_files: tuple[str, ...] = ()
    missing_exercise_images: tuple[str, ...] = ()
    finance_currencies_count: int = 0
    finance_categories_count: int = 0
    finance_standard_items_count: int = 0
    food_items_count: int = 0


@dataclass(frozen=True)
class PrivateDataSelection:
    """Which private-data parts to pack or install."""

    api_keys: bool = True
    fitness: bool = True
    finance: bool = False
    food: bool = False
    api_key_files: tuple[str, ...] = ()

    def any_selected(self) -> bool:
        """Return whether at least one part is selected."""
        return self.api_keys or self.fitness or self.finance or self.food


def collect_fitness_image_files(
    fitness_img_dir: Path,
    exercise_names: Sequence[str],
) -> tuple[list[Path], list[str]]:
    """Return files to pack from `fitness_img_dir` and catalog names missing `{name}.avif`.

    Packs every file under the folder (small AVIFs, `high/` copies, plus extras).
    Missing names are catalog exercises with no `{name}.avif` in the folder root
    (a file only under `high/` does not count).

    """
    if not fitness_img_dir.is_dir():
        return [], [str(name) for name in exercise_names]

    files = sorted(path for path in fitness_img_dir.rglob("*") if path.is_file())
    existing_stems = {path.stem for path in fitness_img_dir.glob("*.avif") if path.is_file()}
    missing = [str(name) for name in exercise_names if name not in existing_stems]
    return files, missing


def default_private_data_zip_path(project_root: Path) -> Path:
    """Return default ZIP path under `install/`."""
    return project_root / "install" / DEFAULT_PRIVATE_DATA_ZIP_NAME


def find_importable_fitness_private_data_zip(project_root: Path) -> Path | None:
    """Return the default private-data ZIP when it contains fitness catalog or images.

    Args:

    - `project_root` (`Path`): Application project root (contains `install/`).

    Returns:

    - `Path | None`: ZIP path when it can supply exercise images, otherwise `None`.

    """
    zip_path = default_private_data_zip_path(project_root)
    if not zip_path.is_file():
        return None
    try:
        present = inspect_private_data_zip(zip_path)
    except (OSError, ValueError, zipfile.BadZipFile):
        return None
    return zip_path if present.fitness else None


def inspect_private_data_zip(zip_path: Path) -> PrivateDataSelection:
    """Return which parts a private-data ZIP contains."""
    if not zip_path.is_file():
        msg = f"ZIP not found: {zip_path}"
        raise FileNotFoundError(msg)
    with zipfile.ZipFile(zip_path, "r") as archive:
        names = [_zip_member_posix(name) for name in archive.namelist()]
    has_api_keys = any(
        name.startswith(f"{ZIP_API_KEYS_DIR}/") and name.lower().endswith(".txt") and name.count("/") == 1
        for name in names
    )
    has_catalog = ZIP_CATALOG_NAME in names
    has_images = any(name.startswith(f"{ZIP_FITNESS_IMG_DIR}/") and not name.endswith("/") for name in names)
    has_finance = ZIP_FINANCE_CATALOG_NAME in names
    has_food = ZIP_FOOD_CATALOG_NAME in names
    return PrivateDataSelection(
        api_keys=has_api_keys,
        fitness=has_catalog or has_images,
        finance=has_finance,
        food=has_food,
    )


def install_private_data(
    *,
    project_root: Path,
    sqlite_fitness: str,
    zip_path: Path,
    recover_sql_path: Path,
    selection: PrivateDataSelection | None = None,
    sqlite_finance: str = "",
    sqlite_food: str = "",
    finance_recover_sql_path: Path | None = None,
    food_recover_sql_path: Path | None = None,
) -> InstallPrivateDataResult:
    """Install selected parts from a private-data ZIP.

    API keys overwrite matching `api-keys/*.txt`. Fitness images overlay
    `{name}.avif` into the target `fitness_img` (existing extra files stay).
    Catalogs upsert by stable names. Never writes workout, transaction, or
    food-log history.

    """
    if not zip_path.is_file():
        msg = f"ZIP not found: {zip_path}"
        raise FileNotFoundError(msg)

    present = inspect_private_data_zip(zip_path)
    wanted = selection if selection is not None else present
    if not wanted.any_selected():
        msg = "Select at least one data type to import."
        raise ValueError(msg)

    include_api_keys = wanted.api_keys and present.api_keys
    include_fitness = wanted.fitness and present.fitness
    include_finance = wanted.finance and present.finance
    include_food = wanted.food and present.food
    if wanted.api_keys and not present.api_keys:
        msg = f"ZIP has no API keys: {zip_path}"
        raise FileNotFoundError(msg)
    if wanted.fitness and not present.fitness:
        msg = f"ZIP has no exercise catalog or images: {zip_path}"
        raise FileNotFoundError(msg)
    if wanted.finance and not present.finance:
        msg = f"ZIP has no finance catalog: {zip_path}"
        raise FileNotFoundError(msg)
    if wanted.food and not present.food:
        msg = f"ZIP has no food catalog: {zip_path}"
        raise FileNotFoundError(msg)
    if not include_api_keys and not include_fitness and not include_finance and not include_food:
        msg = "Nothing to import from this ZIP with the current selection."
        raise ValueError(msg)

    db_path: Path | None = None
    fitness_img_dir: Path | None = None
    created_database = False
    if include_fitness:
        db_path, fitness_img_dir = resolve_fitness_paths(sqlite_fitness)
        created_database = _ensure_sqlite_database(
            db_path,
            recover_sql_path,
            create=create_empty_fitness_database,
        )

    finance_db_path: Path | None = None
    created_finance_database = False
    if include_finance:
        finance_db_path = resolve_configured_sqlite_path(sqlite_finance, setting_name="sqlite_finance")
        created_finance_database = _ensure_sqlite_database(
            finance_db_path,
            finance_recover_sql_path,
            create=create_empty_finance_database,
        )

    food_db_path: Path | None = None
    created_food_database = False
    if include_food:
        food_db_path = resolve_configured_sqlite_path(sqlite_food, setting_name="sqlite_food")
        created_food_database = _ensure_sqlite_database(
            food_db_path,
            food_recover_sql_path,
            create=create_empty_food_database,
        )

    _cleanup_adjacent_stage_dirs(zip_path)
    stage_root = Path(tempfile.mkdtemp(prefix="hsk-private-data-install-"))

    key_count = 0
    img_count = 0
    stats = CatalogUpsertStats()
    finance_stats = FinanceCatalogUpsertStats()
    food_stats = FoodCatalogUpsertStats()
    missing_images: list[str] = []
    try:
        with zipfile.ZipFile(zip_path, "r") as archive:
            archive.extractall(stage_root)

        if include_api_keys:
            key_count = _install_api_keys(
                stage_root / ZIP_API_KEYS_DIR,
                project_root / ZIP_API_KEYS_DIR,
                selected_names=wanted.api_key_files,
            )

        if include_fitness:
            if db_path is None or fitness_img_dir is None:
                msg = "Fitness database path is not resolved."
                raise ValueError(msg)
            img_count, missing_images, stats = _install_fitness_data(
                stage_root,
                db_path=db_path,
                fitness_img_dir=fitness_img_dir,
            )
        if include_finance:
            if finance_db_path is None:
                msg = "Finance database path is not resolved."
                raise ValueError(msg)
            finance_stats = _install_json_catalog(
                stage_root / ZIP_FINANCE_CATALOG_NAME,
                db_path=finance_db_path,
                load_catalog=load_finance_catalog_json,
                upsert_catalog=upsert_finance_catalog,
                locked_label="finance",
            )
        if include_food:
            if food_db_path is None:
                msg = "Food database path is not resolved."
                raise ValueError(msg)
            food_stats = _install_json_catalog(
                stage_root / ZIP_FOOD_CATALOG_NAME,
                db_path=food_db_path,
                load_catalog=load_food_catalog_json,
                upsert_catalog=upsert_food_catalog,
                locked_label="food",
            )
    finally:
        _remove_tree(stage_root)

    return InstallPrivateDataResult(
        api_keys_count=key_count,
        fitness_img_count=img_count,
        catalog_stats=stats,
        fitness_db_path=db_path,
        fitness_img_dir=fitness_img_dir,
        created_database=created_database,
        missing_exercise_images=tuple(missing_images),
        finance_stats=finance_stats,
        food_stats=food_stats,
        finance_db_path=finance_db_path,
        food_db_path=food_db_path,
        created_finance_database=created_finance_database,
        created_food_database=created_food_database,
    )


def list_api_key_files_in_zip(zip_path: Path) -> list[str]:
    """Return secret API key filenames stored under `api-keys/` in a ZIP.

    Args:

    - `zip_path` (`Path`): Private-data ZIP.

    Returns:

    - `list[str]`: Filenames (not `*.example.txt`), sorted.

    """
    if not zip_path.is_file():
        msg = f"ZIP not found: {zip_path}"
        raise FileNotFoundError(msg)
    prefix = f"{ZIP_API_KEYS_DIR}/"
    with zipfile.ZipFile(zip_path, "r") as archive:
        names = [_zip_member_posix(name) for name in archive.namelist()]
    return sorted(
        Path(name).name
        for name in names
        if name.startswith(prefix)
        and name.count("/") == 1
        and name.lower().endswith(".txt")
        and not Path(name).name.endswith(".example.txt")
    )


def list_api_key_secret_files(api_keys_dir: Path) -> list[Path]:
    """Return secret `*.txt` files under `api-keys` (exclude `*.example.txt`)."""
    if not api_keys_dir.is_dir():
        msg = f"api-keys folder not found: {api_keys_dir}"
        raise FileNotFoundError(msg)
    return sorted(
        path
        for path in api_keys_dir.iterdir()
        if path.is_file() and path.suffix.lower() == ".txt" and not path.name.endswith(".example.txt")
    )


def pack_private_data(
    *,
    project_root: Path,
    sqlite_fitness: str,
    output_zip: Path,
    selection: PrivateDataSelection | None = None,
    sqlite_finance: str = "",
    sqlite_food: str = "",
) -> PackPrivateDataResult:
    """Pack selected private-data parts into `output_zip`."""
    wanted = selection if selection is not None else PrivateDataSelection()
    if not wanted.any_selected():
        msg = "Select at least one data type to export."
        raise ValueError(msg)

    key_files: list[Path] = []
    if wanted.api_keys:
        api_keys_dir = project_root / ZIP_API_KEYS_DIR
        key_files = resolve_api_key_files_for_pack(api_keys_dir, wanted.api_key_files)
        if not key_files:
            msg = f"No secret *.txt files found in {api_keys_dir} (excluding *.example.txt)."
            raise FileNotFoundError(msg)

    fitness_files: list[Path] = []
    missing_images: list[str] = []
    exercises: list[dict[str, Any]] = []
    types_count = 0
    db_path: Path | None = None
    fitness_img_dir: Path | None = None
    catalog: dict[str, Any] | None = None
    if wanted.fitness:
        db_path, fitness_img_dir = resolve_fitness_paths(sqlite_fitness)
        catalog = export_fitness_catalog(db_path)
        exercises = catalog["exercises"]
        types_count = sum(len(exercise["types"]) for exercise in exercises)
        names = [str(exercise["name"]) for exercise in exercises]
        fitness_files, missing_images = collect_fitness_image_files(fitness_img_dir, names)

    finance_catalog: dict[str, Any] | None = None
    finance_db_path: Path | None = None
    if wanted.finance:
        finance_db_path = resolve_configured_sqlite_path(sqlite_finance, setting_name="sqlite_finance")
        finance_catalog = export_finance_catalog(finance_db_path)

    food_catalog: dict[str, Any] | None = None
    food_db_path: Path | None = None
    if wanted.food:
        food_db_path = resolve_configured_sqlite_path(sqlite_food, setting_name="sqlite_food")
        food_catalog = export_food_catalog(food_db_path)

    finance_currencies_count = len(finance_catalog["currencies"]) if finance_catalog is not None else 0
    finance_categories_count = len(finance_catalog["categories"]) if finance_catalog is not None else 0
    finance_standard_items_count = len(finance_catalog["standard_items"]) if finance_catalog is not None else 0
    food_items_count = len(food_catalog["food_items"]) if food_catalog is not None else 0

    _cleanup_adjacent_stage_dirs(output_zip)
    stage_root = Path(tempfile.mkdtemp(prefix="hsk-private-data-pack-"))

    try:
        if wanted.api_keys:
            stage_api = stage_root / ZIP_API_KEYS_DIR
            stage_api.mkdir(parents=True, exist_ok=True)
            for key_file in key_files:
                shutil.copy2(key_file, stage_api / key_file.name)

        if wanted.fitness:
            if catalog is None or fitness_img_dir is None or db_path is None:
                msg = "Fitness catalog is not resolved."
                raise ValueError(msg)
            stage_img = stage_root / ZIP_FITNESS_IMG_DIR
            stage_img.mkdir(parents=True, exist_ok=True)
            for img_file in fitness_files:
                rel = img_file.relative_to(fitness_img_dir)
                target = stage_img / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(img_file, target)
            catalog_path = stage_root / ZIP_CATALOG_NAME
            catalog_path.write_text(
                json.dumps(catalog, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

        if wanted.finance:
            if finance_catalog is None:
                msg = "Finance catalog is not resolved."
                raise ValueError(msg)
            (stage_root / ZIP_FINANCE_CATALOG_NAME).write_text(
                json.dumps(finance_catalog, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

        if wanted.food:
            if food_catalog is None:
                msg = "Food catalog is not resolved."
                raise ValueError(msg)
            (stage_root / ZIP_FOOD_CATALOG_NAME).write_text(
                json.dumps(food_catalog, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

        manifest: dict[str, Any] = {
            "created_utc": datetime.now(UTC).isoformat(),
            "parts": {
                "api_keys": wanted.api_keys,
                "fitness": wanted.fitness,
                "finance": wanted.finance,
                "food": wanted.food,
            },
            "api_keys_count": len(key_files),
            "fitness_img_count": len(fitness_files),
            "exercises_count": len(exercises),
            "types_count": types_count,
            "finance_currencies_count": finance_currencies_count,
            "finance_categories_count": finance_categories_count,
            "finance_standard_items_count": finance_standard_items_count,
            "food_items_count": food_items_count,
            "api_key_files": [path.name for path in key_files],
            "missing_exercise_images": missing_images,
        }
        if fitness_img_dir is not None:
            manifest["fitness_img_source"] = str(fitness_img_dir)
        if db_path is not None:
            manifest["fitness_db_source"] = str(db_path)
        if finance_db_path is not None:
            manifest["finance_db_source"] = str(finance_db_path)
        if food_db_path is not None:
            manifest["food_db_source"] = str(food_db_path)
        (stage_root / ZIP_MANIFEST_NAME).write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        output_zip.parent.mkdir(parents=True, exist_ok=True)
        if output_zip.exists():
            output_zip.unlink()

        with zipfile.ZipFile(output_zip, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for file_path in stage_root.rglob("*"):
                if file_path.is_file():
                    archive.write(file_path, file_path.relative_to(stage_root).as_posix())
    finally:
        _remove_tree(stage_root)

    return PackPrivateDataResult(
        zip_path=output_zip,
        api_keys_count=len(key_files),
        api_key_files=tuple(path.name for path in key_files),
        fitness_img_count=len(fitness_files),
        exercises_count=len(exercises),
        types_count=types_count,
        missing_exercise_images=tuple(missing_images),
        finance_currencies_count=finance_currencies_count,
        finance_categories_count=finance_categories_count,
        finance_standard_items_count=finance_standard_items_count,
        food_items_count=food_items_count,
    )


def resolve_api_key_files_for_pack(
    api_keys_dir: Path,
    selected_names: Sequence[str] | None = None,
) -> list[Path]:
    """Return secret key files to pack, optionally filtered by filename.

    Empty `selected_names` means every secret `*.txt` in `api-keys/`.

    Args:

    - `api_keys_dir` (`Path`): Project `api-keys` folder.
    - `selected_names` (`Sequence[str] | None`): Filenames to include, or all.

    Returns:

    - `list[Path]`: Key files in directory order.

    """
    all_files = list_api_key_secret_files(api_keys_dir)
    if not selected_names:
        return all_files
    wanted = {str(name).strip() for name in selected_names if str(name).strip()}
    available = {path.name for path in all_files}
    missing = sorted(wanted - available)
    if missing:
        msg = f"Unknown API key file(s): {', '.join(missing)}"
        raise FileNotFoundError(msg)
    return [path for path in all_files if path.name in wanted]


def resolve_configured_sqlite_path(value: str, *, setting_name: str) -> Path:
    """Return a configured SQLite path, rejecting empty values and placeholders."""
    if not value.strip() or _PLACEHOLDER_RE.search(value):
        msg = f"config.json must set a real {setting_name} path (not a <YOUR_...> placeholder)."
        raise ValueError(msg)
    return Path(value).expanduser()


def resolve_fitness_paths(sqlite_fitness: str) -> tuple[Path, Path]:
    """Return `(db_path, fitness_img_dir)` from config `sqlite_fitness` value."""
    db_path = resolve_configured_sqlite_path(sqlite_fitness, setting_name="sqlite_fitness")
    return db_path, db_path.parent / "fitness_img"


def selection_from_part_flags(
    *,
    api_keys: bool,
    fitness: bool,
    finance: bool = False,
    food: bool = False,
) -> PrivateDataSelection:
    """Build a selection; when every flag is false, include every part."""
    if not api_keys and not fitness and not finance and not food:
        return PrivateDataSelection(api_keys=True, fitness=True, finance=True, food=True)
    return PrivateDataSelection(api_keys=api_keys, fitness=fitness, finance=finance, food=food)


def _cleanup_adjacent_stage_dirs(zip_path: Path) -> None:
    """Remove leftover `.hsk-private-data-*` folders next to a ZIP.

    Args:

    - `zip_path` (`Path`): Pack or install ZIP whose sibling stage folders to drop.

    """
    parent = zip_path.parent
    if not parent.is_dir():
        return
    leftovers = [
        child
        for child in parent.iterdir()
        if child.is_dir()
        and (child.name.startswith(_STAGE_PACK_PREFIX) or child.name.startswith(_STAGE_INSTALL_PREFIX))
    ]
    for child in leftovers:
        _remove_tree(child)


def _ensure_sqlite_database(
    db_path: Path,
    recover_sql_path: Path | None,
    *,
    create: Callable[[Path, Path], None],
) -> bool:
    """Create `db_path` from recover SQL when the file is missing.

    Returns:

    - `bool`: `True` when a new database file was created.

    """
    if db_path.is_file():
        return False
    if recover_sql_path is None or not recover_sql_path.is_file():
        msg = f"recover.sql not found: {recover_sql_path}"
        raise FileNotFoundError(msg)
    create(db_path, recover_sql_path)
    return True


def _install_api_keys(
    stage_api: Path,
    dest_api: Path,
    *,
    selected_names: Sequence[str] | None = None,
) -> int:
    """Copy secret `*.txt` files from the extracted ZIP into `api-keys`.

    Args:

    - `stage_api` (`Path`): Extracted `api-keys` folder from the ZIP.
    - `dest_api` (`Path`): Project `api-keys` folder.
    - `selected_names` (`Sequence[str] | None`): Filenames to copy, or all.

    Returns:

    - `int`: Number of files copied.

    """
    dest_api.mkdir(parents=True, exist_ok=True)
    key_files = sorted(path for path in stage_api.iterdir() if path.is_file() and path.suffix.lower() == ".txt")
    if selected_names:
        wanted = {str(name).strip() for name in selected_names if str(name).strip()}
        key_files = [path for path in key_files if path.name in wanted]
        if not key_files:
            missing = ", ".join(sorted(wanted))
            msg = f"ZIP {ZIP_API_KEYS_DIR}/ has none of the selected API key file(s): {missing}"
            raise FileNotFoundError(msg)
    elif not key_files:
        msg = f"ZIP {ZIP_API_KEYS_DIR}/ has no *.txt files"
        raise FileNotFoundError(msg)
    for key_file in key_files:
        shutil.copy2(key_file, dest_api / key_file.name)
    return len(key_files)


def _install_fitness_data(
    stage_root: Path,
    *,
    db_path: Path,
    fitness_img_dir: Path,
) -> tuple[int, list[str], CatalogUpsertStats]:
    """Overlay `fitness_img` files and upsert the catalog by English name."""
    stage_img = stage_root / ZIP_FITNESS_IMG_DIR
    catalog_file = stage_root / ZIP_CATALOG_NAME
    img_files = sorted(path for path in stage_img.rglob("*") if path.is_file()) if stage_img.is_dir() else []

    fitness_img_dir.mkdir(parents=True, exist_ok=True)
    for img_file in img_files:
        rel = img_file.relative_to(stage_img)
        target = fitness_img_dir / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(img_file, target)

    stats = CatalogUpsertStats()
    missing_images: list[str] = []
    if catalog_file.is_file():
        catalog = load_fitness_catalog_json(catalog_file)
        try:
            stats = upsert_fitness_catalog(db_path, catalog)
        except sqlite3.Error as exc:
            err_text = str(exc).lower()
            if "locked" in err_text or "busy" in err_text:
                msg = f"Cannot write fitness database (is Fitness tracker open?): {db_path}\n{exc}"
                raise OSError(msg) from exc
            raise
        names = [str(exercise["name"]) for exercise in catalog["exercises"]]
        _copied, missing_images = collect_fitness_image_files(fitness_img_dir, names)

    return len(img_files), missing_images, stats


def _install_json_catalog(
    catalog_file: Path,
    *,
    db_path: Path,
    load_catalog: Callable[[Path], dict[str, Any]],
    upsert_catalog: Callable[[Path, dict[str, Any]], Any],
    locked_label: str,
) -> Any:
    """Load a catalog JSON from the extracted ZIP and upsert it into `db_path`."""
    if not catalog_file.is_file():
        msg = f"ZIP is missing {catalog_file.name}"
        raise FileNotFoundError(msg)
    catalog = load_catalog(catalog_file)
    try:
        return upsert_catalog(db_path, catalog)
    except sqlite3.Error as exc:
        err_text = str(exc).lower()
        if "locked" in err_text or "busy" in err_text:
            msg = f"Cannot write {locked_label} database (is the tracker open?): {db_path}\n{exc}"
            raise OSError(msg) from exc
        raise


def _remove_tree(path: Path) -> None:
    """Delete a directory tree, retrying Windows locks and leftover empty folders.

    Args:

    - `path` (`Path`): Directory to remove.

    """
    if not path.exists():
        return

    def _onerror(_func: object, name: str, _exc: object) -> None:
        target = Path(name)
        with contextlib.suppress(OSError):
            target.chmod(stat.S_IWRITE)
            if target.is_file() or target.is_symlink():
                target.unlink()
            elif target.is_dir():
                target.rmdir()

    for _ in range(_REMOVE_TREE_ATTEMPTS):
        if not path.exists():
            return
        try:
            shutil.rmtree(path, onerror=_onerror)
        except OSError:
            time.sleep(_REMOVE_TREE_RETRY_S)
        else:
            return
    shutil.rmtree(path, ignore_errors=True)
    if path.is_dir() and not any(path.iterdir()):
        with contextlib.suppress(OSError):
            path.rmdir()


def _zip_member_posix(name: str) -> str:
    """Normalize a ZIP member name to a POSIX path without a leading slash."""
    return name.replace("\\", "/").lstrip("/")
