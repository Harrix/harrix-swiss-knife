"""Load annotation color palette (Quick paste colors when available)."""

from __future__ import annotations

from pathlib import Path

import harrix_pylib as h

from harrix_swiss_knife.apps.snippets.constants import ZONE_COLOR
from harrix_swiss_knife.apps.snippets.seed import SEED_COLORS
from harrix_swiss_knife.paths import get_config_path_str


def load_annotation_colors() -> list[tuple[str, str]]:
    """Return `(hex, hint)` colors from Quick paste DB, else the seed list."""
    try:
        config = h.dev.config_load(get_config_path_str())
    except (OSError, TypeError, ValueError):
        return list(SEED_COLORS)
    raw = str(config.get("sqlite_snippets") or "").strip()
    if not raw:
        return list(SEED_COLORS)
    db_path = Path(raw)
    if not db_path.is_file():
        return list(SEED_COLORS)
    try:
        from harrix_swiss_knife.apps.snippets.database_manager import DatabaseManager  # noqa: PLC0415

        manager = DatabaseManager(str(db_path))
        items = manager.list_items(ZONE_COLOR)
        manager.close()
    except (OSError, RuntimeError, ValueError):
        return list(SEED_COLORS)
    colors = [(item.value.strip(), (item.hint or "").strip()) for item in items if item.value.strip()]
    return colors or list(SEED_COLORS)
