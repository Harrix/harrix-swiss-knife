"""Actions for Python development and Markdown file management."""

from __future__ import annotations

from typing import Any

import harrix_pylib as h

from harrix_swiss_knife.actions.base import ActionBase


class OnIncreaseHeadingLevelContent(ActionBase):
    """Increase the heading level of all headings in Markdown content.

    This action takes Markdown content and increases the level of all headings
    by adding an additional `#` character to each heading, making them one level
    deeper in the document hierarchy.
    """

    icon = "👉"
    title = "Heading level: Increase…"

    @ActionBase.handle_exceptions("increasing heading level")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Increase the heading level of all headings in Markdown content."""
        content = self.dialogs.get_text_textarea(
            "Markdown content", "Input Markdown content", "# Title\n\nText\n\n## Subtitle\n\nText"
        )
        if not content:
            return

        new_content = h.md.increase_heading_level_content(content)
        self.add_line(new_content)
        self.show_result()
