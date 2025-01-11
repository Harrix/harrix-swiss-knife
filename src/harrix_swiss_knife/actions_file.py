from pathlib import Path

import harrix_pylib as h
from PySide6.QtWidgets import QFileDialog

config = h.dev.load_config("config/config.json")


class on_file_all_files_to_parent_folder:
    icon: str = "🗂️"
    title: str = "Moves and flattens files from nested folders"
    tip: str = (
        "The function moves all files from subfolders to their parent folder, removing any then-empty subfolders."
    )

    def __init__(self, **kwargs): ...

    @h.dev.write_in_output_txt(is_show_output=True)
    def __call__(self, *args, **kwargs) -> None:
        title = "Project folder"
        folder_path = QFileDialog.getExistingDirectory(None, title, config["path_github"])

        if not folder_path:
            self.__call__.add_line("❌ The folder was not selected.")
            return

        self.__call__.add_line(h.file.all_to_parent_folder(folder_path))


class on_file_block_disks:
    icon: str = "🔒"
    title: str = "Block disks"

    def __init__(self, **kwargs): ...

    @h.dev.write_in_output_txt(is_show_output=True)
    def __call__(self, *args, **kwargs) -> None:
        commands = """
            manage-bde -lock E: -ForceDismount
            manage-bde -lock F: -ForceDismount
            """

        output = h.dev.run_powershell_script_as_admin(commands)
        self.__call__.add_line(output)


class on_file_check_featured_image:
    icon: str = "✅"
    title: str = "Check featured_image.* in …"
    tip: str = "Checks for the presence of `featured_image.*` files in every child folder, not recursively."

    def __init__(self, **kwargs): ...

    @h.dev.write_in_output_txt(is_show_output=True)
    def __call__(self, *args, **kwargs) -> None:
        title = "Folder"
        folder_path = QFileDialog.getExistingDirectory(None, title, config["path_3d"])

        if not folder_path:
            self.__call__.add_line("❌ The folder was not selected.")
            return

        try:
            self.__call__.add_line(h.file.check_featured_image(folder_path)[1])
        except Exception as e:
            self.__call__.add_line(f"❌ Error: {e}")


class on_file_check_featured_image_in_folders:
    icon: str = "✅"
    title: str = "Check featured_image.*"

    def __init__(self, **kwargs): ...

    @h.dev.write_in_output_txt(is_show_output=True)
    def __call__(self, *args, **kwargs) -> None:
        paths_with_featured_image = config["paths_with_featured_image"]

        for path in paths_with_featured_image:
            try:
                self.__call__.add_line(h.file.check_featured_image(path)[1])
            except Exception as e:
                self.__call__.add_line(f"❌ Error: {e}")


class on_file_open_camera_uploads:
    icon: str = "📸"
    title: str = "Open Camera Uploads"

    def __init__(self, **kwargs): ...

    @h.dev.write_in_output_txt(is_show_output=False)
    def __call__(self, *args, **kwargs) -> None:
        folder_path = Path(config["path_camera_uploads"])
        h.file.open_file_or_folder(folder_path)
        h.file.open_file_or_folder(folder_path / "info")
        h.file.open_file_or_folder(folder_path / "temp")
        h.file.open_file_or_folder(folder_path / "video")
        h.file.open_file_or_folder(folder_path / "work")
        h.file.open_file_or_folder(folder_path / "work_video")
        h.file.open_file_or_folder(folder_path / "screenshots")
        self.__call__.add_line('The folder "Camera Uploads" is opened.')


class on_file_tree_view_folder:
    icon: str = "├"
    title: str = "Tree view of a folder"

    def __init__(self, **kwargs): ...

    @h.dev.write_in_output_txt(is_show_output=True)
    def __call__(self, *args, **kwargs) -> None:
        title = "Project folder"
        folder_path = QFileDialog.getExistingDirectory(None, title, config["path_github"])

        if not folder_path:
            self.__call__.add_line("❌ The folder was not selected.")
            return

        result_output = h.file.tree_view_folder(folder_path, kwargs.get("is_ignore_hidden_folders", False))
        self.__call__.add_line(result_output)


class on_file_tree_view_folder_ignore_hidden_folders:
    icon: str = "├"
    title: str = "Tree view of a folder (ignore hidden folders)"

    def __init__(self, **kwargs): ...

    @h.dev.write_in_output_txt(is_show_output=True)
    def __call__(self, *args, **kwargs) -> None:
        on_file_tree_view_folder.__call__(self, is_ignore_hidden_folders=True)
