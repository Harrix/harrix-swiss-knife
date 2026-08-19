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
- [🔧 Function `default_private_data_zip_path`](#-function-default_private_data_zip_path)
- [🔧 Function `install_private_data`](#-function-install_private_data)
- [🔧 Function `list_api_key_secret_files`](#-function-list_api_key_secret_files)
- [🔧 Function `pack_private_data`](#-function-pack_private_data)
- [🔧 Function `resolve_fitness_paths`](#-function-resolve_fitness_paths)

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
    fitness_db_path: Path
    fitness_img_dir: Path
    created_database: bool
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

## 🔧 Function `install_private_data`

```python
def install_private_data(*, project_root: Path, sqlite_fitness: str, zip_path: Path, recover_sql_path: Path) -> InstallPrivateDataResult
```

Install api-keys, overlay fitness_img, and upsert catalog into target DB.

Does not delete extra images or local-only exercises/types. Never writes
`process` or `weight`. Creates the DB from `recover.sql` when missing.

<details>
<summary>Code:</summary>

```python
def install_private_data(
    *,
    project_root: Path,
    sqlite_fitness: str,
    zip_path: Path,
    recover_sql_path: Path,
) -> InstallPrivateDataResult:
    if not zip_path.is_file():
        msg = f"ZIP not found: {zip_path}"
        raise FileNotFoundError(msg)

    db_path, fitness_img_dir = resolve_fitness_paths(sqlite_fitness)
    created_database = False
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

    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(stage_root)

        stage_api = stage_root / "api-keys"
        stage_img = stage_root / "fitness_img"
        catalog_file = stage_root / "fitness_catalog.json"

        if not stage_api.is_dir():
            msg = f"ZIP is missing api-keys/: {zip_path}"
            raise FileNotFoundError(msg)
        if not stage_img.is_dir():
            msg = f"ZIP is missing fitness_img/: {zip_path}"
            raise FileNotFoundError(msg)
        if not catalog_file.is_file():
            msg = f"ZIP is missing fitness_catalog.json: {zip_path}. Repack with the current pack-private-data action."
            raise FileNotFoundError(msg)

        dest_api = project_root / "api-keys"
        dest_api.mkdir(parents=True, exist_ok=True)
        key_files = sorted(p for p in stage_api.iterdir() if p.is_file() and p.suffix.lower() == ".txt")
        if not key_files:
            msg = f"ZIP api-keys/ has no *.txt files: {zip_path}"
            raise FileNotFoundError(msg)
        for key_file in key_files:
            shutil.copy2(key_file, dest_api / key_file.name)

        fitness_img_dir.mkdir(parents=True, exist_ok=True)
        img_files = sorted(p for p in stage_img.rglob("*") if p.is_file())
        if not img_files:
            msg = f"ZIP fitness_img/ is empty: {zip_path}"
            raise FileNotFoundError(msg)
        for img_file in img_files:
            rel = img_file.relative_to(stage_img)
            target = fitness_img_dir / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(img_file, target)

        catalog = load_fitness_catalog_json(catalog_file)
        try:
            stats = upsert_fitness_catalog(db_path, catalog)
        except sqlite3.Error as exc:
            err_text = str(exc).lower()
            if "locked" in err_text or "busy" in err_text:
                msg = f"Cannot write fitness database (is Fitness tracker open?): {db_path}\n{exc}"
                raise OSError(msg) from exc
            raise
    finally:
        if stage_root.exists():
            shutil.rmtree(stage_root, ignore_errors=True)

    return InstallPrivateDataResult(
        api_keys_count=len(key_files),
        fitness_img_count=len(img_files),
        catalog_stats=stats,
        fitness_db_path=db_path,
        fitness_img_dir=fitness_img_dir,
        created_database=created_database,
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
        p
        for p in api_keys_dir.iterdir()
        if p.is_file() and p.suffix.lower() == ".txt" and not p.name.endswith(".example.txt")
    )
```

</details>

## 🔧 Function `pack_private_data`

```python
def pack_private_data(*, project_root: Path, sqlite_fitness: str, output_zip: Path) -> PackPrivateDataResult
```

Pack api-keys secrets, fitness_img, and exercise catalog into `output_zip`.

<details>
<summary>Code:</summary>

```python
def pack_private_data(
    *,
    project_root: Path,
    sqlite_fitness: str,
    output_zip: Path,
) -> PackPrivateDataResult:
    api_keys_dir = project_root / "api-keys"
    key_files = list_api_key_secret_files(api_keys_dir)
    if not key_files:
        msg = f"No secret *.txt files found in {api_keys_dir} (excluding *.example.txt)."
        raise FileNotFoundError(msg)

    db_path, fitness_img_dir = resolve_fitness_paths(sqlite_fitness)
    if not fitness_img_dir.is_dir():
        msg = f"fitness_img folder not found: {fitness_img_dir}"
        raise FileNotFoundError(msg)
    fitness_files = sorted(p for p in fitness_img_dir.rglob("*") if p.is_file())
    if not fitness_files:
        msg = f"fitness_img folder is empty: {fitness_img_dir}"
        raise FileNotFoundError(msg)

    catalog = export_fitness_catalog(db_path)
    exercises = catalog["exercises"]
    types_count = sum(len(ex["types"]) for ex in exercises)

    stage_root = output_zip.parent / f".hsk-private-data-pack-{output_zip.stem}"
    if stage_root.exists():
        shutil.rmtree(stage_root, ignore_errors=True)
    stage_root.mkdir(parents=True, exist_ok=True)

    try:
        stage_api = stage_root / "api-keys"
        stage_api.mkdir(parents=True, exist_ok=True)
        for key_file in key_files:
            shutil.copy2(key_file, stage_api / key_file.name)

        stage_img = stage_root / "fitness_img"
        stage_img.mkdir(parents=True, exist_ok=True)
        for img_file in fitness_files:
            rel = img_file.relative_to(fitness_img_dir)
            target = stage_img / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(img_file, target)

        catalog_path = stage_root / "fitness_catalog.json"
        catalog_path.write_text(
            json.dumps(catalog, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        manifest: dict[str, Any] = {
            "created_utc": datetime.now(UTC).isoformat(),
            "fitness_img_source": str(fitness_img_dir),
            "fitness_db_source": str(db_path),
            "api_keys_count": len(key_files),
            "fitness_img_count": len(fitness_files),
            "exercises_count": len(exercises),
            "types_count": types_count,
            "api_key_files": [p.name for p in key_files],
        }
        (stage_root / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        output_zip.parent.mkdir(parents=True, exist_ok=True)
        if output_zip.exists():
            output_zip.unlink()

        with zipfile.ZipFile(output_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for file_path in stage_root.rglob("*"):
                if file_path.is_file():
                    zf.write(file_path, file_path.relative_to(stage_root).as_posix())
    finally:
        if stage_root.exists():
            shutil.rmtree(stage_root, ignore_errors=True)

    return PackPrivateDataResult(
        zip_path=output_zip,
        api_keys_count=len(key_files),
        fitness_img_count=len(fitness_files),
        exercises_count=len(exercises),
        types_count=types_count,
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
