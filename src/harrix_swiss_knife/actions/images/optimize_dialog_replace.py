"""Image optimization and management actions."""

from __future__ import annotations

import shutil
from typing import Any

import harrix_pylib as h

from harrix_swiss_knife.actions.base import ActionBase
from harrix_swiss_knife.actions.images.optimize import OnOptimize


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
        """Optimize images in a selected folder and replace the originals."""
        self.folder_path = self.dialogs.get_existing_directory("Select folder", self.config["path_articles"])
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
