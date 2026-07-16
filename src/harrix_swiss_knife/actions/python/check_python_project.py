"""Actions for Python development and code management."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from harrix_swiss_knife.actions.base import ActionBase
from harrix_swiss_knife.actions.python.python_project_checks import PythonProjectChecksMixin


class OnCheckPythonProject(PythonProjectChecksMixin):
    """Run ty, ruff, pytest, Harrix PY and MD checks for one project folder."""

    icon = "🔎"
    title = "Full PY check in …"
    cli_available = True
    cli_hint = "py check-project"

    def check_python_project_common(self) -> None:
        """Run ty, ruff, pytest, and Harrix Python/Markdown checks for ``folder_path``."""
        if self.folder_path is None:
            return

        project_path = Path(self.folder_path).resolve()
        if not project_path.is_dir():
            self.add_line(f"❌ Not a directory: {project_path}")
            return

        self.add_line(f"\n=== {project_path.name} ({project_path}) ===")
        project_failures = self.check_single_python_project(project_path)

        if not project_failures:
            self.add_line(f"\n✅ All checks passed for {project_path.name}.")
            return

        self.add_line(f"\n❌ Checks failed for {project_path.name}: {', '.join(project_failures)}")

    @ActionBase.handle_exceptions("checking Python project")
    def execute(
        self,
        *_args: Any,
        folder_path: Path | None = None,
        noninteractive: bool = False,
        **_kwargs: Any,
    ) -> None:
        """Run full Python checks for one project folder."""
        if noninteractive and folder_path is None:
            self.handle_error(
                ValueError("folder_path is required when noninteractive is True"),
                self.title,
            )
            return

        if folder_path is not None:
            self.folder_path = Path(folder_path).resolve()
        else:
            self.folder_path = self.dialogs.get_folder_with_choice_option(
                self.config["paths_python_projects"], self.config["path_github"]
            )
        if not self.folder_path:
            return

        if noninteractive:
            self.add_line(f"🔵 Starting full PY check for path: {self.folder_path}")
            self.check_python_project_common()
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("checking Python project thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        self.check_python_project_common()

    @ActionBase.handle_exceptions("checking Python project thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} {self.folder_path} completed")
        self.show_result()
