"""Image optimization and management actions."""

from __future__ import annotations

import harrix_pylib as h

from harrix_swiss_knife.actions.base import ActionBase
from harrix_swiss_knife.actions.images.optimize import OnOptimize


class OnOptimizeQuality(OnOptimize):
    """Optimize images with higher quality settings.

    This action runs the npm optimize script with the quality flag enabled,
    which processes all images in the temp/images directory using settings
    that prioritize visual quality over file size reduction, suitable for
    images where detail preservation is important.
    """

    icon = "🔝"
    title = "Optimize images (high quality)"
    bold_title = False

    @ActionBase.handle_exceptions("high quality optimization thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        return self.optimize_images_common(
            "npm run optimize quality=true convertPngToAvif=compare",
            h.dev.get_project_root() / "temp/optimized_images",
        )
