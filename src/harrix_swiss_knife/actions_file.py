from pathlib import Path

import harrix_pylib as h

from harrix_swiss_knife import action_base

config = h.dev.load_config("config/config.json")


class on_all_files_to_parent_folder(action_base.ActionBase):
    icon = "🗂️"
    title = "Moves and flattens files from nested folders"
    tip: str = (
        "The function moves all files from subfolders to their parent folder, removing any then-empty subfolders."
    )

    def execute(self, *args, **kwargs):
        folder_path = self.get_existing_directory("Select a folder", config["path_3d"])
        if folder_path is None:
            return

        result = h.file.all_to_parent_folder(folder_path)
        self.add_line(result)
        self.show_text_textarea(result)


class on_block_disks(action_base.ActionBase):
    icon = "🔒"
    title = "Block disks"

    def execute(self, *args, **kwargs):
        commands = "\n".join([f"manage-bde -lock {drive}: -ForceDismount" for drive in config["block_drives"]])
        result = h.dev.run_powershell_script_as_admin(commands)
        self.add_line(result)
        self.show_text_textarea(result)


class on_check_featured_image(action_base.ActionBase):
    icon = "✅"
    title = "Check featured_image.* in …"
    tip: str = "Checks for the presence of `featured_image.*` files in every child folder, not recursively."

    def execute(self, *args, **kwargs):
        folder_path = self.get_existing_directory("Select a folder", config["path_3d"])
        if folder_path is None:
            return

        try:
            result = h.file.check_featured_image(folder_path)[1]
        except Exception as e:
            result = f"❌ Error: {e}"
        self.add_line(result)
        self.show_text_textarea(result)


class on_check_featured_image_in_folders(action_base.ActionBase):
    icon = "✅"
    title = "Check featured_image.*"

    def execute(self, *args, **kwargs):
        result_lines = []
        for path in config["paths_with_featured_image"]:
            try:
                result = h.file.check_featured_image(path)[1]
            except Exception as e:
                result = f"❌ Error: {e}"
            self.add_line(result)
            result_lines.append(result)
        self.show_text_textarea("\n".join(result_lines))


class on_open_camera_uploads(action_base.ActionBase):
    icon = "📸"
    title = "Open Camera Uploads"

    def execute(self, *args, **kwargs):
        for path in config["paths_camera_uploads"]:
            h.file.open_file_or_folder(Path(path))
        self.add_line('The folders from "Camera Uploads" is opened.')


class on_tree_view_folder(action_base.ActionBase):
    icon = "├"
    title = "Tree view of a folder"

    def execute(self, *args, **kwargs):
        folder_path = self.get_existing_directory("Select a folder", config["path_3d"])
        if folder_path is None:
            return

        result = h.file.tree_view_folder(folder_path, kwargs.get("is_ignore_hidden_folders", False))
        self.add_line(result)
        self.show_text_textarea(result)


class on_tree_view_folder_ignore_hidden_folders(action_base.ActionBase):
    icon = "├"
    title = "Tree view of a folder (ignore hidden folders)"

    def execute(self, *args, **kwargs):
        on_tree_view_folder.execute(self, is_ignore_hidden_folders=True)
