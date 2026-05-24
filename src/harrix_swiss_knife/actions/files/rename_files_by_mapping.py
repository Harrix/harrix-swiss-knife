"""Actions for file operations and management of directory structures."""

from __future__ import annotations

from typing import Any

import harrix_pylib as h

from harrix_swiss_knife.actions.base import ActionBase


class OnRenameFilesByMapping(ActionBase):
    """Rename files recursively based on a mapping dictionary.

    This action prompts the user to select a folder and provide a mapping text
    (old filename TAB new filename per line), then renames files recursively
    from the selected directory according to the mapping.
    """

    icon = "📝"
    title = "Rename files by mapping in …"

    @ActionBase.handle_exceptions("renaming files by mapping")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Rename files recursively based on a mapping dictionary."""
        self.folder_path = self.dialogs.get_existing_directory("Select folder to rename files", self.config["path_3d"])
        if self.folder_path is None:
            return

        # Get mapping text from user
        mapping_text = self.dialogs.get_text_textarea(
            "File Rename Mapping",
            "Enter file rename mapping (one per line):\nold_filename.ext<TAB>new_filename.ext",
            "old_file.txt\tnew_file.txt\nconfig.json\tsettings.json",
        )
        if mapping_text is None:
            return

        # Parse mapping text into dictionary
        self.rename_mapping = self._parse_mapping_text(mapping_text)
        if not self.rename_mapping:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("renaming files by mapping thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        if self.folder_path is None or not self.rename_mapping:
            return

        self.add_line(f"🔵 Starting file renaming for path: {self.folder_path}")
        self.add_line(f"🔵 Renaming {len(self.rename_mapping)} file mappings")
        result = h.file.rename_files_by_mapping(self.folder_path, self.rename_mapping)
        self.add_line(result)

    @ActionBase.handle_exceptions("renaming files by mapping thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} completed")
        self.show_result()

    def _parse_mapping_text(self, mapping_text: str) -> dict[str, str] | None:
        """Parse mapping text into a dictionary.

        Args:

        -`mapping_text` (`str`): Text with `old_filename<TAB>new_filename` per line.

        Returns:

        - `dict[str, str] | None`: Dictionary mapping old names to new names, or None if error.

        """
        try:
            mapping_dict = {}
            lines = mapping_text.strip().split("\n")

            for line_num, line in enumerate(lines, 1):
                line_new = line.strip()
                if not line_new:  # Skip empty lines
                    continue

                # Split by tab character
                parts = line_new.split("\t")
                count_parts = 2
                if len(parts) != count_parts:
                    self.add_line(
                        f"❌ Invalid format on line {line_num}: '{line_new}'. Expected: old_filename<TAB>new_filename"
                    )
                    return None

                old_name, new_name = parts[0].strip(), parts[1].strip()

                if not old_name or not new_name:
                    self.add_line(f"❌ Empty filename on line {line_num}: '{line_new}'")
                    return None

                mapping_dict[old_name] = new_name

            if not mapping_dict:
                self.add_line("❌ No valid mappings found in the text")
                return None

        except Exception as e:
            self.add_line(f"❌ Error parsing mapping text: {e}")
            return None
        else:
            self.add_line(f"✅ Parsed {len(mapping_dict)} file mappings")
            return mapping_dict
