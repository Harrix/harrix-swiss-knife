---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `check_musicbee_playlists.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnCheckMusicBeePlaylists`](#%EF%B8%8F-class-oncheckmusicbeeplaylists)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread)
  - [⚙️ Method `thread_after`](#%EF%B8%8F-method-thread_after)

</details>

## 🏛️ Class `OnCheckMusicBeePlaylists`

```python
class OnCheckMusicBeePlaylists(ActionBase)
```

Backup MusicBee data, preview remaps and Stream rules, then apply on confirm.

Static `.mbp` playlists and `MusicBeeLibrary.mbl` paths can be rewritten so
play counts stay on the same library record. Smart `.xautopf` playlists and
files under the music folder are not modified.

<details>
<summary>Code:</summary>

```python
class OnCheckMusicBeePlaylists(ActionBase):

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
            ok_button_before_actions=True,
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
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Backup, scan, and show a preview with an Apply button when needed.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        self._plan: CheckPlan | None = None
        try:
            self._settings = load_musicbee_settings(self.config, config_path=get_config_path_str())
        except ValueError as exc:
            self.add_line(f"❌ {exc}")
            self.show_result()
            return
        self.start_thread(self.in_thread, self.thread_after, self.title)
```

</details>

### ⚙️ Method `in_thread`

```python
def in_thread(self) -> CheckPlan
```

Backup the library and compute remaps plus Stream rule diffs.

<details>
<summary>Code:</summary>

```python
def in_thread(self) -> CheckPlan:
        return run_check(self._settings)
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
            ok_button_before_actions=True,
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
```

</details>
