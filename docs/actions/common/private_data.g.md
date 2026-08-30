---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `private_data.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `InstallPrivateDataResult`](#%EF%B8%8F-class-installprivatedataresult)
- [🏛️ Class `PackPrivateDataResult`](#%EF%B8%8F-class-packprivatedataresult)
- [🏛️ Class `PrivateDataSelection`](#%EF%B8%8F-class-privatedataselection)
  - [⚙️ Method `any_selected`](#%EF%B8%8F-method-any_selected)
- [🔧 Function `api_key_file_matches_config_token`](#-function-api_key_file_matches_config_token)
- [🔧 Function `collect_fitness_image_files`](#-function-collect_fitness_image_files)
- [🔧 Function `default_private_data_zip_path`](#-function-default_private_data_zip_path)
- [🔧 Function `default_selected_api_key_files`](#-function-default_selected_api_key_files)
- [🔧 Function `find_importable_fitness_private_data_zip`](#-function-find_importable_fitness_private_data_zip)
- [🔧 Function `inspect_private_data_zip`](#-function-inspect_private_data_zip)
- [🔧 Function `install_private_data`](#-function-install_private_data)
- [🔧 Function `list_api_key_files_in_zip`](#-function-list_api_key_files_in_zip)
- [🔧 Function `list_api_key_secret_files`](#-function-list_api_key_secret_files)
- [🔧 Function `pack_private_data`](#-function-pack_private_data)
- [🔧 Function `resolve_api_key_files_for_pack`](#-function-resolve_api_key_files_for_pack)
- [🔧 Function `resolve_configured_sqlite_path`](#-function-resolve_configured_sqlite_path)
- [🔧 Function `resolve_fitness_paths`](#-function-resolve_fitness_paths)
- [🔧 Function `selection_from_part_flags`](#-function-selection_from_part_flags)

</details>

## 🏛️ Class `InstallPrivateDataResult`

```python
class InstallPrivateDataResult
```

Result of installing a private-data ZIP.

<details>
<summary>Code:</summary>

```python
class InstallPrivateDataResult:

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
```

</details>

## 🏛️ Class `PackPrivateDataResult`

```python
class PackPrivateDataResult
```

Result of packing a private-data ZIP.

<details>
<summary>Code:</summary>

```python
class PackPrivateDataResult:

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
    food_recipes_count: int = 0
```

</details>

## 🏛️ Class `PrivateDataSelection`

```python
class PrivateDataSelection
```

Which private-data parts to pack or install.

<details>
<summary>Code:</summary>

```python
class PrivateDataSelection:

    api_keys: bool = True
    fitness: bool = True
    finance: bool = False
    food: bool = False
    api_key_files: tuple[str, ...] = ()

    def any_selected(self) -> bool:
        """Return whether at least one part is selected."""
        return self.api_keys or self.fitness or self.finance or self.food
```

</details>

### ⚙️ Method `any_selected`

```python
def any_selected(self) -> bool
```

Return whether at least one part is selected.

<details>
<summary>Code:</summary>

```python
def any_selected(self) -> bool:
        return self.api_keys or self.fitness or self.finance or self.food
```

</details>

## 🔧 Function `api_key_file_matches_config_token`

```python
def api_key_file_matches_config_token(filename: str, token: str) -> bool
```

Return whether an `api-keys` filename matches a config default-key token.

Tokens match the full filename, the stem, `{token}-api-key`, or the same
forms after `.` is treated as `-` (`bothub.ru` → `bothub-ru-api-key.txt`).

Args:

- `filename` (`str`): Secret key filename, such as `bothub-api-key.txt`.
- `token` (`str`): Config value such as `bothub` or `bothub.ru`.

Returns:

- `bool`: `True` when this file should be selected by default.

<details>
<summary>Code:</summary>

```python
def api_key_file_matches_config_token(filename: str, token: str) -> bool:
    raw = token.strip()
    name = filename.strip()
    if not raw or not name:
        return False
    if name.casefold() == raw.casefold():
        return True
    stem = name[: -len(".txt")] if name.casefold().endswith(".txt") else name
    norm_stem = stem.replace("_", "-").casefold()
    norm_token = _normalize_transfer_api_key_token(raw)
    if not norm_token:
        return False
    if norm_stem in (norm_token, f"{norm_token}-api-key"):
        return True
    token_hyphen = norm_token.replace(".", "-")
    return token_hyphen != norm_token and norm_stem in (token_hyphen, f"{token_hyphen}-api-key")
