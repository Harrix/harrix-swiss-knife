"""Actions for Python development and Markdown file management."""

from __future__ import annotations

import re
import shlex
from collections import Counter
from pathlib import Path
from typing import Any

import harrix_pylib as h

from harrix_swiss_knife.actions.base import ActionBase
from harrix_swiss_knife.cli_menu import CLI_EXECUTABLE

_RULE_ID_RE = re.compile(r"^H\d+")


class OnCheckMdFolder(ActionBase):
    """Action to check all Markdown files in a folder for errors with Harrix rules."""

    icon = "🚧"
    title = "Check MD in …"
    cli_available = True
    cli_hint = "md check"

    def check_md_folder_common(self) -> None:
        """Check Markdown files in ``folder_path`` with ``selected_rule_ids`` and log results."""
        checker = h.md_check.MarkdownChecker()
        if self.folder_path is None:
            return

        errors_dict: dict[str, list[str]] = {}
        for md_file in checker.find_markdown_files(self.folder_path):
            if md_file.name.endswith(".g.md"):
                continue
            errors = checker.check(md_file, select=self.selected_rule_ids)
            if errors:
                errors_dict[str(md_file)] = errors

        all_errors = []
        for file_path, file_errors in errors_dict.items():
            for error in file_errors:
                # MarkdownChecker formats errors with a path relative to the git root.
                # Replace that relative prefix with the full absolute path (the dict key).
                _, sep, rest = error.partition(":")
                all_errors.append(f"{file_path}:{rest}" if sep else error)

        if all_errors:
            self.add_line("\n".join(all_errors))
            self.add_line(f"\n🔢 Count errors = {len(all_errors)}")

            desc_counts = Counter()
            for err in all_errors:
                # Format from MarkdownChecker._format_error: "{path}:{line}:{col}: {error_code} {message}"
                parts = err.split(": ", maxsplit=2)
                count_parts = 2
                if len(parts) >= count_parts:
                    description = parts[1]
                    if description.strip():
                        desc_counts[description] += 1

            sorted_stats = sorted(desc_counts.items(), key=lambda x: (-x[1], x[0]))
            stats_lines = [f"  {count}: {desc}" for desc, count in sorted_stats]
            self.add_line("📊 Stats by error type:\n" + "\n".join(stats_lines))

            first_rule_id: str | None = None
            for desc, _count in sorted_stats:
                rule_id_match = _RULE_ID_RE.match(desc.strip())
                if rule_id_match is not None:
                    first_rule_id = rule_id_match.group(0)
                    break

            if first_rule_id is not None:
                folder_quoted = shlex.quote(str(self.folder_path))
                self.add_line(
                    "💡 Check a single rule — put the rule id in place of <>:\n"
                    f"  {CLI_EXECUTABLE} md check {folder_quoted} --rule <>\n"
                    f"  Example: {CLI_EXECUTABLE} md check {folder_quoted} --rule {first_rule_id}"
                )
        else:
            self.add_line(f"✅ There are no errors in {self.folder_path}.")

    @ActionBase.handle_exceptions("checking markdown folder")
    def execute(
        self,
        *_args: Any,
        folder_path: Path | None = None,
        rule_ids: set[str] | None = None,
        noninteractive: bool = False,
        **_kwargs: Any,
    ) -> None:
        """Check all Markdown files in a folder for errors with Harrix rules."""
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
                self.config["paths_notes"], self.config["path_notes"]
            )
        if not self.folder_path:
            return

        checker = h.md_check.MarkdownChecker()
        all_rule_ids = checker.all_rules

        if noninteractive:
            if rule_ids is None:
                self.selected_rule_ids = all_rule_ids
            else:
                unknown = rule_ids - set(checker.RULES)
                if unknown:
                    self.handle_error(
                        ValueError(f"Unknown rule id(s): {', '.join(sorted(unknown))}"),
                        self.title,
                    )
                    return
                self.selected_rule_ids = rule_ids
            self.add_line(f"🔵 Starting Markdown check for path: {self.folder_path}")
            self.check_md_folder_common()
            return

        # Convert rules dict to list of rule descriptions for display
        rule_choices = [f"{rule_id}: {description}" for rule_id, description in checker.RULES.items()]

        # Show dialog to select rules (all selected by default)
        selected_rules = self.dialogs.get_checkbox_selection(
            "Select Rules for Markdown Check",
            "Choose which rules to check:",
            rule_choices,
            default_selected=rule_choices,
        )

        if not selected_rules:
            return

        # Extract rule IDs from selected descriptions
        self.selected_rule_ids = set()
        for selected_rule in selected_rules:
            # Extract rule ID (e.g., "H001" from "H001: Description")
            rule_id = selected_rule.split(":")[0].strip()
            self.selected_rule_ids.add(rule_id)

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("markdown folder checking thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        self.check_md_folder_common()

    @ActionBase.handle_exceptions("markdown folder checking thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} {self.folder_path} completed")
        self.show_result()
