---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `backup_cursor.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnBackupCursor`](#%EF%B8%8F-class-onbackupcursor)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread)
  - [⚙️ Method `thread_after`](#%EF%B8%8F-method-thread_after)

</details>

## 🏛️ Class `OnBackupCursor`

```python
class OnBackupCursor(ActionBase)
```

Zip Cursor User data, home `.cursor`, and project `.cursor` folders.

Chat history lives mainly in `%APPDATA%\Cursor\User\globalStorage\state.vscdb`
(often multi-GB). Prefer quitting Cursor before packing so SQLite files are
not locked mid-write.

<details>
<summary>Code:</summary>

```python
class OnBackupCursor(ActionBase):

    icon = "💾"
    title = "Backup Cursor AI…"
    description = "Zip Cursor settings, chat history, home .cursor, and project .cursor rules."
    cli_available = True
    cli_hint = "vscode backup-cursor [--part …] [--output PATH]"
    bold_title = True

    PART_CHOICES: tuple[str, ...] = (PART_USER, PART_DOT_CURSOR, PART_EXTENSIONS, PART_PROJECT_CURSOR)
    CLI_PART_TOKENS: tuple[str, ...] = tuple(part.value for part in BackupPart)

    @ActionBase.handle_exceptions("backup Cursor")
    def execute(
        self,
        *_args: Any,
        parts: tuple[str, ...] | list[str] | None = None,
        output: str | Path | None = None,
        force: bool = False,
        noninteractive: bool = False,
        **_kwargs: Any,
    ) -> None:
        """Select parts (GUI) or use CLI flags, then pack a ZIP in a worker thread."""
        if noninteractive:
            selected = self._resolve_cli_parts(parts)
            if selected is None:
                return
            output_zip = self._resolve_output_zip(output)
        else:
            selected = self._select_parts_interactive()
            if selected is None:
                return
            output_zip = self._resolve_output_zip(None)

        if cursor_running() and not force:
            if noninteractive:
                self.add_line("❌ Cursor is running. Quit it and retry, or pass --force.")
                return
            proceed = self.get_yes_no_question(
                self.title,
                "Cursor is running. Chat databases may be locked or inconsistent.\n\nContinue anyway?",
                default_yes=False,
            )
            if not proceed:
                self.add_line("Cancelled.")
                self.show_result()
                return

        self._backup_parts = selected
        self._backup_output = output_zip
        self.start_thread(
            self.in_thread,
            self.thread_after,
            "Backing up Cursor…",
            cancellable=True,
        )

    @ActionBase.handle_exceptions("backup Cursor thread")
    def in_thread(self) -> BackupResult:
        """Pack the selected Cursor parts into the output ZIP."""
        return pack_cursor_backup(
            self._backup_output,
            self._backup_parts,
            should_cancel=self.is_work_cancelled,
        )

    @ActionBase.handle_exceptions("backup Cursor thread completion")
    def thread_after(self, result: Any) -> None:
        """Show the backup report and open the ZIP folder."""
        if not isinstance(result, BackupResult):
            self.show_result()
            return
        self.result_folder = result.zip_path.parent
        report = format_backup_report(result)
        self.add_line(report)
        self.show_toast("Cursor backup ready")
        self.show_result(display_text=report)

    def _default_output_zip(self) -> Path:
        stamp = datetime.now(UTC).astimezone().strftime("%Y%m%d-%H%M%S")
        return get_action_output_dir() / f"cursor-backup-{stamp}.zip"

    def _resolve_cli_parts(self, parts: tuple[str, ...] | list[str] | None) -> list[BackupPart] | None:
        tokens = [str(token).strip().casefold() for token in (parts or ()) if str(token).strip()]
        if not tokens:
            return list(DEFAULT_PARTS)
        selected: list[BackupPart] = []
        for token in tokens:
            match = next((part for part in BackupPart if part.value == token), None)
            if match is None:
                supported = ", ".join(self.CLI_PART_TOKENS)
                self.add_line(f'❌ Unknown part "{token}". Supported: {supported}.')
                return None
            if match not in selected:
                selected.append(match)
        return selected

    def _resolve_output_zip(self, output: str | Path | None) -> Path:
        if output is None or str(output).strip() == "":
            return self._default_output_zip()
        path = Path(output).expanduser()
        if path.suffix.casefold() != ".zip":
            path = path.with_suffix(".zip")
        return path.resolve()

    def _select_parts_interactive(self) -> list[BackupPart] | None:
        """Show part checkboxes with sizes; return selected parts or `None`."""
        sizes = estimate_part_sizes()
        choice_sizes = {PART_LABELS[part]: sizes.get(part, 0) for part in BackupPart}
        missing: list[str] = []
        if not cursor_user_dir().is_dir():
            missing.append(PART_USER)
        if not cursor_dot_dir().is_dir():
            missing.extend([PART_DOT_CURSOR, PART_EXTENSIONS])
        default_labels = [PART_LABELS[part] for part in DEFAULT_PARTS if PART_LABELS[part] not in missing]
        selected = self.get_checkbox_selection(
            self.title,
            "Choose what to include. Chat history is inside Cursor User "
            f"(`{cursor_user_dir() / 'globalStorage' / 'state.vscdb'}`).",
            list(self.PART_CHOICES),
            default_selected=default_labels,
            disabled_choices=missing or None,
            choice_sizes=choice_sizes,
        )
        if selected is None:
            self.add_line("Cancelled.")
            self.show_result()
            return None
        parts = parts_from_labels(selected)
        if not parts:
            self.add_line("❌ Select at least one part.")
            self.show_result()
            return None
        return parts
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *_args: Any, parts: tuple[str, ...] | list[str] | None = None, output: str | Path | None = None, force: bool = False, noninteractive: bool = False, **_kwargs: Any) -> None
```

Select parts (GUI) or use CLI flags, then pack a ZIP in a worker thread.

<details>
<summary>Code:</summary>

```python
def execute(
        self,
        *_args: Any,
        parts: tuple[str, ...] | list[str] | None = None,
        output: str | Path | None = None,
        force: bool = False,
        noninteractive: bool = False,
        **_kwargs: Any,
    ) -> None:
        if noninteractive:
            selected = self._resolve_cli_parts(parts)
            if selected is None:
                return
            output_zip = self._resolve_output_zip(output)
        else:
            selected = self._select_parts_interactive()
            if selected is None:
                return
            output_zip = self._resolve_output_zip(None)

        if cursor_running() and not force:
            if noninteractive:
                self.add_line("❌ Cursor is running. Quit it and retry, or pass --force.")
                return
            proceed = self.get_yes_no_question(
                self.title,
                "Cursor is running. Chat databases may be locked or inconsistent.\n\nContinue anyway?",
                default_yes=False,
            )
            if not proceed:
                self.add_line("Cancelled.")
                self.show_result()
                return

        self._backup_parts = selected
        self._backup_output = output_zip
        self.start_thread(
            self.in_thread,
            self.thread_after,
            "Backing up Cursor…",
            cancellable=True,
        )
```

</details>

### ⚙️ Method `in_thread`

```python
def in_thread(self) -> BackupResult
```

Pack the selected Cursor parts into the output ZIP.

<details>
<summary>Code:</summary>

```python
def in_thread(self) -> BackupResult:
        return pack_cursor_backup(
            self._backup_output,
            self._backup_parts,
            should_cancel=self.is_work_cancelled,
        )
```

</details>

### ⚙️ Method `thread_after`

```python
def thread_after(self, result: Any) -> None
```

Show the backup report and open the ZIP folder.

<details>
<summary>Code:</summary>

```python
def thread_after(self, result: Any) -> None:
        if not isinstance(result, BackupResult):
            self.show_result()
            return
        self.result_folder = result.zip_path.parent
        report = format_backup_report(result)
        self.add_line(report)
        self.show_toast("Cursor backup ready")
        self.show_result(display_text=report)
```

</details>
