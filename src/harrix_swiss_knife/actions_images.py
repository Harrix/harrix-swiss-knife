import shutil
import tempfile
from pathlib import Path

import clr
from PIL import Image, ImageGrab
from PySide6.QtWidgets import QFileDialog, QInputDialog

from harrix_swiss_knife import functions

config = functions.load_config("config.json")


class on_image_clear_images:
    icon: str = "🧹"
    title: str = "Clear the folder images"

    def __init__(self, **kwargs): ...

    @functions.write_in_output_txt(is_show_output=False)
    def __call__(self, *args, **kwargs) -> None:
        path = functions.get_project_root() / "temp" / "images"
        if path.exists():
            shutil.rmtree(path)
            path.mkdir(parents=True)
            self.__call__.add_line(f"Folder `{path}` is clean.")
        else:
            self.__call__.add_line(f"❌ Folder `{path}` is not exist.")


class on_image_clear_optimized_images:
    icon: str = "🧹"
    title: str = "Clear the folder optimized_images"

    def __init__(self, **kwargs): ...

    @functions.write_in_output_txt(is_show_output=False)
    def __call__(self, *args, **kwargs) -> None:
        path = functions.get_project_root() / "temp" / "optimized_images"
        if path.exists():
            shutil.rmtree(path)
            path.mkdir(parents=True)
            self.__call__.add_line(f"Folder `{path}` is clean.")
        else:
            self.__call__.add_line(f"❌ Folder `{path}` is not exist.")


class on_image_open_images:
    icon: str = "📂"
    title: str = "Open the folder images"

    def __init__(self, **kwargs): ...

    @functions.write_in_output_txt(is_show_output=False)
    def __call__(self, *args, **kwargs) -> None:
        path = functions.get_project_root() / "temp" / "images"
        if path.exists():
            functions.os_open_file_or_folder(path)
            self.__call__.add_line(f"Folder `{path}` is opened.")
        else:
            self.__call__.add_line(f"❌ Folder `{path}` is not exist.")


class on_image_open_optimized_images:
    icon: str = "📂"
    title: str = "Open the folder optimized_images"

    def __init__(self, **kwargs): ...

    @functions.write_in_output_txt(is_show_output=False)
    def __call__(self, *args, **kwargs) -> None:
        path = functions.get_project_root() / "temp" / "optimized_images"
        if path.exists():
            functions.os_open_file_or_folder(path)
            self.__call__.add_line(f"Folder `{path}` is opened.")
        else:
            self.__call__.add_line(f"❌ Folder `{path}` is not exist.")


class on_image_optimize_clipboard:
    icon: str = "🚀"
    title: str = "Optimize image from clipboard"

    def __init__(self, **kwargs): ...

    @functions.write_in_output_txt(is_show_output=False)
    def __call__(self, *args, **kwargs) -> None:
        image = ImageGrab.grabclipboard()

        if not isinstance(image, Image.Image):
            self.__call__.add_line("❌ No image found in the clipboard")
            return

        filename: str = "image.png"

        if "is_dialog" in kwargs and kwargs["is_dialog"]:
            title: str = "Image name"
            label: str = "Enter the name of the image (English, without spaces):"
            image_name, ok = QInputDialog.getText(None, title, label, text="image")

            if ok and image_name:
                filename = image_name.replace(" ", "-") + ".png"
            else:
                self.__call__.add_line("❌ The name of the image was not entered.")
                return

        temp_folder: Path = Path(tempfile.mkdtemp())
        temp_file_path: Path = temp_folder / filename
        image.save(temp_file_path, "PNG")
        self.__call__.add_line(f"Image is saved as {temp_file_path}")

        commands: str = f'npm run optimize imagesFolder="{temp_folder}" outputFolder="optimized_images"'
        result_output = functions.run_powershell_script(commands)

        clr.AddReference("System.Collections.Specialized")
        clr.AddReference("System.Windows.Forms")
        from System.Collections.Specialized import StringCollection
        from System.Windows.Forms import Clipboard

        file_path: Path = functions.get_project_root() / "temp" / "optimized_images" / filename
        file_path = file_path.resolve()

        files = StringCollection()
        files.Add(str(file_path))
        Clipboard.SetFileDropList(files)

        shutil.rmtree(temp_folder)

        self.__call__.add_line(result_output)
        self.__call__.add_line("Image is optimized and copied to clipboard.")


