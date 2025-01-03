from datetime import datetime
from pathlib import Path
from typing import Tuple

from PySide6.QtWidgets import QFileDialog

from harrix_swiss_knife import functions

path_diary = "D:/Dropbox/Diaries/Diary"
path_dream = "D:/Dropbox/Diaries/Dreams"
path_notes = "D:/Dropbox/Notes/Notes"
path_github: str = "C:/GitHub"
vscode_workspace_diaries = "D:/Dropbox/_Temp/_VS Code Workspaces/Diaries.code-workspace"
vscode_workspace_notes = "D:/Dropbox/_Temp/_VS Code Workspaces/Notes.code-workspace"
beginning_of_md = """---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: ru
---"""


class on_diary_new:
    icon: str = "📖"
    title = "New diary note"

    @functions.write_in_output_txt(is_show_output=False)
    def __call__(self, *args, **kwargs) -> None:
        output, file_path = add_diary_new_diary()
        functions.run_powershell_script(f'code-insiders "{vscode_workspace_diaries}" "{file_path}"')
        self.__call__.add_line(output)


class on_diary_new_dream:
    icon: str = "💤"
    title = "New dream note"

    @functions.write_in_output_txt(is_show_output=False)
    def __call__(self, *args, **kwargs) -> None:
        output, file_path = add_diary_new_dream()
        functions.run_powershell_script(f'code-insiders "{vscode_workspace_diaries}" "{file_path}"')
        self.__call__.add_line(output)


class on_diary_new_with_images:
    icon: str = "📚"
    title = "New diary note with images"

    @functions.write_in_output_txt(is_show_output=False)
    def __call__(self, *args, **kwargs) -> None:
        output, file_path = add_diary_new_diary(is_with_images=True)
        functions.run_powershell_script(f'code-insiders "{vscode_workspace_diaries}" "{file_path}"')
        self.__call__.add_line(output)


class on_new_note_dialog:
    icon: str = "📓"
    title = "New note"

    @functions.write_in_output_txt(is_show_output=False)
    def __call__(self, *args, **kwargs) -> None:
        file_path, _ = QFileDialog.getSaveFileName(None, "Save Note", path_notes, "Markdown (*.md);;All Files (*)")

        if file_path:
            path = Path(file_path)

            folder_path = path.parent
            note_name = path.stem

            self.__call__.add_line(f"Folder path: {folder_path}")
            self.__call__.add_line(f"File name without extension: {note_name}")
        else:
            self.__call__.add_line("❌ No file was selected.")
            return

        is_with_images = kwargs.get("is_with_images", False)

        text = beginning_of_md
        text += f"\n\n# {note_name}\n\n\n"

        output, file_path = add_note(folder_path, note_name, text, is_with_images)
        functions.run_powershell_script(f'code-insiders "{vscode_workspace_notes}" "{file_path}"')
        self.__call__.add_line(output)


class on_new_note_dialog_with_images:
    icon: str = "📓"
    title = "New note with images"

    @functions.write_in_output_txt(is_show_output=False)
    def __call__(self, *args, **kwargs) -> None:
        on_new_note_dialog.__call__(self, is_with_images=True)


def add_diary_new_diary(is_with_images: bool = False) -> Tuple[str, Path]:
    """
    Creates a new diary entry with the current date and time.

    Args:

    - `is_with_images` (`bool`, optional): Determines whether to include images in the diary entry. Defaults to `False`.

    Returns:

    - `Tuple[str, Path]`: A tuple containing the diary text and the path to the diary file.
    """
    text = f"{beginning_of_md}\n\n"
    text += f"# {datetime.now().strftime('%Y-%m-%d')}\n\n"
    text += f"## {datetime.now().strftime('%H:%M')}\n\n"
    return add_diary_new_note(path_diary, text, is_with_images)


def add_diary_new_dream(is_with_images: bool = False) -> Tuple[str, Path]:
    """
    Creates a new dream diary entry with the current date and time.

    Args:

    - `is_with_images` (`bool`, optional): Determines whether to include images in the dream diary entry. Defaults to `False`.

    Returns:

    - `Tuple[str, Path]`: A tuple containing the dream diary text and the path to the diary file.
    """
    text = f"{beginning_of_md}\n\n"
    text += f"# {datetime.now().strftime('%Y-%m-%d')}\n\n"
    text += f"## {datetime.now().strftime('%H:%M')}\n\n"
    text += "`` — не помню.\n\n" * 15 + "`` — не помню.\n"
    return add_diary_new_note(path_dream, text, is_with_images)


def add_diary_new_note(base_path: str, text: str, is_with_images: bool) -> Tuple[str, Path]:
    """
    Creates a new diary note file in the specified path, organizing directories by year and month.

    Args:

    - `base_path` (`str`): The base directory path where the diary note will be created.
    - `text` (`str`): The content to write into the diary note.
    - `is_with_images` (`bool`): Determines whether to create an images directory alongside the diary note.

    Returns:

    - `Tuple[str, Path]`: A tuple containing a success message and the path to the created diary file.
    """
    current_date = datetime.now()
    year = current_date.strftime("%Y")
    month = current_date.strftime("%m")
    day = current_date.strftime("%Y-%m-%d")

    base_path = Path(base_path)

    year_path = base_path / year
    year_path.mkdir(exist_ok=True)

    month_path = year_path / month
    month_path.mkdir(exist_ok=True)

    return add_note(month_path, day, text, is_with_images)


def add_note(base_path: str, name: str, text: str, is_with_images: bool) -> Tuple[str, Path]:
    """
    Adds a note by creating a Markdown file, optionally with an images directory.

    Args:

    - `base_path` (`str`): The base directory path where the note will be added.
    - `name` (`str`): The name of the note.
    - `text` (`str`): The content of the note.
    - `is_with_images` (`bool`): Flag indicating whether to create an images directory.

    Returns:

    - `Tuple[str, Path]`: A tuple containing a success message and the path to the created file.
    """
    base_path = Path(base_path)

    if is_with_images:
        (base_path / name).mkdir(exist_ok=True)
        (base_path / name / "img").mkdir(exist_ok=True)
        file_path = base_path / name / f"{name}.md"
    else:
        file_path = base_path / f"{name}.md"

    print("is_with_images", is_with_images)
    print("+", file_path)

    with file_path.open(mode="w", encoding="utf-8") as file:
        file.write(text)

    return f"File {file_path} created.", file_path
