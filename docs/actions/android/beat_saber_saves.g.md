---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `beat_saber_saves.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnBeatSaberSaves`](#%EF%B8%8F-class-onbeatsabersaves)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread)
  - [⚙️ Method `thread_after`](#%EF%B8%8F-method-thread_after)

</details>

## 🏛️ Class `OnBeatSaberSaves`

```python
class OnBeatSaberSaves(ActionBase)
```

Export or import Beat Saber ranks / campaign progress.

Local ranks (C — SS), campaign progress, and related files live in
`PlayerData.dat` (and sibling `.dat` / `settings.cfg`). Online leaderboard
scores stay on Beat Games servers; this action backs up the local files.

- **PC** — `%USERPROFILE%\AppData\LocalLow\Hyperbolic Magnetism\Beat Saber`
- **Quest** — `/sdcard/Android/data/com.beatgames.beatsaber/files` via `adb`

Exports go to `{path_backups}/BeatSaber/beat-saber-YYYYMMDD-HHMMSS.zip`.

<details>
<summary>Code:</summary>

```python
class OnBeatSaberSaves(ActionBase):

    icon = "🎮"
    title = "Beat Saber saves…"
    description = "Export or import Beat Saber local ranks/progress (PC or Quest)."
    cli_available = True
    cli_hint = "android beat-saber-saves export|import pc|quest [--zip PATH]"
    bold_title = True

    CHOICE_EXPORT: ClassVar[str] = "Export"
    CHOICE_IMPORT: ClassVar[str] = "Import"
    CHOICE_PC: ClassVar[str] = "PC"
    CHOICE_QUEST: ClassVar[str] = "Quest (Meta headset)"

    _job_mode: str = ""
    _job_source: str = ""
    _job_zip: Path | None = None
    _job_serial: str | None = None
    _job_adb: Path | None = None

    @ActionBase.handle_exceptions("Beat Saber saves")
    def execute(
        self,
        *_args: Any,
        mode: str | None = None,
        source: str | None = None,
        zip_path: str | Path | None = None,
        noninteractive: bool = False,
        **_kwargs: Any,
    ) -> None:
        """Choose export/import and PC/Quest, then run the transfer."""
        if sys.platform != "win32":
            self.add_line("❌ This action is only available on Windows.")
            if not noninteractive:
                self.show_result()
            return

        resolved_mode = self._resolve_mode(mode, noninteractive=noninteractive)
        if resolved_mode is None:
            return
        resolved_source = self._resolve_source(source, noninteractive=noninteractive)
        if resolved_source is None:
            return

        adb: Path | None = None
        serial: str | None = None
        if resolved_source == "quest":
            picked = self._resolve_quest_device(noninteractive=noninteractive)
            if picked is None:
                return
            adb, serial = picked

        if resolved_mode == "export":
            out_zip = self._resolve_export_zip(zip_path, noninteractive=noninteractive)
            if out_zip is None:
                return
        else:
            out_zip = self._resolve_import_zip(zip_path, noninteractive=noninteractive)
            if out_zip is None:
                return
            if not self._confirm_import(resolved_source, out_zip, noninteractive=noninteractive):
                return

        self._job_mode = resolved_mode
        self._job_source = resolved_source
        self._job_zip = out_zip
        self._job_adb = adb
        self._job_serial = serial

        toast = "Exporting Beat Saber saves…" if resolved_mode == "export" else "Importing Beat Saber saves…"
        if noninteractive:
            result = self._run_transfer()
            self._report_result(result)
            return

        self.start_thread(self.in_thread, self.thread_after, toast, cancellable=True)

    @ActionBase.handle_exceptions("Beat Saber saves thread")
    def in_thread(self) -> BeatSaberTransferResult:
        """Run export/import in a worker thread."""
        return self._run_transfer()

    @ActionBase.handle_exceptions("Beat Saber saves thread completion")
    def thread_after(self, result: Any) -> None:
        """Show the transfer report."""
        if isinstance(result, BeatSaberTransferResult):
            self._report_result(result)
            return
        self.show_result()

    def _confirm_import(self, source: str, zip_path: Path, *, noninteractive: bool) -> bool:
        if noninteractive:
            return True
        target = f"PC folder `{pc_saves_dir()}`" if source == "pc" else "Quest Beat Saber files"
        proceed = self.get_yes_no_question(
            self.title,
            f"Overwrite existing Beat Saber saves on {target} with `{zip_path.name}`?\n\n"
            "Quit Beat Saber first so files are not locked.",
            default_yes=False,
        )
        if not proceed:
            self.add_line("Cancelled.")
            self.show_result()
            return False
        return True

    def _device_label(self, adb: Path, serial: str) -> str:
        model = adb_shell_getprop(adb, serial, "ro.product.model")
        if model:
            return f"{model} ({serial})"
        return serial

    def _report_result(self, result: BeatSaberTransferResult) -> None:
        for line in result.lines:
            self.add_line(line)
        if result.ok:
            self.add_line(f"✅ {result.message}")
            if result.zip_path is not None:
                self.result_folder = result.zip_path.parent
            self.show_toast("Beat Saber saves ready" if result.mode == "export" else "Beat Saber saves restored")
        else:
            self.add_line(f"❌ {result.message}")
            self.show_toast("Beat Saber saves failed")
        self.show_result()

    def _resolve_export_zip(self, zip_path: str | Path | None, *, noninteractive: bool) -> Path | None:
        if zip_path is not None:
            return Path(zip_path)
        if noninteractive:
            return default_export_zip_path(self.config)
        return default_export_zip_path(self.config)

    def _resolve_import_zip(self, zip_path: str | Path | None, *, noninteractive: bool) -> Path | None:
        if zip_path is not None:
            path = Path(zip_path)
            if not path.is_file():
                self.add_line(f"❌ ZIP not found: `{path}`")
                if not noninteractive:
                    self.show_result()
                return None
            return path
        if noninteractive:
            self.add_line("❌ Import requires `--zip PATH`.")
            return None
        chosen = self.get_open_filename(
            "Select Beat Saber backup ZIP",
            str(default_export_zip_path(self.config).parent),
            "ZIP archives (*.zip)",
        )
        if chosen is None:
            self.add_line("Cancelled.")
            self.show_result()
            return None
        return chosen

    def _resolve_mode(self, mode: str | None, *, noninteractive: bool) -> str | None:
        if mode:
            key = str(mode).strip().lower()
            if key in {"export", "import"}:
                return key
            self.add_line("❌ Mode must be `export` or `import`.")
            if not noninteractive:
                self.show_result()
            return None
        if noninteractive:
            self.add_line("❌ CLI requires `export` or `import`.")
            return None
        chosen = self.get_choice_from_list_with_descriptions(
            self.title,
            "Export packs a ZIP; import restores from a ZIP.",
            [
                (self.CHOICE_EXPORT, "Copy local saves into `{path_backups}/BeatSaber/`."),
                (self.CHOICE_IMPORT, "Overwrite local saves from a ZIP backup."),
            ],
        )
        if chosen is None:
            self.add_line("Cancelled.")
            self.show_result()
            return None
        return "export" if chosen == self.CHOICE_EXPORT else "import"

    def _resolve_quest_device(self, *, noninteractive: bool) -> tuple[Path, str] | None:
        adb = resolve_adb()
        if adb is None:
            self.add_line(f"❌ adb not found. {ANDROID_SDK_SETUP_HINT}")
            if not noninteractive:
                self.show_result()
            return None
        authorized, unauthorized, output = list_adb_device_states(adb)
        if output:
            self.add_line(output)
        if unauthorized and not authorized:
            self.add_line("❌ Headset connected but unauthorized — allow USB debugging on the Quest.")
            if not noninteractive:
                self.show_result()
            return None
        if not authorized:
            self.add_line("❌ No authorized adb devices. Connect the Quest with USB debugging enabled.")
            if not noninteractive:
                self.show_result()
            return None
        if len(authorized) == 1 or noninteractive:
            return adb, authorized[0]
        labels = [self._device_label(adb, serial) for serial in authorized]
        chosen = self.get_choice_from_list(self.title, "Select Meta Quest / adb device:", labels)
        if chosen is None:
            self.add_line("Cancelled.")
            self.show_result()
            return None
        index = labels.index(chosen)
        return adb, authorized[index]

    def _resolve_source(self, source: str | None, *, noninteractive: bool) -> str | None:
        if source:
            key = str(source).strip().lower()
            if key in {"pc", "quest"}:
                return key
            self.add_line("❌ Source must be `pc` or `quest`.")
            if not noninteractive:
                self.show_result()
            return None
        if noninteractive:
            self.add_line("❌ CLI requires `pc` or `quest`.")
            return None
        chosen = self.get_choice_from_list_with_descriptions(
            self.title,
            "Where are the Beat Saber saves?",
            [
                (self.CHOICE_PC, f"Windows LocalLow folder (`{pc_saves_dir()}`)."),
                (self.CHOICE_QUEST, "Meta Quest via USB + adb (PlayerData.dat and related)."),
            ],
        )
        if chosen is None:
            self.add_line("Cancelled.")
            self.show_result()
            return None
        return "pc" if chosen == self.CHOICE_PC else "quest"

    def _run_transfer(self) -> BeatSaberTransferResult:
        zip_path = self._job_zip
        if zip_path is None:
            return BeatSaberTransferResult(
                ok=False, mode=self._job_mode, source=self._job_source, message="No ZIP path."
            )
        if self._job_source == "pc":
            if self._job_mode == "export":
                return export_pc_saves(zip_path, should_cancel=self.is_work_cancelled)
            return import_pc_saves(zip_path, should_cancel=self.is_work_cancelled)

        adb = self._job_adb
        serial = self._job_serial
        if adb is None or serial is None:
            return BeatSaberTransferResult(
                ok=False,
                mode=self._job_mode,
                source="quest",
                message="No adb device selected.",
            )
        if self._job_mode == "export":
            return export_quest_saves(adb, serial, zip_path, should_cancel=self.is_work_cancelled)
        return import_quest_saves(adb, serial, zip_path, should_cancel=self.is_work_cancelled)
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *_args: Any, mode: str | None = None, source: str | None = None, zip_path: str | Path | None = None, noninteractive: bool = False, **_kwargs: Any) -> None
```

Choose export/import and PC/Quest, then run the transfer.

<details>
<summary>Code:</summary>

```python
def execute(
        self,
        *_args: Any,
        mode: str | None = None,
        source: str | None = None,
        zip_path: str | Path | None = None,
        noninteractive: bool = False,
        **_kwargs: Any,
    ) -> None:
        if sys.platform != "win32":
            self.add_line("❌ This action is only available on Windows.")
            if not noninteractive:
                self.show_result()
            return

        resolved_mode = self._resolve_mode(mode, noninteractive=noninteractive)
        if resolved_mode is None:
            return
        resolved_source = self._resolve_source(source, noninteractive=noninteractive)
        if resolved_source is None:
            return

        adb: Path | None = None
        serial: str | None = None
        if resolved_source == "quest":
            picked = self._resolve_quest_device(noninteractive=noninteractive)
            if picked is None:
                return
            adb, serial = picked

        if resolved_mode == "export":
            out_zip = self._resolve_export_zip(zip_path, noninteractive=noninteractive)
            if out_zip is None:
                return
        else:
            out_zip = self._resolve_import_zip(zip_path, noninteractive=noninteractive)
            if out_zip is None:
                return
            if not self._confirm_import(resolved_source, out_zip, noninteractive=noninteractive):
                return

        self._job_mode = resolved_mode
        self._job_source = resolved_source
        self._job_zip = out_zip
        self._job_adb = adb
        self._job_serial = serial

        toast = "Exporting Beat Saber saves…" if resolved_mode == "export" else "Importing Beat Saber saves…"
        if noninteractive:
            result = self._run_transfer()
            self._report_result(result)
            return

        self.start_thread(self.in_thread, self.thread_after, toast, cancellable=True)
```

</details>

### ⚙️ Method `in_thread`

```python
def in_thread(self) -> BeatSaberTransferResult
```

Run export/import in a worker thread.

<details>
<summary>Code:</summary>

```python
def in_thread(self) -> BeatSaberTransferResult:
        return self._run_transfer()
```

</details>

### ⚙️ Method `thread_after`

```python
def thread_after(self, result: Any) -> None
```

Show the transfer report.

<details>
<summary>Code:</summary>

```python
def thread_after(self, result: Any) -> None:
        if isinstance(result, BeatSaberTransferResult):
            self._report_result(result)
            return
        self.show_result()
```

</details>
