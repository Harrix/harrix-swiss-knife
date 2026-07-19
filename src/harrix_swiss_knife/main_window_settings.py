"""Main window view mode settings from config-temp.json."""

from __future__ import annotations

import harrix_pylib as h

from harrix_swiss_knife.paths import get_config_path_str, get_temp_config_path

MAIN_WINDOW_ICON_GRID_KEY = "main_window_icon_grid"


def load_main_window_icon_grid() -> bool:
    """Return whether the tray window uses icon grid view. Defaults to `True`."""
    try:
        config = h.dev.config_load(get_config_path_str(), is_temp=True)
    except (FileNotFoundError, OSError, ValueError):
        return True
    value = config.get(MAIN_WINDOW_ICON_GRID_KEY, True)
    if isinstance(value, bool):
        return value
    return bool(value)


def save_main_window_icon_grid(*, icon_grid: bool) -> None:
    """Persist tray window view mode in `config-temp.json`."""
    temp_config_path = get_temp_config_path()
    temp_config_path.parent.mkdir(parents=True, exist_ok=True)
    if not temp_config_path.exists() or temp_config_path.stat().st_size == 0:
        temp_config_path.write_text("{}", encoding="utf-8")
    h.dev.config_update_value(
        MAIN_WINDOW_ICON_GRID_KEY,
        icon_grid,
        get_config_path_str(),
        is_temp=True,
    )
