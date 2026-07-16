"""Actions for Python development and code management."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any, ClassVar

import harrix_pylib as h

from harrix_swiss_knife.actions.base import ActionBase
from harrix_swiss_knife.actions.markdown.check_md_folder import OnCheckMdFolder
from harrix_swiss_knife.actions.python.check_python_folder import OnCheckPythonFolder


class OnCheckPythonProjects(ActionBase):
    """Run ty, ruff, pytest, Harrix PY and MD checks for all paths_python_projects."""

    icon = "✅"
    title = "Full PY check all projects"
    cli_available = True
    cli_hint = "py check-all"

    _UV_CHECKS: ClassVar[tuple[tuple[str, str], ...]] = (
        ("ty", "check"),
        ("ruff", "check"),
        ("pytest", ""),
    )

    def check_all_python_projects_common(self) -> None:
        """Run ty, ruff, pytest, and Harrix Python/Markdown checks for each configured project."""
        raw = self.config.get("paths_python_projects")
        if not isinstance(raw, list):
            self.add_line('❌ config "paths_python_projects" must be a list.')
            return

        project_paths: list[Path] = []
        for entry in raw:
            path = Path(str(entry)).expanduser()
            try:
                resolved = path.resolve()
            except OSError:
                self.add_line(f"⚠️ Could not resolve path: {entry}")
                continue
            if not resolved.is_dir():
                self.add_line(f"⚠️ Skip (not a directory): {resolved}")
                continue
            project_paths.append(resolved)

        if not project_paths:
            self.add_line("❌ No valid project paths in paths_python_projects.")
            return

        failed_projects: dict[str, list[str]] = {}

        for project_path in project_paths:
            project_name = project_path.name
            self.add_line(f"\n=== {project_name} ({project_path}) ===")
            project_failures: list[str] = []

            for tool, args in self._UV_CHECKS:
                label = f"{tool} {args}".strip()
                self.add_line(f"🔵 [{project_name}] {label}")
                ok, output = self._run_uv_command(project_path, tool, args)
                if output:
                    self.add_line(output)
                if ok:
                    self.add_line(f"✅ {label} passed")
                else:
                    self.add_line(f"❌ {label} failed")
                    project_failures.append(label)

            self.add_line(f"🔵 [{project_name}] Harrix python check")
            if self._run_harrix_python_check(project_path):
                self.add_line("✅ Harrix python check passed")
            else:
                self.add_line("❌ Harrix python check failed")
                project_failures.append("Harrix python check")

            self.add_line(f"🔵 [{project_name}] Harrix markdown check")
            if self._run_harrix_markdown_check(project_path):
                self.add_line("✅ Harrix markdown check passed")
            else:
                self.add_line("❌ Harrix markdown check failed")
                project_failures.append("Harrix markdown check")

            if project_failures:
                failed_projects[project_name] = project_failures

        passed_count = len(project_paths) - len(failed_projects)
        total_count = len(project_paths)
        if not failed_projects:
            self.add_line(f"\n✅ All projects passed all checks ({passed_count}/{total_count}).")
            return

        self.add_line(f"\n❌ Checks failed in {len(failed_projects)} project(s):")
        for name, failures in failed_projects.items():
            self.add_line(f"- {name}: {', '.join(failures)}")

    @ActionBase.handle_exceptions("checking all Python projects")
    def execute(self, *_args: Any, noninteractive: bool = False, **_kwargs: Any) -> None:
        """Run full Python checks for each path in paths_python_projects."""
        if noninteractive:
            self.add_line("🔵 Starting full PY checks for all projects")
            self.check_all_python_projects_common()
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("checking all Python projects thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        self.check_all_python_projects_common()

    @ActionBase.handle_exceptions("checking all Python projects thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} completed")
        self.show_result()

    def _run_harrix_markdown_check(self, project_path: Path) -> bool:
        checker = OnCheckMdFolder()
        checker.folder_path = project_path
        checker.selected_rule_ids = set(h.md_check.MarkdownChecker().all_rules)
        checker.check_md_folder_common()
        return not any("🔢 Count errors" in line for line in checker.result_lines)

    def _run_harrix_python_check(self, project_path: Path) -> bool:
        checker = OnCheckPythonFolder()
        checker.folder_path = project_path
        checker.check_python_folder_common()
        # checker's add_line writes to this action's output via thread-local file override
        return not any("🔢 Count errors" in line for line in checker.result_lines)

    def _run_uv_command(self, project_path: Path, tool: str, args: str) -> tuple[bool, str]:
        pyproject = project_path / "pyproject.toml"
        if not pyproject.is_file():
            return False, f"❌ Missing pyproject.toml in {project_path}"

        venv_dir = project_path / ".venv"
        if not venv_dir.is_dir():
            return False, f"❌ Missing .venv in {project_path}"

        command = ["uv", "run", tool, *args.split()]
        env = os.environ.copy()
        env.pop("VIRTUAL_ENV", None)
        try:
            process = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding="utf-8",
                cwd=project_path,
                env=env,
                check=False,
            )
        except Exception as e:
            return False, f"Error executing command: {e!s}"

        output_parts = [(process.stdout or "").strip(), (process.stderr or "").strip()]
        output = "\n".join(filter(None, output_parts))
        return process.returncode == 0, output
