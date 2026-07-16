"""Actions for Python development and code management."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from harrix_swiss_knife.actions.base import ActionBase
from harrix_swiss_knife.actions.python.python_project_checks import PythonProjectChecksMixin


class OnCheckPythonProjects(PythonProjectChecksMixin):
    """Run ty, ruff, pytest, Harrix PY and MD checks for all paths_python_projects."""

    icon = "✅"
    title = "Full PY check all projects"
    cli_available = True
    cli_hint = "py check-all"

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
            self.add_line(f"\n=== {project_path.name} ({project_path}) ===")
            project_failures = self.check_single_python_project(project_path)
            if project_failures:
                failed_projects[project_path.name] = project_failures

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
