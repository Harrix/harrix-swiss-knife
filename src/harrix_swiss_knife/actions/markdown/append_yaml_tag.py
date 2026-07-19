"""Actions for Python development and Markdown file management."""

from __future__ import annotations

from typing import Any

import harrix_pylib as h

from harrix_swiss_knife.actions.base import ActionBase


class OnAppendYamlTag(ActionBase):
    """Append a YAML tag to Markdown files in a folder.

    This action processes all Markdown files in a selected folder to add or update
    a YAML tag in the front matter. The user specifies the tag key and value,
    and the action applies this tag to all Markdown files in the folder.

    If a file doesn't have YAML front matter, it will be added. If the YAML tag
    already exists, it will be updated with the new value.

    """

    icon = "🏷️"
    title = "Append YAML tag in …"

    @ActionBase.handle_exceptions("appending YAML tag")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Append a YAML tag to Markdown files in a folder."""
        self.folder_path = self.dialogs.get_folder_with_choice_option(
            self.config["paths_notes"], self.config["path_notes"]
        )
        if not self.folder_path:
            return

        # Get YAML tag key
        yaml_tag_key = self.dialogs.get_text_input("YAML Tag Key", "Enter the YAML tag key:", "author")
        if not yaml_tag_key:
            return

        # Get YAML tag value
        yaml_tag_value = self.dialogs.get_text_input("YAML Tag Value", "Enter the YAML tag value:", "")
        if yaml_tag_value is None:
            return

        self.yaml_tag_tuple = (yaml_tag_key, yaml_tag_value)
        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("appending YAML tag thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        self.add_line(f"🔵 Starting processing for path: {self.folder_path}")
        if self.folder_path is None:
            return
        self.add_line(
            h.file.apply_func(
                str(self.folder_path),
                ".md",
                lambda filename: h.md.append_yaml_tag(filename, self.yaml_tag_tuple),
            )
        )

    @ActionBase.handle_exceptions("appending YAML tag thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} completed")
        self.show_result()
