"""Image optimization and management actions."""

from __future__ import annotations

import harrix_pylib as h

from harrix_swiss_knife.actions.base import ActionBase
from harrix_swiss_knife.actions.images.optimize import OnOptimize


class OnOptimizeQuality(OnOptimize):
    """Optimize images with higher quality settings.

    Processes all images in the temp/images directory using settings
    that prioritize visual quality over file size reduction.
    """

    icon = "🔝"
    title = "Optimize images (high quality)"
    bold_title = False

    @ActionBase.handle_exceptions("high quality optimization thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        project_root = h.dev.get_project_root()
        return self.run_optimize_images(
            project_root / "temp/images",
            project_root / "temp/optimized_images",
            quality=True,
        )
