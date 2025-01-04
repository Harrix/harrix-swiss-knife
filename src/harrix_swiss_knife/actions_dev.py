from harrix_swiss_knife import functions

config = functions.load_config("config.json")
config_data = {"editor": config["editor"]}


class on_get_menu:
    icon: str = "☰"
    title: str = "Get the list of items from this menu"

    def __init__(self, **kwargs):
        self.parent = kwargs.get('parent', None)

    @functions.write_in_output_txt(is_show_output=False)
    def __call__(self, *args, **kwargs) -> None:
        if self.parent:
            self.__call__.add_line(self.parent.get_menu())


class on_open_config_json:
    icon: str = "⚙️"
    title: str = "Open config.json"

    def __init__(self, **kwargs):
        ...

    @functions.write_in_output_txt(is_show_output=False)
    def __call__(self, *args, **kwargs) -> None:
        commands = f"{config_data["editor"]} {functions.get_project_root() / "config.json"}"
        output = functions.run_powershell_script(commands)
        self.__call__.add_line(output)
