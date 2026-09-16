"""User preference for Food day-macros text language (`config-temp.json`)."""

from __future__ import annotations

from typing import Any, Literal

import harrix_pylib as h

from harrix_swiss_knife.paths import get_config_path_str

MacrosTextLanguage = Literal["local", "en"]

_CONFIG_KEY = "food_day_macros_preferred_text"
_DEFAULT: MacrosTextLanguage = "local"


def load_macros_preferred_text_language() -> MacrosTextLanguage:
    """Return preferred macros text tab (`local` or `en`; default `local`)."""
    try:
        loaded: dict[str, Any] = h.dev.config_load(get_config_path_str(), is_temp=True)
    except Exception:
        return _DEFAULT
    raw = loaded.get(_CONFIG_KEY, _DEFAULT)
    if isinstance(raw, str) and raw.strip().casefold() in {"en", "english"}:
        return "en"
    return "local"


def save_macros_preferred_text_language(value: MacrosTextLanguage) -> None:
    """Persist preferred macros text tab into `config-temp.json`."""
    h.dev.config_update_value(_CONFIG_KEY, value, get_config_path_str(), is_temp=True)
