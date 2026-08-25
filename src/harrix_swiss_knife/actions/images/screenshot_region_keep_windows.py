"""Screenshot region capture that keeps application Windows visible."""

from __future__ import annotations

from typing import Any

from harrix_swiss_knife.actions.common.base import ActionBase
from harrix_swiss_knife.screenshot import capture_region


class OnScreenshotRegionKeepWindows(ActionBase):
    """Capture a screen region without hiding this application's Windows.

    Same ShareX-like flow as `OnScreenshotRegion`, but tracker and other app
    Windows stay on screen so they can be included in the screenshot.

    """

    icon = "📷"
    title = "Screenshot region (keep Windows)"
    bold_title = False
    quick_launcher = True

    @ActionBase.handle_exceptions("screenshot region keep Windows")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Start region selection without concealing application Windows."""
        image = capture_region(show_preview=True, show_shutter_button=True, hide_app=False)
        if image is None:
            self.add_line("Screenshot cancelled")
            return
        message = "Screenshot copied to clipboard"
        self.add_line(message)
        self.show_toast(message)
