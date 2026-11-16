---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `pack.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `BackupPart`](#%EF%B8%8F-class-backuppart)
- [🏛️ Class `BackupResult`](#%EF%B8%8F-class-backupresult)
- [🔧 Function `estimate_part_sizes`](#-function-estimate_part_sizes)
- [🔧 Function `format_backup_report`](#-function-format_backup_report)
- [🔧 Function `pack_cursor_backup`](#-function-pack_cursor_backup)
- [🔧 Function `parts_from_labels`](#-function-parts_from_labels)

</details>

## 🏛️ Class `BackupPart`

```python
class BackupPart(StrEnum)
```

Selectable Cursor backup sections.

<details>
<summary>Code:</summary>

```python
class BackupPart(StrEnum):

    USER = "cursor-user"
    DOT_CURSOR = "dot-cursor"
    EXTENSIONS = "dot-cursor-extensions"
    PROJECT_CURSOR = "project-cursor"
```

</details>

## 🏛️ Class `BackupResult`

```python
class BackupResult
```

Outcome of packing a Cursor backup ZIP.

<details>
<summary>Code:</summary>

```python
class BackupResult:

    zip_path: Path
    parts: tuple[BackupPart, ...]
    file_count: int
    byte_count: int
    skipped: tuple[str, ...] = ()
    project_cursor_dirs: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
```

</details>

## 🔧 Function `estimate_part_sizes`

```python
def estimate_part_sizes(parts: Iterable[BackupPart] | None = None) -> dict[BackupPart, int]
```

Return approximate on-disk byte sizes for each backup part.

<details>
<summary>Code:</summary>

```python
def estimate_part_sizes(
    parts: Iterable[BackupPart] | None = None,
) -> dict[BackupPart, int]:
    wanted = tuple(parts) if parts is not None else tuple(BackupPart)
    sizes: dict[BackupPart, int] = {}
    for part in wanted:
        if part is BackupPart.USER:
            sizes[part] = _directory_size(cursor_user_dir())
        elif part is BackupPart.DOT_CURSOR:
            sizes[part] = sum(_path_size(path) for path in iter_dot_cursor_entries())
        elif part is BackupPart.EXTENSIONS:
            sizes[part] = _directory_size(cursor_dot_dir() / "extensions")
        elif part is BackupPart.PROJECT_CURSOR:
            sizes[part] = sum(_directory_size(path) for path in discover_project_cursor_dirs())
    return sizes
```

</details>

## 🔧 Function `format_backup_report`

```python
def format_backup_report(result: BackupResult) -> str
```

Return a short markdown-ish report for the result dialog.

<details>
<summary>Code:</summary>

```python
def format_backup_report(result: BackupResult) -> str:
    size_mb = result.byte_count / (1024 * 1024)
    zip_mb = result.zip_path.stat().st_size / (1024 * 1024) if result.zip_path.is_file() else 0.0
    lines = [
        f"ZIP: `{result.zip_path}` ({zip_mb:.1f} MB)",
        f"Packed {result.file_count} file(s), {size_mb:.1f} MB source data.",
        "Parts:",
    ]
    lines.extend(f"- {PART_LABELS[part]}" for part in result.parts)
    if result.project_cursor_dirs:
        lines.append("Project `.cursor` folders:")
        lines.extend(f"- `{path}`" for path in result.project_cursor_dirs)
    if result.skipped:
        lines.append(f"Skipped {len(result.skipped)} path(s) (locked or unreadable).")
        lines.extend(f"- `{path}`" for path in result.skipped[:_SKIPPED_PREVIEW_LIMIT])
        if len(result.skipped) > _SKIPPED_PREVIEW_LIMIT:
            lines.append(f"- … and {len(result.skipped) - _SKIPPED_PREVIEW_LIMIT} more")
    if result.warnings:
        lines.extend(result.warnings)
    lines.append("")
    lines.append(
        "Restore: fully quit Cursor, then unpack over `%APPDATA%\\Cursor\\User`, "
        "`%USERPROFILE%\\.cursor`, and each project `.cursor` as needed."
    )
    return "\n".join(lines)
```

</details>

## 🔧 Function `pack_cursor_backup`

```python
def pack_cursor_backup(output_zip: Path, parts: Iterable[BackupPart], *, should_cancel: Callable[[], bool] | None = None) -> BackupResult
```

Write selected Cursor data into `output_zip` and return a summary.

<details>
<summary>Code:</summary>

```python
def pack_cursor_backup(
    output_zip: Path,
    parts: Iterable[BackupPart],
    *,
    should_cancel: Callable[[], bool] | None = None,
) -> BackupResult:
    selected = tuple(dict.fromkeys(parts))
    if not selected:
        msg = "No Cursor backup parts selected."
        raise ValueError(msg)

    output_zip = output_zip.expanduser().resolve()
    output_zip.parent.mkdir(parents=True, exist_ok=True)
    if output_zip.exists():
        output_zip.unlink()

    state = _PackState()
    warnings: list[str] = []
    cancel = should_cancel or (lambda: False)

    try:
        with zipfile.ZipFile(output_zip, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=1) as archive:
            for part in selected:
                _raise_if_cancelled(cancel)
                _pack_part(archive, part, state, cancel=cancel)

            manifest = {
                "created_at": datetime.now(UTC).astimezone().isoformat(timespec="seconds"),
                "parts": [part.value for part in selected],
                "file_count": state.file_count,
                "byte_count": state.byte_count,
                "skipped": state.skipped,
                "project_cursor_dirs": state.project_cursor_dirs,
                "sources": {
                    "user": str(cursor_user_dir()),
                    "dot_cursor": str(cursor_dot_dir()),
                },
            }
            archive.writestr(_MANIFEST_NAME, json.dumps(json_safe(manifest), indent=2, ensure_ascii=False) + "\n")
    except DownloadCancelledError:
        if output_zip.is_file():
            output_zip.unlink(missing_ok=True)
        raise

    if state.skipped:
        warnings.append("Some files were skipped; close Cursor and re-run for a consistent chat DB copy.")

    return BackupResult(
        zip_path=output_zip,
        parts=selected,
        file_count=state.file_count,
        byte_count=state.byte_count,
        skipped=tuple(state.skipped),
        project_cursor_dirs=tuple(state.project_cursor_dirs),
        warnings=tuple(warnings),
    )
```

</details>

## 🔧 Function `parts_from_labels`

```python
def parts_from_labels(labels: Iterable[str]) -> list[BackupPart]
```

Map dialog checkbox labels to [`BackupPart`](#%EF%B8%8F-class-backuppart) values.

<details>
<summary>Code:</summary>

```python
def parts_from_labels(labels: Iterable[str]) -> list[BackupPart]:
    parts: list[BackupPart] = []
    for label in labels:
        part = LABEL_TO_PART.get(label)
        if part is not None and part not in parts:
            parts.append(part)
    return parts
```

</details>
