---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `exercise_media.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `RebuildSmallAvifResult`](#%EF%B8%8F-class-rebuildsmallavifresult)
- [🔧 Function `is_exercise_media_path`](#-function-is_exercise_media_path)
- [🔧 Function `rebuild_small_avifs_from_high`](#-function-rebuild_small_avifs_from_high)
- [🔧 Function `save_exercise_avif`](#-function-save_exercise_avif)

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

## 🔧 Function `save_exercise_avif`

```python
def save_exercise_avif(source: Path | str, exercise_name: str, avif_dir: Path | str, *, project_root: Path | None = None, max_size: int | None = None, high_max_size: int | None = None) -> Path
```

Optimize `source` into a small AVIF and, optionally, a high-resolution copy.

Writes `{avif_dir}/{exercise_name}.avif` (UI size). When `high_max_size` is set,
also writes `{avif_dir}/high/{exercise_name}.avif` for the lightbox. An existing
file with the same name is replaced.

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
        return _convert_source_to_avif(
            source_path,
            small_target,
            project_root=root,
            max_size=max_size,
        )

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

    return small_target
```

</details>
