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
- [🔧 Function `collect_fitness_image_files`](#-function-collect_fitness_image_files)
- [🔧 Function `default_private_data_zip_path`](#-function-default_private_data_zip_path)
- [🔧 Function `inspect_private_data_zip`](#-function-inspect_private_data_zip)
- [🔧 Function `install_private_data`](#-function-install_private_data)
- [🔧 Function `list_api_key_secret_files`](#-function-list_api_key_secret_files)
- [🔧 Function `pack_private_data`](#-function-pack_private_data)
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
    missing_exercise_images: tuple[str, ...] = ()
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

    def any_selected(self) -> bool:
        """Return whether at least one part is selected."""
        return self.api_keys or self.fitness
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
        return self.api_keys or self.fitness
```

</details>

## 🔧 Function `collect_fitness_image_files`

```python
def collect_fitness_image_files(fitness_img_dir: Path, exercise_names: Sequence[str]) -> tuple[list[Path], list[str]]
```

Return files to pack from `fitness_img_dir` and catalog names missing `{name}.avif`.

Packs every file under the folder (all exercise AVIFs that exist, plus extras).
Missing names are catalog exercises with no `{name}.avif`.

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
    existing_stems = {path.stem for path in files if path.suffix.lower() == ".avif"}
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
    return PrivateDataSelection(api_keys=has_api_keys, fitness=has_catalog or has_images)
```

</details>

## 🔧 Function `install_private_data`

```python
def install_private_data(*, project_root: Path, sqlite_fitness: str, zip_path: Path, recover_sql_path: Path, selection: PrivateDataSelection | None = None) -> InstallPrivateDataResult
```

Install selected parts from a private-data ZIP.

API keys overwrite matching `api-keys/*.txt`. Fitness images overlay
`{name}.avif` into the target `fitness_img` (existing extra files stay).
Catalog upserts by English name. Never writes `process` or `weight`.

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
    if wanted.api_keys and not present.api_keys:
        msg = f"ZIP has no API keys: {zip_path}"
        raise FileNotFoundError(msg)
    if wanted.fitness and not present.fitness:
        msg = f"ZIP has no exercise catalog or images: {zip_path}"
        raise FileNotFoundError(msg)
    if not include_api_keys and not include_fitness:
        msg = "Nothing to import from this ZIP with the current selection."
        raise ValueError(msg)

    db_path: Path | None = None
    fitness_img_dir: Path | None = None
    created_database = False
    if include_fitness:
        db_path, fitness_img_dir = resolve_fitness_paths(sqlite_fitness)
        if not db_path.is_file():
            if not recover_sql_path.is_file():
                msg = f"recover.sql not found: {recover_sql_path}"
                raise FileNotFoundError(msg)
            create_empty_fitness_database(db_path, recover_sql_path)
            created_database = True

    stage_root = zip_path.parent / f".hsk-private-data-install-{zip_path.stem}"
    if stage_root.exists():
        shutil.rmtree(stage_root, ignore_errors=True)
    stage_root.mkdir(parents=True, exist_ok=True)

    key_count = 0
    img_count = 0
    stats = CatalogUpsertStats()
    missing_images: list[str] = []
    try:
        with zipfile.ZipFile(zip_path, "r") as archive:
            archive.extractall(stage_root)

        if include_api_keys:
            key_count = _install_api_keys(stage_root / ZIP_API_KEYS_DIR, project_root / ZIP_API_KEYS_DIR)

        if include_fitness:
            if db_path is None or fitness_img_dir is None:
                msg = "Fitness database path is not resolved."
                raise ValueError(msg)
            img_count, missing_images, stats = _install_fitness_data(
                stage_root,
                db_path=db_path,
                fitness_img_dir=fitness_img_dir,
            )
    finally:
        if stage_root.exists():
            shutil.rmtree(stage_root, ignore_errors=True)

    return InstallPrivateDataResult(
        api_keys_count=key_count,
        fitness_img_count=img_count,
        catalog_stats=stats,
        fitness_db_path=db_path,
        fitness_img_dir=fitness_img_dir,
        created_database=created_database,
        missing_exercise_images=tuple(missing_images),
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
def pack_private_data(*, project_root: Path, sqlite_fitness: str, output_zip: Path, selection: PrivateDataSelection | None = None) -> PackPrivateDataResult
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
) -> PackPrivateDataResult:
    wanted = selection if selection is not None else PrivateDataSelection()
    if not wanted.any_selected():
        msg = "Select at least one data type to export."
        raise ValueError(msg)

    key_files: list[Path] = []
    if wanted.api_keys:
        api_keys_dir = project_root / ZIP_API_KEYS_DIR
        key_files = list_api_key_secret_files(api_keys_dir)
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

    stage_root = output_zip.parent / f".hsk-private-data-pack-{output_zip.stem}"
    if stage_root.exists():
        shutil.rmtree(stage_root, ignore_errors=True)
    stage_root.mkdir(parents=True, exist_ok=True)

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

        manifest: dict[str, Any] = {
            "created_utc": datetime.now(UTC).isoformat(),
            "parts": {
                "api_keys": wanted.api_keys,
                "fitness": wanted.fitness,
            },
            "api_keys_count": len(key_files),
            "fitness_img_count": len(fitness_files),
            "exercises_count": len(exercises),
            "types_count": types_count,
            "api_key_files": [path.name for path in key_files],
            "missing_exercise_images": missing_images,
        }
        if fitness_img_dir is not None:
            manifest["fitness_img_source"] = str(fitness_img_dir)
        if db_path is not None:
            manifest["fitness_db_source"] = str(db_path)
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
        if stage_root.exists():
            shutil.rmtree(stage_root, ignore_errors=True)

    return PackPrivateDataResult(
        zip_path=output_zip,
        api_keys_count=len(key_files),
        fitness_img_count=len(fitness_files),
        exercises_count=len(exercises),
        types_count=types_count,
        missing_exercise_images=tuple(missing_images),
    )
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
    if not sqlite_fitness.strip() or _PLACEHOLDER_RE.search(sqlite_fitness):
        msg = "config.json must set a real sqlite_fitness path (not a <YOUR_...> placeholder)."
        raise ValueError(msg)
    db_path = Path(sqlite_fitness).expanduser()
    img_dir = db_path.parent / "fitness_img"
    return db_path, img_dir
```

</details>

## 🔧 Function `selection_from_part_flags`

```python
def selection_from_part_flags(*, api_keys: bool, fitness: bool) -> PrivateDataSelection
```

Build a selection; when both flags are false, include every part.

<details>
<summary>Code:</summary>

```python
def selection_from_part_flags(*, api_keys: bool, fitness: bool) -> PrivateDataSelection:
    if not api_keys and not fitness:
        return PrivateDataSelection(api_keys=True, fitness=True)
    return PrivateDataSelection(api_keys=api_keys, fitness=fitness)
```

</details>
