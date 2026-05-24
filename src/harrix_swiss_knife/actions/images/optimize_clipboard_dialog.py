"""Image optimization and management actions."""

from __future__ import annotations

from typing import Any

from harrix_swiss_knife.actions.base import ActionBase
from harrix_swiss_knife.actions.images.optimize_clipboard import OnOptimizeClipboard


class OnOptimizeClipboardDialog(ActionBase):
    """Optimize an image from the clipboard with custom naming.

    This action extends OnOptimizeClipboard by prompting the user to provide
    a custom filename for the optimized image, allowing for more organized
    image management in the output directory.
    """

    icon = "🚀"
    title = "Optimize image from clipboard as …"
    bold_title = False

    @ActionBase.handle_exceptions("clipboard image optimization with dialog")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Optimize an image from the clipboard with custom naming."""
        OnOptimizeClipboard().execute(is_dialog=True)
