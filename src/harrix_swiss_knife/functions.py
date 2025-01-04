import fnmatch
import json
import os
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Callable, List, Optional

import libcst as cst
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QMenu


def apply_func_to_files(folder: str, ext: str, func: Callable) -> str:
    """
    Applies a given function to all files with a specified extension in a folder and its sub-folders.

    Args:

    - `folder` (`str`): The path to the root folder where the function should be applied. Defaults to `None`.
    - `ext` (`str`): The file extension to filter files by. Should include the dot (e.g., '.py').
    - `func` (`Callable`): The function to apply to each file. This function should take an argument, the file path.

    Returns:

    - `str`: A string listing the results of applying the function to each file, with each result on a new line.
    """
    list_files = []
    for root, dirs, files in os.walk(folder):
        # Exclude all directories and files starting with a dot
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        files = [f for f in files if not f.startswith(".")]

        # Filter and process files with the specified extension
        for filename in fnmatch.filter(files, f"*{ext}"):
            file_path = os.path.join(root, filename)
            try:
                func(file_path)
                list_files.append(f"File {filename} is applied.")
            except Exception:
                list_files.append(f"❌ File {filename} is not applied.")

    return "\n".join(list_files)


def get_project_root() -> Path:
    """
    Finds the root directory of the current project.

    This function traverses up the directory tree from the current file looking for a directory containing
    a `.venv` folder, which is assumed to indicate the project root.

    Returns:

    - `Path`: The path to the project's root directory.

    """
    current_file: Path = Path(__file__).resolve()
    for parent in current_file.parents:
        if (parent / ".venv").exists():
            return parent
    return current_file.parent


def load_config(file_path: str) -> dict:
    """
    Loads configuration from a JSON file.

    Args:

    - `file_path` (`str`): Path to the JSON configuration file. Defaults to `None`.

    Returns:

    - `dict`: Configuration loaded from the file.
    """
    with open(file_path, "r", encoding="utf8") as config_file:
        config = json.load(config_file)
    return config


def pyside_create_emoji_icon(emoji: str, size: int = 32) -> QIcon:
    """
    Creates an icon with the given emoji.

    Args:

    - `emoji` (`str`): The emoji to be used in the icon.
    - `size` (`int`): The size of the icon in pixels. Defaults to `32`.

    Returns:

    - `QIcon`: A QIcon object containing the emoji as an icon.
    """
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    font = QFont()
    font.setPointSize(int(size * 0.8))
    painter.setFont(font)
    painter.drawText(pixmap.rect(), Qt.AlignCenter, emoji)
    painter.end()

    return QIcon(pixmap)


def pyside_generate_markdown_from_qmenu(menu: QMenu, level: int = 0) -> List[str]:
    """
    Generates a markdown representation of a QMenu structure.

    This function traverses the QMenu and its submenus to produce a nested list in markdown format.

    Args:

    - `menu` (`QMenu`): The QMenu object to convert to markdown.
    - `level` (`int`, optional): The current indentation level for nested menus. Defaults to `0`.

    Returns:

    - `List[str]`: A list of strings, each representing a line of markdown text that describes the menu structure.
    """
    markdown_lines: List[str] = []
    for action in menu.actions():
        if action.menu():  # If the action has a submenu
            # Add a header for the submenu
            markdown_lines.append(f'{"  " * level}- **{action.text()}**')
            # Recursively traverse the submenu
            markdown_lines.extend(pyside_generate_markdown_from_qmenu(action.menu(), level + 1))
        else:
            # Add a regular menu item
            if action.text():
                markdown_lines.append(f'{"  " * level}- {action.text()}')
    return markdown_lines


