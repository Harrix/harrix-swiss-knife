"""Quick launcher settings from `config.json`."""

from __future__ import annotations

import harrix_pylib as h

from harrix_swiss_knife.paths import get_config_path_str

QUICK_LAUNCHER_MARKDOWN_IN_PANEL_KEY = "quick_launcher_markdown_in_panel"


def load_quick_launcher_markdown_in_panel() -> bool:
    """Return whether Markdown commands appear in a separate quick launcher panel."""
    try:
        config = h.dev.config_load(get_config_path_str())
    except (FileNotFoundError, OSError, ValueError):
        return True
    value = config.get(QUICK_LAUNCHER_MARKDOWN_IN_PANEL_KEY, True)
    if isinstance(value, bool):
        return value
    return bool(value)
