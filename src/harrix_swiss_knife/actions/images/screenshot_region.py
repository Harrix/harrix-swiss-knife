"""Screenshot region capture action."""

from __future__ import annotations

from typing import Any

from harrix_swiss_knife.actions.base import ActionBase
from harrix_swiss_knife.screenshot import capture_region


class OnScreenshotRegion(ActionBase):
    """Capture a screen region to the clipboard (ShareX-like flow)."""

    icon = "📷"
    title = "Screenshot region"
    bold_title = False
    quick_launcher = True

    @ActionBase.handle_exceptions("screenshot region")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Hide app Windows, select a region, copy it, and show a preview dialog."""
        image = capture_region(show_preview=True, show_shutter_button=True)
        if image is None:
            self.add_line("Screenshot cancelled")
            return
        self.add_line("Screenshot copied to clipboard")
