"""Screenshot region capture to clipboard only (app hidden, no preview)."""

from __future__ import annotations

from typing import Any

from harrix_swiss_knife.actions.common.base import ActionBase
from harrix_swiss_knife.screenshot import capture_region


class OnScreenshotRegionClipboard(ActionBase):
    """Capture a screen region to the clipboard without opening the preview window.

    Same ShareX-like selection as `OnScreenshotRegion`, but skips the preview UI.

    """

    icon = "📷"
    title = "Screenshot region (clipboard)"
    bold_title = False
    quick_launcher = True

    @ActionBase.handle_exceptions("screenshot region clipboard")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Start region selection; copy to clipboard only."""
        image = capture_region(show_preview=False, show_shutter_button=True, hide_app=True)
        if image is None:
            self.add_line("Screenshot cancelled")
            return
        message = "Screenshot copied to clipboard"
        self.add_line(message)
        self.show_toast(message)
