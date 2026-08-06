---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `exif_datetime.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ExifDatetimeResult`](#%EF%B8%8F-class-exifdatetimeresult)
- [🔧 Function `format_exif_datetime`](#-function-format_exif_datetime)
- [🔧 Function `iter_exif_image_files`](#-function-iter_exif_image_files)
- [🔧 Function `set_exif_datetime`](#-function-set_exif_datetime)
- [🔧 Function `set_exif_datetime_in_folder`](#-function-set_exif_datetime_in_folder)
- [🔧 Function `summarize_exif_datetime_results`](#-function-summarize_exif_datetime_results)

</details>

## 🏛️ Class `ExifDatetimeResult`

```python
class ExifDatetimeResult
```

Outcome of setting EXIF date/time on one image.

<details>
<summary>Code:</summary>

```python
class ExifDatetimeResult:

    path: Path
    status: Literal["updated", "skipped", "error"]
    detail: str = ""
```

</details>

## 🔧 Function `format_exif_datetime`

```python
def format_exif_datetime(value: datetime) -> str
```

Format a datetime as EXIF `YYYY:MM:DD HH:MM:SS`.

<details>
<summary>Code:</summary>

```python
def format_exif_datetime(value: datetime) -> str:
    return value.strftime("%Y:%m:%d %H:%M:%S")
```

</details>

## 🔧 Function `iter_exif_image_files`

```python
def iter_exif_image_files(folder: Path) -> list[Path]
```

Return image paths under `folder` that support EXIF date tags.

<details>
<summary>Code:</summary>

```python
def iter_exif_image_files(folder: Path, *, recursive: bool = True) -> list[Path]:
    if recursive:
        paths = [path for path in folder.rglob("*") if path.is_file()]
    else:
        paths = [path for path in folder.iterdir() if path.is_file()]
    return sorted(path for path in paths if path.suffix.lower() in EXIF_IMAGE_EXTENSIONS)
```

</details>

## 🔧 Function `set_exif_datetime`

```python
def set_exif_datetime(path: Path, value: datetime) -> ExifDatetimeResult
```

Write DateTime, DateTimeOriginal, and DateTimeDigitized on `path`.

Re-saves the image with Pillow. JPEG uses `quality='keep'` when possible
to limit re-encode quality loss. Other EXIF tags already present are kept
when Pillow preserves them on save.

<details>
<summary>Code:</summary>

```python
def set_exif_datetime(path: Path, value: datetime) -> ExifDatetimeResult:
    if path.suffix.lower() not in EXIF_IMAGE_EXTENSIONS:
        return ExifDatetimeResult(path, "skipped", "unsupported extension")

    dt_str = format_exif_datetime(value)
    try:
        with Image.open(path) as image:
            image.load()
            exif = image.getexif()
            exif[Base.DateTime] = dt_str
            exif_ifd = exif.get_ifd(IFD.Exif)
            exif_ifd[Base.DateTimeOriginal] = dt_str
            exif_ifd[Base.DateTimeDigitized] = dt_str
            exif[IFD.Exif] = exif_ifd

            fmt = image.format
            if path.suffix.lower() in _JPEG_EXTENSIONS:
                image.save(path, format=fmt, exif=exif, quality="keep")
            else:
                image.save(path, format=fmt, exif=exif)
    except OSError as exc:
        return ExifDatetimeResult(path, "error", str(exc))
    except ValueError as exc:
        return ExifDatetimeResult(path, "error", str(exc))

    return ExifDatetimeResult(path, "updated", dt_str)
```

</details>

## 🔧 Function `set_exif_datetime_in_folder`

```python
def set_exif_datetime_in_folder(folder: Path, value: datetime) -> list[ExifDatetimeResult]
```

Set EXIF date/time on all supported images under `folder`.

<details>
<summary>Code:</summary>

```python
def set_exif_datetime_in_folder(
    folder: Path,
    value: datetime,
    *,
    recursive: bool = True,
) -> list[ExifDatetimeResult]:
    return [set_exif_datetime(path, value) for path in iter_exif_image_files(folder, recursive=recursive)]
```

</details>

## 🔧 Function `summarize_exif_datetime_results`

```python
def summarize_exif_datetime_results(results: list[ExifDatetimeResult]) -> str
```

Build a short human-readable summary of batch EXIF updates.

<details>
<summary>Code:</summary>

```python
def summarize_exif_datetime_results(results: list[ExifDatetimeResult]) -> str:
    updated = sum(1 for item in results if item.status == "updated")
    skipped = sum(1 for item in results if item.status == "skipped")
    errors = sum(1 for item in results if item.status == "error")
    lines = [
        f"Updated: {updated}",
        f"Skipped: {skipped}",
        f"Errors: {errors}",
    ]
    for item in results:
        if item.status == "error":
            lines.append(f"❌ {item.path}: {item.detail}")
        elif item.status == "updated":
            lines.append(f"✅ {item.path.name} → {item.detail}")
    return "\n".join(lines)
```

</details>
