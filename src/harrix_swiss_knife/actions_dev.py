from PySide6.QtWidgets import QApplication

from harrix_swiss_knife import funcs_dev

config = funcs_dev.dev_load_config("config/config.json")


class on_dev_exit:
    icon: str = "×"
    title: str = "Exit"

    def __init__(self, **kwargs):
        self.parent = kwargs.get("parent", None)

    @funcs_dev.dev_write_in_output_txt(is_show_output=False)
    def __call__(self, *args, **kwargs) -> None:
        if self.parent:
            QApplication.quit()


class on_dev_get_menu:
    icon: str = "☰"
    title: str = "Get the list of items from this menu"

    def __init__(self, **kwargs):
        self.parent = kwargs.get("parent", None)

    @funcs_dev.dev_write_in_output_txt(is_show_output=False)
    def __call__(self, *args, **kwargs) -> None:
        if self.parent:
            self.__call__.add_line(self.parent.get_menu())


class on_dev_open_config_json:
    icon: str = "⚙️"
    title: str = "Open config.json"

    def __init__(self, **kwargs): ...

    @funcs_dev.dev_write_in_output_txt(is_show_output=False)
    def __call__(self, *args, **kwargs) -> None:
        commands = f"{config["editor"]} {funcs_dev.dev_get_project_root() / "config.json"}"
        output = funcs_dev.dev_run_powershell_script(commands)
        self.__call__.add_line(output)
