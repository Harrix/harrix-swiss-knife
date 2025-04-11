import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

import clr
import harrix_pylib as h
from PIL import Image, ImageGrab

from harrix_swiss_knife import action_base

config = h.dev.load_config("config/config.json")


class OnClearImages(action_base.ActionBase):
    icon = "🧹"
    title = "Clear folders images"

    def execute(self, *args, **kwargs):
        paths = [h.dev.get_project_root() / "temp/images", h.dev.get_project_root() / "temp/optimized_images"]
        for path in paths:
            if path.exists():
                shutil.rmtree(path)
                path.mkdir(parents=True)
                result = f"Folder `{path}` is clean."
            else:
                result = f"❌ Folder `{path}` is not exist."
            self.add_line(result)
        self.show_result()


class OnOpenImages(action_base.ActionBase):
    icon = "📂"
    title = "Open the folder images"

    def execute(self, *args, **kwargs):
        path = h.dev.get_project_root() / "temp/images"
        if path.exists():
            h.file.open_file_or_folder(path)
            result = f"Folder `{path}` is opened."
        else:
            result = f"❌ Folder `{path}` is not exist."
        self.add_line(result)


class OnOpenOptimizedImages(action_base.ActionBase):
    icon = "📂"
    title = "Open the folder optimized_images"

    def execute(self, *args, **kwargs):
        path = h.dev.get_project_root() / "temp/optimized_images"
        if path.exists():
            h.file.open_file_or_folder(path)
            result = f"Folder `{path}` is opened."
        else:
            result = f"❌ Folder `{path}` is not exist."
        self.add_line(result)


class OnOptimize(action_base.ActionBase):
    icon = "🚀"
    title = "Optimize images"

    def execute(self, *args, **kwargs):
        self.start_thread(self.in_thread, self.thread_after, self.title)

    def in_thread(self):
        return h.dev.run_powershell_script("npm run optimize")

    def thread_after(self, result):
        h.file.open_file_or_folder(h.dev.get_project_root() / "temp/images")
        h.file.open_file_or_folder(h.dev.get_project_root() / "temp/optimized_images")
        self.show_toast("Optimize completed")
        self.add_line(result)
        self.show_result()


class OnOptimizeClipboard(action_base.ActionBase):
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
            from System.Collections.Specialized import StringCollection  # type: ignore
            from System.Windows.Forms import Clipboard  # type: ignore

            filename = h.dev.get_project_root() / "temp/optimized_images" / filename
            filename = filename.resolve()

            files = StringCollection()
            files.Add(str(filename))
            Clipboard.SetFileDropList(files)

        self.add_line(result)
        self.add_line("Image is optimized and copied to clipboard.")


class OnOptimizeClipboardDialog(action_base.ActionBase):
    icon = "🚀"
    title = "Optimize image from clipboard as …"

    def execute(self, *args, **kwargs):
        OnOptimizeClipboard.execute(self, is_dialog=True)


class OnOptimizeDialog(action_base.ActionBase):
    icon = "⬆️"
    title = "Optimize images in …/temp"

    def execute(self, *args, **kwargs):
        self.folder_path = self.get_existing_directory("Select a folder", config["path_articles"])
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    def in_thread(self):
        return h.dev.run_powershell_script(f'npm run optimize imagesFolder="{self.folder_path}"')

    def thread_after(self, result):
        h.file.open_file_or_folder(Path(self.folder_path) / "temp")
        self.show_toast("Optimize completed")
        self.add_line(result)
        self.show_result()


class OnOptimizeDialogReplace(action_base.ActionBase):
    icon = "⬆️"
    title = "Optimize images in … and replace"

    def execute(self, *args, **kwargs):
        self.folder_path = self.get_existing_directory("Select a folder", config["path_articles"])
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    def in_thread(self):
        result = h.dev.run_powershell_script(f'npm run optimize imagesFolder="{self.folder_path}"')

        for item in self.folder_path.iterdir():
            if item.is_file():
                item.unlink()

        temp_folder = self.folder_path / "temp"

        for item in temp_folder.iterdir():
            if item.is_file() or item.is_symlink():
                shutil.copy2(item, self.folder_path / item.name)

        shutil.rmtree(temp_folder)

        return result

    def thread_after(self, result):
        h.file.open_file_or_folder(self.folder_path)
        self.show_toast("Optimize completed")
        self.add_line(result)
        self.show_result()


class OnOptimizeFile(action_base.ActionBase):
    icon = "🖼️"
    title = "Optimize one image"

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
        self.show_result()


class OnOptimizePngToAvif(action_base.ActionBase):
    icon = "➤"
    title = "Optimize images (with PNG to AVIF)"

    def execute(self, *args, **kwargs):
        self.start_thread(self.in_thread, self.thread_after, self.title)

    def in_thread(self):
        return h.dev.run_powershell_script("npm run optimize convertPngToAvif=true")

    def thread_after(self, result):
        h.file.open_file_or_folder(h.dev.get_project_root() / "temp/images")
        h.file.open_file_or_folder(h.dev.get_project_root() / "temp/optimized_images")
        self.show_toast("Optimize completed")
        self.add_line(result)
        self.show_result()


class OnOptimizeQuality(action_base.ActionBase):
    icon = "🔝"
    title = "Optimize images (high quality)"

    def execute(self, *args, **kwargs):
        self.start_thread(self.in_thread, self.thread_after, self.title)

    def in_thread(self):
        return h.dev.run_powershell_script("npm run optimize quality=true")

    def thread_after(self, result):
        h.file.open_file_or_folder(h.dev.get_project_root() / "temp/images")
        h.file.open_file_or_folder(h.dev.get_project_root() / "temp/optimized_images")
        self.show_toast("Optimize completed")
        self.add_line(result)
        self.show_result()
