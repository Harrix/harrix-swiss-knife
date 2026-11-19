---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `maintenance_checklist_dialog.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `MaintenanceChecklistDialog`](#%EF%B8%8F-class-maintenancechecklistdialog)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)

</details>

## 🏛️ Class `MaintenanceChecklistDialog`

```python
class MaintenanceChecklistDialog(QDialog)
```

Scrollable Fluent checklist: Run each step, mark session done, Run all.

<details>
<summary>Code:</summary>

```python
class MaintenanceChecklistDialog(QDialog):

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        output_bus: ActionOutputBus | None = None,
    ) -> None:
        """Build the checklist UI."""
        super().__init__(parent)
        self.setWindowTitle("Maintenance checklist")
        self.setModal(False)
        self.setWindowModality(Qt.WindowModality.NonModal)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)  # noqa: FBT003
        self.setMinimumSize(720, 560)
        enable_fluent_theme(self)

        self._output_bus = output_bus
        self._session_done: set[str] = set()
        self._busy = False
        self._rows: dict[str, _StepRow] = {}

        root = QVBoxLayout(self)
        root.setContentsMargins(SPACE_XL, SPACE_XL, SPACE_XL, SPACE_XL)
        root.setSpacing(SPACE_M)

        root.addWidget(FluentText("Maintenance checklist", self, style=TextStyle.SUBTITLE))
        root.addWidget(
            FluentText(
                "Run update, sync, and check actions. Last run comes from action usage; "
                "green cards ran in the last 24 hours; Done marks steps finished in this session.",
                self,
                role=TextRole.SECONDARY,
                word_wrap=True,
            )
        )

        toolbar = QHBoxLayout()
        toolbar.setSpacing(SPACE_S)
        self._run_all_button = FluentPrimaryButton("Run all remaining", self)
        self._run_all_button.clicked.connect(self._on_run_all)
        toolbar.addWidget(self._run_all_button)
        self._progress = FluentText("", self, role=TextRole.SECONDARY)
        toolbar.addWidget(self._progress, 1)
        root.addLayout(toolbar)

        scroll = FluentScrollArea(self)
        content = QWidget(scroll)
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, SPACE_S, 0)
        content_layout.setSpacing(SPACE_L)

        for group_title, steps in maintenance_groups():
            group = FluentGroupBox(group_title, content)
            for step in steps:
                row = _StepRow(step, group)
                row.run_button.clicked.connect(lambda _checked=False, s=step: self._on_run_one(s))
                self._rows[step.class_name] = row
                group.add_widget(row.card)
            content_layout.addWidget(group)

        content_layout.addStretch(1)
        scroll.setWidget(content)
        root.addWidget(scroll, 1)

        footer = QHBoxLayout()
        footer.addStretch(1)
        close_button = FluentPushButton("Close", self)
        close_button.clicked.connect(self.accept)
        footer.addWidget(close_button)
        root.addLayout(footer)

        self._refresh_all_rows()
        self._last_run_timer = QTimer(self)
        self._last_run_timer.setInterval(_LAST_RUN_REFRESH_MS)
        self._last_run_timer.timeout.connect(self._refresh_last_run_labels)
        self._last_run_timer.start()
        # Same sizing as food/finance/habits main windows (maximize or ~1920 wide).
        apply_app_window_size_and_position(self)

    def _on_run_all(self) -> None:
        if self._busy:
            return
        ordered = [
            row.step
            for row in self._rows.values()
            if row.step.include_in_run_all and row.step.class_name not in self._session_done
        ]
        if not ordered:
            self._progress.setText("Nothing left to run in this session")
            return

        self._set_busy(busy=True)
        try:
            for index, step in enumerate(ordered, start=1):
                self._progress.setText(f"Running {index}/{len(ordered)}: {step.title}")
                self._run_step(step)
                self._session_done.add(step.class_name)
                self._refresh_row(step.class_name)
        finally:
            self._set_busy(busy=False)
            self._progress.setText("Run all finished")
            self._refresh_all_rows()

    def _on_run_one(self, step: MaintenanceStep) -> None:
        if self._busy:
            return
        self._set_busy(busy=True)
        self._progress.setText(f"Running: {step.title}")
        try:
            self._run_step(step)
            self._session_done.add(step.class_name)
        finally:
            self._set_busy(busy=False)
            self._progress.setText("")
            self._refresh_row(step.class_name)
            done = len(self._session_done)
            self._progress.setText(f"Done this session: {done}/{len(self._rows)}")

    def _refresh_all_rows(self) -> None:
        for class_name in self._rows:
            self._refresh_row(class_name)
        done = len(self._session_done)
        if done:
            self._progress.setText(f"Done this session: {done}/{len(self._rows)}")

    def _refresh_last_run_labels(self) -> None:
        """Recompute relative Last-run captions without touching progress/busy UI."""
        for class_name in self._rows:
            self._refresh_row_last_run(class_name)

    def _refresh_row(self, class_name: str) -> None:
        row = self._rows.get(class_name)
        if row is None:
            return
        self._refresh_row_last_run(class_name)
        row.set_done(done=class_name in self._session_done)
        row.run_button.setEnabled(not self._busy)

    def _refresh_row_last_run(self, class_name: str) -> None:
        row = self._rows.get(class_name)
        if row is None:
            return
        stamp = last_used_for_class(class_name)
        last_label = format_last_used(stamp)
        note = row.step.note
        description = f"Last run: {last_label}"
        if note:
            description = f"{description} · {note}"
        if not row.step.include_in_run_all:
            description = f"{description} · Not in Run all"
        row.set_description(description)
        row.set_recent(recent=is_last_used_within(stamp, hours=24))

    def _run_step(self, step: MaintenanceStep) -> None:
        action: ActionBase = step.action_cls(output_bus=self._output_bus)
        action()
        worker = getattr(action, "_current_worker", None)
        if worker is not None and worker.isRunning():
            loop = QEventLoop(self)
            worker.finished.connect(loop.quit)
            if worker.isRunning():
                loop.exec()

    def _set_busy(self, *, busy: bool) -> None:
        self._busy = busy
        self._run_all_button.setEnabled(not busy)
        for row in self._rows.values():
            row.run_button.setEnabled(not busy)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None, *, output_bus: ActionOutputBus | None = None) -> None
