"""Config keys and helpers for desktop Photo Sync auto-listen."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

CONFIG_AUTO_LISTEN = "photo_sync_auto_listen"
CONFIG_TOKEN = "photo_sync_token"  # noqa: S105
CONFIG_CONFIRM_CODE = "photo_sync_confirm_code"
CONFIG_FOLDER = "path_photos"


def is_auto_listen_enabled(config: dict[str, Any]) -> bool:
    """Return whether Photo Sync should keep listening in the background."""
    return bool(config.get(CONFIG_AUTO_LISTEN))


def load_saved_credentials(config: dict[str, Any]) -> tuple[str, str] | None:
    """Return `(token, confirm_code)` when both are non-empty in config."""
    token = str(config.get(CONFIG_TOKEN) or "").strip()
    confirm_code = str(config.get(CONFIG_CONFIRM_CODE) or "").strip()
    if not token or not confirm_code:
        return None
    return token, confirm_code


def persist_credentials(config_path: Path | str, *, token: str, confirm_code: str) -> None:
    """Save pairing credentials so auto-listen can reuse them after restart."""
    write_config_values(
        config_path,
        {
            CONFIG_TOKEN: token.strip(),
            CONFIG_CONFIRM_CODE: confirm_code.strip(),
        },
    )


def photos_dir_from_config(config: dict[str, Any]) -> Path | None:
    """Return a usable photos folder from config, or `None`."""
    raw = str(config.get(CONFIG_FOLDER) or "").strip()
    if not raw:
        return None
    path = Path(raw).expanduser()
    try:
        path = path.resolve()
    except OSError:
        return None
    if not path.is_dir():
        return None
    return path


def write_config_values(config_path: Path | str, updates: dict[str, Any]) -> None:
    """Merge `updates` into the JSON config file and write it back."""
    path = Path(config_path)
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        data = {}
    data.update(updates)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
