"""Sync global Saved Commands (Save Commands extension) across VS Code-family editors."""

from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import QApplication, QMessageBox

from harrix_swiss_knife.actions.common.base import ActionBase
from harrix_swiss_knife.actions.common.text_result_dialog import (
    CANCEL_BUTTON_LABEL,
    RERUN_DIALOG_CODE,
)
from harrix_swiss_knife.apps.common import message_box
from harrix_swiss_knife.qt_lucide_icon import CANCEL_BUTTON_ICON
from harrix_swiss_knife.save_commands_sync.editors import (
    CLI_EDITOR_CHOICES,
    SUPPORTED_EDITOR_LABELS,
    canonical_editor_label,
    discover_editors,
    editor_choice_label,
    resolve_editor_cli_token,
    running_editor_names,
    save_commands_extension_installed,
    state_vscdb_path,
)
from harrix_swiss_knife.save_commands_sync.storage import SaveCommandsStorageError
from harrix_swiss_knife.save_commands_sync.sync import (
    MIN_SYNC_EDITORS,
    SyncPlan,
    apply_sync_plan,
    build_sync_plan,
    default_sync_editor_labels,
    format_sync_report,
)


class OnSyncSaveCommands(ActionBase):
    """Union global Saved Commands from the Save Commands extension across selected editors.

    Merges commands stored in each editor's `state.vscdb` (`deepakgupta191199.save-commands`).
    Workspace-scoped commands stay in that workspace. Close selected editors before Apply so
    they do not overwrite the database on exit.

    """

    icon = "🔄"
    title = "Sync Saved Commands between editors…"
    description = "Union global Save Commands lists across VS Code Insiders, Cursor, and other editors."
    cli_available = True
    cli_hint = "vscode sync-save-commands [EDITOR...]"
    bold_title = True
    CLI_EDITOR_CHOICES: tuple[str, ...] = CLI_EDITOR_CHOICES

    @ActionBase.handle_exceptions("sync Saved Commands")
    def execute(
        self,
        *_args: Any,
        editors: tuple[str, ...] | list[str] | None = None,
        force: bool = False,
        noninteractive: bool = False,
        **_kwargs: Any,
    ) -> None:
        """Select editors, preview the union, and write merged commands into each `state.vscdb`."""
        if noninteractive:
            self._execute_cli(editors, force=force)
            return
        self._execute_gui()

    def _apply_plan(self, plan: SyncPlan, *, force: bool, show_dialog: bool) -> bool:
        """Write the merged commands; return `False` when storage fails."""
        try:
            apply_sync_plan(plan, force=force)
        except SaveCommandsStorageError as exc:
            self.add_line(f"❌ {exc}")
            if show_dialog:
                self.show_result()
            return False
        return True

    def _build_plan(self, labels: list[str], *, show_dialog: bool) -> SyncPlan | None:
        """Read selected editors and merge; return `None` when storage fails."""
        try:
            return build_sync_plan(labels)
        except SaveCommandsStorageError as exc:
            self.add_line(f"❌ {exc}")
            if show_dialog:
                self.show_result()
            return None

    def _execute_cli(self, editors: tuple[str, ...] | list[str] | None, *, force: bool) -> None:
        """CLI path: resolve editors, print a report, and write unless blocked."""
        labels = self._resolve_cli_editors(editors)
        if labels is None:
            return
        plan = self._build_plan(labels, show_dialog=False)
        if plan is None:
            return
        report = format_sync_report(plan)
        self.add_line(report)
        if not plan.has_writes:
            return
        if plan.running and not force:
            names = ", ".join(plan.running)
            self.add_line(
                f"❌ Close {names} and run again, or pass --force (the editors overwrite state.vscdb on exit)."
            )
            return
        if not self._apply_plan(plan, force=force, show_dialog=False):
            return
        self.add_line(format_sync_report(plan, applied=True))

    def _execute_gui(self) -> None:
        """Tray path: checkbox editors, preview, then Apply after they are closed."""
        labels = self._select_editors_interactive()
        if labels is None:
            return
        plan = self._build_plan(labels, show_dialog=True)
        if plan is None:
            return
        self._plan = plan
        report = format_sync_report(plan)
        self.add_line(report)
        if not plan.has_writes:
            self.show_toast("Saved Commands already in sync")
            self.show_result(display_text=report)
            return
        shown = self.show_text_multiline(
            report,
            title=self.title,
            rerun_button=True,
            rerun_button_label="Apply",
            rerun_button_icon="save",
            ok_button_label=CANCEL_BUTTON_LABEL,
            ok_button_icon=CANCEL_BUTTON_ICON,
            ok_button_before_actions=True,
        )
        if not isinstance(shown, tuple) or shown[1] != RERUN_DIALOG_CODE:
            return
        if not self._wait_until_editors_closed(labels):
            self.add_line("Sync cancelled.")
            return
        if not self._apply_plan(plan, force=False, show_dialog=True):
            return
        if plan.backup_path is not None:
            self.result_folder = plan.backup_path
        done = format_sync_report(plan, applied=True)
        self.add_line(done)
        self.show_toast("Saved Commands synced")
        self.show_result(display_text=done)

    def _resolve_cli_editors(self, editors: tuple[str, ...] | list[str] | None) -> list[str] | None:
        tokens = [str(token).strip() for token in (editors or ()) if str(token).strip()]
        if not tokens:
            labels = default_sync_editor_labels()
            if len(labels) < MIN_SYNC_EDITORS:
                supported = ", ".join(self.CLI_EDITOR_CHOICES)
                self.add_line(
                    f"❌ Need at least two editors with Save Commands user data. Pass EDITOR tokens ({supported})."
                )
                return None
            return labels

        labels: list[str] = []
        for token in tokens:
            label = resolve_editor_cli_token(token)
            if label is None:
                supported = ", ".join(self.CLI_EDITOR_CHOICES)
                self.add_line(f'❌ Unknown editor "{token}". Supported: {supported}.')
                return None
            if label not in labels:
                labels.append(label)
        if len(labels) < MIN_SYNC_EDITORS:
            self.add_line("❌ Pass at least two editors.")
            return None
        return labels

    def _select_editors_interactive(self) -> list[str] | None:
        """Show editor checkboxes; return canonical labels or `None` if canceled."""
        installed = set(discover_editors())
        has_db: set[str] = set()
        for label in SUPPORTED_EDITOR_LABELS:
            db_path = state_vscdb_path(label)
            if db_path is not None and db_path.is_file():
                has_db.add(label)
        enabled = installed | has_db
        choices = [editor_choice_label(label, installed=label in enabled) for label in SUPPORTED_EDITOR_LABELS]
        disabled_choices = [
            editor_choice_label(label, installed=False) for label in SUPPORTED_EDITOR_LABELS if label not in enabled
        ]
        with_extension = [
            label for label in SUPPORTED_EDITOR_LABELS if label in enabled and save_commands_extension_installed(label)
        ]
        default_labels = (
            with_extension
            if len(with_extension) >= MIN_SYNC_EDITORS
            else [label for label in SUPPORTED_EDITOR_LABELS if label in enabled]
        )
        default_selected = [editor_choice_label(label, installed=True) for label in default_labels]

        selected_raw = self.dialogs.get_checkbox_selection(
            self.title,
            "Union global Saved Commands (Save Commands extension) across which editors? "
            "Workspace-scoped commands are not copied. Close those editors before Apply. "
            "Grayed items are not detected on this system.",
            choices,
            default_selected=default_selected,
            disabled_choices=disabled_choices,
        )
        if selected_raw is None:
            return None
        labels = [canonical_editor_label(item) for item in selected_raw]
        if len(labels) < MIN_SYNC_EDITORS:
            self.add_line("❌ Select at least two editors.")
            self.show_result()
            return None
        return labels

    def _wait_until_editors_closed(self, labels: list[str]) -> bool:
        """Prompt until selected editors are closed, or the user cancels."""
        while True:
            still_running = running_editor_names(labels)
            if not still_running:
                return True
            names = ", ".join(still_running)
            reply = message_box.question(
                QApplication.activeWindow(),
                "Close editors",
                f"Close {names}, then click OK to continue sync.\n\nCancel aborts without writing.",
                QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Ok,
            )
            if reply != QMessageBox.StandardButton.Ok:
                return False
