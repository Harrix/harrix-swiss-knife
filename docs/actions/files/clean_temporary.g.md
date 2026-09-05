---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `clean_temporary.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnCleanTemporary`](#%EF%B8%8F-class-oncleantemporary)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)
  - [⚙️ Method `in_thread_clean`](#%EF%B8%8F-method-in_thread_clean)
  - [⚙️ Method `in_thread_scan`](#%EF%B8%8F-method-in_thread_scan)
  - [⚙️ Method `thread_after_clean`](#%EF%B8%8F-method-thread_after_clean)
  - [⚙️ Method `thread_after_scan`](#%EF%B8%8F-method-thread_after_scan)

</details>

## 🏛️ Class `OnCleanTemporary`

```python
class OnCleanTemporary(ActionBase)
```

Offer reclaimable temp locations with sizes, then clean the selected ones.

Discovery runs in a background thread with a progress toast, then the user
picks targets on the UI thread. Deletion runs in a second background thread.

<details>
<summary>Code:</summary>

```python
class OnCleanTemporary(ActionBase):

    icon = "🧽"
    title = "Clean temporary files"
    cli_available = False

    @ActionBase.handle_exceptions("cleaning temporary files")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Scan reclaimable locations in a thread, then prompt and clean."""
        self.selected_targets: list[CleanupTarget] = []
        self._scan_found_bytes = 0
        self._toast_bridge = self._ToastBridge()
        self._toast_bridge.message_changed.connect(self._on_scan_toast_message)
        self.add_line("🔵 Scanning cleanup targets…")
        self.start_thread(self.in_thread_scan, self.thread_after_scan, self._scan_toast_message())

    @ActionBase.handle_exceptions("cleaning temporary files thread")
    def in_thread_clean(self) -> None:
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

    @ActionBase.handle_exceptions("scanning temporary files thread")
    def in_thread_scan(self) -> list[CleanupTarget]:
        """Measure reclaimable locations in a background thread."""

        def on_found(target: CleanupTarget) -> None:
            self._scan_found_bytes += target.size_bytes
            total = self._scan_found_bytes
            self.add_line(
                f"Found `{target.title}`: {h.file.format_byte_size(target.size_bytes)} "
                f"(total {h.file.format_byte_size(total)})"
            )
            self._toast_bridge.message_changed.emit(
                f"Scanning cleanup targets…\nFound (all): {h.file.format_byte_size(total)}"
            )

        targets = discover_targets(on_progress=self.add_line, on_found=on_found)
        self.add_elapsed_time()
        return targets

    @ActionBase.handle_exceptions("cleaning temporary files completion")
    def thread_after_clean(self, result: Any) -> None:  # noqa: ARG002
        """Show toast and result dialog after cleanup finishes."""
        self.show_toast(f"{self.title} completed")
        self.show_result()

    @ActionBase.handle_exceptions("scanning temporary files completion")
    def thread_after_scan(self, result: Any) -> None:
        """Show selection dialogs, then start the cleanup thread."""
        targets = result if isinstance(result, list) else []
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
        self.start_thread(self.in_thread_clean, self.thread_after_clean, self.title)

    def _on_scan_toast_message(self, message: str) -> None:
        """Update the scan countdown toast from the UI thread."""
        toast = getattr(self, "toast", None)
        if isinstance(toast, ToastCountdownNotification):
            toast.set_message(message)

    def _scan_toast_message(self) -> str:
        """Return toast text with the reclaimable total if every target is selected."""
        total = h.file.format_byte_size(self._scan_found_bytes)
        return f"Scanning cleanup targets…\nFound (all): {total}"

    class _ToastBridge(QObject):
        """Relay scan toast text from the worker thread to the UI thread."""

        message_changed = Signal(str)
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Scan reclaimable locations in a thread, then prompt and clean.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        self.selected_targets: list[CleanupTarget] = []
        self._scan_found_bytes = 0
        self._toast_bridge = self._ToastBridge()
        self._toast_bridge.message_changed.connect(self._on_scan_toast_message)
        self.add_line("🔵 Scanning cleanup targets…")
        self.start_thread(self.in_thread_scan, self.thread_after_scan, self._scan_toast_message())
```

</details>

### ⚙️ Method `in_thread_clean`

```python
def in_thread_clean(self) -> None
```

Delete selected cleanup targets in a background thread.

<details>
<summary>Code:</summary>

```python
def in_thread_clean(self) -> None:
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
```

</details>

### ⚙️ Method `in_thread_scan`

```python
def in_thread_scan(self) -> list[CleanupTarget]
```

Measure reclaimable locations in a background thread.

<details>
<summary>Code:</summary>

```python
def in_thread_scan(self) -> list[CleanupTarget]:

        def on_found(target: CleanupTarget) -> None:
            self._scan_found_bytes += target.size_bytes
            total = self._scan_found_bytes
            self.add_line(
                f"Found `{target.title}`: {h.file.format_byte_size(target.size_bytes)} "
                f"(total {h.file.format_byte_size(total)})"
            )
            self._toast_bridge.message_changed.emit(
                f"Scanning cleanup targets…\nFound (all): {h.file.format_byte_size(total)}"
            )

        targets = discover_targets(on_progress=self.add_line, on_found=on_found)
        self.add_elapsed_time()
        return targets
```

</details>

### ⚙️ Method `thread_after_clean`

```python
def thread_after_clean(self, result: Any) -> None
```

Show toast and result dialog after cleanup finishes.

<details>
<summary>Code:</summary>

```python
def thread_after_clean(self, result: Any) -> None:  # noqa: ARG002
        self.show_toast(f"{self.title} completed")
        self.show_result()
```

</details>

### ⚙️ Method `thread_after_scan`

```python
def thread_after_scan(self, result: Any) -> None
```

Show selection dialogs, then start the cleanup thread.

<details>
<summary>Code:</summary>

```python
def thread_after_scan(self, result: Any) -> None:
        targets = result if isinstance(result, list) else []
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
        self.start_thread(self.in_thread_clean, self.thread_after_clean, self.title)
```

</details>
