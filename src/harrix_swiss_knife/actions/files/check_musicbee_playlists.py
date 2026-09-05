"""Check MusicBee playlists, remap moved files, and apply Stream rules."""

from __future__ import annotations

from typing import Any

from harrix_swiss_knife.actions.common.base import ActionBase
from harrix_swiss_knife.actions.common.text_result_dialog import (
    CANCEL_BUTTON_EMOJI,
    CANCEL_BUTTON_LABEL,
    RERUN_DIALOG_CODE,
)
from harrix_swiss_knife.musicbee.process import (
    CheckPlan,
    apply_plan,
    format_check_report,
    is_musicbee_running,
    run_check,
)
from harrix_swiss_knife.musicbee.settings import load_musicbee_settings
from harrix_swiss_knife.paths import get_config_path_str


class OnCheckMusicBeePlaylists(ActionBase):
    """Backup MusicBee data, preview remaps and Stream rules, then apply on confirm.

    Static `.mbp` playlists and `MusicBeeLibrary.mbl` paths can be rewritten so
    play counts stay on the same library record. Smart `.xautopf` playlists and
    files under the music folder are not modified.

    """

    icon = "🎵"
    title = "Check MusicBee playlists"
    description = "Backup MusicBee data, remap moved tracks, and apply Stream playlist rules."

    @ActionBase.handle_exceptions("checking MusicBee playlists")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Backup, scan, and show a preview with an Apply button when needed."""
        self._plan: CheckPlan | None = None
        try:
            self._settings = load_musicbee_settings(self.config, config_path=get_config_path_str())
        except ValueError as exc:
            self.add_line(f"❌ {exc}")
            self.show_result()
            return
        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("checking MusicBee playlists thread")
    def in_thread(self) -> CheckPlan:
        """Backup the library and compute remaps plus Stream rule diffs."""
        return run_check(self._settings)

    @ActionBase.handle_exceptions("checking MusicBee playlists thread completion")
    def thread_after(self, result: Any) -> None:
        """Show the preview report and apply writes when the user confirms."""
        if not isinstance(result, CheckPlan):
            self.show_result()
            return
        self._plan = result
        self.result_folder = result.backup_path
        report = format_check_report(result)
        self.add_line(report)
        if not result.has_writes:
            self.show_toast("MusicBee playlists are up to date")
            self.show_result(display_text=report)
            return
        shown = self.show_text_multiline(
            report,
            title="MusicBee playlists",
            open_folder_path=result.backup_path,
            rerun_button=True,
            rerun_button_label="Apply",
            rerun_button_emoji="💾",
            ok_button_label=CANCEL_BUTTON_LABEL,
            ok_button_emoji=CANCEL_BUTTON_EMOJI,
        )
        if not isinstance(shown, tuple) or shown[1] != RERUN_DIALOG_CODE:
            return
        if is_musicbee_running():
            self.add_line("Close MusicBee before applying changes")
            self.show_result(display_text="Close MusicBee, then run Check MusicBee playlists again.")
            return
        written = apply_plan(result)
        summary = "\n".join(["Applied:", *[str(path) for path in written]])
        self.add_line(summary)
        self.show_toast("MusicBee playlists updated")
        self.show_result(display_text=f"{report}\n\n{summary}")
