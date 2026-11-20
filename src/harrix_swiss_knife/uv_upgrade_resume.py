"""Persist post-`uv` upgrade restore intent in `config-temp.json`."""

from __future__ import annotations

from pathlib import Path  # noqa: TC003
from typing import Any, TypedDict

import harrix_pylib as h

from harrix_swiss_knife.paths import get_config_path_str, get_project_root

_RESUME_KEY = "uv_upgrade_resume"
_UPGRADE_STEP_CLASS = "OnUpgradeUvPackages"
# Watched by `.vscode/tasks.json` (`runOn: folderOpen`) to start HSK in Cursor's terminal.
CURSOR_TERMINAL_RESUME_FLAG_NAME = "hsk-resume-after-uv-upgrade.flag"


class UvUpgradeResume(TypedDict):
    """What to restore after the detached uv upgrade relaunches HSK."""

    reopen_maintenance_checklist: bool
    maintenance_session_done: list[str]


def clear_cursor_terminal_resume_flag(project_root: Path | None = None) -> None:
    """Remove the folderOpen flag that starts HSK inside Cursor's terminal."""
    path = cursor_terminal_resume_flag_path(project_root)
    path.unlink(missing_ok=True)


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


def cursor_terminal_resume_flag_path(project_root: Path | None = None) -> Path:
    """Return `temp/hsk-resume-after-uv-upgrade.flag` under the project root."""
    root = project_root if project_root is not None else get_project_root()
    return root.resolve() / "temp" / CURSOR_TERMINAL_RESUME_FLAG_NAME


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


def write_cursor_terminal_resume_flag(project_root: Path | None = None) -> Path:
    """Create the flag that makes Cursor's folderOpen task start HSK in a terminal."""
    path = cursor_terminal_resume_flag_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("1\n", encoding="utf-8")
    return path
