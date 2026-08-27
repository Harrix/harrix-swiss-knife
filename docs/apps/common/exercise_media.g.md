---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `exercise_media.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `RebuildMinThumbnailResult`](#%EF%B8%8F-class-rebuildminthumbnailresult)
- [🏛️ Class `RebuildSmallAvifResult`](#%EF%B8%8F-class-rebuildsmallavifresult)
- [🏛️ Class `RebuildStaticThumbnailResult`](#%EF%B8%8F-class-rebuildstaticthumbnailresult)
- [🔧 Function `has_missing_min_thumbnails`](#-function-has_missing_min_thumbnails)
- [🔧 Function `has_missing_static_thumbnails`](#-function-has_missing_static_thumbnails)
- [🔧 Function `is_exercise_media_path`](#-function-is_exercise_media_path)
- [🔧 Function `rebuild_min_thumbnails_from_small`](#-function-rebuild_min_thumbnails_from_small)
- [🔧 Function `rebuild_small_avifs_from_high`](#-function-rebuild_small_avifs_from_high)
- [🔧 Function `rebuild_static_thumbnails_from_avif`](#-function-rebuild_static_thumbnails_from_avif)
- [🔧 Function `save_exercise_avif`](#-function-save_exercise_avif)

</details>

## 🏛️ Class `RebuildMinThumbnailResult`

```python
class RebuildMinThumbnailResult
```

Outcome of rebuilding table thumbnails in `fitness_img/min/`.

<details>
<summary>Code:</summary>

```python
class RebuildMinThumbnailResult:

    rebuilt: tuple[str, ...]
    skipped: tuple[str, ...]
    failed: tuple[tuple[str, str], ...]
```

</details>

## 🏛️ Class `RebuildSmallAvifResult`

```python
class RebuildSmallAvifResult
```

Outcome of rebuilding UI-sized AVIFs from `fitness_img/high/`.

<details>
<summary>Code:</summary>

```python
class RebuildSmallAvifResult:

    rebuilt: tuple[str, ...]
    skipped: tuple[str, ...]
    failed: tuple[tuple[str, str], ...]
```

</details>

## 🏛️ Class `RebuildStaticThumbnailResult`

```python
class RebuildStaticThumbnailResult
```

Outcome of rebuilding dialog previews in `fitness_img/static/`.

<details>
<summary>Code:</summary>

```python
class RebuildStaticThumbnailResult:

    rebuilt: tuple[str, ...]
    skipped: tuple[str, ...]
    failed: tuple[tuple[str, str], ...]
```

</details>

## 🔧 Function `has_missing_min_thumbnails`

```python
def has_missing_min_thumbnails(avif_dir: Path | str) -> bool
```

Return whether any UI AVIF lacks an up-to-date WebP under `min/`.

<details>
<summary>Code:</summary>

```python
def has_missing_min_thumbnails(avif_dir: Path | str) -> bool:
    target_dir = Path(avif_dir)
    min_dir = target_dir / FITNESS_IMG_MIN_DIR
    for small_path in target_dir.glob("*.avif"):
        if not small_path.is_file():
            continue
        min_target = min_dir / f"{small_path.stem}.webp"
        try:
            if not min_target.is_file():
                return True
            if min_target.stat().st_mtime < small_path.stat().st_mtime:
                return True
        except OSError:
            return True
    return False
```

</details>

## 🔧 Function `has_missing_static_thumbnails`

```python
def has_missing_static_thumbnails(avif_dir: Path | str) -> bool
```

Return whether any exercise lacks an up-to-date WebP under `static/`.

<details>
<summary>Code:</summary>

```python
def has_missing_static_thumbnails(avif_dir: Path | str) -> bool:
    target_dir = Path(avif_dir)
    static_dir = target_dir / FITNESS_IMG_STATIC_DIR
    for small_path in target_dir.glob("*.avif"):
        if not small_path.is_file():
            continue
        source = _exercise_hover_avif_path(target_dir, small_path.stem)
        if source is None:
            continue
        static_target = static_dir / f"{small_path.stem}.webp"
        try:
            if not static_target.is_file():
                return True
            if static_target.stat().st_mtime < source.stat().st_mtime:
                return True
        except OSError:
            return True
    return False
```

</details>

## 🔧 Function `is_exercise_media_path`

```python
def is_exercise_media_path(path: str | Path) -> bool
```

Return `True` when `path` has a supported exercise media extension.

<details>
<summary>Code:</summary>

```python
def is_exercise_media_path(path: str | Path) -> bool:
    return Path(path).suffix.lower() in EXERCISE_MEDIA_EXTENSIONS
