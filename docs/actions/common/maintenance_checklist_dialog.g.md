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
  - [⚙️ Method `apply_restored_session_done`](#%EF%B8%8F-method-apply_restored_session_done)
  - [⚙️ Method `nativeEvent`](#%EF%B8%8F-method-nativeevent)
  - [⚙️ Method `session_done_class_names`](#%EF%B8%8F-method-session_done_class_names)

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
        self.setObjectName("maintenanceChecklistDialog")
        self.setWindowTitle("Maintenance checklist")
        self.setModal(False)
        self.setWindowModality(Qt.WindowModality.NonModal)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)  # noqa: FBT003
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, on=True)
        self.setProperty(OVERLAY_CAPTION_PROPERTY, True)  # noqa: FBT003
        self.setMinimumSize(720, 560)
        apply_window_icon(self)
        prepare_fluent_app_window(self)

        self._output_bus = output_bus
        self._session_done: set[str] = set()
        self._busy = False
        self._rows: dict[str, _StepRow] = {}
        self._win11_caption = False

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._win11_caption = install_win11_caption(self)

        body = QWidget(self)
        body.setObjectName("maintenanceChecklistBody")
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(SPACE_XL, SPACE_M, SPACE_XL, SPACE_XL)
        body_layout.setSpacing(SPACE_M)

        body_layout.addWidget(
            FluentText(
                "Run update, sync, and check actions. Last run comes from action usage; "
                "green cards ran in the last 24 hours "
                "(Git / Full PY checks stay green on last success, red on failure); "
                "Done marks steps finished in this session.",
                body,
                role=TextRole.SECONDARY,
                word_wrap=True,
            )
        )

        toolbar = QHBoxLayout()
        toolbar.setSpacing(SPACE_S)
        self._run_all_button = FluentPrimaryButton("Run all remaining", body)
        self._run_all_button.clicked.connect(self._on_run_all)
        toolbar.addWidget(self._run_all_button)
        self._progress = FluentText("", body, role=TextRole.SECONDARY)
        toolbar.addWidget(self._progress, 1)
        body_layout.addLayout(toolbar)

        self._scroll = FluentScrollArea(body)
        content = QWidget(self._scroll)
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
        self._scroll.setWidget(content)
        body_layout.addWidget(self._scroll, 1)

        footer = QHBoxLayout()
        footer.setSpacing(SPACE_S)
        update_title = (
            self._rows[UPDATE_HSK_STEP_CLASS].step.title
            if UPDATE_HSK_STEP_CLASS in self._rows
            else ("Update Harrix Swiss Knife from GitHub…")
        )
        self._show_update_hsk = FluentCheckBox(f"Show {update_title}", body)
        self._show_update_hsk.setChecked(load_show_update_hsk_step())
        self._show_update_hsk.toggled.connect(lambda checked: self._on_show_update_hsk_toggled(enabled=checked))
        footer.addWidget(self._show_update_hsk, 1)
        close_button = FluentPushButton("Close", body)
        close_button.clicked.connect(self.accept)
        footer.addWidget(close_button)
        body_layout.addLayout(footer)

        root.addWidget(body, 1)
        install_fluent_app_window(self)

        self._apply_update_hsk_visibility(visible=self._show_update_hsk.isChecked())
        self._refresh_all_rows()
        self._last_run_timer = QTimer(self)
        self._last_run_timer.setInterval(_LAST_RUN_REFRESH_MS)
        self._last_run_timer.timeout.connect(self._refresh_last_run_labels)
        self._last_run_timer.start()
        # Same sizing as food/finance/habits main windows (maximize or ~1920 wide).
        # Win11 caption is frameless; maximize uses the monitor work area (above the taskbar).
        apply_app_window_size_and_position(self)

    def apply_restored_session_done(self, class_names: list[str] | tuple[str, ...]) -> None:
        """Restore session Done marks after a post-upgrade relaunch."""
        for name in class_names:
            if name in self._rows:
                self._session_done.add(name)
        self._refresh_all_rows()

    def nativeEvent(self, event_type: Any, message: Any) -> tuple[bool, int]:  # noqa: N802
        """Keep caption drag, edge resize, and maximized work-area sizing on Windows."""
        handled = try_handle_win11_caption_native_event(self, event_type, message)
        if handled is not None:
            return handled
        return cast("tuple[bool, int]", super().nativeEvent(event_type, message))

    def session_done_class_names(self) -> list[str]:
        """Return action class names marked Done in this checklist session."""
        return sorted(self._session_done)

    def _apply_update_hsk_visibility(self, *, visible: bool) -> None:
        row = self._rows.get(UPDATE_HSK_STEP_CLASS)
        if row is not None:
            row.card.setVisible(visible)

    def _ensure_step_card_visible(self, step: MaintenanceStep) -> None:
        """Keep the step card in view after Run (busy disable can scroll the list away)."""
        row = self._rows.get(step.class_name)
        if row is None:
            return
        self._scroll.ensureWidgetVisible(row.card, 0, 48)

    def _on_run_all(self) -> None:
        if self._busy:
            return
        ordered = [
            row.step
            for row in self._rows.values()
            if self._row_is_listed(row)
            and row.step.include_in_run_all
            and row.step.class_name not in self._session_done
        ]
        if not ordered:
            self._progress.setText("Nothing left to run in this session")
            return

        scroll_pos = self._scroll.verticalScrollBar().value()
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
            self._scroll.verticalScrollBar().setValue(scroll_pos)
            self._ensure_step_card_visible(ordered[-1])

    def _on_run_one(self, step: MaintenanceStep) -> None:
        if self._busy:
            return
        scroll_pos = self._scroll.verticalScrollBar().value()
        self._set_busy(busy=True)
        self._progress.setText(f"Running: {step.title}")
        try:
            self._run_step(step)
            self._session_done.add(step.class_name)
        finally:
            self._set_busy(busy=False)
            self._progress.setText("")
            self._refresh_row(step.class_name)
            visible = self._visible_row_count()
            done = self._visible_session_done_count()
            self._progress.setText(f"Done this session: {done}/{visible}")
            self._scroll.verticalScrollBar().setValue(scroll_pos)
            self._ensure_step_card_visible(step)

    def _on_show_update_hsk_toggled(self, *, enabled: bool) -> None:
        save_show_update_hsk_step(enabled=enabled)
        self._apply_update_hsk_visibility(visible=enabled)
        self._refresh_all_rows()

    def _refresh_all_rows(self) -> None:
        for class_name in self._rows:
            self._refresh_row(class_name)
        done = self._visible_session_done_count()
        if done:
            self._progress.setText(f"Done this session: {done}/{self._visible_row_count()}")

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
        row.run_button.setEnabled(not self._busy and self._row_is_listed(row))

    def _refresh_row_last_run(self, class_name: str) -> None:
        row = self._rows.get(class_name)
        if row is None:
            return
        stamp = last_used_for_class(class_name)
        last_label = format_last_used(stamp)
        note = row.step.note
        description = f"Last run: {last_label}"
        if class_name == CHECK_GIT_REPOS_STEP_CLASS:
            git_clean = load_git_repos_all_clean()
            if git_clean is True:
                note = "All configured repos are clean"
            elif git_clean is False:
                note = "Git: dirty repos under `paths_git_roots`"
        elif class_name == CHECK_PYTHON_PROJECTS_STEP_CLASS:
            py_ok = load_py_check_all_passed()
            if py_ok is True:
                note = "All configured projects passed"
            elif py_ok is False:
                note = "Full PY check failed for one or more projects"
        if note:
            description = f"{description} · {note}"
        if not row.step.include_in_run_all:
            description = f"{description} · Not in Run all"
        row.set_description(description)
        success, danger = self._step_status_tints(class_name, stamp=stamp)
        row.set_status_tints(success=success, danger=danger)

    def _row_is_listed(self, row: _StepRow) -> bool:
        """Return whether the step is shown in the checklist (not Qt visibility).

        `QWidget.isVisible()` is false before the dialog is shown, so Run buttons
        must not depend on it during construction.

        """
        if row.step.class_name == UPDATE_HSK_STEP_CLASS:
            return self._show_update_hsk.isChecked()
        return True

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
        if busy:
            # Disabling the focused Run button makes Qt move focus to the next
            # focusable card inside the scroll area and auto-scroll to it.
            # Keep focus on the dialog itself (Run all is also disabled while busy).
            self.setFocus(Qt.FocusReason.OtherFocusReason)
        self._busy = busy
        self._run_all_button.setEnabled(not busy)
        for row in self._rows.values():
            row.run_button.setEnabled(not busy and self._row_is_listed(row))

    def _step_status_tints(self, class_name: str, *, stamp: str) -> tuple[bool, bool]:
        """Return `(success, danger)` card tints for a checklist step."""
        if class_name == CHECK_GIT_REPOS_STEP_CLASS:
            clean = load_git_repos_all_clean()
            return clean is True, clean is False
        if class_name == CHECK_PYTHON_PROJECTS_STEP_CLASS:
            passed = load_py_check_all_passed()
            return passed is True, passed is False
        return is_last_used_within(stamp, hours=24), False

    def _visible_row_count(self) -> int:
        return sum(1 for row in self._rows.values() if self._row_is_listed(row))

    def _visible_session_done_count(self) -> int:
        return sum(
            1 for class_name, row in self._rows.items() if self._row_is_listed(row) and class_name in self._session_done
        )
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
        self.setObjectName("maintenanceChecklistDialog")
        self.setWindowTitle("Maintenance checklist")
        self.setModal(False)
        self.setWindowModality(Qt.WindowModality.NonModal)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)  # noqa: FBT003
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, on=True)
        self.setProperty(OVERLAY_CAPTION_PROPERTY, True)  # noqa: FBT003
        self.setMinimumSize(720, 560)
        apply_window_icon(self)
        prepare_fluent_app_window(self)

        self._output_bus = output_bus
        self._session_done: set[str] = set()
        self._busy = False
        self._rows: dict[str, _StepRow] = {}
        self._win11_caption = False

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._win11_caption = install_win11_caption(self)

        body = QWidget(self)
        body.setObjectName("maintenanceChecklistBody")
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(SPACE_XL, SPACE_M, SPACE_XL, SPACE_XL)
        body_layout.setSpacing(SPACE_M)

        body_layout.addWidget(
            FluentText(
                "Run update, sync, and check actions. Last run comes from action usage; "
                "green cards ran in the last 24 hours "
                "(Git / Full PY checks stay green on last success, red on failure); "
                "Done marks steps finished in this session.",
                body,
                role=TextRole.SECONDARY,
                word_wrap=True,
            )
        )

        toolbar = QHBoxLayout()
        toolbar.setSpacing(SPACE_S)
        self._run_all_button = FluentPrimaryButton("Run all remaining", body)
        self._run_all_button.clicked.connect(self._on_run_all)
        toolbar.addWidget(self._run_all_button)
        self._progress = FluentText("", body, role=TextRole.SECONDARY)
        toolbar.addWidget(self._progress, 1)
        body_layout.addLayout(toolbar)

        self._scroll = FluentScrollArea(body)
        content = QWidget(self._scroll)
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
        self._scroll.setWidget(content)
        body_layout.addWidget(self._scroll, 1)

        footer = QHBoxLayout()
        footer.setSpacing(SPACE_S)
        update_title = (
            self._rows[UPDATE_HSK_STEP_CLASS].step.title
            if UPDATE_HSK_STEP_CLASS in self._rows
            else ("Update Harrix Swiss Knife from GitHub…")
        )
        self._show_update_hsk = FluentCheckBox(f"Show {update_title}", body)
        self._show_update_hsk.setChecked(load_show_update_hsk_step())
        self._show_update_hsk.toggled.connect(lambda checked: self._on_show_update_hsk_toggled(enabled=checked))
        footer.addWidget(self._show_update_hsk, 1)
        close_button = FluentPushButton("Close", body)
        close_button.clicked.connect(self.accept)
        footer.addWidget(close_button)
        body_layout.addLayout(footer)

        root.addWidget(body, 1)
        install_fluent_app_window(self)

        self._apply_update_hsk_visibility(visible=self._show_update_hsk.isChecked())
        self._refresh_all_rows()
        self._last_run_timer = QTimer(self)
        self._last_run_timer.setInterval(_LAST_RUN_REFRESH_MS)
        self._last_run_timer.timeout.connect(self._refresh_last_run_labels)
        self._last_run_timer.start()
        # Same sizing as food/finance/habits main windows (maximize or ~1920 wide).
        # Win11 caption is frameless; maximize uses the monitor work area (above the taskbar).
        apply_app_window_size_and_position(self)
