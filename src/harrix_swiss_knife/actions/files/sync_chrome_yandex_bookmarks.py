"""Sync bookmarks between Google Chrome and Yandex Browser."""

from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import QApplication, QMessageBox

from harrix_swiss_knife.actions.common.base import ActionBase
from harrix_swiss_knife.actions.common.text_result_dialog import (
    CANCEL_BUTTON_EMOJI,
    CANCEL_BUTTON_LABEL,
    RERUN_DIALOG_CODE,
)
from harrix_swiss_knife.apps.common import message_box
from harrix_swiss_knife.browser_bookmarks.paths import running_browser_names
from harrix_swiss_knife.browser_bookmarks.sync import (
    SyncPlan,
    apply_sync_plan,
    build_sync_plan,
    format_sync_report,
)


class OnSyncChromeYandexBookmarks(ActionBase):
    """Bidirectional Chrome ↔ Yandex bookmark sync with a deletion-aware snapshot.

    First run merges missing URLs both ways without deletions. Later runs use a
    LocalAppData snapshot so deletes propagate. Preview shows Cancel / Apply;
    browsers must be closed before Apply.

    """

    icon = "🔖"
    title = "Sync Chrome and Yandex bookmarks"
    description = "Merge and sync bookmarks between Google Chrome and Yandex Browser."

    @ActionBase.handle_exceptions("syncing Chrome and Yandex bookmarks")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Scan Bookmarks files and show a preview with Apply when needed."""
        self._plan: SyncPlan | None = None
        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("syncing Chrome and Yandex bookmarks thread")
    def in_thread(self) -> SyncPlan:
        """Build the sync plan from both Bookmarks files and the snapshot."""
        return build_sync_plan()

    @ActionBase.handle_exceptions("syncing Chrome and Yandex bookmarks thread completion")
    def thread_after(self, result: Any) -> None:
        """Show the preview report and apply writes when the user confirms."""
        if not isinstance(result, SyncPlan):
            self.show_result()
            return
        self._plan = result
        report = format_sync_report(result)
        self.add_line(report)
        if not result.has_writes:
            self.show_toast("Chrome and Yandex bookmarks are in sync")
            self.show_result(display_text=report)
            return
        shown = self.show_text_multiline(
            report,
            title="Sync Chrome and Yandex bookmarks",
            rerun_button=True,
            rerun_button_label="Apply",
            rerun_button_emoji="💾",
            ok_button_label=CANCEL_BUTTON_LABEL,
            ok_button_emoji=CANCEL_BUTTON_EMOJI,
            ok_button_before_actions=True,
        )
        if not isinstance(shown, tuple) or shown[1] != RERUN_DIALOG_CODE:
            return
        if not self._wait_until_browsers_closed():
            self.add_line("Sync cancelled.")
            return
        apply_sync_plan(result)
        if result.backup_path is not None:
            self.result_folder = result.backup_path
        done = format_sync_report(result, applied=True)
        self.add_line(done)
        self.show_toast("Bookmarks synced")
        self.show_result(display_text=done)

    def _wait_until_browsers_closed(self) -> bool:
        """Prompt until Chrome and Yandex are closed, or the user cancels.

        Returns:

        - `bool`: `True` when browsers are closed and sync may proceed.

        """
        while True:
            still_running = running_browser_names()
            if not still_running:
                return True
            names = ", ".join(still_running)
            reply = message_box.question(
                QApplication.activeWindow(),
                "Close browsers",
                f"Close {names}, then click OK to continue sync.\n\nCancel aborts without writing.",
                QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Ok,
            )
            if reply != QMessageBox.StandardButton.Ok:
                return False