class on_image_optimize_clipboard_dialog:
    icon: str = "🚀"
    title: str = "Optimize image from clipboard as …"

    def __init__(self, **kwargs): ...

    @functions.write_in_output_txt(is_show_output=False)
    def __call__(self, *args, **kwargs) -> None:
        on_image_optimize_clipboard.__call__(self, is_dialog=True)


class on_image_optimize_dialog:
    icon: str = "⬆️"
    title: str = "Optimize images in …/temp"

    def __init__(self, **kwargs): ...

    @functions.write_in_output_txt(is_show_output=True)
    def __call__(self, *args, **kwargs) -> None:
        title: str = "Project folder"
        folder_path: str = QFileDialog.getExistingDirectory(None, title, config["path_articles"])

        if not folder_path:
            self.__call__.add_line("❌ The folder was not selected.")
            return

        commands: str = f'npm run optimize imagesFolder="{folder_path}"'

        result_output = functions.run_powershell_script(commands)
        functions.os_open_file_or_folder(Path(folder_path) / "temp")
        self.__call__.add_line(result_output)


class on_image_optimize_dialog_replace:
    icon: str = "⬆️"
    title: str = "Optimize images in … and replace"

    def __init__(self, **kwargs): ...

    @functions.write_in_output_txt(is_show_output=True)
    def __call__(self, *args, **kwargs) -> None:
        title: str = "Project folder"
        folder_path: str = QFileDialog.getExistingDirectory(None, title, config["path_articles"])

        if not folder_path:
            self.__call__.add_line("❌ The folder was not selected.")
            return

        commands: str = f'npm run optimize imagesFolder="{folder_path}"'
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

        functions.os_open_file_or_folder(folder_path)
        self.__call__.add_line(result_output)


class on_image_optimize_file:
    icon: str = "🖼️"
    title: str = "Optimize one image"

    def __init__(self, **kwargs): ...

    @functions.write_in_output_txt(is_show_output=True)
    def __call__(self, *args, **kwargs) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "Select an Image File",
            config["path_articles"],
            "Image Files (*.jpg *.jpeg *.webp *.png *.svg);;All Files (*)",
        )

        if not file_path:
            self.__call__.add_line("❌ The file was not selected.")
            return

        temp_folder: Path = Path(tempfile.mkdtemp())
        filename: str = Path(file_path).name
        temp_file_path: Path = temp_folder / filename
        shutil.copy(file_path, temp_file_path)

        commands: str = f'npm run optimize imagesFolder="{temp_folder}" outputFolder="optimized_images"'

        result_output = functions.run_powershell_script(commands)

        shutil.rmtree(temp_folder)

        functions.os_open_file_or_folder(functions.get_project_root() / "temp" / "optimized_images")
        self.__call__.add_line(result_output)


class on_images_optimize:
    icon: str = "🚀"
    title: str = "Optimize images"

    def __init__(self, **kwargs): ...

    @functions.write_in_output_txt(is_show_output=True)
    def __call__(self, *args, **kwargs) -> None:
        commands: str = "npm run optimize"

        result_output = functions.run_powershell_script(commands)
        functions.os_open_file_or_folder(functions.get_project_root() / "temp" / "images")
        functions.os_open_file_or_folder(functions.get_project_root() / "temp" / "optimized_images")
        self.__call__.add_line(result_output)


class on_images_optimize_quality:
    icon: str = "🔝"
    title: str = "Optimize images (high quality)"

    def __init__(self, **kwargs): ...

    @functions.write_in_output_txt(is_show_output=True)
    def __call__(self, *args, **kwargs) -> None:
        commands: str = "npm run optimize quality=true"

        result_output = functions.run_powershell_script(commands)
        functions.os_open_file_or_folder(functions.get_project_root() / "temp" / "images")
        functions.os_open_file_or_folder(functions.get_project_root() / "temp" / "optimized_images")
        self.__call__.add_line(result_output)
