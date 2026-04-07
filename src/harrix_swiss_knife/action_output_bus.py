"""Qt signal bus for streaming action output to the UI."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QObject, Signal


class ActionOutputBus(QObject):
    """Thread-safe bus for action output events (via queued Qt signals)."""

    active_output_changed: Signal = Signal(str)  # absolute path as string
    line_appended: Signal = Signal(str, str)  # (absolute path, line)

    def append_line(self, path: Path, line: str) -> None:
        self.line_appended.emit(str(path.resolve()), line)

    def set_active_output(self, path: Path) -> None:
        self.active_output_changed.emit(str(path.resolve()))
