import os
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Callable, List, Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QMenu


def create_emoji_icon(emoji: str, size: int = 32) -> QIcon:
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


def generate_markdown_from_qmenu(menu: QMenu, level: int = 0) -> List[str]:
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
            markdown_lines.extend(generate_markdown_from_qmenu(action.menu(), level + 1))
        else:
            # Add a regular menu item
            if action.text():
                markdown_lines.append(f'{"  " * level}- {action.text()}')
    return markdown_lines


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
