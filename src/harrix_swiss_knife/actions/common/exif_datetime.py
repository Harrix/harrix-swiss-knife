"""Set EXIF date/time tags on image files with Pillow."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from PIL import Image
from PIL.ExifTags import IFD, Base

if TYPE_CHECKING:
    from datetime import datetime
    from pathlib import Path

EXIF_IMAGE_EXTENSIONS = frozenset({".jpg", ".jpeg", ".tif", ".tiff", ".webp"})

_JPEG_EXTENSIONS = frozenset({".jpg", ".jpeg"})


@dataclass(frozen=True, slots=True)
class ExifDatetimeResult:
    """Outcome of setting EXIF date/time on one image."""

    path: Path
    status: Literal["updated", "skipped", "error"]
    detail: str = ""


def format_exif_datetime(value: datetime) -> str:
    """Format a datetime as EXIF `YYYY:MM:DD HH:MM:SS`."""
    return value.strftime("%Y:%m:%d %H:%M:%S")


def iter_exif_image_files(folder: Path, *, recursive: bool = True) -> list[Path]:
    """Return image paths under `folder` that support EXIF date tags."""
    if recursive:
        paths = [path for path in folder.rglob("*") if path.is_file()]
    else:
        paths = [path for path in folder.iterdir() if path.is_file()]
    return sorted(path for path in paths if path.suffix.lower() in EXIF_IMAGE_EXTENSIONS)


def set_exif_datetime(path: Path, value: datetime) -> ExifDatetimeResult:
    """Write DateTime, DateTimeOriginal, and DateTimeDigitized on `path`.

    Re-saves the image with Pillow. JPEG uses `quality='keep'` when possible
    to limit re-encode quality loss. Other EXIF tags already present are kept
    when Pillow preserves them on save.

    """
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


def set_exif_datetime_in_folder(
    folder: Path,
    value: datetime,
    *,
    recursive: bool = True,
) -> list[ExifDatetimeResult]:
    """Set EXIF date/time on all supported images under `folder`."""
    return [set_exif_datetime(path, value) for path in iter_exif_image_files(folder, recursive=recursive)]


def summarize_exif_datetime_results(results: list[ExifDatetimeResult]) -> str:
    """Build a short human-readable summary of batch EXIF updates."""
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