```

Build the checklist UI.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        parent: QWidget | None = None,
        *,
        output_bus: ActionOutputBus | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Maintenance checklist")
        self.setModal(False)
        self.setWindowModality(Qt.WindowModality.NonModal)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)  # noqa: FBT003
        self.setMinimumSize(720, 560)
        enable_fluent_theme(self)

        self._output_bus = output_bus
        self._session_done: set[str] = set()
        self._busy = False
        self._rows: dict[str, _StepRow] = {}

        root = QVBoxLayout(self)
        root.setContentsMargins(SPACE_XL, SPACE_XL, SPACE_XL, SPACE_XL)
        root.setSpacing(SPACE_M)

        root.addWidget(FluentText("Maintenance checklist", self, style=TextStyle.SUBTITLE))
        root.addWidget(
            FluentText(
                "Run update, sync, and check actions. Last run comes from action usage; "
                "green cards ran in the last 24 hours; Done marks steps finished in this session.",
                self,
                role=TextRole.SECONDARY,
                word_wrap=True,
            )
        )

        toolbar = QHBoxLayout()
        toolbar.setSpacing(SPACE_S)
        self._run_all_button = FluentPrimaryButton("Run all remaining", self)
        self._run_all_button.clicked.connect(self._on_run_all)
        toolbar.addWidget(self._run_all_button)
        self._progress = FluentText("", self, role=TextRole.SECONDARY)
        toolbar.addWidget(self._progress, 1)
        root.addLayout(toolbar)

        scroll = FluentScrollArea(self)
        content = QWidget(scroll)
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, SPACE_S, 0)
        content_layout.setSpacing(SPACE_L)

        for group_title, steps in maintenance_groups():
            group = FluentGroupBox(group_title, content)
            for step in steps:
                row = _StepRow(step, group)
                row.run_button.clicked.connect(lambda _checked=False, s=step: self._on_run_one(s))
                self._rows[step.class_name] = row
                group.add_widget(row.card)
            content_layout.addWidget(group)

        content_layout.addStretch(1)
        scroll.setWidget(content)
        root.addWidget(scroll, 1)

        footer = QHBoxLayout()
        footer.addStretch(1)
        close_button = FluentPushButton("Close", self)
        close_button.clicked.connect(self.accept)
        footer.addWidget(close_button)
        root.addLayout(footer)

        self._refresh_all_rows()
        self._last_run_timer = QTimer(self)
        self._last_run_timer.setInterval(_LAST_RUN_REFRESH_MS)
        self._last_run_timer.timeout.connect(self._refresh_last_run_labels)
        self._last_run_timer.start()
        # Same sizing as food/finance/habits main windows (maximize or ~1920 wide).
        apply_app_window_size_and_position(self)
```

</details>
