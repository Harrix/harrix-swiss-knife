import os
from pathlib import Path

from harrix_swiss_knife import functions

config = functions.load_config("config.json")
config_data = {"editor": config["editor"]}


class on_open_config_json:
    icon: str = "⚙️"
    title: str = "Open config.json"

    @functions.write_in_output_txt(is_show_output=False)
    def __call__(self, *args, **kwargs) -> None:
        commands = f"{config_data["editor"]} {functions.get_project_root() / "config.json"}"
        output = functions.run_powershell_script(commands)
        self.__call__.add_line(output)
