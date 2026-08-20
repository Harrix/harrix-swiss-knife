"""Logging helpers for the installer."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

LogFn = Callable[[str], None]


@dataclass
class OutcomeLog:
    """Collect install/skip/already/failed messages like the PowerShell installer."""

    installed: list[str] = field(default_factory=list)
    already: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    failed: list[str] = field(default_factory=list)
    _log: LogFn | None = None
    _file: Path | None = None

    def add(self, category: str, message: str) -> None:
        """Record a categorized outcome and emit a log line."""
        bucket = {
            "installed": self.installed,
            "already": self.already,
            "skipped": self.skipped,
            "failed": self.failed,
        }.get(category)
        if bucket is not None:
            bucket.append(message)
        prefix = {"installed": "✅", "already": "i", "skipped": "⚠️", "failed": "❌"}.get(category, "•")
        self.line(f"{prefix} {message}")

    def detail(self, message: str) -> None:
        """Emit an indented detail line."""
        self.line(f"    {message}")

    def line(self, message: str) -> None:
        """Write a line to the callback and optional log file."""
        if self._log is not None:
            self._log(message)
        if self._file is not None:
            self._file.parent.mkdir(parents=True, exist_ok=True)
            with self._file.open("a", encoding="utf-8") as f:
                f.write(message + "\n")

    def set_log(self, log: LogFn | None, *, log_file: Path | None = None) -> None:
        """Attach a live log callback and optional log file path."""
        self._log = log
        self._file = log_file

    def step(self, message: str) -> None:
        """Emit a step header line."""
        self.line(f"==> {message}")

    def summary_lines(self, *, action_label: str = "What was installed:") -> list[str]:
        """Build human-readable summary lines from collected outcomes."""
        lines: list[str] = ["", "Summary"]
        for title, items in (
            ("What already existed:", self.already),
            ("What was skipped:", self.skipped),
            (action_label, self.installed),
            ("What failed (installation continued):", self.failed),
        ):
            if items:
                lines.append("")
                lines.append(title)
                lines.extend(f"  - {m}" for m in items)
        return lines
