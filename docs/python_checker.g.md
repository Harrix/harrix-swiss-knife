---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# File `python_checker.py`

<details>
<summary>📖 Contents</summary>

## Contents

- [Class `PythonChecker`](#class-pythonchecker)
  - [Method `__init__`](#method-__init__)
  - [Method `__call__`](#method-__call__)
  - [Method `check`](#method-check)
  - [Method `_check_all_rules`](#method-_check_all_rules)
  - [Method `_check_content_rules`](#method-_check_content_rules)
  - [Method `_determine_project_root`](#method-_determine_project_root)
  - [Method `_find_russian_letters_position`](#method-_find_russian_letters_position)
  - [Method `_format_error`](#method-_format_error)
  - [Method `_get_relative_path`](#method-_get_relative_path)
  - [Method `_has_russian_letters`](#method-_has_russian_letters)
  - [Method `_parse_rules_string`](#method-_parse_rules_string)
  - [Method `_should_ignore_line`](#method-_should_ignore_line)

</details>

## Class `PythonChecker`

```python
class PythonChecker
```

Class for checking Python files for compliance with specified rules.

Rules:

- **HP001** - Presence of Russian letters in the code.

Examples for ignore directives:

```text
# ignore: HP001
# ignore: HP001, HP002
```

<details>
<summary>Code:</summary>

```python
class PythonChecker:

    # Rule constants for easier maintenance
    RULES: ClassVar[dict[str, str]] = {
        "HP001": "Presence of Russian letters in the code",
    }

    # Comment pattern for ignoring checks
    IGNORE_PATTERN: ClassVar[re.Pattern] = re.compile(r"#\s*ignore:\s*([A-Z0-9,\s]+)", re.IGNORECASE)

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
        if "HP001" not in rules:
            return

        for line_num, line in enumerate(lines, 1):
            # Check if this line should be ignored for P001
            if self._should_ignore_line(line, "HP001"):
                continue

            if self._has_russian_letters(line):
                col = self._find_russian_letters_position(line)
                yield self._format_error("HP001", self.RULES["HP001"], filename, line_num=line_num, col=col)

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

        - `error_code` (`str`): The error code (e.g., "HP001").
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

    def _parse_rules_string(self, rules_str: str) -> set[str]:
        """Parse comma-separated rules string into a set.

        Args:

        - `rules_str` (`str`): Comma-separated string of rule codes.

        Returns:

        - `set[str]`: Set of rule codes.

        """
        return {rule.strip().upper() for rule in rules_str.split(",") if rule.strip()}

    def _should_ignore_line(self, line: str, rule_code: str) -> bool:
        """Check if a line should be ignored for a specific rule.

        Args:

        - `line` (`str`): Line content to check.
        - `rule_code` (`str`): Rule code to check.

        Returns:

        - `bool`: `True` if the line should be ignored for this rule, `False` otherwise.

        """
        # Look for ignore pattern anywhere in the line
        match = self.IGNORE_PATTERN.search(line)
        if not match:
            return False

        rules_str = match.group(1)
        ignored_rules = self._parse_rules_string(rules_str)

        return rule_code in ignored_rules
```

</details>

### Method `__init__`

```python
def __init__(self, project_root: Path | str | None = None) -> None
```

Initialize the PythonChecker with all available rules.

Args:

- `project_root` (`Path | str | None`): Root directory of the project for relative path calculation.
  If `None`, will try to find git root or use current working directory. Defaults to `None`.

<details>
<summary>Code:</summary>

```python
def __init__(self, project_root: Path | str | None = None) -> None:
        self.all_rules = set(self.RULES.keys())
        self.project_root = self._determine_project_root(project_root)
```

</details>

### Method `__call__`

```python
def __call__(self, filename: Path | str, exclude_rules: set | None = None) -> list[str]
```

Check Python file for compliance with specified rules.

Args:

- `filename` (`Path | str`): Path to the Python file to check.
- `exclude_rules` (`set | None`): Set of rule codes to exclude from checking. Defaults to `None`.

Returns:

- `list[str]`: List of error messages found during checking.

<details>
<summary>Code:</summary>

```python
def __call__(self, filename: Path | str, exclude_rules: set | None = None) -> list[str]:
        return self.check(filename, exclude_rules)
```

</details>

### Method `check`

```python
def check(self, filename: Path | str, exclude_rules: set | None = None) -> list[str]
```

Check Python file for compliance with specified rules.

Args:

- `filename` (`Path | str`): Path to the Python file to check.
- `exclude_rules` (`set | None`): Set of rule codes to exclude from checking. Defaults to `None`.

Returns:

- `list[str]`: List of error messages found during checking.

<details>
<summary>Code:</summary>

```python
def check(self, filename: Path | str, exclude_rules: set | None = None) -> list[str]:
        filename = Path(filename)
        return list(self._check_all_rules(filename, self.all_rules - (exclude_rules or set())))
```

</details>

### Method `_check_all_rules`

```python
def _check_all_rules(self, filename: Path, rules: set) -> Generator[str, None, None]
```

Generate all errors found during checking.

Args:

- `filename` (`Path`): Path to the Python file being checked.
- `rules` (`set`): Set of rule codes to apply during checking.

Yields:

- `str`: Error message for each found issue.

<details>
<summary>Code:</summary>

```python
def _check_all_rules(self, filename: Path, rules: set) -> Generator[str, None, None]:
        try:
            content = filename.read_text(encoding="utf-8")
            lines = content.splitlines()

            yield from self._check_content_rules(filename, lines, rules)

        except Exception as e:
            yield self._format_error("P000", f"Exception error: {e}", filename)
```

</details>

### Method `_check_content_rules`

```python
def _check_content_rules(self, filename: Path, lines: list[str], rules: set) -> Generator[str, None, None]
```

Check content-related rules.

Args:

- `filename` (`Path`): Path to the Python file being checked.
- `lines` (`list[str]`): All lines from the file.
- `rules` (`set`): Set of rule codes to apply during checking.

Yields:

- `str`: Error message for each content-related issue found.

<details>
<summary>Code:</summary>

```python
def _check_content_rules(self, filename: Path, lines: list[str], rules: set) -> Generator[str, None, None]:
        if "HP001" not in rules:
            return

        for line_num, line in enumerate(lines, 1):
            # Check if this line should be ignored for P001
            if self._should_ignore_line(line, "HP001"):
                continue

            if self._has_russian_letters(line):
                col = self._find_russian_letters_position(line)
                yield self._format_error("HP001", self.RULES["HP001"], filename, line_num=line_num, col=col)
```

</details>

### Method `_determine_project_root`

```python
def _determine_project_root(self, project_root: Path | str | None) -> Path
```

Determine the project root directory.

Args:

- `project_root` (`Path | str | None`): Provided project root path.

Returns:

- `Path`: Resolved project root directory.

<details>
<summary>Code:</summary>

```python
def _determine_project_root(self, project_root: Path | str | None) -> Path:
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
```

</details>

### Method `_find_russian_letters_position`

```python
def _find_russian_letters_position(self, text: str) -> int
```

Find the position of the first Russian letter in text (1-based).

Args:

- `text` (`str`): Text to search in.

Returns:

- `int`: Position of the first Russian letter (1-based), or 1 if not found.

<details>
<summary>Code:</summary>

```python
def _find_russian_letters_position(self, text: str) -> int:
        match = re.search(r"[\u0430-\u044F\u0451\u0410-\u042F\u0401]", text)
        return match.start() + 1 if match else 1
```

</details>

### Method `_format_error`

```python
def _format_error(self, error_code: str, message: str, filename: Path) -> str
```

Format error message in ruff style.

Args:

- `error_code` (`str`): The error code (e.g., "HP001").
- `message` (`str`): Description of the error.
- `filename` (`Path`): Path to the file where the error was found.
- `line_num` (`int`): Line number where the error occurred. Defaults to `0`.
- `col` (`int`): Column number where the error occurred. Defaults to `0`.

Returns:

- `str`: Formatted error message in ruff style.

<details>
<summary>Code:</summary>

```python
def _format_error(self, error_code: str, message: str, filename: Path, *, line_num: int = 0, col: int = 0) -> str:
        relative_path = self._get_relative_path(filename)

        location = relative_path
        if line_num > 0:
            location += f":{line_num}"
            if col > 0:
                location += f":{col}"

        return f"{location}: {error_code} {message}"
```

</details>

### Method `_get_relative_path`

```python
def _get_relative_path(self, filename: Path) -> str
```

Get relative path from project root, fallback to absolute if outside project.

Args:

- `filename` (`Path`): Path to the file.

Returns:

- `str`: Relative path from project root or absolute path if outside project.

<details>
<summary>Code:</summary>

```python
def _get_relative_path(self, filename: Path) -> str:
        try:
            return str(filename.resolve().relative_to(self.project_root))
        except ValueError:
            # File is outside project root
            return str(filename.resolve())
```

</details>

### Method `_has_russian_letters`

```python
def _has_russian_letters(self, text: str) -> bool
```

Check if text contains Russian letters.

Args:

- `text` (`str`): Text to check for Russian letters.

Returns:

- `bool`: `True` if text contains Russian letters, `False` otherwise.

<details>
<summary>Code:</summary>

```python
def _has_russian_letters(self, text: str) -> bool:
        return bool(re.search(r"[\u0430-\u044F\u0451\u0410-\u042F\u0401]", text))
```

</details>

### Method `_parse_rules_string`

```python
def _parse_rules_string(self, rules_str: str) -> set[str]
```

Parse comma-separated rules string into a set.

Args:

- `rules_str` (`str`): Comma-separated string of rule codes.

Returns:

- `set[str]`: Set of rule codes.

<details>
<summary>Code:</summary>

```python
def _parse_rules_string(self, rules_str: str) -> set[str]:
        return {rule.strip().upper() for rule in rules_str.split(",") if rule.strip()}
```

</details>

### Method `_should_ignore_line`

```python
def _should_ignore_line(self, line: str, rule_code: str) -> bool
```

Check if a line should be ignored for a specific rule.

Args:

- `line` (`str`): Line content to check.
- `rule_code` (`str`): Rule code to check.

Returns:

- `bool`: `True` if the line should be ignored for this rule, `False` otherwise.

<details>
<summary>Code:</summary>

```python
def _should_ignore_line(self, line: str, rule_code: str) -> bool:
        # Look for ignore pattern anywhere in the line
        match = self.IGNORE_PATTERN.search(line)
        if not match:
            return False

        rules_str = match.group(1)
        ignored_rules = self._parse_rules_string(rules_str)

        return rule_code in ignored_rules
```

</details>
