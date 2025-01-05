from datetime import datetime
from pathlib import Path

from PySide6.QtWidgets import QFileDialog, QInputDialog

from harrix_swiss_knife import functions

config = functions.load_config("config.json")


class on_diary_new:
    icon: str = "📖"
    title = "New diary note"

    def __init__(self, **kwargs): ...

    @functions.write_in_output_txt(is_show_output=False)
    def __call__(self, *args, **kwargs) -> None:
        output, file_path = add_diary_new_diary()
        functions.run_powershell_script(f'{config["editor"]} "{config["vscode_workspace_diaries"]}" "{file_path}"')
        self.__call__.add_line(output)


class on_diary_new_dream:
    icon: str = "💤"
    title = "New dream note"

    def __init__(self, **kwargs): ...

    @functions.write_in_output_txt(is_show_output=False)
    def __call__(self, *args, **kwargs) -> None:
        output, file_path = add_diary_new_dream()
        functions.run_powershell_script(f'{config["editor"]} "{config["vscode_workspace_diaries"]}" "{file_path}"')
        self.__call__.add_line(output)


class on_diary_new_with_images:
    icon: str = "📚"
    title = "New diary note with images"

    def __init__(self, **kwargs): ...

    @functions.write_in_output_txt(is_show_output=False)
    def __call__(self, *args, **kwargs) -> None:
        output, file_path = add_diary_new_diary(is_with_images=True)
        functions.run_powershell_script(f'{config["editor"]} "{config["vscode_workspace_diaries"]}" "{file_path}"')
        self.__call__.add_line(output)


class on_new_article:
    icon: str = "✍️"
    title = "New article"

    def __init__(self, **kwargs): ...

    @functions.write_in_output_txt(is_show_output=False)
    def __call__(self, *args, **kwargs) -> None:
        title: str = "Article title"
        label: str = "Enter the name of the article (English, without spaces):"
        article_name, ok = QInputDialog.getText(None, title, label)

        if not (ok and article_name):
            self.__call__.add_line("❌ The name of the article was not entered.")
            return

        article_name = article_name.replace(" ", "-")

        text = config["beginning_of_article"].replace("[YEAR]", datetime.now().strftime("%Y"))
        text = text.replace("[NAME]", article_name)
        text = text.replace("[DATE]", datetime.now().strftime("%Y-%m-%d"))
        text += f"\n\n# {article_name}\n\n\n"

        output, file_path = add_note(Path(config["path_articles"]), article_name, text, True)
        functions.run_powershell_script(f'{config["editor"]} "{config["vscode_workspace_articles"]}" "{file_path}"')
        self.__call__.add_line(output)


class on_new_note_dialog:
    icon: str = "📓"
    title = "New note"

    def __init__(self, **kwargs): ...

    @functions.write_in_output_txt(is_show_output=False)
    def __call__(self, *args, **kwargs) -> None:
        file_path, _ = QFileDialog.getSaveFileName(
            None, "Save Note", config["path_notes"], "Markdown (*.md);;All Files (*)"
        )

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

        text = config["beginning_of_md"]
        text += f"\n\n# {note_name}\n\n\n"

        output, file_path = add_note(folder_path, note_name, text, is_with_images)
        functions.run_powershell_script(f'{config["editor"]} "{config["vscode_workspace_notes"]}" "{file_path}"')
        self.__call__.add_line(output)


class on_new_note_dialog_with_images:
    icon: str = "📓"
    title = "New note with images"

    def __init__(self, **kwargs): ...

    @functions.write_in_output_txt(is_show_output=False)
    def __call__(self, *args, **kwargs) -> None:
        on_new_note_dialog.__call__(self, is_with_images=True)


def add_diary_new_diary(is_with_images: bool = False) -> str | Path:
    """
    Creates a new diary entry for the current day and time.

    Args:

    - `is_with_images` (`bool`): Whether to create directories for images. Defaults to `False`.

    Returns:

    - `str | Path`: The path to the created diary entry file or a string message indicating creation.
    """
    text = f"{config['beginning_of_md']}\n\n"
    text += f"# {datetime.now().strftime('%Y-%m-%d')}\n\n"
    text += f"## {datetime.now().strftime('%H:%M')}\n\n"
    return add_diary_new_note(config["path_diary"], text, is_with_images)


def add_diary_new_dream(is_with_images: bool = False) -> str | Path:
    """
    Creates a new dream diary entry for the current day and time with placeholders for dream descriptions.

    Args:

    - `is_with_images` (`bool`): Whether to create directories for images. Defaults to `False`.

    Returns:

    - `str | Path`: The path to the created dream diary entry file or a string message indicating creation.
    """
    text = f"{config['beginning_of_md']}\n\n"
    text += f"# {datetime.now().strftime('%Y-%m-%d')}\n\n"
    text += f"## {datetime.now().strftime('%H:%M')}\n\n"
    text += "`` — не помню.\n\n" * 15 + "`` — не помню.\n"
    return add_diary_new_note(config["path_dream"], text, is_with_images)


def add_diary_new_note(base_path: str | Path, text: str, is_with_images: bool) -> str | Path:
    """
    Adds a new note to the diary or dream diary for the given base path.

    Args:

    - `base_path` (`str | Path`): The base path where the note should be added.
    - `text` (`str`): The content to write in the note.
    - `is_with_images` (`bool`): Whether to create a directory for images alongside the note.

    Returns:

    - `str | Path`: A string message indicating the file was created along with the file path.
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


def add_note(base_path: str | Path, name: str, text: str, is_with_images: bool) -> str | Path:
    """
    Adds a note to the specified base path.

    Args:

    - `base_path` (`str | Path`): The path where the note will be added.
    - `name` (`str`): The name for the note file or directory.
    - `text` (`str`): The text content for the note.
    - `is_with_images` (`bool`): If true, creates directories for images.

    Returns:

    - `str | Path`: A tuple containing a message about file creation and the path to the file.
    """
    base_path = Path(base_path)

    if is_with_images:
        (base_path / name).mkdir(exist_ok=True)
        (base_path / name / "img").mkdir(exist_ok=True)
        file_path = base_path / name / f"{name}.md"
    else:
        file_path = base_path / f"{name}.md"

    with file_path.open(mode="w", encoding="utf-8") as file:
        file.write(text)

    return f"File {file_path} created.", file_path
