"""Image optimization and management actions."""

import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

import clr
import harrix_pylib as h
from PIL import Image, ImageGrab

from harrix_swiss_knife.actions.base import ActionBase


class OnClearImages(ActionBase):
    """Clear temporary image directories.

    This action removes all files from the temporary image folders
    (`images` and `optimized_images`) and recreates the empty directories,
    providing a clean workspace for new image operations.
    """

    icon = "🧹"
    title = "Clear folders images"

    @ActionBase.handle_exceptions("clearing image folders")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
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


class OnOpenCameraUploads(ActionBase):
    """Open all Camera Uploads folders.

    This action opens all directories specified in the `paths_camera_uploads`
    configuration setting in the system's file explorer, providing quick access
    to folders where camera photos are typically uploaded or stored.
    """

    icon = "📸"
    title = "Open Camera Uploads"

    @ActionBase.handle_exceptions("opening camera uploads")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        for path in self.config["paths_camera_uploads"]:
            h.file.open_file_or_folder(Path(path))
        self.add_line('The folders from "Camera Uploads" is opened.')


class OnOpenCameraUploadsShort(ActionBase):
    """Open all Camera Uploads folders (short list of folders).

    This action opens all directories specified in the `paths_camera_uploads`
    configuration setting in the system's file explorer, providing quick access
    to folders where camera photos are typically uploaded or stored.
    """

    icon = "📸"
    title = "Open Camera Uploads (short list of folders)"

    @ActionBase.handle_exceptions("opening camera uploads")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        for path in self.config["paths_camera_uploads-short"]:
            h.file.open_file_or_folder(Path(path))
        self.add_line('The folders from "Camera Uploads" is opened.')


class OnOpenImages(ActionBase):
    """Open the source images temporary folder.

    This action opens the temporary directory containing original images
    (`images`) in the system's file explorer, allowing quick access
    to view or manage the source image files.
    """

    icon = "📂"
    title = "Open the folder images"

    @ActionBase.handle_exceptions("opening images folder")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        path = h.dev.get_project_root() / "temp/images"
        if not path.exists():
            path.mkdir(parents=True)
            result = f"Folder `{path}` is created and opened."
        else:
            result = f"Folder `{path}` is opened."
        h.file.open_file_or_folder(path)
        self.add_line(result)


class OnOpenOptimizedImages(ActionBase):
    """Open the optimized images temporary folder.

    This action opens the temporary directory containing optimized images
    (`optimized_images`) in the system's file explorer, allowing quick access
    to view or use the processed image files.
    """

    icon = "📂"
    title = "Open the folder optimized_images"

    @ActionBase.handle_exceptions("opening optimized images folder")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        path = h.dev.get_project_root() / "temp/optimized_images"
        if not path.exists():
            path.mkdir(parents=True)
            result = f"Folder `{path}` is created and opened."
        else:
            result = f"Folder `{path}` is opened."
        h.file.open_file_or_folder(path)
        self.add_line(result)


class OnOptimize(ActionBase):
    """Run standard image optimization on all images in the temp folder.

    This action executes the npm optimize script to process all images
    in the temporary `images` directory using default optimization settings,
    creating compressed versions in the `optimized_images` directory.
    """

    icon = "🚀"
    title = "Optimize images"
    bold_title = True

    @ActionBase.handle_exceptions("image optimization")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("optimization thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        return self.optimize_images_common(
            "npm run optimize convertPngToAvif=compare", h.dev.get_project_root() / "temp/optimized_images"
        )

    def optimize_images_common(self, command: str, output_folder: str | Path | None = None) -> str | None:
        """Perform common image optimization operations.

        Args:

        - `command` (`str`): The npm command to execute for optimization.
        - `output_folder` (`str | Path | None`): Optional output folder to open after optimization.

        Returns:

        - `str | None`: The result of the command execution

        """
        result = h.dev.run_command(command)

        if output_folder:
            h.file.open_file_or_folder(output_folder)

        return result

    @ActionBase.handle_exceptions("optimization thread completion")
    def thread_after(self, result: Any) -> None:
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast("Optimize completed")
        self.add_line(result)
        self.show_result()


class OnOptimizeClipboard(ActionBase):
    """Optimize an image from the clipboard with default naming.

    This action takes an image from the clipboard, saves it as a temporary file,
    optimizes it using the npm optimize script, and then places the optimized
    image path back into the clipboard for easy pasting into documents.
    """

    icon = "🚀"
    title = "Optimize image from clipboard"
    bold_title = False

    @ActionBase.handle_exceptions("clipboard image optimization")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        image = ImageGrab.grabclipboard()

        if not isinstance(image, Image.Image):
            self.add_line("❌ No image found in the clipboard")
            return

        filename = "image.png"

        if kwargs.get("is_dialog"):
            image_name = self.get_text_input(
                "Image name", "Enter the name of the image (English, without spaces):", "image_01"
            )
            if not image_name:
                return
            filename = image_name.replace(" ", "-") + ".png"

        with TemporaryDirectory() as temp_folder:
            temp_filename = Path(temp_folder) / filename
            image.save(temp_filename, "PNG")
            self.add_line(f"Image is saved as {temp_filename}")

            commands = (
                f'npm run optimize imagesFolder="{temp_folder}" '
                'outputFolder="optimized_images" convertPngToAvif=compare'
            )
            result = h.dev.run_command(commands)

            optimized_dir = h.dev.get_project_root() / "temp/optimized_images"
            stem = Path(filename).stem
            output_ext = ".avif" if (optimized_dir / (stem + ".avif")).exists() else ".png"
            filename = (optimized_dir / (stem + output_ext)).resolve()

            clr.AddReference("System.Collections.Specialized")
            clr.AddReference("System.Windows.Forms")
            from System.Collections.Specialized import StringCollection  # type: ignore # noqa: PGH003, PLC0415
            from System.Windows.Forms import Clipboard  # type: ignore # noqa: PGH003, PLC0415

            files = StringCollection()
            files.Add(str(filename))
            Clipboard.SetFileDropList(files)

        self.add_line(result)
        self.add_line("Image is optimized and copied to clipboard.")


