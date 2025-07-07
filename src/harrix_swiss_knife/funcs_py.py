"""Module for optimizing images in Markdown files and content."""

from pathlib import Path

import harrix_pylib as h

from harrix_swiss_knife import action_base


def format_and_sort_python_common(
    self: action_base.ActionBase, folder_path: str, include_docs_generation: bool = False
) -> None:
    """Perform common formatting and sorting operations on Python files in a folder.

    This method applies a series of code formatting and organization operations to all
    Python files in the specified folder, including import sorting with isort, code
    formatting with ruff, and custom code element sorting. Optionally includes
    documentation generation and markdown formatting.

    Args:

    - `folder_path` (`str`): Path to the folder containing Python files to process.
    - `include_docs_generation` (`bool`): Whether to include documentation generation
      and markdown formatting steps. Defaults to `False`.

    Returns:

    - `None`: This method performs operations and logs results but returns nothing.

    Note:

    - The method preserves the exact execution order of operations for consistency.
    - All operations are logged using `self.add_line()` for user feedback.
    - If `include_docs_generation` is `True`, the method will generate markdown
      documentation and format it with prettier.

    """
    # Run isort and ruff format
    self.add_line("🔵 Format and sort imports")
    commands = f"cd {folder_path}\nuv run --active isort .\nuv run --active ruff format"
    self.add_line(h.dev.run_powershell_script(commands))

    # Sort Python code elements
    self.add_line("🔵 Sort Python code elements")
    self.add_line(h.file.apply_func(folder_path, ".py", h.py.sort_py_code))

    if include_docs_generation:
        # Generate markdown documentation
        self.add_line("🔵 Generate markdown documentation")
        domain = f"https://github.com/{self.config['github_user']}/{Path(folder_path).parts[-1]}"
        self.add_line(h.py.generate_md_docs(folder_path, self.config["beginning_of_md_docs"], domain))

        # Format markdown files with prettier
        self.add_line("🔵 Format markdown files")
        commands = f"cd {folder_path}\nprettier --parser markdown --write **/*.md --end-of-line crlf"
        self.add_line(h.dev.run_powershell_script(commands))
