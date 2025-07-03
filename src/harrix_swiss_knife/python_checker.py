"""Module providing functionality for checking Python files for compliance with specified rules."""

import re
from collections.abc import Generator
from pathlib import Path
from typing import ClassVar


class PythonChecker:
    """Class for checking Python files for compliance with specified rules.

    ```
    Rules:

    - **P001** - Presence of Russian letters in the code.

    """

    # Rule constants for easier maintenance
    RULES: ClassVar[dict[str, str]] = {
        "P001": "Presence of Russian letters in the code",
    }

    def __init__(self, project_root: Path | str | None = None) -> None:
        """Initialize the PythonChecker with all available rules.

        Args:

        - `project_root` (`Path | str | None`): Root directory of the project for relative path calculation.
        If `None`, will try to find git root or use current working directory. Defaults to `None`.

        """
        self.all_rules = set(self.RULES.keys())
        self.project_root = self._determine_project_root(project_root)

    def __call__(self, filename: Path | str, exclude_rules: set | None = None) -> list[str]:
        """Check Python file for compliance with specified rules.

        Args:

        - `filename` (`Path | str`): Path to the Python file to check.
        - `exclude_rules` (`set | None`): Set of rule codes to exclude from checking. Defaults to `None`.

        Returns:

        - `list[str]`: List of error messages found during checking.

        """
        return self.check(filename, exclude_rules)

    def _check_all_rules(self, filename: Path, rules: set) -> Generator[str, None, None]:
        """Generate all errors found during checking.

        Args:

        - `filename` (`Path`): Path to the Python file being checked.
        - `rules` (`set`): Set of rule codes to apply during checking.

        Yields:

        - `str`: Error message for each found issue.

        """
        try:
            content = filename.read_text(encoding="utf-8")
            lines = content.splitlines()

            yield from self._check_content_rules(filename, lines, rules)

        except Exception as e:
            yield self._format_error("P000", f"Exception error: {e}", filename)

    def _check_content_rules(self, filename: Path, lines: list[str], rules: set) -> Generator[str, None, None]:
        """Check content-related rules.

        Args:

        - `filename` (`Path`): Path to the Python file being checked.
        - `lines` (`list[str]`): All lines from the file.
        - `rules` (`set`): Set of rule codes to apply during checking.

        Yields:

        - `str`: Error message for each content-related issue found.

        """
        if "P001" not in rules:
            return

        for line_num, line in enumerate(lines, 1):
            if self._has_russian_letters(line):
                col = self._find_russian_letters_position(line)
                yield self._format_error("P001", self.RULES["P001"], filename, line_num=line_num, col=col)

    def _determine_project_root(self, project_root: Path | str | None) -> Path:
        """Determine the project root directory.

        Args:

        - `project_root` (`Path | str | None`): Provided project root path.

        Returns:

        - `Path`: Resolved project root directory.

        """
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

    def _find_russian_letters_position(self, text: str) -> int:
        """Find the position of the first Russian letter in text (1-based).

        Args:

        - `text` (`str`): Text to search in.

        Returns:

        - `int`: Position of the first Russian letter (1-based), or 1 if not found.

        """
        match = re.search(r"[\u0430-\u044F\u0451\u0410-\u042F\u0401]", text)
        return match.start() + 1 if match else 1

    def _format_error(self, error_code: str, message: str, filename: Path, *, line_num: int = 0, col: int = 0) -> str:
        """Format error message in ruff style.

        Args:

        - `error_code` (`str`): The error code (e.g., "P001").
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
        """Get relative path from project root, fallback to absolute if outside project.

        Args:

        - `filename` (`Path`): Path to the file.

        Returns:

        - `str`: Relative path from project root or absolute path if outside project.

        """
        try:
            return str(filename.resolve().relative_to(self.project_root))
        except ValueError:
            # File is outside project root
            return str(filename.resolve())

    def _has_russian_letters(self, text: str) -> bool:
        """Check if text contains Russian letters.

        Args:

        - `text` (`str`): Text to check for Russian letters.

        Returns:

        - `bool`: `True` if text contains Russian letters, `False` otherwise.

        """
        return bool(re.search(r"[\u0430-\u044F\u0451\u0410-\u042F\u0401]", text))

    def check(self, filename: Path | str, exclude_rules: set | None = None) -> list[str]:
        """Check Python file for compliance with specified rules.

        Args:

        - `filename` (`Path | str`): Path to the Python file to check.
        - `exclude_rules` (`set | None`): Set of rule codes to exclude from checking. Defaults to `None`.

        Returns:

        - `list[str]`: List of error messages found during checking.

        """
        filename = Path(filename)
        return list(self._check_all_rules(filename, self.all_rules - (exclude_rules or set())))
