"""Convert exercise media (video/image) to `fitness_img/{name}.avif`."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory

from harrix_pylib.img_tools import process_animated_avif
from PIL import Image, ImageOps

from harrix_swiss_knife.actions.common.image_optimize import find_optimized_output, optimize_image_file
from harrix_swiss_knife.paths import get_project_root

EXERCISE_MEDIA_EXTENSIONS = frozenset(
    {".png", ".jpg", ".jpeg", ".webp", ".gif", ".mp4", ".avif", ".bmp"},
)

FITNESS_IMG_HIGH_DIR = "high"
FITNESS_IMG_MIN_DIR = "min"
FITNESS_IMG_STATIC_DIR = "static"
MIN_THUMBNAIL_EXTENSIONS = (".webp", ".jpg", ".jpeg", ".avif")

MEDIA_FILE_FILTER = "Media (*.mp4 *.avif *.gif *.png *.jpg *.jpeg *.webp *.bmp);;All files (*)"


@dataclass(frozen=True, slots=True)
class RebuildMinThumbnailResult:
    """Outcome of rebuilding table thumbnails in `fitness_img/min/`."""

    rebuilt: tuple[str, ...]
    skipped: tuple[str, ...]
    failed: tuple[tuple[str, str], ...]


@dataclass(frozen=True, slots=True)
class RebuildStaticThumbnailResult:
    """Outcome of rebuilding dialog previews in `fitness_img/static/`."""

    rebuilt: tuple[str, ...]
    skipped: tuple[str, ...]
    failed: tuple[tuple[str, str], ...]


@dataclass(frozen=True, slots=True)
class RebuildSmallAvifResult:
    """Outcome of rebuilding UI-sized AVIFs from `fitness_img/high/`."""

    rebuilt: tuple[str, ...]
    skipped: tuple[str, ...]
    failed: tuple[tuple[str, str], ...]


def has_missing_min_thumbnails(avif_dir: Path | str) -> bool:
    """Return whether any UI AVIF lacks an up-to-date WebP under `min/`."""
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


def has_missing_static_thumbnails(avif_dir: Path | str) -> bool:
    """Return whether any exercise lacks an up-to-date WebP under `static/`."""
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


def is_exercise_media_path(path: str | Path) -> bool:
    """Return `True` when `path` has a supported exercise media extension."""
    return Path(path).suffix.lower() in EXERCISE_MEDIA_EXTENSIONS


def rebuild_min_thumbnails_from_small(
    avif_dir: Path | str,
    *,
    min_max_size: int,
) -> RebuildMinThumbnailResult:
    """Write missing or stale static WebP thumbnails from UI-sized AVIFs."""
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


def rebuild_static_thumbnails_from_avif(
    avif_dir: Path | str,
    *,
    static_max_size: int,
) -> RebuildStaticThumbnailResult:
    """Write missing or stale static WebP previews from hover AVIF sources."""
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


def rebuild_small_avifs_from_high(
    avif_dir: Path | str,
    *,
    max_size: int,
    project_root: Path | None = None,
) -> RebuildSmallAvifResult:
    """Rewrite still or missing UI AVIFs from animated `high/` originals.

    For each `{avif_dir}/high/{name}.avif` that is animated, writes
    `{avif_dir}/{name}.avif` at `max_size`, keeping every frame.

    """
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
    """Optimize `source` into a small AVIF and, optionally, a high-resolution copy.

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


def _exercise_hover_avif_path(avif_dir: Path, name: str) -> Path | None:
    """Return the AVIF file used for dialog hover previews."""
    small = avif_dir / f"{name}.avif"
    high = avif_dir / FITNESS_IMG_HIGH_DIR / f"{name}.avif"
    small_exists = small.is_file()
    high_exists = high.is_file()
    if (
        high_exists
        and _avif_file_is_animated(high)
        and (not small_exists or not _avif_file_is_animated(small))
    ):
        return high
    if small_exists:
        return small
    return high if high_exists else None


def _avif_file_is_animated(avif_path: Path) -> bool:
    """Return whether `avif_path` has more than one frame."""
    try:
        import pillow_avif  # noqa: F401, PLC0415
    except ImportError:
        return False
    try:
        with Image.open(avif_path) as image:
            return bool(getattr(image, "is_animated", False) and getattr(image, "n_frames", 1) > 1)
    except Exception:
        return False


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

        _replace_file(optimized, target)

    return target


def _pil_frame_to_rgb(image: Image.Image) -> Image.Image:
    frame = ImageOps.exif_transpose(image)
    if frame.mode in ("RGBA", "LA", "P"):
        background = Image.new("RGB", frame.size, (255, 255, 255))
        if frame.mode == "P":
            frame = frame.convert("RGBA")
        if frame.mode in ("RGBA", "LA"):
            background.paste(frame, mask=frame.split()[-1])
        else:
            background.paste(frame)
        return background
    if frame.mode != "RGB":
        return frame.convert("RGB")
    return frame


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


def _replace_file(source: Path, target: Path) -> None:
    """Copy `source` over `target`, replacing an existing file."""
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        target.unlink()
    shutil.copy2(source, target)


def _write_min_webp_thumbnail(source: Path, target: Path, *, max_size: int) -> Path:
    """Write a static WebP thumbnail for table icons."""
    target.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source) as image:
        if getattr(image, "is_animated", False):
            image.seek(0)
        frame = _pil_frame_to_rgb(image.copy())
        frame.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        if target.exists():
            target.unlink()
        frame.save(target, format="WEBP", quality=75, method=4)
    return target


def _write_small_from_animated_avif(
    high_path: Path,
    target: Path,
    *,
    project_root: Path,
    max_size: int | None,
) -> Path:
    """Resize an animated high-resolution AVIF to the UI size, keeping every frame."""
    target.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix="exercise_small_") as temp_folder:
        temp_target = Path(temp_folder) / "small.avif"
        process_animated_avif(high_path, temp_target, project_root, max_size=max_size)
        if not temp_target.is_file():
            msg = f"Animated shrink produced no output for {high_path.name}"
            raise ValueError(msg)
        _replace_file(temp_target, target)
    return target
