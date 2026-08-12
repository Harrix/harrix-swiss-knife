"""Resolve Illustrator / vector source files for icon families."""

from __future__ import annotations

import re
from pathlib import Path

# Non-SVG vector masters (beautify-md places these under `files/`).
SOURCE_EXTENSIONS: tuple[str, ...] = (
    ".ai",
    ".eps",
    ".pdf",
    ".afdesign",
    ".sketch",
    ".cdr",
    ".wmf",
    ".emf",
)

_VARIANT_TOKEN_RE = re.compile(
    r"_(?:white|black|gray|grey|line-[a-z0-9]+)(?=(?:_\d+)?$)",
    re.IGNORECASE,
)


def candidate_source_stems(family_id: str, svg_path: Path | None = None) -> list[str]:
    """Return ordered stem candidates for looking up a source master file.

    Prefers the SVG stem, then the same stem without color/line tokens
    (e.g. `fiction__alien_white_02` → `fiction__alien_02`), then family ID.

    """
    stems: list[str] = []

    def add(stem: str) -> None:
        cleaned = stem.strip()
        if cleaned and cleaned not in stems:
            stems.append(cleaned)

    if svg_path is not None:
        stem = svg_path.stem
        if stem.casefold() != "featured-image":
            add(stem)
            add(_VARIANT_TOKEN_RE.sub("", stem))
    add(family_id)
    return stems


def find_icon_source_file(
    *,
    family_id: str,
    note_dir: Path,
    svg_path: Path | None = None,
    external_ai_root: Path | None = None,
) -> Path | None:
    """Find a vector source file for an icon family / selected SVG.

    Search order:

    1. Note `files/` (beautify-md destination for `.ai` / `.pdf` / …)
    2. Note root
    3. Note `img/`
    4. External AI repo (`path_vector_icons_ai`), including nested `src/`

    """
    stems = candidate_source_stems(family_id, svg_path)
    for directory in source_search_directories(note_dir, external_ai_root):
        found = _first_matching_source(directory, stems)
        if found is not None:
            return found
    return None


def resolve_external_ai_root(raw: str | Path | None) -> Path | None:
    """Normalize `path_vector_icons_ai` to an existing directory, or `None`."""
    if raw is None:
        return None
    text = str(raw).strip()
    if not text or text.startswith("<"):
        return None
    path = Path(text)
    return path if path.is_dir() else None


def source_search_directories(note_dir: Path, external_ai_root: Path | None = None) -> list[Path]:
    """Return existing directories to search for source masters."""
    dirs: list[Path] = []

    def add(path: Path) -> None:
        if path.is_dir() and path not in dirs:
            dirs.append(path)

    add(note_dir / "files")
    add(note_dir)
    add(note_dir / "img")

    if external_ai_root is not None:
        add(external_ai_root / "src")
        add(external_ai_root)
    return dirs


def _first_matching_source(directory: Path, stems: list[str]) -> Path | None:
    for stem in stems:
        for ext in SOURCE_EXTENSIONS:
            path = directory / f"{stem}{ext}"
            if path.is_file():
                return path
    # Case-insensitive fallback for Windows-ish layouts with odd casing.
    try:
        entries = {entry.name.casefold(): entry for entry in directory.iterdir() if entry.is_file()}
    except OSError:
        return None
    for stem in stems:
        for ext in SOURCE_EXTENSIONS:
            match = entries.get(f"{stem}{ext}".casefold())
            if match is not None:
                return match
    return None
