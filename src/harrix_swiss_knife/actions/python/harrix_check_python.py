"""Check Python files with Harrix PY rules and docstring Markdown typography (incl. private)."""

from __future__ import annotations

import ast
import tempfile
from pathlib import Path
from typing import Any, ClassVar

import harrix_pylib as h

from harrix_swiss_knife.actions.common.base import ActionBase

# Matches harrix_pylib.py.check_python_docstring_markdown_errors exclude set.
_DOCSTRING_MD_EXCLUDE_RULES: frozenset[str] = frozenset(
    {
        "H001",
        "H002",
        "H003",
        "H004",
        "H005",
        "H011",
        "H046",
        "H047",
        "H082",
        "H083",
        "H086",
        "H087",
        "H089",
        "H090",
        "H091",
        "H092",
        "H093",
    }
)


class OnHarrixCheckPython(ActionBase):
    """Check Python files with Harrix PY rules and docstring Markdown typography (incl. private)."""

    icon = "🚧"
    title = "Harrix PY check in …"
    cli_available = True
    cli_hint = "py harrix-check"

    selected_python_files: list[Path] | None = None

    _DOCSTRING_SECTION_HEADERS_REQUIRING_BLANK_LINE: ClassVar[set[str]] = {
        "Args:",
        "Raises:",
        "Returns:",
        "Yields:",
    }
    _DOCSTRING_SECTION_ERROR_CODE = "HSKPYDOC001"
    _DOCSTRING_LIST_INDENT_ERROR_CODE = "HSKPYDOC002"

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
            self.add_line(f"🔵 Starting Harrix PY check for path: {self.folder_path}")
            self.harrix_check_python_common()
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    def harrix_check_python_common(self) -> None:
        """Check Python files in `folder_path` (or `selected_python_files`) and log results."""
        self.last_error_count = 0
        checker = h.py_check.PyChecker()
        if self.folder_path is None:
            return

        folder = Path(self.folder_path)
        selected = getattr(self, "selected_python_files", None)
        py_files = list(selected) if selected is not None else self._iter_python_files(folder)

        errors: list[str] = []
        if selected is None:
            errors = h.file.check_func(self.folder_path, ".py", checker) or []
        else:
            for py_file in h.file.iter_with_progress(py_files):
                file_errors = checker.check(py_file)
                if file_errors:
                    errors.extend(file_errors)

        docstring_errors: list[str] = []
        for py_file in h.file.iter_with_progress(py_files):
            docstring_errors.extend(self._check_docstring_section_blank_line_before_list(py_file))
        if docstring_errors:
            errors.extend(docstring_errors)

        self.add_line("🔵 Starting docstring Markdown check (incl. private, locations in .py)")
        if selected is None:
            md_doc_errors = h.py.check_python_docstring_markdown_errors(folder, include_private=True)
        else:
            md_doc_errors = self._check_docstring_markdown_for_files(folder, py_files, include_private=True)
        if md_doc_errors:
            errors.extend(md_doc_errors)

        self.last_error_count = len(errors)
        if errors:
            for index, error in enumerate(errors):
                if index:
                    self.add_line("")
                self.add_line(error)
            self.add_line("")
            self.add_line(f"🔢 Count errors = {len(errors)}")
        else:
            self.add_line(f"✅ There are no errors in {self.folder_path}.")

    @ActionBase.handle_exceptions("python folder checking thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        self.harrix_check_python_common()

    @ActionBase.handle_exceptions("python folder checking thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} {self.folder_path} completed")
        self.show_result()

    def _check_docstring_markdown_for_files(
        self,
        folder: Path,
        py_files: list[Path],
        *,
        include_private: bool = True,
    ) -> list[str]:
        """Run docstring Markdown checks only for the given Python files."""
        src_folder = folder / "src"
        if not src_folder.is_dir():
            return []

        md_checker = h.md_check.MdChecker()
        errors: list[str] = []
        scoped_files: list[Path] = []
        for py_file in py_files:
            try:
                py_file.resolve().relative_to(src_folder.resolve())
            except ValueError:
                continue
            scoped_files.append(py_file)

        with tempfile.TemporaryDirectory(prefix="hsk-py-docstring-md-") as temp_dir:
            temp_root = Path(temp_dir)
            for py_file in h.file.iter_with_progress(scoped_files):
                if not h.py._is_docs_python_file(py_file):  # noqa: SLF001
                    continue
                try:
                    with py_file.open(encoding="utf-8") as source_file:
                        tree = ast.parse(source_file.read(), filename=str(py_file))
                except (OSError, SyntaxError, UnicodeDecodeError):
                    continue
                if not h.py._has_documented_entities(tree, include_private=include_private):  # noqa: SLF001
                    continue
                content, line_map = h.py.generate_md_docs_content_with_source_map(
                    py_file,
                    include_private=include_private,
                )
                relative = h.py._docs_g_md_relative_path(py_file, src_folder)  # noqa: SLF001
                md_path = temp_root / relative
                md_path.parent.mkdir(parents=True, exist_ok=True)
                md_path.write_text(content, encoding="utf-8", newline="\n")
                errors.extend(
                    h.py.remap_markdown_docs_error(error, line_map)
                    for error in md_checker.check(md_path, exclude_rules=set(_DOCSTRING_MD_EXCLUDE_RULES))
                )
        return errors

    def _check_docstring_section_blank_line_before_list(self, path: Path) -> list[str]:
        """Check blank lines and list indentation in docstrings."""
        try:
            content = self._read_text_best_effort(path)
        except (OSError, UnicodeDecodeError) as e:
            return [f"{path}:1:1: {self._DOCSTRING_SECTION_ERROR_CODE}\n  Cannot read file: {e!s}"]

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
                    errors.append(f"{path}:{block_start + i + 1}:1: {self._DOCSTRING_SECTION_ERROR_CODE}\n  {msg}")

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
                                f"{path}:{block_start + k + 1}:1: {self._DOCSTRING_LIST_INDENT_ERROR_CODE}\n  {msg}"
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
