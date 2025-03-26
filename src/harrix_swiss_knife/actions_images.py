import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

import clr
import harrix_pylib as h
from PIL import Image, ImageGrab

from harrix_swiss_knife import action_base

config = h.dev.load_config("config/config.json")


class on_clear_images(action_base.ActionBase):
    icon = "🧹"
    title = "Clear folders images"

    def execute(self, *args, **kwargs):
        paths = [h.dev.get_project_root() / "temp/images", h.dev.get_project_root() / "temp" / "optimized_images"]
        for path in paths:
            if path.exists():
                shutil.rmtree(path)
                path.mkdir(parents=True)
                self.add_line(f"Folder `{path}` is clean.")
            else:
                self.add_line(f"❌ Folder `{path}` is not exist.")


class on_open_images(action_base.ActionBase):
    icon = "📂"
    title = "Open the folder images"

    def execute(self, *args, **kwargs):
        path = h.dev.get_project_root() / "temp" / "images"
        if path.exists():
            h.file.open_file_or_folder(path)
            self.add_line(f"Folder `{path}` is opened.")
        else:
            self.add_line(f"❌ Folder `{path}` is not exist.")


class on_open_optimized_images(action_base.ActionBase):
    icon = "📂"
    title = "Open the folder optimized_images"

    def execute(self, *args, **kwargs):
        path = h.dev.get_project_root() / "temp" / "optimized_images"
        if path.exists():
            h.file.open_file_or_folder(path)
            self.add_line(f"Folder `{path}` is opened.")
        else:
            self.add_line(f"❌ Folder `{path}` is not exist.")


class on_optimize(action_base.ActionBase):
    icon = "🚀"
    title = "Optimize images"
    is_show_output = True

    def execute(self, *args, **kwargs):
        result = h.dev.run_powershell_script("npm run optimize")
        h.file.open_file_or_folder(h.dev.get_project_root() / "temp" / "images")
        h.file.open_file_or_folder(h.dev.get_project_root() / "temp" / "optimized_images")
        self.add_line(result)


class on_optimize_clipboard(action_base.ActionBase):
    icon = "🚀"
    title = "Optimize image from clipboard"

    def execute(self, *args, **kwargs):
        image = ImageGrab.grabclipboard()

        if not isinstance(image, Image.Image):
            self.add_line("❌ No image found in the clipboard")
            return

        filename = "image.png"

        if "is_dialog" in kwargs and kwargs["is_dialog"]:
            image_name = self.get_text_input("Image name", "Enter the name of the image (English, without spaces):")
            if not image_name:
                return
            filename = image_name.replace(" ", "-") + ".png"

        with TemporaryDirectory() as temp_folder:
            temp_filename = Path(temp_folder) / filename
            image.save(temp_filename, "PNG")
            self.add_line(f"Image is saved as {temp_filename}")

            commands = f'npm run optimize imagesFolder="{temp_folder}" outputFolder="optimized_images"'
            result = h.dev.run_powershell_script(commands)

            clr.AddReference("System.Collections.Specialized")
            clr.AddReference("System.Windows.Forms")
            from System.Collections.Specialized import StringCollection
            from System.Windows.Forms import Clipboard

            filename = h.dev.get_project_root() / "temp/optimized_images" / filename
            filename = filename.resolve()

            files = StringCollection()
            files.Add(str(filename))
            Clipboard.SetFileDropList(files)

        self.add_line(result)
        self.add_line("Image is optimized and copied to clipboard.")


class on_optimize_clipboard_dialog(action_base.ActionBase):
    icon = "🚀"
    title = "Optimize image from clipboard as …"

    def execute(self, *args, **kwargs):
        on_optimize_clipboard.execute(self, is_dialog=True)


class on_optimize_dialog(action_base.ActionBase):
    icon = "⬆️"
    title = "Optimize images in …/temp"
    is_show_output = True

    def execute(self, *args, **kwargs):
        folder_path = self.get_existing_directory("Select a folder", config["path_articles"])
        if not folder_path:
            return

        result = h.dev.run_powershell_script(f'npm run optimize imagesFolder="{folder_path}"')
        h.file.open_file_or_folder(Path(folder_path) / "temp")
        self.add_line(result)


class on_optimize_dialog_replace(action_base.ActionBase):
    icon = "⬆️"
    title = "Optimize images in … and replace"
    is_show_output = True

    def execute(self, *args, **kwargs):
        folder_path = self.get_existing_directory("Select a folder", config["path_articles"])
        if not folder_path:
            return

        result = h.dev.run_powershell_script(f'npm run optimize imagesFolder="{folder_path}"')

        for item in folder_path.iterdir():
            if item.is_file():
                item.unlink()

        temp_folder = folder_path / "temp"

        for item in temp_folder.iterdir():
            if item.is_file() or item.is_symlink():
                shutil.copy2(item, folder_path / item.name)

        shutil.rmtree(temp_folder)

        h.file.open_file_or_folder(folder_path)
        self.add_line(result)


class on_optimize_file(action_base.ActionBase):
    icon = "🖼️"
    title = "Optimize one image"
    is_show_output = True

    def execute(self, *args, **kwargs):
        filename = self.get_open_filename(
            "Select an Image File",
            config["path_articles"],
            "Image Files (*.jpg *.jpeg *.webp *.png *.svg);;All Files (*)",
        )
        if not filename:
            return

        with TemporaryDirectory() as temp_folder:
            temp_filename = Path(temp_folder) / Path(filename).name
            shutil.copy(filename, temp_filename)

            commands: str = f'npm run optimize imagesFolder="{temp_folder}" outputFolder="optimized_images"'
            result = h.dev.run_powershell_script(commands)

        h.file.open_file_or_folder(h.dev.get_project_root() / "temp/optimized_images")
        self.add_line(result)


class on_optimize_quality(action_base.ActionBase):
    icon = "🔝"
    title = "Optimize images (high quality)"
    is_show_output = True

    def execute(self, *args, **kwargs):
        result = h.dev.run_powershell_script("npm run optimize quality=true")
        h.file.open_file_or_folder(h.dev.get_project_root() / "temp/images")
        h.file.open_file_or_folder(h.dev.get_project_root() / "temp/optimized_images")
        self.add_line(result)
