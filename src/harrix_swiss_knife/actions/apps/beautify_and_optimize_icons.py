"""Beautify Markdown notes and optimize SVG files in a Vector Icons repo."""

from __future__ import annotations

from typing import Any

from harrix_swiss_knife.actions.apps.icon_repo import pick_vector_icons_repo
from harrix_swiss_knife.actions.common.base import ActionBase
from harrix_swiss_knife.apps.icons.repo_maintenance import beautify_and_optimize_icons


class OnBeautifyAndOptimizeIcons(ActionBase):
    """Beautify icon Markdown notes and optimize SVG files in place.

    Uses the same job as Vector Icons → File → Beautify and optimize icons:
    `Beautify MD` on `icons/`, then SVG optimize (the existing optimize
    action) for every `.svg` under that tree.

    """

    icon = "💎"
    title = "Beautify and optimize icons"

    @ActionBase.handle_exceptions("beautifying and optimizing icons")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Beautify Markdown and optimize SVGs in the selected repo."""
        self.folder_path = pick_vector_icons_repo(self)
        if self.folder_path is None:
            return
        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("beautifying and optimizing icons thread")
    def in_thread(self) -> None:
        """Run Beautify MD and SVG optimize."""
        if self.folder_path is None:
            return
        self.add_line(beautify_and_optimize_icons(self.folder_path))

    @ActionBase.handle_exceptions("beautifying and optimizing icons thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Show toast and the beautify/optimize report."""
        self.show_toast(f"{self.title} completed")
        self.show_result()
