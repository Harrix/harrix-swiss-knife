from datetime import datetime
from pathlib import Path

from PySide6.QtWidgets import QFileDialog, QInputDialog

from harrix_swiss_knife import functions

config = functions.dev_load_config("config/config.json")


class on_markdown_add_author_book:
    icon: str = "❞"
    title: str = "Quotes. Add author and title"

    def __init__(self, **kwargs): ...

    @functions.dev_write_in_output_txt(is_show_output=True)
    def __call__(self, *args, **kwargs) -> None:
        title = "Folder"
        folder_path = QFileDialog.getExistingDirectory(None, title, config["path_quotes"])

        if not folder_path:
            self.__call__.add_line("❌ The folder was not selected.")
            return

        try:
            result_output = functions.file_apply_func(folder_path, ".md", functions.markdown_add_author_book)
            self.__call__.add_line(result_output)
        except Exception as e:
            self.__call__.add_line(f"❌ Error: {e}")


class on_markdown_diary_new:
    icon: str = "📖"
    title = "New diary note"

    def __init__(self, **kwargs): ...

    @functions.dev_write_in_output_txt(is_show_output=False)
    def __call__(self, *args, **kwargs) -> None:
        output, file_path = markdown_add_diary_new_diary()
        functions.dev_run_powershell_script(f'{config["editor"]} "{config["vscode_workspace_diaries"]}" "{file_path}"')
        self.__call__.add_line(output)


class on_markdown_diary_new_dream:
    icon: str = "💤"
    title = "New dream note"

    def __init__(self, **kwargs): ...

    @functions.dev_write_in_output_txt(is_show_output=False)
    def __call__(self, *args, **kwargs) -> None:
        output, file_path = markdown_add_diary_new_dream()
        functions.dev_run_powershell_script(f'{config["editor"]} "{config["vscode_workspace_diaries"]}" "{file_path}"')
        self.__call__.add_line(output)


class on_markdown_diary_new_with_images:
    icon: str = "📚"
    title = "New diary note with images"

    def __init__(self, **kwargs): ...

    @functions.dev_write_in_output_txt(is_show_output=False)
    def __call__(self, *args, **kwargs) -> None:
        output, file_path = markdown_add_diary_new_diary(is_with_images=True)
        functions.dev_run_powershell_script(f'{config["editor"]} "{config["vscode_workspace_diaries"]}" "{file_path}"')
        self.__call__.add_line(output)


class on_markdown_new_article:
    icon: str = "✍️"
    title = "New article"

    def __init__(self, **kwargs): ...

    @functions.dev_write_in_output_txt(is_show_output=False)
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
        text += f"\n# {article_name}\n\n\n"

        output, file_path = functions.markdown_add_note(Path(config["path_articles"]), article_name, text, True)
        functions.dev_run_powershell_script(f'{config["editor"]} "{config["vscode_workspace_articles"]}" "{file_path}"')
        self.__call__.add_line(output)


class on_markdown_new_note_dialog:
    icon: str = "📓"
    title = "New note"

    def __init__(self, **kwargs): ...

    @functions.dev_write_in_output_txt(is_show_output=False)
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
        text += f"\n# {note_name}\n\n\n"

        output, file_path = functions.markdown_add_note(folder_path, note_name, text, is_with_images)
        functions.dev_run_powershell_script(f'{config["editor"]} "{config["vscode_workspace_notes"]}" "{file_path}"')
        self.__call__.add_line(output)


class on_markdown_new_note_dialog_with_images:
    icon: str = "📓"
    title = "New note with images"

    def __init__(self, **kwargs): ...

    @functions.dev_write_in_output_txt(is_show_output=False)
    def __call__(self, *args, **kwargs) -> None:
        on_markdown_new_note_dialog.__call__(self, is_with_images=True)


def markdown_add_diary_new_diary(is_with_images: bool = False) -> str | Path:
    """
    Creates a new diary entry for the current day and time.

    Args:

    - `is_with_images` (`bool`): Whether to create folders for images. Defaults to `False`.

    Returns:

    - `str | Path`: The path to the created diary entry file or a string message indicating creation.
    """
    text = f"{config['beginning_of_md']}\n\n"
    text += f"# {datetime.now().strftime('%Y-%m-%d')}\n\n"
    text += f"## {datetime.now().strftime('%H:%M')}\n\n"
    return markdown_add_diary_new_note(config["path_diary"], text, is_with_images)


def markdown_add_diary_new_dream(is_with_images: bool = False) -> str | Path:
    """
    Creates a new dream diary entry for the current day and time with placeholders for dream descriptions.

    Args:

    - `is_with_images` (`bool`): Whether to create folders for images. Defaults to `False`.

    Returns:

    - `str | Path`: The path to the created dream diary entry file or a string message indicating creation.
    """
    text = f"{config['beginning_of_md']}\n"
    text += f"# {datetime.now().strftime('%Y-%m-%d')}\n\n"
    text += f"## {datetime.now().strftime('%H:%M')}\n\n"
    text += "`` — не помню.\n\n" * 15 + "`` — не помню.\n"
    return markdown_add_diary_new_note(config["path_dream"], text, is_with_images)


def markdown_add_diary_new_note(base_path: str | Path, text: str, is_with_images: bool) -> str | Path:
    """
    Adds a new note to the diary or dream diary for the given base path.

    Args:

    - `base_path` (`str | Path`): The base path where the note should be added.
    - `text` (`str`): The content to write in the note.
    - `is_with_images` (`bool`): Whether to create a folder for images alongside the note.

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

    return functions.markdown_add_note(month_path, day, text, is_with_images)
