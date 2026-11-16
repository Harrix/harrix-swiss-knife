"""Open the Fluent maintenance checklist for update / sync / check actions."""

from __future__ import annotations

from typing import Any

from harrix_swiss_knife.actions.common.base import ActionBase
from harrix_swiss_knife.actions.common.maintenance_checklist_steps import maintenance_steps


class OnRunMaintenanceChecklist(ActionBase):
    """Fluent checklist of recurring update, sync, and health-check actions.

    Shows last-run times from `action_usage.json`, a Done mark for steps finished
    in the current session, per-step Run buttons, and Run all remaining
    (skips steps marked `include_in_run_all=False` in the registry).

    """

    icon = "🛠️"
    title = "Maintenance checklist…"
    description = "Run update / sync / check actions with last-run times and session Done marks."
    cli_available = True
    cli_hint = "dev maintenance-checklist"
    bold_title = True

    @ActionBase.handle_exceptions("maintenance checklist")
    def execute(self, *_args: Any, noninteractive: bool = False, **_kwargs: Any) -> None:
        """Open the checklist dialog, or print the step list in CLI mode."""
        steps = maintenance_steps()
        if noninteractive:
            self.add_line(f"🔵 {len(steps)} maintenance step(s):")
            for step in steps:
                flag = "" if step.include_in_run_all else " (manual only)"
                self.add_line(f"  • [{step.group}] {step.title}{flag}")
                if step.note:
                    self.add_line(f"      {step.note}")
            return

        from harrix_swiss_knife.actions.common.maintenance_checklist_dialog import (  # noqa: PLC0415
            MaintenanceChecklistDialog,
        )

        dialog = MaintenanceChecklistDialog(output_bus=self._output_bus)
        dialog.exec()
