"""Actions for Python development and code management."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from harrix_swiss_knife.actions.base import ActionBase
from harrix_swiss_knife.paths import list_recent_action_output_files

if TYPE_CHECKING:
    from pathlib import Path


class OnViewRecentActionLogs(ActionBase):
    """Browse and open text logs from recent action runs (`temp/action_output`)."""

    icon = "📋"
    title = "View recent action logs"

    @ActionBase.handle_exceptions("view recent action logs")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Open split-view browser: file list and live preview; sync main window when selection changes."""
        paths = list_recent_action_output_files(non_empty_only=True)
        if not paths:
            self.add_line("No action log files found in temp/action_output.")
            self.show_result()
            return

        entries: list[tuple[Path, str]] = []
        for path in paths:
            stat = path.stat()
            mtime = datetime.fromtimestamp(stat.st_mtime, tz=UTC).astimezone().strftime("%Y-%m-%d %H:%M:%S")
            entries.append((path, f"{mtime} · {self._format_byte_size(stat.st_size)}"))

        def sync_main_window(path: Path) -> None:
            if self._output_bus is not None:
                self._output_bus.set_active_output(path)

        self.dialogs.show_action_output_log_browser(entries, on_file_selected=sync_main_window)

    def _format_byte_size(self, num_bytes: int) -> str:
        """Return a short human-readable size for file listings."""
        bytes_per_kib = 1024
        if num_bytes < bytes_per_kib:
            return f"{num_bytes} B"
        return f"{num_bytes / bytes_per_kib:.1f} KiB"
