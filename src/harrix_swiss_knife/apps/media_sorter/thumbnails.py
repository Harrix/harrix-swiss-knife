"""Thumbnail loading for images and videos (ffmpeg for video frames)."""

from __future__ import annotations

import hashlib
import logging
import subprocess
from pathlib import Path

import harrix_pylib as h
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

from harrix_swiss_knife.apps.common.audio_compress import ffmpeg_exe_path, is_ffmpeg_available
from harrix_swiss_knife.apps.common.avif_manager import load_image_pixmap
from harrix_swiss_knife.apps.media_sorter.media_scan import is_video_path

logger = logging.getLogger(__name__)

_DEFAULT_THUMB = 160


def load_media_thumbnail(path: str | Path, size: int = _DEFAULT_THUMB) -> QPixmap | None:
    """Load a scaled thumbnail for an image or video path."""
    file_path = Path(path)
    if not file_path.is_file():
        return None
    pixmap = _load_video_thumbnail(file_path) if is_video_path(file_path) else load_image_pixmap(str(file_path))
    if pixmap is None or pixmap.isNull():
        return None
    return pixmap.scaled(
        size,
        size,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )


def media_thumb_cache_dir() -> Path:
    """Return cache directory for extracted video thumbnails."""
    cache = h.dev.get_project_root() / "temp" / "media_sorter_thumbs"
    cache.mkdir(parents=True, exist_ok=True)
    return cache


def _extract_video_frame(video_path: Path, output_path: Path, project_root: Path) -> bool:
    ffmpeg = ffmpeg_exe_path(project_root)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    args = [
        str(ffmpeg),
        "-y",
        "-ss",
        "0.5",
        "-i",
        str(video_path),
        "-frames:v",
        "1",
        "-q:v",
        "4",
        str(output_path),
    ]
    try:
        completed = subprocess.run(
            args,
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        logger.warning("ffmpeg thumbnail failed for %s: %s", video_path, exc)
        return False
    if completed.returncode != 0 or not output_path.is_file():
        logger.warning(
            "ffmpeg thumbnail exit %s for %s: %s",
            completed.returncode,
            video_path,
            (completed.stderr or "")[:300],
        )
        return False
    return True


def _load_video_thumbnail(video_path: Path) -> QPixmap | None:
    project_root = h.dev.get_project_root()
    if not is_ffmpeg_available(project_root):
        return None
    cache_path = _video_cache_path(video_path)
    if not cache_path.is_file() and not _extract_video_frame(video_path, cache_path, project_root):
        return None
    pixmap = QPixmap(str(cache_path))
    if pixmap.isNull():
        return None
    return pixmap


def _video_cache_path(video_path: Path) -> Path:
    try:
        mtime_ns = video_path.stat().st_mtime_ns
    except OSError:
        mtime_ns = 0
    digest = hashlib.sha1(f"{video_path.resolve()}|{mtime_ns}".encode()).hexdigest()  # noqa: S324
    return media_thumb_cache_dir() / f"{digest}.jpg"
