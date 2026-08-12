"""Variant display modes for the Vector Icons main grid."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from harrix_swiss_knife.apps.icons.catalog import IconFamily, IconVariant

MODE_FEATURED = "featured"
MODE_COLOR = "color"
MODE_WHITE = "white"
MODE_BLACK = "black"
MODE_GRAY = "gray"
MODE_LINE_8 = "line-8"
MODE_LINE_16 = "line-16"
MODE_LINE_32 = "line-32"
MODE_ALL = "all"

# Combobox value → label (order is UI order).
VARIANT_VIEW_MODES: tuple[tuple[str, str], ...] = (
    (MODE_FEATURED, "Featured (default)"),
    (MODE_COLOR, "Color (all ordinary versions)"),
    (MODE_WHITE, "White"),
    (MODE_BLACK, "Black"),
    (MODE_GRAY, "Gray"),
    (MODE_LINE_8, "Line 8"),
    (MODE_LINE_16, "Line 16"),
    (MODE_LINE_32, "Line 32"),
    (MODE_ALL, "All variants"),
)

_LINE_RE = re.compile(r"_line-(\d+)-?(?:_|$)", re.IGNORECASE)
_COLOR_TOKEN_RE = re.compile(r"(?:^|_)(white|black|gray|grey)(?:_|$)", re.IGNORECASE)


@dataclass(frozen=True, slots=True)
class GridEntry:
    """One tile in the main icon grid."""

    family: IconFamily
    svg_path: Path
    is_fallback: bool = False


def build_grid_entries(
    families: list[IconFamily],
    *,
    repo_root: Path,
    mode: str,
) -> list[GridEntry]:
    """Build main-grid tiles for the selected variant view mode.

    Kind modes (`white`, `black`, …) list matching variants first; families
    without that kind append their featured/ordinary tile at the end.

    """
    known = {key for key, _ in VARIANT_VIEW_MODES}
    normalized = mode if mode in known else MODE_FEATURED

    if normalized == MODE_FEATURED:
        entries: list[GridEntry] = []
        for family in families:
            featured = _featured_entry(family, repo_root)
            if featured is not None:
                entries.append(featured)
        return entries

    if normalized == MODE_ALL:
        entries = []
        for family in families:
            if family.variants:
                entries.extend(_variant_entries(family, repo_root, variants=family.variants))
            else:
                featured = _featured_entry(family, repo_root)
                if featured is not None:
                    entries.append(featured)
        return entries

    if normalized == MODE_COLOR:
        matched: list[GridEntry] = []
        fallback: list[GridEntry] = []
        for family in families:
            color_variants = [item for item in family.variants if classify_variant_kind(item.name) == MODE_COLOR]
            if color_variants:
                matched.extend(_variant_entries(family, repo_root, variants=color_variants))
            else:
                featured = _featured_entry(family, repo_root, is_fallback=True)
                if featured is not None:
                    fallback.append(featured)
        return matched + fallback

    # Specific kind: white / black / gray / line-*
    matched = []
    fallback = []
    for family in families:
        kind_variants = [item for item in family.variants if classify_variant_kind(item.name) == normalized]
        if kind_variants:
            matched.extend(_variant_entries(family, repo_root, variants=kind_variants))
        else:
            featured = _featured_entry(family, repo_root, is_fallback=True)
            if featured is not None:
                fallback.append(featured)
    return matched + fallback


def classify_variant_kind(stem: str) -> str:
    """Return kind token for an SVG stem (`color`, `white`, `line-16`, …)."""
    text = stem.casefold()
    line_match = _LINE_RE.search(text)
    if line_match is not None:
        return f"line-{line_match.group(1)}"
    color_match = _COLOR_TOKEN_RE.search(text)
    if color_match is not None:
        color_kind = color_match.group(1).casefold()
        return "gray" if color_kind == "grey" else color_kind
    return MODE_COLOR


def _featured_entry(family: IconFamily, repo_root: Path, *, is_fallback: bool = False) -> GridEntry | None:
    path = family.featured_path(repo_root)
    if path is None and family.variants:
        path = family.variants[0].absolute_path(repo_root, family.folder)
    if path is None:
        return None
    return GridEntry(family=family, svg_path=path, is_fallback=is_fallback)


def _variant_entries(
    family: IconFamily,
    repo_root: Path,
    *,
    variants: list[IconVariant],
) -> list[GridEntry]:
    return [
        GridEntry(family=family, svg_path=variant.absolute_path(repo_root, family.folder), is_fallback=False)
        for variant in variants
    ]
