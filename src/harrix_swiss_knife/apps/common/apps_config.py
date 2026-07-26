"""Shared config helpers for desktop apps."""

from __future__ import annotations

from typing import Any

DEFAULT_INITIAL_COUNT = 1000
DEFAULT_LOAD_MORE_COUNT = 500


def get_apps_list_limits(config: dict[str, Any]) -> tuple[int, int]:
    """Return `(initial_count, load_more_count)` from the shared `apps` config block.

    Used for table first-page size, scroll load-more size, and similar limits
    (autocomplete sample size, frequency window) that share the same defaults.

    """
    apps = config.get("apps") or {}
    return (
        int(apps.get("initial_count", DEFAULT_INITIAL_COUNT)),
        int(apps.get("load_more_count", DEFAULT_LOAD_MORE_COUNT)),
    )
