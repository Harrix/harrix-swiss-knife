"""Helpers for Qt UI sound playback."""

from __future__ import annotations

import os

_MUTE_ENV = "HSK_MUTE_SOUNDS"


def qt_sounds_muted() -> bool:
    """Return whether UI sounds should stay silent (pytest and check runners)."""
    flag = os.environ.get(_MUTE_ENV, "").strip().lower()
    if flag in {"1", "true", "yes"}:
        return True
    return bool(os.environ.get("PYTEST_CURRENT_TEST"))
