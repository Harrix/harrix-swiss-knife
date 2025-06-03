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

    def __init__(self) -> None:
        """Initialize the MarkdownChecker with all available rules."""
        self.all_rules = set(self.RULES.keys())

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
            yaml_part, markdown_part = h.md.split_yaml_content(content)

            yield from self._check_yaml_rules(filename, yaml_part, rules)
            yield from self._check_content_rules(filename, markdown_part, rules)

        except Exception as e:  # noqa: BLE001
            yield self._format_error("H000", f"Exception error: {e}", filename)

    def _check_content_rules(self, filename: Path, content: str, rules: set) -> Generator[str, None, None]:
        """Check content-related rules.

        Args:

        - `filename` (`Path`): Path to the Markdown file being checked.
        - `content` (`str`): The content part of the markdown file (without YAML).
        - `rules` (`set`): Set of rule codes to apply during checking.

        Yields:

        - `str`: Error message for each content-related issue found.

        """
        for line_num, (line, is_code_block) in enumerate(h.md.identify_code_blocks(content.splitlines()), 1):
            if is_code_block:
                continue

            # Remove inline code from line before checking
            clean_line = ""
            for segment, in_code in h.md.identify_code_blocks_line(line):
                if not in_code:
                    clean_line += segment

            words = [word.strip(".") for word in re.findall(r"\b[\w/\\.-]+\b", clean_line)]

            if "H006" in rules and "markdown" in words:
                yield self._format_error("H006", self.RULES["H006"], filename, line=line, line_num=line_num)

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

    def _check_yaml_rules(self, filename: Path, yaml_content: str, rules: set) -> Generator[str, None, None]:
        """Check YAML-related rules.

        Args:

        - `filename` (`Path`): Path to the Markdown file being checked.
        - `yaml_content` (`str`): The YAML frontmatter content from the markdown file.
        - `rules` (`set`): Set of rule codes to apply during checking.

        Yields:

        - `str`: Error message for each YAML-related issue found.

        """
        try:
            data = yaml.safe_load(yaml_content.replace("---\n", "").replace("\n---", "")) if yaml_content else None

            if not data and "H003" in rules:
                yield self._format_error("H003", self.RULES["H003"], filename)
                return

            if data:
                lang = data.get("lang")
                if "H004" in rules and not lang:
                    yield self._format_error("H004", self.RULES["H004"], filename)
                elif "H005" in rules and lang and lang not in ["en", "ru"]:
                    yield self._format_error("H005", self.RULES["H005"], filename)

        except yaml.YAMLError as e:
            yield self._format_error("H000", f"YAML parsing error: {e}", filename)

    def _format_error(self, error_code: str, message: str, filename: Path, *, line: str = "", line_num: int = 0) -> str:
        """Format error message consistently.

        Args:

        - `error_code` (`str`): The error code (e.g., "H001").
        - `message` (`str`): Description of the error.
        - `filename` (`Path`): Path to the file where the error was found.
        - `line` (`str`): The specific line where the error occurred. Defaults to `""`.
        - `line_num` (`int`): Line number where the error occurred. Defaults to `0`.

        Returns:

        - `str`: Formatted error message.

        """
        result = f"❌ {error_code} {message}:\n{filename}\n"
        if line:
            result += f"Line {line_num}: {line}\n"
        return result

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
