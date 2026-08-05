"""Scan folders for image and video files used by Media Sorter."""

from __future__ import annotations

from pathlib import Path

IMAGE_EXTENSIONS = frozenset(
    {
        ".avif",
        ".bmp",
        ".gif",
        ".heic",
        ".heif",
        ".jpeg",
        ".jpg",
        ".png",
        ".tif",
        ".tiff",
        ".webp",
    },
)

VIDEO_EXTENSIONS = frozenset(
    {
        ".avi",
        ".m4v",
        ".mkv",
        ".mov",
        ".mp4",
        ".mpeg",
        ".mpg",
        ".webm",
        ".wmv",
    },
)

MEDIA_EXTENSIONS = IMAGE_EXTENSIONS | VIDEO_EXTENSIONS


def is_image_path(path: str | Path) -> bool:
    """Return whether `path` looks like an image file."""
    return Path(path).suffix.lower() in IMAGE_EXTENSIONS


def is_media_path(path: str | Path) -> bool:
    """Return whether `path` looks like a supported image or video."""
    return Path(path).suffix.lower() in MEDIA_EXTENSIONS


def is_video_path(path: str | Path) -> bool:
    """Return whether `path` looks like a video file."""
    return Path(path).suffix.lower() in VIDEO_EXTENSIONS


def iter_media_files(root: str | Path) -> list[Path]:
    """Return sorted media files under `root` (recursive), skipping missing roots."""
    root_path = Path(root).expanduser()
    if not root_path.is_dir():
        return []
    found: list[Path] = []
    for path in root_path.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in MEDIA_EXTENSIONS:
            continue
        # Skip thumbnail cache folders if present under the tree
        if any(part.startswith(".") for part in path.parts):
            continue
        found.append(path)
    found.sort(key=lambda p: str(p).lower())
    return found


def list_immediate_subdirs(folder: str | Path) -> list[Path]:
    """Return sorted immediate child directories of `folder`."""
    folder_path = Path(folder).expanduser()
    if not folder_path.is_dir():
        return []
    dirs = [p for p in folder_path.iterdir() if p.is_dir() and not p.name.startswith(".")]
    dirs.sort(key=lambda p: p.name.lower())
    return dirs


def list_media_in_folder(folder: str | Path, *, recursive: bool = False) -> list[Path]:
    """Return media files in `folder` (optionally recursive)."""
    folder_path = Path(folder).expanduser()
    if not folder_path.is_dir():
        return []
    if recursive:
        return iter_media_files(folder_path)
    files = [
        p
        for p in folder_path.iterdir()
        if p.is_file() and p.suffix.lower() in MEDIA_EXTENSIONS and not p.name.startswith(".")
    ]
    files.sort(key=lambda p: p.name.lower())
    return files