```

</details>

## 🔧 Function `rebuild_min_thumbnails_from_small`

```python
def rebuild_min_thumbnails_from_small(avif_dir: Path | str, *, min_max_size: int) -> RebuildMinThumbnailResult
```

Write missing or stale static WebP thumbnails from UI-sized AVIFs.

<details>
<summary>Code:</summary>

```python
def rebuild_min_thumbnails_from_small(
    avif_dir: Path | str,
    *,
    min_max_size: int,
) -> RebuildMinThumbnailResult:
    target_dir = Path(avif_dir)
    min_dir = target_dir / FITNESS_IMG_MIN_DIR
    rebuilt: list[str] = []
    skipped: list[str] = []
    failed: list[tuple[str, str]] = []
    for small_path in sorted(target_dir.glob("*.avif")):
        if not small_path.is_file():
            continue
        name = small_path.stem
        min_target = min_dir / f"{name}.webp"
        try:
            if min_target.is_file() and min_target.stat().st_mtime >= small_path.stat().st_mtime:
                skipped.append(name)
                continue
            _write_min_webp_thumbnail(small_path, min_target, max_size=min_max_size)
        except Exception as error:
            failed.append((name, str(error)))
            continue
        rebuilt.append(name)
    return RebuildMinThumbnailResult(tuple(rebuilt), tuple(skipped), tuple(failed))
```

</details>

## 🔧 Function `rebuild_small_avifs_from_high`

```python
def rebuild_small_avifs_from_high(avif_dir: Path | str, *, max_size: int, project_root: Path | None = None) -> RebuildSmallAvifResult
```

Rewrite still or missing UI AVIFs from animated `high/` originals.

For each `{avif_dir}/high/{name}.avif` that is animated, writes
`{avif_dir}/{name}.avif` at `max_size`, keeping every frame.

<details>
<summary>Code:</summary>

```python
def rebuild_small_avifs_from_high(
    avif_dir: Path | str,
    *,
    max_size: int,
    project_root: Path | None = None,
) -> RebuildSmallAvifResult:
    root = project_root if project_root is not None else get_project_root()
    target_dir = Path(avif_dir)
    high_dir = target_dir / FITNESS_IMG_HIGH_DIR
    rebuilt: list[str] = []
    skipped: list[str] = []
    failed: list[tuple[str, str]] = []
    if not high_dir.is_dir():
        return RebuildSmallAvifResult((), (), ())

    for high_path in sorted(high_dir.glob("*.avif")):
        if not high_path.is_file():
            continue
        name = high_path.stem
        if not _avif_file_is_animated(high_path):
            skipped.append(name)
            continue
        small_target = target_dir / high_path.name
        try:
            _write_small_from_animated_avif(
                high_path,
                small_target,
                project_root=root,
                max_size=max_size,
            )
        except Exception as error:
            failed.append((name, str(error)))
            continue
        rebuilt.append(name)

    return RebuildSmallAvifResult(tuple(rebuilt), tuple(skipped), tuple(failed))
```

</details>

## 🔧 Function `rebuild_static_thumbnails_from_avif`

```python
def rebuild_static_thumbnails_from_avif(avif_dir: Path | str, *, static_max_size: int) -> RebuildStaticThumbnailResult
```

Write missing or stale static WebP previews from hover AVIF sources.

<details>
<summary>Code:</summary>

```python
def rebuild_static_thumbnails_from_avif(
    avif_dir: Path | str,
    *,
    static_max_size: int,
) -> RebuildStaticThumbnailResult:
    target_dir = Path(avif_dir)
    static_dir = target_dir / FITNESS_IMG_STATIC_DIR
    rebuilt: list[str] = []
    skipped: list[str] = []
    failed: list[tuple[str, str]] = []
    for small_path in sorted(target_dir.glob("*.avif")):
        if not small_path.is_file():
            continue
        name = small_path.stem
        source = _exercise_hover_avif_path(target_dir, name)
        if source is None:
            continue
        static_target = static_dir / f"{name}.webp"
        try:
            if static_target.is_file() and static_target.stat().st_mtime >= source.stat().st_mtime:
                skipped.append(name)
                continue
            _write_min_webp_thumbnail(source, static_target, max_size=static_max_size)
        except Exception as error:
            failed.append((name, str(error)))
            continue
        rebuilt.append(name)
    return RebuildStaticThumbnailResult(tuple(rebuilt), tuple(skipped), tuple(failed))
