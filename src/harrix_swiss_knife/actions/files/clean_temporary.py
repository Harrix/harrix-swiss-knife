"""Select and clean temporary / reclaimable disk locations."""

from __future__ import annotations

from typing import Any

import harrix_pylib as h

from harrix_swiss_knife.actions.common.base import ActionBase
from harrix_swiss_knife.actions.common.disk_cleanup import (
    CleanupTarget,
    discover_targets,
    format_cleanup_choice_sizes,
    run_cleanup,
)


class OnCleanTemporary(ActionBase):
    """Offer reclaimable temp locations with sizes, then clean the selected ones."""

    icon = "🧽"
    title = "Clean temporary files"
    cli_available = False

    @ActionBase.handle_exceptions("cleaning temporary files")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Scan targets, let the user select, confirm, then clean in a thread."""
        self.selected_targets: list[CleanupTarget] = []
        self.show_toast("Scanning cleanup targets…")
        self.add_line("🔵 Scanning cleanup targets…")
        targets = discover_targets(on_progress=self.add_line)
        if not targets:
            self.add_line("Nothing to clean (no reclaimable locations found).")
            self.show_toast("Nothing to clean")
            self.show_result()
            return

        choices = [target.choice_label() for target in targets]
        label_to_target = {target.choice_label(): target for target in targets}
        default_selected = [target.choice_label() for target in targets if target.default_selected]
        choice_sizes = format_cleanup_choice_sizes(targets)

        selected_labels = self.dialogs.get_checkbox_selection(
            self.title,
            "Choose locations to clean. Sizes are approximate; locked files may remain.",
            choices,
            default_selected=default_selected or None,
            choice_sizes=choice_sizes,
        )
        if not selected_labels:
            return

        selected = [label_to_target[label] for label in selected_labels if label in label_to_target]
        if not selected:
            return

        selected_bytes = sum(target.size_bytes for target in selected)
        warning = ""
        if any(target.id == "windows_old" for target in selected):
            warning = "\n\nWarning: Windows.old will be permanently deleted."

        confirmed = self.dialogs.get_yes_no_question(
            self.title,
            (f"Delete {len(selected)} location(s) and free about {h.file.format_byte_size(selected_bytes)}?{warning}"),
            default_yes=False,
        )
        if not confirmed:
            return

        self.selected_targets = selected
        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("cleaning temporary files thread")
    def in_thread(self) -> None:
        """Delete selected cleanup targets in a background thread."""
        result = run_cleanup(self.selected_targets, on_progress=self.add_line)
        for line in result.lines:
            self.add_line(line)
        self.add_line(
            f"Expected reclaimable space: {h.file.format_byte_size(result.expected_bytes)} "
            "(actual free space may be less if some files were locked)."
        )
        if result.errors:
            self.add_line(f"Errors: {len(result.errors)}")
        self.add_elapsed_time()

    @ActionBase.handle_exceptions("cleaning temporary files completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Show toast and result dialog after cleanup finishes."""
        self.show_toast(f"{self.title} completed")
        self.show_result()
