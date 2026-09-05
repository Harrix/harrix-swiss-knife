"""Screen region recording action."""

from __future__ import annotations

from typing import Any

from harrix_swiss_knife.actions.common.base import ActionBase
from harrix_swiss_knife.screen_record import record_region


class OnRecordRegion(ActionBase):
    """Record a screen region to MP4 (ShareX-like).

    Select a region, adjust the frame (move/resize), choose audio, then record
    immediately or after a configurable countdown. Stop saves `temp/videos`.

    """

    icon = "🎥"
    title = "Record region"
    bold_title = False
    quick_launcher = True

    @ActionBase.handle_exceptions("record region")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Open region selection, then the recording frame."""

        def on_finished(path: object) -> None:
            message = f"Recording saved: {path}"
            self.add_line(message)
            self.show_toast(message)

        started = record_region(on_finished=on_finished)
        if not started:
            self.add_line("Screen recording cancelled or unavailable")
