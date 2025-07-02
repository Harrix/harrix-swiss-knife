"""Module providing functionality for checking Markdown files for compliance with specified rules."""

import re
from collections.abc import Generator
from pathlib import Path
from typing import ClassVar

import harrix_pylib as h
import yaml


class MarkdownChecker:
    """Class for checking Markdown files for compliance with specified rules.

    Rules:

    - **H001** - Presence of a space in the Markdown file name.
    - **H002** - Presence of a space in the path to the Markdown file.
    - **H003** - YAML is missing.
    - **H004** - The lang field is missing in YAML.
    - **H005** - In YAML, lang is not set to `en` or `ru`.
    - **H006** - Markdown is written with a small letter.

    """

    # Rule constants for easier maintenance
    RULES: ClassVar[dict[str, str]] = {
        "H001": "Presence of a space in the Markdown file name",
        "H002": "Presence of a space in the path to the Markdown file",
        "H003": "YAML is missing",
        "H004": "The lang field is missing in YAML",
        "H005": "In YAML, lang is not set to en or ru",
        "H006": "Markdown is written with a small letter",
    }

    def __init__(self, project_root: Path | str | None = None) -> None:
        """Initialize the MarkdownChecker with all available rules.

        Args:
            project_root: Root directory of the project for relative path calculation.
                         If None, will try to find git root or use current working directory.
        """
        self.all_rules = set(self.RULES.keys())
        self.project_root = self._determine_project_root(project_root)

    def __call__(self, filename: Path | str, exclude_rules: set | None = None) -> list[str]:
        """Check Markdown file for compliance with specified rules."""
        return self.check(filename, exclude_rules)

    def _check_all_rules(self, filename: Path, rules: set) -> Generator[str, None, None]:
        """Generate all errors found during checking.

        Args:

        - `filename` (`Path`): Path to the Markdown file being checked.
        - `rules` (`set`): Set of rule codes to apply during checking.

        Yields:

        - `str`: Error message for each found issue.

        """
        yield from self._check_filename_rules(filename, rules)

        # Read file only once for performance
        try:
            content = filename.read_text(encoding="utf-8")
            all_lines = content.splitlines()
            yaml_end_line = self._find_yaml_end_line(all_lines)

            yaml_part, markdown_part = h.md.split_yaml_content(content)

            yield from self._check_yaml_rules(filename, yaml_part, all_lines, rules)
            yield from self._check_content_rules(filename, all_lines, yaml_end_line, rules)

        except Exception as e:
            yield self._format_error("H000", f"Exception error: {e}", filename)

    def _check_content_rules(
        self, filename: Path, all_lines: list[str], yaml_end_line: int, rules: set
    ) -> Generator[str, None, None]:
        """Check content-related rules working directly with original file lines.

        Args:

        - `filename` (`Path`): Path to the Markdown file being checked.
        - `all_lines` (`list[str]`): All lines from the original file.
        - `yaml_end_line` (`int`): Line number where YAML block ends (1-based).
        - `rules` (`set`): Set of rule codes to apply during checking.

        Yields:

        - `str`: Error message for each content-related issue found.

        """
        if "H006" not in rules:
            return

        # Get content lines (after YAML)
        content_lines = all_lines[yaml_end_line - 1 :] if yaml_end_line > 1 else all_lines

        # Use identify_code_blocks to determine which lines are in code blocks
        code_block_info = list(h.md.identify_code_blocks(content_lines))

        for i, (line, is_code_block) in enumerate(code_block_info):
            if is_code_block:
                continue

            # Calculate actual line number in the original file
            actual_line_num = (yaml_end_line - 1) + i + 1  # Convert to 1-based

            # Remove inline code from line before checking
            clean_line = ""
            for segment, in_code in h.md.identify_code_blocks_line(line):
                if not in_code:
                    clean_line += segment

            words = [word.strip(".") for word in re.findall(r"\b[\w/\\.-]+\b", clean_line)]

            if "markdown" in words:
                # Find position of "markdown" in the original line
                markdown_match = re.search(r"\bmarkdown\b", line.lower())
                col = markdown_match.start() + 1 if markdown_match else 1

                yield self._format_error("H006", self.RULES["H006"], filename, line_num=actual_line_num, col=col)

    def _check_filename_rules(self, filename: Path, rules: set) -> Generator[str, None, None]:
        """Check filename-related rules.

        Args:

        - `filename` (`Path`): Path to the Markdown file being checked.
        - `rules` (`set`): Set of rule codes to apply during checking.

        Yields:

        - `str`: Error message for each filename-related issue found.

        """
        if "H001" in rules and " " in filename.name:
            yield self._format_error("H001", self.RULES["H001"], filename)

        if "H002" in rules and " " in str(filename):
            yield self._format_error("H002", self.RULES["H002"], filename)

    def _check_yaml_rules(
        self, filename: Path, yaml_content: str, all_lines: list[str], rules: set
    ) -> Generator[str, None, None]:
        """Check YAML-related rules.

        Args:

        - `filename` (`Path`): Path to the Markdown file being checked.
        - `yaml_content` (`str`): The YAML frontmatter content from the markdown file.
        - `all_lines` (`list[str]`): All lines from the original file.
        - `rules` (`set`): Set of rule codes to apply during checking.

        Yields:

        - `str`: Error message for each YAML-related issue found.

        """
        try:
            data = yaml.safe_load(yaml_content.replace("---\n", "").replace("\n---", "")) if yaml_content else None

            if not data and "H003" in rules:
                yield self._format_error("H003", self.RULES["H003"], filename, line_num=1)
                return

            if data:
                lang = data.get("lang")
                if "H004" in rules and not lang:
                    # Find end of YAML block or use line 2 as default
                    line_num = self._find_yaml_block_end_line(all_lines)
                    yield self._format_error("H004", self.RULES["H004"], filename, line_num=line_num)
                elif "H005" in rules and lang and lang not in ["en", "ru"]:
                    # Find the line with lang field in original file
                    line_num = self._find_yaml_field_line_in_original(all_lines, "lang")
                    col = self._find_yaml_field_column(all_lines, line_num, "lang")
                    yield self._format_error("H005", self.RULES["H005"], filename, line_num=line_num, col=col)

        except yaml.YAMLError as e:
            yield self._format_error("H000", f"YAML parsing error: {e}", filename, line_num=1)

    def _determine_project_root(self, project_root: Path | str | None) -> Path:
        """Determine the project root directory."""
        if project_root:
            return Path(project_root).resolve()

        # Try to find git root
        current = Path.cwd()
        while current != current.parent:
            if (current / ".git").exists():
                return current
            current = current.parent

        # Fallback to current working directory
        return Path.cwd()

    def _find_yaml_block_end_line(self, all_lines: list[str]) -> int:
        """Find the line number where YAML block ends (the closing --- line)."""
        if not all_lines or all_lines[0].strip() != "---":
            return 1

        for i, line in enumerate(all_lines[1:], 2):  # Start from line 2
            if line.strip() == "---":
                return i
        return len(all_lines)

    def _find_yaml_end_line(self, lines: list[str]) -> int:
        """Find the line number where YAML block ends (1-based).

        Returns:
            Line number after YAML block, or 1 if no YAML.
        """
        if not lines or lines[0].strip() != "---":
            return 1

        for i, line in enumerate(lines[1:], 2):  # Start from line 2 (1-based)
            if line.strip() == "---":
                return i + 1  # Return line after YAML block

        return len(lines) + 1  # If no closing ---, YAML goes to end

    def _find_yaml_field_column(self, all_lines: list[str], line_num: int, field: str) -> int:
        """Find column position of field value in YAML."""
        if line_num <= len(all_lines):
            line = all_lines[line_num - 1]  # Convert to 0-based index
            match = re.search(f"{field}:\\s*(.+)", line)
            if match:
                return match.start(1) + 1  # +1 for 1-based column numbering
        return 1

    def _find_yaml_field_line_in_original(self, all_lines: list[str], field: str) -> int:
        """Find line number of a specific field in YAML content within original file."""
        if not all_lines or all_lines[0].strip() != "---":
            return 1

        # Look for field within YAML block (between first --- and second ---)
        for i, line in enumerate(all_lines[1:], 2):  # Start from line 2
            if line.strip() == "---":  # End of YAML block
                break
            if line.strip().startswith(f"{field}:"):
                return i

        return 2  # Default to line 2 if not found

    def _format_error(self, error_code: str, message: str, filename: Path, *, line_num: int = 0, col: int = 0) -> str:
        """Format error message in ruff style.

        Args:

        - `error_code` (`str`): The error code (e.g., "H001").
        - `message` (`str`): Description of the error.
        - `filename` (`Path`): Path to the file where the error was found.
        - `line_num` (`int`): Line number where the error occurred. Defaults to `0`.
        - `col` (`int`): Column number where the error occurred. Defaults to `0`.

        Returns:

        - `str`: Formatted error message in ruff style.

        """
        relative_path = self._get_relative_path(filename)

        location = relative_path
        if line_num > 0:
            location += f":{line_num}"
            if col > 0:
                location += f":{col}"

        return f"{location}: {error_code} {message}"

    def _get_relative_path(self, filename: Path) -> str:
        """Get relative path from project root, fallback to absolute if outside project."""
        try:
            return str(filename.resolve().relative_to(self.project_root))
        except ValueError:
            # File is outside project root
            return str(filename.resolve())

    def check(self, filename: Path | str, exclude_rules: set | None = None) -> list[str]:
        """Check Markdown file for compliance with specified rules.

        Args:

        - `filename` (`Path | str`): Path to the Markdown file to check.
        - `exclude_rules` (`set | None`): Set of rule codes to exclude from checking. Defaults to `None`.

        Returns:

        - `list[str]`: List of error messages found during checking.

        """
        filename = Path(filename)
        return list(self._check_all_rules(filename, self.all_rules - (exclude_rules or set())))
