"""Allocate dated filenames for screenshots in `temp/images`."""

from __future__ import annotations

import re
from datetime import UTC, datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import date
    from pathlib import Path

_DATED_STEM = re.compile(r"^(\d{4}-\d{2}-\d{2})_(\d+)$")


def images_folder(project_root: Path) -> Path:
    """Return the OnOpenImages folder (`temp/images`) under `project_root`."""
    return project_root / "temp" / "images"


def next_dated_image_path(
    folder: Path,
    *,
    today: date | None = None,
    extension: str = ".png",
) -> Path:
    """Return the next free `YYYY-MM-DD_NN` path in `folder`.

    Existing files with the same date stem (any extension) reserve their index
    numbers so saves never overwrite.

    Args:

    - `folder` (`Path`): Destination directory (created if missing).
    - `today` (`date | None`): Calendar day for the stem; defaults to local today.
    - `extension` (`str`): File suffix including the leading dot. Defaults to `.png`.

    Returns:

    - `Path`: Absolute path such as `…/2026-08-29_01.png`.

    """
    folder.mkdir(parents=True, exist_ok=True)
    day = (today or datetime.now(UTC).astimezone().date()).isoformat()
    used: set[int] = set()
    for path in folder.iterdir():
        if not path.is_file():
            continue
        match = _DATED_STEM.match(path.stem)
        if match is None or match.group(1) != day:
            continue
        used.add(int(match.group(2)))
    index = 1
    while index in used:
        index += 1
    suffix = extension if extension.startswith(".") else f".{extension}"
    return (folder / f"{day}_{index:02d}{suffix}").resolve()
