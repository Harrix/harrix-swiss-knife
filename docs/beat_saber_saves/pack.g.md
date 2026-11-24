---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `pack.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `BeatSaberTransferResult`](#%EF%B8%8F-class-beatsabertransferresult)
- [🔧 Function `export_pc_saves`](#-function-export_pc_saves)
- [🔧 Function `export_quest_saves`](#-function-export_quest_saves)
- [🔧 Function `import_pc_saves`](#-function-import_pc_saves)
- [🔧 Function `import_quest_saves`](#-function-import_quest_saves)

</details>

## 🏛️ Class `BeatSaberTransferResult`

```python
class BeatSaberTransferResult
```

Outcome of an export or import.

<details>
<summary>Code:</summary>

```python
class BeatSaberTransferResult:

    ok: bool
    mode: str
    source: str
    files: list[str] = field(default_factory=list)
    zip_path: Path | None = None
    message: str = ""
    lines: list[str] = field(default_factory=list)
```

</details>

## 🔧 Function `export_pc_saves`

```python
def export_pc_saves(zip_path: Path, *, should_cancel: Callable[[], bool] | None = None) -> BeatSaberTransferResult
```

Copy PC LocalLow save files into a ZIP.

<details>
<summary>Code:</summary>

```python
def export_pc_saves(
    zip_path: Path,
    *,
    should_cancel: Callable[[], bool] | None = None,
) -> BeatSaberTransferResult:
    folder = pc_saves_dir()
    if not folder.is_dir():
        return BeatSaberTransferResult(
            ok=False,
            mode="export",
            source="pc",
            message=f"PC saves folder not found: `{folder}`",
        )
    collected = _collect_local_files(folder)
    if REQUIRED_SAVE_NAME not in collected:
        return BeatSaberTransferResult(
            ok=False,
            mode="export",
            source="pc",
            message=f"`{REQUIRED_SAVE_NAME}` not found in `{folder}`",
        )
    if should_cancel and should_cancel():
        return BeatSaberTransferResult(ok=False, mode="export", source="pc", message="Cancelled.")
    return _write_zip(zip_path, collected, source="pc", mode="export")
```

</details>

## 🔧 Function `export_quest_saves`

```python
def export_quest_saves(adb: Path, serial: str, zip_path: Path, *, should_cancel: Callable[[], bool] | None = None) -> BeatSaberTransferResult
```

Pull Quest Beat Saber save files into a ZIP via adb.

<details>
<summary>Code:</summary>

```python
def export_quest_saves(
    adb: Path,
    serial: str,
    zip_path: Path,
    *,
    should_cancel: Callable[[], bool] | None = None,
) -> BeatSaberTransferResult:
    remote_dir = quest_remote_files_dir()
    lines: list[str] = []
    with tempfile.TemporaryDirectory(prefix="hsk-beat-saber-") as tmp:
        tmp_dir = Path(tmp)
        collected: dict[str, Path] = {}
        for name in SAVE_FILE_NAMES:
            if should_cancel and should_cancel():
                return BeatSaberTransferResult(
                    ok=False,
                    mode="export",
                    source="quest",
                    message="Cancelled.",
                    lines=lines,
                )
            remote = f"{remote_dir}/{name}"
            local = tmp_dir / name
            process = adb_pull(adb, serial, remote, local)
            if process.returncode == 0 and local.is_file() and local.stat().st_size > 0:
                collected[name] = local
                lines.append(f"Pulled `{name}`")
            else:
                detail = "\n".join(part for part in (process.stdout.strip(), process.stderr.strip()) if part)
                if detail:
                    lines.append(f"Skip `{name}`: {detail}")
                else:
                    lines.append(f"Skip `{name}` (not on device or inaccessible)")

        if REQUIRED_SAVE_NAME not in collected:
            hint = (
                "Could not pull `PlayerData.dat`. Confirm Beat Saber is installed, "
                "USB file access is allowed, and Android/data is readable over adb "
                f"(path `{remote_dir}`)."
            )
            return BeatSaberTransferResult(
                ok=False,
                mode="export",
                source="quest",
                message=hint,
                lines=lines,
            )
        result = _write_zip(zip_path, collected, source="quest", mode="export")
        result.lines = [*lines, *result.lines]
        return result
