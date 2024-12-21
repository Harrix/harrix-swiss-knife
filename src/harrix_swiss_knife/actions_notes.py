from pathlib import Path
from datetime import datetime

from harrix_swiss_knife import functions

path_diary = "D:/Dropbox/Diaries/Diary"


class on_diary_new:
    title = "Add a new diary note"

    @functions.write_in_output_txt
    def __call__(self, *args, **kwargs):
        f = on_diary_new.__call__

        current_date = datetime.now()
        year = current_date.strftime("%Y")
        month = current_date.strftime("%m")
        day = current_date.strftime("%Y-%m-%d")

        base_path = Path(path_diary)

        year_path = base_path / year
        year_path.mkdir(exist_ok=True)

        month_path = year_path / month
        month_path.mkdir(exist_ok=True)

        file_path = month_path / f"{day}.md"

        with file_path.open(mode="w", encoding="utf-8") as file:
            file.write(f"""---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: ru
---

# {day}

## {current_date.strftime("%H:%M")}


""")

        f.add_line(f"File {file_path} was successfully created.")
