"""Build online/offline install zip archives via a selectable Python pipeline."""

from __future__ import annotations

import sys
from typing import Any

from harrix_swiss_knife.actions.common.base import ActionBase
from harrix_swiss_knife.actions.common.install_zip_builder import (
    ALL_STEP_LABELS,
    DEFAULT_STEP_LABELS,
    BuildSteps,
    PipelineResult,
    install_dir,
    run_pipeline,
    steps_from_cli_flags,
)
from harrix_swiss_knife.paths import get_project_root


class OnBuildInstallZips(ActionBase):
    """Build `install/` zip bundles with selectable steps.

    Shows checkboxes for wipe, binaries, installers, repo snapshots, uv cache,
    zip packing, open folder, and log cleanup. From the tray the pipeline runs
    in a worker thread and logs here like other actions. Uv cache uses an isolated
    Python/venv so the live `.venv` can stay locked. Target-PC payload stays
    PowerShell (`install.bat` / `harrix-swiss-knife.ps1`).

    """

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

        if noninteractive:
            self._run_in_process()
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("build install zips thread")
    def in_thread(self) -> PipelineResult:
        """Run the builder in a worker thread; lines go to the usual output."""
        return run_pipeline(
            self._project_root,
            self._steps,
            config=dict(self.config),
            log=self.add_line,
        )

    @ActionBase.handle_exceptions("build install zips thread completion")
    def thread_after(self, result: Any) -> None:
        """Show toast and the result window after the worker finishes."""
        ok = isinstance(result, PipelineResult) and result.ok
        self.show_toast("Install zips built" if ok else "Install zip build finished (see output)")
        self.show_result()

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

        label = "Select builder steps. Output is logged here like other actions."
        selected = self.get_checkbox_selection(
            self.title,
            label,
            list(ALL_STEP_LABELS),
            list(DEFAULT_STEP_LABELS),
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
