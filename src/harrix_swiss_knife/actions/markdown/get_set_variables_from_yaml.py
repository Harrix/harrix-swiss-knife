"""Actions for Python development and Markdown file management."""

from __future__ import annotations

from typing import Any

import harrix_pylib as h

from harrix_swiss_knife.actions.base import ActionBase


class OnGetSetVariablesFromYaml(ActionBase):
    """Get a sorted list of all variables from YAML frontmatter in Markdown files.

    This action recursively searches through all Markdown files in a selected folder
    and extracts all unique variable names from their YAML frontmatter. It:

    1. Recursively searches all subfolders for `.md` files
    2. Extracts YAML frontmatter from each file
    3. Collects all unique variable names (keys) from the YAML
    4. Returns a sorted list of all variables found

    Files and folders matching common ignore patterns (like `.git`, `__pycache__`,
    `node_modules`, etc.) and hidden files/folders are automatically ignored.

    Example output: `['categories', 'date', 'tags']`

    """

    icon = "📋"
    title = "Get set variables from YAML in …"

    @ActionBase.handle_exceptions("getting set variables from YAML")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Get a sorted list of all variables from YAML frontmatter in Markdown files."""
        self.folder_path = self.dialogs.get_folder_with_choice_option(
            self.config["paths_notes"], self.config["path_notes"]
        )
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("getting set variables from YAML thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        if self.folder_path is None:
            return

        self.add_line(f"🔵 Processing folder: {self.folder_path}")
        variables = h.md.get_set_variables_from_yaml(self.folder_path)

        if variables:
            self.add_line(f"\n✅ Found {len(variables)} unique variable(s):\n")
            for variable in variables:
                self.add_line(f"  - {variable}")
        else:
            self.add_line("ℹ️ No variables found in YAML frontmatter.")  # noqa: RUF001

    @ActionBase.handle_exceptions("getting set variables from YAML thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} completed")
        self.show_result()
