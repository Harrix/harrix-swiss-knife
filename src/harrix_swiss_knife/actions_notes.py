from pathlib import Path
from datetime import datetime

from harrix_swiss_knife import functions

path_diary = "D:/Dropbox/Diaries/Diary"
path_dream = "D:/Dropbox/Diaries/Dreams"
vscode_workspace = "D:/Dropbox/_Temp/_VS Code Workspaces/Diaries.code-workspace"
beginning_of_md = """---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: ru
---"""


class on_diary_new:
    title = "New diary note"

    @functions.write_in_output_txt(is_show_output=False)
    def __call__(self, *args, **kwargs):
        output, file_path = add_diary_new_diary()
        functions.run_powershell_script(
            f'code-insiders "{vscode_workspace}" "{file_path}"'
        )
        self.__call__.add_line(output)


class on_diary_new_with_images:
    title = "New diary note with images"

    @functions.write_in_output_txt(is_show_output=False)
    def __call__(self, *args, **kwargs):
        output, file_path = add_diary_new_diary(is_with_images=True)
        functions.run_powershell_script(
            f'code-insiders "{vscode_workspace}" "{file_path}"'
        )
        self.__call__.add_line(output)


class on_diary_new_dream:
    title = "New dream note"

    @functions.write_in_output_txt(is_show_output=False)
    def __call__(self, *args, **kwargs):
        output, file_path = add_diary_new_dream()
        functions.run_powershell_script(
            f'code-insiders "{vscode_workspace}" "{file_path}"'
        )
        self.__call__.add_line(output)


def add_diary_new_diary(is_with_images=False):
    text = f"{beginning_of_md}\n\n"
    text += f"# {datetime.now().strftime("%Y-%m-%d")}\n\n"
    text += f"## {datetime.now().strftime("%H:%M")}\n\n"
    return add_diary_new_note(path_diary, text, is_with_images)


def add_diary_new_dream(is_with_images=False):
    text = f"{beginning_of_md}\n\n"
    text += f"# {datetime.now().strftime("%Y-%m-%d")}\n\n"
    text += f"## {datetime.now().strftime("%H:%M")}\n\n"
    text += "`` — .\n\n" * 5
    return add_diary_new_note(path_dream, text, is_with_images)


def add_diary_new_note(base_path, text, is_with_images):
    current_date = datetime.now()
    year = current_date.strftime("%Y")
    month = current_date.strftime("%m")
    day = current_date.strftime("%Y-%m-%d")

    base_path = Path(base_path)

    year_path = base_path / year
    year_path.mkdir(exist_ok=True)

    month_path = year_path / month
    month_path.mkdir(exist_ok=True)

    if is_with_images:
        (month_path / day).mkdir(exist_ok=True)
        (month_path / day / "img").mkdir(exist_ok=True)
        file_path = month_path / day / f"{day}.md"
    else:
        file_path = month_path / f"{day}.md"

    with file_path.open(mode="w", encoding="utf-8") as file:
        file.write(text)

    return f"File {file_path} created.", file_path
