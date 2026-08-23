"""Convert exercise media (video/image) to `fitness_img/{name}.avif`."""

from __future__ import annotations

import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

from PIL import Image

from harrix_swiss_knife.actions.common.image_optimize import find_optimized_output, optimize_image_file
from harrix_swiss_knife.paths import get_project_root

EXERCISE_MEDIA_EXTENSIONS = frozenset(
    {".png", ".jpg", ".jpeg", ".webp", ".gif", ".mp4", ".avif", ".bmp"},
)

FITNESS_IMG_HIGH_DIR = "high"

MEDIA_FILE_FILTER = "Media (*.mp4 *.avif *.gif *.png *.jpg *.jpeg *.webp *.bmp);;All files (*)"


def is_exercise_media_path(path: str | Path) -> bool:
    """Return `True` when `path` has a supported exercise media extension."""
    return Path(path).suffix.lower() in EXERCISE_MEDIA_EXTENSIONS


def save_exercise_avif(
    source: Path | str,
    exercise_name: str,
    avif_dir: Path | str,
    *,
    project_root: Path | None = None,
    max_size: int | None = None,
    high_max_size: int | None = None,
) -> Path:
    """Optimize `source` into a small AVIF and, optionally, a high-resolution copy.

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

    """
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


def _convert_source_to_avif(
    source_path: Path,
    target: Path,
    *,
    project_root: Path,
    max_size: int | None,
) -> Path:
    """Optimize `source_path` to AVIF and replace `target` when it already exists."""
    target.parent.mkdir(parents=True, exist_ok=True)

    with TemporaryDirectory(prefix="exercise_media_") as temp_folder:
        temp_dir = Path(temp_folder)
        work_source = _prepare_work_source(source_path, temp_dir)
        output_folder = temp_dir / "optimized"
        output_folder.mkdir(parents=True, exist_ok=True)

        optimize_image_file(
            work_source,
            output_folder,
            project_root,
            max_size=max_size,
            compare_png_avif=False,
            convert_png_to_avif=True,
        )

        optimized = find_optimized_output(output_folder, work_source.stem)
        if optimized is None or not optimized.is_file():
            msg = f"Optimization produced no output for {source_path.name}"
            raise ValueError(msg)
        if optimized.suffix.lower() != ".avif":
            msg = f"Expected AVIF output, got {optimized.suffix} for {source_path.name}"
            raise ValueError(msg)

        if target.exists():
            target.unlink()
        shutil.copy2(optimized, target)

    return target


def _prepare_work_source(source: Path, temp_dir: Path) -> Path:
    """Copy source into temp; convert BMP to PNG for the shared optimize pipeline."""
    if source.suffix.lower() != ".bmp":
        destination = temp_dir / source.name
        shutil.copy2(source, destination)
        return destination

    png_path = temp_dir / f"{source.stem}.png"
    with Image.open(source) as image:
        image.save(png_path, format="PNG")
    return png_path