```

</details>

## 🔧 Function `collect_fitness_image_files`

```python
def collect_fitness_image_files(fitness_img_dir: Path, exercise_names: Sequence[str]) -> tuple[list[Path], list[str]]
```

Return files to pack from `fitness_img_dir` and catalog names missing `{name}.avif`.

Packs every file under the folder (small AVIFs, `high/` and `min/` copies, plus extras).
Missing names are catalog exercises with no `{name}.avif` in the folder root
(a file only under `high/` does not count).

<details>
<summary>Code:</summary>

```python
def collect_fitness_image_files(
    fitness_img_dir: Path,
    exercise_names: Sequence[str],
) -> tuple[list[Path], list[str]]:
    if not fitness_img_dir.is_dir():
        return [], [str(name) for name in exercise_names]

    files = sorted(path for path in fitness_img_dir.rglob("*") if path.is_file())
    existing_stems = {path.stem for path in fitness_img_dir.glob("*.avif") if path.is_file()}
    missing = [str(name) for name in exercise_names if name not in existing_stems]
    return files, missing
```

</details>

## 🔧 Function `default_private_data_zip_path`

```python
def default_private_data_zip_path(project_root: Path) -> Path
```

Return default ZIP path under `install/`.

<details>
<summary>Code:</summary>

```python
def default_private_data_zip_path(project_root: Path) -> Path:
    return project_root / "install" / DEFAULT_PRIVATE_DATA_ZIP_NAME
```

</details>

## 🔧 Function `default_selected_api_key_files`

```python
def default_selected_api_key_files(filenames: Sequence[str], config_tokens: Sequence[object]) -> list[str]
```

Return filenames that match `transfer_private_data_default_api_keys`.

Empty or missing tokens select nothing. Unknown tokens are ignored.

Args:

- `filenames` (`Sequence[str]`): Secret key filenames to consider.
- `config_tokens` (`Sequence[object]`): Tokens from config.

Returns:

- `list[str]`: Filenames to check by default, in `filenames` order.

<details>
<summary>Code:</summary>

```python
def default_selected_api_key_files(
    filenames: Sequence[str],
    config_tokens: Sequence[object],
) -> list[str]:
    tokens = [str(item).strip() for item in config_tokens if str(item).strip()]
    if not tokens:
        return []
    return [name for name in filenames if any(api_key_file_matches_config_token(name, token) for token in tokens)]
```

</details>

## 🔧 Function `find_importable_fitness_private_data_zip`

```python
def find_importable_fitness_private_data_zip(project_root: Path) -> Path | None
```

Return the default private-data ZIP when it contains fitness catalog or images.

Args:

- `project_root` (`Path`): Application project root (contains `install/`).

Returns:

- `Path | None`: ZIP path when it can supply exercise images, otherwise `None`.

<details>
<summary>Code:</summary>

```python
def find_importable_fitness_private_data_zip(project_root: Path) -> Path | None:
    zip_path = default_private_data_zip_path(project_root)
    if not zip_path.is_file():
        return None
    try:
        present = inspect_private_data_zip(zip_path)
    except (OSError, ValueError, zipfile.BadZipFile):
        return None
    return zip_path if present.fitness else None
