from pathlib import Path

import harrix_pylib as h

from harrix_swiss_knife import action_base

config = h.dev.load_config("config/config.json")


class OnAllFilesToParentFolder(action_base.ActionBase):
    icon = "🗂️"
    title = "Moves and flattens files from nested folders"

    def execute(self, *args, **kwargs):
        folder_path = self.get_existing_directory("Select a folder", config["path_3d"])
        if folder_path is None:
            return

        result = h.file.all_to_parent_folder(folder_path)
        self.add_line(result)
        self.show_result()


class OnBlockDisks(action_base.ActionBase):
    icon = "🔒"
    title = "Block disks"

    def execute(self, *args, **kwargs):
        commands = "\n".join([f"manage-bde -lock {drive}: -ForceDismount" for drive in config["block_drives"]])
        result = h.dev.run_powershell_script_as_admin(commands)
        self.add_line(result)
        self.show_result()


class OnCheckFeaturedImage(action_base.ActionBase):
    icon = "✅"
    title = "Check featured_image.* in …"

    def execute(self, *args, **kwargs):
        folder_path = self.get_existing_directory("Select a folder", config["path_3d"])
        if folder_path is None:
            return

        try:
            result = h.file.check_featured_image(folder_path)[1]
        except Exception as e:
            result = f"❌ Error: {e}"
        self.add_line(result)
        self.show_result()


class OnCheckFeaturedImageInFolders(action_base.ActionBase):
    icon = "✅"
    title = "Check featured_image.*"

    def execute(self, *args, **kwargs):
        for path in config["paths_with_featured_image"]:
            try:
                result = h.file.check_featured_image(path)[1]
            except Exception as e:
                result = f"❌ Error: {e}"
            self.add_line(result)
        self.show_result()


class OnOpenCameraUploads(action_base.ActionBase):
    icon = "📸"
    title = "Open Camera Uploads"

    def execute(self, *args, **kwargs):
        for path in config["paths_camera_uploads"]:
            h.file.open_file_or_folder(Path(path))
        self.add_line('The folders from "Camera Uploads" is opened.')


class OnTreeViewFolder(action_base.ActionBase):
    icon = "├"
    title = "Tree view of a folder"

    def execute(self, *args, **kwargs):
        folder_path = self.get_existing_directory("Select a folder", config["path_3d"])
        if folder_path is None:
            return

        result = h.file.tree_view_folder(folder_path, kwargs.get("is_ignore_hidden_folders", False))
        self.add_line(result)
        self.show_result()


class OnTreeViewFolderIgnoreHiddenFolders(action_base.ActionBase):
    icon = "├"
    title = "Tree view of a folder (ignore hidden folders)"

    def execute(self, *args, **kwargs):
        OnTreeViewFolder.execute(self, is_ignore_hidden_folders=True)


class RenameLargestImagesToFeaturedImage(action_base.ActionBase):
    icon = "🖲️"
    title = "Rename largest images to featured_image.* in …"

    def execute(self, *args, **kwargs):
        folder_path = self.get_existing_directory("Select a folder", config["path_3d"])
        if folder_path is None:
            return

        try:
            result = h.file.rename_largest_images_to_featured(folder_path)
        except Exception as e:
            result = f"❌ Error: {e}"
        self.add_line(result)
        self.show_result()
