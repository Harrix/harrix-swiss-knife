import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path

import clr
from PIL import Image, ImageGrab
from PySide6.QtWidgets import QFileDialog, QInputDialog

from harrix_swiss_knife import functions

path_default_articles: str = f"C:/GitHub/_content__harrix-dev/harrix.dev-articles-{datetime.now().year}"


class on_image_clear_images:
    icon: str = "🧹"
    title: str = "Clear the folder `images`"

    @functions.write_in_output_txt(is_show_output=False)
    def __call__(self, *args, **kwargs) -> None:
        path = functions.get_project_root() / "temp" / "images"
        if os.path.exists(path):
            shutil.rmtree(path)
            os.makedirs(path)
            self.__call__.add_line(f"Folder '{path}' is clean.")
        else:
            self.__call__.add_line(f"❌ Folder '{path}' is not exist.")


class on_image_clear_optimized_images:
    icon: str = "🧹"
    title: str = "Clear the folder `optimized_images`"

    @functions.write_in_output_txt(is_show_output=False)
    def __call__(self, *args, **kwargs) -> None:
        path = functions.get_project_root() / "temp" / "optimized_images"
        if os.path.exists(path):
            shutil.rmtree(path)
            os.makedirs(path)
            self.__call__.add_line(f"Folder '{path}' is clean.")
        else:
            self.__call__.add_line(f"❌ Folder '{path}' is not exist.")


class on_image_open_images:
    icon: str = "📂"
    title: str = "Open the folder `images`"

    @functions.write_in_output_txt(is_show_output=False)
    def __call__(self, *args, **kwargs) -> None:
        path = functions.get_project_root() / "temp" / "images"
        if os.path.exists(path):
            os.startfile(path)
            self.__call__.add_line(f"Folder '{path}' is opened.")
        else:
            self.__call__.add_line(f"❌ Folder '{path}' is not exist.")


class on_image_open_optimized_images:
    icon: str = "📂"
    title: str = "Open the folder `optimized_images`"

    @functions.write_in_output_txt(is_show_output=False)
    def __call__(self, *args, **kwargs) -> None:
        path = functions.get_project_root() / "temp" / "optimized_images"
        if os.path.exists(path):
            os.startfile(path)
            self.__call__.add_line(f"Folder '{path}' is opened.")
        else:
            self.__call__.add_line(f"❌ Folder '{path}' is not exist.")


class on_image_optimize_clipboard:
    icon: str = "🚀"
    title: str = "Optimize image from clipboard"

    @functions.write_in_output_txt(is_show_output=False)
    def __call__(self, *args, **kwargs) -> None:
        image = ImageGrab.grabclipboard()

        if not isinstance(image, Image.Image):
            self.__call__.add_line("❌ No image found in the clipboard")
            return

        file_name: str = "image.png"

        if "is_dialog" in kwargs and kwargs["is_dialog"]:
            title: str = "Image name"
            label: str = "Enter the name of the image (English, without spaces):"
            image_name, ok = QInputDialog.getText(None, title, label, text="image")

            if ok and image_name:
                file_name = image_name + ".png"
            else:
                self.__call__.add_line("❌ The name of the image was not entered.")
                return

        temp_dir: Path = Path(tempfile.mkdtemp())
        temp_file_path: Path = temp_dir / file_name
        image.save(temp_file_path, "PNG")
        self.__call__.add_line(f"Image is saved as {temp_file_path}")

        commands: str = f'npm run optimize imagesDir="{temp_dir}" outputDir="optimized_images"'
        result_output = functions.run_powershell_script(commands)

        clr.AddReference("System.Collections.Specialized")
        clr.AddReference("System.Windows.Forms")
        from System.Collections.Specialized import StringCollection
        from System.Windows.Forms import Clipboard

        file_path: Path = functions.get_project_root() / "temp" / "optimized_images" / file_name
        file_path = file_path.resolve()

        files = StringCollection()
        files.Add(str(file_path))
        Clipboard.SetFileDropList(files)

        shutil.rmtree(temp_dir)

        self.__call__.add_line(result_output)
        self.__call__.add_line("Image is optimized and copied to clipboard.")


