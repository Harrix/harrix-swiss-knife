from pathlib import Path

import harrix_pylib as h
from PySide6.QtWidgets import QFileDialog

from harrix_swiss_knife import action_base

config = h.dev.load_config("config/config.json")


class on_file_all_files_to_parent_folder(action_base.ActionBase):
    icon: str = "🗂️"
    title: str = "Moves and flattens files from nested folders"
    tip: str = (
        "The function moves all files from subfolders to their parent folder, removing any then-empty subfolders."
    )
    is_show_output = True

    def execute(self, *args, **kwargs):
        folder_path = self.get_existing_directory("Select a Project folder", config["path_github"])
        if folder_path is None:
            return

        self.add_line(h.file.all_to_parent_folder(folder_path))


class on_file_block_disks(action_base.ActionBase):
    icon: str = "🔒"
    title: str = "Block disks"
    is_show_output = True

    def execute(self, *args, **kwargs):
        commands = ""
        for drive in config["block_drives"]:
            commands += f"manage-bde -lock {drive}: -ForceDismount\n"

        output = h.dev.run_powershell_script_as_admin(commands)
        self.add_line(output)


class on_file_check_featured_image(action_base.ActionBase):
    icon: str = "✅"
    title: str = "Check featured_image.* in …"
    tip: str = "Checks for the presence of `featured_image.*` files in every child folder, not recursively."
    is_show_output = True

    def execute(self, *args, **kwargs):
        folder_path = self.get_existing_directory("Select a folder", config["path_3d"])
        if folder_path is None:
            return

        try:
            self.add_line(h.file.check_featured_image(folder_path)[1])
        except Exception as e:
            self.add_line(f"❌ Error: {e}")


class on_file_check_featured_image_in_folders(action_base.ActionBase):
    icon: str = "✅"
    title: str = "Check featured_image.*"
    is_show_output = True

    def execute(self, *args, **kwargs):
        for path in config["paths_with_featured_image"]:
            try:
                self.add_line(h.file.check_featured_image(path)[1])
            except Exception as e:
                self.add_line(f"❌ Error: {e}")


class on_file_open_camera_uploads(action_base.ActionBase):
    icon: str = "📸"
    title: str = "Open Camera Uploads"

    def execute(self, *args, **kwargs):
        folder_path = Path(config["path_camera_uploads"])
        h.file.open_file_or_folder(folder_path)
        h.file.open_file_or_folder(folder_path / "info")
        h.file.open_file_or_folder(folder_path / "temp")
        h.file.open_file_or_folder(folder_path / "video")
        h.file.open_file_or_folder(folder_path / "work")
        h.file.open_file_or_folder(folder_path / "work_video")
        h.file.open_file_or_folder(folder_path / "screenshots")
        self.add_line('The folder "Camera Uploads" is opened.')


class on_file_tree_view_folder(action_base.ActionBase):
    icon: str = "├"
    title: str = "Tree view of a folder"
    is_show_output = True

    def execute(self, *args, **kwargs):
        folder_path = self.get_existing_directory("Select a Project folder", config["path_github"])
        if folder_path is None:
            return

        result_output = h.file.tree_view_folder(folder_path, kwargs.get("is_ignore_hidden_folders", False))
        self.add_line(result_output)


class on_file_tree_view_folder_ignore_hidden_folders(action_base.ActionBase):
    icon: str = "├"
    title: str = "Tree view of a folder (ignore hidden folders)"
    is_show_output = True

    def execute(self, *args, **kwargs):
        on_file_tree_view_folder.execute(self, is_ignore_hidden_folders=True)
