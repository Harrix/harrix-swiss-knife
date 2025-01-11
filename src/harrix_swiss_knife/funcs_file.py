import os
import platform
import re
import shutil
import subprocess
from pathlib import Path
from typing import Callable


def all_to_parent_folder(path: Path | str) -> str:
    """
    Moves all files from subfolders within the given path to the parent folder and then
    removes empty folders.

    Args:

    - `path` (`Path | str`): The path to the folder whose subfolders you want to flatten.
      Can be either a `Path` object or a string.

    Returns:

    - `str`: A string where each line represents an action taken on a subfolder (e.g., "Fix subfolder_name").

    Notes:

    - This function will print exceptions to stdout if there are issues with moving files or deleting folders.
    - Folders will only be removed if they become empty after moving all files.

    Before:

    ```text
    C:\test
    ├─ folder1
    │  ├─ image.jpg
    │  ├─ sub1
    │  │  ├─ file1.txt
    │  │  └─ file2.txt
    │  └─ sub2
    │     ├─ file3.txt
    │     └─ file4.txt
    └─ folder2
       └─ sub3
          ├─ file6.txt
          └─ sub4
             └─ file5.txt
    ```

    After:

    ```text
    C:\test
    ├─ folder1
    │  ├─ file1.txt
    │  ├─ file2.txt
    │  ├─ file3.txt
    │  ├─ file4.txt
    │  └─ image.jpg
    └─ folder2
       ├─ file5.txt
       └─ file6.txt
    ```
    """
    list_lines = []
    for child_folder in Path(path).iterdir():
        for file in Path(child_folder).glob("**/*"):
            if file.is_file():
                try:
                    file.replace(child_folder / file.name)
                except Exception as exception:
                    print(exception)
        for file in Path(child_folder).glob("**/*"):
            if file.is_dir():
                try:
                    shutil.rmtree(file)
                except Exception as exception:
                    print(exception)
        list_lines.append(f"Fix {child_folder}")
    return "\n".join(list_lines)


def apply_func(folder: str, ext: str, func: Callable) -> str:
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
    folder_path = Path(folder)

    for path in folder_path.rglob(f"*{ext}"):
        # Exclude all folders and files starting with a dot
        if path.is_file() and not any(part.startswith(".") for part in path.parts):
            try:
                func(str(path))
                list_files.append(f"File {path.name} is applied.")
            except Exception:
                list_files.append(f"❌ File {path.name} is not applied.")

    return "\n".join(list_files)


def check_featured_image(path: str) -> tuple[bool, str]:
    """
    Checks for the presence of `featured_image.*` files in every child folder, not recursively.

    This function goes through each immediate subfolder of the given path and checks if there
    is at least one file with the name starting with "featured-image". If such a file is missing
    in any folder, it logs this occurrence.

    Args:

    - `path` (`str`): Path to the folder being checked. Can be either a string or a Path object.

    Returns:

    - `tuple[bool, str]`: A tuple where:
        - The first element (`bool`) indicates if all folders have a `featured_image.*` file.
        - The second element (`str`) contains a formatted string with status or error messages.

    Note:

    - This function does not search recursively; it only checks the immediate child folders.
    - The output string uses ANSI color codes for visual distinction of errors.
    """
    line_list: list[str] = []
    is_correct: bool = True

    for child_folder in Path(path).iterdir():
        is_featured_image: bool = False
        for file in child_folder.iterdir():
            if file.is_file() and file.name.startswith("featured-image"):
                is_featured_image = True
        if not is_featured_image:
            is_correct = False
            line_list.append(f"❌ {child_folder} without featured-image")

    if is_correct:
        line_list.append(f"All correct in {path}")
    return is_correct, "\n".join(line_list)


def find_max_folder_number(base_path: str, start_pattern: str) -> int:
    """
    Finds the highest folder number in a given folder based on a pattern.

    Args:

    - `base_path` (`str`): The base folder path to search for folders.
    - `start_pattern` (`str`): A regex pattern for matching folder names.

    Returns:

    - `int`: The maximum folder number found, or 0 if no matches are found.
    """
    pattern = re.compile(start_pattern + r"(\d+)$")
    max_number: int = 0
    base_path = Path(base_path)

    for item in base_path.iterdir():
        if item.is_dir():
            match = pattern.match(item.name)
            if match:
                number = int(match.group(1))
                if number > max_number:
                    max_number = number

    return max_number


def open_file_or_folder(path: Path | str) -> None:
    """
    Opens a file or folder using the operating system's default application.

    This function checks the operating system and uses the appropriate method to open
    the given path:

    - On **Windows**, it uses `os.startfile`.
    - On **macOS**, it invokes the `open` command.
    - On **Linux**, it uses `xdg-open`.

    Args:

    - `path` (`Path | str`): The path to the file or folder to be opened. Can be either a `Path` object or a string.

    Returns:

    - `None`: This function does not return any value but opens the file or folder in the default application.

    Note:

    - Ensure the path provided is valid and accessible.
    - If the path does not exist or cannot be opened, the function might raise an exception,
      depending on the underlying command's behavior.
    """
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":  # macOS
        subprocess.call(["open", str(path)])
    elif platform.system() == "Linux":
        subprocess.call(["xdg-open", str(path)])
    return


def tree_view_folder(path: Path, is_ignore_hidden_folders: bool = False) -> str:
    """
    Generates a tree-like representation of folder contents.

    Example output:

    ```text
    ├─ note1
    │  ├─ featured-image.png
    │  └─ note1.md
    └─ note2
        └─ note2.md
    ```

    Args:

    - `path` (`Path`): The root folder path to start the tree from.
    - `is_ignore_hidden_folders` (`bool`): If `True`, hidden folders (starting with a dot) are excluded from the tree.
      Defaults to `False`.

    Returns:

    - `str`: A string representation of the folder structure with ASCII art tree elements.

    Note:

    - This function uses recursion to traverse folders. It handles `PermissionError`
      by excluding folders without permission.
    - Uses ASCII characters to represent tree branches (`├──`, `└──`, `│`).
    """

    def __tree(path: Path, is_ignore_hidden_folders: bool = False, prefix: str = ""):
        if is_ignore_hidden_folders and path.name.startswith("."):
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
                yield from __tree(path, is_ignore_hidden_folders, prefix=prefix + extension)

    return "\n".join([line for line in __tree(Path(path), is_ignore_hidden_folders)])
