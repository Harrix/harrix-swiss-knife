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
    Applies a specified function to all files with a given extension within a folder.

    Args:

    - `folder` (`str`): The path to the folder containing the files.
    - `ext` (`str`): The file extension to filter by (e.g., ".txt").
    - `func` (`Callable`): The function to apply to each filtered file.

    Returns:

    - `str`: A summary of the results after applying the function to each file.
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


def get_project_root() -> Optional[Path]:
    """
    Locate the project root directory by searching for the ".venv" folder.

    Args:

    Returns:

    - `Optional[Path]`: The absolute path to the project root directory if found, or `None`.
    """
    current_file = Path(__file__).resolve()
    for parent in current_file.parents:
        if (parent / ".venv").exists():
            return parent
    return current_file.parent


def load_config(file_path: str) -> dict:
    """
    Loads a configuration file.

    Args:

    - `file_path` (`str`): The path to the configuration file.

    Returns:

    - `dict`: The configuration data.
    """
    with open(file_path, "r", encoding="utf8") as config_file:
        config = json.load(config_file)
    return config


def pyside_create_emoji_icon(emoji: str, size: int = 32) -> QIcon:
    """
    Creates a QIcon object displaying the specified emoji.

    Args:

    - `emoji` (`str`): The emoji character to display.
    - `size` (`int`, optional): The size of the icon in pixels. Defaults to 32.

    Returns:

    - `QIcon`: A QIcon object containing the rendered emoji.
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
    Recursively traverse the menu and its submenus, generating a Markdown list.

    Args:

    - `menu` (`QMenu`): The menu to traverse.
    - `level` (`int`, optional): The current indentation level. Defaults to `0`.

    Returns:

    - `List[str]`: A list of strings representing the Markdown lines.
    """
    markdown_lines = []
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
    Executes a PowerShell script composed of multiple commands.

    Args:

    - `commands` (`str`): A string containing PowerShell commands separated by newlines.

    Returns:

    - `str`: The combined output from stdout and stderr of the executed script.
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
    Executes PowerShell commands with administrative privileges.

    Args:

    - `commands` (`str`): A string containing PowerShell commands separated by newlines.

    Returns:

    - `str`: The combined output from the executed script's stdout and stderr.
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
    Sorts the classes and functions in a Python file alphabetically.

    This function reads the specified Python file, parses its contents using `libcst`,
    and rearranges the classes and functions in alphabetical order. Class attributes
    and methods are organized within each class, and the sorted code is written back
    to the file.

    Args:

    - `filename` (`str`): The path to the Python file to be sorted.

    Returns:

    - `None`: This function does not return any value.
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


def write_in_output_txt(is_show_output: bool = True) -> Callable:
    """
    Decorator that captures the output of a function and writes it to a text file.

    Args:

    - `is_show_output` (`bool`, optional): Determines whether to automatically open the output file after writing.
      Defaults to `True`.

    Returns:

    - `Callable`: A decorator that wraps the target function with output capturing and writing functionality.
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
