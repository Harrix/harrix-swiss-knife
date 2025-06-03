"""Module providing functionality for checking Markdown files for compliance with specified rules."""

import re
from pathlib import Path

import harrix_pylib as h
import yaml


class MarkdownChecker:
    """Class for checking Markdown files for compliance with specified rules.

    Rules:

    - **H000** - Exception error.
    - **H001** - Presence of a space in the Markdown file name.
    - **H002** - Presence of a space in the path to the Markdown file.
    - **H003** - YAML is missing.
    - **H004** - The lang field is missing in YAML.
    - **H005** - In YAML, lang is not set to `en` or `ru`.
    - **H006** - Markdown is written with a small letter.

    Example:

    ```python
    import harrix_pylib as h
    from pathlib import Path

    checker = MarkdownChecker()
    errors = checker("C:/Notes/Note.md")
    # or
    errors = checker.check("C:/Notes/Note.md")

    for error in errors:
        print(error)
    ```

    """

    def __init__(self) -> None:
        """Initialize the MarkdownChecker with all available rules."""
        number_rules = 6
        self.all_rules = {f"H{i:03d}" for i in range(1, number_rules + 1)}

    def __call__(self, filename: Path | str, exclude_rules: set | None = None) -> list:
        """Check Markdown file for compliance with specified rules.

        Args:

        - `filename` (`Path | str`): Path to the Markdown file to check.
        - `exclude_rules` (`set | None`): Set of rule codes to exclude from checking. Defaults to `None`.

        Returns:

        - `list`: List of error messages found during checking.

        """
        return self.check(filename, exclude_rules)

    def _check_content(self, filename: Path, content_md: str, rules: set) -> None:
        """Check markdown content for style issues.

        Args:

        - `filename` (`Path`): Path to the Markdown file being checked.
        - `content_md` (`str`): The content part of the markdown file (without YAML).
        - `rules` (`set`): Set of rule codes to apply during checking.

        """
        lines = content_md.split("\n")
        for i, (line, is_code_block) in enumerate(h.md.identify_code_blocks(lines)):
            if is_code_block:
                # Skip code lines
                continue

            # Check non-code lines
            clean_line = ""
            for segment, in_code in h.md.identify_code_blocks_line(line):
                if not in_code:
                    clean_line += segment

            words = re.findall(r"\b[\w/\\.-]+\b", clean_line)
            words = [word.strip(".") for word in words]

            if "H006" in rules and "markdown" in words:
                self._add_error("H006", "Markdown is written with a small letter in", filename, line=line)

    def _check_filename(self, filename: Path, rules: set) -> None:
        """Check filename for spaces.

        Args:

        - `filename` (`Path`): Path to the Markdown file being checked.
        - `rules` (`set`): Set of rule codes to apply during checking.

        """
        if "H001" in rules and " " in str(filename.name):
            self._add_error("H001", "Presence of a space in the Markdown file name", filename)

        if "H002" in rules and " " in str(filename):
            self._add_error("H002", "Presence of a space in the path to the Markdown file", filename)

    def _check_yaml(self, filename: Path, yaml_md: str, rules: set) -> None:
        """Check YAML for required fields.

        Args:

        - `filename` (`Path`): Path to the Markdown file being checked.
        - `yaml_md` (`str`): The YAML frontmatter content from the markdown file.
        - `rules` (`set`): Set of rule codes to apply during checking.

        """
        try:
            data_yaml = yaml.safe_load(yaml_md.replace("---\n", "").replace("\n---", ""))
            if not data_yaml:
                self._add_error("H003", "YAML is missing in", filename)
            else:
                lang = data_yaml.get("lang")
                if "H004" in rules and not lang:
                    self._add_error("H004", "The lang field is missing in YAML in", filename)
                elif "H005" in rules and lang not in ["en", "ru"]:
                    self._add_error("H005", "In YAML, lang is not set to en or ru in", filename)
        except Exception as e:  # noqa: BLE001
            self._add_error("H000", f"YAML {e} in", filename)

    def _add_error(self, type_error: str, text: str, filename: str | Path, *, line: str = "") -> None:
        """Add an error message to the errors list.

        Args:

        - `type_error` (`str`): The error code (e.g., "H001").
        - `text` (`str`): Description of the error.
        - `filename` (`str | Path`): Path to the file where the error was found.
        - `line` (`str`): The specific line where the error occurred. Defaults to `""`.

        """
        message = f"❌ {type_error} {text}: \n{filename}\n"
        if line:
            message += f"{line}\n"
        self.errors.append(message)

    def check(self, filename: Path | str, exclude_rules: set | None = None) -> list:
        """Check Markdown file for compliance with specified rules.

        Args:

        - `filename` (`Path | str`): Path to the Markdown file to check.
        - `exclude_rules` (`set | None`): Set of rule codes to exclude from checking. Defaults to `None`.

        Returns:

        - `list`: List of error messages found during checking.

        """
        rules = self.all_rules - (set() if exclude_rules is None else exclude_rules)
        self.errors = []

        filename = Path(filename)

        with Path.open(filename, encoding="utf-8") as f:
            markdown_text = f.read()

        yaml_md, content_md = h.md.split_yaml_content(markdown_text)

        self._check_filename(filename, rules)
        self._check_yaml(filename, yaml_md, rules)
        self._check_content(filename, content_md, rules)

        return self.errors
