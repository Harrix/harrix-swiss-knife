"""Screenshot region to clipboard only, keeping application Windows visible."""

from __future__ import annotations

from typing import Any

from harrix_swiss_knife.actions.common.base import ActionBase
from harrix_swiss_knife.screenshot import capture_region


class OnScreenshotRegionClipboardKeepWindows(ActionBase):
    """Capture a region to the clipboard without preview, keeping app Windows visible.

    Same flow as `OnScreenshotRegionClipboard`, but tracker and other app Windows
    stay on screen so they can be included in the screenshot.

    """

    icon = "📷"
    title = "Screenshot region (clipboard, keep Windows)"
    bold_title = False
    quick_launcher = True

    @ActionBase.handle_exceptions("screenshot region clipboard keep Windows")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Start region selection without concealing Windows; no preview."""
        image = capture_region(show_preview=False, show_shutter_button=True, hide_app=False)
        if image is None:
            self.add_line("Screenshot cancelled")
            return
        message = "Screenshot copied to clipboard"
        self.add_line(message)
        self.show_toast(message)
