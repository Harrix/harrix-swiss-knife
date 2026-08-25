"""Open the Quick paste overlay."""

from __future__ import annotations

from typing import Any

from harrix_swiss_knife.actions.common.base import ActionBase
from harrix_swiss_knife.apps.snippets.dialog import SnippetsDialog


class OnSnippets(ActionBase):
    """Show or hide the Quick paste overlay."""

    icon = "📋"
    title = "Quick paste"
    bold_title = False
    quick_launcher = True

    @ActionBase.handle_exceptions("opening quick paste")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Toggle the snippets overlay."""
        SnippetsDialog.toggle()
