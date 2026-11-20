"""Persist post-`uv` upgrade restore intent in `config-temp.json`."""

from __future__ import annotations

from typing import Any, TypedDict

import harrix_pylib as h

from harrix_swiss_knife.paths import get_config_path_str

_RESUME_KEY = "uv_upgrade_resume"
_UPGRADE_STEP_CLASS = "OnUpgradeUvPackages"


class UvUpgradeResume(TypedDict):
    """What to restore after the detached uv upgrade relaunches HSK."""

    reopen_maintenance_checklist: bool
    maintenance_session_done: list[str]


def clear_uv_upgrade_resume() -> None:
    """Remove a leftover resume payload without applying it."""
    try:
        loaded: dict[str, Any] = h.dev.config_load(get_config_path_str(), is_temp=True)
    except Exception:
        return
    if _RESUME_KEY not in loaded:
        return
    loaded.pop(_RESUME_KEY, None)
    h.dev.config_save(loaded, get_config_path_str(), is_temp=True)


def normalize_uv_upgrade_resume(raw: object) -> UvUpgradeResume | None:
    """Return a typed resume payload, or `None` when `raw` is invalid."""
    if not isinstance(raw, dict):
        return None
    reopen = bool(raw.get("reopen_maintenance_checklist"))
    done_raw = raw.get("maintenance_session_done")
    done: list[str] = []
    if isinstance(done_raw, list):
        done = [str(item) for item in done_raw if isinstance(item, str) and item.strip()]
    if reopen and _UPGRADE_STEP_CLASS not in done:
        done.append(_UPGRADE_STEP_CLASS)
    return {
        "reopen_maintenance_checklist": reopen,
        "maintenance_session_done": done,
    }


def pop_uv_upgrade_resume() -> UvUpgradeResume | None:
    """Load and clear the pending resume payload, or `None` when absent."""
    try:
        loaded: dict[str, Any] = h.dev.config_load(get_config_path_str(), is_temp=True)
    except Exception:
        return None
    raw = loaded.pop(_RESUME_KEY, None)
    if raw is None:
        return None
    try:
        h.dev.config_save(loaded, get_config_path_str(), is_temp=True)
    except Exception:
        return None
    return normalize_uv_upgrade_resume(raw)


def save_uv_upgrade_resume(
    *,
    reopen_maintenance_checklist: bool,
    maintenance_session_done: list[str] | None = None,
) -> None:
    """Store resume intent for the next HSK process after uv upgrade."""
    done = list(maintenance_session_done or [])
    if reopen_maintenance_checklist and _UPGRADE_STEP_CLASS not in done:
        done.append(_UPGRADE_STEP_CLASS)
    payload: UvUpgradeResume = {
        "reopen_maintenance_checklist": reopen_maintenance_checklist,
        "maintenance_session_done": done,
    }
    h.dev.config_update_value(_RESUME_KEY, payload, get_config_path_str(), is_temp=True)
