"""Image optimization and management actions."""

from __future__ import annotations

from typing import Any

import harrix_pylib as h

from harrix_swiss_knife.actions.base import ActionBase
from harrix_swiss_knife.actions.images.optimize import OnOptimize


class OnOptimizeResize(OnOptimize):
    """Resize and optimize images (asks for max size in pixels)."""

    icon = "↔️"
    title = "Resize and optimize images"

    @ActionBase.handle_exceptions("resize and optimize")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Resize and optimize images (asks for max size in pixels)."""
        self.max_size = self.dialogs.get_text_input("Max size", "Input max image size in pixels", "1024")

        if self.max_size is None:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("resize and optimize thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        return self.optimize_images_common(
            f"npm run optimize convertPngToAvif=compare maxSize={self.max_size}",
            h.dev.get_project_root() / "temp/optimized_images",
        )