class OnOptimizeClipboardDialog(ActionBase):
    """Optimize an image from the clipboard with custom naming.

    This action extends OnOptimizeClipboard by prompting the user to provide
    a custom filename for the optimized image, allowing for more organized
    image management in the output directory.
    """

    icon = "🚀"
    title = "Optimize image from clipboard as …"
    bold_title = False

    @ActionBase.handle_exceptions("clipboard image optimization with dialog")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        OnOptimizeClipboard().execute(is_dialog=True)


class OnOptimizeDialogReplace(OnOptimize):
    """Optimize images in a selected folder and replace the originals.

    This action allows the user to select a folder containing images, processes
    all images using the npm optimize script, and then replaces the original files
    with their optimized versions, maintaining a clean directory structure.
    """

    icon = "⬆️"
    title = "Optimize images in … and replace"
    bold_title = False

    @ActionBase.handle_exceptions("folder image optimization with replacement")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.folder_path = self.get_existing_directory("Select folder", self.config["path_articles"])
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("folder optimization thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        if self.folder_path is None:
            return None

        result = self.optimize_images_common(
            f'npm run optimize imagesFolder="{self.folder_path}" convertPngToAvif=compare'
        )

        # Replace original files with optimized versions
        for item in self.folder_path.iterdir():
            if item.is_file():
                item.unlink()

        temp_folder = self.folder_path / "temp"

        for item in temp_folder.iterdir():
            if item.is_file() or item.is_symlink():
                shutil.copy2(item, self.folder_path / item.name)

        shutil.rmtree(temp_folder)

        return result

    @ActionBase.handle_exceptions("folder optimization thread completion")
    def thread_after(self, result: Any) -> None:
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        if self.folder_path is None:
            return
        h.file.open_file_or_folder(self.folder_path)
        self.show_toast("Optimize completed")
        self.add_line(result)
        self.show_result()


class OnOptimizeQuality(OnOptimize):
    """Optimize images with higher quality settings.

    This action runs the npm optimize script with the quality flag enabled,
    which processes all images in the temp/images directory using settings
    that prioritize visual quality over file size reduction, suitable for
    images where detail preservation is important.
    """

    icon = "🔝"
    title = "Optimize images (high quality)"
    bold_title = False

    @ActionBase.handle_exceptions("high quality optimization thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        return self.optimize_images_common(
            "npm run optimize quality=true convertPngToAvif=compare",
            h.dev.get_project_root() / "temp/optimized_images",
        )


class OnOptimizeResize(OnOptimize):
    """Resize and optimize images (asks for max size in pixels)."""

    icon = "↔️"
    title = "Resize and optimize images"
    bold_title = True

    @ActionBase.handle_exceptions("resize and optimize")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.max_size = self.get_text_input("Max size", "Input max image size in pixels", "1024")

        if self.max_size is None:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("resize and optimize thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        return self.optimize_images_common(
            f"npm run optimize convertPngToAvif=compare maxSize={self.max_size}",
            h.dev.get_project_root() / "temp/optimized_images",
        )


class OnOptimizeSingleImage(OnOptimize):
    """Optimize a single image file and replace the original in place.

    This action prompts the user to select a single image file, processes it
    using the npm optimize script, and replaces the original file with the
    optimized version in the same folder.
    """

    icon = "🖼️"
    title = "Optimize one image"
    bold_title = False

    @ActionBase.handle_exceptions("single file optimization")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        filename = self.get_open_filename(
            "Select an Image File",
            self.config["path_articles"],
            "Image Files (*.jpg *.jpeg *.webp *.png *.svg *.avif *.mp4);;All Files (*)",
        )
        if not filename:
            return

        filename = Path(filename)
        target_dir = filename.parent
        stem = filename.stem

        with TemporaryDirectory() as temp_folder:
            temp_filename = Path(temp_folder) / filename.name
            shutil.copy(filename, temp_filename)

            # E501 fix: split long line for readability and line length
            npm_command = (
                f'npm run optimize imagesFolder="{temp_folder}" '
                'outputFolder="optimized_images" convertPngToAvif=compare'
            )
            result = self.optimize_images_common(
                npm_command,
                None,
            )

            if result is not None:
                self.add_line(result)

            optimized_dir = h.dev.get_project_root() / "temp/optimized_images"
            for ext in (".avif", ".png", ".svg"):
                output_file = optimized_dir / (stem + ext)
                if output_file.exists():
                    target_path = target_dir / (stem + ext)
                    shutil.copy2(output_file, target_path)
                    if target_path != filename and filename.exists():
                        filename.unlink()
                    h.file.open_file_or_folder(target_dir)
                    break

        self.show_result()
