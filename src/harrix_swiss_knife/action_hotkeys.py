"""Load global action hotkey bindings from `config.json`."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import harrix_pylib as h

from harrix_swiss_knife.paths import get_config_path_str

HOTKEYS_KEY = "hotkeys"


@dataclass(frozen=True)
class ActionHotkeyBinding:
    """One global hotkey bound to an action class name (e.g. `OnQuickLauncher`)."""

    action: str
    hotkey: str


def load_action_hotkeys(config: dict[str, Any] | None = None) -> list[ActionHotkeyBinding]:
    """Return hotkey bindings from `config.json` (or from the given config dict).

    Expected shape::

        `hotkeys`: [
          {`action`: `OnQuickLauncher`, `hotkeys`: ["Ctrl+Shift+F1"]},
          {`action`: `OnScreenshotRegion`, `hotkeys`: ["Ctrl+Shift+F2"]}
        ]

    Each entry may use `"hotkeys"` (list of strings) or a single `"hotkey"` string.

    """
    data = config if config is not None else _load_main_config()
    raw = data.get(HOTKEYS_KEY)
    if not isinstance(raw, list):
        return []

    bindings: list[ActionHotkeyBinding] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        action = str(item.get("action") or "").strip()
        if not action:
            continue
        for hotkey in _hotkeys_from_entry(item):
            bindings.append(ActionHotkeyBinding(action=action, hotkey=hotkey))
    return bindings


def load_hotkeys_for_action(action_name: str, config: dict[str, Any] | None = None) -> list[str]:
    """Return hotkey strings bound to `action_name`, in config order."""
    name = action_name.strip()
    return [binding.hotkey for binding in load_action_hotkeys(config) if binding.action == name]


def _hotkeys_from_entry(item: dict[str, Any]) -> list[str]:
    raw_list = item.get("hotkeys")
    if isinstance(raw_list, list):
        return [text for value in raw_list if (text := str(value).strip())]

    single = item.get("hotkey")
    if single is None:
        return []
    text = str(single).strip()
    return [text] if text else []


def _load_main_config() -> dict[str, Any]:
    try:
        loaded = h.dev.config_load(get_config_path_str())
    except (FileNotFoundError, OSError, ValueError):
        return {}
    return loaded if isinstance(loaded, dict) else {}