def run_powershell_script(commands: str) -> str:
    """
    Runs a PowerShell script with the given commands.

    This function executes a PowerShell script by concatenating multiple commands into a single command string,
    which is then run through the `subprocess` module. It ensures that the output encoding is set to UTF-8.

    Args:

    - `commands` (`str`): A string containing PowerShell commands to execute.

    Returns:

    - `str`: Combined output and error messages from the PowerShell execution.
    """
    command = ";".join(map(str.strip, commands.strip().splitlines()))

    process = subprocess.run(
        [
            "powershell",
            "-Command",
            (
                "[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; "
                "$OutputEncoding = [System.Text.Encoding]::UTF8; "
                f"{command}"
            ),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return "\n".join(filter(None, [process.stdout, process.stderr]))


def run_powershell_script_as_admin(commands: str) -> str:
    """
    Executes a PowerShell script with administrator privileges and captures the output.

    Args:

    - `commands` (`str`): A string containing the PowerShell commands to execute.

    Returns:

    - `str`: The output from running the PowerShell script.

    Raises:

    - `subprocess.CalledProcessError`: If the PowerShell script execution fails.

    Note:

    - This function creates temporary files to store the script and its output, which are deleted after execution.
    - The function waits for the script to finish and ensures the output file exists before reading from it.
    """
    res_output = []
    command = ";".join(map(str.strip, commands.strip().splitlines()))

    # Create a temporary file with the PowerShell script
    with tempfile.NamedTemporaryFile(suffix=".ps1", delete=False) as tmp_script_file:
        tmp_script_file.write(command.encode("utf-8"))
        tmp_script_path = tmp_script_file.name

    # Create a temporary file for the output
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_output_file:
        tmp_output_path = tmp_output_file.name

    try:
        # Wrapper script that runs the main script and writes the output to a file
        wrapper_script = f"& '{tmp_script_path}' | Out-File -FilePath '{tmp_output_path}' -Encoding UTF8"

        # Save the wrapper script to a temporary file
        with tempfile.NamedTemporaryFile(suffix=".ps1", delete=False) as tmp_wrapper_file:
            tmp_wrapper_file.write(wrapper_script.encode("utf-8"))
            tmp_wrapper_path = tmp_wrapper_file.name

        # Command to run PowerShell with administrator privileges
        cmd = [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            f"Start-Process powershell.exe -ArgumentList '-NoProfile -ExecutionPolicy Bypass -File \"{tmp_wrapper_path}\"' -Verb RunAs",
        ]

        # Start the process
        process = subprocess.Popen(cmd)

        # Wait for the process to finish
        process.wait()

        # Ensure the output file has been created
        while not os.path.exists(tmp_output_path):
            time.sleep(0.1)

        # Wait until the file is fully written (can adjust wait time as needed)
        time.sleep(1)  # Delay to complete writing to the file

        # Read the output data from the file
        with open(tmp_output_path, "r", encoding="utf-8") as f:
            output = f.read()
            res_output.append(output)

    finally:
        # Delete temporary files after execution
        if os.path.exists(tmp_script_path):
            os.remove(tmp_script_path)
        if os.path.exists(tmp_output_path):
            os.remove(tmp_output_path)
        if os.path.exists(tmp_wrapper_path):
            os.remove(tmp_wrapper_path)

    return "\n".join(filter(None, res_output))


def sort_py_code(filename: str) -> None:
    """
    Sorts the Python code in the given file by organizing classes, functions, and statements.

    This function reads a Python file, parses it, sorts classes and functions alphabetically,
    and ensures that class attributes, methods, and other statements within classes are ordered
    in a structured manner. The sorted code is then written back to the file.

    Args:

    - `filename` (`str`): The path to the Python file that needs sorting.

    Returns:

    - `None`: This function does not return a value, it modifies the file in place.

    Note:

    - This function uses `libcst` for parsing and manipulating Python ASTs.
    - Sorting prioritizes initial non-class, non-function statements, followed by sorted classes,
      then sorted functions, and finally any trailing statements.
    - Within classes, `__init__` method is placed first among methods, followed by other methods
      sorted alphabetically.
    """
    with open(filename, "r", encoding="utf-8") as f:
        code: str = f.read()

    module: cst.Module = cst.parse_module(code)

    # Split the module content into initial statements, final statements, classes, and functions
    initial_statements: List[cst.BaseStatement] = []
    final_statements: List[cst.BaseStatement] = []
    class_defs: List[cst.ClassDef] = []
    func_defs: List[cst.FunctionDef] = []

    state: str = "initial"

    for stmt in module.body:
        if isinstance(stmt, cst.ClassDef):
            state = "collecting"
            class_defs.append(stmt)
        elif isinstance(stmt, cst.FunctionDef):
            state = "collecting"
            func_defs.append(stmt)
        else:
            if state == "initial":
                initial_statements.append(stmt)
            else:
                final_statements.append(stmt)

    # Sort classes alphabetically and process each class
    class_defs_sorted: List[cst.ClassDef] = sorted(class_defs, key=lambda cls: cls.name.value)

    sorted_class_defs: List[cst.ClassDef] = []
    for class_def in class_defs_sorted:
        class_body_statements = class_def.body.body

        # Initialize containers
        docstring: Optional[cst.SimpleStatementLine] = None
        class_attributes: List[cst.SimpleStatementLine] = []
        methods: List[cst.FunctionDef] = []
        other_statements: List[cst.BaseStatement] = []

        idx: int = 0
        total_statements: int = len(class_body_statements)

        # Check if there is a docstring
        if total_statements > 0:
            first_stmt = class_body_statements[0]
            if (
                isinstance(first_stmt, cst.SimpleStatementLine)
                and isinstance(first_stmt.body[0], cst.Expr)
                and isinstance(first_stmt.body[0].value, cst.SimpleString)
            ):
                docstring = first_stmt
                idx = 1  # Start from the next statement

        # Process the remaining statements in the class body
        for stmt in class_body_statements[idx:]:
            if isinstance(stmt, cst.SimpleStatementLine) and any(
                isinstance(elem, (cst.Assign, cst.AnnAssign)) for elem in stmt.body
            ):
                # This is a class attribute
                class_attributes.append(stmt)
            elif isinstance(stmt, cst.FunctionDef):
                # This is a class method
                methods.append(stmt)
            else:
                # Other statements (e.g., pass, expressions, etc.)
                other_statements.append(stmt)

        # Process methods: __init__ and other methods
        init_method: Optional[cst.FunctionDef] = None
        other_methods: List[cst.FunctionDef] = []

        for method in methods:
            if method.name.value == "__init__":
                init_method = method
            else:
                other_methods.append(method)

        other_methods_sorted: List[cst.FunctionDef] = sorted(other_methods, key=lambda m: m.name.value)

        if init_method is not None:
            methods_sorted: List[cst.FunctionDef] = [init_method] + other_methods_sorted
        else:
            methods_sorted = other_methods_sorted

        # Assemble the new class body
        new_body: List[cst.BaseStatement] = []
        if docstring:
            new_body.append(docstring)
        new_body.extend(class_attributes)  # Class attributes remain at the top in original order
        new_body.extend(methods_sorted)
        new_body.extend(other_statements)

        new_class_body: cst.IndentedBlock = cst.IndentedBlock(body=new_body)

        # Update the class definition with the new body
        new_class_def: cst.ClassDef = class_def.with_changes(body=new_class_body)
        sorted_class_defs.append(new_class_def)

    # Sort functions alphabetically
    func_defs_sorted: List[cst.FunctionDef] = sorted(func_defs, key=lambda func: func.name.value)

    # Assemble the new module body
    new_module_body: List[cst.BaseStatement] = (
        initial_statements + sorted_class_defs + func_defs_sorted + final_statements
    )

    new_module: cst.Module = module.with_changes(body=new_module_body)

    # Convert the module back to code
    new_code: str = new_module.code

    # Write the sorted code back to the file
    with open(filename, "w", encoding="utf-8") as f:
        f.write(new_code)


def tree_folder(path: Path, is_ignore_hidden_dirs: bool = False) -> str:
    """
    Generates a tree-like representation of directory contents.

    Example output:

    ```text
    ├─ note1
    │  ├─ featured-image.png
    │  └─ note1.md
    └─ note2
        └─ note2.md
    ```

    Args:

    - `path` (`Path`): The root directory path to start the tree from.
    - `is_ignore_hidden_dirs` (`bool`): If `True`, hidden directories (starting with a dot) are excluded from the tree.
      Defaults to `False`.

    Returns:

    - `str`: A string representation of the directory structure with ASCII art tree elements.

    Note:

    - This function uses recursion to traverse directories. It handles `PermissionError`
      by excluding directories without permission.
    - Uses ASCII characters to represent tree branches (`├──`, `└──`, `│`).
    """

    def __tree(path: Path, is_ignore_hidden_dirs: bool = False, prefix: str = ""):
        if is_ignore_hidden_dirs and path.name.startswith("."):
            contents = []
        else:
            try:
                contents = list(path.iterdir())
            except PermissionError:
                contents = []
        pointers = ["├─ "] * (len(contents) - 1) + ["└─ "]
        for pointer, path in zip(pointers, contents):
            yield prefix + pointer + path.name
            if path.is_dir():
                extension = "│  " if pointer == "├─ " else "   "
                yield from __tree(path, is_ignore_hidden_dirs, prefix=prefix + extension)

    return "\n".join([line for line in __tree(Path(path), is_ignore_hidden_dirs)])


def write_in_output_txt(is_show_output: bool = True) -> Callable:
    """
    Decorator to write function output to a temporary file and optionally display it.

    This decorator captures all output of the decorated function into a list,
    measures execution time, and writes this information into an `output.txt` file
    in a temporary directory within the project root. It also offers the option
    to automatically open this file after writing.

    Args:

    - `is_show_output` (`bool`): If `True`, automatically open the output file
      after writing. Defaults to `True`.

    Returns:

    - `Callable`: A decorator function that wraps another function.

    The decorator adds the following methods to the wrapped function:

    - `add_line` (`Callable`): A method to add lines to the output list, which
      will be written to the file.

    Note:

    - This decorator changes the behavior of the decorated function by capturing
      its output and timing its execution.
    - The `output.txt` file is created in a `temp` folder under the project root.
      If the folder does not exist, it will be created.
    - The function uses `os.startfile` to open the file which might not work on
      all platforms or with all file types.
    """

    def decorator(func: Callable) -> Callable:
        output_lines = []

        def wrapper(*args, **kwargs):
            output_lines.clear()
            start_time = time.time()
            func(*args, **kwargs)
            end_time = time.time()
            elapsed_time = end_time - start_time
            wrapper.add_line(f"Execution time: {elapsed_time:.4f} seconds")
            temp_path = get_project_root() / "temp"
            if not temp_path.exists():
                temp_path.mkdir(parents=True, exist_ok=True)
            file = Path(temp_path / "output.txt")
            output_text = "\n".join(output_lines) if output_lines else ""

            file.write_text(output_text, encoding="utf8")
            if is_show_output:
                os.startfile(file)

        def add_line(line: str):
            output_lines.append(line)
            print(line)

        wrapper.add_line = add_line
        return wrapper

    return decorator
