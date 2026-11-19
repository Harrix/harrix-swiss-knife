---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `run_maintenance_checklist.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnRunMaintenanceChecklist`](#%EF%B8%8F-class-onrunmaintenancechecklist)
  - [⚙️ Method `clear_checklist_dialog (classmethod)`](#%EF%B8%8F-method-clear_checklist_dialog-classmethod)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)

</details>

## 🏛️ Class `OnRunMaintenanceChecklist`

```python
class OnRunMaintenanceChecklist(ActionBase)
```

Fluent checklist of recurring update, sync, and health-check actions.

Shows last-run times from `action_usage.json`, a Done mark for steps finished
in the current session, per-step Run buttons, and Run all remaining
(skips steps marked `include_in_run_all=False` in the registry).

<details>
<summary>Code:</summary>

```python
class OnRunMaintenanceChecklist(ActionBase):

    icon = "🛠️"
    title = "Maintenance checklist…"
    description = "Run update / sync / check actions with last-run times and session Done marks."
    cli_available = True
    cli_hint = "dev maintenance-checklist"
    bold_title = True
    checklist_dialog: ClassVar[MaintenanceChecklistDialog | None] = None

    @classmethod
    def clear_checklist_dialog(cls, *_args: object) -> None:
        """Drop the cached checklist after Qt destroys it."""
        cls.checklist_dialog = None

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

        dialog = OnRunMaintenanceChecklist.checklist_dialog
        if dialog is not None and isValid(dialog):
            dialog.show()
            dialog.raise_()
            dialog.activateWindow()
            self.add_line("✅ Maintenance checklist is already open")
            return

        dialog = MaintenanceChecklistDialog(output_bus=self._output_bus)
        dialog.destroyed.connect(OnRunMaintenanceChecklist.clear_checklist_dialog)
        OnRunMaintenanceChecklist.checklist_dialog = dialog
        dialog.show()
        dialog.raise_()
        dialog.activateWindow()
        self.add_line("✅ Maintenance checklist opened")
```

</details>

### ⚙️ Method `clear_checklist_dialog (classmethod)`

```python
def clear_checklist_dialog(cls, *_args: object) -> None
```

Drop the cached checklist after Qt destroys it.

<details>
<summary>Code:</summary>

```python
def clear_checklist_dialog(cls, *_args: object) -> None:
        cls.checklist_dialog = None
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *_args: Any, noninteractive: bool = False, **_kwargs: Any) -> None
```

Open the checklist dialog, or print the step list in CLI mode.

<details>
<summary>Code:</summary>

```python
def execute(self, *_args: Any, noninteractive: bool = False, **_kwargs: Any) -> None:
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

        dialog = OnRunMaintenanceChecklist.checklist_dialog
        if dialog is not None and isValid(dialog):
            dialog.show()
            dialog.raise_()
            dialog.activateWindow()
            self.add_line("✅ Maintenance checklist is already open")
            return

        dialog = MaintenanceChecklistDialog(output_bus=self._output_bus)
        dialog.destroyed.connect(OnRunMaintenanceChecklist.clear_checklist_dialog)
        OnRunMaintenanceChecklist.checklist_dialog = dialog
        dialog.show()
        dialog.raise_()
        dialog.activateWindow()
        self.add_line("✅ Maintenance checklist opened")
```

</details>
