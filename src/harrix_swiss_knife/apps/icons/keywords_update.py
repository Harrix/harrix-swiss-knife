"""Update icon keywords in the Markdown note and `catalog.json`."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from harrix_pylib.funcs_md import parse_keywords_text, replace_frontmatter_list

if TYPE_CHECKING:
    from pathlib import Path


def update_keywords_files(
    *,
    md_path: Path,
    catalog_path: Path,
    family_id: str,
    tags: list[str],
) -> None:
    """Write tags into the note frontmatter and the matching catalog entry."""
    text = md_path.read_text(encoding="utf-8")
    new_markdown = replace_frontmatter_list(text, "tags", tags)

    catalog_text: str | None = None
    new_catalog_text: str | None = None
    if catalog_path.is_file():
        catalog_text = catalog_path.read_text(encoding="utf-8")
        raw = json.loads(catalog_text)
        icons = raw.get("icons") if isinstance(raw, dict) else None
        if not isinstance(icons, list):
            msg = f"Invalid icons list in {catalog_path}"
            raise ValueError(msg)
        matching = [item for item in icons if isinstance(item, dict) and item.get("id") == family_id]
        if not matching:
            msg = f"Icon {family_id!r} not found in {catalog_path}"
            raise ValueError(msg)
        matching[0]["tags"] = list(tags)
        new_catalog_text = json.dumps(raw, ensure_ascii=False, indent=2) + "\n"

    old_markdown = text
    try:
        md_path.write_text(new_markdown, encoding="utf-8")
        if new_catalog_text is not None:
            catalog_path.write_text(new_catalog_text, encoding="utf-8")
    except OSError:
        md_path.write_text(old_markdown, encoding="utf-8")
        if catalog_text is not None:
            catalog_path.write_text(catalog_text, encoding="utf-8")
        raise


__all__ = ["parse_keywords_text", "replace_frontmatter_list", "update_keywords_files"]
