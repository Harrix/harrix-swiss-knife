"""Persist and load per-action invocation counts (GUI and CLI)."""

from __future__ import annotations

import json
import logging
import threading
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, TypedDict

from harrix_swiss_knife.paths import get_action_usage_path

if TYPE_CHECKING:
    from pathlib import Path

logger = logging.getLogger(__name__)

_lock = threading.Lock()

RECENT_GUI_ACTIONS_LIMIT = 6
RECENT_GUI_EXCLUDED_CLASS_NAMES = frozenset({"OnExit"})


class ActionUsageEntry(TypedDict):
    """Usage counters for one action class."""

    count: int
    gui: int
    cli: int
    last_used: str
    last_used_gui: str


def list_recent_gui_action_names(
    *,
    limit: int = RECENT_GUI_ACTIONS_LIMIT,
    path: Path | None = None,
    excluded: frozenset[str] | None = None,
) -> list[str]:
    """Return class names of the most recently used GUI actions, newest first.

    CLI invocations are ignored. Entries without a GUI timestamp are skipped,
    except historical GUI-only records that only have `last_used`.
    Class names in `excluded` (Exit by default) are omitted before the limit.

    """
    if limit <= 0:
        return []
    skip = RECENT_GUI_EXCLUDED_CLASS_NAMES if excluded is None else excluded
    ranked: list[tuple[datetime, str]] = []
    for class_name, entry in load_action_usage(path).items():
        if class_name in skip:
            continue
        stamp = _effective_last_used_gui(entry)
        if not stamp:
            continue
        ranked.append((_parse_usage_timestamp(stamp), class_name))
    ranked.sort(key=lambda item: (item[0], item[1]), reverse=True)
    return [name for _, name in ranked[:limit]]


def load_action_usage(path: Path | None = None) -> ActionUsageMap:
    """Load usage map from JSON; return empty dict if missing or invalid."""
    usage_path = path if path is not None else get_action_usage_path()
    if not usage_path.is_file():
        return {}
    try:
        raw = json.loads(usage_path.read_text(encoding="utf8"))
    except (OSError, json.JSONDecodeError):
        logger.exception("Failed to load action usage from %s", usage_path)
        return {}
    if not isinstance(raw, dict):
        return {}
    result: ActionUsageMap = {}
    for key, value in raw.items():
        if not isinstance(key, str) or not isinstance(value, dict):
            continue
        entry = _normalize_entry(value)
        if entry is not None:
            result[key] = entry
    return result


def record_action_usage(class_name: str, *, via_cli: bool, path: Path | None = None) -> None:
    """Increment counters for `class_name` and persist atomically.

    Errors are logged and swallowed so statistics never break actions.

    """
    if not class_name:
        return
    usage_path = path if path is not None else get_action_usage_path()
    try:
        with _lock:
            data = load_action_usage(usage_path)
            entry = data.get(class_name) or ActionUsageEntry(
                count=0,
                gui=0,
                cli=0,
                last_used="",
                last_used_gui="",
            )
            entry["count"] = int(entry["count"]) + 1
            if via_cli:
                entry["cli"] = int(entry["cli"]) + 1
            else:
                entry["gui"] = int(entry["gui"]) + 1
            now = datetime.now(UTC).astimezone().isoformat(timespec="seconds")
            entry["last_used"] = now
            if not via_cli:
                entry["last_used_gui"] = now
            data[class_name] = entry
            _write_atomic(usage_path, data)
    except Exception:
        logger.exception("Failed to record action usage for %s", class_name)


def _effective_last_used_gui(entry: ActionUsageEntry) -> str:
    """Return the GUI recency stamp, with a fallback for older usage files."""
    if entry["last_used_gui"]:
        return entry["last_used_gui"]
    if entry["gui"] > 0 and entry["cli"] == 0:
        return entry["last_used"]
    return ""


def _normalize_entry(value: dict[str, Any]) -> ActionUsageEntry | None:
    """Return a typed entry from a raw dict, or `None` if unusable."""
    try:
        count = int(value.get("count", 0))
        gui = int(value.get("gui", 0))
        cli = int(value.get("cli", 0))
        last_used = value.get("last_used", "")
        if not isinstance(last_used, str):
            last_used = ""
        last_used_gui = value.get("last_used_gui", "")
        if not isinstance(last_used_gui, str):
            last_used_gui = ""
    except (TypeError, ValueError):
        return None
    return ActionUsageEntry(
        count=max(count, 0),
        gui=max(gui, 0),
        cli=max(cli, 0),
        last_used=last_used,
        last_used_gui=last_used_gui,
    )


def _parse_usage_timestamp(value: str) -> datetime:
    """Parse an ISO usage stamp; invalid values sort as oldest."""
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return datetime.min.replace(tzinfo=UTC)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed


def _write_atomic(path: Path, data: ActionUsageMap) -> None:
    """Write JSON via a sibling temp file then replace."""
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(payload, encoding="utf8")
    tmp_path.replace(path)


ActionUsageMap = dict[str, ActionUsageEntry]
