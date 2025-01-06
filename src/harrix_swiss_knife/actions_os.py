import os
from pathlib import Path

from PySide6.QtWidgets import QFileDialog

from harrix_swiss_knife import functions

config = functions.load_config("config.json")


class on_all_files_to_parent_folder:
    icon: str = "🗂️"
    title: str = "Moves and flattens files from nested folders"
    tip: str = (
        "The function moves all files from subfolders to their parent folder, removing any then-empty subfolders."
    )

    def __init__(self, **kwargs): ...

    @functions.write_in_output_txt(is_show_output=True)
    def __call__(self, *args, **kwargs) -> None:
        title = "Project folder"
        folder_path = QFileDialog.getExistingDirectory(None, title, config["path_github"])

        if not folder_path:
            self.__call__.add_line("❌ The folder was not selected.")
            return

        result_output = functions.all_files_to_parent_folder(folder_path)

        self.__call__.add_line(result_output)


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


class on_check_featured_image_not_recursively:
    icon: str = "✅"
    title: str = "Check featured_image.* in …"
    tip: str = "Checks for the presence of `featured_image.*` files in every child folder, not recursively."

    def __init__(self, **kwargs): ...

    @functions.write_in_output_txt(is_show_output=True)
    def __call__(self, *args, **kwargs) -> None:
        title = "Folder"
        folder_path = QFileDialog.getExistingDirectory(None, title, config["path_github"])

        if not folder_path:
            self.__call__.add_line("❌ The folder was not selected.")
            return

        try:
            _, result_output = functions.check_featured_image_not_recursively(folder_path)
            self.__call__.add_line(result_output)
        except Exception as e:
            self.__call__.add_line(f"❌ Error: {e}")


class on_check_featured_image_not_recursively_in_folders:
    icon: str = "✅"
    title: str = "Check featured_image.*"

    def __init__(self, **kwargs): ...

    @functions.write_in_output_txt(is_show_output=True)
    def __call__(self, *args, **kwargs) -> None:
        folders_with_featured_image = config["folders_with_featured_image"]

        for path in folders_with_featured_image:
            try:
                _, result_output = functions.check_featured_image_not_recursively(path)
                self.__call__.add_line(result_output)
            except Exception as e:
                self.__call__.add_line(f"❌ Error: {e}")


class on_open_camera_uploads:
    icon: str = "📸"
    title: str = "Open Camera Uploads"

    def __init__(self, **kwargs): ...

    @functions.write_in_output_txt(is_show_output=False)
    def __call__(self, *args, **kwargs) -> None:
        folder_path = Path(config["path_camera_uploads"])
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
        title = "Project folder"
        folder_path = QFileDialog.getExistingDirectory(None, title, config["path_github"])

        if not folder_path:
            self.__call__.add_line("❌ The folder was not selected.")
            return

        result_output = functions.tree_view_folder(folder_path, kwargs.get("is_ignore_hidden_folders", False))

        self.__call__.add_line(result_output)


class on_tree_view_folder_ignore_hidden_folders:
    icon: str = "├"
    title: str = "Tree view of a folder (ignore hidden folders)"

    def __init__(self, **kwargs): ...

    @functions.write_in_output_txt(is_show_output=True)
    def __call__(self, *args, **kwargs) -> None:
        on_tree_view_folder.__call__(self, is_ignore_hidden_folders=True)
