---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `check_python_folder.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnCheckPythonFolder`](#%EF%B8%8F-class-oncheckpythonfolder)
  - [⚙️ Method `check_python_folder_common`](#%EF%B8%8F-method-check_python_folder_common)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread)
  - [⚙️ Method `thread_after`](#%EF%B8%8F-method-thread_after)
  - [⚙️ Method `_check_docstring_section_blank_line_before_list`](#%EF%B8%8F-method-_check_docstring_section_blank_line_before_list)
  - [⚙️ Method `_iter_python_files`](#%EF%B8%8F-method-_iter_python_files)
  - [⚙️ Method `_read_text_best_effort`](#%EF%B8%8F-method-_read_text_best_effort)

</details>

## 🏛️ Class `OnCheckPythonFolder`

```python
class OnCheckPythonFolder(ActionBase)
```

Action to check all Python files in a folder for errors with Harrix rules.

<details>
<summary>Code:</summary>

```python
class OnCheckPythonFolder(ActionBase):

    icon = "🚧"
    title = "Check PY in …"
    cli_available = True
    cli_hint = "python check"

    _DOCSTRING_SECTION_HEADERS_REQUIRING_BLANK_LINE: ClassVar[set[str]] = {
        "Args:",
        "Raises:",
        "Returns:",
        "Yields:",
    }
    _DOCSTRING_SECTION_ERROR_CODE = "HSKPYDOC001"
    _DOCSTRING_LIST_INDENT_ERROR_CODE = "HSKPYDOC002"

    def check_python_folder_common(self) -> None:
        """Check all Python files in ``folder_path`` and log results."""
        checker = h.py_check.PythonChecker()
        if self.folder_path is None:
            return

        errors = h.file.check_func(self.folder_path, ".py", checker)
        folder = Path(self.folder_path)
        docstring_errors: list[str] = []
        for py_file in self._iter_python_files(folder):
            docstring_errors.extend(self._check_docstring_section_blank_line_before_list(py_file))
        if docstring_errors:
            errors = (errors or []) + docstring_errors

        if errors:
            self.add_line("\n".join(errors))
            self.add_line(f"🔢 Count errors = {len(errors)}")
        else:
            self.add_line(f"✅ There are no errors in {self.folder_path}.")

    @ActionBase.handle_exceptions("checking Python folder")
    def execute(
        self,
        *_args: Any,
        folder_path: Path | None = None,
        noninteractive: bool = False,
        **_kwargs: Any,
    ) -> None:
        """Check all Python files in a folder for errors with Harrix rules."""
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
                self.config["paths_python_projects"], self.config["path_github"]
            )
        if not self.folder_path:
            return

        if noninteractive:
            self.add_line(f"🔵 Starting Python check for path: {self.folder_path}")
            self.check_python_folder_common()
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("Python folder checking thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        self.check_python_folder_common()

    @ActionBase.handle_exceptions("Python folder checking thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} {self.folder_path} completed")
        self.show_result()

    def _check_docstring_section_blank_line_before_list(self, path: Path) -> list[str]:
        """Check blank lines and list indentation in docstrings."""
        try:
            content = self._read_text_best_effort(path)
        except (OSError, UnicodeDecodeError) as e:
            return [f"{path}:1:1: {self._DOCSTRING_SECTION_ERROR_CODE} Cannot read file: {e!s}"]

        file_lines = content.splitlines()
        errors: list[str] = []

        # Extract triple-quoted blocks and validate only inside them to avoid false positives
        # from code/SQL strings (e.g., lines starting with '--').
        blocks: list[tuple[int, int]] = []
        in_block = False
        delim: str | None = None
        start_idx = 0

        for idx, line in enumerate(file_lines):
            if not in_block:
                if '"""' in line or "'''" in line:
                    pos_dq = line.find('"""')
                    pos_sq = line.find("'''")
                    delim = '"""' if pos_dq != -1 and (pos_sq == -1 or pos_dq < pos_sq) else "'''"
                    if delim and (line.count(delim) % 2 == 1):
                        in_block = True
                        start_idx = idx
                continue

            if delim and (line.count(delim) % 2 == 1):
                blocks.append((start_idx, idx))
                in_block = False
                delim = None

        for block_start, block_end in blocks:
            lines = file_lines[block_start : block_end + 1]

            for i, line in enumerate(lines):
                header = line.strip()
                if header not in self._DOCSTRING_SECTION_HEADERS_REQUIRING_BLANK_LINE:
                    continue

                header_indent = line[: len(line) - len(line.lstrip())]

                # Find next non-empty line after header
                j = i + 1
                while j < len(lines) and not lines[j].strip():
                    j += 1
                if j >= len(lines):
                    continue

                # Consider only Markdown list items "- " (not "--" and not "-\t")
                if j == i + 1 and lines[j].lstrip().startswith("- "):
                    msg = f"Missing blank line after '{header}' before list"
                    errors.append(f"{path}:{block_start + i + 1}:1: {self._DOCSTRING_SECTION_ERROR_CODE} {msg}")

                # Validate indentation of list items within this section:
                # First-level list items should align with the section header indentation.
                # Nested list items are allowed when they follow a list item and are indented more.
                k = j
                allowed_indents: set[str] = {header_indent}
                prev_list_indent: str | None = None
                prev_was_list_item = False
                while k < len(lines):
                    current = lines[k]
                    stripped = current.strip()
                    if not stripped:
                        prev_was_list_item = False
                        k += 1
                        continue
                    if stripped in self._DOCSTRING_SECTION_HEADERS_REQUIRING_BLANK_LINE:
                        break
                    if current.lstrip().startswith("- "):
                        item_indent = current[: len(current) - len(current.lstrip())]
                        if item_indent in allowed_indents:
                            prev_list_indent = item_indent
                            prev_was_list_item = True
                        # Permit nested list only right after a list item, and only by increasing indentation.
                        elif (
                            prev_was_list_item
                            and prev_list_indent is not None
                            and len(item_indent) > len(prev_list_indent)
                        ):
                            allowed_indents.add(item_indent)
                            prev_list_indent = item_indent
                            prev_was_list_item = True
                        else:
                            msg = f"Unexpected list indentation in '{header}' section"
                            errors.append(
                                f"{path}:{block_start + k + 1}:1: {self._DOCSTRING_LIST_INDENT_ERROR_CODE} {msg}"
                            )
                            prev_list_indent = item_indent
                            prev_was_list_item = True
                    else:
                        prev_was_list_item = False
                    k += 1

        return errors

    def _iter_python_files(self, folder_path: Path) -> list[Path]:
        folder_resolved = folder_path.resolve()
        return [
            py_file
            for py_file in folder_path.rglob("*.py")
            if not h.file.should_ignore_path(py_file.resolve().relative_to(folder_resolved))
        ]

    @staticmethod
    def _read_text_best_effort(path: Path) -> str:
        try:
            return path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return path.read_text(encoding="utf-8-sig")
```

</details>

### ⚙️ Method `check_python_folder_common`

```python
def check_python_folder_common(self) -> None
```

Check all Python files in `folder_path` and log results.

<details>
<summary>Code:</summary>

```python
def check_python_folder_common(self) -> None:
        checker = h.py_check.PythonChecker()
        if self.folder_path is None:
            return

        errors = h.file.check_func(self.folder_path, ".py", checker)
        folder = Path(self.folder_path)
        docstring_errors: list[str] = []
        for py_file in self._iter_python_files(folder):
            docstring_errors.extend(self._check_docstring_section_blank_line_before_list(py_file))
        if docstring_errors:
            errors = (errors or []) + docstring_errors

        if errors:
            self.add_line("\n".join(errors))
            self.add_line(f"🔢 Count errors = {len(errors)}")
        else:
            self.add_line(f"✅ There are no errors in {self.folder_path}.")
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *_args: Any, **_kwargs: Any) -> None
```

Check all Python files in a folder for errors with Harrix rules.

<details>
<summary>Code:</summary>

```python
def execute(
        self,
        *_args: Any,
        folder_path: Path | None = None,
        noninteractive: bool = False,
        **_kwargs: Any,
    ) -> None:
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
                self.config["paths_python_projects"], self.config["path_github"]
            )
        if not self.folder_path:
            return

        if noninteractive:
            self.add_line(f"🔵 Starting Python check for path: {self.folder_path}")
            self.check_python_folder_common()
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)
```

</details>

### ⚙️ Method `in_thread`

```python
def in_thread(self) -> str | None
```

Execute code in a separate thread. For performing long-running operations.

<details>
<summary>Code:</summary>

```python
def in_thread(self) -> str | None:
        self.check_python_folder_common()
```

</details>

### ⚙️ Method `thread_after`

```python
def thread_after(self, result: Any) -> None
```

Execute code in the main thread after in_thread(). For handling the results of thread execution.

<details>
<summary>Code:</summary>

```python
def thread_after(self, result: Any) -> None:  # noqa: ARG002
        self.show_toast(f"{self.title} {self.folder_path} completed")
        self.show_result()
```

</details>

### ⚙️ Method `_check_docstring_section_blank_line_before_list`

```python
def _check_docstring_section_blank_line_before_list(self, path: Path) -> list[str]
```

Check blank lines and list indentation in docstrings.

<details>
<summary>Code:</summary>

```python
def _check_docstring_section_blank_line_before_list(self, path: Path) -> list[str]:
        try:
            content = self._read_text_best_effort(path)
        except (OSError, UnicodeDecodeError) as e:
            return [f"{path}:1:1: {self._DOCSTRING_SECTION_ERROR_CODE} Cannot read file: {e!s}"]

        file_lines = content.splitlines()
        errors: list[str] = []

        # Extract triple-quoted blocks and validate only inside them to avoid false positives
        # from code/SQL strings (e.g., lines starting with '--').
        blocks: list[tuple[int, int]] = []
        in_block = False
        delim: str | None = None
        start_idx = 0

        for idx, line in enumerate(file_lines):
            if not in_block:
                if '"""' in line or "'''" in line:
                    pos_dq = line.find('"""')
                    pos_sq = line.find("'''")
                    delim = '"""' if pos_dq != -1 and (pos_sq == -1 or pos_dq < pos_sq) else "'''"
                    if delim and (line.count(delim) % 2 == 1):
                        in_block = True
                        start_idx = idx
                continue

            if delim and (line.count(delim) % 2 == 1):
                blocks.append((start_idx, idx))
                in_block = False
                delim = None

        for block_start, block_end in blocks:
            lines = file_lines[block_start : block_end + 1]

            for i, line in enumerate(lines):
                header = line.strip()
                if header not in self._DOCSTRING_SECTION_HEADERS_REQUIRING_BLANK_LINE:
                    continue

                header_indent = line[: len(line) - len(line.lstrip())]

                # Find next non-empty line after header
                j = i + 1
                while j < len(lines) and not lines[j].strip():
                    j += 1
                if j >= len(lines):
                    continue

                # Consider only Markdown list items "- " (not "--" and not "-\t")
                if j == i + 1 and lines[j].lstrip().startswith("- "):
                    msg = f"Missing blank line after '{header}' before list"
                    errors.append(f"{path}:{block_start + i + 1}:1: {self._DOCSTRING_SECTION_ERROR_CODE} {msg}")

                # Validate indentation of list items within this section:
                # First-level list items should align with the section header indentation.
                # Nested list items are allowed when they follow a list item and are indented more.
                k = j
                allowed_indents: set[str] = {header_indent}
                prev_list_indent: str | None = None
                prev_was_list_item = False
                while k < len(lines):
                    current = lines[k]
                    stripped = current.strip()
                    if not stripped:
                        prev_was_list_item = False
                        k += 1
                        continue
                    if stripped in self._DOCSTRING_SECTION_HEADERS_REQUIRING_BLANK_LINE:
                        break
                    if current.lstrip().startswith("- "):
                        item_indent = current[: len(current) - len(current.lstrip())]
                        if item_indent in allowed_indents:
                            prev_list_indent = item_indent
                            prev_was_list_item = True
                        # Permit nested list only right after a list item, and only by increasing indentation.
                        elif (
                            prev_was_list_item
                            and prev_list_indent is not None
                            and len(item_indent) > len(prev_list_indent)
                        ):
                            allowed_indents.add(item_indent)
                            prev_list_indent = item_indent
                            prev_was_list_item = True
                        else:
                            msg = f"Unexpected list indentation in '{header}' section"
                            errors.append(
                                f"{path}:{block_start + k + 1}:1: {self._DOCSTRING_LIST_INDENT_ERROR_CODE} {msg}"
                            )
                            prev_list_indent = item_indent
                            prev_was_list_item = True
                    else:
                        prev_was_list_item = False
                    k += 1

        return errors
```

</details>

### ⚙️ Method `_iter_python_files`

```python
def _iter_python_files(self, folder_path: Path) -> list[Path]
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _iter_python_files(self, folder_path: Path) -> list[Path]:
        folder_resolved = folder_path.resolve()
        return [
            py_file
            for py_file in folder_path.rglob("*.py")
            if not h.file.should_ignore_path(py_file.resolve().relative_to(folder_resolved))
        ]
```

</details>

### ⚙️ Method `_read_text_best_effort`

```python
def _read_text_best_effort(path: Path) -> str
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _read_text_best_effort(path: Path) -> str:
        try:
            return path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return path.read_text(encoding="utf-8-sig")
```

</details>
