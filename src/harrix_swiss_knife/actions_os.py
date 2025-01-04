import os
from pathlib import Path

from PySide6.QtWidgets import QFileDialog

from harrix_swiss_knife import functions

config = functions.load_config("config.json")
config_data = {"path_camera_uploads": config["path_camera_uploads"],"path_github": config["path_github"]}


class on_block_disks:
    icon: str = "🔒"
    title: str = "Block disks"

    def __init__(self, **kwargs): ...

    @functions.write_in_output_txt(is_show_output=True)
    def __call__(self, *args, **kwargs) -> None:
        commands = """
            manage-bde -lock E: -ForceDismount
            manage-bde -lock F: -ForceDismount
            """

        output = functions.run_powershell_script_as_admin(commands)
        self.__call__.add_line(output)


class on_open_camera_uploads:
    icon: str = "📸"
    title: str = "Open Camera Uploads"

    def __init__(self, **kwargs): ...

    @functions.write_in_output_txt(is_show_output=False)
    def __call__(self, *args, **kwargs) -> None:
        folder_path = Path(config_data["path_camera_uploads"])
        os.startfile(folder_path)
        os.startfile(folder_path / "info")
        os.startfile(folder_path / "temp")
        os.startfile(folder_path / "video")
        os.startfile(folder_path / "work")
        os.startfile(folder_path / "work_video")
        os.startfile(folder_path / "screenshots")
        self.__call__.add_line('The folder "Camera Uploads" is opened.')

class on_tree_view_folder:
    icon: str = "├"
    title: str = "Tree view of a folder"

    def __init__(self, **kwargs): ...

    @functions.write_in_output_txt(is_show_output=True)
    def __call__(self, *args, **kwargs) -> None:
        title = "Project directory"
        folder_path = QFileDialog.getExistingDirectory(None, title, config_data["path_github"])

        if not folder_path:
            self.__call__.add_line("❌ The directory was not selected.")
            return

        result_output = functions.tree_view_folder(folder_path, kwargs.get("is_ignore_hidden_dirs", False))

        self.__call__.add_line(result_output)

class on_tree_view_folder_ignore_hidden_folders:
    icon: str = "├"
    title: str = "Tree view of a folder (ignore hidden dirs)"

    def __init__(self, **kwargs): ...

    @functions.write_in_output_txt(is_show_output=True)
    def __call__(self, *args, **kwargs) -> None:
        on_tree_view_folder.__call__(self, is_ignore_hidden_dirs = True)