```

</details>

## 🔧 Function `inspect_private_data_zip`

```python
def inspect_private_data_zip(zip_path: Path) -> PrivateDataSelection
```

Return which parts a private-data ZIP contains.

<details>
<summary>Code:</summary>

```python
def inspect_private_data_zip(zip_path: Path) -> PrivateDataSelection:
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
```

</details>

## 🔧 Function `install_private_data`

```python
def install_private_data(*, project_root: Path, sqlite_fitness: str, zip_path: Path, recover_sql_path: Path, selection: PrivateDataSelection | None = None, sqlite_finance: str = '', sqlite_food: str = '', finance_recover_sql_path: Path | None = None, food_recover_sql_path: Path | None = None) -> InstallPrivateDataResult
```

Install selected parts from a private-data ZIP.

API keys overwrite matching `api-keys/*.txt`. Fitness images overlay
`{name}.avif` into the target `fitness_img` (existing extra files stay).
Catalogs upsert by stable names. Never writes workout, transaction, or
food-log history.

<details>
<summary>Code:</summary>

```python
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
```

</details>

## 🔧 Function `list_api_key_files_in_zip`

```python
def list_api_key_files_in_zip(zip_path: Path) -> list[str]
```

Return secret API key filenames stored under `api-keys/` in a ZIP.

Args:

- `zip_path` (`Path`): Private-data ZIP.

Returns:

- `list[str]`: Filenames (not `*.example.txt`), sorted.

<details>
<summary>Code:</summary>

```python
def list_api_key_files_in_zip(zip_path: Path) -> list[str]:
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
```

</details>

## 🔧 Function `list_api_key_secret_files`

```python
def list_api_key_secret_files(api_keys_dir: Path) -> list[Path]
```

Return secret `*.txt` files under `api-keys` (exclude `*.example.txt`).

<details>
<summary>Code:</summary>

```python
def list_api_key_secret_files(api_keys_dir: Path) -> list[Path]:
    if not api_keys_dir.is_dir():
        msg = f"api-keys folder not found: {api_keys_dir}"
        raise FileNotFoundError(msg)
    return sorted(
        path
        for path in api_keys_dir.iterdir()
        if path.is_file() and path.suffix.lower() == ".txt" and not path.name.endswith(".example.txt")
    )
```

</details>

## 🔧 Function `pack_private_data`

```python
def pack_private_data(*, project_root: Path, sqlite_fitness: str, output_zip: Path, selection: PrivateDataSelection | None = None, sqlite_finance: str = '', sqlite_food: str = '') -> PackPrivateDataResult
```

Pack selected private-data parts into `output_zip`.

<details>
<summary>Code:</summary>

```python
def pack_private_data(
    *,
    project_root: Path,
    sqlite_fitness: str,
    output_zip: Path,
    selection: PrivateDataSelection | None = None,
    sqlite_finance: str = "",
    sqlite_food: str = "",
) -> PackPrivateDataResult:
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
    food_recipes_count = len(food_catalog.get("recipes") or []) if food_catalog is not None else 0

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
            "food_recipes_count": food_recipes_count,
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
        food_recipes_count=food_recipes_count,
    )
```

</details>

## 🔧 Function `resolve_api_key_files_for_pack`

```python
def resolve_api_key_files_for_pack(api_keys_dir: Path, selected_names: Sequence[str] | None = None) -> list[Path]
```

Return secret key files to pack, optionally filtered by filename.

Empty `selected_names` means every secret `*.txt` in `api-keys/`.

Args:

- `api_keys_dir` (`Path`): Project `api-keys` folder.
- `selected_names` (`Sequence[str] | None`): Filenames to include, or all.

Returns:

- `list[Path]`: Key files in directory order.

<details>
<summary>Code:</summary>

```python
def resolve_api_key_files_for_pack(
    api_keys_dir: Path,
    selected_names: Sequence[str] | None = None,
) -> list[Path]:
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
```

</details>

## 🔧 Function `resolve_configured_sqlite_path`

```python
def resolve_configured_sqlite_path(value: str, *, setting_name: str) -> Path
```

Return a configured SQLite path, rejecting empty values and placeholders.

<details>
<summary>Code:</summary>

```python
def resolve_configured_sqlite_path(value: str, *, setting_name: str) -> Path:
    if not value.strip() or _PLACEHOLDER_RE.search(value):
        msg = f"config.json must set a real {setting_name} path (not a <YOUR_...> placeholder)."
        raise ValueError(msg)
    return Path(value).expanduser()
```

</details>

## 🔧 Function `resolve_fitness_paths`

```python
def resolve_fitness_paths(sqlite_fitness: str) -> tuple[Path, Path]
```

Return `(db_path, fitness_img_dir)` from config `sqlite_fitness` value.

<details>
<summary>Code:</summary>

```python
def resolve_fitness_paths(sqlite_fitness: str) -> tuple[Path, Path]:
    db_path = resolve_configured_sqlite_path(sqlite_fitness, setting_name="sqlite_fitness")
    return db_path, db_path.parent / "fitness_img"
```

</details>

## 🔧 Function `selection_from_part_flags`

```python
def selection_from_part_flags(*, api_keys: bool, fitness: bool, finance: bool = False, food: bool = False) -> PrivateDataSelection
```

Build a selection; when every flag is false, include every part.

<details>
<summary>Code:</summary>

```python
def selection_from_part_flags(
    *,
    api_keys: bool,
    fitness: bool,
    finance: bool = False,
    food: bool = False,
) -> PrivateDataSelection:
    if not api_keys and not fitness and not finance and not food:
        return PrivateDataSelection(api_keys=True, fitness=True, finance=True, food=True)
    return PrivateDataSelection(api_keys=api_keys, fitness=fitness, finance=finance, food=food)
```

</details>
