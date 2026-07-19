"""Image optimization and management actions."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

import harrix_pylib as h
from PIL import Image, ImageGrab
from PySide6.QtCore import QMimeData, QUrl
from PySide6.QtGui import QGuiApplication

from harrix_swiss_knife.actions.base import ActionBase
from harrix_swiss_knife.actions.images.image_optimize import optimize_images_in_folder


class OnOptimizeClipboard(ActionBase):
    """Optimize an image from the clipboard with default naming.

    Takes an image from the clipboard, saves it as a temporary file,
    optimizes it, and places the optimized image path back into the clipboard.

    """

    icon = "🚀"
    title = "Optimize image from clipboard"
    bold_title = False
    quick_launcher = True

    @ActionBase.handle_exceptions("clipboard image optimization")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Optimize an image from the clipboard with default naming."""
        image = ImageGrab.grabclipboard()

        if not isinstance(image, Image.Image):
            self.add_line("❌ No image found in the clipboard")
            return

        filename = "image.png"

        if kwargs.get("is_dialog"):
            image_name = self.dialogs.get_text_input(
                "Image name", "Enter the name of the image (English, without spaces):", "image_01"
            )
            if not image_name:
                return
            filename = image_name.replace(" ", "-") + ".png"

        project_root = h.dev.get_project_root()
        optimized_dir = project_root / "temp/optimized_images"

        with TemporaryDirectory() as temp_folder:
            temp_path = Path(temp_folder)
            temp_filename = temp_path / filename
            image.save(temp_filename, "PNG")
            self.add_line(f"Image is saved as {temp_filename}")

            result = optimize_images_in_folder(
                temp_path,
                optimized_dir,
                project_root,
            )

            stem = Path(filename).stem
            output_ext = ".avif" if (optimized_dir / (stem + ".avif")).exists() else ".png"
            output_file = (optimized_dir / (stem + output_ext)).resolve()

            clipboard = QGuiApplication.clipboard()
            if clipboard is None:
                self.add_line("❌ Clipboard is not available")
                return

            mime_data = QMimeData()
            mime_data.setUrls([QUrl.fromLocalFile(str(output_file))])
            clipboard.setMimeData(mime_data)

        self.add_line(result)
        self.add_line("Image is optimized and copied to clipboard.")
