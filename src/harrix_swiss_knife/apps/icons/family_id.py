"""Derive icon family ID and note paths from SVG filename stems."""

from __future__ import annotations

import re
from pathlib import Path

_STRIP_SUFFIXES = (
    re.compile(r"_\d{2}$"),
    re.compile(r"_line-(?:8|16|32)$"),
    re.compile(r"_improbable$"),
    re.compile(r"_(?:black|gray|white)$"),
)


def category_from_family_id(family_id: str) -> str:
    """Return category prefix before `__` in a family ID."""
    if "__" not in family_id:
        return family_id
    return family_id.split("__", 1)[0]


def family_id_from_stem(stem: str) -> str:
    """Return family ID by stripping variant suffixes from a filename stem.

    Removes trailing design index (`_01`), stroke weight (`_line-8`),
    `improbable`, and mono color tokens until none remain.

    Args:

    - `stem` (`str`): Filename without extension, e.g. `building__house_black_01`.

    Returns:

    - `str`: Family ID such as `building__house`.

    """
    name = stem
    while True:
        changed = False
        for pattern in _STRIP_SUFFIXES:
            new_name = pattern.sub("", name)
            if new_name != name:
                name = new_name
                changed = True
                break
        if not changed:
            break
    return name


def note_dir_for_family_id(icons_dir: Path, family_id: str) -> Path:
    """Return `icons/{category}/{family_id}` for a family ID."""
    return Path(icons_dir) / category_from_family_id(family_id) / family_id


def tags_from_family_id(family_id: str) -> list[str]:
    """Bootstrap search tags from category and slug tokens."""
    category = category_from_family_id(family_id)
    slug = family_id.split("__", 1)[-1]
    tags: list[str] = []
    seen: set[str] = set()
    for token in (*category.split("_"), *slug.replace("-", " ").split()):
        cleaned = token.strip().lower()
        if not cleaned or cleaned in seen:
            continue
        seen.add(cleaned)
        tags.append(cleaned)
    return tags


def title_from_family_id(family_id: str) -> str:
    """Build a human title from the slug after `__`."""
    slug = family_id.split("__", 1)[-1]
    return slug.replace("-", " ").replace("_", " ").title()
