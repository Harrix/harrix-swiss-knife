"""Persist quick launcher global hotkey in config-temp.json (user-specific, no snippets)."""

from __future__ import annotations

import harrix_pylib as h

from harrix_swiss_knife.paths import get_config_path_str, get_temp_config_path

QUICK_LAUNCHER_HOTKEY_KEY = "quick_launcher_hotkey"


def load_quick_launcher_hotkey() -> str:
    """Return the saved hotkey string, or empty if unset or config-temp is missing."""
    try:
        temp_config = h.dev.config_load(get_config_path_str(), is_temp=True)
    except (FileNotFoundError, OSError, ValueError):
        return ""
    return str(temp_config.get(QUICK_LAUNCHER_HOTKEY_KEY) or "").strip()


def save_quick_launcher_hotkey(hotkey: str) -> None:
    """Save hotkey to ``config-temp.json`` without touching the main config file."""
    temp_config_path = get_temp_config_path()
    temp_config_path.parent.mkdir(parents=True, exist_ok=True)
    if not temp_config_path.exists() or temp_config_path.stat().st_size == 0:
        temp_config_path.write_text("{}", encoding="utf-8")
    h.dev.config_update_value(
        QUICK_LAUNCHER_HOTKEY_KEY,
        hotkey.strip(),
        get_config_path_str(),
        is_temp=True,
    )