```

</details>

## 🔧 Function `import_pc_saves`

```python
def import_pc_saves(zip_path: Path, *, should_cancel: Callable[[], bool] | None = None) -> BeatSaberTransferResult
```

Restore save files from a ZIP into the PC LocalLow folder.

<details>
<summary>Code:</summary>

```python
def import_pc_saves(
    zip_path: Path,
    *,
    should_cancel: Callable[[], bool] | None = None,
) -> BeatSaberTransferResult:
    extracted, err = _extract_zip_saves(zip_path)
    if err or extracted is None:
        return BeatSaberTransferResult(ok=False, mode="import", source="pc", message=err or "Invalid ZIP.")
    if REQUIRED_SAVE_NAME not in extracted:
        _cleanup_temp_map(extracted)
        return BeatSaberTransferResult(
            ok=False,
            mode="import",
            source="pc",
            message=f"ZIP is missing `{REQUIRED_SAVE_NAME}`.",
        )

    folder = pc_saves_dir()
    folder.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    lines: list[str] = []
    try:
        for name, src in extracted.items():
            if should_cancel and should_cancel():
                return BeatSaberTransferResult(
                    ok=False,
                    mode="import",
                    source="pc",
                    message="Cancelled.",
                    files=written,
                    zip_path=zip_path,
                    lines=lines,
                )
            dest = folder / name
            shutil.copy2(src, dest)
            written.append(name)
            lines.append(f"Wrote `{dest}`")
    finally:
        _cleanup_temp_map(extracted)

    return BeatSaberTransferResult(
        ok=True,
        mode="import",
        source="pc",
        files=written,
        zip_path=zip_path,
        message=f"Imported {len(written)} file(s) into `{folder}`.",
        lines=lines,
    )
```

</details>

## 🔧 Function `import_quest_saves`

```python
def import_quest_saves(adb: Path, serial: str, zip_path: Path, *, should_cancel: Callable[[], bool] | None = None) -> BeatSaberTransferResult
```

Push save files from a ZIP onto Quest via adb.

<details>
<summary>Code:</summary>

```python
def import_quest_saves(
    adb: Path,
    serial: str,
    zip_path: Path,
    *,
    should_cancel: Callable[[], bool] | None = None,
) -> BeatSaberTransferResult:
    extracted, err = _extract_zip_saves(zip_path)
    if err or extracted is None:
        return BeatSaberTransferResult(ok=False, mode="import", source="quest", message=err or "Invalid ZIP.")
    if REQUIRED_SAVE_NAME not in extracted:
        _cleanup_temp_map(extracted)
        return BeatSaberTransferResult(
            ok=False,
            mode="import",
            source="quest",
            message=f"ZIP is missing `{REQUIRED_SAVE_NAME}`.",
        )

    remote_dir = quest_remote_files_dir()
    written: list[str] = []
    lines: list[str] = []
    try:
        for name, src in extracted.items():
            if should_cancel and should_cancel():
                return BeatSaberTransferResult(
                    ok=False,
                    mode="import",
                    source="quest",
                    message="Cancelled.",
                    files=written,
                    zip_path=zip_path,
                    lines=lines,
                )
            remote = f"{remote_dir}/{name}"
            process = adb_push(adb, serial, src, remote)
            detail = "\n".join(part for part in (process.stdout.strip(), process.stderr.strip()) if part)
            if process.returncode != 0:
                lines.append(f"❌ Failed to push `{name}`: {detail or process.returncode}")
                return BeatSaberTransferResult(
                    ok=False,
                    mode="import",
                    source="quest",
                    files=written,
                    zip_path=zip_path,
                    message=f"adb push failed for `{name}`.",
                    lines=lines,
                )
            written.append(name)
            lines.append(f"Pushed `{name}` → `{remote}`")
    finally:
        _cleanup_temp_map(extracted)

    return BeatSaberTransferResult(
        ok=True,
        mode="import",
        source="quest",
        files=written,
        zip_path=zip_path,
        message=f"Imported {len(written)} file(s) to Quest (`{remote_dir}`).",
        lines=lines,
    )
```

</details>
