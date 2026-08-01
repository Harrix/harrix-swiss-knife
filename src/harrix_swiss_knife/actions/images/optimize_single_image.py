"""Optimize a single image file and replace the original in place."""

from __future__ import annotations

import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

import harrix_pylib as h

from harrix_swiss_knife.actions.base import ActionBase
from harrix_swiss_knife.actions.images.optimize import OnOptimize


class OnOptimizeSingleImage(OnOptimize):
    """Optimize a single image file and replace the original in place."""

    icon = "🖼️"
    title = "Optimize one image in …"
    bold_title = False

    @ActionBase.handle_exceptions("single file optimization")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Optimize a single image file and replace the original in place."""
        filename = self.dialogs.get_open_filename(
            "Select an Image File",
            self.config["path_articles"],
            "Image Files (*.jpg *.jpeg *.webp *.png *.svg *.avif *.mp4);;All Files (*)",
        )
        if not filename:
            return

        self._source_image = Path(filename)
        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("single file optimization thread")
    def in_thread(self) -> str | None:
        """Optimize the selected image in a worker thread."""
        filename = self._source_image
        target_dir = filename.parent
        stem = filename.stem
        project_root = h.dev.get_project_root()

        with TemporaryDirectory() as temp_folder:
            temp_path = Path(temp_folder)
            shutil.copy(filename, temp_path / filename.name)
            output_folder = project_root / "temp/optimized_images"
            result = self.run_optimize_images(
                temp_path,
                output_folder,
            )

            for ext in (".avif", ".png", ".svg"):
                output_file = output_folder / (stem + ext)
                if output_file.exists():
                    target_path = target_dir / (stem + ext)
                    shutil.copy2(output_file, target_path)
                    if target_path != filename and filename.exists():
                        filename.unlink()
                    self.result_folder = target_dir
                    break

        return result

    @ActionBase.handle_exceptions("single file optimization thread completion")
    def thread_after(self, result: Any) -> None:
        """Show toast and result dialog after a single-image optimize."""
        self.show_toast("Optimize completed")
        self.add_line(result)
        self.show_result()
