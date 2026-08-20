---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `build_install_zips.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnBuildInstallZips`](#%EF%B8%8F-class-onbuildinstallzips)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread)
  - [⚙️ Method `thread_after`](#%EF%B8%8F-method-thread_after)

</details>

## 🏛️ Class `OnBuildInstallZips`

```python
class OnBuildInstallZips(ActionBase)
```

Build `install/` GUI installer EXEs with selectable steps.

Shows checkboxes for wipe, binaries, installers, repo snapshots, uv cache,
EXE packing, open folder, and log cleanup. From the tray the pipeline runs
in a worker thread and logs here like other actions. Uv cache uses an isolated
Python/venv so the live `.venv` can stay locked. Target PCs run
`harrix-swiss-knife-online.exe` or `harrix-swiss-knife-offline.exe`
(PySide6 wizard; no Python on the target).

<details>
<summary>Code:</summary>

```python
class OnBuildInstallZips(ActionBase):

    icon = "🚀"
    title = "Build installer EXEs"
    cli_available = True
    cli_hint = "dev build-install-zips"

    @ActionBase.handle_exceptions("build installer EXEs")
    def execute(self, *args: Any, noninteractive: bool = False, **kwargs: Any) -> None:  # noqa: ARG002
        """Run selected installer-EXE builder steps."""
        if sys.platform != "win32":
            self.add_line("❌ This action is only available on Windows.")
            if not noninteractive:
                self.show_result()
            return

        project_root = get_project_root()
        install_path = install_dir(project_root)
        install_path.mkdir(parents=True, exist_ok=True)

        steps = self._resolve_steps(project_root, noninteractive=noninteractive, **kwargs)
        if steps is None:
            self.add_line("Cancelled.")
            if not noninteractive:
                self.show_result()
            return
        if not steps.any_work() and not steps.open_install:
            self.add_line("❌ No steps selected.")
            if not noninteractive:
                self.show_result()
            return

        self._steps = steps
        self._project_root = project_root
        self._noninteractive = noninteractive

        if noninteractive:
            self._run_in_process()
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("build installer EXEs thread")
    def in_thread(self) -> PipelineResult:
        """Run the builder in a worker thread; lines go to the usual output."""
        return run_pipeline(
            self._project_root,
            self._steps,
            config=dict(self.config),
            log=self.add_line,
        )

    @ActionBase.handle_exceptions("build installer EXEs thread completion")
    def thread_after(self, result: Any) -> None:
        """Show toast and the result window after the worker finishes."""
        ok = isinstance(result, PipelineResult) and result.ok
        self.show_toast("Installer EXEs built" if ok else "Installer EXE build finished (see output)")
        self.show_result()

    def _resolve_steps(self, project_root: Path, *, noninteractive: bool, **kwargs: Any) -> BuildSteps | None:
        if noninteractive or kwargs.get("steps") is not None:
            raw = kwargs.get("steps")
            if isinstance(raw, BuildSteps):
                return raw
            return steps_from_cli_flags(
                no_wipe=bool(kwargs.get("no_wipe")),
                skip_binaries=bool(kwargs.get("skip_binaries")),
                skip_installers=bool(kwargs.get("skip_installers")),
                skip_repos=bool(kwargs.get("skip_repos")),
                skip_uv_cache=bool(kwargs.get("skip_uv_cache")),
                no_zips=bool(kwargs.get("no_zips")),
                no_exes=bool(kwargs.get("no_exes")),
                no_open=bool(kwargs.get("no_open")),
                clean_logs=bool(kwargs.get("clean_logs")),
            )

        tray_defaults = default_tray_step_labels(project_root)
        quick = tray_defaults != list(DEFAULT_STEP_LABELS)
        label = (
            "Select builder steps. Output is logged here like other actions.\n"
            "Full rebuild (uv cache) can take tens of minutes; quick rebuild re-packs EXEs in minutes.\n"
            "Existing files under install/dependencies are reused (presence only — not version-checked)."
        )
        if quick:
            label += "\nDefaults: quick rebuild (existing install/dependencies detected)."
        else:
            label += "\nDefaults: full rebuild (dependencies missing or empty)."
        selected = self.get_checkbox_selection(
            self.title,
            label,
            list(ALL_STEP_LABELS),
            tray_defaults,
            selection_presets=[
                ("⚡ Quick rebuild", list(QUICK_REBUILD_STEP_LABELS)),
                ("🐢 Full rebuild (slow)", list(FULL_REBUILD_STEP_LABELS)),
            ],
        )
        if selected is None:
            return None
        return BuildSteps.from_labels(selected)

    def _run_in_process(self) -> None:
        result = run_pipeline(
            self._project_root,
            self._steps,
            config=dict(self.config),
            log=self.add_line,
        )
        if not result.ok:
            # CLI failure is detected via ❌ lines in result_lines.
            pass
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, noninteractive: bool = False, **kwargs: Any) -> None
```

Run selected installer-EXE builder steps.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, noninteractive: bool = False, **kwargs: Any) -> None:  # noqa: ARG002
        if sys.platform != "win32":
            self.add_line("❌ This action is only available on Windows.")
            if not noninteractive:
                self.show_result()
            return

        project_root = get_project_root()
        install_path = install_dir(project_root)
        install_path.mkdir(parents=True, exist_ok=True)

        steps = self._resolve_steps(project_root, noninteractive=noninteractive, **kwargs)
        if steps is None:
            self.add_line("Cancelled.")
            if not noninteractive:
                self.show_result()
            return
        if not steps.any_work() and not steps.open_install:
            self.add_line("❌ No steps selected.")
            if not noninteractive:
                self.show_result()
            return

        self._steps = steps
        self._project_root = project_root
        self._noninteractive = noninteractive

        if noninteractive:
            self._run_in_process()
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)
```

</details>

### ⚙️ Method `in_thread`

```python
def in_thread(self) -> PipelineResult
```

Run the builder in a worker thread; lines go to the usual output.

<details>
<summary>Code:</summary>

```python
def in_thread(self) -> PipelineResult:
        return run_pipeline(
            self._project_root,
            self._steps,
            config=dict(self.config),
            log=self.add_line,
        )
```

</details>

### ⚙️ Method `thread_after`

```python
def thread_after(self, result: Any) -> None
```

Show toast and the result window after the worker finishes.

<details>
<summary>Code:</summary>

```python
def thread_after(self, result: Any) -> None:
        ok = isinstance(result, PipelineResult) and result.ok
        self.show_toast("Installer EXEs built" if ok else "Installer EXE build finished (see output)")
        self.show_result()
```

</details>
