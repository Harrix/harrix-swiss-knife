"""Screenshot region capture action."""

from __future__ import annotations

from typing import Any

from harrix_swiss_knife.actions.base import ActionBase
from harrix_swiss_knife.screenshot import capture_region


class OnScreenshotRegion(ActionBase):
    """Capture a screen region to the clipboard (ShareX-like flow).

    Starts in region-selection mode immediately. The left camera button toggles
    window-management mode so Windows can be arranged, then selection again.

    """

    icon = "📷"
    title = "Screenshot region"
    bold_title = False
    quick_launcher = True

    @ActionBase.handle_exceptions("screenshot region")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Start region selection immediately; shutter toggles window-management mode."""
        image = capture_region(show_preview=True, show_shutter_button=True)
        if image is None:
            self.add_line("Screenshot cancelled")
            return
        self.add_line("Screenshot copied to clipboard")
