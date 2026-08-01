"""Screenshot region capture action."""

from __future__ import annotations

from typing import Any

from harrix_swiss_knife.actions.base import ActionBase
from harrix_swiss_knife.screenshot import capture_region


class OnScreenshotRegion(ActionBase):
    """Capture a screen region to the clipboard (ShareX-like flow).

    Starts in region-selection mode with the app hidden. The left camera button
    toggles desktop-arrangement mode (app stays hidden); close cancels.

    """

    icon = "📷"
    title = "Screenshot region"
    bold_title = False
    quick_launcher = True

    @ActionBase.handle_exceptions("screenshot region")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Start region selection; camera toggles desktop mode, close cancels."""
        image = capture_region(show_preview=True, show_shutter_button=True)
        if image is None:
            self.add_line("Screenshot cancelled")
            return
        message = "Screenshot copied to clipboard"
        self.add_line(message)
        self.show_toast(message)
