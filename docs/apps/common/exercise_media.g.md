---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `exercise_media.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `is_exercise_media_path`](#-function-is_exercise_media_path)
- [🔧 Function `save_exercise_avif`](#-function-save_exercise_avif)

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

## 🔧 Function `save_exercise_avif`

```python
def save_exercise_avif(source: Path | str, exercise_name: str, avif_dir: Path | str, *, project_root: Path | None = None, max_size: int | None = None, high_max_size: int | None = None) -> Path
```

Optimize `source` into a small AVIF and, optionally, a high-resolution copy.

Writes `{avif_dir}/{exercise_name}.avif` (UI size). When `high_max_size` is set,
also writes `{avif_dir}/high/{exercise_name}.avif` for the lightbox. An existing
file with the same name is replaced.

Supports MP4, GIF, AVIF (animation preserved), PNG/JPEG/WEBP/BMP (static AVIF).

Args:

- `source` (`Path | str`): Input media file.
- `exercise_name` (`str`): Exercise name used as the AVIF filename stem.
- `avif_dir` (`Path | str`): Directory for exercise AVIF files (`fitness_img`).
- `project_root` (`Path | None`): Folder with `ffmpeg.exe` / `avifenc.exe`. Defaults to
  project root.
- `max_size` (`int | None`): Optional max width/height in pixels for the UI file.
- `high_max_size` (`int | None`): When set, also write a high-resolution AVIF using
  this max width/height. If that conversion fails after the small file was written,
  a leftover `{high}/{name}.avif` is removed so the lightbox does not show a stale
  image.

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
    target = _convert_source_to_avif(
        source_path,
        target_dir / f"{name}.avif",
        project_root=root,
        max_size=max_size,
    )

    if high_max_size is None:
        return target

    high_target = target_dir / FITNESS_IMG_HIGH_DIR / f"{name}.avif"
    try:
        _convert_source_to_avif(
            source_path,
            high_target,
            project_root=root,
            max_size=high_max_size,
        )
    except Exception:
        if high_target.is_file():
            high_target.unlink()
        raise

    return target
```

</details>
