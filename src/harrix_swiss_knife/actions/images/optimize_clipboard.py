"""Optimize an image from the clipboard and put the result path back."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

import harrix_pylib as h
from PIL import Image, ImageGrab
from PySide6.QtCore import QMimeData, QUrl
from PySide6.QtGui import QGuiApplication

from harrix_swiss_knife.actions.base import ActionBase
from harrix_swiss_knife.actions.common.image_optimize import optimize_images_in_folder


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
            message = "❌ No image found in the clipboard"
            self.add_line(message)
            self.show_toast(message)
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
        input_dir = project_root / "temp" / "clipboard_optimize"
        if input_dir.exists():
            shutil.rmtree(input_dir)
        input_dir.mkdir(parents=True, exist_ok=True)

        temp_filename = input_dir / filename
        image.save(temp_filename, "PNG")
        self.add_line(f"Image is saved as {temp_filename}")

        self._clipboard_input_dir = input_dir
        self._clipboard_optimized_dir = project_root / "temp" / "optimized_images"
        self._clipboard_filename = filename
        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("clipboard image optimization thread")
    def in_thread(self) -> str | None:
        """Optimize the clipboard image in a worker thread."""
        project_root = h.dev.get_project_root()
        return optimize_images_in_folder(
            self._clipboard_input_dir,
            self._clipboard_optimized_dir,
            project_root,
        )

    @ActionBase.handle_exceptions("clipboard image optimization thread completion")
    def thread_after(self, result: Any) -> None:
        """Put the optimized image path on the clipboard and show feedback."""
        stem = Path(self._clipboard_filename).stem
        optimized_dir = self._clipboard_optimized_dir
        output_ext = ".avif" if (optimized_dir / (stem + ".avif")).exists() else ".png"
        output_file = (optimized_dir / (stem + output_ext)).resolve()

        clipboard = QGuiApplication.clipboard()
        if clipboard is None:
            message = "❌ Clipboard is not available"
            self.add_line(message)
            self.show_toast(message)
            return

        mime_data = QMimeData()
        mime_data.setUrls([QUrl.fromLocalFile(str(output_file))])
        clipboard.setMimeData(mime_data)

        self.add_line(result)
        self.add_line("Image is optimized and copied to clipboard.")
        self.show_toast("Image is optimized and copied to clipboard")
