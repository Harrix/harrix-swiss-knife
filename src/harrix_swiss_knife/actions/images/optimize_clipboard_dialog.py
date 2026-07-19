"""Image optimization and management actions."""

from __future__ import annotations

from typing import Any

from harrix_swiss_knife.actions.base import ActionBase
from harrix_swiss_knife.actions.images.optimize_clipboard import OnOptimizeClipboard


class OnOptimizeClipboardDialog(OnOptimizeClipboard):
    """Optimize an image from the clipboard with custom naming.

    This action extends OnOptimizeClipboard by prompting the user to provide
    a custom filename for the optimized image, allowing for more organized
    image management in the output directory.

    """

    icon = "🚀"
    title = "Optimize image from clipboard as …"
    bold_title = False
    quick_launcher = True

    @ActionBase.handle_exceptions("clipboard image optimization with dialog")
    def execute(self, *args: Any, **kwargs: Any) -> None:
        """Optimize an image from the clipboard with custom naming."""
        super().execute(*args, is_dialog=True, **kwargs)
