"""Screenshot region capture with Harrix app Windows kept visible."""

from __future__ import annotations

from typing import Any

from harrix_swiss_knife.actions.common.base import ActionBase
from harrix_swiss_knife.screenshot import capture_region


class OnScreenshotRegionKeepWindows(ActionBase):
    """Capture a screen region while keeping Harrix Swiss Knife Windows visible.

    Same ShareX-like selection as `OnScreenshotRegion`, but starts with the
    Show Harrix app shutter toggle on so application Windows are not concealed
    before the grab.

    """

    icon = "👀"
    icon_svg = "it__camera.svg"
    title = "Screenshot region (show app)"
    bold_title = False
    quick_launcher = True

    @ActionBase.handle_exceptions("screenshot region show app")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Start region selection without hiding application Windows."""
        image = capture_region(show_preview=True, show_shutter_button=True, hide_app=False)
        if image is None:
            self.add_line("Screenshot cancelled")
            return
        message = "Screenshot copied to clipboard"
        self.add_line(message)
        self.show_toast(message, collapsed=True)
