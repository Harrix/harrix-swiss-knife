"""Check Vector Icons filenames, folders, categories, and Markdown notes."""

from __future__ import annotations

from typing import Any

from harrix_swiss_knife.actions.apps.icon_repo import pick_vector_icons_repo
from harrix_swiss_knife.actions.common.base import ActionBase
from harrix_swiss_knife.apps.icons.repo_maintenance import check_icon_repo


class OnCheckImages(ActionBase):
    """Check icon filenames, folder/category match, and Markdown notes.

    Uses the same checks as Vector Icons → File → Check images: file names
    must match the family ID, category folders must match the family-id
    prefix and YAML `categories`, then `Check MD` runs on `icons/`.

    """

    icon = "🚧"
    title = "Check images"

    @ActionBase.handle_exceptions("checking images")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Check the selected Vector Icons repository."""
        self.folder_path = pick_vector_icons_repo(self)
        if self.folder_path is None:
            return
        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("checking images thread")
    def in_thread(self) -> None:
        """Run filename, folder, category, and Markdown checks."""
        if self.folder_path is None:
            return
        self.add_line(check_icon_repo(self.folder_path))

    @ActionBase.handle_exceptions("checking images thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Show toast and the check report."""
        self.show_toast(f"{self.title} completed")
        self.show_result()
