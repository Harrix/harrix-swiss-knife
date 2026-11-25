---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `ingest.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `IngestResult`](#%EF%B8%8F-class-ingestresult)
- [🔧 Function `ingest_backup_folder`](#-function-ingest_backup_folder)
- [🔧 Function `ingest_backup_zip`](#-function-ingest_backup_zip)
- [🔧 Function `ingest_player_data`](#-function-ingest_player_data)
- [🔧 Function `iso_from_mtime`](#-function-iso_from_mtime)
- [🔧 Function `iso_now`](#-function-iso_now)
- [🔧 Function `seed_official_catalog`](#-function-seed_official_catalog)

</details>

## 🏛️ Class `IngestResult`

```python
class IngestResult
```

Outcome of one ingest / seed operation.

<details>
<summary>Code:</summary>

```python
class IngestResult:

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
```

</details>

## 🔧 Function `ingest_backup_folder`

```python
def ingest_backup_folder(db_path: Path | str, folder: Path | str, *, seed_catalog: bool = True) -> IngestResult
```

Ingest all `beat-saber-*.zip` files under a folder (oldest first).

<details>
<summary>Code:</summary>

```python
def ingest_backup_folder(db_path: Path | str, folder: Path | str, *, seed_catalog: bool = True) -> IngestResult:
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
```

</details>

## 🔧 Function `ingest_backup_zip`

```python
def ingest_backup_zip(db_path: Path | str, zip_path: Path | str, *, source_override: str | None = None, seed_catalog: bool = True) -> IngestResult
```

Ingest `PlayerData.dat` from an HSK Beat Saber backup ZIP.

<details>
<summary>Code:</summary>

```python
def ingest_backup_zip(
    db_path: Path | str,
    zip_path: Path | str,
    *,
    source_override: str | None = None,
    seed_catalog: bool = True,
) -> IngestResult:
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
```

</details>

## 🔧 Function `ingest_player_data`

```python
def ingest_player_data(db_path: Path | str, player_data_path: Path | str, *, source: str, observed_at: str | None = None, backup_path: str | None = None, note: str = '', seed_catalog: bool = True) -> IngestResult
```

Parse `PlayerData.dat` and upsert clears for `source` (`pc` / `quest` / `zip`).

<details>
<summary>Code:</summary>

```python
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
```

</details>

## 🔧 Function `iso_from_mtime`

```python
def iso_from_mtime(path: Path) -> str
```

Return ISO timestamp from a file's mtime.

<details>
<summary>Code:</summary>

```python
def iso_from_mtime(path: Path) -> str:
    stamp = datetime.fromtimestamp(path.stat().st_mtime).astimezone()
    return stamp.isoformat(timespec="seconds")
```

</details>

## 🔧 Function `iso_now`

```python
def iso_now() -> str
```

Return current local ISO timestamp with offset.

<details>
<summary>Code:</summary>

```python
def iso_now() -> str:
    return datetime.now(UTC).astimezone().isoformat(timespec="seconds")
```

</details>

## 🔧 Function `seed_official_catalog`

```python
def seed_official_catalog(db_path: Path | str) -> IngestResult
```

Upsert official songs and Standard Easy — Expert+ modes.

<details>
<summary>Code:</summary>

```python
def seed_official_catalog(db_path: Path | str) -> IngestResult:
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
```

</details>
