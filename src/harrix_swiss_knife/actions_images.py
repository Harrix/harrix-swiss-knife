import os
from pathlib import Path
import shutil
import tempfile
from PIL import Image, ImageGrab
from datetime import datetime
import clr
from PySide6.QtWidgets import QFileDialog


from harrix_swiss_knife import functions

path_default = (
    f"C:/GitHub/_content__harrix-dev/harrix.dev-articles-{datetime.now().year}"
)


class on_images_optimize:
    title = "Optimize images"

    @functions.write_in_output_txt(is_show_output=True)
    def __call__(self, *args, **kwargs):
        commands = "npm run optimize"

        result_output = functions.run_powershell_script(commands)
        os.startfile(Path("data/images"))
        os.startfile(Path("data/optimized_images"))
        self.__call__.add_line(result_output)


class on_images_optimize_quality:
    title = "Optimize images (high quality)"

    @functions.write_in_output_txt(is_show_output=True)
    def __call__(self, *args, **kwargs):
        commands = "npm run optimize quality=true"

        result_output = functions.run_powershell_script(commands)
        os.startfile(Path("data/images"))
        os.startfile(Path("data/optimized_images"))
        self.__call__.add_line(result_output)


class on_image_optimize_dialog:
    title = "Optimize images in …/temp"

    @functions.write_in_output_txt(is_show_output=True)
    def __call__(self, *args, **kwargs):
        title = "Project directory"
        folder_path = QFileDialog.getExistingDirectory(None, title, path_default)

        if not folder_path:
            self.__call__.add_line("The directory was not selected.")
            return

        commands = f'npm run optimize imagesDir="{folder_path}"'

        result_output = functions.run_powershell_script(commands)
        os.startfile(Path(folder_path) / "temp")
        self.__call__.add_line(result_output)


class on_image_optimize_file:
    title = "Optimize one image"

    @functions.write_in_output_txt(is_show_output=True)
    def __call__(self, *args, **kwargs):
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "Select an Image File",
            path_default,
            "Image Files (*.jpg *.jpeg *.webp *.png *.svg);;All Files (*)",
        )

        if not file_path:
            self.__call__.add_line("The file was not selected.")
            return

        temp_dir = Path(tempfile.mkdtemp())
        file_name = Path(file_path).name
        temp_file_path = temp_dir / file_name
        shutil.copy(file_path, temp_file_path)

        commands = (
            f'npm run optimize imagesDir="{temp_dir}" outputDir="optimized_images"'
        )

        result_output = functions.run_powershell_script(commands)

        shutil.rmtree(temp_dir)

        os.startfile(Path("data/optimized_images"))
        self.__call__.add_line(result_output)


class on_image_optimize_clipboard:
    title = "Optimize from clipboard"

    @functions.write_in_output_txt(is_show_output=False)
    def __call__(self, *args, **kwargs):
        image = ImageGrab.grabclipboard()

        if not isinstance(image, Image.Image):
            self.__call__.add_line("No image found in the clipboard")
            return

        temp_dir = Path(tempfile.mkdtemp())
        file_name = "pasted_image.png"
        temp_file_path = temp_dir / file_name
        image.save(temp_file_path, "PNG")
        print(f"Image is saved as {temp_file_path}")

        commands = f'npm run optimize imagesDir="{temp_dir}"'
        result_output = functions.run_powershell_script(commands)

        os.startfile(temp_dir)
        print(str(temp_dir / "temp" / file_name))

        clr.AddReference("System.Collections.Specialized")
        clr.AddReference("System.Windows.Forms")
        from System.Collections.Specialized import StringCollection
        from System.Windows.Forms import Clipboard

        file_path = str(temp_dir / "temp" / file_name)

        files = StringCollection()
        files.Add(file_path)
        Clipboard.SetFileDropList(files)

        # shutil.rmtree(temp_dir)

        self.__call__.add_line(result_output)


class on_image_optimize_dialog_replace:
    title = "Optimize images in … and replace"

    @functions.write_in_output_txt(is_show_output=True)
    def __call__(self, *args, **kwargs):
        title = "Project directory"
        folder_path = QFileDialog.getExistingDirectory(None, title, path_default)

        if not folder_path:
            self.__call__.add_line("The directory was not selected.")
            return

        commands = f'npm run optimize imagesDir="{folder_path}"'

        result_output = functions.run_powershell_script(commands)

        folder_path = Path(folder_path)

        # Remove all files in the main folder
        for item in folder_path.iterdir():
            if item.is_file():
                item.unlink()

        # Specify the path to the 'temp' folder
        temp_folder = folder_path / "temp"

        # Copy all files from the 'temp' folder to the main folder
        for item in temp_folder.iterdir():
            if item.is_file() or item.is_symlink():
                shutil.copy2(item, folder_path / item.name)

        # Remove the empty 'temp' folder
        shutil.rmtree(temp_folder)

        os.startfile(folder_path)
        self.__call__.add_line(result_output)
