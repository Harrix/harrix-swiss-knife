---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `sync_chrome_yandex_bookmarks.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnSyncChromeYandexBookmarks`](#%EF%B8%8F-class-onsyncchromeyandexbookmarks)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread)
  - [⚙️ Method `thread_after`](#%EF%B8%8F-method-thread_after)

</details>

## 🏛️ Class `OnSyncChromeYandexBookmarks`

```python
class OnSyncChromeYandexBookmarks(ActionBase)
```

Bidirectional Chrome ↔ Yandex bookmark sync with a deletion-aware snapshot.

First run merges missing URLs both ways without deletions. Later runs use a
LocalAppData snapshot so deletes propagate. Preview shows Apply / Cancel;
browsers must be closed before Apply.

<details>
<summary>Code:</summary>

```python
class OnSyncChromeYandexBookmarks(ActionBase):

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
        )
        if not isinstance(shown, tuple) or shown[1] != RERUN_DIALOG_CODE:
            return
        still_running = running_browser_names()
        if still_running:
            names = ", ".join(still_running)
            message = f"Close {names}, then run Sync Chrome and Yandex bookmarks again."
            self.add_line(message)
            self.show_result(display_text=message)
            return
        written = apply_sync_plan(result)
        if result.backup_path is not None:
            self.result_folder = result.backup_path
        summary = "\n".join(["Applied:", *[str(path) for path in written]])
        self.add_line(summary)
        self.show_toast("Bookmarks synced")
        self.show_result(display_text=f"{report}\n\n{summary}")
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Scan Bookmarks files and show a preview with Apply when needed.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        self._plan: SyncPlan | None = None
        self.start_thread(self.in_thread, self.thread_after, self.title)
```

</details>

### ⚙️ Method `in_thread`

```python
def in_thread(self) -> SyncPlan
```

Build the sync plan from both Bookmarks files and the snapshot.

<details>
<summary>Code:</summary>

```python
def in_thread(self) -> SyncPlan:
        return build_sync_plan()
```

</details>

### ⚙️ Method `thread_after`

```python
def thread_after(self, result: Any) -> None
```

Show the preview report and apply writes when the user confirms.

<details>
<summary>Code:</summary>

```python
def thread_after(self, result: Any) -> None:
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
        )
        if not isinstance(shown, tuple) or shown[1] != RERUN_DIALOG_CODE:
            return
        still_running = running_browser_names()
        if still_running:
            names = ", ".join(still_running)
            message = f"Close {names}, then run Sync Chrome and Yandex bookmarks again."
            self.add_line(message)
            self.show_result(display_text=message)
            return
        written = apply_sync_plan(result)
        if result.backup_path is not None:
            self.result_folder = result.backup_path
        summary = "\n".join(["Applied:", *[str(path) for path in written]])
        self.add_line(summary)
        self.show_toast("Bookmarks synced")
        self.show_result(display_text=f"{report}\n\n{summary}")
```

</details>