```

</details>

### ⚙️ Method `apply_restored_session_done`

```python
def apply_restored_session_done(self, class_names: list[str] | tuple[str, ...]) -> None
```

Restore session Done marks after a post-upgrade relaunch.

<details>
<summary>Code:</summary>

```python
def apply_restored_session_done(self, class_names: list[str] | tuple[str, ...]) -> None:
        for name in class_names:
            if name in self._rows:
                self._session_done.add(name)
        self._refresh_all_rows()
```

</details>

### ⚙️ Method `nativeEvent`

```python
def nativeEvent(self, event_type: Any, message: Any) -> tuple[bool, int]
```

Keep caption drag, edge resize, and maximized work-area sizing on Windows.

<details>
<summary>Code:</summary>

```python
def nativeEvent(self, event_type: Any, message: Any) -> tuple[bool, int]:  # noqa: N802
        handled = try_handle_win11_caption_native_event(self, event_type, message)
        if handled is not None:
            return handled
        return cast("tuple[bool, int]", super().nativeEvent(event_type, message))
```

</details>

### ⚙️ Method `session_done_class_names`

```python
def session_done_class_names(self) -> list[str]
```

Return action class names marked Done in this checklist session.

<details>
<summary>Code:</summary>

```python
def session_done_class_names(self) -> list[str]:
        return sorted(self._session_done)
```

</details>
