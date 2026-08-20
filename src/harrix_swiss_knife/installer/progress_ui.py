"""Progress-bar mode helpers for the installer wizard (no Qt dependency)."""

from __future__ import annotations

from enum import Enum, auto


class ProgressBarMode(Enum):
    """How the install progress bar should look."""

    INDETERMINATE = auto()
    DETERMINATE = auto()
    COMPLETE = auto()


def progress_mode_for_log_line(line: str, *, extracting: bool) -> ProgressBarMode | None:
    """Return a progress mode change for a log line, or `None` to leave the bar alone.

    Payload extract keeps a determinate byte/file progress. Any later `==>` step
    switches to an indeterminate busy bar so a finished extract does not leave 100%.

    """
    text = line.strip()
    if not text:
        return None
    if text.startswith("==> "):
        if "extract" in text.lower():
            return ProgressBarMode.DETERMINATE
        return ProgressBarMode.INDETERMINATE
    if extracting:
        return None
    return None
