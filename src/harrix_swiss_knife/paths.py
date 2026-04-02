"""Project path helpers (CWD-independent).

The application frequently needs paths relative to the repository root (e.g. config files).
These helpers centralize path construction to avoid repeating string literals like
`config/config.json` and to make behavior independent of the current working directory.
"""

from __future__ import annotations

from pathlib import Path

import harrix_pylib as h


def get_config_path() -> Path:
    """Return absolute path to main config file."""

    return get_project_root() / "config" / "config.json"


def get_config_path_str() -> str:
    """Return config path as a string (for APIs expecting str)."""

    return str(get_config_path())


def get_project_root() -> Path:
    """Return project root directory as detected by harrix_pylib."""

    return h.dev.get_project_root()


def get_temp_config_path() -> Path:
    """Return absolute path to temp config file."""

    return get_project_root() / "config" / "config-temp.json"


def get_temp_config_path_str() -> str:
    """Return temp config path as a string (for APIs expecting str)."""

    return str(get_temp_config_path())
