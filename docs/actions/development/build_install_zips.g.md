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

</details>

## 🏛️ Class `OnBuildInstallZips`

```python
class OnBuildInstallZips(ActionBase)
```

Build `install/` zip bundles with selectable steps.

Shows checkboxes for wipe, binaries, installers, repo snapshots, uv cache,
zip packing, open folder, and log cleanup. When run from the tray, the
pipeline starts in a **new console** so you can Exit this app if uv cache
needs to replace `.venv` files. Target-PC payload stays PowerShell
(`install.bat` / `harrix-swiss-knife.ps1`).

<details>
<summary>Code:</summary>

```python
class OnBuildInstallZips(ActionBase):

    icon = "🚀"
    title = "Build install zips"
    cli_available = True
    cli_hint = "dev build-install-zips"

    @ActionBase.handle_exceptions("build install zips")
    def execute(self, *args: Any, noninteractive: bool = False, **kwargs: Any) -> None:  # noqa: ARG002
        """Run selected install-zip builder steps."""
        if sys.platform != "win32":
            self.add_line("❌ This action is only available on Windows.")
            if not noninteractive:
                self.show_result()
            return

        project_root = get_project_root()
        install_path = install_dir(project_root)
        if not install_path.is_dir():
            self.add_line(f"❌ install folder not found: {install_path}")
            if not noninteractive:
                self.show_result()
            return

        steps = self._resolve_steps(noninteractive=noninteractive, **kwargs)
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

        if steps.uv_cache and not noninteractive:
            self.add_line(
                "ℹ️ uv cache is selected: the build runs in a new console. "
                "You can Exit this app if prompted about `.venv` locks."
            )

        if noninteractive:
            self._run_in_process(interactive=False)
            return

        # Tray: always use a new console so Exit is safe during uv cache.
        self._spawn_console()

    def _resolve_steps(self, *, noninteractive: bool, **kwargs: Any) -> BuildSteps | None:
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
                no_open=bool(kwargs.get("no_open")),
                clean_logs=bool(kwargs.get("clean_logs")),
            )

        label = (
            "Select builder steps. "
            f"If «{STEP_UV_CACHE}» is on, quit this app when the console asks "
            "(uv cannot replace `.venv` while the tray holds it)."
        )
        selected = self.get_checkbox_selection(
            self.title,
            label,
            list(ALL_STEP_LABELS),
            list(DEFAULT_STEP_LABELS),
        )
        if selected is None:
            return None
        return BuildSteps.from_labels(selected)

    def _run_in_process(self, *, interactive: bool) -> None:
        result = run_pipeline(
            self._project_root,
            self._steps,
            config=dict(self.config),
            interactive=interactive,
            log=self.add_line,
        )
        if not self._noninteractive:
            if result.ok:
                self.show_toast("Install zips built")
            else:
                self.show_toast("Install zip build finished (see output)")
            self.show_result()
        elif not result.ok:
            # CLI failure is detected via ❌ lines in result_lines.
            pass

    def _spawn_console(self) -> None:
        try:
            proc = spawn_pipeline_console(self._project_root, self._steps)
        except OSError as exc:
            self.add_line(f"❌ Failed to start console pipeline: {exc}")
            self.show_result()
            return
        self.add_line(f"$ python -c <install_zip_builder> (PID {proc.pid})")
        self.add_line(f"Working directory: {self._project_root}")
        self.add_line("Pipeline continues in the new console window.")
        self.show_toast("Install zip build started in console")
        self.show_result()
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, noninteractive: bool = False, **kwargs: Any) -> None
```

Run selected install-zip builder steps.

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
        if not install_path.is_dir():
            self.add_line(f"❌ install folder not found: {install_path}")
            if not noninteractive:
                self.show_result()
            return

        steps = self._resolve_steps(noninteractive=noninteractive, **kwargs)
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

        if steps.uv_cache and not noninteractive:
            self.add_line(
                "ℹ️ uv cache is selected: the build runs in a new console. "
                "You can Exit this app if prompted about `.venv` locks."
            )

        if noninteractive:
            self._run_in_process(interactive=False)
            return

        # Tray: always use a new console so Exit is safe during uv cache.
        self._spawn_console()
```

</details>