class on_image_optimize_clipboard_dialog:
    icon: str = "🚀"
    title: str = "Optimize image from clipboard as …"

    @functions.write_in_output_txt(is_show_output=False)
    def __call__(self, *args, **kwargs) -> None:
        on_image_optimize_clipboard.__call__(self, is_dialog=True)


class on_image_optimize_dialog:
    icon: str = "⬆️"
    title: str = "Optimize images in …/temp"

    @functions.write_in_output_txt(is_show_output=True)
    def __call__(self, *args, **kwargs) -> None:
        title: str = "Project directory"
        folder_path: str = QFileDialog.getExistingDirectory(None, title, path_default_articles)

        if not folder_path:
            self.__call__.add_line("❌ The directory was not selected.")
            return

        commands: str = f'npm run optimize imagesDir="{folder_path}"'

        result_output = functions.run_powershell_script(commands)
        os.startfile(Path(folder_path) / "temp")
        self.__call__.add_line(result_output)


class on_image_optimize_dialog_replace:
    icon: str = "⬆️"
    title: str = "Optimize images in … and replace"

    @functions.write_in_output_txt(is_show_output=True)
    def __call__(self, *args, **kwargs) -> None:
        title: str = "Project directory"
        folder_path: str = QFileDialog.getExistingDirectory(None, title, path_default_articles)

        if not folder_path:
            self.__call__.add_line("❌ The directory was not selected.")
            return

        commands: str = f'npm run optimize imagesDir="{folder_path}"'
        result_output = functions.run_powershell_script(commands)

        folder_path = Path(folder_path)

        for item in folder_path.iterdir():
            if item.is_file():
                item.unlink()

        temp_folder: Path = folder_path / "temp"

        for item in temp_folder.iterdir():
            if item.is_file() or item.is_symlink():
                shutil.copy2(item, folder_path / item.name)

        shutil.rmtree(temp_folder)

        os.startfile(folder_path)
        self.__call__.add_line(result_output)


class on_image_optimize_file:
    icon: str = "🖼️"
    title: str = "Optimize one image"

    @functions.write_in_output_txt(is_show_output=True)
    def __call__(self, *args, **kwargs) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "Select an Image File",
            path_default_articles,
            "Image Files (*.jpg *.jpeg *.webp *.png *.svg);;All Files (*)",
        )

        if not file_path:
            self.__call__.add_line("❌ The file was not selected.")
            return

        temp_dir: Path = Path(tempfile.mkdtemp())
        file_name: str = Path(file_path).name
        temp_file_path: Path = temp_dir / file_name
        shutil.copy(file_path, temp_file_path)

        commands: str = f'npm run optimize imagesDir="{temp_dir}" outputDir="optimized_images"'

        result_output = functions.run_powershell_script(commands)

        shutil.rmtree(temp_dir)

        os.startfile(functions.get_project_root() / "temp" / "optimized_images")
        self.__call__.add_line(result_output)


class on_images_optimize:
    icon: str = "🚀"
    title: str = "Optimize images"

    @functions.write_in_output_txt(is_show_output=True)
    def __call__(self, *args, **kwargs) -> None:
        commands: str = "npm run optimize"

        result_output = functions.run_powershell_script(commands)
        os.startfile(functions.get_project_root() / "temp" / "images")
        os.startfile(functions.get_project_root() / "temp" / "optimized_images")
        self.__call__.add_line(result_output)


class on_images_optimize_quality:
    icon: str = "🔝"
    title: str = "Optimize images (high quality)"

    @functions.write_in_output_txt(is_show_output=True)
    def __call__(self, *args, **kwargs) -> None:
        commands: str = "npm run optimize quality=true"

        result_output = functions.run_powershell_script(commands)
        os.startfile(functions.get_project_root() / "temp" / "images")
        os.startfile(functions.get_project_root() / "temp" / "optimized_images")
        self.__call__.add_line(result_output)
