from pathlib import Path
from datetime import datetime

from harrix_swiss_knife import functions

path_diary = "D:/Dropbox/Diaries/Diary"
vscode_workspace = "D:/Dropbox/_Temp/_VS Code Workspaces/Diaries.code-workspace"
beginning_of_md = """---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: ru
---"""


class on_diary_new:
    title = "Add a new diary note"

    @functions.write_in_output_txt(is_show_output=False)
    def __call__(self, *args, **kwargs):
        f = self.__call__
        output, file_path = add_diary_new_diary()
        functions.run_powershell_script(
            f'code-insiders "{vscode_workspace}" "{file_path}"'
        )
        f.add_line(output)


class on_diary_new_with_images:
    title = "Add a new diary note with images"

    @functions.write_in_output_txt(is_show_output=False)
    def __call__(self, *args, **kwargs):
        f = self.__call__
        output, file_path = add_diary_new_diary(is_with_images=True)
        functions.run_powershell_script(
            f'code-insiders "{vscode_workspace}" "{file_path}"'
        )
        f.add_line(output)


def add_diary_new_diary(is_with_images=False):
    text = f"""{beginning_of_md}

# {datetime.now().strftime("%Y-%m-%d")}

## {datetime.now().strftime("%H:%M")}


"""
    return add_diary_new_note(text, is_with_images)


def add_diary_new_note(text, is_with_images):
    current_date = datetime.now()
    year = current_date.strftime("%Y")
    month = current_date.strftime("%m")
    day = current_date.strftime("%Y-%m-%d")

    base_path = Path(path_diary)

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