```

</details>

## 🔧 Function `save_exercise_avif`

```python
def save_exercise_avif(source: Path | str, exercise_name: str, avif_dir: Path | str, *, project_root: Path | None = None, max_size: int | None = None, high_max_size: int | None = None, min_max_size: int | None = None, static_max_size: int | None = None) -> Path
```

Optimize `source` into a small AVIF and, optionally, a high-resolution copy.

Writes `{avif_dir}/{exercise_name}.avif` (UI size). When `high_max_size` is set,
also writes `{avif_dir}/high/{exercise_name}.avif` for the lightbox. When
`min_max_size` is set, also writes `{avif_dir}/min/{exercise_name}.webp` for
table icons. An existing file with the same name is replaced.

When the high-resolution file is animated, the small UI file is resized from it
so every frame is kept. Static sources stay static at both sizes.

Supports MP4, GIF, AVIF (animation preserved), PNG/JPEG/WEBP/BMP (static AVIF).

Args:

- `source` (`Path | str`): Input media file.
- `exercise_name` (`str`): Exercise name used as the AVIF filename stem.
- `avif_dir` (`Path | str`): Directory for exercise AVIF files (`fitness_img`).
- `project_root` (`Path | None`): Folder with `ffmpeg.exe` / `avifenc.exe`. Defaults to
  project root.
- `max_size` (`int | None`): Optional max width/height in pixels for the UI file.
- `high_max_size` (`int | None`): When set, also write a high-resolution AVIF using
  this max width/height. Both files are replaced together after conversion succeeds.
- `min_max_size` (`int | None`): When set, also write a static WebP thumbnail under
  `min/` for fast table icons.
- `static_max_size` (`int | None`): When set, also write a static WebP preview under
  `static/` for the Select Exercise dialog.

Returns:

- `Path`: Path to the written small AVIF file.

Raises:

- `ValueError`: Unsupported extension, empty name, or optimization produced no AVIF.
- `FileNotFoundError`: Source file does not exist.
- `RuntimeError`: External tools failed during conversion.

<details>
<summary>Code:</summary>

```python
def save_exercise_avif(
    source: Path | str,
    exercise_name: str,
    avif_dir: Path | str,
    *,
    project_root: Path | None = None,
    max_size: int | None = None,
    high_max_size: int | None = None,
    min_max_size: int | None = None,
    static_max_size: int | None = None,
) -> Path:
    name = exercise_name.strip()
    if not name:
        msg = "Exercise name is required to save media"
        raise ValueError(msg)

    source_path = Path(source)
    if not source_path.is_file():
        msg = f"Media file not found: {source_path}"
        raise FileNotFoundError(msg)

    ext = source_path.suffix.lower()
    if ext not in EXERCISE_MEDIA_EXTENSIONS:
        msg = f"Unsupported media type: {source_path.suffix}"
        raise ValueError(msg)

    root = project_root if project_root is not None else get_project_root()
    target_dir = Path(avif_dir)
    small_target = target_dir / f"{name}.avif"

    if high_max_size is None:
        written = _convert_source_to_avif(
            source_path,
            small_target,
            project_root=root,
            max_size=max_size,
        )
        if min_max_size is not None:
            min_target = target_dir / FITNESS_IMG_MIN_DIR / f"{name}.webp"
            _write_min_webp_thumbnail(written, min_target, max_size=min_max_size)
        if static_max_size is not None:
            static_source = _exercise_hover_avif_path(target_dir, name) or written
            static_target = target_dir / FITNESS_IMG_STATIC_DIR / f"{name}.webp"
            _write_min_webp_thumbnail(static_source, static_target, max_size=static_max_size)
        return written

    high_target = target_dir / FITNESS_IMG_HIGH_DIR / f"{name}.avif"
    with TemporaryDirectory(prefix="exercise_media_pair_") as temp_folder:
        temp_dir = Path(temp_folder)
        temp_high = temp_dir / f"{name}-high.avif"
        temp_small = temp_dir / f"{name}-small.avif"
        _convert_source_to_avif(
            source_path,
            temp_high,
            project_root=root,
            max_size=high_max_size,
        )
        if _avif_file_is_animated(temp_high):
            _write_small_from_animated_avif(
                temp_high,
                temp_small,
                project_root=root,
                max_size=max_size,
            )
        else:
            _convert_source_to_avif(
                source_path,
                temp_small,
                project_root=root,
                max_size=max_size,
            )
        _replace_file(temp_high, high_target)
        _replace_file(temp_small, small_target)

    if min_max_size is not None:
        min_target = target_dir / FITNESS_IMG_MIN_DIR / f"{name}.webp"
        _write_min_webp_thumbnail(small_target, min_target, max_size=min_max_size)
    if static_max_size is not None:
        static_source = _exercise_hover_avif_path(target_dir, name) or small_target
        static_target = target_dir / FITNESS_IMG_STATIC_DIR / f"{name}.webp"
        _write_min_webp_thumbnail(static_source, static_target, max_size=static_max_size)

    return small_target
```

</details>
