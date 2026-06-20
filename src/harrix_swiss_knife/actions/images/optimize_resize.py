"""Image optimization and management actions."""

from __future__ import annotations

from typing import Any

import harrix_pylib as h

from harrix_swiss_knife.actions.base import ActionBase
from harrix_swiss_knife.actions.images.optimize import OnOptimize


class OnOptimizeResize(OnOptimize):
    """Resize and optimize images (asks for max size in pixels)."""

    icon = "↔️"
    title = "Resize and optimize images…"
    max_size: int

    @ActionBase.handle_exceptions("resize and optimize")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Resize and optimize images (asks for max size in pixels)."""
        max_size_text = self.dialogs.get_text_input("Max size", "Input max image size in pixels", "1024")

        if max_size_text is None:
            return

        self.max_size = int(max_size_text)
        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("resize and optimize thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        project_root = h.dev.get_project_root()
        return self.run_optimize_images(
            project_root / "temp/images",
            project_root / "temp/optimized_images",
            max_size=self.max_size,
        )
