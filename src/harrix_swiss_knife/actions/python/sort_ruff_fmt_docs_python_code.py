"""Format, sort Python code and generate documentation in a selected folder."""

from __future__ import annotations

from pathlib import Path
from typing import Any, ClassVar

import harrix_pylib as h

from harrix_swiss_knife.actions.common.base import ActionBase
from harrix_swiss_knife.actions.common.git_changed_files import list_changed_python_files
from harrix_swiss_knife.actions.common.python_project import is_python_project
from harrix_swiss_knife.actions.common.subprocess_run import run_argv_output, venv_module_argv, venv_python
from harrix_swiss_knife.actions.markdown import OnBeautifyMd
from harrix_swiss_knife.actions.markdown.new_markdown import OnNewMarkdown
from harrix_swiss_knife.menu_list_markdown import update_readme_list_of_commands


class OnSortRuffFmtDocsPythonCode(ActionBase):
    """Format, sort Python code and generate documentation in a selected folder.

    This action applies a comprehensive code formatting, organization and documentation
    workflow to all Python files in a user-selected directory. The process consists of:

    1. Running `ruff check --select I --fix` to organize and standardize imports
    2. Applying ruff format to enforce consistent code style and formatting
    3. Using a custom sorting function (`h.py.sort_py_code`) to organize code elements
       such as classes, methods, and functions in a consistent order
    4. Formatting Markdown inside Python docstrings (`h.py.PyDocstringFormatter`)
    5. Re-running ruff format after docstring updates
    6. Generating Markdown documentation from Python code using `h.py.generate_md_docs`
    7. Formatting generated Markdown files with the harrix-pylib formatter

    With `only_changed=True` in a Git repository, steps run only for working-tree-changed
    `.py` files, and docs are regenerated only for those sources (docs folder is not wiped).

    """

    icon = "🌟"
    title = "Ruff sort, ruff format, sort, make docs PY in …"
    bold_title = True
    include_docs_generation: ClassVar[bool] = True
    cli_available = True
    cli_hint = "py ruff-sort-docs [--only-changed]"

    def __init__(self, **kwargs) -> None:  # noqa: ANN003
        """Initialize the OnGetMenu action."""
        super().__init__(**kwargs)
        self.parent = kwargs.get("parent")
        self.only_changed = False

    @ActionBase.handle_exceptions("formatting and sorting Python code with docs")
    def execute(
        self,
        *_args: Any,
        folder_path: Path | None = None,
        noninteractive: bool = False,
        apply_prose_fixes: bool = True,
        only_changed: bool = False,
        **_kwargs: Any,
    ) -> None:
        """Format, sort Python code and generate documentation in a selected folder."""
        self.apply_prose_fixes = apply_prose_fixes
        self.only_changed = only_changed
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

        if not is_python_project(self.folder_path):
            self.add_line(f"❌ {self.folder_path} is not a Python project (no pyproject.toml)")
            if not noninteractive:
                self.show_result()
            return

        if noninteractive:
            self.add_line(f"🔵 Starting processing for path: {self.folder_path}")
            self.format_and_sort_python_common(
                str(self.folder_path),
                is_include_docs_generation=self.include_docs_generation,
                only_changed=self.only_changed,
            )
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    def format_and_sort_python_common(
        self,
        folder_path: str,
        *,
        is_include_docs_generation: bool = True,
        only_changed: bool = False,
    ) -> None:
        """Perform common formatting and sorting operations on Python files in a folder.

        Args:

        - `folder_path` (`str`): Path to the folder containing Python files to process.
        - `is_include_docs_generation` (`bool`): Whether to include documentation generation
          and Markdown formatting steps. Defaults to `True`.
        - `only_changed` (`bool`): When `True` and `folder_path` is inside a Git repo,
          process only working-tree-changed `.py` files (and their docs). Outside Git,
          falls back to the full tree. Defaults to `False`.

        """
        root = Path(folder_path).resolve()
        py_files: list[Path] | None = None
        if only_changed:
            py_files = list_changed_python_files(root)
            if py_files is None:
                self.add_line("⚪ `--only-changed`: not a Git repository; processing all Python files")
            elif not py_files:
                self.add_line("✅ `--only-changed`: no changed Python files; nothing to do")
                return
            else:
                self.add_line(f"🔵 `--only-changed`: {len(py_files)} Python file(s)")
                for path in py_files:
                    self.add_line(f"  • {path.relative_to(root).as_posix()}")

        ruff_targets = ["."] if py_files is None else [str(path) for path in py_files]

        self.add_line("🔵 Format and sort imports")
        self.add_line(self._run_venv_ruff(folder_path, "check", "--select", "I", "--fix", *ruff_targets))
        self.add_line(self._run_venv_ruff(folder_path, "format", *ruff_targets))

        self.add_line("🔵 Sort Python code elements")
        try:
            if py_files is None:
                self.add_line(
                    h.file.apply_func(
                        folder_path,
                        ".py",
                        lambda filename: h.py.sort_py_code(filename, is_use_ruff_format=False),
                    )
                )
            else:
                self.add_line(self._apply_to_files(py_files, lambda p: h.py.sort_py_code(p, is_use_ruff_format=False)))
        except Exception as e:
            self.add_line(f"⚠️ Skip sorting Python code elements due to error: {e!s}")

        self.add_line("🔵 Format Markdown in Python docstrings")
        apply_prose_fixes = getattr(self, "apply_prose_fixes", True)
        try:
            formatter = h.py.PyDocstringFormatter(apply_prose_fixes=apply_prose_fixes)
            if py_files is None:
                self.add_line(formatter.format_folder(folder_path))
            else:
                self.add_line(self._apply_to_files(py_files, formatter.format_file))
        except Exception as e:
            self.add_line(f"⚠️ Skip docstring Markdown formatting due to error: {e!s}")

        self.add_line("🔵 Format with Ruff after docstring updates")
        self.add_line(self._run_venv_ruff(folder_path, "format", *ruff_targets))

        if root == h.dev.get_project_root().resolve():
            self.add_line("🔵 Update README List of commands")
            self.add_line(update_readme_list_of_commands())

        if is_include_docs_generation:
            domain = f"https://github.com/{self.config['github_user']}/{root.name}"
            beginning_docs = OnNewMarkdown.apply_personal_data_to_beginning(
                self.config["beginning_of_md_docs"],
                self.config.get("personal_data"),
            )
            if py_files is None:
                self.add_line("🔵 Generate Markdown documentation")
                self.add_line(h.py.generate_md_docs(folder_path, beginning_docs, domain))
                self.add_line("🔵 Format markdown files")
                OnBeautifyMd.beautify_markdown_common(self, folder_path, is_include_summaries_and_combine=False)
            else:
                self.add_line("🔵 Generate Markdown documentation (changed files only)")
                self.add_line(self._generate_md_docs_for_files(root, py_files, beginning_docs))

        self.add_line("🔵 Remove empty folders")
        self.add_line(h.file.remove_empty_folders(folder_path))

    @ActionBase.handle_exceptions("formatting and sorting Python with docs thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        if self.folder_path is None:
            return
        self.format_and_sort_python_common(
            str(self.folder_path),
            is_include_docs_generation=self.include_docs_generation,
            only_changed=bool(getattr(self, "only_changed", False)),
        )

    @ActionBase.handle_exceptions("formatting and sorting Python with docs thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} completed")
        self.show_result()

    @staticmethod
    def _apply_to_files(files: list[Path], func: Any) -> str:
        """Apply `func` to each path and join status lines."""
        lines: list[str] = []
        for path in files:
            result = func(str(path))
            if result is None:
                lines.append(f"✅ {path}")
            elif isinstance(result, str):
                text = result.strip()
                if text and text != "File is not changed.":
                    lines.append(text)
            else:
                lines.append(str(result))
        if not lines:
            return f"ℹ️ {len(files)} file(s) left unchanged."  # noqa: RUF001
        return "\n".join(lines)

    @staticmethod
    def _docs_g_md_relative_path(py_file: Path, src_folder: Path) -> Path:
        """Mirror harrix-pylib docs path mapping for a source file under `src/`."""
        relative_path = py_file.relative_to(src_folder)
        if len(relative_path.parts) > 1:
            return Path(*relative_path.parts[1:]).with_suffix(".g.md")
        return relative_path.with_suffix(".g.md")

    def _generate_md_docs_for_files(
        self,
        project_root: Path,
        py_files: list[Path],
        beginning_of_md: str,
    ) -> str:
        """Regenerate `.g.md` docs for changed sources without wiping `docs/`."""
        src_folder = project_root / "src"
        docs_folder = project_root / "docs"
        docs_folder.mkdir(parents=True, exist_ok=True)
        lines: list[str] = []
        header = beginning_of_md.rstrip("\n")

        for py_file in py_files:
            try:
                py_file.relative_to(src_folder)
            except ValueError:
                lines.append(f"⚪ Skip docs for {py_file.name} (outside src/)")
                continue

            try:
                docs_relative = self._docs_g_md_relative_path(py_file, src_folder)
                docs_body = h.py.generate_md_docs_content(
                    py_file,
                    docs_relative_path=docs_relative,
                )
            except Exception as exc:
                lines.append(f"⚠️ Skip docs for {py_file.name}: {exc}")
                continue

            if not docs_body.strip():
                lines.append(f"⚪ Skip docs for {py_file.name} (empty / no public API)")
                continue

            final_content = f"{header}\n\n{docs_body.lstrip()}" if header else docs_body
            final_content = h.md.generate_toc_with_links_content(final_content)
            final_content = h.md.generate_image_captions_content(final_content)
            target = docs_folder / docs_relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(final_content, encoding="utf-8", newline="\n")
            lines.append(f"✅ Docs updated: {target.relative_to(project_root).as_posix()}")

        if not lines:
            return "ℹ️ No docs updated."  # noqa: RUF001
        return "\n".join(lines)

    def _run_venv_ruff(self, folder_path: str, *ruff_args: str) -> str:
        """Run `ruff` via the project's `.venv` Python, without `uv run`.

        Args:

        - `folder_path` (`str`): Project root that contains `.venv`.
        - `ruff_args` (`str`): Arguments after `python -m ruff`.

        Returns:

        - `str`: Combined stdout and stderr from Ruff.

        """
        project_path = Path(folder_path)
        python = venv_python(project_path)
        if not python.is_file():
            return f"❌ Missing {python}"
        _code, output = run_argv_output(venv_module_argv(project_path, "ruff", *ruff_args), cwd=folder_path)
        return output
