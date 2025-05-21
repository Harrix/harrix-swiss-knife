---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# File `markdown_checker.py`

<details>
<summary>📖 Contents</summary>

## Contents

- [Class `MarkdownChecker`](#class-markdownchecker)
  - [Method `__init__`](#method-__init__)
  - [Method `__call__`](#method-__call__)
  - [Method `_check_content`](#method-_check_content)
  - [Method `_check_filename`](#method-_check_filename)
  - [Method `_check_yaml`](#method-_check_yaml)
  - [Method `check`](#method-check)

</details>

## Class `MarkdownChecker`

```python
class MarkdownChecker
```

Class for checking Markdown files for compliance with specified rules.

Rules:

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

<details>
<summary>Code:</summary>

```python
class MarkdownChecker:

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

    def _check_content(self, filename: Path, content_md: str, rules: set) -> list:
        """Check markdown content for style issues."""
        errors = []

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
                errors.append(f"❌ H006 {i} - Markdown is written with a small letter in {filename}: {line}")

        return errors

    def _check_filename(self, filename: Path, rules: set) -> list:
        """Check filename for spaces."""
        errors = []

        if "H001" in rules and " " in str(filename.name):
            errors.append(f"❌ H001 Presence of a space in the Markdown file name {filename}.")

        if "H002" in rules and " " in str(filename):
            errors.append(f"❌ H002 Presence of a space in the path to the Markdown file {filename}.")

        return errors

    def _check_yaml(self, filename: Path, yaml_md: str, rules: set) -> list:
        """Check YAML for required fields."""
        errors = []

        try:
            data_yaml = yaml.safe_load(yaml_md.replace("---\n", "").replace("\n---", ""))
            if not data_yaml:
                errors.append(f"❌ H003 YAML is missing in {filename}.")
            else:
                lang = data_yaml.get("lang")
                if "H004" in rules and not lang:
                    errors.append(f"❌ H004 The lang field is missing in YAML in {filename}.")
                elif "H005" in rules and lang not in ["en", "ru"]:
                    errors.append(f"❌ H005 In YAML, lang is not set to en or ru in {filename}.")
        except Exception as e:  # noqa: BLE001
            errors.append(f"❌ YAML {e} in {filename}.")

        return errors

    def check(self, filename: Path | str, exclude_rules: set | None = None) -> list:
        """Check Markdown file for compliance with specified rules.

        Args:
        - `filename` (`Path | str`): Path to the Markdown file to check.
        - `exclude_rules` (`set | None`): Set of rule codes to exclude from checking. Defaults to `None`.

        Returns:

        - `list`: List of error messages found during checking.

        """
        rules = self.all_rules - (set() if exclude_rules is None else exclude_rules)
        errors = []

        filename = Path(filename)

        # Check filename and path
        errors.extend(self._check_filename(filename, rules))

        try:
            with Path.open(filename, encoding="utf-8") as f:
                markdown_text = f.read()

            yaml_md, content_md = h.md.split_yaml_content(markdown_text)

            # Check YAML
            errors.extend(self._check_yaml(filename, yaml_md, rules))

            # Check content
            errors.extend(self._check_content(filename, content_md, rules))

        except Exception as e:  # noqa: BLE001
            errors.append(f"❌ Error reading or processing file: {e} in {filename}.")

        return errors
```

</details>

### Method `__init__`

```python
def __init__(self) -> None
```

Initialize the MarkdownChecker with all available rules.

<details>
<summary>Code:</summary>

```python
def __init__(self) -> None:
        number_rules = 6
        self.all_rules = {f"H{i:03d}" for i in range(1, number_rules + 1)}
```

</details>

### Method `__call__`

```python
def __call__(self, filename: Path | str, exclude_rules: set | None = None) -> list
```

Check Markdown file for compliance with specified rules.

Args:

- `filename` (`Path | str`): Path to the Markdown file to check.
- `exclude_rules` (`set | None`): Set of rule codes to exclude from checking. Defaults to `None`.

Returns:

- `list`: List of error messages found during checking.

<details>
<summary>Code:</summary>

```python
def __call__(self, filename: Path | str, exclude_rules: set | None = None) -> list:
        return self.check(filename, exclude_rules)
```

</details>

### Method `_check_content`

```python
def _check_content(self, filename: Path, content_md: str, rules: set) -> list
```

Check markdown content for style issues.

<details>
<summary>Code:</summary>

```python
def _check_content(self, filename: Path, content_md: str, rules: set) -> list:
        errors = []

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
                errors.append(f"❌ H006 {i} - Markdown is written with a small letter in {filename}: {line}")

        return errors
```

</details>

### Method `_check_filename`

```python
def _check_filename(self, filename: Path, rules: set) -> list
```

Check filename for spaces.

<details>
<summary>Code:</summary>

```python
def _check_filename(self, filename: Path, rules: set) -> list:
        errors = []

        if "H001" in rules and " " in str(filename.name):
            errors.append(f"❌ H001 Presence of a space in the Markdown file name {filename}.")

        if "H002" in rules and " " in str(filename):
            errors.append(f"❌ H002 Presence of a space in the path to the Markdown file {filename}.")

        return errors
```

</details>

### Method `_check_yaml`

```python
def _check_yaml(self, filename: Path, yaml_md: str, rules: set) -> list
```

Check YAML for required fields.

<details>
<summary>Code:</summary>

```python
def _check_yaml(self, filename: Path, yaml_md: str, rules: set) -> list:
        errors = []

        try:
            data_yaml = yaml.safe_load(yaml_md.replace("---\n", "").replace("\n---", ""))
            if not data_yaml:
                errors.append(f"❌ H003 YAML is missing in {filename}.")
            else:
                lang = data_yaml.get("lang")
                if "H004" in rules and not lang:
                    errors.append(f"❌ H004 The lang field is missing in YAML in {filename}.")
                elif "H005" in rules and lang not in ["en", "ru"]:
                    errors.append(f"❌ H005 In YAML, lang is not set to en or ru in {filename}.")
        except Exception as e:  # noqa: BLE001
            errors.append(f"❌ YAML {e} in {filename}.")

        return errors
```

</details>

### Method `check`

```python
def check(self, filename: Path | str, exclude_rules: set | None = None) -> list
```

Check Markdown file for compliance with specified rules.

Args:

- `filename` (`Path | str`): Path to the Markdown file to check.
- `exclude_rules` (`set | None`): Set of rule codes to exclude from checking. Defaults to `None`.

Returns:

- `list`: List of error messages found during checking.

<details>
<summary>Code:</summary>

```python
def check(self, filename: Path | str, exclude_rules: set | None = None) -> list:
        rules = self.all_rules - (set() if exclude_rules is None else exclude_rules)
        errors = []

        filename = Path(filename)

        # Check filename and path
        errors.extend(self._check_filename(filename, rules))

        try:
            with Path.open(filename, encoding="utf-8") as f:
                markdown_text = f.read()

            yaml_md, content_md = h.md.split_yaml_content(markdown_text)

            # Check YAML
            errors.extend(self._check_yaml(filename, yaml_md, rules))

            # Check content
            errors.extend(self._check_content(filename, content_md, rules))

        except Exception as e:  # noqa: BLE001
            errors.append(f"❌ Error reading or processing file: {e} in {filename}.")

        return errors
```

</details>
